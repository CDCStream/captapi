"""Helpers for media URL expiry and description link extraction."""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


_KWAI_TAG_TS_RE = re.compile(r"^\d+-(\d{10,})(?:-|$)")


def _iso_from_unix(ts: int | float) -> str | None:
    try:
        n = float(ts)
    except (TypeError, ValueError):
        return None
    if n < 1_000_000_000:
        return None
    if n > 1e12:  # ms
        n /= 1000.0
    try:
        return datetime.fromtimestamp(n, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    except (OverflowError, OSError, ValueError):
        return None


def jwt_exp_iso(token: str | None) -> str | None:
    """Decode a JWT payload ``exp`` claim → ISO-8601 UTC (no verify)."""
    raw = (token or "").strip()
    if not raw or raw.count(".") < 2:
        return None
    seg = raw.split(".")[1]
    pad = "=" * (-len(seg) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(seg + pad))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    exp = data.get("exp")
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        return _iso_from_unix(exp)
    return None


def _jwt_exp_from_url(url: str) -> str | None:
    """Find a JWT in query values or path segments and read ``exp``."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    qs = parse_qs(parsed.query)
    for values in qs.values():
        for v in values:
            text = str(v)
            if "eyJ" not in text:
                continue
            m = _JWT_RE.search(text)
            got = jwt_exp_iso(m.group(0) if m else text)
            if got:
                return got
    for seg in (parsed.path or "").split("/"):
        if "eyJ" not in seg:
            continue
        m = _JWT_RE.search(seg)
        got = jwt_exp_iso(m.group(0) if m else seg)
        if got:
            return got
    m = _JWT_RE.search(url)
    return jwt_exp_iso(m.group(0)) if m else None


def cdn_expires_at(url: str | None) -> str | None:
    """Parse signed CDN expiry (query params, Kwai ``tag=``, or JWT ``exp``)."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
    except Exception:
        return None
    # Case-insensitive: Google CDN uses ``Expires``, others ``expire`` / ``e``.
    lowered = {str(k).lower(): v for k, v in qs.items()}
    for key in ("x-expires", "expire", "expires", "e"):
        raw = (lowered.get(key) or [None])[0]
        if not raw:
            continue
        try:
            ts = int(raw)
        except (TypeError, ValueError):
            continue
        got = _iso_from_unix(ts)
        if got:
            return got
    # Kwai / Kuaishou: tag=1-{unix}-s-0-{nonce}-{sig}
    tag = (qs.get("tag") or [None])[0]
    if tag:
        m = _KWAI_TAG_TS_RE.match(str(tag))
        if m:
            try:
                ts = int(m.group(1))
            except (TypeError, ValueError):
                ts = 0
            got = _iso_from_unix(ts)
            if got:
                return got
    # Rumble channel-videos: signed playback URLs carry expiry in JWT ``exp``.
    return _jwt_exp_from_url(url)


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
