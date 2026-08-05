"""Helpers for media URL expiry and description link extraction."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


_KWAI_TAG_TS_RE = re.compile(r"^\d+-(\d{10,})(?:-|$)")


def cdn_expires_at(url: str | None) -> str | None:
    """Parse signed CDN expiry (``x-expires`` / ``expire`` / Kwai ``tag=``)."""
    if not url:
        return None
    try:
        qs = parse_qs(urlparse(url).query)
    except Exception:
        return None
    for key in ("x-expires", "expire", "expires", "e"):
        raw = (qs.get(key) or [None])[0]
        if not raw:
            continue
        try:
            ts = int(raw)
        except (TypeError, ValueError):
            continue
        # Prefer unix seconds; ignore tiny / non-epoch values.
        if ts < 1_000_000_000:
            continue
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    # Kwai / Kuaishou: tag=1-{unix}-s-0-{nonce}-{sig}
    tag = (qs.get("tag") or [None])[0]
    if tag:
        m = _KWAI_TAG_TS_RE.match(str(tag))
        if m:
            try:
                ts = int(m.group(1))
            except (TypeError, ValueError):
                ts = 0
            if ts >= 1_000_000_000:
                return datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.000Z"
                )
    return None


def earliest_cdn_expires_at(*urls: str | None) -> str | None:
    stamps = [cdn_expires_at(u) for u in urls if u]
    stamps = [s for s in stamps if s]
    return min(stamps) if stamps else None


def description_links(text: str | None) -> list[dict[str, str]]:
    if not text:
        return []
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for m in _URL_RE.finditer(text):
        url = m.group(0).rstrip(").,;]'\"")
        if url in seen:
            continue
        seen.add(url)
        out.append({"url": url})
    return out


def decode_youtube_handle(handle: str | None) -> str | None:
    """Normalize ``@handle`` text — percent-decode (Cyrillic etc.), keep leading @."""
    from urllib.parse import unquote

    raw = (handle or "").strip()
    if not raw:
        return None
    if raw.startswith("@"):
        body = unquote(raw[1:])
    else:
        body = unquote(raw)
    body = (body or "").strip()
    if not body or body.startswith("channel") or "/" in body:
        return None
    return f"@{body}"


def channel_handle_from_profile_url(profile_url: str | None) -> str | None:
    if not profile_url:
        return None
    from urllib.parse import unquote

    path = urlparse(profile_url).path.strip("/")
    if not path:
        return None
    part = unquote(path.split("/")[0])
    if part in {"channel", "c", "user"}:
        return None
    return decode_youtube_handle(part)


def canonicalize_youtube_channel_url(
    url: str | None = None,
    *,
    channel_id: str | None = None,
    handle: str | None = None,
) -> str | None:
    """Force ``https://www.youtube.com/@handle`` or ``/channel/UC…`` — never ``http://``."""
    h = decode_youtube_handle(handle) or channel_handle_from_profile_url(url)
    if h:
        return f"https://www.youtube.com/{h}"
    cid = (channel_id or "").strip()
    if cid.startswith("UC"):
        return f"https://www.youtube.com/channel/{cid}"
    raw = (url or "").strip()
    if not raw:
        return None
    if raw.startswith("//"):
        raw = "https:" + raw
    elif raw.startswith("http://"):
        raw = "https://" + raw[len("http://") :]
    elif not raw.startswith("https://") and "youtube." in raw:
        raw = "https://" + raw.lstrip("/")
    parsed = urlparse(raw)
    host = (parsed.netloc or "").lower().removeprefix("www.")
    if host.endswith("youtube.com") or host == "youtu.be":
        path = (parsed.path or "").rstrip("/")
        if "/channel/" in path:
            cid_part = path.split("/channel/", 1)[-1].split("/")[0]
            if cid_part.startswith("UC"):
                return f"https://www.youtube.com/channel/{cid_part}"
        h2 = channel_handle_from_profile_url(raw)
        if h2:
            return f"https://www.youtube.com/{h2}"
        if path:
            return f"https://www.youtube.com{path}"
    return raw.split("?")[0] or None


def live_status_from_youtube(details: dict[str, Any]) -> str:
    if details.get("isLive") or details.get("isLiveNow"):
        return "live"
    if details.get("isUpcoming"):
        return "upcoming"
    if details.get("isLiveContent"):
        return "ended"
    return "none"
