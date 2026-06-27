"""Threads (Meta) endpoints: profile, user posts, post details.

Backed by a config-driven Threads actor. Field mappings are defensive because
Threads payloads vary across actor versions (snake_case and camelCase aliases).
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
from app.utils.url import extract_threads_post_code, normalize_threads_username

router = APIRouter()

CREDIT_DETAILS = 1
CREDIT_PROFILE = 1
RATE = 0.7


def _scaled(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


def _user(u: dict[str, Any]) -> dict[str, Any]:
    username = u.get("username") or u.get("userName")
    return {
        "username": safe_str(username),
        "displayName": safe_str(u.get("full_name") or u.get("fullName") or u.get("name")),
        "verified": u.get("is_verified") or u.get("isVerified"),
        "followers": safe_int(u.get("follower_count") or u.get("followerCount") or u.get("followers")),
        "profileImage": safe_str(u.get("profile_pic_url") or u.get("profilePicUrl")),
    }


def _normalize_post(item: dict[str, Any]) -> dict[str, Any]:
    user = item.get("user") or item.get("author") or {}
    code = item.get("code") or item.get("shortcode")
    return {
        "platform": "threads",
        "id": safe_str(item.get("pk") or item.get("id")),
        "code": safe_str(code),
        "url": safe_str(item.get("url"))
        or (f"https://www.threads.net/t/{code}" if code else None),
        "text": safe_str(item.get("caption") or item.get("text") or item.get("caption_text")),
        "publishedAt": safe_str(item.get("taken_at") or item.get("published_on") or item.get("publishedAt")),
        "author": _user(user),
        "engagement": {
            "likes": safe_int(item.get("like_count") or item.get("likeCount") or item.get("likes")),
            "replies": safe_int(item.get("reply_count") or item.get("replyCount") or item.get("replies")),
            "reposts": safe_int(item.get("repost_count") or item.get("repostCount") or item.get("reposts")),
        },
    }


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    username = item.get("username") or item.get("userName")
    return {
        "platform": "threads",
        "username": safe_str(username),
        "url": safe_str(item.get("url"))
        or (f"https://www.threads.net/@{username}" if username else None),
        "id": safe_str(item.get("pk") or item.get("id")),
        "name": safe_str(item.get("full_name") or item.get("fullName") or item.get("name")),
        "bio": safe_str(item.get("biography") or item.get("bio")),
        "verified": item.get("is_verified") or item.get("isVerified"),
        "followers": safe_int(item.get("follower_count") or item.get("followerCount") or item.get("followers")),
        "profileImage": safe_str(item.get("profile_pic_url") or item.get("profilePicUrl")),
    }


@router.get("/profile", summary="Threads profile details & stats")
async def threads_profile(
    url: str = Query(..., description="Threads profile URL or @handle"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = normalize_threads_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid Threads profile URL or handle")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/profile",
        platform="threads",
        resource_url=f"https://www.threads.net/@{handle}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS,
                {"usernames": [handle], "urls": [f"https://www.threads.net/@{handle}"], "resultsType": "profile"},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Profile not found")
            return _normalize_profile(items[0])

        data = await cached_or_run(
            endpoint="threads.profile",
            params={"handle": handle},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/user-posts", summary="List recent posts for a Threads profile")
async def threads_user_posts(
    url: str = Query(..., description="Threads profile URL or @handle"),
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = normalize_threads_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid Threads profile URL or handle")
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/user-posts",
        platform="threads",
        resource_url=f"https://www.threads.net/@{handle}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS,
                {"usernames": [handle], "resultsType": "posts", "resultsLimit": limit},
                max_items=limit,
            )
            posts = [_normalize_post(i) for i in items][:limit]
            return {"handle": handle, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="threads.user-posts",
            params={"handle": handle, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/post-details", summary="Threads post metadata + engagement")
async def threads_post_details(
    url: str = Query(..., description="Threads post URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_threads_post_code(url):
        raise HTTPException(status_code=400, detail="Invalid Threads post URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/post-details",
        platform="threads",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS,
                {"urls": [url], "resultsType": "details", "resultsLimit": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Post not found")
            return _normalize_post(items[0])

        data = await cached_or_run(
            endpoint="threads.post-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)
