"""Instagram endpoints (Reels, Posts, Profiles)."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
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
from app.utils.formatters import (
    normalize_language_code,
    safe_float,
    safe_int,
    safe_list,
    safe_str,
)
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

# Per-result rates calibrated to ~80% markup (rate = cost_per_result * 400 at a
# $0.0045/credit sell price) over verified Apify prices:
#   apify/instagram-scraper          $1.50/1k ($0.0015) -> reels/hashtag search
#   apify/instagram-comment-scraper  $2.30/1k ($0.0023) -> comments
#   apify/instagram-tagged-scraper / reels-audio ~$0.0023 -> tagged / music
# Charged via ctx["credits_override"] on the actual item count.
RATE_IG_POSTS = 0.6
RATE_IG_RICH = 0.9
RATE_IG_MARGIN = 1.4
# channel-posts / channel-reels are served natively (Decodo profile scrape +
# Instagram's own feed API), which is far cheaper than an Apify run, so they
# get their own reduced per-result rate.
RATE_IG_CHANNEL = 0.3


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


def _require_ig_profile_target(value: str) -> tuple[str, str]:
    """Resolve a basic-profile lookup target. Returns ("id", <numeric id>) for a
    bare numeric user ID, else ("handle", <username>) for a profile URL, @handle,
    or username."""
    raw = (value or "").strip()
    if raw.isdigit():
        return ("id", raw)
    handle = extract_instagram_username(raw)
    if not handle:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Instagram user. Pass a numeric user ID (e.g. 314216) or "
                "a profile URL / @handle."
            ),
        )
    return ("handle", handle)


# A valid Instagram hashtag is word chars (unicode letters/digits/underscore)
# with at least one letter. The Apify scrapers hand back the raw token, which
# can keep trailing punctuation (e.g. "#DestinationDeRêv'" -> "DestinationDeRêv'")
# or numeric-only tags. Clean them here so the Apify path matches the Decodo
# path (instagram_decodo._HASHTAG_RE) and both sources return identical tags.
def _clean_hashtag(tag: str) -> str | None:
    trimmed = re.sub(r"^\W+|\W+$", "", tag or "", flags=re.UNICODE)
    if not trimmed or not re.search(r"[^\W\d]", trimmed, flags=re.UNICODE):
        return None
    return trimmed


def _clean_hashtags(raw: Any) -> list[str]:
    cleaned = (_clean_hashtag(str(tag)) for tag in safe_list(raw))
    return [tag for tag in cleaned if tag]


def _normalize_post(item: dict) -> dict:
    owner = item.get("owner") or {}
    author = item.get("ownerUsername") or owner.get("username")
    post_type = safe_str(item.get("type"))
    duration = safe_float(item.get("videoDuration") or item.get("duration") or item.get("durationSeconds"))
    caption = safe_str(item.get("caption") or item.get("text") or item.get("description")) or ""
    return {
        "platform": "instagram",
        "url": safe_str(item.get("url") or item.get("permalink") or item.get("shortcodeUrl")),
        "id": safe_str(item.get("id") or item.get("shortCode") or item.get("shortcode")),
        # "Image" | "Video" | "Sidecar" (carousel) - video-only fields are
        # stripped for non-video posts.
        "postType": post_type,
        "productType": safe_str(item.get("productType")),
        "caption": caption,
        "description": caption,
        "publishedAt": safe_str(item.get("timestamp") or item.get("takenAt") or item.get("taken_at")),
        # Apify reports durations as float32 noise (17.95800018310547); round
        # to millisecond precision like the native mappers.
        "durationSeconds": round(duration, 3) if duration is not None else None,
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
            "likes": decodo.hidden_count(item.get("likesCount") or item.get("likeCount")),
            "comments": decodo.hidden_count(item.get("commentsCount") or item.get("commentCount")),
        },
        "hashtags": _clean_hashtags(item.get("hashtags")),
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


def _instagram_hashtag_candidates(
    settings: Any, tag: str, limit: int, results_type: str
) -> list[tuple[str, dict[str, Any]]]:
    """Hashtag feed candidates; ``results_type`` "reels" keeps only videos."""
    return _dedupe_candidates(
        [
            (
                settings.APIFY_ACTOR_INSTAGRAM_HASHTAG,
                {"hashtags": [tag], "resultsLimit": limit, "resultsType": results_type},
            ),
            (
                settings.APIFY_ACTOR_INSTAGRAM,
                {
                    "directUrls": [f"https://www.instagram.com/explore/tags/{tag}/"],
                    "resultsLimit": limit,
                    "resultsType": results_type,
                },
            ),
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
                start = round(safe_float(seg.get("start") or seg.get("startTime") or seg.get("startMs")) or 0, 3)
                duration = round(safe_float(seg.get("duration") or seg.get("dur")) or 0, 3)
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
                segments.append(
                    {
                        "text": text,
                        "start": start,
                        "duration": duration,
                        "end": round(start + duration, 3),
                        "timestamp": f"{mm:02d}:{ss:02d}",
                    }
                )
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
) -> tuple[str, list[dict[str, Any]], str, str | None]:
    """Return (full transcript, segments, source, detected language).

    Primary: resolve the reel's MP4 natively (~1-2s, Apify scraper fallback)
    and Whisper-transcribe it ourselves. This always yields actual SPEECH,
    with timestamps, and is faster + cheaper than the transcript actors.
    Actors remain as a fallback, but their output is rejected when it merely
    echoes the post caption.

    `language` pins Whisper's language (ISO-639-1) instead of auto-detection.
    """
    settings = get_settings()
    apify = get_apify()

    async def _whisper(media_url: str) -> tuple[str, list[dict[str, Any]], str | None] | None:
        """Whisper a media URL; None = fetch failed / too large (try next)."""
        try:
            tx = await transcribe_video_url(media_url, language=language)
        except Exception:  # noqa: BLE001
            return None
        if tx is None:
            return None
        full = (safe_str(tx.get("transcript")) or "").strip()
        if full:
            detected = normalize_language_code(safe_str(tx.get("language")) or language)
            return full, tx.get("transcriptSegments") or [], detected
        # Whisper ran fine and heard nothing -> genuinely no speech.
        raise HTTPException(status_code=422, detail="No speech found in this Reel")

    # Fast path: native GraphQL resolver gets the MP4 URL in ~1-2s.
    reel_item: dict[str, Any] | None = None
    native = await instagram_native.fetch_reel_media(_require_instagram_post_url(url))
    if native and safe_str(native.get("videoUrl")):
        result = await _whisper(safe_str(native.get("videoUrl")))
        if result:
            return result[0], result[1], "direct", result[2]

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
                return result[0], result[1], "openai", result[2]

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
            detected = normalize_language_code(
                safe_str(items[0].get("language") or items[0].get("detectedLanguage")) or language
            )
            return full, segments, "apify", detected

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
            detected = normalize_language_code(
                safe_str(items[0].get("language") or items[0].get("detectedLanguage")) or language
            )
            return full, segments, "apify", detected

    if reel_item is None and native is None:
        raise HTTPException(status_code=404, detail="Reel not found")
    raise HTTPException(status_code=422, detail="No transcript available")


def _normalize_audio_reel(item: dict) -> dict:
    """Map the reels-by-audio scraper output (capitalized keys) to our shape.

    The actor only exposes the author's profile picture (no reel cover image),
    so we don't emit thumbnailUrl rather than passing the avatar off as one.
    Null-valued fields (empty caption, missing author bits, hidden counts) are
    stripped by strip_null_post_fields at the call site."""
    author = item.get("author") or {}
    username = author.get("username")
    caption = safe_str(item.get("caption")) or ""
    return {
        "platform": "instagram",
        "url": safe_str(item.get("URL") or item.get("url")),
        "id": safe_str(item.get("Id") or item.get("id")),
        "caption": caption,
        "description": caption,
        "publishedAt": safe_str(item.get("postedAt")),
        "durationSeconds": safe_float(item.get("videoDuration")),
        "videoUrl": safe_str(item.get("videoTemporaryUrl") or item.get("storedVideoUrl")),
        "author": {
            "username": safe_str(username),
            "displayName": safe_str(author.get("fullname")),
            "url": f"https://instagram.com/{username}" if username else None,
            "verified": author.get("isVerified"),
            "profileImage": safe_str(author.get("temporaryProfilePictureUrl")),
        },
        "engagement": {
            "views": safe_int(item.get("playCount")),
            "likes": decodo.hidden_count(item.get("likeCount")),
            "comments": decodo.hidden_count(item.get("commentCount")),
        },
        "musicId": safe_str(item.get("musicId")),
        "musicUrl": safe_str(item.get("musicUrl")),
    }


@router.get("/details", summary="Instagram post/reel details")
async def instagram_details(
    url: str = Query(..., description="Instagram post or reel URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            return decodo.strip_null_post_fields(data)

        data = await cached_or_run(
            endpoint="instagram.details",
            params={"url": url, "v": 12},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
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
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            full, segments, source, detected = await _fetch_instagram_transcript(url, language=lang)
            ctx["source"] = source
            return {
                "platform": "instagram",
                "url": url,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
                "language": detected,
            }

        data = await cached_or_run(
            endpoint="instagram.transcript",
            params={"url": url, "language": lang, "v": 10},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
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
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            text, _segments, source, _detected = await _fetch_instagram_transcript(url, language=lang)
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
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Instagram post/reel comments")
async def instagram_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["comments"]), RATE_IG_RICH, 2)
        return ApiResponse(data=data)


@router.get("/channel-details", summary="Instagram profile info")
async def instagram_channel_details(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            # Native first (same web_profile_info as basic-profile), then Decodo, then Apify/meta.
            user = await instagram_native.fetch_web_profile_info(handle)
            if user is not None:
                ctx["source"] = "direct"
                return instagram_native.map_channel_details(user, handle=handle)

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
                        "verified": False,
                        "profileImage": meta["image"],
                        "externalUrl": "",
                    }
                p = items[0]
                verified = p.get("verified")
                return {
                    "platform": "instagram",
                    "url": f"https://instagram.com/{handle}",
                    "username": safe_str(p.get("username") or handle),
                    "displayName": safe_str(p.get("fullName")),
                    "bio": safe_str(p.get("biography")),
                    "followers": safe_int(p.get("followersCount")),
                    "following": safe_int(p.get("followsCount")),
                    "postCount": safe_int(p.get("postsCount")),
                    "verified": False if verified is None else bool(verified),
                    "profileImage": safe_str(p.get("profilePicUrl") or p.get("profilePicUrlHD")),
                    "externalUrl": safe_str(p.get("externalUrl")) or "",
                }

            return await _try_decodo(ctx, lambda: decodo.channel_details(handle), _apify)

        data = await cached_or_run(
            endpoint="instagram.channel-details",
            params={"url": url, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/basic-profile", summary="Full Instagram profile by user ID")
async def instagram_basic_profile(
    userId: str = Query(
        ...,
        description=(
            "Instagram numeric user ID (e.g. 314216). A profile URL, @handle, or "
            "username is also accepted and resolved automatically."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    mode, ident = _require_ig_profile_target(userId)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/basic-profile",
        platform="instagram",
        resource_url=f"instagram_user:{ident}",
        base_credits=CREDIT_CHANNEL,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Numeric id -> resolve the @username first (the by-id info endpoint
            # is minimal logged-out, but always carries the username).
            if mode == "id":
                username = await instagram_native.resolve_username(ident)
                if not username:
                    raise HTTPException(
                        status_code=404,
                        detail="Profile not found for that user ID.",
                    )
            else:
                username = ident

            # Rich profile from the logged-out web_profile_info endpoint; fall
            # back to Decodo (same underlying data) if the native call fails.
            user = await instagram_native.fetch_web_profile_info(username)
            if user is not None:
                ctx["source"] = "native"
            else:
                user = await decodo._profile(username)
                ctx["source"] = "decodo"
            if not user:
                raise HTTPException(status_code=404, detail="Profile not found")
            return instagram_native.map_basic_profile(user)

        data = await cached_or_run(
            endpoint="instagram.basic-profile",
            params={"target": f"{mode}:{ident}", "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


_IG_CURSOR_RE = re.compile(r"^\d+_(\d+)$")
_IG_FEED_MAX_PAGES = 8


async def _ig_feed_collect(
    user_id: str,
    cursor: str | None,
    limit: int,
    *,
    reels_only: bool = False,
    followers: int | None = None,
) -> tuple[list[dict[str, Any]], str | None] | None:
    """Collect up to ``limit`` posts from the native api/v1 feed starting at
    ``cursor``. Returns (posts, next_cursor) or None if the feed is
    unreachable."""
    collected: list[dict[str, Any]] = []
    next_cursor = cursor
    for _ in range(_IG_FEED_MAX_PAGES):
        page = await instagram_native.fetch_user_feed_page(user_id, next_cursor, count=33)
        if page is None:
            return None if not collected else (collected[:limit], next_cursor)
        items, next_max_id, more = page
        for raw in items:
            if reels_only and safe_int(raw.get("media_type")) != 2:
                continue
            collected.append(
                instagram_native.map_feed_post(raw, followers=followers, profile_user_id=user_id)
            )
        next_cursor = next_max_id if more and next_max_id else None
        # Instagram suffixes next_max_id with the last item's owner id, which
        # differs from the profile on collab posts. Our public cursor embeds
        # the profile's user id (the feed accepts either as max_id), so the
        # next request pages the right account.
        if next_cursor:
            next_cursor = f"{next_cursor.split('_')[0]}_{user_id}"
        if len(collected) >= limit or next_cursor is None:
            break
    return collected[:limit], next_cursor


def _ig_channel_page(
    first_page: dict[str, Any] | None, limit: int
) -> tuple[list[dict[str, Any]], str | None, str | None, int | None] | None:
    """Unpack a Decodo first page into (posts, next_cursor, user_id, followers)."""
    if not first_page:
        return None
    posts = first_page["items"]
    user_id = first_page.get("userId")
    followers = first_page.get("followers")
    if followers is None and posts:
        followers = posts[0].get("author", {}).get("followers")
    next_cursor = None
    if first_page.get("hasMore") and posts and user_id and posts[-1].get("id"):
        next_cursor = f"{posts[-1]['id']}_{user_id}"
    return posts, next_cursor, user_id, followers


@router.get("/channel-posts", summary="Latest posts from an Instagram profile")
async def instagram_channel_posts(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    limit: int = Query(20, ge=1, le=200),
    cursor: str | None = Query(None, description="Leave empty for the first page; then pass the nextCursor value returned in the previous response, e.g. 3937014945555313553_1697296"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    if cursor and not _IG_CURSOR_RE.match(cursor):
        raise HTTPException(status_code=400, detail="Invalid cursor. Pass the nextCursor value from a previous response.")
    cost = _scaled_credits(limit, RATE_IG_CHANNEL, 1)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/channel-posts",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            if cursor:
                user_id = _IG_CURSOR_RE.match(cursor).group(1)
                result = await _ig_feed_collect(user_id, cursor, limit)
                if result is None:
                    raise HTTPException(status_code=502, detail="Failed to fetch the next page. Retry shortly.")
                posts, next_cursor = result
                ctx["source"] = "direct"
                return {
                    "url": url,
                    "totalReturned": len(posts),
                    "posts": posts,
                    "nextCursor": next_cursor,
                    "hasMore": next_cursor is not None,
                }

            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items, _actor = await apify.run_with_fallback(
                    _instagram_profile_candidates(settings, f"https://www.instagram.com/{handle}/", limit, "posts"),
                    max_items=limit,
                )
                # Enrich author fields the listing actor omits (followers /
                # verified / avatar) from a cheap profile lookup.
                profile = await decodo._profile(handle)
                author_extra = {}
                if isinstance(profile, dict):
                    author_extra = {
                        "displayName": safe_str(profile.get("full_name")),
                        "followers": safe_int(
                            (profile.get("edge_followed_by") or {}).get("count")
                            if isinstance(profile.get("edge_followed_by"), dict)
                            else profile.get("follower_count") or profile.get("followers")
                        ),
                        "verified": profile.get("is_verified"),
                        "profileImage": safe_str(
                            (profile.get("profile_pic_url_hd") or profile.get("profile_pic_url"))
                        ),
                    }
                    author_extra = {k: v for k, v in author_extra.items() if v is not None}
                posts = []
                for i in items[:limit]:
                    if i.get("error"):
                        continue
                    post = _normalize_post(i)
                    if author_extra:
                        post["author"] = {**author_extra, **(post.get("author") or {})}
                    posts.append(decodo.strip_null_post_fields(post))
                return {
                    "url": url,
                    "totalReturned": len(posts),
                    "posts": posts,
                    "nextCursor": None,
                    "hasMore": False,
                }

            async def _decodo_run() -> dict[str, Any] | None:
                page = _ig_channel_page(await decodo.channel_posts(handle, limit), limit)
                if page is None:
                    return None
                posts, next_cursor, user_id, followers = page
                if len(posts) < limit and next_cursor and user_id:
                    extra = await _ig_feed_collect(user_id, next_cursor, limit - len(posts), followers=followers)
                    if extra is not None:
                        more_posts, next_cursor = extra
                        posts = posts + more_posts
                return {
                    "url": url,
                    "totalReturned": len(posts),
                    "posts": posts,
                    "nextCursor": next_cursor,
                    "hasMore": next_cursor is not None,
                }

            return await _try_decodo(ctx, _decodo_run, _apify)

        data = await cached_or_run(
            endpoint="instagram.channel-posts",
            params={"url": url, "limit": limit, "cursor": cursor or "", "v": 15},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_IG_CHANNEL, 1)
        return ApiResponse(data=data)


@router.get("/channel-reels", summary="Latest Reels from an Instagram profile")
async def instagram_channel_reels(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    limit: int = Query(20, ge=1, le=200),
    cursor: str | None = Query(None, description="Leave empty for the first page; then pass the nextCursor value returned in the previous response, e.g. 3937014945555313553_1697296"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_instagram_profile(url)
    settings = get_settings()
    if cursor and not _IG_CURSOR_RE.match(cursor):
        raise HTTPException(status_code=400, detail="Invalid cursor. Pass the nextCursor value from a previous response.")
    cost = _scaled_credits(limit, RATE_IG_CHANNEL, 1)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/channel-reels",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            if cursor:
                user_id = _IG_CURSOR_RE.match(cursor).group(1)
                result = await _ig_feed_collect(user_id, cursor, limit, reels_only=True)
                if result is None:
                    raise HTTPException(status_code=502, detail="Failed to fetch the next page. Retry shortly.")
                reels, next_cursor = result
                ctx["source"] = "direct"
                return {
                    "url": url,
                    "totalReturned": len(reels),
                    "reels": reels,
                    "nextCursor": next_cursor,
                    "hasMore": next_cursor is not None,
                }

            async def _apify() -> dict[str, Any]:
                apify = get_apify()
                items, _actor = await apify.run_with_fallback(
                    _instagram_profile_candidates(settings, f"https://www.instagram.com/{handle}/", limit, "reels"),
                    max_items=limit,
                )
                reels = [decodo.strip_null_post_fields(_normalize_post(i)) for i in items[:limit] if not i.get("error")]
                return {
                    "url": url,
                    "totalReturned": len(reels),
                    "reels": reels,
                    "nextCursor": None,
                    "hasMore": False,
                }

            async def _decodo_run() -> dict[str, Any] | None:
                page = _ig_channel_page(await decodo.channel_reels(handle, limit), limit)
                if page is None:
                    return None
                reels, next_cursor, user_id, followers = page
                # Prefer the native feed for the whole page: the GraphQL
                # timeline omits duration/play counts for clips and buries
                # recent Reels under legacy IGTV uploads. The Decodo items
                # only serve as a fallback when the feed is unreachable.
                if user_id:
                    native = await _ig_feed_collect(
                        user_id, None, limit, reels_only=True, followers=followers
                    )
                    if native is not None and native[0]:
                        reels, next_cursor = native
                if not reels:
                    return None
                return {
                    "url": url,
                    "totalReturned": len(reels),
                    "reels": reels,
                    "nextCursor": next_cursor,
                    "hasMore": next_cursor is not None,
                }

            return await _try_decodo(ctx, _decodo_run, _apify)

        data = await cached_or_run(
            endpoint="instagram.channel-reels",
            params={"url": url, "limit": limit, "cursor": cursor or "", "v": 16},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["reels"]), RATE_IG_CHANNEL, 1)
        return ApiResponse(data=data)


@router.get("/reels-search", summary="Search Instagram Reels by hashtag")
async def instagram_reels_search(
    q: str = Query(..., min_length=2, description="Hashtag (without #) or keyword"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
                items, _actor = await apify.run_with_fallback(
                    _instagram_hashtag_candidates(settings, q.lstrip("#"), limit, "reels"),
                    max_items=limit,
                )
                results = [
                    decodo.strip_null_post_fields(_normalize_post(i))
                    for i in items[:limit]
                    if not i.get("error") and i.get("type") == "Video"
                ]
                return {"query": q, "totalReturned": len(results), "results": results}

            async def _decodo_run() -> dict[str, Any] | None:
                results = await decodo.hashtag_medias(q, limit, reels_only=True)
                if results is None:
                    return None
                return {"query": q, "totalReturned": len(results), "results": results}

            return await _try_decodo(ctx, _decodo_run, _apify)

        data = await cached_or_run(
            endpoint="instagram.reels-search",
            params={"q": q, "limit": limit, "v": 12},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_IG_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


def _normalize_trending_item(item: dict) -> dict:
    """The trending actor uses its own snake_case schema (username, likes,
    plays, image_url, epoch timestamp...), so the generic Apify post
    normalizer maps it to empty/raw values."""
    username = safe_str(item.get("username"))
    product = safe_str(item.get("type"))  # feed | carousel_container | clips
    is_video = bool(item.get("is_video"))
    # Match the rest of the platform: postType reflects the container, so a
    # carousel is "Sidecar" even when its first media is a video.
    if product == "carousel_container":
        post_type = "Sidecar"
    elif is_video:
        post_type = "Video"
    else:
        post_type = "Image"
    caption = safe_str(item.get("caption")) or ""
    duration = safe_float(item.get("duration"))
    published = safe_str(item.get("date"))
    return {
        "platform": "instagram",
        "url": safe_str(item.get("url")),
        "id": safe_str(item.get("id") or item.get("code")),
        "postType": post_type,
        "productType": product,
        # Explore feed category, e.g. "TV & Movies" / "Bollywood TV & Movies".
        "section": safe_str(item.get("section")),
        "topic": safe_str(item.get("topic")),
        "caption": caption,
        "description": caption,
        "publishedAt": published.replace("+00:00", "Z") if published else None,
        "durationSeconds": round(duration, 3) if duration is not None else None,
        "thumbnailUrl": safe_str(item.get("thumbnail_url") or item.get("image_url")),
        "videoUrl": safe_str(item.get("video_url")),
        "author": {
            "username": username,
            "url": f"https://instagram.com/{username}" if username else None,
        },
        "engagement": {
            "views": safe_int(item.get("plays")),
            "likes": decodo.hidden_count(item.get("likes")),
            "comments": decodo.hidden_count(item.get("comments")),
        },
        "hashtags": decodo._HASHTAG_RE.findall(caption),
        "mentions": decodo._MENTION_RE.findall(caption),
    }


# Countries supported by the trending actor's input enum. Anything else makes
# the run fail instantly with invalid-input, so we validate up front.
_TRENDING_COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Australia", "Germany",
    "France", "Italy", "Spain", "Netherlands", "Sweden", "Norway", "Denmark",
    "Finland", "Poland", "Portugal", "Brazil", "Mexico", "Argentina", "Chile",
    "Colombia", "Japan", "South Korea", "Singapore", "Hong Kong", "Taiwan",
    "India", "Indonesia", "Thailand", "Philippines", "Malaysia", "Vietnam",
    "United Arab Emirates", "Saudi Arabia", "Turkey", "South Africa",
]
_TRENDING_COUNTRY_ALIASES = {
    "us": "United States", "usa": "United States", "u.s.": "United States",
    "ca": "Canada", "gb": "United Kingdom", "uk": "United Kingdom",
    "au": "Australia", "de": "Germany", "fr": "France", "it": "Italy",
    "es": "Spain", "nl": "Netherlands", "se": "Sweden", "no": "Norway",
    "dk": "Denmark", "fi": "Finland", "pl": "Poland", "pt": "Portugal",
    "br": "Brazil", "mx": "Mexico", "ar": "Argentina", "cl": "Chile",
    "co": "Colombia", "jp": "Japan", "kr": "South Korea", "korea": "South Korea",
    "sg": "Singapore", "hk": "Hong Kong", "tw": "Taiwan", "in": "India",
    "id": "Indonesia", "th": "Thailand", "ph": "Philippines", "my": "Malaysia",
    "vn": "Vietnam", "ae": "United Arab Emirates", "uae": "United Arab Emirates",
    "sa": "Saudi Arabia", "ksa": "Saudi Arabia", "tr": "Turkey",
    "turkiye": "Turkey", "türkiye": "Turkey", "za": "South Africa",
}


def _normalize_trending_country(raw: str) -> str:
    cleaned = raw.strip()
    lowered = cleaned.lower()
    for name in _TRENDING_COUNTRIES:
        if name.lower() == lowered:
            return name
    alias = _TRENDING_COUNTRY_ALIASES.get(lowered)
    if alias:
        return alias
    raise HTTPException(
        status_code=422,
        detail=f"Unsupported country '{cleaned}'. Use a country name or ISO code from: {', '.join(_TRENDING_COUNTRIES)}.",
    )


@router.get("/trending-reels", summary="Instagram trending Reels / Explore posts")
async def instagram_trending_reels(
    country: str = Query("United States", description="Country name or ISO code (e.g. 'United States' or 'US') for Explore localization"),
    limit: int = Query(20, ge=10, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    country = _normalize_trending_country(country)
    cost = _scaled_credits(limit, RATE_IG_MARGIN, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/trending-reels",
        platform="instagram",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Explore runs take ~10-12 minutes - far beyond any request
            # timeout - so a live sync wait can never finish. Instead: serve
            # the newest finished snapshot for this country (<=48h old),
            # kick off a background refresh once it is older than 6h, and for
            # a cold country join the in-flight run (or start one) and wait
            # out the request budget before returning a clear retry hint.
            client = ApifyClient(timeout=280, max_attempts=1)
            actor = settings.APIFY_ACTOR_INSTAGRAM_TRENDING
            run_input = {"max_results": limit, "download_medias": "none", "country": country}
            match = {"country": country}

            def _payload(items: list[dict[str, Any]]) -> dict[str, Any]:
                reels = [decodo.strip_null_post_fields(_normalize_trending_item(i)) for i in items[:limit] if not i.get("error")]
                ctx["source"] = "apify"
                return {"platform": "instagram", "country": country, "totalReturned": len(reels), "reels": reels}

            last = await client.last_succeeded_run(actor, max_age_secs=48 * 3600, input_match=match)
            if last:
                items = await client.dataset_items(last["defaultDatasetId"], max_items=limit)
                if items:
                    finished = datetime.fromisoformat(last["finishedAt"].replace("Z", "+00:00"))
                    age_secs = (datetime.now(timezone.utc) - finished).total_seconds()
                    if age_secs > 6 * 3600 and not await client.find_active_run(actor, input_match=match):
                        await client.start_run(actor, run_input)
                    return _payload(items)

            active = await client.find_active_run(actor, input_match=match)
            if active is None:
                active = await client.start_run(actor, run_input)
            items = await client.wait_for_run_items(active["id"], wait_secs=270, max_items=limit) if active else []
            if not items:
                raise HTTPException(
                    status_code=503,
                    detail="Trending Reels for this country are being refreshed right now (Explore scraping takes ~10 minutes). Please retry in a few minutes.",
                )
            return _payload(items)

        data = await cached_or_run(
            endpoint="instagram.trending-reels",
            params={"country": country, "limit": limit, "v": 10},
            runner=_run,
            ctx=ctx,
            # Trending actor runs take minutes; serve the last list instantly
            # after TTL expiry and refresh in the background.
            stale_while_revalidate=True,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["reels"]), RATE_IG_MARGIN, 2)
        return ApiResponse(data=data)


@router.get("/reels-by-audio-id", summary="Instagram Reels by audio ID")
async def instagram_reels_by_audio_id(
    audio_id: str = Query(..., min_length=2, description="Instagram audio/music ID or full audio URL"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
                reels = [
                    decodo.strip_null_post_fields(_normalize_audio_reel(i))
                    for i in items[:limit]
                    if not i.get("error")
                ]
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
            params={"audio_id": audio_id, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["reels"]), RATE_IG_MARGIN, 2)
        return ApiResponse(data=data)


@router.get("/tagged-posts", summary="Posts an Instagram user is tagged in")
async def instagram_tagged_posts(
    url: str = Query(..., description="Instagram profile URL, @handle, or username"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
                posts = [decodo.strip_null_post_fields(_normalize_post(i)) for i in items[:limit] if not i.get("error")]
                return {"url": url, "totalReturned": len(posts), "posts": posts}

            ctx["source"] = "apify"
            return await _apify()

        data = await cached_or_run(
            endpoint="instagram.tagged-posts",
            params={"url": url, "limit": limit, "v": 9},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_IG_RICH, 2)
        return ApiResponse(data=data)


@router.get("/hashtag-search", summary="Search Instagram posts by hashtag")
async def instagram_hashtag_search(
    q: str = Query(..., min_length=2, description="Hashtag (without #)"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
                items, _actor = await apify.run_with_fallback(
                    _instagram_hashtag_candidates(settings, q.lstrip("#"), limit, "posts"),
                    max_items=limit,
                )
                results = [decodo.strip_null_post_fields(_normalize_post(i)) for i in items[:limit] if not i.get("error")]
                return {"query": q, "totalReturned": len(results), "results": results}

            async def _decodo_run() -> dict[str, Any] | None:
                results = await decodo.hashtag_medias(q, limit, reels_only=False)
                if results is None:
                    return None
                return {"query": q, "totalReturned": len(results), "results": results}

            return await _try_decodo(ctx, _decodo_run, _apify)

        data = await cached_or_run(
            endpoint="instagram.hashtag-search",
            params={"q": q, "limit": limit, "v": 11},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_IG_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


# Instagram's keyword search (topsearch) is login-gated - a logged-out request
# gets 401 {"require_login": true} on every proxy tier - so we can't fuzzy-match
# many accounts. What DOES work logged-out is resolving an exact username to its
# public profile (the same web_profile_info/GraphQL path Instagram Details uses).
# So profile-search treats the query as an account name and returns the matching
# public profile natively (no Apify actor, ~1 credit).
def _profile_search_candidates(q: str) -> list[str]:
    """Turn a free-text query into up to two Instagram username candidates.

    Accepts a bare name, an @handle, or a full profile URL. Instagram usernames
    are lowercase [a-z0-9._], so "Planet Fitness" -> "planetfitness".
    """
    raw = (q or "").strip()
    base = (extract_instagram_username(raw) or raw).lstrip("@").strip().lower()
    candidates: list[str] = []
    if base:
        candidates.append(base)
    despaced = re.sub(r"\s+", "", base)
    if despaced and despaced != base:
        candidates.append(despaced)
    valid = [c for c in candidates if re.fullmatch(r"[a-z0-9._]{1,30}", c)]
    # de-dupe while preserving order
    return list(dict.fromkeys(valid))[:2]


def _profile_to_search_user(profile: dict) -> dict:
    username = safe_str(profile.get("username"))
    return {
        "username": username,
        "displayName": safe_str(profile.get("displayName")),
        "url": f"https://instagram.com/{username}" if username else safe_str(profile.get("url")),
        "followers": safe_int(profile.get("followers")),
        "verified": profile.get("verified"),
        "private": profile.get("private"),
        "profileImage": safe_str(profile.get("profileImage")),
    }


@router.get("/profile-search", summary="Find an Instagram profile by name or @handle")
async def instagram_profile_search(
    q: str = Query(..., min_length=2),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/profile-search",
        platform="instagram",
        resource_url=None,
        base_credits=CREDIT_CHANNEL,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            users: list[dict[str, Any]] = []
            for candidate in _profile_search_candidates(q):
                # Native first — same web_profile_info path as basic-profile.
                user = await instagram_native.fetch_web_profile_info(candidate)
                if user is not None:
                    ctx["source"] = "direct"
                    users.append(instagram_native.map_profile_search_user(user))
                    break
                profile: dict[str, Any] | None = None
                if decodo.enabled():
                    profile = await decodo.basic_profile(candidate)
                    if profile is not None:
                        ctx["source"] = "decodo"
                if profile is None:
                    meta = await _public_instagram_meta(f"https://www.instagram.com/{candidate}/")
                    if meta:
                        ctx["source"] = "meta"
                        profile = {
                            "username": candidate,
                            "displayName": meta["title"],
                            "followers": None,
                            "verified": False,
                            "private": False,
                            "profileImage": meta["image"],
                        }
                if profile:
                    users.append(_profile_to_search_user(profile))
                    break
            if not users:
                ctx["source"] = ctx.get("source") or "direct"
            return {"query": q, "totalReturned": len(users), "users": users}

        data = await cached_or_run(
            endpoint="instagram.profile-search",
            params={"q": q, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/embed", summary="Embed HTML for an Instagram post, reel, or profile")
async def instagram_embed(
    url: str = Query(..., description="Instagram post, reel, or profile URL (or @handle)"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    # Posts/reels resolve to a shortcode (type reel when the URL is a /reel/,
    # else post); anything else is treated as a profile handle. Each maps to an
    # Instagram /embed/ page we fetch below.
    shortcode = extract_instagram_shortcode(url)
    username = None if shortcode else extract_instagram_username(url)
    if not shortcode and not username:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                url,
                "instagram",
                "https://www.instagram.com/reel/SHORTCODE/ or https://www.instagram.com/username/",
            ),
        )
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/embed",
        platform="instagram",
        resource_url=url,
        base_credits=1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            if shortcode:
                kind = "reel" if re.search(r"/reels?/", url) else "post"
                permalink = f"https://www.instagram.com/p/{shortcode}/"
                embed_url = f"https://www.instagram.com/p/{shortcode}/embed/captioned/"
            else:
                kind = "profile"
                permalink = f"https://www.instagram.com/{username}/"
                embed_url = f"https://www.instagram.com/{username}/embed/"

            # Prefer Instagram's own self-contained embed document; fall back to
            # the lightweight blockquote snippet if the fetch is unavailable.
            html = await instagram_native.fetch_embed_html(embed_url)
            if html:
                ctx["source"] = "native"
            else:
                ctx["source"] = "direct"
                html = (
                    '<blockquote class="instagram-media" '
                    f'data-instgrm-permalink="{permalink}" data-instgrm-version="14"></blockquote>'
                    '<script async src="//www.instagram.com/embed.js"></script>'
                )

            payload = {
                "platform": "instagram",
                "url": url,
                "type": kind,
                "shortcode": shortcode,
                "username": username,
                "permalink": permalink,
                "embedUrl": embed_url,
                "html": html,
            }
            return {k: v for k, v in payload.items() if v is not None}

        data = await cached_or_run(
            endpoint="instagram.embed",
            params={"url": url, "v": 7},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
