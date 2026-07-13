"""Instagram data through Decodo's managed Social Media Scraping API.

Only Decodo targets with a documented Instagram GraphQL equivalent are used.
Every public function returns ``None`` on transport, auth, parsing, or data
quality failure so the router can safely fall back to Apify.
"""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from typing import Any, Iterable

import httpx
import structlog

from app.core.config import get_settings
from app.utils.formatters import safe_float, safe_int, safe_str

log = structlog.get_logger(__name__)


def enabled() -> bool:
    settings = get_settings()
    if settings.DECODO_AUTH_TOKEN.strip():
        return True
    return bool(settings.DECODO_USERNAME.strip() and settings.DECODO_PASSWORD.strip())


def _auth_header() -> str | None:
    """Decodo accepts a single Basic token or base64(user:pass)."""
    settings = get_settings()
    token = settings.DECODO_AUTH_TOKEN.strip()
    if token:
        return token if token.lower().startswith("basic ") else f"Basic {token}"
    user = settings.DECODO_USERNAME.strip()
    password = settings.DECODO_PASSWORD.strip()
    if user and password:
        encoded = base64.b64encode(f"{user}:{password}".encode()).decode()
        return f"Basic {encoded}"
    return None


async def _scrape(target: str, params: dict[str, Any]) -> Any | None:
    """POST to Decodo /v2/scrape. ``params`` holds target-specific input
    (v2 GraphQL targets take ``query``; URL-based targets take ``url``)."""
    if not enabled():
        return None
    settings = get_settings()
    auth_header = _auth_header()
    if not auth_header:
        return None
    body: dict[str, Any] = {
        "target": target,
        "locale": settings.DECODO_LOCALE,
        **params,
    }
    if settings.DECODO_GEO:
        body["geo"] = settings.DECODO_GEO
    try:
        async with httpx.AsyncClient(timeout=75.0) as client:
            response = await client.post(
                f"{settings.DECODO_BASE.rstrip('/')}/scrape",
                json=body,
                headers={
                    "Accept": "application/json",
                    "Authorization": auth_header,
                },
            )
    except httpx.HTTPError as exc:
        log.warning("decodo_transport_error", target=target, error=str(exc))
        return None
    if response.status_code != 200:
        log.warning("decodo_http_error", target=target, status=response.status_code)
        return None
    try:
        payload = response.json()
    except ValueError:
        return None
    if isinstance(payload, dict):
        # v2 envelope: {"results": [{"content": ...}]}
        results = payload.get("results")
        if isinstance(results, list) and results and isinstance(results[0], dict):
            content = results[0].get("content")
            if isinstance(content, str):
                try:
                    return json.loads(content)
                except ValueError:
                    return None
            if content is not None:
                return content
        # legacy envelope: {"data": {"content": ...}}
        data = payload.get("data")
        if isinstance(data, dict) and data.get("content") is not None:
            content = data["content"]
            if isinstance(content, str):
                try:
                    return json.loads(content)
                except ValueError:
                    return None
            return content
    return payload


def _walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _first_dict(value: Any, *keys: str) -> dict[str, Any] | None:
    for item in _walk(value):
        for key in keys:
            candidate = item.get(key)
            if isinstance(candidate, dict):
                return candidate
    return None


def _edge_nodes(value: Any, *edge_keys: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in _walk(value):
        for key in edge_keys:
            edge = item.get(key)
            if not isinstance(edge, dict) or not isinstance(edge.get("edges"), list):
                continue
            for row in edge["edges"]:
                if not isinstance(row, dict) or not isinstance(row.get("node"), dict):
                    continue
                node = row["node"]
                identity = safe_str(node.get("id") or node.get("shortcode"))
                if identity and identity in seen:
                    continue
                if identity:
                    seen.add(identity)
                result.append(node)
    return result


def _count(value: Any) -> int | None:
    if isinstance(value, dict):
        return safe_int(value.get("count"))
    return safe_int(value)


def _iso_timestamp(value: Any) -> str | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    return safe_str(value) or None


def _image_url(node: dict[str, Any]) -> str | None:
    resources = node.get("display_resources")
    if isinstance(resources, list) and resources:
        last = resources[-1]
        if isinstance(last, dict) and last.get("src"):
            return safe_str(last["src"])
    return safe_str(
        node.get("display_url")
        or node.get("thumbnail_src")
        or node.get("profile_pic_url_hd")
        or node.get("profile_pic_url")
    ) or None


def _caption(node: dict[str, Any]) -> str:
    edges = node.get("edge_media_to_caption")
    if isinstance(edges, dict) and isinstance(edges.get("edges"), list) and edges["edges"]:
        first = edges["edges"][0]
        if isinstance(first, dict) and isinstance(first.get("node"), dict):
            return safe_str(first["node"].get("text"))
    return safe_str(node.get("caption") or node.get("description"))


def _owner(node: dict[str, Any]) -> dict[str, Any]:
    value = node.get("owner")
    return value if isinstance(value, dict) else {}


_HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)
# Usernames may contain dots but never end with one, so "@kyliejenner." in a
# caption must capture "kyliejenner" without the trailing punctuation.
_MENTION_RE = re.compile(r"@([A-Za-z0-9_](?:[A-Za-z0-9_.]*[A-Za-z0-9_])?)")


def strip_null_video_fields(post: dict[str, Any]) -> dict[str, Any]:
    """Video-only fields (videoUrl, durationSeconds, views) don't exist for
    images/carousels; drop them instead of returning nulls."""
    if not post.get("videoUrl"):
        post.pop("videoUrl", None)
    if post.get("durationSeconds") is None:
        post.pop("durationSeconds", None)
    engagement = post.get("engagement")
    if isinstance(engagement, dict) and engagement.get("views") is None:
        engagement.pop("views", None)
    return post


def _post(node: dict[str, Any], profile: dict[str, Any] | None = None) -> dict[str, Any]:
    # Per-post nodes only carry a minimal owner ({id, username}); the full
    # author (name, verified, avatar, followers) lives on the profile object,
    # which is the same for every post in a channel listing. `profile` fills
    # those gaps when the caller knows the owning profile — but only when the
    # node is actually owned by that profile (collab posts can be owned by a
    # different account).
    owner = _owner(node)
    owner_username = safe_str(owner.get("username"))
    profile_username = safe_str((profile or {}).get("username"))
    if profile and (not owner_username or owner_username == profile_username):
        author = {**profile, **owner}
    else:
        author = owner
    username = safe_str(author.get("username") or node.get("user_posted"))
    shortcode = safe_str(node.get("shortcode") or node.get("code"))
    typename = safe_str(node.get("__typename"))
    is_video = bool(node.get("is_video")) or typename == "GraphVideo"
    is_sidecar = typename == "GraphSidecar"
    caption = _caption(node) or ""
    result = {
        "platform": "instagram",
        "url": safe_str(node.get("url"))
        or (f"https://www.instagram.com/{'reel' if is_video else 'p'}/{shortcode}/" if shortcode else None),
        "id": safe_str(node.get("id")),
        "type": "Sidecar" if is_sidecar else ("Video" if is_video else "Image"),
        "isVideo": is_video,
        "productType": safe_str(node.get("product_type")) or ("clips" if is_video else ""),
        "caption": caption,
        "description": caption,
        "publishedAt": _iso_timestamp(node.get("taken_at_timestamp") or node.get("date_posted")),
        "durationSeconds": safe_float(node.get("video_duration") or node.get("length")),
        "thumbnailUrl": _image_url(node),
        "videoUrl": safe_str(node.get("video_url")) or None,
        "author": {
            "username": username,
            "displayName": safe_str(author.get("full_name")),
            "url": f"https://instagram.com/{username}" if username else None,
            "followers": _count(author.get("edge_followed_by")),
            "verified": author.get("is_verified"),
            "profileImage": _image_url(author),
        },
        "engagement": {
            "views": safe_int(node.get("video_view_count") or node.get("video_play_count") or node.get("views")),
            "likes": _count(node.get("edge_media_preview_like")) or safe_int(node.get("likes")) or 0,
            "comments": _count(node.get("edge_media_to_comment")) or safe_int(node.get("num_comments")) or 0,
        },
        "hashtags": _HASHTAG_RE.findall(caption),
        "mentions": _MENTION_RE.findall(caption),
    }
    return strip_null_video_fields(result)


async def _profile(handle: str) -> dict[str, Any] | None:
    data = await _scrape(
        "instagram_graphql_profile",
        {"query": handle.strip().lstrip("@")},
    )
    user = _first_dict(data, "user")
    if user and (user.get("username") or user.get("id")):
        return user
    if isinstance(data, dict) and (data.get("username") or data.get("id")):
        return data
    return None


async def channel_details(handle: str) -> dict[str, Any] | None:
    user = await _profile(handle)
    if not user:
        return None
    username = safe_str(user.get("username")) or handle
    return {
        "platform": "instagram",
        "url": f"https://instagram.com/{username}",
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "bio": safe_str(user.get("biography")),
        "followers": _count(user.get("edge_followed_by")) or safe_int(user.get("followers")),
        "following": _count(user.get("edge_follow")) or safe_int(user.get("following")),
        "postCount": _count(user.get("edge_owner_to_timeline_media")) or safe_int(user.get("posts_count")),
        "verified": user.get("is_verified"),
        "profileImage": _image_url(user),
        "externalUrl": safe_str(user.get("external_url")),
    }


async def basic_profile(handle: str) -> dict[str, Any] | None:
    user = await _profile(handle)
    if not user:
        return None
    username = safe_str(user.get("username")) or handle
    return {
        "platform": "instagram",
        "id": safe_str(user.get("id")),
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "profileImage": _image_url(user),
        "verified": user.get("is_verified"),
        "private": user.get("is_private"),
        "followers": _count(user.get("edge_followed_by")) or safe_int(user.get("followers")),
    }


async def channel_posts(handle: str, limit: int) -> list[dict[str, Any]] | None:
    user = await _profile(handle)
    if not user:
        return None
    nodes = _edge_nodes(user, "edge_owner_to_timeline_media")
    posts = [_post(node, profile=user) for node in nodes if not bool(node.get("is_video"))]
    return posts[:limit] or None


async def channel_reels(handle: str, limit: int) -> list[dict[str, Any]] | None:
    user = await _profile(handle)
    if not user:
        return None
    nodes = _edge_nodes(user, "edge_felix_video_timeline", "edge_owner_to_timeline_media")
    reels = [
        _post(node, profile=user)
        for node in nodes
        if bool(node.get("is_video")) or node.get("__typename") == "GraphVideo"
    ]
    return reels[:limit] or None


async def hashtag_medias(tag: str, limit: int, *, reels_only: bool = False) -> list[dict[str, Any]] | None:
    name = tag.lstrip("#").strip()
    if not name:
        return None
    data = await _scrape("instagram_graphql_hashtag", {"query": name})
    nodes = _edge_nodes(data, "edge_hashtag_to_top_posts", "edge_hashtag_to_media")
    if reels_only:
        nodes = [node for node in nodes if bool(node.get("is_video")) or node.get("__typename") == "GraphVideo"]
    return [_post(node) for node in nodes[:limit]] or None


async def video_download(url: str) -> dict[str, Any] | None:
    data = await _scrape("instagram_graphql_post", {"url": url})
    media = _first_dict(data, "shortcode_media", "xdt_shortcode_media")
    if not media:
        return None
    download_url = safe_str(media.get("video_url"))
    if not download_url:
        return None
    return {
        "platform": "instagram",
        "url": url,
        "downloadUrl": download_url,
        "thumbnailUrl": _image_url(media),
        "duration": safe_float(media.get("video_duration")),
    }
