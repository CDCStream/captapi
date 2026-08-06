"""Native TikTok Commercial Content Library (EU DSA / library.tiktok.com).

Search prefers Decodo headless capture of ``/api/v1/search`` XHRs (page size
server-capped at 12). Pagination clicks the library's load control until the
candidate pool reaches ``limit`` or upstream stops. Direct JSON POSTs from our
exits are chronically HTTP 421 ``system busy``.
"""

from __future__ import annotations

import asyncio
import json
import math
import re
import time
from typing import Any, Literal
from urllib.parse import quote

import httpx
import structlog

from app.services.http_fetch import DEFAULT_HEADERS, proxy_for
from app.services.tiktok_creative_center import (
    normalize_match_mode as _cc_normalize_match_mode,
)
from app.services.tiktok_creative_center import query_tokens, token_in_haystack
from app.utils.media_urls import cdn_expires_at

log = structlog.get_logger(__name__)

_BASE = "https://library.tiktok.com"
_HEADERS = {
    **DEFAULT_HEADERS,
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": _BASE,
    "Referer": f"{_BASE}/",
}

MatchMode = Literal["any", "all"]

# Decodo scrape budget for SERP pagination / detail XHR.
DECODO_TIMEOUT_SECONDS = 75.0
SEARCH_XHR_FILTER = "api/v1/search"
# Hard ceiling for load-more clicks (12 ads/page). Higher caps grow the pool for
# large ``limit``; Decodo sessions typically top out near ~60–100 unique ads.
_MAX_LOAD_CLICKS = 14


def normalize_match_mode(match: str | None) -> MatchMode:
    return _cc_normalize_match_mode(match)


def _looks_like_id(value: Any) -> bool:
    """True for long digit strings (biz ids / sponsor ids — never display names)."""
    s = str(value or "").strip()
    return bool(re.fullmatch(r"\d{10,}", s))


def _human_advertiser_name(*candidates: Any) -> str | None:
    """First human-readable advertiser label; reject bare numeric ids."""
    for cand in candidates:
        if cand is None:
            continue
        s = str(cand).strip()
        if not s or _looks_like_id(s):
            continue
        if s.lower() in {"not mention", "n/a", "unknown", "advertiser", "ad paid for by"}:
            continue
        return s
    return None


def _ms_to_iso(value: Any) -> str | None:
    """Unix ms / sec → calendar-day ISO-8601 UTC, or pass through date strings.

    DSA content dates are day-granularity. Emitting wall-clock scrape/serve times
    into firstShown/lastShown fabricates run dates — always midnight UTC.
    """
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        n = float(value)
        if n > 1e12:
            n = n / 1000.0
        if n < 1_000_000_000:
            return None
        from datetime import datetime, timezone

        return datetime.fromtimestamp(n, tz=timezone.utc).strftime("%Y-%m-%dT00:00:00.000Z")
    raw = str(value).strip()
    if not raw:
        return None
    if raw.isdigit():
        return _ms_to_iso(int(raw))
    return raw


def _media_objects(*sources: Any) -> list[dict[str, Any]]:
    """Build typed media[] from URL strings / video dicts. Signed CDN → expiresAt."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []

    def add(url: str | None, *, typ: str | None = None) -> None:
        u = (url or "").strip()
        if not u.startswith("http") or u in seen:
            return
        if "gtm" in u or "slardar" in u or "privacy" in u:
            return
        seen.add(u)
        low = u.lower()
        inferred = typ
        if inferred is None:
            if "video" in low or "/cdn/" in low or "mime_type=video" in low:
                inferred = "video/mp4"
            elif any(ext in low for ext in (".jpg", ".jpeg", ".png", ".webp")):
                inferred = "image/jpeg"
            else:
                inferred = "image/jpeg"
        item: dict[str, Any] = {
            "url": u,
            "type": inferred,
            "width": None,
            "height": None,
            "durationSeconds": None,
        }
        exp = cdn_expires_at(u)
        if not exp:
            # library.tiktok.com/api/v1/cdn/{unix}/video/... embeds expiry in path.
            m = re.search(r"/api/v1/cdn/(\d{10})/", u)
            if m:
                exp = _ms_to_iso(int(m.group(1)))
        if exp:
            item["expiresAt"] = exp
        out.append(item)

    for src in sources:
        if isinstance(src, str):
            add(src)
        elif isinstance(src, dict):
            add(src.get("video_url") or src.get("url"), typ="video/mp4")
            add(src.get("cover_img") or src.get("cover"))
        elif isinstance(src, list):
            for item in src:
                if isinstance(item, str):
                    add(item)
                elif isinstance(item, dict):
                    add(item.get("video_url") or item.get("url"), typ="video/mp4")
                    add(item.get("cover_img") or item.get("cover") or item.get("image_url"))
    return out


def _spend_value(raw: Any) -> str | None:
    if raw is None or raw == "" or raw == 0 or raw == "0":
        return None
    text = str(raw).strip()
    return text or None


def _impressions_value(row: dict[str, Any]) -> str | None:
    for key in (
        "estimated_audience",
        "estimatedAudience",
        "impressions",
        "uniqueUsersSeen",
    ):
        val = row.get(key)
        if val is None or val == "" or val == 0 or val == "0":
            continue
        text = str(val).strip()
        if text and text not in {"0", "0-0"}:
            return text
    # Numeric impression field is usually 0 when band is in estimated_audience.
    return None


def _to_normalize_shape(row: dict[str, Any]) -> dict[str, Any]:
    """Map SERP / detail JSON into the shape ``_normalize_ad`` expects."""
    ad_id = str(row.get("ad_id") or row.get("id") or "").strip()
    advertiser = row.get("advertiser") if isinstance(row.get("advertiser"), dict) else {}
    sponsor = advertiser.get("sponsor") or row.get("sponsor")
    biz_ids = advertiser.get("adv_biz_ids") or row.get("advertiser_id")
    if isinstance(biz_ids, str) and biz_ids.strip() in {"", "0"}:
        biz_ids = None
    if _looks_like_id(biz_ids):
        biz_ids = str(biz_ids).strip()
    elif biz_ids is not None:
        # Non-digit biz ids are not usable as advertiser.id.
        biz_ids = str(biz_ids).strip() or None
    tt_user = advertiser.get("tt_user")
    adv_url = None
    handle = None
    if isinstance(tt_user, dict):
        handle = tt_user.get("unique_id") or tt_user.get("username") or tt_user.get("nickname")
        if handle and not _looks_like_id(handle):
            adv_url = f"https://www.tiktok.com/@{handle}"
        if not biz_ids:
            uid = tt_user.get("id") or tt_user.get("uid")
            if _looks_like_id(uid):
                biz_ids = str(uid).strip()
    elif isinstance(tt_user, str) and tt_user.startswith("http"):
        adv_url = tt_user
    # Never fall through to numeric sponsor ids — that regressed advertiser.name
    # to a second biz id (e.g. sponsor 7510870833… while adv_biz_ids is different).
    name = _human_advertiser_name(
        handle,
        row.get("advertiser_name"),
        advertiser.get("name"),
        row.get("name"),
        row.get("brand_name"),
        sponsor,
    )

    videos = row.get("videos") if isinstance(row.get("videos"), list) else []
    image_urls = row.get("image_urls") if isinstance(row.get("image_urls"), list) else []
    media = _media_objects(videos, image_urls, row.get("video_url"), row.get("media"))

    video_url = None
    for m in media:
        if str(m.get("type") or "").startswith("video"):
            video_url = m.get("url")
            break

    caption = (
        row.get("ad_text")
        or row.get("adText")
        or row.get("caption")
        or row.get("text")
        or row.get("body")
        or row.get("title")
    )
    first = _ms_to_iso(row.get("first_shown_date") or row.get("firstShownDate"))
    last = _ms_to_iso(row.get("last_shown_date") or row.get("lastShownDate"))
    impressions = _impressions_value(row)
    spend = _spend_value(row.get("spent") if "spent" in row else row.get("spend"))

    out: dict[str, Any] = {
        "adId": ad_id,
        "id": ad_id,
        "advertiserName": name,
        "advertiserId": biz_ids or row.get("advertiserId"),
        "advertiserUrl": adv_url or row.get("advertiser_url") or advertiser.get("url"),
        "advertiserLocation": advertiser.get("registry_location")
        or row.get("advertiserLocation"),
        # Only keep human payer labels — numeric sponsor ids must not reach
        # ``_normalize_ad``'s advertiser coercion path.
        "payer": sponsor if not _looks_like_id(sponsor) else None,
        "cta": row.get("call_to_action")
        or row.get("cta")
        or row.get("cta_text")
        or row.get("ctaText"),
        "landingUrl": row.get("external_url")
        or row.get("landing_url")
        or row.get("landingUrl")
        or row.get("destination_url")
        or row.get("click_url"),
        # Never use advertiser ``name`` as headline — SERP puts the brand in ``name``.
        "headline": row.get("headline") or row.get("title"),
        "adFormat": "video" if video_url else (row.get("ad_format") or row.get("format") or "image"),
        "first_shown_date": first,
        "last_shown_date": last,
        "imageUrls": [m["url"] for m in media if not str(m.get("type") or "").startswith("video")],
        "videoUrl": video_url,
        "media": media,
        "estimatedAudience": impressions,
        "impressions": impressions,
        "text": caption,
        "body": caption,
        "url": f"https://library.tiktok.com/ads/detail/?ad_id={ad_id}" if ad_id else None,
        "library": "dsa",
    }
    if spend is not None:
        out["spend"] = spend
    # Targeting countries (detail payload) — echo as country hint when single.
    targeting = row.get("targeting") if isinstance(row.get("targeting"), dict) else {}
    countries = targeting.get("countries") if isinstance(targeting, dict) else None
    if isinstance(countries, list) and len(countries) == 1:
        out["country"] = countries[0]
    loc = targeting.get("location") if isinstance(targeting, dict) else None
    if isinstance(loc, dict) and not impressions:
        band = loc.get("total_impressions")
        if band:
            out["impressions"] = str(band)
            out["estimatedAudience"] = str(band)
    return out


def ad_matches_query(
    row: dict[str, Any],
    q: str,
    *,
    match: MatchMode = "any",
) -> bool:
    """Whole-word token match on advertiser / copy fields (hair ≠ wheelchair)."""
    tokens = query_tokens(q)
    if not tokens:
        return True
    adv = row.get("advertiser") if isinstance(row.get("advertiser"), dict) else {}
    hay_parts = [
        row.get("advertiserName"),
        row.get("advertiser_name"),
        row.get("brand_name"),
        row.get("name"),
        row.get("payer"),
        row.get("text"),
        row.get("body"),
        row.get("caption"),
        row.get("headline"),
        row.get("title"),
        row.get("cta"),
        row.get("landingUrl"),
        adv.get("name"),
        adv.get("business_name"),
        adv.get("sponsor"),
    ]
    hay = " ".join(str(p) for p in hay_parts if p).lower()
    if not hay.strip():
        # No copy yet — keep for optional detail enrich, filter again later.
        return True
    if match == "all":
        return all(token_in_haystack(t, hay) for t in tokens)
    return any(token_in_haystack(t, hay) for t in tokens)


def matched_from_fields(ad: dict[str, Any], q: str | None) -> list[str]:
    """Public field names where ``q`` tokens hit (per-ad provenance)."""
    tokens = query_tokens(q)
    if not tokens or not isinstance(ad, dict):
        return []
    adv = ad.get("advertiser") if isinstance(ad.get("advertiser"), dict) else {}
    fields: list[tuple[str, str]] = [
        ("text", (str(ad.get("text") or "")).lower()),
        ("headline", (str(ad.get("headline") or "")).lower()),
        ("cta", (str(ad.get("cta") or "")).lower()),
        ("landingUrl", (str(ad.get("landingUrl") or "")).lower()),
        (
            "advertiser.name",
            (
                str(
                    (adv.get("name") if adv else None)
                    or ad.get("advertiserName")
                    or ""
                )
            ).lower(),
        ),
    ]
    hits: list[str] = []
    for name, hay in fields:
        if hay and any(token_in_haystack(t, hay) for t in tokens):
            hits.append(name)
    return hits


def filter_ads_by_query(
    rows: list[dict[str, Any]],
    q: str,
    *,
    match: MatchMode = "any",
) -> dict[str, Any]:
    """Apply local whole-word filter; return rows + match transparency fields."""
    scanned = len(rows)
    if not (q or "").strip():
        return {
            "rows": list(rows),
            "candidatesScanned": scanned,
            "matchedFrom": scanned,  # legacy alias
            "filteredOut": 0,
            "literalMatches": scanned,
            "match": match,
            "matchBasis": "none",
        }
    kept: list[dict[str, Any]] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        # Drop empty-copy stubs at filter time (they would match vacuously).
        hay_probe = " ".join(
            str(p)
            for p in (
                r.get("advertiserName"),
                r.get("name"),
                r.get("text"),
                r.get("body"),
                r.get("headline"),
                r.get("title"),
                r.get("cta"),
                r.get("payer"),
            )
            if p
        ).strip()
        if not hay_probe:
            continue
        if ad_matches_query(r, q, match=match):
            kept.append(r)
    return {
        "rows": kept,
        "candidatesScanned": scanned,
        "matchedFrom": scanned,
        "filteredOut": scanned - len(kept),
        "literalMatches": len(kept),
        "match": match,
        "matchBasis": match,
    }


def re_soft_limit(text: str) -> bool:
    return bool(text) and (not text.lstrip().startswith("{")) and (
        "limit" in text.lower() or "busy" in text.lower() or "exceed" in text.lower()
    )


async def _post_search(
    query: str,
    *,
    region: str,
    limit: int,
    proxy: str | None,
    days: int = 30,
    offset: int = 0,
    search_id: str | None = None,
) -> dict[str, Any] | None:
    """One JSON page. Returns ``{rows, has_more, search_id, total}`` or None."""
    end = int(time.time())
    start = end - max(1, days) * 24 * 3600
    url = (
        f"{_BASE}/api/v1/search"
        f"?region={region.upper()}&type=1&start_time={start}&end_time={end}"
    )
    body: dict[str, Any] = {
        "query": query,
        "query_type": "3",
        "order": "last_shown_date,desc",
        "offset": max(0, int(offset)),
        "limit": min(max(1, limit), 12),
    }
    if search_id:
        body["search_id"] = search_id
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
    code = payload.get("code")
    if code not in (None, 0, "0"):
        log.warning("tiktok_ads_native_code", code=code, proxy=bool(proxy))
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    return {
        "rows": [_to_normalize_shape(r) for r in data if isinstance(r, dict)],
        "has_more": bool(payload.get("has_more")),
        "search_id": payload.get("search_id"),
        "total": payload.get("total"),
    }


def _parse_search_xhr_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
    """Merge unique ads from captured ``/api/v1/search`` XHRs."""
    by_id: dict[str, dict[str, Any]] = {}
    has_more = False
    for item in items:
        u = str(item.get("url") or "")
        if "/api/v1/search" not in u:
            continue
        raw = item.get("response_body")
        if isinstance(raw, str):
            try:
                body = json.loads(raw)
            except ValueError:
                continue
        elif isinstance(raw, dict):
            body = raw
        else:
            continue
        if not isinstance(body, dict):
            continue
        if body.get("has_more"):
            has_more = True
        for row in body.get("data") or []:
            if not isinstance(row, dict):
                continue
            shaped = _to_normalize_shape(row)
            aid = str(shaped.get("id") or "")
            if aid:
                by_id[aid] = shaped
    return list(by_id.values()), has_more


async def search_ads_via_decodo(
    q: str, *, country: str = "GB", limit: int = 20
) -> dict[str, Any] | None:
    """Paginated DSA search via Decodo XHR + load-more clicks.

    Returns ``{rows, has_more, truncated}`` or ``None`` when Decodo fails.
    """
    from app.services import decodo_fetch

    query = (q or "").strip()
    if len(query) < 2 or not decodo_fetch.enabled():
        return None
    region = (country or "GB").upper()
    want = max(1, min(int(limit), 200))
    url = f"{_BASE}/ads?region={region}&query={quote(query, safe='')}"

    async def _first_page() -> dict[str, Any] | None:
        got = await decodo_fetch.fetch_url(
            url,
            timeout=DECODO_TIMEOUT_SECONDS,
            target="universal",
            headless="html",
            geo=region if len(region) == 2 and region.isalpha() else "GB",
            browser_actions=[
                {
                    "type": "fetch_resource",
                    "filter": SEARCH_XHR_FILTER,
                    "on_error": "error",
                }
            ],
        )
        if not got:
            return None
        _status, content = got
        try:
            body = json.loads(content) if isinstance(content, str) else None
        except ValueError:
            return None
        if not isinstance(body, dict) or body.get("code") not in (None, 0, "0"):
            return None
        data = body.get("data") if isinstance(body.get("data"), list) else []
        rows = [_to_normalize_shape(r) for r in data if isinstance(r, dict)]
        return {
            "rows": rows,
            "has_more": bool(body.get("has_more")),
        }

    # Fast path: first page only (fetch_resource early-exit — ~10–15s).
    if want <= 12:
        page1 = await _first_page()
        if not page1:
            return None
        rows = page1["rows"]
        has_more = bool(page1.get("has_more"))
        log.info(
            "tiktok_ads_native_decodo_search_ok",
            count=len(rows),
            q=query[:40],
            region=region,
            mode="fetch_resource",
        )
        return {
            "rows": rows[:want],
            "has_more": has_more,
            "truncated": has_more and len(rows) >= want,
        }

    # Paginate: scroll + click ``[class*='load']`` until pool >= want.
    # ~12 ads per page; keep click count / waits tight so limit=50 stays <30s.
    clicks = min(_MAX_LOAD_CLICKS, max(0, math.ceil((want - 12) / 12)))
    if clicks == 0:
        clicks = 1  # at least one load-more attempt when want > 12
    actions: list[dict[str, Any]] = [{"type": "wait", "wait_time_s": 2}]
    for _ in range(clicks):
        actions.extend(
            [
                {"type": "scroll", "x": "0", "y": "2200"},
                {
                    "type": "click",
                    "selector": {"type": "css", "value": "[class*='load']"},
                    "on_error": "skip",
                },
                {"type": "wait", "wait_time_s": 2},
            ]
        )
    # Timeout scales with clicks but stays under hard deadline headroom.
    timeout = min(100.0, 30.0 + clicks * 3.5)
    got = None
    for attempt in range(2):
        got = await decodo_fetch.fetch_xhr(
            url,
            timeout=timeout,
            target="universal",
            headless="html",
            geo=region if len(region) == 2 and region.isalpha() else "GB",
            browser_actions=actions,
        )
        if got:
            break
        log.warning(
            "tiktok_ads_native_decodo_search_retry",
            attempt=attempt + 1,
            q=query[:40],
            region=region,
        )
    if not got:
        # Fall back to first-page early-exit so large limits still return a pool.
        page1 = await _first_page()
        if not page1 or not page1.get("rows"):
            return None
        rows = page1["rows"]
        has_more = bool(page1.get("has_more"))
        log.info(
            "tiktok_ads_native_decodo_search_ok",
            count=len(rows),
            q=query[:40],
            region=region,
            mode="fetch_resource_fallback",
        )
        return {
            "rows": rows,
            "has_more": has_more,
            "truncated": has_more,
        }
    _status, items = got
    rows, has_more = _parse_search_xhr_items(items)
    if not rows:
        return None
    log.info(
        "tiktok_ads_native_decodo_search_ok",
        count=len(rows),
        q=query[:40],
        region=region,
        mode="xhr_paginate",
        clicks=clicks,
    )
    truncated = len(rows) >= want and has_more
    return {
        "rows": rows[: max(want, min(len(rows), 200))],
        "has_more": has_more,
        "truncated": truncated,
    }


async def _enrich_via_details(
    rows: list[dict[str, Any]],
    *,
    country: str,
    concurrency: int = 4,
    max_enrich: int = 24,
) -> list[dict[str, Any]]:
    """Fill title/cta/landing/advertiser from ``items/{id}/details`` for a subset."""
    if not rows:
        return rows
    sem = asyncio.Semaphore(max(1, min(concurrency, 5)))
    targets = rows[:max_enrich]

    async def _one(row: dict[str, Any]) -> dict[str, Any]:
        aid = str(row.get("id") or row.get("adId") or "").strip()
        if not aid.isdigit():
            return row
        async with sem:
            detail = await ad_details(aid, country=country)
        if not detail:
            return row
        out = dict(row)
        for key, val in detail.items():
            if key == "library":
                continue
            if val in (None, "", [], {}) and out.get(key) not in (None, "", [], {}):
                continue
            if out.get(key) in (None, "", [], {}) and val not in (None, "", [], {}):
                out[key] = val
            elif key in ("media", "text", "body", "headline", "cta", "landingUrl", "spend", "impressions"):
                if val not in (None, "", [], {}):
                    out[key] = val
        return out

    enriched = list(await asyncio.gather(*[_one(r) for r in targets]))
    return enriched + rows[max_enrich:]


async def search_ads(
    q: str, *, country: str = "GB", limit: int = 20
) -> dict[str, Any] | None:
    """Search TikTok Commercial Content Library (EU DSA).

    Returns a filter-ready dict ``{rows, has_more, truncated}`` or ``None`` when
    every native path fails (caller may fall back to Apify).
    """
    query = (q or "").strip()
    if len(query) < 2:
        return {"rows": [], "has_more": False, "truncated": False}

    region = (country or "GB").upper()
    want = max(1, int(limit))
    # Over-fetch SERP candidates for local whole-word filtering (keep modest for latency).
    serp_limit = min(200, max(want * 2, want))

    decodo = await search_ads_via_decodo(query, country=region, limit=serp_limit)
    if decodo is not None:
        rows = list(decodo.get("rows") or [])
        # Do not hydrate every SERP row here — that was the 100s+ path. Filter on
        # SERP fields (advertiser name / sponsor); callers may enrich hits only.
        for r in rows:
            if isinstance(r, dict) and not r.get("country"):
                r["country"] = region
        return {
            "rows": rows,
            "has_more": bool(decodo.get("has_more")),
            "truncated": bool(decodo.get("truncated")),
        }

    # JSON API secondary (cheap when TikTok stops returning 421).
    tiers: list[tuple[str, str | None]] = [
        ("datacenter", proxy_for("datacenter")),
        ("residential", proxy_for("residential")),
        ("direct", None),
    ]
    collected: list[dict[str, Any]] = []
    has_more = False
    search_id: str | None = None
    for tier, proxy in tiers:
        if tier != "direct" and not proxy:
            continue
        offset = 0
        search_id = None
        collected = []
        while len(collected) < serp_limit:
            page = await _post_search(
                query,
                region=region,
                limit=12,
                proxy=proxy,
                offset=offset,
                search_id=search_id,
            )
            if page is None:
                collected = []
                break
            batch = page["rows"]
            if not batch:
                has_more = False
                break
            collected.extend(batch)
            has_more = bool(page.get("has_more"))
            search_id = page.get("search_id") or search_id
            offset += len(batch)
            if not has_more:
                break
        if collected:
            log.info(
                "tiktok_ads_native_search_ok",
                tier=tier,
                count=len(collected),
                q=query[:40],
                region=region,
            )
            for r in collected:
                r["country"] = region
            return {
                "rows": collected[:serp_limit],
                "has_more": has_more,
                "truncated": has_more and len(collected) >= want,
            }

    return None


def detail_url(ad_id: str, *, region: str = "GB") -> str:
    aid = (ad_id or "").strip()
    reg = (region or "GB").upper()
    return f"https://library.tiktok.com/ads/detail/?ad_id={aid}&region={reg}"


def _label_value(html: str, label: str) -> str | None:
    patterns = [
        rf"{re.escape(label)}[:\s]*</[^>]+>\s*<[^>]+>([^<]{{2,200}})",
        rf"{re.escape(label)}[:\s]*</[^>]+>\s*([^<]{{2,200}})",
        rf"{re.escape(label)}\s*</[^>]+>\s*<[^>]+>([^<]{{2,200}})",
    ]
    for pat in patterns:
        m = re.search(pat, html or "", re.I)
        if m:
            text = re.sub(r"\s+", " ", m.group(1)).strip()
            if text:
                return text
    return None


def _metric_from_text_nodes(html: str, label: str) -> str | None:
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
    m = _CAPTION_RE.search(html or "")
    if m:
        text = re.sub(r"\s+", " ", m.group(1)).strip()
        if text and text not in {"-", "N/A", "n/a"}:
            return text
    return _first_label(html or "", "Ad caption")


def extract_ad_details(html: str, *, ad_id: str) -> dict[str, Any] | None:
    """Parse hydrated library.tiktok.com detail HTML (fallback)."""
    if not html or not ad_id:
        return None
    if ad_id not in html and f"Ad ID" not in html:
        return None

    advertiser = _first_label(html, "Advertiser")
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
        r'"external_url"\s*:\s*"(https?://[^"]+)"',
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
        r'"adv_biz_ids"\s*:\s*"?(\d{5,})"?',
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

    media_urls: list[str] = []
    for src in re.findall(
        r'(?:src|poster|data-src)="(https://[^"]+(?:tiktokcdn|byteoversea|ibyteimg|library\.tiktok\.com/api/v1/cdn)[^"]*)"',
        html,
        re.I,
    ):
        u = src.replace("&amp;", "&")
        if u not in media_urls:
            media_urls.append(u)
    if video_url and video_url not in media_urls:
        media_urls.insert(0, video_url)

    if not any([advertiser, paid_by, video_url, media_urls, first_shown]):
        return None

    media = _media_objects(
        [{"video_url": video_url}] if video_url else [],
        media_urls,
    )
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
        "imageUrls": [m["url"] for m in media if not str(m.get("type") or "").startswith("video")],
        "videoUrl": video_url,
        "media": media,
        "url": f"https://library.tiktok.com/ads/detail/?ad_id={ad_id}",
        "library": "dsa",
    }


def extract_ad_details_json(payload: dict[str, Any], *, ad_id: str) -> dict[str, Any] | None:
    """Map ``/api/v1/items/{id}/details`` JSON into normalize shape."""
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return None
    ad = data.get("ad") if isinstance(data.get("ad"), dict) else {}
    advertiser = data.get("advertiser") if isinstance(data.get("advertiser"), dict) else {}
    targeting = data.get("targeting") if isinstance(data.get("targeting"), dict) else {}
    if not ad and not advertiser:
        return None
    merged = {
        **ad,
        "id": ad.get("id") or ad_id,
        "advertiser": advertiser,
        "targeting": targeting,
    }
    # Prefer advertiser.name over empty ad.name
    if not (merged.get("name") or "").strip() and advertiser.get("name"):
        merged["name"] = advertiser.get("name")
    shaped = _to_normalize_shape(merged)
    # Headline: prefer title; don't use empty ad.name
    title = ad.get("title")
    if title:
        shaped["headline"] = title
        if not shaped.get("text"):
            shaped["text"] = title
            shaped["body"] = title
    shaped["library"] = "dsa"
    return shaped


async def ad_details(ad_id: str, *, country: str = "GB") -> dict[str, Any] | None:
    """Fetch one Commercial Content Library ad via Decodo details XHR."""
    from app.services import decodo_fetch

    aid = (ad_id or "").strip()
    if not aid.isdigit() or not decodo_fetch.enabled():
        return None
    region = (country or "GB").upper()
    url = detail_url(aid, region=region)

    got = await decodo_fetch.fetch_url(
        url,
        timeout=DECODO_TIMEOUT_SECONDS,
        target="universal",
        headless="html",
        geo=region if len(region) == 2 and region.isalpha() else "GB",
        browser_actions=[
            {
                "type": "fetch_resource",
                "filter": f"items/{aid}/details",
                "on_error": "error",
            }
        ],
    )
    if got:
        status, content = got
        if status == 200 and isinstance(content, str) and content.lstrip().startswith("{"):
            try:
                payload = json.loads(content)
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                row = extract_ad_details_json(payload, ad_id=aid)
                if row:
                    row["country"] = region
                    log.info("tiktok_ads_native_detail_ok", ad_id=aid, mode="xhr")
                    return row

    # HTML fallback
    got_html = await decodo_fetch.fetch_url(
        url, timeout=DECODO_TIMEOUT_SECONDS, headless="html", geo=region
    )
    if not got_html:
        return None
    status, html = got_html
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
    row["country"] = region
    log.info("tiktok_ads_native_detail_ok", ad_id=aid, mode="html")
    return row
