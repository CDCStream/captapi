"""Reddit endpoints (subreddit posts, post details, comments, search).

Backed by the trudax "Reddit Scraper Lite" actor (config-driven slug). The
actor returns mixed post/comment items; we split them by ``dataType``.
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
from app.utils.url import extract_reddit_post_id, extract_subreddit

router = APIRouter()

CREDIT_DETAILS = 1
RATE = 0.4


def _scaled(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


def _is_comment(item: dict[str, Any]) -> bool:
    dt = (item.get("dataType") or item.get("type") or "").lower()
    return dt == "comment" or item.get("body") is not None and item.get("title") is None


def _normalize_post(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "platform": "reddit",
        "id": safe_str(item.get("id") or item.get("parsedId")),
        "url": safe_str(item.get("url")),
        "title": safe_str(item.get("title")),
        "text": safe_str(item.get("body") or item.get("text")),
        "subreddit": safe_str(item.get("communityName") or item.get("subreddit") or item.get("parsedCommunityName")),
        "author": safe_str(item.get("username") or item.get("author")),
        "upvotes": safe_int(item.get("upVotes") or item.get("score") or item.get("ups")),
        "comments": safe_int(item.get("numberOfComments") or item.get("numComments")),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created")),
        "flair": safe_str(item.get("flair")),
        "nsfw": item.get("over18") or item.get("nsfw"),
        "thumbnail": safe_str(item.get("thumbnailUrl") or item.get("thumbnail")),
    }


def _normalize_comment(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": safe_str(item.get("id")),
        "author": safe_str(item.get("username") or item.get("author")),
        "text": safe_str(item.get("body") or item.get("text")),
        "upvotes": safe_int(item.get("upVotes") or item.get("score")),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created")),
        "url": safe_str(item.get("url")),
    }


@router.get("/subreddit-posts", summary="List recent posts in a subreddit")
async def subreddit_posts(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = extract_subreddit(url)
    if not sub:
        raise HTTPException(status_code=400, detail="Invalid subreddit")
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-posts",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_REDDIT,
                {
                    "startUrls": [{"url": f"https://www.reddit.com/r/{sub}/"}],
                    "type": "posts",
                    "sort": "new",
                    "maxItems": limit,
                },
                max_items=limit,
            )
            posts = [_normalize_post(i) for i in items if not _is_comment(i)][:limit]
            return {"subreddit": sub, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="reddit.subreddit-posts",
            params={"sub": sub, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]), RATE, 2)
        return ApiResponse(data=data)


def _normalize_community(item: dict[str, Any]) -> dict[str, Any]:
    """Map a community-profile actor record to our response shape."""
    name = item.get("name") or item.get("display_name")
    return {
        "platform": "reddit",
        "name": safe_str(name),
        "url": (f"https://www.reddit.com/r/{name}" if name else None),
        "title": safe_str(item.get("title")),
        "description": safe_str(
            item.get("about")
            or item.get("public_description")
            or item.get("description")
        ),
        "members": safe_int(item.get("subscribers")),
        "activeUsers": safe_int(item.get("accounts_active") or item.get("active_user_count")),
        "category": safe_str(item.get("category") or item.get("advertiser_category")),
        "language": safe_str(item.get("language")),
        "type": safe_str(item.get("type") or item.get("subreddit_type")),
        "createdAt": safe_str(item.get("created") or item.get("created_utc")),
        "nsfw": bool(item.get("over_18") or item.get("over18")),
        "icon": safe_str(item.get("icon") or item.get("community_icon")),
        "banner": safe_str(item.get("banner") or item.get("banner_background_image")),
    }


@router.get("/subreddit-details", summary="Subreddit info & member stats")
async def subreddit_details(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = extract_subreddit(url)
    if not sub:
        raise HTTPException(status_code=400, detail="Invalid subreddit")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-details",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_REDDIT_COMMUNITY,
                    {"community": sub},
                    max_items=1,
                )
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=502, detail="Subreddit lookup failed upstream") from exc
            if not items or not (items[0].get("name") or items[0].get("subscribers")):
                raise HTTPException(status_code=404, detail="Subreddit not found")
            return _normalize_community(items[0])

        data = await cached_or_run(
            endpoint="reddit.subreddit-details",
            params={"sub": sub},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/post-details", summary="Reddit post metadata + stats")
async def post_details(
    url: str = Query(..., description="Reddit post URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_reddit_post_id(url):
        raise HTTPException(status_code=400, detail="Invalid Reddit post URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/post-details",
        platform="reddit",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_REDDIT,
                {"startUrls": [{"url": url}], "type": "posts", "maxItems": 1},
                max_items=2,
            )
            posts = [i for i in items if not _is_comment(i)]
            if not posts:
                raise HTTPException(status_code=404, detail="Post not found")
            return _normalize_post(posts[0])

        data = await cached_or_run(
            endpoint="reddit.post-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/post-comments", summary="Comments on a Reddit post")
async def post_comments(
    url: str = Query(..., description="Reddit post URL"),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_reddit_post_id(url):
        raise HTTPException(status_code=400, detail="Invalid Reddit post URL")
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/post-comments",
        platform="reddit",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_REDDIT,
                {"startUrls": [{"url": url}], "type": "comments", "maxItems": limit},
                max_items=limit,
            )
            comments = [_normalize_comment(i) for i in items if _is_comment(i)][:limit]
            return {"totalReturned": len(comments), "comments": comments}

        data = await cached_or_run(
            endpoint="reddit.post-comments",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["comments"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/subreddit-search", summary="Search posts within a specific subreddit")
async def subreddit_search(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = extract_subreddit(url)
    if not sub:
        raise HTTPException(status_code=400, detail="Invalid subreddit")
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-search",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_REDDIT,
                {
                    "searches": [q],
                    "searchCommunityName": sub,
                    "type": "posts",
                    "sort": "relevance",
                    "maxItems": limit,
                },
                max_items=limit,
            )
            results = [_normalize_post(i) for i in items if not _is_comment(i)][:limit]
            return {"subreddit": sub, "query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="reddit.subreddit-search",
            params={"sub": sub, "q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search", summary="Search Reddit posts by keyword")
async def reddit_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/search",
        platform="reddit",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_REDDIT,
                {"searches": [q], "type": "posts", "sort": "relevance", "maxItems": limit},
                max_items=limit,
            )
            results = [_normalize_post(i) for i in items if not _is_comment(i)][:limit]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="reddit.search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
