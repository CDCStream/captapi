"""Public advertising library endpoints."""

from __future__ import annotations

import base64
import json
import math
import re
from typing import Any, Literal
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyClient, ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.services import (
    facebook_ads_native,
    google_ads_native,
    linkedin_ads_native,
    tiktok_ads_native,
    tiktok_creative_center,
)
from app.utils.countries import country_code_from_name
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
# Apify fallback for single-ad Google/LinkedIn details (capped — never silent 17).
CREDIT_AD_DETAILS_APIFY = 5
# FB/LI Ad Library lists: one Decodo headless render (~$0.001–0.0015 Premium+JS).
# 120% markup → ~1 credit; bill 2 flat when native succeeds. Apify fallback keeps
# the legacy per-result RATE_AD_LIST scale.
CREDIT_AD_LIBRARY_NATIVE = 2
# TikTok Commercial Content Library: Decodo-native is the primary path (flat 2).
# Apify fallback is capped — never the old ~70-credit trap.
CREDIT_TIKTOK_AD_SEARCH = 2
CREDIT_TIKTOK_AD_SEARCH_APIFY = 5
# Creative Center Top Ads: flat 2 on Decodo-native; Apify ~1 credit/result (min 2).
# Empty/timeout free. Sync wait for the real upstream JSON (no background warm).
CREDIT_TIKTOK_TOP_ADS = 2
RATE_TIKTOK_TOP_ADS = 1.0
CREDIT_TIKTOK_TOP_ADS_MIN = 2
# Measured Apify success ~74–79s. Cap at 90s — Cloudflare Proxy Read Timeout
# defaults to 125s, so 90s fits with headroom (524s only after that default).
# Exceeding 125s needs Cloudflare Enterprise (up to 6000s via Cache Rule / API).
_TIKTOK_AD_APIFY_TIMEOUT_SECS = 90.0
_TIKTOK_AD_RETRY_AFTER_SECS = 30

_DKI_RE = re.compile(
    r"\{(?:KeyWord|KEYWORD|Keyword|param\d*|CUSTOMIZER\.[^}:]+)(?::[^}]*)?\}",
    re.I,
)


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


def _fb_profile_id_from_url(url: str | None) -> str | None:
    """Numeric id in ``facebook.com/{digits}/`` (often ≠ Ad Library page_id)."""
    raw = safe_str(url)
    if not raw:
        return None
    m = re.search(r"facebook\.com/(?:profile\.php\?id=)?(\d{5,})/?", raw, re.I)
    return m.group(1) if m else None


def _fb_company_matches_query(name: str | None, query: str) -> bool:
    """Entity search: brand tokens must appear in the page name (not ad copy)."""
    q = (query or "").strip().lower()
    n = (name or "").strip().lower()
    if len(q) < 2 or not n:
        return False
    if q == n or n.startswith(q) or q in n:
        return True
    tokens = [t for t in re.findall(r"[a-z0-9]+", q) if len(t) >= 2]
    if not tokens:
        return False
    return all(t in n for t in tokens)


def _rank_fb_companies(companies: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    """Filter off-brand pages, then prefer exact / vanity matches."""
    matched = [c for c in companies if _fb_company_matches_query(c.get("name"), query)]
    # Empty beats Sukeban-for-nike spam — same stance as TikTok Ad Library search.
    if not matched:
        return []
    q = (query or "").strip().lower()

    def score(c: dict[str, Any]) -> tuple:
        name = (c.get("name") or "").lower()
        url = (c.get("url") or "").lower()
        exact = 1 if name == q else 0
        starts = 1 if name.startswith(q) else 0
        word = 1 if q and re.search(rf"\b{re.escape(q)}\b", name) else 0
        vanity = 1 if q and q in url and "/ads/" not in url else 0
        return (exact, starts, word, vanity, -(len(name) or 0))

    return sorted(matched, key=score, reverse=True)


def _fb_company_from_advertiser(
    adv: dict[str, Any], *, country: str = "US"
) -> dict[str, Any]:
    """Shape a search-companies row with pageId vs profileId disambiguated."""
    page_id = safe_str(adv.get("pageId") or adv.get("advertiserId") or adv.get("id"))
    url = safe_str(adv.get("url"))
    profile_id = _fb_profile_id_from_url(url)
    if profile_id and page_id and profile_id == page_id:
        profile_id = None
    library_url = None
    if page_id:
        library_url = (
            "https://www.facebook.com/ads/library/?"
            + urlencode(
                {
                    "active_status": "all",
                    "ad_type": "all",
                    "country": (country or "US").upper(),
                    "view_all_page_id": page_id,
                    "media_type": "all",
                }
            )
        )
    return {
        # `id` = Ad Library page_id — pass this (or libraryUrl) to /facebook/company-ads.
        "id": page_id,
        "pageId": page_id,
        "advertiserId": page_id,
        "profileId": profile_id,
        "name": safe_str(adv.get("name")),
        "url": url,
        "logo": safe_str(adv.get("logo")),
        "libraryUrl": library_url,
    }


def _unify_advertisers_by_id(ads: list[dict[str, Any]]) -> None:
    """Same advertiser id → one canonical name/url/logo within a response.

    Meta often emits both ``Facebook`` and ``Facebook App`` for page id
    20531316728 in one search — grouping by name then invents two brands.
    Prefer the longest non-empty name (usually the fuller brand string) and
    the richest url/logo among rows sharing that id.
    """
    if not ads:
        return
    by_id: dict[str, list[dict[str, Any]]] = {}
    for ad in ads:
        adv = ad.get("advertiser") if isinstance(ad.get("advertiser"), dict) else None
        if not adv:
            continue
        aid = safe_str(adv.get("id"))
        if not aid:
            continue
        by_id.setdefault(aid, []).append(adv)
    for aid, group in by_id.items():
        if len(group) < 2:
            continue
        names = [safe_str(a.get("name")) for a in group if safe_str(a.get("name"))]
        # Prefer longer display name; ties → first seen.
        canon_name = max(names, key=len) if names else None
        canon_url = next((safe_str(a.get("url")) for a in group if safe_str(a.get("url"))), None)
        canon_logo = next((safe_str(a.get("logo")) for a in group if safe_str(a.get("logo"))), None)
        for adv in group:
            if canon_name:
                adv["name"] = canon_name
            if canon_url and not adv.get("url"):
                adv["url"] = canon_url
            if canon_logo and not adv.get("logo"):
                adv["logo"] = canon_logo


def _encode_fb_page_cursor(after_id: str) -> str:
    payload = json.dumps({"a": after_id}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def _decode_fb_page_cursor(cursor: str | None) -> str | None:
    raw = (cursor or "").strip()
    if not raw:
        return None
    pad = "=" * (-len(raw) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(raw + pad).decode())
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return safe_str(data.get("a"))


def _paginate_ads(
    ads: list[dict[str, Any]],
    *,
    limit: int,
    cursor: str | None,
) -> tuple[list[dict[str, Any]], str | None, bool]:
    """Slice a single upstream page with an opaque after-id cursor."""
    after = _decode_fb_page_cursor(cursor)
    start = 0
    if after:
        for i, ad in enumerate(ads):
            if safe_str(ad.get("id")) == after:
                start = i + 1
                break
    page = ads[start : start + limit]
    has_more_in_page = start + limit < len(ads)
    next_cursor = (
        _encode_fb_page_cursor(safe_str(page[-1].get("id")) or "")
        if has_more_in_page and page and safe_str(page[-1].get("id"))
        else None
    )
    return page, next_cursor, has_more_in_page


def _filter_ads_by_platforms(
    ads: list[dict[str, Any]], platforms: list[str] | None
) -> list[dict[str, Any]]:
    if not platforms:
        return ads
    want = {p.upper() for p in platforms if p}
    if not want:
        return ads
    out: list[dict[str, Any]] = []
    for ad in ads:
        got = ad.get("publisherPlatforms") or []
        if not isinstance(got, list):
            continue
        labels = {str(p).upper() for p in got if p}
        if labels & want:
            out.append(ad)
    return out


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


def _fb_pct(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _fb_demographic_rows(raw: Any) -> list[dict[str, Any]] | None:
    if not isinstance(raw, list):
        return None
    out: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        age = safe_str(row.get("age") or row.get("age_range") or row.get("ageRange"))
        gender = safe_str(row.get("gender"))
        pct = _fb_pct(row.get("percentage"))
        if not age and not gender and pct is None:
            continue
        out.append({"age": age, "gender": gender, "percentage": pct})
    return out or None


def _fb_region_rows(raw: Any) -> list[dict[str, Any]] | None:
    if not isinstance(raw, list):
        return None
    out: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        region = safe_str(
            row.get("region") or row.get("name") or row.get("location") or row.get("key")
        )
        pct = _fb_pct(row.get("percentage"))
        if not region and pct is None:
            continue
        out.append({"region": region, "percentage": pct})
    return out or None


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
    advertiser = re.search(r"\b(AR[0-9]+)\b", value, re.I)
    creative = re.search(r"\b(CR[0-9]+)\b", value, re.I)
    return (
        advertiser.group(1).upper() if advertiser else None,
        creative.group(1).upper() if creative else None,
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


def _split_country_tokens(value: Any) -> list[str]:
    if value in (None, "", [], {}):
        return []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, dict):
                token = item.get("country") or item.get("name") or item.get("code")
                if token:
                    out.append(str(token))
            elif item not in (None, ""):
                out.append(str(item))
        return out
    raw = str(value).strip()
    if not raw:
        return []
    return [p.strip() for p in re.split(r"\s*,\s*", raw) if p.strip()]


def _countries_iso(value: Any) -> list[str]:
    """Normalize country names / ISO tokens → unique ISO-3166 alpha-2 list."""
    out: list[str] = []
    seen: set[str] = set()
    for token in _split_country_tokens(value):
        code = country_code_from_name(token)
        if not code or code in seen:
            continue
        seen.add(code)
        out.append(code)
    return out


def _is_ad_text_template(*parts: Any) -> bool:
    """True when Google Ads DKI / customizer macros appear in creative copy."""
    for part in parts:
        text = safe_str(part)
        if text and _DKI_RE.search(text):
            return True
    return False


def _linkedin_company_id(value: Any) -> str | None:
    raw = safe_str(value)
    if not raw:
        return None
    if raw.isdigit():
        return raw
    m = re.search(r"/company/(\d+)", raw)
    return m.group(1) if m else None


def _linkedin_date_iso(value: Any) -> str | None:
    """Normalize LinkedIn dates to ISO-8601 UTC (SC parity)."""
    raw = safe_str(value)
    if not raw:
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}T", raw):
        return raw
    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        return f"{raw}T00:00:00.000Z"
    return raw


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
                    # Synthesize a stable page URL when Meta only gave pageId.
                    (
                        f"https://www.facebook.com/{item.get('pageId')}"
                        if platform == "facebook_ad_library"
                        and (item.get("pageId") or item.get("pageID"))
                        else None
                    ),
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
        countries = _countries_iso(
            item.get("countries")
            or item.get("country")
            or [row.get("country") for row in impressions_by_country]
            or (
                (targeting or {}).get("location")
                if isinstance(targeting, dict)
                else None
            )
        )
        # Prefer a single ISO for `country` (search filter echo / primary market).
        country_iso = countries[0] if len(countries) == 1 else None
        if not country_iso and isinstance(country_value, str) and len(country_value) == 2:
            country_iso = country_value.upper()
        normalized.update(
            {
                "description": description,
                "destinationUrl": destination,
                "adDuration": safe_str(item.get("adDuration") or item.get("dateRange")),
                "startDate": _linkedin_date_iso(
                    item.get("startDate") or normalized.get("firstShown")
                ),
                "endDate": _linkedin_date_iso(
                    item.get("endDate") or normalized.get("lastShown")
                ),
                "firstShown": _linkedin_date_iso(
                    normalized.get("firstShown")
                    or item.get("startDate")
                    or item.get("firstShown")
                ),
                "lastShown": _linkedin_date_iso(
                    normalized.get("lastShown")
                    or item.get("endDate")
                    or item.get("lastShown")
                ),
                "totalImpressions": safe_str(
                    item.get("totalImpressions") or normalized.get("impressions")
                ),
                "impressionsByCountry": impressions_by_country,
                "targeting": targeting,
                "carouselImages": carousel,
                "paidForBy": safe_str(item.get("paidForBy") or item.get("payer")),
                "countries": countries,
                "country": country_iso or normalized.get("country"),
            }
        )
        if not normalized.get("landingUrl") and destination:
            normalized["landingUrl"] = destination
        # SC DX alias — same as advertiser.url (linkedin.com/company/…).
        if adv_url := safe_str(
            (normalized.get("advertiser") or {}).get("url")
            if isinstance(normalized.get("advertiser"), dict)
            else None
        ):
            normalized["advertiserLinkedinPage"] = adv_url
        else:
            normalized["advertiserLinkedinPage"] = None
    adv = normalized["advertiser"]
    if platform == "linkedin_ad_library":
        # advertiser.id is often only embedded in /company/{id} — surface it.
        if not adv.get("id"):
            adv["id"] = _linkedin_company_id(adv.get("url") or item.get("advertiserUrl"))
        elif not str(adv.get("id")).isdigit():
            extracted = _linkedin_company_id(adv.get("id")) or _linkedin_company_id(
                adv.get("url")
            )
            if extracted:
                adv["id"] = extracted
        # Never echo creative headline as the company name (thin SERP stubs).
        adv_name = safe_str(adv.get("name"))
        headline = safe_str(normalized.get("headline") or normalized.get("text"))
        if adv_name and headline and adv_name.lower() == headline.lower():
            adv["name"] = None
        if not normalized.get("advertiserLinkedinPage") and adv.get("url"):
            normalized["advertiserLinkedinPage"] = adv.get("url")
    if platform == "tiktok_ad_library":
        # Stable schema (FB parity): keep null keys — never omit text/cta/….
        for key in ("headline", "cta", "landingUrl", "spend", "text"):
            if normalized.get(key) in ("", [], {}):
                normalized[key] = None
            elif key not in normalized:
                normalized[key] = None
        for key in ("id", "url", "logo"):
            if adv.get(key) in ("", []):
                adv[key] = None
            elif key not in adv:
                adv[key] = None
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
        platforms = (
            item.get("publisherPlatforms")
            or item.get("publisher_platforms")
            or item.get("publisher_platform")
            or item.get("publisherPlatform")
            or []
        )
        if isinstance(platforms, str):
            platforms = [platforms]
        platforms_list = [str(p).upper() for p in platforms if p]
        categories = snapshot.get("pageCategories") or []
        if not isinstance(categories, list):
            categories = [categories] if categories else []
        political = item.get("politicalCountries") or []
        if not isinstance(political, list):
            political = [political] if political else []
        demo = _fb_demographic_rows(
            item.get("demographicDistribution") or item.get("demographic_distribution")
        )
        region = _fb_region_rows(
            item.get("regionDistribution")
            or item.get("region_distribution")
            or item.get("deliveryByRegion")
            or item.get("delivery_by_region")
        )
        age_break = (
            item.get("ageCountryGenderReachBreakdown")
            or item.get("age_country_gender_reach_breakdown")
        )
        if age_break in ("", [], {}):
            age_break = None
        variant_count = safe_int(
            item.get("collationCount")
            or item.get("collation_count")
            or item.get("variantCount")
        )
        collation_id = safe_str(item.get("collationId") or item.get("collation_id"))
        aaa = item.get("isAaaEligible")
        if aaa is None:
            aaa = item.get("is_aaa_eligible")
        target_ages = item.get("targetAges") or item.get("target_ages")
        if isinstance(target_ages, str):
            target_ages = [target_ages]
        elif not isinstance(target_ages, list):
            target_ages = None
        target_gender = safe_str(item.get("targetGender") or item.get("target_gender"))
        target_locations = item.get("targetLocations") or item.get("target_locations")
        if target_locations in ("", [], {}):
            target_locations = None
        eu_reach = safe_int(item.get("euTotalReach") or item.get("eu_total_reach"))
        detail_fetch = bool(item.get("_detailFetch"))
        eu_transparency = None
        if any(
            v is not None
            for v in (age_break, target_ages, target_gender, target_locations, eu_reach)
        ):
            eu_transparency = {
                "euTotalReach": eu_reach,
                "targetAges": target_ages,
                "targetGender": target_gender,
                "targetLocations": target_locations,
                "ageCountryGenderReachBreakdown": age_break,
            }
        cta_type = safe_str(
            snapshot.get("ctaType")
            or item.get("ctaType")
            or item.get("cta_type")
            or _dig(item, "snapshot", "cta_type")
        )
        normalized.update(
            {
                "isActive": item.get("isActive"),
                "publisherPlatforms": platforms_list,
                "platforms": platforms_list,
                "ctaType": cta_type,
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
        # Delivery extras: always on ad-details (null when Meta withholds); on search only when present.
        if detail_fetch or demo is not None:
            normalized["demographicDistribution"] = demo
        if detail_fetch or region is not None:
            normalized["regionDistribution"] = region
        if detail_fetch or age_break is not None:
            normalized["ageCountryGenderReachBreakdown"] = age_break
        if detail_fetch or variant_count is not None:
            normalized["variantCount"] = variant_count
        if detail_fetch or collation_id:
            normalized["collationId"] = collation_id
        if detail_fetch or aaa is not None:
            normalized["isAaaEligible"] = aaa
        if detail_fetch or eu_transparency is not None:
            normalized["euTransparency"] = eu_transparency
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
    if platform == "google_ad_library":
        countries = _countries_iso(
            item.get("countries")
            or item.get("targetCountries")
            or item.get("targetedOrReachedCountries")
            or item.get("regions")
            or country_value
        )
        # `country` stays a single ISO when unambiguous; multi-region → null + countries[].
        if len(countries) == 1:
            normalized["country"] = countries[0]
        elif len(countries) > 1:
            normalized["country"] = None
        elif isinstance(country_value, str) and len(country_value.strip()) == 2:
            normalized["country"] = country_value.strip().upper()
            countries = [normalized["country"]]
        else:
            normalized["country"] = None
        normalized["countries"] = countries
        normalized["textIsTemplate"] = _is_ad_text_template(
            normalized.get("text"), normalized.get("headline")
        )
        # Stable schema (FB parity): keep null keys — never omit text/cta/….
        for key in ("text", "headline", "cta", "landingUrl", "spend", "impressions", "country"):
            if normalized.get(key) in ("", [], {}):
                normalized[key] = None
            elif key not in normalized:
                normalized[key] = None
        for key in ("id", "name", "url", "logo", "location"):
            if adv.get(key) in ("", []):
                adv[key] = None
            elif key not in adv:
                adv[key] = None
    # LinkedIn: keep stable nulls (search parity) — never drop logo/country/id.
    if platform == "linkedin_ad_library":
        for key in ("headline", "cta", "landingUrl", "spend", "impressions", "country", "text"):
            if normalized.get(key) in ("", [], {}):
                normalized[key] = None
            elif key not in normalized:
                normalized[key] = None
        for key in ("id", "name", "url", "logo", "location"):
            if adv.get(key) in ("", []):
                adv[key] = None
            elif key not in adv:
                adv[key] = None
        if "countries" not in normalized:
            normalized["countries"] = []
    elif platform == "facebook_ad_library":
        page_id = safe_str(
            item.get("pageId") or item.get("pageID") or adv.get("id")
        )
        profile_id = _fb_profile_id_from_url(adv.get("url"))
        if profile_id and page_id and profile_id == page_id:
            profile_id = None
        if page_id:
            adv["pageId"] = page_id
            adv["advertiserId"] = page_id
            # Keep id = page_id (company-ads / view_all_page_id).
            adv["id"] = page_id
        if profile_id:
            adv["profileId"] = profile_id
        elif "profileId" not in adv:
            adv["profileId"] = None
        for key in ("id", "name", "url", "logo", "location"):
            if adv.get(key) in ("", []):
                adv.pop(key, None)
    return normalized


def _google_resolved_advertiser(
    native: dict[str, Any],
    ads: list[dict[str, Any]],
    advertiser_input: str,
) -> dict[str, Any] | None:
    """Surface the AR entity company-ads actually queried (chain with advertiser-search)."""
    aid = safe_str(native.get("resolvedId"))
    name = safe_str(native.get("resolvedName"))
    if not aid and ads:
        adv0 = ads[0].get("advertiser") if isinstance(ads[0].get("advertiser"), dict) else {}
        aid = safe_str(adv0.get("id"))
        name = name or safe_str(adv0.get("name"))
    if not aid and re.fullmatch(r"AR\d+", (advertiser_input or "").strip(), flags=re.I):
        aid = advertiser_input.strip().upper()
    if not aid and not name:
        return None
    return {
        "id": aid,
        "name": name,
        "url": f"https://adstransparency.google.com/advertiser/{aid}" if aid else None,
    }


async def _run_actor(actor: str, payload: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    try:
        items = await get_apify().run_actor_sync(actor, payload, max_items=limit)
    except ApifyError as exc:
        raise HTTPException(status_code=502, detail=f"Ad Library upstream error: {exc}") from exc
    return items[:limit]


async def _run_actor_fast(
    actor: str, payload: dict[str, Any], limit: int, *, timeout: float
) -> list[dict[str, Any]]:
    """Apify sync — wait for the real dataset (timeout under CF 125s default)."""
    client = ApifyClient(timeout=timeout, max_attempts=1)
    try:
        items = await client.run_actor_sync(actor, payload, max_items=limit)
    except ApifyError as exc:
        msg = str(exc).lower()
        if "timeout" in msg:
            raise _tiktok_ad_timeout_http(timeout) from exc
        raise HTTPException(status_code=502, detail=f"Ad Library upstream error: {exc}") from exc
    return items[:limit]


def _tiktok_ad_timeout_http(wait_secs: float) -> HTTPException:
    """503 when the upstream genuinely exceeds the sync budget — not billed."""
    return HTTPException(
        status_code=503,
        detail={
            "error": {
                "code": "upstream_timeout",
                "retryAfterSeconds": _TIKTOK_AD_RETRY_AFTER_SECS,
            },
            "message": (
                f"TikTok Ad Library upstream timed out after {wait_secs:g}s. "
                "Retry shortly — empty/timeout responses are not billed. "
                "Set your HTTP client timeout to at least 120s; nginx/ALB "
                "defaults (60s) and Heroku (30s) often cut the connection earlier."
            ),
        },
        headers={"Retry-After": str(_TIKTOK_AD_RETRY_AFTER_SECS)},
    )


def _match_meta(filt: dict[str, Any]) -> dict[str, Any]:
    return {
        "matchedFrom": int(filt.get("matchedFrom") or 0),
        "filteredOut": int(filt.get("filteredOut") or 0),
        "literalMatches": int(filt.get("literalMatches") or 0),
        "match": filt.get("match") or "any",
        "matchBasis": filt.get("matchBasis") or "any",
    }


def _bill_ads(ctx: dict[str, Any], ads: list[Any], *, flat: int, apify_rate: float | None = None) -> None:
    """Empty 200s are free; otherwise flat native or scaled Apify."""
    n = len(ads)
    if n == 0:
        ctx["credits_override"] = 0
        return
    if ctx.get("source") == "direct" or apify_rate is None:
        ctx["credits_override"] = flat
        return
    ctx["credits_override"] = _scaled(n, apify_rate, CREDIT_TIKTOK_TOP_ADS_MIN)


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
    platforms: str | None = Query(
        None,
        description=(
            "Comma-separated publisher platforms to keep: FACEBOOK, INSTAGRAM, "
            "MESSENGER, AUDIENCE_NETWORK, THREADS. Filters the returned page "
            "(Meta's HTML search does not always honor this server-side)."
        ),
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
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor from a previous nextCursor. Pages through the "
            "current Meta HTML result batch (same filters). When nextCursor is "
            "null, refine with start_date/status or a narrower query."
        ),
    ),
    trim: bool = Query(
        False,
        description=(
            "SC-compatible. Captapi payloads are already lean vs Meta nested "
            "snapshots; when true, omit cards/images/videos typed arrays (media[] stays)."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    active_status = status.lower()
    media = media_type.lower()
    platform_filter = [
        p.strip().upper() for p in (platforms or "").split(",") if p.strip()
    ] or None

    def _maybe_trim(ads: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not trim:
            return ads
        out: list[dict[str, Any]] = []
        for ad in ads:
            row = dict(ad)
            for key in ("cards", "images", "videos"):
                row.pop(key, None)
            out.append(row)
        return out

    # Pull a full HTML batch so cursor can page within it (Meta UI ~30–50 ads).
    fetch_limit = 200
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
                limit=fetch_limit,
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
                ads = _filter_ads_by_platforms(ads, platform_filter)
                _unify_advertisers_by_id(ads)
                page, next_cursor, more_in_page = _paginate_ads(
                    ads, limit=limit, cursor=cursor
                )
                page = _maybe_trim(page)
                ctx["credits_override"] = CREDIT_AD_LIBRARY_NATIVE
                count = native.get("searchResultsCount")
                return {
                    "query": q,
                    "country": country.upper(),
                    "status": status,
                    "limit": limit,
                    "totalReturned": len(page),
                    "searchResultsCount": count,
                    "hasMore": bool(more_in_page or (count and isinstance(count, int) and count > len(page))),
                    "nextCursor": next_cursor,
                    "ads": page,
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
                {"startUrls": [{"url": library_url}], "resultsLimit": fetch_limit, "isDetailsPerAd": False},
                fetch_limit,
            )
            ctx["source"] = "apify"
            ads = [_normalize_ad(i, "facebook_ad_library") for i in items]
            ads = _filter_ads_by_platforms(ads, platform_filter)
            _unify_advertisers_by_id(ads)
            page, next_cursor, more_in_page = _paginate_ads(
                ads, limit=limit, cursor=cursor
            )
            page = _maybe_trim(page)
            return {
                "query": q,
                "country": country.upper(),
                "status": status,
                "limit": limit,
                "totalReturned": len(page),
                "searchResultsCount": None,
                "hasMore": more_in_page,
                "nextCursor": next_cursor,
                "ads": page,
            }

        data = await cached_or_run(
            "ad-library.facebook.search",
            {
                "q": q,
                "country": country,
                "limit": limit,
                "status": status,
                "media_type": media_type,
                "platforms": ",".join(platform_filter or []),
                "ad_type": ad_type,
                "search_type": search_type,
                "sort_by": sort_by or "",
                "start_date": start_date or "",
                "end_date": end_date or "",
                "cursor": cursor or "",
                "trim": trim,
                "v": 9,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
            ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get(
    "/facebook/company-ads",
    summary="Meta/Facebook ads for a page or advertiser",
    description=(
        "List ads for one Meta page/advertiser. Prefer pageId (or libraryUrl) from "
        "/facebook/search-companies — that id is view_all_page_id. A facebook.com/"
        "{digits}/ profileId in the page URL is a different namespace and may 404 or "
        "miss ads if used alone; vanity URLs (facebook.com/nike/) work when Meta resolves them."
    ),
)
async def facebook_company_ads(
    url: str = Query(
        ...,
        description=(
            "Page id from search-companies (pageId), libraryUrl, Facebook page URL, "
            "or Ad Library URL with view_all_page_id."
        ),
    ),
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
                _unify_advertisers_by_id(ads)
                ctx["credits_override"] = CREDIT_AD_LIBRARY_NATIVE
                return {"url": url, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

            items = await _run_actor(
                settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                {"startUrls": [{"url": url}], "resultsLimit": limit, "isDetailsPerAd": True},
                limit,
            )
            ctx["source"] = "apify"
            ads = [_normalize_ad(i, "facebook_ad_library") for i in items]
            _unify_advertisers_by_id(ads)
            return {"url": url, "country": country.upper(), "totalReturned": len(ads), "ads": ads}

        data = await cached_or_run("ad-library.facebook.company-ads", {"url": url, "country": country, "limit": limit, "v": 6}, _run, ctx, use_cache=cache)
        if ctx.get("source") != "direct":
            ctx["credits_override"] = _scaled(len(data["ads"]))
        return ApiResponse(data=data)


@router.get(
    "/facebook/search-companies",
    summary="Find advertisers/pages in Meta Ad Library",
    description=(
        "Find Meta Ad Library advertisers/pages by brand name. Results are "
        "relevance-filtered so the query must appear in the page name (empty beats "
        "off-brand pages that merely ran ads near the keyword). Each company exposes "
        "pageId / advertiserId (same value — pass to /facebook/company-ads as url=) "
        "and profileId when the facebook.com/{digits}/ URL uses a different numeric "
        "identity. libraryUrl is the ready view_all_page_id link. Flat 2 credits native."
    ),
)
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
        base_credits=CREDIT_AD_LIBRARY_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Wider ad window so ranking has enough distinct pages to choose from.
            native = await facebook_ads_native.search_companies(
                q, country=country, limit=max(limit * 5, 40)
            )
            items = native
            if native is not None:
                ctx["source"] = "direct"
                ctx["credits_override"] = CREDIT_AD_LIBRARY_NATIVE
            else:
                items = await _run_actor(
                    settings.APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2,
                    {
                        "startUrls": [{"url": _facebook_search_url(q, country)}],
                        "resultsLimit": max(limit * 5, 40),
                        "isDetailsPerAd": False,
                    },
                    max(limit * 5, 40),
                )
                ctx["source"] = "apify"

            advertisers: dict[str, dict[str, Any]] = {}
            for item in items or []:
                ad = _normalize_ad(item, "facebook_ad_library")
                adv = ad.get("advertiser") if isinstance(ad.get("advertiser"), dict) else {}
                key = adv.get("id") or adv.get("name")
                if not key or key in advertisers:
                    continue
                advertisers[key] = _fb_company_from_advertiser(
                    adv, country=country.upper()
                )
            companies = _rank_fb_companies(list(advertisers.values()), q)[:limit]
            return {
                "query": q,
                "country": country.upper(),
                "totalReturned": len(companies),
                "companies": companies,
            }

        data = await cached_or_run(
            "ad-library.facebook.search-companies",
            {"q": q, "country": country, "limit": limit, "v": 5},
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
            ctx["credits_override"] = CREDIT_AD_LIBRARY_NATIVE
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
    row = dict(items[0])
    row["_detailFetch"] = True
    return _normalize_ad(row, "facebook_ad_library")


@router.get(
    "/facebook/ad-details",
    summary="Meta/Facebook ad details",
    description=(
        "Fetch one Meta Ad Library ad by URL or archive ID. Creative fields "
        "(text/headline/cta/landingUrl/media/advertiser) match a search hit for the "
        "same id — use this endpoint for ID lookup without paging search. "
        "Delivery extras are returned when Meta publishes them (mostly political/"
        "issue and EU AAA ads): platforms / publisherPlatforms, "
        "demographicDistribution[], regionDistribution[], "
        "ageCountryGenderReachBreakdown / euTransparency, variantCount "
        "(collation), isAaaEligible. On commercial ads Meta often withholds those "
        "breakdowns — keys stay present as null so the schema is stable. Flat 2 "
        "credits on the native path."
    ),
)
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
                {"url": ad_url, "v": 6},
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
        "as clean JSON. Flat 2 credits on the native path when results are returned "
        f"(Apify fallback capped at {CREDIT_TIKTOK_AD_SEARCH_APIFY}); empty results "
        "are never charged. Local keyword matching is case-insensitive substring "
        "with match=any|all (default any). When the filter reduces the set, "
        "matchedFrom / filteredOut explain how many SERP rows existed before "
        "filtering. Upstream work is capped (~40s Decodo / ~20s Apify) so clients "
        "are not billed after ALB disconnect. Default country GB. For Creative "
        "Center Top Ads use /v1/ad-library/tiktok/top-ads."
    ),
)
async def tiktok_search(
    q: str = Query(..., min_length=2, description="Keyword or advertiser name (min 2 characters)."),
    country: str = Query(
        "GB",
        min_length=2,
        max_length=2,
        description="Two-letter ISO country code (e.g. GB, DE, FR). Default GB — EU Commercial Content Library; US often empty.",
    ),
    match: str = Query(
        "any",
        description='Keyword token mode: "any" (default, OR) or "all" (AND). Substring, case-insensitive.',
    ),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    region = _tiktok_region(country)
    try:
        match_mode = tiktok_ads_native.normalize_match_mode(match)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # Over-fetch then relevance-filter so limit is filled with on-topic ads.
    fetch_limit = min(200, max(limit * 3, limit))
    async with billed_call(
        caller=caller,
        endpoint="/v1/ad-library/tiktok/search",
        platform="tiktok_ad_library",
        resource_url=None,
        base_credits=CREDIT_TIKTOK_AD_SEARCH,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Decodo-native Commercial Content Library first (flat 2 credits).
            native = await tiktok_ads_native.search_ads(
                q, country=region, limit=fetch_limit
            )
            if native is not None:
                ctx["source"] = "direct"
                filt = tiktok_ads_native.filter_ads_by_query(
                    native, q, match=match_mode
                )
                ads = [
                    _normalize_ad(i, "tiktok_ad_library")
                    for i in filt["rows"][:limit]
                ]
                return {
                    "query": q,
                    "country": region,
                    "totalReturned": len(ads),
                    **_match_meta(filt),
                    "ads": ads,
                }

            items = await _run_actor_fast(
                settings.APIFY_ACTOR_TIKTOK_AD_LIBRARY,
                {
                    "source": "both",
                    "searchTerms": [q],
                    "countries": [region],
                    "maxResults": fetch_limit,
                },
                fetch_limit,
                timeout=_TIKTOK_AD_APIFY_TIMEOUT_SECS,
            )
            ctx["source"] = "apify"
            filt = tiktok_ads_native.filter_ads_by_query(items, q, match=match_mode)
            ads = [
                _normalize_ad(i, "tiktok_ad_library") for i in filt["rows"][:limit]
            ]
            return {
                "query": q,
                "country": region,
                "totalReturned": len(ads),
                **_match_meta(filt),
                "ads": ads,
            }

        data = await cached_or_run(
            "ad-library.tiktok.search",
            {"q": q, "country": region, "limit": limit, "match": match_mode, "v": 8},
            _run,
            ctx,
            use_cache=cache,
        )
        ads = data.get("ads") or []
        if not ads:
            ctx["credits_override"] = 0
        elif ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_TIKTOK_AD_SEARCH
        else:
            ctx["credits_override"] = CREDIT_TIKTOK_AD_SEARCH_APIFY
        return ApiResponse(data=data)


@router.get(
    "/tiktok/top-ads",
    summary="TikTok Creative Center Top Ads",
    description=(
        "High-performing TikTok ads from Creative Center Top Ads "
        "(ads.tiktok.com/business/creativecenter) as clean JSON — title, brandName, "
        "advertiser{id,name}, firstSeen/lastSeen (null when CC list omits run dates — "
        "check datesPresent; DSA windows: /tiktok/search), likes (+likesIsApproximate), "
        "ctr/ctrTier, costTier, resolved industry/objective, isSparkAd, and video{} "
        "(urlHd only when a distinct HD rendition exists; no duplicate media[]). "
        "Keyword q is whole-word match=any|all on title/brand/tags/industry — "
        "matchedFrom/filteredOut/literalMatches/matchBasis explain the filter. "
        "No soft Creative Center fallback: zero literal hits → empty ads (free). "
        "This endpoint opens TikTok Creative Center in a browser and intercepts "
        "the signed list XHR (HTML has no ad data). Typically 30–60 seconds — set "
        "your HTTP client timeout to at least 120s (nginx/ALB default 60s and "
        "Heroku 30s will cut the connection). Flat 2 credits on the browser path; "
        "Apify fallback ~1 credit per returned ad (min 2)."
    ),
)
async def tiktok_top_ads(
    q: str | None = Query(
        None,
        description=(
            "Optional keyword. Case-insensitive whole-word match on title, brand, "
            "tags, industry, objective (hair ≠ wheelchair). See match=any|all. "
            "When no row matches, ads[] is empty and matchedFrom shows how many "
            "leaderboard rows were considered — never the unfiltered list."
        ),
    ),
    match: str = Query(
        "any",
        description='Keyword token mode: "any" (default, OR) or "all" (AND).',
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
        description=(
            "Optional industry: Apify/Creative Center labels "
            "(Gaming, Beauty & Personal Care, …) or TikTok keys "
            "(label_25000000000). Invalid values return 400 — not a 502."
        ),
    ),
    objective: str | None = Query(
        None,
        description=(
            "Optional campaign objective: Traffic, App Install, Conversions, "
            "Reach, Video Views, Lead Generation, Engagement (aliases: Conversion)."
        ),
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
        match_mode = tiktok_creative_center.normalize_match_mode(match)
        # Validate/map before Apify fallback — actor enum mismatch used to
        # surface as upstream_actor_error 502 instead of a clear 400.
        tiktok_creative_center.normalize_apify_industry(industry)
        tiktok_creative_center.normalize_apify_objective(objective)
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

        async def _payload(filt: dict[str, Any], *, want: int) -> dict[str, Any]:
            ads = [
                tiktok_creative_center.normalize_top_ad(i, query_country=region)
                for i in filt.get("rows") or []
                if isinstance(i, dict) and (i.get("ad_id") or i.get("id"))
            ][:want]
            dates_present = sum(
                1 for a in ads if a.get("firstSeen") or a.get("lastSeen")
            )
            out: dict[str, Any] = {
                "query": (q or "").strip() or None,
                "country": region,
                "period": period_days,
                "orderBy": order_key,
                "totalReturned": len(ads),
                # Creative Center Top Ads rarely publishes run dates — clients
                # can see how often firstSeen/lastSeen are filled vs null.
                "datesPresent": dates_present,
                **_match_meta(filt),
                "ads": ads,
            }
            # Early-exit collected < limit while Creative Center still has pages.
            if filt.get("truncated"):
                out["truncated"] = True
            return out

        async def _run() -> dict[str, Any]:
            want = max(1, min(int(limit), 100))
            overfetch = tiktok_creative_center.fetch_limit_for_query(want, q)
            # Browser early-exit on signed top_ads/v2/list (not HTML / networkidle).
            # Pass the caller's limit (not Apify overfetch) so truncated is honest.
            native = await tiktok_creative_center.search_top_ads(
                country=region,
                period=period_days,
                order_by=order_label,
                limit=want,
                q=q,
                match=match_mode,
                industry=industry,
                objective=objective,
                ad_format=ad_format,
            )
            # Browser capture succeeded — trust it even when keyword filter
            # returns zero rows (honest empty). Apify only when capture failed.
            if native is not None:
                ctx["source"] = "direct"
                return await _payload(native, want=want)

            payload = tiktok_creative_center.apify_input(
                country=region,
                period=period_days,
                order_by=order_label,
                limit=overfetch,
                q=q,
                industry=industry,
                objective=objective,
                ad_format=ad_format,
            )
            items = await _run_actor_fast(
                settings.APIFY_ACTOR_TIKTOK_CREATIVE_CENTER,
                payload,
                overfetch,
                timeout=_TIKTOK_AD_APIFY_TIMEOUT_SECS,
            )
            ctx["source"] = "apify"
            filt = tiktok_creative_center.filter_top_ads(
                [i for i in items if isinstance(i, dict)],
                q=q,
                match=match_mode,
                industry=industry,
                objective=objective,
                ad_format=ad_format,
            )
            return await _payload(filt, want=want)

        data = await cached_or_run(
            "ad-library.tiktok.top-ads",
            {
                "q": q or "",
                "match": match_mode,
                "country": region,
                "period": period_days,
                "orderBy": order_label,
                "industry": industry or "",
                "objective": objective or "",
                "adFormat": ad_format or "",
                "limit": limit,
                "v": 7,
            },
            _run,
            ctx,
            stale_while_revalidate=True,
            use_cache=cache,
        )
        # Flat 2 browser path; Apify ~1/returned ad (min 2). Empty/timeout free.
        _bill_ads(
            ctx,
            data.get("ads") or [],
            flat=CREDIT_TIKTOK_TOP_ADS,
            apify_rate=RATE_TIKTOK_TOP_ADS if ctx.get("source") != "direct" else None,
        )
        return ApiResponse(data=data)


@router.get(
    "/tiktok/ad-details",
    summary="TikTok ad details",
    description=(
        "Fetch one TikTok Commercial Content Library ad by URL or ad ID. Same "
        "schema as search hits (text/cta/landingUrl/impressions/advertiser.* with "
        "nulls when DSA withholds). Useful for ID lookup without a search page. "
        f"Flat {CREDIT_AD_LIBRARY_NATIVE} credits on the native path; Apify fallback "
        f"capped at {CREDIT_TIKTOK_AD_SEARCH_APIFY} (not 17). Default country GB."
    ),
)
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
            ctx["credits_override"] = CREDIT_TIKTOK_AD_SEARCH_APIFY
            return _normalize_ad(best, "tiktok_ad_library")

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.tiktok.ad-details",
                {"ad_id": ad_id, "country": region, "v": 6},
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
        description=(
            "Advertiser name, domain (e.g. nike.com), or Google advertiser ID (AR…). "
            "Prefer AR… from /google/advertiser-search for a deterministic entity."
        ),
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
    sort: Literal["last_shown", "first_shown"] | None = Query(
        None,
        description=(
            "Client-side sort before slicing: last_shown (recent activity first) or "
            "first_shown. Default is ATC order (often oldest creatives first)."
        ),
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
                if sort == "last_shown":
                    ads.sort(key=lambda a: a.get("lastShown") or "", reverse=True)
                elif sort == "first_shown":
                    ads.sort(key=lambda a: a.get("firstShown") or "", reverse=True)
                resolved = _google_resolved_advertiser(native, ads, advertiser)
                ctx["credits_override"] = CREDIT_GOOGLE_COMPANY_ADS
                return {
                    "advertiser": advertiser,
                    "resolvedAdvertiser": resolved,
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
            if sort == "last_shown":
                ads.sort(key=lambda a: a.get("lastShown") or "", reverse=True)
            elif sort == "first_shown":
                ads.sort(key=lambda a: a.get("firstShown") or "", reverse=True)
            return {
                "advertiser": advertiser,
                "resolvedAdvertiser": _google_resolved_advertiser({}, ads, advertiser),
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
                "sort": sort or "",
                "v": 8,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
            ctx["credits_override"] = _scaled(len(data["ads"]), RATE_GOOGLE_COMPANY_ADS)
        return ApiResponse(data=data)


def _google_detail_identity(
    row: dict[str, Any], *, advertiser_id: str, creative: str
) -> dict[str, Any] | None:
    """Normalize + enforce AR/CR identity (never return a different creative)."""
    out = _normalize_ad(row, "google_ad_library")
    got_cr = safe_str(out.get("id")) or ""
    got_ar = safe_str((out.get("advertiser") or {}).get("id")) or ""
    if got_cr.upper() != creative.upper():
        return None
    # Stamp request identity so chain never drifts even if a scraper mislabels AR.
    out["id"] = creative
    out["url"] = (
        f"https://adstransparency.google.com/advertiser/{advertiser_id}/creative/{creative}"
    )
    adv = out.setdefault("advertiser", {})
    if not isinstance(adv, dict):
        adv = {}
        out["advertiser"] = adv
    if got_ar and got_ar.upper() != advertiser_id.upper():
        # Wrong legal entity for this CR — reject (do not silently swap Nike entities).
        return None
    adv["id"] = advertiser_id
    adv["url"] = f"https://adstransparency.google.com/advertiser/{advertiser_id}"
    return out


@router.get(
    "/google/ad-details",
    summary="Google ad details",
    description=(
        "Fetch one Google Ads Transparency creative by AR… + CR… URL. Adds text/"
        "headline/landingUrl/impressions when ATC publishes them (beyond company-ads "
        "list rows). Response id + advertiser.id always match the request — different "
        "Nike legal entities (Inc. vs Retail BV vs SRL) are not interchangeable. "
        "countries[] is ISO-3166 alpha-2; country is a single ISO when unambiguous. "
        "textIsTemplate marks Google Ads Dynamic Keyword Insertion macros "
        "({KeyWord:…}). Flat 2 credits native; Apify fallback capped at "
        f"{CREDIT_AD_DETAILS_APIFY}."
    ),
)
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
                out = _google_detail_identity(
                    native, advertiser_id=advertiser_id, creative=creative
                )
                if out:
                    ctx["source"] = "direct"
                    return out

            items = await _run_actor(
                settings.APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2,
                {"advertisers": [advertiser_id], "region": country.upper(), "maxResults": 50},
                50,
            )
            want = creative.upper()
            for item in items:
                cand = str(
                    item.get("creativeId") or item.get("adCreativeId") or item.get("id") or ""
                ).upper()
                if cand != want:
                    continue
                out = _google_detail_identity(
                    item, advertiser_id=advertiser_id, creative=creative
                )
                if out:
                    ctx["source"] = "apify"
                    ctx["credits_override"] = CREDIT_AD_DETAILS_APIFY
                    return out
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Creative {creative} not found under advertiser {advertiser_id}. "
                    "Pass the AR… from /google/advertiser-search or company-ads "
                    "resolvedAdvertiser.id — Nike Inc / Retail BV / SRL are different entities."
                ),
            )

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.google.ad-details",
                {"creative_id": f"{advertiser_id}/{creative}", "country": country, "v": 7},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get(
    "/google/advertiser-search",
    summary="Search Google Ads advertisers",
    description=(
        "Search Google Ads Transparency advertisers and return ranked AR… entities. "
        "Brand queries are expanded (e.g. nike → Nike, Inc. + NIKE SRL) so country=US "
        "surfaces the parent company first. Pass advertisers[].id into "
        "/v1/ad-library/google/company-ads?advertiser=AR… for a deterministic creatives chain. "
        "Flat 1 credit."
    ),
)
async def google_advertiser_search(
    q: str = Query(..., min_length=2, description="Brand, domain, or advertiser name (min 2 characters)."),
    country: str = Query(
        "US",
        min_length=2,
        max_length=2,
        description="Two-letter ISO country code used to rank entities (e.g. US prefers Inc. over SRL).",
    ),
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
                {"q": q, "country": country, "limit": limit, "v": 6},
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
    company: str | None = Query(
        None,
        description="SC alias of q — advertiser / account owner name.",
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
    pagination_token: str | None = Query(
        None,
        alias="paginationToken",
        description="SC alias of cursor — pagination token from a previous response.",
    ),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    owner = (q or company or "").strip()
    kw = (keyword or "").strip()
    cid = (company_id or "").strip()
    page_cursor = (cursor or pagination_token or "").strip() or None
    if len(owner) < 2 and len(kw) < 2 and not cid:
        raise HTTPException(
            status_code=400,
            detail="Provide q/company (advertiser), keyword, or companyId.",
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
                pagination_token=page_cursor,
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


@router.get(
    "/linkedin/ad-details",
    summary="LinkedIn ad details",
    description=(
        "Fetch one LinkedIn Ad Library ad by URL or ID. Adds headline, destination/"
        "landingUrl, targeting{}, impressionsByCountry[], and advertiser.url when the "
        "detail page publishes them. advertiser.id is extracted from "
        "/company/{id} for joins with LinkedIn Company endpoints. Schema keeps "
        "null keys for fields search may have (country, logo) so details is never "
        "thinner by omission. Flat 2 credits native; Apify fallback capped at "
        f"{CREDIT_AD_DETAILS_APIFY}."
    ),
)
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
            ctx["credits_override"] = CREDIT_AD_DETAILS_APIFY
            return _normalize_ad(items[0], "linkedin_ad_library")

        return ApiResponse(
            data=await cached_or_run(
                "ad-library.linkedin.ad-details",
                {"url": ad_url, "v": 7},
                _run,
                ctx,
                use_cache=cache,
            )
        )
