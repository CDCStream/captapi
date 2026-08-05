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


def _looks_wrapped(value: Any) -> bool:
    if isinstance(value, dict) and "value" in value:
        return True
    if isinstance(value, str) and value.startswith("{'"):
        return True
    return False


def _normalize(item: dict[str, Any]) -> dict[str, Any]:
    """Map native / Apify rows to the public profile shape."""
    data = item.get("data") if isinstance(item.get("data"), dict) else item
    username = safe_str(data.get("username") or data.get("mutableUsername") or data.get("handle"))

    highlights_raw = data.get("curatedHighlights") or data.get("highlights") or []
    if isinstance(highlights_raw, list) and any(
        isinstance(h, dict) and (
            _looks_wrapped(h.get("highlightId")) or _looks_wrapped(h.get("storyTitle"))
        )
        for h in highlights_raw
    ):
        highlights = native._highlights(highlights_raw)
    else:
        highlights = highlights_raw if isinstance(highlights_raw, list) else []

    related_raw = data.get("relatedAccounts") or data.get("relatedAccountsInfo") or []
    if isinstance(related_raw, list) and related_raw and isinstance(related_raw[0], dict):
        if "publicProfileInfo" in related_raw[0] or "avatar" not in related_raw[0]:
            # Raw SC shape or old profilePictureUrl-only rows → remap.
            if "publicProfileInfo" in related_raw[0]:
                related = native._related(related_raw)
            else:
                related = related_raw
        else:
            related = related_raw
    else:
        related = []

    story = data.get("story")
    if isinstance(story, dict):
        listed = story.get("snapList") if isinstance(story.get("snapList"), list) else []
        # Re-map when snapCount disagrees with snapList, or snaps look unmapped.
        if listed and (
            safe_int(story.get("snapCount")) not in (None, len(listed))
            or any(isinstance(s, dict) and "mediaType" not in s and s.get("snapMediaType") == 0 for s in listed)
            or any(isinstance(s, dict) and _looks_wrapped(s.get("snapId")) for s in listed)
        ):
            story = native._story(story) or {**story, "snapCount": len(listed), "snapList": listed}
        elif listed:
            story = {**story, "snapCount": len(listed)}

    avatar = safe_str(data.get("avatar") or data.get("profilePictureUrl"))
    banner = safe_str(data.get("banner") or data.get("squareHeroImageUrl"))
    website = safe_str(data.get("website") or data.get("websiteUrl"))
    if website and "://" not in website:
        website = native._abs_url(website)

    return strip_empty(
        {
            "platform": "snapchat",
            "username": username,
            "handle": username,
            "url": safe_str(data.get("url") or data.get("webUrl") or data.get("profileUrl"))
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
            "followers": safe_int(
                data.get("followers") or data.get("subscriberCount") or data.get("subscribers")
            ),
            "verified": bool(
                data.get("isVerified") or data.get("verified") or data.get("badge")
            ),
            "badge": safe_int(data.get("badge")),
            "avatar": avatar,
            "banner": banner,
            "profilePictureUrl": avatar,
            "squareHeroImageUrl": banner,
            "snapcode": safe_str(data.get("snapcodeImageUrl") or data.get("snapcode")),
            "website": website,
            "businessProfileId": safe_str(data.get("businessProfileId")),
            "creationTimestampMs": safe_int(data.get("creationTimestampMs")),
            "createdAt": safe_str(data.get("createdAt")),
            "lastUpdateTimestampMs": safe_int(data.get("lastUpdateTimestampMs")),
            "updatedAt": safe_str(data.get("updatedAt")),
            "hasStory": data.get("hasStory"),
            "hasCuratedHighlights": data.get("hasCuratedHighlights"),
            "hasSpotlightHighlights": data.get("hasSpotlightHighlights"),
            "story": story,
            "highlights": highlights,
            "spotlightHighlights": data.get("spotlightHighlights") or [],
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
            {"username": username, "v": 5},
            _run,
            ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
