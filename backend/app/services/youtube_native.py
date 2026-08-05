"""Self-scraped YouTube data from public pages + InnerTube (no Apify).

Every function returns data in the exact shapes the routers already emit, or
``None``/``[]`` on failure so callers can fall back to the Apify actors.

Approach:
- List pages (search results, channel tabs, hashtag pages) embed
  ``ytInitialData``; we parse the video renderers straight out of it and follow
  one continuation via InnerTube when the caller wants more than one page.
- Channel metadata comes from the channel page (``channelMetadataRenderer``)
  plus the About popup fetched through InnerTube ``browse``.
- Transcripts come from InnerTube ANDROID player caption tracks (direct egress
  first — proxy IPs often get LOGIN_REQUIRED; web watch timedtext needs a PoT).
- Community posts come from the channel ``/posts`` tab ``ytInitialData`` plus
  InnerTube browse continuations.
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
import shlex
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator
from urllib.parse import parse_qs, urlparse

import httpx

from app.services.http_fetch import fetch as proxy_fetch, post_json, proxy_for
from app.utils.countries import country_code_from_name, country_name
from app.utils.formatters import safe_int, safe_list, safe_str

YT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
# CONSENT/SOCS skip the EU consent wall; PREF pins English so count/date text
# parses predictably.
YT_COOKIES: dict[str, str] = {"CONSENT": "YES+1", "SOCS": "CAI", "PREF": "hl=en&gl=US"}

_INNERTUBE_CLIENT_VERSION = "2.20250313.00.00"
_INNERTUBE_CONTEXT = {
    "client": {
        "clientName": "WEB",
        "clientVersion": _INNERTUBE_CLIENT_VERSION,
        "hl": "en",
        "gl": "US",
    }
}
# Channel tab browse ``params`` (protobuf) — same values yt-dlp / web UI use.
_CHANNEL_TAB_PARAMS: dict[str, str] = {
    "videos": "EgZ2aWRlb3PyBgQKAjoA",
    "shorts": "EgZzaG9ydHPyBgUKA5oBAA%3D%3D",
    "streams": "EgdzdHJlYW1z8gYECgJ6AA%3D%3D",
    "playlists": "EglwbGF5bGlzdHPyBgQKAkIA",
    "about": "EgVhYm91dPIGBAoCEgA%3D",
}
# Shorts filter for InnerTube ``search`` (same as ``sp=EgIYAQ==`` on /results).
_SEARCH_SHORTS_PARAMS = "EgIYAQ=="

# YouTube search ``sp`` / InnerTube ``params`` enums (Invidious-compatible).
_SEARCH_SORT = {"relevance": 0, "rating": 1, "date": 2, "views": 3, "popular": 3}
_SEARCH_UPLOAD = {
    "any": 0,
    "hour": 1,
    "today": 2,
    "this_week": 3,
    "week": 3,
    "this_month": 4,
    "month": 4,
    "this_year": 5,
    "year": 5,
}
_SEARCH_TYPE = {
    "all": 0,
    "video": 1,
    "videos": 1,
    "channel": 2,
    "channels": 2,
    "playlist": 3,
    "playlists": 3,
    "movie": 4,
    "movies": 4,
}
_SEARCH_DURATION = {
    "any": 0,
    "under_4": 1,
    "short": 1,
    "4_20": 2,
    "medium": 2,
    "over_20": 3,
    "long": 3,
}

_JSON_DECODER = json.JSONDecoder()


def _pb_varint(value: int) -> bytes:
    n = int(value)
    out = bytearray()
    while True:
        bits = n & 0x7F
        n >>= 7
        out.append(bits | (0x80 if n else 0))
        if not n:
            return bytes(out)


def _pb_key(field: int, wire: int) -> bytes:
    return _pb_varint((field << 3) | wire)


def encode_search_params(
    *,
    sort_by: str | None = None,
    upload_date: str | None = None,
    result_type: str | None = None,
    duration: str | None = None,
) -> str | None:
    """Build InnerTube search ``params`` (base64url protobuf), or None if default."""
    import base64

    sort_n = _SEARCH_SORT.get((sort_by or "relevance").strip().lower(), 0)
    date_n = _SEARCH_UPLOAD.get((upload_date or "any").strip().lower().replace("-", "_"), 0)
    type_n = _SEARCH_TYPE.get((result_type or "all").strip().lower().replace("-", "_"), 0)
    dur_n = _SEARCH_DURATION.get((duration or "any").strip().lower().replace("-", "_"), 0)

    # Dedicated Shorts filter (not the same protobuf type enum).
    if (result_type or "").strip().lower() in {"short", "shorts"}:
        return _SEARCH_SHORTS_PARAMS

    embedded = bytearray()
    if date_n:
        embedded += _pb_key(1, 0) + _pb_varint(date_n)
    if type_n:
        embedded += _pb_key(2, 0) + _pb_varint(type_n)
    if dur_n:
        embedded += _pb_key(3, 0) + _pb_varint(dur_n)

    obj = bytearray()
    if sort_n:
        obj += _pb_key(1, 0) + _pb_varint(sort_n)
    if embedded:
        obj += _pb_key(2, 2) + _pb_varint(len(embedded)) + embedded
    if not obj:
        return None
    return base64.urlsafe_b64encode(bytes(obj)).decode("ascii").rstrip("=")


def extract_initial_json(html: str, var_name: str) -> dict[str, Any] | None:
    """Pull an embedded ``var X = {...};`` blob out of a YouTube page.

    The objects are megabytes long with trailing script on the same line, so a
    regex can't find the closing brace; ``raw_decode`` reads exactly one JSON
    value from the opening ``{``.
    """
    for anchor in (f"var {var_name} = ", f'window["{var_name}"] = ', f"{var_name} = "):
        idx = html.find(anchor)
        if idx == -1:
            continue
        start = html.find("{", idx)
        if start == -1:
            continue
        try:
            obj, _ = _JSON_DECODER.raw_decode(html, start)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def text_of(node: Any) -> str | None:
    """Extract text from YouTube's ``{simpleText}`` / ``{runs: [{text}]}`` /
    ``{content}`` shapes."""
    if node is None:
        return None
    if isinstance(node, str):
        return node or None
    if isinstance(node, dict):
        if node.get("simpleText"):
            return str(node["simpleText"])
        if node.get("content"):
            return str(node["content"])
        runs = node.get("runs")
        if isinstance(runs, list):
            joined = "".join(str(r.get("text") or "") for r in runs if isinstance(r, dict))
            return joined or None
    return None


_COUNT_RE = re.compile(r"([\d.,]+)\s*([KMB])?", re.IGNORECASE)
_MULT = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
_RELATIVE_PUBLISHED_RE = re.compile(
    r"(?:streamed\s+|premiered\s+)?"
    r"(?:(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?|years?|mo|yr)"
    r"|(\d+)\s*([smhdwy]))"
    r"\s+ago",
    re.IGNORECASE,
)
_UNIT_SECONDS = {
    "second": 1,
    "seconds": 1,
    "s": 1,
    "minute": 60,
    "minutes": 60,
    "m": 60,
    "hour": 3600,
    "hours": 3600,
    "h": 3600,
    "day": 86400,
    "days": 86400,
    "d": 86400,
    "week": 604800,
    "weeks": 604800,
    "w": 604800,
    "month": 2_592_000,  # 30d — YouTube's label is already approximate
    "months": 2_592_000,
    "mo": 2_592_000,
    "year": 31_536_000,  # 365d
    "years": 31_536_000,
    "y": 31_536_000,
    "yr": 31_536_000,
}


def parse_count_text(value: Any) -> int | None:
    """Parse '1,234,567 views', '1.2M views', '123K', 'No views' -> int."""
    n, _approx = parse_count_text_meta(value)
    return n


def parse_count_text_meta(value: Any) -> tuple[int | None, bool]:
    """Return ``(count, approximate)`` — approximate when K/M/B compact form."""
    s = text_of(value) if not isinstance(value, str) else value
    if not s:
        return None, False
    if "no views" in s.lower():
        return 0, False
    m = _COUNT_RE.search(s.replace("\u00a0", " "))
    if not m:
        return None, False
    num, suffix = m.group(1), (m.group(2) or "").upper()
    try:
        base = float(num.replace(",", ""))
    except ValueError:
        return None, False
    return int(base * _MULT.get(suffix, 1)), bool(suffix)


def approximate_iso_from_relative(value: Any, *, now: datetime | None = None) -> str | None:
    """Turn YouTube labels like ``1 year ago`` / ``5d ago`` into approximate ISO-8601.

    Exact timestamps are rarely on playlist/search cards; this keeps ``publishedAt``
    sortable/ISO-typed while ``publishedTimeText`` retains the original label.
    """
    text = (text_of(value) if not isinstance(value, str) else value) or ""
    text = text.strip()
    if not text:
        return None
    # Already ISO-ish.
    if "T" in text and (text.endswith("Z") or "+" in text[10:]):
        return text
    m = _RELATIVE_PUBLISHED_RE.search(text)
    if not m:
        return None
    amount = int(m.group(1) or m.group(3) or 0)
    unit = (m.group(2) or m.group(4) or "").lower()
    secs = _UNIT_SECONDS.get(unit)
    if not secs or amount <= 0:
        return None
    base = now or datetime.now(timezone.utc)
    approx = base - timedelta(seconds=amount * secs)
    return approx.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def published_fields(relative_or_iso: Any) -> tuple[str | None, str | None]:
    """Return ``(publishedAt ISO|None, publishedTimeText|None)``."""
    text = text_of(relative_or_iso) if not isinstance(relative_or_iso, str) else relative_or_iso
    text = (text or "").strip() or None
    if not text:
        return None, None
    if "T" in text and (text.endswith("Z") or "+" in text[10:]):
        return text, None
    if re.search(r"\bago\b", text, re.I) or re.search(r"\b(premiere|streamed|scheduled)\b", text, re.I):
        return approximate_iso_from_relative(text), text
    # Bare date YYYY-MM-DD from some actors.
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return f"{text}T00:00:00.000Z", None
    return None, text


def _looks_iso8601(value: Any) -> bool:
    s = safe_str(value) or ""
    return bool(s) and "T" in s and (s.endswith("Z") or "+" in s[10:] or s.endswith("+00:00"))


def _looks_relative_published(value: Any) -> bool:
    s = safe_str(value) or ""
    return bool(
        re.search(r"\bago\b", s, re.I)
        or re.search(r"\b(premiere|streamed|scheduled)\b", s, re.I)
    )


def coerce_published_fields(card: dict[str, Any]) -> dict[str, Any]:
    """Guarantee ``publishedAt`` is ISO (or null) — never a relative label.

    YouTube list cards often only expose ``"4 days ago"``. Callers must keep
    that string in ``publishedTimeText`` and put an approximate ISO in
    ``publishedAt`` so typed SDKs / monitors / date filters work.
    """
    if not isinstance(card, dict):
        return card
    current = card.get("publishedAt")
    text = card.get("publishedTimeText") or card.get("publishedTime")
    if _looks_iso8601(current):
        # Already typed; if the only relative label lived in publishedAt before
        # a partial migrate, leave publishedTimeText alone.
        if text is None and _looks_relative_published(card.get("publishedTimeText")):
            pass
        return card
    raw = text if _looks_relative_published(text) else None
    if raw is None and _looks_relative_published(current):
        raw = current
    if raw is None:
        raw = text or current
    iso, rel = published_fields(raw)
    if iso is not None:
        card["publishedAt"] = iso
    elif _looks_relative_published(current):
        # Never leave "4 days ago" in the ISO field.
        card["publishedAt"] = None
    if rel:
        card["publishedTimeText"] = rel
    elif _looks_relative_published(current) and not card.get("publishedTimeText"):
        card["publishedTimeText"] = safe_str(current)
    return card


def walk_find(node: Any, key: str) -> Iterator[dict[str, Any]]:
    """Yield every dict found under ``key`` anywhere in the tree."""
    if isinstance(node, dict):
        found = node.get(key)
        if isinstance(found, dict):
            yield found
        for v in node.values():
            yield from walk_find(v, key)
    elif isinstance(node, list):
        for v in node:
            yield from walk_find(v, key)


def _duration_text_seconds(value: Any) -> int | None:
    s = text_of(value)
    if not s or not re.fullmatch(r"\d+(?::\d{1,2}){0,2}", s.strip()):
        return None
    total = 0
    for part in s.strip().split(":"):
        total = total * 60 + int(part)
    return total


def _best_thumb(node: Any) -> str | None:
    """Last (largest) thumbnail URL from ``{thumbnails: [...]}`` or
    ``{sources: [...]}``."""
    if not isinstance(node, dict):
        return None
    arr = node.get("thumbnails") or node.get("sources")
    if isinstance(arr, list) and arr and isinstance(arr[-1], dict):
        return safe_str(arr[-1].get("url"))
    for v in node.values():
        found = _best_thumb(v) if isinstance(v, dict) else None
        if found:
            return found
    return None


def thumbnail_url_for_video_id(video_id: str | None) -> str | None:
    """Stable YouTube thumbnail from a watch/shorts id (SC uses the same pattern)."""
    vid = (video_id or "").strip()
    if len(vid) != 11:
        return None
    return f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg"


def format_count_text(n: int | None) -> str | None:
    """SC-style ``viewCountText`` / ``likeCountText`` (thousands separators)."""
    if n is None:
        return None
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return None


def format_duration_hms(seconds: int | None) -> str | None:
    if seconds is None:
        return None
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return None
    if total < 0:
        return None
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _stamp_count_fields(
    card: dict[str, Any],
    *,
    count: int | None,
    text: str | None = None,
    approximate: bool = False,
) -> dict[str, Any]:
    """Attach ``viewCount`` + SC-style ``viewCountInt`` / ``viewCountText``."""
    card["viewCount"] = count
    card["viewCountInt"] = count
    card["viewCountText"] = text or format_count_text(count)
    if approximate and count is not None:
        card["viewCountApproximate"] = True
    elif "viewCountApproximate" in card and not approximate:
        card.pop("viewCountApproximate", None)
    return card


def _channel_from_text_runs(node: Any) -> dict[str, Any]:
    """Extract channel id/handle/name from owner/byline text runs."""
    name = text_of(node)
    channel_id = None
    handle = None
    url = None
    if isinstance(node, dict):
        for run in node.get("runs") or []:
            if not isinstance(run, dict):
                continue
            browse = ((run.get("navigationEndpoint") or {}).get("browseEndpoint")) or {}
            channel_id = safe_str(browse.get("browseId")) or channel_id
            base = safe_str(browse.get("canonicalBaseUrl"))
            if base:
                url = f"https://www.youtube.com{base}" if base.startswith("/") else base
                if base.startswith("/@"):
                    handle = base[1:]
            if not name:
                name = safe_str(run.get("text"))
    return {
        "id": channel_id,
        "title": name,
        "handle": handle,
        "url": url,
        "thumbnail": None,
    }


def _badge_labels(node: Any) -> list[str]:
    out: list[str] = []
    for badge in walk_find(node, "metadataBadgeRenderer"):
        label = safe_str(badge.get("label")) or text_of(badge.get("accessibilityData"))
        if not label:
            label = safe_str((badge.get("accessibilityData") or {}).get("label"))
        if label and label not in out:
            out.append(label)
    return out


def _result_type_for_video(vr: dict[str, Any], *, duration: int | None, badges: list[str]) -> str:
    nav = vr.get("navigationEndpoint") or {}
    if (nav.get("reelWatchEndpoint") or {}).get("videoId"):
        return "short"
    low = " ".join(badges).lower()
    if "live" in low or vr.get("badges") and any(
        "LIVE" in str(b) for b in (vr.get("badges") or [])
    ):
        if "upcoming" in low or vr.get("upcomingEventData"):
            return "upcoming"
        return "live"
    if duration is not None and duration > 0 and duration <= 60:
        # Heuristic: sub-minute search hits are often Shorts.
        if "short" in low or duration <= 60:
            # Prefer short only when overlay/shorts signals exist; else video.
            if "short" in low:
                return "short"
    return "video"


def normalize_video_renderer(vr: dict[str, Any]) -> dict[str, Any] | None:
    """``videoRenderer`` (search / channel tabs / hashtag) -> our video card."""
    video_id = safe_str(vr.get("videoId"))
    if not video_id:
        return None
    view_text = text_of(vr.get("viewCountText") or vr.get("shortViewCountText"))
    view_count, view_approx = parse_count_text_meta(vr.get("viewCountText"))
    if view_count is None:
        view_count, view_approx = parse_count_text_meta(vr.get("shortViewCountText"))
    duration = _duration_text_seconds(vr.get("lengthText"))
    badges = _badge_labels(vr)
    channel = _channel_from_text_runs(
        vr.get("ownerText") or vr.get("longBylineText") or vr.get("shortBylineText")
    )
    rtype = _result_type_for_video(vr, duration=duration, badges=badges)
    url = (
        f"https://www.youtube.com/shorts/{video_id}"
        if rtype == "short"
        else f"https://www.youtube.com/watch?v={video_id}"
    )
    published_at, published_text = published_fields(vr.get("publishedTimeText"))
    card: dict[str, Any] = {
        "type": rtype,
        "id": video_id,
        "url": url,
        "title": text_of(vr.get("title")) or "",
        "publishedAt": published_at,
        "publishedTimeText": published_text,
        "viewCount": view_count,
        # Compact label + parsed int (SC-style) — round numbers stay honest.
        "viewCountText": view_text,
        "viewCountInt": view_count,
        "durationSeconds": duration,
        "thumbnailUrl": _best_thumb(vr.get("thumbnail")),
        "channelName": channel.get("title"),
        "channelId": channel.get("id"),
        "channel": channel,
        "badges": badges,
    }
    if view_approx:
        card["viewCountApproximate"] = True
    return card


def _normalize_shorts_lockup(lk: dict[str, Any]) -> dict[str, Any] | None:
    """``shortsLockupViewModel`` (2024+ shorts shelf) -> our video card."""
    on_tap = lk.get("onTap") or {}
    video_id = safe_str(
        (((on_tap.get("innertubeCommand") or {}).get("reelWatchEndpoint")) or {}).get("videoId")
    )
    if not video_id:
        entity = safe_str(lk.get("entityId"))
        m = re.search(r"([\w-]{11})$", entity or "")
        video_id = m.group(1) if m else None
    if not video_id:
        return None
    overlay = lk.get("overlayMetadata") or {}
    view_text = text_of(overlay.get("secondaryText"))
    view_count, view_approx = parse_count_text_meta(overlay.get("secondaryText"))
    # Modern shelf uses thumbnailViewModel (not thumbnail); always fall back to
    # the stable i.ytimg.com URL ScrapeCreators derives from the video id.
    thumb = (
        _best_thumb(lk.get("thumbnailViewModel"))
        or _best_thumb(lk.get("thumbnail"))
        or _best_thumb(((on_tap.get("innertubeCommand") or {}).get("reelWatchEndpoint") or {}).get("thumbnail"))
        or thumbnail_url_for_video_id(video_id)
    )
    card = {
        "type": "short",
        "id": video_id,
        "url": f"https://www.youtube.com/shorts/{video_id}",
        "title": text_of((overlay.get("primaryText") or {})) or "",
        "publishedAt": None,
        "durationSeconds": None,
        "thumbnailUrl": thumb,
        "channelName": None,
        "channelId": None,
        "channel": None,
        "badges": [],
    }
    return _stamp_count_fields(card, count=view_count, text=view_text, approximate=view_approx)


def _normalize_reel_item(r: dict[str, Any]) -> dict[str, Any] | None:
    """Legacy ``reelItemRenderer`` -> our video card."""
    video_id = safe_str(r.get("videoId"))
    if not video_id:
        return None
    view_text = text_of(r.get("viewCountText"))
    view_count, view_approx = parse_count_text_meta(r.get("viewCountText"))
    card = {
        "type": "short",
        "id": video_id,
        "url": f"https://www.youtube.com/shorts/{video_id}",
        "title": text_of(r.get("headline")) or "",
        "publishedAt": None,
        "durationSeconds": None,
        "thumbnailUrl": _best_thumb(r.get("thumbnail")) or thumbnail_url_for_video_id(video_id),
        "channelName": None,
        "channelId": None,
        "channel": None,
        "badges": [],
    }
    return _stamp_count_fields(card, count=view_count, text=view_text, approximate=view_approx)


def _normalize_video_lockup(lk: dict[str, Any]) -> dict[str, Any] | None:
    """``lockupViewModel`` video card used on modern channel tabs."""
    if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO":
        return None
    video_id = safe_str(lk.get("contentId"))
    if not video_id:
        ctx = ((lk.get("rendererContext") or {}).get("commandContext") or {}).get("onTap") or {}
        video_id = safe_str(((ctx.get("innertubeCommand") or {}).get("watchEndpoint") or {}).get("videoId"))
    if not video_id:
        return None

    meta = (lk.get("metadata") or {}).get("lockupMetadataViewModel") or {}
    title = text_of(meta.get("title")) or ""
    rows = (((meta.get("metadata") or {}).get("contentMetadataViewModel") or {}).get("metadataRows")) or []
    parts: list[str] = []
    for row in rows:
        for part in row.get("metadataParts") or []:
            txt = text_of(part.get("text"))
            if txt:
                parts.append(txt)

    # Metadata parts vary by page variant: ["Channel", "1.1M views", "2 days ago"]
    # or the compact form ["Channel", "1.7M", "5d ago"] without the word "views".
    channel_name = None
    view_count = None
    view_approx = False
    published_raw = None
    for txt in parts:
        low = txt.lower()
        stripped = txt.strip()
        if view_count is None and (
            "view" in low or re.fullmatch(r"[\d.,]+\s*[KMB]?", stripped, re.IGNORECASE)
        ):
            view_count, view_approx = parse_count_text_meta(txt)
        elif published_raw is None and any(
            word in low for word in ("ago", "premiere", "streamed", "scheduled")
        ):
            published_raw = txt
        elif channel_name is None:
            channel_name = txt

    duration = None
    for badge in walk_find(lk.get("contentImage"), "thumbnailBadgeViewModel"):
        duration = _duration_text_seconds(badge.get("text"))
        if duration is not None:
            break

    published_at, published_text = published_fields(published_raw)
    rtype = _lockup_result_type(published_raw)
    card: dict[str, Any] = {
        "type": rtype,
        "id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": title,
        "publishedAt": published_at,
        "publishedTimeText": published_text,
        "viewCount": view_count,
        "durationSeconds": duration,
        "thumbnailUrl": _best_thumb(lk.get("contentImage")) or thumbnail_url_for_video_id(video_id),
        "channelName": channel_name,
        "channelId": None,
        "channel": {"id": None, "title": channel_name, "handle": None, "url": None, "thumbnail": None},
        "badges": [],
    }
    if view_approx:
        card["viewCountApproximate"] = True
    return card


def _lockup_result_type(published_raw: str | None) -> str:
    """Classify Live-tab lockups: upcoming / live stream VOD / regular video."""
    low = (published_raw or "").lower()
    if "scheduled" in low or "premiere" in low:
        return "upcoming"
    if "streamed" in low:
        return "stream"
    return "video"


def _normalize_playlist_video(pv: dict[str, Any]) -> dict[str, Any] | None:
    """``playlistVideoRenderer`` on /playlist pages -> our video card."""
    video_id = safe_str(pv.get("videoId"))
    if not video_id:
        return None
    view_count = None
    view_approx = False
    published_raw = None
    for run in (pv.get("videoInfo") or {}).get("runs") or []:
        txt = safe_str(run.get("text")) or ""
        low = txt.lower()
        if "view" in low:
            view_count, view_approx = parse_count_text_meta(txt)
        elif "ago" in low or "streamed" in low or "premiere" in low:
            published_raw = txt
    secs = safe_str(pv.get("lengthSeconds"))
    duration = int(secs) if secs and secs.isdigit() else _duration_text_seconds(pv.get("lengthText"))
    channel = _channel_from_text_runs(pv.get("shortBylineText"))
    published_at, published_text = published_fields(published_raw)
    card: dict[str, Any] = {
        "type": "video",
        "id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": text_of(pv.get("title")) or "",
        "publishedAt": published_at,
        "publishedTimeText": published_text,
        "viewCount": view_count,
        "durationSeconds": duration,
        "thumbnailUrl": _best_thumb(pv.get("thumbnail")),
        "channelName": channel.get("title") or text_of(pv.get("shortBylineText")),
        "channelId": channel.get("id"),
        "channel": channel,
        "badges": [],
    }
    if view_approx:
        card["viewCountApproximate"] = True
    return card


def _normalize_channel_renderer(cr: dict[str, Any]) -> dict[str, Any] | None:
    channel_id = safe_str(cr.get("channelId"))
    if not channel_id:
        return None
    handle = None
    base = safe_str(((cr.get("navigationEndpoint") or {}).get("browseEndpoint") or {}).get("canonicalBaseUrl"))
    if base and base.startswith("/@"):
        handle = base[1:]
    url = f"https://www.youtube.com/channel/{channel_id}"
    if handle:
        url = f"https://www.youtube.com/{handle}"
    return {
        "type": "channel",
        "id": channel_id,
        "url": url,
        "title": text_of(cr.get("title")) or "",
        "publishedAt": None,
        "viewCount": None,
        "durationSeconds": None,
        "thumbnailUrl": _best_thumb(cr.get("thumbnail")),
        "channelName": text_of(cr.get("title")),
        "channelId": channel_id,
        "channel": {
            "id": channel_id,
            "title": text_of(cr.get("title")),
            "handle": handle,
            "url": url,
            "thumbnail": _best_thumb(cr.get("thumbnail")),
        },
        "badges": _badge_labels(cr),
        "subscriberCount": parse_count_text(cr.get("subscriberCountText") or cr.get("videoCountText")),
    }


def _normalize_playlist_renderer(pr: dict[str, Any]) -> dict[str, Any] | None:
    playlist_id = safe_str(pr.get("playlistId"))
    if not playlist_id:
        return None
    channel = _channel_from_text_runs(pr.get("longBylineText") or pr.get("shortBylineText"))
    video_count = parse_count_text(pr.get("videoCount") or pr.get("videoCountText"))
    return {
        "type": "playlist",
        "id": playlist_id,
        "url": f"https://www.youtube.com/playlist?list={playlist_id}",
        "title": text_of(pr.get("title")) or "",
        "publishedAt": None,
        "viewCount": None,
        "durationSeconds": None,
        "thumbnailUrl": _best_thumb(pr.get("thumbnails") or pr.get("thumbnail")),
        "channelName": channel.get("title"),
        "channelId": channel.get("id"),
        "channel": channel,
        "badges": [],
        "videoCount": video_count,
    }


def collect_video_cards(data: Any, *, shorts: bool = False) -> list[dict[str, Any]]:
    """All video cards in a ytInitialData tree / continuation payload."""
    cards: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(card: dict[str, Any] | None) -> None:
        if not card:
            return
        key = safe_str(card.get("id")) or card.get("url")
        if not key or key in seen:
            return
        seen.add(key)
        cards.append(card)

    if shorts:
        for lk in walk_find(data, "shortsLockupViewModel"):
            add(_normalize_shorts_lockup(lk))
        for r in walk_find(data, "reelItemRenderer"):
            add(_normalize_reel_item(r))
        # Some Shorts tabs / filtered search still emit video lockups.
        for vr in walk_find(data, "videoRenderer"):
            card = normalize_video_renderer(vr)
            if card:
                vid = card.get("id") or card["url"].rsplit("/", 1)[-1].replace("watch?v=", "")
                card["type"] = "short"
                card["url"] = f"https://www.youtube.com/shorts/{vid}"
                add(card)
        for lk in walk_find(data, "lockupViewModel"):
            card = _normalize_video_lockup(lk)
            if card:
                vid = card.get("id")
                card["type"] = "short"
                card["url"] = f"https://www.youtube.com/shorts/{vid}"
                add(card)
    else:
        for vr in walk_find(data, "videoRenderer"):
            add(normalize_video_renderer(vr))
        for pv in walk_find(data, "playlistVideoRenderer"):
            add(_normalize_playlist_video(pv))
        for lk in walk_find(data, "lockupViewModel"):
            add(_normalize_video_lockup(lk))
    return _coerce_card_dates(cards)


def collect_search_results(data: Any) -> list[dict[str, Any]]:
    """Mixed search hits: videos/shorts/channels/playlists (document order)."""
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(card: dict[str, Any] | None) -> None:
        if not card:
            return
        key = f"{card.get('type')}:{card.get('id') or card.get('url')}"
        if key in seen:
            return
        seen.add(key)
        results.append(card)

    # Walk top-level section contents in order when possible.
    sections = list(walk_find(data, "itemSectionRenderer"))
    if sections:
        for section in sections:
            for item in section.get("contents") or []:
                if not isinstance(item, dict):
                    continue
                if "videoRenderer" in item:
                    add(normalize_video_renderer(item["videoRenderer"]))
                elif "channelRenderer" in item:
                    add(_normalize_channel_renderer(item["channelRenderer"]))
                elif "playlistRenderer" in item:
                    add(_normalize_playlist_renderer(item["playlistRenderer"]))
                elif "shortsLockupViewModel" in item:
                    add(_normalize_shorts_lockup(item["shortsLockupViewModel"]))
                elif "reelItemRenderer" in item:
                    add(_normalize_reel_item(item["reelItemRenderer"]))
                elif "lockupViewModel" in item:
                    add(_normalize_video_lockup(item["lockupViewModel"]))
    else:
        for card in collect_video_cards(data):
            add(card)
        for cr in walk_find(data, "channelRenderer"):
            add(_normalize_channel_renderer(cr))
        for pr in walk_find(data, "playlistRenderer"):
            add(_normalize_playlist_renderer(pr))
    return _coerce_card_dates(results)


def find_continuation_tokens(data: Any) -> list[str]:
    """All continuation tokens in document order (deduped)."""
    out: list[str] = []
    seen: set[str] = set()
    for c in walk_find(data, "continuationCommand"):
        token = safe_str(c.get("token"))
        if token and token not in seen:
            seen.add(token)
            out.append(token)
    return out


def find_continuation_token(data: Any) -> str | None:
    tokens = find_continuation_tokens(data)
    return tokens[0] if tokens else None


def _proxy_tiers() -> list[str]:
    """Datacenter first (cheap/fast); residential if configured."""
    tiers: list[str] = ["datacenter"]
    if proxy_for("residential"):
        tiers.append("residential")
    return tiers


def _player_tiers() -> list[str]:
    """Egress order for InnerTube ``player`` / timedtext.

    Proxy IPs often get ``LOGIN_REQUIRED`` ("confirm you're not a bot") while
    the host's own IP still returns ``OK`` + caption tracks. Try direct first,
    then the configured proxy pools.
    """
    tiers: list[str] = ["none"]
    for t in _proxy_tiers():
        if t not in tiers:
            tiers.append(t)
    return tiers


async def fetch_page_data(url: str, *, timeout: float = 12.0) -> tuple[dict[str, Any] | None, str]:
    """GET a YouTube page and return (ytInitialData, raw html)."""
    last_html = ""
    for tier in _proxy_tiers():
        try:
            resp = await proxy_fetch(
                url, tier=tier, headers=YT_HEADERS, cookies=YT_COOKIES, timeout=timeout  # type: ignore[arg-type]
            )
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        last_html = resp.text or ""
        data = extract_initial_json(last_html, "ytInitialData")
        if data is not None:
            return data, last_html
    return None, last_html


async def innertube(
    endpoint: str,
    body: dict[str, Any],
    *,
    timeout: float = 12.0,
    region: str | None = None,
    direct_first: bool = False,
) -> dict[str, Any] | None:
    """POST to InnerTube (web client). ``endpoint``: search | browse | next | reel/...

    ``direct_first``: try the host IP before proxies. Required for Shorts reel
    endpoints — datacenter proxies often return an empty ``playerResponse``.
    """
    context = {
        "client": {
            **_INNERTUBE_CONTEXT["client"],
        }
    }
    gl = (region or "").strip().upper()
    if gl and len(gl) == 2:
        context["client"]["gl"] = gl
    tiers = _player_tiers() if direct_first else _proxy_tiers()
    for tier in tiers:
        try:
            resp = await post_json(
                f"https://www.youtube.com/youtubei/v1/{endpoint}",
                {"context": context, **body},
                tier=tier,  # type: ignore[arg-type]
                headers={
                    **YT_HEADERS,
                    "X-Youtube-Client-Name": "1",
                    "X-Youtube-Client-Version": _INNERTUBE_CLIENT_VERSION,
                },
                params={"prettyPrint": "false"},
                timeout=timeout,
            )
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        try:
            data = resp.json()
        except ValueError:
            continue
        if not isinstance(data, dict):
            continue
        # Shorts reel watch via proxy can 200 with a hollow playerResponse.
        if endpoint.startswith("reel/") and direct_first:
            pr = data.get("playerResponse")
            if isinstance(pr, dict):
                details = pr.get("videoDetails") or {}
                if not details.get("videoId") and not details.get("title"):
                    continue
            entries = data.get("entries")
            if endpoint.endswith("reel_watch_sequence") and not entries and not _reel_sequence_video_ids(data):
                continue
        return data
    return None


async def _paginate(
    first_page: Any,
    *,
    limit: int,
    continuation_endpoint: str,
    shorts: bool = False,
    max_hops: int = 8,
) -> list[dict[str, Any]]:
    """Cards from the initial tree plus InnerTube continuations up to limit."""
    cards = collect_video_cards(first_page, shorts=shorts)
    pending = find_continuation_tokens(first_page)
    hops = 0
    while pending and len(cards) < limit and hops < max_hops:
        token = pending.pop(0)
        payload = await innertube(continuation_endpoint, {"continuation": token})
        if payload is None:
            continue
        new_cards = collect_video_cards(payload, shorts=shorts)
        existing = {c["url"] for c in cards}
        added = [c for c in new_cards if c["url"] not in existing]
        hops += 1
        if not added:
            # Wrong token (shelf / related) — try the next candidate.
            for nxt in find_continuation_tokens(payload):
                if nxt not in pending:
                    pending.append(nxt)
            continue
        cards.extend(added)
        pending = find_continuation_tokens(payload) + pending
        # Dedupe pending while preserving order.
        seen_tok: set[str] = set()
        uniq: list[str] = []
        for t in pending:
            if t not in seen_tok:
                seen_tok.add(t)
                uniq.append(t)
        pending = uniq
    return cards[:limit]


async def resolve_channel_id(url: str) -> str | None:
    """Resolve ``UC…`` from a channel URL, @handle, or bare channel id."""
    raw = (url or "").strip()
    if not raw:
        return None
    if re.fullmatch(r"UC[\w-]{20,}", raw):
        return raw
    m = re.search(r"youtube\.com/channel/(UC[\w-]+)", raw)
    if m:
        return m.group(1)
    # Need a page (or redirect) for @handles / custom URLs.
    page = raw if "://" in raw else f"https://www.youtube.com/{raw.lstrip('/')}"
    data, html = await fetch_page_data(page, timeout=15.0)
    if data:
        meta = next(walk_find(data, "channelMetadataRenderer"), {}) or {}
        cid = safe_str(meta.get("externalId"))
        if cid:
            return cid
    if html:
        found = re.search(r'"externalId":"(UC[\w-]+)"', html) or re.search(
            r'"channelId":"(UC[\w-]+)"', html
        )
        if found:
            return found.group(1)
    return None


# ---------------------------------------------------------------- search ---
async def search_native_page(
    q: str,
    limit: int = 20,
    *,
    cursor: str | None = None,
    sort_by: str | None = None,
    upload_date: str | None = None,
    result_type: str | None = None,
    duration: str | None = None,
    region: str | None = None,
) -> dict[str, Any] | None:
    """One page of YouTube search results + ``nextCursor``.

    Pass ``cursor`` from a previous response to continue. Filters map to
    InnerTube ``params`` (protobuf). ``region`` sets client ``gl``.
    """
    from urllib.parse import quote

    query = (q or "").strip()
    token = (cursor or "").strip() or None
    if not query and not token:
        return {"results": [], "nextCursor": None}

    params = encode_search_params(
        sort_by=sort_by,
        upload_date=upload_date,
        result_type=result_type,
        duration=duration,
    )
    gl = (region or "").strip().upper() or None

    if token:
        data = await innertube(
            "search", {"continuation": token}, timeout=15, region=gl
        )
    else:
        body: dict[str, Any] = {"query": query}
        if params:
            body["params"] = params
        data = await innertube("search", body, timeout=15, region=gl)
        if data is None:
            # HTML fallback for first page only.
            url = f"https://www.youtube.com/results?search_query={quote(query)}"
            if params:
                url += f"&sp={quote(params)}"
            data, _ = await fetch_page_data(url)
    if data is None:
        return None

    # Shorts-filtered search uses the shorts collectors.
    shorts_mode = (result_type or "").strip().lower() in {"short", "shorts"}
    if shorts_mode:
        results = collect_video_cards(data, shorts=True)
    else:
        results = collect_search_results(data)
    results = results[: max(0, int(limit))]
    next_cursor = find_continuation_token(data)
    # Avoid returning the same cursor we just used.
    if next_cursor and token and next_cursor == token:
        next_cursor = None
    return {"results": results, "nextCursor": next_cursor}


async def search_native(q: str, limit: int) -> list[dict[str, Any]]:
    """Backward-compatible helper: first pages until ``limit`` (no cursor)."""
    page = await search_native_page(q, limit=limit)
    if not page:
        return []
    results = list(page.get("results") or [])
    token = page.get("nextCursor")
    hops = 0
    while token and len(results) < limit and hops < 8:
        nxt = await search_native_page(q, limit=limit - len(results), cursor=token)
        hops += 1
        if not nxt:
            break
        batch = nxt.get("results") or []
        if not batch:
            break
        seen = {r.get("id") or r.get("url") for r in results}
        for row in batch:
            key = row.get("id") or row.get("url")
            if key in seen:
                continue
            results.append(row)
            seen.add(key)
            if len(results) >= limit:
                break
        token = nxt.get("nextCursor")
    return results[:limit]


async def search_shorts_native(q: str, limit: int) -> list[dict[str, Any]] | None:
    """Shorts-filtered YouTube search via InnerTube, then HTML ``sp=EgIYAQ==``."""
    from urllib.parse import quote

    seed = (q or "").strip() or "trending"
    data = await innertube(
        "search", {"query": seed, "params": _SEARCH_SHORTS_PARAMS}, timeout=15
    )
    if data is not None:
        cards = await _paginate(
            data, limit=limit, continuation_endpoint="search", shorts=True
        )
        if cards:
            return cards
    data, _ = await fetch_page_data(
        f"https://www.youtube.com/results?search_query={quote(seed)}&sp=EgIYAQ%3D%3D"
    )
    if data is None:
        return None
    cards = await _paginate(data, limit=limit, continuation_endpoint="search", shorts=True)
    return cards if cards else None


def encode_reel_sequence_params(short_id: str) -> str:
    """Build InnerTube ``reel/reel_watch_sequence`` ``sequenceParams`` (youtube.js ReelSequence)."""
    vid = (short_id or "").strip()
    if len(vid) != 11:
        raise ValueError("short_id must be an 11-char YouTube video id")
    # field1=shortId, field2={number:5}, field3=25, field4=0
    inner = _pb_key(1, 0) + _pb_varint(5)
    msg = (
        _pb_key(1, 2)
        + _pb_varint(len(vid.encode()))
        + vid.encode()
        + _pb_key(2, 2)
        + _pb_varint(len(inner))
        + inner
        + _pb_key(3, 0)
        + _pb_varint(25)
        + _pb_key(4, 0)
        + _pb_varint(0)
    )
    return base64.urlsafe_b64encode(msg).decode("ascii").rstrip("=")


def _reel_sequence_video_ids(payload: dict[str, Any] | None) -> list[str]:
    if not isinstance(payload, dict):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for rw in walk_find(payload, "reelWatchEndpoint"):
        vid = safe_str(rw.get("videoId"))
        if vid and len(vid) == 11 and vid not in seen:
            seen.add(vid)
            out.append(vid)
    return out


def _reel_sequence_next_params(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    for c in walk_find(payload, "continuationCommand"):
        token = safe_str(c.get("token"))
        if token:
            return token
    return None


async def _seed_short_id_for_trending(q: str | None = None) -> str | None:
    """Pick a Short id to seed the reel sequence (homepage or optional topic)."""
    seed_q = (q or "").strip()
    if seed_q and seed_q.lower() not in {"trending", "shorts", "#shorts"}:
        found = await search_shorts_native(seed_q, 3)
        if found:
            for row in found:
                vid = safe_str(row.get("id"))
                if vid and len(vid) == 11:
                    return vid
    _, html = await fetch_page_data("https://www.youtube.com/shorts/", timeout=12.0)
    if html:
        for m in re.finditer(r"/shorts/([\w-]{11})", html):
            return m.group(1)
        for m in re.finditer(r'"videoId"\s*:\s*"([\w-]{11})"', html):
            return m.group(1)
    # Last resort: a known Shorts-eligible seed so the sequence still boots.
    fallback = await search_shorts_native("#shorts", 1)
    if fallback:
        return safe_str(fallback[0].get("id"))
    return None


async def trending_shorts_native(
    limit: int,
    *,
    q: str | None = None,
) -> list[dict[str, Any]] | None:
    """YouTube Shorts recommendation / trending reel sequence (not keyword search).

    Uses InnerTube ``reel/reel_watch_sequence`` — the same surface ScrapeCreators
    hits for ``GET /v1/youtube/shorts/trending`` (~48 per batch, fresh each call).
    Optional ``q`` only seeds the sequence from a topic Short; it is not a search
    of the word \"trending\".
    """
    seed = await _seed_short_id_for_trending(q)
    if not seed:
        return None
    try:
        params = encode_reel_sequence_params(seed)
    except ValueError:
        return None
    ids: list[str] = []
    seen: set[str] = set()
    body: dict[str, Any] = {"sequenceParams": params}
    hops = 0
    while len(ids) < limit and hops < 8:
        hops += 1
        payload = await innertube(
            "reel/reel_watch_sequence", body, timeout=18, direct_first=True
        )
        if payload is None:
            break
        for vid in _reel_sequence_video_ids(payload):
            if vid in seen:
                continue
            seen.add(vid)
            ids.append(vid)
            if len(ids) >= limit:
                break
        nxt = _reel_sequence_next_params(payload)
        if not nxt or nxt == body.get("sequenceParams"):
            break
        body = {"sequenceParams": nxt}
    if not ids:
        return None
    cards = [
        {
            "type": "short",
            "id": vid,
            "url": f"https://www.youtube.com/shorts/{vid}",
            "thumbnailUrl": thumbnail_url_for_video_id(vid),
        }
        for vid in ids[:limit]
    ]
    return await enrich_short_cards(cards)


async def short_details_via_reel_watch(video_id: str, norm_url: str) -> dict[str, Any] | None:
    """Shorts-optimized details via ``reel/reel_item_watch`` (has microformat publishDate).

    ANDROID ``player`` often omits ``playerMicroformatRenderer`` for Shorts, which
    is why shelf enrichment previously left ``publishedAt`` / ``genre`` null even
    after a successful player call. WEB reel_item_watch returns both.
    """
    vid = (video_id or "").strip()
    if len(vid) != 11:
        return None
    payload = await innertube(
        "reel/reel_item_watch",
        {"playerRequest": {"videoId": vid}, "params": "CAUwAg%3D%3D"},
        timeout=15,
        direct_first=True,
    )
    if not isinstance(payload, dict):
        return None
    player = payload.get("playerResponse")
    if not isinstance(player, dict):
        return None
    return build_youtube_video_details(
        player=player,
        video_id=vid,
        norm_url=norm_url,
        require_playable=False,
    )


def merge_short_player_details(
    android: dict[str, Any] | None,
    reel: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Prefer reel_item_watch microformat; keep ANDROID engagement when richer."""
    if not isinstance(android, dict) and not isinstance(reel, dict):
        return None
    out = dict(android or {})
    if isinstance(reel, dict):
        for key in (
            "publishedAt",
            "description",
            "descriptionLinks",
            "channelHandle",
            "channelUrl",
            "channelName",
            "channelId",
            "genre",
            "categoryId",
            "isFamilySafe",
            "defaultLanguage",
            "defaultAudioLanguage",
            "tags",
            "title",
            "availableCaptions",
            "thumbnailUrl",
            "thumbnails",
        ):
            val = reel.get(key)
            if val in (None, "", []):
                continue
            if key in (
                "publishedAt",
                "description",
                "descriptionLinks",
                "channelHandle",
                "thumbnailUrl",
                "thumbnails",
            ) or not out.get(key):
                out[key] = val
        if out.get("viewCount") is None and reel.get("viewCount") is not None:
            out["viewCount"] = reel["viewCount"]
            out["viewCountIsApproximate"] = reel.get("viewCountIsApproximate", False)
        if out.get("durationSeconds") is None and reel.get("durationSeconds") is not None:
            out["durationSeconds"] = reel["durationSeconds"]
        if out.get("likeCount") is None and reel.get("likeCount") is not None:
            out["likeCount"] = reel["likeCount"]
        if out.get("commentCount") is None and reel.get("commentCount") is not None:
            out["commentCount"] = reel["commentCount"]
            if "commentCountIsApproximate" in reel:
                out["commentCountIsApproximate"] = reel["commentCountIsApproximate"]
    if out.get("viewCount") is None and not (isinstance(reel, dict) and reel.get("title")):
        return None
    return out if out else None


def _finalize_short_list_card(vid: str, details: dict[str, Any] | None) -> dict[str, Any]:
    """Canonical Shorts list row — nested channel, no flat aliases / dead keys."""
    from app.utils.media_urls import (
        canonicalize_youtube_channel_url,
        decode_youtube_handle,
    )

    out: dict[str, Any] = {
        "id": vid,
        "url": f"https://www.youtube.com/shorts/{vid}",
        "type": "short",
    }
    if not isinstance(details, dict):
        out["thumbnailUrl"] = thumbnail_url_for_video_id(vid)
        return out

    for key in ("title", "description", "publishedAt", "genre"):
        val = details.get(key)
        if val not in (None, "", []):
            out[key] = val
    tags = details.get("tags") or details.get("keywords")
    if isinstance(tags, list) and tags:
        out["keywords"] = tags

    exact_views = safe_int(details.get("viewCount"))
    if exact_views is not None:
        out["viewCount"] = exact_views
        out["viewCountText"] = format_count_text(exact_views)
        out["viewCountIsApproximate"] = bool(details.get("viewCountIsApproximate"))

    dur = safe_int(details.get("durationSeconds"))
    if dur is not None:
        out["durationSeconds"] = dur
        out["durationFormatted"] = format_duration_hms(dur)

    thumbs, thumb_url = prefer_short_thumbnails(
        vid, details.get("thumbnails"), details.get("thumbnailUrl")
    )
    out["thumbnailUrl"] = thumb_url or thumbnail_url_for_video_id(vid)
    # List cards keep a single thumbnailUrl (not the full thumbnails[] ladder).

    handle = decode_youtube_handle(details.get("channelHandle"))
    channel_id = safe_str(details.get("channelId"))
    channel_url = canonicalize_youtube_channel_url(
        details.get("channelUrl"), channel_id=channel_id, handle=handle
    )
    channel_title = safe_str(details.get("channelName"))
    if channel_id or channel_title or handle or channel_url:
        channel: dict[str, Any] = {
            "id": channel_id,
            "title": channel_title,
            "handle": handle,
            "url": channel_url,
        }
        out["channel"] = {k: v for k, v in channel.items() if v not in (None, "")}

    if details.get("commentCount") is not None:
        cc = safe_int(details.get("commentCount"))
        if cc is not None:
            out["commentCount"] = cc
            out["commentCountText"] = format_count_text(cc)
            out["commentCountIsApproximate"] = bool(
                details.get("commentCountIsApproximate", True)
            )
    if details.get("likeCount") is not None:
        like = safe_int(details.get("likeCount"))
        if like is not None:
            out["likeCount"] = like
            out["likeCountText"] = format_count_text(like)
    return out


async def enrich_short_cards(
    cards: list[dict[str, Any]],
    *,
    concurrency: int = 8,
    with_engagement: bool = True,
) -> list[dict[str, Any]]:
    """Fill Shorts list rows via InnerTube player (SC channel/trending Shorts parity).

    Merges ``reel_item_watch`` (microformat) with ANDROID player when either is
    incomplete — some Shorts omit publishDate/handle on one path only.
    Canonical row shape: nested ``channel{}``, ``viewCount``+Text, no flat
    channel* aliases, no empty ``badges`` / ``channel.thumbnail``.
    """
    if not cards:
        return cards
    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(card: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            vid = safe_str(card.get("id"))
            if not vid and card.get("url"):
                m = re.search(r"(?:shorts/|v=)([\w-]{11})", str(card.get("url")))
                vid = m.group(1) if m else None
            if not vid:
                return card
            url = f"https://www.youtube.com/shorts/{vid}"
            reel = await short_details_via_reel_watch(vid, url)
            need_android = (
                not isinstance(reel, dict)
                or reel.get("publishedAt") is None
                or not reel.get("channelHandle")
                or not reel.get("genre")
                or is_auto_frame_still_url(reel.get("thumbnailUrl"))
            )
            android = await video_details_native(vid, url) if need_android else None
            details = merge_short_player_details(android, reel)
            if details is None and isinstance(reel, dict):
                details = reel
            if details is None and isinstance(android, dict):
                details = android

            if with_engagement and isinstance(details, dict):
                boot = await innertube("next", {"videoId": vid}, timeout=12)
                if boot is not None:
                    cc, cc_approx = _comments_total_meta(boot)
                    if cc is not None:
                        details["commentCount"] = cc
                        details["commentCountIsApproximate"] = cc_approx
                    like = None
                    for btn in walk_find(boot, "toggleButtonRenderer"):
                        a11y = (
                            ((btn.get("defaultText") or {}).get("accessibility") or {}).get(
                                "accessibilityData"
                            )
                            or {}
                        )
                        label = text_of(a11y) or text_of(btn.get("defaultText")) or ""
                        if "like" in label.lower():
                            like = parse_count_text(label)
                            if like is not None:
                                break
                    if like is None:
                        for vm in walk_find(boot, "likeButtonViewModel"):
                            like = parse_count_text(vm.get("likeCountEntity")) or parse_count_text(
                                vm
                            )
                            if like is not None:
                                break
                    if like is not None:
                        details["likeCount"] = like

            return _finalize_short_list_card(vid, details)

    return list(await asyncio.gather(*[_one(c) for c in cards]))


async def enrich_video_cards(
    cards: list[dict[str, Any]],
    *,
    concurrency: int = 6,
) -> list[dict[str, Any]]:
    """Player-enrich long-form / stream list rows (exact views, ISO publishedAt).

    Same dual-field pattern as ``enrich_short_cards`` but uses the watch player
    (not reel_item_watch). Preserves card ``type`` (video|stream|upcoming|live).
    """
    if not cards:
        return cards
    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(card: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            vid = safe_str(card.get("id"))
            if not vid and card.get("url"):
                m = re.search(r"(?:shorts/|v=|youtu\.be/)([\w-]{11})", str(card.get("url")))
                vid = m.group(1) if m else None
            if not vid:
                return card
            url = safe_str(card.get("url")) or f"https://www.youtube.com/watch?v={vid}"
            out = {**card, "id": vid, "url": url}
            out["thumbnailUrl"] = out.get("thumbnailUrl") or thumbnail_url_for_video_id(vid)
            details = await video_details_native(vid, url)
            if not isinstance(details, dict):
                return coerce_published_fields(out)
            exact_views = safe_int(details.get("viewCount"))
            if exact_views is not None:
                _stamp_count_fields(out, count=exact_views, approximate=False)
                out.pop("viewCountApproximate", None)
            for src, dest in (
                ("title", "title"),
                ("description", "description"),
                ("publishedAt", "publishedAt"),
                ("durationSeconds", "durationSeconds"),
                ("channelName", "channelName"),
                ("channelId", "channelId"),
                ("channelHandle", "channelHandle"),
                ("channelUrl", "channelUrl"),
                ("thumbnailUrl", "thumbnailUrl"),
            ):
                val = details.get(src)
                if val not in (None, "", []):
                    out[dest] = val
            if out.get("channelId") or out.get("channelName"):
                out["channel"] = {
                    "id": out.get("channelId"),
                    "title": out.get("channelName"),
                    "handle": out.get("channelHandle"),
                    "url": out.get("channelUrl"),
                    "thumbnail": None,
                }
            # Keep relative label when player only gave ISO.
            if out.get("publishedAt") and not out.get("publishedTimeText"):
                _, rel = published_fields(card.get("publishedTimeText") or card.get("publishedAt"))
                if rel:
                    out["publishedTimeText"] = rel
            return coerce_published_fields(out)

    return list(await asyncio.gather(*[_one(c) for c in cards]))


async def channel_has_live_tab(channel_url: str) -> bool:
    """True when the channel exposes a Live / Streams tab.

    YouTube accepts the streams browse ``params`` even when the tab is missing
    and silently returns Videos/Home content (MrBeast). Gate on the tab list.
    """
    base = (channel_url or "").strip().rstrip("/")
    for suffix in (
        "/videos",
        "/shorts",
        "/streams",
        "/live",
        "/playlists",
        "/featured",
        "/posts",
        "/community",
        "/about",
    ):
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)]
            break
    data, _ = await fetch_page_data(base or channel_url, timeout=12.0)
    if data is None:
        return False
    for tab in walk_find(data, "tabRenderer"):
        title = (text_of(tab.get("title")) or safe_str(tab.get("title")) or "").strip().lower()
        if title in {"live", "streams", "livestreams"}:
            return True
    return False


# ---------------------------------------------------------------- playlist -
def _playlist_total_videos(data: Any, header: dict[str, Any] | None) -> int | None:
    """Playlist size from header / sidebar stats (not the page slice length)."""
    candidates: list[Any] = []
    if isinstance(header, dict):
        candidates.extend(
            [
                header.get("numVideosText"),
                header.get("numVideos"),
            ]
        )
        for byline in header.get("byline") or []:
            if isinstance(byline, dict):
                pbr = byline.get("playlistBylineRenderer") or {}
                candidates.append(pbr.get("text"))
        for key in ("stats", "briefStats"):
            stats = header.get(key)
            if isinstance(stats, list) and stats:
                candidates.append(stats[0])
    for side in walk_find(data, "playlistSidebarPrimaryInfoRenderer"):
        for key in ("stats", "briefStats"):
            stats = side.get(key)
            if isinstance(stats, list) and stats:
                candidates.append(stats[0])
        candidates.append(side.get("statsText"))
    for cand in candidates:
        n = parse_count_text(cand)
        if n is not None and n >= 0:
            return n
    # Fallback: scan "98 videos" style strings near the header.
    blob = json.dumps(header or {}, ensure_ascii=False)
    m = re.search(r"([\d,.]+)\s+videos?", blob, re.I)
    if m:
        return safe_int(m.group(1).replace(",", ""))
    return None


def _playlist_owner(data: Any, header: dict[str, Any] | None) -> dict[str, Any]:
    owner_node = None
    if isinstance(header, dict):
        owner_node = header.get("ownerText")
    if owner_node is None:
        for side in walk_find(data, "playlistSidebarSecondaryInfoRenderer"):
            vor = ((side.get("videoOwner") or {}).get("videoOwnerRenderer")) or {}
            owner_node = vor.get("title")
            if owner_node:
                break
    channel = _channel_from_text_runs(owner_node) if owner_node else {
        "id": None,
        "title": None,
        "handle": None,
        "url": None,
        "thumbnail": None,
    }
    # Normalize to SC-like owner{id,name,url,handle}; keep title alias.
    name = channel.get("title")
    return {
        "id": channel.get("id"),
        "name": name,
        "title": name,
        "url": channel.get("url")
        or (f"https://www.youtube.com/channel/{channel['id']}" if channel.get("id") else None),
        "handle": channel.get("handle"),
    }


async def playlist_native(url: str, limit: int) -> dict[str, Any] | None:
    """Videos (plus title/owner/totalVideos) straight from a /playlist page."""
    data, _ = await fetch_page_data(url)
    if data is None:
        return None
    videos = await _paginate(data, limit=limit, continuation_endpoint="browse")
    if not videos:
        return None

    title = None
    header: dict[str, Any] | None = None
    for meta in walk_find(data, "playlistMetadataRenderer"):
        title = safe_str(meta.get("title"))
        break
    for hdr in walk_find(data, "playlistHeaderRenderer"):
        header = hdr
        title = title or text_of(hdr.get("title"))
        break

    owner = _playlist_owner(data, header)
    channel_name = owner.get("name")
    if not channel_name:
        channel_name = videos[0].get("channelName")
        owner["name"] = channel_name
        owner["title"] = channel_name

    playlist_id = None
    m = re.search(r"[?&]list=([\w-]+)", url or "")
    if m:
        playlist_id = m.group(1)
    if not playlist_id and isinstance(header, dict):
        playlist_id = safe_str(header.get("playlistId"))

    total_videos = _playlist_total_videos(data, header)
    # Drop empty nested channel thumbs on video cards for a leaner payload.
    for vid in videos:
        coerce_published_fields(vid)
        ch = vid.get("channel")
        if isinstance(ch, dict):
            vid["channel"] = {k: v for k, v in ch.items() if v is not None}
            if not vid["channel"]:
                vid.pop("channel", None)
        if vid.get("publishedTimeText") is None:
            vid.pop("publishedTimeText", None)

    return {
        "id": playlist_id,
        "title": title,
        "channelName": channel_name,
        "owner": {k: v for k, v in owner.items() if v is not None},
        "totalVideos": total_videos,
        "videos": videos,
    }


# ---------------------------------------------------- channel tab lists ---
def _channel_title_from_data(data: Any) -> str | None:
    """Channel display name from browse / channel-page ytInitialData."""
    if not data:
        return None
    meta = next(walk_find(data, "channelMetadataRenderer"), None) or {}
    title = safe_str(meta.get("title"))
    if title:
        return title
    # pageHeaderViewModel.title.dynamicTextViewModel.text.content
    for ph in walk_find(data, "pageHeaderViewModel"):
        dyn = ((ph.get("title") or {}).get("dynamicTextViewModel") or {}).get("text")
        title = safe_str(text_of(dyn))
        if title:
            return title
    return None


def _fill_missing_channel_name(
    cards: list[dict[str, Any]], channel_name: str | None
) -> list[dict[str, Any]]:
    """Channel tabs omit byline; stamp the owning channel onto each card."""
    if not channel_name:
        return cards
    for card in cards:
        if not card.get("channelName"):
            card["channelName"] = channel_name
    return cards


def _coerce_card_dates(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for card in cards:
        coerce_published_fields(card)
    return cards


async def channel_tab_native(
    tab_url: str,
    limit: int,
    *,
    shorts: bool = False,
    tab: str | None = None,
) -> list[dict[str, Any]]:
    """Videos / streams / shorts tab of a channel.

    Prefers InnerTube ``browse`` with known tab ``params`` (works when the
    HTML tab is 429'd). Falls back to ``ytInitialData`` on the tab URL.
    """
    tab_key = (tab or "").strip().lower()
    if not tab_key:
        low = (tab_url or "").rstrip("/").lower()
        for name in ("shorts", "streams", "videos", "playlists"):
            if low.endswith("/" + name):
                tab_key = name
                break
    params = _CHANNEL_TAB_PARAMS.get(tab_key) if tab_key else None
    if params:
        channel_id = await resolve_channel_id(tab_url)
        if channel_id:
            data = await innertube(
                "browse",
                {"browseId": channel_id, "params": params},
                timeout=18,
            )
            if data is not None:
                cards = await _paginate(
                    data, limit=limit, continuation_endpoint="browse", shorts=shorts
                )
                if cards:
                    return _coerce_card_dates(
                        _fill_missing_channel_name(
                            cards, _channel_title_from_data(data)
                        )
                    )
    data, _ = await fetch_page_data(tab_url, timeout=15.0)
    if data is None:
        return []
    cards = await _paginate(data, limit=limit, continuation_endpoint="browse", shorts=shorts)
    return _coerce_card_dates(
        _fill_missing_channel_name(cards, _channel_title_from_data(data))
    )


def collect_playlist_cards(data: Any) -> list[dict[str, Any]]:
    """``LOCKUP_CONTENT_TYPE_PLAYLIST`` rows from a channel playlists tab."""
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for lk in walk_find(data, "lockupViewModel"):
        if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_PLAYLIST":
            continue
        pid = safe_str(lk.get("contentId"))
        if not pid or pid in seen:
            continue
        seen.add(pid)
        meta = (lk.get("metadata") or {}).get("lockupMetadataViewModel") or {}
        title = text_of(meta.get("title")) or ""
        video_count = None
        for badge in walk_find(lk, "thumbnailBadgeViewModel"):
            video_count = parse_count_text(badge.get("text"))
            if video_count is not None:
                break
        if video_count is None:
            blob = json.dumps(lk)
            m = re.search(r"([\d,.]+)\s+videos?", blob)
            if m:
                video_count = safe_int(m.group(1).replace(",", ""))
        rows.append(
            {
                "id": pid,
                "url": f"https://www.youtube.com/playlist?list={pid}",
                "title": title,
                "videoCount": video_count,
                "thumbnailUrl": _best_thumb(lk.get("contentImage")),
            }
        )
    return rows


async def channel_playlists_native(channel_url: str, limit: int) -> list[dict[str, Any]]:
    """Channel playlists via InnerTube browse, then HTML tab parse."""
    if limit <= 0:
        return []
    channel_id = await resolve_channel_id(channel_url)
    params = _CHANNEL_TAB_PARAMS["playlists"]
    if channel_id:
        data = await innertube(
            "browse",
            {"browseId": channel_id, "params": params},
            timeout=18,
        )
        if data is not None:
            rows = collect_playlist_cards(data)
            if rows:
                return rows[:limit]
    # HTML fallthrough (proxy-aware).
    base = (channel_url or "").rstrip("/")
    for suffix in (
        "/videos",
        "/shorts",
        "/streams",
        "/playlists",
        "/featured",
        "/posts",
        "/community",
    ):
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)]
            break
    data, _ = await fetch_page_data(f"{base}/playlists", timeout=15.0)
    if data is None:
        return []
    return collect_playlist_cards(data)[:limit]


# ---------------------------------------------------------------- hashtag --
async def hashtag_native(tag: str, limit: int) -> list[dict[str, Any]]:
    from urllib.parse import quote

    name = (tag or "").lstrip("#").strip()
    if not name:
        return []
    data, _ = await fetch_page_data(f"https://www.youtube.com/hashtag/{quote(name)}")
    if data is None:
        return []
    return _coerce_card_dates(
        await _paginate(data, limit=limit, continuation_endpoint="browse")
    )


# --------------------------------------------------------- channel details --
_ABOUT_PARAMS = _CHANNEL_TAB_PARAMS["about"]


async def channel_details_native(url: str) -> dict[str, Any] | None:
    """Channel metadata from the channel page + the About popup (InnerTube)."""
    data, html = await fetch_page_data(url)
    if not html:
        return None

    meta: dict[str, Any] = {}
    if data:
        meta = next(walk_find(data, "channelMetadataRenderer"), {}) or {}
    channel_id = safe_str(meta.get("externalId"))
    if not channel_id:
        m = re.search(r'"externalId":"(UC[\w-]+)"', html) or re.search(r'"channelId":"(UC[\w-]+)"', html)
        channel_id = m.group(1) if m else None
    if not channel_id:
        return None

    name = safe_str(meta.get("title"))
    description = safe_str(meta.get("description"))
    avatar = _best_thumb(meta.get("avatar"))
    vanity = safe_str(meta.get("vanityChannelUrl"))
    handle = None
    if vanity and "@" in vanity:
        handle = "@" + vanity.split("@", 1)[1]

    subscriber_count = None
    subscriber_count_is_approximate = False
    video_count = None
    banner = _channel_banner_url(data, avatar=avatar) if data else None
    if data:
        page_blob = json.dumps(data, ensure_ascii=False)
        header_html = json.dumps(data.get("header") or {}, ensure_ascii=False)
        m = re.search(r"([\d.,]+[KMB]?) subscribers", header_html) or re.search(
            r"([\d.,]+[KMB]?) subscribers", page_blob
        )
        if m:
            subscriber_count, subscriber_count_is_approximate = parse_count_text_meta(
                m.group(1)
            )
        m = re.search(r"([\d.,]+[KMB]?) videos?", header_html) or re.search(
            r"([\d.,]+[KMB]?) videos?", page_blob
        )
        if m:
            video_count = parse_count_text(m.group(1))

    # About popup: exact view count, joined date, country, links.
    view_count = None
    joined = None
    country = None
    links: list[dict[str, str]] = []
    # Channel page metadata also embeds primaryLinks (often present when the
    # About popup returns an empty links array).
    for link in meta.get("primaryLinks") or []:
        if not isinstance(link, dict):
            continue
        nav = link.get("navigationEndpoint") or {}
        link_url = safe_str(
            (nav.get("urlEndpoint") or {}).get("url")
            or (nav.get("commandMetadata") or {}).get("webCommandMetadata", {}).get("url")
        )
        # YouTube wraps external URLs in a redirector — unwrap when present.
        if link_url and "q=" in link_url and "youtube.com/redirect" in link_url:
            q = parse_qs(urlparse(link_url).query).get("q") or []
            if q:
                link_url = q[0]
        link_url = _absolute_http_url(link_url)
        link_title = text_of(link.get("title"))
        if link_url:
            links.append({"text": safe_str(link_title) or "", "url": link_url})
    # About fields: InnerTube about-tab params often return the main channel
    # browse without aboutChannelViewModel. Prefer that when present, else
    # fetch /about (ytInitialData still embeds the about view model).
    about: dict[str, Any] | None = None
    about_payload = await innertube(
        "browse", {"browseId": channel_id, "params": _ABOUT_PARAMS}
    )
    if about_payload:
        about = next(walk_find(about_payload, "aboutChannelViewModel"), None)
    if about is None:
        about_data, about_html = await fetch_page_data(
            f"https://www.youtube.com/channel/{channel_id}/about",
            timeout=15,
        )
        if about_data:
            about = next(walk_find(about_data, "aboutChannelViewModel"), None)
        if about is None and about_html:
            html = about_html  # use /about HTML for regex fallbacks below

    if about:
        view_count = parse_count_text(about.get("viewCountText"))
        joined = safe_str(text_of(about.get("joinedDateText")))
        if joined:
            joined = re.sub(r"^joined\s+", "", joined, flags=re.I).strip() or joined
        country = safe_str(text_of(about.get("country"))) or safe_str(about.get("country"))
        if subscriber_count is None:
            subscriber_count, subscriber_count_is_approximate = parse_count_text_meta(
                about.get("subscriberCountText")
            )
        if video_count is None:
            video_count = parse_count_text(about.get("videoCountText"))
        if not description:
            description = safe_str(text_of(about.get("description")))
        about_links: list[dict[str, str]] = []
        for link in about.get("links") or []:
            view_model = link.get("channelExternalLinkViewModel") or {}
            link_title = text_of(view_model.get("title"))
            link_url = _absolute_http_url(text_of(view_model.get("link")))
            if link_url:
                about_links.append({"text": safe_str(link_title) or "", "url": link_url})
        if about_links:
            links = about_links

    # Last-resort fallbacks from page HTML / metadata JSON.
    if view_count is None:
        m = re.search(r"([\d.,]+[KMB]?)\s+views", html, re.I)
        if m:
            view_count = parse_count_text(m.group(1))
    if country is None:
        country = safe_str(meta.get("country")) or None
        if country is None:
            m = re.search(r'"country"\s*:\s*"([^"]+)"', html)
            if m:
                country = safe_str(m.group(1))
    if joined is None:
        m = re.search(r"Joined\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", html)
        if m:
            joined = safe_str(m.group(1))
        else:
            m = re.search(
                r'"joinedDateText"\s*:\s*\{\s*"content"\s*:\s*"Joined\s+([^"]+)"',
                html,
            ) or re.search(
                r'"joinedDateText"[^}]*?"simpleText"\s*:\s*"Joined\s+([^"]+)"',
                html,
            )
            if m:
                joined = safe_str(m.group(1))

    if not links:
        links = _links_from_html(html)
    else:
        # Ensure scheme even when About returned bare hosts.
        links = [
            {"text": row.get("text") or "", "url": _absolute_http_url(row.get("url")) or ""}
            for row in links
            if row.get("url")
        ]

    verified = None
    if data:
        header_blob = json.dumps(data.get("header") or {})
        verified = "CHECK_CIRCLE" in header_blob or '"BADGE_STYLE_TYPE_VERIFIED"' in header_blob

    # SEO keywords from channelMetadataRenderer (space-separated; multi-word in quotes).
    tags = _channel_tags(meta.get("keywords"))
    if not tags and html:
        m = re.search(r'"keywords"\s*:\s*"((?:\\.|[^"\\])*)"', html)
        if m:
            raw_kw = bytes(m.group(1), "utf-8").decode("unicode_escape")
            tags = _channel_tags(raw_kw)

    # Business email when the creator put it in the About/description text or
    # a mailto: link. YouTube's CAPTCHA "View email address" reveal is not scraped.
    email = _email_from_texts(description, *(link.get("url") for link in links))
    if email is None and html:
        email = _email_from_texts(html[:200_000])

    country_code = country_code_from_name(country)
    country_display = country_name(country_code) if country_code else safe_str(country)
    joined_at = _parse_joined_at(joined)
    canonical = (
        f"https://www.youtube.com/{handle}"
        if handle
        else f"https://www.youtube.com/channel/{channel_id}"
    )

    return {
        "platform": "youtube",
        "url": f"https://www.youtube.com/channel/{channel_id}",
        "canonicalUrl": canonical,
        "id": channel_id,
        "name": name or "",
        "handle": handle,
        "description": description,
        "subscriberCount": subscriber_count,
        "subscriberCountIsApproximate": (
            bool(subscriber_count_is_approximate)
            if subscriber_count is not None
            else None
        ),
        "videoCount": video_count,
        "viewCount": view_count,
        "thumbnailUrl": avatar,
        "bannerUrl": banner,
        "country": country_code,
        "countryName": country_display,
        "joinedAt": joined_at,
        "joinedDate": joined,
        "verified": verified,
        "links": links,
        "email": email,
        "tags": tags,
    }


_EMAIL_RE = re.compile(
    r"(?:mailto:)?([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})",
    re.I,
)
# Skip obvious non-contact noise from page chrome / tracking.
_EMAIL_BLOCKLIST = {
    "noreply@",
    "no-reply@",
    "donotreply@",
    "@youtube.com",
    "@google.com",
    "@sentry.io",
    "@example.com",
}


def _channel_tags(raw: Any) -> list[str]:
    """Normalize channel SEO keywords to a clean string list.

    YouTube stores keywords as one space-separated string where multi-word tags
    are double-quoted (``"medical facts" neuroscience``). Naive ``.split()``
    leaves quote characters and splits those groups — use a quote-aware tokenizer.
    """
    if raw is None:
        return []
    if isinstance(raw, list):
        out: list[str] = []
        for item in raw:
            s = safe_str(item)
            if s:
                out.append(s.strip().strip('"').strip("'"))
        return [t for t in out if t]
    text = safe_str(raw) or ""
    if not text:
        return []
    # Comma-separated (rare) — treat commas as separators first.
    if "," in text and '"' not in text:
        return [p.strip() for p in re.split(r"\s*,\s*", text) if p.strip()]
    try:
        parts = shlex.split(text)
    except ValueError:
        parts = text.split()
    return [p.strip().strip('"').strip("'") for p in parts if p and p.strip().strip('"').strip("'")]


def _absolute_http_url(url: str | None) -> str | None:
    """Ensure external / relative YouTube link values are absolute https URLs."""
    raw = safe_str(url)
    if not raw:
        return None
    if raw.startswith("//"):
        return f"https:{raw}"
    if re.match(r"^https?://", raw, re.I):
        return raw
    if raw.startswith("/"):
        return f"https://www.youtube.com{raw}"
    # Bare host/path from About (instagram.com/foo) — assume https.
    return f"https://{raw.lstrip('/')}"


def _yt_image_file_id(url: str | None) -> str | None:
    raw = safe_str(url) or ""
    m = re.search(r"/([A-Za-z0-9_-]{16,})=", raw)
    return m.group(1) if m else None


def _looks_like_avatar_thumb(url: str | None) -> bool:
    """Avatar CDN params look like ``=s160-c-k-c0x00ffffff-no-rj``."""
    raw = safe_str(url) or ""
    return bool(re.search(r"=s\d+-c-k-c0x00ffffff", raw, re.I))


def _channel_banner_url(data: dict[str, Any], *, avatar: str | None) -> str | None:
    """Real channel banner — never fall back to the avatar thumbnail.

    Prefer ``c4TabbedHeaderRenderer.banner|tvBanner|mobileBanner``, then
    ``pageHeaderViewModel.banner.imageBannerViewModel.image``.
    """
    header = data.get("header") if isinstance(data.get("header"), dict) else {}
    avatar_id = _yt_image_file_id(avatar)

    def _accept(url: str | None) -> str | None:
        if not url:
            return None
        if avatar_id and _yt_image_file_id(url) == avatar_id:
            return None
        if _looks_like_avatar_thumb(url):
            return None
        return url

    c4 = header.get("c4TabbedHeaderRenderer")
    if isinstance(c4, dict):
        for key in ("banner", "tvBanner", "mobileBanner"):
            got = _accept(_best_thumb(c4.get(key)))
            if got:
                return got

    page_header = header.get("pageHeaderRenderer")
    if isinstance(page_header, dict):
        content = page_header.get("content") if isinstance(page_header.get("content"), dict) else {}
        vm = content.get("pageHeaderViewModel") if isinstance(content.get("pageHeaderViewModel"), dict) else {}
        banner_wrap = vm.get("banner") if isinstance(vm.get("banner"), dict) else {}
        image_vm = banner_wrap.get("imageBannerViewModel") or banner_wrap
        if isinstance(image_vm, dict):
            got = _accept(_best_thumb(image_vm.get("image") or image_vm))
            if got:
                return got

    # Named banner keys only — never recurse the whole header (avatars live there).
    for key in ("tvBanner", "banner", "mobileBanner"):
        for node in walk_find(header, key):
            got = _accept(_best_thumb(node))
            if got:
                return got
    return None


_JOINED_DATE_FORMATS = (
    "%b %d, %Y",  # Jul 31, 2017
    "%B %d, %Y",  # July 31, 2017
    "%d %b %Y",  # 31 Jul 2017
    "%d %B %Y",  # 31 July 2017
)


def _parse_joined_at(joined: str | None) -> str | None:
    """Parse About ``joinedDateText`` (English) → ``YYYY-MM-DD``."""
    text = safe_str(joined)
    if not text:
        return None
    cleaned = re.sub(r"^joined\s+", "", text, flags=re.I).strip()
    # Already ISO.
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cleaned):
        return cleaned
    for fmt in _JOINED_DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _email_from_texts(*texts: Any) -> str | None:
    """First plausible contact email from description / mailto links."""
    for text in texts:
        if not text or not isinstance(text, str):
            continue
        for m in _EMAIL_RE.finditer(text):
            addr = (m.group(1) or "").strip().lower()
            if not addr or len(addr) > 120:
                continue
            if any(bad in addr for bad in _EMAIL_BLOCKLIST):
                continue
            return addr
    return None


_SOCIAL_LINK_RE = re.compile(
    r"https?://(?:www\.)?"
    r"(instagram\.com|twitter\.com|x\.com|facebook\.com|tiktok\.com|twitch\.tv|"
    r"linkedin\.com|discord\.gg|discord\.com)"
    r"/[^\s\"'<>\\]+",
    re.I,
)
_SOCIAL_LABELS = {
    "instagram.com": "Instagram",
    "twitter.com": "Twitter",
    "x.com": "Twitter",
    "facebook.com": "Facebook",
    "tiktok.com": "TikTok",
    "twitch.tv": "Twitch",
    "linkedin.com": "LinkedIn",
    "discord.gg": "Discord",
    "discord.com": "Discord",
}


def _links_from_html(html: str) -> list[dict[str, str]]:
    """Fallback social links from channel HTML when About/primaryLinks are empty."""
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for m in _SOCIAL_LINK_RE.finditer(html or ""):
        raw = m.group(0).rstrip(").,];")
        host = m.group(1).lower()
        # Dedupe by host so description noise doesn't flood the list.
        if host in seen:
            continue
        seen.add(host)
        out.append({"text": _SOCIAL_LABELS.get(host, host), "url": _absolute_http_url(raw) or raw})
    return out


# ------------------------------------------------------------- transcript --
# Caption URLs served on the web watch page require a proof-of-origin token
# since ~2025 and return empty bodies to plain HTTP clients. The ANDROID
# InnerTube client still hands out working (signed) timedtext URLs.
# Keep this on a version that still returns captionTracks (newer clients 400).
_ANDROID_CLIENT_VERSION = "20.10.38"
_ANDROID_CONTEXT = {
    "client": {
        "clientName": "ANDROID",
        "clientVersion": _ANDROID_CLIENT_VERSION,
        "androidSdkVersion": 30,
        "hl": "en",
        "gl": "US",
    }
}
_ANDROID_HEADERS = {
    "User-Agent": (
        f"com.google.android.youtube/{_ANDROID_CLIENT_VERSION} "
        "(Linux; U; Android 11) gzip"
    ),
    "X-Youtube-Client-Name": "3",
    "X-Youtube-Client-Version": _ANDROID_CLIENT_VERSION,
}


async def _player_innertube(
    video_id: str,
    *,
    context: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, str | None]:
    """InnerTube ``player`` across tiers (direct → DC → residential).

    Returns ``(player, tier)``. Skips ``LOGIN_REQUIRED`` / empty-caption bot
    walls so a later tier can still succeed.
    """
    fallback: tuple[dict[str, Any], str] | None = None
    for tier in _player_tiers():
        try:
            resp = await post_json(
                "https://www.youtube.com/youtubei/v1/player",
                {
                    "context": context,
                    "videoId": video_id,
                    "contentCheckOk": True,
                    "racyCheckOk": True,
                },
                tier=tier,  # type: ignore[arg-type]
                headers=headers,
                params={"prettyPrint": "false"},
                timeout=15,
            )
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        try:
            data = resp.json()
        except ValueError:
            continue
        if not isinstance(data, dict) or not data:
            continue
        status = ((data.get("playabilityStatus") or {}).get("status") or "").upper()
        tracks = _caption_tracks(data) if status == "OK" else []
        if status == "OK" and tracks:
            return data, tier
        if status == "OK" and fallback is None:
            fallback = (data, tier)
        # LOGIN_REQUIRED / ERROR: keep trying other egress IPs.
    if fallback:
        return fallback
    return None, None


async def _player_android(video_id: str) -> dict[str, Any] | None:
    player, _tier = await _player_innertube(
        video_id, context=_ANDROID_CONTEXT, headers=_ANDROID_HEADERS
    )
    return player


async def _player_android_with_tier(
    video_id: str,
) -> tuple[dict[str, Any] | None, str | None]:
    return await _player_innertube(
        video_id, context=_ANDROID_CONTEXT, headers=_ANDROID_HEADERS
    )


def _parse_timedtext(body: str) -> list[dict[str, Any]]:
    """Parse a timedtext payload: json3 events or srv3 XML ``<p t= d=>``."""
    stripped = body.strip()
    segments: list[dict[str, Any]] = []
    if stripped.startswith("{"):
        try:
            payload = json.loads(stripped)
        except ValueError:
            return []
        for ev in payload.get("events") or []:
            segs = ev.get("segs")
            if not segs:
                continue
            text = "".join(s.get("utf8") or "" for s in segs).replace("\n", " ").strip()
            if not text:
                continue
            segments.append(
                {
                    "text": text,
                    "start": float(ev.get("tStartMs") or 0) / 1000.0,
                    "duration": float(ev.get("dDurationMs") or 0) / 1000.0,
                }
            )
        return segments
    try:
        root = ET.fromstring(stripped)
    except ET.ParseError:
        return []
    for p in root.iter("p"):
        text = "".join(p.itertext()).replace("\n", " ").strip()
        if not text:
            continue
        segments.append(
            {
                "text": text,
                "start": float(p.get("t") or 0) / 1000.0,
                "duration": float(p.get("d") or 0) / 1000.0,
            }
        )
    return segments


def _with_timedtext_fmt(url: str, fmt: str) -> str:
    if not url:
        return url
    if re.search(r"[?&]fmt=", url):
        return re.sub(r"([?&])fmt=[^&]*", rf"\1fmt={fmt}", url)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}fmt={fmt}"


async def _fetch_timedtext(
    base_url: str,
    *,
    headers: dict[str, str],
    prefer_tier: str | None = None,
) -> list[dict[str, Any]]:
    """GET a caption URL across proxy tiers and fmt variants.

    Prefer the same egress that produced the player response — caption
    ``baseUrl`` tokens can be sensitive to IP changes.
    """
    tiers = list(_player_tiers())
    if prefer_tier:
        tiers = [prefer_tier] + [t for t in tiers if t != prefer_tier]
    for fmt in ("json3", "srv3"):
        url = _with_timedtext_fmt(base_url, fmt)
        for tier in tiers:
            try:
                cap = await proxy_fetch(url, tier=tier, headers=headers, timeout=15)  # type: ignore[arg-type]
            except httpx.HTTPError:
                continue
            if cap.status_code >= 400 or not (cap.text or "").strip():
                continue
            segments = _parse_timedtext(cap.text)
            if segments:
                return segments
    return []


def _caption_tracks(player: dict[str, Any]) -> list[dict[str, Any]]:
    return list(
        ((player.get("captions") or {}).get("playerCaptionsTracklistRenderer") or {}).get(
            "captionTracks"
        )
        or []
    )


def _caption_track_name(track: dict[str, Any]) -> str | None:
    """Human language label for a caption track.

    ANDROID player payloads often omit ``name.simpleText`` (runs-only or empty),
    so fall back to resolving ``languageCode`` → English name (en → English).
    """
    from app.utils.formatters import language_name_from_code

    name = track.get("name")
    if isinstance(name, dict):
        got = (
            safe_str(name.get("simpleText") or name.get("content"))
            or text_of(name)
        )
    else:
        got = safe_str(name)
    if got:
        return got
    return language_name_from_code(safe_str(track.get("languageCode")))


def _available_caption_languages(tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for t in tracks:
        code = safe_str(t.get("languageCode"))
        if not code:
            continue
        is_asr = t.get("kind") == "asr"
        # Keep manual + ASR tracks for the same language as separate options.
        key = f"{code}:{'asr' if is_asr else 'manual'}"
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "languageCode": code,
                "languageName": _caption_track_name(t),
                "isAutoGenerated": is_asr,
            }
        )
    return out


def _rank_caption_tracks(
    tracks: list[dict[str, Any]], language: str | None
) -> list[dict[str, Any]]:
    def score(t: dict[str, Any]) -> tuple[int, int]:
        code = (t.get("languageCode") or "").lower()
        is_asr = 1 if t.get("kind") == "asr" else 0
        if language:
            want = language.lower()[:2]
            match = 0 if code.startswith(want) else 1
        else:
            match = 0 if code.startswith("en") else 1
        return (match, is_asr)

    return sorted(tracks, key=score)


async def transcript_native(norm_url: str, language: str | None) -> dict[str, Any] | None:
    """Transcript via InnerTube ANDROID caption tracks (timedtext).

    Tries every caption track (lang-ranked) and fmt=json3/srv3 across egress
    tiers (direct first — proxy IPs often trip YouTube bot-check) before
    giving up so callers hit Apify less often.
    """
    m = re.search(r"(?:v=|shorts/|youtu\.be/)([\w-]{11})", norm_url)
    if not m:
        return None
    video_id = m.group(1)

    player, player_tier = await _player_android_with_tier(video_id)
    if not player:
        return None
    if ((player.get("playabilityStatus") or {}).get("status")) != "OK":
        return None
    tracks = _caption_tracks(player)
    if not tracks:
        return None

    available = _available_caption_languages(tracks)
    ranked = _rank_caption_tracks(tracks, language)
    attempts: list[tuple[dict[str, Any], bool]] = [(t, False) for t in ranked]
    if language:
        want = language.lower()[:2]
        if not any((t.get("languageCode") or "").lower().startswith(want) for t in ranked):
            attempts.append((ranked[0], True))

    for track, use_tlang in attempts:
        base_url = safe_str(track.get("baseUrl"))
        if not base_url:
            continue
        url = f"{base_url}&tlang={language}" if use_tlang and language else base_url
        segments = await _fetch_timedtext(
            url, headers=_ANDROID_HEADERS, prefer_tier=player_tier
        )
        if not segments:
            continue
        title = safe_str((player.get("videoDetails") or {}).get("title"))
        return {
            "segments": segments,
            "title": title,
            "language": safe_str(
                language if use_tlang else (track.get("languageCode") or language)
            ),
            "isAutoGenerated": track.get("kind") == "asr",
            "isTranslated": bool(use_tlang),
            "availableLanguages": available,
        }
    return None



# ---------------------------------------------------------- video details --
def _youtube_thumbnails(thumbs: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for t in thumbs:
        if not isinstance(t, dict):
            continue
        url = safe_str(t.get("url"))
        if not url:
            continue
        out.append(
            {
                "url": url,
                "width": safe_int(t.get("width")),
                "height": safe_int(t.get("height")),
            }
        )
    return out


_AUTO_FRAME2_THUMB_RE = re.compile(
    r"/(?:mq|hq|sd|maxres)?2\.(?:jpg|webp)(?:\?|$)",
    re.I,
)


def is_auto_frame_still_url(url: str | None) -> bool:
    """True for YouTube auto storyboard stills (``2.jpg`` / ``mq2.jpg`` / …)."""
    return bool(url and _AUTO_FRAME2_THUMB_RE.search(url))


def prefer_short_thumbnails(
    video_id: str,
    thumbs: list[Any] | None,
    thumbnail_url: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    """Prefer vertical / channel-set covers over landscape frame-2 stills."""
    cleaned = _youtube_thumbnails(thumbs if isinstance(thumbs, list) else [])
    vertical = [
        t
        for t in cleaned
        if (t.get("height") or 0) > (t.get("width") or 0)
    ]
    if vertical:
        return vertical, safe_str(vertical[-1].get("url")) or thumbnail_url
    non_frame2 = [t for t in cleaned if not is_auto_frame_still_url(t.get("url"))]
    if non_frame2:
        return non_frame2, safe_str(non_frame2[-1].get("url")) or thumbnail_url
    if cleaned and not all(is_auto_frame_still_url(t.get("url")) for t in cleaned):
        return cleaned, safe_str(cleaned[-1].get("url")) or thumbnail_url
    # Player only shipped frame-2 landscape stills — fall back to stable covers.
    vid = (video_id or "").strip()
    if len(vid) == 11:
        synth = [
            {
                "url": f"https://i.ytimg.com/vi/{vid}/oardefault.jpg",
                "width": None,
                "height": None,
            },
            {
                "url": f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
                "width": 1280,
                "height": 720,
            },
        ]
        return synth, synth[0]["url"]
    return cleaned, thumbnail_url or (cleaned[-1]["url"] if cleaned else None)


def _youtube_available_captions(player: dict[str, Any]) -> list[dict[str, Any]]:
    from app.utils.media_urls import cdn_expires_at

    out: list[dict[str, Any]] = []
    for t in _caption_tracks(player):
        if not isinstance(t, dict):
            continue
        code = safe_str(t.get("languageCode"))
        if not code:
            continue
        base_url = safe_str(t.get("baseUrl"))
        row: dict[str, Any] = {
            "languageCode": code,
            "languageName": _caption_track_name(t),
            "kind": safe_str(t.get("kind")) or "standard",
            "baseUrl": base_url,
            "expiresAt": cdn_expires_at(base_url),
        }
        out.append(row)
    return out


def build_youtube_video_details(
    *,
    player: dict[str, Any],
    video_id: str,
    norm_url: str,
    like_count: int | None = None,
    comment_count: int | None = None,
    fetched_at: str | None = None,
    require_playable: bool = True,
) -> dict[str, Any] | None:
    """Normalize an InnerTube player payload into the public video-details shape."""
    from app.utils.media_urls import (
        canonicalize_youtube_channel_url,
        channel_handle_from_profile_url,
        decode_youtube_handle,
        description_links,
        live_status_from_youtube,
        utc_now_iso,
    )

    status = ((player.get("playabilityStatus") or {}).get("status")) or ""
    details = player.get("videoDetails") or {}
    # reel/reel_item_watch often returns UNPLAYABLE ("reload page") while still
    # shipping full videoDetails + microformat — enough for list enrichment.
    if require_playable and status != "OK":
        return None
    if not details.get("title"):
        return None
    micro = (player.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    thumbs = (details.get("thumbnail") or {}).get("thumbnails") or []
    thumbnails = _youtube_thumbnails(thumbs if isinstance(thumbs, list) else [])
    channel_id = safe_str(details.get("channelId"))
    length = details.get("lengthSeconds") or micro.get("lengthSeconds")
    try:
        duration_seconds = int(length) if length is not None else None
    except (TypeError, ValueError):
        duration_seconds = None
    if duration_seconds is None:
        approx = details.get("approxDurationMs") or micro.get("approxDurationMs")
        try:
            duration_seconds = int(int(approx) / 1000) if approx is not None else None
        except (TypeError, ValueError):
            duration_seconds = None

    owner_profile = safe_str(micro.get("ownerProfileUrl"))
    channel_handle = decode_youtube_handle(
        channel_handle_from_profile_url(owner_profile)
    )
    channel_url = canonicalize_youtube_channel_url(
        owner_profile, channel_id=channel_id, handle=channel_handle
    )
    live_status = live_status_from_youtube(details)
    # Shorts hard-cap is 180s. Prefer YouTube's isShortsEligible; also treat
    # /shorts/ URLs and classic ≤60s watch links as Shorts when in range.
    is_short = False
    if duration_seconds is None or duration_seconds <= 180:
        is_short = bool(
            details.get("isShortsEligible")
            or "/shorts/" in (norm_url or "")
            or (duration_seconds is not None and duration_seconds <= 60)
        )
    if live_status == "live":
        content_type = "live"
    elif is_short:
        content_type = "short"
    else:
        content_type = "video"

    playability = player.get("playabilityStatus") or {}
    reason = (safe_str(playability.get("reason")) or "").lower()
    is_members_only = "members" in reason or "member" in reason
    live_broadcast = micro.get("liveBroadcastDetails")
    if not isinstance(live_broadcast, dict):
        live_broadcast = details.get("liveBroadcastDetails")
    if not isinstance(live_broadcast, dict):
        live_broadcast = {}

    description = safe_str(details.get("shortDescription"))
    if is_short and thumbnails:
        thumbnails, best_thumb = prefer_short_thumbnails(video_id, thumbnails)
    else:
        best_thumb = thumbnails[-1]["url"] if thumbnails else None
    out: dict[str, Any] = {
        "platform": "youtube",
        "url": norm_url,
        "id": video_id,
        "title": safe_str(details.get("title")) or "",
        "description": description,
        "descriptionLinks": description_links(description),
        "channelName": safe_str(details.get("author") or micro.get("ownerChannelName")),
        "channelId": channel_id,
        "channelHandle": channel_handle,
        "channelUrl": channel_url,
        "publishedAt": safe_str(micro.get("publishDate") or micro.get("uploadDate")),
        "durationSeconds": duration_seconds,
        "viewCount": safe_int(details.get("viewCount")),
        "likeCount": like_count,
        "commentCount": comment_count,
        "thumbnailUrl": best_thumb,
        "thumbnails": thumbnails,
        "genre": safe_str(micro.get("category")),
        "categoryId": safe_str(details.get("categoryId") or micro.get("categoryId")),
        "tags": safe_list(details.get("keywords")),
        "contentType": content_type,
        "isShort": is_short,
        "liveStatus": live_status,
        "scheduledStartTime": safe_str(live_broadcast.get("startTimestamp")),
        "actualStartTime": safe_str(live_broadcast.get("actualStartTime")),
        "concurrentViewers": safe_int(details.get("concurrentViewers")),
        "defaultLanguage": safe_str(details.get("defaultLanguage")),
        "defaultAudioLanguage": safe_str(details.get("defaultAudioLanguage")),
        "isFamilySafe": None if micro.get("isFamilySafe") is None else bool(micro.get("isFamilySafe")),
        "isPrivate": bool(details.get("isPrivate")),
        "isUnlisted": bool(details.get("isUnlisted")),
        "isAgeRestricted": bool(
            details.get("isCrawlable") is False
            or "age" in reason
            or playability.get("desktopLegacyAgeGateReason") is not None
        ),
        "isMembersOnly": is_members_only,
        "availableCaptions": _youtube_available_captions(player),
        "chapters": [],  # filled later via InnerTube next when available
        "fetchedAt": fetched_at or utc_now_iso(),
        "viewCountIsApproximate": False,
    }
    if duration_seconds is not None:
        out["durationFormatted"] = format_duration_hms(duration_seconds)
    return out


async def video_details_native(video_id: str, norm_url: str) -> dict[str, Any] | None:
    """Metadata/stats via InnerTube ANDROID player (watch HTML is often 429)."""
    player = await _player_android(video_id)
    if not player:
        return None
    return build_youtube_video_details(player=player, video_id=video_id, norm_url=norm_url)

# --------------------------------------------------------------- comments --
def _comment_author_avatar(author: dict[str, Any]) -> str | None:
    direct = safe_str(author.get("avatarThumbnailUrl") or author.get("avatarUrl"))
    if direct:
        return direct
    # Newer InnerTube nests avatars under avatar.image.sources[].
    avatar = author.get("avatar") if isinstance(author.get("avatar"), dict) else {}
    image = avatar.get("image") if isinstance(avatar.get("image"), dict) else {}
    sources = image.get("sources") if isinstance(image.get("sources"), list) else []
    if sources and isinstance(sources[0], dict):
        return safe_str(sources[0].get("url"))
    thumbs = author.get("thumbnails") if isinstance(author.get("thumbnails"), list) else []
    if thumbs and isinstance(thumbs[0], dict):
        return safe_str(thumbs[0].get("url"))
    return _best_thumb(author.get("avatar")) or _best_thumb(author.get("thumbnail"))


def _comment_author_channel_id(author: dict[str, Any]) -> str | None:
    for key in ("channelId", "externalChannelId", "browseId"):
        v = safe_str(author.get(key))
        if v and (v.startswith("UC") or len(v) >= 18):
            return v
    for nest_key in ("channelCommand", "frameworkUpdates", "navigationEndpoint"):
        nest = author.get(nest_key)
        if not isinstance(nest, dict):
            continue
        browse = (
            ((nest.get("innertubeCommand") or {}).get("browseEndpoint") or {})
            if nest_key == "channelCommand"
            else (nest.get("browseEndpoint") or {})
        )
        if not isinstance(browse, dict):
            browse = ((nest.get("command") or {}).get("browseEndpoint") or {})
        v = safe_str(browse.get("browseId"))
        if v and v.startswith("UC"):
            return v
    channel_url = safe_str(author.get("channelUrl") or author.get("canonicalBaseUrl"))
    if channel_url and "/channel/" in channel_url:
        return channel_url.rstrip("/").split("/channel/")[-1] or None
    return None


def _comment_published_time(props: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return (publishedTimeText, publishedTime ISO or None)."""
    text = text_of(props.get("publishedTime")) or safe_str(props.get("publishedTimeText"))
    iso: str | None = None
    for key in (
        "publishedTimeSeconds",
        "publishedTimestamp",
        "timestamp",
        "createTime",
        "publishedAt",
    ):
        raw = props.get(key)
        if isinstance(raw, str) and "T" in raw and ("Z" in raw or "+" in raw):
            iso = raw
            break
        ts = safe_int(raw)
        if ts and ts > 1_000_000_000:
            iso = datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.000Z"
            )
            break
    if iso is None and text:
        # Strip YouTube's "(edited)" suffix before approximating ISO.
        clean = re.sub(r"\s*\(edited\)\s*$", "", text, flags=re.I).strip()
        iso = approximate_iso_from_relative(clean)
    return text, iso


def _has_creator_heart(toolbar: dict[str, Any]) -> bool:
    """True only when the creator actually hearted the comment.

    YouTube ships ``heartActiveTooltip`` like ``❤ by @Channel`` on *every*
    unhearted comment (Rickroll replies: 5/5 tooltips, 0 ``creatorHeart``).
    Never treat a non-empty tooltip alone as hearted — that was the 10/10-true bug.
    """
    if toolbar.get("isHeartedByCreator") is True:
        return True
    heart = toolbar.get("creatorHeart")
    if isinstance(heart, dict) and heart:
        # Real hearts carry a renderer/view-model with creator identity — not an
        # empty shell or tracking-only object.
        renderer = (
            heart.get("creatorHeartRenderer")
            or heart.get("creatorHeartViewModel")
            or heart.get("heartedCreatorHeartViewModel")
        )
        if isinstance(renderer, dict) and (
            renderer.get("creatorThumbnail")
            or renderer.get("creatorThumbnailEndpoint")
            or renderer.get("creatorName")
            or next(walk_find(renderer, "thumbnail"), None) is not None
        ):
            return True
    tip = toolbar.get("heartActiveTooltip")
    if not isinstance(tip, str):
        tip = text_of(tip) or ""
    t = tip.strip().lower()
    if not t:
        return False
    # Reject inactive chrome: "❤ by @Channel" / "heart by @…" without past tense.
    if re.fullmatch(r"[❤❤️♥]\s*by\s+@?\S+", t) or re.fullmatch(r"by\s+@?\S+", t):
        return False
    return any(
        needle in t
        for needle in (
            "hearted by",
            "hearts this",
            "loved by the creator",
            "loved by creator",
            "creator hearted",
            "hearted this comment",
        )
    )


def _comment_payload_to_api(p: dict[str, Any]) -> dict[str, Any] | None:
    props = p.get("properties") or {}
    author = p.get("author") or {}
    toolbar = p.get("toolbar") or {}
    if not isinstance(author, dict):
        author = {}
    if not isinstance(toolbar, dict):
        toolbar = {}
    if not isinstance(props, dict):
        props = {}
    cid = safe_str(props.get("commentId"))
    text = text_of(props.get("content"))
    if not cid or text is None:
        return None
    like_count = parse_count_text(toolbar.get("likeCountLiked") or toolbar.get("likeCountNotliked") or toolbar.get("likeCountA11y"))
    published_text, published_iso = _comment_published_time(props)
    return {
        "id": cid,
        "author": safe_str(author.get("displayName")),
        "authorChannelId": _comment_author_channel_id(author),
        "authorAvatarUrl": _comment_author_avatar(author),
        "authorIsVerified": bool(author.get("isVerified")),
        "authorIsChannelOwner": bool(author.get("isCreator")),
        "text": text.strip(),
        "likeCount": like_count,
        "replyCount": safe_int(toolbar.get("replyCount")) or parse_count_text(toolbar.get("replyCountA11y")),
        "hasCreatorHeart": _has_creator_heart(toolbar),
        "publishedTimeText": published_text,
        "publishedTime": published_iso,
    }


def _comment_payloads(data: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for payload in walk_find(data, "commentEntityPayload"):
        row = _comment_payload_to_api(payload)
        if row and row["id"] not in seen:
            seen.add(row["id"])
            rows.append(row)
    return rows


def _comments_section_token(data: Any) -> str | None:
    """Pick the comments-section continuation token, not the watch-next feed."""
    first = None
    for c in walk_find(data, "continuationCommand"):
        token = safe_str(c.get("token"))
        if token and first is None:
            first = token
        if token and "comments-section" in token:
            return token
    return first


def _comments_total_meta(data: Any) -> tuple[int | None, bool]:
    """Best-effort total from comments header / engagement panel.

    Returns ``(count, approximate)`` — approximate when the source used K/M/B.
    """
    for header in walk_find(data, "commentsHeaderRenderer"):
        for key in ("countText", "commentsCount", "headerText"):
            n, approx = parse_count_text_meta(text_of(header.get(key)))
            if n is not None:
                return n, approx
    # Current InnerTube ``next`` shape: engagementPanelTitleHeaderRenderer
    # with title "Comments" and contextualInfo like "2.4M" / "10M".
    for header in walk_find(data, "engagementPanelTitleHeaderRenderer"):
        title = (text_of(header.get("title")) or "").strip().lower()
        if title and title not in ("comments", "comment"):
            continue
        for key in ("contextualInfo", "subtitle", "countText", "headerText"):
            n, approx = parse_count_text_meta(text_of(header.get(key)))
            if n is not None:
                return n, approx
    return None, False


def _comments_total(data: Any) -> int | None:
    n, _approx = _comments_total_meta(data)
    return n


async def comment_count_native_meta(video_id: str) -> tuple[int | None, bool]:
    """Resolve comment count + approximate flag via InnerTube ``next``."""
    if not video_id:
        return None, False
    boot = await innertube("next", {"videoId": video_id}, timeout=15)
    if boot is None:
        return None, False
    return _comments_total_meta(boot)


async def comment_count_native(video_id: str) -> int | None:
    """Resolve comment count via InnerTube ``next`` engagement panel."""
    n, _approx = await comment_count_native_meta(video_id)
    return n


async def _comments_entry_token(norm_url: str) -> tuple[str | None, int | None]:
    """Resolve the comments-section continuation + optional total.

    Prefer InnerTube ``next`` with ``videoId`` — watch-page HTML is frequently
    429'd on datacenter IPs. Fall back to ytInitialData when needed.
    """
    # Lazy import avoids a circular dependency with app.utils.url.
    from app.utils.url import extract_youtube_id

    vid = extract_youtube_id(norm_url)
    if vid:
        boot = await innertube("next", {"videoId": vid}, timeout=15)
        if boot is not None:
            token = _comments_section_token(boot)
            if token:
                return token, _comments_total(boot)

    data, _ = await fetch_page_data(norm_url, timeout=12)
    if data is None:
        return None, None
    return _comments_section_token(data), _comments_total(data)


async def comments_native(
    norm_url: str,
    limit: int,
    *,
    cursor: str | None = None,
) -> dict[str, Any] | None:
    """Top-level comments via InnerTube continuation tokens.

    Pass ``cursor`` (previous ``nextCursor``) to fetch the next page. Without a
    cursor we bootstrap via InnerTube ``next`` (videoId), not the watch HTML.
    """
    token = cursor or None
    total_comments: int | None = None
    if not token:
        token, total_comments = await _comments_entry_token(norm_url)
    if not token:
        return None

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    # ~20 comments per InnerTube hop; keep a small buffer for empty pages.
    max_hops = max(8, (limit // 15) + 3)
    hops = 0
    while token and len(rows) < limit and hops < max_hops:
        payload = await innertube("next", {"continuation": token}, timeout=15)
        if payload is None:
            break
        if total_comments is None:
            total_comments = _comments_total(payload)
        for row in _comment_payloads(payload):
            if row["id"] not in seen:
                seen.add(row["id"])
                rows.append(row)
                if len(rows) >= limit:
                    break
        token = find_continuation_token(payload)
        hops += 1

    if not rows:
        return None
    next_cursor = token if token else None
    return {
        "comments": rows[:limit],
        "totalComments": total_comments,
        "nextCursor": next_cursor,
    }


def _reply_continuation_for_thread(thread: dict[str, Any], comment_id: str) -> str | None:
    vm = (((thread.get("commentViewModel") or {}).get("commentViewModel")) or {})
    if safe_str(vm.get("commentId")) != comment_id:
        return None
    replies = thread.get("replies") or {}
    return find_continuation_token(replies)


async def comment_replies_native(norm_url: str, comment_id: str, limit: int) -> list[dict[str, Any]]:
    """Paginate reply continuations for ``comment_id`` (no hard ~20 cap)."""
    token, _ = await _comments_entry_token(norm_url)
    if not token:
        return []

    reply_token = None
    hops = 0
    while token and not reply_token and hops < 6:
        payload = await innertube("next", {"continuation": token}, timeout=15)
        if payload is None:
            break
        for thread in walk_find(payload, "commentThreadRenderer"):
            reply_token = _reply_continuation_for_thread(thread, comment_id)
            if reply_token:
                break
        token = find_continuation_token(payload)
        hops += 1

    if not reply_token:
        return []

    replies: list[dict[str, Any]] = []
    seen: set[str] = set()
    token = reply_token
    max_hops = max(8, (limit // 15) + 3)
    hops = 0
    while token and len(replies) < limit and hops < max_hops:
        payload = await innertube("next", {"continuation": token}, timeout=15)
        if payload is None:
            break
        for row in _comment_payloads(payload):
            rid = row["id"]
            if rid in seen:
                continue
            seen.add(rid)
            row["replyToId"] = comment_id
            replies.append(row)
            if len(replies) >= limit:
                break
        token = find_continuation_token(payload)
        hops += 1
    return replies[:limit]


# --------------------------------------------------------- community posts --
def _channel_from_community_post(post: dict[str, Any]) -> dict[str, Any]:
    """``channel{id,title,url,handle}`` from authorEndpoint / authorText."""
    channel = _channel_from_text_runs(post.get("authorText"))
    browse = ((post.get("authorEndpoint") or {}).get("browseEndpoint")) or {}
    if isinstance(browse, dict):
        cid = safe_str(browse.get("browseId"))
        if cid:
            channel["id"] = cid
        base = safe_str(browse.get("canonicalBaseUrl"))
        if base:
            channel["url"] = (
                f"https://www.youtube.com{base}" if base.startswith("/") else base
            )
            if base.startswith("/@"):
                channel["handle"] = base[1:]
    if not channel.get("title"):
        channel["title"] = text_of(post.get("authorText"))
    return {
        "id": channel.get("id"),
        "title": channel.get("title"),
        "url": channel.get("url"),
        "handle": channel.get("handle"),
    }


def _video_from_community_renderer(vr: dict[str, Any]) -> dict[str, Any] | None:
    """Linked video card — id, display + numeric views, length."""
    if not isinstance(vr, dict):
        return None
    vid = safe_str(vr.get("videoId"))
    if not vid:
        watch = ((vr.get("navigationEndpoint") or {}).get("watchEndpoint")) or {}
        vid = safe_str(watch.get("videoId")) if isinstance(watch, dict) else None
    if not vid:
        return None
    view_text = text_of(vr.get("viewCountText") or vr.get("shortViewCountText"))
    view_int, _approx = parse_count_text_meta(view_text)
    length_text = text_of(vr.get("lengthText"))
    length_secs = _duration_text_seconds(vr.get("lengthText"))
    if length_secs is None:
        raw_secs = safe_str(vr.get("lengthSeconds"))
        if raw_secs and raw_secs.isdigit():
            length_secs = int(raw_secs)
    thumb = _best_thumb(vr.get("thumbnail"))
    return {
        "id": vid,
        "title": text_of(vr.get("title")),
        "thumbnail": thumb,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "viewCountText": view_text,
        "viewCountInt": view_int,
        "lengthText": length_text,
        "lengthSeconds": length_secs,
    }


def _poll_from_attachment(attachment: Any) -> dict[str, Any] | None:
    """Extract poll options (+ totalVotes when YouTube exposes them).

    Public HTML/InnerTube often omits per-choice vote counts until the viewer
    is signed in — in that case ``voteCount`` / ``percentage`` are null but
    option ``text`` and ``totalVotes`` still return.
    """
    if not isinstance(attachment, dict):
        return None
    poll = next(walk_find(attachment, "pollRenderer"), None)
    if not isinstance(poll, dict):
        return None
    options: list[dict[str, Any]] = []
    for choice in poll.get("choices") or []:
        if not isinstance(choice, dict):
            continue
        label = text_of(choice.get("text"))
        if not label:
            continue
        vote_text = text_of(choice.get("voteCount") or choice.get("numVotes"))
        pct_raw = choice.get("votePercentage") or choice.get("percentage")
        pct: float | None = None
        if isinstance(pct_raw, (int, float)):
            pct = float(pct_raw)
        elif isinstance(pct_raw, str):
            try:
                pct = float(pct_raw.replace("%", "").strip())
            except ValueError:
                pct = None
        vote_n = parse_count_text(vote_text) if vote_text else safe_int(choice.get("numVotes"))
        options.append(
            {
                "text": label,
                "voteCount": vote_n,
                "percentage": pct,
            }
        )
    if not options:
        return None
    total_text = text_of(poll.get("totalVotes"))
    total_n, total_approx = parse_count_text_meta(total_text)
    out: dict[str, Any] = {
        "pollOptions": options,
        "totalVotes": total_n,
        "totalVotesText": total_text,
    }
    if total_approx:
        out["totalVotesApproximate"] = True
    return out


def _normalize_community_post(post: dict[str, Any]) -> dict[str, Any] | None:
    """Shape matching ``/v1/youtube/community-posts`` list items."""
    if not isinstance(post, dict):
        return None
    post_id = safe_str(post.get("postId"))
    if not post_id:
        return None
    text = text_of(post.get("contentText")) or ""
    images: list[str] = []
    linked: list[dict[str, Any]] = []
    post_type = "text"
    attachment = post.get("backstageAttachment") or {}
    for renderer in walk_find(attachment, "backstageImageRenderer"):
        url = _best_thumb({"thumbnails": ((renderer.get("image") or {}).get("thumbnails") or [])})
        if not url:
            thumbs = (renderer.get("image") or {}).get("thumbnails") or []
            if thumbs and isinstance(thumbs[-1], dict):
                url = safe_str(thumbs[-1].get("url"))
        if url:
            if url.startswith("//"):
                url = "https:" + url
            images.append(url)
            post_type = "image"
    poll_meta = _poll_from_attachment(attachment)
    if poll_meta:
        post_type = "poll"
    elif next(walk_find(attachment, "quizRenderer"), None) is not None:
        post_type = "quiz"
    elif next(walk_find(attachment, "playlistRenderer"), None) is not None or next(
        walk_find(attachment, "compactPlaylistRenderer"), None
    ) is not None:
        post_type = "playlist"
    for key in (
        "videoRenderer",
        "compactVideoRenderer",
        "gridVideoRenderer",
        "videoAttachmentPostRenderer",
        "backstageVideoRenderer",
    ):
        for vr in walk_find(attachment, key):
            video = _video_from_community_renderer(vr)
            if not video:
                continue
            # Keep videoId for older clients; mirror SC-style fields too.
            linked.append(
                {
                    "videoId": video["id"],
                    "id": video["id"],
                    "url": video["url"],
                    "title": video.get("title"),
                    "thumbnail": video.get("thumbnail"),
                    "viewCountText": video.get("viewCountText"),
                    "viewCountInt": video.get("viewCountInt"),
                    "lengthText": video.get("lengthText"),
                    "lengthSeconds": video.get("lengthSeconds"),
                }
            )
            # Poll/quiz/playlist type wins over a linked video card.
            if post_type in {"text", "image"}:
                post_type = "video"
    # Deduplicate images / videos while preserving order.
    seen_img: set[str] = set()
    uniq_images: list[str] = []
    for img in images:
        if img not in seen_img:
            seen_img.add(img)
            uniq_images.append(img)
    seen_vid: set[str] = set()
    uniq_linked: list[dict[str, Any]] = []
    for row in linked:
        vid = row.get("id") or row.get("videoId")
        if not vid or vid in seen_vid:
            continue
        seen_vid.add(vid)
        uniq_linked.append(row)
    hashtags = re.findall(r"#(\w+)", text)
    like_text = text_of(post.get("voteCount"))
    like_count, like_approx = parse_count_text_meta(like_text)
    published_iso, published_text = published_fields(post.get("publishedTimeText"))
    channel = _channel_from_community_post(post)
    source_url = f"https://www.youtube.com/post/{post_id}"
    primary_video = None
    if uniq_linked:
        first = uniq_linked[0]
        primary_video = {
            "id": first.get("id"),
            "title": first.get("title"),
            "thumbnail": first.get("thumbnail"),
            "url": first.get("url"),
            "viewCountText": first.get("viewCountText"),
            "viewCountInt": first.get("viewCountInt"),
            "lengthText": first.get("lengthText"),
            "lengthSeconds": first.get("lengthSeconds"),
        }
    out: dict[str, Any] = {
        "id": post_id,
        "url": source_url,
        "author": channel.get("title") or text_of(post.get("authorText")),
        "channel": channel,
        "text": text.strip(),
        "likeCount": like_count,
        "likeCountText": like_text,
        "hashtags": hashtags,
        "linkedVideos": uniq_linked,
        "video": primary_video,
        # publishedTime is ISO-8601 (approx from relative labels); keep the
        # YouTube UI string separately — same dual-field pattern as playlist.
        "publishedTime": published_iso,
        "publishedTimeText": published_text,
        # Alias used by /community-post-details docs historically.
        "publishedAt": published_iso,
        "postType": post_type,
        "images": uniq_images,
        "image": uniq_images[0] if uniq_images else None,
        "sourceUrl": source_url,
    }
    if like_approx:
        out["likeCountApproximate"] = True
    if poll_meta:
        out.update(poll_meta)
    return out


def _collect_community_posts(data: Any) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in walk_find(data, "backstagePostRenderer"):
        item = _normalize_community_post(raw)
        if not item:
            continue
        pid = item["id"]
        if pid in seen:
            continue
        seen.add(pid)
        posts.append(item)
    return posts


def _posts_tab_url(channel_url: str) -> str:
    base = (channel_url or "").strip().rstrip("/")
    # Strip existing tab suffixes.
    for suffix in ("/posts", "/community", "/videos", "/shorts", "/streams", "/playlists", "/about"):
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}/posts"


async def community_posts_native(
    channel_url: str,
    limit: int = 20,
    *,
    cursor: str | None = None,
) -> dict[str, Any] | None:
    """Channel community posts from the public ``/posts`` tab + continuations.

    Returns ``{posts, nextCursor}``. Pass ``cursor`` (previous ``nextCursor``)
    to page; without a cursor we bootstrap from the public ``/posts`` HTML.
    """
    capped = max(1, min(int(limit or 20), 200))
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    token: str | None = (cursor or "").strip() or None

    if not token:
        tab = _posts_tab_url(channel_url)
        data, _ = await fetch_page_data(tab)
        if data is None:
            return None
        for item in _collect_community_posts(data):
            if item["id"] in seen:
                continue
            seen.add(item["id"])
            posts.append(item)
            if len(posts) >= capped:
                break
        token = find_continuation_token(data)

    hops = 0
    max_hops = max(8, (capped // 10) + 3)
    while token and len(posts) < capped and hops < max_hops:
        payload = await innertube("browse", {"continuation": token})
        if payload is None:
            token = None
            break
        added = [p for p in _collect_community_posts(payload) if p["id"] not in seen]
        token = find_continuation_token(payload)
        hops += 1
        if not added:
            # Empty page but another continuation may still yield posts.
            if not token:
                break
            continue
        for item in added:
            seen.add(item["id"])
            posts.append(item)
            if len(posts) >= capped:
                break

    if not posts:
        return None
    next_cursor = token if token else None
    return {
        "posts": posts[:capped],
        "nextCursor": next_cursor,
    }

