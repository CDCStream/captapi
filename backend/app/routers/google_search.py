"""Google Search endpoints backed by Apify SERP scraping."""

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

router = APIRouter()

RATE = 4.2


def _scaled(n: int, rate: float = RATE, minimum: int = 2) -> int:
    return max(minimum, math.ceil(n * rate))


def _organic_result(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": safe_str(item.get("title")),
        "url": safe_str(item.get("url") or item.get("link")),
        "displayUrl": safe_str(item.get("displayedUrl") or item.get("displayUrl")),
        "description": safe_str(item.get("description") or item.get("snippet")),
        "position": safe_int(item.get("position") or item.get("rank")),
        "type": safe_str(item.get("type") or item.get("resultType") or "organic"),
    }


def _extract_results(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in items:
        nested = item.get("organicResults") or item.get("results") or item.get("items")
        if isinstance(nested, list):
            for child in nested:
                if isinstance(child, dict):
                    results.append(_organic_result(child))
        elif item.get("title") and (item.get("url") or item.get("link")):
            results.append(_organic_result(item))
        if len(results) >= limit:
            break
    return results[:limit]


@router.get("/search", summary="Google Search results")
async def google_search(
    q: str = Query(..., min_length=2, description="Google search query"),
    country: str = Query("us", min_length=2, max_length=2, description="Two-letter country code"),
    language: str = Query("en", min_length=2, max_length=5, description="Google interface language"),
    limit: int = Query(10, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit)
    async with billed_call(
        caller=caller,
        endpoint="/v1/google/search",
        platform="google",
        resource_url=f"https://www.google.com/search?q={q}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            per_page = min(max(limit, 10), 100)
            pages = max(1, math.ceil(limit / per_page))
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_GOOGLE_SEARCH,
                {
                    "queries": q,
                    "resultsPerPage": per_page,
                    "maxPagesPerQuery": pages,
                    "countryCode": country.lower(),
                    "languageCode": language.lower(),
                    "includeUnfilteredResults": False,
                    "mobileResults": False,
                },
                max_items=pages,
            )
            results = _extract_results(items, limit)
            if not results:
                raise HTTPException(status_code=404, detail="No Google results found")
            return {
                "platform": "google",
                "query": q,
                "country": country.lower(),
                "language": language.lower(),
                "totalReturned": len(results),
                "results": results,
            }

        data = await cached_or_run(
            endpoint="google.search",
            params={"q": q, "country": country, "language": language, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["results"]))
        return ApiResponse(data=data)
