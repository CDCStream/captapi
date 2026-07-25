"""Native LinkedIn Ad Library search via Decodo JS-rendered HTML (no Apify).

LinkedIn serves an SSR shell without ad cards to plain HTTP clients. Decodo
``headless=html`` hydrates the SERP so we can parse detail links, headlines,
advertiser names, and preview images.
"""

from __future__ import annotations

import html as html_lib
import re
from typing import Any
from urllib.parse import urlencode

import structlog

from app.services import decodo_fetch

log = structlog.get_logger(__name__)


def search_url(q: str, country: str) -> str:
    params = {
        "accountOwner": q,
        "countries": (country or "US").upper(),
    }
    return f"https://www.linkedin.com/ad-library/search?{urlencode(params)}"


def _unescape(value: str | None) -> str | None:
    if not value:
        return None
    text = html_lib.unescape(value).strip()
    return text or None


def extract_ads(html: str, *, country: str, limit: int) -> list[dict[str, Any]]:
    """Parse hydrated Ad Library SERP HTML into Apify-compatible rows."""
    ids = list(dict.fromkeys(re.findall(r"/ad-library/detail/(\d+)", html)))
    ads: list[dict[str, Any]] = []
    for ad_id in ids:
        # Window around the first occurrence of this detail id.
        m = re.search(rf"/ad-library/detail/{ad_id}", html)
        if not m:
            continue
        start = max(0, m.start() - 2500)
        end = min(len(html), m.start() + 1500)
        win = html[start:end]

        def _clean_text(value: str | None) -> str | None:
            text = _unescape(value)
            if not text:
                return None
            text = re.sub(r"%FIRSTNAME%", "", text, flags=re.I).strip(" ,")
            text = re.sub(r"\s+", " ", text).strip()
            return text or None

        def _bad_name(value: str | None) -> bool:
            if not value:
                return True
            low = value.strip().lower()
            return (
                low
                in {
                    "profile",
                    "view details",
                    "linkedin",
                    "ad library",
                    "company",
                    "advertiser logo",
                    "logo",
                }
                or low.startswith("advertiser ")
            )

        headline = None
        hm = re.search(
            r"<h2[^>]*class=\"[^\"]*text-sm[^\"]*\"[^>]*>(.*?)</h2>",
            win,
            re.S | re.I,
        )
        if hm:
            headline = _clean_text(re.sub(r"<[^>]+>", "", hm.group(1)))

        advertiser = None
        company_url = None
        for am in re.finditer(
            r'href="(https://www\.linkedin\.com/company/[^"]+)"[^>]*>(.*?)</a>',
            win,
            re.S | re.I,
        ):
            name = _clean_text(re.sub(r"<[^>]+>", "", am.group(2)))
            if _bad_name(name):
                continue
            company_url = am.group(1)
            # Prefer vanity slug when anchor text looks like creative copy.
            slug = company_url.rstrip('/').split('/')[-1]
            slug_name = slug.replace('-', ' ').strip()
            if name and name.lower() != (headline or '').lower() and len(name) <= 80:
                advertiser = name
            elif slug_name:
                advertiser = slug_name.title() if slug_name.islower() or '-' in slug else slug_name
            else:
                advertiser = name
            break

        logo = None
        media: list[str] = []
        for im in re.finditer(
            r"<img[^>]+>",
            win,
            re.I,
        ):
            tag = im.group(0)
            src_m = re.search(r'\bsrc="(https://[^"]+)"', tag, re.I)
            alt_m = re.search(r'\balt="([^"]*)"', tag, re.I)
            if not src_m:
                continue
            src = src_m.group(1)
            alt = _clean_text(alt_m.group(1) if alt_m else None)
            if "company-logo" in src or "ghost" in src or "entity-ghost" in src:
                if not logo:
                    logo = src
                if advertiser is None and not _bad_name(alt):
                    advertiser = alt
                continue
            if "media.licdn.com" in src and src not in media:
                media.append(src)
            if not headline and not _bad_name(alt):
                headline = alt
            if advertiser is None and not _bad_name(alt):
                advertiser = alt

        row: dict[str, Any] = {
            "id": ad_id,
            "adId": ad_id,
            "url": f"https://www.linkedin.com/ad-library/detail/{ad_id}",
            "text": headline,
            "adFormat": "Single Image Ad" if media else None,
            "country": (country or "US").upper(),
            "advertiserName": advertiser,
            "advertiserUrl": company_url,
            "advertiserLogo": logo,
            "imageUrls": media,
        }
        ads.append(row)
        if len(ads) >= limit:
            break
    return ads


async def search_ads(
    q: str, *, country: str = "US", limit: int = 20
) -> list[dict[str, Any]] | None:
    query = (q or "").strip()
    if len(query) < 2:
        return []
    if not decodo_fetch.enabled():
        return None

    url = search_url(query, country)
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or len(html) < 5000:
        log.warning("linkedin_ads_native_weak", status=status, length=len(html))
        return None

    rows = extract_ads(html, country=country, limit=max(0, int(limit)))
    if not rows:
        if "ad-library" in html.lower():
            return []
        log.warning("linkedin_ads_native_no_ads", length=len(html))
        return None

    log.info(
        "linkedin_ads_native_search_ok",
        count=len(rows),
        q=query[:40],
        country=country,
    )
    return rows
