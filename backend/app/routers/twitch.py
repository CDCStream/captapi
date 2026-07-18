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
from app.services.twitch_native import (
    channel_native,
    clip_native,
    schedule_native,
)
from app.utils.formatters import safe_int, safe_str, strip_empty
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


def _clip_slug(value: str) -> str | None:
    """Extract a clip slug from clips.twitch.tv/<slug> or
    twitch.tv/<channel>/clip/<slug> URLs. Returns None for non-clip inputs."""
    v = (value or "").strip().rstrip("/")
    if not v:
        return None
    if "clips.twitch.tv/" in v:
        tail = v.split("clips.twitch.tv/", 1)[1]
    elif "/clip/" in v:
        tail = v.split("/clip/", 1)[1]
    else:
        return None
    # Drop any query string / embed params.
    slug = tail.split("?", 1)[0].split("/", 1)[0]
    return slug or None


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
    url = safe_str(item.get("url") or item.get("videoUrl") or item.get("clipUrl") or item.get("sourceUrl"))
    slug = safe_str(item.get("slug") or item.get("clipSlug")) or (_clip_slug(url) if url else None)
    if not url and slug:
        url = f"https://clips.twitch.tv/{slug}"
    video_id = safe_str(item.get("id") or item.get("videoId") or item.get("clipId"))
    # Actor clip rows often omit embed/mp4; derive embed from slug or VOD id.
    embed = safe_str(item.get("embedUrl") or item.get("embedURL"))
    if not embed and slug:
        embed = f"https://clips.twitch.tv/embed?clip={slug}"
    elif not embed and video_id and url and "/videos/" in url:
        embed = f"https://player.twitch.tv/?video={video_id}&parent=captapi.com"
    broadcaster = safe_str(
        item.get("broadcasterName")
        or item.get("broadcasterLogin")
        or item.get("displayName")
        or item.get("login")
    )
    if not broadcaster and url and "twitch.tv/" in url and "/clip/" in url:
        # https://www.twitch.tv/<login>/clip/<slug>
        try:
            broadcaster = url.split("twitch.tv/", 1)[1].split("/clip/", 1)[0].strip("/") or None
        except IndexError:
            broadcaster = None
    qualities = item.get("videoQualities") if isinstance(item.get("videoQualities"), list) else []
    quality_url = None
    if qualities and isinstance(qualities[0], dict):
        quality_url = qualities[0].get("sourceURL") or qualities[0].get("sourceUrl")
    return strip_empty(
        {
            "platform": "twitch",
            "id": video_id,
            "slug": slug,
            "url": url,
            "embedUrl": embed,
            "title": safe_str(item.get("title") or item.get("clipTitle")),
            "createdAt": safe_str(item.get("createdAt") or item.get("publishedAt")),
            "durationSeconds": safe_int(
                item.get("durationSeconds") or item.get("lengthSeconds") or item.get("duration")
            ),
            "views": safe_int(item.get("viewCount") or item.get("views") or item.get("clipViewCount")),
            "thumbnail": safe_str(item.get("thumbnailUrl") or item.get("thumbnailURL") or item.get("thumbnail")),
            "videoUrl": safe_str(
                item.get("videoMp4Url")
                or item.get("mp4Url")
                or item.get("sourceURL")
                or item.get("sourceUrl")
                or item.get("videoQualitiesUrl")
                or quality_url
            ),
            "game": safe_str(
                item.get("gameName")
                or item.get("currentGame")
                or ((item.get("game") or {}).get("name") if isinstance(item.get("game"), dict) else item.get("game"))
            ),
            "language": safe_str(item.get("language") or item.get("broadcastLanguage")),
            "broadcaster": broadcaster,
            "broadcasterProfileImage": safe_str(
                item.get("broadcasterProfileImageUrl")
                or item.get("profileImageUrl")
                or item.get("profileImageURL")
                or (
                    (item.get("broadcaster") or {}).get("profileImageURL")
                    if isinstance(item.get("broadcaster"), dict)
                    else None
                ),
            ),
        }
    )


def _profile(item: dict[str, Any]) -> dict[str, Any]:
    return strip_empty(
        {
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
                "title": safe_str(item.get("streamTitle") or item.get("broadcastTitle")),
                "game": safe_str(item.get("currentGame") or item.get("broadcastGameName")),
                "viewers": safe_int(item.get("currentViewers") or item.get("viewersCount")),
                "startedAt": safe_str(item.get("startedAt") or item.get("streamStartedAt")),
                "thumbnail": safe_str(item.get("thumbnailUrl")),
            },
            "lastBroadcast": {
                "title": safe_str(item.get("lastBroadcastTitle")),
                "game": safe_str(item.get("lastBroadcastGame")),
                "startedAt": safe_str(item.get("lastBroadcastDate") or item.get("lastBroadcastStartedAt")),
            },
            "recentVideos": [_video(v) for v in item.get("recentVideos", []) if isinstance(v, dict)],
            "topClips": [_video(v) for v in item.get("topClips", []) if isinstance(v, dict)],
            "schedule": _schedule_segments(item.get("nextSchedule") or item.get("schedule")),
            "createdAt": safe_str(item.get("createdAt")),
        }
    )


def _schedule_segments(value: Any) -> list[dict[str, Any]]:
    segments = value if isinstance(value, list) else [value] if isinstance(value, dict) else []
    out: list[dict[str, Any]] = []
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        game = seg.get("game") or seg.get("category")
        out.append(
            {
                "title": safe_str(seg.get("title")),
                "startAt": safe_str(seg.get("startAt") or seg.get("startTime")),
                "endAt": safe_str(seg.get("endAt") or seg.get("endTime")),
                "game": safe_str(game.get("name") if isinstance(game, dict) else game),
            }
        )
    return out


async def _schedule_actor(username: str) -> list[dict[str, Any]]:
    """The primary channel actor never returns schedule segments; this
    dedicated actor exposes the channel's nextSchedule."""
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_TWITCH_SCHEDULE,
        # The actor enforces maxItems >= 20; it does a keyword search, so
        # filter for the exact login afterwards.
        {"keywords": [username], "maxItems": 20},
        max_items=20,
    )
    uname = username.lower()
    match = next(
        (i for i in items if isinstance(i, dict) and (i.get("login") or "").lower() == uname),
        None,
    )
    if match is None:
        return []
    return _schedule_segments(match.get("nextSchedule") or match.get("schedule"))


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
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    async with billed_call(caller=caller, endpoint="/v1/twitch/profile", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=1) as ctx:
        async def _run() -> dict[str, Any]:
            native = await channel_native(username)
            if native is not None:
                ctx["source"] = "direct"
                return native
            ctx["source"] = "apify"
            return await _channel(username)

        data = await cached_or_run("twitch.profile", {"username": username, "v": 3}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/user-videos", summary="Twitch channel videos")
async def user_videos(
    url: str = Query(..., description="Twitch channel URL or username"),
    limit: int = Query(20, ge=1, le=30),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    cost = _scaled(limit)
    async with billed_call(caller=caller, endpoint="/v1/twitch/user-videos", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            native = await channel_native(username, video_limit=limit)
            if native is not None:
                ctx["source"] = "direct"
                videos = native.get("recentVideos") or []
                return {"platform": "twitch", "username": username, "totalReturned": len(videos[:limit]), "videos": videos[:limit]}

            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_TWITCH,
                _run_input("channels", [username], limit),
                max_items=1,
            )
            videos = [_video(v) for v in (items[0].get("recentVideos") if items else []) or [] if isinstance(v, dict)]
            ctx["source"] = "apify"
            return {"platform": "twitch", "username": username, "totalReturned": len(videos), "videos": videos[:limit]}

        data = await cached_or_run("twitch.user-videos", {"username": username, "limit": limit, "v": 3}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["videos"]))
        return ApiResponse(data=data)


@router.get("/user-schedule", summary="Twitch channel schedule")
async def user_schedule(
    url: str = Query(..., description="Twitch channel URL or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    async with billed_call(caller=caller, endpoint="/v1/twitch/user-schedule", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=1) as ctx:
        async def _run() -> dict[str, Any]:
            native = await schedule_native(username)
            if native is not None:
                ctx["source"] = "direct"
                return {"platform": "twitch", "username": username, "schedule": native}

            ctx["source"] = "apify"
            schedule = await _schedule_actor(username)
            if not schedule:
                channel = await _channel(username)
                schedule = _schedule_segments(channel.get("schedule"))
            return {"platform": "twitch", "username": username, "schedule": schedule}

        data = await cached_or_run("twitch.user-schedule", {"username": username, "v": 2}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/clip", summary="Twitch clip metadata")
async def clip(
    url: str = Query(..., description="Twitch clip URL, channel URL, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/twitch/clip", platform="twitch", resource_url=url, base_credits=1) as ctx:
        async def _run() -> dict[str, Any]:
            is_clip_url = "clips.twitch.tv" in url or "/clip/" in url

            # Primary: public GraphQL clip lookup by slug (no actor cost).
            slug = _clip_slug(url)
            if slug:
                native = await clip_native(slug)
                if native is not None:
                    ctx["source"] = "direct"
                    return native

            def _clip_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
                # Channel inputs make the URL actor emit a channel record; only
                # keep rows that are actually clips/videos.
                return [
                    r
                    for r in rows
                    if isinstance(r, dict)
                    and (r.get("recordType") or r.get("rowType") or "clip") not in ("channel", "stream")
                ]

            items: list[dict[str, Any]] = []
            if is_clip_url:
                items = _clip_rows(
                    await get_apify().run_actor_sync(
                        settings.APIFY_ACTOR_TWITCH_URL,
                        {"mode": "url", "urls": [url], "includeMediaUrls": True, "maxResults": 1, "maxPages": 1},
                        max_items=1,
                    )
                )
            if not items:
                target = _target(url)
                items = _clip_rows(
                    await get_apify().run_actor_sync(
                        settings.APIFY_ACTOR_TWITCH,
                        _run_input("clips", [target], 1),
                        max_items=1,
                    )
                )
            if not items:
                raise HTTPException(status_code=404, detail="Twitch clip not found")
            ctx["source"] = "apify"
            return _video(items[0])

        data = await cached_or_run("twitch.clip", {"url": url, "v": 4}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)
