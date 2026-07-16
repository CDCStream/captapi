"""Self-scraped TikTok data from public web pages (no Apify).

TikTok web pages embed a ``__UNIVERSAL_DATA_FOR_REHYDRATION__`` JSON blob with
``webapp.video-detail`` (full video stats) and ``webapp.user-detail`` (full
profile stats). Fetching MUST go through the datacenter proxy tier: direct
requests from server IPs get an empty shell page without the blob.

List data (profile posts, search, comments) is NOT in the blob - those XHR
calls need TikTok's signed parameters - so list endpoints stay on Apify.

Every function returns data in the exact shapes the router already emits, or
``None`` on failure so callers can fall back to the Apify actors.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.http_fetch import fetch as proxy_fetch
from app.utils.formatters import safe_float, safe_int, safe_str

TT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.tiktok.com/",
}

_UNIVERSAL_RE = re.compile(
    r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', re.DOTALL
)


async def _fetch_scope(url: str) -> dict[str, Any] | None:
    """GET a TikTok page and return the ``__DEFAULT_SCOPE__`` dict."""
    for _ in range(2):  # occasional empty shell page; one retry is cheap
        try:
            resp = await proxy_fetch(url, tier="datacenter", headers=TT_HEADERS, timeout=15)
        except httpx.HTTPError:
            return None
        if resp.status_code >= 400:
            return None
        m = _UNIVERSAL_RE.search(resp.text)
        if not m:
            continue
        try:
            data = json.loads(m.group(1))
        except ValueError:
            continue
        scope = data.get("__DEFAULT_SCOPE__")
        if isinstance(scope, dict):
            return scope
    return None


def _stat(stats_v2: dict[str, Any], stats: dict[str, Any], key: str) -> int | None:
    """statsV2 carries exact counts as strings; legacy stats rounds big ones."""
    return safe_int(stats_v2.get(key) if stats_v2.get(key) is not None else stats.get(key))


def _iso(create_time: Any) -> str | None:
    ts = safe_int(create_time)
    if not ts:
        return None
    # Match the Apify path's createTimeISO format (…T00:45:18.000Z) so publishedAt
    # is identical whichever source serves the request. TikTok timestamps are
    # whole seconds, so milliseconds are always .000.
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


async def video_details_native(url: str) -> dict[str, Any] | None:
    scope = await _fetch_scope(url)
    if not scope:
        return None
    vd = scope.get("webapp.video-detail") or {}
    if vd.get("statusCode") != 0:
        return None  # deleted / private / region-locked -> let the actor try
    item = (vd.get("itemInfo") or {}).get("itemStruct") or {}
    if not item.get("id"):
        return None

    stats_v2 = item.get("statsV2") or {}
    stats = item.get("stats") or {}
    author = item.get("author") or {}
    author_stats = item.get("authorStats") or {}
    video = item.get("video") or {}
    music = item.get("music") or {}
    username = safe_str(author.get("uniqueId"))

    hashtags = []
    for te in item.get("textExtra") or []:
        name = safe_str((te or {}).get("hashtagName"))
        if name:
            hashtags.append(name)
    if not hashtags:
        hashtags = [
            safe_str(c.get("title")) for c in item.get("challenges") or [] if safe_str(c.get("title"))
        ]

    return {
        "platform": "tiktok",
        "url": f"https://www.tiktok.com/@{username}/video/{item['id']}" if username else url,
        "id": safe_str(item.get("id")),
        "caption": safe_str(item.get("desc")),
        "description": safe_str(item.get("desc")),
        "publishedAt": _iso(item.get("createTime")),
        "durationSeconds": safe_float(video.get("duration")),
        "thumbnailUrl": safe_str(video.get("cover") or video.get("originCover")),
        # playAddr/downloadAddr are CDN URLs tied to the fetching IP+cookies and
        # usually 403 for API consumers, so we don't surface them here; the
        # video-download endpoint (actor-backed) handles downloads.
        "videoUrl": None,
        "author": {
            "username": username,
            "displayName": safe_str(author.get("nickname")),
            "url": f"https://www.tiktok.com/@{username}" if username else None,
            "followers": safe_int(author_stats.get("followerCount")),
            "verified": author.get("verified"),
            "profileImage": safe_str(author.get("avatarLarger") or author.get("avatarMedium")),
        },
        "engagement": {
            "views": _stat(stats_v2, stats, "playCount"),
            "likes": _stat(stats_v2, stats, "diggCount"),
            "comments": _stat(stats_v2, stats, "commentCount"),
            "shares": _stat(stats_v2, stats, "shareCount"),
            "saves": _stat(stats_v2, stats, "collectCount"),
        },
        "hashtags": hashtags,
        "musicName": safe_str(music.get("title")),
    }


async def fetch_video_bytes(url: str, max_bytes: int) -> bytes | None:
    """Download a TikTok video's media (watermarked) for transcription.

    The page's ``playAddr`` CDN URL only works with the cookies set by the
    page response (``tt_chain_token`` et al.) and from the same IP, so both
    requests must share one client + proxy connection.
    """
    from app.services.http_fetch import proxy_for

    proxy = proxy_for("datacenter")
    try:
        async with httpx.AsyncClient(
            timeout=30, follow_redirects=True, headers=TT_HEADERS, proxy=proxy
        ) as client:
            resp = await client.get(url)
            if resp.status_code >= 400:
                return None
            m = _UNIVERSAL_RE.search(resp.text)
            if not m:
                return None
            try:
                scope = json.loads(m.group(1)).get("__DEFAULT_SCOPE__") or {}
            except ValueError:
                return None
            item = ((scope.get("webapp.video-detail") or {}).get("itemInfo") or {}).get(
                "itemStruct"
            ) or {}
            video = item.get("video") or {}
            play = safe_str(video.get("playAddr") or video.get("downloadAddr"))
            if not play:
                return None
            media = await client.get(play, headers={**TT_HEADERS, "Range": "bytes=0-"})
            if media.status_code >= 400 or not media.content:
                return None
            if len(media.content) > max_bytes:
                return None
            return media.content
    except httpx.HTTPError:
        return None


async def _user_info(handle: str) -> dict[str, Any] | None:
    scope = await _fetch_scope(f"https://www.tiktok.com/@{handle}")
    if not scope:
        return None
    ui = (scope.get("webapp.user-detail") or {}).get("userInfo") or {}
    user = ui.get("user") or {}
    if not user.get("uniqueId"):
        return None
    return ui


async def channel_details_native(handle: str, url: str) -> dict[str, Any] | None:
    ui = await _user_info(handle)
    if ui is None:
        return None
    user = ui.get("user") or {}
    stats_v2 = ui.get("statsV2") or {}
    stats = ui.get("stats") or {}
    username = safe_str(user.get("uniqueId")) or handle
    bio_link = user.get("bioLink")
    if isinstance(bio_link, dict):
        bio_link = bio_link.get("link")
    return {
        "platform": "tiktok",
        "url": f"https://www.tiktok.com/@{username}",
        "username": username,
        "displayName": safe_str(user.get("nickname")),
        "bio": safe_str(user.get("signature")),
        "followers": _stat(stats_v2, stats, "followerCount"),
        "following": _stat(stats_v2, stats, "followingCount"),
        "likes": _stat(stats_v2, stats, "heartCount"),
        "postCount": _stat(stats_v2, stats, "videoCount"),
        "verified": user.get("verified"),
        "private": user.get("privateAccount"),
        "profileImage": safe_str(user.get("avatarLarger") or user.get("avatarMedium")),
        "externalUrl": safe_str(bio_link),
        "category": safe_str((user.get("commerceUserInfo") or {}).get("category")),
    }


async def profile_region_native(handle: str) -> dict[str, Any] | None:
    """Region/language signals from the profile page.

    Returns None when the page exposes neither region nor language, so the
    caller can fall back to the actor (which samples video caption language).
    """
    ui = await _user_info(handle)
    if ui is None:
        return None
    user = ui.get("user") or {}
    region = safe_str(user.get("region"))
    language = safe_str(user.get("language"))
    if not region and not language:
        return None
    stats_v2 = ui.get("statsV2") or {}
    stats = ui.get("stats") or {}
    username = safe_str(user.get("uniqueId")) or handle
    return {
        "platform": "tiktok",
        "username": username,
        "displayName": safe_str(user.get("nickname")),
        "url": f"https://www.tiktok.com/@{username}",
        "region": region,
        "language": language,
        "followers": _stat(stats_v2, stats, "followerCount"),
        "following": _stat(stats_v2, stats, "followingCount"),
        "likes": _stat(stats_v2, stats, "heartCount"),
        "videos": _stat(stats_v2, stats, "videoCount"),
        "verified": user.get("verified"),
        "private": user.get("privateAccount"),
        "profileImage": safe_str(user.get("avatarLarger") or user.get("avatarMedium")),
        "raw": {"user": user, "statsV2": stats_v2},
    }
