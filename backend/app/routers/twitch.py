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
    user_videos_native,
)
from app.utils.formatters import safe_int, safe_str, strip_empty
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

RATE = 1.7
# Public GQL (datacenter) is ~free; flat 2 credits on native success.
CREDIT_TWITCH_NATIVE = 2


def _scaled(n: int, rate: float = RATE, minimum: int = 2) -> int:
    if n <= 0:
        return 0
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
    game_obj = item.get("game") if isinstance(item.get("game"), dict) else {}
    game_name = safe_str(
        item.get("gameName")
        or item.get("currentGame")
        or game_obj.get("name")
        or (item.get("game") if isinstance(item.get("game"), str) else None)
    )
    game_box = safe_str(
        item.get("gameBoxArtUrl")
        or item.get("gameBoxArtURL")
        or game_obj.get("boxArtURL")
        or game_obj.get("boxArtUrl")
    )
    if game_box and "{width}" in game_box:
        game_box = game_box.replace("{width}", "144").replace("{height}", "192")
    raw_thumb = safe_str(
        item.get("thumbnailUrl") or item.get("thumbnailURL") or item.get("thumbnail")
    )
    thumb = raw_thumb
    thumb_template = None
    if raw_thumb and ("{width}" in raw_thumb or "{height}" in raw_thumb):
        thumb_template = raw_thumb
        thumb = raw_thumb.replace("{width}", "320").replace("{height}", "180")
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
            "thumbnail": thumb,
            "thumbnailTemplate": thumb_template,
            "animatedPreviewUrl": safe_str(
                item.get("animatedPreviewUrl")
                or item.get("animatedPreviewURL")
                or item.get("animated_preview_url")
            ),
            "videoUrl": safe_str(
                item.get("videoMp4Url")
                or item.get("mp4Url")
                or item.get("sourceURL")
                or item.get("sourceUrl")
                or item.get("videoQualitiesUrl")
                or quality_url
            ),
            "game": game_name,
            "gameBoxArtUrl": game_box,
            "language": (
                (safe_str(item.get("language") or item.get("broadcastLanguage")) or "").lower()
                or None
            ),
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


def _empty_stream() -> dict[str, Any]:
    return {
        "title": None,
        "game": None,
        "gameBoxArtUrl": None,
        "viewers": None,
        "startedAt": None,
        "thumbnail": None,
    }


def _empty_last_broadcast() -> dict[str, Any]:
    return {"title": None, "game": None, "gameBoxArtUrl": None, "startedAt": None}


def _profile(item: dict[str, Any]) -> dict[str, Any]:
    """Normalize Apify channel rows to the public profile contract.

    ``strip_empty`` must not drop ``stream`` / ``topClips`` / ``schedule`` —
    clients dereference those keys; missing keys crash harder than nulls.
    """
    out = strip_empty(
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
            "createdAt": safe_str(item.get("createdAt")),
        }
    )
    stream = {
        "title": safe_str(item.get("streamTitle") or item.get("broadcastTitle")),
        "game": safe_str(item.get("currentGame") or item.get("broadcastGameName")),
        "gameBoxArtUrl": safe_str(item.get("gameBoxArtUrl") or item.get("currentGameBoxArtUrl")),
        "viewers": safe_int(item.get("currentViewers") or item.get("viewersCount")),
        "startedAt": safe_str(item.get("startedAt") or item.get("streamStartedAt")),
        "thumbnail": safe_str(item.get("thumbnailUrl")),
    }
    last = {
        "title": safe_str(item.get("lastBroadcastTitle")),
        "game": safe_str(item.get("lastBroadcastGame")),
        "gameBoxArtUrl": safe_str(item.get("lastBroadcastGameBoxArtUrl")),
        "startedAt": safe_str(item.get("lastBroadcastDate") or item.get("lastBroadcastStartedAt")),
    }
    # Offline → stream null (not six null fields). Live → filled stream block.
    out["stream"] = stream if (out.get("isLive") and any(v is not None for v in stream.values())) else None
    out["lastBroadcast"] = (
        last if any(v is not None for v in last.values()) else _empty_last_broadcast()
    )
    out["recentVideos"] = [
        _video(v) for v in item.get("recentVideos", []) if isinstance(v, dict)
    ]
    out["topClips"] = [_video(v) for v in item.get("topClips", []) if isinstance(v, dict)]
    out["schedule"] = _schedule_segments(item.get("nextSchedule") or item.get("schedule"))
    out["socials"] = item.get("socials") if isinstance(item.get("socials"), list) else []
    return out


def _schedule_segments(value: Any) -> list[dict[str, Any]]:
    from app.services.twitch_native import _map_schedule_segment

    segments = value if isinstance(value, list) else [value] if isinstance(value, dict) else []
    out: list[dict[str, Any]] = []
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        # Actor rows often use startTime / category; normalize to the native shape.
        if "startAt" not in seg and seg.get("startTime"):
            seg = {**seg, "startAt": seg.get("startTime")}
        if "endAt" not in seg and seg.get("endTime"):
            seg = {**seg, "endAt": seg.get("endTime")}
        if not seg.get("categories") and (seg.get("game") or seg.get("category")):
            game = seg.get("game") or seg.get("category")
            if isinstance(game, dict):
                seg = {**seg, "categories": [game]}
            elif game:
                seg = {**seg, "categories": [{"name": game}]}
        out.append(_map_schedule_segment(seg))
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
    cache: bool = Query(
        False,
        description=(
            "Set true to serve from the response cache (default TTL). Default false — "
            "always fetch fresh. Prefer cacheMaxAge when you need 1d–30d freshness control."
        ),
    ),
    cacheMaxAge: str | None = Query(
        None,
        description=(
            "Max age of a cached response: 1d, 3d, 7d, 14d, or 30d. "
            "When set, enables caching with that TTL. Envelope includes cached + cachedAt."
        ),
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    from app.core.cache_params import resolve_cache_options

    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    async with billed_call(caller=caller, endpoint="/v1/twitch/profile", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=1) as ctx:
        async def _run() -> dict[str, Any]:
            from app.utils.retry import retry_none

            native = await retry_none(
                lambda: channel_native(username), attempts=2, delay=0.35
            )
            if native is not None:
                # Contract keys — stream is null when offline (not an object of nulls).
                native.setdefault("stream", None)
                native.setdefault("lastBroadcast", _empty_last_broadcast())
                native.setdefault("recentVideos", [])
                native.setdefault("topClips", [])
                native.setdefault("schedule", [])
                native.setdefault("socials", [])
                if not native.get("isLive"):
                    native["stream"] = None
                ctx["source"] = "direct"
                return native
            ctx["source"] = "apify"
            return await _channel(username)

        data = await cached_or_run(
            "twitch.profile",
            {"username": username, "v": 7, "cacheMaxAge": cacheMaxAge},
            _run,
            ctx,
            use_cache=use_cache,
            ttl=ttl,
        )
        return ApiResponse(data=data)


@router.get("/user-videos", summary="Twitch channel videos")
async def user_videos(
    url: str = Query(..., description="Twitch channel URL or username"),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description=(
            "Max items to return (default 20, max 100). Flat 2 credits per call. "
            "Twitch's anonymous surface only exposes the first 100 matching videos — "
            "deeper history is not available."
        ),
    ),
    filterBy: str | None = Query(
        None,
        description=(
            "Video type filter: ARCHIVE | HIGHLIGHT | UPLOAD. "
            "Omit (or null) for all types — there is no default filter."
        ),
    ),
    sortBy: str = Query(
        "TIME",
        description="Sort: TIME (default, newest first) or VIEWS.",
    ),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor = the last video id from the previous page "
            "(nextCursor). Leave empty for the first page. Pages within the first "
            "100 matching videos only — Twitch rejects GQL after-cursors on this surface."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    sort_key = (sortBy or "TIME").strip().upper()
    if sort_key not in {"TIME", "VIEWS"}:
        raise HTTPException(status_code=400, detail="Invalid sortBy. Use TIME or VIEWS.")
    filter_key: str | None = None
    if filterBy:
        filter_key = filterBy.strip().upper()
        if filter_key not in {"ARCHIVE", "HIGHLIGHT", "UPLOAD"}:
            raise HTTPException(
                status_code=400,
                detail="Invalid filterBy. Use ARCHIVE, HIGHLIGHT, or UPLOAD.",
            )
    cursor_key = (cursor or "").strip() or None
    # Old clients sent integer offsets ("5"); those are no longer valid.
    if cursor_key and cursor_key.isdigit() and len(cursor_key) < 8:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid cursor. Pass nextCursor (a Twitch video id) from the previous "
                "response — integer offsets are no longer supported."
            ),
        )

    cost = CREDIT_TWITCH_NATIVE
    async with billed_call(caller=caller, endpoint="/v1/twitch/user-videos", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            # 1) Public Twitch web GraphQL (datacenter) — no Apify.
            native = await user_videos_native(
                username,
                limit=limit,
                cursor=cursor_key,
                filter_by=filter_key,
                sort_by=sort_key,
            )
            if native is not None:
                ctx["source"] = "direct"
                videos = [strip_empty(v) for v in (native.get("videos") or [])]
                out: dict[str, Any] = {
                    "platform": "twitch",
                    "username": native.get("username") or username,
                    "sortBy": native.get("sortBy") or sort_key,
                    "broadcaster": native.get("broadcaster"),
                    "totalReturned": len(videos),
                    "nextCursor": native.get("nextCursor"),
                    "hasMore": bool(native.get("hasMore")),
                    "windowMax": 100,
                    "videos": videos,
                }
                # Echo filter only when the caller set one — omit ≠ ARCHIVE.
                if native.get("filterBy"):
                    out["filterBy"] = native["filterBy"]
                else:
                    out["filterBy"] = None
                return out

            # 2) Apify fallback (first page only; no type/sort/cursor).
            if cursor_key or filter_key or sort_key != "TIME":
                raise HTTPException(
                    status_code=502,
                    detail="Twitch videos temporarily unavailable for that filter/sort/page.",
                )
            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_TWITCH,
                _run_input("channels", [username], min(limit, 30)),
                max_items=1,
            )
            videos = [
                _video(v)
                for v in (items[0].get("recentVideos") if items else []) or []
                if isinstance(v, dict)
            ]
            # Apify path: drop per-row channel bloat — single-channel list.
            for v in videos:
                v.pop("channel", None)
                v.pop("broadcaster", None)
                v.pop("broadcasterProfileImage", None)
            ctx["source"] = "apify"
            page = videos[:limit]
            return {
                "platform": "twitch",
                "username": username,
                "filterBy": None,
                "sortBy": "TIME",
                "broadcaster": None,
                "totalReturned": len(page),
                "nextCursor": None,
                "hasMore": False,
                "windowMax": 100,
                "videos": page,
            }

        data = await cached_or_run(
            "twitch.user-videos",
            {
                "username": username,
                "limit": limit,
                "filterBy": filter_key or "",
                "sortBy": sort_key,
                "cursor": cursor_key or "",
                "v": 6,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_TWITCH_NATIVE
        else:
            ctx["credits_override"] = _scaled(len(data["videos"]))
        return ApiResponse(data=data)


@router.get("/user-schedule", summary="Twitch channel schedule")
async def user_schedule(
    url: str = Query(..., description="Twitch channel URL or username"),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Max schedule segments to return (default 50, max 100). Flat 1 credit per call.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _target(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Twitch channel")
    async with billed_call(caller=caller, endpoint="/v1/twitch/user-schedule", platform="twitch", resource_url=f"https://www.twitch.tv/{username}", base_credits=1) as ctx:
        async def _run() -> dict[str, Any]:
            native = await schedule_native(username, limit=limit)
            if native is not None:
                ctx["source"] = "direct"
                return {
                    "platform": "twitch",
                    "username": username,
                    "totalReturned": len(native),
                    "schedule": native,
                }

            ctx["source"] = "apify"
            schedule = await _schedule_actor(username)
            if not schedule:
                channel = await _channel(username)
                schedule = _schedule_segments(channel.get("schedule"))
            schedule = schedule[:limit]
            return {
                "platform": "twitch",
                "username": username,
                "totalReturned": len(schedule),
                "schedule": schedule,
            }

        data = await cached_or_run(
            "twitch.user-schedule",
            {"username": username, "limit": limit, "v": 3},
            _run,
            ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/clip",
    summary="Twitch clip metadata",
    description=(
        "Fetch a Twitch clip as clean JSON — curator vs channel (broadcaster), "
        "followers/isPartner, lowercase language, multi-quality videoQualities, "
        "signedVideoUrl, and playbackAccessToken.expiresAt. Not the raw GraphQL envelope."
    ),
)
async def clip(
    url: str = Query(..., description="Twitch clip URL, channel URL, or username"),
    cache: bool = Query(
        False,
        description=(
            "Set true to serve from the response cache (default TTL). Default false — "
            "always fetch fresh. Prefer cacheMaxAge when you need 1d–30d freshness control."
        ),
    ),
    cacheMaxAge: str | None = Query(
        None,
        description=(
            "Max age of a cached response: 1d, 3d, 7d, 14d, or 30d. "
            "When set, enables caching with that TTL. Envelope includes cached + cachedAt."
        ),
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    from app.core.cache_params import resolve_cache_options

    settings = get_settings()
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
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

        data = await cached_or_run(
            "twitch.clip",
            {"url": url, "v": 6, "cacheMaxAge": cacheMaxAge},
            _run,
            ctx,
            use_cache=use_cache,
            ttl=ttl,
        )
        return ApiResponse(data=data)
