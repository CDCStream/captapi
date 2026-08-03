"""Native Google Ads Transparency Center helpers (no Apify).

Hits Google's public SearchSuggestions + SearchCreatives RPCs used by
adstransparency.google.com. Cost is proxy bandwidth only; cascades
datacenter -> residential -> direct.
"""

from __future__ import annotations

import base64
import json
import re
from datetime import date, datetime, timezone
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


def _suggestion_queries(query: str) -> list[str]:
    """Expand a brand/domain query so ATC returns Inc./regional entities, not one SRL.

    Bare ``nike`` often autocompletes only to ``NIKE SRL``; also querying
    ``Nike, Inc.`` / ``Nike`` surfaces the parent entity used by company-ads.
    """
    q = (query or "").strip()
    if not q:
        return []
    if re.fullmatch(r"AR\d+", q, flags=re.I):
        return [q.upper() if q.startswith("AR") else q]
    brand = _brand_from_query(q)
    out: list[str] = []
    for candidate in (q, f"{brand.title()}, Inc.", brand.title(), brand):
        c = (candidate or "").strip()
        if not c:
            continue
        if c.lower() in {x.lower() for x in out}:
            continue
        out.append(c)
    return out


async def _merge_suggestions(
    queries: list[str],
    *,
    per_query: int = 30,
) -> list[dict[str, Any]] | None:
    """Run SearchSuggestions for each query; merge by AR id. None = all tiers failed."""
    merged: dict[str, dict[str, Any]] = {}
    any_ok = False
    for search_q in queries:
        got_page = False
        for tier, proxy in _proxy_tiers():
            payload = await _post_suggestions(search_q, per_query, proxy)
            if payload is None:
                continue
            any_ok = True
            got_page = True
            parsed = _parse_suggestions(payload, limit=per_query, country=None)
            for adv in parsed:
                prev = merged.get(adv["id"])
                if prev is None:
                    merged[adv["id"]] = adv
                else:
                    # Keep richer adsCount / country when a later query has them.
                    if adv.get("adsCount") and not prev.get("adsCount"):
                        prev["adsCount"] = adv["adsCount"]
                    if adv.get("country") and not prev.get("country"):
                        prev["country"] = adv["country"]
            log.info(
                "google_ads_suggestions_ok",
                tier=tier,
                count=len(parsed),
                q=search_q[:40],
            )
            break
        if not got_page and not any_ok:
            continue
    if not any_ok:
        return None
    return list(merged.values())


async def search_advertisers(
    query: str,
    *,
    country: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]] | None:
    """Search advertisers via Google ATC SearchSuggestions.

    Expands brand queries (same family as company-ads resolve) and ranks with
    ``_rank_advertisers`` so ``q=nike&country=US`` returns Nike, Inc. ahead of
    NIKE SRL, plus sibling entities the caller can pick for company-ads.

    Returns a list of ``{id, name, url, country?, adsCount?}`` or ``None`` when
    every transport tier fails (caller should fall back to Apify).
    """
    q = (query or "").strip()
    if len(q) < 2:
        return []

    want = max(1, min(int(limit), 50))
    raw = await _merge_suggestions(_suggestion_queries(q), per_query=30)
    if raw is None:
        return None
    ranked = _rank_advertisers(raw, query=q, country=country)
    log.info(
        "google_ads_search_ranked",
        q=q[:40],
        country=(country or "").upper(),
        candidates=len(raw),
        returned=min(want, len(ranked)),
        top=(ranked[0].get("name") if ranked else None),
    )
    return ranked[:want]


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


_GOOGLE_CDN_HINTS = (
    "googlesyndication.com",
    "googleusercontent.com",
    "gstatic.com",
    "adstransparency.google.com",
    "google.com/aclk",
    "doubleclick.net",
    "displayads-formats",
)


def _extract_landing_url(blob: str) -> str | None:
    """Best-effort destination URL from ATC creative payload JSON."""
    if not blob:
        return None
    for pat in (
        r'"(?:finalUrl|destinationUrl|clickUrl|landingUrl|exitUrl)"\s*:\s*"(https?://[^"]+)"',
        r'"(?:final_url|destination_url|click_url)"\s*:\s*"(https?://[^"]+)"',
    ):
        m = re.search(pat, blob, re.I)
        if m:
            url = m.group(1).replace("\\u003d", "=").replace("\\/", "/")
            if not any(h in url for h in _GOOGLE_CDN_HINTS):
                return url
    for url in re.findall(r"https?://[^\s\\\"'<>]+", blob):
        url = url.rstrip("\\").rstrip(")").replace("\\u003d", "=").replace("\\/", "/")
        if any(h in url for h in _GOOGLE_CDN_HINTS):
            continue
        if url.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".js", ".css")):
            continue
        return url
    return None


def _extract_creative_text(blob: str) -> tuple[str | None, str | None]:
    """Return (body, headline) when ATC embeds copy in the creative archive."""
    if not blob:
        return None, None
    body = None
    headline = None
    for pat in (
        r'"(?:adText|description|body|bodyText)"\s*:\s*"([^"]{2,500})"',
        r'"(?:text)"\s*:\s*"([^"]{2,500})"',
    ):
        m = re.search(pat, blob, re.I)
        if m:
            body = m.group(1).encode("utf-8").decode("unicode_escape", errors="ignore")
            break
    for pat in (
        r'"(?:headline|title|adTitle)"\s*:\s*"([^"]{2,200})"',
    ):
        m = re.search(pat, blob, re.I)
        if m:
            headline = m.group(1).encode("utf-8").decode("unicode_escape", errors="ignore")
            break
    return body, headline


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
    body, headline = _extract_creative_text(html)
    landing = _extract_landing_url(html)
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
        "text": body,
        "headline": headline,
        "landingUrl": landing,
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
    if q_norm.endswith(".com") or _looks_like_domain(query):
        q_norm = brand
    want = (country or "").strip().upper()
    corp_re = re.compile(
        r"\b(inc\.?|ltd\.?|llc|gmbh|b\.?v\.?|s\.?r\.?l\.?|corp\.?|company|co\.)\b",
        re.I,
    )
    # Prefer US-style entities when country=US; demote EU subsidiaries (SRL/BV).
    us_corp_re = re.compile(r"\b(inc\.?|llc|corp\.?)\b", re.I)
    eu_corp_re = re.compile(
        r"\b(s\.?r\.?l\.?|b\.?v\.?|gmbh|s\.?a\.?s\.?|oyj?|ab|ag|nv)\b",
        re.I,
    )
    person_re = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$")

    def score(adv: dict[str, Any]) -> tuple:
        raw_name = adv.get("name") or ""
        name = raw_name.lower()
        ads = int(adv.get("adsCount") or 0)
        exact = 1 if name in {q_norm, brand, f"{brand}, inc.", f"{brand} inc."} else 0
        inc_exact = 1 if name in {f"{brand}, inc.", f"{brand} inc."} else 0
        corp = 1 if corp_re.search(raw_name) else 0
        us_corp = 1 if want == "US" and us_corp_re.search(raw_name) else 0
        eu_pen = 1 if want == "US" and eu_corp_re.search(raw_name) else 0
        brand_word = 1 if brand and re.search(rf"\b{re.escape(brand)}\b", name) else 0
        starts = 1 if name.startswith(brand) else 0
        contains = 1 if brand and brand in name else 0
        country_hit = 1 if want and adv.get("country") == want else 0
        personish = 1 if person_re.match(raw_name) and not corp else 0
        return (
            exact,
            inc_exact,
            us_corp,
            brand_word,
            corp,
            starts,
            contains,
            country_hit,
            ads,
            -eu_pen,
            -personish,
        )

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


def _encode_page_cursor(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_page_cursor(value: str | None) -> dict[str, Any] | None:
    if not value or not str(value).strip():
        return None
    raw = str(value).strip()
    pad = "=" * (-len(raw) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(raw + pad).decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _parse_ymd(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def _iso_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _creative_in_date_window(item: dict[str, Any], start: date | None, end: date | None) -> bool:
    """Keep creatives whose [firstShown, lastShown] overlaps [start, end]."""
    if start is None and end is None:
        return True
    first = _iso_date(item.get("firstShown"))
    last = _iso_date(item.get("lastShown")) or first
    if first is None and last is None:
        return False
    if first is None:
        first = last
    if last is None:
        last = first
    assert first is not None and last is not None
    if start is not None and last < start:
        return False
    if end is not None and first > end:
        return False
    return True


async def resolve_advertiser_ids(
    query: str,
    *,
    country: str | None = None,
    max_ids: int = 3,
) -> list[str] | None:
    """Resolve name/domain/AR id → one or more AR advertiser ids."""
    meta = await resolve_advertisers(query, country=country, max_ids=max_ids)
    if meta is None:
        return None
    return list(meta.get("ids") or [])


async def resolve_advertisers(
    query: str,
    *,
    country: str | None = None,
    max_ids: int = 3,
) -> dict[str, Any] | None:
    """Resolve name/domain/AR id → advertiser ids + adsCount estimate.

    Returns ``None`` on transport failure, or
    ``{"ids": [...], "adsCountEstimate": int|None, "name": str|None}``.
    """
    q = (query or "").strip()
    if not q:
        return {"ids": [], "adsCountEstimate": None, "name": None}
    if re.fullmatch(r"AR\d+", q, flags=re.I):
        aid = q.upper() if q.startswith("AR") else q
        return {"ids": [aid], "adsCountEstimate": None, "name": None}

    brand = _brand_from_query(q)
    queries = _suggestion_queries(q)
    corp_re = re.compile(
        r"\b(inc\.?|ltd\.?|llc|gmbh|b\.?v\.?|s\.?r\.?l\.?|corp\.?|company|co\.)\b",
        re.I,
    )
    raw = await _merge_suggestions(queries, per_query=30)
    if raw is None:
        return None
    # Domains / brands: if top Inc. already has volume, we still rank the full set.
    ranked_early = _rank_advertisers(raw, query=q, country=country)
    top_early = ranked_early[0] if ranked_early else None
    if (
        top_early
        and corp_re.search(top_early.get("name") or "")
        and brand.lower() in (top_early.get("name") or "").lower()
        and int(top_early.get("adsCount") or 0) >= 50
    ):
        log.info(
            "google_ads_resolve_early",
            q=q[:40],
            top=top_early.get("name"),
            ads=top_early.get("adsCount"),
        )
    ranked = ranked_early
    ids: list[str] = []
    for adv in ranked:
        aid = adv["id"]
        if aid in ids:
            continue
        ids.append(aid)
        if len(ids) >= max_ids:
            break
    top = ranked[0] if ranked else None
    return {
        "ids": ids,
        "adsCountEstimate": int(top["adsCount"]) if top and top.get("adsCount") is not None else None,
        "name": (top or {}).get("name"),
    }


async def _collect_creatives(
    ids: list[str],
    *,
    want: int,
    page_size: int,
    region_enums: list[int] | None,
    proxy: str | None,
    start_cursor: Any = None,
    primary_only: bool = False,
) -> tuple[list[dict[str, Any]], Any]:
    """Page SearchCreatives for ``ids`` on one proxy; may return [].

    Returns ``(items, next_raw_cursor)``. ``next_raw_cursor`` is ATC's opaque
    page token for the primary advertiser when more pages exist.
    """
    collected: list[dict[str, Any]] = []
    seen: set[str] = set()
    next_raw: Any = None

    def _consume(payload: dict[str, Any]) -> Any:
        """Ingest a full ATC page; return the next-page cursor (or None)."""
        rows = payload.get("1")
        if isinstance(rows, list):
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
        return payload.get("2")

    for index, adv_id in enumerate(ids):
        if len(collected) >= want:
            break
        cursor: Any = start_cursor if index == 0 else None
        first = True
        while first or cursor is not None:
            first = False
            if len(collected) >= want:
                break
            payload = await _post_creatives(
                [adv_id],
                page_size=page_size if index == 0 else min(page_size, max(1, want - len(collected))),
                cursor=cursor,
                region_enums=region_enums,
                proxy=proxy,
            )
            if payload is None:
                break
            cursor = _consume(payload)
            if index == 0:
                next_raw = cursor
            # Only paginate the primary advertiser; extras are one page each.
            if index > 0 or primary_only:
                break
            if len(collected) >= want:
                break
    return collected, next_raw


async def fetch_ad_details(
    advertiser_id: str,
    creative_id: str,
    *,
    country: str | None = None,
    max_pages: int = 8,
) -> dict[str, Any] | None:
    """Resolve one ATC creative (AR… + CR…) via SearchCreatives paging.

    Returns ``_normalize_ad`` input shape, or ``None`` so the router can Apify.
    """
    adv = (advertiser_id or "").strip().upper()
    cr = (creative_id or "").strip().upper()
    if not adv.startswith("AR") or not cr.startswith("CR"):
        return None

    region_enums = _region_enums(country)
    working_proxy: str | None | bool = False  # False = unset
    for _tier, proxy in _proxy_tiers():
        probe = await _post_creatives(
            [adv],
            page_size=10,
            cursor=None,
            region_enums=region_enums,
            proxy=proxy,
        )
        if probe is None and region_enums is not None:
            probe = await _post_creatives(
                [adv],
                page_size=10,
                cursor=None,
                region_enums=None,
                proxy=proxy,
            )
            if probe is not None:
                region_enums = None
        if probe is None:
            continue
        working_proxy = proxy
        break
    if working_proxy is False:
        return None

    for regions in (region_enums, None):
        cursor: Any = None
        first = True
        pages = 0
        while first or cursor is not None:
            first = False
            if pages >= max_pages:
                break
            pages += 1
            payload = await _post_creatives(
                [adv],
                page_size=40,
                cursor=cursor,
                region_enums=regions,
                proxy=working_proxy,  # type: ignore[arg-type]
            )
            if payload is None:
                break
            rows = payload.get("1")
            if isinstance(rows, list):
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    item = _to_normalize_shape(row)
                    if item and item.get("id") == cr:
                        log.info(
                            "google_ads_detail_ok",
                            advertiser=adv,
                            creative=cr,
                            page=pages,
                        )
                        return item
            cursor = payload.get("2")
        if region_enums is None:
            break

    log.info("google_ads_detail_miss", advertiser=adv, creative=cr)
    return None


async def fetch_company_ads(
    advertiser: str,
    *,
    country: str | None = None,
    limit: int = 20,
    cursor: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any] | None:
    """Fetch creatives for an advertiser name, domain, or AR id.

    Returns ``None`` when every transport tier fails (caller → Apify), else::

        {
          "ads": [...],                 # for _normalize_ad
          "nextCursor": str | None,
          "hasMore": bool,
          "adsCountEstimate": int | None,
          "resolvedName": str | None,
        }

    Country is a soft preference: ATC often resolves brands to non-US legal
    entities whose creatives vanish under a hard region filter. We try the
    requested region first, then retry without a region filter when empty.

    ``start_date`` / ``end_date`` (YYYY-MM-DD) filter creatives client-side by
    firstShown/lastShown overlap — ATC's RPC date filters are unreliable.
    """
    want = max(0, int(limit))
    start_d = _parse_ymd(start_date)
    end_d = _parse_ymd(end_date)
    page_cursor = _decode_page_cursor(cursor)
    if cursor and page_cursor is None:
        return {
            "ads": [],
            "nextCursor": None,
            "hasMore": False,
            "adsCountEstimate": None,
            "resolvedName": None,
            "error": "invalid_cursor",
        }

    if want == 0:
        return {
            "ads": [],
            "nextCursor": None,
            "hasMore": False,
            "adsCountEstimate": None,
            "resolvedName": None,
        }

    if page_cursor:
        ids = [str(page_cursor.get("advertiserId") or "")]
        ids = [i for i in ids if i.startswith("AR")]
        estimate = page_cursor.get("adsCountEstimate")
        resolved_name = page_cursor.get("name")
        start_raw = page_cursor.get("rpcCursor")
        region_mode = page_cursor.get("regionMode")  # "requested" | "any"
        if not ids:
            return {
                "ads": [],
                "nextCursor": None,
                "hasMore": False,
                "adsCountEstimate": estimate,
                "resolvedName": resolved_name,
            }
        meta = {
            "ids": ids,
            "adsCountEstimate": estimate,
            "name": resolved_name,
        }
    else:
        meta = await resolve_advertisers(advertiser, country=country, max_ids=3)
        if meta is None:
            return None
        ids = list(meta.get("ids") or [])
        start_raw = None
        region_mode = "requested"
        if not ids:
            return {
                "ads": [],
                "nextCursor": None,
                "hasMore": False,
                "adsCountEstimate": meta.get("adsCountEstimate"),
                "resolvedName": meta.get("name"),
            }

    region_enums = _region_enums(country) if region_mode != "any" else None
    # Match page size to limit so we don't drop leftover creatives on a fat page.
    page_size = min(40, max(want, 1))

    # Pick a working proxy with a probe request (region preferred).
    working: tuple[str, str | None] | None = None
    for tier, proxy in _proxy_tiers():
        probe = await _post_creatives(
            ids[:1],
            page_size=min(10, page_size),
            cursor=None,
            region_enums=region_enums,
            proxy=proxy,
        )
        if probe is None and region_enums is not None:
            probe = await _post_creatives(
                ids[:1],
                page_size=min(10, page_size),
                cursor=None,
                region_enums=None,
                proxy=proxy,
            )
        if probe is None:
            continue
        working = (tier, proxy)
        break

    if working is None:
        return None

    tier_used, proxy = working
    used_region = bool(region_enums)

    async def _pull(regions: list[int] | None, rpc_cursor: Any) -> tuple[list[dict[str, Any]], Any]:
        return await _collect_creatives(
            ids,
            want=want if not (start_d or end_d) else min(200, max(want * 4, 40)),
            page_size=page_size if not (start_d or end_d) else 40,
            region_enums=regions,
            proxy=proxy,
            start_cursor=rpc_cursor,
            primary_only=bool(page_cursor),
        )

    collected, next_raw = await _pull(region_enums, start_raw)

    # Soft country: resolved AR ids are often foreign entities with ads that
    # ATC's region filter hides (e.g. "Samsung" → MY entity, country=US → 0).
    if not collected and region_enums is not None and not page_cursor:
        collected, next_raw = await _pull(None, None)
        used_region = False
        if collected:
            log.info(
                "google_ads_creatives_region_fallback",
                tier=tier_used,
                count=len(collected),
                q=advertiser[:40],
                country=country,
            )

    if start_d or end_d:
        # Keep paging while the filtered page is short and ATC still has rows.
        filtered = [a for a in collected if _creative_in_date_window(a, start_d, end_d)]
        safety = 0
        while len(filtered) < want and next_raw is not None and safety < 8:
            safety += 1
            more, next_raw = await _collect_creatives(
                ids[:1],
                want=40,
                page_size=40,
                region_enums=region_enums if used_region else None,
                proxy=proxy,
                start_cursor=next_raw,
                primary_only=True,
            )
            if not more:
                break
            filtered.extend(a for a in more if _creative_in_date_window(a, start_d, end_d))
        collected = filtered

    page = collected[:want]
    next_cursor = None
    if next_raw is not None and ids:
        next_cursor = _encode_page_cursor(
            {
                "v": 1,
                "advertiserId": ids[0],
                "rpcCursor": next_raw,
                "regionMode": "requested" if used_region else "any",
                "adsCountEstimate": meta.get("adsCountEstimate"),
                "name": meta.get("name"),
            }
        )

    log.info(
        "google_ads_creatives_ok",
        tier=tier_used,
        count=len(page),
        advertisers=len(ids),
        region_filter=used_region,
        has_more=bool(next_cursor),
        q=advertiser[:40],
    )
    return {
        "ads": page,
        "nextCursor": next_cursor,
        "hasMore": next_cursor is not None,
        "adsCountEstimate": meta.get("adsCountEstimate"),
        "resolvedName": meta.get("name"),
        "resolvedId": ids[0] if ids else None,
    }
