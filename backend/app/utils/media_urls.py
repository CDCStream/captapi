"""Helpers for media URL expiry and description link extraction."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def cdn_expires_at(url: str | None) -> str | None:
    """Parse TikTok/YouTube-style signed URL expiry (``x-expires`` / ``expire``)."""
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


def channel_handle_from_profile_url(profile_url: str | None) -> str | None:
    if not profile_url:
        return None
    path = urlparse(profile_url).path.strip("/")
    if not path:
        return None
    part = path.split("/")[0]
    if part.startswith("@"):
        return part
    if part.startswith("channel") or part.startswith("c/") or part.startswith("user"):
        return None
    return f"@{part}" if part else None


def live_status_from_youtube(details: dict[str, Any]) -> str:
    if details.get("isLive") or details.get("isLiveNow"):
        return "live"
    if details.get("isUpcoming"):
        return "upcoming"
    if details.get("isLiveContent"):
        return "ended"
    return "none"
