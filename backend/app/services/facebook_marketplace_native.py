"""Native Facebook Marketplace via Decodo JS-rendered HTML.

Search hydrates GroupCommerceProductItem list cards. Item pages carry a richer
Relay blob (description, condition, coordinates, photos). Plain DC/residential
GETs return 400 — Decodo ``headless=html`` is required.

List cards already include a cover photo; ``details=true`` fetches each item
page for description / condition / coordinates / full photo gallery.
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_float, safe_int, safe_str, strip_empty

log = structlog.get_logger(__name__)

CREDIT_FB_MARKETPLACE_NATIVE = 2
CREDIT_FB_MARKETPLACE_ITEM_NATIVE = 2

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)
_SLUG_RE = re.compile(r"[^a-z0-9]+")
_ITEM_ID_RE = re.compile(r"/marketplace/item/(\d+)", re.I)
_PAGE_INFO_RE = re.compile(
    r'"page_info"\s*:\s*\{\s*"end_cursor"\s*:\s*"((?:\\.|[^"\\])*)"\s*,\s*"has_next_page"\s*:\s*(true|false)',
    re.I,
)
_PAGE_INFO_RE_ALT = re.compile(
    r'"page_info"\s*:\s*\{\s*"has_next_page"\s*:\s*(true|false)\s*,\s*"end_cursor"\s*:\s*"((?:\\.|[^"\\])*)"',
    re.I,
)

_ENRICH_CONCURRENCY = 4

# Facebook Marketplace URL filter surface (SSR reads these back in params:).
_SORT_BY = {
    "suggested": None,  # omit → best match
    "distance": "distance_ascend",
    "distance_ascend": "distance_ascend",
    "creation_time": "creation_time_descend",
    "creation_time_descend": "creation_time_descend",
    "price_ascend": "price_ascend",
    "price_descend": "price_descend",
    "price_asc": "price_ascend",
    "price_desc": "price_descend",
}
_CONDITION = {
    "new": "new",
    "like_new": "used_like_new",
    "used_like_new": "used_like_new",
    "good": "used_good",
    "used_good": "used_good",
    "fair": "used_fair",
    "used_fair": "used_fair",
}
_DELIVERY = {
    "all": None,
    "local_pickup": "local_pick_up",
    "local_pick_up": "local_pick_up",
    "in_person": "local_pick_up",
    "shipping": "shipping",
}
_AVAILABILITY = {
    "available": "in stock",
    "in_stock": "in stock",
    "in stock": "in stock",
    "sold": "out of stock",
    "out_of_stock": "out of stock",
    "out of stock": "out of stock",
    "all": "all",
}
_DATE_LISTED = {"1": "1", "7": "7", "30": "30", "last24hours": "1", "last7days": "7", "last30days": "30"}
_RADIUS_MILES = {1, 2, 5, 10, 20, 40, 60, 80, 100, 250, 500}

_SCROLL_ACTIONS: list[dict[str, Any]] = [
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
]


def location_slug(location: str) -> str | None:
    """Turn 'Austin, TX' into 'austin' and 'New York' into 'new-york'."""
    raw = (location or "").strip()
    if not raw:
        return None
    city = raw.split(",", 1)[0].strip().lower()
    slug = _SLUG_RE.sub("-", city).strip("-")
    return slug or None


def normalize_filters(
    *,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    days_since_listed: str | int | None = None,
    condition: str | None = None,
    delivery_method: str | None = None,
    availability: str | None = None,
    radius_miles: int | None = None,
    category: str | None = None,
) -> dict[str, str]:
    """Map public query params → Facebook Marketplace URL query keys."""
    out: dict[str, str] = {}
    if min_price is not None:
        out["minPrice"] = str(int(min_price))
    if max_price is not None:
        out["maxPrice"] = str(int(max_price))
    if sort_by:
        mapped = _SORT_BY.get(sort_by.strip().lower().replace("-", "_"))
        if mapped:
            out["sortBy"] = mapped
    if days_since_listed is not None:
        key = str(days_since_listed).strip().lower().replace("_", "").replace("-", "")
        mapped = _DATE_LISTED.get(key) or _DATE_LISTED.get(str(days_since_listed).strip())
        if mapped:
            out["daysSinceListed"] = mapped
    if condition:
        parts = []
        for raw in re.split(r"[,|]", condition):
            mapped = _CONDITION.get(raw.strip().lower().replace("-", "_"))
            if mapped:
                parts.append(mapped)
        if parts:
            out["itemCondition"] = ",".join(dict.fromkeys(parts))
    if delivery_method:
        mapped = _DELIVERY.get(delivery_method.strip().lower().replace("-", "_"))
        if mapped:
            out["deliveryMethod"] = mapped
    if availability:
        mapped = _AVAILABILITY.get(availability.strip().lower().replace("-", "_"))
        if mapped:
            out["availability"] = mapped
    if radius_miles is not None and int(radius_miles) in _RADIUS_MILES:
        out["radius"] = str(int(radius_miles))
    if category:
        cat = re.sub(r"[^a-z0-9]", "", category.strip().lower())
        if cat:
            out["category"] = cat
    return out


def search_url(
    q: str,
    location: str,
    *,
    filters: dict[str, str] | None = None,
) -> str | None:
    slug = location_slug(location)
    if not slug:
        return None
    params: dict[str, str] = {"query": (q or "").strip()}
    if filters:
        params.update(filters)
    return (
        f"https://www.facebook.com/marketplace/{slug}/search/?{urlencode(params)}"
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


def _extract_page_info(html: str) -> tuple[str | None, bool]:
    """Return (end_cursor, has_next_page) from SSR marketplace feed."""
    m = _PAGE_INFO_RE.search(html) or _PAGE_INFO_RE_ALT.search(html)
    if not m:
        # Fallback: unordered has_next only.
        hn = re.search(r'"has_next_page"\s*:\s*(true|false)', html, re.I)
        return None, (hn.group(1).lower() == "true") if hn else False
    if m.re is _PAGE_INFO_RE:
        raw_cursor, has_next = m.group(1), m.group(2)
    else:
        has_next, raw_cursor = m.group(1), m.group(2)
    try:
        cursor = json.loads(f'"{raw_cursor}"')
    except ValueError:
        cursor = raw_cursor.encode("utf-8").decode("unicode_escape")
    return safe_str(cursor), has_next.lower() == "true"


def _encode_cursor(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_cursor(cursor: str) -> dict[str, Any] | None:
    if not cursor:
        return None
    pad = "=" * (-len(cursor) % 4)
    try:
        raw = base64.urlsafe_b64decode(cursor + pad)
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) and data.get("v") == 1 else None


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


def _price_fields(price_obj: dict[str, Any]) -> dict[str, Any]:
    price_fmt = safe_str(
        price_obj.get("formatted_amount_zeros_stripped") or price_obj.get("formatted_amount")
    )
    amount = safe_float(price_obj.get("amount"))
    # Minor units (cents): Facebook's amount_with_offset_in_currency.
    offset = safe_int(price_obj.get("amount_with_offset_in_currency"))
    currency = safe_str(price_obj.get("currency"))
    if not currency and price_fmt and price_fmt.startswith("$"):
        currency = "USD"
    return {
        "price": amount,
        "priceFormatted": price_fmt,
        "priceAmount": offset,
        "currency": currency,
    }


def _map_listing(node: dict[str, Any]) -> dict[str, Any] | None:
    lid = safe_str(node.get("id"))
    title = safe_str(node.get("marketplace_listing_title") or node.get("custom_title"))
    if not lid or not title:
        return None
    price_obj = node.get("listing_price") if isinstance(node.get("listing_price"), dict) else {}
    strike = (
        node.get("strikethrough_price")
        if isinstance(node.get("strikethrough_price"), dict)
        else {}
    )
    loc = node.get("location") if isinstance(node.get("location"), dict) else {}
    geo = loc.get("reverse_geocode") if isinstance(loc.get("reverse_geocode"), dict) else {}
    city = safe_str(geo.get("city"))
    state = safe_str(geo.get("state"))
    loc_display = ", ".join(p for p in (city, state) if p) or None
    city_page = geo.get("city_page") if isinstance(geo.get("city_page"), dict) else {}
    photos = _photo_uris(node)
    delivery = node.get("delivery_types")
    if not isinstance(delivery, list) or not delivery:
        delivery = None
    strike_fields = _price_fields(strike) if strike else {}
    return strip_empty(
        {
            "platform": "facebook",
            "id": lid,
            "title": title,
            "url": item_url(lid),
            **_price_fields(price_obj),
            "strikethroughPrice": strike_fields.get("price"),
            "strikethroughPriceFormatted": strike_fields.get("priceFormatted"),
            "strikethroughPriceAmount": strike_fields.get("priceAmount"),
            "categoryId": safe_str(node.get("marketplace_listing_category_id")),
            "location": loc_display,
            "city": city,
            "state": state,
            "cityPageId": safe_str(city_page.get("id")),
            "isSold": bool(node.get("is_sold")) if node.get("is_sold") is not None else None,
            "isLive": bool(node.get("is_live")) if node.get("is_live") is not None else None,
            "isPending": bool(node.get("is_pending")) if node.get("is_pending") is not None else None,
            "isHidden": bool(node.get("is_hidden")) if node.get("is_hidden") is not None else None,
            "isViewerSeller": (
                bool(node.get("is_viewer_seller"))
                if node.get("is_viewer_seller") is not None
                else None
            ),
            "deliveryTypes": delivery,
            "image": photos[0] if photos else None,
            # Cover photo(s) from the search card — not the full gallery.
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
    strike = (
        node.get("strikethrough_price")
        if isinstance(node.get("strikethrough_price"), dict)
        else {}
    )
    desc = node.get("redacted_description") if isinstance(node.get("redacted_description"), dict) else {}
    loc_text = node.get("location_text") if isinstance(node.get("location_text"), dict) else {}
    coords = node.get("location") if isinstance(node.get("location"), dict) else {}
    if coords.get("latitude") is None:
        item_loc = node.get("item_location") if isinstance(node.get("item_location"), dict) else {}
        if item_loc.get("latitude") is not None:
            coords = item_loc
    photos = _photo_uris(node)
    delivery = node.get("delivery_types")
    if not isinstance(delivery, list):
        delivery = []
    strike_fields = _price_fields(strike) if strike else {}
    return strip_empty(
        {
            "platform": "facebook",
            "id": lid,
            "url": safe_str(node.get("share_uri")) or url or item_url(lid),
            "title": title,
            "description": safe_str(desc.get("text")),
            **_price_fields(price),
            "strikethroughPrice": strike_fields.get("price"),
            "strikethroughPriceFormatted": strike_fields.get("priceFormatted"),
            "strikethroughPriceAmount": strike_fields.get("priceAmount"),
            "categoryId": safe_str(node.get("marketplace_listing_category_id")),
            "condition": _condition_label(node),
            "location": safe_str(loc_text.get("text")),
            "latitude": coords.get("latitude"),
            "longitude": coords.get("longitude"),
            "isSold": bool(node.get("is_sold")) if node.get("is_sold") is not None else None,
            "isLive": bool(node.get("is_live")) if node.get("is_live") is not None else None,
            "isPending": bool(node.get("is_pending")) if node.get("is_pending") is not None else None,
            "isHidden": bool(node.get("is_hidden")) if node.get("is_hidden") is not None else None,
            "deliveryTypes": delivery,
            "image": photos[0] if photos else None,
            "photos": photos or None,
            "createdAt": _created_at(node),
        }
    )


async def _fetch_search_html(url: str, *, scroll: bool) -> tuple[int, str] | None:
    actions = _SCROLL_ACTIONS if scroll else None
    got = await decodo_fetch.fetch_url(
        url,
        timeout=120.0 if not scroll else 150.0,
        headless="html",
        browser_actions=actions,
    )
    if got:
        return got
    if scroll:
        # Scroll path sometimes 400s; fall back to plain SSR.
        return await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    return None


async def marketplace_search_native(
    q: str,
    location: str,
    limit: int,
    *,
    filters: dict[str, str] | None = None,
    cursor: str | None = None,
) -> dict[str, Any] | None:
    """Search Marketplace. Returns ``{listings, hasMore, nextCursor}`` or None."""
    if limit <= 0:
        return {"listings": [], "hasMore": False, "nextCursor": None}
    if not decodo_fetch.enabled():
        return None

    skip = 0
    end_cursor_in: str | None = None
    if cursor:
        decoded = _decode_cursor(cursor)
        if not decoded:
            return {"listings": [], "hasMore": False, "nextCursor": None}
        # Cursor is page-offset within SSR/scroll results for the same query.
        skip = max(0, safe_int(decoded.get("skip")) or 0)
        end_cursor_in = safe_str(decoded.get("ec"))
        # Re-bind filters from the cursor so page 2 matches page 1.
        if isinstance(decoded.get("f"), dict):
            filters = {str(k): str(v) for k, v in decoded["f"].items()}

    url = search_url(q, location, filters=filters)
    if not url:
        return None

    # Need more than a typical first paint (~15–24) → try scroll once.
    need = skip + limit
    got = await _fetch_search_html(url, scroll=need > 20)
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

    page_cursor, has_next = _extract_page_info(body)
    if end_cursor_in and not page_cursor:
        page_cursor = end_cursor_in

    window = mapped[skip : skip + limit]
    next_skip = skip + len(window)
    # Only page within the SSR/scroll payload we actually fetched. Facebook's
    # feed has_next_page needs a session-bound GraphQL cursor we can't replay
    # across Decodo calls — don't advertise hasMore we can't serve.
    more_in_page = next_skip < len(mapped)
    next_cursor = None
    if more_in_page and window:
        next_cursor = _encode_cursor(
            {
                "v": 1,
                "q": q,
                "loc": location,
                "f": filters or {},
                "skip": next_skip,
                "ec": page_cursor,
            }
        )

    log.info(
        "fb_marketplace_search_ok",
        n=len(window),
        total_nodes=len(mapped),
        skip=skip,
        has_more=more_in_page,
        fb_has_next=has_next,
        filters=bool(filters),
    )
    return {
        "listings": window,
        "hasMore": more_in_page,
        "nextCursor": next_cursor,
    }


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
        "priceAmount",
        "currency",
        "strikethroughPrice",
        "strikethroughPriceFormatted",
        "strikethroughPriceAmount",
        "categoryId",
        "isSold",
        "isLive",
        "isPending",
        "isHidden",
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
    q: str,
    location: str,
    limit: int,
    *,
    filters: dict[str, str] | None = None,
    cursor: str | None = None,
) -> dict[str, Any] | None:
    """List search + per-item Decodo enrich (description / coords / full photos)."""
    page = await marketplace_search_native(
        q, location, limit, filters=filters, cursor=cursor
    )
    if page is None:
        return None
    listings = page.get("listings") or []
    if not listings:
        return page

    sem = asyncio.Semaphore(_ENRICH_CONCURRENCY)

    async def _enrich(row: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            detail = await marketplace_item_native(safe_str(row.get("url")) or "")
        if detail:
            return _merge_detail_into_listing(row, detail)
        return row

    enriched = list(await asyncio.gather(*[_enrich(row) for row in listings]))
    return {
        "listings": enriched,
        "hasMore": page.get("hasMore"),
        "nextCursor": page.get("nextCursor"),
    }


def credits_for_details(n: int) -> int:
    """Search fetch + one item fetch per returned listing."""
    if n <= 0:
        return CREDIT_FB_MARKETPLACE_NATIVE
    return CREDIT_FB_MARKETPLACE_NATIVE + CREDIT_FB_MARKETPLACE_ITEM_NATIVE * n
