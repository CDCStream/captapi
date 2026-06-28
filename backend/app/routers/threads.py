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
    user = item.get("user") or item.get("author") or item
    code = item.get("code") or item.get("shortcode") or item.get("post_code")
    return {
        "platform": "threads",
        "id": safe_str(item.get("pk") or item.get("id") or item.get("post_id")),
        "code": safe_str(code),
        "url": safe_str(item.get("url") or item.get("post_url"))
        or (f"https://www.threads.net/t/{code}" if code else None),
        "text": safe_str(item.get("caption") or item.get("text") or item.get("caption_text")),
        "publishedAt": safe_str(
            item.get("taken_at") or item.get("published_on") or item.get("publishedAt")
        ),
        "author": _user(user),
        "engagement": {
            "likes": safe_int(item.get("like_count") or item.get("likeCount") or item.get("likes")),
            "replies": safe_int(
                item.get("reply_count")
                or item.get("replyCount")
                or item.get("direct_reply_count")
                or item.get("replies")
            ),
            "reposts": safe_int(item.get("repost_count") or item.get("repostCount") or item.get("reposts")),
            "quotes": safe_int(item.get("quote_count") or item.get("quoteCount")),
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


def _normalize_post_download(item: dict[str, Any]) -> dict[str, Any]:
    result = item.get("result") if isinstance(item.get("result"), dict) else item
    media = result.get("medias") if isinstance(result.get("medias"), list) else []
    first_media = media[0] if media and isinstance(media[0], dict) else {}
    return {
        "platform": "threads",
        "id": safe_str(first_media.get("id")),
        "code": safe_str(extract_threads_post_code(result.get("url") or item.get("url") or "")),
        "url": safe_str(result.get("url") or item.get("url")),
        "text": safe_str(result.get("title") or first_media.get("caption")),
        "publishedAt": None,
        "author": {
            "username": safe_str(result.get("author")),
            "displayName": safe_str(result.get("author")),
            "verified": None,
            "followers": 0,
            "profileImage": None,
        },
        "engagement": {"likes": 0, "replies": 0, "reposts": 0, "quotes": 0},
        "media": media,
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
                {"username": handle, "maxPosts": 1},
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
                {"username": handle, "maxPosts": limit},
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


@router.get("/search", summary="Search Threads posts by keyword")
async def threads_search(
    q: str = Query(..., min_length=2, description="Keyword or phrase to search Threads"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/search",
        platform="threads",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_SEARCH,
                {"mode": "search", "searchQueries": [q], "maxPosts": limit},
                max_items=limit,
            )
            results = [_normalize_post(i) for i in items][:limit]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="threads.search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search-users", summary="Find Threads users matching a keyword")
async def threads_search_users(
    q: str = Query(..., min_length=2, description="Keyword to search Threads users"),
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/search-users",
        platform="threads",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            # No dedicated user-search; derive distinct authors from a keyword
            # search over a wider post sample.
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_SEARCH,
                {"mode": "search", "searchQueries": [q], "maxPosts": limit * 4},
                max_items=limit * 4,
            )
            seen: set[str] = set()
            users: list[dict[str, Any]] = []
            for item in items:
                u = _user(item.get("user") or item.get("author") or item)
                uname = u.get("username")
                if not uname or uname in seen:
                    continue
                seen.add(uname)
                users.append(u)
                if len(users) >= limit:
                    break
            return {"query": q, "totalReturned": len(users), "users": users}

        data = await cached_or_run(
            endpoint="threads.search-users",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["users"]), RATE, 2)
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
                settings.APIFY_ACTOR_THREADS_POST,
                {"links": [url], "proxyConfiguration": {"useApifyProxy": False}},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Post not found")
            return _normalize_post_download(items[0])

        data = await cached_or_run(
            endpoint="threads.post-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)
