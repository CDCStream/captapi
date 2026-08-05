"""Native TikTok Commercial Content Library search (DSA public JSON API).

Hits ``library.tiktok.com/api/v1/search`` without OAuth. Currently TikTok often
returns HTTP 421 ``system busy`` from datacenter/residential exits and Decodo
POST also fails (613), so callers should treat ``None`` as “fall back to Apify”.
When the endpoint recovers this path is ~proxy bandwidth only.
"""

from __future__ import annotations

import asyncio
import re
import time
from urllib.parse import quote
from typing import Any, Literal

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
    caption = (
        row.get("ad_text")
        or row.get("adText")
        or row.get("caption")
        or row.get("text")
        or row.get("body")
    )
    return {
        "adId": ad_id,
        "id": ad_id,
        "advertiserName": name,
        "advertiserId": row.get("advertiser_id")
        or advertiser.get("id")
        or row.get("advertiserId"),
        "advertiserUrl": row.get("advertiser_url") or advertiser.get("url"),
        "cta": row.get("cta") or row.get("cta_text") or row.get("ctaText"),
        "landingUrl": row.get("landing_url")
        or row.get("landingUrl")
        or row.get("destination_url")
        or row.get("click_url"),
        "headline": row.get("headline") or row.get("title"),
        "adFormat": row.get("ad_format") or row.get("format") or "video",
        "first_shown_date": row.get("first_shown_date") or row.get("firstShownDate"),
        "last_shown_date": row.get("last_shown_date") or row.get("lastShownDate"),
        "imageUrls": media,
        "videoUrl": next((m for m in media if "video" in m or "cdn" in m), None),
        "estimatedAudience": row.get("estimated_audience") or row.get("estimatedAudience"),
        "text": caption,
        "body": caption,
    }


MatchMode = Literal["any", "all"]

# Cap Decodo HTML SERP so clients are not billed after ALB/nginx disconnect.
DECODO_TIMEOUT_SECONDS = 40.0


def _query_tokens(q: str) -> list[str]:
    return [t for t in re.split(r"\W+", (q or "").lower()) if len(t) >= 2]


def normalize_match_mode(match: str | None) -> MatchMode:
    raw = (match or "any").strip().lower()
    if raw in {"any", "or"}:
        return "any"
    if raw in {"all", "and"}:
        return "all"
    raise ValueError('match must be "any" or "all"')


def ad_matches_query(
    row: dict[str, Any],
    q: str,
    *,
    match: MatchMode = "any",
) -> bool:
    """True when query tokens appear as case-insensitive substrings in copy.

    ``match=any`` (default): at least one token. ``match=all``: every token.
    TikTok's library SERP is noisy; local filtering is a second pass.
    """
    tokens = _query_tokens(q)
    if not tokens:
        return True
    hay_parts = [
        row.get("advertiserName"),
        row.get("advertiser_name"),
        row.get("brand_name"),
        row.get("payer"),
        row.get("text"),
        row.get("body"),
        row.get("caption"),
        row.get("headline"),
        row.get("cta"),
        row.get("landingUrl"),
    ]
    adv = row.get("advertiser") if isinstance(row.get("advertiser"), dict) else {}
    if adv:
        hay_parts.extend([adv.get("name"), adv.get("business_name")])
    hay = " ".join(str(p) for p in hay_parts if p).lower()
    if not hay.strip():
        # No copy yet (pre-hydrate) — keep for hydrate, filter again later.
        return True
    if match == "all":
        return all(t in hay for t in tokens)
    return any(t in hay for t in tokens)


def filter_ads_by_query(
    rows: list[dict[str, Any]],
    q: str,
    *,
    match: MatchMode = "any",
) -> dict[str, Any]:
    """Apply local keyword filter; return rows + match transparency fields."""
    matched_from = len(rows)
    if not (q or "").strip():
        return {
            "rows": list(rows),
            "matchedFrom": matched_from,
            "filteredOut": 0,
            "literalMatches": matched_from,
            "match": match,
            "matchBasis": "none",
        }
    # Rows without copy yet stay in (hydrate path); drop only after text exists
    # and fails the token test.
    kept: list[dict[str, Any]] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        if ad_matches_query(r, q, match=match):
            kept.append(r)
    return {
        "rows": kept,
        "matchedFrom": matched_from,
        "filteredOut": matched_from - len(kept),
        "literalMatches": len(kept),
        "match": match,
        "matchBasis": match,
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


async def _hydrate_captions(
    rows: list[dict[str, Any]],
    *,
    country: str,
    concurrency: int = 3,
) -> list[dict[str, Any]]:
    """SERP/JSON search omit ad copy — fill ``text`` from each detail page."""
    if not rows:
        return rows
    sem = asyncio.Semaphore(max(1, min(concurrency, 5)))

    async def _one(row: dict[str, Any]) -> dict[str, Any]:
        has_text = bool(row.get("text") or row.get("body") or row.get("caption"))
        has_loc = bool(row.get("advertiserLocation"))
        if has_text and has_loc:
            return row
        aid = str(row.get("id") or row.get("adId") or "").strip()
        if not aid.isdigit():
            return row
        async with sem:
            detail = await ad_details(aid, country=country)
        if not detail:
            return row
        out = dict(row)
        caption = detail.get("text") or detail.get("body")
        if caption:
            out["text"] = caption
            out["body"] = caption
        # Detail page often has richer advertiser / delivery fields than SERP.
        for key in (
            "advertiserName",
            "advertiserId",
            "advertiserUrl",
            "payer",
            "advertiserLocation",
            "first_shown_date",
            "last_shown_date",
            "estimatedAudience",
            "videoUrl",
            "imageUrls",
            "media",
            "adFormat",
            "cta",
            "landingUrl",
            "headline",
        ):
            if detail.get(key) not in (None, "", [], {}) and out.get(key) in (None, "", [], {}):
                out[key] = detail[key]
        return out

    return list(await asyncio.gather(*[_one(r) for r in rows]))


async def search_ads(
    q: str, *, country: str = "GB", limit: int = 20
) -> list[dict[str, Any]] | None:
    """Search TikTok Commercial Content Library (EU DSA).

    Prefers Decodo HTML SERP — the JSON ``/api/v1/search`` endpoint is chronically
    HTTP 421 ``system busy`` from our exits. Returns ``None`` only when every
    native path fails (caller may fall back to Apify).
    """
    query = (q or "").strip()
    if len(query) < 2:
        return []

    region = (country or "GB").upper()
    want = max(1, int(limit))
    # Over-fetch SERP candidates — TikTok soft-matches, then we relevance-filter.
    serp_limit = min(60, max(want * 3, want))
    rows: list[dict[str, Any]] | None = None

    # 1) Decodo SERP first (reliable; ~1 headless render).
    decodo_rows = await search_ads_via_decodo(query, country=region, limit=serp_limit)
    if decodo_rows is not None:
        rows = decodo_rows[:serp_limit]

    # 2) JSON API secondary (cheap when TikTok stops returning 421).
    if rows is None:
        tiers: list[tuple[str, str | None]] = [
            ("datacenter", proxy_for("datacenter")),
            ("residential", proxy_for("residential")),
            ("direct", None),
        ]
        for tier, proxy in tiers:
            if tier != "direct" and not proxy:
                continue
            page = await _post_search(
                query, region=region, limit=min(12, serp_limit), proxy=proxy
            )
            if page is None:
                continue
            log.info(
                "tiktok_ads_native_search_ok",
                tier=tier,
                count=len(page),
                q=query[:40],
                region=region,
            )
            rows = page[:serp_limit]
            break

    if rows is None:
        return None
    if not rows:
        return []
    hydrated = await _hydrate_captions(rows, country=region)
    # Caller applies filter_ads_by_query (match=any|all + matchedFrom).
    filled = sum(1 for r in hydrated if r.get("text") or r.get("body"))
    log.info(
        "tiktok_ads_native_search_captions",
        q=query[:40],
        region=region,
        n=len(hydrated),
        with_text=filled,
    )
    return hydrated[: max(want * 3, want)]


def detail_url(ad_id: str, *, region: str = "GB") -> str:
    aid = (ad_id or "").strip()
    reg = (region or "GB").upper()
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


def _metric_from_text_nodes(html: str, label: str) -> str | None:
    """SERP/detail pages often put label and value in consecutive text nodes."""
    import html as html_lib

    texts = [
        html_lib.unescape(t).strip()
        for t in re.findall(r">([^<>]{1,200})<", html or "")
        if t and t.strip()
    ]
    want = label.lower().rstrip(":")
    skip = {want, "-", "n/a", "na", "—", "–"}
    for i, t in enumerate(texts):
        if t.lower().rstrip(":") == want and i + 1 < len(texts):
            cand = re.sub(r"\s+", " ", texts[i + 1]).strip()
            if cand and cand.lower() not in skip:
                return cand
    return None


def _first_label(html: str, *labels: str) -> str | None:
    for label in labels:
        for getter in (_label_value, _metric_from_text_nodes):
            val = getter(html, label)
            if val:
                return val
    return None


def _reach_from_html(html: str) -> str | None:
    """Unique-users / impressions band from detail HTML (search parity)."""
    for label in (
        "Unique users seen",
        "Unique user seen",
        "Users seen",
        "Impressions",
        "Estimated audience",
    ):
        val = _first_label(html, label)
        if val and re.search(r"\d", val):
            return val
    for key in (
        "unique_users_seen",
        "uniqueUsersSeen",
        "estimated_audience",
        "estimatedAudience",
        "impressions",
        "impression",
    ):
        m = re.search(rf'"{key}"\s*:\s*"([^"]+)"', html or "", re.I)
        if m and re.search(r"\d", m.group(1)):
            return m.group(1).strip()
    m = re.search(
        r"(?:Unique users seen|Impressions?)[^0-9<>]{0,80}"
        r"([<>]?\s*[0-9][\d,.]*\s*(?:[-–—]\s*[0-9][\d,.]*\s*)?[KMB]?)",
        html or "",
        re.I,
    )
    if m:
        band = re.sub(r"\s+", " ", m.group(1)).strip()
        if band:
            return band
    return None


_CAPTION_RE = re.compile(
    r"Ad caption[\s\S]{0,4000}?<div[^>]*>([^<]{1,500})</div>\s*<div[^>]*>\s*Call to action",
    re.I,
)


def _caption_from_html(html: str) -> str | None:
    """Detail pages put copy in the div between Ad caption and Call to action."""
    m = _CAPTION_RE.search(html or "")
    if m:
        text = re.sub(r"\s+", " ", m.group(1)).strip()
        if text and text not in {"-", "N/A", "n/a"}:
            return text
    return _first_label(html or "", "Ad caption")


def extract_ad_details(html: str, *, ad_id: str) -> dict[str, Any] | None:
    """Parse hydrated library.tiktok.com detail HTML."""
    if not html or not ad_id:
        return None
    if ad_id not in html and f"Ad ID" not in html:
        return None

    advertiser = _first_label(html, "Advertiser")
    # Skip section headers that leak through.
    if advertiser and advertiser.lower() in {"advertiser", "ad paid for by"}:
        advertiser = None
    paid_by = _first_label(html, "Ad paid for by")
    first_shown = _first_label(html, "First shown")
    last_shown = _first_label(html, "Last shown")
    reach = _reach_from_html(html)
    location = _first_label(html, "Advertiser's registered location", "Registered location")
    caption = _caption_from_html(html)
    cta = _first_label(html, "Call to action")
    if cta and cta.lower() in {"call to action", "cta", "-"}:
        cta = None

    landing = None
    for pat in (
        r'Call to action[\s\S]{0,800}?href="(https?://[^"]+)"',
        r'"landing_page_url"\s*:\s*"(https?://[^"]+)"',
        r'"click_url"\s*:\s*"(https?://[^"]+)"',
        r'"destination_url"\s*:\s*"(https?://[^"]+)"',
    ):
        lm = re.search(pat, html or "", re.I)
        if lm:
            cand = lm.group(1).replace("&amp;", "&")
            if "library.tiktok.com" not in cand and "tiktok.com/@" not in cand:
                landing = cand
                break
            if landing is None:
                landing = cand

    advertiser_id = None
    for pat in (
        r'"advertiser_id"\s*:\s*"?(\d{5,})"?',
        r'"business_id"\s*:\s*"?(\d{5,})"?',
        r'advertiserId["\s:=]+(\d{5,})',
    ):
        am = re.search(pat, html or "", re.I)
        if am:
            advertiser_id = am.group(1)
            break

    advertiser_url = None
    um = re.search(
        r'Advertiser[\s\S]{0,400}?href="(https?://(?:www\.)?tiktok\.com/@[^"]+)"',
        html or "",
        re.I,
    )
    if um:
        advertiser_url = um.group(1).replace("&amp;", "&")

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
        "advertiserId": advertiser_id,
        "advertiserUrl": advertiser_url,
        "payer": paid_by,
        "advertiserLocation": location,
        "adFormat": "video" if video_url else "image",
        "text": caption,
        "body": caption,
        "cta": cta,
        "landingUrl": landing,
        "first_shown_date": first_shown,
        "last_shown_date": last_shown,
        "estimatedAudience": reach,
        "impressions": reach,
        "imageUrls": [m for m in media if "video" not in m.lower() or "cdn" not in m],
        "videoUrl": video_url,
        "media": media,
        "url": f"https://library.tiktok.com/ads/detail/?ad_id={ad_id}",
    }


async def ad_details(
    ad_id: str, *, country: str = "GB"
) -> dict[str, Any] | None:
    """Fetch one Commercial Content Library ad via Decodo HTML."""
    from app.services import decodo_fetch

    aid = (ad_id or "").strip()
    if not aid.isdigit() or not decodo_fetch.enabled():
        return None
    url = detail_url(aid, region=country)
    got = await decodo_fetch.fetch_url(url, timeout=DECODO_TIMEOUT_SECONDS, headless="html")
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
    q: str, *, country: str = "GB", limit: int = 20
) -> list[dict[str, Any]] | None:
    """HTML SERP for ``library.tiktok.com`` (EU Commercial Content Library).

    Note: region=US often returns an empty library — this surface is DSA/EU-led.
    """
    from app.services import decodo_fetch
    import html as html_lib

    query = (q or "").strip()
    if len(query) < 2 or not decodo_fetch.enabled():
        return None
    region = (country or "GB").upper()
    url = f"https://library.tiktok.com/ads?region={region}&query={quote(query, safe='')}"
    got = await decodo_fetch.fetch_url(url, timeout=DECODO_TIMEOUT_SECONDS, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or len(body) < 5000:
        log.warning(
            "tiktok_ads_native_decodo_search_weak",
            status=status,
            length=len(body or ""),
            region=region,
            q=query[:40],
        )
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
