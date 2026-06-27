"""Bluesky endpoints: profile, user posts, post details.

Uses the public AT-Protocol AppView API (public.api.bsky.app) directly — no
Apify actor and no auth required for public data, so these calls are cheap.
"""

from __future__ import annotations

import math
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import extract_bluesky_post, normalize_bluesky_handle

router = APIRouter()

CREDIT_DETAILS = 1
CREDIT_PROFILE = 1
RATE = 0.1


def _scaled(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


async def _xrpc(method: str, params: dict[str, Any]) -> dict[str, Any]:
    base = get_settings().BLUESKY_API_BASE
    url = f"{base}/xrpc/{method}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
    if resp.status_code == 400:
        raise HTTPException(status_code=404, detail="Not found on Bluesky")
    if resp.status_code >= 500:
        raise HTTPException(status_code=502, detail="Bluesky upstream error")
    resp.raise_for_status()
    return resp.json()


def _author(a: dict[str, Any]) -> dict[str, Any]:
    return {
        "handle": safe_str(a.get("handle")),
        "displayName": safe_str(a.get("displayName")),
        "did": safe_str(a.get("did")),
        "avatar": safe_str(a.get("avatar")),
    }


def _normalize_post(post: dict[str, Any]) -> dict[str, Any]:
    record = post.get("record") or {}
    author = post.get("author") or {}
    return {
        "platform": "bluesky",
        "uri": safe_str(post.get("uri")),
        "cid": safe_str(post.get("cid")),
        "text": safe_str(record.get("text")),
        "publishedAt": safe_str(record.get("createdAt") or post.get("indexedAt")),
        "author": _author(author),
        "engagement": {
            "likes": safe_int(post.get("likeCount")),
            "reposts": safe_int(post.get("repostCount")),
            "replies": safe_int(post.get("replyCount")),
            "quotes": safe_int(post.get("quoteCount")),
        },
    }


def _normalize_profile(p: dict[str, Any]) -> dict[str, Any]:
    handle = p.get("handle")
    return {
        "platform": "bluesky",
        "handle": safe_str(handle),
        "url": f"https://bsky.app/profile/{handle}" if handle else None,
        "did": safe_str(p.get("did")),
        "name": safe_str(p.get("displayName")),
        "bio": safe_str(p.get("description")),
        "followers": safe_int(p.get("followersCount")),
        "following": safe_int(p.get("followsCount")),
        "posts": safe_int(p.get("postsCount")),
        "avatar": safe_str(p.get("avatar")),
        "banner": safe_str(p.get("banner")),
    }


@router.get("/profile", summary="Bluesky profile details & stats")
async def bluesky_profile(
    url: str = Query(..., description="Bluesky profile URL, @handle, or handle"),
    caller: ApiCaller = Depends(require_api_key),
):
    actor = normalize_bluesky_handle(url)
    if not actor:
        raise HTTPException(status_code=400, detail="Invalid Bluesky profile URL or handle")
    async with billed_call(
        caller=caller,
        endpoint="/v1/bluesky/profile",
        platform="bluesky",
        resource_url=f"https://bsky.app/profile/{actor}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _xrpc("app.bsky.actor.getProfile", {"actor": actor})
            return _normalize_profile(data)

        result = await cached_or_run(
            endpoint="bluesky.profile",
            params={"actor": actor},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=result)


@router.get("/user-posts", summary="List recent posts for a Bluesky profile")
async def bluesky_user_posts(
    url: str = Query(..., description="Bluesky profile URL, @handle, or handle"),
    limit: int = Query(25, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    actor = normalize_bluesky_handle(url)
    if not actor:
        raise HTTPException(status_code=400, detail="Invalid Bluesky profile URL or handle")
    cost = _scaled(limit, RATE, 1)
    async with billed_call(
        caller=caller,
        endpoint="/v1/bluesky/user-posts",
        platform="bluesky",
        resource_url=f"https://bsky.app/profile/{actor}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _xrpc(
                "app.bsky.feed.getAuthorFeed", {"actor": actor, "limit": limit}
            )
            feed = data.get("feed") or []
            posts = [_normalize_post(f["post"]) for f in feed if f.get("post")][:limit]
            return {"handle": actor, "totalReturned": len(posts), "posts": posts}

        result = await cached_or_run(
            endpoint="bluesky.user-posts",
            params={"actor": actor, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(result["posts"]), RATE, 1)
        return ApiResponse(data=result)


@router.get("/post-details", summary="Bluesky post metadata + engagement")
async def bluesky_post_details(
    url: str = Query(..., description="Bluesky post URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    parsed = extract_bluesky_post(url)
    if not parsed:
        raise HTTPException(status_code=400, detail="Invalid Bluesky post URL")
    handle, rkey = parsed
    async with billed_call(
        caller=caller,
        endpoint="/v1/bluesky/post-details",
        platform="bluesky",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            did = handle
            if not did.startswith("did:"):
                profile = await _xrpc("app.bsky.actor.getProfile", {"actor": handle})
                did = profile.get("did") or handle
            at_uri = f"at://{did}/app.bsky.feed.post/{rkey}"
            data = await _xrpc("app.bsky.feed.getPosts", {"uris": at_uri})
            posts = data.get("posts") or []
            if not posts:
                raise HTTPException(status_code=404, detail="Post not found")
            return _normalize_post(posts[0])

        result = await cached_or_run(
            endpoint="bluesky.post-details",
            params={"handle": handle, "rkey": rkey},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=result)
