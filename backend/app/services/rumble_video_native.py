"""Native Rumble video details via Decodo-rendered HTML + JSON-LD.

Datacenter / residential proxies usually hit Cloudflare 403. Decodo
``headless=html`` returns a page with ``VideoObject`` JSON-LD (title,
description, views, duration, upload date, thumbnail, embed).

Keyword search pages expose ``video-listing-entry`` cards with title,
channel, duration, thumbnail, and publish time.
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
_CLOCK_DURATION_RE = re.compile(r"^(?:(\d+):)?(\d{1,2}):(\d{2})$")
_EMBED_ID_RE = re.compile(
    r'Rumble\s*\(\s*["\']play["\']\s*,\s*\{[^}]*?"video"\s*:\s*"([a-zA-Z0-9]+)"',
    re.I | re.S,
)
_EMBED_URL_ID_RE = re.compile(r"rumble\.com/embed/([a-zA-Z0-9]+)", re.I)
_NUMERIC_ID_RE = re.compile(r'data-video-id=["\'](\d+)["\']', re.I)
_VOTES_TITLE_RE = re.compile(
    r'title="([\d.,]+[KMBkmb]?)\s*Likes?\s*\|\s*([\d.,]+[KMBkmb]?)\s*Dislikes?"',
    re.I,
)
_VOTES_UP_RE = re.compile(
    r'data-js=["\']rumbles_up_votes["\']\s*>\s*([\d.,]+[KMBkmb]?)\s*<',
    re.I,
)
_VOTES_DOWN_RE = re.compile(
    r'data-js=["\']rumbles_down_votes["\']\s*>\s*([\d.,]+[KMBkmb]?)\s*<',
    re.I,
)
_COMMENT_COUNT_RE = re.compile(
    r'class=["\']comment-count["\'][^>]*>\s*([\d.,]+[KMBkmb]?)\s*Comments?',
    re.I,
)
_TRACK_CAPTION_RE = re.compile(
    r'<track[^>]+kind=["\']captions["\'][^>]*>',
    re.I,
)
_ATTR_RE = re.compile(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*"([^"]*)"', re.I)
_LIVE_BADGE_RE = re.compile(
    r'class=["\'][^"\']*(?:live-video|video-item--live|livestream)[^"\']*["\']',
    re.I,
)


def _iso_duration_parts(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None
    m = _DURATION_RE.fullmatch(value.strip())
    if not m:
        return None
    return int(m.group(1) or 0), int(m.group(2) or 0), int(m.group(3) or 0)


def _parse_iso_duration(value: str | None) -> str | None:
    """``PT01H26M25S`` -> ``1:26:25`` (or ``26:25`` / ``0:25``)."""
    parts = _iso_duration_parts(value)
    if not parts:
        return safe_str(value)
    hours, minutes, seconds = parts
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _iso_duration_seconds(value: str | None) -> int | None:
    parts = _iso_duration_parts(value)
    if not parts:
        return None
    hours, minutes, seconds = parts
    return hours * 3600 + minutes * 60 + seconds


def _clock_to_seconds(value: str | None) -> int | None:
    """``1:26:25`` / ``26:25`` -> seconds."""
    text = safe_str(value)
    if not text:
        return None
    m = _CLOCK_DURATION_RE.fullmatch(text)
    if not m:
        return None
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    seconds = int(m.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def _seconds_to_clock(seconds: int | None) -> str | None:
    if seconds is None or seconds < 0:
        return None
    hours, rem = divmod(int(seconds), 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def _parse_count(raw: str | None) -> int | None:
    """Parse ``1.2K`` / ``3M`` / ``12,345`` view strings."""
    if not raw:
        return None
    text = raw.strip().replace(",", "").upper()
    mult = 1
    if text.endswith("K"):
        mult = 1_000
        text = text[:-1]
    elif text.endswith("M"):
        mult = 1_000_000
        text = text[:-1]
    elif text.endswith("B"):
        mult = 1_000_000_000
        text = text[:-1]
    try:
        return int(float(text) * mult)
    except ValueError:
        return safe_int(re.sub(r"[^\d]", "", raw))


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
# Shorts UI: creator link + lit-rendered name.
_SHORTS_CREATOR_RE = re.compile(
    r'data-testid="creator"\s+href="https?://(?:www\.)?rumble\.com/c/([^"/?]+)[^"]*"[^>]*>'
    r'.*?<rum-text[^>]*>\s*(?:<!--.*?-->)?\s*([^<]+)',
    re.I | re.S,
)
_FOLLOWERS_RE = re.compile(
    r'media-heading-num-followers[^>]*>\s*([\d.,]+[KMBkmb]?)\s*followers?',
    re.I,
)
_SHORTS_FOLLOWERS_RE = re.compile(
    r'data-testid="followers-count"[^>]*>.*?([\d.,]+[KMBkmb]?)\s*followers?',
    re.I | re.S,
)
_VERIFIED_RE_PAGE = re.compile(r'class="[^"]*media-heading-verified', re.I)
_SHORTS_VERIFIED_RE = re.compile(
    r'data-testid="creator"[^>]*>.{0,1200}?name="user__verified"',
    re.I | re.S,
)
_MP4_RE = re.compile(r'https://[^"\'<>\s]+\.mp4[^"\'<>\s]*', re.I)
# CDN filenames: Foo.haa.mp4 / Foo.caa.rec.mp4 — letter codes map to resolution.
_STREAM_CODE_RE = re.compile(r"\.([A-Za-z])aa(?:\.rec)?\.mp4", re.I)
_QUALITY_BY_CODE = {
    "a": "1080p",
    "h": "1080p",
    "g": "720p",
    "c": "480p",
    "b": "360p",
    "o": "240p",
    "f": "180p",
}


def _channel_from_html(html: str) -> tuple[str | None, str | None]:
    m = _CHANNEL_RE.search(html or "")
    if m:
        return safe_str(unescape(m.group(1))), safe_str(m.group(2))
    sm = _SHORTS_CREATOR_RE.search(html or "")
    if not sm:
        return None, None
    return safe_str(unescape(sm.group(2))), safe_str(sm.group(1))


def _followers_from_html(html: str) -> int | None:
    m = _FOLLOWERS_RE.search(html or "") or _SHORTS_FOLLOWERS_RE.search(html or "")
    if not m:
        return None
    return _parse_count(m.group(1))


def _verified_from_html(html: str) -> bool | None:
    """True/False when a channel block is present; None if channel missing."""
    if not html:
        return None
    has_channel = bool(_CHANNEL_RE.search(html) or _SHORTS_CREATOR_RE.search(html))
    if not has_channel:
        return None
    return bool(_VERIFIED_RE_PAGE.search(html) or _SHORTS_VERIFIED_RE.search(html))


def _quality_from_stream_url(url: str) -> str | None:
    m = _STREAM_CODE_RE.search(url or "")
    if not m:
        return None
    return _QUALITY_BY_CODE.get(m.group(1).lower())


def _streams_from_html(html: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for url in _MP4_RE.findall(html or ""):
        clean = unescape(url).split("&amp;")[0].split("?")[0]
        if clean in seen:
            continue
        seen.add(clean)
        out.append(
            {
                "url": clean,
                "type": "mp4",
                "quality": _quality_from_stream_url(clean),
            }
        )
        if len(out) >= 8:
            break
    return out


def _votes_from_html(html: str) -> tuple[int | None, int | None]:
    """Likes/dislikes when the vote UI is present; otherwise ``(None, None)``."""
    title_m = _VOTES_TITLE_RE.search(html or "")
    if title_m:
        return _parse_count(title_m.group(1)), _parse_count(title_m.group(2))
    up_m = _VOTES_UP_RE.search(html or "")
    down_m = _VOTES_DOWN_RE.search(html or "")
    if not up_m and not down_m:
        return None, None
    return (
        _parse_count(up_m.group(1)) if up_m else None,
        _parse_count(down_m.group(1)) if down_m else None,
    )


def _comments_from_html(html: str) -> int | None:
    m = _COMMENT_COUNT_RE.search(html or "")
    return _parse_count(m.group(1)) if m else None


def _embed_id_from_html(html: str, embed_url: str | None = None) -> str | None:
    m = _EMBED_ID_RE.search(html or "")
    if m:
        return safe_str(m.group(1))
    if embed_url:
        em = _EMBED_URL_ID_RE.search(embed_url)
        if em:
            return safe_str(em.group(1))
    em = _EMBED_URL_ID_RE.search(html or "")
    return safe_str(em.group(1)) if em else None


def _numeric_id_from_html(html: str) -> int | None:
    m = _NUMERIC_ID_RE.search(html or "")
    return safe_int(m.group(1)) if m else None


def _captions_from_html(html: str) -> dict[str, dict[str, str]] | None:
    out: dict[str, dict[str, str]] = {}
    for tag_m in _TRACK_CAPTION_RE.finditer(html or ""):
        attrs = {a.group(1).lower(): unescape(a.group(2)) for a in _ATTR_RE.finditer(tag_m.group(0))}
        src = safe_str(attrs.get("src"))
        if not src:
            continue
        lang = safe_str(attrs.get("srclang")) or "und"
        out[lang] = {
            "language": safe_str(attrs.get("label")) or lang,
            "path": src,
        }
    return out or None


def _is_live_from_html(html: str) -> bool | None:
    if not html:
        return None
    if _LIVE_BADGE_RE.search(html):
        return True
    # Presence of a VOD player config implies not live.
    if _EMBED_ID_RE.search(html) or 'Rumble("play"' in html or "Rumble('play'" in html:
        return False
    return None


def _media_asset(node: Any) -> dict[str, Any] | None:
    if not isinstance(node, dict):
        return None
    url = safe_str(node.get("url"))
    if not url:
        return None
    meta_raw = node.get("meta") if isinstance(node.get("meta"), dict) else {}
    meta = {
        "bitrate": safe_int(meta_raw.get("bitrate")),
        "size": safe_int(meta_raw.get("size")),
        "w": safe_int(meta_raw.get("w")),
        "h": safe_int(meta_raw.get("h")),
    }
    # Drop empty meta keys but keep 0 (audio w/h).
    meta = {k: v for k, v in meta.items() if v is not None}
    out: dict[str, Any] = {"url": url}
    if meta:
        out["meta"] = meta
    return out


def _media_from_embed(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize embedJS ``ua`` (quality-keyed) into SC-shaped ``media``.

    Rumble uses ``tar`` (HLS chunklists) for some VODs and ``mp4`` (progressive
    files) for others — keep whichever buckets are present.
    """
    ua = payload.get("ua") if isinstance(payload.get("ua"), dict) else None
    source = ua or (payload.get("u") if isinstance(payload.get("u"), dict) else None)
    if not source:
        return None
    out: dict[str, Any] = {}
    for bucket in ("tar", "mp4", "timeline", "audio", "hls"):
        raw = source.get(bucket)
        if isinstance(raw, dict) and any(isinstance(v, dict) and "url" in v for v in raw.values()):
            # Quality-keyed: {"480": {"url": ...}, ...}
            cleaned: dict[str, Any] = {}
            for key, node in raw.items():
                asset = _media_asset(node)
                if asset:
                    cleaned[str(key)] = asset
            if cleaned:
                out[bucket] = cleaned
        else:
            asset = _media_asset(raw)
            if asset:
                # Flat single asset — keep under a stable key.
                default_key = "auto" if bucket == "hls" else "default"
                out[bucket] = {default_key: asset}
    return out or None


def _streams_from_media(media: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Build a flat playable ``streams`` list from ``media`` (+ keep mp4 first)."""
    if not media:
        return []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add(url: str | None, typ: str, quality: str | None) -> None:
        clean = safe_str(url)
        if not clean or clean in seen:
            return
        seen.add(clean)
        out.append({"url": clean, "type": typ, "quality": quality})

    def _quality_label(q: Any, *, suffix: str = "p") -> str | None:
        if str(q).isdigit():
            return f"{q}{suffix}"
        return safe_str(q)

    # Progressive MP4 qualities first (incl. timeline preview + ua.mp4).
    mp4 = media.get("mp4") if isinstance(media.get("mp4"), dict) else {}
    for q, node in sorted(mp4.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else 0, reverse=True):
        if isinstance(node, dict):
            _add(node.get("url"), "mp4", _quality_label(q))

    timeline = media.get("timeline") if isinstance(media.get("timeline"), dict) else {}
    for q, node in timeline.items():
        if isinstance(node, dict):
            _add(node.get("url"), "mp4", _quality_label(q))

    tar = media.get("tar") if isinstance(media.get("tar"), dict) else {}
    for q, node in tar.items():
        if isinstance(node, dict):
            _add(node.get("url"), "hls", _quality_label(q))

    hls = media.get("hls") if isinstance(media.get("hls"), dict) else {}
    for q, node in hls.items():
        if isinstance(node, dict):
            _add(node.get("url"), "hls", safe_str(q) or "auto")

    audio = media.get("audio") if isinstance(media.get("audio"), dict) else {}
    for q, node in audio.items():
        if isinstance(node, dict):
            _add(node.get("url"), "audio", _quality_label(q, suffix="k"))

    return out[:12]


def _width_height_from_embed(payload: dict[str, Any], media: dict[str, Any] | None) -> tuple[int | None, int | None]:
    best_w: int | None = None
    best_h: int | None = None
    if media:
        for bucket in ("tar", "mp4", "timeline"):
            nodes = media.get(bucket)
            if not isinstance(nodes, dict):
                continue
            for node in nodes.values():
                if not isinstance(node, dict):
                    continue
                meta = node.get("meta") if isinstance(node.get("meta"), dict) else {}
                w = safe_int(meta.get("w"))
                h = safe_int(meta.get("h"))
                if w and h and (best_w is None or w * h > (best_w or 0) * (best_h or 0)):
                    best_w, best_h = w, h
    thumbs = payload.get("t")
    if isinstance(thumbs, list):
        for t in thumbs:
            if not isinstance(t, dict):
                continue
            w = safe_int(t.get("w"))
            h = safe_int(t.get("h"))
            if w and h and (best_w is None or w * h > (best_w or 0) * (best_h or 0)):
                best_w, best_h = w, h
    if best_w and best_h:
        return best_w, best_h
    return safe_int(payload.get("w")), safe_int(payload.get("h"))


def _merge_streams(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for group in groups:
        for item in group:
            url = safe_str(item.get("url"))
            if not url or url in seen:
                continue
            seen.add(url)
            out.append(item)
            if len(out) >= 12:
                return out
    return out


def apply_embedjs(card: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Merge embedJS media/captions/ids into an existing video-details card."""
    if not payload:
        return card
    embed_id = safe_str(payload.get("video") or card.get("embedId"))
    # embedJS uses the bare id in the request URL; response has vid + share_url.
    numeric = safe_int(payload.get("vid"))
    if numeric is not None:
        card["numericId"] = numeric
    if embed_id:
        card["embedId"] = embed_id
        card["embedUrl"] = card.get("embedUrl") or f"https://rumble.com/embed/{embed_id}/"
    share = safe_str(payload.get("share_url"))
    if share:
        card["shareUrl"] = share
    elif card.get("id"):
        card["shareUrl"] = card.get("shareUrl") or f"https://rumble.com/share/{card['id']}"

    dur = safe_int(payload.get("duration"))
    if dur is not None and dur > 0:
        card["durationSeconds"] = dur
        card["duration"] = card.get("duration") or _seconds_to_clock(dur)

    live_raw = payload.get("live")
    if live_raw is not None:
        card["isLive"] = bool(safe_int(live_raw) or 0) if not isinstance(live_raw, bool) else live_raw

    captions = payload.get("cc") if isinstance(payload.get("cc"), dict) else None
    if captions:
        cleaned: dict[str, dict[str, str]] = {}
        for key, node in captions.items():
            if not isinstance(node, dict):
                continue
            path = safe_str(node.get("path") or node.get("url"))
            if not path:
                continue
            cleaned[str(key)] = {
                "language": safe_str(node.get("language")) or str(key),
                "path": path,
            }
        if cleaned:
            card["captions"] = cleaned

    media = _media_from_embed(payload)
    if media:
        card["media"] = media
        # Prefer embedJS qualities (full ladder); keep page mp4s as extras.
        card["streams"] = _merge_streams(
            _streams_from_media(media),
            [s for s in (card.get("streams") or []) if isinstance(s, dict)],
        )

    width, height = _width_height_from_embed(payload, media)
    if width:
        card["width"] = width
    if height:
        card["height"] = height

    author = payload.get("author") if isinstance(payload.get("author"), dict) else {}
    if not card.get("channel"):
        card["channel"] = safe_str(author.get("name"))
    author_url = safe_str(author.get("url"))
    if author_url and not card.get("channelUrl"):
        card["channelUrl"] = author_url
        slug = author_url.rstrip("/").split("/")[-1]
        if slug and not card.get("channelHandle"):
            card["channelHandle"] = slug
    return card


def parse_embedjs_body(body: str) -> dict[str, Any] | None:
    text = (body or "").strip()
    if not text:
        return None
    if text.startswith("{"):
        try:
            data = json.loads(text)
            return data if isinstance(data, dict) else None
        except ValueError:
            return None
    # Decodo sometimes wraps JSON in a minimal HTML shell.
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


async def fetch_embedjs(embed_id: str) -> dict[str, Any] | None:
    """Fetch Rumble embedJS media payload (no headless — JSON endpoint)."""
    eid = safe_str(embed_id)
    if not eid or not decodo_fetch.enabled():
        return None
    url = f"https://rumble.com/embedJS/u3/?request=video&ver=2&v={eid}"
    got = await decodo_fetch.fetch_url(url, timeout=60.0)
    if not got:
        return None
    status, body = got
    if status != 200 or not body:
        log.info("rumble_embedjs_http", status=status, embed_id=eid)
        return None
    parsed = parse_embedjs_body(body)
    if not parsed:
        log.warning("rumble_embedjs_parse_miss", embed_id=eid, length=len(body))
        return None
    return parsed


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
    likes, dislikes = _votes_from_html(html)
    iso_dur = safe_str((video or {}).get("duration"))
    duration_str = _parse_iso_duration(iso_dur)
    duration_seconds = _iso_duration_seconds(iso_dur) or _clock_to_seconds(duration_str)
    embed_id = _embed_id_from_html(html, embed)
    if embed_id and not embed:
        embed = f"https://rumble.com/embed/{embed_id}/"
    numeric_id = _numeric_id_from_html(html)
    captions = _captions_from_html(html)
    is_live = _is_live_from_html(html)

    return {
        "platform": "rumble",
        "id": safe_str(video_id),
        "numericId": numeric_id,
        "embedId": embed_id,
        "url": canonical,
        "embedUrl": embed,
        "shareUrl": f"https://rumble.com/share/{video_id}" if video_id else None,
        "title": title,
        "description": description,
        "channel": channel_name,
        "channelUrl": channel_url,
        "channelHandle": channel_slug,
        "channelFollowers": _followers_from_html(html),
        "channelVerified": _verified_from_html(html),
        # Missing engagement must stay null — never invent 0.
        "views": views,
        "likes": likes,
        "dislikes": dislikes,
        "comments": _comments_from_html(html),
        "duration": duration_str,
        "durationSeconds": duration_seconds,
        "publishedAt": safe_str((video or {}).get("uploadDate")),
        "thumbnail": thumbnail,
        "width": None,
        "height": None,
        "captions": captions,
        "media": None,
        "isLive": is_live,
        "streams": streams,
    }


async def video_details_native(url: str) -> dict[str, Any] | None:
    """Fetch a Rumble video page via Decodo and parse JSON-LD + embedJS media."""
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

    embed_id = safe_str(parsed.get("embedId"))
    if embed_id:
        embed_payload = await fetch_embedjs(embed_id)
        if embed_payload:
            # Request id is the embed id; stamp it before merge.
            embed_payload.setdefault("video", embed_id)
            parsed = apply_embedjs(parsed, embed_payload)

    log.info(
        "rumble_video_native_ok",
        id=parsed.get("id"),
        views=parsed.get("views"),
        likes=parsed.get("likes"),
        comments=parsed.get("comments"),
        duration_seconds=parsed.get("durationSeconds"),
        has_media=bool(parsed.get("media")),
        title=(parsed.get("title") or "")[:80],
    )
    return parsed


_ENTRY_RE = re.compile(r'<li class="video-listing-entry">', re.I)
_HREF_RE = re.compile(r'href="(/v[^"?]+\.html)', re.I)
_TITLE_RE = re.compile(r'<h3 class="video-item--title">([^<]+)</h3>', re.I)
_BY_RE = re.compile(
    r'href="(/c/[^"?]+)[^"]*"[^>]*>\s*<div class="ellipsis-1">([^<]+)',
    re.I,
)
_DURATION_ATTR_RE = re.compile(r'video-item--duration"[^>]*data-value="([^"]+)"', re.I)
_TIME_RE = re.compile(
    r'<time class="video-item--meta video-item--time"[^>]*datetime="([^"]+)"',
    re.I,
)
_THUMB_RE = re.compile(r'<img class="video-item--img"[^>]+src="([^"]+)"', re.I)
_VERIFIED_RE = re.compile(r"video-item--by-verified", re.I)
# Counters sit after an inline SVG inside the item div.
_VIEWS_RE = re.compile(
    r'video-item--views[^>]*>.*?</svg>\s*([\d.,]+[KMBkmb]?)|'
    r'video-item--views[^>]*>\s*([\d.,]+[KMBkmb]?)\s*<|'
    r'data-views=["\']([\d.,]+[KMBkmb]?)["\']',
    re.I | re.S,
)
_COMMENTS_RE = re.compile(
    r'video-item--comments[^>]*>.*?</svg>\s*([\d.,]+[KMBkmb]?)|'
    r'video-item--comments[^>]*>\s*([\d.,]+[KMBkmb]?)\s*<',
    re.I | re.S,
)
_LIKES_DISLIKES_RE = re.compile(
    r'title="([\d.,]+[KMBkmb]?)\s*Likes?\s*\|\s*([\d.,]+[KMBkmb]?)\s*Dislikes?"',
    re.I,
)


def _counter_from_match(match: re.Match[str] | None) -> int | None:
    if not match:
        return None
    raw = next((g for g in match.groups() if g), None)
    return _parse_count(raw) if raw else None


def parse_search_html(html: str, limit: int = 20) -> list[dict[str, Any]]:
    """Parse Rumble search result cards into video list items."""
    if not html:
        return []
    capped = max(1, min(int(limit or 20), 200))
    starts = list(_ENTRY_RE.finditer(html))
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, match in enumerate(starts):
        end = starts[idx + 1].start() if idx + 1 < len(starts) else min(len(html), match.start() + 6000)
        chunk = html[match.start() : end]
        href_m = _HREF_RE.search(chunk)
        if not href_m:
            continue
        path = href_m.group(1)
        if path in seen:
            continue
        seen.add(path)
        title_m = _TITLE_RE.search(chunk)
        by_m = _BY_RE.search(chunk)
        dur_m = _DURATION_ATTR_RE.search(chunk)
        time_m = _TIME_RE.search(chunk)
        thumb_m = _THUMB_RE.search(chunk)
        votes_m = _LIKES_DISLIKES_RE.search(chunk)
        likes = _parse_count(votes_m.group(1)) if votes_m else None
        dislikes = _parse_count(votes_m.group(2)) if votes_m else None
        channel = safe_str(unescape(by_m.group(2))) if by_m else None
        channel_url = f"https://rumble.com{by_m.group(1)}" if by_m else None
        out.append(
            {
                "platform": "rumble",
                "id": path.split("/")[-1].split("-")[0],
                "url": f"https://rumble.com{path}",
                "title": safe_str(unescape(title_m.group(1))) if title_m else None,
                "channel": channel,
                "channelUrl": channel_url,
                "views": _counter_from_match(_VIEWS_RE.search(chunk)),
                "likes": likes,
                "dislikes": dislikes,
                "duration": safe_str(dur_m.group(1)) if dur_m else None,
                "publishedAt": safe_str(time_m.group(1)) if time_m else None,
                "thumbnail": safe_str(unescape(thumb_m.group(1))) if thumb_m else None,
                "comments": _counter_from_match(_COMMENTS_RE.search(chunk)),
            }
        )
        if len(out) >= capped:
            break
    return out


async def search_native(query: str, limit: int = 20) -> list[dict[str, Any]] | None:
    """Public keyword search via Decodo-rendered search HTML."""
    from urllib.parse import quote

    q = (query or "").strip()
    if len(q) < 2 or not decodo_fetch.enabled():
        return None
    url = f"https://rumble.com/search/video?q={quote(q)}"
    got = await decodo_fetch.fetch_url(url, timeout=90.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body:
        log.info("rumble_search_native_http", status=status, query=q[:80])
        return None
    results = parse_search_html(body, limit=limit)
    if not results:
        log.warning("rumble_search_native_parse_miss", query=q[:80], length=len(body))
        return None
    log.info("rumble_search_native_ok", query=q[:80], returned=len(results))
    return results

