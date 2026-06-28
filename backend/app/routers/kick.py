"""Kick endpoints."""

from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str

router = APIRouter()


def _channel_url(value: str) -> str | None:
    value = (value or "").strip().rstrip("/")
    match = re.search(r"kick\.com/([^/?#]+)", value)
    if match:
        return f"https://kick.com/{match.group(1)}"
    if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{1,30}", value):
        return f"https://kick.com/{value}"
    return None


def _clip_key(value: str) -> str:
    value = (value or "").strip().rstrip("/")
    return value.rsplit("/", 1)[-1].lower()


def _normalize_clip(item: dict[str, Any]) -> dict[str, Any]:
    channel = item.get("channel") if isinstance(item.get("channel"), dict) else {}
    return {
        "platform": "kick",
        "id": safe_str(item.get("id") or item.get("clipId") or item.get("slug")),
        "url": safe_str(item.get("url") or item.get("clipUrl")),
        "title": safe_str(item.get("title")),
        "createdAt": safe_str(item.get("createdAt") or item.get("created_at")),
        "durationSeconds": safe_int(item.get("duration") or item.get("durationSeconds")),
        "views": safe_int(item.get("views") or item.get("viewCount")),
        "thumbnailUrl": safe_str(item.get("thumbnail") or item.get("thumbnailUrl")),
        "videoUrl": safe_str(item.get("videoUrl") or item.get("sourceUrl")),
        "channel": {
            "username": safe_str(channel.get("slug") or item.get("channelSlug") or item.get("username")),
            "name": safe_str(channel.get("name") or item.get("channelName")),
            "url": safe_str(channel.get("url") or item.get("channelUrl")),
        },
        "raw": item,
    }


@router.get("/clip", summary="Kick clip metadata")
async def kick_clip(
    url: str = Query(..., description="Kick clip URL, channel URL, or channel username"),
    limit: int = Query(30, ge=1, le=100, description="How many recent clips to inspect when a channel is passed"),
    caller: ApiCaller = Depends(require_api_key),
):
    channel = _channel_url(url)
    if not channel:
        raise HTTPException(status_code=400, detail="Invalid Kick URL or username")
    wanted = _clip_key(url) if "/clips/" in url.lower() or "/clip/" in url.lower() else ""
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/kick/clip", platform="kick", resource_url=url, base_credits=max(2, limit // 10)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_KICK,
                {"channelUrls": [channel], "searchType": "clips", "maxitems": limit, "useProxy": True},
                max_items=limit,
            )
            clips = [_normalize_clip(i) for i in items[:limit] if not i.get("error")]
            selected = None
            if wanted:
                selected = next(
                    (
                        c for c in clips
                        if any(wanted in candidate for candidate in ((c.get("url") or "").lower(), (c.get("id") or "").lower()))
                    ),
                    None,
                )
            selected = selected or (clips[0] if clips else None)
            if not selected:
                raise HTTPException(status_code=404, detail="Kick clip not found")
            return {"channelUrl": channel, "clip": selected, "totalReturned": len(clips), "clips": clips}

        data = await cached_or_run("kick.clip", {"url": url, "limit": limit}, _run, ctx)
        return ApiResponse(data=data)
