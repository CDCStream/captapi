"""Native TikTok Commercial Content Library search (DSA public JSON API).

Hits ``library.tiktok.com/api/v1/search`` without OAuth. Currently TikTok often
returns HTTP 421 ``system busy`` from datacenter/residential exits and Decodo
POST also fails (613), so callers should treat ``None`` as “fall back to Apify”.
When the endpoint recovers this path is ~proxy bandwidth only.
"""

from __future__ import annotations

import re
import time
from urllib.parse import quote
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

    # JSON API often 421 "system busy" — Decodo-rendered library SERP.
    decodo_rows = await search_ads_via_decodo(query, country=region, limit=want)
    if decodo_rows is not None:
        return decodo_rows[:want]
    return None



def detail_url(ad_id: str, *, region: str = "DE") -> str:
    aid = (ad_id or "").strip()
    reg = (region or "DE").upper()
    return f"https://library.tiktok.com/ads/detail/?ad_id={aid}&region={reg}"


def _label_value(html: str, label: str) -> str | None:
    """Pull the first text node after a visible label."""
    patterns = [
        rf">{re.escape(label)}[:\s]*</[^>]+>\s*<[^>]+>([^<]{{2,200}})",
        rf">{re.escape(label)}[:\s]*</[^>]+>\s*([^<]{{2,200}})",
        rf">{re.escape(label)}\s*</[^>]+>\s*<[^>]+>([^<]{{2,200}})",
    ]
    for pat in patterns:
        m = re.search(pat, html or "", re.I)
        if m:
            text = re.sub(r"\s+", " ", m.group(1)).strip()
            if text:
                return text
    return None


def extract_ad_details(html: str, *, ad_id: str) -> dict[str, Any] | None:
    """Parse hydrated library.tiktok.com detail HTML."""
    if not html or not ad_id:
        return None
    if ad_id not in html and f"Ad ID" not in html:
        return None

    advertiser = _label_value(html, "Advertiser")
    # Skip section headers that leak through.
    if advertiser and advertiser.lower() in {"advertiser", "ad paid for by"}:
        advertiser = None
    paid_by = _label_value(html, "Ad paid for by")
    first_shown = _label_value(html, "First shown")
    last_shown = _label_value(html, "Last shown")
    reach = _label_value(html, "Unique users seen")
    location = _label_value(html, "Advertiser's registered location")
    caption = _label_value(html, "Ad caption")

    video_url = None
    vm = re.search(
        r'<video[^>]+src="(https://library\.tiktok\.com/api/v1/cdn/[^"]+)"',
        html,
        re.I,
    )
    if vm:
        video_url = vm.group(1).replace("&amp;", "&")

    media: list[str] = []
    for src in re.findall(
        r'(?:src|poster|data-src)="(https://[^"]+(?:tiktokcdn|byteoversea|ibyteimg)[^"]*)"',
        html,
        re.I,
    ):
        url = src.replace("&amp;", "&")
        if "gtm" in url or "slardar" in url or "privacy" in url:
            continue
        if url not in media:
            media.append(url)
    if video_url and video_url not in media:
        media.insert(0, video_url)

    if not any([advertiser, paid_by, video_url, media, first_shown]):
        return None

    return {
        "adId": ad_id,
        "id": ad_id,
        "advertiserName": advertiser or paid_by,
        "payer": paid_by,
        "advertiserLocation": location,
        "adFormat": "video" if video_url else "image",
        "text": caption,
        "body": caption,
        "first_shown_date": first_shown,
        "last_shown_date": last_shown,
        "estimatedAudience": reach,
        "imageUrls": [m for m in media if "video" not in m.lower() or "cdn" not in m],
        "videoUrl": video_url,
        "media": media,
        "url": f"https://library.tiktok.com/ads/detail/?ad_id={ad_id}",
    }


async def ad_details(
    ad_id: str, *, country: str = "DE"
) -> dict[str, Any] | None:
    """Fetch one Commercial Content Library ad via Decodo HTML."""
    from app.services import decodo_fetch

    aid = (ad_id or "").strip()
    if not aid.isdigit() or not decodo_fetch.enabled():
        return None
    url = detail_url(aid, region=country)
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or len(html) < 5000:
        log.warning(
            "tiktok_ads_native_detail_weak",
            status=status,
            length=len(html or ""),
            ad_id=aid,
        )
        return None
    row = extract_ad_details(html, ad_id=aid)
    if not row:
        log.warning("tiktok_ads_native_detail_miss", ad_id=aid, length=len(html))
        return None
    log.info("tiktok_ads_native_detail_ok", ad_id=aid)
    return row


async def search_ads_via_decodo(
    q: str, *, country: str = "DE", limit: int = 20
) -> list[dict[str, Any]] | None:
    """HTML SERP fallthrough when the JSON search API returns 421."""
    from app.services import decodo_fetch
    import html as html_lib

    query = (q or "").strip()
    if len(query) < 2 or not decodo_fetch.enabled():
        return None
    region = (country or "DE").upper()
    url = f"https://library.tiktok.com/ads?region={region}&query={quote(query, safe='')}"
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or len(body) < 5000:
        return None

    ads: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in re.finditer(r"/ads/detail/\?ad_id=(\d{10,})", body):
        ad_id = m.group(1)
        if ad_id in seen:
            continue
        seen.add(ad_id)
        win = body[max(0, m.start() - 1600) : m.end() + 900]
        texts = [
            html_lib.unescape(t).strip()
            for t in re.findall(r">([^<>]{2,160})<", win)
            if t and t.strip()
        ]
        advertiser = None
        first = last = reach = None
        for i, t in enumerate(texts):
            low = t.lower()
            if low == "ad" and i + 1 < len(texts):
                cand = texts[i + 1]
                if cand.lower() not in {"ad", "first shown:", "last shown:"}:
                    advertiser = cand
            if low == "first shown:" and i + 1 < len(texts):
                first = texts[i + 1]
            if low == "last shown:" and i + 1 < len(texts):
                last = texts[i + 1]
            if low == "unique users seen:" and i + 1 < len(texts):
                reach = texts[i + 1]
        imgs = [
            html_lib.unescape(u)
            for u in re.findall(
                r'(https://[^"\s]+(?:tiktokcdn|byteoversea|ibyteimg)[^"\s]*)', win
            )
        ]
        ads.append(
            {
                "adId": ad_id,
                "id": ad_id,
                "advertiserName": advertiser,
                "adFormat": "video",
                "first_shown_date": first,
                "last_shown_date": last,
                "estimatedAudience": reach,
                "imageUrls": imgs[:3],
                "media": imgs[:3],
                "url": f"https://library.tiktok.com/ads/detail/?ad_id={ad_id}",
            }
        )
        if len(ads) >= limit:
            break
    if not ads:
        return None
    log.info(
        "tiktok_ads_native_decodo_search_ok",
        count=len(ads),
        q=query[:40],
        region=region,
    )
    return ads
