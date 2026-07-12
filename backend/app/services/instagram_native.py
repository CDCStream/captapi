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
from typing import Any

import httpx
import structlog

from app.services.http_fetch import proxy_for
from app.utils.formatters import safe_float, safe_str

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
    media = items[0]

    videos = media.get("video_versions") or []
    video_url = safe_str(videos[0].get("url")) if videos else None
    images = (media.get("image_versions2") or {}).get("candidates") or []
    caption = media.get("caption")
    return {
        "videoUrl": video_url,
        "thumbnailUrl": safe_str(images[0].get("url")) if images else None,
        "duration": safe_float(media.get("video_duration")),
        "caption": safe_str(caption.get("text")) if isinstance(caption, dict) else None,
        "username": safe_str((media.get("user") or {}).get("username")),
    }
