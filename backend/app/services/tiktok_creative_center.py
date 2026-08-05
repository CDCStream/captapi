"""TikTok Creative Center Top Ads.

Public Top Ads live on ``ads.tiktok.com/business/creativecenter`` and are served
by TikTok's signed ``creative_radar_api`` (browser ``user-sign`` bootstrap).
Native path: Decodo headless + XHR capture of ``top_ads/v2/list``.
Apify remains the fallback when Decodo is down or returns nothing.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import structlog

from app.utils.formatters import duration_seconds, safe_float, safe_int, safe_str

log = structlog.get_logger(__name__)

_FILTER_ECHO = frozenset(
    {
        "",
        "all",
        "all industries",
        "all_industries",
        "all formats",
        "all_formats",
        "all format",
        "n/a",
        "unknown",
        "-",
    }
)

TOP_ADS_PAGE = (
    "https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en"
)
LIST_PATH = "creative_radar_api/v1/top_ads/v2/list"

# Captapi / actor order labels -> Creative Center page `order_by` query values.
PAGE_ORDER_BY: dict[str, str] = {
    "For You": "for_you",
    "Likes": "like",
    "CTR": "ctr",
    "Impressions": "impression",
    "Cost": "cost",
}

OBJECTIVE_LABELS: dict[str, str] = {
    "campaign_objective_traffic": "Traffic",
    "campaign_objective_conversion": "Conversion",
    "campaign_objective_app_install": "App Install",
    "campaign_objective_video_view": "Video View",
    "campaign_objective_reach": "Reach",
    "campaign_objective_lead_generation": "Lead Generation",
    "campaign_objective_product_sales": "Product Sales",
    "campaign_objective_engagement": "Engagement",
}

# Actor display labels -> Captapi orderBy query values.
ORDER_BY_ALIASES: dict[str, str] = {
    "for_you": "For You",
    "foryou": "For You",
    "like": "Likes",
    "likes": "Likes",
    "ctr": "CTR",
    "impression": "Impressions",
    "impressions": "Impressions",
    "cost": "Cost",
    # ScrapeCreators-style aliases -> closest Creative Center sort.
    "play_2s_rate": "CTR",
    "play_6s_rate": "CTR",
    "cvr": "CTR",
}

ALLOWED_PERIODS = frozenset({7, 30, 180})

# ``khadinakbar/tiktok-ads-scraper`` input.industry enum (19 values).
# Source: https://apify.com/khadinakbar/tiktok-ads-scraper — Filter Reference.
APIFY_INDUSTRIES: tuple[str, ...] = (
    "All Industries",
    "Gaming",
    "E-commerce & Shopping",
    "Beauty & Personal Care",
    "Food & Beverage",
    "Health & Fitness",
    "Entertainment",
    "Sports & Outdoors",
    "Finance",
    "Education",
    "Travel",
    "Business Services",
    "Fashion & Apparel",
    "Technology",
    "Home & Décor",
    "Parenting & Kids",
    "Media & Entertainment",
    "News & Information",
    "Music",
)

# TikTok Creative Center top-level industry id prefix → nearest Apify enum.
_TIKTOK_PREFIX_TO_APIFY: dict[str, str] = {
    "10": "Education",
    "12": "Parenting & Kids",
    "13": "Finance",
    "14": "Beauty & Personal Care",
    "15": "Technology",
    "16": "Home & Décor",
    "17": "Travel",
    "18": "Home & Décor",
    "20": "Technology",
    "21": "Home & Décor",
    "22": "Fashion & Apparel",
    "23": "Media & Entertainment",
    "24": "Business Services",
    "25": "Gaming",
    "26": "Business Services",
    "27": "Food & Beverage",
    "28": "Sports & Outdoors",
    "29": "Health & Fitness",
    "30": "E-commerce & Shopping",
}

_INDUSTRY_ALIASES: dict[str, str] = {
    "games": "Gaming",
    "game": "Gaming",
    "gaming": "Gaming",
    "casino": "Gaming",
    "hyper casual": "Gaming",
    "e commerce": "E-commerce & Shopping",
    "ecommerce": "E-commerce & Shopping",
    "e commerce shopping": "E-commerce & Shopping",
    "ecommerce shopping": "E-commerce & Shopping",
    "shopping": "E-commerce & Shopping",
    "beauty": "Beauty & Personal Care",
    "beauty personal care": "Beauty & Personal Care",
    "cosmetics": "Beauty & Personal Care",
    "skincare": "Beauty & Personal Care",
    "personal care": "Beauty & Personal Care",
    "food": "Food & Beverage",
    "beverage": "Food & Beverage",
    "food beverage": "Food & Beverage",
    "health": "Health & Fitness",
    "fitness": "Health & Fitness",
    "health fitness": "Health & Fitness",
    "sports": "Sports & Outdoors",
    "outdoors": "Sports & Outdoors",
    "sports outdoors": "Sports & Outdoors",
    "sports outdoor": "Sports & Outdoors",
    "fintech": "Finance",
    "financial services": "Finance",
    "finance": "Finance",
    "tech": "Technology",
    "tech electronics": "Technology",
    "technology": "Technology",
    "electronics": "Technology",
    "apps": "Technology",
    "cell phones": "Technology",
    "fashion": "Fashion & Apparel",
    "apparel": "Fashion & Apparel",
    "apparel accessories": "Fashion & Apparel",
    "fashion apparel": "Fashion & Apparel",
    "home": "Home & Décor",
    "home decor": "Home & Décor",
    "decor": "Home & Décor",
    "household products": "Home & Décor",
    "appliances": "Home & Décor",
    "home improvement": "Home & Décor",
    "parenting": "Parenting & Kids",
    "kids": "Parenting & Kids",
    "baby kids maternity": "Parenting & Kids",
    "parenting kids": "Parenting & Kids",
    "media": "Media & Entertainment",
    "news": "News & Information",
    "news entertainment": "Media & Entertainment",
    "news information": "News & Information",
    "business": "Business Services",
    "business services": "Business Services",
    "life services": "Business Services",
    "travel": "Travel",
    "education": "Education",
    "music": "Music",
    "entertainment": "Entertainment",
}

# Actor objective enum (Filter Reference). Captapi aliases → actor labels.
APIFY_OBJECTIVES: tuple[str, ...] = (
    "All Objectives",
    "Traffic",
    "App Install",
    "Conversions",
    "Reach",
    "Video Views",
    "Lead Generation",
    "Engagement",
)

_OBJECTIVE_ALIASES: dict[str, str] = {
    "traffic": "Traffic",
    "app install": "App Install",
    "app_install": "App Install",
    "appinstall": "App Install",
    "conversion": "Conversions",
    "conversions": "Conversions",
    "reach": "Reach",
    "video view": "Video Views",
    "video views": "Video Views",
    "video_view": "Video Views",
    "video_views": "Video Views",
    "lead generation": "Lead Generation",
    "lead_generation": "Lead Generation",
    "engagement": "Engagement",
    "campaign_objective_traffic": "Traffic",
    "campaign_objective_conversion": "Conversions",
    "campaign_objective_app_install": "App Install",
    "campaign_objective_video_view": "Video Views",
    "campaign_objective_reach": "Reach",
    "campaign_objective_lead_generation": "Lead Generation",
    "campaign_objective_engagement": "Engagement",
}


def _fold_key(value: str) -> str:
    t = (
        value.strip()
        .lower()
        .replace("é", "e")
        .replace("è", "e")
        .replace("&", " ")
    )
    t = re.sub(r"[\s\-_/,]+", " ", t)
    return t.strip()


def normalize_order_by(value: str | None) -> str:
    raw = (value or "for_you").strip().lower().replace("-", "_").replace(" ", "_")
    mapped = ORDER_BY_ALIASES.get(raw)
    if mapped:
        return mapped
    # Allow exact actor labels.
    for label in ("For You", "Likes", "CTR", "Impressions", "Cost"):
        if raw == label.lower().replace(" ", "_"):
            return label
    raise ValueError(
        "orderBy must be one of: for_you, likes, ctr, impressions, cost "
        "(aliases: like, impression, play_2s_rate, play_6s_rate, cvr)"
    )


def normalize_period(value: int | None) -> int:
    period = int(value or 30)
    if period not in ALLOWED_PERIODS:
        raise ValueError("period must be 7, 30, or 180 days")
    return period


def detail_url(ad_id: str) -> str:
    aid = (ad_id or "").strip()
    return f"https://ads.tiktok.com/business/creativecenter/topads/{aid}/pc/en"


@lru_cache(maxsize=1)
def _industry_labels() -> dict[str, str]:
    path = Path(__file__).resolve().parent.parent / "data" / "tiktok_industry_labels.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        log.warning("tiktok_cc_industry_labels_miss", error=str(exc))
        return {}
    return data if isinstance(data, dict) else {}


def resolve_industry_label(key: str | None, raw: str | None = None) -> str | None:
    """Human label for an industry key; never echo filter placeholders."""
    cleaned = (raw or "").strip()
    if cleaned and cleaned.lower() not in _FILTER_ECHO:
        return cleaned
    if not key:
        return None
    labels = _industry_labels()
    k = key.strip()
    bare = k.removeprefix("label_")
    for candidate in (k, bare, f"label_{bare}"):
        hit = labels.get(candidate)
        if isinstance(hit, str) and hit.strip():
            return hit.strip()
    digits = bare
    if digits.isdigit() and len(digits) >= 2:
        # Walk parents: 25100000000 → 25000000000 (Games), etc.
        for cut in (2, 3, 5):
            if cut >= len(digits):
                continue
            parent = digits[:cut] + ("0" * (len(digits) - cut))
            if parent == digits:
                continue
            hit = labels.get(parent) or labels.get(f"label_{parent}")
            if isinstance(hit, str) and hit.strip():
                return hit.strip()
    return None


def resolve_ad_format(raw: str | None, is_spark: bool | None) -> str | None:
    cleaned = (raw or "").strip()
    if cleaned and cleaned.lower() not in _FILTER_ECHO:
        return cleaned
    if is_spark is True:
        return "Spark Ads"
    if is_spark is False:
        return "Non-Spark Ads"
    return None


def query_tokens(q: str | None) -> list[str]:
    return [t for t in re.split(r"\W+", (q or "").lower()) if len(t) >= 2]


def top_ad_matches_query(row: dict[str, Any], q: str | None) -> bool:
    """True when every query token appears in title, brand, tags, or industry.

    Creative Center's ``keyword`` param is soft (often ignored with for_you).
    Prefer empty over unrelated results the customer paid credits for.
    """
    tokens = query_tokens(q)
    if not tokens:
        return True
    industry_key = safe_str(row.get("industry_key") or row.get("industryKey"))
    industry = resolve_industry_label(
        industry_key,
        safe_str(row.get("industry")),
    )
    tags = row.get("tags") if isinstance(row.get("tags"), list) else []
    keywords = row.get("keywords") if isinstance(row.get("keywords"), list) else []
    hay = " ".join(
        str(p)
        for p in (
            row.get("ad_title"),
            row.get("title"),
            row.get("adTitle"),
            row.get("brand_name"),
            row.get("brandName"),
            row.get("advertiser_name"),
            industry,
            industry_key,
            " ".join(str(t) for t in tags if t),
            " ".join(str(t) for t in keywords if t),
        )
        if p
    ).lower()
    if not hay.strip():
        return False
    return all(t in hay for t in tokens)


def filter_top_ads_by_query(
    rows: list[dict[str, Any]], q: str | None
) -> list[dict[str, Any]]:
    return [r for r in rows if isinstance(r, dict) and top_ad_matches_query(r, q)]


def fetch_limit_for_query(limit: int, q: str | None) -> int:
    """Over-fetch when keyword filtering will drop soft-matched noise."""
    base = max(1, min(int(limit), 100))
    if not (q or "").strip():
        return base
    return min(100, max(base * 5, 40))


def likes_is_approximate(likes: int | None) -> bool:
    """TikTok often surfaces rounded displays (60K → 60000) on Top Ads cards."""
    if likes is None or likes < 10_000:
        return False
    if likes < 1_000_000:
        return likes % 1000 == 0
    return likes % 100_000 == 0


def _video_block(row: dict[str, Any]) -> dict[str, Any]:
    info = row.get("video_info") if isinstance(row.get("video_info"), dict) else {}
    video_urls = info.get("video_url") if isinstance(info.get("video_url"), dict) else {}
    url = safe_str(
        row.get("video_url")
        or row.get("videoUrl")
        or video_urls.get("720p")
        or video_urls.get("540p")
    )
    url_hd = safe_str(row.get("video_url_hd") or row.get("videoUrlHd") or video_urls.get("1080p"))
    # Drop fake HD when it's a byte-identical copy of the standard rendition.
    if url_hd and url and url_hd == url:
        url_hd = None
    cover = safe_str(
        row.get("cover_url")
        or row.get("coverUrl")
        or info.get("cover")
        or row.get("cover")
    )
    return {
        "id": safe_str(row.get("video_id") or row.get("videoId") or info.get("vid")),
        "url": url,
        "urlHd": url_hd,
        "cover": cover,
        "durationSeconds": duration_seconds(
            row.get("video_duration_seconds")
            or row.get("durationSeconds")
            or info.get("duration")
        ),
        "width": safe_int(row.get("video_width") or row.get("width") or info.get("width")),
        "height": safe_int(row.get("video_height") or row.get("height") or info.get("height")),
    }


def normalize_top_ad(row: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream Top Ads row to the public Captapi shape."""
    ad_id = safe_str(row.get("ad_id") or row.get("id") or row.get("material_id"))
    brand = safe_str(row.get("brand_name") or row.get("brandName") or row.get("advertiser_name"))
    if brand and brand.strip().lower() in {"not mention", "n/a", "unknown", "-"}:
        brand = None
    countries = row.get("countries") or row.get("country") or []
    if isinstance(countries, str):
        countries = [countries]
    if not isinstance(countries, list):
        countries = []
    countries = [str(c).upper() for c in countries if c]

    video = _video_block(row)
    # Convenience list for clients that want flat media URLs (deduped).
    media: list[str] = []
    for u in (video.get("cover"), video.get("urlHd"), video.get("url")):
        if isinstance(u, str) and u.startswith("http") and u not in media:
            media.append(u)

    tags = row.get("tags") if isinstance(row.get("tags"), list) else []
    tag_list = [str(t) for t in tags if t]
    ctr = row.get("ctr")
    if ctr is None:
        ctr = row.get("ctr_rank_pct")
    # Creative Center ships a normalized 0–1 score (not raw click %); keep as-is.
    ctr_num = safe_float(ctr)

    objective_key = safe_str(row.get("objective_key") or row.get("objectiveKey"))
    objective = safe_str(row.get("objective"))
    if not objective and objective_key:
        objective = OBJECTIVE_LABELS.get(objective_key) or objective_key.replace(
            "campaign_objective_", ""
        ).replace("_", " ").title()

    is_spark_raw = row.get("is_spark_ad")
    if is_spark_raw is None:
        is_spark_raw = row.get("isSparkAd")
    is_spark = bool(is_spark_raw) if is_spark_raw is not None else None

    industry_key = safe_str(row.get("industry_key") or row.get("industryKey"))
    industry = resolve_industry_label(industry_key, safe_str(row.get("industry")))
    ad_format = resolve_ad_format(
        safe_str(row.get("ad_format") or row.get("adFormat")),
        is_spark,
    )
    likes = safe_int(row.get("likes") or row.get("like"))

    # Prefer the per-ad Creative Center detail page — never the search-page echo
    # that actors put in source_url.
    per_ad = detail_url(ad_id) if ad_id else None
    upstream_detail = safe_str(row.get("detail_url") or row.get("detailsUrl") or row.get("details_url"))
    if upstream_detail and "/topads/" in upstream_detail and "keyword=" not in upstream_detail:
        per_ad = upstream_detail or per_ad

    out: dict[str, Any] = {
        "platform": "tiktok_creative_center",
        "id": ad_id,
        "url": per_ad,
        "title": safe_str(row.get("ad_title") or row.get("title") or row.get("adTitle")),
        "brandName": brand,
        "likes": likes,
        "likesIsApproximate": likes_is_approximate(likes),
        "ctr": ctr_num,
        "ctrTier": safe_str(row.get("ctr_tier") or row.get("ctrTier")),
        "costTier": safe_int(
            row.get("cost_tier") if row.get("cost_tier") is not None else row.get("cost")
        ),
        "isSparkAd": is_spark,
        "industry": industry,
        "industryKey": industry_key,
        "objective": objective,
        "adFormat": ad_format,
        "countries": countries,
        "video": video,
        "media": media,
    }
    if objective_key:
        out["objectiveKey"] = objective_key
    if tag_list:
        out["tags"] = tag_list
    return out


def apify_input(
    *,
    country: str,
    period: int,
    order_by: str,
    limit: int,
    q: str | None = None,
    industry: str | None = None,
    objective: str | None = None,
    ad_format: str | None = None,
) -> dict[str, Any]:
    """Build ``khadinakbar/tiktok-ads-scraper`` (and compatible) actor input."""
    payload: dict[str, Any] = {
        "countryCode": (country or "US").upper(),
        "country": (country or "US").upper(),
        "period": str(period),
        "orderBy": order_by,
        "maxResults": max(1, min(int(limit), 100)),
        "maxItems": max(1, min(int(limit), 100)),
    }
    query = (q or "").strip()
    if query:
        payload["keyword"] = query
        payload["query"] = query
    # Actor rejects anything outside its fixed industry enum with 400
    # invalid-input (we wrap that as 502). Map/validate before send.
    apify_industry = normalize_apify_industry(industry)
    if apify_industry:
        payload["industry"] = apify_industry
    apify_objective = normalize_apify_objective(objective)
    if apify_objective:
        payload["objective"] = apify_objective
    if ad_format:
        # Actor accepts labels like "Spark Ads" / filter echoes.
        fmt = ad_format.strip().lower().replace("-", "_")
        if fmt in {"spark", "spark_ads", "sparkads"}:
            payload["adFormat"] = "Spark Ads"
        elif fmt in {"non_spark", "nonspark", "non-spark"}:
            payload["adFormat"] = "Non-Spark Ads"
        elif fmt in {"collection", "collection_ads"}:
            payload["adFormat"] = "Collection Ads"
        else:
            fmt_raw = ad_format.strip()
            if fmt_raw.lower() not in _FILTER_ECHO:
                payload["adFormat"] = fmt_raw
    return payload


def normalize_apify_industry(value: str | None) -> str | None:
    """Map Captapi industry (key or label) → actor enum, or None for all.

    Raises ``ValueError`` when the value cannot be mapped — callers should
    return HTTP 400 instead of forwarding raw strings that Apify rejects.
    """
    if value is None:
        return None
    raw = value.strip()
    if not raw or _fold_key(raw) in _FILTER_ECHO or _fold_key(raw) == "all industries":
        return None

    by_norm = {_fold_key(x): x for x in APIFY_INDUSTRIES}
    folded = _fold_key(raw)
    if folded in by_norm:
        label = by_norm[folded]
        return None if label == "All Industries" else label
    if folded in _INDUSTRY_ALIASES:
        return _INDUSTRY_ALIASES[folded]

    # label_25100000000 / 25100000000 → prefix map (Games → Gaming).
    digits = raw.removeprefix("label_")
    if digits.isdigit() and len(digits) >= 2:
        mapped = _TIKTOK_PREFIX_TO_APIFY.get(digits[:2])
        if mapped:
            return mapped
        resolved = resolve_industry_label(raw, None)
        if resolved:
            return normalize_apify_industry(resolved)

    # Human TikTok leaf label ("Cosmetics", "Games") → alias / contains match.
    resolved = resolve_industry_label(None, raw) or raw
    resolved_fold = _fold_key(resolved)
    if resolved_fold in _INDUSTRY_ALIASES:
        return _INDUSTRY_ALIASES[resolved_fold]
    if resolved_fold in by_norm:
        label = by_norm[resolved_fold]
        return None if label == "All Industries" else label
    for key, apify_label in _INDUSTRY_ALIASES.items():
        if key in resolved_fold or resolved_fold in key:
            return apify_label
    for norm, apify_label in by_norm.items():
        if norm == "all industries":
            continue
        if norm in resolved_fold or resolved_fold in norm:
            return apify_label

    allowed = ", ".join(APIFY_INDUSTRIES)
    raise ValueError(
        f"industry must be one of: {allowed} "
        f"(or a TikTok industry key like label_25000000000). Got: {raw!r}"
    )


def normalize_apify_objective(value: str | None) -> str | None:
    """Map Captapi objective → actor enum, or None for all. Raises ValueError."""
    if value is None:
        return None
    raw = value.strip()
    if not raw or _fold_key(raw) in _FILTER_ECHO or _fold_key(raw) == "all objectives":
        return None
    folded = _fold_key(raw).replace(" ", "_")
    spaced = _fold_key(raw)
    by_norm = {_fold_key(x): x for x in APIFY_OBJECTIVES}
    if spaced in by_norm:
        label = by_norm[spaced]
        return None if label == "All Objectives" else label
    if spaced in _OBJECTIVE_ALIASES:
        return _OBJECTIVE_ALIASES[spaced]
    if folded in _OBJECTIVE_ALIASES:
        return _OBJECTIVE_ALIASES[folded]
    # Product Sales etc. are Creative Center labels the actor does not accept.
    allowed = ", ".join(APIFY_OBJECTIVES)
    raise ValueError(
        f"objective must be one of: {allowed}. Got: {raw!r}"
    )


def _page_url(
    *,
    country: str,
    period: int,
    order_by: str,
    q: str | None = None,
    industry: str | None = None,
    objective: str | None = None,
) -> str:
    page_order = PAGE_ORDER_BY.get(order_by, "for_you")
    params: dict[str, str] = {
        "period": str(period),
        "region": (country or "US").upper(),
        "order_by": page_order,
    }
    query = (q or "").strip()
    if query:
        params["keyword"] = query
    if industry:
        params["industry"] = industry.strip()
    if objective:
        params["objective"] = objective.strip()
    return f"{TOP_ADS_PAGE}?{urlencode(params)}"


def _parse_xhr_body(item: dict[str, Any]) -> dict[str, Any] | None:
    rb = item.get("response_body")
    if isinstance(rb, dict):
        return rb
    if isinstance(rb, str) and rb.strip():
        try:
            data = json.loads(rb)
        except ValueError:
            return None
        return data if isinstance(data, dict) else None
    return None


def _list_query(url: str) -> dict[str, str]:
    qs = parse_qs(urlparse(url).query)
    return {k: (v[0] if v else "") for k, v in qs.items()}


def _score_list_xhr(
    item: dict[str, Any],
    *,
    country: str,
    period: int,
    order_by: str,
    q: str | None,
) -> int:
    url = str(item.get("url") or "")
    if LIST_PATH not in url:
        return -1
    status = item.get("status_code")
    if status is not None and status != 200:
        return -1
    qs = _list_query(url)
    page_order = PAGE_ORDER_BY.get(order_by, "for_you")
    score = 0
    if qs.get("country_code", "").upper() == (country or "US").upper():
        score += 3
    if qs.get("period") == str(period):
        score += 2
    api_order = (qs.get("order_by") or "").lower()
    if api_order == page_order or api_order == order_by.lower().replace(" ", "_"):
        score += 4
    elif page_order == "for_you" and api_order in {"for_you", ""}:
        score += 2
    query = (q or "").strip().lower()
    if query:
        kw = (qs.get("keyword") or qs.get("q") or "").lower()
        if query in kw or kw in query:
            score += 3
    body = _parse_xhr_body(item)
    if not body:
        return -1
    materials = (body.get("data") or {}).get("materials") if isinstance(body.get("data"), dict) else None
    if isinstance(materials, list) and materials:
        score += 5
    return score


def filter_top_ads(
    materials: list[dict[str, Any]],
    *,
    q: str | None = None,
    industry: str | None = None,
    objective: str | None = None,
    ad_format: str | None = None,
) -> list[dict[str, Any]]:
    out = materials
    ind = (industry or "").strip().lower()
    if ind and ind not in _FILTER_ECHO:
        out = [
            m
            for m in out
            if ind in str(m.get("industry_key") or m.get("industryKey") or "").lower()
            or ind in str(m.get("industry") or "").lower()
            or ind
            in (
                resolve_industry_label(
                    safe_str(m.get("industry_key") or m.get("industryKey")),
                    safe_str(m.get("industry")),
                )
                or ""
            ).lower()
        ]
    obj = (objective or "").strip().lower().replace(" ", "_").replace("-", "_")
    if obj and obj not in _FILTER_ECHO:
        out = [
            m
            for m in out
            if obj in str(m.get("objective_key") or m.get("objectiveKey") or "").lower()
            or obj in str(m.get("objective") or "").lower().replace(" ", "_")
        ]
    fmt = (ad_format or "").strip().lower().replace("-", "_")
    if fmt in {"spark", "spark_ads", "sparkads"}:
        out = [m for m in out if m.get("is_spark_ad") is True or m.get("isSparkAd") is True]
    elif fmt in {"non_spark", "nonspark", "non_spark_ads"}:
        out = [m for m in out if m.get("is_spark_ad") is False or m.get("isSparkAd") is False]
    if (q or "").strip():
        out = filter_top_ads_by_query(out, q)
    return out


async def search_top_ads(
    *,
    country: str = "US",
    period: int = 30,
    order_by: str = "For You",
    limit: int = 20,
    q: str | None = None,
    industry: str | None = None,
    objective: str | None = None,
    ad_format: str | None = None,
) -> list[dict[str, Any]] | None:
    """Decodo-native Top Ads via Creative Center XHR capture.

    Returns raw material dicts (same keys as creative_radar ``materials``), or
    ``None`` when Decodo is unavailable / capture failed so the router can fall
    back to Apify.
    """
    from app.services import decodo_fetch

    if not decodo_fetch.enabled():
        return None
    # Spark / Non-Spark is not present on the public list payload — Apify only.
    if (ad_format or "").strip():
        return None

    region = (country or "US").strip().upper() or "US"
    want = max(0, min(int(limit), 100))
    page = _page_url(
        country=region,
        period=period,
        order_by=order_by,
        q=q,
        industry=industry,
        objective=objective,
    )
    # Brief wait so the signed top_ads list XHR fires after hydration.
    actions = [{"type": "wait", "timeout": 5}]
    got = await decodo_fetch.fetch_xhr(
        page,
        timeout=150.0,
        headless="html",
        browser_actions=actions,
        geo=region if region.isalpha() and len(region) == 2 else "US",
    )
    if got is None:
        log.warning("tiktok_cc_native_decodo_miss", page=page)
        return None
    _status, xhrs = got
    best: dict[str, Any] | None = None
    best_score = -1
    for item in xhrs:
        score = _score_list_xhr(
            item,
            country=region,
            period=period,
            order_by=order_by,
            q=q,
        )
        if score > best_score:
            best_score = score
            best = item
    if not best or best_score < 5:
        log.warning("tiktok_cc_native_no_list_xhr", page=page, xhr_count=len(xhrs))
        return None
    body = _parse_xhr_body(best)
    if not body:
        return None
    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    materials = data.get("materials") if isinstance(data, dict) else None
    if not isinstance(materials, list):
        return None
    rows = [m for m in materials if isinstance(m, dict) and (m.get("id") or m.get("ad_id"))]
    for row in rows:
        row.setdefault("period_days", period)
        if region and not row.get("countries") and not row.get("country"):
            row["countries"] = [region]
    rows = filter_top_ads(
        rows,
        q=q,
        industry=industry,
        objective=objective,
        ad_format=ad_format,
    )
    return rows[:want]
