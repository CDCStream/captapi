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
from app.utils.formatters import first_present, safe_float, safe_int, safe_str

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
        return (
            datetime.fromtimestamp(value, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
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


# Instagram hashtags must contain at least one non-numeric character, so
# "#1" in a caption ("ranked #1") is not a real hashtag - require one letter
# or underscore to avoid capturing purely numeric tokens.
_HASHTAG_RE = re.compile(r"#(\w*[^\W\d]\w*)", re.UNICODE)
# Usernames may contain dots but never end with one, so "@kyliejenner." in a
# caption must capture "kyliejenner" without the trailing punctuation.
_MENTION_RE = re.compile(r"@([A-Za-z0-9_](?:[A-Za-z0-9_.]*[A-Za-z0-9_])?)")


def hidden_count(value: Any) -> int | None:
    """Normalize Instagram engagement counts.

    Instagram uses ``-1`` for hidden like counts — map that to ``None``.
    Missing values stay ``None`` too (never invent ``0``; silent zeros poison
    averages and engagement rates).
    """
    n = safe_int(value)
    if n is None or n < 0:
        return None
    return n


def dedupe_preserve(items: Iterable[Any] | None) -> list[str]:
    """Stable unique strings (caption @mentions often repeat)."""
    out: list[str] = []
    seen: set[str] = set()
    for raw in items or []:
        s = safe_str(raw)
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def pick_video_views(
    *,
    view_count: int | None,
    play_count: int | None,
    likes: int | None,
    is_video: bool,
) -> tuple[int | None, int | None]:
    """Pick ``(views, plays)`` for a post.

    GraphQL ``video_view_count`` undercounts many Reels vs real ``play_count``
    (and can sit *below* ``like_count`` — impossible for a real view metric).
    Prefer play counts for video; drop views when likes > views rather than
    inventing a swap.
    """
    if not is_video:
        return None, None
    # Prefer play_count — GraphQL video_view_count undercounts many Reels.
    views = play_count or view_count
    plays = None
    if view_count is not None and play_count is not None and view_count != play_count:
        # Secondary metric = the one not chosen as views.
        plays = view_count if views == play_count else play_count
    if likes is not None and views is not None and likes > views:
        views = None
    return views, plays


def strip_null_post_fields(post: dict[str, Any]) -> dict[str, Any]:
    """Drop fields we can't fill instead of returning nulls: video-only
    fields (videoUrl, durationSeconds) on images/carousels, hidden engagement
    counts (None) except ``engagement.views`` (always present — null on
    Image/Sidecar), and author fields the source doesn't provide.
    """
    if not post.get("videoUrl"):
        post.pop("videoUrl", None)
    if post.get("durationSeconds") is None:
        post.pop("durationSeconds", None)
    if post.get("productType") == "":
        post["productType"] = None
    engagement = post.get("engagement")
    if isinstance(engagement, dict):
        likes = engagement.get("likes")
        views = engagement.get("views")
        if likes is not None and views is not None and likes > views:
            engagement["views"] = None
            views = None
        cleaned = {k: v for k, v in engagement.items() if v is not None or k == "views"}
        # Typed clients always read engagement.views (null when unknown / N/A).
        cleaned["views"] = views
        post["engagement"] = cleaned
    author = post.get("author")
    if isinstance(author, dict):
        post["author"] = {k: v for k, v in author.items() if v is not None}
    for key in (
        "location",
        "music",
        "accessibilityCaption",
        "musicId",
        "previewComments",
        "shortcode",
        "mediaId",
        "hasAudio",
    ):
        val = post.get(key)
        if val in (None, [], {}):
            post.pop(key, None)
    return post


def _post(node: dict[str, Any], profile: dict[str, Any] | None = None) -> dict[str, Any]:
    # Per-post nodes only carry a minimal owner ({id, username}); the full
    # author (name, verified, avatar, followers) lives on the profile object,
    # which is the same for every post in a channel listing. `profile` fills
    # those gaps when the caller knows the owning profile â€” but only when the
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
    media_id = safe_str(node.get("id") or node.get("pk"))
    typename = safe_str(node.get("__typename"))
    is_video = bool(node.get("is_video")) or typename == "GraphVideo"
    is_sidecar = typename == "GraphSidecar"
    caption = _caption(node) or ""
    view_count = safe_int(node.get("video_view_count") or node.get("views"))
    play_count = safe_int(
        node.get("video_play_count") or node.get("play_count") or node.get("ig_play_count")
    )
    likes = hidden_count(
        first_present(
            _count(node.get("edge_media_preview_like")),
            _count(node.get("edge_liked_by")),
            node.get("like_count"),
            node.get("likes"),
        )
    )
    views, plays = pick_video_views(
        view_count=view_count,
        play_count=play_count,
        likes=likes,
        is_video=is_video,
    )
    product = safe_str(node.get("product_type")) or ("clips" if is_video else None)
    # Prefer shortcode as id (matches Polaris hydrate + enrich_posts_from_author_feeds).
    result = {
        "platform": "instagram",
        "url": safe_str(node.get("url"))
        or (f"https://www.instagram.com/{'reel' if is_video else 'p'}/{shortcode}/" if shortcode else None),
        "id": shortcode or media_id,
        "shortcode": shortcode,
        "mediaId": media_id if media_id and media_id != shortcode else None,
        "postType": "Sidecar" if is_sidecar else ("Video" if is_video else "Image"),
        "productType": product,
        "caption": caption,
        "description": caption,
        "publishedAt": _iso_timestamp(node.get("taken_at_timestamp") or node.get("date_posted")),
        "durationSeconds": safe_float(node.get("video_duration") or node.get("length")),
        "thumbnailUrl": _image_url(node),
        "videoUrl": safe_str(node.get("video_url")) or None,
        "hasAudio": node.get("has_audio") if node.get("has_audio") is not None else None,
        "author": {
            "username": username,
            "displayName": safe_str(author.get("full_name")),
            "url": f"https://instagram.com/{username}" if username else None,
            "followers": _count(author.get("edge_followed_by")),
            "verified": author.get("is_verified"),
            "profileImage": _image_url(author),
        },
        "engagement": {
            "views": views,
            "plays": plays,
            "likes": likes,
            "comments": hidden_count(
                first_present(
                    _count(node.get("edge_media_to_comment")),
                    node.get("comment_count"),
                    node.get("num_comments"),
                )
            ),
        },
        "hashtags": dedupe_preserve(_HASHTAG_RE.findall(caption)),
        "mentions": dedupe_preserve(_MENTION_RE.findall(caption)),
        "isPaidPartnership": bool(node.get("is_paid_partnership"))
        if node.get("is_paid_partnership") is not None
        else False,
        "isAd": bool(node.get("is_ad") or node.get("ad_id")),
        "isAffiliate": bool(node.get("affiliate_info") or node.get("is_affiliate")),
        "accessibilityCaption": safe_str(node.get("accessibility_caption")),
    }
    loc = node.get("location") if isinstance(node.get("location"), dict) else None
    if loc and (loc.get("name") or loc.get("id") or loc.get("pk")):
        result["location"] = {
            "id": safe_str(loc.get("pk") or loc.get("id")),
            "name": safe_str(loc.get("name")),
            "latitude": safe_float(loc.get("lat") or loc.get("latitude")),
            "longitude": safe_float(loc.get("lng") or loc.get("longitude")),
        }
        result["location"] = {k: v for k, v in result["location"].items() if v is not None}
    music = node.get("clips_music_attribution_info")
    if isinstance(music, dict) and (
        music.get("audio_id") or music.get("song_name") or music.get("artist_name")
    ):
        result["music"] = {
            "id": safe_str(music.get("audio_id")),
            "title": safe_str(music.get("song_name")),
            "artist": safe_str(music.get("artist_name")),
        }
        result["musicId"] = result["music"].get("id")
    # Owner stats when the GraphQL node carries them (often only on richer edges).
    if isinstance(owner, dict):
        followers = _count(owner.get("edge_followed_by")) or safe_int(owner.get("follower_count"))
        posts = _count(owner.get("edge_owner_to_timeline_media")) or safe_int(
            owner.get("media_count") or owner.get("post_count")
        )
        if followers is not None:
            result["author"]["followers"] = followers
        if posts is not None:
            result["author"]["postCount"] = posts
        if owner.get("is_private") is not None:
            result["author"]["private"] = owner.get("is_private")
        oid = safe_str(owner.get("id") or owner.get("pk"))
        if oid:
            result["author"]["id"] = oid
    return strip_null_post_fields(result)


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
    # Keep field parity with instagram_native.map_channel_details (additive).
    from app.services.instagram_native import map_channel_details

    user = await _profile(handle)
    if not user:
        return None
    return map_channel_details(user, handle=handle)


async def profile_user(handle: str) -> dict[str, Any] | None:
    """Raw Instagram GraphQL user node for profile-search enrichment."""
    return await _profile(handle)


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


async def channel_posts(handle: str, limit: int) -> dict[str, Any] | None:
    """First timeline page. Returns {"items", "userId", "hasMore", "followers"}
    so the router can build a feed cursor (``<media pk>_<user id>``) and
    continue through Instagram's api/v1 feed endpoint."""
    user = await _profile(handle)
    if not user:
        return None
    nodes = _edge_nodes(user, "edge_owner_to_timeline_media")
    posts = [_post(node, profile=user) for node in nodes]
    if not posts:
        return None
    timeline = user.get("edge_owner_to_timeline_media") or {}
    has_more = bool((timeline.get("page_info") or {}).get("has_next_page")) or len(posts) > limit
    return {
        "items": posts[:limit],
        "userId": safe_str(user.get("id")),
        "hasMore": has_more,
        "followers": _count(user.get("edge_followed_by")),
    }


async def channel_reels(handle: str, limit: int) -> dict[str, Any] | None:
    user = await _profile(handle)
    if not user:
        return None
    # The felix (IGTV) edge only carries legacy uploads that stop around
    # 2022, so leading with it buries an account's actual recent Reels.
    # Videos on the regular timeline come first; felix is a fallback for
    # accounts whose videos never hit the grid.
    def _videos(*edges: str) -> list[dict[str, Any]]:
        return [
            _post(node, profile=user)
            for node in _edge_nodes(user, *edges)
            if bool(node.get("is_video")) or node.get("__typename") == "GraphVideo"
        ]

    reels = _videos("edge_owner_to_timeline_media") or _videos("edge_felix_video_timeline")
    timeline = user.get("edge_owner_to_timeline_media") or {}
    has_more = bool((timeline.get("page_info") or {}).get("has_next_page")) or len(reels) > limit
    return {
        "items": reels[:limit],
        "userId": safe_str(user.get("id")),
        "hasMore": has_more,
        "followers": _count(user.get("edge_followed_by")),
    }


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
