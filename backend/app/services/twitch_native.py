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
from urllib.parse import unquote, urlencode, urlparse

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
    lean: bool = False,
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
        "thumbnail": _thumb_url(node.get("previewThumbnailURL")),
        "thumbnailTemplate": _thumb_template(node.get("previewThumbnailURL")),
        "animatedPreviewUrl": safe_str(node.get("animatedPreviewURL") or node.get("animatedPreviewUrl")),
        "broadcastType": btype,
        "game": game_name,
        "gameId": safe_str(game.get("id")),
        "gameSlug": safe_str(game.get("slug")),
        "gameBoxArtUrl": _box_art(game_box) if game_box and "{width}" in (game_box or "") else game_box,
        "language": _language(node.get("language")),
    }
    # user-videos is a single-channel list — channel identity lives once at the
    # top-level broadcaster{}. Profile recentVideos keep the flat aliases.
    if not lean:
        out["broadcaster"] = broadcaster
        out["broadcasterProfileImage"] = profile_image
        out["channel"] = broadcaster_meta
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
    cursor: str | None = None,
    filter_by: str | None = None,
    sort_by: str = "TIME",
) -> dict[str, Any] | None:
    """Channel videos with type filter + sort. Returns None on failure.

    Twitch anonymous GQL rejects ``videos(after:)`` with IntegrityCheckFailed, so
    we fetch up to 100 matching videos in one shot (the hard ceiling) and page
    with a stable video-id cursor — not a raw offset that shifts when new VODs
    land between pages.
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

    limit = min(max(limit, 1), 100)
    after_id = (cursor or "").strip() or None

    if types:
        data = await _gql(
            _VIDEOS_QUERY,
            {"login": login_key, "first": 100, "types": types, "sort": sort_key},
        )
    else:
        data = await _gql(
            _VIDEOS_QUERY_ALL,
            {"login": login_key, "first": 100, "sort": sort_key},
        )
    u = (data or {}).get("user") if isinstance(data, dict) else None
    if not isinstance(u, dict) or not u.get("id"):
        return None

    login_val = safe_str(u.get("login")) or login_key
    channel = _broadcaster_meta(u, login_val)
    edges = ((u.get("videos") or {}).get("edges")) or []
    mapped = [
        _video_node(e["node"], lean=True)
        for e in edges
        if isinstance(e, dict) and isinstance(e.get("node"), dict)
    ]
    start = 0
    if after_id:
        for i, row in enumerate(mapped):
            if safe_str(row.get("id")) == after_id:
                start = i + 1
                break
        else:
            # Unknown/stale cursor — empty page rather than silently restarting.
            return {
                "username": login_val,
                "filterBy": filter_key,
                "sortBy": sort_key,
                "broadcaster": channel,
                "videos": [],
                "nextCursor": None,
                "hasMore": False,
                "fetched": len(mapped),
                "windowMax": 100,
            }
    page = mapped[start : start + limit]
    has_more = (start + len(page)) < len(mapped)
    next_cursor = safe_str(page[-1].get("id")) if page and has_more else None
    return {
        "username": login_val,
        "filterBy": filter_key,
        "sortBy": sort_key,
        "broadcaster": channel,
        "videos": page,
        "nextCursor": next_cursor,
        "hasMore": has_more,
        "fetched": len(mapped),
        "windowMax": 100,
    }


_GAME_FIELDS = "game { name boxArtURL(width: 144, height: 192) }"

_PROFILE_QUERY = f"""
query($login: String!, $videoLimit: Int!, $clipLimit: Int!) {{
  user(login: $login) {{
    id login displayName description createdAt
    profileImageURL(width: 300)
    bannerImageURL
    roles {{ isPartner isAffiliate }}
    followers {{ totalCount }}
    channel {{
      socialMedias {{ id name title url }}
    }}
    panels {{
      id
      ... on DefaultPanel {{ title linkURL imageURL description }}
    }}
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
    clips(first: $clipLimit) {{
      edges {{
        node {{
          id slug title viewCount createdAt
          thumbnailURL url embedURL
          game {{ name boxArtURL(width: 144, height: 192) }}
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
    channel {{
      socialMedias {{ id name title url }}
    }}
    panels {{
      id
      ... on DefaultPanel {{ title linkURL imageURL description }}
    }}
    stream {{
      id title viewersCount type createdAt
      previewImageURL(width: 640, height: 360)
      {_GAME_FIELDS}
    }}
    lastBroadcast {{ title startedAt {_GAME_FIELDS} }}
  }}
}}
"""

_SOCIAL_HOSTS: list[tuple[str, tuple[str, ...]]] = [
    ("instagram", ("instagram.com",)),
    ("twitter", ("twitter.com", "x.com", "mobile.twitter.com")),
    ("tiktok", ("tiktok.com",)),
    ("youtube", ("youtube.com", "youtu.be", "m.youtube.com")),
    ("discord", ("discord.gg", "discord.com")),
    ("facebook", ("facebook.com", "fb.com")),
    ("reddit", ("reddit.com",)),
    ("kick", ("kick.com",)),
]


def _platform_from_url(url: str) -> str | None:
    try:
        host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    except Exception:
        return None
    if not host:
        return None
    for platform, hosts in _SOCIAL_HOSTS:
        if host == hosts[0] or host.endswith("." + hosts[0]) or host in hosts:
            return platform
    return None


def _socials_from_user(u: dict[str, Any]) -> list[dict[str, Any]]:
    """Linked accounts from channel.socialMedias + DefaultPanel linkURLs."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add(platform: str | None, url: str | None, title: str | None = None) -> None:
        if not url:
            return
        key = url.rstrip("/").lower()
        if key in seen:
            return
        seen.add(key)
        plat = platform or _platform_from_url(url) or "link"
        out.append(strip_empty({"platform": plat, "url": url, "title": title}))

    channel = u.get("channel") if isinstance(u.get("channel"), dict) else {}
    for row in channel.get("socialMedias") or []:
        if not isinstance(row, dict):
            continue
        _add(safe_str(row.get("name")), safe_str(row.get("url")), safe_str(row.get("title")))

    for panel in u.get("panels") or []:
        if not isinstance(panel, dict):
            continue
        _add(None, safe_str(panel.get("linkURL")), safe_str(panel.get("title")))

    return out


def _clip_node(node: dict[str, Any], *, broadcaster: str | None = None) -> dict[str, Any]:
    game_name, game_box = _game_fields(node.get("game"))
    slug = safe_str(node.get("slug"))
    thumb = safe_str(node.get("thumbnailURL") or node.get("thumbnailUrl"))
    embed = safe_str(node.get("embedURL") or node.get("embedUrl"))
    if not embed and slug:
        embed = f"https://clips.twitch.tv/embed?clip={slug}&parent=captapi.com"
    return strip_empty(
        {
            "platform": "twitch",
            "id": safe_str(node.get("id")),
            "slug": slug,
            "url": safe_str(node.get("url"))
            or (f"https://www.twitch.tv/{broadcaster}/clip/{slug}" if broadcaster and slug else None),
            "embedUrl": embed,
            "title": safe_str(node.get("title")),
            "views": safe_int(node.get("viewCount")),
            "createdAt": safe_str(node.get("createdAt")),
            "thumbnail": _thumb_url(thumb) if thumb and "{width}" in thumb else thumb,
            "thumbnailTemplate": _thumb_template(thumb),
            "game": game_name,
            "gameBoxArtUrl": _box_art(game_box) if game_box and "{width}" in (game_box or "") else game_box,
            "broadcaster": broadcaster,
        }
    )


def _map_channel(
    u: dict[str, Any],
    login: str,
    *,
    recent: list[dict[str, Any]] | None = None,
    top_clips: list[dict[str, Any]] | None = None,
    schedule: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from app.utils.profile_core import stamp_profile_core as _stamp

    roles = u.get("roles") or {}
    stream = u.get("stream")
    last = u.get("lastBroadcast") or {}
    login_val = safe_str(u.get("login")) or login
    profile_image = safe_str(u.get("profileImageURL"))
    banner = safe_str(u.get("bannerImageURL"))
    stream_game, stream_box = _game_fields((stream or {}).get("game") if stream else None)
    last_game, last_box = _game_fields(last.get("game"))
    is_live = bool(stream)
    stream_block = (
        {
            "title": safe_str(stream.get("title")),
            "game": stream_game,
            "gameBoxArtUrl": stream_box,
            "viewers": safe_int(stream.get("viewersCount")),
            "startedAt": safe_str(stream.get("createdAt")),
            "thumbnail": safe_str(stream.get("previewImageURL")),
        }
        if is_live and isinstance(stream, dict)
        else None
    )
    out = {
        "platform": "twitch",
        "id": safe_str(u.get("id")),
        "handle": login_val,
        "login": login_val,
        "username": login_val,
        "displayName": safe_str(u.get("displayName")),
        "url": f"https://www.twitch.tv/{login_val}",
        "bio": safe_str(u.get("description")),
        "description": safe_str(u.get("description")),
        "followers": safe_int((u.get("followers") or {}).get("totalCount")),
        "avatar": profile_image,
        "profileImage": profile_image,  # deprecated alias — prefer avatar
        "banner": banner,
        "bannerImage": banner,  # deprecated alias — prefer banner
        "isPartner": bool(roles.get("isPartner")),
        "isAffiliate": bool(roles.get("isAffiliate")),
        "isLive": is_live,
        "stream": stream_block,
        "lastBroadcast": {
            "title": safe_str(last.get("title")),
            "game": last_game,
            "gameBoxArtUrl": last_box,
            "startedAt": safe_str(last.get("startedAt")),
        },
        "recentVideos": recent if recent is not None else [],
        "topClips": top_clips if top_clips is not None else [],
        # Lean preview — full schedule lives on /v1/twitch/user-schedule.
        "schedule": schedule if schedule is not None else [],
        "socials": _socials_from_user(u),
        "createdAt": safe_str(u.get("createdAt")),
    }
    return _stamp(out, platform="twitch")


async def channel_native(login: str, video_limit: int = 30) -> dict[str, Any] | None:
    login_key = (login or "").strip().lstrip("@")
    if not login_key:
        return None
    vlim = min(max(video_limit, 1), 100)
    clip_limit = 10

    data = await _gql(
        _PROFILE_QUERY,
        {"login": login_key, "videoLimit": vlim, "clipLimit": clip_limit},
    )
    u = (data or {}).get("user") if isinstance(data, dict) else None
    lite = False
    if not isinstance(u, dict) or not u.get("id"):
        # Full query occasionally trips complexity limits — retry lite shape.
        data = await _gql(_PROFILE_LITE_QUERY, {"login": login_key})
        u = (data or {}).get("user") if isinstance(data, dict) else None
        if not isinstance(u, dict) or not u.get("id"):
            return None
        lite = True

    login_val = safe_str(u.get("login")) or login_key
    profile_image = safe_str(u.get("profileImageURL"))
    recent: list[dict[str, Any]] = []
    top_clips: list[dict[str, Any]] = []
    if not lite:
        edges = ((u.get("videos") or {}).get("edges")) or []
        recent = [
            _video_node(e["node"], broadcaster=login_val, profile_image=profile_image)
            for e in edges
            if isinstance(e, dict) and isinstance(e.get("node"), dict)
        ]
        clip_edges = ((u.get("clips") or {}).get("edges")) or []
        top_clips = [
            _clip_node(e["node"], broadcaster=login_val)
            for e in clip_edges
            if isinstance(e, dict) and isinstance(e.get("node"), dict)
        ]
    if not top_clips:
        # Lite path (or empty clips on full query) — dedicated clips fetch.
        clips_data = await _gql(
            """
query($login: String!, $clipLimit: Int!) {
  user(login: $login) {
    clips(first: $clipLimit) {
      edges {
        node {
          id slug title viewCount createdAt
          thumbnailURL url embedURL
          game { name boxArtURL(width: 144, height: 192) }
        }
      }
    }
  }
}
""",
            {"login": login_key, "clipLimit": clip_limit},
        )
        cu = (clips_data or {}).get("user") if isinstance(clips_data, dict) else None
        if isinstance(cu, dict):
            clip_edges = ((cu.get("clips") or {}).get("edges")) or []
            top_clips = [
                _clip_node(e["node"], broadcaster=login_val)
                for e in clip_edges
                if isinstance(e, dict) and isinstance(e.get("node"), dict)
            ]

    # Lean preview only — canonical full schedule: GET /v1/twitch/user-schedule.
    schedule = await schedule_native(login_key, limit=10)
    if schedule is None:
        schedule = []

    return _map_channel(
        u,
        login_key,
        recent=recent,
        top_clips=top_clips,
        schedule=schedule,
    )


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


def _thumb_template(url: Any) -> str | None:
    """Keep the unsubstituted Twitch template when present (callers pick size)."""
    text = safe_str(url)
    if text and "{width}" in text and "{height}" in text:
        return text
    return None


def _thumb_url(url: Any, *, width: int = 320, height: int = 180) -> str | None:
    """VOD thumbnails ship as ``…/{width}x{height}.jpg`` — substitute a default size."""
    text = safe_str(url)
    if not text:
        return None
    if "{width}" in text or "{height}" in text:
        return text.replace("{width}", str(width)).replace("{height}", str(height))
    return text


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


def _language(value: Any) -> str | None:
    """BCP-47 style lowercase — Twitch clips often return EN/ES; VODs return es."""
    text = safe_str(value)
    return text.lower() if text else None


def _frame_rate(value: Any) -> float | int | None:
    """Round Twitch's raw float frame rates to 2dp (field doc example: 60)."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return round(value, 2)
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


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


def _parse_playback_token(token_raw: dict[str, Any] | None) -> dict[str, Any] | None:
    """Unwrap playbackAccessToken.value JSON string into typed fields.

    Drops the escaped-JSON ``value`` string (same unwrap we do for TikTok
    live-info). ``clipUri`` is Twitch's reference URI inside the token — often
    a mid/low rendition; it is not the quality we pick for videoUrl.
    """
    if not isinstance(token_raw, dict):
        return None
    signature = safe_str(token_raw.get("signature"))
    raw_value = safe_str(token_raw.get("value"))
    expires, expires_at = _token_expires(raw_value)
    payload: dict[str, Any] = {}
    if raw_value:
        for candidate in (raw_value, unquote(raw_value)):
            try:
                parsed = json.loads(candidate)
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if isinstance(parsed, dict):
                payload = parsed
                break
    out = strip_empty(
        {
            "signature": signature,
            "expires": expires,
            "expiresAt": expires_at,
            "clipUri": safe_str(payload.get("clip_uri") or payload.get("clipUri")),
            "clipSlug": safe_str(payload.get("clip_slug") or payload.get("clipSlug")),
            "deviceId": safe_str(payload.get("device_id") or payload.get("deviceId")),
            "version": safe_int(payload.get("version")),
            "authorization": payload.get("authorization")
            if isinstance(payload.get("authorization"), dict)
            else None,
        }
    )
    # Internal only — used to build signedVideoUrl; never returned to clients.
    if out and raw_value:
        out["_rawValue"] = raw_value
    return out or None


def _sign_clip_url(
    source_url: str | None, signature: str | None, token_value: str | None
) -> str | None:
    """Append Twitch clip playback ``?sig=&token=`` (required for /nauth/ URLs)."""
    if not source_url or not signature or not token_value:
        return None
    return f"{source_url}?{urlencode({'sig': signature, 'token': token_value})}"


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

    token_raw = c.get("playbackAccessToken") if isinstance(c.get("playbackAccessToken"), dict) else {}
    token = _parse_playback_token(token_raw)
    raw_token_value = (token or {}).pop("_rawValue", None) if token else None
    signature = safe_str((token or {}).get("signature"))

    qualities_out: list[dict[str, Any]] = []
    for q in c.get("videoQualities") or []:
        if not isinstance(q, dict):
            continue
        source = safe_str(q.get("sourceURL") or q.get("sourceUrl") or q.get("url"))
        row = strip_empty(
            {
                "quality": safe_str(q.get("quality")),
                "frameRate": _frame_rate(q.get("frameRate")),
                "url": source,
                "signedUrl": _sign_clip_url(source, signature, raw_token_value),
            }
        )
        if row.get("url"):
            qualities_out.append(row)
    # Prefer highest listed quality for the flat videoUrl (Twitch returns 1080 first).
    mp4 = qualities_out[0]["url"] if qualities_out else None
    # /nauth/ clip MP4s require ?sig=&token= — unsigned HEAD is 401. The same
    # token signs every listed quality (token.clipUri may be 360 while videoUrl
    # is 1080; both return 200 when signed).
    signed_mp4 = qualities_out[0].get("signedUrl") if qualities_out else None

    login = safe_str(b.get("login") or b.get("displayName")) or safe_str(channel.get("username"))
    slug = safe_str(c.get("slug"))
    related = c.get("_relatedClips") if isinstance(c.get("_relatedClips"), list) else None
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
            "signedVideoUrl": signed_mp4,
            "videoQualities": qualities_out or None,
            "language": _language(c.get("language")),
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
            "relatedClips": related,
        }
    )


_RELATED_CLIPS_QUERY = """
query($login: String!, $limit: Int!) {
  user(login: $login) {
    clips(first: $limit) {
      edges {
        node {
          id slug title createdAt viewCount durationSeconds language
          url thumbnailURL
        }
      }
    }
  }
}
"""


async def clip_native(slug: str) -> dict[str, Any] | None:
    data = await _gql(_CLIP_QUERY, {"slug": slug})
    if not data:
        return None
    c = data.get("clip")
    if not isinstance(c, dict) or not c.get("id"):
        return None
    # Additional clips from the same broadcaster (SC ships these).
    b = c.get("broadcaster") if isinstance(c.get("broadcaster"), dict) else {}
    login = safe_str(b.get("login"))
    if login:
        rel = await _gql(_RELATED_CLIPS_QUERY, {"login": login, "limit": 8})
        u = (rel or {}).get("user") if isinstance(rel, dict) else None
        edges = (((u or {}).get("clips") or {}).get("edges")) or []
        related: list[dict[str, Any]] = []
        for e in edges:
            if not isinstance(e, dict):
                continue
            node = e.get("node") if isinstance(e.get("node"), dict) else None
            if not node:
                continue
            rslug = safe_str(node.get("slug"))
            if not rslug or rslug == slug:
                continue
            related.append(
                strip_empty(
                    {
                        "id": safe_str(node.get("id")),
                        "slug": rslug,
                        "url": safe_str(node.get("url")) or f"https://clips.twitch.tv/{rslug}",
                        "title": safe_str(node.get("title")),
                        "createdAt": safe_str(node.get("createdAt")),
                        "views": safe_int(node.get("viewCount")),
                        "durationSeconds": safe_int(node.get("durationSeconds")),
                        "language": _language(node.get("language")),
                        "thumbnail": safe_str(node.get("thumbnailURL")),
                    }
                )
            )
        if related:
            c = {**c, "_relatedClips": related[:6]}
    return _map_clip(c)


_SCHEDULE_QUERY = """
query($login: String!) {
  user(login: $login) {
    channel {
      schedule {
        id
        segments {
          id
          title
          startAt
          endAt
          isCancelled
          cancelledUntil
          firstOccurrenceDate
          repeatEndsAfterCount
          categories { id name }
        }
      }
    }
  }
}
"""


def _map_schedule_segment(seg: dict[str, Any]) -> dict[str, Any]:
    cats = seg.get("categories") or []
    cat0 = cats[0] if cats and isinstance(cats[0], dict) else {}
    started = safe_str(seg.get("startAt") or seg.get("startedAt"))
    ended = safe_str(seg.get("endAt") or seg.get("endedAt"))
    # GQL uses British cancelledUntil; Helix uses canceled_until — emit US spelling.
    canceled_until = safe_str(seg.get("cancelledUntil") or seg.get("canceledUntil"))
    is_cancelled = seg.get("isCancelled") if isinstance(seg.get("isCancelled"), bool) else None
    repeat = safe_int(seg.get("repeatEndsAfterCount"))
    # repeatEndsAfterCount == 1 → one-off; 0 / >1 → recurring series (Helix isRecurring).
    is_recurring: bool | None
    if repeat is None and seg.get("firstOccurrenceDate") is None:
        is_recurring = None
    elif repeat == 1:
        is_recurring = False
    else:
        is_recurring = True
    return strip_empty(
        {
            "id": safe_str(seg.get("id")),
            "title": safe_str(seg.get("title")),
            # Canonical timestamps match stream/lastBroadcast (startedAt).
            "startedAt": started,
            "endedAt": ended,
            # Deprecated aliases — Twitch GQL field names; prefer startedAt/endedAt.
            "startAt": started,
            "endAt": ended,
            "game": safe_str(cat0.get("name")),
            "gameId": safe_str(cat0.get("id")),
            "isRecurring": is_recurring,
            "isCancelled": is_cancelled,
            "canceledUntil": canceled_until,
            "firstOccurrenceAt": safe_str(seg.get("firstOccurrenceDate")),
        }
    )


async def schedule_native(
    login: str, *, limit: int | None = None
) -> list[dict[str, Any]] | None:
    """Upcoming schedule segments. Returns None on error, [] when the channel
    simply has no schedule set (a valid empty result).

    Anonymous GQL Schedule has no timezone/vacation fields — those stay on Helix.
    """
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
        out.append(_map_schedule_segment(seg))
    if limit is not None:
        out = out[: max(0, min(int(limit), 100))]
    return out
