"""Native Facebook public group posts via Decodo.

Scroll the group feed HTML for ``/posts/{id}`` / ``/permalink/{id}`` links,
reuse any Story already embedded, then hydrate the rest with
``facebook_details_native``. No Apify.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any
from urllib.parse import urlparse

import structlog

from app.services import decodo_fetch, facebook_details_native
from app.utils.formatters import safe_str

log = structlog.get_logger(__name__)

CREDIT_FB_GROUP_POSTS_NATIVE = 2

_SCROLL_ACTIONS: list[dict[str, Any]] = [
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 3000},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 3000},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 4000},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 4000},
    {"type": "wait", "wait_time_s": 2},
]

_MAX_HYDRATE = 30
_HYDRATE_CONCURRENCY = 3


def _group_key(url: str) -> str | None:
    path = urlparse(url).path or ""
    m = re.search(r"/groups/([^/?#]+)", path, re.I)
    return m.group(1) if m else None


def _norm_url(url: str) -> str:
    u = (url or "").replace("\\/", "/").split("?")[0].rstrip("/")
    u = u.replace("://m.facebook.com", "://www.facebook.com")
    # Prefer /posts/ over /permalink/ for the same id.
    u = re.sub(r"/permalink/(\d+)$", r"/posts/\1", u, flags=re.I)
    return u


def _extract_post_urls(html: str, group_url: str) -> list[str]:
    text = html.replace("\\/", "/")
    key = _group_key(group_url) or ""
    found: list[str] = []

    patterns = [
        r"https://(?:www|m)\.facebook\.com/groups/([^/\"'\s<>]+)/(?:posts|permalink)/(\d+)",
        r"/groups/([^/\"'\s<>]+)/(?:posts|permalink)/(\d+)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.I):
            gkey, pid = m.group(1), m.group(2)
            if key and gkey.lower() != key.lower():
                continue
            found.append(f"https://www.facebook.com/groups/{gkey}/posts/{pid}")

    out: list[str] = []
    seen: set[str] = set()
    for url in found:
        n = _norm_url(url)
        if n in seen:
            continue
        seen.add(n)
        out.append(n)
    return out


def _inline_raw_posts(html: str, group_url: str) -> list[dict[str, Any]]:
    blobs = facebook_details_native._load_blobs(html)
    key = (_group_key(group_url) or "").lower()
    raws: list[dict[str, Any]] = []
    seen: set[str] = set()

    stories: list[dict[str, Any]] = []
    facebook_details_native._walk(
        blobs,
        lambda o: o.get("__typename") == "Story" and o.get("post_id") and o.get("permalink_url"),
        stories,
        limit=60,
    )
    for st in stories:
        permalink = (safe_str(st.get("permalink_url")) or "").lower()
        if key and f"/groups/{key}/" not in permalink:
            continue
        item = facebook_details_native._from_story(st, blobs, group_url)
        pid = safe_str(item.get("postId") or item.get("post_id"))
        if pid and pid not in seen and (item.get("text") or item.get("media") or item.get("thumbnailUrl")):
            seen.add(pid)
            raws.append(item)
    return raws


def _ts(item: dict[str, Any]) -> int:
    for key in ("creation_time", "publish_time"):
        val = item.get(key)
        if isinstance(val, (int, float)) and val > 0:
            return int(val)
    return 0


async def _hydrate(url: str, sem: asyncio.Semaphore) -> dict[str, Any] | None:
    async with sem:
        return await facebook_details_native.details_native(url)


async def group_posts_native(url: str, limit: int) -> list[dict[str, Any]] | None:
    """Return raw post dicts for ``_normalize_post`` (newest-first), or None."""
    if limit <= 0:
        return []
    if not url or not decodo_fetch.enabled():
        return None
    if "/groups/" not in (url or "").lower():
        return None

    got = await decodo_fetch.fetch_url(
        url,
        timeout=180.0,
        headless="html",
        browser_actions=_SCROLL_ACTIONS,
    )
    if not got:
        return None
    status, html = got
    if status != 200 or not html:
        return None

    inline = _inline_raw_posts(html, url)
    urls = _extract_post_urls(html, url)
    inline_urls = {
        _norm_url(safe_str(i.get("url") or i.get("facebookUrl") or ""))
        for i in inline
    }
    inline_ids = {
        safe_str(i.get("postId") or i.get("post_id"))
        for i in inline
        if safe_str(i.get("postId") or i.get("post_id"))
    }

    need: list[str] = []
    for u in urls:
        if u in inline_urls:
            continue
        need.append(u)

    hydrate_n = max(0, min(limit, _MAX_HYDRATE) - len(inline))
    need = need[:hydrate_n]

    hydrated: list[dict[str, Any]] = []
    if need:
        sem = asyncio.Semaphore(_HYDRATE_CONCURRENCY)
        rows = await asyncio.gather(*[_hydrate(u, sem) for u in need])
        for row in rows:
            if not isinstance(row, dict):
                continue
            pid = safe_str(row.get("postId") or row.get("post_id"))
            if pid and pid in inline_ids:
                continue
            if pid:
                inline_ids.add(pid)
            hydrated.append(row)

    raws = inline + hydrated
    if not raws:
        log.info("facebook_group_posts_native_empty", url=url[:120])
        return None

    raws.sort(key=_ts, reverse=True)
    out = raws[:limit]
    log.info(
        "facebook_group_posts_native_ok",
        url=url[:120],
        inline=len(inline),
        hydrated=len(hydrated),
        returned=len(out),
    )
    return out
