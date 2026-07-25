"""Native TikTok Commercial Content Library search (DSA public JSON API).

Hits ``library.tiktok.com/api/v1/search`` without OAuth. Currently TikTok often
returns HTTP 421 ``system busy`` from datacenter/residential exits and Decodo
POST also fails (613), so callers should treat ``None`` as “fall back to Apify”.
When the endpoint recovers this path is ~proxy bandwidth only.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
import structlog

from app.services.http_fetch import DEFAULT_HEADERS, proxy_for

log = structlog.get_logger(__name__)

_BASE = "https://library.tiktok.com"
_HEADERS = {
    **DEFAULT_HEADERS,
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": _BASE,
    "Referer": f"{_BASE}/",
}


def _to_normalize_shape(row: dict[str, Any]) -> dict[str, Any]:
    ad_id = str(row.get("ad_id") or row.get("id") or "").strip()
    advertiser = row.get("advertiser") if isinstance(row.get("advertiser"), dict) else {}
    name = (
        row.get("advertiser_name")
        or advertiser.get("name")
        or advertiser.get("business_name")
        or row.get("brand_name")
    )
    media: list[str] = []
    for key in ("cover_image_url", "image_urls", "videos", "video_url", "cover"):
        val = row.get(key)
        if isinstance(val, str) and val.startswith("http"):
            media.append(val)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, str) and item.startswith("http"):
                    media.append(item)
                elif isinstance(item, dict):
                    for k in ("url", "cover", "video_url", "image_url"):
                        u = item.get(k)
                        if isinstance(u, str) and u.startswith("http"):
                            media.append(u)
    return {
        "adId": ad_id,
        "id": ad_id,
        "advertiserName": name,
        "adFormat": row.get("ad_format") or row.get("format") or "video",
        "first_shown_date": row.get("first_shown_date") or row.get("firstShownDate"),
        "last_shown_date": row.get("last_shown_date") or row.get("lastShownDate"),
        "imageUrls": media,
        "videoUrl": next((m for m in media if "video" in m or "cdn" in m), None),
        "estimatedAudience": row.get("estimated_audience") or row.get("estimatedAudience"),
    }


async def _post_search(
    query: str,
    *,
    region: str,
    limit: int,
    proxy: str | None,
    days: int = 30,
) -> list[dict[str, Any]] | None:
    end = int(time.time())
    start = end - max(1, days) * 24 * 3600
    url = (
        f"{_BASE}/api/v1/search"
        f"?region={region.upper()}&type=1&start_time={start}&end_time={end}"
    )
    # query_type must be a STRING ("3" = keyword). Page size is server-capped at 12.
    body = {
        "query": query,
        "query_type": "3",
        "order": "last_shown_date,desc",
        "offset": 0,
        "limit": min(max(1, limit), 12),
    }
    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            headers=_HEADERS,
            proxy=proxy,
        ) as client:
            resp = await client.post(url, json=body)
    except httpx.HTTPError as exc:
        log.warning("tiktok_ads_native_transport", error=str(exc), proxy=bool(proxy))
        return None

    text = resp.text or ""
    if resp.status_code != 200:
        log.warning(
            "tiktok_ads_native_http",
            status=resp.status_code,
            body=text[:80],
            proxy=bool(proxy),
        )
        return None
    if re_soft_limit(text):
        log.warning("tiktok_ads_native_rate_limited", proxy=bool(proxy))
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    # code 0 = ok; some responses omit code when healthy.
    code = payload.get("code")
    if code not in (None, 0, "0"):
        log.warning("tiktok_ads_native_code", code=code, proxy=bool(proxy))
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    return [_to_normalize_shape(r) for r in data if isinstance(r, dict)]


def re_soft_limit(text: str) -> bool:
    return bool(text) and (not text.lstrip().startswith("{")) and (
        "limit" in text.lower() or "busy" in text.lower() or "exceed" in text.lower()
    )


async def search_ads(
    q: str, *, country: str = "DE", limit: int = 20
) -> list[dict[str, Any]] | None:
    query = (q or "").strip()
    if len(query) < 2:
        return []

    region = (country or "DE").upper()
    want = max(1, int(limit))
    tiers: list[tuple[str, str | None]] = [
        ("datacenter", proxy_for("datacenter")),
        ("residential", proxy_for("residential")),
        ("direct", None),
    ]

    # Server caps page size at 12; first healthy tier wins (incl. empty list).
    for tier, proxy in tiers:
        if tier != "direct" and not proxy:
            continue
        page = await _post_search(query, region=region, limit=min(12, want), proxy=proxy)
        if page is None:
            continue
        log.info(
            "tiktok_ads_native_search_ok",
            tier=tier,
            count=len(page),
            q=query[:40],
            region=region,
        )
        return page[:want]
    return None
