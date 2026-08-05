"""Kwai endpoints.

Backed by native Decodo HTML parse (JSON-LD + Nuxt SSR) with Apify fallthrough.
Profile URLs: ``https://www.kwai.com/@handle``. Video URLs:
``.../@handle/video/<id>``.
"""

from __future__ import annotations

import base64
import json
import math
import re
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.services import kwai_native as native
from app.utils.formatters import safe_int, safe_str
from app.utils.media_urls import cdn_expires_at
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

_PROFILE_EXAMPLE = "https://www.kwai.com/@topfilmeseseriesnatv"
_HANDLE_RE = re.compile(r"[A-Za-z0-9._-]{2,}")
_PLACEHOLDER_CAPTION = frozenset({".", "..", "...", "…", "....", "……"})
# Kwai headshot size suffixes on overseaHead / similar CDN paths.
_AVATAR_VARIANT_RE = re.compile(
    r"_(?:t|tw|l|m|s)\.(?:jpe?g|webp|png)(\?|$)",
    re.I,
)

CREDIT_POST = 2
RATE_USER_POSTS = 1.0  # 1 credit per post; transcript is JSON-LD when Kwai exposes it


def _scaled(n: int, rate: float = RATE_USER_POSTS, minimum: int = 2) -> int:
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _guard_platform(value: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "kwai":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "kwai", _PROFILE_EXAMPLE),
        )


def _profile_url(value: str) -> str | None:
    """Canonical ``https://www.kwai.com/@handle`` from a URL or bare handle."""
    value = (value or "").strip().rstrip("/")
    _guard_platform(value)
    match = re.search(r"kwai\.com/@([A-Za-z0-9._-]+)", value)
    if match:
        return f"https://www.kwai.com/@{match.group(1)}"
    if _HANDLE_RE.fullmatch(value.lstrip("@")):
        return f"https://www.kwai.com/@{value.lstrip('@')}"
    return None


def _video_url(value: str) -> str | None:
    """Canonical Kwai video URL. Requires a full share URL (the actor needs the
    handle in the path, so a bare video id can't be reconstructed)."""
    value = (value or "").strip().rstrip("/")
    _guard_platform(value)
    if not value.startswith("http"):
        value = f"https://{value}"
    if re.search(r"kwai\.com/(?:@[A-Za-z0-9._-]+/video|photo)/[A-Za-z0-9_-]+", value):
        return value
    return None


def _good_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [i for i in items if isinstance(i, dict) and i.get("status") != "error"]


async def _run_kwai(run_input: dict[str, Any], max_items: int) -> list[dict[str, Any]]:
    settings = get_settings()
    apify = get_apify()
    return await apify.run_actor_sync(settings.APIFY_ACTOR_KWAI, run_input, max_items=max_items)


def _author(item: dict[str, Any]) -> dict[str, Any]:
    meta = item.get("authorMeta")
    return meta if isinstance(meta, dict) else {}


def _normalize_avatar(url: str | None) -> str | None:
    """Prefer a single headshot variant (``_s.jpg``) across list rows."""
    raw = safe_str(url)
    if not raw:
        return None
    if _AVATAR_VARIANT_RE.search(raw):
        return _AVATAR_VARIANT_RE.sub(r"_s.jpg\1", raw, count=1)
    return raw


def _clean_caption(caption: Any, *, title: Any = None) -> str | None:
    """Drop Kwai placeholder descriptions (``.`` / ``...``). Never invent text."""
    for candidate in (caption, title):
        text = safe_str(candidate)
        if not text:
            continue
        if text.strip() in _PLACEHOLDER_CAPTION:
            continue
        return text
    return None


def _dedupe_transcript(text: str | None) -> str | None:
    """Collapse exact / near-exact doubled caption tracks merged without a separator."""
    raw = (text or "").strip()
    if not raw:
        return None
    n = len(raw)
    if n >= 16 and n % 2 == 0 and raw[: n // 2] == raw[n // 2 :]:
        return raw[: n // 2]
    for i in range(n // 2, 7, -1):
        a = raw[:i].rstrip(" .,;…")
        b = raw[i:].rstrip(" .,;…")
        if len(a) >= 8 and a == b:
            return a + ("." if raw.rstrip().endswith(".") else "")
    return raw


def _video_type(url: str | None) -> str | None:
    if not url:
        return None
    path = (urlparse(url).path or "").lower()
    if path.endswith(".m3u8") or ".m3u8" in path:
        return "hls"
    if path.endswith(".mp4") or ".mp4" in path:
        return "mp4"
    # Kwai progressive CDN paths are almost always mp4 even without extension.
    if "kwai.net" in (urlparse(url).netloc or "").lower():
        return "mp4"
    return None


def _author_card(author: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(author, dict) or not author:
        return None
    out = {
        "id": safe_str(author.get("eid") or author.get("id")),
        "username": safe_str(author.get("username")),
        "displayName": safe_str(author.get("name")),
        "avatar": _normalize_avatar(safe_str(author.get("avatar"))),
        "url": safe_str(author.get("url")),
    }
    cleaned = {k: v for k, v in out.items() if v not in (None, "", [])}
    return cleaned or None


def _encode_posts_cursor(offset: int) -> str:
    payload = json.dumps({"o": offset}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def _decode_posts_cursor(cursor: str | None) -> int:
    raw = (cursor or "").strip()
    if not raw:
        return 0
    pad = "=" * (-len(raw) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(raw + pad).decode())
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass nextCursor from the previous response.",
        ) from None
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass nextCursor from the previous response.",
        )
    try:
        offset = int(data.get("o"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass nextCursor from the previous response.",
        ) from None
    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass nextCursor from the previous response.",
        )
    return offset


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    author = _author(item)
    handle = author.get("username") or author.get("name")
    page_url = author.get("url") or (f"https://www.kwai.com/@{handle}" if handle else None)
    eid = safe_str(author.get("eid") or author.get("id"))
    public_posts = safe_int(author.get("publicPostCount") or author.get("videosCount"))
    private_posts = safe_int(author.get("privatePostCount"))
    verified = author.get("verified")
    if not isinstance(verified, bool):
        verified = None
    is_private = author.get("isPrivate")
    if not isinstance(is_private, bool):
        is_private = None
    out: dict[str, Any] = {
        "platform": "kwai",
        "id": eid,
        "eid": eid,
        "url": safe_str(page_url),
        "username": safe_str(handle),
        "displayName": safe_str(author.get("name")),
        "bio": safe_str(author.get("bio") or author.get("description")),
        "avatar": _normalize_avatar(safe_str(author.get("avatar"))),
        "verified": verified,
        "verifiedDescription": safe_str(author.get("verifiedDescription")),
        "verifiedNumber": safe_int(author.get("verifiedNumber")),
        "gender": safe_str(author.get("gender")),
        "followers": safe_int(author.get("followersCount")),
        "following": safe_int(author.get("followingCount")),
        "likedCount": safe_int(author.get("likesCount")),
        "publicPostCount": public_posts,
        "privatePostCount": private_posts,
        "postCount": public_posts,
        "videoCount": public_posts,
        "isPrivate": is_private,
    }
    for key in (
        "bio",
        "verifiedDescription",
        "verifiedNumber",
        "gender",
        "following",
        "publicPostCount",
        "privatePostCount",
        "postCount",
        "videoCount",
        "eid",
    ):
        if out.get(key) in (None, "", []):
            out.pop(key, None)
    for key in ("verified", "isPrivate"):
        if out.get(key) is None:
            out.pop(key, None)
    return out


def _normalize_post(
    item: dict[str, Any],
    *,
    include_author: bool = True,
) -> dict[str, Any]:
    author = _author(item)
    duration = item.get("duration")
    video_url = safe_str(item.get("playUrl"))
    thumb = safe_str(item.get("thumb"))
    text = _clean_caption(item.get("caption"), title=item.get("name") or item.get("title"))
    transcript = _dedupe_transcript(safe_str(item.get("transcript")))
    expires = cdn_expires_at(video_url) or cdn_expires_at(thumb)
    out: dict[str, Any] = {
        "platform": "kwai",
        "id": safe_str(item.get("id")),
        "url": safe_str(item.get("url")),
        "text": text,
        "transcript": transcript,
        "publishedAt": safe_str(item.get("createTime")),
        "durationSeconds": safe_int(duration) if isinstance(duration, (int, float)) else None,
        "thumbnailUrl": thumb,
        "videoUrl": video_url,
        "videoType": _video_type(video_url),
        "mediaUrlsExpireAt": expires,
        "engagement": {
            "views": safe_int(item.get("viewCount")),
            "likes": safe_int(item.get("likeCount")),
            "comments": safe_int(item.get("commentCount")),
            "shares": safe_int(item.get("shareCount")),
        },
    }
    if include_author:
        card = _author_card(author)
        if card:
            out["author"] = card
    for key in (
        "text",
        "transcript",
        "durationSeconds",
        "thumbnailUrl",
        "videoUrl",
        "videoType",
        "mediaUrlsExpireAt",
    ):
        if out.get(key) in (None, "", []):
            out.pop(key, None)
    return out


def _hashtags(text: str | None) -> list[str]:
    if not text:
        return []
    return [h for h in re.findall(r"#(\w+)", text) if h]


@router.get(
    "/profile",
    summary="Kwai profile",
    description=(
        "Fetch a Kwai profile — display name, bio, counts, and verification as structured JSON. "
        "Parsed from Kwai's public web page (JSON-LD + Nuxt SSR state)."
    ),
)
async def profile(
    url: str = Query(..., description="Kwai profile URL or @handle (e.g. https://www.kwai.com/@topfilmeseseriesnatv)"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    profile_url = _profile_url(url)
    if not profile_url:
        raise HTTPException(status_code=400, detail="Invalid Kwai profile URL or handle")
    async with billed_call(caller=caller, endpoint="/v1/kwai/profile", platform="kwai", resource_url=url, base_credits=1) as ctx:
        async def _run() -> dict[str, Any]:
            native_row = await native.fetch_profile(profile_url)
            if native_row:
                ctx["source"] = "direct"
                return _normalize_profile(native_row)
            items = _good_rows(await _run_kwai({"urls": [profile_url], "maxItems": 1}, max_items=1))
            if not items:
                raise HTTPException(status_code=404, detail="Kwai profile not found")
            ctx["source"] = "apify"
            return _normalize_profile(items[0])

        data = await cached_or_run("kwai.profile", {"url": profile_url, "v": 7}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)


@router.get(
    "/user-posts",
    summary="Kwai user posts",
    description=(
        "Public posts for a Kwai profile as clean JSON. Each post includes caption when "
        "Kwai publishes one (placeholder \"...\" descriptions are omitted), engagement, "
        "mp4 videoUrl + videoType, mediaUrlsExpireAt from the signed CDN tag, and "
        "transcript when Kwai's JSON-LD exposes auto-captions (deduped). Author{} is "
        "hoisted once at the top. Opaque cursor pages within the posts returned from "
        "one profile fetch (Kwai's public web surface does not expose deep archive "
        "pagination). ~1 credit per post returned (min 2)."
    ),
)
async def user_posts(
    url: str = Query(..., description="Kwai profile URL or @handle (e.g. https://www.kwai.com/@topfilmeseseriesnatv)"),
    limit: int = Query(20, ge=1, le=200),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor from the previous nextCursor. Leave empty for "
            "the first page. Pages within the posts Kwai exposes on one profile fetch."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    profile_url = _profile_url(url)
    if not profile_url:
        raise HTTPException(status_code=400, detail="Invalid Kwai profile URL or handle")
    offset = _decode_posts_cursor(cursor)
    # Over-fetch so cursor pages can walk the single HTML/Apify batch.
    fetch_cap = min(200, max(limit + offset, limit))
    async with billed_call(
        caller=caller,
        endpoint="/v1/kwai/user-posts",
        platform="kwai",
        resource_url=url,
        base_credits=_scaled(limit),
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_items = await native.fetch_user_posts(profile_url, limit=fetch_cap)
            if native_items:
                ctx["source"] = "direct"
                rows = native_items
            else:
                items = _good_rows(
                    await _run_kwai({"urls": [profile_url], "maxItems": fetch_cap}, max_items=fetch_cap)
                )
                if not items:
                    raise HTTPException(status_code=404, detail="Kwai profile not found")
                ctx["source"] = "apify"
                rows = items

            page_rows = rows[offset : offset + limit]
            posts = [_normalize_post(i, include_author=False) for i in page_rows]
            author = None
            for i in rows:
                author = _author_card(_author(i))
                if author:
                    break
            next_offset = offset + len(posts)
            has_more = next_offset < len(rows)
            out: dict[str, Any] = {
                "profileUrl": profile_url,
                "totalReturned": len(posts),
                "nextCursor": _encode_posts_cursor(next_offset) if has_more else None,
                "hasMore": has_more,
                "posts": posts,
            }
            if author:
                out["author"] = author
            return out

        data = await cached_or_run(
            "kwai.user-posts",
            {"url": profile_url, "limit": limit, "cursor": cursor or "", "v": 8},
            _run,
            ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]))
        return ApiResponse(data=data)


@router.get(
    "/post",
    summary="Kwai post",
    description=(
        "Single Kwai video as clean JSON: caption when published (placeholder "
        "\"...\" omitted), author{}, engagement, videoUrl/videoType=mp4, "
        "mediaUrlsExpireAt from the signed CDN tag, hashtags[] from the caption, "
        "and transcript when Kwai JSON-LD exposes auto-captions (deduped). Same "
        "core card as user-posts rows, plus hashtags. Flat 2 credits."
    ),
)
async def post(
    url: str = Query(..., description="Kwai video URL (e.g. https://www.kwai.com/@handle/video/5238962376325675745)"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    video_url = _video_url(url)
    if not video_url:
        raise HTTPException(status_code=400, detail="Invalid Kwai post URL")
    async with billed_call(
        caller=caller,
        endpoint="/v1/kwai/post",
        platform="kwai",
        resource_url=url,
        base_credits=CREDIT_POST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_row = await native.fetch_post(video_url)
            if native_row:
                ctx["source"] = "direct"
                row = native_row
            else:
                items = _good_rows(await _run_kwai({"urls": [video_url], "maxItems": 1}, max_items=1))
                if not items:
                    raise HTTPException(status_code=404, detail="Kwai post not found")
                ctx["source"] = "apify"
                row = items[0]
            out = _normalize_post(row, include_author=True)
            tags = _hashtags(out.get("text") if isinstance(out.get("text"), str) else None)
            if tags:
                out["hashtags"] = tags
            return out

        data = await cached_or_run("kwai.post", {"url": video_url, "v": 8}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)
