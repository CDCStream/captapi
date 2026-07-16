"""Truth Social public profile and post endpoints."""

from __future__ import annotations

import html
import math
import re
from typing import Any

import httpx
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

BASE = "https://truthsocial.com"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)",
}


def _username(value: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "truth_social":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "truth_social", "https://truthsocial.com/@username"),
        )
    value = (value or "").strip().rstrip("/")
    match = re.search(r"truthsocial\.com/@([^/?#]+)", value)
    if match:
        return match.group(1)
    return value.lstrip("@")


def _post_id(value: str) -> str | None:
    detected = detect_url_platform(value)
    if detected and detected != "truth_social":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "truth_social", "https://truthsocial.com/@username/posts/1234567890"),
        )
    match = re.search(r"/posts/([0-9]+)", value or "")
    if match:
        return match.group(1)
    match = re.search(r"truthsocial\.com/@[^/?#]+/([0-9]+)", value or "")
    if match:
        return match.group(1)
    match = re.search(r"\b([0-9]{10,})\b", value or "")
    return match.group(1) if match else None


def _post_username(value: str) -> str | None:
    match = re.search(r"truthsocial\.com/@([^/?#]+)/", value or "")
    return match.group(1) if match else None


def _strip_html(value: Any) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _normalize_account(item: dict[str, Any]) -> dict[str, Any]:
    username = item.get("username") or item.get("acct") or item.get("authorUsername")
    fields = item.get("fields") if isinstance(item.get("fields"), list) else []
    return {
        "platform": "truth_social",
        "id": safe_str(item.get("id") or item.get("authorId")),
        "username": safe_str(username),
        "url": safe_str(item.get("url") or item.get("authorUrl")) or (f"https://truthsocial.com/@{username}" if username else None),
        "displayName": safe_str(item.get("display_name") or item.get("displayName") or item.get("authorName")),
        "bio": _strip_html(item.get("note") or item.get("bio")),
        "avatar": safe_str(item.get("avatar") or item.get("authorAvatar")),
        "banner": safe_str(item.get("header") or item.get("banner")),
        "verified": bool(item.get("verified") or item.get("authorVerified")),
        "followers": safe_int(item.get("followers_count") or item.get("followersCount")),
        "following": safe_int(item.get("following_count") or item.get("followingCount")),
        "postCount": safe_int(item.get("statuses_count") or item.get("statusesCount")),
        "website": safe_str(item.get("website")),
        "createdAt": safe_str(item.get("created_at") or item.get("createdAt") or item.get("authorCreatedAt")),
        "lastStatusAt": safe_str(item.get("last_status_at") or item.get("lastStatusAt")),
        "fields": [
            {
                "name": safe_str(f.get("name")),
                "value": _strip_html(f.get("value")),
            }
            for f in fields
            if isinstance(f, dict)
        ],
    }


def _normalize_post(item: dict[str, Any]) -> dict[str, Any]:
    account = item.get("account") if isinstance(item.get("account"), dict) else {}
    media = item.get("media_attachments") if isinstance(item.get("media_attachments"), list) else []
    return {
        "platform": "truth_social",
        "id": safe_str(item.get("id") or item.get("postId")),
        "url": safe_str(item.get("url") or item.get("postUrl")),
        "text": _strip_html(item.get("content") or item.get("text") or item.get("contentHtml")),
        "publishedAt": safe_str(item.get("created_at") or item.get("createdAt")),
        "author": _normalize_account(account) if account else _normalize_account(item) if item.get("authorUsername") else None,
        "engagement": {
            "replies": safe_int(item.get("replies_count") or item.get("repliesCount") or item.get("replyCount")),
            "reblogs": safe_int(item.get("reblogs_count") or item.get("reblogsCount") or item.get("repostCount")),
            "likes": safe_int(item.get("favourites_count") or item.get("favouritesCount") or item.get("likeCount")),
        },
        "language": safe_str(item.get("language")),
        "sensitive": bool(item.get("sensitive")),
        "media": [
            {
                "type": safe_str(m.get("type")),
                "url": safe_str(m.get("url")),
                "previewUrl": safe_str(m.get("preview_url") or m.get("previewUrl")),
                "description": safe_str(m.get("description")),
            }
            for m in media
            if isinstance(m, dict)
        ],
    }


async def _get_json(path: str, params: dict[str, Any] | None = None) -> Any:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        resp = await client.get(f"{BASE}{path}", params=params)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Truth Social resource not found")
    if resp.status_code in (401, 403, 429):
        raise HTTPException(status_code=502, detail="Truth Social public API is temporarily unavailable")
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail="Truth Social lookup failed")
    return resp.json()


async def _actor_posts(username: str, limit: int) -> list[dict[str, Any]]:
    settings = get_settings()
    max_posts = max(limit, 5)
    items, _actor = await get_apify().run_with_fallback(
        [
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL,
                {"truthSocialUsername": [username], "maxPosts": max_posts},
            ),
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL_FALLBACK,
                {"mode": "profile", "usernames": [username], "maxPosts": max_posts},
            ),
        ],
        max_items=max_posts,
    )
    return [i for i in items if isinstance(i, dict)]


async def _actor_account(username: str) -> dict[str, Any]:
    posts = await _actor_posts(username, 5)
    for post in posts:
        account = post.get("account") if isinstance(post.get("account"), dict) else None
        if account:
            return _normalize_account(account)
        if post.get("authorUsername"):
            return _normalize_account(post)
    raise HTTPException(status_code=404, detail="Truth Social profile not found")


async def _actor_post(post_id: str, url: str) -> dict[str, Any]:
    settings = get_settings()
    username = _post_username(url)
    canonical = url if "truthsocial.com" in (url or "") else f"{BASE}/@{username or 'realDonaldTrump'}/posts/{post_id}"
    items, _actor = await get_apify().run_with_fallback(
        [
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL,
                {"fetchSinglePostByIdOrUrl": [canonical], "maxPosts": 5},
            ),
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL,
                {"fetchSinglePostByIdOrUrl": [post_id], "maxPosts": 5},
            ),
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL_FALLBACK,
                {"mode": "post", "postUrls": [canonical], "maxPosts": 1},
            ),
        ],
        max_items=5,
    )
    for item in items:
        if isinstance(item, dict) and safe_str(item.get("id") or item.get("postId")) == post_id:
            return _normalize_post(item)
    if username:
        for item in await _actor_posts(username, 80):
            if safe_str(item.get("id") or item.get("postId")) == post_id:
                return _normalize_post(item)
    raise HTTPException(status_code=404, detail="Truth Social post not found")


@router.get("/profile", summary="Truth Social profile")
async def profile(
    url: str = Query(..., description="Truth Social profile URL or @username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Truth Social profile")
    async with billed_call(caller=caller, endpoint="/v1/truth-social/profile", platform="truth_social", resource_url=f"{BASE}/@{username}", base_credits=5) as ctx:
        async def _run() -> dict[str, Any]:
            try:
                data = await _get_json("/api/v1/accounts/lookup", {"acct": username})
                return _normalize_account(data)
            except HTTPException as exc:
                if exc.status_code not in {502, 503, 504}:
                    raise
            return await _actor_account(username)

        data = await cached_or_run("truth-social.profile", {"username": username, "v": 2}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/user-posts", summary="Truth Social user posts")
async def user_posts(
    url: str = Query(..., description="Truth Social profile URL or @username"),
    limit: int = Query(20, ge=1, le=80),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Truth Social profile")
    async with billed_call(caller=caller, endpoint="/v1/truth-social/user-posts", platform="truth_social", resource_url=f"{BASE}/@{username}", base_credits=max(5, math.ceil(limit * 0.85))) as ctx:
        async def _run() -> dict[str, Any]:
            try:
                account = await _get_json("/api/v1/accounts/lookup", {"acct": username})
                account_id = account.get("id")
                if not account_id:
                    raise HTTPException(status_code=404, detail="Truth Social profile not found")
                items = await _get_json(
                    f"/api/v1/accounts/{account_id}/statuses",
                    {"limit": min(limit, 40), "exclude_replies": "true", "with_muted": "true"},
                )
            except HTTPException as exc:
                if exc.status_code not in {502, 503, 504}:
                    raise
                items = await _actor_posts(username, limit)
            posts = [_normalize_post(i) for i in items[:limit] if isinstance(i, dict)]
            return {"username": username, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run("truth-social.user-posts", {"username": username, "limit": limit, "v": 2}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/post", summary="Truth Social post")
async def post(
    url: str = Query(..., description="Truth Social post URL or post ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    post_id = _post_id(url)
    if not post_id:
        raise HTTPException(status_code=400, detail="Invalid Truth Social post URL or ID")
    async with billed_call(caller=caller, endpoint="/v1/truth-social/post", platform="truth_social", resource_url=f"{BASE}/api/v1/statuses/{post_id}", base_credits=5) as ctx:
        async def _run() -> dict[str, Any]:
            try:
                data = await _get_json(f"/api/v1/statuses/{post_id}")
                return _normalize_post(data)
            except HTTPException as exc:
                if exc.status_code not in {502, 503, 504}:
                    raise
            return await _actor_post(post_id, url)

        data = await cached_or_run("truth-social.post", {"post_id": post_id, "v": 2}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)
