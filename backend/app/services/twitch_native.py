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

import json
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import unquote

import httpx

from app.services.http_fetch import post_json
from app.utils.formatters import safe_int, safe_str, strip_empty

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


def _game_fields(game: Any) -> tuple[str | None, str | None]:
    """Return (name, boxArtUrl). ``game`` stays a plain name string in the API."""
    if isinstance(game, dict):
        return safe_str(game.get("name")), safe_str(game.get("boxArtURL") or game.get("boxArtUrl"))
    return safe_str(game), None


def _video_node(
    node: dict[str, Any],
    *,
    broadcaster: str | None = None,
    profile_image: str | None = None,
    broadcaster_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    game = node.get("game") if isinstance(node.get("game"), dict) else {}
    game_name, game_box = _game_fields(node.get("game"))
    video_id = safe_str(node.get("id"))
    btype = safe_str(node.get("broadcastType") or node.get("broadcast_type"))
    # VODs have no clip slug and no public MP4 URL (tokenized). Omit those
    # keys rather than returning always-null placeholders; clips keep them.
    out: dict[str, Any] = {
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
        "animatedPreviewUrl": safe_str(node.get("animatedPreviewURL") or node.get("animatedPreviewUrl")),
        "broadcastType": btype,
        "game": game_name,
        "gameId": safe_str(game.get("id")),
        "gameSlug": safe_str(game.get("slug")),
        "gameBoxArtUrl": _box_art(game_box) if game_box and "{width}" in (game_box or "") else game_box,
        "language": safe_str(node.get("language")),
        # Flat string kept for back-compat; structured channel is additive.
        "broadcaster": broadcaster,
        "broadcasterProfileImage": profile_image,
        "channel": broadcaster_meta,
    }
    return strip_empty(out)


_VIDEO_TYPES = {"ARCHIVE", "HIGHLIGHT", "UPLOAD"}
_VIDEO_SORTS = {"TIME", "VIEWS"}

_VIDEOS_QUERY = """
query($login: String!, $first: Int!, $types: [BroadcastType!], $sort: VideoSort!) {
  user(login: $login) {
    id login displayName
    profileImageURL(width: 300)
    followers { totalCount }
    roles { isPartner isAffiliate }
    videos(first: $first, types: $types, sort: $sort) {
      pageInfo { hasNextPage }
      edges {
        node {
          id title lengthSeconds viewCount createdAt
          previewThumbnailURL animatedPreviewURL language
          broadcastType
          game { id name slug boxArtURL(width: 144, height: 192) }
        }
      }
    }
  }
}
"""

_VIDEOS_QUERY_ALL = """
query($login: String!, $first: Int!, $sort: VideoSort!) {
  user(login: $login) {
    id login displayName
    profileImageURL(width: 300)
    followers { totalCount }
    roles { isPartner isAffiliate }
    videos(first: $first, sort: $sort) {
      pageInfo { hasNextPage }
      edges {
        node {
          id title lengthSeconds viewCount createdAt
          previewThumbnailURL animatedPreviewURL language
          broadcastType
          game { id name slug boxArtURL(width: 144, height: 192) }
        }
      }
    }
  }
}
"""


def _broadcaster_meta(u: dict[str, Any], login: str) -> dict[str, Any]:
    login_val = safe_str(u.get("login")) or login
    roles = u.get("roles") if isinstance(u.get("roles"), dict) else {}
    followers = u.get("followers") if isinstance(u.get("followers"), dict) else {}
    return strip_empty(
        {
            "id": safe_str(u.get("id")),
            "username": login_val,
            "displayName": safe_str(u.get("displayName")) or login_val,
            "url": f"https://www.twitch.tv/{login_val}" if login_val else None,
            "profileImage": safe_str(u.get("profileImageURL")),
            "followers": safe_int(followers.get("totalCount")),
            "isPartner": bool(roles.get("isPartner")) if roles.get("isPartner") is not None else None,
            "isAffiliate": bool(roles.get("isAffiliate")) if roles.get("isAffiliate") is not None else None,
        }
    )


async def user_videos_native(
    login: str,
    *,
    limit: int = 20,
    offset: int = 0,
    filter_by: str | None = None,
    sort_by: str = "TIME",
) -> dict[str, Any] | None:
    """Channel videos with type filter + sort. Returns None on failure.

    Twitch anonymous GQL ``after`` cursors are unreliable, so we fetch up to
    100 newest matching videos in one shot and slice by ``offset`` for paging.
    """
    login_key = (login or "").strip().lstrip("@")
    if not login_key:
        return None
    sort_key = (sort_by or "TIME").strip().upper()
    if sort_key not in _VIDEO_SORTS:
        sort_key = "TIME"
    types: list[str] | None = None
    filter_key: str | None = None
    if filter_by:
        filter_key = filter_by.strip().upper()
        if filter_key in _VIDEO_TYPES:
            types = [filter_key]
        else:
            filter_key = None

    offset = max(0, offset)
    limit = min(max(limit, 1), 100)
    # Fetch one extra when possible so hasMore/nextCursor are accurate.
    fetch_n = min(100, offset + limit + 1)

    if types:
        data = await _gql(
            _VIDEOS_QUERY,
            {"login": login_key, "first": fetch_n, "types": types, "sort": sort_key},
        )
    else:
        data = await _gql(
            _VIDEOS_QUERY_ALL,
            {"login": login_key, "first": fetch_n, "sort": sort_key},
        )
    u = (data or {}).get("user") if isinstance(data, dict) else None
    if not isinstance(u, dict) or not u.get("id"):
        return None

    login_val = safe_str(u.get("login")) or login_key
    profile_image = safe_str(u.get("profileImageURL"))
    channel = _broadcaster_meta(u, login_val)
    edges = ((u.get("videos") or {}).get("edges")) or []
    mapped = [
        _video_node(
            e["node"],
            broadcaster=login_val,
            profile_image=profile_image,
            broadcaster_meta=channel,
        )
        for e in edges
        if isinstance(e, dict) and isinstance(e.get("node"), dict)
    ]
    page = mapped[offset : offset + limit]
    next_offset = offset + len(page)
    has_more = next_offset < len(mapped)
    return {
        "username": login_val,
        "filterBy": filter_key,
        "sortBy": sort_key,
        "broadcaster": channel,
        "videos": page,
        "nextOffset": next_offset if has_more else None,
        "hasMore": has_more,
        "fetched": len(mapped),
    }


_GAME_FIELDS = "game { name boxArtURL(width: 144, height: 192) }"

_PROFILE_QUERY = f"""
query($login: String!, $videoLimit: Int!) {{
  user(login: $login) {{
    id login displayName description createdAt
    profileImageURL(width: 300)
    bannerImageURL
    roles {{ isPartner isAffiliate }}
    followers {{ totalCount }}
    stream {{
      id title viewersCount type createdAt
      previewImageURL(width: 640, height: 360)
      {_GAME_FIELDS}
    }}
    lastBroadcast {{ title startedAt {_GAME_FIELDS} }}
    videos(first: $videoLimit, sort: TIME) {{
      edges {{
        node {{
          id title lengthSeconds viewCount createdAt
          previewThumbnailURL animatedPreviewURL language
          {_GAME_FIELDS}
        }}
      }}
    }}
  }}
}}
"""

# Lighter query used when the full profile query is rejected / rate-limited.
_PROFILE_LITE_QUERY = f"""
query($login: String!) {{
  user(login: $login) {{
    id login displayName description createdAt
    profileImageURL(width: 300)
    bannerImageURL
    roles {{ isPartner isAffiliate }}
    followers {{ totalCount }}
    stream {{
      id title viewersCount type createdAt
      previewImageURL(width: 640, height: 360)
      {_GAME_FIELDS}
    }}
    lastBroadcast {{ title startedAt {_GAME_FIELDS} }}
  }}
}}
"""


def _map_channel(u: dict[str, Any], login: str, recent: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    roles = u.get("roles") or {}
    stream = u.get("stream")
    last = u.get("lastBroadcast") or {}
    login_val = safe_str(u.get("login")) or login
    profile_image = safe_str(u.get("profileImageURL"))
    stream_game, stream_box = _game_fields((stream or {}).get("game") if stream else None)
    last_game, last_box = _game_fields(last.get("game"))
    stream_block = {
        "title": safe_str((stream or {}).get("title")),
        "game": stream_game if stream else None,
        "gameBoxArtUrl": stream_box if stream else None,
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
            "game": last_game,
            "gameBoxArtUrl": last_box,
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
    id slug title createdAt viewCount durationSeconds language
    url embedURL thumbnailURL
    isFeatured isPublished videoOffsetSeconds
    game { id name slug boxArtURL }
    curator { id login displayName profileImageURL(width: 150) }
    broadcaster {
      id login displayName profileImageURL(width: 150)
      roles { isPartner }
      followers { totalCount }
      lastBroadcast { startedAt title }
    }
    videoQualities { quality frameRate sourceURL }
    playbackAccessToken(params: {platform: "web", playerBackend: "mediaplayer", playerType: "site"}) {
      signature value
    }
  }
}
"""


def _box_art(url: str | None, *, width: int = 285, height: int = 380) -> str | None:
    if not url:
        return None
    return url.replace("{width}", str(width)).replace("{height}", str(height))


def _person(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    login = safe_str(raw.get("login") or raw.get("username"))
    name = safe_str(raw.get("displayName") or raw.get("name") or login)
    if not login and not name and raw.get("id") is None:
        return None
    return strip_empty(
        {
            "id": safe_str(raw.get("id")),
            "username": login,
            "name": name,
            "url": f"https://www.twitch.tv/{login}" if login else None,
            "profileImage": safe_str(raw.get("profileImageURL") or raw.get("profileImageUrl")),
        }
    )


def _token_expires(value: Any) -> tuple[int | None, str | None]:
    """Parse playbackAccessToken.value JSON → (unix expires, ISO expiresAt)."""
    text = safe_str(value)
    if not text:
        return None, None
    payload: Any = None
    for candidate in (text, unquote(text)):
        try:
            payload = json.loads(candidate)
            break
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
    if not isinstance(payload, dict):
        return None, None
    expires = safe_int(payload.get("expires"))
    if expires is None:
        return None, None
    try:
        iso = datetime.fromtimestamp(expires, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, OSError, ValueError):
        iso = None
    return expires, iso


def _map_clip(c: dict[str, Any]) -> dict[str, Any]:
    game = c.get("game") if isinstance(c.get("game"), dict) else {}
    b = c.get("broadcaster") if isinstance(c.get("broadcaster"), dict) else {}
    curator = _person(c.get("curator"))
    channel = _person(b) or {}
    followers = None
    if isinstance(b.get("followers"), dict):
        followers = safe_int(b["followers"].get("totalCount"))
    roles = b.get("roles") if isinstance(b.get("roles"), dict) else {}
    is_partner = roles.get("isPartner") if isinstance(roles.get("isPartner"), bool) else None
    last_raw = b.get("lastBroadcast") if isinstance(b.get("lastBroadcast"), dict) else None
    last_broadcast = None
    if last_raw:
        last_broadcast = strip_empty(
            {
                "startedAt": safe_str(last_raw.get("startedAt")),
                "title": safe_str(last_raw.get("title")),
            }
        ) or None
    if channel:
        channel = strip_empty(
            {
                **channel,
                "followers": followers,
                "isPartner": is_partner,
                "lastBroadcast": last_broadcast,
            }
        )

    qualities_out: list[dict[str, Any]] = []
    for q in c.get("videoQualities") or []:
        if not isinstance(q, dict):
            continue
        row = strip_empty(
            {
                "quality": safe_str(q.get("quality")),
                "frameRate": q.get("frameRate") if isinstance(q.get("frameRate"), (int, float)) else None,
                "url": safe_str(q.get("sourceURL") or q.get("sourceUrl") or q.get("url")),
            }
        )
        if row.get("url"):
            qualities_out.append(row)
    # Prefer highest listed quality for the flat videoUrl (Twitch returns 1080 first).
    mp4 = qualities_out[0]["url"] if qualities_out else None

    token_raw = c.get("playbackAccessToken") if isinstance(c.get("playbackAccessToken"), dict) else {}
    expires, expires_at = _token_expires(token_raw.get("value"))
    token = strip_empty(
        {
            "signature": safe_str(token_raw.get("signature")),
            "value": safe_str(token_raw.get("value")),
            "expires": expires,
            "expiresAt": expires_at,
        }
    ) or None

    login = safe_str(b.get("login") or b.get("displayName")) or safe_str(channel.get("username"))
    slug = safe_str(c.get("slug"))
    return strip_empty(
        {
            "platform": "twitch",
            "id": safe_str(c.get("id")),
            "slug": slug,
            "url": safe_str(c.get("url")) or (f"https://clips.twitch.tv/{slug}" if slug else None),
            "embedUrl": safe_str(c.get("embedURL"))
            or (f"https://clips.twitch.tv/embed?clip={slug}" if slug else None),
            "title": safe_str(c.get("title")),
            "createdAt": safe_str(c.get("createdAt")),
            "durationSeconds": safe_int(c.get("durationSeconds")),
            "views": safe_int(c.get("viewCount")),
            "thumbnail": safe_str(c.get("thumbnailURL")),
            "videoUrl": mp4,
            "videoQualities": qualities_out or None,
            "language": safe_str(c.get("language")),
            "isFeatured": c.get("isFeatured") if isinstance(c.get("isFeatured"), bool) else None,
            "isPublished": c.get("isPublished") if isinstance(c.get("isPublished"), bool) else None,
            "videoOffsetSeconds": safe_int(c.get("videoOffsetSeconds")),
            # String game kept for back-compat; structured fields additive.
            "game": safe_str(game.get("name") if game else c.get("game")),
            "gameId": safe_str(game.get("id")),
            "gameSlug": safe_str(game.get("slug")),
            "gameBoxArtUrl": _box_art(safe_str(game.get("boxArtURL") or game.get("boxArtUrl"))),
            # Flat broadcaster string kept for back-compat (Kick-style channel/curator added).
            "broadcaster": login,
            "broadcasterProfileImage": safe_str(b.get("profileImageURL")) or safe_str(channel.get("profileImage")),
            "channel": channel or None,
            "curator": curator,
            "playbackAccessToken": token,
        }
    )


async def clip_native(slug: str) -> dict[str, Any] | None:
    data = await _gql(_CLIP_QUERY, {"slug": slug})
    if not data:
        return None
    c = data.get("clip")
    if not isinstance(c, dict) or not c.get("id"):
        return None
    return _map_clip(c)


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
