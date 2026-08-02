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
from app.services import snapchat_native as native
from app.utils.formatters import safe_int, safe_str, strip_empty
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

CREDIT_PROFILE = native.CREDIT_SNAPCHAT_PROFILE


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
    """Map native / Apify rows to the public profile shape (additive)."""
    data = item.get("data") if isinstance(item.get("data"), dict) else item
    username = safe_str(data.get("username") or data.get("mutableUsername"))
    highlights = data.get("curatedHighlights") or data.get("highlights") or []
    spotlights = data.get("spotlightHighlights") or []
    related = data.get("relatedAccounts") or []
    # Apify sometimes nests differently — keep lists as-is when already mapped.
    return strip_empty(
        {
            "platform": "snapchat",
            "username": username,
            "url": safe_str(
                data.get("url") or data.get("webUrl") or data.get("profileUrl")
            )
            or (f"https://www.snapchat.com/@{username}" if username else None),
            "displayName": safe_str(
                data.get("displayName") or data.get("title") or data.get("name")
            ),
            "bio": safe_str(data.get("bio") or data.get("description")),
            "category": safe_str(data.get("category")),
            "categoryId": safe_str(data.get("categoryId") or data.get("categoryStringId")),
            "subcategory": safe_str(data.get("subcategory")),
            "subcategoryId": safe_str(
                data.get("subcategoryId") or data.get("subcategoryStringId")
            ),
            "subscriberCount": safe_int(data.get("subscriberCount") or data.get("subscribers")),
            "verified": bool(
                data.get("isVerified") or data.get("verified") or data.get("badge")
            ),
            "badge": safe_int(data.get("badge")),
            "avatar": safe_str(
                data.get("profilePictureUrl")
                or data.get("avatar")
                or data.get("squareHeroImageUrl")
            ),
            "squareHeroImageUrl": safe_str(data.get("squareHeroImageUrl")),
            "snapcode": safe_str(data.get("snapcodeImageUrl") or data.get("snapcode")),
            "website": safe_str(data.get("websiteUrl") or data.get("website")),
            "businessProfileId": safe_str(data.get("businessProfileId")),
            "creationTimestampMs": safe_int(data.get("creationTimestampMs")),
            "createdAt": safe_str(data.get("createdAt")),
            "lastUpdateTimestampMs": safe_int(data.get("lastUpdateTimestampMs")),
            "updatedAt": safe_str(data.get("updatedAt")),
            "hasStory": data.get("hasStory"),
            "hasCuratedHighlights": data.get("hasCuratedHighlights"),
            "hasSpotlightHighlights": data.get("hasSpotlightHighlights"),
            "story": data.get("story"),
            "highlights": highlights,
            "spotlightHighlights": spotlights,
            "relatedAccounts": related,
        }
    )


@router.get("/user-profile", summary="Snapchat public user profile")
async def user_profile(
    url: str = Query(..., description="Snapchat username or profile URL"),
    cache: bool = Query(
        False,
        description="Set true to use the 24h cache. Default false — always fetch fresh data.",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Snapchat username")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/snapchat/user-profile",
        platform="snapchat",
        resource_url=f"https://www.snapchat.com/@{username}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_row = await native.fetch_user_profile(username)
            if native_row:
                ctx["source"] = "direct"
                return _normalize(native_row)

            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SNAPCHAT_PROFILE,
                {"usernames": [username]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Snapchat profile not found")
            ctx["source"] = "apify"
            return _normalize(items[0])

        data = await cached_or_run(
            "snapchat.user-profile",
            {"username": username, "v": 4},
            _run,
            ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
