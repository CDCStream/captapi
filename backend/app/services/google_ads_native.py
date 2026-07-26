"""Native Google Ads Transparency Center helpers (no Apify).

Hits Google's public SearchSuggestions + SearchCreatives RPCs used by
adstransparency.google.com. Cost is proxy bandwidth only; cascades
datacenter -> residential -> direct.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import httpx
import structlog

from app.services.http_fetch import DEFAULT_HEADERS, proxy_for

log = structlog.get_logger(__name__)

_SUGGESTIONS_URL = (
    "https://adstransparency.google.com/anji/_/rpc/"
    "SearchService/SearchSuggestions?authuser=0"
)
_CREATIVES_URL = (
    "https://adstransparency.google.com/anji/_/rpc/"
    "SearchService/SearchCreatives?authuser=0"
)

# ISO 3166-1 alpha-2 → numeric. ATC region filter uses 2000 + numeric code.
_ISO_NUMERIC: dict[str, int] = {
    "US": 840,
    "GB": 826,
    "UK": 826,
    "DE": 276,
    "FR": 250,
    "IT": 380,
    "ES": 724,
    "NL": 528,
    "BE": 56,
    "AT": 40,
    "CH": 756,
    "SE": 752,
    "NO": 578,
    "DK": 208,
    "FI": 246,
    "IE": 372,
    "PT": 620,
    "PL": 616,
    "CZ": 203,
    "HU": 348,
    "RO": 642,
    "BG": 100,
    "GR": 300,
    "TR": 792,
    "CA": 124,
    "MX": 484,
    "BR": 76,
    "AR": 32,
    "AU": 36,
    "NZ": 554,
    "JP": 392,
    "KR": 410,
    "IN": 356,
    "ID": 360,
    "SG": 702,
    "MY": 458,
    "TH": 764,
    "PH": 608,
    "VN": 704,
    "AE": 784,
    "SA": 682,
    "IL": 376,
    "ZA": 710,
}

_RPC_HEADERS = {
    **DEFAULT_HEADERS,
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Origin": "https://adstransparency.google.com",
    "Referer": "https://adstransparency.google.com/",
    "Accept": "*/*",
}


def _ads_count(raw: Any) -> int | None:
    if not isinstance(raw, dict):
        return None
    # Shape seen in production: {"2": {"1": "9", "2": "9"}}
    nested = raw.get("2") if isinstance(raw.get("2"), dict) else raw
    for key in ("2", "1"):
        val = nested.get(key) if isinstance(nested, dict) else None
        if val is None:
            continue
        try:
            return int(str(val).replace(",", "").strip())
        except (TypeError, ValueError):
            continue
    return None


def _parse_suggestions(payload: Any, *, limit: int, country: str | None) -> list[dict[str, Any]]:
    rows = payload.get("1") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return []

    parsed: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = row.get("1") if isinstance(row.get("1"), dict) else row
        if not isinstance(item, dict):
            continue
        adv_id = str(item.get("2") or "").strip()
        name = str(item.get("1") or "").strip()
        if not adv_id.startswith("AR") or not name:
            continue
        region = str(item.get("3") or "").strip().upper() or None
        ads_count = _ads_count(item.get("4"))
        entry: dict[str, Any] = {
            "id": adv_id,
            "name": name,
            "url": f"https://adstransparency.google.com/advertiser/{adv_id}",
        }
        if region:
            entry["country"] = region
        if ads_count is not None:
            entry["adsCount"] = ads_count
        parsed.append(entry)

    want = (country or "").strip().upper()
    if want and want not in {"ANY", "ANYWHERE", "ALL"}:
        preferred = [a for a in parsed if a.get("country") == want]
        others = [a for a in parsed if a.get("country") != want]
        parsed = preferred + others

    # Dedupe by advertiser id, keep first (preferred region first).
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for adv in parsed:
        aid = adv["id"]
        if aid in seen:
            continue
        seen.add(aid)
        out.append(adv)
        if len(out) >= limit:
            break
    return out


async def _post_suggestions(query: str, limit: int, proxy: str | None) -> dict[str, Any] | None:
    # Field 2/3 are result counts Google's UI sends as integers.
    n = max(1, min(int(limit), 50))
    body = "f.req=" + quote(
        json.dumps({"1": query, "2": n, "3": n}, separators=(",", ":")),
        safe="",
    )
    try:
        async with httpx.AsyncClient(
            timeout=12.0,
            follow_redirects=True,
            headers=_RPC_HEADERS,
            proxy=proxy,
        ) as client:
            resp = await client.post(_SUGGESTIONS_URL, content=body)
    except httpx.HTTPError as exc:
        log.warning("google_ads_suggestions_transport", error=str(exc), proxy=bool(proxy))
        return None

    if resp.status_code == 429:
        log.warning("google_ads_suggestions_rate_limited", proxy=bool(proxy))
        return None
    if resp.status_code >= 400:
        log.warning(
            "google_ads_suggestions_http",
            status=resp.status_code,
            proxy=bool(proxy),
            body=resp.text[:200],
        )
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    if not isinstance(payload, dict) or "1" not in payload:
        return None
    return payload


async def search_advertisers(
    query: str,
    *,
    country: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]] | None:
    """Search advertisers via Google ATC SearchSuggestions.

    Returns a list of ``{id, name, url, country?, adsCount?}`` or ``None`` when
    every transport tier fails (caller should fall back to Apify).
    """
    q = (query or "").strip()
    if len(q) < 2:
        return []

    tiers: list[tuple[str, str | None]] = [
        ("datacenter", proxy_for("datacenter")),
        ("residential", proxy_for("residential")),
        ("direct", None),
    ]
    # Skip duplicate None proxies.
    seen_proxy: set[str | None] = set()
    for tier, proxy in tiers:
        if proxy in seen_proxy and proxy is not None:
            continue
        if proxy is None and tier != "direct":
            continue
        seen_proxy.add(proxy)
        payload = await _post_suggestions(q, limit, proxy)
        if payload is None:
            continue
        rows = _parse_suggestions(payload, limit=limit, country=country)
        if rows:
            log.info("google_ads_suggestions_ok", tier=tier, count=len(rows), q=q[:40])
            return rows
        # Empty but valid response — still a success (no matches).
        if isinstance(payload, dict) and "1" in payload:
            return []
    return None


def _proxy_tiers() -> list[tuple[str, str | None]]:
    tiers: list[tuple[str, str | None]] = [
        ("datacenter", proxy_for("datacenter")),
        ("residential", proxy_for("residential")),
        ("direct", None),
    ]
    out: list[tuple[str, str | None]] = []
    seen: set[str | None] = set()
    for tier, proxy in tiers:
        if proxy is None and tier != "direct":
            continue
        if proxy in seen and proxy is not None:
            continue
        seen.add(proxy)
        out.append((tier, proxy))
    return out


def _looks_like_domain(value: str) -> bool:
    v = value.strip().lower()
    if " " in v or v.startswith("ar"):
        return False
    return "." in v and re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", v.removeprefix("www.")) is not None


def _brand_from_query(value: str) -> str:
    v = value.strip()
    if _looks_like_domain(v):
        host = v.lower().removeprefix("https://").removeprefix("http://").removeprefix("www.")
        host = host.split("/")[0]
        return host.split(".")[0]
    return v


def _region_enums(country: str | None) -> list[int] | None:
    code = (country or "").strip().upper()
    if not code or code in {"ANY", "ANYWHERE", "ALL"}:
        return None
    num = _ISO_NUMERIC.get(code)
    if num is None:
        return None
    return [2000 + num]


def _ts_iso(node: Any) -> str | None:
    if not isinstance(node, dict):
        return None
    raw = node.get("1")
    if raw in (None, "", 0, "0"):
        return None
    try:
        ts = int(raw)
    except (TypeError, ValueError):
        return None
    if ts > 10_000_000_000:
        ts //= 1000
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _extract_urls(blob: str) -> list[str]:
    found = re.findall(r"https://[^\s\\\"'<>]+", blob)
    out: list[str] = []
    seen: set[str] = set()
    for url in found:
        url = url.rstrip("\\").rstrip(")")
        if "googlesyndication.com" not in url and "googleusercontent.com" not in url:
            # Keep tpc creatives; skip random preview JS unless no other media.
            if "displayads-formats" in url:
                continue
            continue
        if "simgad" in url or "/archive/" in url or url.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            if url not in seen:
                seen.add(url)
                out.append(url)
    return out


def _creative_format(row: dict[str, Any], media: list[str], html: str) -> str:
    kind = row.get("13")
    if kind == 7 or media:
        return "image"
    if kind == 42 or "video" in html.lower() or ".mp4" in html.lower():
        return "video" if ("video" in html.lower() or ".mp4" in html.lower()) else "display"
    return "text"


def _to_normalize_shape(row: dict[str, Any]) -> dict[str, Any] | None:
    adv_id = str(row.get("1") or "").strip()
    creative_id = str(row.get("2") or "").strip()
    if not creative_id.startswith("CR"):
        return None
    if not adv_id.startswith("AR"):
        adv_id = ""
    html = json.dumps(row.get("3") or {}, ensure_ascii=False)
    media = _extract_urls(html)
    name = str(row.get("12") or "").strip() or None
    return {
        "creativeId": creative_id,
        "adCreativeId": creative_id,
        "id": creative_id,
        "advertiserId": adv_id or None,
        "advertiserName": name,
        "advertiserUrl": (
            f"https://adstransparency.google.com/advertiser/{adv_id}" if adv_id else None
        ),
        "url": (
            f"https://adstransparency.google.com/advertiser/{adv_id}/creative/{creative_id}"
            if adv_id
            else f"https://adstransparency.google.com/creative/{creative_id}"
        ),
        "adFormat": _creative_format(row, media, html),
        "firstShown": _ts_iso(row.get("6")),
        "lastShown": _ts_iso(row.get("7")),
        "imageUrls": media,
        "media": media,
    }


def _rank_advertisers(
    rows: list[dict[str, Any]], *, query: str, country: str | None
) -> list[dict[str, Any]]:
    brand = _brand_from_query(query).lower()
    q_norm = query.strip().lower().removeprefix("www.")
    want = (country or "").strip().upper()
    corp_re = re.compile(
        r"\b(inc\.?|ltd\.?|llc|gmbh|b\.?v\.?|s\.?r\.?l\.?|corp\.?|company|co\.)\b",
        re.I,
    )
    person_re = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$")

    def score(adv: dict[str, Any]) -> tuple:
        raw_name = adv.get("name") or ""
        name = raw_name.lower()
        ads = int(adv.get("adsCount") or 0)
        exact = 1 if name in {q_norm, brand, f"{brand}, inc."} else 0
        corp = 1 if corp_re.search(raw_name) else 0
        brand_word = 1 if brand and re.search(rf"\b{re.escape(brand)}\b", name) else 0
        starts = 1 if name.startswith(brand) else 0
        contains = 1 if brand and brand in name else 0
        country_hit = 1 if want and adv.get("country") == want else 0
        personish = 1 if person_re.match(raw_name) and not corp else 0
        return (exact, corp, brand_word, starts, contains, country_hit, ads, -personish)

    return sorted(rows, key=score, reverse=True)


async def _post_creatives(
    advertiser_ids: list[str],
    *,
    page_size: int,
    cursor: Any,
    region_enums: list[int] | None,
    proxy: str | None,
) -> dict[str, Any] | None:
    filt: dict[str, Any] = {"13": {"1": advertiser_ids}}
    if region_enums:
        filt["8"] = region_enums
    body: dict[str, Any] = {
        "2": max(1, min(int(page_size), 40)),
        "3": filt,
        "7": {"1": 1},
    }
    if cursor is not None:
        body["4"] = cursor
    payload = "f.req=" + quote(json.dumps(body, separators=(",", ":")), safe="")
    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            headers=_RPC_HEADERS,
            proxy=proxy,
        ) as client:
            resp = await client.post(_CREATIVES_URL, content=payload)
    except httpx.HTTPError as exc:
        log.warning("google_ads_creatives_transport", error=str(exc), proxy=bool(proxy))
        return None
    if resp.status_code == 429:
        log.warning("google_ads_creatives_rate_limited", proxy=bool(proxy))
        return None
    if resp.status_code >= 400:
        log.warning(
            "google_ads_creatives_http",
            status=resp.status_code,
            proxy=bool(proxy),
            body=resp.text[:200],
        )
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


async def resolve_advertiser_ids(
    query: str,
    *,
    country: str | None = None,
    max_ids: int = 3,
) -> list[str] | None:
    """Resolve name/domain/AR id → one or more AR advertiser ids."""
    q = (query or "").strip()
    if not q:
        return []
    if re.fullmatch(r"AR\d+", q, flags=re.I):
        return [q.upper() if q.startswith("AR") else q]

    brand = _brand_from_query(q)
    if _looks_like_domain(q):
        queries = [f"{brand.title()}, Inc.", brand.title(), brand]
    else:
        queries = [q]

    raw: list[dict[str, Any]] | None = None
    merged: dict[str, dict[str, Any]] = {}
    corp_re = re.compile(
        r"\b(inc\.?|ltd\.?|llc|gmbh|b\.?v\.?|s\.?r\.?l\.?|corp\.?|company|co\.)\b",
        re.I,
    )
    for search_q in queries:
        for tier, proxy in _proxy_tiers():
            payload = await _post_suggestions(search_q, 30, proxy)
            if payload is None:
                continue
            parsed = _parse_suggestions(payload, limit=30, country=None)
            for adv in parsed:
                merged.setdefault(adv["id"], adv)
            raw = list(merged.values())
            log.info(
                "google_ads_resolve_suggestions",
                tier=tier,
                count=len(parsed),
                q=search_q[:40],
            )
            break
        # Domains: stop once we have a corporate brand match with volume.
        if raw and _looks_like_domain(q):
            ranked_early = _rank_advertisers(raw, query=q, country=country)
            top = ranked_early[0] if ranked_early else None
            if (
                top
                and corp_re.search(top.get("name") or "")
                and brand.lower() in (top.get("name") or "").lower()
                and int(top.get("adsCount") or 0) >= 50
            ):
                break
    if raw is None:
        return None
    ranked = _rank_advertisers(raw, query=q, country=country)
    ids: list[str] = []
    for adv in ranked:
        aid = adv["id"]
        if aid in ids:
            continue
        ids.append(aid)
        if len(ids) >= max_ids:
            break
    return ids


async def fetch_company_ads(
    advertiser: str,
    *,
    country: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]] | None:
    """Fetch creatives for an advertiser name, domain, or AR id.

    Returns rows shaped for ``_normalize_ad(..., google_ad_library)``, or
    ``None`` when every transport tier fails (caller should fall back to Apify).
    """
    want = max(0, int(limit))
    if want == 0:
        return []

    ids = await resolve_advertiser_ids(advertiser, country=country, max_ids=3)
    if ids is None:
        return None
    if not ids:
        return []

    region_enums = _region_enums(country)
    page_size = min(40, max(want, 10))
    collected: list[dict[str, Any]] = []
    seen: set[str] = set()

    # Try tiers until the first page succeeds; keep that proxy for pagination.
    working: tuple[str, str | None] | None = None
    first_payload: dict[str, Any] | None = None
    for tier, proxy in _proxy_tiers():
        payload = await _post_creatives(
            ids[:1],
            page_size=page_size,
            cursor=None,
            region_enums=region_enums,
            proxy=proxy,
        )
        if payload is None:
            continue
        working = (tier, proxy)
        first_payload = payload
        break

    if working is None or first_payload is None:
        return None

    tier_used, proxy = working

    async def _consume(payload: dict[str, Any], remaining_ids: list[str]) -> Any:
        rows = payload.get("1")
        if not isinstance(rows, list):
            return payload.get("2")
        for row in rows:
            if not isinstance(row, dict):
                continue
            item = _to_normalize_shape(row)
            if not item:
                continue
            cid = item["id"]
            if cid in seen:
                continue
            seen.add(cid)
            collected.append(item)
            if len(collected) >= want:
                return None
        return payload.get("2")

    # Page first advertiser, then fill from additional resolved advertisers.
    cursor = await _consume(first_payload, ids)
    while cursor is not None and len(collected) < want:
        payload = await _post_creatives(
            ids[:1],
            page_size=page_size,
            cursor=cursor,
            region_enums=region_enums,
            proxy=proxy,
        )
        if payload is None:
            break
        cursor = await _consume(payload, ids)
        if cursor is None:
            break

    for extra_id in ids[1:]:
        if len(collected) >= want:
            break
        payload = await _post_creatives(
            [extra_id],
            page_size=min(page_size, want - len(collected)),
            cursor=None,
            region_enums=region_enums,
            proxy=proxy,
        )
        if payload is None:
            continue
        await _consume(payload, [extra_id])

    log.info(
        "google_ads_creatives_ok",
        tier=tier_used,
        count=len(collected),
        advertisers=len(ids),
        q=advertiser[:40],
    )
    return collected[:want]
