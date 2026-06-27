"""Pinterest endpoints: pin details, user pins, search.

Backed by a config-driven Pinterest actor. Field mappings are defensive.
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
from app.utils.url import extract_pinterest_pin_id, extract_pinterest_username

router = APIRouter()

CREDIT_DETAILS = 1
RATE = 0.5


def _scaled(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


def _image(item: dict[str, Any]) -> str | None:
    imgs = item.get("images") or item.get("image")
    if isinstance(imgs, dict):
        for key in ("orig", "736x", "564x", "474x"):
            v = imgs.get(key)
            if isinstance(v, dict) and v.get("url"):
                return safe_str(v["url"])
            if isinstance(v, str):
                return safe_str(v)
        if imgs.get("url"):
            return safe_str(imgs["url"])
    return safe_str(item.get("imageUrl") or item.get("image_url") or item.get("thumbnail"))


def _normalize_pin(item: dict[str, Any]) -> dict[str, Any]:
    pinner = item.get("pinner") or item.get("user") or {}
    pin_id = item.get("id") or item.get("pinId") or item.get("pin_id")
    pin_url = item.get("url") or item.get("pinUrl") or item.get("pin_url")
    return {
        "platform": "pinterest",
        "id": safe_str(pin_id),
        "url": safe_str(pin_url)
        or (f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else None),
        "title": safe_str(item.get("title") or item.get("grid_title")),
        "description": safe_str(item.get("description")),
        "destinationUrl": safe_str(item.get("link") or item.get("destinationUrl") or item.get("sourceLink")),
        "image": _image(item),
        "saves": safe_int(
            item.get("repin_count")
            or item.get("saveCount")
            or item.get("repinCount")
            or item.get("save_count")
        ),
        "comments": safe_int(item.get("comment_count") or item.get("commentCount")),
        "publishedAt": safe_str(item.get("created_at") or item.get("createdAt")),
        "author": {
            "username": safe_str(
                pinner.get("username") or item.get("pinner_username")
            ),
            "displayName": safe_str(
                pinner.get("full_name")
                or pinner.get("fullName")
                or item.get("pinner_name")
            ),
            "followers": safe_int(pinner.get("follower_count") or pinner.get("followerCount")),
        },
    }


@router.get("/pin-details", summary="Pinterest pin metadata + stats")
async def pin_details(
    url: str = Query(..., description="Pinterest pin URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_pinterest_pin_id(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest pin URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/pinterest/pin-details",
        platform="pinterest",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_PINTEREST,
                {"pinUrls": [url], "maxResults": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Pin not found")
            return _normalize_pin(items[0])

        data = await cached_or_run(
            endpoint="pinterest.pin-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/user-pins", summary="List pins for a Pinterest profile")
async def user_pins(
    url: str = Query(..., description="Pinterest profile URL or username"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    username = extract_pinterest_username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Pinterest profile")
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/pinterest/user-pins",
        platform="pinterest",
        resource_url=f"https://www.pinterest.com/{username}/",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_PINTEREST,
                {"usernames": [username], "maxResults": limit},
                max_items=limit,
            )
            pins = [_normalize_pin(i) for i in items][:limit]
            return {"username": username, "totalReturned": len(pins), "pins": pins}

        data = await cached_or_run(
            endpoint="pinterest.user-pins",
            params={"username": username, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["pins"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search", summary="Search Pinterest pins by keyword")
async def pinterest_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/pinterest/search",
        platform="pinterest",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_PINTEREST,
                {"searchQueries": [q], "maxResults": limit},
                max_items=limit,
            )
            results = [_normalize_pin(i) for i in items][:limit]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="pinterest.search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
