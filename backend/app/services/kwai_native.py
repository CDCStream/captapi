"""Kwai public pages via Decodo HTML (schema.org JSON-LD). No Apify."""

from __future__ import annotations

import json
import re
from typing import Any

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(\{.*?\})</script>',
    re.S | re.I,
)
_DURATION_RE = re.compile(
    r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
    re.I,
)


def _ld_blocks(html: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for match in _LD_RE.finditer(html or ""):
        raw = (match.group(1) or "").strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            out.append(data)
        elif isinstance(data, list):
            out.extend(x for x in data if isinstance(x, dict))
    return out


def _interaction_count(stats: Any, action: str) -> int | None:
    rows = stats if isinstance(stats, list) else ([stats] if isinstance(stats, dict) else [])
    needle = action.lower()
    for row in rows:
        if not isinstance(row, dict):
            continue
        itype = row.get("interactionType")
        label = ""
        if isinstance(itype, dict):
            label = str(itype.get("@type") or "")
        elif isinstance(itype, str):
            label = itype
        if needle in label.lower():
            return safe_int(row.get("userInteractionCount"))
    return None


def _duration_seconds(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    text = safe_str(value) or ""
    match = _DURATION_RE.fullmatch(text.strip())
    if not match:
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    total = hours * 3600 + minutes * 60 + seconds
    return total or None


def _thumb(value: Any) -> str | None:
    if isinstance(value, list) and value:
        return safe_str(value[0])
    return safe_str(value)


def _author_meta_from_person(person: dict[str, Any], fallback_url: str | None = None) -> dict[str, Any]:
    handle = safe_str(person.get("alternateName")) or safe_str(person.get("name"))
    url = safe_str(person.get("url")) or fallback_url
    if not url and handle:
        url = f"https://www.kwai.com/@{handle.lstrip('@')}"
    stats = person.get("interactionStatistic")
    agent = person.get("agentInteractionStatistic")
    videos = None
    if isinstance(agent, dict):
        videos = safe_int(agent.get("userInteractionCount"))
    return {
        "id": safe_str(person.get("identifier")),
        "username": handle.lstrip("@") if handle else None,
        "name": safe_str(person.get("name")),
        "url": url,
        "avatar": safe_str(person.get("image")),
        "followersCount": _interaction_count(stats, "FollowAction"),
        "likesCount": _interaction_count(stats, "LikeAction"),
        "videosCount": videos,
    }


def _video_id(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"/(?:video|photo)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None


def _post_from_video_ld(video: dict[str, Any], *, profile_url: str | None = None) -> dict[str, Any] | None:
    url = safe_str(video.get("url"))
    if not url:
        return None
    creator = video.get("creator") if isinstance(video.get("creator"), dict) else {}
    person = creator.get("mainEntity") if isinstance(creator.get("mainEntity"), dict) else creator
    if not isinstance(person, dict):
        person = {}
    author = _author_meta_from_person(person, fallback_url=profile_url)
    stats = video.get("interactionStatistic")
    caption = safe_str(video.get("description"))
    if caption in (None, ".", "...", "…"):
        caption = safe_str(video.get("transcript")) or safe_str(video.get("name"))
    return {
        "id": _video_id(url),
        "url": url,
        "caption": caption,
        "transcript": safe_str(video.get("transcript")),
        "createTime": safe_str(video.get("uploadDate")),
        "duration": _duration_seconds(video.get("duration")),
        "thumb": _thumb(video.get("thumbnailUrl")),
        "playUrl": safe_str(video.get("contentUrl")),
        "viewCount": _interaction_count(stats, "WatchAction"),
        "likeCount": _interaction_count(stats, "LikeAction"),
        "commentCount": safe_int(video.get("commentCount")),
        "shareCount": _interaction_count(stats, "ShareAction"),
        "authorMeta": author,
        "status": "ok",
    }


async def _fetch_html(url: str) -> str | None:
    if not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=90.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body or len(body) < 500:
        return None
    return body


async def fetch_profile(profile_url: str) -> dict[str, Any] | None:
    """Actor-shaped row with ``authorMeta`` for router ``_normalize_profile``."""
    html = await _fetch_html(profile_url)
    if not html:
        return None
    person: dict[str, Any] | None = None
    for block in _ld_blocks(html):
        if block.get("@type") == "ProfilePage":
            entity = block.get("mainEntity")
            if isinstance(entity, dict) and entity.get("@type") == "Person":
                person = entity
                break
        if block.get("@type") == "Person":
            person = block
            break
    if not person:
        log.info("kwai_native_profile_empty", url=profile_url[:120])
        return None
    author = _author_meta_from_person(person, fallback_url=profile_url)
    if not author.get("username") and not author.get("name"):
        return None
    log.info(
        "kwai_native_profile_ok",
        username=author.get("username"),
        followers=author.get("followersCount"),
    )
    return {"authorMeta": author, "status": "ok"}


async def fetch_user_posts(profile_url: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    """Posts from profile CollectionPage / ItemList JSON-LD."""
    if limit <= 0:
        return None
    html = await _fetch_html(profile_url)
    if not html:
        return None
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for block in _ld_blocks(html):
        if block.get("@type") == "BreadcrumbList":
            continue
        elements = block.get("itemListElement")
        if not isinstance(elements, list):
            continue
        for el in elements:
            if not isinstance(el, dict):
                continue
            # CollectionPage wraps VideoObject-like items directly.
            if el.get("@type") in ("ListItem", None) and not el.get("contentUrl") and not el.get("url"):
                continue
            row = _post_from_video_ld(el, profile_url=profile_url)
            if not row or not row.get("url"):
                continue
            key = str(row.get("id") or row["url"])
            if key in seen:
                continue
            seen.add(key)
            posts.append(row)
            if len(posts) >= limit:
                break
        if len(posts) >= limit:
            break
    if not posts:
        log.info("kwai_native_posts_empty", url=profile_url[:120])
        return None
    log.info("kwai_native_posts_ok", n=len(posts), url=profile_url[:120])
    return posts[:limit]


async def fetch_post(video_url: str) -> dict[str, Any] | None:
    """Single video page → actor-shaped post row."""
    html = await _fetch_html(video_url)
    if not html:
        return None
    for block in _ld_blocks(html):
        if block.get("@type") == "VideoObject" or block.get("contentUrl"):
            row = _post_from_video_ld(block, profile_url=None)
            if row and (row.get("playUrl") or row.get("thumb") or row.get("transcript")):
                log.info("kwai_native_post_ok", id=row.get("id"))
                return row
    log.info("kwai_native_post_empty", url=video_url[:120])
    return None