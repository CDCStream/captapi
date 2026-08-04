"""Truth Social public profile and post endpoints.

As of late 2025 Truth Social only exposes public profiles/posts for prominent
accounts (e.g. Trump, Vance) without login; most other accounts require auth
and 404 here. Documented on every endpoint; auth-gated responses become a clear
404 rather than a generic 502.
"""

from __future__ import annotations

import html
import json
import math
import re
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services import decodo_fetch
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.services.http_fetch import DEFAULT_HEADERS
from app.utils.formatters import safe_int, safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

BASE = "https://truthsocial.com"
CREDIT_PROFILE = 1
CREDIT_POST = 1
CREDIT_USER_POSTS = 2
RATE_USER_POSTS = 0.85
HEADERS = {
    **DEFAULT_HEADERS,
    "Accept": "application/json",
}

_AUTH_LIMIT_NOTE = (
    "As of late 2025, Truth Social only lets you view public profiles/posts of "
    "prominent users (e.g. Trump, Vance) without authentication; most other "
    "accounts require auth and will 404 here."
)

_AUTH_GATED_DETAIL = (
    "Truth Social resource not publicly available. " + _AUTH_LIMIT_NOTE
)

_DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _scaled_posts(count: int) -> int:
    return max(CREDIT_USER_POSTS, math.ceil(max(0, count) * RATE_USER_POSTS))


def _status_at_iso(value: Any) -> str | None:
    """Mastodon last_status_at is often YYYY-MM-DD — normalize to ISO-8601 UTC midnight."""
    text = safe_str(value)
    if not text:
        return None
    if _DATE_ONLY_RE.match(text):
        return f"{text}T00:00:00.000Z"
    return text


def _username(value: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "truth_social":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "truth_social", "https://truthsocial.com/@username"),
        )
    value = (value or "").strip().rstrip("/")
    match = re.search(r"truthsocial\.com/@([^/?#]+)", value)
    if match:
        return match.group(1)
    return value.lstrip("@")


def _post_id(value: str) -> str | None:
    detected = detect_url_platform(value)
    if detected and detected != "truth_social":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "truth_social", "https://truthsocial.com/@username/posts/1234567890"),
        )
    match = re.search(r"/posts/([0-9]+)", value or "")
    if match:
        return match.group(1)
    match = re.search(r"truthsocial\.com/@[^/?#]+/([0-9]+)", value or "")
    if match:
        return match.group(1)
    match = re.search(r"\b([0-9]{10,})\b", value or "")
    return match.group(1) if match else None


def _post_username(value: str) -> str | None:
    match = re.search(r"truthsocial\.com/@([^/?#]+)/", value or "")
    return match.group(1) if match else None


_TAG_RE = re.compile(r"<[^>]+>", re.I)
_A_HREF_RE = re.compile(
    r'<a\b[^>]*\bhref\s*=\s*(?:"([^"]*)"|\'([^\']*)\')[^>]*>(.*?)</a>',
    re.I | re.S,
)
_MISSING_MEDIA_RE = re.compile(r"/icons/missing\.(?:png|jpg|jpeg|gif|webp)(?:\?|$)", re.I)
_RUMBLE_ID_RE = re.compile(r"(?:rumble\.com/(?:embed/)?|(?:^|/))(v[a-z0-9]{5,})\b", re.I)


def _media_url(value: Any) -> str | None:
    """Drop Truth Social placeholder thumbnails (missing.png is not a real preview)."""
    url = safe_str(value)
    if not url:
        return None
    if _MISSING_MEDIA_RE.search(url):
        return None
    return url


def _html_to_text(value: Any) -> str:
    """HTML→text without breaking Mastodon/Truth URL soft-wraps.

    Truth Social inserts ``<span>`` inside long URLs for line breaks. Replacing
    every tag with a space produced ``www. whitehouse.gov`` / ``integr ity``.
    Inline tags are removed with no spacer; ``<a href>`` is replaced by the
    authoritative href so shared links stay usable.
    """
    raw = str(value or "")
    if not raw.strip():
        return ""

    def _anchor(match: re.Match[str]) -> str:
        href = html.unescape((match.group(1) or match.group(2) or "").strip())
        if href.startswith(("http://", "https://")):
            return href
        return _html_fragment_to_text(match.group(3) or "")

    text = _A_HREF_RE.sub(_anchor, raw)
    return _html_fragment_to_text(text)


def _html_fragment_to_text(raw: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", raw or "", flags=re.I)
    s = re.sub(r"</p\s*>", "\n", s, flags=re.I)
    s = re.sub(r"<p\b[^>]*>", "", s, flags=re.I)
    s = s.replace("\u00ad", "")  # soft hyphen
    # Inline tags (span, b, …) → no space, so URL fragments rejoin.
    s = _TAG_RE.sub("", s)
    s = html.unescape(s)
    s = re.sub(r"[^\S\n]+", " ", s)
    s = re.sub(r" *\n+ *", "\n", s)
    return s.strip()


def _extract_links(value: Any) -> list[dict[str, str]]:
    """Authoritative URLs from ``<a href>`` (never from span-broken visible text)."""
    raw = str(value or "")
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for m in _A_HREF_RE.finditer(raw):
        href = html.unescape((m.group(1) or m.group(2) or "").strip())
        if not href.startswith(("http://", "https://")):
            continue
        if href in seen:
            continue
        seen.add(href)
        out.append({"url": href})
    return out


def _strip_html(value: Any) -> str:
    """Back-compat alias — prefer :func:`_html_to_text` for post bodies."""
    return _html_to_text(value)


def _bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        low = value.strip().lower()
        if low in {"true", "1", "yes"}:
            return True
        if low in {"false", "0", "no"}:
            return False
    return None


def _normalize_emojis(raw: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        row = {
            "shortcode": safe_str(item.get("shortcode")),
            "url": safe_str(item.get("url")),
            "staticUrl": safe_str(item.get("static_url") or item.get("staticUrl")),
        }
        if any(row.values()):
            out.append({k: v for k, v in row.items() if v is not None})
    return out


def _normalize_fields(raw: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = safe_str(item.get("name"))
        value = _strip_html(item.get("value"))
        if not name and not value:
            continue
        row: dict[str, Any] = {
            "name": name,
            "value": value,
            "verifiedAt": safe_str(item.get("verified_at") or item.get("verifiedAt")),
        }
        out.append(row)
    return out


def _normalize_account(item: dict[str, Any]) -> dict[str, Any]:
    username = item.get("username") or item.get("acct") or item.get("authorUsername")
    # Full Mastodon/Truth account payloads expose these; Apify author stubs often don't.
    rich = any(
        k in item
        for k in (
            "followers_count",
            "followersCount",
            "locked",
            "bot",
            "group",
            "avatar_static",
            "header_static",
            "note",
            "statuses_count",
            "statusesCount",
        )
    )
    locked = item.get("locked") if "locked" in item else item.get("isPrivate")
    locked_bool = bool(locked) if locked is not None else False
    out: dict[str, Any] = {
        "platform": "truth_social",
        "id": safe_str(item.get("id") or item.get("authorId")),
        "username": safe_str(username),
        "acct": safe_str(item.get("acct") or username),
        "url": safe_str(item.get("url") or item.get("authorUrl"))
        or (f"https://truthsocial.com/@{username}" if username else None),
        "displayName": safe_str(
            item.get("display_name") or item.get("displayName") or item.get("authorName")
        ),
        "bio": _strip_html(item.get("note") or item.get("bio")),
        "avatar": safe_str(item.get("avatar") or item.get("authorAvatar")),
        "avatarStatic": safe_str(item.get("avatar_static") or item.get("avatarStatic")),
        "banner": safe_str(item.get("header") or item.get("banner")),
        "headerStatic": safe_str(item.get("header_static") or item.get("headerStatic")),
        "verified": bool(item.get("verified") or item.get("authorVerified")),
        "followers": safe_int(item.get("followers_count") or item.get("followersCount")),
        "following": safe_int(item.get("following_count") or item.get("followingCount")),
        "postCount": safe_int(item.get("statuses_count") or item.get("statusesCount")),
        "location": safe_str(item.get("location")),
        "website": safe_str(item.get("website")),
        "createdAt": safe_str(
            item.get("created_at") or item.get("createdAt") or item.get("authorCreatedAt")
        ),
        "lastStatusAt": _status_at_iso(item.get("last_status_at") or item.get("lastStatusAt")),
        "emojis": _normalize_emojis(item.get("emojis")),
        "fields": _normalize_fields(item.get("fields")),
    }
    if rich:
        # Classification triad — not Mastodon junk flags; keep always-key on rich payloads.
        out["bot"] = bool(item.get("bot"))
        out["locked"] = locked_bool
        out["isPrivate"] = locked_bool  # BC alias of locked
        out["group"] = bool(item.get("group"))
        out["discoverable"] = _bool_or_none(item.get("discoverable"))
        if out.get("location") == "":
            out["location"] = None
        if "accepting_messages" in item or "acceptingMessages" in item:
            out["acceptingMessages"] = _bool_or_none(
                item.get("accepting_messages", item.get("acceptingMessages"))
            )
        if "chats_onboarded" in item or "chatsOnboarded" in item:
            out["chatsOnboarded"] = _bool_or_none(
                item.get("chats_onboarded", item.get("chatsOnboarded"))
            )
        if "tv_account" in item or "tvAccount" in item:
            out["tvAccount"] = _bool_or_none(item.get("tv_account", item.get("tvAccount")))
        for key in ("website", "avatarStatic", "headerStatic"):
            if out.get(key) in (None, ""):
                out.pop(key, None)
    else:
        for key in ("location", "website", "avatarStatic", "headerStatic", "acct"):
            if out.get(key) in (None, ""):
                out.pop(key, None)
    return out


def _author_slim(full: dict[str, Any] | None) -> dict[str, Any] | None:
    """Per-post identity on list endpoints — full card lives once at the top level."""
    if not full:
        return None
    return {
        "id": full.get("id"),
        "username": full.get("username"),
        "displayName": full.get("displayName"),
        "avatar": full.get("avatar"),
        "verified": bool(full.get("verified")),
    }


def _num(value: Any, *, as_float: bool = False) -> int | float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) if as_float else int(value)
    if isinstance(value, str) and value.strip():
        text = value.strip()
        # Mastodon frame_rate often looks like "30/1".
        if "/" in text and as_float:
            left, _, right = text.partition("/")
            try:
                den = float(right) or 1.0
                return float(left) / den
            except ValueError:
                return None
        try:
            return float(text) if as_float else int(float(text))
        except ValueError:
            return None
    return None


def _media_meta(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    original = raw.get("original") if isinstance(raw.get("original"), dict) else {}
    out: dict[str, Any] = {}
    for src_key, dst_key, as_float in (
        ("width", "width", False),
        ("height", "height", False),
        ("duration", "duration", True),
        ("bitrate", "bitrate", False),
        ("frame_rate", "frameRate", True),
        ("frameRate", "frameRate", True),
    ):
        val = _num(original.get(src_key), as_float=as_float)
        if val is None:
            val = _num(raw.get(src_key), as_float=as_float)
        if val is not None and dst_key not in out:
            out[dst_key] = val
    blur = safe_str(raw.get("blurhash") or original.get("blurhash"))
    if blur:
        out["blurhash"] = blur
    return out or None


def _normalize_media(raw: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(raw, list):
        return out
    for m in raw:
        if not isinstance(m, dict):
            continue
        meta = _media_meta(m.get("meta"))
        row: dict[str, Any] = {
            "type": safe_str(m.get("type")),
            "url": _media_url(m.get("url")),
            "previewUrl": _media_url(m.get("preview_url") or m.get("previewUrl")),
            "description": safe_str(m.get("description")),
        }
        if meta:
            row["meta"] = meta
            if "duration" in meta:
                dur = meta["duration"]
                row["durationSeconds"] = int(dur) if float(dur).is_integer() else float(dur)
        blur = safe_str(m.get("blurhash"))
        if blur and "meta" not in row:
            row["meta"] = {"blurhash": blur}
        elif blur and isinstance(row.get("meta"), dict) and "blurhash" not in row["meta"]:
            row["meta"]["blurhash"] = blur
        # Drop empty description key noise? keep for schema stability when present upstream
        out.append(row)
    return out


def _normalize_card(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    out = {
        "url": safe_str(raw.get("url")),
        "title": safe_str(raw.get("title")),
        "description": safe_str(raw.get("description")),
        "image": _media_url(raw.get("image")),
        "type": safe_str(raw.get("type")),
        "providerName": safe_str(raw.get("provider_name") or raw.get("providerName")),
    }
    cleaned = {k: v for k, v in out.items() if v not in (None, "")}
    return cleaned or None


def _external_video_id(item: dict[str, Any], media: list[dict[str, Any]]) -> str | None:
    """Rumble video id when Truth Social hosts the clip on Rumble (cross-link to /v1/rumble/*)."""
    for key in ("external_video_id", "externalVideoId"):
        got = safe_str(item.get(key))
        if got:
            return got
    card = item.get("card") if isinstance(item.get("card"), dict) else {}
    for key in ("external_video_id", "externalVideoId"):
        got = safe_str(card.get(key))
        if got:
            return got
    for blob in (card.get("url"), item.get("url"), *(m.get("url") for m in media if isinstance(m, dict))):
        text = safe_str(blob)
        if not text:
            continue
        match = _RUMBLE_ID_RE.search(text)
        if match:
            return match.group(1)
    for m in item.get("media_attachments") or []:
        if not isinstance(m, dict):
            continue
        got = safe_str(m.get("external_video_id") or m.get("externalVideoId"))
        if got:
            return got
    return None


def _normalize_post(
    item: dict[str, Any],
    *,
    author_mode: str = "full",
) -> dict[str, Any]:
    account = item.get("account") if isinstance(item.get("account"), dict) else {}
    content_html = item.get("content") or item.get("text") or item.get("contentHtml") or ""
    media_raw = item.get("media_attachments") if isinstance(item.get("media_attachments"), list) else item.get("media")
    media = _normalize_media(media_raw)
    full_author: dict[str, Any] | None = None
    if account:
        full_author = _normalize_account(account)
    elif item.get("authorUsername"):
        full_author = _normalize_account(item)

    if author_mode == "omit":
        author: dict[str, Any] | None = None
    elif author_mode == "slim":
        author = _author_slim(full_author)
    else:
        author = full_author

    engagement = {
        "replies": safe_int(item.get("replies_count") or item.get("repliesCount") or item.get("replyCount")),
        "reblogs": safe_int(item.get("reblogs_count") or item.get("reblogsCount") or item.get("repostCount")),
        "likes": safe_int(item.get("favourites_count") or item.get("favouritesCount") or item.get("likeCount")),
        "upvotes": safe_int(item.get("upvotes_count") or item.get("upvotesCount") or item.get("upvotes")),
        "downvotes": safe_int(item.get("downvotes_count") or item.get("downvotesCount") or item.get("downvotes")),
    }
    out: dict[str, Any] = {
        "platform": "truth_social",
        "id": safe_str(item.get("id") or item.get("postId")),
        "url": safe_str(item.get("url") or item.get("postUrl")),
        "text": _html_to_text(content_html),
        "links": _extract_links(content_html),
        "publishedAt": safe_str(item.get("created_at") or item.get("createdAt")),
        "author": author,
        "engagement": engagement,
        "language": safe_str(item.get("language")),
        "sensitive": bool(item.get("sensitive")),
        "media": media,
    }
    card = _normalize_card(item.get("card"))
    if card:
        out["card"] = card
    external = _external_video_id(item, media)
    if external:
        out["externalVideoId"] = external
        out["externalVideoUrl"] = f"https://rumble.com/{external}"
    return out


def _looks_like_json(body: str) -> bool:
    text = (body or "").lstrip()
    return text.startswith("{") or text.startswith("[")


async def _get_json(
    path: str,
    params: dict[str, Any] | None = None,
    *,
    auth_gated_as_404: bool = False,
) -> Any:
    url = f"{BASE}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"

    status: int | None = None
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=HEADERS) as client:
            resp = await client.get(url)
        status = resp.status_code
        if status == 200 and _looks_like_json(resp.text):
            return json.loads(resp.text)
    except (httpx.HTTPError, json.JSONDecodeError):
        pass

    # Datacenter IPs often get Cloudflare HTML; retry via Decodo.
    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_json(url, timeout=45.0)
        if got is not None:
            status, payload = got
            if status == 200 and payload is not None:
                return payload

    if status == 404:
        raise HTTPException(status_code=404, detail="Truth Social resource not found")
    if status in (401, 403):
        if auth_gated_as_404:
            raise HTTPException(status_code=404, detail=_AUTH_GATED_DETAIL)
        raise HTTPException(
            status_code=502,
            detail="Truth Social public API is temporarily unavailable",
        )
    if status == 429:
        raise HTTPException(
            status_code=502,
            detail="Truth Social public API is temporarily unavailable",
        )
    raise HTTPException(status_code=502, detail="Truth Social lookup failed")


async def _actor_posts(username: str, limit: int) -> list[dict[str, Any]]:
    settings = get_settings()
    max_posts = max(limit, 5)
    items, _actor = await get_apify().run_with_fallback(
        [
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL,
                {"truthSocialUsername": [username], "maxPosts": max_posts},
            ),
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL_FALLBACK,
                {"mode": "profile", "usernames": [username], "maxPosts": max_posts},
            ),
        ],
        max_items=max_posts,
    )
    return [i for i in items if isinstance(i, dict)]


async def _actor_account(username: str) -> dict[str, Any]:
    posts = await _actor_posts(username, 5)
    for post in posts:
        account = post.get("account") if isinstance(post.get("account"), dict) else None
        if account:
            return _normalize_account(account)
        if post.get("authorUsername"):
            return _normalize_account(post)
    raise HTTPException(status_code=404, detail="Truth Social profile not found")


async def _actor_post(post_id: str, url: str) -> dict[str, Any]:
    settings = get_settings()
    username = _post_username(url)
    canonical = url if "truthsocial.com" in (url or "") else f"{BASE}/@{username or 'realDonaldTrump'}/posts/{post_id}"
    items, _actor = await get_apify().run_with_fallback(
        [
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL,
                {"fetchSinglePostByIdOrUrl": [canonical], "maxPosts": 5},
            ),
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL,
                {"fetchSinglePostByIdOrUrl": [post_id], "maxPosts": 5},
            ),
            (
                settings.APIFY_ACTOR_TRUTH_SOCIAL_FALLBACK,
                {"mode": "post", "postUrls": [canonical], "maxPosts": 1},
            ),
        ],
        max_items=5,
    )
    for item in items:
        if isinstance(item, dict) and safe_str(item.get("id") or item.get("postId")) == post_id:
            return _normalize_post(item)
    if username:
        for item in await _actor_posts(username, 80):
            if safe_str(item.get("id") or item.get("postId")) == post_id:
                return _normalize_post(item)
    raise HTTPException(status_code=404, detail="Truth Social post not found")


@router.get(
    "/profile",
    summary="Truth Social profile",
    description=(
        "Public Truth Social profile (Mastodon-compatible account fields). "
        f"{_AUTH_LIMIT_NOTE} Flat 1 credit."
    ),
)
async def profile(
    url: str = Query(..., description="Truth Social profile URL or @username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Truth Social profile")
    async with billed_call(
        caller=caller,
        endpoint="/v1/truth-social/profile",
        platform="truth_social",
        resource_url=f"{BASE}/@{username}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:

        async def _run() -> dict[str, Any]:
            try:
                data = await _get_json(
                    "/api/v1/accounts/lookup",
                    {"acct": username},
                    auth_gated_as_404=True,
                )
                ctx["source"] = "direct"
                return _normalize_account(data)
            except HTTPException as exc:
                if exc.status_code not in {502, 503, 504}:
                    raise
            ctx["source"] = "apify"
            return await _actor_account(username)

        data = await cached_or_run(
            "truth-social.profile",
            {"username": username, "v": 4},
            _run,
            ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/user-posts",
    summary="Truth Social user posts (cursor-paginated)",
    description=(
        "Recent public Truth Social posts for a profile (cursor via Mastodon max_id). "
        "Full author{} once at the top; each post keeps a slim author "
        "{id,username,displayName,avatar,verified}. "
        "Post text preserves real URLs (span soft-wraps are not turned into spaces) "
        "and links[] lists authoritative <a href> targets. "
        f"{_AUTH_LIMIT_NOTE} Native path is flat {CREDIT_USER_POSTS} credits; "
        f"Apify fallback ~{RATE_USER_POSTS}/post (min {CREDIT_USER_POSTS})."
    ),
)
async def user_posts(
    url: str = Query(..., description="Truth Social profile URL or @username"),
    limit: int = Query(
        20,
        ge=1,
        le=80,
        description=(
            "Max posts to return (default 20, max 80). Capped at 80 because Truth "
            "Social's statuses page size is ~40 and larger asks still page via cursor."
        ),
    ),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor (Mastodon max_id). Leave empty for the first page; "
            "then pass the nextCursor value returned in the previous response."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _username(url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid Truth Social profile")
    if cursor is not None and cursor != "" and not str(cursor).isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    # Reserve Apify worst-case; native path overrides to flat CREDIT_USER_POSTS.
    cost = _scaled_posts(limit)
    async with billed_call(
        caller=caller,
        endpoint="/v1/truth-social/user-posts",
        platform="truth_social",
        resource_url=f"{BASE}/@{username}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            next_cursor: str | None = None
            author_full: dict[str, Any] | None = None
            try:
                account = await _get_json(
                    "/api/v1/accounts/lookup",
                    {"acct": username},
                    auth_gated_as_404=True,
                )
                account_id = account.get("id")
                if not account_id:
                    raise HTTPException(status_code=404, detail="Truth Social profile not found")
                author_full = _normalize_account(account)
                params: dict[str, Any] = {
                    "limit": min(limit, 40),
                    "exclude_replies": "true",
                    "with_muted": "true",
                }
                if cursor:
                    params["max_id"] = cursor
                items = await _get_json(
                    f"/api/v1/accounts/{account_id}/statuses",
                    params,
                    auth_gated_as_404=True,
                )
                ctx["source"] = "direct"
            except HTTPException as exc:
                if exc.status_code not in {502, 503, 504}:
                    raise
                if cursor:
                    raise HTTPException(
                        status_code=400,
                        detail="Cursor pagination is only available on the native Truth Social path. Start a new request without cursor.",
                    ) from exc
                items = await _actor_posts(username, limit)
                ctx["source"] = "apify"
                for raw in items:
                    if not isinstance(raw, dict):
                        continue
                    acc = raw.get("account") if isinstance(raw.get("account"), dict) else None
                    if acc:
                        author_full = _normalize_account(acc)
                        break
            posts = [
                _normalize_post(i, author_mode="slim")
                for i in items[:limit]
                if isinstance(i, dict)
            ]
            if ctx.get("source") == "direct" and posts and len(posts) >= min(limit, 40):
                next_cursor = posts[-1].get("id")
            return {
                "username": username,
                "author": author_full,
                "totalReturned": len(posts),
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "posts": posts,
            }

        data = await cached_or_run(
            "truth-social.user-posts",
            {"username": username, "limit": limit, "cursor": cursor or "", "v": 5},
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_USER_POSTS
        else:
            ctx["credits_override"] = _scaled_posts(len(data.get("posts") or []))
        return ApiResponse(data=data)


@router.get(
    "/post",
    summary="Truth Social post",
    description=(
        "Public Truth Social post (text, author, engagement, media). "
        f"{_AUTH_LIMIT_NOTE} Flat 1 credit."
    ),
)
async def post(
    url: str = Query(..., description="Truth Social post URL or post ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    post_id = _post_id(url)
    if not post_id:
        raise HTTPException(status_code=400, detail="Invalid Truth Social post URL or ID")
    async with billed_call(caller=caller, endpoint="/v1/truth-social/post", platform="truth_social", resource_url=f"{BASE}/api/v1/statuses/{post_id}", base_credits=CREDIT_POST) as ctx:
        async def _run() -> dict[str, Any]:
            try:
                data = await _get_json(
                    f"/api/v1/statuses/{post_id}",
                    auth_gated_as_404=True,
                )
                return _normalize_post(data)
            except HTTPException as exc:
                if exc.status_code not in {502, 503, 504}:
                    raise
            return await _actor_post(post_id, url)

        data = await cached_or_run("truth-social.post", {"post_id": post_id, "v": 4}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)
