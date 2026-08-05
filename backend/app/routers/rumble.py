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
from app.services import rumble_comments_native, rumble_video_native
from app.utils.formatters import first_present, parse_compact_count, safe_int, safe_str
from app.utils.url import (
    extract_rumble_channel,
    extract_rumble_video_id,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
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


def _dedupe_streams(streams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Prefer unique playable URLs; collapse duplicate quality labels."""
    seen_url: set[str] = set()
    seen_quality: set[str] = set()
    out: list[dict[str, Any]] = []
    for s in streams:
        if not isinstance(s, dict):
            continue
        url = safe_str(s.get("url"))
        if not url or url in seen_url:
            continue
        quality = (safe_str(s.get("quality")) or "").lower()
        stype = (safe_str(s.get("type")) or "").lower()
        # Keep first HLS auto; dedupe repeated 1080p mp4 rows.
        qkey = f"{stype}:{quality}" if quality else url
        if quality and quality != "auto" and qkey in seen_quality:
            continue
        seen_url.add(url)
        if quality and quality != "auto":
            seen_quality.add(qkey)
        row: dict[str, Any] = {
            "url": url,
            "type": safe_str(s.get("type")),
            "quality": safe_str(s.get("quality")),
        }
        expires = safe_str(s.get("expiresAt"))
        if not expires:
            from app.utils.media_urls import cdn_expires_at

            expires = cdn_expires_at(url)
        if expires:
            row["expiresAt"] = expires
        out.append(row)
        if len(out) >= 12:
            break
    return out


def _normalize_video(item: dict[str, Any]) -> dict[str, Any]:
    url = _clean_url(item.get("url") or item.get("videoUrl") or item.get("sourceUrl"))
    duration_seconds, duration_text = _coerce_duration_pair(
        item.get("durationSeconds") if item.get("durationSeconds") is not None else item.get("duration")
    )
    is_live = item.get("isLive") if item.get("isLive") is not None else item.get("is_live")
    out: dict[str, Any] = {
        "platform": "rumble",
        "id": safe_str(item.get("id") or item.get("videoId") or item.get("videoSlug"))
        or extract_rumble_video_id(url or ""),
        "url": url,
        "type": _rumble_content_type(url, is_live=bool(is_live) if is_live is not None else None),
        "title": safe_str(item.get("title") or item.get("videoTitle")),
        # Search actor never returns description — omit always-null key.
        "channel": safe_str(item.get("channel") or item.get("channelName") or item.get("author")),
        "channelUrl": _clean_url(item.get("channelUrl")),
        "views": parse_compact_count(item.get("views") or item.get("viewCount") or item.get("viewsCount")),
        # Do not map engagementCount/votes blobs into likes — missing stays null.
        "likes": parse_compact_count(
            item.get("likes") or item.get("likeCount") or item.get("likesCount")
        ),
        "dislikes": parse_compact_count(item.get("dislikes") or item.get("dislikeCount")),
        "durationSeconds": duration_seconds,
        "durationText": duration_text,
        "durationFormatted": rumble_video_native._duration_formatted(duration_seconds),
        "publishedAt": safe_str(
            item.get("uploadedAt")
            or item.get("uploadDate")
            or item.get("publishedAt")
            or item.get("date")
        ),
        "thumbnail": safe_str(item.get("thumbnail") or item.get("thumbnailUrl") or item.get("image")),
        "comments": parse_compact_count(item.get("commentsCount") or item.get("comments")),
    }
    # Never invent embedUrl from the page permalink id — Rumble's embed id is
    # often different (page v7cv2cc → embed v7aoh22). Fabricated embeds 404.
    video_id = safe_str(item.get("id") or item.get("permalink_id"))
    embed_id = safe_str(item.get("embedId") or item.get("embed_id"))
    if embed_id and video_id and embed_id == video_id:
        embed_id = None
    if embed_id:
        out["embedId"] = embed_id
        out["embedUrl"] = f"https://rumble.com/embed/{embed_id}/"
    return out


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
    streams = [v for v in item.get("videos") or [] if isinstance(v, dict) and v.get("url")]
    live_raw = first_present(item.get("is_live"), item.get("livestream_status"))
    is_live = bool(live_raw) if live_raw is not None else None
    url = _clean_url(item.get("url"))
    out: dict[str, Any] = {
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
        # Missing engagement stays null — never invent 0.
        "views": safe_int(item.get("views")),
        "likes": safe_int(votes.get("num_votes_up")) if votes else None,
        "dislikes": safe_int(votes.get("num_votes_down")) if votes else None,
        "durationSeconds": duration_seconds,
        "durationText": duration_text,
        "durationFormatted": rumble_video_native._duration_formatted(duration_seconds),
        "publishedAt": safe_str(item.get("upload_date")),
        "thumbnail": safe_str(item.get("thumb")),
        "comments": safe_int(comments.get("count")) if comments else None,
        "isLive": is_live,
        "streams": _dedupe_streams(
            [
                {
                    "url": safe_str(v.get("url")),
                    "type": safe_str(v.get("type")),
                    "quality": safe_str(v.get("quality_text") or v.get("resolution")),
                    "expiresAt": safe_str(v.get("expiresAt")),
                }
                for v in streams
            ]
        ),
    }
    if embed_id:
        out["embedId"] = embed_id
        out["embedUrl"] = f"https://rumble.com/embed/{embed_id}/"
    if video_id:
        out["shareUrl"] = f"https://rumble.com/share/{video_id}"
    if include_description:
        # Channel-list rows never include description; single-video / page
        # fallback may. Keep the key only when the caller wants it.
        out["description"] = safe_str(
            item.get("description") or item.get("body") or item.get("summary") or item.get("desc")
        )
    # Drop empty optional keys.
    for key in list(out.keys()):
        if out.get(key) in (None, "", [], {}):
            out.pop(key, None)
    return out


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
            "verified": bool(author.get("verified_badge")),
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
        "createdAt": safe_str(item.get("createdAt") or item.get("date") or item.get("publishedAt")),
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
    return {
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
        "durationSeconds": None,
        "durationText": None,
        "publishedAt": None,
        "thumbnail": safe_str(thumbnail),
        "comments": None,
        "isLive": None,
        "streams": [],
    }


@router.get(
    "/video-details",
    summary="Rumble video metadata + stats (null engagement when unknown; captions + media)",
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
                return native

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
            params={"url": url, "v": 7},
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
            params={"channel": channel, "limit": limit, "v": 6},
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
                ctx["source"] = "direct"
                return {"url": url, "totalReturned": len(native), "comments": native}

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
            params={"url": url, "limit": limit, "v": 4},
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
                return {"query": q, "totalReturned": len(native), "results": native}

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
            params={"q": q, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
