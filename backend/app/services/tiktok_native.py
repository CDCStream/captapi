"""Self-scraped TikTok data from public web pages + mobile aweme APIs (no Apify).

TikTok web pages embed a ``__UNIVERSAL_DATA_FOR_REHYDRATION__`` JSON blob with
``webapp.video-detail`` (full video stats) and ``webapp.user-detail`` (full
profile stats). Fetching MUST go through the datacenter proxy tier: direct
requests from server IPs get an empty shell page without the blob.

List data (profile posts, comments) is NOT in the blob — the *web* XHR
endpoints need signed params — but TikTok's *mobile* aweme endpoints serve
logged-out lists with plain device params over a US residential IP.

Every function returns data in the exact shapes the router already emits, or
``None`` on failure so callers can fall back (or raise) as they choose.
"""

from __future__ import annotations

import asyncio
import json
import random
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
        "author": {
            "username": username,
            "displayName": safe_str(author.get("nickname")),
            "url": f"https://www.tiktok.com/@{username}" if username else None,
            "followers": safe_int(author_stats.get("followerCount")),
            "verified": False if author.get("verified") is None else bool(author.get("verified")),
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


def _residential_proxy(country: str = "US") -> str | None:
    """Residential proxy URL pinned to ``country`` (Evomi: ``pass_country-XX``).

    TikTok's mobile aweme APIs soft-block most exits; US (and often NL) are the
    geos that actually return data. Any existing ``_country-`` suffix on the
    password is replaced so callers can race multiple geos.
    """
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
        pwd = pwd.split("_country-", 1)[0]
    return f"{scheme}://{user}:{pwd}_country-{country}@{hostpart}"


def _us_residential_proxy() -> str | None:
    """US-pinned residential proxy (comments path)."""
    return _residential_proxy("US")


async def _comment_once(
    host: str,
    params: dict[str, str],
    headers: dict[str, str],
    proxy: str | None = None,
) -> dict[str, Any] | None:
    """Single mobile-API request on a residential IP. None unless the response
    is a clean ``status_code == 0`` payload."""
    try:
        async with httpx.AsyncClient(
            timeout=12,
            follow_redirects=True,
            proxy=proxy or _us_residential_proxy(),
            headers=headers,
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


# Reply threads use the same mobile hosts with ``/comment/list/reply/``.
_TT_REPLY_HOSTS = tuple(
    h.replace("/comment/list/", "/comment/list/reply/") for h in _TT_COMMENT_HOSTS
)


def _map_reply(c: dict[str, Any]) -> dict[str, Any] | None:
    """Map a mobile reply row to the public comment-replies shape."""
    mapped = _map_comment(c)
    if mapped is None:
        return None
    user = c.get("user") or {}
    verified = user.get("is_verified") or user.get("verified")
    return {
        "id": mapped["id"],
        "text": mapped["text"],
        "author": mapped["author"],
        "authorName": safe_str(user.get("nickname") or user.get("nickName")),
        "likeCount": mapped["likeCount"],
        "publishedAt": mapped["publishedAt"],
        "verified": False if verified is None else bool(verified),
        "profileImage": mapped.get("authorAvatarUrl"),
    }


async def _reply_page(
    aweme_id: str, comment_id: str, cursor: str, count: int
) -> dict[str, Any] | None:
    """One page of replies under ``comment_id``, or None if every attempt is blocked."""
    did = str(random.randint(10**18, 10**19 - 1))
    params = {
        **_TT_COMMENT_PARAMS,
        "device_id": did,
        "iid": did,
        "aweme_id": aweme_id,
        "comment_id": str(comment_id),
        "cursor": str(cursor),
        "count": str(count),
    }
    headers = {"User-Agent": _TT_MOBILE_UA, "Accept": "application/json"}
    geos = ("US", "NL")
    for _ in range(2):
        tasks = [
            asyncio.create_task(
                _comment_once(
                    _TT_REPLY_HOSTS[i % len(_TT_REPLY_HOSTS)],
                    params,
                    headers,
                    _residential_proxy(geos[i % len(geos)]),
                )
            )
            for i in range(8)
        ]
        try:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if res is not None and isinstance(res.get("comments"), list):
                    return res
        finally:
            for t in tasks:
                t.cancel()
    return None


async def comment_replies_native(
    aweme_id: str, comment_id: str, cursor: str | None, limit: int
) -> tuple[list[dict[str, Any]], str | None, int | None] | None:
    """Fetch up to ``limit`` replies under ``comment_id`` starting at ``cursor``.

    Returns ``(replies, next_cursor, total)``. ``None`` on first-page failure so
    the router can fall back to Apify.
    """
    collected: list[dict[str, Any]] = []
    cur = str(cursor) if cursor else "0"
    total: int | None = None
    max_pages = max(3, limit // 15 + 2)
    for _ in range(max_pages):
        if len(collected) >= limit:
            break
        want = min(30, limit - len(collected))
        page = await _reply_page(aweme_id, comment_id, cur, want)
        if page is None:
            return None if not collected else (collected, cur, total)
        if total is None:
            total = safe_int(page.get("total"))
        for c in page.get("comments") or []:
            mapped = _map_reply(c)
            if mapped:
                collected.append(mapped)
                if len(collected) >= limit:
                    break
        nxt = page.get("cursor")
        cur = str(nxt) if nxt is not None else cur
        if not page.get("has_more"):
            return collected[:limit], None, total
    return collected[:limit], cur, total


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


# --- Channel posts (mobile aweme/post API, cursor-paginated) ---------------
#
# Profile post lists are not in the rehydration blob, and the web
# ``/api/post/item_list/`` endpoint needs signed params. The mobile
# ``/aweme/v1/aweme/post/`` endpoint, however, returns logged-out post pages
# with ``sec_user_id`` + plain device params — same residential soft-block
# pattern as comments (empty body / status 2146). Pagination uses TikTok's
# own ``max_cursor`` timestamp cursor and ``has_more`` flag.
_TT_POST_HOSTS = (
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/post/",
    "https://api22-normal-c-useast2a.tiktokv.com/aweme/v1/aweme/post/",
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/post/",
    "https://api31-normal-useast2a.tiktokv.com/aweme/v1/aweme/post/",
    "https://api.tiktokv.com/aweme/v1/aweme/post/",
)


def _url_list_first(node: Any) -> str | None:
    if isinstance(node, dict):
        urls = node.get("url_list") or node.get("urlList") or []
        return safe_str(urls[0] if urls else None)
    return safe_str(node)


# Caption fallback: mobile aweme rows often omit/partial-fill text_extra /
# cha_list even when the desc is full of #tags.
_HASHTAG_RE = re.compile(r"#([^\s#]+)")


def _collect_hashtags(item: dict[str, Any], caption: str | None) -> list[str]:
    """Deduped hashtags from structured fields + caption, skipping empties."""
    seen: set[str] = set()
    out: list[str] = []

    def _add(raw: Any) -> None:
        name = safe_str(raw)
        if not name:
            return
        name = name.lstrip("#").strip()
        if not name or name in seen:
            return
        seen.add(name)
        out.append(name)

    for te in item.get("text_extra") or item.get("textExtra") or []:
        if isinstance(te, dict):
            _add(te.get("hashtag_name") or te.get("hashtagName"))
    for cha in item.get("cha_list") or item.get("chaList") or item.get("challenges") or []:
        if isinstance(cha, dict):
            _add(cha.get("cha_name") or cha.get("chaName") or cha.get("title"))
    if caption:
        for tag in _HASHTAG_RE.findall(caption):
            _add(tag)
    return out


def _map_aweme_post(item: dict[str, Any]) -> dict[str, Any] | None:
    """Map a mobile aweme row to the same post shape as video_details_native."""
    aweme_id = safe_str(item.get("aweme_id") or item.get("id"))
    if not aweme_id:
        return None
    author = item.get("author") or {}
    if not isinstance(author, dict):
        author = {}
    stats = item.get("statistics") or item.get("stats") or {}
    if not isinstance(stats, dict):
        stats = {}
    video = item.get("video") or {}
    if not isinstance(video, dict):
        video = {}
    music = item.get("music") or {}
    if not isinstance(music, dict):
        music = {}
    author_stats = item.get("author_stats") or item.get("authorStats") or {}
    if not isinstance(author_stats, dict):
        author_stats = {}

    username = safe_str(author.get("unique_id") or author.get("uniqueId"))
    duration = safe_float(video.get("duration") or item.get("duration"))
    # Mobile aweme occasionally reports duration in milliseconds.
    if duration is not None and duration > 1000:
        duration = duration / 1000.0

    caption = safe_str(item.get("desc"))
    hashtags = _collect_hashtags(item, caption)

    avatar = (
        _url_list_first(author.get("avatar_larger") or author.get("avatarLarger"))
        or _url_list_first(author.get("avatar_medium") or author.get("avatarMedium"))
        or _url_list_first(author.get("avatar_thumb") or author.get("avatarThumb"))
    )
    cover = (
        _url_list_first(video.get("cover"))
        or _url_list_first(video.get("origin_cover") or video.get("originCover"))
        or _url_list_first(video.get("dynamic_cover") or video.get("dynamicCover"))
    )

    # Badge flag: missing/unknown -> false (never null).
    verified = author.get("verified")
    if verified is None:
        verified = author.get("is_verified")
    verified = bool(verified) if verified is not None else False

    return {
        "platform": "tiktok",
        "url": (
            f"https://www.tiktok.com/@{username}/video/{aweme_id}"
            if username
            else safe_str(item.get("share_url") or item.get("shareUrl"))
        ),
        "id": aweme_id,
        "caption": caption,
        "description": caption,
        "publishedAt": _iso(item.get("create_time") or item.get("createTime")),
        "durationSeconds": duration,
        "thumbnailUrl": cover,
        "author": {
            "username": username,
            "displayName": safe_str(author.get("nickname") or author.get("nickName")),
            "url": f"https://www.tiktok.com/@{username}" if username else None,
            "followers": safe_int(
                author.get("follower_count")
                or author.get("followerCount")
                or author_stats.get("follower_count")
                or author_stats.get("followerCount")
            ),
            "verified": verified,
            "profileImage": avatar,
        },
        "engagement": {
            "views": safe_int(stats.get("play_count") or stats.get("playCount")),
            "likes": safe_int(stats.get("digg_count") or stats.get("diggCount")),
            "comments": safe_int(stats.get("comment_count") or stats.get("commentCount")),
            "shares": safe_int(stats.get("share_count") or stats.get("shareCount")),
            "saves": safe_int(stats.get("collect_count") or stats.get("collectCount")),
        },
        "hashtags": hashtags,
        "musicName": safe_str(music.get("title")),
    }


def _post_page_ok(page: dict[str, Any], *, expect_items: bool) -> bool:
    """Reject soft-block decoys: status_code 0 with an empty aweme_list.

    Blocked exits often answer with ``status_code == 0``, ``aweme_list: []``
    (sometimes echoing ``max_cursor``). A profile that has videos never
    legitimately returns an empty page — the last page still has items with
    ``has_more == 0`` — so empty payloads are always treated as a miss when
    ``expect_items`` is true.
    """
    awemes = page.get("aweme_list")
    if not isinstance(awemes, list):
        return False
    if awemes:
        return True
    return not expect_items


async def _post_page(
    sec_user_id: str, max_cursor: str, count: int, *, expect_items: bool
) -> dict[str, Any] | None:
    """One page of the mobile user-post API, or None if every attempt is blocked."""
    # ``max_cursor`` is the real pager; ``cursor`` is accepted as an alias on
    # some hosts. Deeper pages are softer-blocked, so we race harder for them.
    headers = {"User-Agent": _TT_MOBILE_UA, "Accept": "application/json"}
    # Keep races short — the router falls back to Apify when we miss. US + NL
    # are the Evomi geos that actually return aweme_list (GB/CA/DE soft-block).
    rounds = 3 if max_cursor not in ("", "0") else 2
    concurrency = 12
    geos = ("US", "NL")

    async def _attempt(host: str, country: str) -> dict[str, Any] | None:
        did = str(random.randint(10**18, 10**19 - 1))
        # Both max_cursor and cursor must be set (including on page 2+); hosts
        # that only see max_cursor often return empty soft-block decoys.
        params = {
            **_TT_COMMENT_PARAMS,
            "device_id": did,
            "iid": did,
            "sec_user_id": sec_user_id,
            "count": str(max(1, min(count, 35))),
            "max_cursor": str(max_cursor),
            "min_cursor": "0",
            "cursor": str(max_cursor),
        }
        return await _comment_once(host, params, headers, _residential_proxy(country))

    for _ in range(rounds):
        tasks = [
            asyncio.create_task(
                _attempt(_TT_POST_HOSTS[i % len(_TT_POST_HOSTS)], geos[i % len(geos)])
            )
            for i in range(concurrency)
        ]
        try:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if res is not None and _post_page_ok(res, expect_items=expect_items):
                    return res
        finally:
            for t in tasks:
                t.cancel()
        await asyncio.sleep(0.15)
    return None


async def channel_posts_native(
    handle: str, cursor: str | None, limit: int
) -> tuple[list[dict[str, Any]], str | None] | None:
    """Fetch up to ``limit`` latest posts for ``handle``, starting at ``cursor``.

    ``cursor`` is TikTok's ``max_cursor`` (numeric timestamp string); omit / ``0``
    for the first page. Returns ``(posts, next_cursor)`` where ``next_cursor`` is
    ``None`` when the feed is exhausted. Returns ``None`` if the profile or the
    first page cannot be loaded.
    """
    ui = await _user_info(handle)
    if ui is None:
        return None
    user = ui.get("user") or {}
    sec = safe_str(user.get("secUid"))
    if not sec:
        return None
    stats_v2 = ui.get("statsV2") or {}
    stats = ui.get("stats") or {}
    video_count = _stat(stats_v2, stats, "videoCount") or 0
    expect_items = video_count > 0

    collected: list[dict[str, Any]] = []
    cur = str(cursor) if cursor else "0"
    max_pages = max(3, limit // 10 + 3)
    for _ in range(max_pages):
        if len(collected) >= limit:
            break
        want = min(30, limit - len(collected))
        page = await _post_page(sec, cur, want, expect_items=expect_items)
        if page is None:
            return None if not collected else (collected, cur)
        for raw in page.get("aweme_list") or []:
            if not isinstance(raw, dict):
                continue
            mapped = _map_aweme_post(raw)
            if mapped:
                collected.append(mapped)
                if len(collected) >= limit:
                    break
        nxt = page.get("max_cursor")
        has_more = bool(page.get("has_more"))
        if not has_more:
            return collected[:limit], None
        cur = str(nxt) if nxt is not None else cur
        if len(collected) >= limit:
            return collected[:limit], cur
    return collected[:limit], (cur if collected else None)


# --- Audience geography (commenter region sampling) ------------------------
#
# TikTok never exposes a creator's follower geography publicly, but the mobile
# comment API returns each commenter's ``region`` (ISO-3166 alpha-2 country
# code). Sampling commenters across a creator's recent videos and tallying
# those regions yields an engagement-based audience-country breakdown — the
# same signal third-party "audience" endpoints surface. Video IDs come from the
# caller (or from ``channel_posts_native``).
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


# --- Search suggestions (public web autocomplete) ---------------------------
#
# TikTok's logged-out search preview endpoint returns ``sug_list`` for a seed
# keyword. Same shape the Apify keywords-discovery actor scrapes; we hit it
# directly so a flaky actor doesn't 502 the whole route.
_TT_SUGGEST_URL = "https://www.tiktok.com/api/search/general/preview/"


async def search_suggestions_native(
    q: str,
    *,
    country: str = "US",
    language: str = "en-US",
    limit: int = 20,
) -> list[dict[str, Any]] | None:
    """Return raw suggestion rows (``suggestion``, ``rank``, …) or ``None``."""
    seed = (q or "").strip()
    if not seed:
        return None
    region = (country or "US").upper()
    lang = language or "en-US"
    params = {
        "aid": "1988",
        "app_name": "tiktok_web",
        "device_platform": "web_pc",
        "keyword": seed,
        "region": region,
        "priority_region": region,
    }
    headers = {
        **TT_HEADERS,
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.tiktok.com/search?q={seed}",
        "Accept-Language": lang,
    }
    body: dict[str, Any] | None = None
    for tier in ("datacenter", "residential"):
        try:
            resp = await proxy_fetch(
                _TT_SUGGEST_URL, tier=tier, headers=headers, params=params, timeout=20
            )
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        try:
            parsed = resp.json()
        except ValueError:
            continue
        if isinstance(parsed, dict) and isinstance(parsed.get("sug_list"), list):
            body = parsed
            break
    if body is None:
        return None

    out: list[dict[str, Any]] = []
    for idx, row in enumerate(body.get("sug_list") or [], start=1):
        if not isinstance(row, dict):
            continue
        word = safe_str(
            row.get("content")
            or (row.get("word_record") or {}).get("words_content")
            or row.get("word")
        )
        if not word:
            continue
        rank = safe_int((row.get("word_record") or {}).get("words_position"))
        out.append(
            {
                "seedKeyword": seed,
                "suggestion": word,
                "suggestionRank": (rank + 1) if rank is not None else idx,
                "region": region,
                "language": lang,
            }
        )
        if len(out) >= limit:
            break
    return out if out else None
