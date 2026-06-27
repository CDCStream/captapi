"""Public advertising library endpoints."""

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

RATE = 1.0


def _scaled(limit: int, minimum: int = 2) -> int:
    return max(minimum, math.ceil(limit * RATE))


def _normalize_ad(item: dict[str, Any], platform: str) -> dict[str, Any]:
    advertiser = item.get("advertiser") or item.get("page") or item.get("company") or {}
    media = item.get("media") or item.get("mediaUrls") or item.get("images") or item.get("videos") or []
    return {
        "platform": platform,
        "id": safe_str(
            item.get("id")
            or item.get("adId")
            or item.get("ad_id")
            or item.get("creativeId")
            or item.get("creative_id")
        ),
        "url": safe_str(
            item.get("url")
            or item.get("adUrl")
            or item.get("ad_url")
            or item.get("detailUrl")
            or item.get("previewUrl")
            or item.get("sourceUrl")
        ),
        "text": safe_str(
            item.get("text")
            or item.get("body")
            or item.get("body_text")
            or item.get("adText")
            or item.get("ad_text")
            or item.get("copy")
        ),
        "headline": safe_str(item.get("headline") or item.get("title") or item.get("adTitle")),
        "cta": safe_str(item.get("cta") or item.get("ctaText") or item.get("cta_text") or item.get("callToAction")),
        "landingUrl": safe_str(item.get("landingUrl") or item.get("landing_page_url") or item.get("ctaUrl") or item.get("cta_url")),
        "adFormat": safe_str(item.get("adFormat") or item.get("ad_format") or item.get("format") or item.get("type")),
        "firstShown": safe_str(item.get("firstShown") or item.get("first_shown_date") or item.get("startDate")),
        "lastShown": safe_str(item.get("lastShown") or item.get("last_shown_date") or item.get("endDate")),
        "impressions": item.get("impressions") or item.get("impressionsRange") or item.get("reach"),
        "spend": item.get("spend") or item.get("spendRange"),
        "country": safe_str(item.get("country") or item.get("region")),
        "advertiser": {
            "id": safe_str(advertiser.get("id") or item.get("advertiserId") or item.get("advertiser_id")),
            "name": safe_str(
                advertiser.get("name")
                or item.get("advertiserName")
                or item.get("advertiser_name")
                or item.get("pageName")
                or item.get("brandName")
            ),
            "url": safe_str(advertiser.get("url") or item.get("advertiserUrl") or item.get("advertiser_url")),
        },
        "media": media if isinstance(media, list) else [media],
    }


async def _run_actor(actor: str, payload: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    items = await get_apify().run_actor_sync(actor, payload, max_items=limit)
    return items[:limit]


@router.get("/facebook/search", summary="Search Meta/Facebook Ad Library")
async def facebook_search(
    q: str = Query(..., min_length=2),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/search", platform="facebook_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY, {"queries": [q], "countries": [country.upper()], "activeStatus": "all", "maxAdsPerQuery": limit}, limit)
            ads = [_normalize_ad(i, "facebook_ad_library") for i in items]
            return {"query": q, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.facebook.search", {"q": q, "country": country, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/facebook/company-ads", summary="Meta/Facebook ads for a page or advertiser")
async def facebook_company_ads(
    url: str = Query(..., description="Facebook page URL or Meta Ad Library URL"),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/company-ads", platform="facebook_ad_library", resource_url=url, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY, {"pageUrls": [url], "countries": [country.upper()], "activeStatus": "all", "maxAdsPerQuery": limit}, limit)
            ads = [_normalize_ad(i, "facebook_ad_library") for i in items]
            return {"url": url, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.facebook.company-ads", {"url": url, "country": country, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/facebook/ad-details", summary="Meta/Facebook ad details")
async def facebook_ad_details(
    url: str = Query(..., description="Meta Ad Library ad URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/ad-details", platform="facebook_ad_library", resource_url=url, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY, {"pageUrls": [url], "queries": [], "scrapeAdDetails": True, "maxAdsPerQuery": 1}, 1)
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "facebook_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.facebook.ad-details", {"url": url}, _run, ctx))


@router.get("/tiktok/search", summary="Search TikTok Ad Library")
async def tiktok_search(
    q: str = Query(..., min_length=2),
    country: str = Query("DE", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/tiktok/search", platform="tiktok_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY, {"source": "both", "searchTerms": [q], "countries": [country.upper()], "maxResults": limit}, limit)
            ads = [_normalize_ad(i, "tiktok_ad_library") for i in items]
            return {"query": q, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.tiktok.search", {"q": q, "country": country, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/tiktok/ad-details", summary="TikTok ad details")
async def tiktok_ad_details(
    url: str = Query(..., description="TikTok Ad Library URL or ad ID"),
    country: str = Query("DE", min_length=2, max_length=2),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/tiktok/ad-details", platform="tiktok_ad_library", resource_url=url, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY, {"source": "library", "searchTerms": [url], "countries": [country.upper()], "maxResults": 1, "resolveAdDetails": True}, 1)
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "tiktok_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.tiktok.ad-details", {"url": url, "country": country}, _run, ctx))


@router.get("/google/company-ads", summary="Google Ads Transparency Center company ads")
async def google_company_ads(
    advertiser: str = Query(..., min_length=2, description="Advertiser name, domain, or Google advertiser ID"),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/google/company-ads", platform="google_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            payload = {"searchTerms": [advertiser], "region": country.upper(), "maxAds": limit}
            if "." in advertiser and not advertiser.startswith("AR"):
                payload = {"domains": [advertiser.replace("https://", "").replace("http://", "").strip("/")], "region": country.upper(), "maxAds": limit}
            elif advertiser.startswith("AR"):
                payload = {"advertiserIds": [advertiser], "region": country.upper(), "maxAds": limit}
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY, payload, limit)
            ads = [_normalize_ad(i, "google_ad_library") for i in items]
            return {"advertiser": advertiser, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.google.company-ads", {"advertiser": advertiser, "country": country, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/google/ad-details", summary="Google ad details")
async def google_ad_details(
    creative_id: str = Query(..., description="Google creative/ad ID or preview URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/google/ad-details", platform="google_ad_library", resource_url=creative_id, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY, {"creativeIds": [creative_id], "maxAds": 1, "enrichDetails": True}, 1)
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "google_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.google.ad-details", {"creative_id": creative_id}, _run, ctx))


@router.get("/google/advertiser-search", summary="Search Google Ads advertisers")
async def google_advertiser_search(
    q: str = Query(..., min_length=2),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(10, ge=1, le=50),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/google/advertiser-search", platform="google_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY, {"searchTerms": [q], "region": country.upper(), "maxAds": limit}, limit)
            advertisers = {}
            for item in items:
                ad = _normalize_ad(item, "google_ad_library")
                name = ad["advertiser"]["name"] or ad["advertiser"]["id"]
                if name:
                    advertisers[name] = ad["advertiser"]
            return {"query": q, "country": country.upper(), "totalReturned": len(advertisers), "advertisers": list(advertisers.values())}

        return ApiResponse(data=await cached_or_run("ad-library.google.advertiser-search", {"q": q, "country": country, "limit": limit}, _run, ctx))


@router.get("/linkedin/search-ads", summary="Search LinkedIn Ad Library")
async def linkedin_search_ads(
    q: str = Query(..., min_length=2),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/linkedin/search-ads", platform="linkedin_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_LINKEDIN_AD_LIBRARY, {"search": q, "country": country.upper(), "sort": "NEWEST"}, limit)
            ads = [_normalize_ad(i, "linkedin_ad_library") for i in items]
            return {"query": q, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.linkedin.search-ads", {"q": q, "country": country, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/linkedin/ad-details", summary="LinkedIn ad details")
async def linkedin_ad_details(
    url: str = Query(..., description="LinkedIn Ad Library URL or ad ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/linkedin/ad-details", platform="linkedin_ad_library", resource_url=url, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_LINKEDIN_AD_LIBRARY, {"search": url, "sort": "NEWEST"}, 1)
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "linkedin_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.linkedin.ad-details", {"url": url}, _run, ctx))
