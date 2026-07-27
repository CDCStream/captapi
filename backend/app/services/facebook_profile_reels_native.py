"""Native Facebook profile/page Reels via Decodo.

Logged-out `/reels` is a login wall. The public `/videos` tab embeds many
video permalinks whose numeric ids resolve as `/reel/{id}` with the same
``short_form_video_context`` blobs ``details_native`` already hydrates.
No Apify.
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

CREDIT_FB_PROFILE_REELS_NATIVE = 2

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


def _page_slug(url: str) -> str | None:
    path = urlparse(url).path or ""
    parts = [p for p in path.split("/") if p]
    skip = {
        "pages", "people", "profile.php", "pg", "public", "posts",
        "photos", "reels", "videos", "watch", "events",
    }
    for part in parts:
        if part.lower() in skip or part.isdigit() or part.startswith("pfbid"):
            continue
        return part
    return None


def _videos_url(page_url: str) -> str:
    slug = _page_slug(page_url)
    if slug:
        return f"https://www.facebook.com/{slug}/videos"
    return page_url.rstrip("/") + "/videos"


def _extract_reel_ids(html: str, page_url: str) -> list[str]:
    text = html.replace("\\/", "/")
    slug = (_page_slug(page_url) or "").lower()
    ids: list[str] = []

    for m in re.finditer(r"https://(?:www|m)\.facebook\.com/reel/(\d{8,})", text, re.I):
        ids.append(m.group(1))
    for m in re.finditer(r"/reel/(\d{8,})", text):
        ids.append(m.group(1))

    if slug:
        for m in re.finditer(
            rf"https://(?:www|m)\.facebook\.com/{re.escape(slug)}/videos/[^/\"'\s<>]+/(\d{{8,}})",
            text,
            re.I,
        ):
            ids.append(m.group(1))
        for m in re.finditer(rf"/{re.escape(slug)}/videos/[^/\"'\s<>]+/(\d{{8,}})", text, re.I):
            ids.append(m.group(1))

    out: list[str] = []
    seen: set[str] = set()
    for vid in ids:
        if vid in seen:
            continue
        seen.add(vid)
        out.append(vid)
    return out


def _is_reel_raw(item: dict[str, Any]) -> bool:
    if isinstance(item.get("short_form_video_context"), dict):
        return True
    u = (safe_str(item.get("url") or item.get("facebookUrl") or "")).lower()
    return "/reel/" in u or "/reels/" in u


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


async def _hydrate_reel(vid: str, sem: asyncio.Semaphore) -> dict[str, Any] | None:
    async with sem:
        raw = await facebook_details_native.details_native(
            f"https://www.facebook.com/reel/{vid}"
        )
        if isinstance(raw, dict) and _is_reel_raw(raw):
            return raw
        return None


async def profile_reels_native(url: str, limit: int) -> list[dict[str, Any]] | None:
    """Return raw reel dicts for ``_normalize_post`` (newest-first), or None."""
    if limit <= 0:
        return []
    if not url or not decodo_fetch.enabled():
        return None

    listing_url = _videos_url(url)
    got = await decodo_fetch.fetch_url(
        listing_url,
        timeout=180.0,
        headless="html",
        browser_actions=_SCROLL_ACTIONS,
    )
    if not got:
        return None
    status, html = got
    if status != 200 or not html:
        return None

    ids = _extract_reel_ids(html, url)
    # If the videos tab is thin, also mine /reel/ links from the profile home.
    if len(ids) < min(limit, _MAX_HYDRATE):
        home = await decodo_fetch.fetch_url(
            url,
            timeout=120.0,
            headless="html",
            browser_actions=_SCROLL_ACTIONS[:6],
        )
        if home and home[0] == 200 and home[1]:
            for vid in _extract_reel_ids(home[1], url):
                if vid not in ids:
                    ids.append(vid)

    if not ids:
        log.info("facebook_profile_reels_native_empty", url=url[:120])
        return None

    need = ids[: min(limit, _MAX_HYDRATE)]
    sem = asyncio.Semaphore(_HYDRATE_CONCURRENCY)
    rows = await asyncio.gather(*[_hydrate_reel(vid, sem) for vid in need])
    raws = [r for r in rows if isinstance(r, dict)]
    if not raws:
        log.info("facebook_profile_reels_native_hydrate_empty", url=url[:120], ids=len(ids))
        return None

    raws.sort(key=_ts, reverse=True)
    out = raws[:limit]
    log.info(
        "facebook_profile_reels_native_ok",
        url=url[:120],
        ids=len(ids),
        hydrated=len(raws),
        returned=len(out),
    )
    return out
