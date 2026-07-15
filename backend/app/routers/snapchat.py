"""Snapchat public profile endpoint."""

from __future__ import annotations

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


def _username(value: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "snapchat":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "snapchat", "https://www.snapchat.com/@username"),
        )
    value = (value or "").strip().rstrip("/")
    if "snapchat.com/add/" in value:
        value = value.split("snapchat.com/add/", 1)[1]
    elif "snapchat.com/@" in value:
        value = value.split("snapchat.com/@", 1)[1]
    return value.lstrip("@")


def _normalize(item: dict[str, Any]) -> dict[str, Any]:
    data = item.get("data") if isinstance(item.get("data"), dict) else item
    return {
        "platform": "snapchat",
        "username": safe_str(data.get("username") or data.get("mutableUsername")),
        "url": safe_str(data.get("url") or data.get("webUrl") or data.get("profileUrl")),
        "displayName": safe_str(data.get("displayName") or data.get("title") or data.get("name")),
        "bio": safe_str(data.get("bio") or data.get("description")),
        "category": safe_str(data.get("category") or data.get("categoryStringId")),
        "subscriberCount": safe_int(data.get("subscriberCount") or data.get("subscribers")),
        "verified": bool(data.get("isVerified") or data.get("verified") or data.get("badge")),
        "avatar": safe_str(data.get("profilePictureUrl") or data.get("avatar") or data.get("squareHeroImageUrl")),
        "snapcode": safe_str(data.get("snapcodeImageUrl") or data.get("snapcode")),
        "website": safe_str(data.get("websiteUrl") or data.get("website")),
        "highlights": data.get("curatedHighlights") or data.get("highlights") or [],
        "relatedAccounts": data.get("relatedAccounts") or [],
    }


@router.get("/user-profile", summary="Snapchat public user profile")
async def user_profile(
    url: str = Query(..., description="Snapchat username or profile URL"),
    cache: bool = Query(True, description="Set false to bypass the 24h cache and fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Snapchat username")
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/snapchat/user-profile", platform="snapchat", resource_url=f"https://www.snapchat.com/@{username}", base_credits=11) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SNAPCHAT_PROFILE,
                {"usernames": [username]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Snapchat profile not found")
            return _normalize(items[0])

        data = await cached_or_run("snapchat.user-profile", {"username": username, "v": 2}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)
