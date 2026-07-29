"""Snapchat public profile via Decodo HTML (__NEXT_DATA__). No Apify."""

from __future__ import annotations

import json
import re
from typing import Any

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

_NEXT_RE = re.compile(
    r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(\{.*?\})</script>',
    re.S,
)


def _highlights(raw: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "id": safe_str(row.get("highlightId") or row.get("storyId")),
                "title": safe_str(row.get("storyTitle")),
                "subtitle": safe_str(row.get("storySubtitle")),
                "thumbnailUrl": safe_str(row.get("thumbnailUrl")),
                "emoji": safe_str(row.get("emoji")),
            }
        )
    return [h for h in out if h.get("id") or h.get("title")]


def _related(raw: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        info = row.get("publicProfileInfo") if isinstance(row.get("publicProfileInfo"), dict) else row
        username = safe_str(info.get("username"))
        if not username:
            continue
        out.append(
            {
                "username": username,
                "displayName": safe_str(info.get("title") or info.get("displayName")),
                "avatar": safe_str(info.get("profilePictureUrl") or info.get("avatar")),
                "url": f"https://www.snapchat.com/@{username}",
            }
        )
    return out


async def fetch_user_profile(username: str) -> dict[str, Any] | None:
    """Public Snapchat profile page → shape compatible with router ``_normalize``."""
    handle = (username or "").strip().lstrip("@").rstrip("/")
    if not handle:
        return None
    if not decodo_fetch.enabled():
        return None

    url = f"https://www.snapchat.com/@{handle}"
    got = await decodo_fetch.fetch_url(url, timeout=90.0, geo="US")
    if not got:
        return None
    status, html = got
    if status != 200 or not html or len(html) < 2000:
        return None

    match = _NEXT_RE.search(html)
    if not match:
        log.info("snapchat_native_no_next_data", username=handle)
        return None
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

    page = (payload.get("props") or {}).get("pageProps") or {}
    profile_wrap = page.get("userProfile") if isinstance(page.get("userProfile"), dict) else {}
    info = profile_wrap.get("publicProfileInfo")
    if not isinstance(info, dict) or not info.get("username"):
        log.info("snapchat_native_no_profile", username=handle)
        return None

    uname = safe_str(info.get("username")) or handle
    highlights = _highlights(page.get("curatedHighlights") or [])
    related = _related(info.get("relatedAccountsInfo") or [])

    out = {
        "username": uname,
        "mutableUsername": uname,
        "url": f"https://www.snapchat.com/@{uname}",
        "webUrl": f"https://www.snapchat.com/@{uname}",
        "displayName": safe_str(info.get("title") or info.get("mutableName")),
        "title": safe_str(info.get("title")),
        "bio": safe_str(info.get("bio")),
        "description": safe_str(info.get("bio")),
        "category": safe_str(info.get("categoryStringId")),
        "categoryStringId": safe_str(info.get("categoryStringId")),
        "subscriberCount": safe_int(info.get("subscriberCount")),
        "isVerified": bool(info.get("badge")),
        "verified": bool(info.get("badge")),
        "badge": info.get("badge"),
        "profilePictureUrl": safe_str(info.get("profilePictureUrl")),
        "squareHeroImageUrl": safe_str(info.get("squareHeroImageUrl")),
        "snapcodeImageUrl": safe_str(info.get("snapcodeImageUrl")),
        "websiteUrl": safe_str(info.get("websiteUrl")),
        "curatedHighlights": highlights,
        "highlights": highlights,
        "relatedAccounts": related,
    }
    log.info(
        "snapchat_native_profile_ok",
        username=uname,
        subscribers=out.get("subscriberCount"),
        highlights=len(highlights),
    )
    return out
