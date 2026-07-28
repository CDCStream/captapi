"""Native Rumble video details via Decodo-rendered HTML + JSON-LD.

Datacenter / residential proxies usually hit Cloudflare 403. Decodo
``headless=html`` returns a page with ``VideoObject`` JSON-LD (title,
description, views, duration, upload date, thumbnail, embed).
"""

from __future__ import annotations

import json
import re
from html import unescape
from typing import Any

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str
from app.utils.url import extract_rumble_video_id

log = structlog.get_logger(__name__)

_LD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)
_OG_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']([^"\']+)["\'][^>]+content=["\']([^"\']*)["\']',
    re.I,
)
_DURATION_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", re.I)


def _parse_iso_duration(value: str | None) -> str | None:
    """``PT01H26M25S`` -> ``1:26:25`` (or ``26:25`` / ``0:25``)."""
    if not value:
        return None
    m = _DURATION_RE.fullmatch(value.strip())
    if not m:
        return safe_str(value)
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    seconds = int(m.group(3) or 0)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _og_map(html: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _OG_RE.finditer(html or ""):
        key = (m.group(1) or "").strip().lower()
        val = unescape(m.group(2) or "").strip()
        if key and val and key not in out:
            out[key] = val
    return out


def _video_object(html: str) -> dict[str, Any] | None:
    for m in _LD_RE.finditer(html or ""):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "VideoObject":
                return item
    return None



_CHANNEL_RE = re.compile(
    r'data-title="([^"]+)"\s+data-slug="([^"]+)"\s+data-id="\d+"\s+data-type="channel"',
    re.I,
)
_MP4_RE = re.compile(r'https://[^"\'<>\s]+\.mp4[^"\'<>\s]*', re.I)


def _channel_from_html(html: str) -> tuple[str | None, str | None]:
    m = _CHANNEL_RE.search(html or "")
    if not m:
        return None, None
    return safe_str(unescape(m.group(1))), safe_str(m.group(2))


def _streams_from_html(html: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for url in _MP4_RE.findall(html or ""):
        clean = unescape(url).split("&amp;")[0]
        if clean in seen:
            continue
        seen.add(clean)
        out.append({"url": clean, "type": "mp4", "quality": None})
        if len(out) >= 8:
            break
    return out


def parse_video_html(html: str, url: str | None = None) -> dict[str, Any] | None:
    """Build the video-details card from JSON-LD (+ OG fallbacks)."""
    if not html:
        return None
    video = _video_object(html)
    og = _og_map(html)
    title = safe_str((video or {}).get("name") or og.get("og:title"))
    description = safe_str(
        (video or {}).get("description") or og.get("og:description") or og.get("description")
    )
    thumbnail = safe_str((video or {}).get("thumbnailUrl") or og.get("og:image"))
    canonical = safe_str((video or {}).get("url") or og.get("og:url") or url)
    embed = safe_str((video or {}).get("embedUrl"))
    if not (title or description or thumbnail):
        return None

    views = None
    if video:
        stats = video.get("interactionStatistic")
        if isinstance(stats, dict):
            views = safe_int(stats.get("userInteractionCount"))
        elif isinstance(stats, list):
            for s in stats:
                if isinstance(s, dict) and s.get("userInteractionCount") is not None:
                    views = safe_int(s.get("userInteractionCount"))
                    break

    video_id = extract_rumble_video_id(canonical or "") or extract_rumble_video_id(url or "")
    channel_name, channel_slug = _channel_from_html(html)
    channel_url = f"https://rumble.com/c/{channel_slug}" if channel_slug else None
    streams = _streams_from_html(html)

    return {
        "platform": "rumble",
        "id": safe_str(video_id),
        "url": canonical,
        "embedUrl": embed,
        "title": title,
        "description": description,
        "channel": channel_name,
        "channelUrl": channel_url,
        "channelFollowers": None,
        "channelVerified": None,
        "views": views or 0,
        "likes": 0,
        "dislikes": 0,
        "duration": _parse_iso_duration(safe_str((video or {}).get("duration"))),
        "publishedAt": safe_str((video or {}).get("uploadDate")),
        "thumbnail": thumbnail,
        "comments": 0,
        "isLive": False,
        "streams": streams,
    }


async def video_details_native(url: str) -> dict[str, Any] | None:
    """Fetch a Rumble video page via Decodo and parse JSON-LD metadata."""
    if not url or not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=90.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body:
        log.info("rumble_video_native_http", status=status, url=url[:120])
        return None
    parsed = parse_video_html(body, url=url)
    if not parsed:
        log.warning("rumble_video_native_parse_miss", url=url[:120], length=len(body))
        return None
    log.info(
        "rumble_video_native_ok",
        id=parsed.get("id"),
        views=parsed.get("views"),
        title=(parsed.get("title") or "")[:80],
    )
    return parsed
