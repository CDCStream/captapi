"""Native Facebook Marketplace search via Decodo JS-rendered HTML.

Plain DC/residential GETs return 400. Decodo ``headless=html`` hydrates
GroupCommerceProductItem nodes (title, price, location, photo).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_float, safe_str, strip_empty

log = structlog.get_logger(__name__)

CREDIT_FB_MARKETPLACE_NATIVE = 2

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def location_slug(location: str) -> str | None:
    """Turn 'Austin, TX' into 'austin' and 'New York' into 'new-york'."""
    raw = (location or "").strip()
    if not raw:
        return None
    city = raw.split(",", 1)[0].strip().lower()
    slug = _SLUG_RE.sub("-", city).strip("-")
    return slug or None


def search_url(q: str, location: str) -> str | None:
    slug = location_slug(location)
    if not slug:
        return None
    return (
        f"https://www.facebook.com/marketplace/{slug}/search/?query="
        f"{quote_plus((q or '').strip())}"
    )


def _walk(obj: Any, found: list[dict[str, Any]], depth: int = 0) -> None:
    if depth > 40:
        return
    if isinstance(obj, dict):
        title = obj.get("marketplace_listing_title")
        lid = obj.get("id")
        if title and lid and (
            "Marketplace" in str(obj.get("__typename") or "")
            or obj.get("listing_price") is not None
            or obj.get("__isMarketplaceListingRenderable")
        ):
            found.append(obj)
        for value in obj.values():
            _walk(value, found, depth + 1)
    elif isinstance(obj, list):
        for value in obj:
            _walk(value, found, depth + 1)


def _extract_nodes(html: str) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for match in _SCRIPT_RE.finditer(html):
        raw = match.group(1)
        if "marketplace_listing_title" not in raw:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        _walk(data, nodes)
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for node in nodes:
        lid = safe_str(node.get("id"))
        if not lid or lid in seen:
            continue
        seen.add(lid)
        out.append(node)
    return out


def _map_listing(node: dict[str, Any]) -> dict[str, Any] | None:
    lid = safe_str(node.get("id"))
    title = safe_str(node.get("marketplace_listing_title") or node.get("custom_title"))
    if not lid or not title:
        return None
    price_obj = node.get("listing_price") if isinstance(node.get("listing_price"), dict) else {}
    price_fmt = safe_str(price_obj.get("formatted_amount"))
    amount = safe_float(price_obj.get("amount"))
    loc = node.get("location") if isinstance(node.get("location"), dict) else {}
    geo = loc.get("reverse_geocode") if isinstance(loc.get("reverse_geocode"), dict) else {}
    city = safe_str(geo.get("city"))
    state = safe_str(geo.get("state"))
    loc_display = ", ".join(p for p in (city, state) if p) or None
    photo = None
    primary = node.get("primary_listing_photo")
    if isinstance(primary, dict):
        image = primary.get("image") if isinstance(primary.get("image"), dict) else {}
        photo = safe_str(image.get("uri") or primary.get("uri"))
    created = node.get("creation_time")
    created_at = None
    if isinstance(created, (int, float)) and created > 0:
        try:
            created_at = datetime.fromtimestamp(int(created), tz=timezone.utc).isoformat()
        except (OSError, OverflowError, ValueError):
            created_at = None
    currency = "USD" if price_fmt and price_fmt.startswith("$") else None
    delivery = node.get("delivery_types")
    if not isinstance(delivery, list) or not delivery:
        delivery = None
    return strip_empty(
        {
            "platform": "facebook",
            "id": lid,
            "title": title,
            "url": f"https://www.facebook.com/marketplace/item/{lid}/",
            "price": amount,
            "priceFormatted": price_fmt,
            "currency": currency,
            "location": loc_display,
            "city": city,
            "state": state,
            "isSold": bool(node.get("is_sold")) if node.get("is_sold") is not None else None,
            "isLive": bool(node.get("is_live")) if node.get("is_live") is not None else None,
            "deliveryTypes": delivery,
            "image": photo,
            "photos": [photo] if photo else None,
            "createdAt": created_at,
        }
    )


async def marketplace_search_native(
    q: str, location: str, limit: int
) -> list[dict[str, Any]] | None:
    if limit <= 0:
        return []
    url = search_url(q, location)
    if not url or not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body or "marketplace_listing_title" not in body:
        return None
    mapped: list[dict[str, Any]] = []
    for node in _extract_nodes(body):
        row = _map_listing(node)
        if row:
            mapped.append(row)
        if len(mapped) >= limit:
            break
    return mapped if mapped else None
