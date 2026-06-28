"""Twitch public data endpoints."""

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
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

RATE = 1.7


def _scaled(n: int, rate: float = RATE, minimum: int = 2) -> int:
    return max(minimum, math.ceil(n * rate))


def _target(value: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "twitch":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "twitch", "https://www.twitch.tv/channel"),
        )
    value = (value or "").strip().rstrip("/")
    if "twitch.tv/" in value:
        value = value.split("twitch.tv/", 1)[1].split("/", 1)[0]
    return value.lstrip("@")


def _run_input(mode: str, targets: list[str], limit: int = 30) -> dict[str, Any]:
    return {
        "mode": mode,
        "targets": targets,
        "maxResults": min(limit, 30),
        "clipPeriod": "LAST_WEEK",
        "includeRecentVideos": True,
        "includeTopClips": False,
        "recentVideosLimit": min(limit, 30),
        "topClipsLimit": min(limit, 30),
    }


def _video(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "platform": "twitch",
        "id": safe_str(item.get("id") or item.get("videoId")),
        "url": safe_str(item.get("url") or item.get("videoUrl") or item.get("sourceUrl")),
        "title": safe_str(item.get("title")),
        "createdAt": safe_str(item.get("createdAt") or item.get("publishedAt")),
        "durationSeconds": safe_int(item.get("durationSeconds") or item.get("lengthSeconds")),
        "views": safe_int(item.get("viewCount") or item.get("views")),
        "thumbnail": safe_str(item.get("thumbnailUrl") or item.get("thumbnailURL") or item.get("thumbnail")),
        "game": safe_str(item.get("gameName") or item.get("currentGame")),
        "broadcaster": safe_str(item.get("broadcasterName") or item.get("displayName") or item.get("login")),
    }


def _profile(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "platform": "twitch",
        "id": safe_str(item.get("id") or item.get("channelId")),
        "login": safe_str(item.get("login")),
        "displayName": safe_str(item.get("displayName") or item.get("name")),
        "url": safe_str(item.get("sourceUrl") or item.get("url")),
        "description": safe_str(item.get("description")),
        "followers": safe_int(item.get("followersCount") or item.get("followers")),
        "profileImage": safe_str(item.get("profileImageUrl") or item.get("profileImageURL")),
        "bannerImage": safe_str(item.get("bannerImageUrl") or item.get("bannerImageURL")),
        "isPartner": bool(item.get("isPartner")),
        "isAffiliate": bool(item.get("isAffiliate")),
        "isLive": bool(item.get("isLive")),
        "stream": {
            "title": safe_str(item.get("streamTitle")),
            "game": safe_str(item.get("currentGame")),
            "viewers": safe_int(item.get("currentViewers")),
            "startedAt": safe_str(item.get("startedAt")),
        },
        "recentVideos": [_video(v) for v in item.get("recentVideos", []) if isinstance(v, dict)],
        "topClips": [_video(v) for v in item.get("topClips", []) if isinstance(v, dict)],
        "schedule": item.get("nextSchedule") or item.get("schedule") or [],
        "createdAt": safe_str(item.get("createdAt")),
    }


async def _channel(username: str) -> dict[str, Any]:
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_TWITCH,
        _run_input("channels", [username], 5),
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Twitch channel not found")
    return _profile(items[0])


@router.get("/profile", summary="Twitch channel profile")
async def profile(
    url: str = Query(..., description="Twitch channel URL or username"),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    async with billed_call(caller=caller, endpoint="/v1/twitch/profile", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=9) as ctx:
        data = await cached_or_run("twitch.profile", {"username": username}, lambda: _channel(username), ctx)
        return ApiResponse(data=data)


@router.get("/user-videos", summary="Twitch channel videos")
async def user_videos(
    url: str = Query(..., description="Twitch channel URL or username"),
    limit: int = Query(20, ge=1, le=30),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    cost = _scaled(limit)
    async with billed_call(caller=caller, endpoint="/v1/twitch/user-videos", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_TWITCH,
                _run_input("channels", [username], limit),
                max_items=1,
            )
            videos = [_video(v) for v in (items[0].get("recentVideos") if items else []) or [] if isinstance(v, dict)]
            return {"platform": "twitch", "username": username, "totalReturned": len(videos), "videos": videos[:limit]}

        data = await cached_or_run("twitch.user-videos", {"username": username, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["videos"]))
        return ApiResponse(data=data)


@router.get("/user-schedule", summary="Twitch channel schedule")
async def user_schedule(
    url: str = Query(..., description="Twitch channel URL or username"),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    async with billed_call(caller=caller, endpoint="/v1/twitch/user-schedule", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=34) as ctx:
        async def _run() -> dict[str, Any]:
            channel = await _channel(username)
            return {"platform": "twitch", "username": username, "schedule": channel.get("schedule")}

        data = await cached_or_run("twitch.user-schedule", {"username": username}, _run, ctx)
        return ApiResponse(data=data)


@router.get("/clip", summary="Twitch clip metadata")
async def clip(
    url: str = Query(..., description="Twitch clip URL, channel URL, or username"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/twitch/clip", platform="twitch", resource_url=url, base_credits=9) as ctx:
        async def _run() -> dict[str, Any]:
            # The URL-capable actor handles direct clip URLs. If the input is a
            # channel, it returns that channel's top clip metadata.
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_TWITCH_URL,
                {"mode": "url", "urls": [url], "includeMediaUrls": True, "maxResults": 1, "maxPages": 1},
                max_items=1,
            )
            if not items:
                target = _target(url)
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_TWITCH,
                    _run_input("clips", [target], 1),
                    max_items=1,
                )
            if not items:
                raise HTTPException(status_code=404, detail="Twitch clip not found")
            return _video(items[0])

        data = await cached_or_run("twitch.clip", {"url": url}, _run, ctx)
        return ApiResponse(data=data)
