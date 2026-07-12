"""Instagram endpoints (Reels, Posts, Profiles)."""

from __future__ import annotations

import json
import math
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyClient, ApifyError, get_apify
from app.services import instagram_decodo as decodo
from app.services import instagram_native
from app.services.cached_runner import cached_or_run
from app.services.openai_client import summarize_transcript, transcribe_video_url
from app.utils.formatters import safe_float, safe_int, safe_list, safe_str
from app.utils.url import (
    detect_url_platform,
    extract_instagram_shortcode,
    extract_instagram_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_TRANSCRIPT = 2
CREDIT_SUMMARIZE = 4
CREDIT_DETAILS = 1
CREDIT_CHANNEL = 1
CREDIT_SEARCH = 2
CREDIT_DOWNLOAD = 3

# Per-result rates calibrated to ~80% markup (rate = cost_per_result * 400 at a
# $0.0045/credit sell price) over verified Apify prices:
#   apify/instagram-scraper          $1.50/1k ($0.0015) -> posts/reels/search
#   apify/instagram-comment-scraper  $2.30/1k ($0.0023) -> comments
#   apify/instagram-tagged-scraper / reels-audio ~$0.0023 -> tagged / music
# Charged via ctx["credits_override"] on the actual item count.
RATE_IG_POSTS = 0.6
RATE_IG_RICH = 0.9
RATE_IG_MARGIN = 1.4


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    return max(minimum, math.ceil(n * rate))


def _reject_instagram_platform_mismatch(url: str, example: str) -> None:
    detected = detect_url_platform(url)
    if detected and detected != "instagram":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "instagram", example),
        )


def _require_instagram_post_url(url: str) -> str:
    shortcode = extract_instagram_shortcode(url)
    if not shortcode:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "instagram", "https://www.instagram.com/reel/SHORTCODE/"),
        )
    return shortcode


def _require_instagram_profile(value: str) -> str:
    handle = extract_instagram_username(value)
    if not handle:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "instagram", "https://www.instagram.com/username/"),
        )
    return handle


def _normalize_post(item: dict) -> dict:
    owner = item.get("owner") or {}
    author = item.get("ownerUsername") or owner.get("username")
    post_type = safe_str(item.get("type"))
    return {
        "platform": "instagram",
        "url": safe_str(item.get("url") or item.get("permalink") or item.get("shortcodeUrl")),
        "id": safe_str(item.get("id") or item.get("shortCode") or item.get("shortcode")),
        # "Image" | "Video" | "Sidecar" â€” video fields are null for images.
        "type": post_type,
        "productType": safe_str(item.get("productType")),
        "caption": safe_str(item.get("caption") or item.get("text") or item.get("description")),
        "description": safe_str(item.get("caption") or item.get("text") or item.get("description")),
        "publishedAt": safe_str(item.get("timestamp") or item.get("takenAt") or item.get("taken_at")),
        "durationSeconds": safe_float(item.get("videoDuration") or item.get("duration") or item.get("durationSeconds")),
        "thumbnailUrl": safe_str(item.get("displayUrl") or item.get("thumbnailUrl") or item.get("thumbnail")),
        "videoUrl": safe_str(item.get("videoUrl") or item.get("video_url") or item.get("downloadUrl")),
        "author": {
            "username": safe_str(author),
            "displayName": safe_str(item.get("ownerFullName") or owner.get("fullName") or owner.get("full_name")),
            "url": f"https://instagram.com/{author}" if author else None,
            "followers": safe_int(owner.get("followerCount") or owner.get("followersCount")),
            "verified": owner.get("isVerified") if owner.get("isVerified") is not None else owner.get("is_verified"),
            "profileImage": safe_str(owner.get("profilePicUrl") or owner.get("profile_pic_url")),
        },
        "engagement": {
            "views": safe_int(item.get("videoViewCount") or item.get("videoPlayCount")),
            "likes": safe_int(item.get("likesCount") or item.get("likeCount")) or 0,
            "comments": safe_int(item.get("commentsCount") or item.get("commentCount")) or 0,
        },
        "hashtags": safe_list(item.get("hashtags")),
        "mentions": safe_list(item.get("mentions")),
    }


def _dedupe_candidates(candidates: list[tuple[str, dict[str, Any]]]) -> list[tuple[str, dict[str, Any]]]:
    """Drop consecutive duplicate (actor, payload) pairs so a fallback that
    matches the primary doesn't burn a second identical run."""
    seen: set[str] = set()
    unique = []
    for actor, payload in candidates:
        key = f"{actor}:{json.dumps(payload, sort_keys=True, default=str)}"
        if key not in seen:
            seen.add(key)
            unique.append((actor, payload))
    return unique


async def _try_decodo(
    ctx: dict[str, Any],
    decodo_fn: Any,
    apify_fn: Any,
) -> Any:
    """Prefer Decodo when configured; fall back to Apify and stamp source."""
    if decodo.enabled():
        result = await decodo_fn()
        if result is not None:
            ctx["source"] = "direct"
            return result
    ctx["source"] = "apify"
    return await apify_fn()


def _instagram_profile_candidates(settings: Any, profile_url: str, limit: int, results_type: str) -> list[tuple[str, dict[str, Any]]]:
    payload = {"directUrls": [profile_url], "resultsLimit": limit, "resultsType": results_type}
    return _dedupe_candidates(
        [
            (settings.APIFY_ACTOR_INSTAGRAM, payload),
            (settings.APIFY_ACTOR_INSTAGRAM_FALLBACK, payload),
        ]
    )


def _instagram_reel_candidates(settings: Any, url: str, *, subtitles: bool = False) -> list[tuple[str, dict[str, Any]]]:
    payload: dict[str, Any] = {"directUrls": [url], "resultsLimit": 1}
    if subtitles:
        payload["shouldDownloadSubtitles"] = True
    return _dedupe_candidates(
        [
            (settings.APIFY_ACTOR_INSTAGRAM_REEL, payload),
            (settings.APIFY_ACTOR_INSTAGRAM_REEL_FALLBACK, payload),
        ]
    )


def _meta(page: str, key: str) -> str:
    patterns = [
        rf'<meta[^>]+property=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(key)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


async def _public_instagram_meta(url: str) -> dict[str, str] | None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
    }
    try:
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True, headers=headers) as client:
            resp = await client.get(url)
    except httpx.HTTPError:
        return None
    if resp.status_code >= 400:
        return None
    title = _meta(resp.text, "og:title")
    description = _meta(resp.text, "og:description")
    image = _meta(resp.text, "og:image")
    if not (title or description or image):
        return None
    return {"url": str(resp.url), "title": title, "description": description, "image": image}


def _transcript_from_item(item: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    raw_segments = (
        item.get("transcriptSegments")
        or item.get("segments")
        or item.get("subtitles")
        or item.get("captions")
        or []
    )
    segments: list[dict[str, Any]] = []
    parts: list[str] = []
    if isinstance(raw_segments, list):
        for seg in raw_segments:
            if isinstance(seg, dict):
                text = safe_str(seg.get("text") or seg.get("caption") or seg.get("sentence")).strip()
                start = safe_float(seg.get("start") or seg.get("startTime") or seg.get("startMs")) or 0
                duration = safe_float(seg.get("duration") or seg.get("dur")) or 0
                if not duration:
                    end = safe_float(seg.get("end")) or 0
                    duration = round(max(end - start, 0), 3)
            else:
                text = str(seg).strip()
                start = 0
                duration = 0
            if text:
                mm = int(start // 60)
                ss = int(start % 60)
                segments.append({"text": text, "start": start, "duration": duration, "timestamp": f"{mm:02d}:{ss:02d}"})
                parts.append(text)
    # Deliberately NOT falling back to item["text"]/item["caption"]: those are
    # the post caption, not speech. Returning them as "transcript" is wrong
    # (a talking reel would get its description back).
    full = (
        safe_str(item.get("transcript"))
        or safe_str(item.get("fullText"))
        or " ".join(parts)
        or ""
    ).strip()
    return full, segments


def _looks_like_caption(full: str, item: dict[str, Any]) -> bool:
    """True when an actor stuffed the post caption into its transcript field."""
    caption = (safe_str(item.get("caption") or item.get("text")) or "").strip()
    if not caption or not full:
        return False
    a = " ".join(full.lower().split())
    b = " ".join(caption.lower().split())
    return a == b or (len(a) > 40 and (a in b or b in a))


async def _fetch_instagram_transcript(
    url: str, language: str | None = None
) -> tuple[str, list[dict[str, Any]], str]:
    """Return (full transcript, segments, source).

    Primary: resolve the reel's MP4 natively (~1-2s, Apify scraper fallback)
    and Whisper-transcribe it ourselves. This always yields actual SPEECH,
    with timestamps, and is faster + cheaper than the transcript actors.
    Actors remain as a fallback, but their output is rejected when it merely
    echoes the post caption.

    `language` pins Whisper's language (ISO-639-1) instead of auto-detection.
    """
    settings = get_settings()
    apify = get_apify()

    async def _whisper(media_url: str) -> tuple[str, list[dict[str, Any]]] | None:
        """Whisper a media URL; None = fetch failed / too large (try next)."""
        try:
            tx = await transcribe_video_url(media_url, language=language)
        except Exception:  # noqa: BLE001
            return None
        if tx is None:
            return None
        full = (safe_str(tx.get("transcript")) or "").strip()
        if full:
            return full, tx.get("transcriptSegments") or []
        # Whisper ran fine and heard nothing -> genuinely no speech.
        raise HTTPException(status_code=422, detail="No speech found in this Reel")

    # Fast path: native GraphQL resolver gets the MP4 URL in ~1-2s.
    reel_item: dict[str, Any] | None = None
    native = await instagram_native.fetch_reel_media(_require_instagram_post_url(url))
    if native and safe_str(native.get("videoUrl")):
        result = await _whisper(safe_str(native.get("videoUrl")))
        if result:
            return result[0], result[1], "direct"

    # Decodo failed or the MP4 was too large for Whisper's 25 MB cap: the reel
    # scraper also exposes an audio-only track (~30x smaller), so long reels
    # still fit.
    try:
        items, _actor = await apify.run_with_fallback(
            _instagram_reel_candidates(settings, url), max_items=1
        )
    except Exception:  # noqa: BLE001
        items = []
    if items:
        reel_item = items[0]
        for key in ("audioUrl", "videoUrl", "video_url", "downloadUrl"):
            media_url = safe_str(reel_item.get(key))
            if not media_url:
                continue
            result = await _whisper(media_url)
            if result:
                return result[0], result[1], "openai"

    # Fallback: transcript actors (video URL could not be resolved/downloaded).
    try:
        items = await apify.run_actor_sync(
            settings.APIFY_ACTOR_INSTAGRAM_TRANSCRIPT,
            {
                "videoUrls": [url],
                "transcriptionMethod": settings.APIFY_INSTAGRAM_TRANSCRIPT_METHOD,
                "includeSegments": True,
            },
            max_items=1,
        )
    except Exception:  # noqa: BLE001
        items = []
    if items:
        full, segments = _transcript_from_item(items[0])
        if full and not _looks_like_caption(full, items[0]):
            return full, segments, "apify"

    try:
        items = await apify.run_actor_sync(
            settings.APIFY_ACTOR_INSTAGRAM_TRANSCRIPT_FAST,
            {"instagramUrl": url, "wordLevelTimestamps": False, "fastProcessing": True},
            max_items=1,
        )
    except Exception:  # noqa: BLE001
        items = []
    if items and safe_str(items[0].get("status")) != "error":
        full, segments = _transcript_from_item(items[0])
        if full and not _looks_like_caption(full, items[0]):
            return full, segments, "apify"

    if reel_item is None and native is None:
        raise HTTPException(status_code=404, detail="Reel not found")
    raise HTTPException(status_code=422, detail="No transcript available")


def _normalize_audio_reel(item: dict) -> dict:
    """Map the reels-by-audio scraper output (capitalized keys) to our shape."""
    author = item.get("author") or {}
    username = author.get("username")
    return {
        "platform": "instagram",
        "url": safe_str(item.get("URL") or item.get("url")),
        "id": safe_str(item.get("Id") or item.get("id")),
        "caption": safe_str(item.get("caption")),
        "description": safe_str(item.get("caption")),
        "publishedAt": safe_str(item.get("postedAt")),
        "durationSeconds": safe_float(item.get("videoDuration")),
        "thumbnailUrl": safe_str(author.get("temporaryProfilePictureUrl")),
        "videoUrl": safe_str(item.get("videoTemporaryUrl") or item.get("storedVideoUrl")),
        "author": {
            "username": safe_str(username),
            "displayName": safe_str(author.get("fullname")),
            "url": f"https://instagram.com/{username}" if username else None,
            "followers": None,
            "verified": author.get("isVerified"),
            "profileImage": safe_str(author.get("temporaryProfilePictureUrl")),
        },
        "engagement": {
            "views": safe_int(item.get("playCount")),
            "likes": safe_int(item.get("likeCount")),
            "comments": safe_int(item.get("commentCount")),
        },
        "musicId": safe_str(item.get("musicId")),
        "musicUrl": safe_str(item.get("musicUrl")),
    }


@router.get("/details", summary="Instagram post/reel details")
async def instagram_details(
    url: str = Query(..., description="Instagram post or reel URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_instagram_post_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/details",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: Instagram's own GraphQL (~3-4s, no actor cost). Same
            # upstream numbers as the actor; actor stays as fallback.
            shortcode = extract_instagram_shortcode(url)
            if shortcode:
                native = await instagram_native.fetch_post_details(shortcode)
                if native:
                    ctx["source"] = "direct"
                    return native

            apify = get_apify()
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM_POST,
                    {"directUrls": [url], "resultsLimit": 1},
                    max_items=1,
                )
            except (ApifyError, httpx.HTTPError):
                items = []
            if not items:
                meta = await _public_instagram_meta(url)
                if meta:
                    return {
                        "platform": "instagram",
                        "url": meta["url"] or url,
                        "id": extract_instagram_shortcode(url) or "",
                        "caption": meta["description"],
                        "description": meta["description"],
                        "publishedAt": "",
                        "durationSeconds": 0,
                        "thumbnailUrl": meta["image"],
                        "videoUrl": "",
                        "author": {"username": "", "displayName": meta["title"], "url": None, "verified": None, "profileImage": ""},
                        "engagement": {"likes": 0, "comments": 0},
                        "hashtags": [],
                    }
            if not items:
                raise HTTPException(status_code=404, detail="Post not found")
            ctx["source"] = "apify"
            data = _normalize_post(items[0])
            # Shape parity with the native result: `followers` isn't reliably
            # available on a post lookup and `views` is hidden for clips, so
            # neither is part of this endpoint (use channel-details for
            # followers).
            data["author"].pop("followers", None)
            data["engagement"].pop("views", None)
            return data

        data = await cached_or_run(
            endpoint="instagram.details",
            params={"url": url, "v": 8},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/transcript", summary="Instagram Reel transcript")
async def instagram_transcript(
    url: str = Query(...),
    language: str | None = Query(
        None,
        min_length=2,
        max_length=5,
        description=(
            "Optional ISO-639-1 language hint (e.g. 'tr', 'en'). Pins the "
            "transcription language instead of auto-detection; recommended "
            "for short clips with little speech."
        ),
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_instagram_post_url(url)
    settings = get_settings()
    lang = (language or "").strip().lower()[:2] or None
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/transcript",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            full, segments, source = await _fetch_instagram_transcript(url, language=lang)
            ctx["source"] = source
            return {
                "platform": "instagram",
                "url": url,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
            }

        data = await cached_or_run(
            endpoint="instagram.transcript",
            params={"url": url, "language": lang, "v": 8},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/summarize", summary="AI summary of Instagram Reel")
async def instagram_summarize(
    url: str = Query(...),
    language: str | None = Query(
        None,
        min_length=2,
        max_length=5,
        description=(
            "Optional ISO-639-1 code (e.g. 'tr'): pins the speech language "
            "and sets the summary output language."
        ),
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_instagram_post_url(url)
    lang = (language or "").strip().lower()[:2] or None
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/summarize",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            text, _segments, source = await _fetch_instagram_transcript(url, language=lang)
            ctx["source"] = source
            if not text:
                raise HTTPException(status_code=422, detail="No content to summarize")
            ai = await summarize_transcript(text, language=lang or "en")
            return {
                "platform": "instagram",
                "url": url,
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
            }

        data = await cached_or_run(
            endpoint="instagram.summarize",
            params={"url": url, "language": lang, "v": 8},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Instagram post/reel comments")
async def instagram_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_instagram_post_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_RICH, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/comments",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM_COMMENT,
                    {"directUrls": [url], "resultsLimit": limit},
                    max_items=limit,
                )
                comments = []
                for c in items[:limit]:
                    owner = c.get("owner") or {}
                    comments.append(
                        {
                            "id": safe_str(c.get("id")),
                            "url": safe_str(c.get("commentUrl")),
                            "text": (c.get("text") or "").strip(),
                            "author": safe_str(c.get("ownerUsername") or owner.get("username")),
                            "authorAvatarUrl": safe_str(c.get("ownerProfilePicUrl") or owner.get("profile_pic_url")),
                            "authorIsVerified": bool(owner.get("is_verified")),
                            "likeCount": safe_int(c.get("likesCount") or c.get("likeCount")) or 0,
                            "publishedAt": safe_str(c.get("timestamp")),
                            "replyCount": safe_int(c.get("replyCount") or c.get("repliesCount")) or 0,
                        }
                    )
                return {
                    "platform": "instagram",
                    "url": url,
                    "totalReturned": len(comments),
                    "comments": comments,
                }

            ctx["source"] = "apify"
            return await _apify()

        data = await cached_or_run(
            endpoint="instagram.comments",
            params={"url": url, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["comments"]), RATE_IG_RICH, 2)
        return ApiResponse(data=data)


@router.get("/channel-details", summary="Instagram profile info")
async def instagram_channel_details(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/channel-details",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_CHANNEL,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                try:
                    items = await apify.run_actor_sync(
                        settings.APIFY_ACTOR_INSTAGRAM_PROFILE,
                        {"usernames": [handle]},
                        max_items=1,
                    )
                except (ApifyError, httpx.HTTPError):
                    items = []
                if not items:
                    meta = await _public_instagram_meta(f"https://www.instagram.com/{handle}/")
                    if not meta:
                        raise HTTPException(status_code=404, detail="Profile not found")
                    return {
                        "platform": "instagram",
                        "url": meta["url"] or f"https://instagram.com/{handle}",
                        "username": handle,
                        "displayName": meta["title"],
                        "bio": meta["description"],
                        "followers": 0,
                        "following": 0,
                        "postCount": 0,
                        "verified": None,
                        "profileImage": meta["image"],
                        "externalUrl": "",
                    }
                p = items[0]
                return {
                    "platform": "instagram",
                    "url": f"https://instagram.com/{handle}",
                    "username": safe_str(p.get("username") or handle),
                    "displayName": safe_str(p.get("fullName")),
                    "bio": safe_str(p.get("biography")),
                    "followers": safe_int(p.get("followersCount")),
                    "following": safe_int(p.get("followsCount")),
                    "postCount": safe_int(p.get("postsCount")),
                    "verified": p.get("verified"),
                    "profileImage": safe_str(p.get("profilePicUrl") or p.get("profilePicUrlHD")),
                    "externalUrl": safe_str(p.get("externalUrl")),
                }

            return await _try_decodo(ctx, lambda: decodo.channel_details(handle), _apify)

        data = await cached_or_run(
            endpoint="instagram.channel-details",
            params={"url": url, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/basic-profile", summary="Lightweight Instagram profile lookup")
async def instagram_basic_profile(
    url: str = Query(..., description="Instagram profile URL or @handle"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/basic-profile",
        platform="instagram",
        resource_url=f"https://instagram.com/{handle}",
        base_credits=CREDIT_CHANNEL,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                try:
                    items = await apify.run_actor_sync(
                        settings.APIFY_ACTOR_INSTAGRAM_PROFILE,
                        {"usernames": [handle]},
                        max_items=1,
                    )
                except (ApifyError, httpx.HTTPError):
                    items = []
                if not items:
                    meta = await _public_instagram_meta(f"https://www.instagram.com/{handle}/")
                    if not meta:
                        raise HTTPException(status_code=404, detail="Profile not found")
                    return {
                        "platform": "instagram",
                        "id": "",
                        "username": handle,
                        "displayName": meta["title"],
                        "profileImage": meta["image"],
                        "verified": None,
                        "private": None,
                        "followers": 0,
                    }
                p = items[0]
                return {
                    "platform": "instagram",
                    "id": safe_str(p.get("id") or p.get("pk")),
                    "username": safe_str(p.get("username") or handle),
                    "displayName": safe_str(p.get("fullName")),
                    "profileImage": safe_str(p.get("profilePicUrl") or p.get("profilePicUrlHD")),
                    "verified": p.get("verified"),
                    "private": p.get("private") or p.get("isPrivate"),
                    "followers": safe_int(p.get("followersCount")),
                }

            return await _try_decodo(ctx, lambda: decodo.basic_profile(handle), _apify)

        data = await cached_or_run(
            endpoint="instagram.basic-profile",
            params={"url": url, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/channel-posts", summary="Latest posts from an Instagram profile")
async def instagram_channel_posts(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_POSTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/channel-posts",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items, _actor = await apify.run_with_fallback(
                    _instagram_profile_candidates(settings, f"https://www.instagram.com/{handle}/", limit, "posts"),
                    max_items=limit,
                )
                posts = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
                return {"url": url, "totalReturned": len(posts), "posts": posts}

            async def _decodo_run() -> dict[str, Any] | None:
                posts = await decodo.channel_posts(handle, limit)
                if posts is None:
                    return None
                return {"url": url, "totalReturned": len(posts), "posts": posts}

            return await _try_decodo(ctx, _decodo_run, _apify)

        data = await cached_or_run(
            endpoint="instagram.channel-posts",
            params={"url": url, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_IG_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/channel-reels", summary="Latest Reels from an Instagram profile")
async def instagram_channel_reels(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_POSTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/channel-reels",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items, _actor = await apify.run_with_fallback(
                    _instagram_profile_candidates(settings, f"https://www.instagram.com/{handle}/", limit, "reels"),
                    max_items=limit,
                )
                reels = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
                return {"url": url, "totalReturned": len(reels), "reels": reels}

            async def _decodo_run() -> dict[str, Any] | None:
                reels = await decodo.channel_reels(handle, limit)
                if reels is None:
                    return None
                return {"url": url, "totalReturned": len(reels), "reels": reels}

            return await _try_decodo(ctx, _decodo_run, _apify)

        data = await cached_or_run(
            endpoint="instagram.channel-reels",
            params={"url": url, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["reels"]), RATE_IG_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/reels-search", summary="Search Instagram Reels by hashtag")
async def instagram_reels_search(
    q: str = Query(..., min_length=2, description="Hashtag (without #) or keyword"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/reels-search",
        platform="instagram",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                tag = q.lstrip("#")
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM,
                    {
                        "directUrls": [f"https://www.instagram.com/explore/tags/{tag}/"],
                        "resultsLimit": limit,
                        "resultsType": "posts",
                    },
                    max_items=limit,
                )
                results = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
                return {"query": q, "totalReturned": len(results), "results": results}

            async def _decodo_run() -> dict[str, Any] | None:
                results = await decodo.hashtag_medias(q, limit, reels_only=True)
                if results is None:
                    return None
                return {"query": q, "totalReturned": len(results), "results": results}

            return await _try_decodo(ctx, _decodo_run, _apify)

        data = await cached_or_run(
            endpoint="instagram.reels-search",
            params={"q": q, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_IG_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


@router.get("/trending-reels", summary="Instagram trending Reels / Explore posts")
async def instagram_trending_reels(
    country: str = Query("United States", description="Country name for Explore localization"),
    limit: int = Query(20, ge=10, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_MARGIN, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/trending-reels",
        platform="instagram",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Explore scraping regularly needs >120s (sometimes >10 min); try a
            # live run first, then fall back to the actor's latest successful
            # run - trending content stays relevant for hours.
            client = ApifyClient(timeout=280, max_attempts=1)
            try:
                items = await client.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM_TRENDING,
                    {"max_results": limit, "download_medias": "none", "country": country},
                    max_items=limit,
                )
            except ApifyError:
                items = await client.last_succeeded_items(
                    settings.APIFY_ACTOR_INSTAGRAM_TRENDING,
                    max_age_secs=48 * 3600,
                    max_items=limit,
                )
                if not items:
                    raise
            reels = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
            ctx["source"] = "apify"
            return {"platform": "instagram", "country": country, "totalReturned": len(reels), "reels": reels}

        data = await cached_or_run(
            endpoint="instagram.trending-reels",
            params={"country": country, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            # Trending actor runs take minutes; serve the last list instantly
            # after TTL expiry and refresh in the background.
            stale_while_revalidate=True,
        )
        ctx["credits_override"] = _scaled_credits(len(data["reels"]), RATE_IG_MARGIN, 2)
        return ApiResponse(data=data)


@router.get("/video-download", summary="Direct video URL for Instagram Reel")
async def instagram_video_download(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/video-download",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_DOWNLOAD,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await instagram_native.fetch_reel_media(_require_instagram_post_url(url))
            if native and safe_str(native.get("videoUrl")):
                ctx["source"] = "direct"
                return {
                    "platform": "instagram",
                    "url": url,
                    "downloadUrl": safe_str(native.get("videoUrl")),
                    "thumbnailUrl": safe_str(native.get("thumbnailUrl")),
                    "duration": safe_float(native.get("duration")),
                }

            ctx["source"] = "apify"
            apify = get_apify()
            items, _actor = await apify.run_with_fallback(
                _instagram_reel_candidates(settings, url),
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Reel not found")
            v = items[0]
            download_url = safe_str(v.get("videoUrl") or v.get("video_url") or v.get("downloadUrl"))
            if not download_url:
                raise HTTPException(status_code=404, detail="Video download URL not found")
            return {
                "platform": "instagram",
                "url": url,
                "downloadUrl": download_url,
                "thumbnailUrl": safe_str(v.get("displayUrl") or v.get("thumbnailUrl") or v.get("thumbnail")),
                "duration": safe_float(v.get("videoDuration") or v.get("duration") or v.get("durationSeconds")),
            }

        data = await cached_or_run(
            endpoint="instagram.video-download",
            params={"url": url, "v": 7},
            runner=_run,
            ctx=ctx,
            ttl=3600,
        )
        return ApiResponse(data=data)


@router.get("/reels-by-audio-id", summary="Instagram Reels by audio ID")
async def instagram_reels_by_audio_id(
    audio_id: str = Query(..., min_length=2, description="Instagram audio/music ID or full audio URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_instagram_platform_mismatch(audio_id, "https://www.instagram.com/reels/audio/123456789/")
    audio_url = audio_id if audio_id.startswith("http") else f"https://www.instagram.com/reels/audio/{audio_id}/"
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_MARGIN, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/reels-by-audio-id",
        platform="instagram",
        resource_url=audio_url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM_AUDIO,
                    {"audioUrls": [audio_url], "maxResults": limit, "downloadVideos": False},
                    max_items=limit,
                )
                reels = [_normalize_audio_reel(i) for i in items[:limit] if not i.get("error")]
                return {
                    "platform": "instagram",
                    "audioId": audio_id,
                    "audioUrl": audio_url,
                    "totalReturned": len(reels),
                    "reels": reels,
                }

            ctx["source"] = "apify"
            return await _apify()

        data = await cached_or_run(
            endpoint="instagram.reels-by-audio-id",
            params={"audio_id": audio_id, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["reels"]), RATE_IG_MARGIN, 2)
        return ApiResponse(data=data)


@router.get("/tagged-posts", summary="Posts an Instagram user is tagged in")
async def instagram_tagged_posts(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_RICH, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/tagged-posts",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM_TAGGED,
                    {"username": [handle], "resultsLimit": limit},
                    max_items=limit,
                )
                posts = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
                return {"url": url, "totalReturned": len(posts), "posts": posts}

            ctx["source"] = "apify"
            return await _apify()

        data = await cached_or_run(
            endpoint="instagram.tagged-posts",
            params={"url": url, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_IG_RICH, 2)
        return ApiResponse(data=data)


@router.get("/music-posts", summary="Posts/Reels using an Instagram audio")
async def instagram_music_posts(
    url: str = Query(..., description="Instagram audio/music page URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_instagram_platform_mismatch(url, "https://www.instagram.com/reels/audio/123456789/")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_RICH, 3)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/music-posts",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM_AUDIO,
                    {"audioUrls": [url], "maxResults": limit, "downloadVideos": False},
                    max_items=limit,
                )
                posts = [_normalize_audio_reel(i) for i in items[:limit] if not i.get("error")]
                return {"url": url, "totalReturned": len(posts), "posts": posts}

            ctx["source"] = "apify"
            return await _apify()

        data = await cached_or_run(
            endpoint="instagram.music-posts",
            params={"url": url, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_IG_RICH, 3)
        return ApiResponse(data=data)


@router.get("/hashtag-search", summary="Search Instagram posts by hashtag")
async def instagram_hashtag_search(
    q: str = Query(..., min_length=2, description="Hashtag (without #)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/hashtag-search",
        platform="instagram",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                tag = q.lstrip("#")
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM,
                    {
                        "directUrls": [f"https://www.instagram.com/explore/tags/{tag}/"],
                        "resultsLimit": limit,
                        "resultsType": "posts",
                    },
                    max_items=limit,
                )
                results = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
                return {"query": q, "totalReturned": len(results), "results": results}

            async def _decodo_run() -> dict[str, Any] | None:
                results = await decodo.hashtag_medias(q, limit, reels_only=False)
                if results is None:
                    return None
                return {"query": q, "totalReturned": len(results), "results": results}

            return await _try_decodo(ctx, _decodo_run, _apify)

        data = await cached_or_run(
            endpoint="instagram.hashtag-search",
            params={"q": q, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_IG_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


def _normalize_ig_profile(item: dict) -> dict:
    username = item.get("username") or item.get("ownerUsername")
    return {
        "username": safe_str(username),
        "displayName": safe_str(item.get("fullName") or item.get("ownerFullName")),
        "url": f"https://instagram.com/{username}" if username else None,
        "followers": safe_int(item.get("followersCount")),
        "verified": item.get("verified") or item.get("isVerified"),
        "private": item.get("private") or item.get("isPrivate"),
        "profileImage": safe_str(item.get("profilePicUrl")),
    }


@router.get("/profile-search", summary="Search Instagram profiles by keyword")
async def instagram_profile_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/profile-search",
        platform="instagram",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM,
                    {"search": q, "searchType": "user", "searchLimit": limit, "resultsType": "details"},
                    max_items=limit,
                )
                users = [_normalize_ig_profile(i) for i in items[:limit] if i.get("username") or i.get("ownerUsername")]
                return {"query": q, "totalReturned": len(users), "users": users}

            ctx["source"] = "apify"
            return await _apify()

        data = await cached_or_run(
            endpoint="instagram.profile-search",
            params={"q": q, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["users"]), RATE_IG_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


def _highlight_payload(item: dict) -> dict:
    return {
        "id": safe_str(item.get("id") or item.get("highlightId")),
        "title": safe_str(item.get("title") or item.get("name")),
        "coverUrl": safe_str(item.get("coverUrl") or item.get("cover") or item.get("coverMediaUrl") or item.get("coverImageUrl")),
        "itemCount": safe_int(item.get("itemCount") or item.get("mediaCount")),
    }


@router.get("/story-highlights", summary="List an Instagram profile's story highlights")
async def instagram_story_highlights(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/story-highlights",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_CHANNEL + 4,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM_HIGHLIGHTS,
                    {
                        "usernames": [handle],
                        "includeStories": False,
                        "includeHighlights": True,
                        "expandHighlightItems": False,
                    },
                    max_items=1,
                )
                highlights: list[dict[str, Any]] = []
                for row in items:
                    raw = row.get("highlights") or row.get("highlightsList") or []
                    if isinstance(raw, list):
                        highlights.extend(_highlight_payload(h) for h in raw if isinstance(h, dict))
                return {"url": url, "totalReturned": len(highlights), "highlights": highlights}

            ctx["source"] = "apify"
            return await _apify()

        data = await cached_or_run(
            endpoint="instagram.story-highlights",
            params={"url": url, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/highlights-details", summary="Items inside an Instagram profile's highlights")
async def instagram_highlights_details(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    limit: int = Query(10, ge=1, le=50, description="Max highlights to expand"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_RICH, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/highlights-details",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_INSTAGRAM_HIGHLIGHTS,
                    {
                        "usernames": [handle],
                        "includeStories": False,
                        "includeHighlights": True,
                        "expandHighlightItems": True,
                        "maxHighlightsPerUser": limit,
                    },
                    max_items=limit,
                )
                highlights: list[dict[str, Any]] = []
                for row in items:
                    raw = row.get("highlights") or row.get("highlightsList") or []
                    if not isinstance(raw, list):
                        continue
                    for h in raw:
                        if not isinstance(h, dict):
                            continue
                        payload = _highlight_payload(h)
                        media = h.get("items") or h.get("media") or []
                        payload["items"] = [
                            {
                                "type": safe_str(m.get("type") or m.get("mediaType")),
                                "url": safe_str(m.get("url") or m.get("mediaUrl") or m.get("videoUrl") or m.get("imageUrl")),
                                "thumbnailUrl": safe_str(m.get("thumbnailUrl") or m.get("displayUrl")),
                                "takenAt": safe_str(m.get("takenAt") or m.get("timestamp")),
                            }
                            for m in (media if isinstance(media, list) else [])
                            if isinstance(m, dict)
                        ]
                        if payload.get("itemCount") is None and payload["items"]:
                            payload["itemCount"] = len(payload["items"])
                        highlights.append(payload)
                return {"url": url, "totalReturned": len(highlights), "highlights": highlights}

            ctx["source"] = "apify"
            return await _apify()

        data = await cached_or_run(
            endpoint="instagram.highlights-details",
            params={"url": url, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["highlights"]), RATE_IG_RICH, 5)
        return ApiResponse(data=data)


@router.get("/embed", summary="Embed HTML for an Instagram post/reel")
async def instagram_embed(
    url: str = Query(..., description="Instagram post or reel URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    shortcode = _require_instagram_post_url(url)
    # Pure string build â€” no Apify call, so this is a flat 1-credit endpoint.
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/embed",
        platform="instagram",
        resource_url=url,
        base_credits=1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            async def _local() -> dict[str, Any]:
                permalink = f"https://www.instagram.com/p/{shortcode}/"
                html = (
                    '<blockquote class="instagram-media" '
                    f'data-instgrm-permalink="{permalink}" data-instgrm-version="14"></blockquote>'
                    '<script async src="//www.instagram.com/embed.js"></script>'
                )
                return {
                    "platform": "instagram",
                    "url": url,
                    "shortcode": shortcode,
                    "permalink": permalink,
                    "html": html,
                }

            ctx["source"] = "direct"
            return await _local()

        data = await cached_or_run(
            endpoint="instagram.embed",
            params={"url": url, "v": 4},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)
