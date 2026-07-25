"""Native Amazon seller storefront scraper (no Apify).

Fetches Amazon's server-rendered ``/s?me=<sellerId>`` listing via
datacenter -> residential -> Decodo, then parses ``s-search-result`` cards.
"""

from __future__ import annotations

import html as htmlmod
import math
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
import structlog

from app.services import decodo_fetch
from app.services.http_fetch import DEFAULT_HEADERS, proxy_for

log = structlog.get_logger(__name__)

# Approximate organic results per storefront page.
_PAGE_SIZE = 16

_MARKETPLACES: dict[str, tuple[str, str]] = {
    "US": ("www.amazon.com", "ATVPDKIKX0DER"),
    "UK": ("www.amazon.co.uk", "A1F83G8C2ARO7P"),
    "DE": ("www.amazon.de", "A1PA6795UKMFR9"),
    "FR": ("www.amazon.fr", "A13V1IB3VIYZZH"),
    "IT": ("www.amazon.it", "APJ6JRA9NG5V4"),
    "ES": ("www.amazon.es", "A1RKKUPIHCS9HS"),
    "CA": ("www.amazon.ca", "A2EUQ1WTGCTBG2"),
    "JP": ("www.amazon.co.jp", "A1VC38T7YXB528"),
    "IN": ("www.amazon.in", "A21TJRUUN4KGV"),
    "AU": ("www.amazon.com.au", "A39IBJ37TRP1C6"),
    "MX": ("www.amazon.com.mx", "A1AM78C64UM0Y8"),
    "BR": ("www.amazon.com.br", "A2Q3Y263D00KWC"),
}

_SELLER_RE = re.compile(r"\b(A[A-Z0-9]{10,14})\b")
_CARD_SPLIT = re.compile(r'(?=<div[^>]+data-component-type="s-search-result")', re.I)
_ASIN_RE = re.compile(r'data-asin="([A-Z0-9]{10})"')
_TITLE_PATS = (
    re.compile(r"<h2[^>]*>[\s\S]*?<span[^>]*>([^<]{5,400})</span>", re.I),
    re.compile(r'<h2[^>]+aria-label="([^"]{5,400})"', re.I),
    re.compile(
        r'class="[^"]*a-size-medium[^"]*a-color-base[^"]*a-text-normal[^"]*"[^>]*>([^<]{5,400})<',
        re.I,
    ),
)
_PRICE_RE = re.compile(
    r'class="a-price"[^>]*>[\s\S]*?class="a-offscreen"[^>]*>([^<]+)<', re.I
)
_PRICE_FALLBACK_RE = re.compile(r'a-offscreen[^>]*>([$€£¥₹][\d,.]+)<', re.I)
_IMG_RE = re.compile(
    r'src="(https://m\.media-amazon\.com/images/I/[^"]+\.(?:jpg|png|webp)[^"]*)"',
    re.I,
)
_RATING_RE = re.compile(r"([\d.]+)\s+out of\s+5", re.I)
_REVIEWS_RE = re.compile(
    r"(?:aria-label=\"([0-9,.]+)\s+ratings?\"|>)([0-9,.]+)\s*</span>\s*</a>\s*</span>\s*<span[^>]*>\s*</span>\s*<span class=\"a-letter-space\">",
    re.I,
)
_REVIEWS_SIMPLE_RE = re.compile(
    r's-underline-text[^>]*>\s*([0-9,.]+)\s*<', re.I
)


def extract_seller_id(url_or_id: str) -> str | None:
    raw = (url_or_id or "").strip()
    if not raw:
        return None
    if re.fullmatch(r"A[A-Z0-9]{10,14}", raw):
        return raw
    try:
        parsed = urlparse(raw if "://" in raw else f"https://www.amazon.com/{raw}")
        qs = parse_qs(parsed.query)
        for key in ("seller", "me", "merchant"):
            vals = qs.get(key) or []
            if vals and re.fullmatch(r"A[A-Z0-9]{10,14}", vals[0]):
                return vals[0]
    except Exception:  # noqa: BLE001
        pass
    m = _SELLER_RE.search(raw)
    return m.group(1) if m else None


def storefront_url(seller_id: str, marketplace: str, page: int = 1) -> str:
    host, mid = _MARKETPLACES.get(marketplace.upper(), _MARKETPLACES["US"])
    url = f"https://{host}/s?me={seller_id}&marketplaceID={mid}"
    if page > 1:
        url += f"&page={page}"
    return url


def _parse_price(text: str | None) -> tuple[float | None, str | None, str | None]:
    if not text:
        return None, None, None
    cleaned = htmlmod.unescape(text).strip()
    currency = None
    if cleaned.startswith("$"):
        currency = "USD"
    elif cleaned.startswith("£"):
        currency = "GBP"
    elif cleaned.startswith("€"):
        currency = "EUR"
    elif cleaned.startswith("¥"):
        currency = "JPY"
    elif cleaned.startswith("₹"):
        currency = "INR"
    num = re.sub(r"[^\d.]", "", cleaned.replace(",", ""))
    try:
        value = float(num) if num else None
    except ValueError:
        value = None
    return value, currency, cleaned


def _parse_card(part: str, *, host: str, seller_id: str) -> dict[str, Any] | None:
    asin_m = _ASIN_RE.search(part)
    if not asin_m:
        return None
    asin = asin_m.group(1)
    if asin in {"", "0000000000"} or len(asin) != 10:
        return None

    title = None
    for pat in _TITLE_PATS:
        tm = pat.search(part)
        if tm:
            title = htmlmod.unescape(tm.group(1)).strip()
            break
    if not title:
        return None

    price_m = _PRICE_RE.search(part) or _PRICE_FALLBACK_RE.search(part)
    price, currency, price_fmt = _parse_price(price_m.group(1) if price_m else None)

    img_m = _IMG_RE.search(part)
    href_m = re.search(
        rf'href="(/[^"]*?/dp/{re.escape(asin)}[^"]*)"', part, flags=re.I
    )
    product_url = (
        f"https://{host}{href_m.group(1)}"
        if href_m
        else f"https://{host}/dp/{asin}"
    )

    rating = None
    rm = _RATING_RE.search(part)
    if rm:
        try:
            rating = float(rm.group(1))
        except ValueError:
            rating = None

    reviews = None
    for pat in (_REVIEWS_SIMPLE_RE,):
        rvm = pat.search(part)
        if rvm:
            try:
                reviews = int(rvm.group(1).replace(",", ""))
                break
            except ValueError:
                pass

    item: dict[str, Any] = {
        "asin": asin,
        "title": title,
        "productUrl": product_url,
        "url": product_url,
        "imageUrl": img_m.group(1) if img_m else None,
        "image": img_m.group(1) if img_m else None,
        "price": price,
        "currency": currency,
        "priceFormatted": f"{currency} {price}".strip() if currency and price is not None else price_fmt,
        "rating": rating,
        "reviews": reviews,
        "reviewsCount": reviews,
        "sellerId": seller_id,
    }
    return item


def parse_storefront_html(page_html: str, *, host: str, seller_id: str) -> list[dict[str, Any]]:
    if not page_html or len(page_html) < 2000:
        return []
    lowered = page_html.lower()
    if "robot check" in lowered or "/errors/validatecaptcha" in lowered:
        return []

    parts = _CARD_SPLIT.split(page_html)
    products: list[dict[str, Any]] = []
    seen: set[str] = set()
    for part in parts[1:]:
        item = _parse_card(part, host=host, seller_id=seller_id)
        if not item:
            continue
        asin = item["asin"]
        if asin in seen:
            continue
        seen.add(asin)
        products.append(item)
    return products


async def _fetch_html(url: str) -> tuple[str | None, str]:
    """Return (html, tier) or (None, last_tier)."""
    headers = {
        **DEFAULT_HEADERS,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for tier, proxy in (
        ("datacenter", proxy_for("datacenter")),
        ("residential", proxy_for("residential")),
        ("direct", None),
    ):
        if tier != "direct" and not proxy:
            continue
        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers=headers,
                proxy=proxy,
            ) as client:
                resp = await client.get(url)
            if resp.status_code == 200 and len(resp.text) > 5000:
                products_probe = "data-asin=" in resp.text
                if products_probe:
                    return resp.text, tier
            log.warning(
                "amazon_shop_fetch_weak",
                tier=tier,
                status=resp.status_code,
                length=len(resp.text),
            )
        except httpx.HTTPError as exc:
            log.warning("amazon_shop_fetch_error", tier=tier, error=str(exc))

    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=45.0)
        if got and got[0] == 200 and got[1] and len(got[1]) > 5000:
            return got[1], "decodo"

    return None, "none"


async def fetch_shop_products(
    url_or_id: str,
    *,
    marketplace: str = "US",
    limit: int = 20,
) -> dict[str, Any] | None:
    """Fetch seller storefront products natively.

    Returns a dict shaped for ``_normalize_shop`` (list of product-like items
    plus sellerId), or ``None`` when every transport tier fails.
    """
    seller_id = extract_seller_id(url_or_id)
    if not seller_id:
        return None

    market = (marketplace or "US").upper()
    host, _mid = _MARKETPLACES.get(market, _MARKETPLACES["US"])
    want = max(0, int(limit))
    if want == 0:
        # Metadata-only: one page is enough to confirm the shop exists.
        want_fetch = 1
    else:
        want_fetch = want

    pages_needed = max(1, math.ceil(want_fetch / _PAGE_SIZE))
    items: list[dict[str, Any]] = []
    tier_used = "none"

    for page in range(1, pages_needed + 1):
        page_url = storefront_url(seller_id, market, page=page)
        html, tier = await _fetch_html(page_url)
        tier_used = tier
        if not html:
            break
        batch = parse_storefront_html(html, host=host, seller_id=seller_id)
        if not batch:
            break
        for item in batch:
            items.append(item)
            if want > 0 and len(items) >= want:
                break
        if want > 0 and len(items) >= want:
            break
        if len(batch) < 5:
            # Likely last page / soft empty.
            break

    if not items:
        if want > 0 or tier_used == "none":
            return None

    log.info(
        "amazon_shop_native_ok",
        seller=seller_id,
        count=len(items),
        tier=tier_used,
        market=market,
    )
    for item in items:
        item.setdefault("sellerId", seller_id)
        item.setdefault("marketplace", market)
    return {
        "seller_id": seller_id,
        "marketplace": market,
        "host": host,
        "tier": tier_used,
        "items": items[:want] if want > 0 else [],
        "pages": pages_needed,
    }
