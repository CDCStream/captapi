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

import asyncio
import json
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.http_fetch import fetch as proxy_fetch
from app.services.http_fetch import proxy_for
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


# --- Comments (mobile aweme API, cursor-paginated) -------------------------
#
# Comments are NOT in the page's rehydration blob, and TikTok's *web* comment
# endpoint (www.tiktok.com/api/comment/list/) needs signed params (X-Bogus /
# msToken) and returns an empty body without them. The *mobile* aweme endpoint,
# however, serves logged-out comments with plain musical.ly device params and no
# signature — as long as the request exits from a residential IP (datacenter and
# some residential IPs get soft-blocked with status_code 2146). It is natively
# cursor-paginated: each page returns ``cursor`` (next offset), ``has_more``,
# and ``total``.
_TT_COMMENT_HOSTS = (
    "https://api22-normal-c-useast2a.tiktokv.com/aweme/v1/comment/list/",
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/comment/list/",
)
_TT_MOBILE_UA = (
    "com.zhiliaoapp.musically/2023600030 (Linux; U; Android 10; en; Pixel 4; "
    "Build/QQ3A.200805.001)"
)
_TT_COMMENT_PARAMS: dict[str, str] = {
    "aid": "1233",
    "device_id": "7318518857994389254",
    "iid": "7318518857994389254",
    "device_type": "Pixel 4",
    "device_platform": "android",
    "os_version": "10",
    "version_code": "230600",
    "app_name": "musical_ly",
    "channel": "googleplay",
    "region": "US",
    "sys_region": "US",
    "app_language": "en",
    "language": "en",
}


def _map_comment(c: dict[str, Any]) -> dict[str, Any] | None:
    cid = safe_str(c.get("cid") or c.get("id"))
    if not cid:
        return None
    user = c.get("user") or {}
    avatars = (user.get("avatar_thumb") or {}).get("url_list") or []
    return {
        "id": cid,
        "text": (safe_str(c.get("text")) or "").strip(),
        "author": safe_str(user.get("unique_id") or user.get("nickname")),
        "authorAvatarUrl": safe_str(avatars[0] if avatars else None),
        "likeCount": safe_int(c.get("digg_count")) or 0,
        "publishedAt": _iso(c.get("create_time")),
    }


def _us_residential_proxy() -> str | None:
    """Residential proxy URL pinned to US exits (Evomi appends geo targeting to
    the password: ``pass_country-US``). The mobile comment API 2146-blocks most
    non-US IPs, so pinning US sharply raises the per-request success rate."""
    base = proxy_for("residential")
    if not base:
        return None
    try:
        scheme, rest = base.split("://", 1)
        creds, hostpart = rest.rsplit("@", 1)
        user, pwd = creds.split(":", 1)
    except ValueError:
        return base
    if "_country-" in pwd:
        return base
    return f"{scheme}://{user}:{pwd}_country-US@{hostpart}"


async def _comment_once(host: str, params: dict[str, str], headers: dict[str, str]) -> dict[str, Any] | None:
    """Single mobile-API request on a fresh US residential IP. None unless the
    response is a clean ``status_code == 0`` payload."""
    try:
        async with httpx.AsyncClient(
            timeout=12, follow_redirects=True, proxy=_us_residential_proxy(), headers=headers
        ) as client:
            resp = await client.get(host, params=params)
    except httpx.HTTPError:
        return None
    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) and data.get("status_code") == 0 else None


async def _comment_page(aweme_id: str, cursor: str, count: int) -> dict[str, Any] | None:
    """One page of the mobile comment API, or None if every attempt is blocked.

    The residential pool rotates its exit IP per connection but a large share of
    IPs are soft-blocked (status_code 2146) at any moment, so we fire a batch of
    concurrent requests (each a fresh IP) and take the first clean response,
    cancelling the rest. A second batch covers an unlucky first round.
    """
    params = {**_TT_COMMENT_PARAMS, "aweme_id": aweme_id, "cursor": str(cursor), "count": str(count)}
    headers = {"User-Agent": _TT_MOBILE_UA, "Accept": "application/json"}
    for _ in range(2):
        tasks = [
            asyncio.create_task(_comment_once(_TT_COMMENT_HOSTS[i % len(_TT_COMMENT_HOSTS)], params, headers))
            for i in range(8)
        ]
        try:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if res is not None:
                    return res
        finally:
            for t in tasks:
                t.cancel()
    return None


async def comments_native(
    aweme_id: str, cursor: str | None, limit: int
) -> tuple[list[dict[str, Any]], str | None, int | None] | None:
    """Fetch up to ``limit`` comments starting at ``cursor`` (offset).

    Returns ``(comments, next_cursor, total)`` where ``next_cursor`` is the
    offset to resume from (``None`` once the thread is exhausted) and ``total``
    is the video's total comment count. Returns ``None`` if the very first page
    fails so the caller can fall back to the Apify actor.
    """
    collected: list[dict[str, Any]] = []
    cur = str(cursor) if cursor else "0"
    total: int | None = None
    max_pages = limit // 15 + 3
    for _ in range(max_pages):
        if len(collected) >= limit:
            break
        want = min(30, limit - len(collected))
        page = await _comment_page(aweme_id, cur, want)
        if page is None:
            # Total failure on the first page -> let the caller use Apify.
            # A later-page failure returns what we have plus the resume cursor.
            return None if not collected else (collected, cur, total)
        if total is None:
            total = safe_int(page.get("total"))
        for c in page.get("comments") or []:
            mapped = _map_comment(c)
            if mapped:
                collected.append(mapped)
        nxt = page.get("cursor")
        cur = str(nxt) if nxt is not None else cur
        if not page.get("has_more"):
            return collected, None, total
    return collected, cur, total


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


# --- Audience geography (commenter region sampling) ------------------------
#
# TikTok never exposes a creator's follower geography publicly, but the mobile
# comment API returns each commenter's ``region`` (ISO-3166 alpha-2 country
# code). Sampling commenters across a creator's recent videos and tallying
# those regions yields an engagement-based audience-country breakdown — the
# same signal third-party "audience" endpoints surface. Video IDs still have to
# come from the caller (TikTok gates the post list behind signed params).
async def audience_regions_native(
    aweme_ids: list[str], target_total: int = 500, per_video: int = 150
) -> list[str] | None:
    """Collect commenter country codes across the given videos.

    Fetches comment pages natively and pulls ``user.region`` from each comment,
    stopping once ``target_total`` codes are gathered or the videos are
    exhausted. Returns the list of ISO country codes (with duplicates, ready to
    tally) or ``None`` if every video's comments were blocked.
    """
    regions: list[str] = []
    any_success = False
    for aweme_id in aweme_ids:
        if len(regions) >= target_total:
            break
        collected = 0
        cur = "0"
        for _ in range(per_video // 15 + 2):
            if collected >= per_video or len(regions) >= target_total:
                break
            want = min(30, per_video - collected)
            page = await _comment_page(aweme_id, cur, want)
            if page is None:
                break  # this video is blocked right now; try the next one
            any_success = True
            comments = page.get("comments") or []
            for c in comments:
                user = c.get("user") or {}
                code = safe_str(user.get("region"))
                if code:
                    regions.append(code.strip().upper())
            collected += len(comments)
            nxt = page.get("cursor")
            cur = str(nxt) if nxt is not None else cur
            if not page.get("has_more"):
                break
    if not any_success:
        return None
    return regions
