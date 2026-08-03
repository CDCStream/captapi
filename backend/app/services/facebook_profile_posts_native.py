"""Native Facebook profile/page posts via Decodo.

Logged-out page HTML only embeds ~1 full Story. We scroll to collect post/reel
permalinks, reuse any Story already in the HTML, then hydrate the rest with
``facebook_details_native`` (same Decodo Pathfinder blobs). No Apify.
"""

from __future__ import annotations

import asyncio
import re
import time
from typing import Any
from urllib.parse import urlparse

import structlog

from app.services import decodo_fetch, facebook_details_native
from app.utils.formatters import safe_str, strip_empty

log = structlog.get_logger(__name__)

# One scrolled listing + a handful of detail hydrations; flat fee.
CREDIT_FB_PROFILE_POSTS_NATIVE = 2

_SCROLL_ACTIONS: list[dict[str, Any]] = [
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
]

# Bound Decodo fan-out; one scroll rarely surfaces more than this anyway.
_MAX_HYDRATE = 30
_HYDRATE_CONCURRENCY = 3


def _page_slug(url: str) -> str | None:
    path = urlparse(url).path or ""
    parts = [p for p in path.split("/") if p]
    skip = {"pages", "people", "profile.php", "pg", "public", "posts", "photos", "reels", "videos"}
    for part in parts:
        if part.lower() in skip or part.isdigit() or part.startswith("pfbid"):
            continue
        return part
    return None


def _norm_url(url: str) -> str:
    u = (url or "").replace("\\/", "/").split("?")[0].rstrip("/")
    u = u.replace("://m.facebook.com", "://www.facebook.com")
    return u


def _extract_post_urls(html: str, page_url: str) -> list[str]:
    text = html.replace("\\/", "/")
    slug = (_page_slug(page_url) or "").lower()
    found: list[str] = []

    for m in re.finditer(
        r"https://(?:www|m)\.facebook\.com/([^/\"'\s<>]+)/posts/(pfbid[\w]+)",
        text,
        re.I,
    ):
        owner, token = m.group(1), m.group(2)
        if slug and owner.lower() != slug:
            continue
        found.append(f"https://www.facebook.com/{owner}/posts/{token}")

    for m in re.finditer(r"https://(?:www|m)\.facebook\.com/reel/(\d+)", text, re.I):
        found.append(f"https://www.facebook.com/reel/{m.group(1)}")

    # Relative paths
    if slug:
        for m in re.finditer(rf"/{re.escape(slug)}/posts/(pfbid[\w]+)", text, re.I):
            found.append(f"https://www.facebook.com/{slug}/posts/{m.group(1)}")
    for m in re.finditer(r"/reel/(\d+)", text):
        found.append(f"https://www.facebook.com/reel/{m.group(1)}")

    out: list[str] = []
    seen: set[str] = set()
    for url in found:
        n = _norm_url(url)
        if n in seen:
            continue
        seen.add(n)
        out.append(n)
    return out


def _inline_raw_posts(html: str, page_url: str) -> list[dict[str, Any]]:
    """Map full Story / creation_story nodes already present in the listing HTML."""
    blobs = facebook_details_native._load_blobs(html)
    signals = facebook_details_native._url_signals(page_url)
    # Preserve vanity casing from the request URL ("NASA" vs "nasa"). Lowercase
    # only for membership checks — stamping .lower() into pageUsername made
    # Story rows disagree with Reel rows that keep Facebook's URL casing.
    slug_raw = _page_slug(page_url) or ""
    slug = slug_raw.lower()
    raws: list[dict[str, Any]] = []
    seen: set[str] = set()

    creation: list[dict[str, Any]] = []
    facebook_details_native._walk(
        blobs,
        lambda o: isinstance(o.get("creation_story"), dict)
        and isinstance(o["creation_story"].get("short_form_video_context"), dict),
        creation,
        limit=40,
    )
    for wrap in creation:
        cs = wrap["creation_story"]
        item = facebook_details_native._from_creation_story(cs, blobs, page_url)
        pid = safe_str(item.get("postId") or item.get("post_id"))
        if pid and pid not in seen:
            seen.add(pid)
            raws.append(item)

    stories: list[dict[str, Any]] = []
    facebook_details_native._walk(
        blobs,
        lambda o: o.get("__typename") == "Story" and o.get("post_id") and o.get("permalink_url"),
        stories,
        limit=60,
    )
    for st in stories:
        permalink = (safe_str(st.get("permalink_url")) or "").lower()
        if slug and slug not in permalink and "/reel/" not in permalink:
            # Keep reel permalinks even when slug missing from path.
            actors = st.get("actors") if isinstance(st.get("actors"), list) else []
            actor_ok = False
            for actor in actors[:2]:
                if isinstance(actor, dict) and slug in (safe_str(actor.get("url")) or "").lower():
                    actor_ok = True
                    break
            if not actor_ok:
                continue
        item = facebook_details_native._from_story(st, blobs, page_url)
        if slug_raw:
            existing = safe_str(item.get("pageUsername"))
            # Fill gaps only — never overwrite actor/URL casing with a lowercased slug.
            if not existing:
                item["pageUsername"] = slug_raw
            user = item.get("user") if isinstance(item.get("user"), dict) else {}
            if not user.get("username"):
                user["username"] = existing or slug_raw
                item["user"] = user
        pid = safe_str(item.get("postId") or item.get("post_id"))
        if pid and pid not in seen and (item.get("text") or item.get("media") or item.get("short_form_video_context")):
            seen.add(pid)
            raws.append(item)

    # silence unused
    _ = signals
    return raws


async def _hydrate_url(url: str, sem: asyncio.Semaphore) -> dict[str, Any] | None:
    async with sem:
        return await facebook_details_native.details_native(url)


async def profile_posts_native(url: str, limit: int) -> list[dict[str, Any]] | None:
    """Return raw post dicts for ``_normalize_post`` (newest-first), or None.

    Wall-clock budget (~45s): if inline posts are already available, skip the
    expensive per-URL hydrate rather than sitting until the 180s client timeout.
    """
    if limit <= 0:
        return []
    if not url or not decodo_fetch.enabled():
        return None

    t0 = time.monotonic()
    budget_s = 45.0
    # Cap the Decodo page fetch so we leave room to return inline posts.
    page_timeout = min(40.0, budget_s)

    got = await decodo_fetch.fetch_url(
        url,
        timeout=page_timeout,
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
    # Prefer URLs not already covered by inline post ids / permalinks.
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

    # Enough inline posts and budget nearly spent → return partial (no hydrate).
    elapsed = time.monotonic() - t0
    if inline and (elapsed >= budget_s * 0.7 or (len(inline) >= limit and elapsed >= 20)):
        need = []

    hydrated: list[dict[str, Any]] = []
    if need and time.monotonic() - t0 < budget_s:
        sem = asyncio.Semaphore(_HYDRATE_CONCURRENCY)
        rows = await asyncio.gather(*[_hydrate_url(u, sem) for u in need])
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
        log.info("facebook_profile_posts_native_empty", url=url[:120])
        return None

    # Sort by creation_time desc when present.
    def _ts(item: dict[str, Any]) -> int:
        for key in ("creation_time", "publish_time"):
            val = item.get(key)
            if isinstance(val, (int, float)) and val > 0:
                return int(val)
        short = item.get("short_form_video_context")
        if isinstance(short, dict):
            playback = short.get("playback_video")
            if isinstance(playback, dict):
                for key in ("publish_time", "creation_time"):
                    val = playback.get(key)
                    if isinstance(val, (int, float)) and val > 0:
                        return int(val)
        return 0

    raws.sort(key=_ts, reverse=True)
    out = raws[:limit]
    log.info(
        "facebook_profile_posts_native_ok",
        url=url[:120],
        inline=len(inline),
        hydrated=len(hydrated),
        returned=len(out),
    )
    return out
