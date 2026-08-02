"""Amazon seller storefront endpoint.

Scrapes third-party seller storefronts (``/sp?seller=``, ``/s?me=``, raw seller
IDs) — not influencer Amazon Shops (``amazon.com/shop/<handle>``). Those are a
different Amazon surface (creator vitrines) and are out of scope here.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.services import amazon_shop_native
from app.utils.formatters import safe_float, safe_int, safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

# Native storefront HTML ≈ $0.002/page via DC proxy. 120% markup @ $0.0045/credit
# → ~1 credit/page (~16 products). Was 4.45/result on Apify.
CREDIT_PER_PAGE = 1
NATIVE_PAGE_SIZE = amazon_shop_native.PAGE_SIZE


def _credits_for_limit(limit: int) -> int:
    if limit <= 0:
        return CREDIT_PER_PAGE
    return max(CREDIT_PER_PAGE, math.ceil(limit / NATIVE_PAGE_SIZE) * CREDIT_PER_PAGE)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _canonical_product_url(item: dict[str, Any], marketplace: str) -> str | None:
    asin = safe_str(item.get("asin") or item.get("ASIN"))
    if asin:
        return amazon_shop_native.canonical_product_url(asin, marketplace)
    raw = safe_str(item.get("url") or item.get("productUrl"))
    if not raw:
        return None
    # Strip tracking query /ref=… path noise when an ASIN is embedded.
    m = re.search(r"/dp/([A-Z0-9]{10})", raw, flags=re.I)
    if m:
        return amazon_shop_native.canonical_product_url(m.group(1).upper(), marketplace)
    return raw.split("?")[0] or raw


def _format_price(price: Any, currency: str | None, price_formatted: str | None) -> str | None:
    """Prefer Amazon's display string; otherwise build a readable fallback."""
    if price_formatted:
        # Reject our old non-display form "USD 5498".
        if not re.match(r"^[A-Z]{3}\s+\d", price_formatted):
            return price_formatted
    if price is None:
        return None
    try:
        num = float(price)
    except (TypeError, ValueError):
        return str(price)
    cur = (currency or "").upper()
    symbols = {"USD": "$", "GBP": "£", "EUR": "€", "JPY": "¥", "INR": "₹"}
    sym = symbols.get(cur)
    if sym:
        if num == int(num) and cur in {"USD", "EUR", "GBP"}:
            # Keep cents when present; whole dollars get grouping.
            whole = int(num)
            return f"{sym}{whole:,}"
        if cur == "JPY":
            return f"{sym}{int(num):,}"
        return f"{sym}{num:,.2f}"
    if cur:
        return f"{cur} {num:,.2f}".rstrip("0").rstrip(".")
    return f"{num:,.2f}".rstrip("0").rstrip(".")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _normalize_product(item: dict[str, Any], marketplace: str) -> dict[str, Any]:
    price = item.get("price")
    if price is None:
        price = item.get("priceValue")
    try:
        price_num = float(price) if price is not None else None
    except (TypeError, ValueError):
        price_num = safe_float(price)

    currency = safe_str(item.get("currency") or item.get("currencyCode"))
    price_formatted = _format_price(
        price_num,
        currency,
        safe_str(item.get("priceFormatted") or item.get("priceText")),
    )
    asin = safe_str(item.get("asin") or item.get("ASIN"))
    # Stable shape: always include price/flags keys (null when unknown).
    return {
        "asin": asin,
        "title": safe_str(item.get("title") or item.get("name")),
        "url": _canonical_product_url(item, marketplace),
        "image": safe_str(item.get("image") or item.get("imageUrl")),
        "price": price_num,
        "currency": currency,
        "priceFormatted": price_formatted,
        "rating": safe_float(item.get("rating") or item.get("stars")),
        "reviews": safe_int(item.get("reviews") or item.get("reviewsCount") or item.get("reviewCount")),
        "isPrime": _as_bool(item.get("isPrime")),
        "isBestSeller": _as_bool(item.get("isBestSeller") or item.get("bestSeller")),
        "isSponsored": _as_bool(item.get("isSponsored") or item.get("sponsored")),
    }


def _normalize_shop(
    items: list[dict[str, Any]],
    *,
    url: str,
    marketplace: str,
    seller: dict[str, Any] | None = None,
    scraped_at: str | None = None,
    has_more: bool = False,
    next_cursor: str | None = None,
) -> dict[str, Any]:
    first = items[0] if items else {}
    products = [_normalize_product(i, marketplace) for i in items if i.get("asin") or i.get("title")]

    seller_src = first.get("seller") if isinstance(first.get("seller"), dict) else first
    seller_out: dict[str, Any] = {
        "id": safe_str(
            (seller or {}).get("id")
            or seller_src.get("sellerId")
            or seller_src.get("seller_id")
            or seller_src.get("id")
        ),
        "name": safe_str(
            (seller or {}).get("name")
            or seller_src.get("sellerName")
            or seller_src.get("seller_name")
            or seller_src.get("storeName")
            or seller_src.get("brand")
        ),
        "url": safe_str(
            (seller or {}).get("url")
            or seller_src.get("sellerUrl")
            or seller_src.get("storefrontUrl")
        ),
    }
    if not seller_out.get("url") and seller_out.get("id"):
        seller_out["url"] = amazon_shop_native.seller_profile_url(seller_out["id"], marketplace)
    # Drop empty optional seller fields; keep id when present.
    if not seller_out.get("name"):
        seller_out.pop("name", None)
    if not seller_out.get("url"):
        seller_out.pop("url", None)
    if not seller_out.get("id"):
        seller_out.pop("id", None)

    scraped = (
        scraped_at
        or safe_str(first.get("scrapedAt") or first.get("scraped_at"))
        or _now_iso()
    )
    return {
        "platform": "amazon_shop",
        "url": safe_str(url),
        "marketplace": marketplace.upper(),
        "seller": seller_out,
        "scrapedAt": scraped,
        "totalReturned": len(products),
        "hasMore": bool(has_more),
        "nextCursor": next_cursor,
        "products": products,
    }


def _parse_cursor(cursor: str | None) -> tuple[int, int]:
    """Return (storefront_page, offset_within_page)."""
    if not cursor:
        return 1, 0
    raw = cursor.strip()
    if raw.lower().startswith("p:"):
        raw = raw[2:]
    page_raw, _, offset_raw = raw.partition(":")
    try:
        page = int(page_raw)
        offset = int(offset_raw) if offset_raw else 0
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        ) from exc
    if page < 1 or offset < 0:
        raise HTTPException(status_code=400, detail="Invalid cursor.")
    return page, offset


def _next_cursor(*, page: int, offset: int, returned: int, page_len: int, page_full: bool) -> str | None:
    """Advance within the current Amazon page, then to the next page when full."""
    consumed = offset + returned
    if consumed < page_len:
        return f"{page}:{consumed}"
    if page_full:
        return str(page + 1)
    return None


@router.get("/page", summary="Amazon seller storefront page")
async def amazon_shop_page(
    url: str = Query(
        ...,
        description=(
            "Amazon seller storefront URL (/sp?seller=… or /s?me=…) or raw seller ID "
            "(e.g. A294P4X9EWVXLJ). Not influencer Amazon Shops (/shop/<handle>) — "
            "those are a different surface."
        ),
    ),
    marketplace: str = Query("US", min_length=2, max_length=5),
    limit: int = Query(
        20,
        ge=0,
        le=200,
        description="Max products to include on this page fetch. Use 0 for seller metadata only.",
    ),
    cursor: str | None = Query(
        None,
        description="Pagination cursor from a previous nextCursor (storefront page number).",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    detected = detect_url_platform(url)
    if detected and detected != "amazon_shop":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                url, "amazon_shop", "https://www.amazon.com/sp?seller=A294P4X9EWVXLJ"
            ),
        )
    if amazon_shop_native.is_influencer_shop_url(url):
        raise HTTPException(
            status_code=400,
            detail=(
                "This endpoint scrapes Amazon seller storefronts (/sp?seller= or /s?me=), "
                "not influencer Amazon Shops (/shop/<handle>). Pass a seller ID or seller "
                "profile URL."
            ),
        )
    if not amazon_shop_native.extract_seller_id(url):
        raise HTTPException(
            status_code=400,
            detail="Could not find an Amazon seller ID. Pass /sp?seller=…, /s?me=…, or a raw seller ID.",
        )

    page, offset = _parse_cursor(cursor)
    settings = get_settings()
    cost = _credits_for_limit(limit if limit > 0 else NATIVE_PAGE_SIZE)
    async with billed_call(
        caller=caller,
        endpoint="/v1/amazon-shop/page",
        platform="amazon_shop",
        resource_url=url,
        base_credits=cost,
    ) as ctx:

        async def _run() -> dict[str, Any]:
            max_products = limit if limit > 0 else 0
            market = marketplace.upper()

            # Walk storefront pages from ``page``/``offset`` until ``limit`` is filled.
            first = await amazon_shop_native.fetch_shop_products(
                url,
                marketplace=market,
                limit=NATIVE_PAGE_SIZE if max_products > 0 else 0,
                page=page,
            )
            if first is not None:
                ctx["source"] = "direct"
                seller_id = first.get("seller_id") or amazon_shop_native.extract_seller_id(url) or ""
                profile = await amazon_shop_native.fetch_seller_profile(seller_id, market)
                seller = {
                    "id": seller_id,
                    "name": profile.get("name"),
                    "url": profile.get("url") or amazon_shop_native.seller_profile_url(seller_id, market),
                }
                scraped_at = first.get("scraped_at") or _now_iso()
                if max_products == 0:
                    return _normalize_shop(
                        [],
                        url=url,
                        marketplace=market,
                        seller=seller,
                        scraped_at=scraped_at,
                        has_more=False,
                        next_cursor=None,
                    )

                page_items = list(first.get("items") or [])
                if page_items:
                    collected: list[dict[str, Any]] = []
                    cur_page = page
                    cur_offset = offset
                    page_full = len(page_items) >= NATIVE_PAGE_SIZE
                    while True:
                        chunk = page_items[cur_offset:]
                        need = max_products - len(collected)
                        take = chunk[:need]
                        collected.extend(take)
                        if len(collected) >= max_products:
                            nxt = _next_cursor(
                                page=cur_page,
                                offset=cur_offset,
                                returned=len(take),
                                page_len=len(page_items),
                                page_full=page_full,
                            )
                            return _normalize_shop(
                                collected,
                                url=url,
                                marketplace=market,
                                seller=seller,
                                scraped_at=scraped_at,
                                has_more=bool(nxt),
                                next_cursor=nxt,
                            )
                        if not page_full:
                            return _normalize_shop(
                                collected,
                                url=url,
                                marketplace=market,
                                seller=seller,
                                scraped_at=scraped_at,
                                has_more=False,
                                next_cursor=None,
                            )
                        cur_page += 1
                        cur_offset = 0
                        nxt_native = await amazon_shop_native.fetch_shop_products(
                            url,
                            marketplace=market,
                            limit=NATIVE_PAGE_SIZE,
                            page=cur_page,
                        )
                        if not nxt_native or not nxt_native.get("items"):
                            return _normalize_shop(
                                collected,
                                url=url,
                                marketplace=market,
                                seller=seller,
                                scraped_at=scraped_at,
                                has_more=False,
                                next_cursor=None,
                            )
                        page_items = list(nxt_native.get("items") or [])
                        page_full = len(page_items) >= NATIVE_PAGE_SIZE
                        if nxt_native.get("scraped_at"):
                            scraped_at = nxt_native["scraped_at"]

            # Apify last resort (single page of maxProducts; no storefront cursor).
            try:
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_AMAZON_SHOP,
                    {
                        "sellerUrls": [url],
                        "marketplace": market,
                        "maxProducts": max(max_products, 1),
                    },
                    max_items=max(max_products, 1),
                )
            except (ApifyError, httpx.HTTPError):
                items = []
            if items:
                ctx["source"] = "apify"
                seller_id = amazon_shop_native.extract_seller_id(url) or ""
                first = items[0] if isinstance(items[0], dict) else {}
                seller = {
                    "id": safe_str(first.get("sellerId") or seller_id),
                    "name": safe_str(first.get("sellerName") or first.get("storeName")),
                    "url": amazon_shop_native.seller_profile_url(seller_id, market) if seller_id else None,
                }
                scraped = safe_str(first.get("scrapedAt")) or _now_iso()
                return _normalize_shop(
                    items[: max(max_products, 1)],
                    url=url,
                    marketplace=market,
                    seller=seller,
                    scraped_at=scraped,
                    has_more=False,
                    next_cursor=None,
                )

            raise HTTPException(status_code=404, detail="Amazon seller storefront not found")

        data = await cached_or_run(
            "amazon-shop.page",
            {
                "url": url,
                "marketplace": marketplace.upper(),
                "limit": limit,
                "cursor": cursor or "",
                "v": 5,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        n = int(data.get("totalReturned") or 0)
        ctx["credits_override"] = _credits_for_limit(n if limit > 0 else NATIVE_PAGE_SIZE)
        return ApiResponse(data=data)
