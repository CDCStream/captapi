"""Native Threads lookups without Apify.

Public profile pages hydrate a Relay payload
(``BarcelonaProfilePageDirectQueryRelayPreloader``) that includes username,
display name, bio, follower count, verified flag, and avatar. The same HTML
also embeds recent posts under ``thread_items`` (soft-capped by the page).

Keyword search pages (``/search?q=...``) hydrate
``BarcelonaSearchResultsQueryRelayPreloader`` and likewise embed matching
posts under ``thread_items`` (soft-capped ~20 per page render).

``search-users`` derives distinct authors from that same search HTML
(Users-tab GraphQL is deferred / not hydrated for logged-out scrapes).

Permalink pages hydrate ``BarcelonaPostPageDirectQueryRelayPreloader``
with the target post under ``thread_items``.

Logged-out datacenter GETs usually redirect to login — Decodo
``headless=html`` returns the hydrated HTML.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
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
        "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
_HANDLE_RE = re.compile(r"^[A-Za-z0-9._]{1,30}$")
_POST_CODE_RE = re.compile(r"^[A-Za-z0-9_-]{5,20}$")
_POST_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?threads\.(?:net|com)/"
    r"(?:@(?P<author>[A-Za-z0-9._]+)/post/|(?:t/))"
    r"(?P<code>[A-Za-z0-9_-]+)",
    re.I,
)
_PROFILE_MARKER = "BarcelonaProfilePageDirectQueryRelayPreloader"
_THREAD_ITEMS_RE = re.compile(r'"thread_items"\s*:\s*\[')
_OG_TITLE_RE = re.compile(
    r"<meta[^>]+property=['\"]og:title['\"][^>]+content=['\"]([^'\"]+)['\"]",
    re.I,
)
_OG_DESC_RE = re.compile(
    r"<meta[^>]+(?:property=['\"]og:description['\"]|name=['\"]description['\"])"
    r"[^>]+content=['\"]([^'\"]*)['\"]",
    re.I,
)
_OG_IMAGE_RE = re.compile(
    r"<meta[^>]+property=['\"]og:image(?::secure_url)?['\"][^>]+content=['\"]([^'\"]+)['\"]",
    re.I,
)
_OG_URL_RE = re.compile(
    r"<meta[^>]+property=['\"]og:url['\"][^>]+content=['\"]([^'\"]+)['\"]",
    re.I,
)


def _normalize_handle(handle: str) -> str | None:
    raw = (handle or "").strip().lstrip("@")
    if "://" in raw or "/" in raw:
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


def _extract_json_array(source: str, bracket_start: int) -> str | None:
    if bracket_start < 0 or bracket_start >= len(source) or source[bracket_start] != "[":
        return None
    depth = 0
    in_str = False
    esc = False
    for idx in range(bracket_start, len(source)):
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
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return source[bracket_start : idx + 1]
    return None


def _profile_pic(user: dict[str, Any]) -> str | None:
    versions = user.get("hd_profile_pic_versions")
    if isinstance(versions, list) and versions:
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
        if (
            user.get("follower_count") is None
            and user.get("biography") is None
            and not user.get("full_name")
        ):
            continue
        threads_only = user.get("is_threads_only_user")
        if threads_only is None:
            threads_only = user.get("isThreadsOnlyUser")
        is_private = user.get("text_post_app_is_private")
        if is_private is None:
            is_private = user.get("isPrivate")
        onboarded = user.get("has_onboarded_to_text_post_app")
        if onboarded is None:
            onboarded = user.get("hasOnboardedToTextPostApp")
        return {
            "username": username,
            "pk": safe_str(user.get("pk") or user.get("id") or user.get("userId")),
            "full_name": safe_str(user.get("full_name") or user.get("fullName") or user.get("name")),
            "biography": safe_str(user.get("biography") or user.get("bio")),
            "is_verified": bool(user.get("is_verified") or user.get("isVerified")),
            "follower_count": safe_int(user.get("follower_count") or user.get("followerCount")),
            "profile_pic_url": _profile_pic(user),
            "url": f"https://www.threads.net/@{username}",
            # Additive profile intel (web Relay / Apify). Keys may be absent on
            # older blobs — router maps them to stable camelCase with null/[].
            "is_threads_only_user": (
                bool(threads_only) if isinstance(threads_only, bool) else threads_only
            ),
            "text_post_app_is_private": (
                bool(is_private) if isinstance(is_private, bool) else is_private
            ),
            "transparency_label": user.get("transparency_label")
            if user.get("transparency_label") is not None
            else user.get("transparencyLabel"),
            "bio_links": user.get("bio_links")
            if isinstance(user.get("bio_links"), list)
            else (user.get("bioLinks") if isinstance(user.get("bioLinks"), list) else []),
            "hd_profile_pic_versions": (
                user.get("hd_profile_pic_versions")
                if isinstance(user.get("hd_profile_pic_versions"), list)
                else (
                    user.get("hdProfilePicVersions")
                    if isinstance(user.get("hdProfilePicVersions"), list)
                    else []
                )
            ),
            "has_onboarded_to_text_post_app": (
                bool(onboarded) if isinstance(onboarded, bool) else onboarded
            ),
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

    name = None
    username = handle
    m = re.match(r"^(.*?)\s*\(@([^)]+)\)", title)
    if m:
        name = m.group(1).strip() or None
        username = m.group(2).strip() or handle

    bio = None
    followers = None
    if desc:
        parts = [p.strip() for p in re.split(r"\s*[•\u2022]\s*", desc) if p.strip()]
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


def _unix_to_iso(value: Any) -> str | None:
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return safe_str(value)
    if ts <= 0:
        return None
    if ts > 10_000_000_000:
        ts = ts // 1000
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _media_urls(post: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    def _add(url: str | None) -> None:
        u = safe_str(url)
        if u and u not in seen:
            seen.add(u)
            urls.append(u)

    versions = post.get("video_versions")
    if isinstance(versions, list):
        for item in versions:
            if isinstance(item, dict):
                _add(item.get("url"))

    carousel = post.get("carousel_media")
    if isinstance(carousel, list):
        for item in carousel:
            if not isinstance(item, dict):
                continue
            iv = item.get("image_versions2") if isinstance(item.get("image_versions2"), dict) else {}
            cands = iv.get("candidates") if isinstance(iv.get("candidates"), list) else []
            if cands and isinstance(cands[0], dict):
                _add(cands[0].get("url"))
            vv = item.get("video_versions")
            if isinstance(vv, list) and vv and isinstance(vv[0], dict):
                _add(vv[0].get("url"))

    iv = post.get("image_versions2") if isinstance(post.get("image_versions2"), dict) else {}
    cands = iv.get("candidates") if isinstance(iv.get("candidates"), list) else []
    best = None
    best_w = -1
    for cand in cands:
        if not isinstance(cand, dict):
            continue
        try:
            width = int(cand.get("width") or 0)
        except (TypeError, ValueError):
            width = 0
        url = safe_str(cand.get("url"))
        if url and width >= best_w:
            best = url
            best_w = width
    _add(best)

    info = post.get("text_post_app_info") if isinstance(post.get("text_post_app_info"), dict) else {}
    linked = info.get("linked_inline_media")
    if isinstance(linked, dict):
        liv = linked.get("image_versions2") if isinstance(linked.get("image_versions2"), dict) else {}
        lcands = liv.get("candidates") if isinstance(liv.get("candidates"), list) else []
        if lcands and isinstance(lcands[0], dict):
            _add(lcands[0].get("url"))
    return urls


def _caption_text(post: dict[str, Any]) -> str | None:
    caption = post.get("caption")
    if isinstance(caption, dict):
        return safe_str(caption.get("text"))
    if isinstance(caption, str):
        return safe_str(caption)
    info = post.get("text_post_app_info") if isinstance(post.get("text_post_app_info"), dict) else {}
    frags = ((info.get("text_fragments") or {}).get("fragments") or [])
    parts: list[str] = []
    if isinstance(frags, list):
        for frag in frags:
            if isinstance(frag, dict) and frag.get("plaintext"):
                parts.append(str(frag["plaintext"]))
    return safe_str("".join(parts)) if parts else None


def _normalize_relay_post(post: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(post, dict):
        return None
    code = safe_str(post.get("code"))
    pk = safe_str(post.get("pk") or post.get("id"))
    if not code and not pk:
        return None
    user = post.get("user") if isinstance(post.get("user"), dict) else {}
    info = post.get("text_post_app_info") if isinstance(post.get("text_post_app_info"), dict) else {}
    media = _media_urls(post)
    return {
        "pk": pk,
        "code": code,
        "caption": _caption_text(post),
        "taken_at": _unix_to_iso(post.get("taken_at")),
        "user": {
            "username": safe_str(user.get("username") or user.get("userName")),
            "full_name": safe_str(user.get("full_name") or user.get("fullName") or user.get("name")),
            "is_verified": bool(user.get("is_verified") or user.get("isVerified")),
            "profile_pic_url": _profile_pic(user) or safe_str(user.get("profile_pic_url")),
        },
        "like_count": safe_int(post.get("like_count") or post.get("likeCount")),
        "reply_count": safe_int(info.get("direct_reply_count") or info.get("reply_count")),
        "repost_count": safe_int(info.get("repost_count") or info.get("reshare_count")),
        "quote_count": safe_int(info.get("quote_count")),
        "media": [{"url": u} for u in media],
    }


def _posts_from_thread_items(
    html: str,
    *,
    handle: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Extract unique posts from Relay ``thread_items`` blobs.

    When ``handle`` is set, keep only that author's posts (profile pages).
    When omitted, keep every post (search pages).
    """
    if not html:
        return []
    needle = handle.lower() if handle else None
    capped = max(1, min(int(limit or 20), 100))
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in _THREAD_ITEMS_RE.finditer(html):
        arr_s = _extract_json_array(html, match.end() - 1)
        if not arr_s:
            continue
        try:
            items = json.loads(arr_s)
        except ValueError:
            continue
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            post = item.get("post")
            if not isinstance(post, dict):
                continue
            if needle is not None:
                user = post.get("user") if isinstance(post.get("user"), dict) else {}
                username = safe_str(user.get("username") or user.get("userName"))
                if username and username.lower() != needle:
                    continue
            normalized = _normalize_relay_post(post)
            if not normalized:
                continue
            key = normalized.get("code") or normalized.get("pk")
            if not key or key in seen:
                continue
            seen.add(str(key))
            posts.append(normalized)
            if len(posts) >= capped:
                return posts
    return posts[:capped]


def parse_user_posts_html(html: str, handle: str, limit: int = 20) -> list[dict[str, Any]]:
    """Extract unique posts from Relay ``thread_items`` blobs on a profile page."""
    if not html or not handle:
        return []
    return _posts_from_thread_items(html, handle=handle, limit=limit)


def parse_search_html(html: str, limit: int = 25) -> list[dict[str, Any]]:
    """Extract unique posts from Relay ``thread_items`` on a search results page."""
    return _posts_from_thread_items(html, handle=None, limit=limit)


def parse_post_code(url_or_code: str) -> tuple[str | None, str | None]:
    """Return ``(author, code)`` from a Threads post URL or bare shortcode."""
    raw = (url_or_code or "").strip()
    if not raw:
        return None, None
    m = _POST_URL_RE.search(raw)
    if m:
        author = m.group("author")
        code = m.group("code")
        return (author.lower() if author else None), code
    # bare code
    code = raw.split("/")[-1].split("?")[0].strip()
    if _POST_CODE_RE.fullmatch(code):
        return None, code
    return None, None


def parse_post_html(html: str, code: str) -> dict[str, Any] | None:
    """Extract a single post by shortcode from a permalink page HTML."""
    if not html or not code:
        return None
    needle = code.strip()
    # Prefer thread_items (full engagement payload).
    for match in _THREAD_ITEMS_RE.finditer(html):
        arr_s = _extract_json_array(html, match.end() - 1)
        if not arr_s:
            continue
        try:
            items = json.loads(arr_s)
        except ValueError:
            continue
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            post = item.get("post")
            if not isinstance(post, dict):
                continue
            if safe_str(post.get("code")) != needle:
                continue
            normalized = _normalize_relay_post(post)
            if normalized:
                return normalized
    # Fallback: scan for post objects containing the code.
    for m in re.finditer(r'"code"\s*:\s*"' + re.escape(needle) + r'"', html):
        brace = html.rfind("{", max(0, m.start() - 4000), m.start())
        if brace < 0:
            continue
        raw = _extract_json_object(html, brace)
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(obj, dict) or safe_str(obj.get("code")) != needle:
            continue
        if obj.get("like_count") is None and obj.get("caption") is None and not obj.get("user"):
            continue
        normalized = _normalize_relay_post(obj)
        if normalized:
            return normalized
    return None





async def _fetch_profile_html(handle: str) -> str | None:
    url = f"https://www.threads.net/@{handle}"
    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
        if got:
            status, body = got
            if status == 200 and body and (
                _PROFILE_MARKER in body
                or "thread_items" in body
                or "follower_count" in body
                or "og:title" in body
            ):
                return body
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and len(resp.text) > 2000:
            if (
                _PROFILE_MARKER in resp.text
                or "thread_items" in resp.text
                or "follower_count" in resp.text
            ):
                return resp.text
    except httpx.HTTPError as exc:
        log.info("threads_profile_direct_fail", handle=handle, error=str(exc))
    return None


async def profile_by_handle(handle: str) -> dict[str, Any] | None:
    """Fetch a public Threads profile via hydrated HTML (Decodo -> direct)."""
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


async def user_posts(handle: str, limit: int = 20) -> list[dict[str, Any]] | None:
    """Recent public posts from a Threads profile page (Decodo -> direct)."""
    raw = _normalize_handle(handle)
    if not raw:
        return None
    html = await _fetch_profile_html(raw)
    if not html:
        return None
    posts = parse_user_posts_html(html, raw, limit=limit)
    if not posts:
        log.warning("threads_user_posts_native_parse_miss", handle=raw, length=len(html))
        return None
    log.info("threads_user_posts_native_ok", handle=raw, returned=len(posts))
    return posts

async def _fetch_search_html(query: str) -> str | None:
    from urllib.parse import quote

    q = (query or "").strip()
    if not q:
        return None
    url = f"https://www.threads.net/search?q={quote(q)}&serp_type=default"
    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
        if got:
            status, body = got
            if status == 200 and body and (
                "thread_items" in body
                or "BarcelonaSearchResults" in body
                or "XDTSearchThread" in body
            ):
                return body
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and len(resp.text) > 2000:
            if (
                "thread_items" in resp.text
                or "BarcelonaSearchResults" in resp.text
                or "XDTSearchThread" in resp.text
            ):
                return resp.text
    except httpx.HTTPError as exc:
        log.info("threads_search_direct_fail", query=q[:80], error=str(exc))
    return None


async def search(query: str, limit: int = 25) -> list[dict[str, Any]] | None:
    """Public keyword search via hydrated search-page HTML (Decodo -> direct)."""
    q = (query or "").strip()
    if len(q) < 2:
        return None
    html = await _fetch_search_html(q)
    if not html:
        return None
    posts = parse_search_html(html, limit=limit)
    if not posts:
        log.warning("threads_search_native_parse_miss", query=q[:80], length=len(html))
        return None
    log.info("threads_search_native_ok", query=q[:80], returned=len(posts))
    return posts

async def search_users(query: str, limit: int = 20) -> list[dict[str, Any]] | None:
    """Distinct creators matching a keyword, derived from search-page posts."""
    q = (query or "").strip()
    if len(q) < 2:
        return None
    # Pull a wider post sample so unique authors can fill ``limit``.
    post_limit = max(int(limit or 20) * 4, 25)
    post_limit = min(post_limit, 100)
    posts = await search(q, limit=post_limit)
    if not posts:
        return None
    capped = max(1, min(int(limit or 20), 100))
    users: list[dict[str, Any]] = []
    seen: set[str] = set()
    for post in posts:
        user = post.get("user") if isinstance(post.get("user"), dict) else {}
        username = safe_str(user.get("username") or user.get("userName"))
        if not username or username in seen:
            continue
        seen.add(username)
        users.append(
            {
                "username": username,
                "full_name": safe_str(user.get("full_name") or user.get("fullName") or user.get("name")),
                "is_verified": bool(user.get("is_verified") or user.get("isVerified")),
                "profile_pic_url": safe_str(user.get("profile_pic_url") or user.get("profilePicUrl")),
                "url": f"https://www.threads.net/@{username}",
            }
        )
        if len(users) >= capped:
            break
    if not users:
        log.warning("threads_search_users_native_empty", query=q[:80], posts=len(posts))
        return None
    log.info("threads_search_users_native_ok", query=q[:80], returned=len(users))
    return users

async def _fetch_post_html(author: str | None, code: str) -> str | None:
    if author:
        url = f"https://www.threads.net/@{author}/post/{code}"
    else:
        url = f"https://www.threads.net/t/{code}"
    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
        if got:
            status, body = got
            if status == 200 and body and (
                code in body
                or "BarcelonaPostPageDirectQuery" in body
                or "thread_items" in body
            ):
                return body
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and len(resp.text) > 2000 and (
            code in resp.text
            or "BarcelonaPostPageDirectQuery" in resp.text
            or "thread_items" in resp.text
        ):
            return resp.text
    except httpx.HTTPError as exc:
        log.info("threads_post_direct_fail", code=code, error=str(exc))
    return None


async def post_details(url_or_code: str) -> dict[str, Any] | None:
    """Public post metadata via hydrated permalink HTML (Decodo -> direct)."""
    author, code = parse_post_code(url_or_code)
    if not code:
        return None
    html = await _fetch_post_html(author, code)
    if not html and author:
        # Retry short /t/CODE form when author URL failed.
        html = await _fetch_post_html(None, code)
    if not html:
        return None
    parsed = parse_post_html(html, code)
    if not parsed:
        log.warning("threads_post_native_parse_miss", code=code, length=len(html))
        return None
    log.info(
        "threads_post_native_ok",
        code=code,
        likes=parsed.get("like_count"),
        author=(parsed.get("user") or {}).get("username"),
    )
    return parsed

