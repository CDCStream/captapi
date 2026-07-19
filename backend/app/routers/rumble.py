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
from app.utils.formatters import parse_compact_count, safe_int, safe_str
from app.utils.url import (
    extract_rumble_channel,
    extract_rumble_video_id,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
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


def _normalize_video(item: dict[str, Any]) -> dict[str, Any]:
    url = _clean_url(item.get("url") or item.get("videoUrl") or item.get("sourceUrl"))
    return {
        "platform": "rumble",
        "id": safe_str(item.get("id") or item.get("videoId") or item.get("videoSlug")) or extract_rumble_video_id(url or ""),
        "url": url,
        "title": safe_str(item.get("title") or item.get("videoTitle")),
        "description": safe_str(item.get("description")),
        "channel": safe_str(item.get("channel") or item.get("channelName") or item.get("author")),
        "channelUrl": _clean_url(item.get("channelUrl")),
        "views": parse_compact_count(item.get("views") or item.get("viewCount") or item.get("viewsCount")),
        "likes": parse_compact_count(
            item.get("likes")
            or item.get("likeCount")
            or item.get("likesCount")
            or item.get("engagementCount")
            or item.get("votes")
        ),
        "dislikes": parse_compact_count(item.get("dislikes") or item.get("dislikeCount")),
        "duration": safe_str(item.get("duration") or item.get("durationSeconds")),
        "publishedAt": safe_str(
            item.get("uploadedAt")
            or item.get("uploadDate")
            or item.get("publishedAt")
            or item.get("date")
        ),
        "thumbnail": safe_str(item.get("thumbnail") or item.get("thumbnailUrl") or item.get("image")),
        "comments": parse_compact_count(item.get("commentsCount") or item.get("comments")),
    }


def _normalize_az_video(item: dict[str, Any], *, include_description: bool = True) -> dict[str, Any]:
    """Map a row from the all-inclusive scraper (azzouzana) to the video schema."""
    by = item.get("by") if isinstance(item.get("by"), dict) else {}
    votes = item.get("rumble_votes") if isinstance(item.get("rumble_votes"), dict) else {}
    comments = item.get("comments") if isinstance(item.get("comments"), dict) else {}
    video_id = safe_str(item.get("permalink_id") or item.get("id"))
    streams = [v for v in item.get("videos") or [] if isinstance(v, dict) and v.get("url")]
    out: dict[str, Any] = {
        "platform": "rumble",
        "id": video_id,
        "url": _clean_url(item.get("url")),
        "embedUrl": f"https://rumble.com/embed/{video_id}/" if video_id else None,
        "title": safe_str(item.get("title")),
        "channel": safe_str(by.get("name") or by.get("title")),
        "channelUrl": _clean_url(by.get("url")),
        "channelFollowers": safe_int(by.get("followers")),
        "channelVerified": bool(by.get("verified_badge")),
        "views": safe_int(item.get("views")),
        "likes": safe_int(votes.get("num_votes_up")),
        "dislikes": safe_int(votes.get("num_votes_down")),
        "duration": safe_str(item.get("duration")),
        "publishedAt": safe_str(item.get("upload_date")),
        "thumbnail": safe_str(item.get("thumb")),
        "comments": safe_int(comments.get("count")),
        "isLive": bool(item.get("is_live") or item.get("livestream_status")),
        "streams": [
            {
                "url": safe_str(v.get("url")),
                "type": safe_str(v.get("type")),
                "quality": safe_str(v.get("quality_text") or v.get("resolution")),
            }
            for v in streams[:10]
        ],
    }
    if include_description:
        # Channel-list rows never include description; single-video / page
        # fallback may. Keep the key only when the caller wants it.
        out["description"] = safe_str(
            item.get("description") or item.get("body") or item.get("summary") or item.get("desc")
        )
    return out


def _normalize_comment(item: dict[str, Any]) -> dict[str, Any]:
    author = item.get("author") or item.get("user") or {}
    replies = item.get("replies") if isinstance(item.get("replies"), list) else []
    return {
        "platform": "rumble",
        "id": safe_str(item.get("id") or item.get("commentId")),
        "text": safe_str(item.get("text") or item.get("comment") or item.get("body")),
        "author": {
            "name": safe_str(
                author.get("name") or author.get("title") or author.get("slug")
                or item.get("authorName") or item.get("username")
            ),
            "url": safe_str(author.get("url") or item.get("authorUrl")),
            "verified": bool(author.get("verified_badge")),
        },
        "likes": safe_int(item.get("likes") or item.get("upvotes") or item.get("comment_score")),
        "replyCount": len(replies) or safe_int(item.get("replyCount")),
        "createdAt": safe_str(item.get("createdAt") or item.get("date") or item.get("publishedAt")),
        "videoUrl": safe_str(item.get("videoUrl") or item.get("sourceUrl")),
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
    video_id = extract_rumble_video_id(str(resp.url)) or extract_rumble_video_id(url)
    title = _meta(page, "og:title")
    description = _meta(page, "og:description") or _meta(page, "description")
    thumbnail = _meta(page, "og:image")
    canonical = _meta(page, "og:url") or str(resp.url)
    if not (title or description or thumbnail):
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "platform": "rumble",
        "id": safe_str(video_id),
        "url": safe_str(canonical),
        "title": safe_str(title),
        "description": safe_str(description),
        "channel": None,
        "channelUrl": None,
        "views": 0,
        "likes": 0,
        "dislikes": 0,
        "duration": None,
        "publishedAt": None,
        "thumbnail": safe_str(thumbnail),
        "comments": 0,
    }


@router.get("/video-details", summary="Rumble video metadata + stats")
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
                return _normalize_az_video(rows[0])
            return await _fetch_video_page(url)

        data = await cached_or_run(
            endpoint="rumble.video-details",
            params={"url": url, "v": 3},
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
            params={"channel": channel, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["videos"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/comments", summary="Rumble video comments")
async def comments(
    url: str = Query(..., description="Rumble video URL"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_rumble_video_url(url)
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/rumble/comments",
        platform="rumble",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
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
            return {"url": url, "totalReturned": len(comments), "comments": comments}

        data = await cached_or_run(
            endpoint="rumble.comments",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["comments"]), RATE, 2)
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
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_RUMBLE,
                {"searchQueries": [q], "maxItems": limit},
                max_items=limit,
            )
            results = [_normalize_video(i) for i in items][:limit]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="rumble.search",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
