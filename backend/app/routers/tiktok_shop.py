"""TikTok Shop endpoints."""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_float, safe_int, safe_str
from app.utils.url import detect_url_platform, extract_tiktok_username, platform_mismatch_detail

router = APIRouter()

RATE_SHOP = 2.8
RATE_REVIEWS = 2.25


def _scaled(limit: int, rate: float, minimum: int = 2) -> int:
    if limit <= 0:
        return 0
    return max(minimum, math.ceil(limit * rate))


def _reject_non_tiktok_url(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "tiktok":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "tiktok", example),
        )


_SHOP_URL_RE = re.compile(r"/shop/store/([^/?#]+)/(\d+)", re.IGNORECASE)
_PRICE_RE = re.compile(r"[\d]+(?:[.,]\d+)?")


def _shop_slug(name: str) -> str | None:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or None


def _parse_shop_url(url: str | None) -> tuple[str | None, str | None]:
    """Return (shop_id, slug) from a TikTok Shop store URL."""
    if not url:
        return None, None
    m = _SHOP_URL_RE.search(url)
    if not m:
        return None, None
    return m.group(2), m.group(1)


def _coerce_price(value: Any) -> float | int | str | None:
    """Normalize prices to numbers when possible ('$17.98' → 17.98)."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    s = str(value).strip()
    if not s:
        return None
    m = _PRICE_RE.search(s.replace(",", ""))
    if not m:
        return safe_str(s)
    parsed = safe_float(m.group(0).replace(",", ""))
    return parsed if parsed is not None else safe_str(s)


def _normalize_product(
    item: dict[str, Any],
    *,
    search_mode: bool = False,
    catalog_mode: bool = False,
    details_mode: bool = False,
    showcase_mode: bool = False,
) -> dict[str, Any]:
    # Sellers come nested (seller/shop/store/store_info) or flat (shopId/shopName).
    seller = item.get("seller") or item.get("shop") or item.get("store") or item.get("store_info") or {}
    if not isinstance(seller, dict):
        seller = {}
    price = item.get("price") or item.get("salePrice") or item.get("currentPrice") or item.get("productPrice")
    currency = item.get("currency") or item.get("productCurrency")
    if isinstance(price, dict):
        # cunning_soil details actor: {"min_price": "$18.99", "max_price": ..., "currency": "USD"}
        currency = currency or price.get("currency")
        candidates = (price.get("min_price"), price.get("price"), price.get("max_price"))
        price = next((c for c in candidates if c not in (None, "")), None)
    price = _coerce_price(price)
    images = item.get("images")
    first_image = images[0] if isinstance(images, list) and images else None
    seller_url = safe_str(seller.get("url") or seller.get("shopUrl") or item.get("shopUrl"))
    shop_id_from_url, shop_slug_from_url = _parse_shop_url(seller_url)
    seller_id = safe_str(
        seller.get("id")
        or seller.get("sellerId")
        or seller.get("shop_id")
        or item.get("shopId")
        or item.get("shop_id")
        or item.get("seller_id")
        or shop_id_from_url
    )
    seller_name = safe_str(
        seller.get("name")
        or seller.get("sellerName")
        or seller.get("shopName")
        or item.get("shopName")
        or (shop_slug_from_url.replace("-", " ").title() if shop_slug_from_url else None)
    )
    if not seller_url and seller_id and seller_name:
        slug = _shop_slug(seller_name) or shop_slug_from_url
        if slug:
            seller_url = f"https://www.tiktok.com/shop/store/{slug}/{seller_id}"

    # Mode-specific omissions for fields the upstream actor never returns.
    include_description = not search_mode and not catalog_mode and not details_mode and not showcase_mode
    include_rating_reviews = not search_mode and not details_mode and not showcase_mode
    include_stock = not search_mode and not catalog_mode and not showcase_mode
    include_seller_rating = not search_mode and not catalog_mode and not showcase_mode
    include_list_pricing = not details_mode and not showcase_mode  # originalPrice / discount
    include_sold = not showcase_mode
    include_full_seller = not details_mode and not showcase_mode

    out: dict[str, Any] = {
        "platform": "tiktok_shop",
        "id": safe_str(item.get("id") or item.get("productId") or item.get("product_id")),
        "url": safe_str(item.get("url") or item.get("productUrl") or item.get("product_url")),
        "title": safe_str(
            item.get("title")
            or item.get("name")
            or item.get("productName")
            or item.get("productTitle")
        ),
    }
    if include_description:
        out["description"] = safe_str(
            item.get("description")
            or item.get("product_desc")
            or item.get("productDesc")
            or item.get("desc")
            or item.get("productDescription")
        )
    out["price"] = price
    if include_list_pricing:
        out["originalPrice"] = _coerce_price(
            item.get("originalPrice") or item.get("origin_price") or item.get("original_price")
        )
    out["currency"] = safe_str(currency)
    if include_list_pricing:
        out["discount"] = safe_str(item.get("discountPercent") or item.get("discount") or item.get("discount_rate"))
    if include_rating_reviews:
        out["rating"] = item.get("rating") or item.get("reviewRating") or item.get("product_rating")
        out["reviews"] = safe_int(item.get("reviews") or item.get("reviewCount") or item.get("review_count"))
    if include_sold:
        out["sold"] = safe_int(item.get("sold") or item.get("soldCount") or item.get("unitsSold") or item.get("sales_count"))
    if include_stock:
        out["stock"] = safe_int(item.get("stock") or item.get("stock_num") or item.get("inventory") or item.get("sku_stock"))
    out["image"] = safe_str(
        item.get("image")
        or item.get("imageUrl")
        or item.get("thumbnail")
        or item.get("primaryImage")
        or item.get("productImage")
        or first_image
    )
    if showcase_mode:
        # Creator showcase only exposes shopId — not store name/url/rating.
        if seller_id:
            out["seller"] = {"id": seller_id}
    elif include_full_seller:
        out["seller"] = {
            "id": seller_id,
            "name": seller_name,
            "url": seller_url,
        }
        if include_seller_rating:
            out["seller"]["rating"] = seller.get("rating")
    else:
        # Details actor only returns store name + rating.
        out["seller"] = {"name": seller_name}
        if include_seller_rating:
            out["seller"]["rating"] = seller.get("rating")
    return out


def _review_timestamp(item: dict[str, Any]) -> str | None:
    raw = item.get("createdAt") or item.get("date") or item.get("review_time")
    if isinstance(raw, str) and raw.isdigit():
        raw = int(raw)
    if isinstance(raw, (int, float)) and raw > 0:
        seconds = raw / 1000 if raw > 10_000_000_000 else raw
        return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()
    return safe_str(raw)


def _normalize_review(item: dict[str, Any]) -> dict[str, Any]:
    user = item.get("user") if isinstance(item.get("user"), dict) else None
    if user is None:
        user = item.get("author") if isinstance(item.get("author"), dict) else {}
    author_name = safe_str(
        user.get("name") or user.get("nickname") or item.get("authorName") or item.get("reviewer_name")
    )
    author_avatar = safe_str(user.get("avatar") or user.get("avatarUrl"))
    raw_images = item.get("images") or item.get("review_images") or []
    images = [img for img in raw_images if img] if isinstance(raw_images, list) else []
    out: dict[str, Any] = {
        "platform": "tiktok_shop",
        "id": safe_str(item.get("id") or item.get("reviewId") or item.get("review_id")),
        "rating": item.get("rating") or item.get("stars") or item.get("review_rating"),
        "text": safe_str(item.get("text") or item.get("content") or item.get("review") or item.get("review_text")),
        "createdAt": _review_timestamp(item),
        "verifiedPurchase": item.get("is_verified_purchase"),
        "sku": safe_str(item.get("sku_specification") or item.get("sku")),
        "country": safe_str(item.get("review_country") or item.get("country")),
    }
    # Review actor almost never returns reviewer identity / images — omit empty shells.
    if author_name or author_avatar:
        out["author"] = {"name": author_name, "avatar": author_avatar}
    if images:
        out["images"] = images
    return out


async def _run_shop(mode: str, payload: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    apify = get_apify()
    items = await apify.run_actor_sync(
        get_settings().APIFY_ACTOR_TIKTOK_SHOP,
        {"mode": mode, **payload},
        max_items=limit,
    )
    return items[:limit]


@router.get("/shop-search", summary="Search TikTok Shop products")
async def shop_search(
    q: str = Query(..., min_length=2, description="Product search query"),
    region: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/shop-search", platform="tiktok_shop", resource_url=None, base_credits=_scaled(limit, RATE_SHOP)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("shop_search", {"searchKeywords": [q], "region": region.upper(), "maxResults": limit}, limit)
            products = [_normalize_product(i, search_mode=True) for i in items]
            return {"query": q, "region": region.upper(), "totalReturned": len(products), "products": products}

        data = await cached_or_run("tiktok-shop.shop-search", {"q": q, "region": region, "limit": limit, "v": 3}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_SHOP)
        return ApiResponse(data=data)


@router.get("/shop-products", summary="List products from a TikTok Shop store")
async def shop_products(
    url: str = Query(..., description="TikTok Shop store URL"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_non_tiktok_url(url, "https://www.tiktok.com/shop/store")
    if "tiktok" not in url or "shop" not in url:
        raise HTTPException(status_code=400, detail="Invalid TikTok Shop URL. Pass a TikTok Shop URL like https://www.tiktok.com/shop/store.")
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/shop-products", platform="tiktok_shop", resource_url=url, base_credits=_scaled(limit, RATE_SHOP)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("shop_catalog", {"shopUrls": [url], "maxResults": limit}, limit)
            products = [_normalize_product(i, catalog_mode=True) for i in items]
            return {"url": url, "totalReturned": len(products), "products": products}

        data = await cached_or_run("tiktok-shop.shop-products", {"url": url, "limit": limit, "v": 3}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_SHOP)
        return ApiResponse(data=data)


@router.get("/product-details", summary="TikTok Shop product details")
async def product_details(
    url: str = Query(..., description="TikTok Shop product URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_non_tiktok_url(url, "https://www.tiktok.com/shop/pdp/product/123")
    if "tiktok" not in url or "shop" not in url:
        raise HTTPException(status_code=400, detail="Invalid TikTok Shop product URL. Pass a TikTok Shop product URL like https://www.tiktok.com/shop/pdp/product/123.")
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/product-details", platform="tiktok_shop", resource_url=url, base_credits=14) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            # The mobile-API details actor returns title/price/images/stock; the
            # generic shop scraper's product_details mode often echoes the URL only.
            items: list[dict[str, Any]] = []
            for _attempt in range(2):
                try:
                    items = await apify.run_actor_sync(
                        get_settings().APIFY_ACTOR_TIKTOK_SHOP_DETAILS,
                        {"productInput": url, "region": "US", "outputMode": "formatted_filtered"},
                        max_items=1,
                    )
                except Exception:  # noqa: BLE001
                    items = []
                if items and items[0].get("title"):
                    break
            if not items or not items[0].get("title"):
                items = await _run_shop("product_details", {"productUrls": [url], "maxResults": 1}, 1)
            if not items:
                # Keep the endpoint useful with canonical basics for valid PDP URLs.
                product_id = url.rstrip("/").split("/")[-1]
                return _normalize_product(
                    {"productUrl": url, "productId": product_id},
                    details_mode=True,
                )
            normalized = _normalize_product(items[0], details_mode=True)
            normalized["url"] = normalized["url"] or url
            return normalized

        return ApiResponse(data=await cached_or_run("tiktok-shop.product-details", {"url": url, "v": 4}, _run, ctx, use_cache=cache))


@router.get("/product-reviews", summary="TikTok Shop product reviews")
async def product_reviews(
    url: str = Query(..., description="TikTok Shop product URL"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_non_tiktok_url(url, "https://www.tiktok.com/shop/pdp/product/123")
    if "tiktok" not in url or "shop" not in url:
        raise HTTPException(status_code=400, detail="Invalid TikTok Shop product URL. Pass a TikTok Shop product URL like https://www.tiktok.com/shop/pdp/product/123.")
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/product-reviews", platform="tiktok_shop", resource_url=url, base_credits=_scaled(limit, RATE_REVIEWS)) as ctx:
        async def _run() -> dict[str, Any]:
            # Dedicated review actor first: the generic scraper's
            # product_reviews mode usually returns 0 rows.
            items: list[dict[str, Any]] = []
            try:
                items = await get_apify().run_actor_sync(
                    get_settings().APIFY_ACTOR_TIKTOK_SHOP_REVIEWS,
                    {"region": "US", "product_ids": [url], "reviews_limit": limit},
                    max_items=limit,
                )
            except Exception:  # noqa: BLE001 — fall through to the generic scraper
                items = []
            if not items:
                items = await _run_shop("product_reviews", {"productUrls": [url], "maxReviews": limit, "maxResults": limit}, limit)
            reviews = [_normalize_review(i) for i in items[:limit]]
            return {"url": url, "totalReturned": len(reviews), "reviews": reviews}

        data = await cached_or_run("tiktok-shop.product-reviews", {"url": url, "limit": limit, "v": 3}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["reviews"]), RATE_REVIEWS)
        return ApiResponse(data=data)


@router.get(
    "/user-showcase",
    summary="List products a TikTok creator promotes in their Shop showcase",
)
async def user_showcase(
    username: str = Query(
        ...,
        description="TikTok username, @handle, or profile URL, e.g. hydrojug or https://www.tiktok.com/@hydrojug",
    ),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_non_tiktok_url(username, "https://www.tiktok.com/@username")
    handle = extract_tiktok_username(username) or username.strip().lstrip("@")
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid TikTok username")
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/user-showcase", platform="tiktok_shop", resource_url=f"https://www.tiktok.com/@{handle}", base_credits=_scaled(limit, RATE_REVIEWS)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("creator_showcase", {"usernames": [handle], "maxResults": limit}, limit)
            products = [_normalize_product(i, showcase_mode=True) for i in items]
            return {"username": handle, "totalReturned": len(products), "products": products}

        data = await cached_or_run("tiktok-shop.user-showcase", {"username": handle, "limit": limit, "v": 3}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_REVIEWS)
        return ApiResponse(data=data)
