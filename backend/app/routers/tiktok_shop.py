"""TikTok Shop endpoints."""

from __future__ import annotations

import math
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
    seller = item.get("seller") or item.get("shop") or item.get("store") or {}
    price = item.get("price") or item.get("salePrice") or item.get("currentPrice")
    return {
        "platform": "tiktok_shop",
        "id": safe_str(item.get("id") or item.get("productId") or item.get("product_id")),
        "url": safe_str(item.get("url") or item.get("productUrl") or item.get("product_url")),
        "title": safe_str(item.get("title") or item.get("name") or item.get("productName")),
        "description": safe_str(item.get("description")),
        "price": price,
        "currency": safe_str(item.get("currency")),
        "rating": item.get("rating") or item.get("reviewRating"),
        "reviews": safe_int(item.get("reviews") or item.get("reviewCount")),
        "sold": safe_int(item.get("sold") or item.get("soldCount") or item.get("unitsSold")),
        "image": safe_str(item.get("image") or item.get("imageUrl") or item.get("thumbnail")),
        "seller": {
            "id": safe_str(seller.get("id") or seller.get("sellerId")),
            "name": safe_str(seller.get("name") or seller.get("sellerName") or seller.get("shopName")),
            "url": safe_str(seller.get("url") or seller.get("shopUrl")),
            "rating": seller.get("rating"),
        },
    }


def _normalize_review(item: dict[str, Any]) -> dict[str, Any]:
    user = item.get("user") or item.get("author") or {}
    return {
        "platform": "tiktok_shop",
        "id": safe_str(item.get("id") or item.get("reviewId")),
        "rating": item.get("rating") or item.get("stars"),
        "text": safe_str(item.get("text") or item.get("content") or item.get("review")),
        "createdAt": safe_str(item.get("createdAt") or item.get("date")),
        "author": {
            "name": safe_str(user.get("name") or user.get("nickname") or item.get("authorName")),
            "avatar": safe_str(user.get("avatar") or user.get("avatarUrl")),
        },
        "images": item.get("images") or [],
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
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/shop-search", platform="tiktok_shop", resource_url=None, base_credits=_scaled(limit, RATE_SHOP)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("shop_search", {"searchKeywords": [q], "region": region.upper(), "maxResults": limit}, limit)
            products = [_normalize_product(i) for i in items]
            return {"query": q, "region": region.upper(), "totalReturned": len(products), "products": products}

        data = await cached_or_run("tiktok-shop.shop-search", {"q": q, "region": region, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_SHOP)
        return ApiResponse(data=data)


@router.get("/shop-products", summary="List products from a TikTok Shop store")
async def shop_products(
    url: str = Query(..., description="TikTok Shop store URL"),
    limit: int = Query(20, ge=1, le=200),
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

        data = await cached_or_run("tiktok-shop.shop-products", {"url": url, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_SHOP)
        return ApiResponse(data=data)


@router.get("/product-details", summary="TikTok Shop product details")
async def product_details(
    url: str = Query(..., description="TikTok Shop product URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_non_tiktok_url(url, "https://www.tiktok.com/shop/pdp/product/123")
    if "tiktok" not in url or "shop" not in url:
        raise HTTPException(status_code=400, detail="Invalid TikTok Shop product URL. Pass a TikTok Shop product URL like https://www.tiktok.com/shop/pdp/product/123.")
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/product-details", platform="tiktok_shop", resource_url=url, base_credits=14) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("product_details", {"productUrls": [url], "maxResults": 1}, 1)
            if not items:
                # Some TikTok Shop detail lookups return no enriched payload for
                # valid PDP URLs; keep the endpoint useful with canonical basics.
                product_id = url.rstrip("/").split("/")[-1]
                return _normalize_product({"productUrl": url, "productId": product_id})
            return _normalize_product(items[0])

        return ApiResponse(data=await cached_or_run("tiktok-shop.product-details", {"url": url}, _run, ctx))


@router.get("/product-reviews", summary="TikTok Shop product reviews")
async def product_reviews(
    url: str = Query(..., description="TikTok Shop product URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_non_tiktok_url(url, "https://www.tiktok.com/shop/pdp/product/123")
    if "tiktok" not in url or "shop" not in url:
        raise HTTPException(status_code=400, detail="Invalid TikTok Shop product URL. Pass a TikTok Shop product URL like https://www.tiktok.com/shop/pdp/product/123.")
    async with billed_call(caller=caller, endpoint="/v1/tiktok-shop/product-reviews", platform="tiktok_shop", resource_url=url, base_credits=_scaled(limit, RATE_REVIEWS)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _run_shop("product_reviews", {"productUrls": [url], "maxReviews": limit, "maxResults": limit}, limit)
            reviews = [_normalize_review(i) for i in items]
            return {"url": url, "totalReturned": len(reviews), "reviews": reviews}

        data = await cached_or_run("tiktok-shop.product-reviews", {"url": url, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["reviews"]), RATE_REVIEWS)
        return ApiResponse(data=data)


@router.get("/user-showcase", summary="TikTok Shop creator showcase")
async def user_showcase(
    username: str = Query(..., description="TikTok username, with or without @"),
    limit: int = Query(20, ge=1, le=200),
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

        data = await cached_or_run("tiktok-shop.user-showcase", {"username": handle, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["products"]), RATE_REVIEWS)
        return ApiResponse(data=data)
