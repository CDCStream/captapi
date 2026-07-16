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

import base64
import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog

from app.services.http_fetch import proxy_for
from app.services.instagram_decodo import hidden_count
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
    # Reels can be carousels; the playable video lives on the cover child.
    cover = (media.get("carousel_media") or [media])[0]
    videos = media.get("video_versions") or cover.get("video_versions") or []
    images = (media.get("image_versions2") or {}).get("candidates") or []
    caption = media.get("caption")
    return {
        "videoUrl": safe_str(videos[0].get("url")) if videos else None,
        "thumbnailUrl": safe_str(images[0].get("url")) if images else None,
        "duration": _video_duration(media, cover),
        "caption": safe_str(caption.get("text")) if isinstance(caption, dict) else None,
        "username": safe_str((media.get("user") or {}).get("username")),
    }


_MEDIA_TYPE_NAMES = {1: "Image", 2: "Video", 8: "Sidecar"}
# Instagram hashtags must contain at least one non-numeric character, so
# "#1" in a caption ("ranked #1") is not a real hashtag - require one letter
# or underscore to avoid capturing purely numeric tokens.
_HASHTAG_RE = re.compile(r"#(\w*[^\W\d]\w*)", re.UNICODE)
# Same as instagram_decodo._MENTION_RE: usernames may contain dots but never
# end with one, so "@herbalife." in a caption must capture "herbalife".
_MENTION_RE = re.compile(r"@([A-Za-z0-9_](?:[A-Za-z0-9_.]*[A-Za-z0-9_])?)")
# DASH manifest carries the duration when `video_duration` is absent,
# e.g. mediaPresentationDuration="PT0H0M30.033S".
_MPD_DURATION_RE = re.compile(
    r'mediaPresentationDuration="PT(?:(\d+)H)?(?:(\d+)M)?([\d.]+)S"'
)


def _duration_from_video_url(url: str) -> float | None:
    """Instagram CDN video URLs embed the duration in the base64 ``efg`` query
    param (JSON with a ``duration_s`` field). Coarse (integer seconds) but a
    useful fallback when the media object omits video_duration/dash manifest."""
    if not url:
        return None
    try:
        efg = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("efg", [None])[0]
        if not efg:
            return None
        padded = efg + "=" * (-len(efg) % 4)
        blob = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8", "ignore"))
        dur = safe_float(blob.get("duration_s"))
        return round(dur, 3) if dur else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def _video_duration(media: dict[str, Any], cover: dict[str, Any]) -> float | None:
    direct = safe_float(media.get("video_duration") or cover.get("video_duration"))
    if direct:
        return round(direct, 3)
    m = _MPD_DURATION_RE.search(
        safe_str(media.get("video_dash_manifest") or cover.get("video_dash_manifest")) or ""
    )
    if m:
        hours, minutes, seconds = int(m.group(1) or 0), int(m.group(2) or 0), float(m.group(3))
        return round(hours * 3600 + minutes * 60 + seconds, 3)
    videos = media.get("video_versions") or cover.get("video_versions") or []
    return _duration_from_video_url(safe_str(videos[0].get("url")) if videos else "")


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
        "postType": _MEDIA_TYPE_NAMES.get(safe_int(media.get("media_type")) or 0),
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
        # No "views": Instagram hides play counts from the logged-out API for
        # clips, so the field can't be served consistently across post types.
        "engagement": {
            "likes": hidden_count(media.get("like_count")),
            "comments": hidden_count(media.get("comment_count")),
        },
        "hashtags": _HASHTAG_RE.findall(caption or ""),
        "mentions": _MENTION_RE.findall(caption or ""),
    }


async def fetch_highlight_reel(highlight_id: str) -> dict[str, Any] | None:
    """Details for one Story Highlight album via the logged-out reels_media
    endpoint. ``highlight_id`` is the numeric id (no ``highlight:`` prefix).
    Datacenter IPs get the full tray here; residential often returns an empty
    tray, so try datacenter first. Returns the raw reel node or None.
    """
    reel_id = f"highlight:{highlight_id}"
    for tier in ("datacenter", "residential"):
        try:
            node = await _fetch_reels_media_once(tier, reel_id)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            log.info("ig_highlight_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        if node is not None:
            return node
    return None


async def _fetch_reels_media_once(tier: str, reel_id: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient(
        timeout=12, proxy=proxy_for(tier), follow_redirects=True
    ) as client:
        await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
        csrf = client.cookies.get("csrftoken")
        if not csrf:
            return None
        resp = await client.get(
            "https://www.instagram.com/api/v1/feed/reels_media/",
            params={"reel_ids": reel_id},
            headers={
                "User-Agent": _UA,
                "X-IG-App-ID": "936619743392459",
                "X-CSRFToken": csrf,
                "Referer": "https://www.instagram.com/",
            },
        )
        if resp.status_code != 200:
            log.info("ig_highlight_http_error", tier=tier, status=resp.status_code)
            return None
        payload = resp.json()
    reels = payload.get("reels")
    if not isinstance(reels, dict):
        return None
    node = reels.get(reel_id)
    return node if isinstance(node, dict) else None


def _map_story_item(item: dict[str, Any]) -> dict[str, Any]:
    media_type = safe_int(item.get("media_type"))
    is_video = media_type == 2
    videos = item.get("video_versions") or []
    images = (item.get("image_versions2") or {}).get("candidates") or []
    thumb = safe_str(images[0].get("url")) if images else None
    taken_at = safe_int(item.get("taken_at"))
    published = (
        datetime.fromtimestamp(taken_at, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if taken_at
        else None
    )
    mapped = {
        "type": _MEDIA_TYPE_NAMES.get(media_type or 0),
        "url": (safe_str(videos[0].get("url")) if videos else None) if is_video else thumb,
        "thumbnailUrl": thumb,
        "takenAt": published,
        "width": safe_int(item.get("original_width")),
        "height": safe_int(item.get("original_height")),
        "durationSeconds": _video_duration(item, item) if is_video else None,
    }
    return {k: v for k, v in mapped.items() if v is not None}


def map_highlight_reel(node: dict[str, Any]) -> dict[str, Any]:
    """Map a reels_media highlight node to the highlights-details shape."""
    cover = node.get("cover_media") or {}
    cover_url = (cover.get("cropped_image_version") or {}).get("url") or (
        cover.get("full_image_version") or {}
    ).get("url")
    raw_items = node.get("items") or []
    items = [_map_story_item(it) for it in raw_items if isinstance(it, dict)]
    media_count = safe_int(node.get("media_count"))
    return {
        "id": safe_str(node.get("id")),
        "title": safe_str(node.get("title")),
        "coverUrl": safe_str(cover_url),
        "itemCount": media_count if media_count is not None else (len(items) or None),
        "items": items,
    }


def map_feed_post(
    media: dict[str, Any],
    followers: int | None = None,
    profile_user_id: str | None = None,
) -> dict[str, Any]:
    """Map an api/v1 feed item to the channel-posts/reels list shape.

    ``followers`` is the requested profile's count; it only belongs on items
    that profile actually owns (collab posts in the feed are authored by a
    different account), hence the ``profile_user_id`` ownership check.
    """
    from app.services.instagram_decodo import strip_null_post_fields

    caption_obj = media.get("caption")
    caption = (safe_str(caption_obj.get("text")) if isinstance(caption_obj, dict) else "") or ""
    user = media.get("user") or {}
    username = safe_str(user.get("username"))
    shortcode = safe_str(media.get("code"))
    media_type = safe_int(media.get("media_type"))
    is_video = media_type == 2

    cover = (media.get("carousel_media") or [media])[0]
    videos = cover.get("video_versions") or []
    images = (cover.get("image_versions2") or {}).get("candidates") or []

    taken_at = safe_int(media.get("taken_at"))
    published = (
        datetime.fromtimestamp(taken_at, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if taken_at
        else None
    )

    author: dict[str, Any] = {
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "url": f"https://instagram.com/{username}" if username else None,
        "verified": user.get("is_verified"),
        "profileImage": safe_str(user.get("profile_pic_url")) or None,
    }
    owner_id = safe_str(user.get("pk") or user.get("pk_id") or user.get("id"))
    if followers is not None and (
        profile_user_id is None or owner_id is None or owner_id == profile_user_id
    ):
        author["followers"] = followers

    return strip_null_post_fields(
        {
            "platform": "instagram",
            "url": f"https://www.instagram.com/{'reel' if is_video else 'p'}/{shortcode}/" if shortcode else None,
            "id": safe_str(media.get("pk") or media.get("id")),
            "postType": _MEDIA_TYPE_NAMES.get(media_type or 0),
            "productType": safe_str(media.get("product_type")),
            "caption": caption,
            "description": caption,
            "publishedAt": published,
            "durationSeconds": _video_duration(media, cover),
            "thumbnailUrl": safe_str(images[0].get("url")) if images else None,
            "videoUrl": safe_str(videos[0].get("url")) if videos else None,
            "author": author,
            "engagement": {
                "views": safe_int(media.get("play_count") or media.get("view_count")),
                "likes": hidden_count(media.get("like_count")),
                "comments": hidden_count(media.get("comment_count")),
            },
            "hashtags": _HASHTAG_RE.findall(caption),
            "mentions": _MENTION_RE.findall(caption),
        }
    )


async def fetch_user_feed_page(
    user_id: str, max_id: str | None = None, count: int = 12
) -> tuple[list[dict[str, Any]], str | None, bool] | None:
    """One page of a profile's timeline via the logged-out api/v1 feed
    endpoint. Datacenter IPs get a flat 401 here, so this goes straight to
    the residential tier. Whether a residential IP gets 200 or 401 is
    per-session luck, so retry on a fresh session before giving up.
    Returns (raw items, next_max_id, more_available) or None on failure.
    """
    params: dict[str, Any] = {"count": max(1, min(count, 33))}
    if max_id:
        params["max_id"] = max_id
    degraded: tuple[list[dict[str, Any]], str | None, bool] | None = None
    for attempt in range(3):
        result = await _fetch_feed_once(user_id, params, attempt)
        if result is None:
            continue
        # Some sessions get a stripped feed variant whose clips carry no
        # video_duration/dash manifest. One fresh session usually fixes it,
        # but don't burn more than one extra request on cosmetics.
        if not _feed_page_degraded(result[0]):
            return result
        if degraded is not None:
            return result
        degraded = result
    return degraded


def _feed_page_degraded(items: list[dict[str, Any]]) -> bool:
    return any(
        safe_int(item.get("media_type")) == 2
        and not item.get("video_duration")
        and not item.get("video_dash_manifest")
        for item in items
    )


async def _fetch_feed_once(
    user_id: str, params: dict[str, Any], attempt: int
) -> tuple[list[dict[str, Any]], str | None, bool] | None:
    try:
        async with httpx.AsyncClient(
            timeout=12, proxy=proxy_for("residential"), follow_redirects=True
        ) as client:
            await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
            resp = await client.get(
                f"https://www.instagram.com/api/v1/feed/user/{user_id}/",
                params=params,
                headers={
                    "User-Agent": _UA,
                    "X-IG-App-ID": "936619743392459",
                    "X-CSRFToken": client.cookies.get("csrftoken") or "",
                    "Referer": "https://www.instagram.com/",
                },
            )
    except httpx.HTTPError as exc:
        log.info("ig_feed_transport_error", attempt=attempt, error=str(exc)[:120])
        return None
    if resp.status_code != 200:
        log.info("ig_feed_http_error", attempt=attempt, status=resp.status_code)
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    items = payload.get("items")
    if not isinstance(items, list):
        return None
    return items, safe_str(payload.get("next_max_id")) or None, bool(payload.get("more_available"))


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


# Instagram serves the classic server-rendered embed page (<html id="facebook">)
# only to non-browser clients; a modern Chrome UA gets the heavy React app shell.
_EMBED_UA = "curl/8.4.0"


async def fetch_embed_html(embed_url: str) -> str | None:
    """Fetch Instagram's self-contained embed page HTML for a post/reel/profile.

    ``embed_url`` is a fully-qualified .../embed/ (or /embed/captioned/) URL.
    Returns the rendered document (the ``<html id="facebook">`` embed page) or
    None if every proxy tier fails or Instagram returns the app shell instead.
    """
    for tier in _TIERS:
        try:
            html = await _fetch_embed_once(tier, embed_url)
        except (httpx.HTTPError, ValueError) as exc:
            log.info("ig_embed_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        if html is not None:
            return html
    return None


async def _fetch_embed_once(tier: str, embed_url: str) -> str | None:
    async with httpx.AsyncClient(
        timeout=12, proxy=proxy_for(tier), follow_redirects=True
    ) as client:
        resp = await client.get(embed_url, headers={"User-Agent": _EMBED_UA})
        if resp.status_code != 200:
            log.info("ig_embed_http_error", tier=tier, status=resp.status_code)
            return None
        html = resp.text
    # Reject the heavy React app shell; we only want the lightweight embed doc.
    if "EmbedFrame" not in html and 'id="facebook"' not in html:
        return None
    return html


# --- Profile lookup (logged-out) --------------------------------------------
_IG_APP_ID = "936619743392459"


async def _ig_web_get(tier: str, url: str, referer: str) -> dict[str, Any] | None:
    """GET an Instagram web api/v1 JSON endpoint logged-out (csrf + app id)."""
    async with httpx.AsyncClient(
        timeout=12, proxy=proxy_for(tier), follow_redirects=True
    ) as client:
        await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
        csrf = client.cookies.get("csrftoken")
        if not csrf:
            return None
        resp = await client.get(
            url,
            headers={
                "User-Agent": _UA,
                "X-IG-App-ID": _IG_APP_ID,
                "X-CSRFToken": csrf,
                "Referer": referer,
            },
        )
        if resp.status_code != 200:
            log.info("ig_web_http_error", tier=tier, status=resp.status_code)
            return None
        try:
            return resp.json()
        except ValueError:
            return None


async def resolve_username(user_id: str) -> str | None:
    """Map a numeric Instagram user id to its @username via users/{id}/info/.
    The logged-out response is minimal but always carries ``username``."""
    url = f"https://www.instagram.com/api/v1/users/{user_id}/info/"
    for tier in _TIERS:
        try:
            payload = await _ig_web_get(tier, url, "https://www.instagram.com/")
        except (httpx.HTTPError, ValueError) as exc:
            log.info("ig_userinfo_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        user = (payload or {}).get("user") if isinstance(payload, dict) else None
        username = safe_str((user or {}).get("username"))
        if username:
            return username
    return None


async def fetch_web_profile_info(username: str) -> dict[str, Any] | None:
    """Rich logged-out profile via users/web_profile_info/?username=. Returns
    the raw ``user`` node (69+ fields incl. counts, bio, verification)."""
    handle = username.lstrip("@")
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={urllib.parse.quote(handle)}"
    referer = f"https://www.instagram.com/{handle}/"
    for tier in _TIERS:
        try:
            payload = await _ig_web_get(tier, url, referer)
        except (httpx.HTTPError, ValueError) as exc:
            log.info("ig_wpi_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        if not isinstance(payload, dict):
            continue
        user = (payload.get("data") or {}).get("user") or payload.get("user")
        if isinstance(user, dict) and (user.get("username") or user.get("id")):
            return user
    return None


def _edge_count(value: Any) -> int | None:
    if isinstance(value, dict):
        return safe_int(value.get("count"))
    return safe_int(value)


def map_basic_profile(user: dict[str, Any]) -> dict[str, Any]:
    """Map a web_profile_info user node to a clean, competitor-compatible
    profile shape. Null/absent fields are dropped so the JSON stays tidy."""
    hd = safe_str(user.get("profile_pic_url_hd"))
    bio_entities = user.get("biography_with_entities")
    out: dict[str, Any] = {
        "id": safe_str(user.get("id") or user.get("pk")),
        "pk": safe_str(user.get("pk") or user.get("id")),
        "username": safe_str(user.get("username")),
        "full_name": safe_str(user.get("full_name")),
        "biography": safe_str(user.get("biography")),
        "biography_with_entities": bio_entities if isinstance(bio_entities, dict) else None,
        "external_url": safe_str(user.get("external_url")),
        "follower_count": _edge_count(user.get("edge_followed_by") or user.get("follower_count")),
        "following_count": _edge_count(user.get("edge_follow") or user.get("following_count")),
        "media_count": _edge_count(user.get("edge_owner_to_timeline_media") or user.get("media_count")),
        "highlight_reel_count": safe_int(user.get("highlight_reel_count")),
        "is_private": user.get("is_private"),
        "is_verified": user.get("is_verified"),
        "is_business": user.get("is_business_account"),
        "is_professional_account": user.get("is_professional_account"),
        "category": safe_str(user.get("category_name") or user.get("category")),
        "should_show_category": user.get("should_show_category"),
        "profile_pic_url": safe_str(user.get("profile_pic_url")),
        "hd_profile_pic_url_info": {"url": hd} if hd else None,
        "fbid_v2": safe_str(user.get("fbid") or user.get("fbid_v2")),
        "pronouns": user.get("pronouns"),
        "bio_links": user.get("bio_links"),
        "is_embeds_disabled": user.get("is_embeds_disabled"),
        "is_regulated_c18": user.get("is_regulated_c18"),
        "show_account_transparency_details": user.get("show_account_transparency_details"),
        "transparency_label": user.get("transparency_label"),
        "transparency_product": user.get("transparency_product"),
        "show_text_post_app_badge": user.get("show_text_post_app_badge"),
        "remove_message_entrypoint": user.get("remove_message_entrypoint"),
        "ai_agent_type": user.get("ai_agent_type"),
    }
    return {k: v for k, v in out.items() if v is not None}
