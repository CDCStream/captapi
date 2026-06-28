"""YouTube + YouTube Shorts endpoints."""

from __future__ import annotations

import asyncio
import math
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.services.openai_client import summarize_transcript
from app.utils.formatters import safe_int, safe_list, safe_str
from app.utils.url import (
    extract_youtube_id,
    normalize_youtube_url,
)

router = APIRouter()

CREDIT_TRANSCRIPT = 1
CREDIT_SUMMARIZE = 3
CREDIT_VIDEO_DETAILS = 1
CREDIT_CHANNEL_DETAILS = 1
CREDIT_DOWNLOAD = 5

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


def _reply_payload(r: dict) -> dict:
    return {
        "id": safe_str(r.get("cid") or r.get("commentId") or r.get("id")),
        "author": safe_str(r.get("author") or r.get("authorName")),
        "text": (r.get("comment") or r.get("text") or r.get("content") or "").strip(),
        "likeCount": safe_int(r.get("voteCount") or r.get("votes") or r.get("likeCount")),
        "publishedAt": safe_str(r.get("publishedAt") or r.get("publishedTimeText")),
    }


def _video_card(v: dict) -> dict:
    return {
        "url": safe_str(v.get("url") or v.get("videoUrl")),
        "title": safe_str(v.get("title")) or "",
        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
        "durationSeconds": safe_int(v.get("duration")),
        "thumbnailUrl": safe_str(v.get("thumbnailUrl")),
        "channelName": safe_str(v.get("channelName") or v.get("channel")),
    }


# ---------- helpers -------------------------------------------------------
def _require_youtube_url(url: str) -> tuple[str, str]:
    vid = extract_youtube_id(url)
    if not vid:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
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


async def _fetch_transcript_item(norm_url: str, language: str | None) -> dict[str, Any]:
    """Fetch a timestamped transcript, falling back across independent actors.

    A single third-party actor can silently start returning empty results
    (as pintostudio did), so we try a primary actor and a fallback. When a
    specific non-English language is requested we lead with the language-aware
    actor. Returns a normalized item ``{segments, title, language}``.
    """
    apify = get_apify()
    settings = get_settings()
    a1 = settings.APIFY_ACTOR_YT_TRANSCRIPT_1
    a2 = settings.APIFY_ACTOR_YT_TRANSCRIPT_2
    if language and language.lower() not in ("en", "en-us", "english"):
        chain = [a2, a1]
    else:
        chain = [a1, a2]

    last: dict[str, Any] = {"segments": [], "title": None, "language": language}
    for actor in chain:
        for attempt in range(2):
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
                    }
                last = {"segments": [], "title": title, "language": language}
            if attempt == 0:
                await asyncio.sleep(1.0)
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
            return {
                "url": norm_url,
                "videoId": vid,
                "title": safe_str(item.get("title")),
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
                "language": safe_str(item.get("language") or language),
            }

        data = await cached_or_run(
            endpoint="youtube.transcript",
            params={"url": norm_url, "language": language or "", "v": 2},
            runner=_run,
            ctx=ctx,
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
            title = safe_str(item.get("title")) or ""
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
            params={"url": norm_url, "language": language or "", "v": 2},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


# ---------- VIDEO DETAILS -------------------------------------------------
@router.get("/video-details", summary="YouTube video metadata + stats")
async def youtube_video_details(
    url: str = Query(...),
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
            apify = get_apify()
            run_input = {"startUrls": [{"url": norm_url}], "maxResults": 1}
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_VIDEO, run_input, max_items=1
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            v = items[0]
            return {
                "url": norm_url,
                "id": vid,
                "title": safe_str(v.get("title")) or "",
                "description": safe_str(v.get("description") or v.get("text")),
                "channelName": safe_str(v.get("channelName") or v.get("channel")),
                "channelId": safe_str(v.get("channelId") or v.get("authorId")),
                "channelUrl": safe_str(v.get("channelUrl")),
                "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                "durationSeconds": safe_int(v.get("duration") or v.get("durationSeconds")),
                "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                "likeCount": safe_int(v.get("likes") or v.get("likeCount")),
                "commentCount": safe_int(v.get("commentsCount") or v.get("commentCount")),
                "thumbnailUrl": safe_str(v.get("thumbnailUrl") or (v.get("thumbnails") or [{}])[-1].get("url")),
                "tags": safe_list(v.get("tags")),
            }

        data = await cached_or_run(
            endpoint="youtube.video-details",
            params={"url": norm_url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


# ---------- COMMENTS ------------------------------------------------------
@router.get("/comments", summary="YouTube video comments (paginated)")
async def youtube_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_COMMENTS, 2)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/comments",
        platform="youtube",
        resource_url=norm_url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_COMMENTS,
                {"startUrls": [{"url": norm_url}], "maxComments": limit},
                max_items=limit,
            )
            comments = []
            for c in items[:limit]:
                comments.append(
                    {
                        "id": safe_str(c.get("cid") or c.get("commentId") or c.get("id")),
                        "author": safe_str(c.get("author") or c.get("authorName")),
                        "text": (
                            c.get("comment")
                            or c.get("text")
                            or c.get("content")
                            or ""
                        ).strip(),
                        "likeCount": safe_int(
                            c.get("voteCount") or c.get("votes") or c.get("likeCount")
                        ),
                        "publishedAt": safe_str(
                            c.get("publishedAt") or c.get("publishedTimeText")
                        ),
                        "replyCount": safe_int(
                            c.get("replyCount") or c.get("replies")
                        ),
                    }
                )
            return {
                "url": norm_url,
                "videoId": vid,
                "totalReturned": len(comments),
                "comments": comments,
            }

        data = await cached_or_run(
            endpoint="youtube.comments",
            params={"url": norm_url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["comments"]), RATE_YT_COMMENTS, 2)
        return ApiResponse(data=data)


# ---------- CHANNEL DETAILS -----------------------------------------------
@router.get("/channel-details", summary="YouTube channel info & stats")
async def youtube_channel_details(
    url: str = Query(..., description="Channel URL (youtube.com/@handle or /channel/UC...)"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-details",
        platform="youtube",
        resource_url=url,
        base_credits=CREDIT_CHANNEL_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_CHANNEL,
                {"startUrls": [{"url": url}]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Channel not found")
            c = items[0]
            return {
                "url": url,
                "id": safe_str(c.get("channelId") or c.get("id")),
                "name": safe_str(c.get("channelName") or c.get("name")) or "",
                "description": safe_str(c.get("channelDescription") or c.get("description")),
                "subscriberCount": safe_int(c.get("subscriberCount") or c.get("numberOfSubscribers")),
                "videoCount": safe_int(c.get("videosCount") or c.get("videoCount")),
                "viewCount": safe_int(c.get("viewCount") or c.get("totalViews")),
                "thumbnailUrl": safe_str(c.get("avatarUrl") or c.get("thumbnailUrl")),
                "bannerUrl": safe_str(c.get("bannerUrl")),
                "country": safe_str(c.get("country")),
            }

        data = await cached_or_run(
            endpoint="youtube.channel-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


# ---------- CHANNEL VIDEOS ------------------------------------------------
@router.get("/channel-videos", summary="List videos for a YouTube channel")
async def youtube_channel_videos(
    url: str = Query(...),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
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
                        "durationSeconds": safe_int(v.get("duration")),
                        "thumbnailUrl": safe_str(v.get("thumbnailUrl")),
                    }
                )
            return {"url": url, "totalReturned": len(videos), "videos": videos}

        data = await cached_or_run(
            endpoint="youtube.channel-videos",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["videos"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- PLAYLIST VIDEOS -----------------------------------------------
@router.get("/playlist-videos", summary="List videos in a YouTube playlist")
async def youtube_playlist_videos(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
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
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": url}], "maxResults": limit, "type": "playlist"},
                max_items=limit,
            )
            videos = []
            for v in items[:limit]:
                videos.append(
                    {
                        "url": safe_str(v.get("url")),
                        "title": safe_str(v.get("title")) or "",
                        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                        "durationSeconds": safe_int(v.get("duration")),
                        "channelName": safe_str(v.get("channelName") or v.get("channel")),
                    }
                )
            return {"url": url, "totalReturned": len(videos), "videos": videos}

        data = await cached_or_run(
            endpoint="youtube.playlist-videos",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["videos"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- SEARCH --------------------------------------------------------
@router.get("/search", summary="Search YouTube videos by keyword")
async def youtube_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=200),
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
                        "durationSeconds": safe_int(v.get("duration")),
                    }
                )
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="youtube.search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- VIDEO DOWNLOAD ------------------------------------------------
@router.get("/video-download", summary="Get direct video download URLs")
async def youtube_video_download(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/video-download",
        platform="youtube",
        resource_url=norm_url,
        base_credits=CREDIT_DOWNLOAD,
    ) as ctx:
        _DISCRETE_URLS = (
            ("downloadedFileUrl", "combined"),
            ("videoOnlyUrl", "video-only"),
            ("audioOnlyUrl", "audio-only"),
        )
        # Keys the primary downloader emits per format; fallback entries carry
        # the same keys (null) so the formats[] element schema is path-stable.
        _FALLBACK_FORMAT_KEYS = {
            "itag": None, "mimeType": None, "bitrate": None,
            "width": None, "height": None, "fps": None, "qualityLabel": None,
            "audioQuality": None, "approxDurationMs": None,
            "audioSampleRate": None, "audioChannels": None,
            "lastModified": None, "projectionType": None, "qualityOrdinal": None,
        }

        def _has_download(items: list[dict[str, Any]]) -> bool:
            if not items:
                return False
            v = items[0]
            fmts = v.get("formats") or v.get("downloads") or []
            return bool(
                v.get("downloadUrl") or v.get("url") or v.get("mediaUrl") or fmts
                or any(v.get(k) for k, _ in _DISCRETE_URLS)
            )

        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items, _ = await apify.run_with_fallback(
                [
                    (settings.APIFY_ACTOR_YOUTUBE_DOWNLOAD,
                     {"urls": [norm_url], "format": "all", "ttl": "none"}),
                    (settings.APIFY_ACTOR_YOUTUBE_DOWNLOAD_FALLBACK,
                     {"videos": [{"url": norm_url}]}),
                ],
                max_items=1,
                is_valid=_has_download,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not available")
            v = items[0]
            formats_raw = v.get("formats") or v.get("downloads") or []
            download_url = safe_str(
                v.get("downloadUrl")
                or v.get("url")
                or v.get("mediaUrl")
                or (formats_raw[0].get("url") if formats_raw else None)
            )
            # The fallback downloader returns discrete file URLs rather than a
            # formats array; synthesize entries carrying the same keys as the
            # primary actor (null where unknown) so the formats[] element schema
            # is identical on both paths.
            if not formats_raw:
                synth = [
                    {**_FALLBACK_FORMAT_KEYS, "url": safe_str(v.get(key)), "quality": label}
                    for key, label in _DISCRETE_URLS
                    if v.get(key)
                ]
                if synth:
                    formats_raw = synth
                    download_url = download_url or synth[0]["url"]
            return {
                "url": norm_url,
                "videoId": vid,
                "title": safe_str(v.get("title")),
                "downloadUrl": download_url,
                "formats": formats_raw,
                "expiresAt": safe_str(v.get("expiresAt")),
            }

        data = await cached_or_run(
            endpoint="youtube.video-download",
            params={"url": norm_url},
            runner=_run,
            ctx=ctx,
            ttl=3600,
        )
        return ApiResponse(data=data)


# ---------- SHORTS (alias to same actors with Short URL handling) ---------
@router.get("/channel-shorts", summary="List Shorts for a YouTube channel")
async def youtube_channel_shorts(
    url: str = Query(..., description="Channel URL (youtube.com/@handle)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
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
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": _channel_tab_url(url, "shorts")}], "maxResults": limit},
                max_items=limit,
            )
            shorts = [_video_card(v) for v in items[:limit]]
            return {"url": url, "totalReturned": len(shorts), "shorts": shorts}

        data = await cached_or_run(
            endpoint="youtube.channel-shorts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["shorts"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/channel-streams", summary="List live/past streams for a YouTube channel")
async def youtube_channel_streams(
    url: str = Query(..., description="Channel URL (youtube.com/@handle)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
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
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": _channel_tab_url(url, "streams")}], "maxResults": limit},
                max_items=limit,
            )
            streams = [_video_card(v) for v in items[:limit]]
            return {"url": url, "totalReturned": len(streams), "streams": streams}

        data = await cached_or_run(
            endpoint="youtube.channel-streams",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["streams"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/hashtag-search", summary="Search YouTube videos by hashtag")
async def youtube_hashtag_search(
    q: str = Query(..., min_length=2, description="Hashtag (with or without #)"),
    limit: int = Query(20, ge=1, le=200),
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
            apify = get_apify()
            tag = q.lstrip("#")
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {
                    "startUrls": [{"url": f"https://www.youtube.com/hashtag/{tag}"}],
                    "maxResults": limit,
                },
                max_items=limit,
            )
            results = [_video_card(v) for v in items[:limit]]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="youtube.hashtag-search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/shorts/transcript", summary="YouTube Shorts transcript")
async def shorts_transcript(
    url: str = Query(...),
    language: str | None = Query(None, description="ISO language code (en, tr, es...)"),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_transcript(url=url, language=language, caller=caller)


@router.get("/shorts/summarize", summary="YouTube Shorts AI summary")
async def shorts_summarize(
    url: str = Query(...),
    language: str | None = Query(None),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_summarize(url=url, language=language, caller=caller)


@router.get("/shorts/video-details", summary="YouTube Shorts metadata")
async def shorts_details(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_video_details(url=url, caller=caller)


@router.get("/shorts/comments", summary="YouTube Shorts comments")
async def shorts_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_comments(url=url, limit=limit, caller=caller)


# ---------- COMMENT REPLIES ----------------------------------------------
@router.get("/comment-replies", summary="Replies to a YouTube comment")
async def youtube_comment_replies(
    url: str = Query(..., description="YouTube video URL the comment belongs to"),
    comment_id: str = Query(..., description="ID of the parent comment"),
    limit: int = Query(50, ge=1, le=500),
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
            return {
                "url": norm_url,
                "videoId": vid,
                "commentId": comment_id,
                "totalReturned": len(replies[:limit]),
                "replies": replies[:limit],
            }

        data = await cached_or_run(
            endpoint="youtube.comment-replies",
            params={"url": norm_url, "comment_id": comment_id, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["replies"]), RATE_YT_COMMENTS, 2)
        return ApiResponse(data=data)


# ---------- CHANNEL PLAYLISTS ---------------------------------------------
@router.get("/channel-playlists", summary="List a YouTube channel's playlists")
async def youtube_channel_playlists(
    url: str = Query(..., description="Channel URL (youtube.com/@handle)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
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
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": _channel_tab_url(url, "playlists")}], "maxResults": limit},
                max_items=limit,
            )
            playlists = []
            for p in items[:limit]:
                playlists.append(
                    {
                        "url": safe_str(p.get("url") or p.get("playlistUrl")),
                        "title": safe_str(p.get("title")) or "",
                        "videoCount": safe_int(p.get("videoCount") or p.get("numberOfVideos")),
                        "thumbnailUrl": safe_str(p.get("thumbnailUrl")),
                    }
                )
            return {"url": url, "totalReturned": len(playlists), "playlists": playlists}

        data = await cached_or_run(
            endpoint="youtube.channel-playlists",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["playlists"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- COMMUNITY POSTS -----------------------------------------------
@router.get("/community-posts", summary="List a YouTube channel's community posts")
async def youtube_community_posts(
    url: str = Query(..., description="Channel URL (youtube.com/@handle)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
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
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="youtube.community-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_YT_COMMUNITY, 2)
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
            params={"vid": vid},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)
