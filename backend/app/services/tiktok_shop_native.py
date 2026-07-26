"""Native TikTok Shop store catalog via SSR HTML (no Apify).

Store pages embed a Remix/loader JSON blob with ``component_data.products``.
Datacenter proxy usually returns the full page; residential/Decodo are
fallbacks. Search pages are WAF/captcha gated   keep those on Apify.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import unquote

import structlog

from app.services import decodo_fetch
from app.services.http_fetch import fetch, proxy_for

log = structlog.get_logger(__name__)

_SHOP_URL_RE = re.compile(
    r"(?:tiktok\.com|shop\.tiktok\.com)/shop/store/([^/?#]+)/(\d+)",
    re.IGNORECASE,
)
_SCRIPT_RE = re.compile(r"<script[^>]*>(.*?)</script>", re.S)

# Flat bill when native succeeds. One proxied HTML fetch is well under $0.001;
# at $0.0045/credit with 120% markup �! 1 credit; bill 2 for headroom.
CREDIT_SHOP_NATIVE = 2


def parse_shop_url(url: str) -> tuple[str | None, str | None]:
    """Return (shop_id, slug) from a store URL."""
    if not url:
        return None, None
    m = _SHOP_URL_RE.search(unquote(url.strip()))
    if not m:
        return None, None
    return m.group(2), m.group(1)


def _find_product_lists(obj: Any) -> list[list[dict[str, Any]]]:
    found: list[list[dict[str, Any]]] = []
    if isinstance(obj, dict):
        prods = obj.get("products")
        if (
            isinstance(prods, list)
            and prods
            and isinstance(prods[0], dict)
            and ("product_id" in prods[0] or "productId" in prods[0])
        ):
            found.append([p for p in prods if isinstance(p, dict)])
        for v in obj.values():
            found.extend(_find_product_lists(v))
    elif isinstance(obj, list):
        for v in obj[:80]:
            found.extend(_find_product_lists(v))
    return found


def extract_products_from_html(html: str) -> list[dict[str, Any]]:
    """Parse SSR script JSON and return the largest product list."""
    best: list[dict[str, Any]] = []
    for m in _SCRIPT_RE.finditer(html or ""):
        blob = (m.group(1) or "").strip()
        if not blob.startswith("{") or "product_id" not in blob:
            continue
        try:
            data = json.loads(blob)
        except ValueError:
            continue
        for prods in _find_product_lists(data):
            if len(prods) > len(best):
                best = prods
    return best


def _image_url(image: Any) -> str | None:
    if isinstance(image, str) and image.strip():
        return image.strip()
    if not isinstance(image, dict):
        return None
    urls = image.get("url_list") or image.get("urlList")
    if isinstance(urls, list) and urls:
        first = urls[0]
        if isinstance(first, str) and first.strip():
            return first.strip()
    uri = image.get("uri")
    return uri.strip() if isinstance(uri, str) and uri.strip() else None


def _product_url(raw: dict[str, Any], product_id: str) -> str | None:
    seo = raw.get("seo_url") if isinstance(raw.get("seo_url"), dict) else {}
    canonical = seo.get("canonical_url") or seo.get("canonicalUrl")
    if isinstance(canonical, str) and canonical.strip():
        can = canonical.strip()
        if "/pdp/" in can:
            parts = can.rstrip("/").split("/")
            pid = parts[-1] if parts else product_id
            slug = parts[-2] if len(parts) >= 2 else None
            if slug and str(pid).isdigit():
                return f"https://www.tiktok.com/shop/pdp/{slug}/{pid}"
            return f"https://www.tiktok.com/shop/pdp/{pid}"
        return can
    if product_id:
        return f"https://www.tiktok.com/shop/pdp/{product_id}"
    return None


def normalize_raw_product(
    raw: dict[str, Any],
    *,
    shop_id: str | None = None,
    shop_slug: str | None = None,
) -> dict[str, Any]:
    """Map SSR product dict to Apify-like fields for router._normalize_product."""
    product_id = str(raw.get("product_id") or raw.get("productId") or "").strip()
    price_info = raw.get("product_price_info") if isinstance(raw.get("product_price_info"), dict) else {}
    sold_info = raw.get("sold_info") if isinstance(raw.get("sold_info"), dict) else {}
    seller_info = raw.get("seller_info") if isinstance(raw.get("seller_info"), dict) else {}
    rate_info = raw.get("rate_info") if isinstance(raw.get("rate_info"), dict) else {}

    seller_id = str(
        seller_info.get("seller_id")
        or seller_info.get("shop_id")
        or seller_info.get("id")
        or shop_id
        or ""
    ).strip() or None
    seller_name = (
        seller_info.get("shop_name")
        or seller_info.get("seller_name")
        or seller_info.get("name")
        or (shop_slug.replace("-", " ").title() if shop_slug else None)
    )
    seller_url = None
    if seller_id and (shop_slug or seller_name):
        slug = shop_slug or re.sub(r"[^a-z0-9]+", "-", str(seller_name).lower()).strip("-")
        if slug:
            seller_url = f"https://www.tiktok.com/shop/store/{slug}/{seller_id}"

    sale = price_info.get("sale_price_decimal") or price_info.get("sale_price_format")
    origin = price_info.get("origin_price_decimal") or price_info.get("origin_price_format")
    try:
        price = float(sale) if sale not in (None, "") else None
    except (TypeError, ValueError):
        price = sale
    try:
        original = float(origin) if origin not in (None, "") else None
    except (TypeError, ValueError):
        original = origin

    return {
        "id": product_id or None,
        "productId": product_id or None,
        "title": raw.get("title") or raw.get("name"),
        "url": _product_url(raw, product_id),
        "price": price,
        "originalPrice": original,
        "currency": price_info.get("currency_name") or price_info.get("currency"),
        "discount": price_info.get("discount_format") or price_info.get("discount_decimal"),
        "sold": sold_info.get("sold_count"),
        "rating": rate_info.get("score"),
        "reviewCount": rate_info.get("review_count"),
        "image": _image_url(raw.get("image") or raw.get("transparent_image")),
        "seller": {
            "id": seller_id,
            "name": seller_name,
            "url": seller_url,
        },
        "shopId": seller_id,
        "shopName": seller_name,
    }


async def _fetch_html(url: str) -> str | None:
    for tier in ("datacenter", "residential"):
        if not proxy_for(tier):  # type: ignore[arg-type]
            continue
        try:
            resp = await fetch(url, tier=tier, timeout=25)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001
            log.debug("tiktok_shop_native_fetch_error", tier=tier, error=str(exc)[:120])
            continue
        if resp.status_code != 200:
            continue
        text = resp.text or ""
        if "product_id" in text:
            return text
    if decodo_fetch.enabled():
        for headless in (None, "html"):
            got = await decodo_fetch.fetch_url(url, timeout=90, headless=headless)
            if not got:
                continue
            status, body = got
            if status == 200 and body and "product_id" in body:
                return body
    return None


async def fetch_shop_products(url: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    """Fetch store catalog products natively.

    Returns Apify-shaped raw product dicts, or ``None`` when the page could not
    be fetched/parsed (caller should fall back to Apify).
    """
    if limit <= 0:
        return []
    shop_id, shop_slug = parse_shop_url(url)
    fetch_url = url.strip()
    if shop_id and shop_slug:
        fetch_url = f"https://www.tiktok.com/shop/store/{shop_slug}/{shop_id}"

    html = await _fetch_html(fetch_url)
    if not html:
        return None
    raw_products = extract_products_from_html(html)
    if not raw_products:
        log.info("tiktok_shop_native_no_products", url=fetch_url[:120])
        return None
    out = [
        normalize_raw_product(p, shop_id=shop_id, shop_slug=shop_slug)
        for p in raw_products[:limit]
    ]
    out = [p for p in out if p.get("id") or p.get("title")]
    if not out:
        return None
    log.info("tiktok_shop_native_ok", url=fetch_url[:120], n=len(out))
    return out
