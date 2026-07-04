"""Kwai / Kuaishou endpoints."""

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


def _id(value: str) -> str | None:
    detected = detect_url_platform(value)
    if detected and detected != "kwai":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "kwai", "https://www.kuaishou.com/profile/2542916559"),
        )
    value = (value or "").strip().rstrip("/")
    match = re.search(r"(?:profile|user)/([A-Za-z0-9_-]+)", value)
    if match:
        return match.group(1)
    match = re.search(r"(?:short-video|photo)/([A-Za-z0-9_-]+)", value)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{4,}", value):
        return value
    return None


def _good_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [i for i in items if isinstance(i, dict) and i.get("status") != "error"]


def _check_rows(items: list[dict[str, Any]], not_found_detail: str) -> list[dict[str, Any]]:
    """The actor emits ``{"status": "error", "errorMessage": ...}`` rows instead of
    failing the run. Surface those as proper HTTP errors rather than returning
    empty/garbage payloads to the caller."""
    good = [i for i in items if isinstance(i, dict) and i.get("status") != "error"]
    if good:
        return good
    errs = [str(i.get("errorMessage") or "") for i in items if isinstance(i, dict)]
    message = next((e for e in errs if e), "")
    if message and ("invalid" in message.lower() or "not found" in message.lower() or "private" in message.lower()):
        raise HTTPException(status_code=404, detail=not_found_detail)
    if message:
        raise HTTPException(status_code=502, detail=f"Kwai upstream error: {message}")
    raise HTTPException(status_code=404, detail=not_found_detail)


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    owner = item.get("ownerCount") if isinstance(item.get("ownerCount"), dict) else {}
    user_id = item.get("userId") or item.get("user_id")
    page_url = item.get("userPageUrl") or (f"https://www.kuaishou.com/profile/{user_id}" if user_id else None)
    return {
        "platform": "kwai",
        "id": safe_str(user_id),
        "url": safe_str(page_url),
        "username": safe_str(item.get("kwaiId") or item.get("userName") or item.get("user_name")),
        "displayName": safe_str(item.get("userName") or item.get("user_name")),
        "bio": safe_str(item.get("userBio") or item.get("user_text")),
        "avatar": safe_str(item.get("avatarUrl") or item.get("headurl")),
        "banner": safe_str(item.get("bannerUrl") or item.get("user_profile_bg_url")),
        "followers": safe_int(item.get("fanCount") or owner.get("fan")),
        "following": safe_int(item.get("followCount") or owner.get("follow")),
        "postCount": safe_int(item.get("photoCount") or owner.get("photo")),
        "likedCount": safe_int(item.get("likeCount") or owner.get("like")),
        "verified": bool(item.get("userVerified") or item.get("verified")),
        "location": safe_str(item.get("cityName")),
        "raw": item,
    }


def _normalize_post(item: dict[str, Any]) -> dict[str, Any]:
    video_id = item.get("videoId") or item.get("photo_id") or item.get("photoId")
    duration_ms = item.get("durationMs") or item.get("duration")
    return {
        "platform": "kwai",
        "id": safe_str(video_id),
        "url": safe_str(item.get("videoPageUrl") or (f"https://www.kuaishou.com/short-video/{video_id}" if video_id else None)),
        "text": safe_str(item.get("caption")),
        "publishedAt": safe_str(item.get("postedAt") or item.get("time")),
        "durationSeconds": safe_int(round(duration_ms / 1000)) if isinstance(duration_ms, (int, float)) and duration_ms else None,
        "thumbnailUrl": safe_str(item.get("coverUrl")),
        "videoUrl": safe_str(item.get("videoUrl")),
        "author": {
            "id": safe_str(item.get("userId") or item.get("user_id")),
            "username": safe_str(item.get("kwaiId") or item.get("userName") or item.get("user_name")),
            "displayName": safe_str(item.get("userName") or item.get("user_name")),
            "avatar": safe_str(item.get("avatarUrl")),
            "url": safe_str(item.get("userPageUrl")),
        },
        "engagement": {
            "views": safe_int(item.get("viewCount") or item.get("view_count")),
            "likes": safe_int(item.get("likeCount") or item.get("like_count")),
            "comments": safe_int(item.get("commentCount") or item.get("comment_count")),
            "shares": safe_int(item.get("shareCount") or item.get("share_count")),
        },
        "raw": item,
    }


@router.get("/profile", summary="Kwai profile")
async def profile(
    url: str = Query(..., description="Kuaishou profile URL or numeric user ID (e.g. .../profile/2542916559)"),
    caller: ApiCaller = Depends(require_api_key),
):
    user_id = _id(url)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Kwai profile URL or user ID")
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/kwai/profile", platform="kwai", resource_url=url, base_credits=17) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_KWAI,
                {"operation": "userDetail", "userId": user_id},
                max_items=1,
            )
            good = _good_rows(items)
            if good:
                return _normalize_profile(good[0])
            # The actor's userDetail op is frequently broken while userVideos
            # keeps working; synthesize the profile from the newest video row,
            # enriched with follower counts via searchUser when possible.
            videos = _good_rows(
                await apify.run_actor_sync(
                    settings.APIFY_ACTOR_KWAI,
                    {"operation": "userVideos", "userId": user_id, "maxPages": 1},
                    max_items=5,
                )
            )
            if not videos:
                _check_rows(items, "Kwai profile not found")  # raises with actor's error
            base = videos[0]
            profile = _normalize_profile(base)
            profile["id"] = profile["id"] or safe_str(user_id)
            profile["url"] = profile["url"] or f"https://www.kuaishou.com/profile/{user_id}"
            user_name = base.get("userName") or base.get("user_name")
            if user_name:
                matches = _good_rows(
                    await apify.run_actor_sync(
                        settings.APIFY_ACTOR_KWAI,
                        {"operation": "searchUser", "keyword": str(user_name), "maxPages": 1},
                        max_items=20,
                    )
                )
                match = next((m for m in matches if str(m.get("userId") or m.get("user_id")) == str(user_id)), None)
                if match:
                    profile["followers"] = profile["followers"] or safe_int(match.get("fansCount") or match.get("fanCount"))
                    profile["bio"] = profile["bio"] or safe_str(match.get("userBio"))
                    profile["verified"] = profile["verified"] or bool(match.get("userVerified") or match.get("verified"))
                    profile["avatar"] = profile["avatar"] or safe_str(match.get("avatarUrl") or match.get("headurl"))
            profile["raw"] = {k: v for k, v in base.items() if k in ("userId", "userName", "kwaiId", "userSex", "userVerified", "avatarUrl", "userPageUrl")}
            return profile

        data = await cached_or_run("kwai.profile", {"user_id": user_id, "v": 2}, _run, ctx)
        return ApiResponse(data=data)


@router.get("/user-posts", summary="Kwai user posts")
async def user_posts(
    url: str = Query(..., description="Kuaishou profile URL or numeric user ID (e.g. .../profile/2542916559)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    user_id = _id(url)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Kwai profile URL or user ID")
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/kwai/user-posts", platform="kwai", resource_url=url, base_credits=max(2, math.ceil(limit * 2.25))) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_KWAI,
                {"operation": "userVideos", "userId": user_id, "maxPages": max(1, math.ceil(limit / 10))},
                max_items=limit,
            )
            good = _check_rows(items, "Kwai profile not found")
            posts = [_normalize_post(i) for i in good[:limit]]
            return {"userId": user_id, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run("kwai.user-posts", {"user_id": user_id, "limit": limit}, _run, ctx)
        ctx["credits_override"] = max(2, math.ceil(len(data["posts"]) * 2.25))
        return ApiResponse(data=data)


@router.get("/post", summary="Kwai post")
async def post(
    url: str = Query(..., description="Kuaishou video URL or numeric video/photo ID (e.g. .../short-video/5241627202658372579)"),
    caller: ApiCaller = Depends(require_api_key),
):
    video_id = _id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid Kwai post URL or ID")
    author_match = re.search(r"[?&](?:authorId|userId)=(\w+)", url or "")
    author_id = author_match.group(1) if author_match else None
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/kwai/post", platform="kwai", resource_url=url, base_credits=17) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_KWAI,
                {"operation": "videoDetail", "videoId": video_id},
                max_items=1,
            )
            good = _good_rows(items)
            if good:
                return _normalize_post(good[0])
            # videoDetail is frequently broken in the actor. When the URL
            # carries the author (kuaishou share links include ?authorId=...),
            # find the video in the author's recent uploads instead.
            if author_id:
                videos = _good_rows(
                    await apify.run_actor_sync(
                        settings.APIFY_ACTOR_KWAI,
                        {"operation": "userVideos", "userId": author_id, "maxPages": 3},
                        max_items=100,
                    )
                )
                match = next(
                    (v for v in videos if str(v.get("videoId") or v.get("photo_id") or v.get("photoId")) == str(video_id)),
                    None,
                )
                if match:
                    return _normalize_post(match)
            _check_rows(items, "Kwai post not found")  # raises with actor's error
            raise HTTPException(status_code=404, detail="Kwai post not found")

        data = await cached_or_run("kwai.post", {"video_id": video_id, "author_id": author_id, "v": 2}, _run, ctx)
        return ApiResponse(data=data)
