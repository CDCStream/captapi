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
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

RATE_AD_LIST = 3.5
RATE_GOOGLE_COMPANY_ADS = 3.35
RATE_GOOGLE_ADVERTISER = 4.5


def _scaled(limit: int, rate: float = RATE_AD_LIST, minimum: int = 2) -> int:
    if limit <= 0:
        return 0
    return max(minimum, math.ceil(limit * rate))


def _reject_ad_platform_mismatch(value: str, expected: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != expected:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, expected, example),
        )


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


# Prefer original/HD assets first; keep media as URL strings only.
_MEDIA_URL_KEYS = (
    "originalImageUrl",
    "videoHdUrl",
    "videoSdUrl",
    "videoUrl",
    "adVideoUrl",
    "resizedImageUrl",
    "videoPreviewImageUrl",
    "imageUrl",
    "thumbnailUrl",
    "coverImageUrl",
    "previewUrl",
    "url",
    "src",
)


def _flatten_media(values: list[Any]) -> list[str]:
    """Normalize mixed media (URL strings + actor image/video objects) to http URLs."""
    seen: set[str] = set()
    out: list[str] = []

    def add(raw: Any) -> None:
        url = safe_str(raw)
        if not url or not url.startswith("http") or url in seen:
            return
        seen.add(url)
        out.append(url)

    for value in values:
        if isinstance(value, str):
            add(value)
        elif isinstance(value, dict):
            for key in _MEDIA_URL_KEYS:
                add(value.get(key))
    return out


def _facebook_ad_url(value: str) -> str:
    _reject_ad_platform_mismatch(value, "facebook", "https://www.facebook.com/ads/library/?id=123456789")
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
    _reject_ad_platform_mismatch(value, "tiktok", "https://ads.tiktok.com/business/creativecenter/inspiration/topads/detail/123456789")
    match = re.search(r"(?:ad_id|id)=([0-9]+)", value)
    if match:
        return match.group(1)
    match = re.search(r"/ads/(?:detail/)?([0-9]+)", value)
    if match:
        return match.group(1)
    match = re.search(r"\b([0-9]{10,})\b", value)
    return match.group(1) if match else value.strip()


def _tiktok_region(value: str) -> str:
    region = (value or "DE").strip().upper()
    return region or "DE"


def _linkedin_ad_url(value: str) -> str:
    _reject_ad_platform_mismatch(value, "linkedin", "https://www.linkedin.com/ad-library/detail/123456789")
    value = value.strip()
    urn = re.search(r"urn:li:sponsoredCreative:([0-9]+)", value)
    if urn:
        return f"https://www.linkedin.com/ad-library/detail/{urn.group(1)}"
    if value.isdigit():
        return f"https://www.linkedin.com/ad-library/detail/{value}"
    return value


def _google_ids(value: str) -> tuple[str | None, str | None]:
    _reject_ad_platform_mismatch(value, "google_ad_library", "https://adstransparency.google.com/advertiser/AR123/creative/CR123")
    advertiser = re.search(r"\b(AR[0-9]+)\b", value)
    creative = re.search(r"\b(CR[0-9]+)\b", value)
    return (
        advertiser.group(1) if advertiser else None,
        creative.group(1) if creative else None,
    )


def _normalize_ad(item: dict[str, Any], platform: str) -> dict[str, Any]:
    snapshot = item.get("snapshot") if isinstance(item.get("snapshot"), dict) else {}
    advertiser = (
        item.get("advertiser")
        or item.get("page")
        or item.get("company")
        or item.get("organization")
        or item.get("payingEntity")
        or item.get("payer")
        or item.get("adPayer")
        or item.get("posterInfo")
        or {}
    )
    if not isinstance(advertiser, dict):
        advertiser = {"name": advertiser} if advertiser else {}
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

    media = _flatten_media(media)

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
    if platform == "tiktok_ad_library" and not url and ad_id:
        url = f"https://library.tiktok.com/ads/detail/?ad_id={ad_id}"
    if platform == "linkedin_ad_library" and not url and ad_id:
        url = f"https://www.linkedin.com/ad-library/detail/{ad_id}"

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
            item.get("caption"),
            item.get("previewText"),
            item.get("description"),
            _dig(snapshot, "body", "text"),
        )
    )
    headline = safe_str(
        _first(
            item.get("headline"),
            item.get("title"),
            item.get("adTitle"),
            item.get("ctaHeadline"),
            snapshot.get("title"),
            next(
                (c.get("title") for c in _listify(snapshot.get("cards")) if isinstance(c, dict) and c.get("title")),
                None,
            ),
        )
    )
    # jy-labs detail actor uses a placeholder title that isn't a real headline.
    if headline and headline.strip().lower() in {"ad summary", "not mention", "n/a"}:
        headline = None

    ad_format = safe_str(
        _first(
            item.get("adFormat"),
            item.get("ad_format"),
            item.get("ad_type"),
            item.get("format"),
            item.get("type"),
            item.get("creativeType"),
            snapshot.get("displayFormat"),
        )
    )
    if not ad_format:
        # Derive from creative assets when the actor has no explicit format.
        if item.get("videoUrl") or item.get("adVideoUrl") or _listify(snapshot.get("videos")):
            ad_format = "video"
        elif _listify(item.get("imageUrls")) or _listify(item.get("images")) or _listify(snapshot.get("images")):
            ad_format = "image"

    country_value = _first(
        item.get("country"),
        item.get("region"),
        item.get("regions"),
        item.get("targetCountries"),
        item.get("countries"),
    )
    if isinstance(country_value, list):
        country_value = ", ".join(str(c) for c in country_value if c) or None

    linked_urls = _listify(item.get("linkedInUrls") or item.get("linkedinUrls"))
    landing = safe_str(
        _first(
            item.get("landingUrl"),
            item.get("landing_page_url"),
            item.get("destinationUrl"),
            item.get("ctaUrl"),
            item.get("cta_url"),
            item.get("clickUrl"),
            item.get("click_url"),
            snapshot.get("linkUrl"),
            next((u for u in linked_urls if isinstance(u, str) and u.startswith("http")), None),
        )
    )

    advertiser_name = safe_str(
        _first(
            advertiser.get("name") if isinstance(advertiser, dict) else None,
            advertiser.get("companyName") if isinstance(advertiser, dict) else None,
            advertiser.get("title") if isinstance(advertiser, dict) else None,
            item.get("advertiserName"),
            item.get("advertiser_name"),
            item.get("adPaidForBy"),
            item.get("paidForBy"),
            item.get("payerName"),
            item.get("payingEntity"),
            item.get("pageName"),
            item.get("brandName"),
            item.get("companyName"),
            item.get("organizationName"),
            _dig(item, "pageInfo", "page", "name"),
            _dig(item, "advertiser", "companyName"),
            snapshot.get("pageName"),
            snapshot.get("advertiserName"),
        )
    )
    if advertiser_name and advertiser_name.strip().lower() in {"not mention", "n/a", "unknown"}:
        advertiser_name = None

    normalized = {
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
                item.get("ctaCategory"),
                snapshot.get("ctaText"),
            )
        ),
        "landingUrl": landing,
        "adFormat": ad_format,
        "firstShown": safe_str(
            _first(
                item.get("firstShown"),
                item.get("first_shown_date"),
                item.get("firstShownDate"),
                item.get("firstShownAt"),
                item.get("startDateFormatted"),
                item.get("startDate"),
                item.get("adStartDate"),
            )
        ),
        "lastShown": safe_str(
            _first(
                item.get("lastShown"),
                item.get("last_shown_date"),
                item.get("lastShownDate"),
                item.get("lastShownAt"),
                item.get("endDateFormatted"),
                item.get("endDate"),
                item.get("adEndDate"),
            )
        ),
        "impressions": _first(
            item.get("impressions"),
            item.get("impressionsRange"),
            item.get("reach"),
            item.get("reachRange"),
            item.get("impressionRange"),
            item.get("totalImpressionsInterval"),
            item.get("impressionsMin"),
            item.get("uniqueUsersSeen"),
            item.get("estimatedAudience"),
        ),
        "spend": _first(item.get("spend"), item.get("spendRange"), item.get("adSpent"), item.get("budgetRange")),
        "country": safe_str(country_value),
        "advertiser": {
            "id": safe_str(
                _first(
                    advertiser.get("id") if isinstance(advertiser, dict) else None,
                    item.get("advertiserId"),
                    item.get("advertiser_id"),
                    item.get("advertiserBusinessId"),
                    item.get("pageID"),
                    item.get("pageId"),
                    item.get("companyId"),
                )
            ),
            "name": advertiser_name,
            "url": safe_str(
                _first(
                    advertiser.get("url") if isinstance(advertiser, dict) else None,
                    advertiser.get("profileUrl") if isinstance(advertiser, dict) else None,
                    advertiser.get("companyUrl") if isinstance(advertiser, dict) else None,
                    item.get("advertiserUrl"),
                    item.get("advertiser_url"),
                    item.get("companyUrl"),
                    item.get("companyURL"),
                    item.get("pageUrl"),
                    item.get("pageURL"),
                    item.get("organizationUrl"),
                    snapshot.get("pageProfileUri"),
                    snapshot.get("advertiserUrl"),
                )
            ),
            "logo": safe_str(
                _first(
                    advertiser.get("logo") if isinstance(advertiser, dict) else None,
                    advertiser.get("logoUrl") if isinstance(advertiser, dict) else None,
                    advertiser.get("image") if isinstance(advertiser, dict) else None,
                    item.get("advertiserLogo"),
                    item.get("advertiser_logo"),
                    item.get("companyLogo"),
                    item.get("logoUrl"),
                    item.get("logo"),
                    item.get("pageProfilePictureUrl"),
                    snapshot.get("pageProfilePictureUrl"),
                    snapshot.get("advertiserLogo"),
                )
            ),
        },
        "media": media,
    }
    adv = normalized["advertiser"]
    if platform == "google_ad_library" and not adv["url"] and adv["id"]:
        adv["url"] = f"https://adstransparency.google.com/advertiser/{adv['id']}"
    # LinkedIn / TikTok libraries often withhold spend/impressions/CTA. Prefer
    # omitting always-null metadata over shipping dead keys. Facebook/Google
    # sometimes return these, so keep explicit null when missing.
    if platform in {"tiktok_ad_library", "linkedin_ad_library"}:
        for key in ("cta", "landingUrl", "firstShown", "lastShown", "impressions", "spend", "country", "headline"):
            if normalized.get(key) in (None, "", [], {}):
                normalized.pop(key, None)
    # Advertiser logo is never supplied by Google Ads Transparency; omit empty
    # advertiser keys across libraries when upstream gave nothing.
    for key in ("id", "name", "url", "logo"):
        if adv.get(key) in (None, "", []):
            adv.pop(key, None)
    return normalized


async def _run_actor(actor: str, payload: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    try:
        items = await get_apify().run_actor_sync(actor, payload, max_items=limit)
    except ApifyError as exc:
        raise HTTPException(status_code=502, detail=f"Ad Library upstream error: {exc}") from exc
    return items[:limit]


@router.get("/facebook/search", summary="Search Meta/Facebook Ad Library")
async def facebook_search(
    q: str = Query(..., min_length=2),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/search", platform="facebook_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(
                settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                {"startUrls": [{"url": _facebook_search_url(q, country)}], "resultsLimit": limit, "isDetailsPerAd": False},
                limit,
            )
            ads = [_normalize_ad(i, "facebook_ad_library") for i in items]
            return {"query": q, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.facebook.search", {"q": q, "country": country, "limit": limit, "v": 4}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/facebook/company-ads", summary="Meta/Facebook ads for a page or advertiser")
async def facebook_company_ads(
    url: str = Query(..., description="Facebook page URL or Meta Ad Library URL"),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_ad_platform_mismatch(url, "facebook", "https://www.facebook.com/ads/library/?id=123456789")
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

        data = await cached_or_run("ad-library.facebook.company-ads", {"url": url, "country": country, "limit": limit, "v": 4}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/facebook/search-companies", summary="Find advertisers/pages in Meta Ad Library")
async def facebook_search_companies(
    q: str = Query(..., min_length=2, description="Company or brand name to search for"),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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

        data = await cached_or_run("ad-library.facebook.search-companies", {"q": q, "country": country, "limit": limit, "v": 3}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["companies"]))
        return ApiResponse(data=data)


@router.get("/facebook/ad-details", summary="Meta/Facebook ad details")
async def facebook_ad_details(
    url: str = Query(..., description="Meta Ad Library ad URL or ad ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    ad_url = _facebook_ad_url(url)
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/ad-details", platform="facebook_ad_library", resource_url=ad_url, base_credits=17) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2, {"startUrls": [{"url": ad_url}], "resultsLimit": 1, "isDetailsPerAd": True}, 1)
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "facebook_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.facebook.ad-details", {"url": ad_url, "v": 4}, _run, ctx, use_cache=cache))


@router.get("/facebook/ad-transcript", summary="Meta/Facebook ad transcript / creative text")
async def facebook_ad_transcript(
    url: str = Query(..., description="Meta Ad Library ad URL or ad ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    ad_url = _facebook_ad_url(url)
    async with billed_call(caller=caller, endpoint="/v1/ad-library/facebook/ad-transcript", platform="facebook_ad_library", resource_url=ad_url, base_credits=17) as ctx:
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

        return ApiResponse(data=await cached_or_run("ad-library.facebook.ad-transcript", {"url": ad_url, "v": 3}, _run, ctx, use_cache=cache))


@router.get("/tiktok/search", summary="Search TikTok Ad Library")
async def tiktok_search(
    q: str = Query(..., min_length=2),
    country: str = Query("DE", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/tiktok/search", platform="tiktok_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY, {"source": "both", "searchTerms": [q], "countries": [country.upper()], "maxResults": limit}, limit)
            ads = [_normalize_ad(i, "tiktok_ad_library") for i in items]
            return {"query": q, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.tiktok.search", {"q": q, "country": country, "limit": limit, "v": 4}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/tiktok/ad-details", summary="TikTok ad details")
async def tiktok_ad_details(
    url: str = Query(..., description="TikTok Ad Library URL or ad ID"),
    country: str = Query("DE", min_length=2, max_length=2),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    ad_id = _tiktok_ad_id(url)
    region = _tiktok_region(country)
    async with billed_call(caller=caller, endpoint="/v1/ad-library/tiktok/ad-details", platform="tiktok_ad_library", resource_url=ad_id, base_credits=17) as ctx:
        async def _run() -> dict[str, Any]:
            candidates: list[tuple[str, dict[str, Any]]] = [
                (
                    settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY_DETAIL,
                    {"adIds": [ad_id], "country": region, "maxResults": 1, "quickSearch": False},
                ),
                (
                    settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY_DETAIL_FALLBACK,
                    {"ad_id": ad_id, "region": region, "limit": 1},
                ),
                (
                    settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY_DETAIL_FALLBACK,
                    {"ad_id": ad_id, "region": "all", "limit": 1},
                ),
                (
                    settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY,
                    {"source": "both", "searchTerms": [ad_id], "countries": [region], "maxResults": 1},
                ),
            ]

            def _has_substance(row: dict[str, Any]) -> bool:
                # Some detail actors return a placeholder row (e.g. adTitle "Ad
                # summary" with empty fields) for ads they can't resolve.
                return any(
                    row.get(key) for key in ("adText", "text", "body", "advertiserName", "videoUrl", "adVideoUrl")
                )

            best: dict[str, Any] | None = None
            for actor, payload in candidates:
                try:
                    items = await get_apify().run_actor_sync(actor, payload, max_items=1)
                except Exception:  # noqa: BLE001
                    continue
                if not items:
                    continue
                if best is None:
                    best = items[0]
                if _has_substance(items[0]):
                    best = items[0]
                    break
            if best is None:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(best, "tiktok_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.tiktok.ad-details", {"ad_id": ad_id, "country": region, "v": 4}, _run, ctx, use_cache=cache))


@router.get("/google/company-ads", summary="Google Ads Transparency Center company ads")
async def google_company_ads(
    advertiser: str = Query(..., min_length=2, description="Advertiser name, domain, or Google advertiser ID"),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/google/company-ads", platform="google_ad_library", resource_url=None, base_credits=_scaled(limit, RATE_GOOGLE_COMPANY_ADS)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2, {"advertisers": [advertiser], "region": country.upper(), "maxResults": limit}, limit)
            ads = [_normalize_ad(i, "google_ad_library") for i in items]
            return {"advertiser": advertiser, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.google.company-ads", {"advertiser": advertiser, "country": country, "limit": limit, "v": 3}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["ads"]), RATE_GOOGLE_COMPANY_ADS)
        return ApiResponse(data=data)


@router.get("/google/ad-details", summary="Google ad details")
async def google_ad_details(
    creative_id: str = Query(..., description="Google Ads Transparency URL containing AR... and CR... IDs"),
    country: str = Query("US", min_length=2, max_length=2),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    advertiser_id, creative = _google_ids(creative_id)
    if not advertiser_id or not creative:
        raise HTTPException(status_code=400, detail="Google ad details requires a Transparency Center URL containing both AR advertiser ID and CR creative ID")
    async with billed_call(caller=caller, endpoint="/v1/ad-library/google/ad-details", platform="google_ad_library", resource_url=creative_id, base_credits=17) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2, {"advertisers": [advertiser_id], "region": country.upper(), "maxResults": 50}, 50)
            for item in items:
                if item.get("creativeId") == creative or item.get("adCreativeId") == creative:
                    return _normalize_ad(item, "google_ad_library")
            raise HTTPException(status_code=404, detail="Ad not found")

        return ApiResponse(data=await cached_or_run("ad-library.google.ad-details", {"creative_id": creative_id, "country": country, "v": 3}, _run, ctx, use_cache=cache))


@router.get("/google/advertiser-search", summary="Search Google Ads advertisers")
async def google_advertiser_search(
    q: str = Query(..., min_length=2),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(10, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/google/advertiser-search", platform="google_ad_library", resource_url=None, base_credits=_scaled(limit, RATE_GOOGLE_ADVERTISER)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2, {"advertisers": [q], "region": country.upper(), "maxResults": limit}, limit)
            advertisers = {}
            for item in items:
                ad = _normalize_ad(item, "google_ad_library")
                name = ad["advertiser"]["name"] or ad["advertiser"]["id"]
                if name:
                    advertisers[name] = ad["advertiser"]
            return {"query": q, "country": country.upper(), "totalReturned": len(advertisers), "advertisers": list(advertisers.values())}

        return ApiResponse(data=await cached_or_run("ad-library.google.advertiser-search", {"q": q, "country": country, "limit": limit, "v": 3}, _run, ctx, use_cache=cache))


@router.get("/linkedin/search-ads", summary="Search LinkedIn Ad Library")
async def linkedin_search_ads(
    q: str = Query(..., min_length=2),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/ad-library/linkedin/search-ads", platform="linkedin_ad_library", resource_url=None, base_credits=_scaled(limit)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_actor(settings.APIFY_ACTOR_LINKEDIN_AD_LIBRARY, {"search": q, "country": country.upper(), "sort": "NEWEST"}, limit)
            ads = [_normalize_ad(i, "linkedin_ad_library") for i in items]
            return {"query": q, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.linkedin.search-ads", {"q": q, "country": country, "limit": limit, "v": 5}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get("/linkedin/ad-details", summary="LinkedIn ad details")
async def linkedin_ad_details(
    url: str = Query(..., description="LinkedIn Ad Library URL or ad ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    ad_url = _linkedin_ad_url(url)
    async with billed_call(caller=caller, endpoint="/v1/ad-library/linkedin/ad-details", platform="linkedin_ad_library", resource_url=ad_url, base_credits=17) as ctx:
        async def _run() -> dict[str, Any]:
            # Only the elliotpadfield actor accepts adUrls input. The s-r
            # search actor 400s without `search`, and the silentflow fallback
            # is a rented actor we no longer have — both just burned retries.
            items, _actor = await get_apify().run_with_fallback(
                [
                    (
                        settings.APIFY_ACTOR_LINKEDIN_AD_LIBRARY_DETAIL,
                        {"adUrls": [ad_url], "maxResults": 1, "includeDetails": False},
                    ),
                    (
                        settings.APIFY_ACTOR_LINKEDIN_AD_LIBRARY_DETAIL,
                        {"adUrls": [ad_url], "maxResults": 1, "includeDetails": True},
                    ),
                ],
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Ad not found")
            return _normalize_ad(items[0], "linkedin_ad_library")

        return ApiResponse(data=await cached_or_run("ad-library.linkedin.ad-details", {"url": ad_url, "v": 5}, _run, ctx, use_cache=cache))
