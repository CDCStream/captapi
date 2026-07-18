"""YouTube + YouTube Shorts endpoints."""

from __future__ import annotations

import asyncio
import json
import math
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse
import xml.etree.ElementTree as ET

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyClient, ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.services.http_fetch import fetch as proxy_fetch
from app.services.openai_client import summarize_transcript
from app.services.youtube_native import (
    channel_details_native,
    channel_tab_native,
    comment_replies_native,
    comments_native,
    hashtag_native,
    playlist_native,
    search_native,
    transcript_native,
)
from app.utils.formatters import normalize_language_code, safe_int, safe_list, safe_str
from app.utils.url import (
    extract_youtube_id,
    normalize_youtube_channel_url,
    normalize_youtube_url,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_TRANSCRIPT = 1
CREDIT_SUMMARIZE = 3
CREDIT_VIDEO_DETAILS = 1
CREDIT_CHANNEL_DETAILS = 1

# YouTube list endpoints hit per-result Apify actors:
#   streamers/youtube-scraper          $2.40/1k WITH an Apify sub ($5/1k without)
#   streamers/youtube-comments-scraper $0.90/1k results (comments)
# Rates target ~80% markup (rate = cost * 400) at the subscription price:
#   videos:   1.0 * $0.0045 = $0.0045 vs $0.0024 -> ~88%. NOTE: requires the
#             $29 Apify Starter sub; at the no-sub $5/1k it's break-even, so
#             keep the subscription active.
#   comments: 0.4 * $0.0045 = $0.0018 vs $0.0009 -> ~100%.
# Charged via ctx["credits_override"] on the actual item count returned.
RATE_YT_VIDEO = 1.0
RATE_YT_MARGIN = 1.4
RATE_YT_COMMENTS = 0.4
# Community posts use a third-party HTTP actor; cost not yet verified, so the
# rate is conservative until confirmed in the Apify console.
RATE_YT_COMMUNITY = 0.5


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    return max(minimum, math.ceil(n * rate))


def _channel_tab_url(url: str, tab: str) -> str:
    """Build a channel sub-tab URL (videos / shorts / streams)."""
    base = (url or "").rstrip("/")
    for suffix in ("/videos", "/shorts", "/streams", "/featured"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}/{tab}"


_YT_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_JSON_DECODER = json.JSONDecoder()


def _extract_initial_json(html: str, var_name: str) -> dict[str, Any] | None:
    """Pull an embedded ``var X = {...};`` blob out of a YouTube page.

    The objects (ytInitialData / ytInitialPlayerResponse) are megabytes long and
    followed by more script on the same line, so a lazy/greedy regex can't find
    the matching brace. We locate the opening ``{`` and let ``raw_decode`` read
    exactly one JSON value, ignoring whatever trails it.
    """
    for anchor in (f"var {var_name} = ", f"{var_name} = "):
        idx = html.find(anchor)
        if idx == -1:
            continue
        start = html.find("{", idx)
        if start == -1:
            continue
        try:
            obj, _ = _JSON_DECODER.raw_decode(html, start)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


async def _channel_playlists_native(url: str, limit: int) -> list[dict[str, Any]]:
    """Parse a channel's /playlists tab straight from ytInitialData.

    The scraping actor cannot handle the playlists tab (it falls back to the
    videos tab and returns videos), while the page itself embeds every playlist
    as a LOCKUP_CONTENT_TYPE_PLAYLIST lockup with id, title, thumbnail and a
    "N videos" badge.
    """
    page_url = _channel_tab_url(url, "playlists")
    # YouTube occasionally serves a page variant without the playlist lockups;
    # one cheap retry avoids falling back to the slow (and wrong) actor.
    data = None
    for _ in range(2):
        try:
            async with httpx.AsyncClient(
                timeout=10, follow_redirects=True, headers=_YT_BROWSER_HEADERS
            ) as client:
                resp = await client.get(page_url)
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        m = re.search(r"var ytInitialData = (\{.*?\});</script>", resp.text, re.DOTALL)
        if not m:
            continue
        try:
            candidate = json.loads(m.group(1))
        except ValueError:
            continue
        if "LOCKUP_CONTENT_TYPE_PLAYLIST" in m.group(1):
            data = candidate
            break
        data = data or candidate
    if data is None:
        return []

    lockups: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            lockup = node.get("lockupViewModel")
            if isinstance(lockup, dict) and lockup.get("contentType") == "LOCKUP_CONTENT_TYPE_PLAYLIST":
                lockups.append(lockup)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for lk in lockups:
        pid = safe_str(lk.get("contentId"))
        if not pid or pid in seen:
            continue
        seen.add(pid)
        meta = (lk.get("metadata") or {}).get("lockupMetadataViewModel") or {}
        title = safe_str((meta.get("title") or {}).get("content"))
        badge = re.search(r'"text":\s*"([\d,.]+)\s+videos?"', json.dumps(lk))
        # Playlist lockups nest the image under collectionThumbnailViewModel,
        # so find the first image "sources" list wherever it lives.
        thumbnail = None

        def find_sources(node: Any) -> list | None:
            if isinstance(node, dict):
                srcs = node.get("sources")
                if isinstance(srcs, list) and srcs and isinstance(srcs[0], dict) and srcs[0].get("url"):
                    return srcs
                for v in node.values():
                    found = find_sources(v)
                    if found:
                        return found
            elif isinstance(node, list):
                for v in node:
                    found = find_sources(v)
                    if found:
                        return found
            return None

        sources = find_sources(lk.get("contentImage")) or []
        if sources:
            thumbnail = safe_str(sources[-1].get("url"))
        rows.append(
            {
                "url": f"https://www.youtube.com/playlist?list={pid}",
                "title": title or "",
                "videoCount": safe_int(badge.group(1).replace(",", "")) if badge else None,
                "thumbnailUrl": thumbnail,
            }
        )
        if len(rows) >= limit:
            break
    return rows


def _playlist_id(url: str) -> str | None:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    return parse_qs(parsed.query).get("list", [None])[0]


async def _youtube_channel_id(url: str) -> str | None:
    match = re.search(r"youtube\.com/channel/(UC[\w-]+)", url)
    if match:
        return match.group(1)
    headers = {"User-Agent": "Captapi/1.0 (+https://captapi.com)"}
    try:
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True, headers=headers) as client:
            resp = await client.get(url)
    except httpx.HTTPError:
        return None
    if resp.status_code >= 400:
        return None
    for pattern in (
        r'"channelId":"(UC[\w-]+)"',
        r'<meta itemprop="channelId" content="(UC[\w-]+)"',
        r'"externalId":"(UC[\w-]+)"',
    ):
        found = re.search(pattern, resp.text)
        if found:
            return found.group(1)
    return None


async def _youtube_feed_videos(feed_url: str, limit: int) -> list[dict[str, Any]]:
    headers = {"User-Agent": "Captapi/1.0 (+https://captapi.com)"}
    async with httpx.AsyncClient(timeout=6.0, follow_redirects=True, headers=headers) as client:
        resp = await client.get(feed_url)
    if resp.status_code >= 400:
        return []
    root = ET.fromstring(resp.text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    videos: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns)[:limit]:
        video_id = safe_str(entry.findtext("yt:videoId", default="", namespaces=ns))
        title = safe_str(entry.findtext("atom:title", default="", namespaces=ns))
        published = safe_str(entry.findtext("atom:published", default="", namespaces=ns))
        channel_name = safe_str(entry.findtext("atom:author/atom:name", default="", namespaces=ns))
        videos.append(
            {
                "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
                "title": title,
                "publishedAt": published,
                "viewCount": 0,
                "durationSeconds": 0,
                "thumbnailUrl": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
                "channelName": channel_name,
            }
        )
    return videos


async def _youtube_channel_feed(url: str, limit: int) -> list[dict[str, Any]]:
    channel_id = await _youtube_channel_id(url)
    if not channel_id:
        return []
    return await _youtube_feed_videos(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}", limit)


async def _youtube_playlist_feed(url: str, limit: int) -> list[dict[str, Any]]:
    playlist_id = _playlist_id(url)
    if not playlist_id:
        return []
    return await _youtube_feed_videos(f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}", limit)


def _reply_payload(r: dict) -> dict:
    return {
        "id": safe_str(r.get("cid") or r.get("commentId") or r.get("id")),
        "author": safe_str(r.get("author") or r.get("authorName")),
        "authorAvatarUrl": safe_str(r.get("avatar") or r.get("authorThumbnail")),
        "authorIsVerified": bool(r.get("isVerified")),
        "authorIsChannelOwner": bool(r.get("authorIsChannelOwner")),
        "text": (r.get("comment") or r.get("text") or r.get("content") or "").strip(),
        "likeCount": safe_int(r.get("voteCount") or r.get("votes") or r.get("likeCount")) or 0,
        "hasCreatorHeart": bool(r.get("hasCreatorHeart")),
        "publishedTimeText": safe_str(r.get("publishedTimeText") or r.get("publishedAt")),
    }


def _best_snippet_thumbnail(snippet: dict) -> str | None:
    thumbs = snippet.get("thumbnails") or {}
    for key in ("maxres", "standard", "high", "medium", "default"):
        entry = thumbs.get(key)
        if isinstance(entry, dict) and entry.get("url"):
            return safe_str(entry["url"])
    return None


def _video_card(v: dict) -> dict:
    # powerai/youtube-playlist-videos-scraper emits YouTube Data API
    # playlistItem objects with everything nested under `snippet`.
    snippet = v.get("snippet")
    if isinstance(snippet, dict) and (snippet.get("resourceId") or snippet.get("videoUrl")):
        video_id = safe_str((snippet.get("resourceId") or {}).get("videoId"))
        return {
            "url": safe_str(snippet.get("videoUrl"))
            or (f"https://www.youtube.com/watch?v={video_id}" if video_id else ""),
            "title": safe_str(snippet.get("title")) or "",
            "publishedAt": safe_str(snippet.get("publishedAt")),
            "viewCount": safe_int(snippet.get("viewCount")),
            "durationSeconds": _duration_seconds(snippet.get("duration")),
            "thumbnailUrl": _best_snippet_thumbnail(snippet),
            "channelName": safe_str(snippet.get("videoOwnerChannelTitle") or snippet.get("channelTitle")),
        }
    video_id = safe_str(v.get("videoId") or v.get("video_id") or v.get("id"))
    url = safe_str(v.get("url") or v.get("videoUrl") or v.get("video_url") or v.get("link"))
    if not url and video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
    return {
        "url": url,
        "title": safe_str(v.get("title") or v.get("videoTitle") or v.get("video_title") or v.get("name")) or "",
        "publishedAt": safe_str(v.get("date") or v.get("publishedAt") or v.get("published_at") or v.get("published")),
        "viewCount": safe_int(v.get("viewCount") or v.get("views") or v.get("view_count") or v.get("view_count_text")),
        "durationSeconds": _duration_seconds(
            v.get("duration") or v.get("durationSeconds") or v.get("duration_seconds") or v.get("lengthSeconds")
        ),
        "thumbnailUrl": safe_str(v.get("thumbnailUrl") or v.get("thumbnail") or v.get("thumbnail_url") or v.get("thumbnailUrlHigh")),
        "channelName": safe_str(v.get("channelName") or v.get("channel") or v.get("channelTitle") or v.get("channel_name")),
    }


def _has_video_card_data(v: dict[str, Any]) -> bool:
    if v.get("error"):
        return False
    snippet = v.get("snippet")
    if isinstance(snippet, dict) and (snippet.get("resourceId") or snippet.get("videoUrl")):
        return True
    explicit_url = safe_str(v.get("url") or v.get("videoUrl") or v.get("video_url") or v.get("link"))
    title = safe_str(v.get("title") or v.get("videoTitle") or v.get("video_title") or v.get("name"))
    return bool(explicit_url or title)


def _valid_video_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [i for i in items if isinstance(i, dict) and _has_video_card_data(i)]


def _playlist_actor_candidates(settings: Any, url: str, limit: int) -> list[tuple[str, dict[str, Any]]]:
    playlist_id = _playlist_id(url)
    dedicated_payload: dict[str, Any] = {
        "playlistUrl": url,
        # powerai actor schema currently enforces min 50; max_items trims output.
        "maxResults": max(limit, 50),
    }
    if playlist_id:
        dedicated_payload["playlistId"] = playlist_id
    return [
        (settings.APIFY_ACTOR_YOUTUBE_PLAYLIST, dedicated_payload),
        (
            settings.APIFY_ACTOR_YOUTUBE_PLAYLIST_FALLBACK,
            {"startUrls": [{"url": url}], "maxResults": limit, "type": "playlist"},
        ),
        (
            settings.APIFY_ACTOR_YOUTUBE_SEARCH,
            {"startUrls": [{"url": url}], "maxResults": limit, "type": "playlist"},
        ),
    ]


def _community_post(p: dict) -> dict:
    # The community actor emits snake_case fields (post_id, author_name,
    # content_text, media_urls, likes as a display string like "330K").
    post_id = safe_str(p.get("id") or p.get("postId") or p.get("post_id"))
    url = safe_str(p.get("url") or p.get("postUrl") or p.get("post_url"))
    if not url and post_id:
        url = f"https://www.youtube.com/post/{post_id}"
    media = p.get("images") or p.get("media") or p.get("media_urls") or []
    images = [safe_str(i) for i in media if isinstance(i, str) and i]
    return {
        "platform": "youtube",
        "id": post_id,
        "url": url,
        "text": safe_str(p.get("text") or p.get("content") or p.get("message") or p.get("content_text")),
        "publishedAt": safe_str(p.get("publishedAt") or p.get("date") or p.get("published_time_text")),
        "channelName": safe_str(p.get("channelName") or p.get("channel") or p.get("author_name")),
        "channelUrl": safe_str(p.get("channelUrl") or p.get("author_url")),
        "likes": safe_int(p.get("likes") or p.get("likeCount")) or safe_str(p.get("likes")),
        "comments": safe_int(p.get("comments") or p.get("commentCount") or p.get("comments_count")),
        "images": images,
        "raw": p,
    }


# ---------- helpers -------------------------------------------------------
def _require_youtube_url(url: str) -> tuple[str, str]:
    vid = extract_youtube_id(url)
    if not vid:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                url,
                "youtube",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            ),
        )
    return vid, normalize_youtube_url(url)


def _ts_float(x: Any) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _normalize_segments(rec: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize one transcript record into ``[{text, start, duration}]``.

    Handles the different shapes returned by our transcript actors:
    - scrape-creators: ``transcript: [{text, startMs, endMs, ...}]`` (ms strings)
    - automation-lab:  ``segments:   [{text, start, duration, end}]`` (seconds)
    - legacy/other:    ``data``/``transcript`` with ``start``/``offset``/``dur``
    """
    raw = rec.get("transcript") or rec.get("segments") or rec.get("data") or []
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for s in raw:
        if not isinstance(s, dict):
            continue
        text = (s.get("text") or "").strip()
        if not text:
            continue
        if s.get("startMs") is not None:
            start = _ts_float(s.get("startMs")) / 1000.0
            end_ms = s.get("endMs")
            duration = (_ts_float(end_ms) / 1000.0 - start) if end_ms is not None else 0.0
        elif s.get("start") is not None or s.get("offset") is not None:
            start = _ts_float(s.get("start") if s.get("start") is not None else s.get("offset"))
            duration = _ts_float(s.get("duration") if s.get("duration") is not None else s.get("dur"))
        else:
            start, duration = 0.0, 0.0
        out.append({"text": text, "start": start, "duration": max(duration, 0.0)})
    return out


def _transcript_segments(item: dict[str, Any]) -> list[dict[str, Any]]:
    raw = item.get("segments")
    return raw if isinstance(raw, list) else []


def _transcript_run_input(actor: str, norm_url: str, language: str | None) -> dict[str, Any]:
    """Build the actor-specific input for a transcript run."""
    a = actor.lower()
    if "automation-lab" in a:
        return {"urls": [norm_url], "language": (language or "en"), "includeAutoGenerated": True}
    if "scrape-creators" in a:
        return {"videoUrls": [norm_url]}
    if "pintostudio" in a:
        return {"videoUrl": norm_url, "targetLanguage": (language or "en")}
    return {"videoUrls": [norm_url]}


async def _oembed_title(norm_url: str) -> str | None:
    """Fetch the video title from YouTube's free oEmbed endpoint.

    Transcript actors often omit the title; oEmbed needs no API key and
    answers in ~100ms, so it fills the gap without another actor run.
    """
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                "https://www.youtube.com/oembed",
                params={"url": norm_url, "format": "json"},
            )
        if resp.status_code == 200:
            return safe_str(resp.json().get("title"))
    except Exception:
        pass
    return None


async def _fetch_transcript_item(norm_url: str, language: str | None) -> dict[str, Any]:
    """Fetch a timestamped transcript, falling back across independent actors.

    A single third-party actor can silently start returning empty results
    (as pintostudio did), so we try a primary actor and a fallback. When a
    specific non-English language is requested we lead with the language-aware
    actor. Returns a normalized item ``{segments, title, language}``.
    """
    native = await transcript_native(norm_url, language)
    if native and native.get("segments"):
        return {**native, "source": "direct"}

    apify = get_apify()
    settings = get_settings()
    a1 = settings.APIFY_ACTOR_YT_TRANSCRIPT_1
    a2 = settings.APIFY_ACTOR_YT_TRANSCRIPT_2
    if language and language.lower() not in ("en", "en-us", "english"):
        chain = [a2, a1]
    else:
        chain = [a1, a2]

    # One attempt per actor: an actor that just returned empty/errored almost
    # never succeeds on an immediate retry, and each retry risked another full
    # actor run (~2 min worst case). Two independent actors are redundancy
    # enough; worst case is now 2 runs instead of 4.
    last: dict[str, Any] = {"segments": [], "title": None, "language": language}
    for actor in chain:
        try:
            items = await apify.run_actor_sync(
                actor, _transcript_run_input(actor, norm_url, language), max_items=1
            )
        except Exception:
            items = []
        if items:
            rec = items[0]
            segs = _normalize_segments(rec)
            title = safe_str(rec.get("videoTitle") or rec.get("video_title") or rec.get("title"))
            if segs:
                return {
                    "segments": segs,
                    "title": title,
                    "language": safe_str(rec.get("language") or rec.get("selectedLanguage") or language),
                    "source": "apify",
                }
            last = {"segments": [], "title": title, "language": language}
    return last


# ---------- TRANSCRIPT ----------------------------------------------------
@router.get(
    "/transcript",
    summary="Get YouTube video transcript",
    description=f"Returns the full transcript with timestamps. Costs {CREDIT_TRANSCRIPT} credit.",
)
async def youtube_transcript(
    url: str = Query(..., description="YouTube video URL"),
    language: str | None = Query(None, description="ISO language code (en, tr, es...)"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/transcript",
        platform="youtube",
        resource_url=norm_url,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            item = await _fetch_transcript_item(norm_url, language)
            ctx["source"] = item.get("source")
            segments_raw = _transcript_segments(item)
            segments = []
            text_parts = []
            for s in segments_raw:
                text = (s.get("text") or "").strip()
                start = float(s.get("start") or s.get("offset") or 0.0)
                duration = float(s.get("duration") or s.get("dur") or 0.0)
                mm = int(start // 60)
                ss = int(start % 60)
                if text:
                    segments.append(
                        {
                            "text": text,
                            "start": start,
                            "duration": duration,
                            "end": round(start + duration, 3),
                            "timestamp": f"{mm:02d}:{ss:02d}",
                        }
                    )
                    text_parts.append(text)
            if not segments:
                raise HTTPException(
                    status_code=404,
                    detail="Transcript not available for this video",
                )
            full = " ".join(text_parts)
            title = safe_str(item.get("title")) or await _oembed_title(norm_url)
            return {
                "url": norm_url,
                "videoId": vid,
                "title": title,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
                "language": normalize_language_code(safe_str(item.get("language") or language)),
            }

        data = await cached_or_run(
            endpoint="youtube.transcript",
            params={"url": norm_url, "language": language or "", "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


# ---------- SUMMARIZE -----------------------------------------------------
@router.get(
    "/summarize",
    summary="AI summary of a YouTube video",
    description=f"Transcript + GPT summary. Costs {CREDIT_SUMMARIZE} credits.",
)
async def youtube_summarize(
    url: str = Query(...),
    language: str | None = Query(None),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/summarize",
        platform="youtube",
        resource_url=norm_url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            item = await _fetch_transcript_item(norm_url, language)
            ctx["source"] = item.get("source")
            title = safe_str(item.get("title")) or await _oembed_title(norm_url) or ""
            seg_raw = _transcript_segments(item)
            transcript_text = " ".join(
                (s.get("text") or "").strip() for s in seg_raw
            ).strip()
            if not transcript_text:
                raise HTTPException(
                    status_code=404,
                    detail="Transcript not available for this video",
                )

            ai = await summarize_transcript(
                transcript_text, title=title, language=language or "en"
            )
            return {
                "url": norm_url,
                "videoId": vid,
                "title": title or None,
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
            }

        data = await cached_or_run(
            endpoint="youtube.summarize",
            params={"url": norm_url, "language": language or "", "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _duration_seconds(value: Any) -> int | None:
    """Parse a video duration into whole seconds.

    Actors return durations in mixed shapes: int/float seconds, digit strings,
    "HH:MM:SS" / "M:SS" text (streamers/youtube-scraper), or ISO-8601
    ("PT5M48S"). `safe_int` silently dropped the text shapes to null.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?", s, re.IGNORECASE)
    if m and any(m.groups()):
        hours = int(m.group(1) or 0)
        minutes = int(m.group(2) or 0)
        seconds = float(m.group(3) or 0)
        return int(hours * 3600 + minutes * 60 + seconds)
    if re.fullmatch(r"\d+(?::\d{1,2}){1,2}", s):
        total = 0
        for part in s.split(":"):
            total = total * 60 + int(part)
        return total
    return None


def _format_duration(seconds: int | None) -> str | None:
    if seconds is None:
        return None
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# ---------- VIDEO DETAILS -------------------------------------------------
_LIKE_LABEL_RES = [
    # "like this video along with 1,234,567 other people"
    re.compile(r"along with ([\d.,]+) other", re.IGNORECASE),
    # "1,234,567 likes"
    re.compile(r'"([\d.,]+) likes"', re.IGNORECASE),
]


def _parse_like_count(html: str) -> int | None:
    """Best-effort like count from the watch page's embedded JSON.

    YouTube exposes likes only as a localized accessibility label, so this is
    inherently fuzzy; returns None when no known pattern matches (caller then
    falls back to the Apify actor which reports likes directly)."""
    for rx in _LIKE_LABEL_RES:
        m = rx.search(html)
        if m:
            digits = re.sub(r"[.,]", "", m.group(1))
            if digits.isdigit():
                return int(digits)
    return None


async def _video_details_native(vid: str, norm_url: str) -> dict[str, Any] | None:
    """Fetch video metadata straight from the watch page (no Apify).

    Parses ``ytInitialPlayerResponse`` for core metadata/stats and the like
    count from the page JSON. Returns None if the page can't be fetched or the
    core fields are missing, so the caller can fall back to the actor.
    """
    try:
        resp = await proxy_fetch(
            norm_url,
            tier="datacenter",
            headers=_YT_BROWSER_HEADERS,
            cookies={"CONSENT": "YES+1", "SOCS": "CAI"},
            timeout=12,
        )
    except httpx.HTTPError:
        return None
    if resp.status_code >= 400:
        return None

    player = _extract_initial_json(resp.text, "ytInitialPlayerResponse")
    if player is None:
        return None

    details = player.get("videoDetails") or {}
    if not details.get("title"):
        return None  # age-gated / unavailable -> let actor try

    micro = (player.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    thumbs = (details.get("thumbnail") or {}).get("thumbnails") or []
    duration_seconds = _duration_seconds(details.get("lengthSeconds"))
    channel_id = safe_str(details.get("channelId"))

    return {
        "url": norm_url,
        "id": vid,
        "title": safe_str(details.get("title")) or "",
        "description": safe_str(details.get("shortDescription")),
        "channelName": safe_str(details.get("author") or micro.get("ownerChannelName")),
        "channelId": channel_id,
        "channelUrl": (f"https://www.youtube.com/channel/{channel_id}" if channel_id else None),
        "publishedAt": safe_str(micro.get("publishDate") or micro.get("uploadDate")),
        "durationSeconds": duration_seconds,
        "durationFormatted": _format_duration(duration_seconds),
        "viewCount": safe_int(details.get("viewCount")),
        "likeCount": _parse_like_count(resp.text),
        "commentCount": None,  # not exposed in page JSON; enrich via actor only if requested
        "thumbnailUrl": safe_str(thumbs[-1].get("url")) if thumbs else None,
        "genre": safe_str(micro.get("category")),
        "tags": safe_list(details.get("keywords")),
    }


@router.get("/video-details", summary="YouTube video metadata + stats")
async def youtube_video_details(
    url: str = Query(...),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/video-details",
        platform="youtube",
        resource_url=norm_url,
        base_credits=CREDIT_VIDEO_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: parse the watch page ourselves (no actor cost, ~1-2s).
            native = await _video_details_native(vid, norm_url)
            if native is not None and native.get("viewCount") is not None:
                ctx["source"] = "direct"
                return native

            # Fallback: Apify actor (also fills likeCount/commentCount).
            apify = get_apify()
            run_input = {"startUrls": [{"url": norm_url}], "maxResults": 1}
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_VIDEO, run_input, max_items=1
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            v = items[0]
            ctx["source"] = "apify"
            duration_seconds = _duration_seconds(
                v.get("duration")
                if v.get("duration") is not None
                else v.get("durationSeconds") or v.get("lengthSeconds")
            )
            if duration_seconds is None:
                ms = safe_int(v.get("durationMs"))
                duration_seconds = int(ms / 1000) if ms else None
            return {
                "url": norm_url,
                "id": vid,
                "title": safe_str(v.get("title")) or "",
                "description": safe_str(v.get("description") or v.get("text")),
                "channelName": safe_str(v.get("channelName") or v.get("channel")),
                "channelId": safe_str(v.get("channelId") or v.get("authorId")),
                "channelUrl": safe_str(v.get("channelUrl")),
                "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                "durationSeconds": duration_seconds,
                "durationFormatted": _format_duration(duration_seconds),
                "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                "likeCount": safe_int(v.get("likes") or v.get("likeCount")),
                "commentCount": safe_int(v.get("commentsCount") or v.get("commentCount")),
                "thumbnailUrl": safe_str(v.get("thumbnailUrl") or (v.get("thumbnails") or [{}])[-1].get("url")),
                "genre": safe_str(v.get("genre") or v.get("category") or v.get("categoryName")),
                "tags": safe_list(v.get("tags")),
            }

        data = await cached_or_run(
            endpoint="youtube.video-details",
            params={"url": norm_url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


# ---------- COMMENTS ------------------------------------------------------
@router.get("/comments", summary="YouTube video comments (cursor-paginated)")
async def youtube_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the "
            "nextCursor value returned in the previous response."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    cost = _scaled_credits(limit, RATE_YT_COMMENTS, 2)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/comments",
        platform="youtube",
        resource_url=norm_url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Native InnerTube only — Apify's streamers comments actor has no
            # client-facing cursor, so it cannot power nextCursor/hasMore.
            native = await comments_native(norm_url, limit, cursor=cursor)
            if not native or not native.get("comments"):
                raise HTTPException(
                    status_code=400 if cursor else 502,
                    detail=(
                        "Invalid or expired cursor. Start a new request without cursor."
                        if cursor
                        else "Could not fetch YouTube comments"
                    ),
                )
            ctx["source"] = "direct"
            comments = native["comments"]
            next_cursor = safe_str(native.get("nextCursor")) or None
            return {
                "url": norm_url,
                "videoId": vid,
                "totalReturned": len(comments),
                "totalComments": native.get("totalComments"),
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "comments": comments,
            }

        data = await cached_or_run(
            endpoint="youtube.comments",
            params={"url": norm_url, "limit": limit, "cursor": cursor or "", "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["comments"]), RATE_YT_COMMENTS, 2)
        return ApiResponse(data=data)


# ---------- CHANNEL DETAILS -----------------------------------------------
@router.get("/channel-details", summary="YouTube channel info & stats")
async def youtube_channel_details(
    url: str = Query(..., description="Channel URL, @handle, bare handle, or UC... channel ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = normalize_youtube_channel_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-details",
        platform="youtube",
        resource_url=url,
        base_credits=CREDIT_CHANNEL_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await channel_details_native(url)
            if native and native.get("id"):
                ctx["source"] = "direct"
                return native

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_CHANNEL,
                {"startUrls": [{"url": url}]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Channel not found")
            c = items[0]
            ctx["source"] = "apify"
            links = [
                {"text": safe_str(link.get("text")), "url": safe_str(link.get("url"))}
                for link in safe_list(c.get("channelDescriptionLinks"))
                if isinstance(link, dict) and link.get("url")
            ]
            return {
                "url": safe_str(c.get("channelUrl")) or url,
                "id": safe_str(c.get("channelId") or c.get("id")),
                "name": safe_str(c.get("channelName") or c.get("name")) or "",
                "handle": safe_str(c.get("channelUsername")),
                "description": safe_str(c.get("channelDescription") or c.get("description")),
                "subscriberCount": safe_int(c.get("subscriberCount") or c.get("numberOfSubscribers")),
                "videoCount": safe_int(c.get("channelTotalVideos") or c.get("videosCount") or c.get("videoCount")),
                "viewCount": safe_int(c.get("channelTotalViews") or c.get("viewCount") or c.get("totalViews")),
                "thumbnailUrl": safe_str(c.get("channelAvatarUrl") or c.get("avatarUrl") or c.get("thumbnailUrl")),
                "bannerUrl": safe_str(c.get("channelBannerUrl") or c.get("bannerUrl")),
                "country": safe_str(c.get("channelLocation") or c.get("country")),
                "joinedDate": safe_str(c.get("channelJoinedDate")),
                "verified": c.get("isChannelVerified"),
                "links": links,
            }

        data = await cached_or_run(
            endpoint="youtube.channel-details",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


# ---------- CHANNEL VIDEOS ------------------------------------------------
@router.get("/channel-videos", summary="List videos for a YouTube channel")
async def youtube_channel_videos(
    url: str = Query(..., description="Channel URL, @handle, bare handle, or UC... channel ID"),
    limit: int = Query(20, ge=1, le=200),
    fast: bool = Query(False, description="Use YouTube's public RSS feed for faster but less detailed metadata."),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = normalize_youtube_channel_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-videos",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            if fast:
                feed_videos = await _youtube_channel_feed(url, limit)
                if feed_videos:
                    ctx["source"] = "direct"
                    return {"url": url, "totalReturned": len(feed_videos), "videos": feed_videos}
            native_videos = await channel_tab_native(_channel_tab_url(url, "videos"), limit)
            if native_videos:
                ctx["source"] = "direct"
                return {"url": url, "totalReturned": len(native_videos), "videos": native_videos}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": url}], "maxResults": limit},
                max_items=limit,
            )
            videos = []
            for v in items[:limit]:
                videos.append(
                    {
                        "url": safe_str(v.get("url") or v.get("videoUrl")),
                        "title": safe_str(v.get("title")) or "",
                        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                        "durationSeconds": _duration_seconds(v.get("duration") or v.get("lengthSeconds")),
                        "thumbnailUrl": safe_str(v.get("thumbnailUrl")),
                    }
                )
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(videos), "videos": videos}

        data = await cached_or_run(
            endpoint="youtube.channel-videos",
            params={"url": url, "limit": limit, "fast": fast, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["videos"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- PLAYLIST VIDEOS -----------------------------------------------
@router.get("/playlist-videos", summary="List videos in a YouTube playlist")
async def youtube_playlist_videos(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    fast: bool = Query(False, description="Use YouTube's public RSS feed for faster but less detailed metadata."),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/playlist-videos",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # RSS is instant but caps at 15 items with no view/duration data,
            # so it only serves the explicit fast mode.
            if fast:
                feed_videos = await _youtube_playlist_feed(url, limit)
                if feed_videos:
                    ctx["source"] = "direct"
                    return {"url": url, "totalReturned": len(feed_videos), "videos": feed_videos}
            native = await playlist_native(url, limit)
            if native and native.get("videos"):
                ctx["source"] = "direct"
                return {"url": url, "totalReturned": len(native["videos"]), "videos": native["videos"]}
            apify = get_apify()
            items, _actor = await apify.run_with_fallback(
                _playlist_actor_candidates(settings, url, limit),
                max_items=limit,
                is_valid=lambda rows: bool(_valid_video_items(rows)),
            )
            items = _valid_video_items(items)
            if not items:
                feed_videos = await _youtube_playlist_feed(url, limit)
                if feed_videos:
                    ctx["source"] = "direct"
                    return {"url": url, "totalReturned": len(feed_videos), "videos": feed_videos}
            videos = []
            for v in items[:limit]:
                videos.append(_video_card(v))
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(videos), "videos": videos}

        data = await cached_or_run(
            endpoint="youtube.playlist-videos",
            params={"url": url, "limit": limit, "fast": fast, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["videos"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/playlist", summary="YouTube playlist metadata + videos")
async def youtube_playlist(
    url: str = Query(..., description="YouTube playlist URL"),
    limit: int = Query(50, ge=1, le=500),
    fast: bool = Query(False, description="Use YouTube's public RSS feed for faster but less detailed metadata."),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/playlist",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            if fast:
                feed_videos = await _youtube_playlist_feed(url, limit)
                if feed_videos:
                    ctx["source"] = "direct"
                    return {
                        "platform": "youtube",
                        "url": url,
                        "title": "",
                        "channelName": feed_videos[0].get("channelName") if feed_videos else "",
                        "totalReturned": len(feed_videos),
                        "videos": feed_videos,
                    }
            native = await playlist_native(url, limit)
            if native and native.get("videos"):
                ctx["source"] = "direct"
                return {
                    "platform": "youtube",
                    "url": url,
                    "title": safe_str(native.get("title")) or "",
                    "channelName": safe_str(native.get("channelName")) or "",
                    "totalReturned": len(native["videos"]),
                    "videos": native["videos"],
                }
            items, _actor = await get_apify().run_with_fallback(
                _playlist_actor_candidates(settings, url, limit),
                max_items=limit,
                is_valid=lambda rows: bool(_valid_video_items(rows)),
            )
            items = _valid_video_items(items)
            if not items:
                feed_videos = await _youtube_playlist_feed(url, limit)
                if feed_videos:
                    ctx["source"] = "direct"
                    return {
                        "platform": "youtube",
                        "url": url,
                        "title": "",
                        "channelName": feed_videos[0].get("channelName") if feed_videos else "",
                        "totalReturned": len(feed_videos),
                        "videos": feed_videos,
                    }
            videos = [_video_card(v) for v in items[:limit]]
            first = items[0] if items else {}
            ctx["source"] = "apify"
            return {
                "platform": "youtube",
                "url": url,
                "title": safe_str(first.get("playlistTitle") or first.get("playlistName")),
                "channelName": safe_str(first.get("channelName") or first.get("channel")),
                "totalReturned": len(videos),
                "videos": videos,
            }

        data = await cached_or_run(
            endpoint="youtube.playlist",
            params={"url": url, "limit": limit, "fast": fast, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["videos"]), RATE_YT_VIDEO, 5)
        return ApiResponse(data=data)


# ---------- SEARCH --------------------------------------------------------
@router.get("/search", summary="Search YouTube videos by keyword")
async def youtube_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/search",
        platform="youtube",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_results = await search_native(q, limit)
            if native_results:
                ctx["source"] = "direct"
                return {"query": q, "totalReturned": len(native_results), "results": native_results}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"searchQueries": [q], "maxResults": limit, "maxResultsShorts": 0},
                max_items=limit,
            )
            results = []
            for v in items[:limit]:
                results.append(
                    {
                        "url": safe_str(v.get("url") or v.get("videoUrl")),
                        "title": safe_str(v.get("title")) or "",
                        "channelName": safe_str(v.get("channelName") or v.get("channel")),
                        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                        "thumbnailUrl": safe_str(v.get("thumbnailUrl")),
                        "durationSeconds": _duration_seconds(v.get("duration") or v.get("lengthSeconds")),
                    }
                )
            ctx["source"] = "apify"
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="youtube.search",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/trending-shorts", summary="Trending YouTube Shorts")
async def youtube_trending_shorts(
    q: str = Query("trending", min_length=2, description="Seed keyword for trending Shorts"),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_MARGIN, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/trending-shorts",
        platform="youtube",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Browser-based actor regularly needs >120s; the default sync
            # timeout turns those runs into 502s. When even 280s is not
            # enough, reuse the actor's latest successful run instead of
            # failing -- trending content stays relevant for hours.
            client = ApifyClient(timeout=280, max_attempts=1)
            try:
                items = await client.run_actor_sync(
                    settings.APIFY_ACTOR_YOUTUBE_SHORTS,
                    {
                        "searchQuery": q,
                        "searchQueries": [],
                        "channelUrls": [],
                        "hashtagUrls": [],
                        "startUrls": [],
                        "maxResults": limit,
                        "proxyConfiguration": {"useApifyProxy": False},
                    },
                    max_items=limit,
                )
            except ApifyError:
                items = await client.last_succeeded_items(
                    settings.APIFY_ACTOR_YOUTUBE_SHORTS,
                    max_age_secs=48 * 3600,
                    max_items=limit,
                )
                if not items:
                    raise
            ctx["source"] = "apify"
            shorts = [_video_card(v) for v in items[:limit]]
            return {"platform": "youtube", "query": q, "totalReturned": len(shorts), "shorts": shorts}

        data = await cached_or_run(
            endpoint="youtube.trending-shorts",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            # Trending actor runs take minutes; serve the last list instantly
            # after TTL expiry and refresh in the background.
            stale_while_revalidate=True,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["shorts"]), RATE_YT_MARGIN, 2)
        return ApiResponse(data=data)


# ---------- SHORTS (alias to same actors with Short URL handling) ---------
@router.get("/channel-shorts", summary="List Shorts for a YouTube channel")
async def youtube_channel_shorts(
    url: str = Query(..., description="Channel URL, @handle, bare handle, or UC... channel ID"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = normalize_youtube_channel_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-shorts",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_shorts = await channel_tab_native(_channel_tab_url(url, "shorts"), limit, shorts=True)
            if native_shorts:
                ctx["source"] = "direct"
                return {"url": url, "totalReturned": len(native_shorts), "shorts": native_shorts}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": _channel_tab_url(url, "shorts")}], "maxResults": limit},
                max_items=limit,
            )
            shorts = [_video_card(v) for v in items[:limit]]
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(shorts), "shorts": shorts}

        data = await cached_or_run(
            endpoint="youtube.channel-shorts",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["shorts"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/channel-streams", summary="List live/past streams for a YouTube channel")
async def youtube_channel_streams(
    url: str = Query(..., description="Channel URL, @handle, bare handle, or UC... channel ID"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = normalize_youtube_channel_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-streams",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_streams = await channel_tab_native(_channel_tab_url(url, "streams"), limit)
            if native_streams:
                ctx["source"] = "direct"
                return {"url": url, "totalReturned": len(native_streams), "streams": native_streams}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": _channel_tab_url(url, "streams")}], "maxResults": limit},
                max_items=limit,
            )
            streams = [_video_card(v) for v in items[:limit]]
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(streams), "streams": streams}

        data = await cached_or_run(
            endpoint="youtube.channel-streams",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["streams"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/hashtag-search", summary="Search YouTube videos by hashtag")
async def youtube_hashtag_search(
    q: str = Query(..., min_length=2, description="Hashtag (with or without #)"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/hashtag-search",
        platform="youtube",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            tag = q.lstrip("#")
            native_results = await hashtag_native(tag, limit)
            if native_results:
                ctx["source"] = "direct"
                return {"query": q, "totalReturned": len(native_results), "results": native_results}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {
                    "startUrls": [{"url": f"https://www.youtube.com/hashtag/{tag}"}],
                    "maxResults": limit,
                },
                max_items=limit,
            )
            results = [_video_card(v) for v in items[:limit]]
            ctx["source"] = "apify"
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="youtube.hashtag-search",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/shorts/transcript", summary="YouTube Shorts transcript")
async def shorts_transcript(
    url: str = Query(...),
    language: str | None = Query(None, description="ISO language code (en, tr, es...)"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_transcript(url=url, language=language, cache=cache, caller=caller)


@router.get("/shorts/summarize", summary="YouTube Shorts AI summary")
async def shorts_summarize(
    url: str = Query(...),
    language: str | None = Query(None),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_summarize(url=url, language=language, cache=cache, caller=caller)


@router.get("/shorts/video-details", summary="YouTube Shorts metadata")
async def shorts_details(
    url: str = Query(...),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_video_details(url=url, cache=cache, caller=caller)


@router.get("/shorts/comments", summary="YouTube Shorts comments")
async def shorts_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the "
            "nextCursor value returned in the previous response."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_comments(url=url, limit=limit, cursor=cursor, cache=cache, caller=caller)


# ---------- COMMENT REPLIES ----------------------------------------------
@router.get("/comment-replies", summary="Replies to a YouTube comment")
async def youtube_comment_replies(
    url: str = Query(..., description="YouTube video URL the comment belongs to"),
    comment_id: str = Query(..., description="ID of the parent comment"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_COMMENTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/comment-replies",
        platform="youtube",
        resource_url=norm_url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_replies = await comment_replies_native(norm_url, comment_id, limit) if limit <= 20 else []
            if native_replies:
                ctx["source"] = "direct"
                return {
                    "url": norm_url,
                    "videoId": vid,
                    "commentId": comment_id,
                    "totalReturned": len(native_replies),
                    "replies": native_replies,
                }

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_COMMENTS,
                {"startUrls": [{"url": norm_url}], "maxComments": limit * 4, "includeReplies": True},
                max_items=limit * 4,
            )
            replies = []
            for c in items:
                parent = safe_str(c.get("replyToCid") or c.get("parentCommentId") or c.get("replyTo"))
                nested = c.get("replies")
                # Some actors nest replies inside the parent comment object.
                if isinstance(nested, list) and safe_str(c.get("cid") or c.get("commentId") or c.get("id")) == comment_id:
                    for r in nested:
                        replies.append(_reply_payload(r))
                elif parent == comment_id:
                    replies.append(_reply_payload(c))
                if len(replies) >= limit:
                    break
            ctx["source"] = "apify"
            return {
                "url": norm_url,
                "videoId": vid,
                "commentId": comment_id,
                "totalReturned": len(replies[:limit]),
                "replies": replies[:limit],
            }

        data = await cached_or_run(
            endpoint="youtube.comment-replies",
            params={"url": norm_url, "comment_id": comment_id, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["replies"]), RATE_YT_COMMENTS, 2)
        return ApiResponse(data=data)


# ---------- CHANNEL PLAYLISTS ---------------------------------------------
@router.get("/channel-playlists", summary="List a YouTube channel's playlists")
async def youtube_channel_playlists(
    url: str = Query(..., description="Channel URL, @handle, bare handle, or UC... channel ID"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = normalize_youtube_channel_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-playlists",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: parse the playlists tab directly (the scraping actor
            # can't — it silently returns the videos tab instead).
            playlists = await _channel_playlists_native(url, limit)
            if not playlists:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                    {"startUrls": [{"url": _channel_tab_url(url, "playlists")}], "maxResults": limit},
                    max_items=limit,
                )
                for p in items[:limit]:
                    if p.get("type") and p.get("type") != "playlist":
                        continue
                    playlists.append(
                        {
                            "url": safe_str(p.get("url") or p.get("playlistUrl")),
                            "title": safe_str(p.get("title")) or "",
                            "videoCount": safe_int(p.get("videoCount") or p.get("numberOfVideos")),
                            "thumbnailUrl": safe_str(p.get("thumbnailUrl")),
                        }
                    )
                if playlists:
                    ctx["source"] = "apify"
            else:
                ctx["source"] = "direct"
            return {"url": url, "totalReturned": len(playlists), "playlists": playlists}

        data = await cached_or_run(
            endpoint="youtube.channel-playlists",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["playlists"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- COMMUNITY POSTS -----------------------------------------------
@router.get("/community-posts", summary="List a YouTube channel's community posts")
async def youtube_community_posts(
    url: str = Query(..., description="Channel URL, @handle, bare handle, or UC... channel ID"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = normalize_youtube_channel_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_COMMUNITY, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/community-posts",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_COMMUNITY,
                {"startUrls": [{"url": url}], "maxposts": limit},
                max_items=limit,
            )
            posts = []
            for p in items[:limit]:
                if p.get("_parse_error") or p.get("error"):
                    continue
                media = p.get("media_urls") or []
                images = [safe_str(i) for i in media if isinstance(i, str) and i]
                # The actor reports likes as a display string (e.g. "330K") when
                # present, so we surface it verbatim rather than forcing an int.
                posts.append(
                    {
                        "id": safe_str(p.get("post_id")),
                        "author": safe_str(p.get("author_name")),
                        "text": (p.get("content_text") or "").strip(),
                        "likeCount": safe_str(p.get("likes")),
                        "hashtags": p.get("hashtags") or [],
                        "linkedVideos": p.get("linked_videos") or p.get("video_links") or [],
                        "publishedTime": safe_str(p.get("published_time_text")),
                        "postType": safe_str(p.get("post_type")),
                        "images": images,
                        "sourceUrl": safe_str(p.get("post_url")) or url,
                    }
                )
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="youtube.community-posts",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_YT_COMMUNITY, 2)
        return ApiResponse(data=data)


def _runs_text(node: Any) -> str | None:
    if not isinstance(node, dict):
        return None
    if node.get("simpleText"):
        return str(node["simpleText"])
    runs = node.get("runs") or []
    text = "".join(str(r.get("text") or "") for r in runs if isinstance(r, dict))
    return text or None


def _find_backstage_post(obj: Any):
    if isinstance(obj, dict):
        if "backstagePostRenderer" in obj:
            yield obj["backstagePostRenderer"]
        for value in obj.values():
            yield from _find_backstage_post(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _find_backstage_post(value)


async def _fetch_community_post_page(url: str) -> dict[str, Any]:
    """Parse a single community post from the public post page's
    ytInitialData (the community actor only accepts channel URLs)."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    cookies = {"CONSENT": "YES+1", "SOCS": "CAI"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers, cookies=cookies) as client:
        resp = await client.get(url)
    if resp.status_code >= 400:
        raise HTTPException(status_code=404, detail="Community post not found")
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", resp.text, flags=re.DOTALL)
    if not match:
        raise HTTPException(status_code=404, detail="Community post not found")
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Failed to parse community post page") from exc
    post = next(_find_backstage_post(data), None)
    if not post:
        raise HTTPException(status_code=404, detail="Community post not found")

    post_id = safe_str(post.get("postId"))
    author = post.get("authorText") or {}
    author_browse = (
        ((post.get("authorEndpoint") or {}).get("browseEndpoint") or {}).get("canonicalBaseUrl")
    )
    attachment = post.get("backstageAttachment") or {}
    images = []
    for renderer in _find_images(attachment):
        thumbs = (renderer.get("image") or {}).get("thumbnails") or []
        if thumbs:
            images.append(safe_str(thumbs[-1].get("url")))
    return {
        "platform": "youtube",
        "id": post_id,
        "url": f"https://www.youtube.com/post/{post_id}" if post_id else url,
        "text": safe_str(_runs_text(post.get("contentText"))),
        "publishedAt": safe_str(_runs_text(post.get("publishedTimeText"))),
        "channelName": safe_str(_runs_text(author)),
        "channelUrl": f"https://www.youtube.com{author_browse}" if author_browse else None,
        "likes": safe_str(_runs_text(post.get("voteCount"))),
        "comments": None,
        "images": [i for i in images if i],
    }


def _find_images(obj: Any):
    if isinstance(obj, dict):
        if "backstageImageRenderer" in obj:
            yield obj["backstageImageRenderer"]
        for value in obj.values():
            yield from _find_images(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _find_images(value)


@router.get("/community-post-details", summary="YouTube community post details")
async def youtube_community_post_details(
    url: str = Query(..., description="YouTube community post URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/community-post-details",
        platform="youtube",
        resource_url=url,
        base_credits=1,  # native: parsed from the public post page, no actor cost
    ) as ctx:
        async def _run() -> dict[str, Any]:
            item = await _fetch_community_post_page(url)
            ctx["source"] = "direct"  # parsed from the public post page, no actor
            return item

        data = await cached_or_run(
            endpoint="youtube.community-post-details",
            params={"url": url, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


# ---------- VIDEO SPONSORS (SponsorBlock) ---------------------------------
CREDIT_SPONSORS = 1
_SPONSOR_CATEGORIES = ["sponsor", "selfpromo", "interaction"]


def _format_seconds(value: float | int | None) -> str | None:
    if value is None:
        return None
    total = int(round(float(value)))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def _normalize_sponsor_segment(seg: dict[str, Any]) -> dict[str, Any]:
    bounds = seg.get("segment") or [None, None]
    start = bounds[0] if len(bounds) > 0 else None
    end = bounds[1] if len(bounds) > 1 else None
    return {
        "category": safe_str(seg.get("category")),
        "actionType": safe_str(seg.get("actionType")),
        "startSeconds": start,
        "endSeconds": end,
        "startFormatted": _format_seconds(start),
        "endFormatted": _format_seconds(end),
        "durationSeconds": round(end - start, 3) if start is not None and end is not None else None,
        "votes": safe_int(seg.get("votes")),
        "uuid": safe_str(seg.get("UUID")),
    }


@router.get("/video-sponsors", summary="Sponsor/self-promo segments in a YouTube video")
async def youtube_video_sponsors(
    url: str = Query(..., description="YouTube video URL or ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, _ = _require_youtube_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/video-sponsors",
        platform="youtube",
        resource_url=f"https://www.youtube.com/watch?v={vid}",
        base_credits=CREDIT_SPONSORS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            params = [("videoID", vid)]
            params += [("category", c) for c in _SPONSOR_CATEGORIES]
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{settings.SPONSORBLOCK_API_BASE}/api/skipSegments",
                    params=params,
                )
            if resp.status_code == 404:
                return {"videoId": vid, "totalReturned": 0, "segments": []}
            if resp.status_code >= 400:
                raise HTTPException(status_code=502, detail="Sponsor lookup failed upstream")
            raw = resp.json()
            ctx["source"] = "direct"  # SponsorBlock public API, no actor
            segments = [_normalize_sponsor_segment(s) for s in raw if isinstance(s, dict)]
            video_duration = next(
                (s.get("videoDuration") for s in raw if isinstance(s, dict) and s.get("videoDuration")),
                None,
            )
            return {
                "videoId": vid,
                "videoDurationSeconds": video_duration,
                "totalReturned": len(segments),
                "segments": segments,
            }

        data = await cached_or_run(
            endpoint="youtube.video-sponsors",
            params={"vid": vid, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
