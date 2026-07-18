"""SoundCloud public data endpoints backed by Apify."""

from __future__ import annotations

import math
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services import soundcloud_native as native
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

RATE = 1.4


def _scaled(n: int, rate: float = RATE, minimum: int = 2) -> int:
    if n <= 0:
        return 0

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
        "genre": safe_str(item.get("genre")),
        "artist": safe_str(user.get("username") or user.get("name") or item.get("userName") or item.get("artistName")),
        "artistUrl": safe_str(
            user.get("permalinkUrl") or user.get("permalink_url") or item.get("userUrl") or item.get("artistUrl")
        ),
        "artistAvatar": safe_str(user.get("avatarUrl") or user.get("avatar_url") or item.get("userAvatarUrl")),
        "artistFollowers": safe_int(user.get("followersCount") or item.get("userFollowersCount")),
        "artistVerified": bool(user.get("verified") or item.get("userVerified")),
        "durationMs": safe_int(item.get("duration") or item.get("durationMs")),
        "plays": safe_int(item.get("playbackCount") or item.get("playback_count") or item.get("plays")),
        "likes": safe_int(item.get("likesCount") or item.get("likes_count") or item.get("likes")),
        "reposts": safe_int(item.get("repostsCount") or item.get("reposts_count")),
        "downloads": safe_int(item.get("downloadCount") or item.get("download_count")),
        "comments": safe_int(item.get("commentCount") or item.get("comment_count") or item.get("comments")),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created_at") or item.get("publishedAt")),
        "releaseDate": safe_str(item.get("releaseDate") or item.get("release_date")),
        "license": safe_str(item.get("license")),
        "isrc": safe_str(item.get("isrc")),
        "downloadable": bool(item.get("downloadable")),
        "streamable": bool(item.get("streamable")),
        "waveformUrl": safe_str(item.get("waveformUrl") or item.get("waveform_url")),
        "artwork": safe_str(item.get("artworkUrl") or item.get("artwork_url") or item.get("thumbnail")),
        "tags": [t for t in (item.get("tagList") or []) if isinstance(t, str)],
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
        "city": safe_str(user.get("city")),
        "countryCode": safe_str(user.get("countryCode") or user.get("country_code")),
        "verified": bool(user.get("verified")),
        "followers": safe_int(user.get("followersCount") or user.get("followers_count")),
        "followings": safe_int(user.get("followingsCount") or user.get("followings_count")),
        "trackCount": safe_int(user.get("trackCount") or user.get("track_count")),
        "playlistCount": safe_int(user.get("playlistCount") or user.get("playlist_count")),
        "likesCount": safe_int(user.get("likesCount") or user.get("likes_count")),
        "createdAt": safe_str(user.get("createdAt") or user.get("created_at")),
    }


@router.get("/artist", summary="SoundCloud artist profile")
async def artist(
    url: str = Query(..., description="SoundCloud artist URL or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    profile = _profile_url(url)
    async with billed_call(caller=caller, endpoint="/v1/soundcloud/artist", platform="soundcloud", resource_url=profile, base_credits=1) as ctx:
        async def _run() -> dict[str, Any]:
            resolved = await native.resolve(profile)
            if isinstance(resolved, dict) and resolved.get("kind") == "user":
                ctx["source"] = "direct"
                return _artist(resolved, profile)

            settings = get_settings()
            try:
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_SOUNDCLOUD,
                    {"mode": "userUrl", "startUrls": [profile], "maxResults": 1, "includeUserDetails": True},
                    max_items=1,
                )
            except ApifyError:
                items = []
            item = items[0] if items and isinstance(items[0], dict) else None
            if not item:
                raise HTTPException(status_code=404, detail="SoundCloud artist not found")
            ctx["source"] = "apify"
            return _artist(item, profile)

        data = await cached_or_run("soundcloud.artist", {"url": profile, "v": 3}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/artist-tracks", summary="SoundCloud artist tracks (cursor-paginated)")
async def artist_tracks(
    url: str = Query(..., description="SoundCloud artist URL or username"),
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the "
            "nextCursor value returned in the previous response."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    profile = _profile_url(url)
    cost = _scaled(limit)
    async with billed_call(caller=caller, endpoint="/v1/soundcloud/artist-tracks", platform="soundcloud", resource_url=profile, base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            resolved = await native.resolve(profile)
            if isinstance(resolved, dict) and resolved.get("kind") == "user" and resolved.get("id"):
                rows, next_cursor = await native.user_tracks(resolved["id"], limit, cursor=cursor)
                if rows:
                    tracks = [_track(native.prep_track_row(r)) for r in rows][:limit]
                    ctx["source"] = "direct"
                    return {
                        "platform": "soundcloud",
                        "artistUrl": profile,
                        "totalReturned": len(tracks),
                        "nextCursor": next_cursor,
                        "hasMore": next_cursor is not None,
                        "tracks": tracks,
                    }

            if cursor:
                raise HTTPException(
                    status_code=400,
                    detail="Cursor pagination is only available on the native SoundCloud path. Start a new request without cursor.",
                )
            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SOUNDCLOUD,
                {"mode": "userUrl", "startUrls": [profile], "maxResults": limit, "includeUserDetails": True},
                max_items=limit,
            )
            # includeUserDetails prepends the artist's user row to the dataset;
            # keep only real tracks (they always carry a title).
            tracks = [_track(i) for i in items if i.get("title") or i.get("name")][:limit]
            ctx["source"] = "apify"
            return {
                "platform": "soundcloud",
                "artistUrl": profile,
                "totalReturned": len(tracks),
                "nextCursor": None,
                "hasMore": False,
                "tracks": tracks,
            }

        data = await cached_or_run(
            "soundcloud.artist-tracks",
            {"url": profile, "limit": limit, "cursor": cursor or "", "v": 5},
            _run,
            ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["tracks"]))
        return ApiResponse(data=data)


@router.get("/track", summary="SoundCloud track details")
async def track(
    url: str = Query(..., description="SoundCloud track URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
    async with billed_call(caller=caller, endpoint="/v1/soundcloud/track", platform="soundcloud", resource_url=url, base_credits=1) as ctx:
        async def _run() -> dict[str, Any]:
            resolved = await native.resolve(url)
            if isinstance(resolved, dict) and resolved.get("kind") == "track":
                ctx["source"] = "direct"
                return _track(native.prep_track_row(resolved))

            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SOUNDCLOUD,
                {"mode": "trackUrl", "startUrls": [url], "maxResults": 1, "includeUserDetails": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="SoundCloud track not found")
            ctx["source"] = "apify"
            return _track(items[0])

        data = await cached_or_run("soundcloud.track", {"url": url, "v": 3}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)
