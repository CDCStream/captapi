"""URL extraction helpers for each social platform."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

YOUTUBE_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/|v/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)

TIKTOK_VIDEO_RE = re.compile(r"tiktok\.com/(?:@[\w.-]+/video|v)/(\d+)")
TIKTOK_USER_RE = re.compile(r"tiktok\.com/@([\w.-]+)")

INSTAGRAM_POST_RE = re.compile(r"instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)")
INSTAGRAM_USER_RE = re.compile(r"instagram\.com/([A-Za-z0-9_.]+)(?:/|$)")

FACEBOOK_VIDEO_RE = re.compile(
    r"facebook\.com/(?:[\w.]+/videos/|watch/?\?v=|reel/)(\d+)"
)
FACEBOOK_PAGE_RE = re.compile(r"facebook\.com/([A-Za-z0-9.\-_]+)/?")


def extract_youtube_id(url: str) -> str | None:
    m = YOUTUBE_RE.search(url or "")
    if m:
        return m.group(1)
    try:
        qs = parse_qs(urlparse(url).query)
        v = qs.get("v", [None])[0]
        if v and len(v) == 11:
            return v
    except Exception:
        pass
    return None


def normalize_youtube_url(url: str) -> str:
    vid = extract_youtube_id(url)
    return f"https://www.youtube.com/watch?v={vid}" if vid else url


def is_youtube_short(url: str) -> bool:
    return "/shorts/" in (url or "")


def extract_tiktok_id(url: str) -> str | None:
    m = TIKTOK_VIDEO_RE.search(url or "")
    return m.group(1) if m else None


def extract_tiktok_username(url: str) -> str | None:
    m = TIKTOK_USER_RE.search(url or "")
    return m.group(1) if m else None


def extract_instagram_shortcode(url: str) -> str | None:
    m = INSTAGRAM_POST_RE.search(url or "")
    return m.group(1) if m else None


def extract_instagram_username(url: str) -> str | None:
    m = INSTAGRAM_USER_RE.search(url or "")
    if not m:
        return None
    handle = m.group(1)
    if handle in {"p", "reel", "tv", "explore"}:
        return None
    return handle


def extract_facebook_video_id(url: str) -> str | None:
    m = FACEBOOK_VIDEO_RE.search(url or "")
    return m.group(1) if m else None


def extract_facebook_page(url: str) -> str | None:
    m = FACEBOOK_PAGE_RE.search(url or "")
    return m.group(1) if m else None
