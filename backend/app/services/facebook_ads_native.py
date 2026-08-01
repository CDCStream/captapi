"""Native Meta Ad Library via Decodo JS-rendered HTML (no Apify).

Facebook blocks plain datacenter/residential fetches (403). Decodo with
``headless=html`` returns the hydrated Ad Library page, which embeds
``collated_results`` (search) or a deeplinked ad object (``?id=``). Cost is
one Decodo render per call.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import structlog

from app.services import decodo_fetch

log = structlog.get_logger(__name__)

_LIBRARY = "https://www.facebook.com/ads/library/"
_AD_ID_RE = re.compile(r"(?:[?&]id=|/ads/library/.*?id=)(\d{5,})", re.I)


def search_url(
    q: str,
    country: str,
    *,
    active_status: str = "all",
    ad_type: str = "all",
    search_type: str = "keyword_unordered",
    media_type: str = "all",
    sort_by: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Build a Meta Ad Library search URL (same query params the public UI uses)."""
    params: dict[str, str] = {
        "active_status": (active_status or "all").lower(),
        "ad_type": (ad_type or "all").lower(),
        "country": (country or "US").upper(),
        "q": q,
        "search_type": (search_type or "keyword_unordered").lower(),
        "media_type": (media_type or "all").lower(),
    }
    if sort_by:
        params["sort_data[mode]"] = sort_by.lower()
        params["sort_data[direction]"] = "desc"
    if start_date:
        params["start_date[min]"] = start_date[:10]
    if end_date:
        params["start_date[max]"] = end_date[:10]
    return f"{_LIBRARY}?{urlencode(params)}"


def ad_id_from_url(url_or_id: str) -> str | None:
    raw = (url_or_id or "").strip()
    if not raw:
        return None
    if raw.isdigit() and len(raw) >= 5:
        return raw
    m = _AD_ID_RE.search(raw)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{10,})\b", raw)
    return m.group(1) if m else None


def ad_library_url(url_or_id: str, *, country: str = "US") -> str | None:
    aid = ad_id_from_url(url_or_id)
    if not aid:
        return None
    return f"{_LIBRARY}?{urlencode({'id': aid, 'country': (country or 'US').upper()})}"


def company_library_url(url_or_page: str, country: str) -> str:
    """Build an Ad Library URL for a page / existing library link."""
    raw = (url_or_page or "").strip()
    country = (country or "US").upper()
    if not raw:
        return search_url("", country)

    if "ads/library" in raw.lower():
        parsed = urlparse(raw)
        qs = parse_qs(parsed.query)
        if "country" not in qs:
            sep = "&" if parsed.query else "?"
            return f"{raw}{sep}country={country}"
        return raw

    page_id = None
    m = re.search(r"(?:profile\.php\?id=|page_id=|view_all_page_id=)(\d+)", raw, re.I)
    if m:
        page_id = m.group(1)
    elif re.fullmatch(r"\d{5,}", raw):
        page_id = raw
    if page_id:
        params = {
            "active_status": "all",
            "ad_type": "all",
            "country": country,
            "view_all_page_id": page_id,
            "media_type": "all",
        }
        return f"{_LIBRARY}?{urlencode(params)}"

    m = re.search(r"facebook\.com/([^/?#]+)", raw, re.I)
    slug = m.group(1) if m else raw
    if slug.lower() in {"pages", "people", "watch", "groups", "events"}:
        slug = raw
    return search_url(slug, country)


def _json_array_at(html: str, start: int) -> list[Any] | None:
    """Parse a JSON array starting at ``start`` (index of '[')."""
    if start < 0 or start >= len(html) or html[start] != "[":
        return None
    depth = 0
    i = start
    n = len(html)
    while i < n:
        ch = html[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                try:
                    data = json.loads(html[start : i + 1])
                except ValueError:
                    return None
                return data if isinstance(data, list) else None
        elif ch == '"':
            i += 1
            while i < n:
                if html[i] == "\\":
                    i += 2
                    continue
                if html[i] == '"':
                    break
                i += 1
        i += 1
    return None


def extract_collated_ads(html: str) -> list[dict[str, Any]]:
    """Pull unique ad objects from embedded ``collated_results`` arrays."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in re.finditer(r'"collated_results"\s*:\s*\[', html):
        arr = _json_array_at(html, m.end() - 1)
        if not arr:
            continue
        for item in arr:
            if not isinstance(item, dict):
                continue
            aid = str(item.get("ad_archive_id") or item.get("adArchiveId") or "").strip()
            if not aid or aid in seen:
                continue
            seen.add(aid)
            out.append(item)
    return out


def extract_ad_by_id(html: str, ad_id: str) -> dict[str, Any] | None:
    """Find the deeplinked / embedded ad object for ``ad_id``."""
    aid = str(ad_id or "").strip()
    if not aid or not html:
        return None

    # Prefer matching collated_results rows when present.
    for item in extract_collated_ads(html):
        if str(item.get("ad_archive_id") or item.get("adArchiveId") or "") == aid:
            return item

    # Deeplink pages often embed the target outside collated_results.
    for needle in (f'"ad_archive_id":"{aid}"', f'"ad_archive_id": "{aid}"'):
        pos = html.find(needle)
        if pos < 0:
            continue
        depth = 0
        start = pos
        for j in range(pos, max(0, pos - 900_000), -1):
            ch = html[j]
            if ch == "}":
                depth += 1
            elif ch == "{":
                if depth == 0:
                    start = j
                    break
                depth -= 1
        try:
            obj, _end = json.JSONDecoder().raw_decode(html[start:])
        except ValueError:
            continue
        if isinstance(obj, dict) and str(obj.get("ad_archive_id") or "") == aid:
            return obj
    return None


def _unix_iso(value: Any) -> str | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return str(value) if value else None
    if ts > 10_000_000_000:  # ms
        ts //= 1000
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _extract_search_results_count(html: str) -> int | None:
    """Best-effort total hit count from embedded Ad Library JSON."""
    for pattern in (
        r'"searchResultsCount"\s*:\s*(\d+)',
        r'"count"\s*:\s*(\d{2,})',
        r'"totalCount"\s*:\s*(\d+)',
    ):
        m = re.search(pattern, html)
        if not m:
            continue
        try:
            n = int(m.group(1))
        except ValueError:
            continue
        if n > 0:
            return n
    return None


def to_normalize_shape(item: dict[str, Any]) -> dict[str, Any]:
    """Map Meta ``collated_results`` row → shape ``_normalize_ad`` understands."""
    snap_in = item.get("snapshot") if isinstance(item.get("snapshot"), dict) else {}
    body = snap_in.get("body")
    body_text = body.get("text") if isinstance(body, dict) else body

    cards_out: list[dict[str, Any]] = []
    for card in snap_in.get("cards") or []:
        if not isinstance(card, dict):
            continue
        card_body = card.get("body")
        if isinstance(card_body, dict):
            card_body = card_body.get("text")
        cards_out.append(
            {
                "body": card_body or card.get("body"),
                "title": card.get("title"),
                "ctaText": card.get("cta_text") or card.get("ctaText"),
                "linkUrl": card.get("link_url") or card.get("linkUrl"),
                "linkDescription": card.get("link_description") or card.get("linkDescription"),
                "caption": card.get("caption"),
                "originalImageUrl": card.get("original_image_url") or card.get("originalImageUrl"),
                "resizedImageUrl": card.get("resized_image_url") or card.get("resizedImageUrl"),
                "videoHdUrl": card.get("video_hd_url") or card.get("videoHdUrl"),
                "videoSdUrl": card.get("video_sd_url") or card.get("videoSdUrl"),
                "videoPreviewImageUrl": card.get("video_preview_image_url")
                or card.get("videoPreviewImageUrl"),
            }
        )

    images = []
    for img in snap_in.get("images") or []:
        if isinstance(img, dict):
            images.append(
                {
                    "originalImageUrl": img.get("original_image_url") or img.get("originalImageUrl"),
                    "resizedImageUrl": img.get("resized_image_url") or img.get("resizedImageUrl"),
                }
            )
        elif isinstance(img, str):
            images.append(img)

    videos = []
    for vid in snap_in.get("videos") or []:
        if isinstance(vid, dict):
            videos.append(
                {
                    "videoHdUrl": vid.get("video_hd_url") or vid.get("videoHdUrl"),
                    "videoSdUrl": vid.get("video_sd_url") or vid.get("videoSdUrl"),
                    "videoPreviewImageUrl": vid.get("video_preview_image_url")
                    or vid.get("videoPreviewImageUrl"),
                }
            )

    page_name = item.get("page_name") or snap_in.get("page_name")
    page_id = item.get("page_id") or snap_in.get("page_id")
    platforms = item.get("publisher_platform") or item.get("publisherPlatform") or []
    if isinstance(platforms, str):
        platforms = [platforms]

    return {
        "adArchiveId": item.get("ad_archive_id") or item.get("adArchiveId"),
        "pageId": page_id,
        "pageName": page_name,
        "isActive": item.get("is_active") if "is_active" in item else item.get("isActive"),
        "isAaaEligible": item.get("is_aaa_eligible")
        if "is_aaa_eligible" in item
        else item.get("isAaaEligible"),
        "publisherPlatforms": [str(p).upper() for p in platforms if p],
        "startDate": _unix_iso(item.get("start_date") or item.get("startDate")),
        "endDate": _unix_iso(item.get("end_date") or item.get("endDate")),
        "totalActiveTime": item.get("total_active_time") or item.get("totalActiveTime"),
        "impressionsWithIndex": item.get("impressions_with_index") or item.get("impressionsWithIndex"),
        "spend": item.get("spend"),
        "reachEstimate": item.get("reach_estimate") or item.get("reachEstimate"),
        "politicalCountries": item.get("political_countries") or item.get("politicalCountries"),
        "targetedOrReachedCountries": item.get("targeted_or_reached_countries")
        or item.get("targetedOrReachedCountries"),
        "snapshot": {
            "pageName": page_name,
            "pageProfileUri": snap_in.get("page_profile_uri") or snap_in.get("pageProfileUri"),
            "pageProfilePictureUrl": snap_in.get("page_profile_picture_url")
            or snap_in.get("pageProfilePictureUrl"),
            "pageLikeCount": snap_in.get("page_like_count") or snap_in.get("pageLikeCount"),
            "pageCategories": snap_in.get("page_categories") or snap_in.get("pageCategories") or [],
            "pageEntityType": snap_in.get("page_entity_type") or snap_in.get("pageEntityType"),
            "pageIsDeleted": snap_in.get("page_is_deleted")
            if "page_is_deleted" in snap_in
            else snap_in.get("pageIsDeleted"),
            "ctaText": snap_in.get("cta_text") or snap_in.get("ctaText"),
            "ctaType": snap_in.get("cta_type") or snap_in.get("ctaType"),
            "linkUrl": snap_in.get("link_url") or snap_in.get("linkUrl"),
            "linkDescription": snap_in.get("link_description") or snap_in.get("linkDescription"),
            "caption": snap_in.get("caption"),
            "title": snap_in.get("title"),
            "displayFormat": snap_in.get("display_format") or snap_in.get("displayFormat"),
            "brandedContent": snap_in.get("branded_content") or snap_in.get("brandedContent"),
            "disclaimerLabel": snap_in.get("disclaimer_label") or snap_in.get("disclaimerLabel"),
            "byline": snap_in.get("byline"),
            "body": {"text": body_text} if body_text else snap_in.get("body"),
            "cards": cards_out,
            "images": images,
            "videos": videos,
        },
    }


async def _fetch_ads_page(library_url: str, *, limit: int) -> dict[str, Any] | None:
    """Fetch Ad Library HTML and return ``{ads, searchResultsCount, hasMore}``."""
    if not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(library_url, timeout=120.0, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or len(html) < 5000:
        log.warning("facebook_ads_native_weak", status=status, length=len(html))
        return None
    raw = extract_collated_ads(html)
    count = _extract_search_results_count(html)
    if not raw:
        # Valid empty result page (no matches) vs parse failure.
        if "ad_library" in html.lower() or "ads/library" in html.lower():
            return {"ads": [], "searchResultsCount": count or 0, "hasMore": False}
        log.warning("facebook_ads_native_no_ads", length=len(html))
        return None
    want = max(0, int(limit))
    mapped = [to_normalize_shape(a) for a in raw]
    ads = mapped[:want] if want else mapped
    has_more = bool(count and count > len(ads)) or (want > 0 and len(mapped) > want)
    return {
        "ads": ads,
        "searchResultsCount": count,
        "hasMore": has_more,
    }


async def _fetch_ads(library_url: str, *, limit: int) -> list[dict[str, Any]] | None:
    page = await _fetch_ads_page(library_url, limit=limit)
    if page is None:
        return None
    return list(page.get("ads") or [])


async def search_ads(
    q: str,
    *,
    country: str = "US",
    limit: int = 20,
    active_status: str = "active",
    ad_type: str = "all",
    search_type: str = "keyword_unordered",
    media_type: str = "all",
    sort_by: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any] | None:
    """Keyword search. Returns ``{ads, searchResultsCount, hasMore}`` or ``None``."""
    query = (q or "").strip()
    if len(query) < 2:
        return {"ads": [], "searchResultsCount": 0, "hasMore": False}
    url = search_url(
        query,
        country,
        active_status=active_status,
        ad_type=ad_type,
        search_type=search_type,
        media_type=media_type,
        sort_by=sort_by,
        start_date=start_date,
        end_date=end_date,
    )
    page = await _fetch_ads_page(url, limit=limit)
    if page is not None:
        log.info(
            "facebook_ads_native_search_ok",
            count=len(page.get("ads") or []),
            q=query[:40],
            country=country,
            status=active_status,
        )
    return page


async def company_ads(
    url_or_page: str, *, country: str = "US", limit: int = 20
) -> list[dict[str, Any]] | None:
    url = company_library_url(url_or_page, country)
    rows = await _fetch_ads(url, limit=limit)
    if rows is not None:
        log.info("facebook_ads_native_company_ok", count=len(rows), country=country)
    return rows


async def search_companies(
    q: str, *, country: str = "US", limit: int = 20
) -> list[dict[str, Any]] | None:
    """Search ads then unique advertisers (same shape as Apify path input)."""
    # Pull a wider ad window so company dedupe has enough pages.
    page = await search_ads(q, country=country, limit=max(limit * 3, limit))
    if page is None:
        return None
    return list(page.get("ads") or [])


async def ad_details(url_or_id: str, *, country: str = "US") -> dict[str, Any] | None:
    """Fetch one Meta Ad Library ad by id/URL → ``_normalize_ad`` input shape."""
    page_url = ad_library_url(url_or_id, country=country)
    aid = ad_id_from_url(url_or_id)
    if not page_url or not aid or not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(page_url, timeout=120.0, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or len(html) < 5000:
        log.warning("facebook_ads_native_detail_weak", status=status, length=len(html), ad_id=aid)
        return None
    raw = extract_ad_by_id(html, aid)
    if not raw:
        log.warning("facebook_ads_native_detail_miss", ad_id=aid, length=len(html))
        return None
    mapped = to_normalize_shape(raw)
    # Country is sometimes omitted on deeplink blobs; keep the request country.
    if not mapped.get("targetedOrReachedCountries"):
        mapped["targetedOrReachedCountries"] = [(country or "US").upper()]
    log.info("facebook_ads_native_detail_ok", ad_id=aid)
    return mapped
