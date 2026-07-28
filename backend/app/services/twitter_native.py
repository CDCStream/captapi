"""Native Twitter/X lookups without Apify.

``cdn.syndication.twimg.com/tweet-result`` powers embedded tweets (text, author,
likes, replies, media). Public profile pages embed schema.org microdata
(``ProfilePage`` / ``Person`` + interaction counters) that a plain GET — or
Decodo when datacenter IPs are login-walled — can parse for follower / tweet
stats.
"""

from __future__ import annotations

import math
import re
from html import unescape
from typing import Any
from urllib.parse import urlparse

import httpx
import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

_UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
_BASE = "https://cdn.syndication.twimg.com/tweet-result"
_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"
_META_RE = re.compile(
    r"<meta[^>]+>",
    re.I,
)
_PROP_CONTENT_RE = re.compile(
    r"""itemprop=["']([^"']+)["'][^>]*content=["']([^"']*)["']"""
    r"|"
    r"""content=["']([^"']*)["'][^>]*itemprop=["']([^"']+)["']""",
    re.I,
)
_INTERACTION_RE = re.compile(
    r"""interactionType[^>]*content=["']([^"']+)["']"""
    r"""[\s\S]{0,400}?"""
    r"""userInteractionCount[^>]*content=["']([^"']+)["']""",
    re.I,
)
_IMAGE_URL_RE = re.compile(
    r"""itemprop=["'](?:contentUrl|thumbnailUrl|image)["'][^>]*content=["']([^"']+)["']"""
    r"|"
    r"""content=["']([^"']+)["'][^>]*itemprop=["'](?:contentUrl|thumbnailUrl|image)["']""",
    re.I,
)


def _token(tweet_id: str) -> str:
    """Reproduce the JS token the web embed derives from the tweet id.

    ``((id / 1e15) * pi).toString(36)`` with ``0`` and ``.`` stripped.
    """
    val = (int(tweet_id) / 1e15) * math.pi
    intpart = int(val)
    frac = val - intpart
    s = "" if intpart else "0"
    while intpart > 0:
        s = _DIGITS[intpart % 36] + s
        intpart //= 36
    s += "."
    for _ in range(12):
        frac *= 36
        d = int(frac)
        s += _DIGITS[d]
        frac -= d
    return s.replace("0", "").replace(".", "")


async def tweet_result(tweet_id: str, lang: str = "en") -> dict[str, Any] | None:
    """Fetch a tweet's public syndication record, or None on any failure."""
    if not tweet_id or not tweet_id.isdigit():
        return None
    try:
        async with httpx.AsyncClient(timeout=10, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(
                _BASE, params={"id": tweet_id, "token": _token(tweet_id), "lang": lang}
            )
    except httpx.HTTPError:
        return None
    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) and data.get("text") is not None else None


def _meta_pairs(html: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for tag in _META_RE.findall(html or ""):
        m = _PROP_CONTENT_RE.search(tag)
        if not m:
            continue
        if m.group(1) is not None:
            out.append((m.group(1), unescape(m.group(2) or "")))
        else:
            out.append((m.group(4), unescape(m.group(3) or "")))
    return out


def _profile_image(html: str) -> str | None:
    for m in _IMAGE_URL_RE.finditer(html or ""):
        uri = unescape(m.group(1) or m.group(2) or "")
        if "profile_images" in uri:
            return uri
    return None


def parse_profile_html(html: str, handle: str) -> dict[str, Any] | None:
    """Map x.com profile microdata → shape ``_normalize_profile`` understands."""
    if not html or "schema.org/ProfilePage" not in html and "schema.org/profilepage" not in html.lower():
        return None
    if "schema.org/Person" not in html and "schema.org/person" not in html.lower():
        return None

    lower = html.lower()
    start = lower.find("schema.org/profilepage")
    if start < 0:
        return None
    # Prefer the Person block when present.
    person_at = lower.find("schema.org/person", start)
    window = html[person_at : person_at + 20_000] if person_at >= 0 else html[start : start + 40_000]

    fields: dict[str, str] = {}
    for key, value in _meta_pairs(window):
        if key and value and key not in fields:
            fields[key] = value
    # Profile-level dateCreated / url sit outside Person.
    page_window = html[start : start + 8_000]
    for key, value in _meta_pairs(page_window):
        if key in ("dateCreated", "url") and key not in fields and value:
            fields[key] = value

    counters: dict[str, list[int]] = {}
    for m in _INTERACTION_RE.finditer(html):
        kind = (m.group(1) or "").rsplit("/", 1)[-1]
        n = safe_int(m.group(2))
        if not kind or n is None:
            continue
        counters.setdefault(kind, []).append(n)

    tweet_count = counters.get("WriteAction", [None])[0]
    follow_vals = counters.get("FollowAction") or []
    if len(follow_vals) >= 2:
        following, followers = sorted(follow_vals)[0], sorted(follow_vals)[-1]
    elif len(follow_vals) == 1:
        following, followers = None, follow_vals[0]
    else:
        following = followers = None

    username = safe_str(fields.get("additionalName") or handle)
    if username:
        username = username.lstrip("@")
    profile_url = safe_str(fields.get("url")) or (f"https://x.com/{username}" if username else None)
    website = None
    for key, value in _meta_pairs(window):
        if key == "sameAs" and value and "x.com" not in value.lower() and "twitter.com" not in value.lower():
            website = value
            break

    location = None
    loc_m = re.search(
        r"""itemprop=["']homeLocation["'][\s\S]{0,400}?itemprop=["']name["'][^>]*content=["']([^"']*)["']""",
        window,
        re.I,
    )
    if loc_m:
        location = unescape(loc_m.group(1))

    if not username and not fields.get("identifier"):
        return None

    return {
        "id": safe_str(fields.get("identifier")),
        "userName": username,
        "name": safe_str(fields.get("name")),
        "description": safe_str(fields.get("description")),
        "location": safe_str(location),
        "followers": followers,
        "following": following,
        "statusesCount": tweet_count,
        "website": safe_str(website),
        "profilePicture": safe_str(_profile_image(window) or _profile_image(html)),
        "createdAt": safe_str(fields.get("dateCreated")),
        "url": profile_url,
    }


async def _fetch_profile_html(handle: str) -> str | None:
    url = f"https://x.com/{handle}"
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and len(resp.text) > 5000:
            return resp.text
    except httpx.HTTPError as exc:
        log.info("twitter_profile_direct_fail", handle=handle, error=str(exc))

    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
        if got:
            status, body = got
            if status == 200 and body and len(body) > 5000:
                return body
    return None


async def profile_by_handle(handle: str) -> dict[str, Any] | None:
    """Fetch a public X profile via HTML microdata (direct, then Decodo)."""
    raw = (handle or "").strip().lstrip("@")
    if "://" in raw or "/" in raw:
        path = urlparse(raw if "://" in raw else f"https://x.com/{raw}").path
        parts = [p for p in path.split("/") if p]
        raw = parts[0] if parts else ""
    raw = raw.lstrip("@")
    if not raw or not re.fullmatch(r"[A-Za-z0-9_]{1,15}", raw):
        return None
    html = await _fetch_profile_html(raw)
    if not html:
        return None
    parsed = parse_profile_html(html, raw)
    if parsed:
        log.info("twitter_profile_native_ok", handle=raw, followers=parsed.get("followers"))
    else:
        log.warning("twitter_profile_native_parse_miss", handle=raw, length=len(html))
    return parsed
