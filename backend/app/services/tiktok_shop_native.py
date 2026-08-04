"""Native TikTok Shop store catalog + PDP reviews via SSR HTML (no Apify).

Store pages embed a Remix/loader JSON blob with ``component_data.products``.
PDP pages embed a short ``product_reviews`` preview (~3 rows).
Datacenter proxy usually returns the full page; residential/Decodo are
fallbacks. Product details use PDP OG/SSR. Keyword search uses Google/DDG
SERP → PDP hydrate (Shop search HTML is WAF/captcha gated). Creator showcase
stays on Apify.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from urllib.parse import quote, unquote

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
# at $0.0045/credit with 120% markup → ~1 credit; bill 2 for headroom.
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


def _find_shop_info_dicts(obj: Any, *, depth: int = 0) -> list[dict[str, Any]]:
    """Walk SSR JSON for ``shopInfo`` / ``shop_info`` objects with sold_count."""
    found: list[dict[str, Any]] = []
    if depth > 12:
        return found
    if isinstance(obj, dict):
        for key in ("shopInfo", "shop_info"):
            cand = obj.get(key)
            if isinstance(cand, dict) and (
                cand.get("sold_count") is not None or cand.get("shop_rating") is not None
            ):
                found.append(cand)
        for v in obj.values():
            found.extend(_find_shop_info_dicts(v, depth=depth + 1))
    elif isinstance(obj, list):
        for v in obj[:60]:
            found.extend(_find_shop_info_dicts(v, depth=depth + 1))
    return found


def extract_shop_info_from_html(html: str) -> dict[str, Any] | None:
    """Parse store-page ``shopInfo`` (sold/followers/rating/productCount/…)."""
    best: dict[str, Any] | None = None
    best_score = -1
    for m in _SCRIPT_RE.finditer(html or ""):
        blob = (m.group(1) or "").strip()
        if not blob.startswith("{"):
            continue
        if "shop_rating" not in blob and "sold_count" not in blob:
            continue
        try:
            data = json.loads(blob)
        except ValueError:
            continue
        for info in _find_shop_info_dicts(data):
            score = sum(
                1
                for k in (
                    "sold_count",
                    "shop_rating",
                    "followers_count",
                    "on_sell_product_count",
                    "review_count",
                    "shop_name",
                )
                if info.get(k) not in (None, "", [])
            )
            if score > best_score:
                best = info
                best_score = score
    return best


def normalize_shop_info(
    raw: dict[str, Any] | None,
    *,
    shop_id: str | None = None,
    shop_slug: str | None = None,
    store_url: str | None = None,
    region: str | None = None,
) -> dict[str, Any] | None:
    """Map SSR shopInfo → Captapi shopInfo card."""
    if not isinstance(raw, dict) or not raw:
        return None
    sid = str(raw.get("seller_id") or raw.get("global_seller_id") or shop_id or "").strip() or None
    name = raw.get("shop_name") or raw.get("name")
    logo = _image_url(raw.get("shop_logo") or raw.get("logo"))
    scores_raw = raw.get("store_sub_score") or raw.get("storeSubScore") or []
    scores: list[dict[str, Any]] = []
    if isinstance(scores_raw, list):
        for row in scores_raw:
            if not isinstance(row, dict):
                continue
            scores.append(
                {
                    "score": row.get("score"),
                    "scorePercentage": str(row.get("score_percentage") or row.get("scorePercentage") or "")
                    or None,
                    "type": row.get("type"),
                }
            )
    rating = raw.get("shop_rating") or raw.get("rating")
    try:
        rating_f = float(rating) if rating not in (None, "") else None
    except (TypeError, ValueError):
        rating_f = None
    url = store_url
    if not url and sid and (shop_slug or name):
        slug = shop_slug or re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
        if slug:
            url = f"https://www.tiktok.com/shop/store/{slug}/{sid}"
    identity = (
        (raw.get("shop_identity_label") or {}).get("identity_label_text")
        if isinstance(raw.get("shop_identity_label"), dict)
        else raw.get("identity_label_text") or raw.get("identityLabel")
    )
    identity_s = str(identity or "").strip()
    region_out = (
        region
        or raw.get("region")
        or raw.get("path_region")
        or raw.get("sale_region")
    )
    out = {
        "id": sid,
        "name": name,
        "url": url,
        "logo": logo,
        "sold": int(raw["sold_count"])
        if str(raw.get("sold_count") or "").isdigit()
        else raw.get("sold_count"),
        "formatSold": raw.get("format_sold_count") or raw.get("formatSold"),
        "reviews": int(raw["review_count"])
        if str(raw.get("review_count") or "").isdigit()
        else raw.get("review_count"),
        "followers": int(raw["followers_count"])
        if str(raw.get("followers_count") or "").isdigit()
        else raw.get("followers_count"),
        "rating": rating_f,
        "productCount": raw.get("on_sell_product_count"),
        "videoCount": int(raw["video_count"])
        if str(raw.get("video_count") or "").isdigit()
        else raw.get("video_count"),
        "slogan": raw.get("shop_slogan") or raw.get("slogan"),
        "identityLabel": identity_s or None,
        "isOfficial": bool(identity_s and "official" in identity_s.lower()) if identity_s else None,
        "region": str(region_out).upper() if region_out else None,
        "storeScores": scores or None,
    }
    # Drop empty slogan/storeScores shells but keep numeric nulls via caller always-key.
    return {k: v for k, v in out.items() if v not in (None, "", [])}


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
    seo = raw.get("seo_url") if isinstance(raw.get("seo_url"), dict) else {}

    return {
        "id": product_id or None,
        "productId": product_id or None,
        "title": raw.get("title") or raw.get("name"),
        "url": _product_url(raw, product_id),
        "slug": seo.get("slug"),
        "price": price,
        "originalPrice": original,
        "currency": price_info.get("currency_name") or price_info.get("currency"),
        "discount": price_info.get("discount_format") or price_info.get("discount_decimal"),
        "savings": price_info.get("reduce_price_format"),
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
        "rate_info": rate_info,
        "sold_info": sold_info,
        "product_price_info": price_info,
        "seo_url": seo,
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
        if "product_id" in text or "review_id" in text:
            return text
    if decodo_fetch.enabled():
        for headless in (None, "html"):
            got = await decodo_fetch.fetch_url(url, timeout=90, headless=headless)
            if not got:
                continue
            status, body = got
            if status == 200 and body and ("product_id" in body or "review_id" in body):
                return body
    return None


async def fetch_shop_products(
    url: str,
    *,
    limit: int = 20,
    region: str | None = "US",
) -> dict[str, Any] | None:
    """Fetch store catalog + shopInfo natively.

    Returns ``{"products": [...], "shopInfo": {...}|None}``, or ``None`` when
    the page could not be fetched/parsed (caller should fall back to Apify).
    """
    if limit <= 0:
        return {"products": [], "shopInfo": None}
    shop_id, shop_slug = parse_shop_url(url)
    geo = (region or "US").strip().upper() or "US"
    fetch_url = url.strip()
    if shop_id and shop_slug:
        # Prefer regional shop host when caller asks for a market; US SSR is the
        # reliable path. Non-US may 404/empty even when search lists the shop.
        if geo == "US":
            fetch_url = f"https://www.tiktok.com/shop/store/{shop_slug}/{shop_id}"
        else:
            fetch_url = f"https://shop.tiktok.com/{geo.lower()}/store/{shop_slug}/{shop_id}"

    html = await _fetch_html(fetch_url)
    if not html and geo != "US" and shop_id and shop_slug:
        # Honest fallthrough: try the US store page rather than silent empty.
        fetch_url = f"https://www.tiktok.com/shop/store/{shop_slug}/{shop_id}"
        html = await _fetch_html(fetch_url)
        geo = "US"
    if not html:
        return None
    raw_products = extract_products_from_html(html)
    shop_info = normalize_shop_info(
        extract_shop_info_from_html(html),
        shop_id=shop_id,
        shop_slug=shop_slug,
        store_url=f"https://www.tiktok.com/shop/store/{shop_slug}/{shop_id}"
        if shop_id and shop_slug
        else fetch_url,
        region=geo,
    )
    if not raw_products:
        log.info("tiktok_shop_native_no_products", url=fetch_url[:120])
        # Still useful when shop card parsed but product list empty.
        if shop_info:
            return {"products": [], "shopInfo": shop_info}
        return None
    out = [
        normalize_raw_product(p, shop_id=shop_id, shop_slug=shop_slug)
        for p in raw_products[:limit]
    ]
    out = [p for p in out if p.get("id") or p.get("title")]
    if not out and not shop_info:
        return None
    log.info(
        "tiktok_shop_native_ok",
        url=fetch_url[:120],
        n=len(out),
        shop_sold=(shop_info or {}).get("sold"),
    )
    return {"products": out, "shopInfo": shop_info}


_PDP_URL_RE = re.compile(
    r'(?:tiktok\.com|shop\.tiktok\.com)/shop/pdp/(?:[^/?#]+/)?(\d+)',
    re.IGNORECASE,
)


def parse_product_url(url: str) -> str | None:
    if not url:
        return None
    m = _PDP_URL_RE.search(unquote(url.strip()))
    return m.group(1) if m else None


def _find_review_lists(obj: Any) -> list[list[dict[str, Any]]]:
    found: list[list[dict[str, Any]]] = []
    if isinstance(obj, dict):
        reviews = obj.get('product_reviews')
        if (
            isinstance(reviews, list)
            and reviews
            and isinstance(reviews[0], dict)
            and ('review_id' in reviews[0] or 'review_text' in reviews[0])
        ):
            found.append([r for r in reviews if isinstance(r, dict)])
        for v in obj.values():
            found.extend(_find_review_lists(v))
    elif isinstance(obj, list):
        for v in obj[:80]:
            found.extend(_find_review_lists(v))
    return found


def extract_reviews_from_html(html: str) -> list[dict[str, Any]]:
    best: list[dict[str, Any]] = []
    for m in _SCRIPT_RE.finditer(html or ''):
        blob = (m.group(1) or '').strip()
        if not blob.startswith('{') or 'review_id' not in blob:
            continue
        try:
            data = json.loads(blob)
        except ValueError:
            continue
        for reviews in _find_review_lists(data):
            if len(reviews) > len(best):
                best = reviews
    return best


def normalize_raw_review(raw: dict[str, Any]) -> dict[str, Any]:
    images = raw.get('review_images') or []
    if not isinstance(images, list):
        images = []
    display = raw.get('display_image_url')
    if display and not images:
        images = [display]
    return {
        'id': raw.get('review_id') or raw.get('reviewId'),
        'review_id': raw.get('review_id') or raw.get('reviewId'),
        'review_rating': raw.get('review_rating') or raw.get('rating'),
        'review_text': raw.get('review_text') or raw.get('text'),
        'review_time': raw.get('review_time') or raw.get('createdAt'),
        'is_verified_purchase': raw.get('is_verified_purchase'),
        'sku_specification': raw.get('sku_specification') or raw.get('sku'),
        'review_country': raw.get('review_country') or raw.get('country'),
        "reviewer_name": raw.get("reviewer_name"),
        "reviewer_avatar_url": raw.get("reviewer_avatar_url"),
        "review_images": images,
        "authorName": raw.get("reviewer_name"),
    }


async def fetch_product_reviews(url: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    """Fetch PDP review preview from SSR HTML.

    Returns Apify-shaped raw review dicts, or ``None`` when the page could not
    be fetched/parsed. SSR typically embeds ~3 reviews; deeper lists need Apify.
    """
    if limit <= 0:
        return []
    product_id = parse_product_url(url)
    fetch_url = url.strip()
    if product_id:
        fetch_url = f"https://www.tiktok.com/shop/pdp/{product_id}"

    html = await _fetch_html(fetch_url)
    if not html:
        return None
    raw = extract_reviews_from_html(html)
    if not raw:
        log.info("tiktok_shop_native_no_reviews", url=fetch_url[:120])
        return None
    out = [normalize_raw_review(r) for r in raw[:limit]]
    out = [r for r in out if r.get("id") or r.get("review_text")]
    if not out:
        return None
    log.info("tiktok_shop_native_reviews_ok", url=fetch_url[:120], n=len(out))
    return out



_PDP_ID_RE = re.compile(r"/pdp/(?:[^/?#]+/)?(\d{6,})", re.I)


def parse_product_id(url: str) -> str | None:
    raw = (url or "").strip()
    if not raw:
        return None
    m = _PDP_ID_RE.search(unquote(raw))
    if m:
        return m.group(1)
    tail = raw.rstrip("/").split("/")[-1]
    return tail if tail.isdigit() else None


def _og(html: str, key: str) -> str | None:
    patterns = [
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{re.escape(key)}["\']',
        rf'<meta\s+(?:property|name)=["\']{re.escape(key)}["\']\s+content=["\']([^"\']+)["\']',
        rf'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']{re.escape(key)}["\']',
    ]
    for pat in patterns:
        m = re.search(pat, html or "", re.I)
        if m:
            return m.group(1).strip() or None
    return None


async def _fetch_pdp_html(url: str) -> str | None:
    """Like ``_fetch_html`` but accept OG-only PDPs (no product_id JSON)."""
    for tier in ("datacenter", "residential"):
        if not proxy_for(tier):  # type: ignore[arg-type]
            continue
        try:
            resp = await fetch(url, tier=tier, timeout=25)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001
            log.debug("tiktok_shop_pdp_fetch_error", tier=tier, error=str(exc)[:120])
            continue
        if resp.status_code == 200 and resp.text and len(resp.text) > 2000:
            return resp.text
    if decodo_fetch.enabled():
        for headless in (None, "html"):
            got = await decodo_fetch.fetch_url(url, timeout=90, headless=headless)
            if not got:
                continue
            status, body = got
            if status == 200 and body and len(body) > 2000:
                return body
    return None


def _extract_balanced_json(s: str, start: int) -> str | None:
    """Return the JSON object starting at/after ``start`` (first ``{``)."""
    i = s.find("{", start)
    if i < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for j in range(i, len(s)):
        ch = s[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[i : j + 1]
    return None


def _image_urls(block: Any) -> list[str]:
    out: list[str] = []
    if isinstance(block, dict):
        urls = block.get("url_list")
        if isinstance(urls, list):
            for u in urls:
                if isinstance(u, str) and u.startswith("http") and u not in out:
                    out.append(u)
        elif isinstance(block.get("url"), str) and block["url"].startswith("http"):
            out.append(block["url"])
    elif isinstance(block, str) and block.startswith("http"):
        out.append(block)
    return out


def _parse_rich_description(raw: Any) -> str | None:
    """product_model.description is often a JSON array of text/ul blocks."""
    if isinstance(raw, str) and raw.strip().startswith("["):
        try:
            raw = json.loads(raw)
        except ValueError:
            return raw.strip() or None
    if isinstance(raw, str):
        return raw.strip() or None
    if not isinstance(raw, list):
        return None
    parts: list[str] = []
    for block in raw:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and block.get("text"):
            parts.append(str(block["text"]).strip())
        elif block.get("type") == "ul":
            for item in block.get("content") or []:
                if isinstance(item, str) and item.strip():
                    parts.append(f"• {item.strip()}")
    text = "\n".join(p for p in parts if p)
    return text or None


def _parse_product_info_blob(html: str) -> dict[str, Any] | None:
    """Pull ``component_data.product_info`` (product_model + promotion + seller)."""
    m = re.search(
        r'"component_data"\s*:\s*\{\s*"error_code"\s*:\s*0\s*,\s*"error_message"\s*:\s*"success"\s*,\s*"product_info"\s*:',
        html or "",
    )
    if not m:
        m = re.search(r'"product_info"\s*:\s*\{"product_model"', html or "")
        if not m:
            return None
        blob = _extract_balanced_json(html, m.end() - 1)
    else:
        blob = _extract_balanced_json(html, m.end() - 1)
    if not blob:
        return None
    try:
        data = json.loads(blob)
    except ValueError:
        return None
    return data if isinstance(data, dict) and isinstance(data.get("product_model"), dict) else None


def _promotion_pricing(promo: dict[str, Any] | None) -> dict[str, Any]:
    """Map promotion_product_price → price / originalPrice / discount / savings / sku prices."""
    out: dict[str, Any] = {
        "price": None,
        "originalPrice": None,
        "currency": None,
        "discount": None,
        "savings": None,
        "skuPrices": {},
    }
    if not isinstance(promo, dict):
        return out
    min_price = (promo.get("promotion_product_price") or {}).get("min_price")
    if not isinstance(min_price, dict):
        min_price = {}
    sale_raw = min_price.get("sale_price_decimal") or min_price.get("single_product_price_decimal")
    try:
        sale = float(sale_raw) if sale_raw not in (None, "", "*") else None
    except (TypeError, ValueError):
        sale = None
    out["price"] = sale
    out["currency"] = min_price.get("currency_name") or min_price.get("currency")
    ded = (min_price.get("promotion_deduction_details") or {}) if isinstance(
        min_price.get("promotion_deduction_details"), dict
    ) else {}
    ded_raw = ded.get("seller_subtotal_deduction_decimal") or ded.get("seller_subtotal_deduction")
    try:
        deduction = float(ded_raw) if ded_raw not in (None, "", "0", "0.0") else None
    except (TypeError, ValueError):
        deduction = None
    origin_raw = min_price.get("origin_price_decimal") or min_price.get("origin_price")
    try:
        origin = float(origin_raw) if origin_raw not in (None, "", "*") else None
    except (TypeError, ValueError):
        origin = None
    if origin is None and sale is not None and deduction is not None and deduction > 0:
        origin = round(sale + deduction, 2)
    out["originalPrice"] = origin
    if sale is not None and origin is not None and origin > sale:
        pct = round((1 - sale / origin) * 100)
        if pct > 0:
            out["discount"] = f"{pct}%"
        saved = round(origin - sale, 2)
        if saved > 0:
            out["savings"] = f"Saving ${saved:.2f}"
    dm = min_price.get("discount_format")
    if isinstance(dm, str) and dm.strip() and "*" not in dm:
        out["discount"] = dm.strip()
    skus_price = (promo.get("promotion_product_price") or {}).get("skus_price")
    if isinstance(skus_price, dict):
        for sid, row in skus_price.items():
            if not isinstance(row, dict):
                continue
            try:
                sp = float(row.get("sale_price_decimal")) if row.get("sale_price_decimal") not in (None, "", "*") else None
            except (TypeError, ValueError):
                sp = None
            out["skuPrices"][str(sid)] = sp
    return out


def _map_skus_from_model(
    skus_raw: list[Any],
    *,
    sku_prices: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], int | None]:
    skus_out: list[dict[str, Any]] = []
    stock_total = 0
    prices = sku_prices or {}
    for sku in skus_raw:
        if not isinstance(sku, dict):
            continue
        sid = str(sku.get("sku_id") or sku.get("id") or "")
        if not sid:
            continue
        qty_block = sku.get("sku_quantity") if isinstance(sku.get("sku_quantity"), dict) else {}
        try:
            qty = int(qty_block.get("available_quantity") if qty_block else sku.get("available_quantity") or 0)
        except (TypeError, ValueError):
            qty = 0
        stock_total += qty
        sale_props: list[dict[str, str]] = []
        for pair in sku.get("property_pairs") or []:
            if not isinstance(pair, dict):
                continue
            name = pair.get("sku_property_name") or pair.get("prop_name")
            value = pair.get("sku_property_value_name") or pair.get("prop_value")
            if name and value:
                sale_props.append({"propName": str(name), "propValue": str(value)})
        row: dict[str, Any] = {
            "id": sid,
            "stock": qty,
            "warehouseId": qty_block.get("warehouse_id") or sku.get("warehouse_id"),
            "status": sku.get("sku_status") or sku.get("status"),
            "saleProps": sale_props,
        }
        if sid in prices and prices[sid] is not None:
            row["price"] = prices[sid]
        limit = sku.get("purchase_limit") or sku.get("purchaseLimit")
        if limit is not None:
            row["purchaseLimit"] = limit
        skus_out.append(row)
    return skus_out, (stock_total if skus_out else None)


def _categories_from_html(html: str) -> list[dict[str, str]]:
    cats: list[dict[str, str]] = []
    seen: set[str] = set()
    for cid, name in re.findall(
        r'"category_id"\s*:\s*"(\d+)"\s*,\s*"category_name"\s*:\s*"((?:\\.|[^"\\])+)"',
        html or "",
    ):
        if cid in seen:
            continue
        seen.add(cid)
        try:
            label = json.loads(f'"{name}"')
        except ValueError:
            label = name
        cats.append({"id": cid, "name": label})
    return cats


def _product_from_info_blob(
    info: dict[str, Any],
    *,
    html: str,
    product_id: str,
    fetch_url: str,
) -> dict[str, Any] | None:
    pm = info.get("product_model") or {}
    if not isinstance(pm, dict):
        return None
    title = (pm.get("name") or "").strip() or None
    description = _parse_rich_description(pm.get("description"))
    images: list[str] = []
    for img in pm.get("images") or []:
        # Prefer the first CDN mirror per image object (url_list often repeats p16/p19).
        urls = _image_urls(img)
        if urls and urls[0] not in images:
            images.append(urls[0])
    pricing = _promotion_pricing(info.get("promotion_model") if isinstance(info.get("promotion_model"), dict) else None)
    skus, stock = _map_skus_from_model(pm.get("skus") or [], sku_prices=pricing.get("skuPrices"))
    review = info.get("review_model") if isinstance(info.get("review_model"), dict) else {}
    try:
        rating = float(review["product_overall_score"]) if review.get("product_overall_score") is not None else None
    except (TypeError, ValueError):
        rating = None
    try:
        review_count = int(review["product_review_count"]) if review.get("product_review_count") not in (None, "") else None
    except (TypeError, ValueError):
        review_count = None
    if rating == 0 and not review_count:
        rating = None
    try:
        sold = int(pm.get("sold_count")) if pm.get("sold_count") not in (None, "") else None
    except (TypeError, ValueError):
        sold = None

    seller_model = info.get("seller_model") if isinstance(info.get("seller_model"), dict) else {}
    seller_name = seller_model.get("shop_name")
    seller_id = str(pm.get("seller_id") or "") or None
    shop_link = None
    sl_m = re.search(r'"shop_link"\s*:\s*"((?:\\.|[^"\\])+)"', html)
    if sl_m:
        try:
            shop_link = json.loads(f'"{sl_m.group(1)}"')
        except ValueError:
            shop_link = sl_m.group(1).encode().decode("unicode_escape")
    shop_rating = None
    sr_m = re.search(r'"shop_rating"\s*:\s*"([0-9.]+)"', html)
    if sr_m:
        try:
            shop_rating = float(sr_m.group(1))
        except ValueError:
            shop_rating = None
    product_count = None
    pc_m = re.search(r'"on_sell_product_count"\s*:\s*(\d+)', html)
    if pc_m:
        product_count = int(pc_m.group(1))

    seller: dict[str, Any] = {}
    if seller_name:
        seller["name"] = seller_name
    if seller_id:
        seller["id"] = seller_id
        if shop_link and "http" in shop_link:
            seller["url"] = shop_link.replace("shop.tiktok.com/us/store", "www.tiktok.com/shop/store")
        elif seller_name:
            seller["url"] = f"https://www.tiktok.com/shop/store/{quote(str(seller_name))}/{seller_id}"
        else:
            seller["url"] = f"https://www.tiktok.com/shop/store/{seller_id}"
    if shop_rating is not None:
        seller["rating"] = shop_rating
    if product_count is not None:
        seller["productCount"] = product_count
    logo_urls = _image_urls(seller_model.get("shop_logo"))
    if logo_urls:
        seller["logo"] = logo_urls[0]

    sale_properties: list[dict[str, Any]] = []
    for prop in pm.get("sale_properties") or []:
        if not isinstance(prop, dict):
            continue
        values = []
        for v in prop.get("property_values") or []:
            if isinstance(v, dict) and v.get("property_value_name"):
                values.append(
                    {
                        "id": str(v.get("property_value_id") or ""),
                        "name": str(v["property_value_name"]),
                    }
                )
        sale_properties.append(
            {
                "id": str(prop.get("property_id") or ""),
                "name": str(prop.get("property_name") or ""),
                "values": values,
            }
        )

    # Desc / product video when TikTok embeds a non-empty videos object/list.
    desc_video = None
    videos = pm.get("videos")
    if isinstance(videos, dict) and videos:
        for u in _image_urls(videos) or []:
            desc_video = {"url": u}
            break
        if videos.get("duration") is not None:
            desc_video = desc_video or {}
            desc_video["durationMs"] = videos.get("duration")
        if isinstance(videos.get("url_list"), list) and videos["url_list"]:
            desc_video = {"url": videos["url_list"][0], "durationMs": videos.get("duration")}
    elif isinstance(videos, list) and videos:
        first = videos[0] if isinstance(videos[0], dict) else {}
        urls = _image_urls(first)
        if urls:
            desc_video = {"url": urls[0], "durationMs": first.get("duration")}

    categories = _categories_from_html(html)
    og_title = _og(html, "og:title")
    if og_title:
        og_title = re.sub(r"\s*[-|]\s*TikTok Shop\s*$", "", og_title, flags=re.I).strip()
    title = title or og_title
    image = images[0] if images else _og(html, "og:image")
    if not title and not image:
        return None
    if (title or "").strip().lower() in {"security check", "tiktok shop", "tiktok"}:
        return None

    canonical = _og(html, "og:url") or fetch_url
    out: dict[str, Any] = {
        "id": product_id,
        "productId": product_id,
        "title": title,
        "description": description or _og(html, "og:description"),
        "url": canonical if canonical and "http" in canonical else f"https://www.tiktok.com/shop/pdp/{product_id}",
        "price": pricing["price"],
        "originalPrice": pricing["originalPrice"],
        "currency": pricing["currency"] or "USD",
        "discount": pricing["discount"],
        "savings": pricing["savings"],
        "sold": sold,
        "stock": stock,
        "rating": rating,
        "reviewCount": review_count,
        "image": image,
        "images": images or ([image] if image else []),
        "seller": seller,
        "skus": skus,
        "saleProperties": sale_properties,
        "categories": categories,
    }
    if desc_video:
        out["descVideo"] = desc_video
    return out


async def fetch_product_details(url: str) -> dict[str, Any] | None:
    """PDP via SSR ``product_info`` JSON (preferred) or OG/regex fallback.

    Returns a dict shaped for ``_normalize_product(..., details_mode=True)``.
    Related affiliate videos are not embedded in US PDP SSR — omitted unless
    an upstream path fills ``relatedVideos``.
    """
    product_id = parse_product_id(url)
    if not product_id:
        return None
    candidates = [
        (url or "").strip(),
        f"https://shop.tiktok.com/us/pdp/{product_id}",
        f"https://www.tiktok.com/shop/pdp/{product_id}",
    ]
    html = None
    fetch_url = candidates[0]
    for candidate in candidates:
        if not candidate:
            continue
        html = await _fetch_html(candidate) or await _fetch_pdp_html(candidate)
        if html:
            fetch_url = candidate
            break
    if not html:
        return None

    info = _parse_product_info_blob(html)
    if info:
        rich = _product_from_info_blob(info, html=html, product_id=product_id, fetch_url=fetch_url)
        if rich:
            log.info(
                "tiktok_shop_native_details_ok",
                product_id=product_id,
                path="product_info",
                has_price=rich.get("price") is not None,
                has_original=rich.get("originalPrice") is not None,
                skus=len(rich.get("skus") or []),
                images=len(rich.get("images") or []),
            )
            return rich

    # --- OG / regex fallback (thin PDPs / partial SSR) ---
    title = _og(html, "og:title") or _og(html, "twitter:title")
    if not title:
        m = re.search(r"<title[^>]*>\s*([^<]+?)\s*</title>", html, re.I)
        if m:
            title = m.group(1).strip()
    if title:
        title = re.sub(r"\s*[-|]\s*TikTok Shop\s*$", "", title, flags=re.I).strip()
    description = _og(html, "og:description")
    image = _og(html, "og:image")
    if not image:
        im = re.search(
            r'(https://p16-oec[^"\s]+|https://[^"\s]+ttcdn[^"\s]+\.(?:jpg|jpeg|png|webp))',
            html,
            re.I,
        )
        if im:
            image = im.group(1)
    canonical = _og(html, "og:url") or fetch_url

    seller_name = None
    sm = re.search(r'"shop_name"\s*:\s*"((?:\\.|[^"\\])+)"', html)
    if sm:
        try:
            seller_name = json.loads(f'"{sm.group(1)}"')
        except ValueError:
            seller_name = sm.group(1)

    seller_id = None
    for pat in (
        r'"seller_id"\s*:\s*"?(\d{5,})"?',
        r'"shop_id"\s*:\s*"?(\d{5,})"?',
        r'"sellerId"\s*:\s*"?(\d{5,})"?',
        r'tiktok\.com/shop/store/[^"\'\s]+/(\d{5,})',
    ):
        sid_m = re.search(pat, html, re.I)
        if sid_m:
            seller_id = sid_m.group(1)
            break

    sold = None
    sold_m = re.search(r'"sold_count"\s*:\s*(\d+)\s*[,}]', html) or re.search(
        r'"sold_count"\s*:\s*"(\d+)"', html
    )
    if sold_m:
        sold = int(sold_m.group(1))

    def _decimal(pat: str) -> float | str | None:
        m = re.search(pat, html)
        if not m:
            return None
        raw = m.group(1)
        if not raw or "*" in raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return raw

    # Prefer promotion min_price (avoid shipping origin_price / SKU noise).
    price = _decimal(
        r'"promotion_product_price"\s*:\s*\{[^}]{0,400}?"sale_price_decimal"\s*:\s*"([0-9.]+)"'
    ) or _decimal(r'"sale_price_decimal"\s*:\s*"([0-9.]+)"')
    original_price = _decimal(r'"origin_price_decimal"\s*:\s*"([0-9.]+)"')
    currency = None
    cm = re.search(r'"currency_name"\s*:\s*"([A-Z]{3})"', html)
    if cm:
        currency = cm.group(1)
    discount = None
    dm = re.search(r'"discount_format"\s*:\s*"([^"*]+)"', html)
    if dm:
        discount = dm.group(1).strip() or None

    stock: int | None = None
    sku_qty: dict[str, int] = {}
    for sid, qty in re.findall(
        r'"sku_id"\s*:\s*"(\d+)".{0,800}?"available_quantity"\s*:\s*(\d+)',
        html,
        re.S,
    ):
        sku_qty[sid] = int(qty)
    if sku_qty:
        stock = sum(sku_qty.values())

    rating: float | None = None
    for pat in (
        r'"product_overall_score"\s*:\s*([0-9.]+)',
        r'"product_rating"\s*:\s*"?([0-9.]+)"?',
        r'"average_rating"\s*:\s*"?([0-9.]+)"?',
    ):
        score_m = re.search(pat, html)
        if not score_m:
            continue
        try:
            rating = float(score_m.group(1))
            break
        except ValueError:
            rating = None
    review_count = None
    for pat in (
        r'"product_review_count"\s*:\s*"?(\d+)"?',
        r'"review_count"\s*:\s*"?(\d+)"?',
    ):
        rc_m = re.search(pat, html)
        if rc_m:
            review_count = int(rc_m.group(1))
            break
    if rating == 0 and not review_count:
        rating = None
    if review_count == 0 and rating is None:
        review_count = None

    shop_rating = None
    sr_m = re.search(r'"shop_rating"\s*:\s*"([0-9.]+)"', html)
    if sr_m:
        try:
            shop_rating = float(sr_m.group(1))
        except ValueError:
            shop_rating = sr_m.group(1)

    if not title and not image:
        return None
    if (title or "").strip().lower() in {"security check", "tiktok shop", "tiktok"}:
        return None

    seller: dict[str, Any] = {}
    if seller_name:
        seller["name"] = seller_name
    if seller_id:
        seller["id"] = seller_id
        if seller_name:
            seller["url"] = (
                f"https://www.tiktok.com/shop/store/{quote(str(seller_name))}/{seller_id}"
            )
        else:
            seller["url"] = f"https://www.tiktok.com/shop/store/{seller_id}"
    if shop_rating is not None:
        seller["rating"] = shop_rating

    skus = [{"id": sid, "stock": qty} for sid, qty in sorted(sku_qty.items(), key=lambda kv: kv[0])]
    out = {
        "id": product_id,
        "productId": product_id,
        "title": title,
        "description": description,
        "url": canonical if canonical and "http" in canonical else f"https://www.tiktok.com/shop/pdp/{product_id}",
        "price": price,
        "originalPrice": original_price,
        "currency": currency,
        "discount": discount,
        "sold": sold,
        "stock": stock,
        "rating": rating,
        "reviewCount": review_count,
        "image": image,
        "images": [image] if image else [],
        "seller": seller,
        "skus": skus,
        "categories": _categories_from_html(html),
    }
    log.info(
        "tiktok_shop_native_details_ok",
        product_id=product_id,
        path="og_fallback",
        has_price=price is not None,
        has_original=original_price is not None,
        has_stock=stock is not None,
        has_rating=rating is not None,
    )
    return out


_SERP_PDP_ID_RE = re.compile(
    r"tiktok\.com/shop/pdp/(?:[^/\"'?#\s]+/)?(\d{10,})",
    re.I,
)


def _product_ids_from_serp_html(html: str, *, limit: int = 40) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for pid in _SERP_PDP_ID_RE.findall(html or ""):
        if pid in seen:
            continue
        seen.add(pid)
        ids.append(pid)
        if len(ids) >= limit:
            break
    return ids


async def _search_product_ids_via_serp(
    q: str,
    *,
    region: str = "US",
    limit: int = 40,
) -> list[str]:
    """Google/DDG ``site:tiktok.com/shop/pdp`` — avoids Shop search WAF."""
    if not decodo_fetch.enabled():
        return []
    query = quote(f"site:tiktok.com/shop/pdp {q}", safe="")
    geo = (region or "US").strip().upper() or "US"
    sources = [
        f"https://www.google.com/search?q={query}&num={min(30, max(10, limit))}&hl=en&gl={geo}",
        f"https://html.duckduckgo.com/html/?q={query}",
    ]
    seen: set[str] = set()
    ids: list[str] = []
    for url in sources:
        headless = "html" if "google.com" in url else None
        got = await decodo_fetch.fetch_url(url, timeout=90.0, headless=headless, geo=geo)
        if not got:
            continue
        status, body = got
        if status != 200 or not body:
            continue
        for pid in _product_ids_from_serp_html(body, limit=limit):
            if pid in seen:
                continue
            seen.add(pid)
            ids.append(pid)
            if len(ids) >= limit:
                break
        if len(ids) >= min(10, limit):
            break
    log.info("tiktok_shop_search_serp_ids", q=q[:80], region=geo, n=len(ids))
    return ids


async def search_products_native(
    q: str,
    *,
    region: str = "US",
    limit: int = 20,
) -> list[dict[str, Any]] | None:
    """Keyword shop search via SERP → PDP OG/SSR hydrate.

    Shop search pages are captcha-gated; this path never hits them.
    """
    query = (q or "").strip()
    if len(query) < 2 or limit <= 0:
        return None
    want = min(40, max(15, limit * 2))
    ids = await _search_product_ids_via_serp(query, region=region, limit=want)
    if not ids:
        return None

    sem = asyncio.Semaphore(5)
    selected = ids[: max(limit * 2, limit + 4)]

    async def _one(pid: str) -> dict[str, Any] | None:
        async with sem:
            return await fetch_product_details(f"https://www.tiktok.com/shop/pdp/{pid}")

    rows = await asyncio.gather(*[_one(pid) for pid in selected])
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        pid = str(row.get("productId") or row.get("id") or "")
        if not pid or pid in seen:
            continue
        title = (row.get("title") or "").strip()
        # OG sometimes collapses to the site name when the PDP is gated.
        if not title or title.lower() in {"tiktok shop", "tiktok", "security check"}:
            continue
        if not row.get("image") and len(title) < 12:
            continue
        # Drop captcha stubs that slipped through without a product image/price.
        if not row.get("image") and row.get("price") is None:
            continue
        seen.add(pid)
        out.append(row)
        if len(out) >= limit:
            break
    if not out:
        return None
    log.info(
        "tiktok_shop_search_native_ok",
        q=query[:80],
        region=(region or "US").upper(),
        n=len(out),
    )
    return out
