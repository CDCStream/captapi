"""TikTok Creative Center Top Ads.

Public Top Ads live on ``ads.tiktok.com/business/creativecenter`` and are served
by TikTok's signed ``creative_radar_api`` (browser ``user-sign`` bootstrap).
Native path: Decodo headless + XHR capture of ``top_ads/v2/list``.
Apify remains the fallback when Decodo is down or returns nothing.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import structlog

from app.utils.formatters import duration_seconds, safe_float, safe_int, safe_str

log = structlog.get_logger(__name__)

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
    media: list[str] = []
    for u in (video.get("cover"), video.get("urlHd"), video.get("url")):
        if isinstance(u, str) and u.startswith("http") and u not in media:
            media.append(u)

    tags = row.get("tags") if isinstance(row.get("tags"), list) else []
    ctr = row.get("ctr")
    if ctr is None:
        ctr = row.get("ctr_rank_pct")
    # Some sources ship CTR as 0-100 percentile; keep numeric as-is when 0-1-ish.
    ctr_num = safe_float(ctr)

    objective_key = safe_str(row.get("objective_key") or row.get("objectiveKey"))
    objective = safe_str(row.get("objective"))
    if not objective and objective_key:
        objective = OBJECTIVE_LABELS.get(objective_key) or objective_key.replace(
            "campaign_objective_", ""
        ).replace("_", " ").title()

    return {
        "platform": "tiktok_creative_center",
        "id": ad_id,
        "url": safe_str(row.get("source_url") or row.get("detail_url")) or (detail_url(ad_id) if ad_id else None),
        "title": safe_str(row.get("ad_title") or row.get("title") or row.get("adTitle")),
        "brandName": brand,
        "likes": safe_int(row.get("likes") or row.get("like")),
        "ctr": ctr_num,
        "ctrTier": safe_str(row.get("ctr_tier") or row.get("ctrTier")),
        "costTier": safe_int(row.get("cost_tier") if row.get("cost_tier") is not None else row.get("cost")),
        "favorite": bool(row.get("favorite")) if row.get("favorite") is not None else None,
        "isSparkAd": bool(row.get("is_spark_ad") if row.get("is_spark_ad") is not None else row.get("isSparkAd"))
        if (row.get("is_spark_ad") is not None or row.get("isSparkAd") is not None)
        else None,
        "industry": safe_str(row.get("industry")),
        "industryKey": safe_str(row.get("industry_key") or row.get("industryKey")),
        "objective": objective,
        "objectiveKey": objective_key,
        "adFormat": safe_str(row.get("ad_format") or row.get("adFormat")),
        "countries": countries,
        "periodDays": safe_int(row.get("period_days") or row.get("periodDays")),
        "video": video,
        "media": media,
        "tags": [str(t) for t in tags if t],
    }


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
    if industry:
        payload["industry"] = industry
        payload["industryKey"] = industry
    if objective:
        payload["objective"] = objective
        payload["objectiveKey"] = objective
    if ad_format:
        # Actor accepts labels like "Spark Ads" / filter echoes.
        fmt = ad_format.strip().lower().replace("-", "_")
        if fmt in {"spark", "spark_ads", "sparkads"}:
            payload["adFormat"] = "Spark Ads"
        elif fmt in {"non_spark", "nonspark", "non-spark"}:
            payload["adFormat"] = "Non-Spark Ads"
        else:
            payload["adFormat"] = ad_format
    return payload


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


def _client_filter(
    materials: list[dict[str, Any]],
    *,
    industry: str | None,
    objective: str | None,
    ad_format: str | None,
) -> list[dict[str, Any]]:
    out = materials
    ind = (industry or "").strip().lower()
    if ind:
        out = [
            m
            for m in out
            if ind in str(m.get("industry_key") or "").lower()
            or ind in str(m.get("industry") or "").lower()
        ]
    obj = (objective or "").strip().lower().replace(" ", "_").replace("-", "_")
    if obj:
        out = [
            m
            for m in out
            if obj in str(m.get("objective_key") or "").lower()
            or obj in str(m.get("objective") or "").lower().replace(" ", "_")
        ]
    fmt = (ad_format or "").strip().lower().replace("-", "_")
    if fmt in {"spark", "spark_ads", "sparkads"}:
        out = [m for m in out if m.get("is_spark_ad") is True or m.get("isSparkAd") is True]
    elif fmt in {"non_spark", "nonspark", "non_spark_ads"}:
        out = [m for m in out if m.get("is_spark_ad") is False or m.get("isSparkAd") is False]
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
    rows = _client_filter(rows, industry=industry, objective=objective, ad_format=ad_format)
    return rows[: max(0, min(int(limit), 100))]
