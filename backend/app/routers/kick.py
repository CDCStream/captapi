"""Kick endpoints."""

from __future__ import annotations

import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services import kick_native
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str, strip_empty
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

CREDIT_KICK_NATIVE = kick_native.CREDIT_KICK_NATIVE
CREDIT_KICK_APIFY = 34

_SENTINEL_TS = re.compile(r"^0001-01-01")
_CLIP_ID_RE = re.compile(r"/clips?/([A-Za-z0-9_-]+)", re.I)


def _channel_url(value: str) -> str | None:
    detected = detect_url_platform(value)
    if detected and detected != "kick":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "kick", "https://kick.com/channel"),
        )
    value = (value or "").strip().rstrip("/")
    # Clip URLs still carry the channel slug in the path.
    match = re.search(r"kick\.com/([^/?#]+)", value)
    if match:
        return f"https://kick.com/{match.group(1)}"
    if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{1,30}", value):
        return f"https://kick.com/{value}"
    return None


def _clip_id_from_url(value: str) -> str | None:
    match = _CLIP_ID_RE.search(value or "")
    return match.group(1) if match else None


def _ts(value: Any) -> str | None:
    text = safe_str(value)
    if not text or _SENTINEL_TS.match(text):
        return None
    return text


def _person(raw: Any, *, fallback_slug: str | None = None) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        raw = {}
    slug = safe_str(raw.get("slug") or raw.get("username") or fallback_slug)
    display = safe_str(raw.get("username") or raw.get("name") or slug)
    # Kick uses slug in URLs; username is often the display casing (xQc vs xqc).
    username = safe_str(raw.get("slug")) or (slug.lower() if slug else None)
    if not username and not display and raw.get("id") is None:
        return None
    return strip_empty(
        {
            "id": safe_str(raw.get("id")) or (str(raw["id"]) if raw.get("id") is not None else None),
            "username": username,
            "name": display,
            "url": safe_str(raw.get("url")) or (f"https://kick.com/{username}" if username else None),
            "profilePicture": safe_str(
                raw.get("profile_picture") or raw.get("profilePicture") or raw.get("avatar")
            ),
        }
    )


def _normalize_clip(item: dict[str, Any]) -> dict[str, Any]:
    channel_raw = item.get("channel") if isinstance(item.get("channel"), dict) else {}
    creator_raw = item.get("creator") if isinstance(item.get("creator"), dict) else {}
    category_raw = item.get("category") if isinstance(item.get("category"), dict) else {}
    vod_raw = item.get("vod") if isinstance(item.get("vod"), dict) else {}

    clip_id = safe_str(item.get("id") or item.get("clipId") or item.get("slug"))
    channel = _person(
        channel_raw,
        fallback_slug=safe_str(item.get("channelSlug") or item.get("username")),
    ) or {}
    slug = safe_str(channel.get("username"))
    web_url = safe_str(item.get("url") or item.get("clipUrl") or item.get("webUrl"))
    if not web_url and slug and clip_id:
        web_url = f"https://kick.com/{slug}/clips/{clip_id}"

    category_name = safe_str(category_raw.get("name")) if category_raw else safe_str(item.get("category"))
    vod_id = safe_str(vod_raw.get("id")) or safe_str(item.get("vod_id") or item.get("vodId"))
    livestream_id = safe_str(item.get("livestream_id") or item.get("livestreamId"))

    is_mature = item.get("is_mature") if isinstance(item.get("is_mature"), bool) else item.get("isMature")
    if not isinstance(is_mature, bool):
        is_mature = None

    return strip_empty(
        {
            "platform": "kick",
            "id": clip_id,
            "url": web_url,
            "title": safe_str(item.get("title")),
            "createdAt": _ts(item.get("createdAt") or item.get("created_at")),
            "startedAt": _ts(item.get("startedAt") or item.get("started_at")),
            "durationSeconds": safe_int(item.get("duration") or item.get("durationSeconds")),
            "views": safe_int(item.get("view_count") or item.get("views") or item.get("viewCount")),
            "likes": safe_int(item.get("likes_count") or item.get("likes")),
            "thumbnailUrl": safe_str(
                item.get("thumbnail") or item.get("thumbnailUrl") or item.get("thumbnail_url")
            ),
            "videoUrl": safe_str(
                item.get("videoUrl") or item.get("sourceUrl") or item.get("video_url") or item.get("clip_url")
            ),
            "privacy": safe_str(item.get("privacy")),
            "isMature": is_mature,
            "livestreamId": livestream_id,
            "vodStartsAt": safe_int(item.get("vod_starts_at") or item.get("vodStartsAt")),
            "vod": {"id": vod_id} if vod_id else None,
            # Keep string category for back-compat; add structured fields additively.
            "category": category_name,
            "categoryId": safe_str(category_raw.get("id") or item.get("category_id") or item.get("categoryId")),
            "categorySlug": safe_str(category_raw.get("slug") or item.get("categorySlug")),
            "parentCategory": safe_str(
                category_raw.get("parent_category") or category_raw.get("parentCategory")
            ),
            "categoryBanner": safe_str(category_raw.get("banner") or category_raw.get("responsive")),
            "channel": channel,
            "creator": _person(creator_raw),
        }
    )


@router.get(
    "/clip",
    summary="Kick clip metadata",
    description=(
        "Fetch a Kick clip by URL, or list recent clips for a channel. "
        "Clip URLs return a single enriched clip (creator vs channel, maturity, VOD). "
        "Channel URLs/usernames return clips[] without duplicating the first item as clip."
    ),
)
async def kick_clip(
    url: str = Query(..., description="Kick clip URL, channel URL, or channel username"),
    limit: int = Query(30, ge=1, le=100, description="How many recent clips to return when a channel is passed"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    channel = _channel_url(url)
    if not channel:
        raise HTTPException(status_code=400, detail="Invalid Kick URL or username")
    clip_id = _clip_id_from_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/kick/clip",
        platform="kick",
        resource_url=url,
        base_credits=CREDIT_KICK_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            slug = channel.rstrip("/").rsplit("/", 1)[-1]

            # Single clip URL → Kick's clip endpoint (has vod.id + real startedAt).
            if clip_id:
                native_clip = await kick_native.fetch_clip(clip_id)
                if native_clip:
                    ctx["source"] = "direct"
                    return {
                        "channelUrl": channel,
                        "clip": _normalize_clip(native_clip),
                    }
                # Fall back: scan recent channel clips for the id.
                items = await kick_native.fetch_channel_clips(slug, limit=limit)
                if items:
                    ctx["source"] = "direct"
                    clips = [_normalize_clip(i) for i in items[:limit]]
                    wanted = clip_id.lower()
                    selected = next(
                        (
                            c
                            for c in clips
                            if wanted in ((c.get("id") or "").lower(), (c.get("url") or "").lower())
                        ),
                        None,
                    )
                    if selected:
                        return {"channelUrl": channel, "clip": selected}
                try:
                    items = await get_apify().run_actor_sync(
                        settings.APIFY_ACTOR_KICK,
                        {"channelUrls": [channel], "searchType": "clips", "maxitems": limit, "useProxy": True},
                        max_items=limit,
                    )
                except (ApifyError, httpx.HTTPError):
                    items = []
                ctx["source"] = "apify"
                clips = [_normalize_clip(i) for i in (items or [])[:limit] if isinstance(i, dict) and not i.get("error")]
                wanted = clip_id.lower()
                selected = next(
                    (
                        c
                        for c in clips
                        if wanted in ((c.get("id") or "").lower(), (c.get("url") or "").lower())
                    ),
                    None,
                )
                if not selected:
                    raise HTTPException(status_code=404, detail="Kick clip not found")
                return {"channelUrl": channel, "clip": selected}

            # Channel URL / username → list only (no duplicate top-level clip).
            items = await kick_native.fetch_channel_clips(slug, limit=limit)
            if items:
                ctx["source"] = "direct"
            else:
                try:
                    items = await get_apify().run_actor_sync(
                        settings.APIFY_ACTOR_KICK,
                        {"channelUrls": [channel], "searchType": "clips", "maxitems": limit, "useProxy": True},
                        max_items=limit,
                    )
                except (ApifyError, httpx.HTTPError):
                    items = []
                ctx["source"] = "apify"

            clips = [_normalize_clip(i) for i in (items or [])[:limit] if isinstance(i, dict) and not i.get("error")]
            if not clips:
                raise HTTPException(status_code=404, detail="Kick clip not found")
            return {
                "channelUrl": channel,
                "totalReturned": len(clips),
                "clips": clips,
            }

        data = await cached_or_run(
            "kick.clip",
            {"url": url, "limit": limit, "v": 4},
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_KICK_NATIVE
        else:
            ctx["credits_override"] = CREDIT_KICK_APIFY
        return ApiResponse(data=data)
