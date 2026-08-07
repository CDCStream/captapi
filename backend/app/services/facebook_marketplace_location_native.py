"""Native Facebook Marketplace location resolve via Decodo.

Fetches ``/marketplace/{slug}/`` and reads schema.org City latitude/longitude
plus Facebook's city page id (``city_page.id``) when the SSR blob exposes it.
Used to disambiguate city names (Austin TX vs Austin MN) and to hand search
callers a lat/lng + canonical place id.

Ambiguous bare-city tables already carry lat/lng (and often cityPageId) — those
rows are returned immediately without Decodo. A single Decodo hub fetch is only
used when the table cannot answer (unknown city / missing coords), with a short
timeout under Cloudflare's ~125s proxy read limit.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Any

import structlog

from app.services import decodo_fetch
from app.services.facebook_marketplace_native import location_slug
from app.utils.formatters import safe_float, safe_str, strip_empty

log = structlog.get_logger(__name__)

CREDIT_FB_MARKETPLACE_LOCATION_NATIVE = 2

# Per-hub Decodo budget — leave headroom under Cloudflare's ~125s proxy read.
_HUB_TIMEOUT_SECS = 35.0
# Whole-call wall (docs budget). Ambiguous known-table path is typically <1s.
_LOCATION_WALL_SECS = 50.0

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)
_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)
_CITY_PAGE_ID_RE = re.compile(
    r'"city_page"\s*:\s*\{\s*(?:"__typename"\s*:\s*"[^"]*"\s*,\s*)?"id"\s*:\s*"(\d+)"',
    re.I,
)
_CITY_PAGE_ID_RE_ALT = re.compile(
    r'"id"\s*:\s*"(\d+)"\s*,\s*"__typename"\s*:\s*"MarketplaceCityPage"',
    re.I,
)

# Query tail like "Austin, TX" / "Austin Texas"
_STATE_ABBR = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC",
}

# Bare city names that Facebook Marketplace hubs often collide on.
# Values are (state, marketplace slug override or None, lat, lng, cityPageId|None).
# cityPageId filled when known from live Marketplace search cards; otherwise
# extracted per-fetch from the hub HTML (only when Decodo is needed).
_AMBIGUOUS: dict[str, list[tuple[str, str | None, float, float, str | None]]] = {
    "austin": [
        ("TX", None, 30.2677, -97.7475, "109791499039942"),
        ("MN", "austin-minnesota", 43.6666, -92.9746, None),
        ("IN", "austin-indiana", 38.7584, -85.8080, None),
    ],
    "portland": [
        ("OR", None, 45.5152, -122.6784, None),
        ("ME", "portland-maine", 43.6591, -70.2568, None),
    ],
    "springfield": [
        ("IL", "springfield-illinois", 39.7817, -89.6501, None),
        ("MO", "springfield-missouri", 37.2090, -93.2923, None),
        ("MA", "springfield-massachusetts", 42.1015, -72.5898, None),
    ],
}


def _parse_city_state(q: str) -> tuple[str | None, str | None]:
    raw = (q or "").strip()
    if not raw:
        return None, None
    if "," in raw:
        city, rest = raw.split(",", 1)
        city = city.strip() or None
        token = rest.strip().split()[0].upper() if rest.strip() else ""
        state = token if token in _STATE_ABBR else None
        return city, state
    parts = raw.split()
    if len(parts) >= 2 and parts[-1].upper() in _STATE_ABBR:
        return " ".join(parts[:-1]).strip() or None, parts[-1].upper()
    return raw, None


def _city_page_id(html: str) -> str | None:
    """Facebook's Marketplace city page id — same value as search ``cityPageId``."""
    m = _CITY_PAGE_ID_RE.search(html or "") or _CITY_PAGE_ID_RE_ALT.search(html or "")
    return m.group(1) if m else None


def _from_ldjson(html: str) -> dict[str, Any] | None:
    for match in _LD_RE.finditer(html):
        raw = match.group(1).strip()
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        items = data if isinstance(data, list) else [data]
        for obj in items:
            if not isinstance(obj, dict):
                continue
            area = obj.get("geographicArea")
            if not isinstance(area, dict):
                if "City" in str(obj.get("@type") or "") and obj.get("latitude") is not None:
                    area = obj
                else:
                    continue
            lat = safe_float(area.get("latitude"))
            lng = safe_float(area.get("longitude"))
            name = safe_str(area.get("name") or obj.get("name"))
            if name or lat is not None:
                return {
                    "name": name,
                    "latitude": lat,
                    "longitude": lng,
                }
    return None


def _from_blobs(html: str) -> dict[str, Any] | None:
    for match in _SCRIPT_RE.finditer(html):
        raw = match.group(1)
        if "latitude" not in raw:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        found: list[dict[str, Any]] = []

        def walk(obj: Any, depth: int = 0) -> None:
            if depth > 35 or found:
                return
            if isinstance(obj, dict):
                lat = obj.get("latitude")
                lng = obj.get("longitude")
                name = obj.get("name")
                if isinstance(lat, (int, float)) and isinstance(lng, (int, float)) and name:
                    found.append({"name": str(name), "latitude": float(lat), "longitude": float(lng)})
                    return
                for value in obj.values():
                    walk(value, depth + 1)
            elif isinstance(obj, list):
                for value in obj:
                    walk(value, depth + 1)

        walk(data)
        if found:
            return found[0]
    return None


async def _fetch_hub(
    slug: str, *, timeout: float = _HUB_TIMEOUT_SECS
) -> tuple[str, dict[str, Any] | None, str | None] | None:
    """Return (html, geo, cityPageId) for a marketplace hub slug."""
    url = f"https://www.facebook.com/marketplace/{slug}/"
    got = await decodo_fetch.fetch_url(url, timeout=timeout, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or not html:
        return None
    geo = _from_ldjson(html) or _from_blobs(html)
    return html, geo, _city_page_id(html)


def _location_row(
    *,
    city: str | None,
    state: str | None,
    name: str | None,
    lat: float | None,
    lng: float | None,
    city_page_id: str | None,
    slug: str | None,
) -> dict[str, Any]:
    label = ", ".join(p for p in [city, state] if p) if state else (city or name)
    # Canonical id = Facebook city page id when known (same as search cityPageId).
    # No duplicate cityPageId key (MP4) — join search via id === listing.cityPageId.
    out = {
        "id": city_page_id,
        "slug": slug,
        "name": label or name,
        "city": city,
        "state": state,
        "latitude": lat,
        "longitude": lng,
    }
    return strip_empty(out)


async def marketplace_location_search_native(
    q: str, limit: int = 10
) -> tuple[list[dict[str, Any]] | None, dict[str, Any]]:
    """Return ``(locations|None, timings)``.

    ``timings`` always includes ``path``, ``hubMs``, ``hubCount``, ``totalMs``.
    """
    t0 = time.perf_counter()
    timings: dict[str, Any] = {
        "path": "none",
        "hubMs": 0,
        "hubCount": 0,
        "totalMs": 0,
    }
    if not (q or "").strip():
        timings["totalMs"] = int((time.perf_counter() - t0) * 1000)
        return None, timings
    city_hint, state_hint = _parse_city_state(q)
    if not city_hint:
        timings["totalMs"] = int((time.perf_counter() - t0) * 1000)
        return None, timings

    city_key = city_hint.strip().lower()

    # Ambiguous bare city → known table (no Decodo). Was serial 120s×N hubs (MP1).
    if not state_hint and city_key in _AMBIGUOUS:
        results: list[dict[str, Any]] = []
        for state, slug_override, lat, lng, known_id in _AMBIGUOUS[city_key][: max(1, limit)]:
            slug = slug_override or location_slug(f"{city_hint}, {state}")
            if not slug:
                continue
            row = _location_row(
                city=city_hint,
                state=state,
                name=f"{city_hint}, {state}",
                lat=lat,
                lng=lng,
                city_page_id=known_id,
                slug=slug,
            )
            if row.get("name"):
                results.append(row)
        timings["path"] = "ambiguous_table"
        timings["hubCount"] = 0
        timings["hubMs"] = 0
        timings["totalMs"] = int((time.perf_counter() - t0) * 1000)
        if results:
            log.info(
                "facebook_marketplace_location_native_ambiguous",
                q=q[:80],
                n=len(results),
                total_ms=timings["totalMs"],
            )
            return results[: max(1, limit)], timings
        return None, timings

    slug = location_slug(q)
    if not slug:
        timings["totalMs"] = int((time.perf_counter() - t0) * 1000)
        return None, timings
    if not decodo_fetch.enabled():
        timings["path"] = "decodo_disabled"
        timings["totalMs"] = int((time.perf_counter() - t0) * 1000)
        return None, timings

    remaining = max(5.0, _LOCATION_WALL_SECS - (time.perf_counter() - t0))
    hub_timeout = min(_HUB_TIMEOUT_SECS, remaining)
    t_hub = time.perf_counter()
    try:
        page = await asyncio.wait_for(_fetch_hub(slug, timeout=hub_timeout), timeout=hub_timeout + 1.0)
    except asyncio.TimeoutError:
        page = None
        timings["path"] = "hub_timeout"
    timings["hubMs"] = int((time.perf_counter() - t_hub) * 1000)
    timings["hubCount"] = 1

    if not page:
        timings["path"] = timings.get("path") or "hub_empty"
        timings["totalMs"] = int((time.perf_counter() - t0) * 1000)
        return None, timings

    html, geo, page_id = page
    name = safe_str((geo or {}).get("name")) or city_hint or q.strip()
    city = city_hint or name
    state = state_hint
    lat = (geo or {}).get("latitude")
    lng = (geo or {}).get("longitude")

    # Prefer known table coords when Decodo geo is thin (e.g. Austin, TX).
    if city and state:
        for st, _slug, la, lo, kid in _AMBIGUOUS.get(city.strip().lower(), []):
            if st != state.upper():
                continue
            if lat is None:
                lat = la
            if lng is None:
                lng = lo
            if not page_id and kid:
                page_id = kid
            break

    if lat is None and "marketplace" not in html.lower():
        log.info("facebook_marketplace_location_native_empty", q=q[:80])
        timings["path"] = "hub_empty"
        timings["totalMs"] = int((time.perf_counter() - t0) * 1000)
        return None, timings

    loc = _location_row(
        city=city,
        state=state,
        name=name,
        lat=safe_float(lat),
        lng=safe_float(lng),
        city_page_id=page_id,
        slug=slug,
    )
    timings["path"] = "hub"
    timings["totalMs"] = int((time.perf_counter() - t0) * 1000)
    log.info(
        "facebook_marketplace_location_native_ok",
        q=q[:80],
        name=loc.get("name"),
        city_page_id=page_id,
        lat=lat,
        lng=lng,
        total_ms=timings["totalMs"],
        hub_ms=timings["hubMs"],
    )
    return [loc][: max(1, limit)], timings
