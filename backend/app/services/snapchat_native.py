"""Snapchat public profile via Decodo HTML (__NEXT_DATA__). No Apify."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str, strip_empty

log = structlog.get_logger(__name__)

CREDIT_SNAPCHAT_PROFILE = 1

_NEXT_RE = re.compile(
    r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(\{.*?\})</script>',
    re.S,
)

# Snapchat snapMediaType enum (web profile).
_MEDIA_TYPES = {0: "image", 1: "video", 2: "video"}


def _val(value: Any) -> Any:
    """Unwrap Snapchat ``{"value": ...}`` protobuf-json wrappers."""
    if isinstance(value, dict) and "value" in value and len(value) <= 2:
        return value.get("value")
    return value


def _ms_to_iso(value: Any) -> str | None:
    raw = _val(value)
    ms = safe_int(raw)
    if ms is None or ms <= 0:
        return None
    # Snapchat sometimes sends seconds; treat small values as seconds.
    if ms < 10_000_000_000:
        ms *= 1000
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (OSError, OverflowError, ValueError):
        return None


def _category_label(raw: str | None) -> str | None:
    """Turn ``public-profile-category-v3-business-group`` into ``Business Group``."""
    s = safe_str(raw)
    if not s:
        return None
    s = re.sub(r"^public-profile-(?:category|subcategory)-v3-", "", s, flags=re.I)
    s = s.replace("-", " ").strip()
    return s.title() if s else None


def _snap_row(raw: dict[str, Any]) -> dict[str, Any] | None:
    urls = raw.get("snapUrls") if isinstance(raw.get("snapUrls"), dict) else {}
    media_url = safe_str(urls.get("mediaUrl"))
    preview = safe_str(_val(urls.get("mediaPreviewUrl")))
    media_type = safe_int(raw.get("snapMediaType"))
    ts = safe_int(_val(raw.get("timestampInSec")))
    published = None
    if ts and ts > 0:
        try:
            published = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        except (OSError, OverflowError, ValueError):
            published = None
    snap_id = safe_str(_val(raw.get("snapId")))
    if not media_url and not preview and not snap_id:
        return None
    return strip_empty(
        {
            "snapIndex": safe_int(raw.get("snapIndex")),
            "snapId": snap_id,
            "snapMediaType": media_type,
            "mediaType": _MEDIA_TYPES.get(media_type or -1),
            "mediaUrl": media_url,
            "mediaPreviewUrl": preview,
            "timestampInSec": ts,
            "publishedAt": published,
        }
    )


def _snap_list(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for row in raw:
        if isinstance(row, dict):
            mapped = _snap_row(row)
            if mapped:
                out.append(mapped)
    return out


def _highlight(raw: dict[str, Any]) -> dict[str, Any] | None:
    snaps = _snap_list(raw.get("snapList"))
    first = snaps[0] if snaps else None
    thumb = safe_str(_val(raw.get("thumbnailUrl")))
    title = safe_str(raw.get("storyTitle"))
    hid = safe_str(raw.get("highlightId") or _val(raw.get("storyId")))
    if not hid and not title and not snaps:
        return None
    return strip_empty(
        {
            "highlightId": hid,
            "storyTitle": title,
            "storySubtitle": safe_str(raw.get("storySubtitle")),
            "emoji": safe_str(raw.get("emoji")),
            "thumbnailUrl": thumb,
            "snapCount": len(snaps) if snaps else None,
            "firstSnapUrl": (first or {}).get("mediaUrl"),
            "firstSnapType": (first or {}).get("mediaType"),
            "snapList": snaps or None,
        }
    )


def _highlights(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for row in raw:
        if isinstance(row, dict):
            mapped = _highlight(row)
            if mapped:
                out.append(mapped)
    return out


def _spotlight_item(
    highlight: dict[str, Any] | None, meta: dict[str, Any] | None
) -> dict[str, Any] | None:
    highlight = highlight if isinstance(highlight, dict) else {}
    meta = meta if isinstance(meta, dict) else {}
    video = meta.get("videoMetadata") if isinstance(meta.get("videoMetadata"), dict) else {}
    engagement = (
        meta.get("engagementStats") if isinstance(meta.get("engagementStats"), dict) else {}
    )
    snaps = _snap_list(highlight.get("snapList"))
    first = snaps[0] if snaps else None
    content_url = safe_str(video.get("contentUrl")) or (first or {}).get("mediaUrl")
    story_id = safe_str(_val(highlight.get("storyId")) or (first or {}).get("snapId"))
    if not content_url and not story_id and not video:
        return None
    creator = video.get("creator") if isinstance(video.get("creator"), dict) else {}
    person = (
        creator.get("personCreator")
        if isinstance(creator.get("personCreator"), dict)
        else creator
    )
    hashtags = []
    for tag in meta.get("hashtags") or []:
        if isinstance(tag, str):
            hashtags.append(tag)
        elif isinstance(tag, dict):
            t = safe_str(tag.get("name") or tag.get("tag") or tag.get("title"))
            if t:
                hashtags.append(t.lstrip("#"))
    return strip_empty(
        {
            "id": story_id,
            "title": safe_str(video.get("name") or highlight.get("storyTitle")),
            "description": safe_str(video.get("description")),
            "caption": safe_str(video.get("embeddedTextCaption")),
            "thumbnailUrl": safe_str(
                video.get("thumbnailUrl") or _val(highlight.get("thumbnailUrl"))
            ),
            "contentUrl": content_url,
            "durationMs": safe_int(video.get("durationMs")),
            "width": safe_int(video.get("width")),
            "height": safe_int(video.get("height")),
            "uploadDateMs": safe_int(video.get("uploadDateMs")),
            "publishedAt": _ms_to_iso(video.get("uploadDateMs")),
            "deeplink": safe_str(meta.get("deeplink")),
            "hashtags": hashtags or None,
            "creator": strip_empty(
                {
                    "username": safe_str(person.get("username")),
                    "displayName": safe_str(person.get("name")),
                    "url": safe_str(person.get("url")),
                }
            )
            or None,
            "engagement": strip_empty(
                {
                    "views": safe_int(
                        engagement.get("viewCount") or video.get("viewCount")
                    ),
                    "shares": safe_int(
                        engagement.get("shareCount") or video.get("shareCount")
                    ),
                    "comments": safe_int(engagement.get("commentCount")),
                    "boosts": safe_int(engagement.get("boostCount")),
                    "recommends": safe_int(engagement.get("recommendCount")),
                }
            )
            or None,
            "snapList": snaps or None,
        }
    )


def _spotlights(highlights: Any, metadata: Any) -> list[dict[str, Any]]:
    hl = highlights if isinstance(highlights, list) else []
    md = metadata if isinstance(metadata, list) else []
    n = max(len(hl), len(md))
    out: list[dict[str, Any]] = []
    for i in range(n):
        h = hl[i] if i < len(hl) and isinstance(hl[i], dict) else None
        m = md[i] if i < len(md) and isinstance(md[i], dict) else None
        mapped = _spotlight_item(h, m)
        if mapped:
            out.append(mapped)
    return out


def _related(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        info = (
            row.get("publicProfileInfo")
            if isinstance(row.get("publicProfileInfo"), dict)
            else row
        )
        username = safe_str(info.get("username"))
        if not username:
            continue
        link = (
            info.get("subscribeLink")
            if isinstance(info.get("subscribeLink"), dict)
            else row.get("subscribeLink")
            if isinstance(row.get("subscribeLink"), dict)
            else None
        )
        out.append(
            strip_empty(
                {
                    "username": username,
                    "displayName": safe_str(info.get("title") or info.get("displayName")),
                    "profileUrl": f"https://www.snapchat.com/@{username}",
                    "profilePictureUrl": safe_str(
                        info.get("profilePictureUrl") or info.get("avatar")
                    ),
                    "isVerified": bool(info.get("badge")) if info.get("badge") is not None else None,
                    "hasStory": bool(info.get("hasStory"))
                    if info.get("hasStory") is not None
                    else None,
                    "hasCuratedHighlights": bool(info.get("hasCuratedHighlights"))
                    if info.get("hasCuratedHighlights") is not None
                    else None,
                    "hasSpotlightHighlights": bool(info.get("hasSpotlightHighlights"))
                    if info.get("hasSpotlightHighlights") is not None
                    else None,
                    "subscribeLink": strip_empty(
                        {
                            "oneLinkBaseUrl": safe_str((link or {}).get("oneLinkBaseUrl")),
                            "deepLinkUrl": safe_str(
                                (link or {}).get("deepLinkUrl")
                                or f"https://www.snapchat.com/@{username}"
                            ),
                            "iosAppStoreUrl": safe_str((link or {}).get("iosAppStoreUrl")),
                        }
                    )
                    or None,
                }
            )
        )
    return out


def _story(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    snaps = _snap_list(raw.get("snapList"))
    if not snaps:
        return None
    return strip_empty(
        {
            "snapCount": len(snaps),
            "thumbnailUrl": safe_str(_val(raw.get("thumbnailUrl"))),
            "snapList": snaps,
        }
    )


async def fetch_user_profile(username: str) -> dict[str, Any] | None:
    """Public Snapchat profile page → rich profile shape for the router."""
    handle = (username or "").strip().lstrip("@").rstrip("/")
    if not handle:
        return None
    if not decodo_fetch.enabled():
        return None

    url = f"https://www.snapchat.com/@{handle}"
    got = await decodo_fetch.fetch_url(url, timeout=90.0, geo="US")
    if not got:
        return None
    status, html = got
    if status != 200 or not html or len(html) < 2000:
        return None

    match = _NEXT_RE.search(html)
    if not match:
        log.info("snapchat_native_no_next_data", username=handle)
        return None
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

    page = (payload.get("props") or {}).get("pageProps") or {}
    profile_wrap = page.get("userProfile") if isinstance(page.get("userProfile"), dict) else {}
    info = profile_wrap.get("publicProfileInfo")
    if not isinstance(info, dict) or not info.get("username"):
        log.info("snapchat_native_no_profile", username=handle)
        return None

    uname = safe_str(info.get("username")) or handle
    category_id = safe_str(info.get("categoryStringId"))
    subcategory_id = safe_str(info.get("subcategoryStringId"))
    highlights = _highlights(page.get("curatedHighlights") or [])
    spotlights = _spotlights(
        page.get("spotlightHighlights"), page.get("spotlightStoryMetadata")
    )
    related = _related(info.get("relatedAccountsInfo") or [])
    story = _story(page.get("story"))
    badge = info.get("badge")

    out = strip_empty(
        {
            "username": uname,
            "mutableUsername": uname,
            "url": f"https://www.snapchat.com/@{uname}",
            "webUrl": f"https://www.snapchat.com/@{uname}",
            "displayName": safe_str(info.get("title") or info.get("mutableName")),
            "title": safe_str(info.get("title")),
            "bio": safe_str(info.get("bio")),
            "description": safe_str(info.get("bio")),
            "categoryId": category_id,
            "category": _category_label(category_id),
            "subcategoryId": subcategory_id,
            "subcategory": _category_label(subcategory_id),
            "subscriberCount": safe_int(info.get("subscriberCount")),
            "badge": safe_int(badge) if badge is not None else None,
            "isVerified": bool(badge),
            "verified": bool(badge),
            "profilePictureUrl": safe_str(info.get("profilePictureUrl")),
            "squareHeroImageUrl": safe_str(info.get("squareHeroImageUrl")),
            "snapcodeImageUrl": safe_str(info.get("snapcodeImageUrl")),
            "websiteUrl": safe_str(info.get("websiteUrl")),
            "businessProfileId": safe_str(info.get("businessProfileId")),
            "creationTimestampMs": safe_int(_val(info.get("creationTimestampMs"))),
            "createdAt": _ms_to_iso(info.get("creationTimestampMs")),
            "lastUpdateTimestampMs": safe_int(_val(info.get("lastUpdateTimestampMs"))),
            "updatedAt": _ms_to_iso(info.get("lastUpdateTimestampMs")),
            "hasStory": bool(info.get("hasStory")) if info.get("hasStory") is not None else None,
            "hasCuratedHighlights": bool(info.get("hasCuratedHighlights"))
            if info.get("hasCuratedHighlights") is not None
            else None,
            "hasSpotlightHighlights": bool(info.get("hasSpotlightHighlights"))
            if info.get("hasSpotlightHighlights") is not None
            else None,
            "story": story,
            "curatedHighlights": highlights,
            "highlights": highlights,
            "spotlightHighlights": spotlights,
            "relatedAccounts": related,
        }
    )
    log.info(
        "snapchat_native_profile_ok",
        username=uname,
        subscribers=out.get("subscriberCount"),
        highlights=len(highlights),
        spotlights=len(spotlights),
        story_snaps=len((story or {}).get("snapList") or []),
    )
    return out
