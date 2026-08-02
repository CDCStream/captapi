"""TikTok Creative Center Top Ads.

Public Top Ads live on ``ads.tiktok.com/business/creativecenter`` and are served
by TikTok's signed ``creative_radar_api`` (browser ``user-sign`` bootstrap).
This module normalizes Apify Top Ads rows into Captapi's clean camelCase shape.
A native signed-bootstrap path can replace Apify later without changing the
router contract.
"""

from __future__ import annotations

from typing import Any

from app.utils.formatters import safe_float, safe_int, safe_str

# Actor display labels → Captapi orderBy query values.
ORDER_BY_ALIASES: dict[str, str] = {
    "for_you": "For You",
    "foryou": "For You",
    "like": "Likes",
    "likes": "Likes",
    "ctr": "CTR",
    "impression": "Impressions",
    "impressions": "Impressions",
    "cost": "Cost",
    # ScrapeCreators-style aliases → closest Creative Center sort.
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
        "durationSeconds": safe_float(
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
        "objective": safe_str(row.get("objective")),
        "objectiveKey": safe_str(row.get("objective_key") or row.get("objectiveKey")),
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
