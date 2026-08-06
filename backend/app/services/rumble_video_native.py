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
from datetime import datetime, timezone
from html import unescape
from typing import Any

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str
from app.utils.url import extract_rumble_video_id

log = structlog.get_logger(__name__)


def to_utc_published_at(value: Any) -> str | None:
    """Normalize timestamps to UTC ``+00:00``.

    Accepts ISO-8601 / ``Z`` and unix epoch seconds (int or digit string).
    Display strings like ``Friday, July 17, 2026 08:33 AM -04`` are rejected
    → ``null`` (never echoed into the public response).
    """
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        ts = float(value)
        if ts > 1e12:  # ms
            ts /= 1000.0
        if ts < 1e9:
            return None
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    text = safe_str(value)
    if not text:
        return None
    if re.fullmatch(r"\d{10,13}", text):
        return to_utc_published_at(int(text))
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def honest_views(
    views: Any,
    *,
    likes: Any = None,
    comments: Any = None,
    dislikes: Any = None,
) -> int | None:
    """Drop impossible ``views: 0`` when other engagement is present.

    Fresh Rumble pages/JSON-LD often ship ``userInteractionCount: 0`` while
    the vote UI already shows likes/comments — treat that as unknown.
    """
    v = safe_int(views)
    if v is None:
        return None
    if v == 0 and any((safe_int(x) or 0) > 0 for x in (likes, comments, dislikes)):
        return None
    return v


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
    value, _approx = _parse_count_ex(raw)
    return value


def _parse_count_ex(raw: str | None) -> tuple[int | None, bool]:
    """Like ``_parse_count`` plus whether the source used a K/M/B compact suffix."""
    if not raw:
        return None, False
    text = raw.strip().replace(",", "").upper()
    mult = 1
    approx = False
    if text.endswith("K"):
        mult = 1_000
        text = text[:-1]
        approx = True
    elif text.endswith("M"):
        mult = 1_000_000
        text = text[:-1]
        approx = True
    elif text.endswith("B"):
        mult = 1_000_000_000
        text = text[:-1]
        approx = True
    try:
        return int(float(text) * mult), approx
    except ValueError:
        return safe_int(re.sub(r"[^\d]", "", raw)), False


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
    """HTML-scraped MP4 URLs — no height metadata, so finalise with null quality.

    EmbedJS path is authoritative; these only fill gaps and are dropped when
    ``finalise_streams(..., require_height=True)`` runs on video-details.
    """
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for url in _MP4_RE.findall(html or ""):
        # Keep query string — signed CDNs often put expiry in ``expire`` / ``e``.
        clean = unescape(url).split("&amp;")[0]
        if clean in seen:
            continue
        seen.add(clean)
        out.append({"url": clean, "type": "video/mp4"})
        if len(out) >= 8:
            break
    return out


def _votes_from_html(html: str) -> tuple[int | None, int | None, bool]:
    """Likes/dislikes + whether likes came from a compact K/M/B display."""
    title_m = _VOTES_TITLE_RE.search(html or "")
    if title_m:
        likes, likes_approx = _parse_count_ex(title_m.group(1))
        dislikes, _ = _parse_count_ex(title_m.group(2))
        return likes, dislikes, likes_approx
    up_m = _VOTES_UP_RE.search(html or "")
    down_m = _VOTES_DOWN_RE.search(html or "")
    if not up_m and not down_m:
        return None, None, False
    likes, likes_approx = _parse_count_ex(up_m.group(1)) if up_m else (None, False)
    dislikes, _ = _parse_count_ex(down_m.group(1)) if down_m else (None, False)
    return likes, dislikes, likes_approx


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


def _captions_from_html(html: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for tag_m in _TRACK_CAPTION_RE.finditer(html or ""):
        attrs = {a.group(1).lower(): unescape(a.group(2)) for a in _ATTR_RE.finditer(tag_m.group(0))}
        src = safe_str(attrs.get("src"))
        if not src:
            continue
        if src.startswith("//"):
            src = f"https:{src}"
        lang = safe_str(attrs.get("srclang")) or "und"
        out.append(
            {
                "code": lang,
                "language": safe_str(attrs.get("label")) or lang,
                "url": src,
            }
        )
    return finalise_captions(out)


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


def quality_from_height(h: Any) -> str | None:
    """Map pixel height → quality label. Never use upstream slot keys (``1081``)."""
    height = safe_int(h)
    if height is None or height <= 0:
        return None
    if height >= 2160:
        return "2160p"
    if height >= 1440:
        return "1440p"
    if height >= 1080:
        return "1080p"
    if height >= 720:
        return "720p"
    if height >= 480:
        return "480p"
    if height >= 360:
        return "360p"
    if height >= 240:
        return "240p"
    return f"{height}p"


# Uniform keys for every streams[] / audioStreams[] row (nested list hygiene).
STREAM_KEYS: tuple[str, ...] = (
    "url",
    "type",
    "quality",
    "width",
    "height",
    "bitrateKbps",
    "sizeBytes",
    "expiresAt",
)
CAPTION_KEYS: tuple[str, ...] = ("code", "language", "url", "expiresAt")


def _media_node_sort_key(kv: tuple[Any, Any]) -> tuple[int, int]:
    _key, node = kv
    meta = node.get("meta") if isinstance(node, dict) and isinstance(node.get("meta"), dict) else {}
    h = safe_int(meta.get("h")) if meta else None
    br = safe_int(meta.get("bitrate")) if meta else None
    return (h or 0, br or 0)


def _normalize_stream_type(typ: str | None, *, audio: bool = False) -> str | None:
    raw = (typ or "").strip().lower()
    if audio or raw.startswith("audio"):
        return "audio/aac" if raw in {"", "audio", "aac", "audio/aac"} else (typ or "audio/aac")
    if raw in {"mp4", "video/mp4", "video"}:
        return "video/mp4"
    if raw in {"hls", "application/x-mpegurl", "application/vnd.apple.mpegurl"}:
        return "hls"
    if raw == "image":
        return "image"
    return typ or None


def finalise_stream(
    s: dict[str, Any],
    *,
    audio: bool = False,
) -> dict[str, Any]:
    """Force ``STREAM_KEYS`` — missing scrape → null, never a missing key."""
    from app.utils.media_urls import cdn_expires_at

    url = safe_str(s.get("url"))
    meta = s.get("meta") if isinstance(s.get("meta"), dict) else {}
    width = safe_int(s.get("width") if s.get("width") is not None else meta.get("w"))
    height = safe_int(s.get("height") if s.get("height") is not None else meta.get("h"))
    bitrate = safe_int(
        s.get("bitrateKbps")
        if s.get("bitrateKbps") is not None
        else s.get("bitrate")
        if s.get("bitrate") is not None
        else meta.get("bitrate")
    )
    size = safe_int(
        s.get("sizeBytes")
        if s.get("sizeBytes") is not None
        else s.get("size")
        if s.get("size") is not None
        else meta.get("size")
    )
    # Zero asserts a real dimension — use null for audio / withheld.
    if width is not None and width <= 0:
        width = None
    if height is not None and height <= 0:
        height = None
    if audio:
        width = None
        height = None
        quality = None  # bitrateKbps already carries the rate
        typ = _normalize_stream_type(safe_str(s.get("type")), audio=True)
    else:
        # Quality only from height — never upstream slot keys (duplicate 480p).
        quality = quality_from_height(height)
        typ = _normalize_stream_type(safe_str(s.get("type")), audio=False)
    expires = safe_str(s.get("expiresAt")) or cdn_expires_at(url)
    return {
        "url": url,
        "type": typ,
        "quality": quality,
        "width": width,
        "height": height,
        "bitrateKbps": bitrate,
        "sizeBytes": size,
        "expiresAt": expires,
    }


def finalise_streams(
    streams: list[dict[str, Any]] | None,
    *,
    thumbnail_url: str | None = None,
    require_height: bool = True,
) -> list[dict[str, Any]]:
    """Dedupe + filter junk + uniform keys + height/bitrate sort desc."""
    seen_url: set[str] = set()
    out: list[dict[str, Any]] = []
    thumb = safe_str(thumbnail_url)
    for s in streams or []:
        if not isinstance(s, dict):
            continue
        url = safe_str(s.get("url"))
        if not url or url in seen_url:
            continue
        if thumb and url == thumb:
            continue
        stype = (safe_str(s.get("type")) or "").lower()
        if stype.startswith("audio") or stype == "image":
            continue
        row = finalise_stream(s, audio=False)
        if require_height and (row.get("height") is None or int(row["height"] or 0) <= 0):
            continue
        seen_url.add(url)
        out.append(row)
        if len(out) >= 24:
            break
    out.sort(
        key=lambda r: (safe_int(r.get("height")) or 0, safe_int(r.get("bitrateKbps")) or 0),
        reverse=True,
    )
    return out


def finalise_audio_streams(streams: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    seen_url: set[str] = set()
    out: list[dict[str, Any]] = []
    for s in streams or []:
        if not isinstance(s, dict):
            continue
        url = safe_str(s.get("url"))
        if not url or url in seen_url:
            continue
        seen_url.add(url)
        out.append(finalise_stream(s, audio=True))
    return out


def finalise_captions(captions: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    from app.utils.media_urls import cdn_expires_at

    out: list[dict[str, Any]] = []
    for c in captions or []:
        if not isinstance(c, dict):
            continue
        url = safe_str(c.get("url"))
        if not url:
            continue
        out.append(
            {
                "code": safe_str(c.get("code")) or "und",
                "language": safe_str(c.get("language")) or safe_str(c.get("code")) or "und",
                "url": url,
                "expiresAt": safe_str(c.get("expiresAt")) or cdn_expires_at(url),
            }
        )
    return out


def finalise_thumbnail_track(track: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(track, dict) or not safe_str(track.get("url")):
        return None
    row = finalise_stream({**track, "type": "image"}, audio=False)
    # Sprite strip — quality label is meaningless.
    row["quality"] = None
    row["type"] = "image"
    return row


def _stream_row_from_node(
    node: dict[str, Any],
    *,
    typ: str,
    require_height: bool = True,
) -> dict[str, Any] | None:
    """One playable stream from embedJS node metadata (not the upstream key)."""
    url = safe_str(node.get("url"))
    if not url:
        return None
    meta = node.get("meta") if isinstance(node.get("meta"), dict) else {}
    height = safe_int(meta.get("h"))
    if require_height and (height is None or height <= 0):
        return None
    return finalise_stream(
        {
            "url": url,
            "type": typ,
            "meta": meta,
            "width": meta.get("w"),
            "height": height,
            "bitrate": meta.get("bitrate"),
            "size": meta.get("size"),
        },
        audio=typ.startswith("audio"),
    )


def _streams_from_media(media: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Flat playable video streams from embed ``mp4`` / ``tar`` / ``hls``.

    Quality comes from ``meta.h``, never the upstream key (``240`` with h=360
    → ``360p``; two 1080p bitrates stay two array entries). Timeline strips and
    audio stay out of this list. Nodes without ``meta.h`` are dropped.
    """
    if not media:
        return []
    out: list[dict[str, Any]] = []
    seen_url: set[str] = set()

    mp4 = media.get("mp4") if isinstance(media.get("mp4"), dict) else {}
    for _q, node in sorted(mp4.items(), key=_media_node_sort_key, reverse=True):
        if not isinstance(node, dict):
            continue
        row = _stream_row_from_node(node, typ="video/mp4", require_height=True)
        if not row or row["url"] in seen_url:
            continue
        seen_url.add(row["url"])
        out.append(row)

    tar = media.get("tar") if isinstance(media.get("tar"), dict) else {}
    for _q, node in sorted(tar.items(), key=_media_node_sort_key, reverse=True):
        if not isinstance(node, dict):
            continue
        row = _stream_row_from_node(node, typ="hls", require_height=True)
        if not row or row["url"] in seen_url:
            continue
        seen_url.add(row["url"])
        out.append(row)

    hls = media.get("hls") if isinstance(media.get("hls"), dict) else {}
    for _q, node in hls.items():
        if not isinstance(node, dict):
            continue
        # HLS without height stays only when meta.h is present — never label
        # quality from the upstream slot key.
        row = _stream_row_from_node(node, typ="hls", require_height=True)
        if not row or row["url"] in seen_url:
            continue
        seen_url.add(row["url"])
        out.append(row)

    return finalise_streams(out, require_height=True)[:24]


def _audio_streams_from_media(media: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not media:
        return []
    audio = media.get("audio") if isinstance(media.get("audio"), dict) else {}
    out: list[dict[str, Any]] = []
    for _q, node in sorted(audio.items(), key=_media_node_sort_key, reverse=True):
        if not isinstance(node, dict):
            continue
        # Audio: do not require height (meta often ships w=0,h=0).
        row = _stream_row_from_node(node, typ="audio/aac", require_height=False)
        if row:
            out.append(row)
    return finalise_audio_streams(out)


def _thumbnail_track_from_media(media: dict[str, Any] | None) -> dict[str, Any] | None:
    """Sprite / timeline strip — not a playable video stream."""
    if not media:
        return None
    timeline = media.get("timeline") if isinstance(media.get("timeline"), dict) else {}
    for _q, node in sorted(timeline.items(), key=_media_node_sort_key, reverse=True):
        if not isinstance(node, dict):
            continue
        url = safe_str(node.get("url"))
        if not url:
            continue
        meta = node.get("meta") if isinstance(node.get("meta"), dict) else {}
        return finalise_thumbnail_track(
            {
                "url": url,
                "type": "image",
                "width": meta.get("w"),
                "height": meta.get("h"),
                "bitrate": meta.get("bitrate"),
                "size": meta.get("size"),
            }
        )
    return None


def _captions_array(payload: dict[str, Any]) -> list[dict[str, Any]]:
    captions = payload.get("cc") if isinstance(payload.get("cc"), dict) else None
    if not captions:
        return []
    out: list[dict[str, Any]] = []
    for key, node in captions.items():
        if not isinstance(node, dict):
            continue
        path = safe_str(node.get("path") or node.get("url"))
        if not path:
            continue
        if path.startswith("//"):
            path = f"https:{path}"
        elif path.startswith("/"):
            path = f"https://rumble.com{path}"
        out.append(
            {
                "code": str(key),
                "language": safe_str(node.get("language")) or str(key),
                "url": path,
            }
        )
    return finalise_captions(out)


def _width_height_from_embed(payload: dict[str, Any], media: dict[str, Any] | None) -> tuple[int | None, int | None]:
    best_w: int | None = None
    best_h: int | None = None
    if media:
        for bucket in ("mp4", "tar"):
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


def apply_embedjs(card: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Merge embedJS streams/captions/ids into an existing video-details card."""
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
        card["durationText"] = _seconds_to_clock(dur)
        # Canonical pair only — no legacy duration string / durationFormatted.
        card.pop("duration", None)
        card.pop("durationFormatted", None)

    live_raw = payload.get("live")
    if live_raw is not None:
        card["isLive"] = bool(safe_int(live_raw) or 0) if not isinstance(live_raw, bool) else live_raw

    caps = _captions_array(payload)
    if caps:
        card["captions"] = caps

    media = _media_from_embed(payload)
    # Never expose raw quality-keyed ``media`` — streams[] is authoritative.
    card.pop("media", None)
    track = _thumbnail_track_from_media(media) if media else None
    thumb_url = safe_str(track.get("url")) if track else None
    if media:
        card["streams"] = finalise_streams(
            list(_streams_from_media(media))
            + [s for s in (card.get("streams") or []) if isinstance(s, dict)],
            thumbnail_url=thumb_url,
            require_height=True,
        )
        audio = _audio_streams_from_media(media)
        if audio:
            card["audioStreams"] = audio
        if track:
            card["thumbnailTrack"] = track
    elif card.get("streams"):
        card["streams"] = finalise_streams(
            [s for s in card["streams"] if isinstance(s, dict)],
            require_height=True,
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
    likes, dislikes, likes_approx = _votes_from_html(html)
    comments = _comments_from_html(html)
    views = honest_views(views, likes=likes, comments=comments, dislikes=dislikes)
    iso_dur = safe_str((video or {}).get("duration"))
    duration_seconds = _iso_duration_seconds(iso_dur)
    duration_text = _seconds_to_clock(duration_seconds) if duration_seconds is not None else _parse_iso_duration(iso_dur)
    embed_id = _embed_id_from_html(html, embed)
    # Only trust embed URLs that use the page's real embed id — never the
    # permalink slug (channel lists used to fabricate /embed/{permalink}/ → 404).
    if embed_id:
        embed = f"https://rumble.com/embed/{embed_id}/"
    elif embed and video_id and f"/embed/{video_id}" in embed:
        embed = None
    numeric_id = _numeric_id_from_html(html)
    captions = _captions_from_html(html)
    is_live = _is_live_from_html(html)
    content_type = "live" if is_live else ("short" if (canonical or url or "") and "/shorts/" in (canonical or url or "").lower() else "video")

    return {
        "platform": "rumble",
        "id": safe_str(video_id),
        "numericId": numeric_id,
        "embedId": embed_id,
        "url": canonical,
        "type": content_type,
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
        "likesIsApproximate": bool(likes_approx) if likes is not None else None,
        "dislikes": dislikes,
        "comments": comments,
        "durationSeconds": duration_seconds,
        "durationText": duration_text,
        "publishedAt": to_utc_published_at((video or {}).get("uploadDate")),
        "thumbnail": thumbnail,
        "width": None,
        "height": None,
        "captions": captions or None,
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
        streams=len(parsed.get("streams") or []),
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
        comments = _counter_from_match(_COMMENTS_RE.search(chunk))
        views = honest_views(
            _counter_from_match(_VIEWS_RE.search(chunk)),
            likes=likes,
            comments=comments,
            dislikes=dislikes,
        )
        channel = safe_str(unescape(by_m.group(2))) if by_m else None
        channel_path = safe_str(by_m.group(1)) if by_m else None
        channel_url = f"https://rumble.com{channel_path}" if channel_path else None
        channel_handle = (
            channel_path.rstrip("/").split("/")[-1] if channel_path else None
        )
        video_id = path.split("/")[-1].split("-")[0]
        clock = safe_str(dur_m.group(1)) if dur_m else None
        is_live = bool(re.search(r"video-item--live|livestream", chunk, re.I))
        content_type = (
            "live"
            if is_live
            else ("short" if "/shorts/" in path.lower() else "video")
        )
        out.append(
            {
                "platform": "rumble",
                "id": video_id,
                "url": f"https://rumble.com{path}",
                "type": content_type,
                "title": safe_str(unescape(title_m.group(1))) if title_m else None,
                "channel": channel,
                "channelUrl": channel_url,
                "channelHandle": channel_handle,
                "channelVerified": bool(_VERIFIED_RE.search(chunk)) or None,
                "views": views,
                "likes": likes,
                "dislikes": dislikes,
                "comments": comments,
                "durationSeconds": _clock_to_seconds(clock),
                "durationText": clock,
                "publishedAt": to_utc_published_at(
                    time_m.group(1) if time_m else None
                ),
                "thumbnail": safe_str(unescape(thumb_m.group(1))) if thumb_m else None,
                "isLive": is_live,
                "streams": [],
                "shareUrl": f"https://rumble.com/share/{video_id}" if video_id else None,
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

