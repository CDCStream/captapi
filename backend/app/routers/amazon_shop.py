"""Amazon Shop / storefront endpoint."""

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
from app.utils.formatters import safe_float, safe_int, safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()


def _normalize_product(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "asin": safe_str(item.get("asin") or item.get("ASIN")),
        "title": safe_str(item.get("title") or item.get("name")),
        "url": safe_str(item.get("url") or item.get("productUrl")),
        "image": safe_str(item.get("image") or item.get("imageUrl")),
        "price": item.get("price") or item.get("priceValue"),
        "priceFormatted": safe_str(item.get("priceFormatted") or item.get("priceText")),
        "rating": safe_float(item.get("rating") or item.get("stars")),
        "reviews": safe_int(item.get("reviews") or item.get("reviewsCount")),
        "availability": safe_str(item.get("availability")),
    }


def _normalize_shop(items: list[dict[str, Any]], url: str, marketplace: str) -> dict[str, Any]:
    first = items[0] if items else {}
    seller = first.get("seller") if isinstance(first.get("seller"), dict) else first
    products = [_normalize_product(i) for i in items]
    return {
        "platform": "amazon_shop",
        "url": safe_str(url),
        "marketplace": marketplace.upper(),
        "seller": {
            "id": safe_str(seller.get("sellerId") or seller.get("seller_id") or seller.get("id")),
            "name": safe_str(seller.get("sellerName") or seller.get("seller_name") or seller.get("name") or seller.get("brand")),
            "url": safe_str(seller.get("sellerUrl") or seller.get("storefrontUrl") or seller.get("url")),
            "rating": safe_float(seller.get("sellerRating") or seller.get("rating")),
            "reviewCount": safe_int(seller.get("sellerReviews") or seller.get("reviewCount")),
        },
        "totalReturned": len(products),
        "products": products,
        "rawFirstItem": first or None,
    }


@router.get("/page", summary="Amazon Shop / storefront page")
async def amazon_shop_page(
    url: str = Query(..., description="Amazon seller storefront URL, seller profile URL, or seller ID"),
    marketplace: str = Query("US", min_length=2, max_length=5),
    limit: int = Query(20, ge=0, le=200, description="Max products to include. Use 0 for shop metadata only when supported."),
    caller: ApiCaller = Depends(require_api_key),
):
    detected = detect_url_platform(url)
    if detected and detected != "amazon_shop":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "amazon_shop", "https://www.amazon.com/shop/storefront"),
        )
    settings = get_settings()
    async with billed_call(caller=caller, endpoint="/v1/amazon-shop/page", platform="amazon_shop", resource_url=url, base_credits=max(5, math.ceil(limit * 4.45))) as ctx:
        async def _run() -> dict[str, Any]:
            max_products = limit if limit > 0 else 1
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_AMAZON_SHOP,
                {"sellerUrls": [url], "marketplace": marketplace.upper(), "maxProducts": max_products},
                max_items=max_products,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Amazon Shop page not found")
            return _normalize_shop(items[:max_products], url, marketplace)

        data = await cached_or_run("amazon-shop.page", {"url": url, "marketplace": marketplace.upper(), "limit": limit}, _run, ctx)
        return ApiResponse(data=data)
