"""Public advertising library endpoints."""

from __future__ import annotations

import math
import re
from typing import Any
from urllib.parse import urlencode

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


def _first(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def _dig(obj: dict[str, Any], *path: str) -> Any:
    cur: Any = obj
    for part in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _listify(value: Any) -> list[Any]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _facebook_ad_url(value: str) -> str:
    value = value.strip()
    if value.isdigit():
        return f"https://www.facebook.com/ads/library/?id={value}"
    return value


def _facebook_search_url(q: str, country: str) -> str:
    params = {
        "active_status": "all",
        "ad_type": "all",
        "country": country.upper(),
        "q": q,
        "search_type": "keyword_unordered",
        "media_type": "all",
    }
    return f"https://www.facebook.com/ads/library/?{urlencode(params)}"


def _tiktok_ad_id(value: str) -> str:
    match = re.search(r"(?:ad_id|id)=([0-9]+)", value)
    if match:
        return match.group(1)
    match = re.search(r"/ads/(?:detail/)?([0-9]+)", value)
    if match:
        return match.group(1)
    match = re.search(r"\b([0-9]{10,})\b", value)
    return match.group(1) if match else value.strip()


def _linkedin_ad_url(value: str) -> str:
    value = value.strip()
    if value.isdigit():
        return f"https://www.linkedin.com/ad-library/detail/{value}"
    return value


def _google_ids(value: str) -> tuple[str | None, str | None]:
    advertiser = re.search(r"\b(AR[0-9]+)\b", value)
    creative = re.search(r"\b(CR[0-9]+)\b", value)
    return (
        advertiser.group(1) if advertiser else None,
        creative.group(1) if creative else None,
    )


def _normalize_ad(item: dict[str, Any], platform: str) -> dict[str, Any]:
    snapshot = item.get("snapshot") if isinstance(item.get("snapshot"), dict) else {}
    advertiser = item.get("advertiser") or item.get("page") or item.get("company") or {}
    media: list[Any] = []

    media.extend(_listify(item.get("media")))
    media.extend(_listify(item.get("mediaUrls")))
    media.extend(_listify(item.get("images")))
    media.extend(_listify(item.get("imageUrls")))
    media.extend(_listify(item.get("videos")))
    media.extend(_listify(item.get("videoUrls")))
    media.extend(
        m
        for m in [
            item.get("imageUrl"),
            item.get("creativeImageUrl"),
            item.get("primaryImageUrl"),
            item.get("thumbnailUrl"),
            item.get("coverImageUrl"),
            item.get("adVideoCover"),
            item.get("videoUrl"),
            item.get("adVideoUrl"),
            item.get("previewUrl"),
            item.get("creativeAssetUrl"),
        ]
        if m
    )
    media.extend(_listify(snapshot.get("images")))
    for video in _listify(snapshot.get("videos")):
        if isinstance(video, dict):
            media.extend(
                m
                for m in [
                    video.get("videoHdUrl"),
                    video.get("videoSdUrl"),
                    video.get("videoPreviewImageUrl"),
                ]
                if m
            )
        else:
            media.append(video)
    for card in _listify(snapshot.get("cards")):
        if isinstance(card, dict):
            media.extend(
                m
                for m in [
                    card.get("originalImageUrl"),
                    card.get("videoHdUrl"),
                    card.get("videoSdUrl"),
                    card.get("videoPreviewImageUrl"),
                ]
                if m
            )

    ad_id = safe_str(
        _first(
            item.get("id"),
            item.get("adId"),
            item.get("ad_id"),
            item.get("adArchiveID"),
            item.get("adArchiveId"),
            item.get("creativeId"),
            item.get("creative_id"),
            item.get("adCreativeId"),
            item.get("ad_id"),
        )
    )
    url = safe_str(
        _first(
            item.get("url"),
            item.get("adUrl"),
            item.get("ad_url"),
            item.get("adLibraryURL"),
            item.get("adLibraryUrl"),
            item.get("ad_library_url"),
            item.get("adTransparencyUrl"),
            item.get("transparencyUrl"),
            item.get("detailUrl"),
            item.get("deeplink"),
            item.get("adDetailUrl"),
            item.get("previewUrl"),
            item.get("sourceUrl"),
            item.get("source_url"),
        )
    )
    if platform == "facebook_ad_library" and not url and ad_id:
        url = _facebook_ad_url(ad_id)

    text = safe_str(
        _first(
            item.get("text"),
            item.get("body"),
            item.get("body_text"),
            item.get("bodyText"),
            item.get("adText"),
            item.get("ad_text"),
            item.get("adCopy"),
            item.get("copy"),
            item.get("description"),
            _dig(snapshot, "body", "text"),
        )
    )
    headline = safe_str(
        _first(
            item.get("headline"),
            item.get("title"),
            item.get("adTitle"),
            item.get("ad_type"),
            item.get("adFormat"),
            item.get("format"),
            item.get("ctaHeadline"),
            snapshot.get("title"),
        )
    )

    return {
        "platform": platform,
        "id": ad_id,
        "url": url,
        "text": text,
        "headline": headline,
        "cta": safe_str(
            _first(
                item.get("cta"),
                item.get("ctaText"),
                item.get("cta_text"),
                item.get("callToAction"),
                snapshot.get("ctaText"),
            )
        ),
        "landingUrl": safe_str(
            _first(
                item.get("landingUrl"),
                item.get("landing_page_url"),
                item.get("destinationUrl"),
                item.get("ctaUrl"),
                item.get("cta_url"),
                snapshot.get("linkUrl"),
            )
        ),
        "adFormat": safe_str(_first(item.get("adFormat"), item.get("ad_format"), item.get("format"), item.get("type"), item.get("creativeType"), snapshot.get("displayFormat"))),
        "firstShown": safe_str(_first(item.get("firstShown"), item.get("first_shown_date"), item.get("startDateFormatted"), item.get("startDate"), item.get("adStartDate"))),
        "lastShown": safe_str(_first(item.get("lastShown"), item.get("last_shown_date"), item.get("endDateFormatted"), item.get("endDate"), item.get("adEndDate"))),
        "impressions": _first(item.get("impressions"), item.get("impressionsRange"), item.get("reach"), item.get("impressionRange"), item.get("totalImpressionsInterval"), item.get("impressionsMin")),
        "spend": _first(item.get("spend"), item.get("spendRange"), item.get("adSpent")),
        "country": safe_str(_first(item.get("country"), item.get("region"), item.get("regions"))),
        "advertiser": {
            "id": safe_str(_first(advertiser.get("id") if isinstance(advertiser, dict) else None, item.get("advertiserId"), item.get("advertiser_id"), item.get("advertiserBusinessId"), item.get("pageID"), item.get("pageId"))),
            "name": safe_str(
                _first(
                    advertiser.get("name") if isinstance(advertiser, dict) else None,
                    item.get("advertiserName"),
                    item.get("advertiser_name"),
                    item.get("pageName"),
                    item.get("brandName"),
                    item.get("pageInfo.page.name"),
                    snapshot.get("pageName"),
                )
            ),
            "url": safe_str(
                _first(
                    advertiser.get("url") if isinstance(advertiser, dict) else None,
                    item.get("advertiserUrl"),
                    item.get("advertiser_url"),
                    item.get("advertiserLogoUrl"),
                    item.get("pageUrl"),
                    item.get("pageURL"),
                    snapshot.get("pageProfileUri"),
                )
            ),
        },
        "media": media,
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
            items = await _run_actor(
                settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                {"startUrls": [{"url": _facebook_search_url(q, country)}], "resultsLimit": limit, "isDetailsPerAd": True},
                limit,
            )
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
            items = await _run_actor(
                settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                {"startUrls": [{"url": url}], "resultsLimit": limit, "isDetailsPerAd": True},
                limit,
            )
            ads = [_normalize_ad(i, "facebook_ad_library") for i in items]
            return {"url": url, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.facebook.company-ads", {"url": url, "country": country, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/facebook/search-companies", summary="Find advertisers/pages in Meta Ad Library")
async def facebook_search_companies(
    q: str = Query(..., min_length=2, description="Company or brand name to search for"),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/search-companies", platform="facebook_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(
                settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                {"startUrls": [{"url": _facebook_search_url(q, country)}], "resultsLimit": limit, "isDetailsPerAd": False},
                limit,
            )
            advertisers: dict[str, Any] = {}
            for item in items:
                ad = _normalize_ad(item, "facebook_ad_library")
                adv = ad["advertiser"]
                key = adv["id"] or adv["name"]
                if key and key not in advertisers:
                    advertisers[key] = adv
            companies = list(advertisers.values())
            return {"query": q, "country": country.upper(), "totalReturned": len(companies), "companies": companies}

        data = await cached_or_run("ad-library.facebook.search-companies", {"q": q, "country": country, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["companies"]))
        return ApiResponse(data=data)


@router.get("/facebook/ad-details", summary="Meta/Facebook ad details")
async def facebook_ad_details(
    url: str = Query(..., description="Meta Ad Library ad URL or ad ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    ad_url = _facebook_ad_url(url)
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/ad-details", platform="facebook_ad_library", resource_url=ad_url, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2, {"startUrls": [{"url": ad_url}], "resultsLimit": 1, "isDetailsPerAd": True}, 1)
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "facebook_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.facebook.ad-details", {"url": ad_url}, _run, ctx))


@router.get("/facebook/ad-transcript", summary="Meta/Facebook ad transcript / creative text")
async def facebook_ad_transcript(
    url: str = Query(..., description="Meta Ad Library ad URL or ad ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    ad_url = _facebook_ad_url(url)
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/ad-transcript", platform="facebook_ad_library", resource_url=ad_url, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2, {"startUrls": [{"url": ad_url}], "resultsLimit": 1, "isDetailsPerAd": True}, 1)
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            ad = _normalize_ad(items[0], "facebook_ad_library")
            segments = []
            parts = []
            for label, value in (
                ("headline", ad.get("headline")),
                ("body", ad.get("text")),
                ("cta", ad.get("cta")),
                ("landingUrl", ad.get("landingUrl")),
            ):
                text = (value or "").strip() if isinstance(value, str) else ""
                if not text:
                    continue
                parts.append(f"{label}: {text}")
                segments.append({"speaker": label, "text": text, "start": 0, "duration": 0, "timestamp": "00:00"})
            transcript = "\n".join(parts).strip()
            if not transcript:
                raise HTTPException(status_code=422, detail="No transcript text available for this ad")
            return {
                "platform": "facebook_ad_library",
                "url": ad.get("url") or ad_url,
                "adId": ad.get("id"),
                "transcript": transcript,
                "transcriptSegments": segments,
                "wordCount": len(transcript.split()),
                "segments": len(segments),
                "advertiser": ad.get("advertiser"),
            }

        return ApiResponse(data=await cached_or_run("ad-library.facebook.ad-transcript", {"url": ad_url}, _run, ctx))


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
    ad_id = _tiktok_ad_id(url)
    async with billed_call(caller=caller, endpoint="/v1/ad-library/tiktok/ad-details", platform="tiktok_ad_library", resource_url=ad_id, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(
                settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY_DETAIL,
                {"adIds": [ad_id], "country": country.upper(), "maxResults": 1, "quickSearch": False},
                1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "tiktok_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.tiktok.ad-details", {"ad_id": ad_id, "country": country}, _run, ctx))


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
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2, {"advertisers": [advertiser], "region": country.upper(), "maxResults": limit}, limit)
            ads = [_normalize_ad(i, "google_ad_library") for i in items]
            return {"advertiser": advertiser, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.google.company-ads", {"advertiser": advertiser, "country": country, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/google/ad-details", summary="Google ad details")
async def google_ad_details(
    creative_id: str = Query(..., description="Google Ads Transparency URL containing AR... and CR... IDs"),
    country: str = Query("US", min_length=2, max_length=2),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    advertiser_id, creative = _google_ids(creative_id)
    if not advertiser_id or not creative:
        raise HTTPException(status_code=400, detail="Google ad details requires a Transparency Center URL containing both AR advertiser ID and CR creative ID")
    async with billed_call(caller=caller, endpoint="/v1/ad-library/google/ad-details", platform="google_ad_library", resource_url=creative_id, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2, {"advertisers": [advertiser_id], "region": country.upper(), "maxResults": 50}, 50)
            for item in items:
                if item.get("creativeId") == creative or item.get("adCreativeId") == creative:
                    return _normalize_ad(item, "google_ad_library")
            raise HTTPException(status_code=404, detail="Ad not found")

        return ApiResponse(data=await cached_or_run("ad-library.google.ad-details", {"creative_id": creative_id, "country": country}, _run, ctx))


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
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2, {"advertisers": [q], "region": country.upper(), "maxResults": limit}, limit)
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
    ad_url = _linkedin_ad_url(url)
    async with billed_call(caller=caller, endpoint="/v1/ad-library/linkedin/ad-details", platform="linkedin_ad_library", resource_url=ad_url, base_credits=2) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_LINKEDIN_AD_LIBRARY_DETAIL, {"adUrls": [ad_url], "maxResults": 1, "includeDetails": True}, 1)
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "linkedin_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.linkedin.ad-details", {"url": ad_url}, _run, ctx))
