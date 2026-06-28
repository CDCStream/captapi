"""Truth Social public profile and post endpoints."""

from __future__ import annotations

import html
import math
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str

router = APIRouter()

BASE = "https://truthsocial.com"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)",
}


def _username(value: str) -> str:
    value = (value or "").strip().rstrip("/")
    match = re.search(r"truthsocial\.com/@([^/?#]+)", value)
    if match:
        return match.group(1)
    return value.lstrip("@")


def _post_id(value: str) -> str | None:
    match = re.search(r"/posts/([0-9]+)", value or "")
    if match:
        return match.group(1)
    match = re.search(r"\b([0-9]{10,})\b", value or "")
    return match.group(1) if match else None


def _strip_html(value: Any) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _normalize_account(item: dict[str, Any]) -> dict[str, Any]:
    username = item.get("username") or item.get("acct")
    fields = item.get("fields") if isinstance(item.get("fields"), list) else []
    return {
        "platform": "truth_social",
        "id": safe_str(item.get("id")),
        "username": safe_str(username),
        "url": safe_str(item.get("url")) or (f"https://truthsocial.com/@{username}" if username else None),
        "displayName": safe_str(item.get("display_name") or item.get("displayName")),
        "bio": _strip_html(item.get("note")),
        "avatar": safe_str(item.get("avatar")),
        "banner": safe_str(item.get("header")),
        "verified": bool(item.get("verified")),
        "followers": safe_int(item.get("followers_count") or item.get("followersCount")),
        "following": safe_int(item.get("following_count") or item.get("followingCount")),
        "postCount": safe_int(item.get("statuses_count") or item.get("statusesCount")),
        "createdAt": safe_str(item.get("created_at") or item.get("createdAt")),
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
        "id": safe_str(item.get("id")),
        "url": safe_str(item.get("url")),
        "text": _strip_html(item.get("content")),
        "publishedAt": safe_str(item.get("created_at") or item.get("createdAt")),
        "author": _normalize_account(account) if account else None,
        "engagement": {
            "replies": safe_int(item.get("replies_count") or item.get("repliesCount")),
            "reblogs": safe_int(item.get("reblogs_count") or item.get("reblogsCount")),
            "likes": safe_int(item.get("favourites_count") or item.get("favouritesCount")),
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


@router.get("/profile", summary="Truth Social profile")
async def profile(
    url: str = Query(..., description="Truth Social profile URL or @username"),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Truth Social profile")
    async with billed_call(caller=caller, endpoint="/v1/truth-social/profile", platform="truth_social", resource_url=f"{BASE}/@{username}", base_credits=5) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _get_json("/api/v1/accounts/lookup", {"acct": username})
            return _normalize_account(data)

        data = await cached_or_run("truth-social.profile", {"username": username}, _run, ctx)
        return ApiResponse(data=data)


@router.get("/user-posts", summary="Truth Social user posts")
async def user_posts(
    url: str = Query(..., description="Truth Social profile URL or @username"),
    limit: int = Query(20, ge=1, le=80),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Truth Social profile")
    async with billed_call(caller=caller, endpoint="/v1/truth-social/user-posts", platform="truth_social", resource_url=f"{BASE}/@{username}", base_credits=max(5, math.ceil(limit * 0.85))) as ctx:
        async def _run() -> dict[str, Any]:
            account = await _get_json("/api/v1/accounts/lookup", {"acct": username})
            account_id = account.get("id")
            if not account_id:
                raise HTTPException(status_code=404, detail="Truth Social profile not found")
            items = await _get_json(
                f"/api/v1/accounts/{account_id}/statuses",
                {"limit": min(limit, 40), "exclude_replies": "true", "with_muted": "true"},
            )
            posts = [_normalize_post(i) for i in items[:limit] if isinstance(i, dict)]
            return {"username": username, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run("truth-social.user-posts", {"username": username, "limit": limit}, _run, ctx)
        return ApiResponse(data=data)


@router.get("/post", summary="Truth Social post")
async def post(
    url: str = Query(..., description="Truth Social post URL or post ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    post_id = _post_id(url)
    if not post_id:
        raise HTTPException(status_code=400, detail="Invalid Truth Social post URL or ID")
    async with billed_call(caller=caller, endpoint="/v1/truth-social/post", platform="truth_social", resource_url=f"{BASE}/api/v1/statuses/{post_id}", base_credits=5) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _get_json(f"/api/v1/statuses/{post_id}")
            return _normalize_post(data)

        data = await cached_or_run("truth-social.post", {"post_id": post_id}, _run, ctx)
        return ApiResponse(data=data)
