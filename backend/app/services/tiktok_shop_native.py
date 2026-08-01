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


async def fetch_product_details(url: str) -> dict[str, Any] | None:
    """PDP via HTML (OG + SSR hints). Prices are often masked as ``*`` in SSR.

    Returns Apify-like product dict for ``_normalize_product(..., details_mode)``.
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

    title = _og(html, "og:title") or _og(html, "twitter:title")
    if not title:
        # React-helmet sometimes emits content before property.
        m = re.search(
            r'<title[^>]*>\s*([^<]+?)\s*</title>',
            html,
            re.I,
        )
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

    # Best-effort seller / sold from nearby SSR text (when not masked).
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
    # Prefer bare integers (product aggregate) over quoted SKU stubs ("5").
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

    # Unmasked price if present (masked values use "*").
    price = _decimal(r'"sale_price_decimal"\s*:\s*"([0-9.]+)"')
    original_price = _decimal(r'"origin_price_decimal"\s*:\s*"([0-9.]+)"')
    currency = None
    cm = re.search(r'"currency_name"\s*:\s*"([A-Z]{3})"', html)
    if cm:
        currency = cm.group(1)
    discount = None
    dm = re.search(r'"discount_format"\s*:\s*"([^"*]+)"', html)
    if dm:
        discount = dm.group(1).strip() or None

    # Sum unique SKU warehouse quantities (HTML often repeats the sku list).
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

    # Product star score; treat 0 + zero reviews as unknown.
    rating: float | None = None
    score_m = re.search(r'"product_overall_score"\s*:\s*([0-9.]+)', html)
    if score_m:
        try:
            rating = float(score_m.group(1))
        except ValueError:
            rating = None
    review_count = None
    rc_m = re.search(r'"product_review_count"\s*:\s*"?(\d+)"?', html)
    if rc_m:
        review_count = int(rc_m.group(1))
    if rating == 0 and not review_count:
        rating = None

    shop_rating = None
    sr_m = re.search(r'"shop_rating"\s*:\s*"([0-9.]+)"', html)
    if sr_m:
        try:
            shop_rating = float(sr_m.group(1))
        except ValueError:
            shop_rating = sr_m.group(1)

    if not title and not image:
        return None
    # Captcha / WAF interstitial — treat as miss so search can skip.
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

    skus = [
        {"id": sid, "stock": qty}
        for sid, qty in sorted(sku_qty.items(), key=lambda kv: kv[0])
    ]
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
    }
    log.info(
        "tiktok_shop_native_details_ok",
        product_id=product_id,
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
