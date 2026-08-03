"""Native LinkedIn Ad Library via Decodo JS-rendered HTML (no Apify).

Search SERP yields ad ids + paginationMetadata; detail pages expose LinkedIn's
transparency fields (targeting, ran-from dates, impressions by country, CTA).
"""

from __future__ import annotations

import asyncio
import html as html_lib
import re
from calendar import month_abbr
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

import structlog

from app.services import decodo_fetch

log = structlog.get_logger(__name__)

_MONTH = {m.lower(): i for i, m in enumerate(month_abbr) if m}


def search_url(
    *,
    account_owner: str | None = None,
    keyword: str | None = None,
    company_id: str | None = None,
    countries: str = "US",
    start_date: str | None = None,
    end_date: str | None = None,
    pagination_token: str | None = None,
) -> str:
    params: dict[str, str] = {}
    owner = (account_owner or "").strip()
    kw = (keyword or "").strip()
    cid = (company_id or "").strip()
    if owner:
        params["accountOwner"] = owner
    if kw:
        params["keyword"] = kw
    if cid:
        params["companyIds"] = cid
        params["companyId"] = cid
    params["countries"] = (countries or "US").upper().replace(" ", "")
    if start_date and end_date:
        params["dateOption"] = "custom-date-range"
        params["startdate"] = start_date
        params["enddate"] = end_date
    if pagination_token:
        params["paginationToken"] = pagination_token
    return f"https://www.linkedin.com/ad-library/search?{urlencode(params)}"


def _unescape(value: str | None) -> str | None:
    if not value:
        return None
    text = html_lib.unescape(value).strip()
    return text or None


def _clean_text(value: str | None) -> str | None:
    text = _unescape(value)
    if not text:
        return None
    text = re.sub(r"%FIRSTNAME%", "", text, flags=re.I).strip(" ,")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _parse_ran_from(raw: str | None) -> tuple[str | None, str | None, str | None]:
    """Return (adDuration, startISO, endISO) from LinkedIn 'Ran from ?' copy."""
    text = _clean_text(raw)
    if not text:
        return None, None, None
    duration = text if text.lower().startswith("ran from") else f"Ran from {text}"
    m = re.search(
        r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})\s+to\s+([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})",
        text,
        re.I,
    )
    if not m:
        return duration, None, None

    def _iso(month: str, day: str, year: str) -> str | None:
        mi = _MONTH.get(month[:3].lower())
        if not mi:
            return None
        try:
            return datetime(int(year), mi, int(day)).strftime("%Y-%m-%d")
        except ValueError:
            return None

    return duration, _iso(m.group(1), m.group(2), m.group(3)), _iso(m.group(4), m.group(5), m.group(6))


def _company_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r"/company/(\d+)", url)
    return m.group(1) if m else None


def extract_search_meta(html: str) -> dict[str, Any]:
    total = None
    tm = re.search(r"([\d,]+)\s+ads?\s+match", html, re.I)
    if tm:
        try:
            total = int(tm.group(1).replace(",", ""))
        except ValueError:
            total = None
    token = None
    is_last = None
    pm = re.search(
        r"paginationMetadata[^>]*>\s*<!--\s*(\{.*?\})\s*-->",
        html,
        re.I | re.S,
    )
    if pm:
        blob = pm.group(1)
        tm2 = re.search(r'"paginationToken"\s*:\s*"([^"]*)"', blob)
        if tm2:
            token = tm2.group(1) or None
        lm = re.search(r'"isLastPage"\s*:\s*(true|false)', blob, re.I)
        if lm:
            is_last = lm.group(1).lower() == "true"
    return {
        "totalAds": total,
        "paginationToken": token,
        "isLastPage": is_last,
    }


def extract_ads(html: str, *, country: str, limit: int) -> list[dict[str, Any]]:
    """Parse hydrated Ad Library SERP HTML into row stubs."""
    ids = list(dict.fromkeys(re.findall(r"/ad-library/detail/(\d+)", html)))
    ads: list[dict[str, Any]] = []
    for ad_id in ids:
        m = re.search(rf"/ad-library/detail/{ad_id}", html)
        if not m:
            continue
        start = max(0, m.start() - 2500)
        end = min(len(html), m.start() + 1500)
        win = html[start:end]

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
            company_url = am.group(1).split("?")[0]
            slug = company_url.rstrip("/").split("/")[-1]
            slug_name = slug.replace("-", " ").strip()
            if name and name.lower() != (headline or "").lower() and len(name) <= 80:
                advertiser = name
            elif slug_name:
                advertiser = slug_name.title() if slug_name.islower() or "-" in slug else slug_name
            else:
                advertiser = name
            break

        logo = None
        media: list[str] = []
        for im in re.finditer(r"<img[^>]+>", win, re.I):
            tag = im.group(0)
            src_m = re.search(r'\bsrc="(https://[^"]+)"', tag, re.I)
            alt_m = re.search(r'\balt="([^"]*)"', tag, re.I)
            if not src_m:
                continue
            src = html_lib.unescape(src_m.group(1))
            alt = _clean_text(alt_m.group(1) if alt_m else None)
            if "company-logo" in src or "ghost" in src or "entity-ghost" in src:
                if not logo:
                    logo = src
                if (
                    advertiser is None
                    and not _bad_name(alt)
                    and (not headline or alt.lower() != headline.lower())
                ):
                    advertiser = alt
                continue
            if "media.licdn.com" in src and src not in media:
                media.append(src)
            if not headline and not _bad_name(alt):
                headline = alt
            # Never treat creative alt/headline as the advertiser name.
            if (
                advertiser is None
                and not _bad_name(alt)
                and (not headline or alt.lower() != headline.lower())
            ):
                advertiser = alt

        row: dict[str, Any] = {
            "id": ad_id,
            "adId": ad_id,
            "url": f"https://www.linkedin.com/ad-library/detail/{ad_id}",
            "text": headline,
            "headline": headline,
            "adFormat": "Single Image Ad" if media else None,
            "country": (country or "US").upper().split(",")[0],
            "countries": [c for c in (country or "US").upper().split(",") if c],
            "advertiserName": advertiser,
            "advertiserUrl": company_url,
            "advertiserId": _company_id_from_url(company_url),
            "advertiserLogo": logo,
            "imageUrls": media,
        }
        ads.append(row)
        if len(ads) >= limit:
            break
    return ads


def ad_id_from_url(url_or_id: str) -> str | None:
    raw = (url_or_id or "").strip()
    if raw.isdigit():
        return raw
    m = re.search(r"/ad-library/detail/(\d+)", raw)
    if m:
        return m.group(1)
    urn = re.search(r"urn:li:sponsoredCreative:(\d+)", raw)
    return urn.group(1) if urn else None


def extract_ad_details(html: str, *, ad_id: str) -> dict[str, Any] | None:
    """Parse a hydrated Ad Library detail page into ``_normalize_ad`` input."""
    if not html or not ad_id:
        return None
    if f"/ad-library/detail/{ad_id}" not in html and ad_id not in html:
        return None

    headline = None
    hm = re.search(
        r'class="[^"]*sponsored-content-headline[^"]*"[\s\S]{0,800}?<h2[^>]*>(.*?)</h2>',
        html,
        re.I,
    )
    if hm:
        headline = _clean_text(re.sub(r"<[^>]+>", "", hm.group(1)))

    commentary = None
    cm = re.search(
        r'class="[^"]*commentary__content[^"]*"[^>]*>(.*?)</p>',
        html,
        re.S | re.I,
    )
    if cm:
        commentary = _clean_text(re.sub(r"<[^>]+>", "", cm.group(1)))

    ad_format = None
    about = re.search(
        r">About the ad</h2>[\s\S]{0,400}?<p[^>]*>(.*?)</p>",
        html,
        re.I,
    )
    if about:
        ad_format = _clean_text(re.sub(r"<[^>]+>", "", about.group(1)))

    paid_by = None
    pm = re.search(r'about-ad__paying-entity[^>]*>(.*?)</p>', html, re.I | re.S)
    if pm:
        paid_by = _clean_text(re.sub(r"<[^>]+>", "", pm.group(1)))
        if paid_by:
            paid_by = re.sub(r"^Paid for by\s*", "", paid_by, flags=re.I).strip() or paid_by

    ran_raw = None
    rm = re.search(r'about-ad__availability-duration[^>]*>(.*?)</p>', html, re.I | re.S)
    if rm:
        ran_raw = _clean_text(re.sub(r"<[^>]+>", "", rm.group(1)))
    ad_duration, start_iso, end_iso = _parse_ran_from(ran_raw)

    total_impressions = None
    im = re.search(
        r">Total Impressions</p>\s*<p[^>]*class=\"[^\"]*font-semibold[^\"]*\"[^>]*>([^<]+)</p>",
        html,
        re.I,
    )
    if not im:
        im = re.search(
            r">Total Impressions</[\s\S]{0,200}?<[^>]+>([\d,.kKmM+\-<??]+)<",
            html,
            re.I,
        )
    if im:
        total_impressions = _clean_text(im.group(1))

    impressions_by_country: list[dict[str, Any]] = []
    for lab in re.finditer(
        r'aria-label="([^"]+),\s*impressions\s+([^"]+)"',
        html,
        re.I,
    ):
        impressions_by_country.append(
            {
                "country": _clean_text(lab.group(1)),
                "impressions": _clean_text(lab.group(2)),
            }
        )

    targeting: dict[str, str | None] = {}
    label_re = (
        r"Language|Location|Company|Audience|Job title|Job function|"
        r"Industry|Seniority|Company size|Company industry"
    )
    for hm in re.finditer(rf"<h3[^>]*>\s*({label_re})[^<]*</h3>", html, re.I):
        key = hm.group(1).strip().lower().replace(" ", "_")
        key = {
            "job_title": "jobTitle",
            "job_function": "jobFunction",
            "company_size": "companySize",
            "company_industry": "companyIndustry",
        }.get(key, key)
        rest = html[hm.end() : hm.end() + 2000]
        sm = re.search(
            r'<span[^>]*ad-targeting__segments[^>]*>([\s\S]*?)</p>',
            rest,
            re.I,
        )
        if not sm:
            continue
        chunk = sm.group(1)
        others = re.search(
            r'ad-targeting__other-segments[^>]*>(.*?)</span>',
            chunk,
            re.I | re.S,
        )
        chunk = re.sub(
            r"<button[^>]*ad-targeting__others-total-button[^>]*>.*?</button>",
            ", ",
            chunk,
            flags=re.I | re.S,
        )
        if others:
            chunk = re.sub(
                r'<span[^>]*ad-targeting__other-segments[^>]*>.*?</span>',
                f" {others.group(1)} ",
                chunk,
                flags=re.I | re.S,
            )
        val = _clean_text(re.sub(r"<[^>]+>", " ", chunk))
        if val:
            val = re.sub(r"\band\s*,", "and", val, flags=re.I)
            val = re.sub(r"\s*,\s*,\s*", ", ", val)
            val = re.sub(r"\s+", " ", val).strip(" ,")
            targeting[key] = val

    cta = None
    cta_m = re.search(
        r'data-tracking-control-name="ad_library_ad_detail_cta"[^>]*>(.*?)</button>',
        html,
        re.I | re.S,
    )
    if cta_m:
        cta = _clean_text(re.sub(r"<[^>]+>", "", cta_m.group(1)))

    destination = None
    for dm in re.finditer(
        r'href="(https?://[^"]+)"[^>]{0,400}data-tracking-control-name="'
        r'(ad_library_ad_preview_headline_content|ad_library_ad_preview_content_image|'
        r'ad_library_ad_detail_cta|ad_library_ad_preview_cta)"',
        html,
        re.I,
    ):
        href = html_lib.unescape(dm.group(1))
        if "linkedin.com/company/" in href or "linkedin.com/ad-library" in href:
            continue
        destination = html_lib.unescape(href)
        break
    if not destination:
        for dm in re.finditer(r'href="(https?://[^"]+trk=ad_library_ad_preview_[^"]+)"', html, re.I):
            href = html_lib.unescape(dm.group(1))
            if "linkedin.com/company/" in href or "linkedin.com/ad-library" in href:
                continue
            destination = href
            break

    advertiser = None
    company_url = None
    for am in re.finditer(
        r'href="(https://www\.linkedin\.com/company/[^"]+)"[^>]*>(.*?)</a>',
        html,
        re.S | re.I,
    ):
        name = _clean_text(re.sub(r"<[^>]+>", "", am.group(2)))
        href = am.group(1).split("?")[0]
        if not name or name.lower() in {"advertiser", "company", "profile"}:
            # Prefer numeric company links even without name.
            if _company_id_from_url(href) and not company_url:
                company_url = href
            continue
        company_url = href
        advertiser = name
        break
    if advertiser is None and paid_by:
        advertiser = paid_by

    logo = None
    media: list[str] = []
    for tag in re.findall(r"<img[^>]+>", html, re.I):
        src_m = re.search(r'\bsrc="(https://[^"]+)"', tag, re.I)
        delayed_m = re.search(r'\bdata-delayed-url="(https://[^"]+)"', tag, re.I)
        src = src_m or delayed_m
        if not src:
            continue
        url = html_lib.unescape(src.group(1))
        if "company-logo" in url or "ghost" in url or "entity-ghost" in url:
            if not logo:
                logo = url
            continue
        if "media.licdn.com" in url and url not in media:
            media.append(url)

    body_text = commentary or headline
    if not body_text and not advertiser and not targeting:
        return None

    carousel = media[:] if len(media) > 1 else []
    if carousel and not ad_format:
        ad_format = "Carousel Ad"
    elif media and not ad_format:
        ad_format = "Single Image Ad"

    return {
        "id": ad_id,
        "adId": ad_id,
        "url": f"https://www.linkedin.com/ad-library/detail/{ad_id}",
        "text": body_text,
        "headline": headline,
        "description": commentary,
        "body": commentary,
        "cta": cta,
        "landingUrl": destination,
        "destinationUrl": destination,
        "adFormat": ad_format,
        "advertiserName": advertiser,
        "advertiserUrl": company_url,
        "advertiserId": _company_id_from_url(company_url),
        "advertiserLogo": logo,
        "payer": paid_by,
        "paidForBy": paid_by,
        "imageUrls": media,
        "media": media,
        "carouselImages": carousel,
        "impressions": total_impressions,
        "totalImpressions": total_impressions,
        "impressionsByCountry": impressions_by_country,
        "targeting": targeting or None,
        "adDuration": ad_duration,
        "startDate": start_iso,
        "endDate": end_iso,
        "firstShown": start_iso,
        "lastShown": end_iso,
        "dateRange": ran_raw,
    }


async def ad_details(url_or_id: str) -> dict[str, Any] | None:
    """Fetch one Ad Library detail page via Decodo ? ``_normalize_ad`` shape."""
    ad_id = ad_id_from_url(url_or_id)
    if not ad_id or not decodo_fetch.enabled():
        return None
    page_url = f"https://www.linkedin.com/ad-library/detail/{ad_id}"
    got = await decodo_fetch.fetch_url(page_url, timeout=120.0, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or len(html) < 5000:
        log.warning("linkedin_ads_native_detail_weak", status=status, length=len(html), ad_id=ad_id)
        return None
    row = extract_ad_details(html, ad_id=ad_id)
    if not row:
        log.warning("linkedin_ads_native_detail_miss", ad_id=ad_id, length=len(html))
        return None
    log.info("linkedin_ads_native_detail_ok", ad_id=ad_id)
    return row


async def _enrich_with_details(rows: list[dict[str, Any]], *, concurrency: int = 4) -> list[dict[str, Any]]:
    if not rows:
        return rows
    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(row: dict[str, Any]) -> dict[str, Any]:
        ad_id = str(row.get("id") or row.get("adId") or "")
        if not ad_id:
            return row
        async with sem:
            detail = await ad_details(ad_id)
        if not detail:
            return row
        merged = {**row, **{k: v for k, v in detail.items() if v not in (None, "", [], {})}}
        # Prefer detail headline/description split.
        if detail.get("headline") is not None:
            merged["headline"] = detail.get("headline")
        if detail.get("description") is not None:
            merged["description"] = detail.get("description")
            merged["body"] = detail.get("description")
            merged["text"] = detail.get("description") or detail.get("headline") or row.get("text")
        return merged

    return list(await asyncio.gather(*[_one(r) for r in rows]))


async def search_ads(
    q: str | None = None,
    *,
    country: str = "US",
    countries: str | None = None,
    limit: int = 20,
    keyword: str | None = None,
    company_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    pagination_token: str | None = None,
    enrich: bool = True,
) -> dict[str, Any] | None:
    """Search Ad Library. Returns ``{ads, totalAds, paginationToken, isLastPage}``."""
    owner = (q or "").strip()
    kw = (keyword or "").strip()
    cid = (company_id or "").strip()
    if len(owner) < 2 and len(kw) < 2 and not cid:
        return {"ads": [], "totalAds": 0, "paginationToken": None, "isLastPage": True}
    if not decodo_fetch.enabled():
        return None

    country_param = (countries or country or "US").strip()
    url = search_url(
        account_owner=owner or None,
        keyword=kw or None,
        company_id=cid or None,
        countries=country_param,
        start_date=start_date,
        end_date=end_date,
        pagination_token=pagination_token,
    )
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or len(html) < 5000:
        log.warning("linkedin_ads_native_weak", status=status, length=len(html))
        return None

    meta = extract_search_meta(html)
    rows = extract_ads(html, country=country_param, limit=max(0, int(limit)))
    if not rows:
        if "ad-library" in html.lower():
            return {
                "ads": [],
                "totalAds": meta.get("totalAds") or 0,
                "paginationToken": meta.get("paginationToken"),
                "isLastPage": True if meta.get("isLastPage") is None else meta.get("isLastPage"),
            }
        log.warning("linkedin_ads_native_no_ads", length=len(html))
        return None

    if enrich:
        rows = await _enrich_with_details(rows)

    log.info(
        "linkedin_ads_native_search_ok",
        count=len(rows),
        q=(owner or kw or cid)[:40],
        country=country_param,
        total=meta.get("totalAds"),
    )
    return {
        "ads": rows,
        "totalAds": meta.get("totalAds"),
        "paginationToken": meta.get("paginationToken"),
        "isLastPage": meta.get("isLastPage"),
    }
