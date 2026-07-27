"""Native Facebook Marketplace location resolve via Decodo.

Fetches ``/marketplace/{slug}/`` and reads schema.org City latitude/longitude
(plus optional state from the query). No Apify.
"""

from __future__ import annotations

import json
import re
from typing import Any

import structlog

from app.services import decodo_fetch
from app.services.facebook_marketplace_native import location_slug
from app.utils.formatters import safe_float, safe_str

log = structlog.get_logger(__name__)

CREDIT_FB_MARKETPLACE_LOCATION_NATIVE = 2

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)
_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)

# Query tail like "Austin, TX" / "Austin Texas"
_STATE_ABBR = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC",
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
                # Sometimes City is top-level
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


async def marketplace_location_search_native(
    q: str, limit: int = 10
) -> list[dict[str, Any]] | None:
    """Return location dicts {id,name,city,state,latitude,longitude}, or None."""
    if not (q or "").strip() or not decodo_fetch.enabled():
        return None
    city_hint, state_hint = _parse_city_state(q)
    slug = location_slug(q)
    if not slug:
        return None

    url = f"https://www.facebook.com/marketplace/{slug}/"
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or not html:
        return None

    geo = _from_ldjson(html) or _from_blobs(html)
    name = safe_str((geo or {}).get("name")) or city_hint or q.strip()
    city = city_hint or name
    state = state_hint
    lat = (geo or {}).get("latitude")
    lng = (geo or {}).get("longitude")

    # If marketplace page is a login wall / empty geo, still return a usable slug hit.
    if lat is None and "marketplace" not in html.lower():
        log.info("facebook_marketplace_location_native_empty", q=q[:80])
        return None

    label = ", ".join(p for p in [city, state] if p) if state else (city or name)
    key = "|".join(str(v or "").lower() for v in [label, city, state])
    loc = {
        "id": key,
        "name": label or name,
        "city": city,
        "state": state,
        "latitude": lat,
        "longitude": lng,
    }
    log.info(
        "facebook_marketplace_location_native_ok",
        q=q[:80],
        name=loc["name"],
        lat=lat,
        lng=lng,
    )
    return [loc][: max(1, limit)]
