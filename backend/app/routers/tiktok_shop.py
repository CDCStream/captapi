"""TikTok Shop endpoints."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import detect_url_platform, extract_tiktok_username, platform_mismatch_detail

router = APIRouter()

RATE_SHOP = 2.8
RATE_REVIEWS = 2.25


def _scaled(limit: int, rate: float, minimum: int = 2) -> int:
    return max(minimum, math.ceil(limit * rate))


def _reject_non_tiktok_url(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "tiktok":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "tiktok", example),
        )


def _normalize_product(item: dict[str, Any]) -> dict[str, Any]:
    # Sellers come nested (seller/shop/store/store_info) or flat (shopId/shopName).
    seller = item.get("seller") or item.get("shop") or item.get("store") or item.get("store_info") or {}
    if not isinstance(seller, dict):
        seller = {}
    price = item.get("price") or item.get("salePrice") or item.get("currentPrice") or item.get("productPrice")
    currency = item.get("currency") or item.get("productCurrency")
    if isinstance(price, dict):
        # cunning_soil details actor: {"min_price": "$18.99", "max_price": ..., "currency": "USD"}
        currency = currency or price.get("currency")
        price = price.get("min_price") or price.get("price") or price.get("max_price")
    images = item.get("images")
    first_image = images[0] if isinstance(images, list) and images else None
    return {
        "platform": "tiktok_shop",
        "id": safe_str(item.get("id") or item.get("productId") or item.get("product_id")),
        "url": safe_str(item.get("url") or item.get("productUrl") or item.get("product_url")),
        "title": safe_str(item.get("title") or item.get("name") or item.get("productName") or item.get("productTitle")),
        "description": safe_str(item.get("description")),
        "price": price,
        "originalPrice": item.get("originalPrice"),
        "currency": safe_str(currency),
        "discount": safe_str(item.get("discountPercent") or item.get("discount")),
        "rating": item.get("rating") or item.get("reviewRating"),
        "reviews": safe_int(item.get("reviews") or item.get("reviewCount")),
        "sold": safe_int(item.get("sold") or item.get("soldCount") or item.get("unitsSold") or item.get("sales_count")),
        "stock": safe_int(item.get("stock")),
        "image": safe_str(
            item.get("image")
            or item.get("imageUrl")
            or item.get("thumbnail")
            or item.get("primaryImage")
            or item.get("productImage")
            or first_image
        ),
        "seller": {
            "id": safe_str(seller.get("id") or seller.get("sellerId") or item.get("shopId")),
            "name": safe_str(seller.get("name") or seller.get("sellerName") or seller.get("shopName") or item.get("shopName")),
            "url": safe_str(seller.get("url") or seller.get("shopUrl")),
            "rating": seller.get("rating"),
        },
    }


def _review_timestamp(item: dict[str, Any]) -> str | None:
    raw = item.get("createdAt") or item.get("date") or item.get("review_time")
    if isinstance(raw, str) and raw.isdigit():
        raw = int(raw)
    if isinstance(raw, (int, float)) and raw > 0:
        seconds = raw / 1000 if raw > 10_000_000_000 else raw
        return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()
    return safe_str(raw)


def _normalize_review(item: dict[str, Any]) -> dict[str, Any]:
    user = item.get("user") or item.get("author") or {}
    return {
        "platform": "tiktok_shop",
        "id": safe_str(item.get("id") or item.get("reviewId") or item.get("review_id")),
        "rating": item.get("rating") or item.get("stars") or item.get("review_rating"),
        "text": safe_str(item.get("text") or item.get("content") or item.get("review") or item.get("review_text")),
        "createdAt": _review_timestamp(item),
        "author": {
            "name": safe_str(
                user.get("name") or user.get("nickname") or item.get("authorName") or item.get("reviewer_name")
            ),
            "avatar": safe_str(user.get("avatar") or user.get("avatarUrl")),
        },
        "images": item.get("images") or item.get("review_images") or [],
        "verifiedPurchase": item.get("is_verified_purchase"),
        "sku": safe_str(item.get("sku_specification") or item.get("sku")),
        "country": safe_str(item.get("review_country") or item.get("country")),
    }


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
    cache: bool = Query(True, description="Set false to bypass the 24h cache and fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/shop-search", platform="tiktok_shop", resource_url=None, base_credits=_scaled(limit, RATE_SHOP)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("shop_search", {"searchKeywords": [q], "region": region.upper(), "maxResults": limit}, limit)
            products = [_normalize_product(i) for i in items]
            return {"query": q, "region": region.upper(), "totalReturned": len(products), "products": products}

        data = await cached_or_run("tiktok-shop.shop-search", {"q": q, "region": region, "limit": limit, "v": 2}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_SHOP)
        return ApiResponse(data=data)


@router.get("/shop-products", summary="List products from a TikTok Shop store")
async def shop_products(
    url: str = Query(..., description="TikTok Shop store URL"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(True, description="Set false to bypass the 24h cache and fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_non_tiktok_url(url, "https://www.tiktok.com/shop/store")
    if "tiktok" not in url or "shop" not in url:
        raise HTTPException(status_code=400, detail="Invalid TikTok Shop URL. Pass a TikTok Shop URL like https://www.tiktok.com/shop/store.")
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/shop-products", platform="tiktok_shop", resource_url=url, base_credits=_scaled(limit, RATE_SHOP)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("shop_catalog", {"shopUrls": [url], "maxResults": limit}, limit)
            products = [_normalize_product(i) for i in items]
            return {"url": url, "totalReturned": len(products), "products": products}

        data = await cached_or_run("tiktok-shop.shop-products", {"url": url, "limit": limit, "v": 2}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_SHOP)
        return ApiResponse(data=data)


@router.get("/product-details", summary="TikTok Shop product details")
async def product_details(
    url: str = Query(..., description="TikTok Shop product URL"),
    cache: bool = Query(True, description="Set false to bypass the 24h cache and fetch fresh data."),
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
                return _normalize_product({"productUrl": url, "productId": product_id})
            normalized = _normalize_product(items[0])
            normalized["url"] = normalized["url"] or url
            return normalized

        return ApiResponse(data=await cached_or_run("tiktok-shop.product-details", {"url": url, "v": 3}, _run, ctx, use_cache=cache))


@router.get("/product-reviews", summary="TikTok Shop product reviews")
async def product_reviews(
    url: str = Query(..., description="TikTok Shop product URL"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(True, description="Set false to bypass the 24h cache and fetch fresh data."),
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

        data = await cached_or_run("tiktok-shop.product-reviews", {"url": url, "limit": limit, "v": 2}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["reviews"]), RATE_REVIEWS)
        return ApiResponse(data=data)


@router.get("/user-showcase", summary="TikTok Shop creator showcase")
async def user_showcase(
    username: str = Query(..., description="TikTok username, with or without @"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(True, description="Set false to bypass the 24h cache and fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_non_tiktok_url(username, "https://www.tiktok.com/@username")
    handle = extract_tiktok_username(username) or username.strip().lstrip("@")
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid TikTok username")
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/user-showcase", platform="tiktok_shop", resource_url=f"https://www.tiktok.com/@{handle}", base_credits=_scaled(limit, RATE_REVIEWS)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("creator_showcase", {"usernames": [handle], "maxResults": limit}, limit)
            products = [_normalize_product(i) for i in items]
            return {"username": handle, "totalReturned": len(products), "products": products}

        data = await cached_or_run("tiktok-shop.user-showcase", {"username": handle, "limit": limit, "v": 2}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_REVIEWS)
        return ApiResponse(data=data)
