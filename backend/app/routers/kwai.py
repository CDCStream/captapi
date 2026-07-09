"""Kwai endpoints.

Backed by the ``natanielsantos/kwai-scraper`` Apify actor, which works off
Kwai's international web model: profile URLs (``https://www.kwai.com/@handle``)
and video URLs (``.../@handle/video/<id>``). The actor returns video rows; a
profile is synthesised from the ``authorMeta`` block carried on each row.
"""

from __future__ import annotations

import math
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
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

_PROFILE_EXAMPLE = "https://www.kwai.com/@easycashindonesia"
_HANDLE_RE = re.compile(r"[A-Za-z0-9._-]{2,}")


def _guard_platform(value: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "kwai":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "kwai", _PROFILE_EXAMPLE),
        )


def _profile_url(value: str) -> str | None:
    """Canonical ``https://www.kwai.com/@handle`` from a URL or bare handle."""
    value = (value or "").strip().rstrip("/")
    _guard_platform(value)
    match = re.search(r"kwai\.com/@([A-Za-z0-9._-]+)", value)
    if match:
        return f"https://www.kwai.com/@{match.group(1)}"
    if _HANDLE_RE.fullmatch(value.lstrip("@")):
        return f"https://www.kwai.com/@{value.lstrip('@')}"
    return None


def _video_url(value: str) -> str | None:
    """Canonical Kwai video URL. Requires a full share URL (the actor needs the
    handle in the path, so a bare video id can't be reconstructed)."""
    value = (value or "").strip().rstrip("/")
    _guard_platform(value)
    if not value.startswith("http"):
        value = f"https://{value}"
    if re.search(r"kwai\.com/(?:@[A-Za-z0-9._-]+/video|photo)/[A-Za-z0-9_-]+", value):
        return value
    return None


def _good_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [i for i in items if isinstance(i, dict) and i.get("status") != "error"]


async def _run_kwai(run_input: dict[str, Any], max_items: int) -> list[dict[str, Any]]:
    settings = get_settings()
    apify = get_apify()
    return await apify.run_actor_sync(settings.APIFY_ACTOR_KWAI, run_input, max_items=max_items)


def _author(item: dict[str, Any]) -> dict[str, Any]:
    meta = item.get("authorMeta")
    return meta if isinstance(meta, dict) else {}


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    author = _author(item)
    handle = author.get("username") or author.get("name")
    page_url = author.get("url") or (f"https://www.kwai.com/@{handle}" if handle else None)
    return {
        "platform": "kwai",
        "id": safe_str(author.get("id")),
        "url": safe_str(page_url),
        "username": safe_str(handle),
        "displayName": safe_str(author.get("name")),
        "avatar": safe_str(author.get("avatar")),
        "followers": safe_int(author.get("followersCount")),
        "likedCount": safe_int(author.get("likesCount")),
        "postCount": safe_int(author.get("videosCount")),
        "raw": author,
    }


def _normalize_post(item: dict[str, Any]) -> dict[str, Any]:
    author = _author(item)
    duration = item.get("duration")
    return {
        "platform": "kwai",
        "id": safe_str(item.get("id")),
        "url": safe_str(item.get("url")),
        "text": safe_str(item.get("caption")),
        "transcript": safe_str(item.get("transcript")),
        "publishedAt": safe_str(item.get("createTime")),
        "durationSeconds": safe_int(duration) if isinstance(duration, (int, float)) else None,
        "thumbnailUrl": safe_str(item.get("thumb")),
        "videoUrl": safe_str(item.get("playUrl")),
        "author": {
            "id": safe_str(author.get("id")),
            "username": safe_str(author.get("username")),
            "displayName": safe_str(author.get("name")),
            "avatar": safe_str(author.get("avatar")),
            "url": safe_str(author.get("url")),
        },
        "engagement": {
            "views": safe_int(item.get("viewCount")),
            "likes": safe_int(item.get("likeCount")),
            "comments": safe_int(item.get("commentCount")),
            "shares": safe_int(item.get("shareCount")),
        },
        "raw": item,
    }


@router.get("/profile", summary="Kwai profile")
async def profile(
    url: str = Query(..., description="Kwai profile URL or @handle (e.g. https://www.kwai.com/@easycashindonesia)"),
    caller: ApiCaller = Depends(require_api_key),
):
    profile_url = _profile_url(url)
    if not profile_url:
        raise HTTPException(status_code=400, detail="Invalid Kwai profile URL or handle")
    async with billed_call(caller=caller, endpoint="/v1/kwai/profile", platform="kwai", resource_url=url, base_credits=17) as ctx:
        async def _run() -> dict[str, Any]:
            items = _good_rows(await _run_kwai({"urls": [profile_url], "maxItems": 1}, max_items=1))
            if not items:
                raise HTTPException(status_code=404, detail="Kwai profile not found")
            return _normalize_profile(items[0])

        data = await cached_or_run("kwai.profile", {"url": profile_url, "v": 3}, _run, ctx)
        return ApiResponse(data=data)


@router.get("/user-posts", summary="Kwai user posts")
async def user_posts(
    url: str = Query(..., description="Kwai profile URL or @handle (e.g. https://www.kwai.com/@easycashindonesia)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    profile_url = _profile_url(url)
    if not profile_url:
        raise HTTPException(status_code=400, detail="Invalid Kwai profile URL or handle")
    async with billed_call(caller=caller, endpoint="/v1/kwai/user-posts", platform="kwai", resource_url=url, base_credits=max(2, math.ceil(limit * 2.25))) as ctx:
        async def _run() -> dict[str, Any]:
            items = _good_rows(await _run_kwai({"urls": [profile_url], "maxItems": limit}, max_items=limit))
            if not items:
                raise HTTPException(status_code=404, detail="Kwai profile not found")
            posts = [_normalize_post(i) for i in items[:limit]]
            return {"profileUrl": profile_url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run("kwai.user-posts", {"url": profile_url, "limit": limit, "v": 2}, _run, ctx)
        ctx["credits_override"] = max(2, math.ceil(len(data["posts"]) * 2.25))
        return ApiResponse(data=data)


@router.get("/post", summary="Kwai post")
async def post(
    url: str = Query(..., description="Kwai video URL (e.g. https://www.kwai.com/@handle/video/5238962376325675745)"),
    caller: ApiCaller = Depends(require_api_key),
):
    video_url = _video_url(url)
    if not video_url:
        raise HTTPException(status_code=400, detail="Invalid Kwai post URL")
    async with billed_call(caller=caller, endpoint="/v1/kwai/post", platform="kwai", resource_url=url, base_credits=17) as ctx:
        async def _run() -> dict[str, Any]:
            items = _good_rows(await _run_kwai({"urls": [video_url], "maxItems": 1}, max_items=1))
            if not items:
                raise HTTPException(status_code=404, detail="Kwai post not found")
            return _normalize_post(items[0])

        data = await cached_or_run("kwai.post", {"url": video_url, "v": 3}, _run, ctx)
        return ApiResponse(data=data)
