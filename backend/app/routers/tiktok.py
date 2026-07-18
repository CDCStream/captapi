"""TikTok endpoints."""

from __future__ import annotations

import asyncio
import math
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.services.openai_client import (
    WHISPER_MAX_BYTES,
    infer_region,
    summarize_transcript,
    transcribe_audio,
)
from app.services import tiktok_native
from app.services.tiktok_native import (
    audience_regions_native,
    channel_details_native,
    profile_region_native,
    video_details_native,
)
from app.utils.countries import country_name
from app.utils.formatters import (
    first_present,
    normalize_language_code,
    safe_float,
    safe_int,
    safe_list,
    safe_str,
)
from app.utils.url import (
    extract_tiktok_id,
    extract_tiktok_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_TRANSCRIPT = 2
CREDIT_SUMMARIZE = 4
CREDIT_VIDEO_DETAILS = 1
CREDIT_CHANNEL_DETAILS = 1
CREDIT_COMMENTS = 2  # native (TikTok's own API); flat fee, our cost ~$0
CREDIT_PROFILE_REGION = 2  # native profile page + fast LLM region estimate
CREDIT_AUDIENCE = 3  # video list (actor) + native commenter-region sampling
CREDIT_SEARCH = 2

# Audience-country sampling for /audience-demographics: how many recent videos
# to pull commenter regions from, and how many country codes to gather before
# tallying.
AUDIENCE_VIDEO_SAMPLE = 12
AUDIENCE_TARGET_TOTAL = 500

# ---------------------------------------------------------------------------
# Per-result credit rates for list endpoints.
#
# These actors are billed by Apify PER RESULT, so our credit charge must scale
# with the number of items, otherwise margin collapses. Rates are chosen so
# that revenue (rate x $0.0045/credit) >= Apify per-result cost x 1.8 (~80%
# markup). The endpoint charges `ctx["credits_override"]` based on the actual
# number of items returned (never more than the upfront `limit` estimate).
# ---------------------------------------------------------------------------
# Verified Apify prices (Free/no-subscription tier = worst case for us). Sell
# price is $0.0045/credit, so an ~80% markup needs rate >= cost_per_result*400.
RATE_FOLLOWERS = 0.4       # clockworks followers-scraper  $1.00/1k ($0.001)
RATE_COMMENTS = 0.2        # clockworks comments-scraper   $0.50/1k ($0.0005)
RATE_CHANNEL_POSTS = 0.7   # clockworks tiktok-scraper     $1.70/1k ($0.0017)
RATE_MUSIC_POSTS = 1.6     # clockworks sound-scraper      $4.00/1k ($0.004)
RATE_USER_SEARCH = 0.4     # clockworks user search (per profile)
# Trending/popular endpoints hit a third-party HTTP actor; cost not yet verified
# in the Apify console, so rates are conservative until confirmed.
RATE_TREND = 0.7
RATE_TREND_MARGIN = 1.4

# Reply scraper crawls a video's comments to find one comment's replies, and is
# billed per ROW pushed (comment or reply) at $2.40/1k = $0.0024/row. We
# therefore bill on the actual crawl size, not the returned reply count, and cap
# the crawl so a viral video can't run up an unbounded bill.
REPLIES_MAX_COMMENTS = 40
REPLIES_MAX_ITEMS = 400
RATE_REPLIES_ROW = 1.0     # ~80% markup on $0.0024/row
CREDIT_REPLIES_MIN = 30


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    return max(minimum, math.ceil(n * rate))


def _require_tiktok_video_url(url: str) -> str:
    video_id = extract_tiktok_id(url)
    if not video_id:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                url,
                "tiktok",
                "https://www.tiktok.com/@user/video/1234567890",
            ),
        )
    return video_id


def _require_tiktok_profile(value: str) -> str:
    handle = extract_tiktok_username(value)
    if not handle:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                value,
                "tiktok",
                "https://www.tiktok.com/@username",
            ),
        )
    return handle


# Residential proxy improves reliability of the dedicated comment/reply scraper
# on large or rate-limited videos (optional but recommended by the actor).
TIKTOK_RESIDENTIAL_PROXY = {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}


def _normalize_connection(item: dict) -> dict:
    """Map a Clockworks follower/following relationship row to our user shape.

    Each row exposes the connected profile under ``authorMeta`` plus a
    ``connectionType`` ("follower" / "following").
    """
    a = item.get("authorMeta") or {}
    username = a.get("name") or a.get("uniqueId")
    return {
        "username": safe_str(username),
        "displayName": safe_str(a.get("nickName") or a.get("nickname")),
        "bio": safe_str(a.get("signature")),
        "url": safe_str(a.get("profileUrl"))
        or (f"https://www.tiktok.com/@{username}" if username else None),
        "followers": safe_int(a.get("fans")),
        "following": safe_int(a.get("following")),
        "verified": a.get("verified"),
        "profileImage": safe_str(a.get("avatar") or a.get("originalAvatarUrl")),
    }


def _normalize_user(item: dict) -> dict:
    """Map a TikTok user-search result to our user shape.

    The search actor may nest the profile under ``authorMeta`` or expose it at
    the top level, so we look in both places.
    """
    a = item.get("authorMeta") or item.get("author") or item
    stats = item.get("authorStats") or item.get("stats") or {}
    username = a.get("name") or a.get("uniqueId") or item.get("uniqueId")
    return {
        "username": safe_str(username),
        "displayName": safe_str(a.get("nickName") or a.get("nickname")),
        "bio": safe_str(a.get("signature")),
        "url": safe_str(a.get("profileUrl"))
        or (f"https://www.tiktok.com/@{username}" if username else None),
        "followers": safe_int(a.get("fans") or a.get("followerCount") or stats.get("followerCount")),
        "verified": a.get("verified"),
        "profileImage": safe_str(a.get("avatar") or a.get("avatarLarger") or a.get("originalAvatarUrl")),
    }


def _normalize_profile_region(item: dict, handle: str) -> dict:
    user = item.get("user") or item.get("authorMeta") or item
    stats = item.get("stats") or item.get("authorStats") or {}
    return {
        "platform": "tiktok",
        "username": safe_str(user.get("uniqueId") or user.get("name") or handle),
        "displayName": safe_str(user.get("nickname") or user.get("nickName")),
        "url": safe_str(user.get("profileUrl")) or f"https://www.tiktok.com/@{handle}",
        "region": safe_str(
            user.get("region")
            or user.get("country")
            or user.get("countryCode")
            or item.get("region")
            or item.get("country")
            or item.get("countryCode")
        ),
        "language": safe_str(
            user.get("language")
            or user.get("languageCode")
            or item.get("language")
            or item.get("languageCode")
            # Language of the sampled video caption — best public signal the
            # profile actor exposes.
            or item.get("textLanguage")
        ),
        "followers": safe_int(
            user.get("followerCount")
            or user.get("fans")
            or stats.get("followerCount")
            or stats.get("followers")
        ),
        "following": safe_int(user.get("followingCount") or user.get("following")),
        "likes": safe_int(
            first_present(user.get("heartCount"), user.get("heart"), user.get("likes"), stats.get("heartCount"))
        ),
        "videos": safe_int(first_present(user.get("videoCount"), user.get("video"), stats.get("videoCount"))),
        "verified": first_present(user.get("verified"), user.get("isVerified")),
        "private": first_present(user.get("privateAccount"), user.get("isPrivate")),
        "profileImage": safe_str(user.get("avatarLarger") or user.get("avatar") or user.get("avatarMedium")),
        "raw": item,
    }


def _tt_published_iso(item: dict) -> str | None:
    """publishedAt as …T00:45:18.000Z. Prefer the actor's ISO string; otherwise
    convert the unix ``createTime`` (never stringify the raw integer)."""
    iso = safe_str(item.get("createTimeISO"))
    if iso:
        return iso
    ts = safe_int(item.get("createTime"))
    if ts:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    return None


def _normalize(item: dict) -> dict:
    """Map raw TikTok actor output to our standard shape."""
    author = item.get("authorMeta") or item.get("author") or {}
    stats = item.get("stats") or {}
    music = item.get("musicMeta") or item.get("music") or {}
    if not isinstance(music, dict):  # aweme rows carry a plain mp3 URL here
        music = {}
    if not isinstance(author, dict):
        author = {}
    video_meta = item.get("videoMeta") or {}
    covers = safe_list(item.get("covers"))
    media_urls = safe_list(item.get("mediaUrls"))
    return {
        "platform": "tiktok",
        "url": safe_str(item.get("webVideoUrl") or item.get("url")),
        "id": safe_str(item.get("id") or item.get("videoId")),
        "caption": safe_str(item.get("text") or item.get("desc")),
        "description": safe_str(item.get("text") or item.get("desc")),
        "publishedAt": _tt_published_iso(item),
        "durationSeconds": safe_float(video_meta.get("duration") or item.get("duration")),
        "thumbnailUrl": safe_str(
            video_meta.get("coverUrl")
            or video_meta.get("originalCoverUrl")
            or (covers[0] if covers else None)
        ),
        "videoUrl": safe_str(
            item.get("videoUrl")
            or video_meta.get("downloadAddr")
            or (item.get("video") or {}).get("downloadAddr")
            or (media_urls[0] if media_urls else None)
        ),
        "author": {
            "username": safe_str(author.get("name") or author.get("uniqueId")),
            "displayName": safe_str(author.get("nickName") or author.get("nickname")),
            "url": safe_str(author.get("profileUrl")),
            "followers": safe_int(author.get("fans") or author.get("followers")),
            "verified": author.get("verified"),
            "profileImage": safe_str(author.get("avatar") or author.get("avatarLarger")),
        },
        "engagement": {
            "views": safe_int(item.get("playCount") or stats.get("playCount")),
            "likes": safe_int(item.get("diggCount") or stats.get("diggCount")),
            "comments": safe_int(item.get("commentCount") or stats.get("commentCount")),
            "shares": safe_int(item.get("shareCount") or stats.get("shareCount")),
            "saves": safe_int(item.get("collectCount") or stats.get("collectCount")),
        },
        "hashtags": [h.get("name") if isinstance(h, dict) else h for h in safe_list(item.get("hashtags"))],
        "musicName": safe_str(music.get("musicName") or music.get("title")),
    }


def _normalize_aweme(item: dict) -> dict:
    """Map raw TikTok API "aweme" rows (powerai music-posts scraper) to our shape.

    These rows use snake_case TikTok-internal fields (digg_count, play_count,
    author.unique_id ...) instead of the clockworks shape `_normalize` expects.
    """
    author = item.get("author") or {}
    username = safe_str(author.get("unique_id"))
    video_id = safe_str(item.get("video_id"))
    create_time = item.get("create_time")
    published = None
    if isinstance(create_time, (int, float)) and create_time > 0:
        published = datetime.fromtimestamp(int(create_time), tz=timezone.utc).isoformat()
    return {
        "platform": "tiktok",
        "url": f"https://www.tiktok.com/@{username}/video/{video_id}" if username and video_id else None,
        "id": video_id or safe_str(item.get("aweme_id")),
        "caption": safe_str(item.get("title")),
        "description": safe_str(item.get("title")),
        "publishedAt": published,
        "durationSeconds": safe_float(item.get("duration")),
        "thumbnailUrl": safe_str(item.get("cover") or item.get("origin_cover")),
        "videoUrl": safe_str(item.get("play") or item.get("wmplay")),
        "author": {
            "username": username,
            "displayName": safe_str(author.get("nickname")),
            "url": f"https://www.tiktok.com/@{username}" if username else None,
            "followers": None,
            "verified": None,
            "profileImage": safe_str(author.get("avatar")),
        },
        "engagement": {
            "views": safe_int(item.get("play_count")),
            "likes": safe_int(item.get("digg_count")),
            "comments": safe_int(item.get("comment_count")),
            "shares": safe_int(item.get("share_count")),
            "saves": safe_int(item.get("collect_count")),
        },
        "hashtags": [],
        "musicName": None,
    }


def _normalize_music_post(item: dict) -> dict:
    is_aweme = bool(item.get("aweme_id") or ("digg_count" in item and "play_count" in item))
    return _normalize_aweme(item) if is_aweme else _normalize(item)


def _tiktok_music_id(value: str) -> str | None:
    match = re.search(r"(\d{6,})(?:\?|$)", value)
    return match.group(1) if match else None


def _tiktok_music_candidates(settings: Any, url: str, limit: int) -> list[tuple[str, dict[str, Any]]]:
    music_id = _tiktok_music_id(url)
    candidates: list[tuple[str, dict[str, Any]]] = []
    if music_id:
        candidates.append(
            (
                settings.APIFY_ACTOR_TIKTOK_MUSIC_POSTS,
                {"music_id": music_id, "maxResults": limit},
            )
        )
    candidates.extend(
        [
            (
                settings.APIFY_ACTOR_TIKTOK_MUSIC,
                {
                    "sounds": [music_id or url],
                    "maxVideosPerSound": limit,
                    "includeSoundSummary": False,
                    "includeVideoFields": True,
                    "stopOnError": False,
                },
            ),
            (
                settings.APIFY_ACTOR_TIKTOK_MUSIC_FALLBACK,
                {"musics": [url], "resultsPerPage": limit, "shouldDownloadVideos": False},
            ),
        ]
    )
    return candidates


def _normalize_suggestion(item: dict, seed: str) -> dict:
    suggestion = (
        item.get("suggestion")
        or item.get("keyword")
        or item.get("query")
        or item.get("text")
        or item.get("searchTerm")
    )
    suggestion = safe_str(suggestion)
    # Always build the search URL ourselves: TikTok's search does not resolve
    # %20-encoded spaces, so we use + (quote_plus). The actor's own searchUrl
    # uses %20 and returns no results, so we ignore it.
    search_url = f"https://www.tiktok.com/search?q={quote_plus(suggestion)}" if suggestion else ""
    return {
        "seed": safe_str(item.get("seedKeyword") or item.get("seed") or item.get("sourceKeyword") or seed),
        "suggestion": suggestion,
        "rank": safe_int(item.get("suggestionRank") or item.get("rank") or item.get("position")),
        "searchUrl": search_url,
        "region": safe_str(item.get("region")),
        "language": safe_str(item.get("language")),
    }


def _normalize_creator(item: dict) -> dict:
    user = item.get("user") or item.get("author") or item
    handle = safe_str(
        user.get("uniqueId") or user.get("username") or user.get("handle") or item.get("creatorHandle")
    )
    if handle:
        handle = handle.lstrip("@")
    # Creative Center trending rows report 0 for counts they don't publish;
    # surface those as unknown instead of a literal zero.
    followers = safe_int(user.get("followerCount") or item.get("followers") or item.get("followersCount"))
    likes = safe_int(user.get("heartCount") or item.get("likes") or item.get("likesCount") or item.get("likeCount"))
    videos = safe_int(user.get("videoCount") or item.get("videoCount"))
    return {
        "rank": safe_int(item.get("rank")),
        "username": handle,
        "displayName": safe_str(user.get("nickname") or user.get("displayName") or user.get("name")),
        "url": safe_str(user.get("profileUrl") or item.get("url"))
        or (f"https://www.tiktok.com/@{handle}" if handle else None),
        "bio": safe_str(user.get("signature") or user.get("bio")),
        "followers": followers or None,
        "engagementRate": item.get("engagementRate") or item.get("engagement_rate"),
        "likes": likes or None,
        "videos": videos or None,
        "country": safe_str(item.get("countryCode") or item.get("country") or user.get("region")),
        "verified": user.get("verified") or user.get("isVerified"),
        "profileImage": safe_str(
            user.get("avatarLarger") or user.get("avatar") or item.get("avatar") or item.get("creatorAvatarUrl")
        ),
    }


@router.get("/video-details", summary="TikTok video metadata + stats")
async def tiktok_video_details(
    url: str = Query(...),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_tiktok_video_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/video-details",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_VIDEO_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: parse the video page's embedded JSON (no actor cost, ~2s).
            native = await video_details_native(url)
            if native is not None and native["engagement"].get("views") is not None:
                ctx["source"] = "direct"
                return native

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {"postURLs": [url], "resultsPerPage": 1, "shouldDownloadVideos": False},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            ctx["source"] = "apify"
            return _normalize(items[0])

        data = await cached_or_run(
            endpoint="tiktok.video-details",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _tiktok_transcript_segments(item: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Normalize a transcript actor item's ``segments`` (start/end shape)."""
    segments = []
    parts = []
    for s in item.get("segments") or []:
        if not isinstance(s, dict):
            continue
        text = safe_str(s.get("text")).strip()
        if not text:
            continue
        start = round(safe_float(s.get("start")) or 0, 3)
        end = round(safe_float(s.get("end")) or 0, 3)
        mm, ss = int(start // 60), int(start % 60)
        segments.append(
            {
                "text": text,
                "start": start,
                "duration": round(max(end - start, 0), 3),
                "end": round(max(end, start), 3),
                "timestamp": f"{mm:02d}:{ss:02d}",
            }
        )
        parts.append(text)
    full = (safe_str(item.get("transcript")) or " ".join(parts)).strip()
    return full, segments


async def _fetch_tiktok_transcript(
    url: str, language: str | None = None
) -> tuple[str, list[dict[str, Any]], str | None]:
    """Return (full transcript, timestamped segments, language).

    Cascade: native download + our Whisper (hallucination-filtered, language
    retries) -> fast native-caption actor -> Whisper-capable actor.
    """
    settings = get_settings()
    apify = get_apify()

    # Primary: fetch the media ourselves and run our own Whisper pipeline.
    # The actors' Whisper has no language handling and mislabels e.g. Turkish
    # speech over music as Russian; ours retries with the detected/pinned
    # language and filters hallucinations.
    raw = await tiktok_native.fetch_video_bytes(url, max_bytes=WHISPER_MAX_BYTES)
    if raw:
        result = await transcribe_audio(raw, filename="tiktok.mp4", language=language)
        if result["transcript"]:
            return (
                result["transcript"],
                result["transcriptSegments"],
                safe_str(result.get("language")),
            )
        # Our Whisper heard no speech; trust that over the actors' output
        # only when a language wasn't forced (actors may still have captions).

    # Fast path: native caption track over plain HTTP. Measured 8.8s vs 33.6s
    # for identical text on the same video. Fails/returns hasCaption=false for
    # caption-less videos, in which case we fall through to Whisper.
    try:
        items = await apify.run_actor_sync(
            settings.APIFY_ACTOR_TIKTOK_TRANSCRIPT_FAST,
            {"videoUrls": [url], "proxyConfiguration": {"useApifyProxy": True}},
            max_items=1,
        )
    except Exception:  # noqa: BLE001
        items = []
    if items and items[0].get("hasCaption"):
        full, segments = _tiktok_transcript_segments(items[0])
        if full:
            return full, segments, safe_str(items[0].get("language"))

    try:
        items = await apify.run_actor_sync(
            settings.APIFY_ACTOR_TIKTOK_TRANSCRIPT,
            {"postUrls": [url], "useWhisperFallback": True},
            max_items=1,
        )
    except Exception:  # noqa: BLE001
        items = []
    if items:
        full, segments = _tiktok_transcript_segments(items[0])
        if full:
            return full, segments, safe_str(items[0].get("languageCode"))

    # Confirm the video exists to give an accurate 404 vs 422. The base
    # scraper's `text` field is the post CAPTION, not speech, so it is
    # deliberately NOT returned as a transcript.
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_TIKTOK,
        {"postURLs": [url], "resultsPerPage": 1, "shouldDownloadSubtitles": True},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Video not found")
    raise HTTPException(status_code=422, detail="No speech/captions available for this TikTok")


@router.get("/transcript", summary="TikTok video transcript (via auto-captions)")
async def tiktok_transcript(
    url: str = Query(...),
    language: str | None = Query(
        None,
        description="Optional ISO-639-1 hint (e.g. 'tr') to pin the speech language",
        max_length=8,
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_tiktok_video_url(url)
    lang = (language or "").strip().lower() or None
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/transcript",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            full, segments, detected = await _fetch_tiktok_transcript(url, language=lang)
            return {
                "platform": "tiktok",
                "url": url,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
                "language": normalize_language_code(detected),
            }

        data = await cached_or_run(
            endpoint="tiktok.transcript",
            params={"url": url, "language": lang, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/summarize", summary="AI summary of a TikTok video")
async def tiktok_summarize(
    url: str = Query(...),
    language: str | None = Query(
        None,
        description="Optional ISO-639-1 code (e.g. 'tr'): pins the speech language and sets the summary output language",
        max_length=8,
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_tiktok_video_url(url)
    lang = (language or "").strip().lower() or None
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/summarize",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            text, _segments, _detected = await _fetch_tiktok_transcript(url, language=lang)
            ai = await summarize_transcript(text, language=lang or "en")
            return {
                "platform": "tiktok",
                "url": url,
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
            }

        data = await cached_or_run(
            endpoint="tiktok.summarize",
            params={"url": url, "language": lang, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Comments on a TikTok video (text, author, likes, timestamp) with cursor pagination")
async def tiktok_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    cursor: str | None = Query(
        None,
        description="Leave empty for the first page; then pass the nextCursor value returned in the previous response (a numeric offset, e.g. 50).",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    aweme_id = _require_tiktok_video_url(url)
    if cursor is not None and not cursor.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    settings = get_settings()
    # Flat fee: comments are served natively from TikTok's own API (our cost is
    # ~$0), so a single low charge covers any page size instead of per-result.
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/comments",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_COMMENTS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: TikTok's own cursor-paginated mobile comment API (no actor
            # cost). Falls back to the Apify actor if every proxy IP is blocked.
            native = await tiktok_native.comments_native(aweme_id, cursor, limit)
            if native is not None:
                comments, next_cursor, total = native
                ctx["source"] = "direct"
                payload = {
                    "platform": "tiktok",
                    "url": url,
                    "totalComments": total,
                    "totalReturned": len(comments),
                    "comments": comments,
                    "nextCursor": next_cursor,
                }
                return {k: v for k, v in payload.items() if v is not None}

            # The Apify actor is not cursor-based, so it only serves the first
            # page; deeper pages require the native path above.
            if cursor:
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch the next page. Retry shortly.",
                )
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_COMMENTS,
                {"postURLs": [url], "commentsPerPost": limit},
                max_items=limit,
            )
            ctx["source"] = "apify"
            comments = []
            for c in items[:limit]:
                user = c.get("user") or {}
                comments.append(
                    {
                        "id": safe_str(c.get("cid") or c.get("id")),
                        "text": (c.get("text") or "").strip(),
                        "author": safe_str(c.get("uniqueId") or user.get("uniqueId") or c.get("authorName")),
                        "authorAvatarUrl": safe_str(c.get("avatarThumbnail") or user.get("avatarThumb")),
                        "likeCount": safe_int(c.get("diggCount") or c.get("likeCount")) or 0,
                        "publishedAt": safe_str(c.get("createTimeISO")),
                    }
                )
            return {
                "platform": "tiktok",
                "url": url,
                "totalReturned": len(comments),
                "comments": comments,
                "nextCursor": None,
            }

        data = await cached_or_run(
            endpoint="tiktok.comments",
            params={"url": url, "limit": limit, "cursor": cursor or "", "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/channel-details", summary="TikTok profile / channel info")
async def tiktok_channel_details(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/channel-details",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_CHANNEL_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: parse the profile page's embedded JSON (no actor cost).
            native = await channel_details_native(handle, url)
            if native is not None and native.get("followers") is not None:
                ctx["source"] = "direct"
                return native

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_PROFILE,
                {"profiles": [handle], "resultsPerPage": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Profile not found")
            ctx["source"] = "apify"
            p = items[0]
            # The profile scraper emits video items with the profile nested
            # under `authorMeta`; older actor versions exposed it at top level.
            a = p.get("authorMeta") or p
            stats = p.get("authorStats") or p.get("stats") or {}
            bio_link = a.get("bioLink")
            if isinstance(bio_link, dict):
                bio_link = bio_link.get("link")
            return {
                "platform": "tiktok",
                "url": safe_str(a.get("profileUrl")) or url,
                "username": safe_str(a.get("name") or a.get("uniqueId") or handle),
                "displayName": safe_str(a.get("nickName") or a.get("nickname")),
                "bio": safe_str(a.get("signature") or a.get("bio")),
                "followers": safe_int(a.get("fans") or stats.get("followerCount")),
                "following": safe_int(a.get("following") or stats.get("followingCount")),
                "likes": safe_int(a.get("heart") or stats.get("heartCount")),
                "postCount": safe_int(a.get("video") or stats.get("videoCount")),
                "verified": a.get("verified"),
                "private": a.get("privateAccount"),
                "profileImage": safe_str(a.get("avatar") or a.get("avatarLarger") or a.get("originalAvatarUrl")),
                "externalUrl": safe_str(bio_link),
                "category": safe_str((a.get("commerceUserInfo") or {}).get("category")),
            }

        data = await cached_or_run(
            endpoint="tiktok.channel-details",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _tally_locations(codes: list[str]) -> list[dict[str, Any]]:
    """Turn a list of ISO country codes (with duplicates) into a sorted
    audience-location breakdown: ``[{country, countryCode, count, percentage}]``."""
    counts = Counter(codes)
    total = sum(counts.values())
    if not total:
        return []
    out: list[dict[str, Any]] = []
    for code, n in counts.most_common():
        out.append(
            {
                "country": country_name(code),
                "countryCode": code,
                "count": n,
                "percentage": f"{n / total * 100:.2f}%",
            }
        )
    return out


async def _fetch_audience_locations(
    handle: str, settings: Any, *, video_sample: int, target_total: int
) -> tuple[list[dict[str, Any]], int]:
    """Sample commenter countries across a creator's recent videos.

    Video IDs come from the profile actor (TikTok gates the post list behind
    signed params), then commenter ``region`` codes are pulled natively from
    TikTok's own comment API and tallied. Returns ``(audienceLocations,
    videosSampled)``; ``audienceLocations`` is empty when comments are blocked.
    """
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_TIKTOK,
        {"profiles": [handle], "resultsPerPage": video_sample, "shouldDownloadVideos": False},
        max_items=video_sample,
    )
    aweme_ids = [safe_str(i.get("id") or i.get("videoId")) for i in (items or [])]
    aweme_ids = [a for a in aweme_ids if a]
    if not aweme_ids:
        return [], 0
    codes = await audience_regions_native(aweme_ids, target_total=target_total)
    return _tally_locations(codes or []), len(aweme_ids)


async def _resolve_region(data: dict[str, Any]) -> None:
    """Populate ``region`` with the best available country signal.

    TikTok almost never exposes an account's ``region`` on any public surface,
    so when it's missing we fill ``region`` with a gpt-4o-mini guess of the
    creator's likely country from public cues (bio, display name, language).
    ``regionSource`` records where the value came from ("tiktok" when authoritative,
    "inferred" when estimated) and ``regionConfidence`` grades the estimate.
    """
    if data.get("region"):
        data["regionConfidence"] = None
        data["regionSource"] = "tiktok"
        return
    raw = data.get("raw") or {}
    user = raw.get("user") or raw.get("authorMeta") or {}
    bio = safe_str(user.get("signature"))
    est = await infer_region(
        username=data.get("username"),
        display_name=data.get("displayName"),
        bio=bio,
        language=data.get("language"),
    )
    data["region"] = (est or {}).get("region")
    data["regionConfidence"] = (est or {}).get("confidence")
    data["regionSource"] = "inferred"


@router.get("/profile-region", summary="TikTok creator region, language & core stats")
async def tiktok_profile_region(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/profile-region",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/@{handle}",
        base_credits=CREDIT_PROFILE_REGION,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: profile page JSON. Returns None when it exposes neither
            # region nor language, in which case the actor's caption-language
            # sampling is still worth the cost.
            native = await profile_region_native(handle)
            if native is not None:
                ctx["source"] = "direct"
                base = native
            else:
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_TIKTOK_PROFILE,
                    {"profiles": [handle], "resultsPerPage": 1},
                    max_items=1,
                )
                if not items:
                    raise HTTPException(status_code=404, detail="Profile not found")
                ctx["source"] = "apify"
                base = _normalize_profile_region(items[0], handle)

            await _resolve_region(base)
            return base

        data = await cached_or_run(
            endpoint="tiktok.profile-region",
            params={"handle": handle, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/live", summary="TikTok live status + room info for a creator")
async def tiktok_live(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/live",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/@{handle}/live",
        base_credits=CREDIT_CHANNEL_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_LIVE,
                {"handles": [handle], "include_stream_urls": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Creator not found")
            item = items[0]
            if item.get("error"):
                raise HTTPException(status_code=404, detail="Creator not found")
            user = item.get("liveRoomUserInfo") or {}
            room = item.get("liveRoom") or {}
            return {
                "platform": "tiktok",
                "username": safe_str(user.get("uniqueId") or handle),
                "isLive": bool(item.get("is_live")),
                "creator": {
                    "displayName": safe_str(user.get("nickname")),
                    "followers": safe_int(user.get("followerCount")),
                    "verified": user.get("verified"),
                    "avatar": safe_str(user.get("avatarUrl") or user.get("avatarThumb")),
                    "bio": safe_str(user.get("signature")),
                },
                "room": {
                    "id": safe_str(item.get("roomId") or room.get("room_id")),
                    "title": safe_str(room.get("title")),
                    "startedAt": safe_str(room.get("started_at")),
                    "viewerCount": safe_int(room.get("viewer_count")),
                    "totalEnterCount": safe_int(room.get("total_enter_count")),
                    "likeCount": safe_int(room.get("like_count")),
                    "coverUrl": safe_str(room.get("cover_url")),
                    "streamUrls": room.get("stream_urls"),
                },
            }

        data = await cached_or_run(
            endpoint="tiktok.live",
            params={"handle": handle, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/live-info", summary="TikTok live room info for a creator")
async def tiktok_live_info(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    # ScrapeCreators exposes both Live and Live Info. Our live endpoint already
    # returns status plus full room details, so this route is an explicit alias
    # with its own billing/cache key for compatibility.
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/live-info",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/@{handle}/live",
        base_credits=7,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_LIVE,
                {"handles": [handle], "include_stream_urls": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Creator not found")
            item = items[0]
            if item.get("error"):
                raise HTTPException(status_code=404, detail="Creator not found")
            user = item.get("liveRoomUserInfo") or {}
            room = item.get("liveRoom") or {}
            return {
                "platform": "tiktok",
                "username": safe_str(user.get("uniqueId") or handle),
                "isLive": bool(item.get("is_live")),
                "room": room,
                "creator": user,
                "streamUrls": item.get("stream_urls") or item.get("streamUrls") or [],
                "raw": item,
            }

        data = await cached_or_run(
            endpoint="tiktok.live-info",
            params={"handle": handle, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/search-suggestions", summary="TikTok search/autocomplete suggestions")
async def tiktok_search_suggestions(
    q: str = Query(..., min_length=1, description="Seed keyword to expand into autocomplete suggestions, e.g. skincare."),
    country: str = Query("US", min_length=2, max_length=2, description="Two-letter ISO country code that localizes the suggestions to a market, e.g. US, GB, DE. Default US."),
    language: str = Query("en-US", description="Interface language for the suggestions, e.g. en-US or de-DE. Default en-US."),
    limit: int = Query(20, ge=1, le=100, description="Upper bound on how many suggestions to return (1-100, default 20). TikTok only surfaces a limited number of real autocomplete suggestions per keyword, so you'll often get fewer than the limit."),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_TREND_MARGIN, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/search-suggestions",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_SEARCH_SUGGESTIONS,
                {
                    "keywords": [q],
                    "maxSuggestionsPerKeyword": limit,
                    "region": country.upper(),
                    "language": language,
                    "includeAlphabetExpansions": False,
                },
                max_items=limit,
            )
            suggestions = [
                s for s in (_normalize_suggestion(i, q) for i in items[:limit])
                if s.get("suggestion")
            ]
            for idx, s in enumerate(suggestions, start=1):
                if s.get("rank") is None:
                    s["rank"] = idx
            return {"platform": "tiktok", "query": q, "totalReturned": len(suggestions), "suggestions": suggestions}

        data = await cached_or_run(
            endpoint="tiktok.search-suggestions",
            params={"q": q, "country": country.upper(), "language": language, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["suggestions"]), RATE_TREND_MARGIN, 2)
        return ApiResponse(data=data)


@router.get("/popular-creators", summary="Popular TikTok creators by country")
async def tiktok_popular_creators(
    country: str = Query("US", min_length=2, max_length=2),
    sort: str = Query("follower", pattern="^(follower|engagement|popularity)$"),
    follower_count: str | None = Query(None, description="Optional range: 10k-100k, 100k-1m, 1m-10m, >10m"),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_TREND_MARGIN, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/popular-creators",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Creative Center trends actor: only trendType/countryCode/maxResults
            # are supported; sort/follower filters apply to fallback actors only.
            run_input: dict[str, Any] = {
                "trendType": "creator",
                "countryCode": country.upper(),
                "maxResults": limit,
            }
            fallback_input: dict[str, Any] = {
                "creator_country": country.upper(),
                "sort_by": "avg_views" if sort == "popularity" else sort,
                "maxResults": limit,
                "limit": min(limit, 50),
            }
            if follower_count:
                range_map = {"10k-100k": "1", "100k-1m": "2", "1m-10m": "3", ">10m": "4"}
                fallback_input["audience_count"] = range_map.get(follower_count.lower(), follower_count)
            items, _actor = await get_apify().run_with_fallback(
                [
                    (settings.APIFY_ACTOR_TIKTOK_POPULAR_CREATORS, run_input),
                    (settings.APIFY_ACTOR_TIKTOK_POPULAR_CREATORS_FALLBACK, fallback_input),
                ],
                max_items=limit,
            )
            creators = [_normalize_creator(i) for i in items[:limit]]
            return {
                "platform": "tiktok",
                "country": country.upper(),
                "sort": sort,
                "totalReturned": len(creators),
                "creators": creators,
            }

        data = await cached_or_run(
            endpoint="tiktok.popular-creators",
            params={"country": country.upper(), "sort": sort, "follower_count": follower_count or "", "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["creators"]), RATE_TREND_MARGIN, 2)
        return ApiResponse(data=data)


@router.get("/audience-demographics", summary="TikTok audience countries (by engaged commenters)")
async def tiktok_audience_demographics(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/audience-demographics",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/@{handle}",
        base_credits=CREDIT_AUDIENCE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # TikTok never publishes follower geography, but every commenter's
            # country IS exposed on its own comment API. Sampling commenters
            # across the creator's recent videos yields an engagement-based
            # audience-country breakdown — computed natively, no audience actor.
            locations, videos_sampled = await _fetch_audience_locations(
                handle, settings,
                video_sample=AUDIENCE_VIDEO_SAMPLE,
                target_total=AUDIENCE_TARGET_TOTAL,
            )
            if videos_sampled == 0:
                raise HTTPException(status_code=404, detail="Profile not found or has no public videos")
            ctx["source"] = "direct"
            return {
                "platform": "tiktok",
                "username": handle,
                "url": f"https://www.tiktok.com/@{handle}",
                "videosSampled": videos_sampled,
                "sampleSize": sum(loc["count"] for loc in locations),
                "audienceLocations": locations,
            }

        data = await cached_or_run(
            endpoint="tiktok.audience-demographics",
            params={"handle": handle, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/channel-posts",
    summary="Latest videos from a TikTok profile",
    description=(
        "Returns a creator's most recent public videos as structured JSON — "
        "caption, engagement (views/likes/comments/shares/saves), thumbnail, "
        "hashtags, sound name, and author profile. Accepts a profile URL, "
        "@handle, or username. Newest first; billed per post returned."
    ),
)
async def tiktok_channel_posts(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    limit: int = Query(20, ge=1, le=200, description="How many latest videos to return (1–200). Newest first. Billed per result."),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_CHANNEL_POSTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/channel-posts",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {"profiles": [handle], "resultsPerPage": limit, "shouldDownloadVideos": False},
                max_items=limit,
            )
            posts = [_normalize(i) for i in items[:limit]]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="tiktok.channel-posts",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_CHANNEL_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/comment-replies", summary="Replies to a TikTok comment")
async def tiktok_comment_replies(
    url: str = Query(..., description="URL of the TikTok video the comment belongs to"),
    comment_id: str = Query(..., description="ID of the parent comment"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_tiktok_video_url(url)
    settings = get_settings()
    # Worst-case crawl is REPLIES_MAX_ITEMS rows; pre-authorize that so we never
    # do paid work the caller can't afford. Actual charge is set from the real
    # number of rows crawled (see credits_override below).
    cost = max(CREDIT_REPLIES_MIN, _scaled_credits(REPLIES_MAX_ITEMS, RATE_REPLIES_ROW, CREDIT_REPLIES_MIN))
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/comment-replies",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        crawled = 0

        async def _run() -> dict[str, Any]:
            nonlocal crawled
            apify = get_apify()
            fast_input = {
                "videoUrls": [url],
                "maxCommentsPerVideo": REPLIES_MAX_COMMENTS,
                "includeReplies": True,
                "maxRepliesPerComment": min(limit, 500),
            }
            legacy_input = {
                "videoUrls": [url],
                "maxComments": REPLIES_MAX_COMMENTS,
                "includeReplies": True,
                "maxRepliesPerComment": min(limit, 500),
                "includeAuthorInfo": True,
                "sort": "top",
                "proxyConfiguration": TIKTOK_RESIDENTIAL_PROXY,
            }
            items, _actor = await apify.run_with_fallback(
                [
                    (settings.APIFY_ACTOR_TIKTOK_COMMENT_REPLIES_FAST, fast_input),
                    (settings.APIFY_ACTOR_TIKTOK_COMMENT_REPLIES, legacy_input),
                ],
                max_items=REPLIES_MAX_ITEMS,
            )
            crawled = len(items)
            replies = []
            for r in items:
                # Reply rows can use different parent id names depending on
                # the actor. Some actors nest replies on the parent comment.
                parent_id = safe_str(
                    r.get("parentCommentId")
                    or r.get("parentId")
                    or r.get("repliesToId")
                    or r.get("replyToCommentId")
                )
                if parent_id != comment_id:
                    nested = r.get("replies") or r.get("_replies") or []
                    if isinstance(nested, list) and safe_str(r.get("id") or r.get("cid")) == comment_id:
                        for child in nested:
                            replies.append(
                                {
                                    "id": safe_str(child.get("replyId") or child.get("cid") or child.get("id")),
                                    "text": (child.get("replyText") or child.get("text") or child.get("body") or "").strip(),
                                    "author": safe_str(child.get("replyAuthorUsername") or child.get("author") or child.get("uniqueId")),
                                    "authorName": safe_str(child.get("replyAuthorNickname") or child.get("authorName") or child.get("nickname")),
                                    "likeCount": safe_int(child.get("replyLikeCount") or child.get("likeCount") or child.get("likes")),
                                    "publishedAt": safe_str(child.get("replyCreateTime") or child.get("createdAt") or child.get("createTimeISO")),
                                    "verified": child.get("replyAuthorVerified") or child.get("verified"),
                                    "profileImage": safe_str(child.get("replyAuthorAvatar") or child.get("avatar")),
                                }
                            )
                            if len(replies) >= limit:
                                break
                    continue
                replies.append(
                    {
                        # automation-lab rows: `authorId` is the @username and
                        # `author` is the display name.
                        "id": safe_str(r.get("replyId") or r.get("cid") or r.get("id")),
                        "text": (r.get("replyText") or r.get("text") or r.get("body") or "").strip(),
                        "author": safe_str(r.get("replyAuthorUsername") or r.get("uniqueId") or r.get("authorId") or r.get("author")),
                        "authorName": safe_str(r.get("replyAuthorNickname") or r.get("authorName") or r.get("nickname") or r.get("author")),
                        "likeCount": safe_int(r.get("replyLikeCount") or r.get("likeCount") or r.get("likes")) or 0,
                        "publishedAt": safe_str(r.get("replyCreateTime") or r.get("createdAt") or r.get("createTimeISO")),
                        "verified": r.get("replyAuthorVerified") or r.get("verified"),
                        "profileImage": safe_str(r.get("replyAuthorAvatar") or r.get("avatar") or r.get("authorAvatarUrl")),
                    }
                )
                if len(replies) >= limit:
                    break
            return {
                "platform": "tiktok",
                "url": url,
                "commentId": comment_id,
                "totalReturned": len(replies),
                "replies": replies,
            }

        data = await cached_or_run(
            endpoint="tiktok.comment-replies",
            params={"url": url, "comment_id": comment_id, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        # Bill on the actual rows crawled (what Apify charged us for), not the
        # filtered reply count. On a cache hit this is ignored (cache_hit -> 0).
        ctx["credits_override"] = max(
            CREDIT_REPLIES_MIN, _scaled_credits(crawled, RATE_REPLIES_ROW, CREDIT_REPLIES_MIN)
        )
        return ApiResponse(data=data)


@router.get("/user-followers", summary="List a TikTok user's followers")
async def tiktok_user_followers(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FOLLOWERS, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/user-followers",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_FOLLOWERS,
                {
                    "profiles": [handle],
                    "maxFollowersPerProfile": limit,
                    "maxFollowingPerProfile": 0,
                },
                max_items=limit,
            )
            users = [
                _normalize_connection(i)
                for i in items
                if i.get("connectionType") == "follower"
            ][:limit]
            return {"url": url, "totalReturned": len(users), "followers": users}

        data = await cached_or_run(
            endpoint="tiktok.user-followers",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["followers"]), RATE_FOLLOWERS, 5)
        return ApiResponse(data=data)


@router.get("/user-followings", summary="List who a TikTok user follows")
async def tiktok_user_followings(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FOLLOWERS, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/user-followings",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_FOLLOWINGS,
                {
                    "profiles": [handle],
                    "maxFollowersPerProfile": 0,
                    "maxFollowingPerProfile": limit,
                },
                max_items=limit,
            )
            users = [
                _normalize_connection(i)
                for i in items
                if i.get("connectionType") == "following"
            ][:limit]
            return {"url": url, "totalReturned": len(users), "followings": users}

        data = await cached_or_run(
            endpoint="tiktok.user-followings",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["followings"]), RATE_FOLLOWERS, 5)
        return ApiResponse(data=data)


@router.get("/music-posts", summary="Posts using a TikTok sound/music")
async def tiktok_music_posts(
    url: str = Query(..., description="TikTok music/sound URL"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_MUSIC_POSTS, 3)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/music-posts",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items, _actor = await apify.run_with_fallback(
                _tiktok_music_candidates(settings, url, limit),
                max_items=limit,
            )
            posts = [_normalize_music_post(i) for i in items[:limit]]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="tiktok.music-posts",
            params={"url": url, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_MUSIC_POSTS, 3)
        return ApiResponse(data=data)


@router.get("/top-search", summary="Top mixed TikTok search results for a keyword")
async def tiktok_top_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_CHANNEL_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/top-search",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {"searchQueries": [q], "searchSection": "", "resultsPerPage": limit},
                max_items=limit,
            )
            results = [_normalize(i) for i in items[:limit]]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="tiktok.top-search",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_CHANNEL_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


@router.get("/search/hashtag", summary="Search TikTok videos by hashtag")
async def tiktok_search_by_hashtag(
    q: str = Query(..., min_length=2, description="Hashtag to search for (with or without the leading #)."),
    limit: int = Query(20, ge=1, le=100, description="Number of videos to return per page."),
    cursor: int = Query(
        0,
        ge=0,
        description="Pagination offset. Pass the `nextCursor` from the previous response to fetch the next page.",
    ),
    region: str = Query(
        "US",
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country the scraping proxy is routed through. This only sets the proxy location — it does not restrict results to that country.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    region_code = region.strip().upper()
    cost = _scaled_credits(limit, RATE_CHANNEL_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/search/hashtag",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            # The actor always starts from the top of the hashtag feed, so we
            # fetch cursor+limit rows and slice the requested page. hasMore is
            # true when the actor still had rows beyond this page.
            want = cursor + limit
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {
                    "hashtags": [q.lstrip("#")],
                    "resultsPerPage": want,
                    "shouldDownloadVideos": False,
                    "proxyConfiguration": {"useApifyProxy": True, "apifyProxyCountry": region_code},
                },
                max_items=want,
            )
            page = items[cursor : cursor + limit]
            results = [_normalize(i) for i in page]
            has_more = len(items) > cursor + limit
            return {
                "query": q,
                "totalReturned": len(results),
                "hasMore": has_more,
                "nextCursor": (cursor + limit) if has_more else None,
                "results": results,
            }

        data = await cached_or_run(
            endpoint="tiktok.search-hashtag",
            params={"q": q, "limit": limit, "cursor": cursor, "region": region_code, "v": 1},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_CHANNEL_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


@router.get("/search/users", summary="Search TikTok users by keyword")
async def tiktok_search_users(
    q: str = Query(..., min_length=2, description="Search query matched against usernames, display names and bios."),
    limit: int = Query(20, ge=1, le=100, description="Number of users to return per page."),
    cursor: int = Query(
        0,
        ge=0,
        description="Pagination offset. Pass the `nextCursor` from the previous response to fetch the next page.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_USER_SEARCH, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/search/users",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            want = cursor + limit
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {
                    "searchQueries": [q],
                    "searchSection": "/user",
                    "maxProfilesPerQuery": want,
                    "resultsPerPage": want,
                },
                max_items=want,
            )
            page = items[cursor : cursor + limit]
            users = [_normalize_user(i) for i in page]
            has_more = len(items) > cursor + limit
            return {
                "query": q,
                "totalReturned": len(users),
                "hasMore": has_more,
                "nextCursor": (cursor + limit) if has_more else None,
                "users": users,
            }

        data = await cached_or_run(
            endpoint="tiktok.search-users",
            params={"q": q, "limit": limit, "cursor": cursor, "v": 1},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["users"]), RATE_USER_SEARCH, 5)
        return ApiResponse(data=data)


@router.get("/song-details", summary="Details of a TikTok sound/song")
async def tiktok_song_details(
    url: str = Query(..., description="TikTok music/sound URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/song-details",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_VIDEO_DETAILS + 1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            # The TikTok music URL ends with the numeric sound id; parse it here
            # because apidojo returns the id as a JS number (precision loss).
            m = re.search(r"(\d{6,})(?:\?|$)", url)
            url_id = m.group(1) if m else None

            # Fast path: apidojo music scraper (~9s, has duration + cover).
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_TIKTOK_SONG,
                    {"startUrls": [url], "maxItems": 1},
                    max_items=1,
                )
            except Exception:  # noqa: BLE001
                items = []
            if items:
                song = items[0].get("song") or {}
                if song:
                    title = safe_str(song.get("title"))
                    return {
                        "platform": "tiktok",
                        "url": url,
                        "id": url_id or safe_str(song.get("id")),
                        "title": title,
                        "author": safe_str(song.get("artist")),
                        "original": bool(title) and title.lower().startswith("original sound"),
                        "album": safe_str(song.get("album")),
                        "duration": safe_float(song.get("duration")),
                        "coverUrl": safe_str(song.get("cover")),
                        "playUrl": None,
                    }

            # apidojo failed: the remaining fallbacks are independent actors, so
            # race them concurrently instead of cascading (worst case used to be
            # 3 more sequential actor runs). Costs one possibly-redundant run
            # only on this already-failing path.
            async def _summary_fallback() -> dict[str, Any] | None:
                # Summary-only sound scraper: no video crawling.
                try:
                    summary_items = await apify.run_actor_sync(
                        settings.APIFY_ACTOR_TIKTOK_SONG_FAST_FALLBACK,
                        {
                            "sounds": [url_id or url],
                            # The actor rejects 0 ("must be >= 1"), so ask for
                            # the minimum even though we only want the summary.
                            "maxVideosPerSound": 1,
                            "includeSoundSummary": True,
                            "includeVideoFields": False,
                        },
                        max_items=1,
                    )
                except Exception:  # noqa: BLE001
                    return None
                if not summary_items:
                    return None
                item = summary_items[0]
                music = item.get("sound") or item.get("music") or item.get("summary") or item
                title = safe_str(music.get("title") or music.get("musicName") or music.get("name"))
                if not title:
                    return None
                return {
                    "platform": "tiktok",
                    "url": url,
                    "id": url_id or safe_str(music.get("id") or music.get("musicId") or music.get("soundId")),
                    "title": title,
                    "author": safe_str(music.get("artist") or music.get("authorName") or music.get("author")),
                    "original": bool(title) and title.lower().startswith("original sound"),
                    "album": safe_str(music.get("album")),
                    "duration": safe_float(music.get("duration") or music.get("durationSeconds")),
                    "coverUrl": safe_str(music.get("cover") or music.get("coverUrl") or music.get("coverLarge")),
                    "playUrl": safe_str(music.get("playUrl") or music.get("audioUrl")),
                }

            async def _clockworks_fallback() -> dict[str, Any] | None:
                # Clockworks sound scraper (slower, exposes playUrl).
                try:
                    items, _actor = await apify.run_with_fallback(
                        [
                            (
                                settings.APIFY_ACTOR_TIKTOK_MUSIC,
                                {
                                    "sounds": [url_id or url],
                                    "maxVideosPerSound": 1,
                                    "includeSoundSummary": True,
                                    "includeVideoFields": False,
                                },
                            ),
                            (
                                settings.APIFY_ACTOR_TIKTOK_MUSIC_FALLBACK,
                                {"musics": [url], "resultsPerPage": 1, "shouldDownloadVideos": False},
                            ),
                        ],
                        max_items=1,
                    )
                except Exception:  # noqa: BLE001
                    return None
                if not items:
                    return None
                music = (
                    items[0].get("musicMeta")
                    or items[0].get("music")
                    or items[0].get("sound")
                    or items[0].get("summary")
                    or items[0]
                )
                return {
                    "platform": "tiktok",
                    "url": url,
                    "id": url_id or safe_str(music.get("musicId") or music.get("soundId") or music.get("id")),
                    "title": safe_str(music.get("musicName") or music.get("title") or music.get("name")),
                    "author": safe_str(music.get("musicAuthor") or music.get("authorName") or music.get("artist") or music.get("author")),
                    "original": music.get("musicOriginal"),
                    "album": None,
                    "duration": safe_float(music.get("duration") or music.get("durationSeconds")),
                    "coverUrl": safe_str(
                        music.get("coverLarge") or music.get("coverMedium") or music.get("coverMediumUrl") or music.get("coverUrl") or music.get("cover")
                    ),
                    "playUrl": safe_str(music.get("playUrl") or music.get("audioUrl")),
                }

            summary_result, clockworks_result = await asyncio.gather(
                _summary_fallback(), _clockworks_fallback()
            )
            result = summary_result or clockworks_result
            if not result:
                raise HTTPException(status_code=404, detail="Song not found")
            return result

        data = await cached_or_run(
            endpoint="tiktok.song-details",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _normalize_trend_video(v: dict) -> dict:
    """Map an xtracto trending video row (TikTok Explore API shape).

    Rows look like ``{id, desc, author:{uniqueId,nickname}, stats:{...},
    video:{cover,playAddr}, _rank}`` — close to the clockworks shape but with
    no top-level webVideoUrl, so we build the URL from author + id.
    """
    author = v.get("author") or {}
    stats = v.get("stats") or {}
    video = v.get("video") or {}
    uid = author.get("uniqueId") or author.get("unique_id")
    vid = v.get("id") or v.get("videoId")
    url = v.get("webVideoUrl") or v.get("url")
    if not url and uid and vid:
        url = f"https://www.tiktok.com/@{uid}/video/{vid}"
    return {
        "url": safe_str(url),
        "id": safe_str(vid),
        "title": safe_str(v.get("desc") or v.get("title") or v.get("text")),
        "coverUrl": safe_str(video.get("cover") or v.get("cover")),
        "author": safe_str(uid),
        "authorName": safe_str(author.get("nickname") or author.get("nickName")),
        "views": safe_int(stats.get("playCount") or v.get("playCount")),
        "likes": safe_int(stats.get("diggCount") or v.get("diggCount")),
        "comments": safe_int(stats.get("commentCount") or v.get("commentCount")),
        "shares": safe_int(stats.get("shareCount") or v.get("shareCount")),
        "rank": safe_int(v.get("_rank") or v.get("rank")),
    }


@router.get("/trending-feed", summary="TikTok trending (For You) videos by region")
async def tiktok_trending_feed(
    country: str = Query("US", min_length=2, max_length=2, description="ISO country code"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_TREND, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/trending-feed",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_TRENDING,
                {"content_type": "video", "country_code": country.upper(), "limit": limit},
                max_items=limit,
            )
            results = [_normalize_trend_video(v) for v in items[:limit]]
            return {"country": country.upper(), "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="tiktok.trending-feed",
            params={"country": country.upper(), "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_TREND, CREDIT_SEARCH)
        return ApiResponse(data=data)


@router.get("/popular-hashtags", summary="Trending TikTok hashtags for a topic/keyword")
async def tiktok_popular_hashtags(
    query: str = Query("trending", min_length=1, description="Topic or keyword to discover trending hashtags for"),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    # Apify cost is driven by the number of videos fetched, not returned tags.
    n_videos = max(limit, 25)
    cost = _scaled_credits(n_videos, RATE_TREND, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/popular-hashtags",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            # The keyword is used as a seed hashtag (coregent's search mode is
            # unreliable, but hashtag pages are solid). We then aggregate the
            # co-occurring hashtags on those videos and rank them by frequency
            # + total plays to surface related/trending hashtags.
            seed = query.lstrip("#").strip()
            items, _actor = await apify.run_with_fallback(
                [
                    (
                        settings.APIFY_ACTOR_TIKTOK_TREND_DISCOVERY,
                        {
                            "searchQueries": [],
                            "hashtags": [seed],
                            "resultsPerQuery": n_videos,
                            "includeVideos": True,
                            "includeHashtags": False,
                            "sortBy": "popular",
                            "proxyConfiguration": {"useApifyProxy": True},
                        },
                    ),
                    (
                        settings.APIFY_ACTOR_TIKTOK,
                        {"hashtags": [seed], "resultsPerPage": n_videos, "shouldDownloadVideos": False},
                    ),
                ],
                max_items=n_videos,
            )
            agg: dict[str, dict[str, int]] = {}
            for v in items:
                if v.get("recordType") and v.get("recordType") != "video":
                    continue
                tags = v.get("hashtags") or v.get("challenges")
                if not isinstance(tags, list):
                    tags = []
                stats = v.get("stats") or {}
                plays = safe_int(v.get("playCount") or stats.get("playCount")) or 0
                for t in tags:
                    name = safe_str(t.get("name") if isinstance(t, dict) else t)
                    if not name:
                        continue
                    name = name.lstrip("#").lower()
                    if not name:
                        continue
                    slot = agg.setdefault(name, {"count": 0, "plays": 0})
                    slot["count"] += 1
                    slot["plays"] += plays
            ranked = sorted(agg.items(), key=lambda kv: (kv[1]["count"], kv[1]["plays"]), reverse=True)
            hashtags = [
                {
                    "name": name,
                    "url": f"https://www.tiktok.com/tag/{name}",
                    "rank": i + 1,
                    "videoCount": slot["count"],
                    "totalPlays": slot["plays"],
                }
                for i, (name, slot) in enumerate(ranked[:limit])
            ]
            return {"query": query, "totalReturned": len(hashtags), "hashtags": hashtags}

        data = await cached_or_run(
            endpoint="tiktok.popular-hashtags",
            params={"query": query, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = cost
        return ApiResponse(data=data)
