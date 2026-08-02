"""Public advertising library endpoints."""

from __future__ import annotations

import math
import re
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.services import (
    facebook_ads_native,
    google_ads_native,
    linkedin_ads_native,
    tiktok_ads_native,
    tiktok_creative_center,
)
from app.utils.formatters import safe_float, safe_int, safe_str
from app.utils.media_urls import utc_now_iso
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

RATE_AD_LIST = 3.5
RATE_GOOGLE_COMPANY_ADS = 3.35
# Native ATC SearchSuggestions: one proxied RPC (~$0.001). At $0.0045/credit
# with 120% markup → ceil(0.001 * 2.2 / 0.0045) = 1 credit flat.
CREDIT_GOOGLE_ADVERTISER = 1
# Native ATC SearchCreatives (+ resolve): a few proxied RPCs (~$0.001–0.003).
# 120% markup → ~1–2 credits; bill 2 flat when native succeeds.
CREDIT_GOOGLE_COMPANY_ADS = 2
# FB/LI Ad Library lists: one Decodo headless render (~$0.001–0.0015 Premium+JS).
# 120% markup → ~1 credit; bill 2 flat when native succeeds. Apify fallback keeps
# the legacy per-result RATE_AD_LIST scale.
CREDIT_AD_LIBRARY_NATIVE = 2
# TikTok Commercial Content Library: Decodo-native is the primary path (flat 2).
# Apify fallback is capped — never the old ~70-credit trap.
CREDIT_TIKTOK_AD_SEARCH = 2
CREDIT_TIKTOK_AD_SEARCH_APIFY = 5
# Creative Center Top Ads: Decodo-native is primary (flat 2). Apify fallback
# keeps ~1 credit/result after markup (~$0.003/ad).
CREDIT_TIKTOK_TOP_ADS = 2
RATE_TIKTOK_TOP_ADS = 1.0
CREDIT_TIKTOK_TOP_ADS_MIN = 2


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


_AMOUNT_TOKEN = re.compile(
    r"(?P<prefix>[<>≤≥]?)\s*\$?\s*(?P<num>\d+(?:\.\d+)?)\s*(?P<suffix>[KMB])?",
    re.I,
)


def _amount_token_to_number(num: str, suffix: str | None) -> float | None:
    try:
        value = float(num)
    except (TypeError, ValueError):
        return None
    mult = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get((suffix or "").upper(), 1)
    return value * mult


def _parse_meta_range(raw: Any, *, currency_default: str | None = None) -> dict[str, Any] | None:
    """Parse Meta display strings / bound objects into ``{min,max,currency?,raw}``.

    Examples: ``">1M"``, ``"$600K - $700K"``, ``"≤999"``,
    ``{"lower_bound": "100", "upper_bound": "199", "currency": "USD"}``.
    """
    if raw in (None, "", [], {}):
        return None
    if isinstance(raw, dict):
        lo = safe_float(raw.get("lower_bound") or raw.get("min") or raw.get("lower"))
        hi = safe_float(raw.get("upper_bound") or raw.get("max") or raw.get("upper"))
        if lo is None and hi is None:
            return None
        out: dict[str, Any] = {
            "min": int(lo) if lo is not None else None,
            "max": int(hi) if hi is not None else None,
            "raw": safe_str(raw.get("text") or raw.get("raw")) or None,
        }
        cur = safe_str(raw.get("currency")) or currency_default
        if cur:
            out["currency"] = cur
        return out

    text = safe_str(raw) or str(raw).strip()
    if not text:
        return None
    tokens = list(_AMOUNT_TOKEN.finditer(text))
    if not tokens:
        return {"min": None, "max": None, "raw": text, **({"currency": currency_default} if currency_default else {})}

    def tok_val(m: re.Match[str]) -> tuple[float | None, str]:
        return _amount_token_to_number(m.group("num"), m.group("suffix")), (m.group("prefix") or "")

    if len(tokens) >= 2:
        a, _ = tok_val(tokens[0])
        b, _ = tok_val(tokens[1])
        lo, hi = (a, b) if (a is not None and b is not None and a <= b) else (b, a)
        out = {
            "min": int(lo) if lo is not None else None,
            "max": int(hi) if hi is not None else None,
            "raw": text,
        }
        if currency_default or "$" in text:
            out["currency"] = currency_default or "USD"
        return out

    val, prefix = tok_val(tokens[0])
    if val is None:
        return {"min": None, "max": None, "raw": text}
    out = {"raw": text}
    if currency_default or "$" in text:
        out["currency"] = currency_default or "USD"
    if prefix in {">", "≥"}:
        out["min"] = int(val)
        out["max"] = None
    elif prefix in {"<", "≤"}:
        out["min"] = None
        out["max"] = int(val)
    else:
        out["min"] = int(val)
        out["max"] = int(val)
    return out


def _fb_typed_images(snapshot: dict[str, Any], item: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for img in _listify(snapshot.get("images")) + _listify(item.get("images")):
        if isinstance(img, str):
            url = safe_str(img)
            if url:
                out.append({"url": url, "resizedUrl": None})
            continue
        if not isinstance(img, dict):
            continue
        url = safe_str(img.get("originalImageUrl") or img.get("url") or img.get("src"))
        resized = safe_str(img.get("resizedImageUrl"))
        if url or resized:
            out.append({"url": url or resized, "resizedUrl": resized})
    return out


def _fb_typed_videos(snapshot: dict[str, Any], item: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for vid in _listify(snapshot.get("videos")) + _listify(item.get("videos")):
        if isinstance(vid, str):
            url = safe_str(vid)
            if url:
                out.append({"url": url, "sdUrl": None, "previewUrl": None})
            continue
        if not isinstance(vid, dict):
            continue
        hd = safe_str(vid.get("videoHdUrl") or vid.get("videoUrl") or vid.get("url"))
        sd = safe_str(vid.get("videoSdUrl"))
        preview = safe_str(vid.get("videoPreviewImageUrl"))
        if hd or sd:
            out.append({"url": hd or sd, "sdUrl": sd, "previewUrl": preview})
    return out


def _fb_cards(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for card in _listify(snapshot.get("cards")):
        if not isinstance(card, dict):
            continue
        body = card.get("body")
        if isinstance(body, dict):
            body = body.get("text")
        out.append(
            {
                "text": safe_str(body),
                "headline": safe_str(card.get("title")),
                "cta": safe_str(card.get("ctaText")),
                "landingUrl": safe_str(card.get("linkUrl")),
                "linkDescription": safe_str(card.get("linkDescription")),
                "caption": safe_str(card.get("caption")),
                "imageUrl": safe_str(card.get("originalImageUrl") or card.get("resizedImageUrl")),
                "videoUrl": safe_str(card.get("videoHdUrl") or card.get("videoSdUrl")),
                "videoPreviewUrl": safe_str(card.get("videoPreviewImageUrl")),
            }
        )
    return out


def _facebook_ad_url(value: str) -> str:
    _reject_ad_platform_mismatch(value, "facebook", "https://www.facebook.com/ads/library/?id=123456789")
    value = value.strip()
    if value.isdigit():
        return f"https://www.facebook.com/ads/library/?id={value}"
    return value


def _facebook_search_url(
    q: str,
    country: str,
    *,
    active_status: str = "active",
    ad_type: str = "all",
    search_type: str = "keyword_unordered",
    media_type: str = "all",
    sort_by: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    return facebook_ads_native.search_url(
        q,
        country,
        active_status=active_status,
        ad_type=ad_type,
        search_type=search_type,
        media_type=media_type,
        sort_by=sort_by,
        start_date=start_date,
        end_date=end_date,
    )


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
    region = (value or "GB").strip().upper()
    return region or "GB"


def _tiktok_library_date_iso(value: Any) -> str | None:
    """Normalize TikTok library dates (often ``MM/DD/YYYY``) to ISO-8601 UTC."""
    raw = safe_str(value)
    if not raw:
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}T", raw):
        return raw
    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        return f"{raw}T00:00:00.000Z"
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", raw)
    if not m:
        return raw
    month, day, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return raw
    return f"{year:04d}-{month:02d}-{day:02d}T00:00:00.000Z"


def _tiktok_reach_range(value: Any) -> dict[str, Any] | None:
    """Parse library reach bands like ``0-1K`` / ``1K-10K`` into min/max."""
    raw = safe_str(value)
    if not raw:
        return None

    def _num(token: str) -> int | None:
        t = token.strip().upper().replace(",", "")
        m = re.fullmatch(r"(\d+(?:\.\d+)?)([KMB])?", t)
        if not m:
            return None
        n = float(m.group(1))
        suf = m.group(2)
        if suf == "K":
            n *= 1_000
        elif suf == "M":
            n *= 1_000_000
        elif suf == "B":
            n *= 1_000_000_000
        return int(n)

    parts = re.split(r"\s*[-–—]\s*", raw)
    if len(parts) == 2:
        lo, hi = _num(parts[0]), _num(parts[1])
        if lo is not None or hi is not None:
            return {"min": lo, "max": hi, "raw": raw}
    single = _num(raw)
    if single is not None:
        return {"min": single, "max": single, "raw": raw}
    return {"min": None, "max": None, "raw": raw}


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


def _google_impressions(item: dict[str, Any]) -> str | None:
    """Google ATC often exposes impressionsMin/Max rather than a single count."""
    direct = _first(
        item.get("impressions"),
        item.get("impressionsRange"),
        item.get("impressionRange"),
        item.get("totalImpressionsInterval"),
    )
    if direct not in (None, "", [], {}):
        return safe_str(direct) or str(direct)
    lo = safe_str(item.get("impressionsMin"))
    hi = safe_str(item.get("impressionsMax"))
    if lo and hi and lo != hi:
        return f"{lo}-{hi}"
    return lo or hi


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
        item.get("targetedOrReachedCountries"),
        snapshot.get("countryIsoCode"),
        snapshot.get("country"),
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
        "impressions": _google_impressions(item)
        if platform == "google_ad_library"
        else (
            # Facebook: do not conflate reachEstimate with impressions (commercial
            # ads often have neither; political ads have impressionsText).
            _first(
                item.get("impressions"),
                item.get("impressionsRange"),
                _dig(item, "impressionsWithIndex", "impressionsText"),
                _dig(item, "impressionsWithIndex", "impressions_text"),
            )
            if platform == "facebook_ad_library"
            else _first(
                item.get("impressions"),
                item.get("impressionsRange"),
                _dig(item, "impressionsWithIndex", "impressionsText"),
                item.get("reachEstimate"),
                item.get("reach"),
                item.get("reachRange"),
                item.get("impressionRange"),
                item.get("totalImpressionsInterval"),
                item.get("impressionsMin"),
                item.get("uniqueUsersSeen"),
                item.get("estimatedAudience"),
                item.get("euTotalReach"),
            )
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
            "location": safe_str(
                _first(
                    advertiser.get("location") if isinstance(advertiser, dict) else None,
                    item.get("advertiserLocation"),
                    item.get("advertiser_location"),
                    item.get("registeredLocation"),
                )
            ),
        },
        "media": media,
    }
    if platform == "tiktok_ad_library":
        # Align date shape with Facebook/Google Ad Library (ISO-8601).
        normalized["firstShown"] = _tiktok_library_date_iso(normalized.get("firstShown"))
        normalized["lastShown"] = _tiktok_library_date_iso(normalized.get("lastShown"))
        reach_range = _tiktok_reach_range(normalized.get("impressions"))
        if reach_range:
            normalized["impressionsRange"] = reach_range
    if platform == "linkedin_ad_library":
        # LinkedIn Ad Library transparency extras (additive; SC-parity).
        description = safe_str(
            _first(item.get("description"), item.get("body"), item.get("bodyText"))
        )
        destination = safe_str(
            _first(item.get("destinationUrl"), normalized.get("landingUrl"))
        )
        targeting = item.get("targeting") if isinstance(item.get("targeting"), dict) else None
        if targeting:
            targeting = {str(k): safe_str(v) for k, v in targeting.items() if safe_str(v)}
        imp_by = item.get("impressionsByCountry")
        impressions_by_country: list[dict[str, Any]] = []
        if isinstance(imp_by, list):
            for row in imp_by:
                if not isinstance(row, dict):
                    continue
                impressions_by_country.append(
                    {
                        "country": safe_str(row.get("country") or row.get("name")),
                        "impressions": safe_str(
                            row.get("impressions") or row.get("share") or row.get("value")
                        ),
                    }
                )
        carousel = [
            str(u)
            for u in _listify(item.get("carouselImages") or item.get("carousel_images"))
            if isinstance(u, str) and u.startswith("http")
        ]
        countries = item.get("countries")
        if isinstance(countries, str):
            countries = [c.strip().upper() for c in countries.split(",") if c.strip()]
        elif isinstance(countries, list):
            countries = [str(c).upper() for c in countries if c]
        else:
            countries = []
        normalized.update(
            {
                "description": description,
                "destinationUrl": destination,
                "adDuration": safe_str(item.get("adDuration") or item.get("dateRange")),
                "startDate": safe_str(item.get("startDate") or normalized.get("firstShown")),
                "endDate": safe_str(item.get("endDate") or normalized.get("lastShown")),
                "totalImpressions": safe_str(
                    item.get("totalImpressions") or normalized.get("impressions")
                ),
                "impressionsByCountry": impressions_by_country,
                "targeting": targeting,
                "carouselImages": carousel,
                "paidForBy": safe_str(item.get("paidForBy") or item.get("payer")),
                "countries": countries,
            }
        )
        if not normalized.get("landingUrl") and destination:
            normalized["landingUrl"] = destination
    adv = normalized["advertiser"]
    if platform == "facebook_ad_library":
        # Additive fields for competitor intel — existing keys above stay stable.
        spend_raw = normalized.get("spend")
        impressions_raw = normalized.get("impressions")
        # Meta sometimes returns spend as a bound object; keep string `spend` for
        # legacy clients and expose structured spendRange/impressionsRange.
        if isinstance(spend_raw, dict):
            normalized["spend"] = safe_str(
                spend_raw.get("text")
                or spend_raw.get("raw")
                or (
                    f"${spend_raw.get('lower_bound')} - ${spend_raw.get('upper_bound')}"
                    if spend_raw.get("lower_bound") is not None
                    else None
                )
            )
        reach_raw = item.get("reachEstimate")
        if isinstance(reach_raw, dict):
            reach_display = safe_str(reach_raw.get("text") or reach_raw.get("raw"))
        else:
            reach_display = safe_str(reach_raw) if reach_raw not in (None, "", [], {}) else None
        platforms = item.get("publisherPlatforms") or item.get("publisher_platform") or []
        if isinstance(platforms, str):
            platforms = [platforms]
        categories = snapshot.get("pageCategories") or []
        if not isinstance(categories, list):
            categories = [categories] if categories else []
        political = item.get("politicalCountries") or []
        if not isinstance(political, list):
            political = [political] if political else []
        normalized.update(
            {
                "isActive": item.get("isActive"),
                "publisherPlatforms": [str(p).upper() for p in platforms if p],
                "caption": safe_str(snapshot.get("caption")),
                "linkDescription": safe_str(snapshot.get("linkDescription")),
                "brandedContent": snapshot.get("brandedContent"),
                "disclaimerLabel": safe_str(snapshot.get("disclaimerLabel")),
                "byline": safe_str(snapshot.get("byline")),
                "reachEstimate": reach_display,
                "reachEstimateRange": _parse_meta_range(reach_raw),
                "totalActiveTime": safe_int(item.get("totalActiveTime")),
                "politicalCountries": [str(c) for c in political if c],
                "pageLikeCount": safe_int(snapshot.get("pageLikeCount")),
                "pageCategories": [str(c) for c in categories if c],
                "pageEntityType": safe_str(snapshot.get("pageEntityType")),
                "cards": _fb_cards(snapshot),
                "images": _fb_typed_images(snapshot, item),
                "videos": _fb_typed_videos(snapshot, item),
                "spendRange": _parse_meta_range(spend_raw, currency_default="USD"),
                "impressionsRange": _parse_meta_range(impressions_raw),
                "fetchedAt": utc_now_iso(),
            }
        )
        like_count = safe_int(snapshot.get("pageLikeCount"))
        if like_count is not None:
            adv["likeCount"] = like_count
        if categories:
            adv["categories"] = [str(c) for c in categories if c]
        entity = safe_str(snapshot.get("pageEntityType"))
        if entity:
            adv["entityType"] = entity
    if platform == "google_ad_library" and not adv["url"] and adv["id"]:
        adv["url"] = f"https://adstransparency.google.com/advertiser/{adv['id']}"
    # TikTok withhold most delivery metadata — omit empties.
    # LinkedIn now surfaces targeting/dates/impressions; keep stable nulls there.
    # Facebook sometimes returns spend/impressions, so keep explicit nulls there.
    if platform == "tiktok_ad_library":
        for key in (
            "cta",
            "landingUrl",
            "firstShown",
            "lastShown",
            "impressions",
            "spend",
            "country",
            "headline",
            "text",
        ):
            if normalized.get(key) in (None, "", [], {}):
                normalized.pop(key, None)
    elif platform == "linkedin_ad_library":
        # Drop only legacy empties that stay unused; keep new transparency keys.
        for key in ("spend",):
            if normalized.get(key) in (None, "", [], {}):
                normalized.pop(key, None)
    elif platform == "google_ad_library":
        # SearchCreatives (native) returns image/video creatives without copy /
        # landing / country; detail actors sometimes fill those — omit empties.
        for key in ("cta", "spend", "impressions", "text", "headline", "landingUrl", "country"):
            if normalized.get(key) in (None, "", [], {}):
                normalized.pop(key, None)
    # Advertiser logo is never supplied by Google Ads Transparency; omit empty
    # advertiser keys across libraries when upstream gave nothing.
    for key in ("id", "name", "url", "logo", "location"):
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
    q: str = Query(..., min_length=2, description="Keyword, brand, or advertiser to search."),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(
        20,
        ge=1,
        le=200,
        description="Max ads to return per call (default 20, max 200). Native HTML page may return fewer.",
    ),
    status: Literal["ALL", "ACTIVE", "INACTIVE"] = Query(
        "ACTIVE",
        description="Ad delivery status filter. Default ACTIVE — use ALL for historical/inactive ads.",
    ),
    media_type: Literal["ALL", "IMAGE", "VIDEO", "MEME", "IMAGE_AND_MEME", "NONE"] = Query(
        "ALL",
        description="Creative media filter (Meta Ad Library media_type).",
    ),
    ad_type: Literal["all", "political_and_issue_ads"] = Query(
        "all",
        description="Ad type filter. political_and_issue_ads is required for spend/impressions on many markets.",
    ),
    search_type: Literal["keyword_unordered", "keyword_exact_phrase"] = Query(
        "keyword_unordered",
        description="Keyword matching: unordered tokens vs exact phrase.",
    ),
    sort_by: Literal["total_impressions", "relevancy_monthly_grouped"] | None = Query(
        None,
        description="Meta sort mode (sort_data[mode]). Omit for Meta default.",
    ),
    start_date: str | None = Query(
        None,
        description="Only ads with delivery start on/after this date (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    ),
    end_date: str | None = Query(
        None,
        description="Only ads with delivery start on/before this date (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    active_status = status.lower()
    media = media_type.lower()
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/facebook/search",
        platform="facebook_ad_library",
        resource_url=None,
        base_credits=_scaled(limit),
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await facebook_ads_native.search_ads(
                q,
                country=country,
                limit=limit,
                active_status=active_status,
                ad_type=ad_type,
                search_type=search_type,
                media_type=media,
                sort_by=sort_by,
                start_date=start_date,
                end_date=end_date,
            )
            if native is not None:
                ctx["source"] = "direct"
                ads = [_normalize_ad(i, "facebook_ad_library") for i in (native.get("ads") or [])]
                ctx["credits_override"] = CREDIT_AD_LIBRARY_NATIVE
                return {
                    "query": q,
                    "country": country.upper(),
                    "status": status,
                    "limit": limit,
                    "totalReturned": len(ads),
                    "searchResultsCount": native.get("searchResultsCount"),
                    "hasMore": bool(native.get("hasMore")),
                    "nextCursor": None,
                    "ads": ads,
                }

            library_url = _facebook_search_url(
                q,
                country,
                active_status=active_status,
                ad_type=ad_type,
                search_type=search_type,
                media_type=media,
                sort_by=sort_by,
                start_date=start_date,
                end_date=end_date,
            )
            items = await _run_actor(
                settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                {"startUrls": [{"url": library_url}], "resultsLimit": limit, "isDetailsPerAd": False},
                limit,
            )
            ctx["source"] = "apify"
            ads = [_normalize_ad(i, "facebook_ad_library") for i in items]
            return {
                "query": q,
                "country": country.upper(),
                "status": status,
                "limit": limit,
                "totalReturned": len(ads),
                "searchResultsCount": None,
                "hasMore": len(ads) >= limit,
                "nextCursor": None,
                "ads": ads,
            }

        data = await cached_or_run(
            "ad-library.facebook.search",
            {
                "q": q,
                "country": country,
                "limit": limit,
                "status": status,
                "media_type": media_type,
                "ad_type": ad_type,
                "search_type": search_type,
                "sort_by": sort_by or "",
                "start_date": start_date or "",
                "end_date": end_date or "",
                "v": 7,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/facebook/company-ads",
        platform="facebook_ad_library",
        resource_url=url,
        base_credits=_scaled(limit),
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await facebook_ads_native.company_ads(url, country=country, limit=limit)
            if native is not None:
                ctx["source"] = "direct"
                ads = [_normalize_ad(i, "facebook_ad_library") for i in native]
                ctx["credits_override"] = CREDIT_AD_LIBRARY_NATIVE
                return {"url": url, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

            items = await _run_actor(
                settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                {"startUrls": [{"url": url}], "resultsLimit": limit, "isDetailsPerAd": True},
                limit,
            )
            ctx["source"] = "apify"
            ads = [_normalize_ad(i, "facebook_ad_library") for i in items]
            return {"url": url, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.facebook.company-ads", {"url": url, "country": country, "limit": limit, "v": 6}, _run, ctx, use_cache=cache)
        if ctx.get("source") != "direct":
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/facebook/search-companies",
        platform="facebook_ad_library",
        resource_url=None,
        base_credits=_scaled(limit),
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await facebook_ads_native.search_companies(q, country=country, limit=limit)
            items = native
            if native is not None:
                ctx["source"] = "direct"
                ctx["credits_override"] = CREDIT_AD_LIBRARY_NATIVE
            else:
                items = await _run_actor(
                    settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                    {"startUrls": [{"url": _facebook_search_url(q, country)}], "resultsLimit": limit, "isDetailsPerAd": False},
                    limit,
                )
                ctx["source"] = "apify"

            advertisers: dict[str, Any] = {}
            for item in items or []:
                ad = _normalize_ad(item, "facebook_ad_library")
                adv = ad["advertiser"]
                key = adv.get("id") or adv.get("name")
                if key and key not in advertisers:
                    advertisers[key] = adv
                if len(advertisers) >= limit:
                    break
            companies = list(advertisers.values())
            return {"query": q, "country": country.upper(), "totalReturned": len(companies), "companies": companies}

        data = await cached_or_run("ad-library.facebook.search-companies", {"q": q, "country": country, "limit": limit, "v": 4}, _run, ctx, use_cache=cache)
        if ctx.get("source") != "direct":
            ctx["credits_override"] = _scaled(len(data["companies"]))
        return ApiResponse(data=data)


def _transcript_from_ad(ad: dict[str, Any], ad_url: str) -> dict[str, Any]:
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


async def _facebook_ad_native_or_apify(ad_url: str, ctx: dict[str, Any]) -> dict[str, Any]:
    """Native Decodo detail first; Apify fallthrough (17 credits)."""
    settings = get_settings()
    native = await facebook_ads_native.ad_details(ad_url)
    if native is not None:
        ctx["source"] = "direct"
        return _normalize_ad(native, "facebook_ad_library")
    items = await _run_actor(
        settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
        {"startUrls": [{"url": ad_url}], "resultsLimit": 1, "isDetailsPerAd": True},
        1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Ad not found")
    ctx["source"] = "apify"
    ctx["credits_override"] = 17
    return _normalize_ad(items[0], "facebook_ad_library")


@router.get("/facebook/ad-details", summary="Meta/Facebook ad details")
async def facebook_ad_details(
    url: str = Query(..., description="Meta Ad Library ad URL or ad ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    ad_url = _facebook_ad_url(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/facebook/ad-details",
        platform="facebook_ad_library",
        resource_url=ad_url,
        base_credits=CREDIT_AD_LIBRARY_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            return await _facebook_ad_native_or_apify(ad_url, ctx)

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.facebook.ad-details",
                {"url": ad_url, "v": 5},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get("/facebook/ad-transcript", summary="Meta/Facebook ad transcript / creative text")
async def facebook_ad_transcript(
    url: str = Query(..., description="Meta Ad Library ad URL or ad ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    ad_url = _facebook_ad_url(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/facebook/ad-transcript",
        platform="facebook_ad_library",
        resource_url=ad_url,
        base_credits=CREDIT_AD_LIBRARY_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            ad = await _facebook_ad_native_or_apify(ad_url, ctx)
            return _transcript_from_ad(ad, ad_url)

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.facebook.ad-transcript",
                {"url": ad_url, "v": 4},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get(
    "/tiktok/search",
    summary="Search TikTok Ad Library",
    description=(
        "Search TikTok's Commercial Content Library (library.tiktok.com / EU DSA) "
        "as clean JSON. Flat 2 credits on the native path. firstShown/lastShown are "
        "ISO-8601. Default country is GB (this library is EU-led; region=US is often "
        "empty). This is not TikTok Creative Center — CTR / play-rate ranking metrics "
        "live on Creative Center, a different public surface."
    ),
)
async def tiktok_search(
    q: str = Query(..., min_length=2, description="Keyword or advertiser name (min 2 characters)."),
    country: str = Query(
        "GB",
        min_length=2,
        max_length=2,
        description="Two-letter ISO country code. Default GB (EU Commercial Content Library; US often empty).",
    ),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    region = _tiktok_region(country)
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/tiktok/search",
        platform="tiktok_ad_library",
        resource_url=None,
        base_credits=CREDIT_TIKTOK_AD_SEARCH,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Decodo-native Commercial Content Library first (flat 2 credits).
            native = await tiktok_ads_native.search_ads(q, country=region, limit=limit)
            if native is not None:
                ctx["source"] = "direct"
                ads = [_normalize_ad(i, "tiktok_ad_library") for i in native]
                ctx["credits_override"] = CREDIT_TIKTOK_AD_SEARCH
                return {"query": q, "country": region, "totalReturned": len(ads), "ads": ads}

            items = await _run_actor(
                settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY,
                {"source": "both", "searchTerms": [q], "countries": [region], "maxResults": limit},
                limit,
            )
            ctx["source"] = "apify"
            ads = [_normalize_ad(i, "tiktok_ad_library") for i in items]
            return {"query": q, "country": region, "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run(
            "ad-library.tiktok.search",
            {"q": q, "country": region, "limit": limit, "v": 6},
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
            ctx["credits_override"] = CREDIT_TIKTOK_AD_SEARCH_APIFY
        return ApiResponse(data=data)


@router.get(
    "/tiktok/top-ads",
    summary="TikTok Creative Center Top Ads",
    description=(
        "High-performing TikTok ads from Creative Center Top Ads "
        "(ads.tiktok.com/business/creativecenter) as clean JSON — title, brandName, "
        "likes, ctr/ctrTier, costTier, industry/objective, isSparkAd, and video{} "
        "renditions. Filter with country (default US), period (7/30/180), orderBy "
        "(for_you|likes|ctr|impressions|cost), optional q/industry/objective/adFormat. "
        "Flat 2 credits on the Decodo-native path; Apify fallback is ~1 credit per "
        "returned ad (minimum 2). This is not the EU Commercial Content Library — "
        "use /v1/ad-library/tiktok/search for DSA transparency ads."
    ),
)
async def tiktok_top_ads(
    q: str | None = Query(
        None,
        description="Optional keyword filter (brand, product, or creative theme).",
    ),
    country: str = Query(
        "US",
        min_length=2,
        max_length=2,
        description="Two-letter ISO country code. Default US.",
    ),
    period: int = Query(
        30,
        description="Lookback window in days: 7, 30, or 180. Default 30.",
    ),
    order_by: str = Query(
        "for_you",
        alias="orderBy",
        description="Sort: for_you, likes, ctr, impressions, or cost.",
    ),
    industry: str | None = Query(
        None,
        description="Optional industry filter (Creative Center industry key or label).",
    ),
    objective: str | None = Query(
        None,
        description="Optional campaign objective filter (e.g. Traffic, Conversion).",
    ),
    ad_format: str | None = Query(
        None,
        alias="adFormat",
        description="Optional format filter: spark, non_spark, or actor label.",
    ),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    region = (country or "US").strip().upper() or "US"
    try:
        period_days = tiktok_creative_center.normalize_period(period)
        order_label = tiktok_creative_center.normalize_order_by(order_by)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/tiktok/top-ads",
        platform="tiktok_ad_library",
        resource_url=None,
        base_credits=CREDIT_TIKTOK_TOP_ADS,
    ) as ctx:
        order_key = order_by.strip().lower().replace(" ", "_").replace("-", "_")

        async def _run() -> dict[str, Any]:
            # Decodo XHR capture of creative_radar top_ads/v2/list first.
            native = await tiktok_creative_center.search_top_ads(
                country=region,
                period=period_days,
                order_by=order_label,
                limit=limit,
                q=q,
                industry=industry,
                objective=objective,
                ad_format=ad_format,
            )
            # Empty native with active filters → try Apify (client-side filter may
            # have dropped everything or Creative Center returned no match).
            filtered = bool(
                (q or "").strip() or industry or objective or ad_format
            )
            if native is not None and (native or not filtered):
                ctx["source"] = "direct"
                ads = [
                    tiktok_creative_center.normalize_top_ad(i)
                    for i in native
                    if isinstance(i, dict) and (i.get("ad_id") or i.get("id"))
                ]
                ctx["credits_override"] = CREDIT_TIKTOK_TOP_ADS
                return {
                    "query": (q or "").strip() or None,
                    "country": region,
                    "period": period_days,
                    "orderBy": order_key,
                    "totalReturned": len(ads),
                    "ads": ads,
                }

            payload = tiktok_creative_center.apify_input(
                country=region,
                period=period_days,
                order_by=order_label,
                limit=limit,
                q=q,
                industry=industry,
                objective=objective,
                ad_format=ad_format,
            )
            items = await _run_actor(
                settings.APIFY_ACTOR_TIKTOK_CREATIVE_CENTER,
                payload,
                limit,
            )
            ctx["source"] = "apify"
            ads = [
                tiktok_creative_center.normalize_top_ad(i)
                for i in items
                if isinstance(i, dict) and (i.get("ad_id") or i.get("id"))
            ]
            return {
                "query": (q or "").strip() or None,
                "country": region,
                "period": period_days,
                "orderBy": order_key,
                "totalReturned": len(ads),
                "ads": ads,
            }

        data = await cached_or_run(
            "ad-library.tiktok.top-ads",
            {
                "q": q or "",
                "country": region,
                "period": period_days,
                "orderBy": order_label,
                "industry": industry or "",
                "objective": objective or "",
                "adFormat": ad_format or "",
                "limit": limit,
                "v": 2,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
            n = len(data.get("ads") or [])
            ctx["credits_override"] = (
                CREDIT_TIKTOK_TOP_ADS_MIN
                if n == 0
                else _scaled(n, RATE_TIKTOK_TOP_ADS, CREDIT_TIKTOK_TOP_ADS_MIN)
            )
        return ApiResponse(data=data)


@router.get("/tiktok/ad-details", summary="TikTok ad details")
async def tiktok_ad_details(
    url: str = Query(..., description="TikTok Ad Library URL or ad ID"),
    country: str = Query(
        "GB",
        min_length=2,
        max_length=2,
        description="Two-letter ISO country code. Default GB.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    ad_id = _tiktok_ad_id(url)
    region = _tiktok_region(country)
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/tiktok/ad-details",
        platform="tiktok_ad_library",
        resource_url=ad_id,
        base_credits=CREDIT_AD_LIBRARY_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await tiktok_ads_native.ad_details(ad_id, country=region)
            if native:
                ctx["source"] = "direct"
                return _normalize_ad(native, "tiktok_ad_library")

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
            ctx["source"] = "apify"
            ctx["credits_override"] = 17
            return _normalize_ad(best, "tiktok_ad_library")

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.tiktok.ad-details",
                {"ad_id": ad_id, "country": region, "v": 5},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get("/google/company-ads", summary="Google Ads Transparency Center company ads")
async def google_company_ads(
    advertiser: str = Query(
        ...,
        min_length=2,
        description="Advertiser name, domain (e.g. nike.com), or Google advertiser ID (AR…).",
    ),
    country: str = Query(
        "US",
        min_length=2,
        max_length=8,
        description="Two-letter ISO country / region code (soft filter). Alias: region.",
    ),
    region: str | None = Query(
        None,
        min_length=2,
        max_length=8,
        description="Alias for country (ISO code). When set, overrides country.",
    ),
    limit: int = Query(20, ge=1, le=200),
    cursor: str | None = Query(
        None,
        description="Pagination cursor from a previous response's nextCursor.",
    ),
    start_date: str | None = Query(
        None,
        description="Optional YYYY-MM-DD — keep creatives whose shown window overlaps this start.",
    ),
    end_date: str | None = Query(
        None,
        description="Optional YYYY-MM-DD — keep creatives whose shown window overlaps this end.",
    ),
    topic: str = Query(
        "all",
        description='Ad topic filter. Only "all" is supported (commercial ATC). "political" is not available here.',
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    country_code = (region or country or "US").strip().upper()
    if country_code in {"UK"}:
        country_code = "GB"
    topic_norm = (topic or "all").strip().lower()
    if topic_norm not in {"all", "political"}:
        raise HTTPException(status_code=400, detail='topic must be "all" or "political"')
    if topic_norm == "political":
        raise HTTPException(
            status_code=400,
            detail=(
                "Political ads are not available on this commercial Ads Transparency endpoint. "
                "Use topic=all for public commercial creatives."
            ),
        )
    for label, value in (("start_date", start_date), ("end_date", end_date)):
        if value and google_ads_native._parse_ymd(value) is None:
            raise HTTPException(status_code=400, detail=f"{label} must be YYYY-MM-DD")

    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/google/company-ads",
        platform="google_ad_library",
        resource_url=None,
        base_credits=_scaled(limit, RATE_GOOGLE_COMPANY_ADS),
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # 1) Native ATC SearchCreatives (proxy/direct) — ~ms–seconds, ~$0.
            # Empty ads with a result envelope means "resolved but no creatives";
            # only transport failure (None) falls through to Apify.
            native = await google_ads_native.fetch_company_ads(
                advertiser,
                country=country_code,
                limit=limit,
                cursor=cursor,
                start_date=start_date,
                end_date=end_date,
            )
            if native is not None:
                if native.get("error") == "invalid_cursor":
                    raise HTTPException(status_code=400, detail="Invalid cursor")
                ctx["source"] = "direct"
                ads = [_normalize_ad(i, "google_ad_library") for i in (native.get("ads") or [])]
                ctx["credits_override"] = CREDIT_GOOGLE_COMPANY_ADS
                return {
                    "advertiser": advertiser,
                    "country": country_code,
                    "totalReturned": len(ads),
                    "adsCountEstimate": native.get("adsCountEstimate"),
                    "hasMore": bool(native.get("hasMore")),
                    "nextCursor": native.get("nextCursor"),
                    "ads": ads,
                }

            # 2) Apify last resort (no cursor paging on this path).
            if cursor:
                raise HTTPException(
                    status_code=502,
                    detail="Google Ads Transparency unavailable for cursor continuation; retry without cursor.",
                )
            items = await _run_actor(
                settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2,
                {"advertisers": [advertiser], "region": country_code, "maxResults": limit},
                limit,
            )
            ctx["source"] = "apify"
            ads = [_normalize_ad(i, "google_ad_library") for i in items]
            if start_date or end_date:
                start_d = google_ads_native._parse_ymd(start_date)
                end_d = google_ads_native._parse_ymd(end_date)
                ads = [
                    a
                    for a in ads
                    if google_ads_native._creative_in_date_window(a, start_d, end_d)
                ]
            return {
                "advertiser": advertiser,
                "country": country_code,
                "totalReturned": len(ads),
                "adsCountEstimate": None,
                "hasMore": False,
                "nextCursor": None,
                "ads": ads,
            }

        data = await cached_or_run(
            "ad-library.google.company-ads",
            {
                "advertiser": advertiser,
                "country": country_code,
                "limit": limit,
                "cursor": cursor or "",
                "start_date": start_date or "",
                "end_date": end_date or "",
                "v": 7,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/google/ad-details",
        platform="google_ad_library",
        resource_url=creative_id,
        base_credits=CREDIT_GOOGLE_COMPANY_ADS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await google_ads_native.fetch_ad_details(
                advertiser_id, creative, country=country
            )
            if native:
                ctx["source"] = "direct"
                return _normalize_ad(native, "google_ad_library")

            items = await _run_actor(
                settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2,
                {"advertisers": [advertiser_id], "region": country.upper(), "maxResults": 50},
                50,
            )
            for item in items:
                if item.get("creativeId") == creative or item.get("adCreativeId") == creative:
                    ctx["source"] = "apify"
                    ctx["credits_override"] = 17
                    return _normalize_ad(item, "google_ad_library")
            raise HTTPException(status_code=404, detail="Ad not found")

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.google.ad-details",
                {"creative_id": creative_id, "country": country, "v": 5},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get("/google/advertiser-search", summary="Search Google Ads advertisers")
async def google_advertiser_search(
    q: str = Query(..., min_length=2),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(10, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/google/advertiser-search",
        platform="google_ad_library",
        resource_url=None,
        base_credits=CREDIT_GOOGLE_ADVERTISER,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # 1) Native ATC SearchSuggestions (proxy/direct) — ~ms, ~$0.
            native = await google_ads_native.search_advertisers(
                q, country=country, limit=limit
            )
            if native is not None:
                ctx["source"] = "direct"
                return {
                    "query": q,
                    "country": country.upper(),
                    "totalReturned": len(native),
                    "advertisers": native,
                }

            # 2) Apify last resort (rare; still billed at the native flat rate).
            items = await _run_actor(
                settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2,
                {"advertisers": [q], "region": country.upper(), "maxResults": limit},
                limit,
            )
            advertisers: dict[str, Any] = {}
            for item in items:
                ad = _normalize_ad(item, "google_ad_library")
                name = ad["advertiser"].get("name") or ad["advertiser"].get("id")
                if name:
                    advertisers[name] = ad["advertiser"]
            ctx["source"] = "apify"
            return {
                "query": q,
                "country": country.upper(),
                "totalReturned": len(advertisers),
                "advertisers": list(advertisers.values()),
            }

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.google.advertiser-search",
                {"q": q, "country": country, "limit": limit, "v": 5},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get(
    "/linkedin/search-ads",
    summary="Search LinkedIn Ad Library",
    description=(
        "Search LinkedIn Ad Library as clean JSON — headline/description, targeting{}, "
        "ISO startDate/endDate + adDuration, totalImpressions + impressionsByCountry[], "
        "cta/destinationUrl, advertiser{id,name,url,logo}, and carouselImages[]. "
        "Supports countries (comma-separated), startDate/endDate, companyId, keyword, and "
        "cursor pagination (paginationToken / nextCursor). Flat 2 credits on the native path."
    ),
)
async def linkedin_search_ads(
    q: str | None = Query(
        None,
        description="Advertiser / account owner name (LinkedIn accountOwner). Min 2 chars when used.",
    ),
    keyword: str | None = Query(
        None,
        description="Optional keyword filter on ad creative copy.",
    ),
    company_id: str | None = Query(
        None,
        alias="companyId",
        description="LinkedIn numeric company id for exact advertiser match.",
    ),
    country: str = Query(
        "US",
        min_length=2,
        max_length=2,
        description="Single ISO country code. Ignored when countries is set. Default US.",
    ),
    countries: str | None = Query(
        None,
        description="Comma-separated ISO country codes (e.g. US,CA,MX). Overrides country.",
    ),
    start_date: str | None = Query(
        None,
        alias="startDate",
        description="Custom range start (YYYY-MM-DD). Use with endDate.",
    ),
    end_date: str | None = Query(
        None,
        alias="endDate",
        description="Custom range end (YYYY-MM-DD). Use with startDate.",
    ),
    cursor: str | None = Query(
        None,
        description="Pagination token from a previous response (paginationToken / nextCursor).",
    ),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    owner = (q or "").strip()
    kw = (keyword or "").strip()
    cid = (company_id or "").strip()
    if len(owner) < 2 and len(kw) < 2 and not cid:
        raise HTTPException(
            status_code=400,
            detail="Provide q (advertiser), keyword, or companyId.",
        )
    if (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=400,
            detail="startDate and endDate must be provided together (YYYY-MM-DD).",
        )
    for label, value in (("startDate", start_date), ("endDate", end_date)):
        if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise HTTPException(status_code=400, detail=f"{label} must be YYYY-MM-DD.")

    country_param = (countries or country or "US").strip()
    primary_country = country_param.split(",")[0].strip().upper() or "US"

    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/linkedin/search-ads",
        platform="linkedin_ad_library",
        resource_url=None,
        base_credits=_scaled(limit),
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await linkedin_ads_native.search_ads(
                owner or None,
                country=primary_country,
                countries=country_param,
                limit=limit,
                keyword=kw or None,
                company_id=cid or None,
                start_date=start_date,
                end_date=end_date,
                pagination_token=cursor,
                enrich=True,
            )
            if native is not None:
                ctx["source"] = "direct"
                ads = [
                    _normalize_ad(i, "linkedin_ad_library")
                    for i in (native.get("ads") or [])
                    if isinstance(i, dict)
                ]
                ctx["credits_override"] = CREDIT_AD_LIBRARY_NATIVE
                token = native.get("paginationToken")
                is_last = native.get("isLastPage")
                return {
                    "query": owner or kw or cid,
                    "keyword": kw or None,
                    "companyId": cid or None,
                    "country": primary_country,
                    "countries": [c.strip().upper() for c in country_param.split(",") if c.strip()],
                    "startDate": start_date,
                    "endDate": end_date,
                    "totalAds": native.get("totalAds"),
                    "totalReturned": len(ads),
                    "paginationToken": token,
                    "nextCursor": token,
                    "isLastPage": is_last,
                    "hasMore": (False if is_last is True else bool(token)),
                    "ads": ads,
                }

            items = await _run_actor(
                settings.APIFY_ACTOR_LINKEDIN_AD_LIBRARY,
                {
                    "search": owner or kw or cid,
                    "country": primary_country,
                    "sort": "NEWEST",
                },
                limit,
            )
            ctx["source"] = "apify"
            ads = [_normalize_ad(i, "linkedin_ad_library") for i in items]
            return {
                "query": owner or kw or cid,
                "keyword": kw or None,
                "companyId": cid or None,
                "country": primary_country,
                "countries": [c.strip().upper() for c in country_param.split(",") if c.strip()],
                "startDate": start_date,
                "endDate": end_date,
                "totalAds": None,
                "totalReturned": len(ads),
                "paginationToken": None,
                "nextCursor": None,
                "isLastPage": None,
                "hasMore": False,
                "ads": ads,
            }

        data = await cached_or_run(
            "ad-library.linkedin.search-ads",
            {
                "q": owner,
                "keyword": kw,
                "companyId": cid,
                "country": country_param,
                "startDate": start_date or "",
                "endDate": end_date or "",
                "cursor": cursor or "",
                "limit": limit,
                "v": 7,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/linkedin/ad-details",
        platform="linkedin_ad_library",
        resource_url=ad_url,
        base_credits=CREDIT_AD_LIBRARY_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await linkedin_ads_native.ad_details(ad_url)
            if native:
                ctx["source"] = "direct"
                return _normalize_ad(native, "linkedin_ad_library")

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
            ctx["source"] = "apify"
            ctx["credits_override"] = 17
            return _normalize_ad(items[0], "linkedin_ad_library")

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.linkedin.ad-details",
                {"url": ad_url, "v": 6},
                _run,
                ctx,
                use_cache=cache,
            )
        )
