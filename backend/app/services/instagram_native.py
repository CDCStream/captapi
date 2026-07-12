"""Native Instagram reel media resolver.

Uses Instagram's public PolarisPostRootQuery GraphQL endpoint (the one the
logged-out web player calls), which returns v1-format media incl.
``video_versions`` in <1s without authentication. Only a fresh ``csrftoken``
cookie + ``X-CSRFToken`` header pair is required.

Instagram deprecated the old ``xdt_shortcode_media`` doc_id in June 2026
(which is also why Decodo's ``instagram_graphql_post`` target is disabled);
this doc_id is its replacement.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog

from app.services.http_fetch import proxy_for
from app.utils.formatters import safe_float, safe_int, safe_str

log = structlog.get_logger(__name__)

_POST_DOC_ID = "27128499623469141"  # PolarisPostRootQuery
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# One rate-limited tier shouldn't kill the fast path; each tier gets its own
# session (fresh IP + csrf token).
_TIERS: tuple[str, ...] = ("datacenter", "residential")


async def fetch_reel_media(shortcode: str) -> dict[str, Any] | None:
    """Resolve a reel/post's media info natively. ~1-2s total.

    Returns {"videoUrl", "thumbnailUrl", "duration", "caption", "username"}
    or None (caller falls back to Apify).
    """
    media = await _fetch_item(shortcode)
    if media is None:
        return None
    videos = media.get("video_versions") or []
    images = (media.get("image_versions2") or {}).get("candidates") or []
    caption = media.get("caption")
    return {
        "videoUrl": safe_str(videos[0].get("url")) if videos else None,
        "thumbnailUrl": safe_str(images[0].get("url")) if images else None,
        "duration": safe_float(media.get("video_duration")),
        "caption": safe_str(caption.get("text")) if isinstance(caption, dict) else None,
        "username": safe_str((media.get("user") or {}).get("username")),
    }


_MEDIA_TYPE_NAMES = {1: "Image", 2: "Video", 8: "Sidecar"}
_HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)
_MENTION_RE = re.compile(r"@([A-Za-z0-9_.]+)")
# DASH manifest carries the duration when `video_duration` is absent,
# e.g. mediaPresentationDuration="PT0H0M30.033S".
_MPD_DURATION_RE = re.compile(
    r'mediaPresentationDuration="PT(?:(\d+)H)?(?:(\d+)M)?([\d.]+)S"'
)


def _video_duration(media: dict[str, Any], cover: dict[str, Any]) -> float | None:
    direct = safe_float(media.get("video_duration") or cover.get("video_duration"))
    if direct:
        return direct
    m = _MPD_DURATION_RE.search(
        safe_str(media.get("video_dash_manifest") or cover.get("video_dash_manifest")) or ""
    )
    if not m:
        return None
    hours, minutes, seconds = int(m.group(1) or 0), int(m.group(2) or 0), float(m.group(3))
    return round(hours * 3600 + minutes * 60 + seconds, 3)


async def fetch_post_details(shortcode: str) -> dict[str, Any] | None:
    """Full post/reel/carousel details in the /v1/instagram/details shape.

    Same upstream numbers as the Apify actor (both read Instagram's own
    data) at ~3-4s instead of an actor run. Returns None so the caller can
    fall back to Apify.
    """
    media = await _fetch_item(shortcode)
    if media is None:
        return None

    caption_obj = media.get("caption")
    caption = safe_str(caption_obj.get("text")) if isinstance(caption_obj, dict) else None
    user = media.get("user") or {}
    username = safe_str(user.get("username"))

    # For carousels the media lives on the children; lead with the cover item.
    cover = (media.get("carousel_media") or [media])[0]
    videos = cover.get("video_versions") or []
    images = (cover.get("image_versions2") or {}).get("candidates") or []

    taken_at = safe_int(media.get("taken_at"))
    published = (
        datetime.fromtimestamp(taken_at, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if taken_at
        else None
    )

    return {
        "platform": "instagram",
        "url": f"https://www.instagram.com/p/{shortcode}/",
        "id": safe_str(media.get("code")) or shortcode,
        "type": _MEDIA_TYPE_NAMES.get(safe_int(media.get("media_type")) or 0),
        "productType": safe_str(media.get("product_type")),
        "caption": caption,
        "description": caption,
        "publishedAt": published,
        "durationSeconds": _video_duration(media, cover),
        "thumbnailUrl": safe_str(images[0].get("url")) if images else None,
        "videoUrl": safe_str(videos[0].get("url")) if videos else None,
        "author": {
            "username": username,
            "displayName": safe_str(user.get("full_name")),
            "url": f"https://instagram.com/{username}" if username else None,
            "verified": user.get("is_verified"),
            "profileImage": safe_str(user.get("profile_pic_url")),
        },
        "engagement": {
            "views": safe_int(media.get("play_count") or media.get("view_count")),
            "likes": safe_int(media.get("like_count")) or 0,
            "comments": safe_int(media.get("comment_count")) or 0,
        },
        "hashtags": _HASHTAG_RE.findall(caption or ""),
        "mentions": _MENTION_RE.findall(caption or ""),
    }


async def _fetch_item(shortcode: str) -> dict[str, Any] | None:
    for tier in _TIERS:
        try:
            media = await _fetch_via(tier, shortcode)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            log.info("ig_native_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        if media is not None:
            return media
    return None


async def _fetch_via(tier: str, shortcode: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient(
        timeout=10, proxy=proxy_for(tier), follow_redirects=True
    ) as client:
        # A GET to the homepage sets the csrftoken cookie the GraphQL
        # endpoint requires (cookie alone is rejected; header must match).
        await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
        csrf = client.cookies.get("csrftoken")
        if not csrf:
            return None
        resp = await client.post(
            "https://www.instagram.com/graphql/query",
            data={
                "doc_id": _POST_DOC_ID,
                "variables": json.dumps(
                    {
                        "shortcode": shortcode,
                        "__relay_internal__pv__PolarisAIGMMediaWebLabelEnabledrelayprovider": False,
                    },
                    separators=(",", ":"),
                ),
            },
            headers={
                "User-Agent": _UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-IG-App-ID": "936619743392459",
                "X-CSRFToken": csrf,
                "Referer": f"https://www.instagram.com/reel/{shortcode}/",
            },
        )
        if resp.status_code != 200:
            log.info("ig_native_http_error", tier=tier, status=resp.status_code)
            return None
        payload = resp.json()

    info = (payload.get("data") or {}).get("xdt_api__v1__media__shortcode__web_info") or {}
    items = info.get("items") or []
    if not items:
        return None
    return items[0]
