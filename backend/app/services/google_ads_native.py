"""Native Google Ads Transparency Center helpers (no Apify).

Hits Google's public SearchSuggestions RPC used by adstransparency.google.com.
Cost is proxy bandwidth only; cascades datacenter -> residential -> direct.
"""

from __future__ import annotations

import json
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
