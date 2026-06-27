"""Rumble endpoints: video details, channel videos, search.

Backed by a config-driven Rumble actor. Field mappings are defensive.
"""

from __future__ import annotations

import math
from typing import Any

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
        "id": safe_str(item.get("id") or item.get("videoId")),
        "url": safe_str(item.get("url") or item.get("videoUrl")),
        "title": safe_str(item.get("title")),
        "description": safe_str(item.get("description")),
        "channel": safe_str(item.get("channel") or item.get("channelName") or item.get("author")),
        "channelUrl": safe_str(item.get("channelUrl")),
        "views": safe_int(item.get("views") or item.get("viewCount")),
        "likes": safe_int(item.get("likes") or item.get("likeCount") or item.get("votes")),
        "dislikes": safe_int(item.get("dislikes") or item.get("dislikeCount")),
        "duration": safe_str(item.get("duration")),
        "publishedAt": safe_str(item.get("uploadDate") or item.get("publishedAt") or item.get("date")),
        "thumbnail": safe_str(item.get("thumbnail") or item.get("thumbnailUrl") or item.get("image")),
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
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_RUMBLE,
                {"startUrls": [{"url": url}], "maxItems": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            return _normalize_video(items[0])

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
                {"startUrls": [{"url": url}], "maxItems": limit},
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
                {"search": q, "maxItems": limit},
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
