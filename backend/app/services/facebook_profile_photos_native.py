"""Native Facebook profile/page photos via Decodo.

Scroll ``/photos`` and collect ``Photo`` Relay nodes (viewer_image +
accessibility_caption). Facebook's photos surface does not expose a true post
caption, publish time, or engagement — only alt-text when present.
No Apify.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

CREDIT_FB_PROFILE_PHOTOS_NATIVE = 2

_SCROLL_ACTIONS: list[dict[str, Any]] = [
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 3000},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 3000},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 4000},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 4000},
    {"type": "wait", "wait_time_s": 2},
]

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)


def _page_slug(url: str) -> str | None:
    path = urlparse(url).path or ""
    parts = [p for p in path.split("/") if p]
    skip = {
        "pages", "people", "profile.php", "pg", "public", "posts",
        "photos", "reels", "videos", "watch", "events", "photos_by",
    }
    for part in parts:
        if part.lower() in skip or part.isdigit() or part.startswith("pfbid"):
            continue
        return part
    return None


def _photos_url(page_url: str) -> str:
    slug = _page_slug(page_url)
    if slug:
        return f"https://www.facebook.com/{slug}/photos"
    return page_url.rstrip("/") + "/photos"


def _walk(obj: Any, out: list[dict[str, Any]], depth: int = 0) -> None:
    if depth > 40 or len(out) >= 80:
        return
    if isinstance(obj, dict):
        if obj.get("__typename") == "Photo" and obj.get("id"):
            out.append(obj)
        for value in obj.values():
            _walk(value, out, depth + 1)
    elif isinstance(obj, list):
        for value in obj:
            _walk(value, out, depth + 1)


def _image_uri(block: Any) -> str | None:
    if isinstance(block, dict):
        return safe_str(block.get("uri") or block.get("url"))
    return None


def _from_photo_node(node: dict[str, Any]) -> dict[str, Any] | None:
    pid = safe_str(node.get("id"))
    if not pid:
        return None
    viewer = node.get("viewer_image") if isinstance(node.get("viewer_image"), dict) else {}
    image = node.get("image") if isinstance(node.get("image"), dict) else {}
    photo_image = node.get("photo_image") if isinstance(node.get("photo_image"), dict) else {}
    uri = (
        _image_uri(viewer)
        or _image_uri(image)
        or _image_uri(photo_image)
    )
    width = safe_int(viewer.get("width") or image.get("width") or photo_image.get("width"))
    height = safe_int(viewer.get("height") or image.get("height") or photo_image.get("height"))
    # This is Facebook's accessibility / alt-text — NOT a user-written caption.
    accessibility = safe_str(
        node.get("accessibility_caption")
        or node.get("accessibilityCaption")
        or node.get("alt_text")
        or node.get("altText")
    )
    thumb = (
        _image_uri(node.get("thumbnailImage") or node.get("thumbnail_image"))
        or _image_uri(node.get("preferred_thumbnail") or node.get("preferredThumbnail"))
        or _image_uri(node.get("small_image") or node.get("smallImage"))
    )
    if not uri and not accessibility:
        return None
    url = f"https://www.facebook.com/photo.php?fbid={pid}"
    out: dict[str, Any] = {
        "id": pid,
        "photoId": pid,
        "url": url,
        "photoUrl": url,
        "imageUrl": uri,
        "image": uri,
        "accessibilityCaption": accessibility,
        "width": width,
        "height": height,
    }
    if thumb and thumb != uri:
        out["thumbnailUrl"] = thumb
        out["thumbnail"] = thumb
    return out


async def profile_photos_native(url: str, limit: int) -> list[dict[str, Any]] | None:
    """Return raw photo dicts for ``_normalize_photo``, or None."""
    if limit <= 0:
        return []
    if not url or not decodo_fetch.enabled():
        return None

    got = await decodo_fetch.fetch_url(
        _photos_url(url),
        timeout=180.0,
        headless="html",
        browser_actions=_SCROLL_ACTIONS,
    )
    if not got:
        return None
    status, html = got
    if status != 200 or not html:
        return None

    nodes: list[dict[str, Any]] = []
    for match in _SCRIPT_RE.finditer(html):
        raw = match.group(1)
        if '"__typename":"Photo"' not in raw:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        _walk(data, nodes)

    raws: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in nodes:
        item = _from_photo_node(node)
        if not item:
            continue
        pid = item["id"]
        if pid in seen:
            continue
        seen.add(pid)
        raws.append(item)
        if len(raws) >= limit:
            break

    if not raws:
        log.info("facebook_profile_photos_native_empty", url=url[:120])
        return None

    log.info("facebook_profile_photos_native_ok", url=url[:120], returned=len(raws))
    return raws[:limit]
