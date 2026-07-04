"""SoundCloud public data endpoints backed by Apify."""

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

RATE = 1.4


def _scaled(n: int, rate: float = RATE, minimum: int = 2) -> int:
    return max(minimum, math.ceil(n * rate))


def _profile_url(value: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "soundcloud":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "soundcloud", "https://soundcloud.com/artist"),
        )
    value = (value or "").strip().rstrip("/")
    if value.startswith("http"):
        return value
    return f"https://soundcloud.com/{value.lstrip('@')}"


def _track(item: dict[str, Any]) -> dict[str, Any]:
    user = item.get("user") or item.get("artist") or item.get("publisher") or {}
    return {
        "platform": "soundcloud",
        "id": safe_str(item.get("id") or item.get("trackId")),
        "url": safe_str(item.get("url") or item.get("permalinkUrl") or item.get("permalink_url")),
        "title": safe_str(item.get("title") or item.get("name")),
        "description": safe_str(item.get("description")),
        "artist": safe_str(user.get("username") or user.get("name") or item.get("artistName")),
        "artistUrl": safe_str(user.get("permalinkUrl") or user.get("permalink_url") or item.get("artistUrl")),
        "durationMs": safe_int(item.get("duration") or item.get("durationMs")),
        "plays": safe_int(item.get("playbackCount") or item.get("playback_count") or item.get("plays")),
        "likes": safe_int(item.get("likesCount") or item.get("likes_count") or item.get("likes")),
        "comments": safe_int(item.get("commentCount") or item.get("comment_count") or item.get("comments")),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created_at") or item.get("publishedAt")),
        "artwork": safe_str(item.get("artworkUrl") or item.get("artwork_url") or item.get("thumbnail")),
    }


def _artist(item: dict[str, Any], url: str) -> dict[str, Any]:
    user = item.get("user") or item.get("artist") or item
    return {
        "platform": "soundcloud",
        "id": safe_str(user.get("id") or user.get("userId")),
        "url": safe_str(user.get("permalinkUrl") or user.get("permalink_url") or url),
        "username": safe_str(user.get("username") or user.get("permalink")),
        "name": safe_str(user.get("fullName") or user.get("full_name") or user.get("name") or user.get("username")),
        "description": safe_str(user.get("description") or user.get("bio")),
        "avatar": safe_str(user.get("avatarUrl") or user.get("avatar_url")),
        "followers": safe_int(user.get("followersCount") or user.get("followers_count")),
        "followings": safe_int(user.get("followingsCount") or user.get("followings_count")),
        "trackCount": safe_int(user.get("trackCount") or user.get("track_count")),
        "likesCount": safe_int(user.get("likesCount") or user.get("likes_count")),
    }


@router.get("/artist", summary="SoundCloud artist profile")
async def artist(
    url: str = Query(..., description="SoundCloud artist URL or username"),
    caller: ApiCaller = Depends(require_api_key),
):
    profile = _profile_url(url)
    async with billed_call(caller=caller, endpoint="/v1/soundcloud/artist", platform="soundcloud", resource_url=profile, base_credits=7) as ctx:
        async def _run() -> dict[str, Any]:
            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SOUNDCLOUD,
                {"mode": "userUrl", "startUrls": [profile], "maxResults": 1, "includeUserDetails": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="SoundCloud artist not found")
            return _artist(items[0], profile)

        data = await cached_or_run("soundcloud.artist", {"url": profile}, _run, ctx)
        return ApiResponse(data=data)


@router.get("/artist-tracks", summary="SoundCloud artist tracks")
async def artist_tracks(
    url: str = Query(..., description="SoundCloud artist URL or username"),
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    profile = _profile_url(url)
    cost = _scaled(limit)
    async with billed_call(caller=caller, endpoint="/v1/soundcloud/artist-tracks", platform="soundcloud", resource_url=profile, base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SOUNDCLOUD,
                {"mode": "userUrl", "startUrls": [profile], "maxResults": limit, "includeUserDetails": True},
                max_items=limit,
            )
            # includeUserDetails prepends the artist's user row to the dataset;
            # keep only real tracks (they always carry a title).
            tracks = [_track(i) for i in items if i.get("title") or i.get("name")][:limit]
            return {"platform": "soundcloud", "artistUrl": profile, "totalReturned": len(tracks), "tracks": tracks}

        data = await cached_or_run("soundcloud.artist-tracks", {"url": profile, "limit": limit, "v": 2}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["tracks"]))
        return ApiResponse(data=data)


@router.get("/track", summary="SoundCloud track details")
async def track(
    url: str = Query(..., description="SoundCloud track URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    detected = detect_url_platform(url)
    if detected and detected != "soundcloud":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "soundcloud", "https://soundcloud.com/artist/track"),
        )
    if "soundcloud.com/" not in url:
        raise HTTPException(status_code=400, detail="Invalid SoundCloud track URL. Pass a SoundCloud URL like https://soundcloud.com/artist/track.")
    async with billed_call(caller=caller, endpoint="/v1/soundcloud/track", platform="soundcloud", resource_url=url, base_credits=7) as ctx:
        async def _run() -> dict[str, Any]:
            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SOUNDCLOUD,
                {"mode": "trackUrl", "startUrls": [url], "maxResults": 1, "includeUserDetails": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="SoundCloud track not found")
            return _track(items[0])

        data = await cached_or_run("soundcloud.track", {"url": url}, _run, ctx)
        return ApiResponse(data=data)
