"""Rumble endpoints: video details, channel videos, search.

Backed by a config-driven Rumble actor. Field mappings are defensive.
"""

from __future__ import annotations

import html
import math
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.apify_proxy import fetch_via_residential
from app.services.cached_runner import cached_or_run
from app.services import rumble_comments_native, rumble_transcript, rumble_video_native
from app.utils.formatters import first_present, parse_compact_count, safe_int, safe_str
from app.utils.url import (
    extract_rumble_channel,
    extract_rumble_video_id,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
CREDIT_TRANSCRIPT = rumble_transcript.CREDIT_TRANSCRIPT
CREDIT_COMMENTS_NATIVE = rumble_comments_native.CREDIT_RUMBLE_COMMENTS_NATIVE
RATE = 0.6


def _scaled(n: int, rate: float, minimum: int) -> int:
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _require_rumble_video_url(url: str) -> str:
    video_id = extract_rumble_video_id(url)
    if not video_id:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "rumble", "https://rumble.com/v123abc-video-title.html"),
        )
    return video_id


def _require_rumble_channel_url(url: str) -> str:
    channel = extract_rumble_channel(url)
    if not channel:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "rumble", "https://rumble.com/c/channel-name"),
        )
    return channel


def _clean_url(value: Any) -> str | None:
    """Strip Rumble's tracking query params (e9s/sci) so returned URLs are
    canonical and reusable as inputs to the detail endpoints."""
    url = safe_str(value)
    if not url:
        return url
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _rumble_content_type(url: str | None, *, is_live: bool | None) -> str:
    if is_live is True:
        return "live"
    if url and "/shorts/" in url.lower():
        return "short"
    return "video"


def _coerce_duration_pair(raw: Any) -> tuple[int | None, str | None]:
    """Return (durationSeconds, durationText) from seconds, clock, or ISO-8601."""
    if raw is None or isinstance(raw, bool):
        return None, None
    if isinstance(raw, (int, float)):
        secs = int(raw)
        if secs < 0:
            return None, None
        return secs, rumble_video_native._seconds_to_clock(secs)
    text = safe_str(raw)
    if not text:
        return None, None
    if re.fullmatch(r"\d+", text):
        secs = int(text)
        return secs, rumble_video_native._seconds_to_clock(secs)
    secs = rumble_video_native._clock_to_seconds(text)
    if secs is not None:
        return secs, rumble_video_native._seconds_to_clock(secs) or text
    iso_secs = rumble_video_native._iso_duration_seconds(text)
    if iso_secs is not None:
        return iso_secs, rumble_video_native._seconds_to_clock(iso_secs)
    return None, text


def _stamp_duration(card: dict[str, Any], raw: Any = None) -> dict[str, Any]:
    """Canonical Rumble duration: durationSeconds + durationText only.

    Drops legacy ``duration`` (string) and redundant ``durationFormatted``
    so video-details / channel-videos / search share one schema.
    """
    seed = raw
    if seed is None:
        seed = (
            card.get("durationSeconds")
            if card.get("durationSeconds") is not None
            else card.get("duration")
        )
    seconds, text = _coerce_duration_pair(seed)
    if seconds is None and card.get("durationText"):
        seconds, text = _coerce_duration_pair(card.get("durationText"))
    card.pop("duration", None)
    card.pop("durationFormatted", None)
    if seconds is not None:
        card["durationSeconds"] = seconds
    elif "durationSeconds" in card and card["durationSeconds"] is None:
        card.pop("durationSeconds", None)
    if text:
        card["durationText"] = text
    elif "durationText" in card and not card.get("durationText"):
        card.pop("durationText", None)
    return card


# Shared list-card keys — search + channel-videos. Presence is stable; null
# means "should have a value / scrape miss", omit only for not-applicable
# extras (embedId when unknown).
RUMBLE_ITEM_KEYS: tuple[str, ...] = (
    "platform",
    "id",
    "url",
    "type",
    "title",
    "channel",
    "channelUrl",
    "channelHandle",
    "channelVerified",
    "views",
    "likes",
    "dislikes",
    "comments",
    "publishedAt",
    "thumbnail",
    "isLive",
    "durationSeconds",
    "durationText",
    "shareUrl",
)
RUMBLE_CHANNEL_ITEM_KEYS: tuple[str, ...] = RUMBLE_ITEM_KEYS + (
    "numericId",
    "channelFollowers",
    "streams",
)


def _finalise_rumble_item(
    partial: dict[str, Any],
    keys: tuple[str, ...] = RUMBLE_ITEM_KEYS,
) -> dict[str, Any]:
    """Force a uniform key set — missing scrape → null, never a missing key."""
    out = {k: partial.get(k, None) for k in keys}
    # Optional extras that are only applicable when known (not null-padded).
    for key in ("embedId", "embedUrl", "description"):
        if key in partial and partial.get(key) not in (None, "", [], {}):
            out[key] = partial[key]
    return out


def _finalise_streams(
    streams: list[dict[str, Any]] | None,
    *,
    thumbnail_url: str | None = None,
    require_height: bool = True,
) -> list[dict[str, Any]]:
    """video-details streams[] — full 8-key shape with rendition meta."""
    return rumble_video_native.finalise_streams(
        streams,
        thumbnail_url=thumbnail_url,
        require_height=require_height,
    )


def _finalise_channel_streams(
    streams: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """channel-videos streams[] — lean {url, type, expiresAt} only."""
    return rumble_video_native.finalise_channel_streams(streams)


def _normalize_video(item: dict[str, Any]) -> dict[str, Any]:
    """Search list-card — always finalised to ``RUMBLE_ITEM_KEYS``."""
    url = _clean_url(item.get("url") or item.get("videoUrl") or item.get("sourceUrl"))
    duration_seconds, duration_text = _coerce_duration_pair(
        item.get("durationSeconds") if item.get("durationSeconds") is not None else item.get("duration")
    )
    is_live_raw = item.get("isLive") if item.get("isLive") is not None else item.get("is_live")
    is_live = bool(is_live_raw) if is_live_raw is not None else False
    channel_url = _clean_url(item.get("channelUrl"))
    channel_handle = safe_str(item.get("channelHandle"))
    if not channel_handle and channel_url:
        channel_handle = channel_url.rstrip("/").split("/")[-1] or None
    likes = parse_compact_count(
        item.get("likes") or item.get("likeCount") or item.get("likesCount")
    )
    dislikes = parse_compact_count(item.get("dislikes") or item.get("dislikeCount"))
    comments = parse_compact_count(item.get("commentsCount") or item.get("comments"))
    views = rumble_video_native.honest_views(
        parse_compact_count(item.get("views") or item.get("viewCount") or item.get("viewsCount")),
        likes=likes,
        comments=comments,
        dislikes=dislikes,
    )
    video_id = (
        safe_str(item.get("id") or item.get("videoId") or item.get("videoSlug") or item.get("permalink_id"))
        or extract_rumble_video_id(url or "")
    )
    partial: dict[str, Any] = {
        "platform": "rumble",
        "id": video_id,
        "url": url,
        "type": _rumble_content_type(url, is_live=is_live),
        "title": safe_str(item.get("title") or item.get("videoTitle")),
        "channel": safe_str(item.get("channel") or item.get("channelName") or item.get("author")),
        "channelUrl": channel_url,
        "channelHandle": channel_handle,
        "channelVerified": (
            bool(item.get("channelVerified"))
            if item.get("channelVerified") is not None
            else None
        ),
        "views": views,
        "likes": likes,
        "dislikes": dislikes,
        "comments": comments,
        "publishedAt": rumble_video_native.to_utc_published_at(
            item.get("uploadedAt")
            or item.get("uploadDate")
            or item.get("publishedAt")
            or item.get("date")
        ),
        "thumbnail": safe_str(item.get("thumbnail") or item.get("thumbnailUrl") or item.get("image")),
        "isLive": is_live,
        "shareUrl": (
            (safe_str(item.get("shareUrl")) or f"https://rumble.com/share/{video_id}")
            if video_id
            else None
        ),
    }
    _stamp_duration(partial, duration_seconds if duration_seconds is not None else duration_text)
    return _finalise_rumble_item(partial, RUMBLE_ITEM_KEYS)


def _normalize_az_video(item: dict[str, Any], *, include_description: bool = True) -> dict[str, Any]:
    """Map a row from the all-inclusive scraper (azzouzana) to the video schema."""
    by = item.get("by") if isinstance(item.get("by"), dict) else {}
    votes = item.get("rumble_votes") if isinstance(item.get("rumble_votes"), dict) else {}
    comments = item.get("comments") if isinstance(item.get("comments"), dict) else {}
    video_id = safe_str(item.get("permalink_id") or item.get("id"))
    # Real embed id only — never fall back to permalink_id (wrong video / 404).
    embed_id = safe_str(item.get("embed_id") or item.get("embedId"))
    if embed_id and video_id and embed_id == video_id:
        # Actor often echoes permalink as embed_id; that pair is usually broken
        # for long-form uploads. Drop until a distinct embed id is known.
        embed_id = None
    channel_url = _clean_url(by.get("url"))
    channel_handle = None
    if channel_url:
        channel_handle = channel_url.rstrip("/").split("/")[-1] or None
    duration_seconds, duration_text = _coerce_duration_pair(
        item.get("duration") if item.get("duration") is not None else item.get("durationSeconds")
    )
    raw_streams = [v for v in item.get("videos") or [] if isinstance(v, dict) and v.get("url")]
    live_raw = first_present(
        item.get("is_live"),
        item.get("livestream_status"),
        item.get("live"),
    )
    # Always emit isLive on channel lists so clients can separate fresh VODs
    # (zeros) from live — unknown upstream → false, not omitted.
    if live_raw is None:
        is_live = False
    elif isinstance(live_raw, str):
        is_live = live_raw.strip().lower() in {"1", "true", "live", "livestream"}
    else:
        is_live = bool(live_raw)
    url = _clean_url(item.get("url"))
    likes = safe_int(votes.get("num_votes_up")) if votes else None
    dislikes = safe_int(votes.get("num_votes_down")) if votes else None
    comment_count = safe_int(comments.get("count")) if comments else None
    views = rumble_video_native.honest_views(
        safe_int(item.get("views")),
        likes=likes,
        comments=comment_count,
        dislikes=dislikes,
    )
    # Channel rows use signed JWT playback URLs with no rendition meta — lean
    # {url,type,expiresAt}. Detail Apify fallback may still ship height bits.
    mapped_streams: list[dict[str, Any]] = []
    for v in raw_streams:
        if (safe_str(v.get("type")) or "").lower() == "audio":
            continue
        height = safe_int(v.get("height") or v.get("h"))
        width = safe_int(v.get("width") or v.get("w"))
        mapped_streams.append(
            {
                "url": safe_str(v.get("url")),
                "type": safe_str(v.get("type")) or "video/mp4",
                "width": width,
                "height": height,
                "bitrateKbps": safe_int(v.get("bitrate") or v.get("bitrateKbps")),
                "sizeBytes": safe_int(v.get("size") or v.get("sizeBytes")),
                "expiresAt": safe_str(v.get("expiresAt")),
            }
        )
    if include_description:
        final_streams = _finalise_streams(mapped_streams, require_height=False)
    else:
        final_streams = _finalise_channel_streams(mapped_streams)
    partial: dict[str, Any] = {
        "platform": "rumble",
        "id": video_id,
        "numericId": safe_int(item.get("video_id") or item.get("numericId")),
        "url": url,
        "type": _rumble_content_type(url, is_live=is_live),
        "title": safe_str(item.get("title")),
        "channel": safe_str(by.get("name") or by.get("title")),
        "channelUrl": channel_url,
        "channelHandle": channel_handle or safe_str(by.get("slug") or by.get("username")),
        "channelFollowers": safe_int(by.get("followers")),
        "channelVerified": bool(by.get("verified_badge")) if by else None,
        "views": views,
        "likes": likes,
        "dislikes": dislikes,
        "publishedAt": rumble_video_native.to_utc_published_at(item.get("upload_date")),
        "thumbnail": safe_str(item.get("thumb")),
        "comments": comment_count,
        "isLive": is_live,
        "streams": final_streams,
        "shareUrl": f"https://rumble.com/share/{video_id}" if video_id else None,
    }
    _stamp_duration(partial, duration_seconds if duration_seconds is not None else duration_text)
    if embed_id:
        partial["embedId"] = embed_id
        partial["embedUrl"] = f"https://rumble.com/embed/{embed_id}/"
    if include_description:
        # Detail path only — channel lists omit description (not applicable).
        desc = safe_str(
            item.get("description") or item.get("body") or item.get("summary") or item.get("desc")
        )
        if desc:
            partial["description"] = desc
        return partial
    return _finalise_rumble_item(partial, RUMBLE_CHANNEL_ITEM_KEYS)


def _normalize_comment(item: dict[str, Any]) -> dict[str, Any]:
    author = item.get("author") if isinstance(item.get("author"), dict) else None
    if author is None:
        author = item.get("user") if isinstance(item.get("user"), dict) else {}
    slug = safe_str(author.get("slug") or item.get("authorSlug") or item.get("username"))
    author_url = safe_str(author.get("url") or item.get("authorUrl"))
    if not author_url and slug:
        author_url = f"https://rumble.com/user/{slug}"
    replies_raw = item.get("replies")
    if isinstance(replies_raw, list):
        reply_count = len(replies_raw)
    else:
        # Upstream uses null (not []) when there are no replies — treat as 0.
        reply_count = safe_int(item.get("replyCount")) or 0
    votes = item.get("rumble_votes") if isinstance(item.get("rumble_votes"), dict) else {}
    # ISO / epoch / Rumble comment title= absolutes — relative text → null.
    published = rumble_video_native.to_utc_published_at(
        item.get("publishedAt")
        or item.get("createdAt")
        or item.get("date")
        or item.get("upload_date")
    )
    return {
        "platform": "rumble",
        "id": safe_str(item.get("id") or item.get("commentId")),
        "text": safe_str(item.get("text") or item.get("comment") or item.get("body")),
        "author": {
            "name": safe_str(
                author.get("name") or author.get("title") or slug
                or item.get("authorName")
            ),
            "url": author_url,
            "verified": bool(
                author.get("verified_badge")
                if author.get("verified_badge") is not None
                else author.get("verified")
            ),
        },
        "likes": safe_int(
            first_present(
                item.get("likes"),
                item.get("upvotes"),
                item.get("comment_score"),
                votes.get("num_votes_up"),
            )
        ),
        "replyCount": reply_count,
        "publishedAt": published,
    }


def _meta(page: str, key: str) -> str | None:
    pattern = rf'<meta\s+(?:property|name)=["\']{re.escape(key)}["\']\s+content=["\']([^"\']+)["\']'
    match = re.search(pattern, page, flags=re.IGNORECASE)
    if not match:
        pattern = rf'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']{re.escape(key)}["\']'
        match = re.search(pattern, page, flags=re.IGNORECASE)
    return html.unescape(match.group(1)).strip() if match else None


def _canonical_video_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


async def _fetch_video_page(url: str) -> dict[str, Any]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
    if resp.status_code >= 400:
        # Rumble serves datacenter IPs a Cloudflare 403; retry residentially.
        resp = await fetch_via_residential(url, headers=headers)
        if resp is None or resp.status_code >= 400:
            raise HTTPException(status_code=404, detail="Video not found")

    page = resp.text
    parsed = rumble_video_native.parse_video_html(page, url=str(resp.url) or url)
    if parsed and parsed.get("title"):
        return parsed

    video_id = extract_rumble_video_id(str(resp.url)) or extract_rumble_video_id(url)
    title = _meta(page, "og:title")
    description = _meta(page, "og:description") or _meta(page, "description")
    thumbnail = _meta(page, "og:image")
    canonical = _meta(page, "og:url") or str(resp.url)
    if not (title or description or thumbnail):
        raise HTTPException(status_code=404, detail="Video not found")

    # Last-resort OG-only card — engagement unknown, so null (not 0).
    return _stamp_duration(
        {
            "platform": "rumble",
            "id": safe_str(video_id),
            "url": safe_str(canonical),
            "type": _rumble_content_type(canonical, is_live=None),
            "title": safe_str(title),
            "description": safe_str(description),
            "channel": None,
            "channelUrl": None,
            "views": None,
            "likes": None,
            "dislikes": None,
            "publishedAt": None,
            "thumbnail": safe_str(thumbnail),
            "comments": None,
            "isLive": None,
            "streams": [],
        }
    )


@router.get(
    "/video-details",
    summary="Rumble video metadata + stats (null engagement when unknown; streams + captions[])",
)
async def video_details(
    url: str = Query(..., description="Rumble video URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_rumble_video_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/rumble/video-details",
        platform="rumble",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Decodo JSON-LD first (CF blocks datacenter/residential).
            native = await rumble_video_native.video_details_native(_canonical_video_url(url))
            if native and native.get("title"):
                ctx["source"] = "direct"
                # Never ship raw quality-keyed embed dump.
                native.pop("media", None)
                thumb = native.get("thumbnailTrack")
                thumb_url = (
                    safe_str(thumb.get("url"))
                    if isinstance(thumb, dict)
                    else None
                )
                native["streams"] = _finalise_streams(
                    native.get("streams") if isinstance(native.get("streams"), list) else [],
                    thumbnail_url=thumb_url,
                    require_height=True,
                )
                if isinstance(native.get("audioStreams"), list):
                    native["audioStreams"] = rumble_video_native.finalise_audio_streams(
                        native["audioStreams"]
                    )
                if isinstance(native.get("captions"), list):
                    native["captions"] = rumble_video_native.finalise_captions(
                        native["captions"]
                    )
                if isinstance(thumb, dict):
                    native["thumbnailTrack"] = rumble_video_native.finalise_thumbnail_track(
                        thumb
                    )
                # Drop null optional flags (likesIsApproximate when likes unknown).
                for key in list(native.keys()):
                    if native.get(key) is None and key in {
                        "likesIsApproximate",
                        "width",
                        "height",
                        "captions",
                        "audioStreams",
                        "thumbnailTrack",
                    }:
                        native.pop(key, None)
                return _stamp_duration(native)

            apify = get_apify()
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_RUMBLE_DETAILS,
                    {"startUrls": [_canonical_video_url(url)]},
                    max_items=1,
                )
            except Exception:
                items = []
            rows = [i for i in items if isinstance(i, dict) and i.get("object_type") == "video"]
            if rows:
                ctx["source"] = "apify"
                return _normalize_az_video(rows[0])
            ctx["source"] = "direct"
            return await _fetch_video_page(url)

        data = await cached_or_run(
            endpoint="rumble.video-details",
            params={"url": url, "v": 12},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _raise_rumble_transcript_unavailable(
    *,
    code: str,
    available: list[dict[str, str]],
    language: str | None,
) -> None:
    """404 with diagnostic body. billed_call never charges status >= 400."""
    if code == "language_not_available":
        reason = (
            f"No caption track matches language '{(language or '').strip()}'."
        )
    else:
        code = "no_captions"
        reason = "Rumble publishes no caption track for this video"
    raise HTTPException(
        status_code=404,
        detail={
            "code": code,
            "reason": reason,
            "availableLanguages": available,
        },
    )


@router.get(
    "/video/transcript",
    summary="Rumble video caption transcript (published .vtt, not STT)",
    description=(
        "Fetches the caption track Rumble already exposes on video-details, "
        "parses the .vtt, and returns timed segments. Does not run "
        "speech-to-text. Missing captions or a language mismatch return 404 "
        f"and cost 0 credits. Flat {CREDIT_TRANSCRIPT} credit on success."
    ),
)
async def video_transcript(
    url: str = Query(..., description="Rumble video URL"),
    language: str | None = Query(
        None,
        description=(
            "Caption language code (e.g. en or en-auto). When set, that track "
            "(or a matching base language like en → en-auto) is required — "
            "never a silent fallback. Missing language → 404 "
            "language_not_available with availableLanguages. Omit to use the "
            "first track and report which one was used."
        ),
    ),
    cache: bool = Query(
        False,
        description="Set true to use the 24h cache. Default false — always fetch fresh data.",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    video_id = _require_rumble_video_url(url)
    canon = _canonical_video_url(url)

    async with billed_call(
        caller=caller,
        endpoint="/v1/rumble/video/transcript",
        platform="rumble",
        resource_url=canon,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await rumble_video_native.video_details_native(canon)
            if not native or not native.get("title"):
                ctx["credits_override"] = 0
                raise HTTPException(status_code=404, detail="Video not found")

            captions = (
                native.get("captions")
                if isinstance(native.get("captions"), list)
                else []
            )
            track, err, available = rumble_transcript.pick_caption_track(
                captions, language
            )
            if err or not track:
                ctx["credits_override"] = 0
                _raise_rumble_transcript_unavailable(
                    code=err or "no_captions",
                    available=available,
                    language=language,
                )

            try:
                vtt = await rumble_transcript.fetch_vtt(track["url"])
            except Exception as exc:
                ctx["credits_override"] = 0
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "caption_fetch_failed",
                        "message": "Failed to download the caption track",
                        "reason": str(exc),
                    },
                ) from exc

            duration = native.get("durationSeconds")
            try:
                duration_i = int(duration) if duration is not None else None
            except (TypeError, ValueError):
                duration_i = None

            payload = rumble_transcript.build_transcript_payload(
                video_id=safe_str(native.get("id")) or video_id,
                url=safe_str(native.get("url")) or canon,
                track=track,
                vtt_body=vtt,
                duration_seconds=duration_i,
            )
            if not payload.get("segments"):
                ctx["credits_override"] = 0
                _raise_rumble_transcript_unavailable(
                    code="no_captions",
                    available=available,
                    language=language,
                )
            ctx["source"] = "captions"
            return payload

        data = await cached_or_run(
            endpoint="rumble.video-transcript",
            params={"url": canon, "language": language or "", "v": 1},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/channel-videos", summary="List videos for a Rumble channel")
async def channel_videos(
    url: str = Query(..., description="Rumble channel URL, e.g. https://rumble.com/c/name"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    channel = _require_rumble_channel_url(url)
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/rumble/channel-videos",
        platform="rumble",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            # The keyword actor can't resolve channel URLs; the all-inclusive
            # scraper lists channel uploads directly.
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_RUMBLE_DETAILS,
                {
                    "startUrls": [f"https://rumble.com/c/{channel}"],
                    "scrapeChannelVideos": True,
                    "maxVideoToScrapeFromChannel": limit,
                },
                max_items=limit,
            )
            rows = [i for i in items if isinstance(i, dict) and i.get("object_type") == "video"]
            # Channel scrape omits per-video description — don't ship always-null keys.
            videos = [_normalize_az_video(i, include_description=False) for i in rows][:limit]
            return {"channel": channel, "totalReturned": len(videos), "videos": videos}

        data = await cached_or_run(
            endpoint="rumble.channel-videos",
            params={"channel": channel, "limit": limit, "v": 12},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["videos"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/comments", summary="Rumble video comments")
async def comments(
    url: str = Query(..., description="Rumble video URL"),
    limit: int = Query(
        50,
        ge=1,
        le=500,
        description="How many top-level comments to return (1–500). Flat 2 credits per call.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_rumble_video_url(url)
    settings = get_settings()
    # Flat fee: Decodo HTML path is cheap; Apify fallback is rare and covered
    # by the same 2-credit charge.
    async with billed_call(
        caller=caller,
        endpoint="/v1/rumble/comments",
        platform="rumble",
        resource_url=url,
        base_credits=CREDIT_COMMENTS_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await rumble_comments_native.comments_native(url, limit)
            if native is not None:
                # Always route through the comment normalizer (ISO publishedAt).
                ctx["source"] = "direct"
                comments = [_normalize_comment(i) for i in native][:limit]
                return {"url": url, "totalReturned": len(comments), "comments": comments}

            apify = get_apify()
            # The all-inclusive scraper embeds the comment thread on the video
            # row itself; prefer it since the keyword actor often returns none.
            try:
                rows = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_RUMBLE_DETAILS,
                    {"startUrls": [_canonical_video_url(url)]},
                    max_items=1,
                )
            except Exception:
                rows = []
            comment_items: list[dict[str, Any]] = []
            for row in rows:
                if isinstance(row, dict) and isinstance(row.get("comments"), dict):
                    comment_items = [c for c in row["comments"].get("items") or [] if isinstance(c, dict)]
                    break
            if not comment_items:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_RUMBLE_COMMENTS,
                    {
                        "queries": [url],
                        "contentTypes": ["videos"],
                        "maxItems": 1,
                        "includeComments": True,
                    },
                    max_items=limit + 1,
                )
                comment_items = [
                    i
                    for i in items
                    if (i.get("type") == "comment" or i.get("comment") or i.get("commentId"))
                ]
            comments = [_normalize_comment(i) for i in comment_items][:limit]
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(comments), "comments": comments}

        data = await cached_or_run(
            endpoint="rumble.comments",
            params={"url": url, "limit": limit, "v": 7},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/search", summary="Search Rumble videos by keyword")
async def rumble_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/rumble/search",
        platform="rumble",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await rumble_video_native.search_native(q, limit=limit)
            if native:
                ctx["source"] = "direct"
                results = [_normalize_video(r) for r in native][:limit]
                return {"query": q, "totalReturned": len(results), "results": results}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_RUMBLE,
                {"searchQueries": [q], "maxItems": limit},
                max_items=limit,
            )
            results = [_normalize_video(i) for i in items][:limit]
            if not results:
                raise HTTPException(status_code=404, detail="No videos found")
            ctx["source"] = "apify"
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="rumble.search",
            params={"q": q, "limit": limit, "v": 7},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
