"""Native Facebook Marketplace via Decodo JS-rendered HTML.

Search hydrates GroupCommerceProductItem list cards. Item pages carry a richer
Relay blob (description, condition, coordinates, photos). Plain DC/residential
GETs return 400 — Decodo ``headless=html`` is required.
"""

from __future__ import annotations

import asyncio
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
CREDIT_FB_MARKETPLACE_ITEM_NATIVE = 2

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)
_SLUG_RE = re.compile(r"[^a-z0-9]+")
_ITEM_ID_RE = re.compile(r"/marketplace/item/(\d+)", re.I)

_ENRICH_CONCURRENCY = 4


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


def item_id_from_url(url: str) -> str | None:
    m = _ITEM_ID_RE.search(url or "")
    return m.group(1) if m else None


def item_url(listing_id: str) -> str:
    return f"https://www.facebook.com/marketplace/item/{listing_id}/"


def _empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


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


def _walk_by_id(obj: Any, listing_id: str, found: list[dict[str, Any]], depth: int = 0) -> None:
    if depth > 50:
        return
    if isinstance(obj, dict):
        if str(obj.get("id") or "") == listing_id:
            found.append(obj)
        for value in obj.values():
            _walk_by_id(value, listing_id, found, depth + 1)
    elif isinstance(obj, list):
        for value in obj:
            _walk_by_id(value, listing_id, found, depth + 1)


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


def _extract_nodes_for_id(html: str, listing_id: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in _SCRIPT_RE.finditer(html):
        raw = match.group(1)
        if listing_id not in raw:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        _walk_by_id(data, listing_id, found)
    return found


def _merge_nodes(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    if not nodes:
        return {}
    ranked = sorted(nodes, key=lambda n: len(n.keys()), reverse=True)
    out = dict(ranked[0])
    for node in ranked[1:]:
        for key, value in node.items():
            if _empty(out.get(key)) and not _empty(value):
                out[key] = value
    return out


def _photo_uris(node: dict[str, Any]) -> list[str]:
    uris: list[str] = []
    seen: set[str] = set()

    def _add(uri: str | None) -> None:
        if not uri or uri in seen:
            return
        seen.add(uri)
        uris.append(uri)

    primary = node.get("primary_listing_photo")
    if isinstance(primary, dict):
        image = primary.get("image") if isinstance(primary.get("image"), dict) else {}
        _add(safe_str(image.get("uri") or primary.get("uri")))
    photos = node.get("listing_photos")
    if isinstance(photos, list):
        for entry in photos:
            if not isinstance(entry, dict):
                continue
            image = entry.get("image") if isinstance(entry.get("image"), dict) else {}
            _add(safe_str(image.get("uri") or entry.get("uri")))
    return uris


def _condition_label(node: dict[str, Any]) -> str | None:
    for attr in node.get("attribute_data") or []:
        if isinstance(attr, dict) and attr.get("attribute_name") == "Condition":
            return safe_str(attr.get("label") or attr.get("value"))
    return None


def _created_at(node: dict[str, Any]) -> str | None:
    created = node.get("creation_time")
    if isinstance(created, (int, float)) and created > 0:
        try:
            return datetime.fromtimestamp(int(created), tz=timezone.utc).isoformat()
        except (OSError, OverflowError, ValueError):
            return None
    return None


def _map_listing(node: dict[str, Any]) -> dict[str, Any] | None:
    lid = safe_str(node.get("id"))
    title = safe_str(node.get("marketplace_listing_title") or node.get("custom_title"))
    if not lid or not title:
        return None
    price_obj = node.get("listing_price") if isinstance(node.get("listing_price"), dict) else {}
    price_fmt = safe_str(
        price_obj.get("formatted_amount_zeros_stripped") or price_obj.get("formatted_amount")
    )
    amount = safe_float(price_obj.get("amount"))
    loc = node.get("location") if isinstance(node.get("location"), dict) else {}
    geo = loc.get("reverse_geocode") if isinstance(loc.get("reverse_geocode"), dict) else {}
    city = safe_str(geo.get("city"))
    state = safe_str(geo.get("state"))
    loc_display = ", ".join(p for p in (city, state) if p) or None
    photos = _photo_uris(node)
    currency = safe_str(price_obj.get("currency"))
    if not currency and price_fmt and price_fmt.startswith("$"):
        currency = "USD"
    delivery = node.get("delivery_types")
    if not isinstance(delivery, list) or not delivery:
        delivery = None
    return strip_empty(
        {
            "platform": "facebook",
            "id": lid,
            "title": title,
            "url": item_url(lid),
            "price": amount,
            "priceFormatted": price_fmt,
            "currency": currency,
            "location": loc_display,
            "city": city,
            "state": state,
            "isSold": bool(node.get("is_sold")) if node.get("is_sold") is not None else None,
            "isLive": bool(node.get("is_live")) if node.get("is_live") is not None else None,
            "deliveryTypes": delivery,
            "image": photos[0] if photos else None,
            "photos": photos or None,
            "createdAt": _created_at(node),
        }
    )


def _map_item_detail(node: dict[str, Any], url: str) -> dict[str, Any] | None:
    lid = safe_str(node.get("id")) or item_id_from_url(url)
    title = safe_str(
        node.get("marketplace_listing_title") or node.get("base_marketplace_listing_title")
    )
    if not lid or not title:
        return None
    price = node.get("listing_price") if isinstance(node.get("listing_price"), dict) else {}
    desc = node.get("redacted_description") if isinstance(node.get("redacted_description"), dict) else {}
    loc_text = node.get("location_text") if isinstance(node.get("location_text"), dict) else {}
    coords = node.get("location") if isinstance(node.get("location"), dict) else {}
    if coords.get("latitude") is None:
        item_loc = node.get("item_location") if isinstance(node.get("item_location"), dict) else {}
        if item_loc.get("latitude") is not None:
            coords = item_loc
    amount = safe_float(price.get("amount"))
    price_fmt = safe_str(
        price.get("formatted_amount_zeros_stripped") or price.get("formatted_amount")
    )
    photos = _photo_uris(node)
    delivery = node.get("delivery_types")
    if not isinstance(delivery, list):
        delivery = []
    return strip_empty(
        {
            "platform": "facebook",
            "id": lid,
            "url": safe_str(node.get("share_uri")) or url or item_url(lid),
            "title": title,
            "description": safe_str(desc.get("text")),
            "price": amount,
            "priceFormatted": price_fmt,
            "currency": safe_str(price.get("currency")),
            "condition": _condition_label(node),
            "location": safe_str(loc_text.get("text")),
            "latitude": coords.get("latitude"),
            "longitude": coords.get("longitude"),
            "isSold": bool(node.get("is_sold")) if node.get("is_sold") is not None else None,
            "isLive": bool(node.get("is_live")) if node.get("is_live") is not None else None,
            "deliveryTypes": delivery,
            "image": photos[0] if photos else None,
            "photos": photos or None,
            "createdAt": _created_at(node),
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


async def marketplace_item_native(url: str) -> dict[str, Any] | None:
    listing_id = item_id_from_url(url)
    if not listing_id or not decodo_fetch.enabled():
        return None
    page_url = item_url(listing_id)
    got = await decodo_fetch.fetch_url(page_url, timeout=120.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body or listing_id not in body:
        return None
    merged = _merge_nodes(_extract_nodes_for_id(body, listing_id))
    if not merged:
        return None
    return _map_item_detail(merged, page_url)


def _merge_detail_into_listing(
    listing: dict[str, Any], detail: dict[str, Any]
) -> dict[str, Any]:
    out = dict(listing)
    for key in (
        "description",
        "condition",
        "latitude",
        "longitude",
        "location",
        "price",
        "priceFormatted",
        "currency",
        "isSold",
        "isLive",
        "deliveryTypes",
        "createdAt",
        "image",
        "photos",
        "title",
    ):
        if not _empty(detail.get(key)):
            out[key] = detail[key]
    return strip_empty(out)


async def marketplace_search_details_native(
    q: str, location: str, limit: int
) -> list[dict[str, Any]] | None:
    """List search + per-item Decodo enrich (description / coords / photos)."""
    listings = await marketplace_search_native(q, location, limit)
    if listings is None:
        return None
    if not listings:
        return []

    sem = asyncio.Semaphore(_ENRICH_CONCURRENCY)

    async def _enrich(row: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            detail = await marketplace_item_native(safe_str(row.get("url")) or "")
        if detail:
            return _merge_detail_into_listing(row, detail)
        return row

    return list(await asyncio.gather(*[_enrich(row) for row in listings]))


def credits_for_details(n: int) -> int:
    """Search fetch + one item fetch per returned listing."""
    if n <= 0:
        return CREDIT_FB_MARKETPLACE_NATIVE
    return CREDIT_FB_MARKETPLACE_NATIVE + CREDIT_FB_MARKETPLACE_ITEM_NATIVE * n
