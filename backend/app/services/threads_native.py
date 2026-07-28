"""Native Threads lookups without Apify.

Public profile pages hydrate a Relay payload
(``BarcelonaProfilePageDirectQueryRelayPreloader``) that includes username,
display name, bio, follower count, verified flag, and avatar. Logged-out
datacenter GETs usually redirect to login — Decodo ``headless=html`` returns
the hydrated HTML.
"""

from __future__ import annotations

import json
import re
from html import unescape
from typing import Any

import httpx
import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

_UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
_HANDLE_RE = re.compile(r"^[A-Za-z0-9._]{1,30}$")
_PROFILE_MARKER = "BarcelonaProfilePageDirectQueryRelayPreloader"
_OG_TITLE_RE = re.compile(
    r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)
_OG_DESC_RE = re.compile(
    r'<meta[^>]+(?:property=["\']og:description["\']|name=["\']description["\'])'
    r'[^>]+content=["\']([^"\']*)["\']',
    re.I,
)
_OG_IMAGE_RE = re.compile(
    r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)
_OG_URL_RE = re.compile(
    r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)


def _normalize_handle(handle: str) -> str | None:
    raw = (handle or "").strip().lstrip("@")
    if "://" in raw or "/" in raw:
        from urllib.parse import urlparse

        path = urlparse(raw if "://" in raw else f"https://www.threads.net/{raw}").path
        parts = [p for p in path.split("/") if p]
        if parts and parts[0].startswith("@"):
            raw = parts[0][1:]
        elif parts:
            raw = parts[0].lstrip("@")
    raw = raw.lstrip("@")
    if not raw or not _HANDLE_RE.fullmatch(raw):
        return None
    return raw


def _extract_json_object(source: str, brace_start: int) -> str | None:
    if brace_start < 0 or brace_start >= len(source) or source[brace_start] != "{":
        return None
    depth = 0
    in_str = False
    esc = False
    for idx in range(brace_start, len(source)):
        ch = source[idx]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start : idx + 1]
    return None


def _profile_pic(user: dict[str, Any]) -> str | None:
    versions = user.get("hd_profile_pic_versions")
    if isinstance(versions, list) and versions:
        # Prefer the largest declared width.
        best = None
        best_w = -1
        for item in versions:
            if not isinstance(item, dict):
                continue
            url = safe_str(item.get("url"))
            try:
                width = int(item.get("width") or 0)
            except (TypeError, ValueError):
                width = 0
            if url and width >= best_w:
                best = url
                best_w = width
        if best:
            return best
    return safe_str(user.get("profile_pic_url") or user.get("profilePicUrl"))


def parse_profile_html(html: str, handle: str) -> dict[str, Any] | None:
    """Extract a Threads user profile from hydrated profile-page HTML."""
    if not html or not handle:
        return None
    needle = handle.lower()
    search_from = 0
    marker = html.find(_PROFILE_MARKER)
    if marker >= 0:
        search_from = marker

    pos = search_from
    while True:
        idx = html.find('"user":{', pos)
        if idx < 0:
            break
        raw = _extract_json_object(html, idx + len('"user":'))
        pos = idx + 8
        if not raw:
            continue
        try:
            user = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(user, dict):
            continue
        username = safe_str(user.get("username") or user.get("userName"))
        if not username or username.lower() != needle:
            continue
        if user.get("follower_count") is None and user.get("biography") is None and not user.get("full_name"):
            continue
        return {
            "username": username,
            "pk": safe_str(user.get("pk") or user.get("id") or user.get("userId")),
            "full_name": safe_str(user.get("full_name") or user.get("fullName") or user.get("name")),
            "biography": safe_str(user.get("biography") or user.get("bio")),
            "is_verified": bool(user.get("is_verified") or user.get("isVerified")),
            "follower_count": safe_int(user.get("follower_count") or user.get("followerCount")),
            "profile_pic_url": _profile_pic(user),
            "url": f"https://www.threads.net/@{username}",
        }

    return parse_profile_og(html, handle)


def parse_profile_og(html: str, handle: str) -> dict[str, Any] | None:
    """Degraded OG-tag profile when Relay JSON is missing."""
    if not html:
        return None
    title_m = _OG_TITLE_RE.search(html)
    desc_m = _OG_DESC_RE.search(html)
    image_m = _OG_IMAGE_RE.search(html)
    url_m = _OG_URL_RE.search(html)
    title = unescape(title_m.group(1)).strip() if title_m else ""
    desc = unescape(desc_m.group(1)).strip() if desc_m else ""
    image = unescape(image_m.group(1)).replace("&amp;", "&").strip() if image_m else None
    og_url = unescape(url_m.group(1)).strip() if url_m else None

    # "Mark Zuckerberg (@zuck) • Threads, Say more"
    name = None
    username = handle
    m = re.match(r"^(.*?)\s*\(@([^)]+)\)", title)
    if m:
        name = m.group(1).strip() or None
        username = m.group(2).strip() or handle

    # "5.7M Followers • 151 Threads • Mostly superintelligence..."
    bio = None
    followers = None
    if desc:
        parts = [p.strip() for p in desc.split("•")]
        for part in parts:
            low = part.lower()
            if "follower" in low:
                num = re.search(r"([\d,.]+)\s*([kmb])?", part, re.I)
                if num:
                    try:
                        val = float(num.group(1).replace(",", ""))
                    except ValueError:
                        val = None
                    if val is not None:
                        mult = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(
                            (num.group(2) or "").lower(), 1
                        )
                        followers = int(val * mult)
            elif "thread" in low:
                continue
            else:
                bio = part or bio

    if not name and not bio and not image:
        return None
    return {
        "username": username,
        "pk": None,
        "full_name": name,
        "biography": bio,
        "is_verified": None,
        "follower_count": followers,
        "profile_pic_url": image,
        "url": og_url or f"https://www.threads.net/@{username}",
    }


async def _fetch_profile_html(handle: str) -> str | None:
    url = f"https://www.threads.net/@{handle}"
    # Direct GETs almost always land on /login without the Relay profile blob.
    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
        if got:
            status, body = got
            if status == 200 and body and (
                _PROFILE_MARKER in body or "follower_count" in body or "og:title" in body
            ):
                return body
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and len(resp.text) > 2000:
            if _PROFILE_MARKER in resp.text or "follower_count" in resp.text:
                return resp.text
    except httpx.HTTPError as exc:
        log.info("threads_profile_direct_fail", handle=handle, error=str(exc))
    return None


async def profile_by_handle(handle: str) -> dict[str, Any] | None:
    """Fetch a public Threads profile via hydrated HTML (Decodo → direct)."""
    raw = _normalize_handle(handle)
    if not raw:
        return None
    html = await _fetch_profile_html(raw)
    if not html:
        return None
    parsed = parse_profile_html(html, raw)
    if parsed:
        log.info(
            "threads_profile_native_ok",
            handle=raw,
            followers=parsed.get("follower_count"),
            verified=parsed.get("is_verified"),
        )
    else:
        log.warning("threads_profile_native_parse_miss", handle=raw, length=len(html))
    return parsed
