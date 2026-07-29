"""Self-scraped Twitch data via the public web GraphQL API (no Apify).

The Twitch web client talks to ``gql.twitch.tv/gql`` with a well-known public
Client-ID that ships in the browser bundle and is used for every anonymous
request. We reuse it to pull channel/profile, recent videos, and clip metadata
directly - far cheaper and faster than the Apify actor.

All functions return the exact shapes ``routers/twitch.py`` already emits
(via ``_profile`` / ``_video``), or ``None`` on failure so the caller can fall
back to the actor.
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx

from app.services.http_fetch import post_json
from app.utils.formatters import safe_int, safe_str

# Public web Client-ID (anonymous). Same value the Twitch web app sends; not a
# secret and not tied to our account.
_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
_GQL_URL = "https://gql.twitch.tv/gql"


def _gql_headers() -> dict[str, str]:
    return {
        "Client-ID": _CLIENT_ID,
        "Accept": "application/json",
        "Content-Type": "application/json",
        # Fresh device id per request reduces intermittent integrity rejects.
        "Device-ID": uuid.uuid4().hex,
        "X-Device-Id": uuid.uuid4().hex,
    }


async def _gql_direct(query: str, variables: dict[str, Any], *, timeout: float = 15) -> dict[str, Any] | None:
    """POST GraphQL without a proxy (server egress)."""
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=_gql_headers()) as client:
            resp = await client.post(_GQL_URL, json={"query": query, "variables": variables})
    except httpx.HTTPError:
        return None
    return _parse_gql_response(resp)


async def _gql_via_tier(
    query: str, variables: dict[str, Any], *, tier: str, timeout: float = 15
) -> dict[str, Any] | None:
    try:
        resp = await post_json(
            _GQL_URL,
            {"query": query, "variables": variables},
            tier=tier,  # type: ignore[arg-type]
            headers=_gql_headers(),
            timeout=timeout,
        )
    except httpx.HTTPError:
        return None
    return _parse_gql_response(resp)


def _parse_gql_response(resp: httpx.Response) -> dict[str, Any] | None:
    if resp.status_code >= 400:
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    # Twitch often returns partial ``data`` alongside non-fatal ``errors``;
    # prefer usable data over a hard reject.
    if isinstance(data, dict) and data:
        return data
    if payload.get("errors"):
        return None
    return None


async def _gql(query: str, variables: dict[str, Any]) -> dict[str, Any] | None:
    """GraphQL with multi-tier retries (datacenter → residential → direct)."""
    for tier in ("datacenter", "datacenter", "residential", "residential", "none"):
        got = await _gql_via_tier(query, variables, tier=tier)
        if got is not None:
            return got
    # Last resort: bare httpx client (same as tier=none, but fresh headers).
    return await _gql_direct(query, variables)


def _video_node(
    node: dict[str, Any],
    *,
    broadcaster: str | None = None,
    profile_image: str | None = None,
) -> dict[str, Any]:
    game = node.get("game") or {}
    video_id = safe_str(node.get("id"))
    # VODs have no clip slug and no public MP4 URL (tokenized). Omit those
    # keys rather than returning always-null placeholders; clips keep them.
    return {
        "platform": "twitch",
        "id": video_id,
        "url": (f"https://www.twitch.tv/videos/{video_id}" if video_id else None),
        "embedUrl": (
            f"https://player.twitch.tv/?video={video_id}&parent=captapi.com" if video_id else None
        ),
        "title": safe_str(node.get("title")),
        "createdAt": safe_str(node.get("createdAt")),
        "durationSeconds": safe_int(node.get("lengthSeconds")),
        "views": safe_int(node.get("viewCount")),
        "thumbnail": safe_str(node.get("previewThumbnailURL")),
        "game": safe_str(game.get("name") if isinstance(game, dict) else game),
        "language": safe_str(node.get("language")),
        "broadcaster": broadcaster,
        "broadcasterProfileImage": profile_image,
    }


_PROFILE_QUERY = """
query($login: String!, $videoLimit: Int!) {
  user(login: $login) {
    id login displayName description createdAt
    profileImageURL(width: 300)
    bannerImageURL
    roles { isPartner isAffiliate }
    followers { totalCount }
    stream {
      id title viewersCount type createdAt
      previewImageURL(width: 640, height: 360)
      game { name }
    }
    lastBroadcast { title startedAt game { name } }
    videos(first: $videoLimit, sort: TIME) {
      edges { node { id title lengthSeconds viewCount createdAt previewThumbnailURL language game { name } } }
    }
  }
}
"""

# Lighter query used when the full profile query is rejected / rate-limited.
_PROFILE_LITE_QUERY = """
query($login: String!) {
  user(login: $login) {
    id login displayName description createdAt
    profileImageURL(width: 300)
    bannerImageURL
    roles { isPartner isAffiliate }
    followers { totalCount }
    stream {
      id title viewersCount type createdAt
      previewImageURL(width: 640, height: 360)
      game { name }
    }
    lastBroadcast { title startedAt game { name } }
  }
}
"""


def _map_channel(u: dict[str, Any], login: str, recent: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    roles = u.get("roles") or {}
    stream = u.get("stream")
    last = u.get("lastBroadcast") or {}
    login_val = safe_str(u.get("login")) or login
    profile_image = safe_str(u.get("profileImageURL"))
    stream_block = {
        "title": safe_str((stream or {}).get("title")),
        "game": safe_str(((stream or {}).get("game") or {}).get("name")) if stream else None,
        "viewers": safe_int((stream or {}).get("viewersCount")) if stream else None,
        "startedAt": safe_str((stream or {}).get("createdAt")) if stream else None,
        "thumbnail": safe_str((stream or {}).get("previewImageURL")) if stream else None,
    }
    return {
        "platform": "twitch",
        "id": safe_str(u.get("id")),
        "login": login_val,
        "displayName": safe_str(u.get("displayName")),
        "url": f"https://www.twitch.tv/{login_val}",
        "description": safe_str(u.get("description")),
        "followers": safe_int((u.get("followers") or {}).get("totalCount")),
        "profileImage": safe_str(u.get("profileImageURL")),
        "bannerImage": safe_str(u.get("bannerImageURL")),
        "isPartner": bool(roles.get("isPartner")),
        "isAffiliate": bool(roles.get("isAffiliate")),
        "isLive": bool(stream),
        "stream": stream_block,
        "lastBroadcast": {
            "title": safe_str(last.get("title")),
            "game": safe_str((last.get("game") or {}).get("name")),
            "startedAt": safe_str(last.get("startedAt")),
        },
        "recentVideos": recent if recent is not None else [],
        "topClips": [],
        "schedule": [],
        "createdAt": safe_str(u.get("createdAt")),
    }


async def channel_native(login: str, video_limit: int = 30) -> dict[str, Any] | None:
    login_key = (login or "").strip().lstrip("@")
    if not login_key:
        return None
    vlim = min(max(video_limit, 1), 100)

    data = await _gql(_PROFILE_QUERY, {"login": login_key, "videoLimit": vlim})
    u = (data or {}).get("user") if isinstance(data, dict) else None
    if not isinstance(u, dict) or not u.get("id"):
        # Full query occasionally trips complexity limits — retry lite shape.
        data = await _gql(_PROFILE_LITE_QUERY, {"login": login_key})
        u = (data or {}).get("user") if isinstance(data, dict) else None
        if not isinstance(u, dict) or not u.get("id"):
            return None
        return _map_channel(u, login_key, recent=[])

    login_val = safe_str(u.get("login")) or login_key
    profile_image = safe_str(u.get("profileImageURL"))
    edges = ((u.get("videos") or {}).get("edges")) or []
    recent = [
        _video_node(e["node"], broadcaster=login_val, profile_image=profile_image)
        for e in edges
        if isinstance(e, dict) and isinstance(e.get("node"), dict)
    ]
    return _map_channel(u, login_key, recent=recent)


_CLIP_QUERY = """
query($slug: ID!) {
  clip(slug: $slug) {
    id slug title createdAt viewCount durationSeconds
    url embedURL thumbnailURL
    game { name }
    broadcaster { login displayName profileImageURL(width: 150) }
    videoQualities { quality sourceURL }
  }
}
"""


async def clip_native(slug: str) -> dict[str, Any] | None:
    data = await _gql(_CLIP_QUERY, {"slug": slug})
    if not data:
        return None
    c = data.get("clip")
    if not c or not c.get("id"):
        return None
    game = c.get("game") or {}
    b = c.get("broadcaster") or {}
    qualities = c.get("videoQualities") or []
    mp4 = safe_str(qualities[0].get("sourceURL")) if qualities else None
    return {
        "platform": "twitch",
        "id": safe_str(c.get("id")),
        "slug": safe_str(c.get("slug")),
        "url": safe_str(c.get("url")) or (f"https://clips.twitch.tv/{c.get('slug')}" if c.get("slug") else None),
        "embedUrl": safe_str(c.get("embedURL")) or (f"https://clips.twitch.tv/embed?clip={c.get('slug')}" if c.get("slug") else None),
        "title": safe_str(c.get("title")),
        "createdAt": safe_str(c.get("createdAt")),
        "durationSeconds": safe_int(c.get("durationSeconds")),
        "views": safe_int(c.get("viewCount")),
        "thumbnail": safe_str(c.get("thumbnailURL")),
        "videoUrl": mp4,
        "game": safe_str(game.get("name") if isinstance(game, dict) else game),
        "language": None,
        "broadcaster": safe_str(b.get("login") or b.get("displayName")),
        "broadcasterProfileImage": safe_str(b.get("profileImageURL")),
    }


_SCHEDULE_QUERY = """
query($login: String!) {
  user(login: $login) {
    channel {
      schedule {
        segments {
          title startAt endAt
          categories { name }
        }
      }
    }
  }
}
"""


async def schedule_native(login: str) -> list[dict[str, Any]] | None:
    """Upcoming schedule segments. Returns None on error, [] when the channel
    simply has no schedule set (a valid empty result)."""
    data = await _gql(_SCHEDULE_QUERY, {"login": login})
    if data is None:
        return None
    u = data.get("user")
    if not u:
        return None
    schedule = ((u.get("channel") or {}).get("schedule")) or {}
    segments = schedule.get("segments") or []
    out: list[dict[str, Any]] = []
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        cats = seg.get("categories") or []
        game = safe_str(cats[0].get("name")) if cats and isinstance(cats[0], dict) else None
        out.append(
            {
                "title": safe_str(seg.get("title")),
                "startAt": safe_str(seg.get("startAt")),
                "endAt": safe_str(seg.get("endAt")),
                "game": game,
            }
        )
    return out
