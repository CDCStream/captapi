"""Threads (Meta) endpoints: profile, user posts, post details.

Backed by a config-driven Threads actor. Field mappings are defensive because
Threads payloads vary across actor versions (snake_case and camelCase aliases).
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
from app.utils.url import (
    detect_url_platform,
    extract_threads_post_code,
    normalize_threads_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
CREDIT_PROFILE = 1
RATE = 0.7


def _scaled(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


def _reject_threads_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "threads":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "threads", example),
        )


def _require_threads_handle(value: str) -> str:
    _reject_threads_platform_mismatch(value, "https://www.threads.net/@username")
    handle = normalize_threads_username(value)
    if not handle:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "threads", "https://www.threads.net/@username"),
        )
    return handle


def _require_threads_post_url(url: str) -> str:
    code = extract_threads_post_code(url)
    if not code:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "threads", "https://www.threads.net/@user/post/POST_ID"),
        )
    return code


def _user(u: dict[str, Any]) -> dict[str, Any]:
    username = u.get("username") or u.get("userName") or u.get("user_name")
    pic_hd = u.get("hd_profile_pic_url_info") if isinstance(u.get("hd_profile_pic_url_info"), dict) else {}
    return {
        "username": safe_str(username),
        "displayName": safe_str(u.get("full_name") or u.get("fullName") or u.get("name")),
        "verified": u.get("is_verified") or u.get("isVerified"),
        "followers": safe_int(
            u.get("follower_count")
            or u.get("followerCount")
            or u.get("followers")
            or u.get("follower_count_text")
        ),
        "profileImage": safe_str(
            u.get("profile_pic_url")
            or u.get("profilePicUrl")
            or u.get("profile_pic_url_hd")
            or u.get("profile_picture_url")
            or u.get("profilePictureUrl")
            or u.get("avatar")
            or pic_hd.get("url")
        ),
    }


def _post_media(item: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    media = item.get("media")
    if isinstance(media, list):
        for m in media:
            if isinstance(m, dict) and m.get("url"):
                urls.append(m["url"])
            elif isinstance(m, str):
                urls.append(m)
    for key in ("video_url", "image_url"):
        if item.get(key) and item[key] not in urls:
            urls.append(item[key])
    return urls


def _normalize_post(item: dict[str, Any]) -> dict[str, Any]:
    user = item.get("user") or item.get("author") or item
    code = item.get("code") or item.get("shortcode") or item.get("post_code")
    author_name = (user.get("username") or user.get("userName")) if isinstance(user, dict) else None
    # Prefer the @user/post/CODE canonical form: /t/CODE links are rejected by
    # the media-downloader actor that post-details falls back to.
    if code and author_name:
        canonical = f"https://www.threads.net/@{author_name}/post/{code}"
    elif code:
        canonical = f"https://www.threads.net/t/{code}"
    else:
        canonical = None
    return {
        "platform": "threads",
        "id": safe_str(item.get("pk") or item.get("id") or item.get("post_id") or item.get("postId")),
        "code": safe_str(code),
        "url": canonical or safe_str(item.get("url") or item.get("post_url")),
        "text": safe_str(item.get("caption") or item.get("text") or item.get("caption_text")),
        "publishedAt": safe_str(
            item.get("taken_at") or item.get("date") or item.get("published_on") or item.get("publishedAt")
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
        "media": _post_media(item),
    }


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    username = item.get("username") or item.get("userName")
    return {
        "platform": "threads",
        "username": safe_str(username),
        "url": safe_str(item.get("url"))
        or (f"https://www.threads.net/@{username}" if username else None),
        "id": safe_str(item.get("pk") or item.get("id") or item.get("userId") or item.get("user_id")),
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
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_threads_handle(url)
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
            # The automation-lab scraper has a dedicated profile mode with
            # followers/bio/verified; the user-media actor only emits posts.
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_SEARCH,
                {"mode": "profile", "usernames": [handle]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Profile not found")
            return _normalize_profile(items[0])

        data = await cached_or_run(
            endpoint="threads.profile",
            params={"handle": handle, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/user-posts", summary="List recent posts for a Threads profile")
async def threads_user_posts(
    url: str = Query(..., description="Threads profile URL or @handle"),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_threads_handle(url)
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
            params={"handle": handle, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search", summary="Search Threads posts by keyword")
async def threads_search(
    q: str = Query(..., min_length=2, description="Keyword or phrase to search Threads"),
    limit: int = Query(25, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            params={"q": q, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search-users", summary="Find Threads users matching a keyword")
async def threads_search_users(
    q: str = Query(..., min_length=2, description="Keyword to search Threads users"),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            # search over a wider post sample. includeProfile adds separate
            # profile rows with followers/bio/verified for each author found.
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_SEARCH,
                {"mode": "search", "searchQueries": [q], "maxPosts": limit * 4, "includeProfile": True},
                max_items=limit * 8,
            )
            profiles: dict[str, dict[str, Any]] = {}
            for item in items:
                if item.get("type") == "profile":
                    uname = item.get("username") or item.get("userName")
                    if uname:
                        profiles[uname] = item
            seen: set[str] = set()
            users: list[dict[str, Any]] = []
            for item in items:
                if item.get("type") == "profile":
                    continue
                u = _user(item.get("user") or item.get("author") or item)
                uname = u.get("username")
                if not uname or uname in seen:
                    continue
                seen.add(uname)
                profile = profiles.get(uname)
                if profile:
                    enriched = _user(profile)
                    for key, value in enriched.items():
                        if u.get(key) is None and value is not None:
                            u[key] = value
                users.append(u)
                if len(users) >= limit:
                    break
            return {"query": q, "totalReturned": len(users), "users": users}

        data = await cached_or_run(
            endpoint="threads.search-users",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["users"]), RATE, 2)
        return ApiResponse(data=data)


_POST_AUTHOR_RE = re.compile(r"@([A-Za-z0-9._]+)/post/")


@router.get("/post-details", summary="Threads post metadata + engagement")
async def threads_post_details(
    url: str = Query(..., description="Threads post URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    code = _require_threads_post_url(url)
    settings = get_settings()
    author_match = _POST_AUTHOR_RE.search(url or "")
    author = author_match.group(1) if author_match else None
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/post-details",
        platform="threads",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            # When the URL names the author, the posts-mode scraper gives full
            # engagement + text; the downloader fallback only has media.
            if author:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_THREADS,
                    {"username": author, "maxPosts": 25},
                    max_items=25,
                )
                match = next(
                    (
                        i
                        for i in items
                        if (i.get("post_code") or i.get("code") or i.get("shortcode")) == code
                    ),
                    None,
                )
                if match:
                    return _normalize_post(match)
            dl_url = f"https://www.threads.com/@{author}/post/{code}" if author else url
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_POST,
                {"links": [dl_url], "proxyConfiguration": {"useApifyProxy": False}},
                max_items=1,
            )
            result = (items[0].get("result") or {}) if items else {}
            if not items or (isinstance(result, dict) and result.get("error")):
                raise HTTPException(status_code=404, detail="Post not found")
            return _normalize_post_download(items[0])

        data = await cached_or_run(
            endpoint="threads.post-details",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
