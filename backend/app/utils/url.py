"""URL extraction helpers for each social platform."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

PLATFORM_HOST_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("youtube", ("youtube.com", "youtu.be")),
    ("tiktok", ("tiktok.com",)),
    ("instagram", ("instagram.com",)),
    ("facebook", ("facebook.com", "fb.watch")),
    ("twitter", ("twitter.com", "x.com")),
    ("reddit", ("reddit.com",)),
    ("threads", ("threads.net", "threads.com")),
    ("bluesky", ("bsky.app",)),
    ("pinterest", ("pinterest.",)),
    ("linkedin", ("linkedin.com",)),
    ("rumble", ("rumble.com",)),
    ("twitch", ("twitch.tv",)),
    ("spotify", ("spotify.com",)),
    ("soundcloud", ("soundcloud.com",)),
    ("google_ad_library", ("adstransparency.google.com",)),
    ("linktree", ("linktr.ee", "linktree.com")),
    ("snapchat", ("snapchat.com",)),
    ("truth_social", ("truthsocial.com",)),
    ("kick", ("kick.com",)),
    ("amazon_shop", ("amazon.",)),
    ("kwai", ("kwai.com", "kuaishou.com")),
    ("komi", ("komi.io",)),
    ("pillar", ("pillar.io",)),
    ("linkbio", ("lnk.bio",)),
    ("linkme", ("link.me",)),
)
PLATFORM_DISPLAY_NAMES = {
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "twitter": "X/Twitter",
    "reddit": "Reddit",
    "threads": "Threads",
    "bluesky": "Bluesky",
    "pinterest": "Pinterest",
    "linkedin": "LinkedIn",
    "rumble": "Rumble",
    "twitch": "Twitch",
    "spotify": "Spotify",
    "soundcloud": "SoundCloud",
    "google_ad_library": "Google Ads Transparency Center",
    "linktree": "Linktree",
    "snapchat": "Snapchat",
    "truth_social": "Truth Social",
    "kick": "Kick",
    "amazon_shop": "Amazon Shop",
    "kwai": "Kwai",
    "komi": "Komi",
    "pillar": "Pillar",
    "linkbio": "Linkbio",
    "linkme": "Linkme",
}

YOUTUBE_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/|v/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)

TIKTOK_VIDEO_RE = re.compile(r"tiktok\.com/(?:@[\w.-]+/video|v)/(\d+)")
TIKTOK_USER_RE = re.compile(r"tiktok\.com/@([\w.-]+)")

# `reels` (plural) is the URL Instagram's web reels viewer produces.
INSTAGRAM_POST_RE = re.compile(r"instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)")
INSTAGRAM_USER_RE = re.compile(r"instagram\.com/([A-Za-z0-9_.]+)(?:/|$)")

FACEBOOK_VIDEO_RE = re.compile(
    r"facebook\.com/(?:[\w.]+/videos/|watch/?\?v=|reel/)(\d+)"
)
FACEBOOK_PAGE_RE = re.compile(r"facebook\.com/([A-Za-z0-9.\-_]+)/?")

# Twitter / X. Tweets live at /{user}/status/{id}; profiles at /{user}.
TWITTER_TWEET_RE = re.compile(r"(?:twitter\.com|x\.com)/[A-Za-z0-9_]+/status/(\d+)")
TWITTER_USER_RE = re.compile(r"(?:twitter\.com|x\.com)/([A-Za-z0-9_]{1,15})")
# Paths under x.com that are not usernames.
_TWITTER_RESERVED = {
    "i", "home", "search", "explore", "notifications", "messages",
    "settings", "compose", "hashtag", "intent", "share", "status",
}


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


def detect_url_platform(value: str) -> str | None:
    """Best-effort platform detection from a public URL's hostname."""
    if not value:
        return None
    try:
        parsed = urlparse(value if "://" in value else f"https://{value}")
        host = (parsed.netloc or "").lower()
    except Exception:
        host = ""
    if not host:
        return None
    for platform, hints in PLATFORM_HOST_HINTS:
        if any(hint in host for hint in hints):
            return platform
    return None


def _article(label: str) -> str:
    return "an" if label[:1].lower() in {"a", "e", "i", "o", "u"} else "a"


def platform_mismatch_detail(value: str, expected: str, expected_example: str) -> str:
    detected = detect_url_platform(value)
    expected_label = PLATFORM_DISPLAY_NAMES.get(expected, expected.title())
    expected_article = _article(expected_label)
    if detected and detected != expected:
        detected_label = PLATFORM_DISPLAY_NAMES.get(detected, detected.title())
        return (
            f"Expected {expected_article} {expected_label} URL, but received {_article(detected_label)} {detected_label} URL. "
            f"Use the {detected_label} endpoint for that URL, or pass {expected_article} {expected_label} URL "
            f"like {expected_example}."
        )
    return f"Invalid {expected_label} URL. Pass {expected_article} {expected_label} URL like {expected_example}."


def is_youtube_short(url: str) -> bool:
    return "/shorts/" in (url or "")


YOUTUBE_CHANNEL_ID_RE = re.compile(r"^UC[A-Za-z0-9_-]{22}$")


def normalize_youtube_channel_url(value: str) -> str:
    """Accept a channel URL, @handle, bare handle, or UC... channel ID.

    Returns a canonical youtube.com URL the scraping actors understand;
    anything unrecognized is passed through untouched.
    """
    raw = (value or "").strip()
    if not raw:
        return raw
    if "youtube.com" in raw or "youtu.be" in raw:
        return raw
    if _is_foreign_platform(raw, "youtube"):
        return raw
    if YOUTUBE_CHANNEL_ID_RE.fullmatch(raw):
        return f"https://www.youtube.com/channel/{raw}"
    handle = raw.lstrip("@")
    if re.fullmatch(r"[\w.-]{3,30}", handle):
        return f"https://www.youtube.com/@{handle}"
    return raw


def _is_foreign_platform(value: str, expected: str) -> bool:
    """True when the input is recognizably a URL for a different platform."""
    detected = detect_url_platform(value)
    return bool(detected and detected != expected)


def extract_tiktok_id(url: str) -> str | None:
    m = TIKTOK_VIDEO_RE.search(url or "")
    return m.group(1) if m else None


def extract_tiktok_username(url: str) -> str | None:
    m = TIKTOK_USER_RE.search(url or "")
    if m:
        return m.group(1)
    raw = (url or "").strip()
    if "/" in raw or _is_foreign_platform(raw, "tiktok"):
        return None
    raw = raw.lstrip("@")
    if re.fullmatch(r"[\w.-]{2,24}", raw):
        return raw
    return None


def extract_instagram_shortcode(url: str) -> str | None:
    m = INSTAGRAM_POST_RE.search(url or "")
    return m.group(1) if m else None


def extract_instagram_username(url: str) -> str | None:
    m = INSTAGRAM_USER_RE.search(url or "")
    if m:
        handle = m.group(1)
        if handle in {"p", "reel", "reels", "tv", "explore", "stories"}:
            return None
        return handle
    # Also accept a bare handle or @handle (AI agents often skip the URL).
    raw = (url or "").strip()
    if "/" in raw or _is_foreign_platform(raw, "instagram"):
        return None
    raw = raw.lstrip("@")
    if re.fullmatch(r"[A-Za-z0-9_.]{1,30}", raw):
        return raw
    return None


def extract_facebook_video_id(url: str) -> str | None:
    m = FACEBOOK_VIDEO_RE.search(url or "")
    return m.group(1) if m else None


def extract_facebook_page(url: str) -> str | None:
    m = FACEBOOK_PAGE_RE.search(url or "")
    if m:
        return m.group(1)
    raw = (url or "").strip()
    if "/" in raw or _is_foreign_platform(raw, "facebook"):
        return None
    raw = raw.lstrip("@")
    if re.fullmatch(r"[A-Za-z0-9.\-_]{3,60}", raw):
        return raw
    return None


def normalize_facebook_page_url(value: str) -> str:
    """Accept a page URL, @handle, or bare page name; return a full URL."""
    raw = (value or "").strip()
    if "facebook.com" in raw or "fb.watch" in raw:
        return raw
    page = extract_facebook_page(raw)
    return f"https://www.facebook.com/{page}" if page else raw


def extract_tweet_id(url: str) -> str | None:
    m = TWITTER_TWEET_RE.search(url or "")
    return m.group(1) if m else None


def extract_twitter_username(url: str) -> str | None:
    m = TWITTER_USER_RE.search(url or "")
    if not m:
        return None
    handle = m.group(1)
    return None if handle.lower() in _TWITTER_RESERVED else handle


def normalize_twitter_username(value: str) -> str | None:
    """Accept a profile URL, @handle, or bare handle and return the handle."""
    if not value:
        return None
    value = value.strip()
    if "twitter.com" in value or "x.com" in value:
        return extract_twitter_username(value)
    handle = value.lstrip("@")
    if re.fullmatch(r"[A-Za-z0-9_]{1,15}", handle):
        return handle
    return None


# --- Reddit ----------------------------------------------------------------
REDDIT_POST_RE = re.compile(r"reddit\.com/r/[A-Za-z0-9_]+/comments/([A-Za-z0-9]+)")
REDDIT_SUBREDDIT_RE = re.compile(r"reddit\.com/r/([A-Za-z0-9_]+)")
REDDIT_USER_RE = re.compile(r"reddit\.com/u(?:ser)?/([A-Za-z0-9_\-]+)")


def extract_reddit_post_id(url: str) -> str | None:
    m = REDDIT_POST_RE.search(url or "")
    return m.group(1) if m else None


def extract_subreddit(value: str) -> str | None:
    """Accept a subreddit URL, r/name, or bare name; return the name."""
    if not value:
        return None
    m = REDDIT_SUBREDDIT_RE.search(value)
    if m:
        return m.group(1)
    if _is_foreign_platform(value, "reddit"):
        return None
    name = value.strip().lstrip("/").removeprefix("r/").strip("/")
    if re.fullmatch(r"[A-Za-z0-9_]{2,21}", name):
        return name
    return None


# --- Threads ---------------------------------------------------------------
THREADS_POST_RE = re.compile(r"threads\.(?:net|com)/(?:@[\w.]+/)?(?:post|t)/([A-Za-z0-9_-]+)")
THREADS_USER_RE = re.compile(r"threads\.(?:net|com)/@([\w.]+)")


def extract_threads_post_code(url: str) -> str | None:
    m = THREADS_POST_RE.search(url or "")
    return m.group(1) if m else None


def normalize_threads_username(value: str) -> str | None:
    if not value:
        return None
    m = THREADS_USER_RE.search(value)
    if m:
        return m.group(1)
    return value.strip().lstrip("@") or None


# --- Pinterest -------------------------------------------------------------
PINTEREST_PIN_RE = re.compile(r"pinterest\.[a-z.]+/pin/(\d+)")
PINTEREST_USER_RE = re.compile(r"pinterest\.[a-z.]+/([A-Za-z0-9_]+)/?")


def extract_pinterest_pin_id(url: str) -> str | None:
    m = PINTEREST_PIN_RE.search(url or "")
    return m.group(1) if m else None


def extract_pinterest_username(value: str) -> str | None:
    if not value:
        return None
    m = PINTEREST_USER_RE.search(value)
    if m and "/pin/" not in value:
        return m.group(1)
    return value.strip().lstrip("@") or None


# --- LinkedIn --------------------------------------------------------------
LINKEDIN_PROFILE_RE = re.compile(r"linkedin\.com/in/([A-Za-z0-9\-_%]+)")
LINKEDIN_COMPANY_RE = re.compile(r"linkedin\.com/company/([A-Za-z0-9\-_%]+)")


def extract_linkedin_profile(url: str) -> str | None:
    m = LINKEDIN_PROFILE_RE.search(url or "")
    return m.group(1) if m else None


def extract_linkedin_company(url: str) -> str | None:
    m = LINKEDIN_COMPANY_RE.search(url or "")
    return m.group(1) if m else None


# --- Rumble ----------------------------------------------------------------
RUMBLE_VIDEO_RE = re.compile(r"rumble\.com/(?:shorts/)?(v[A-Za-z0-9]+)")
RUMBLE_CHANNEL_RE = re.compile(r"rumble\.com/(?:c|user)/([A-Za-z0-9_\-]+)")


def extract_rumble_video_id(url: str) -> str | None:
    m = RUMBLE_VIDEO_RE.search(url or "")
    return m.group(1) if m else None


def extract_rumble_channel(url: str) -> str | None:
    m = RUMBLE_CHANNEL_RE.search(url or "")
    return m.group(1) if m else None


# --- Bluesky ---------------------------------------------------------------
BLUESKY_POST_RE = re.compile(r"bsky\.app/profile/([\w.:%-]+)/post/([A-Za-z0-9]+)")
BLUESKY_PROFILE_RE = re.compile(r"bsky\.app/profile/([\w.:%-]+)")


def extract_bluesky_post(url: str) -> tuple[str, str] | None:
    """Return (handle_or_did, rkey) for a Bluesky post URL."""
    m = BLUESKY_POST_RE.search(url or "")
    return (m.group(1), m.group(2)) if m else None


def normalize_bluesky_handle(value: str) -> str | None:
    """Accept a profile URL, @handle, handle, or DID; return the actor id."""
    if not value:
        return None
    m = BLUESKY_PROFILE_RE.search(value)
    if m:
        return m.group(1)
    return value.strip().lstrip("@") or None
