"""Rumble endpoints: video details, channel videos, search.

Backed by a config-driven Rumble actor. Field mappings are defensive.
"""

from __future__ import annotations

import html
import math
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import extract_rumble_channel, extract_rumble_video_id

router = APIRouter()

CREDIT_DETAILS = 1
RATE = 0.6


def _scaled(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


def _normalize_video(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "platform": "rumble",
        "id": safe_str(item.get("id") or item.get("videoId") or item.get("videoSlug")),
        "url": safe_str(item.get("url") or item.get("videoUrl") or item.get("sourceUrl")),
        "title": safe_str(item.get("title") or item.get("videoTitle")),
        "description": safe_str(item.get("description")),
        "channel": safe_str(item.get("channel") or item.get("channelName") or item.get("author")),
        "channelUrl": safe_str(item.get("channelUrl")),
        "views": safe_int(item.get("views") or item.get("viewCount") or item.get("viewsCount")),
        "likes": safe_int(
            item.get("likes")
            or item.get("likeCount")
            or item.get("likesCount")
            or item.get("engagementCount")
            or item.get("votes")
        ),
        "dislikes": safe_int(item.get("dislikes") or item.get("dislikeCount")),
        "duration": safe_str(item.get("duration") or item.get("durationSeconds")),
        "publishedAt": safe_str(
            item.get("uploadedAt")
            or item.get("uploadDate")
            or item.get("publishedAt")
            or item.get("date")
        ),
        "thumbnail": safe_str(item.get("thumbnail") or item.get("thumbnailUrl") or item.get("image")),
        "comments": safe_int(item.get("commentsCount") or item.get("comments")),
    }


def _normalize_comment(item: dict[str, Any]) -> dict[str, Any]:
    author = item.get("author") or item.get("user") or {}
    return {
        "platform": "rumble",
        "id": safe_str(item.get("id") or item.get("commentId")),
        "text": safe_str(item.get("text") or item.get("comment") or item.get("body")),
        "author": {
            "name": safe_str(author.get("name") or item.get("authorName") or item.get("username")),
            "url": safe_str(author.get("url") or item.get("authorUrl")),
        },
        "likes": safe_int(item.get("likes") or item.get("upvotes")),
        "createdAt": safe_str(item.get("createdAt") or item.get("date") or item.get("publishedAt")),
        "videoUrl": safe_str(item.get("videoUrl") or item.get("sourceUrl")),
    }


def _normalize_transcript(item: dict[str, Any]) -> dict[str, Any]:
    segments = item.get("segments") or item.get("transcript") or item.get("captions") or []
    text = item.get("text") or item.get("plainText") or item.get("transcriptText")
    if not text and isinstance(segments, list):
        text = " ".join(
            safe_str(s.get("text") if isinstance(s, dict) else s) or ""
            for s in segments
        ).strip()
    return {
        "platform": "rumble",
        "url": safe_str(item.get("url") or item.get("videoUrl") or item.get("sourceUrl")),
        "language": safe_str(item.get("language")),
        "title": safe_str(item.get("title") or item.get("videoTitle")),
        "text": safe_str(text),
        "segments": segments if isinstance(segments, list) else [],
    }


def _meta(page: str, key: str) -> str | None:
    pattern = rf'<meta\s+(?:property|name)=["\']{re.escape(key)}["\']\s+content=["\']([^"\']+)["\']'
    match = re.search(pattern, page, flags=re.IGNORECASE)
    if not match:
        pattern = rf'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']{re.escape(key)}["\']'
        match = re.search(pattern, page, flags=re.IGNORECASE)
    return html.unescape(match.group(1)).strip() if match else None


def _query_from_video_url(url: str) -> str | None:
    match = re.search(r"/v[^/]*--([^/?#]+)\.html", url)
    if not match:
        match = re.search(r"/v[^/]*-([^/?#]+)\.html", url)
    if not match:
        return None
    query = re.sub(r"[-_]+", " ", match.group(1)).strip()
    return query or None


async def _fetch_video_page(url: str) -> dict[str, Any]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
    if resp.status_code >= 400:
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
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_rumble_video_id(url):
        raise HTTPException(status_code=400, detail="Invalid Rumble video URL")
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
                    settings.APIFY_ACTOR_RUMBLE,
                    {"searchQueries": [url], "maxItems": 1},
                    max_items=1,
                )
            except Exception:
                items = []
            if not items:
                query = _query_from_video_url(url)
                if query:
                    try:
                        items = await apify.run_actor_sync(
                            settings.APIFY_ACTOR_RUMBLE,
                            {"searchQueries": [query], "maxItems": 1},
                            max_items=1,
                        )
                    except Exception:
                        items = []
            if items:
                return _normalize_video(items[0])
            return await _fetch_video_page(url)

        data = await cached_or_run(
            endpoint="rumble.video-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/channel-videos", summary="List videos for a Rumble channel")
async def channel_videos(
    url: str = Query(..., description="Rumble channel URL, e.g. https://rumble.com/c/name"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    channel = extract_rumble_channel(url)
    if not channel:
        raise HTTPException(status_code=400, detail="Invalid Rumble channel URL")
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
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_RUMBLE,
                {"searchQueries": [url], "maxItems": limit},
                max_items=limit,
            )
            videos = [_normalize_video(i) for i in items][:limit]
            return {"channel": channel, "totalReturned": len(videos), "videos": videos}

        data = await cached_or_run(
            endpoint="rumble.channel-videos",
            params={"channel": channel, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["videos"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/transcript", summary="Rumble video transcript")
async def transcript(
    url: str = Query(..., description="Rumble video URL"),
    language: str = Query("en", min_length=2, max_length=8),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_rumble_video_id(url):
        raise HTTPException(status_code=400, detail="Invalid Rumble video URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/rumble/transcript",
        platform="rumble",
        resource_url=url,
        base_credits=3,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_RUMBLE_TRANSCRIPT,
                {"url": url, "language": language, "format": "json"},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Transcript not found")
            return _normalize_transcript(items[0])

        data = await cached_or_run(
            endpoint="rumble.transcript",
            params={"url": url, "language": language},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Rumble video comments")
async def comments(
    url: str = Query(..., description="Rumble video URL"),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_rumble_video_id(url):
        raise HTTPException(status_code=400, detail="Invalid Rumble video URL")
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
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_RUMBLE_COMMENTS,
                {
                    "queries": [url],
                    "contentTypes": ["videos"],
                    "maxItems": 1,
                    "includeComments": True,
                },
                max_items=limit + 1,
            )
            comments = [
                _normalize_comment(i)
                for i in items
                if (i.get("type") == "comment" or i.get("comment") or i.get("commentId"))
            ][:limit]
            return {"url": url, "totalReturned": len(comments), "comments": comments}

        data = await cached_or_run(
            endpoint="rumble.comments",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["comments"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search", summary="Search Rumble videos by keyword")
async def rumble_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=200),
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
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
