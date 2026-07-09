"""Instagram data via HikerAPI (pay-per-request, sub-second).

Used as the primary path for Instagram endpoints when ``HIKERAPI_KEY`` is set.
Functions return the exact response shapes ``routers/instagram.py`` already
emits, or ``None`` on failure so the router can fall back to Apify actors.

``/v1/instagram/details`` intentionally stays on Apify (high-traffic customer).
Transcript/summarize and trending-reels have no Hiker equivalent and keep Apify.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import get_settings
from app.utils.formatters import safe_float, safe_int, safe_str
from app.utils.url import extract_instagram_shortcode

_BASE = "https://api.hikerapi.com"
_HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)
_AUDIO_ID_RE = re.compile(r"/reels/audio/(\d+)")


def enabled() -> bool:
    return bool(get_settings().HIKERAPI_KEY.strip())


def _headers() -> dict[str, str]:
    return {"x-access-key": get_settings().HIKERAPI_KEY, "accept": "application/json"}


async def _get(path: str, params: dict[str, Any] | None = None) -> Any | None:
    if not enabled():
        return None
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=_headers()) as client:
            resp = await client.get(f"{_BASE}{path}", params=params or {})
    except httpx.HTTPError:
        return None
    if resp.status_code >= 400:
        return None
    try:
        return resp.json()
    except ValueError:
        return None


def _unpack_chunk(data: Any) -> tuple[list[Any], str | None]:
    """Hiker chunk endpoints return ``[items, cursor, ...]``."""
    if not isinstance(data, list) or not data:
        return [], None
    head = data[0]
    items = head if isinstance(head, list) else ([head] if isinstance(head, dict) else [])
    cursor = None
    if len(data) > 1 and isinstance(data[1], str) and data[1]:
        cursor = data[1]
    return items, cursor


async def _collect_chunk(
    path: str,
    params: dict[str, Any],
    *,
    limit: int,
    cursor_key: str = "max_id",
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(25):
        if len(out) >= limit:
            break
        p = dict(params)
        if cursor:
            p[cursor_key] = cursor
        raw = await _get(path, p)
        if raw is None:
            break
        items, cursor = _unpack_chunk(raw)
        for item in items:
            if isinstance(item, dict):
                out.append(item)
                if len(out) >= limit:
                    break
        if not cursor:
            break
    return out[:limit]


def _ts_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    return safe_str(value) or None


def _caption_text(media: dict[str, Any]) -> str:
    cap = media.get("caption_text")
    if cap:
        return safe_str(cap)
    nested = media.get("caption")
    if isinstance(nested, dict):
        return safe_str(nested.get("text"))
    return safe_str(nested)


def _thumb(media: dict[str, Any]) -> str | None:
    thumb = safe_str(media.get("thumbnail_url"))
    if thumb:
        return thumb
    iv2 = media.get("image_versions2") or {}
    cands = iv2.get("candidates") if isinstance(iv2, dict) else None
    if isinstance(cands, list) and cands and isinstance(cands[0], dict):
        return safe_str(cands[0].get("url"))
    imgs = media.get("image_versions")
    if isinstance(imgs, list) and imgs and isinstance(imgs[0], dict):
        return safe_str(imgs[0].get("url"))
    return None


def _video_url(media: dict[str, Any]) -> str | None:
    vu = safe_str(media.get("video_url"))
    if vu:
        return vu
    vv = media.get("video_versions")
    if isinstance(vv, list) and vv and isinstance(vv[0], dict):
        return safe_str(vv[0].get("url"))
    return None


def _media_type_label(media: dict[str, Any]) -> str:
    if media.get("product_type") == "clips":
        return "Video"
    mt = safe_int(media.get("media_type"))
    if mt == 2:
        return "Video"
    if mt == 8:
        return "Sidecar"
    return "Image"


def _hashtags_from_caption(text: str) -> list[str]:
    return list(dict.fromkeys(_HASHTAG_RE.findall(text or "")))


def normalize_post(media: dict[str, Any]) -> dict[str, Any]:
    """Map a Hiker Media object to our ``_normalize_post`` output shape."""
    user = media.get("user") or {}
    username = safe_str(user.get("username"))
    code = safe_str(media.get("code"))
    caption = _caption_text(media)
    url = (
        f"https://www.instagram.com/reel/{code}/"
        if media.get("product_type") == "clips" and code
        else (f"https://www.instagram.com/p/{code}/" if code else None)
    )
    return {
        "platform": "instagram",
        "url": url,
        "id": safe_str(media.get("pk") or media.get("id")),
        "type": _media_type_label(media),
        "productType": safe_str(media.get("product_type")),
        "caption": caption,
        "description": caption,
        "publishedAt": _ts_iso(media.get("taken_at") or media.get("taken_at_ts")),
        "durationSeconds": safe_float(media.get("video_duration")),
        "thumbnailUrl": _thumb(media),
        "videoUrl": _video_url(media),
        "author": {
            "username": username,
            "displayName": safe_str(user.get("full_name")),
            "url": f"https://instagram.com/{username}" if username else None,
            "followers": None,
            "verified": user.get("is_verified"),
            "profileImage": safe_str(user.get("profile_pic_url")),
        },
        "engagement": {
            "views": safe_int(media.get("play_count") or media.get("view_count")),
            "likes": safe_int(media.get("like_count")) or 0,
            "comments": safe_int(media.get("comment_count")) or 0,
        },
        "hashtags": _hashtags_from_caption(caption),
        "mentions": [],
    }


def normalize_audio_reel(media: dict[str, Any], *, music_id: str | None = None) -> dict[str, Any]:
    """Shape expected by ``/reels-by-audio-id`` and ``/music-posts``."""
    post = normalize_post(media)
    return {
        "platform": "instagram",
        "url": post.get("url"),
        "id": post.get("id"),
        "caption": post.get("caption"),
        "description": post.get("description"),
        "publishedAt": post.get("publishedAt"),
        "durationSeconds": post.get("durationSeconds"),
        "thumbnailUrl": post.get("thumbnailUrl"),
        "videoUrl": post.get("videoUrl"),
        "author": post.get("author"),
        "engagement": post.get("engagement"),
        "musicId": music_id,
        "musicUrl": f"https://www.instagram.com/reels/audio/{music_id}/" if music_id else None,
    }


def _normalize_track_item(item: dict[str, Any], *, music_id: str | None = None) -> dict[str, Any] | None:
    media = item.get("media") if isinstance(item.get("media"), dict) else item
    if not isinstance(media, dict) or not media.get("code"):
        return None
    return normalize_audio_reel(media, music_id=music_id)


def _user_pk(user: dict[str, Any]) -> str | None:
    pk = user.get("pk") or user.get("id")
    return safe_str(pk) if pk is not None else None


async def user_by_username(username: str) -> dict[str, Any] | None:
    data = await _get("/v1/user/by/username", {"username": username})
    return data if isinstance(data, dict) and data.get("username") else None


async def channel_details(handle: str) -> dict[str, Any] | None:
    u = await user_by_username(handle)
    if not u:
        return None
    username = safe_str(u.get("username")) or handle
    return {
        "platform": "instagram",
        "url": f"https://instagram.com/{username}",
        "username": username,
        "displayName": safe_str(u.get("full_name")),
        "bio": safe_str(u.get("biography")),
        "followers": safe_int(u.get("follower_count")),
        "following": safe_int(u.get("following_count")),
        "postCount": safe_int(u.get("media_count")),
        "verified": u.get("is_verified"),
        "profileImage": safe_str(u.get("profile_pic_url") or u.get("profile_pic_url_hd")),
        "externalUrl": safe_str(u.get("external_url")),
    }


async def basic_profile(handle: str) -> dict[str, Any] | None:
    u = await user_by_username(handle)
    if not u:
        return None
    username = safe_str(u.get("username")) or handle
    return {
        "platform": "instagram",
        "id": _user_pk(u) or "",
        "username": username,
        "displayName": safe_str(u.get("full_name")),
        "profileImage": safe_str(u.get("profile_pic_url") or u.get("profile_pic_url_hd")),
        "verified": u.get("is_verified"),
        "private": u.get("is_private"),
        "followers": safe_int(u.get("follower_count")),
    }


async def _user_id(handle: str) -> str | None:
    u = await user_by_username(handle)
    return _user_pk(u) if u else None


async def channel_posts(handle: str, limit: int) -> list[dict[str, Any]] | None:
    uid = await _user_id(handle)
    if not uid:
        return None
    raw = await _collect_chunk("/v1/user/medias/chunk", {"user_id": uid}, limit=limit * 2)
    posts = [normalize_post(m) for m in raw if m.get("product_type") != "clips"]
    return posts[:limit] if posts else None


async def channel_reels(handle: str, limit: int) -> list[dict[str, Any]] | None:
    uid = await _user_id(handle)
    if not uid:
        return None
    raw = await _collect_chunk("/v1/user/clips/chunk", {"user_id": uid}, limit=limit)
    reels = [normalize_post(m) for m in raw]
    return reels if reels else None


async def media_by_url(url: str) -> dict[str, Any] | None:
    data = await _get("/v1/media/by/url", {"url": url})
    return data if isinstance(data, dict) and data.get("pk") else None


async def comments(url: str, limit: int) -> list[dict[str, Any]] | None:
    media = await media_by_url(url)
    if not media:
        return None
    mid = safe_str(media.get("pk"))
    if not mid:
        return None
    raw = await _collect_chunk("/v1/media/comments/chunk", {"id": mid}, limit=limit, cursor_key="max_id")
    out: list[dict[str, Any]] = []
    for c in raw:
        user = c.get("user") or {}
        out.append(
            {
                "id": safe_str(c.get("pk") or c.get("id")),
                "url": None,
                "text": safe_str(c.get("text")).strip(),
                "author": safe_str(user.get("username")),
                "authorAvatarUrl": safe_str(user.get("profile_pic_url")),
                "authorIsVerified": bool(user.get("is_verified")),
                "likeCount": safe_int(c.get("like_count")) or 0,
                "publishedAt": _ts_iso(c.get("created_at_utc") or c.get("created_at")),
                "replyCount": 0,
            }
        )
    return out if out else []


async def video_download(url: str) -> dict[str, Any] | None:
    media = await media_by_url(url)
    if not media:
        return None
    download_url = _video_url(media)
    if not download_url:
        return None
    return {
        "platform": "instagram",
        "url": url,
        "downloadUrl": download_url,
        "thumbnailUrl": _thumb(media),
        "duration": safe_float(media.get("video_duration")),
    }


def _clean_tag(q: str) -> str:
    return q.lstrip("#").strip()


async def hashtag_medias(tag: str, limit: int, *, reels_only: bool = False) -> list[dict[str, Any]] | None:
    name = _clean_tag(tag)
    if not name:
        return None
    path = "/v1/hashtag/medias/clips/chunk" if reels_only else "/v1/hashtag/medias/top/chunk"
    raw = await _collect_chunk(path, {"name": name}, limit=limit)
    results = [normalize_post(m) for m in raw]
    return results if results else None


async def profile_search(q: str, limit: int) -> list[dict[str, Any]] | None:
    data = await _get("/v1/search/users", {"query": q})
    if not isinstance(data, list):
        return None
    users: list[dict[str, Any]] = []
    for u in data[:limit]:
        if not isinstance(u, dict):
            continue
        username = safe_str(u.get("username"))
        if not username:
            continue
        users.append(
            {
                "username": username,
                "displayName": safe_str(u.get("full_name")),
                "url": f"https://instagram.com/{username}",
                "followers": safe_int(u.get("follower_count")),
                "verified": u.get("is_verified"),
                "private": u.get("is_private"),
                "profileImage": safe_str(u.get("profile_pic_url")),
            }
        )
    return users if users else None


async def tagged_posts(handle: str, limit: int) -> list[dict[str, Any]] | None:
    uid = await _user_id(handle)
    if not uid:
        return None
    raw = await _collect_chunk("/v1/user/tag/medias/chunk", {"user_id": uid}, limit=limit)
    posts = [normalize_post(m) for m in raw]
    return posts if posts else None


def _audio_id(audio_id_or_url: str) -> str | None:
    m = _AUDIO_ID_RE.search(audio_id_or_url)
    if m:
        return m.group(1)
    if audio_id_or_url.isdigit():
        return audio_id_or_url
    return None


async def _track_reels(audio_id: str, limit: int) -> list[dict[str, Any]] | None:
    out: list[dict[str, Any]] = []
    page_id: str | None = None
    for _ in range(25):
        if len(out) >= limit:
            break
        params: dict[str, Any] = {"id": audio_id}
        if page_id:
            params["page_id"] = page_id
        raw = await _get("/v2/track/by/id", params)
        if not isinstance(raw, dict):
            break
        body = raw.get("response") if isinstance(raw.get("response"), dict) else raw
        items = body.get("items") if isinstance(body, dict) else None
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                norm = _normalize_track_item(item, music_id=audio_id)
                if norm:
                    out.append(norm)
                    if len(out) >= limit:
                        break
        page_id = safe_str(raw.get("next_page_id")) or None
        if not page_id:
            break
    return out[:limit] if out else None


async def reels_by_audio(audio_id_or_url: str, limit: int) -> list[dict[str, Any]] | None:
    aid = _audio_id(audio_id_or_url)
    if not aid:
        return None
    return await _track_reels(aid, limit)


async def music_posts(audio_url: str, limit: int) -> list[dict[str, Any]] | None:
    return await reels_by_audio(audio_url, limit)


def _highlight_cover(h: dict[str, Any]) -> str | None:
    cm = h.get("cover_media") or {}
    if not isinstance(cm, dict):
        return None
    civ = cm.get("cropped_image_version") or {}
    if isinstance(civ, dict):
        return safe_str(civ.get("url"))
    return None


async def story_highlights(handle: str) -> list[dict[str, Any]] | None:
    data = await _get("/v1/user/highlights/by/username", {"username": handle})
    if not isinstance(data, list):
        return None
    out: list[dict[str, Any]] = []
    for h in data:
        if not isinstance(h, dict):
            continue
        out.append(
            {
                "id": safe_str(h.get("pk") or h.get("id")),
                "title": safe_str(h.get("title")),
                "coverUrl": _highlight_cover(h),
                "itemCount": safe_int(h.get("media_count")),
            }
        )
    return out


async def highlights_details(handle: str, limit: int) -> list[dict[str, Any]] | None:
    data = await _get("/v1/user/highlights/by/username", {"username": handle})
    if not isinstance(data, list):
        return None
    out: list[dict[str, Any]] = []
    for h in data[:limit]:
        if not isinstance(h, dict):
            continue
        pk = safe_str(h.get("pk"))
        if not pk:
            continue
        detail = await _get(
            "/v1/highlight/by/url",
            {"url": f"https://www.instagram.com/stories/highlights/{pk}/"},
        )
        if not isinstance(detail, dict):
            continue
        payload = {
            "id": pk,
            "title": safe_str(detail.get("title") or h.get("title")),
            "coverUrl": _highlight_cover(detail) or _highlight_cover(h),
            "itemCount": safe_int(detail.get("media_count") or h.get("media_count")),
            "items": [],
        }
        for m in detail.get("items") or []:
            if not isinstance(m, dict):
                continue
            mt = safe_int(m.get("media_type"))
            typ = "video" if mt == 2 else "image"
            payload["items"].append(
                {
                    "type": typ,
                    "url": _video_url(m) or _thumb(m),
                    "thumbnailUrl": _thumb(m),
                    "takenAt": _ts_iso(m.get("taken_at")),
                }
            )
        if payload["itemCount"] is None and payload["items"]:
            payload["itemCount"] = len(payload["items"])
        out.append(payload)
    return out if out else None


async def embed_html(url: str) -> dict[str, Any] | None:
    shortcode = extract_instagram_shortcode(url)
    if not shortcode:
        return None
    oembed = await _get("/v1/media/oembed", {"url": url})
    permalink = f"https://www.instagram.com/p/{shortcode}/"
    html = None
    if isinstance(oembed, dict) and oembed.get("html"):
        html = safe_str(oembed.get("html"))
    if not html:
        html = (
            '<blockquote class="instagram-media" '
            f'data-instgrm-permalink="{permalink}" data-instgrm-version="14"></blockquote>'
            '<script async src="//www.instagram.com/embed.js"></script>'
        )
    return {
        "platform": "instagram",
        "url": url,
        "shortcode": shortcode,
        "permalink": permalink,
        "html": html,
    }
