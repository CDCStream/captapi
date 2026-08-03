"""Native Instagram reel media resolver.

Uses Instagram's public PolarisPostRootQuery GraphQL endpoint (the one the
logged-out web player calls), which returns v1-format media incl.
``video_versions`` in <1s without authentication. Only a fresh ``csrftoken``
cookie + ``X-CSRFToken`` header pair is required.

Instagram deprecated the old ``xdt_shortcode_media`` doc_id in June 2026
(which is also why Decodo's ``instagram_graphql_post`` target is disabled);
this doc_id is its replacement.
"""

from __future__ import annotations

import asyncio
import base64
import itertools
import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog

from app.services.http_fetch import proxy_for
from app.services.instagram_decodo import dedupe_preserve, hidden_count, pick_video_views
from app.utils.formatters import safe_float, safe_int, safe_str

log = structlog.get_logger(__name__)

_POST_DOC_ID = "27128499623469141"  # PolarisPostRootQuery
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# One rate-limited tier shouldn't kill the fast path; each tier gets its own
# session (fresh IP + csrf token).
_TIERS: tuple[str, ...] = ("datacenter", "residential")


async def fetch_reel_media(shortcode: str) -> dict[str, Any] | None:
    """Resolve a reel/post's media info natively. ~1-2s total.

    Returns {"videoUrl", "thumbnailUrl", "duration", "caption", "username"}
    or None (caller falls back to Apify).
    """
    media = await _fetch_item(shortcode)
    if media is None:
        media = await _fetch_item_with_session(shortcode)
    if media is None:
        return None
    # Reels can be carousels; the playable video lives on the cover child.
    cover = (media.get("carousel_media") or [media])[0]
    videos = media.get("video_versions") or cover.get("video_versions") or []
    images = (media.get("image_versions2") or {}).get("candidates") or []
    caption = media.get("caption")
    return {
        "videoUrl": safe_str(videos[0].get("url")) if videos else None,
        "thumbnailUrl": safe_str(images[0].get("url")) if images else None,
        "duration": _video_duration(media, cover),
        "caption": safe_str(caption.get("text")) if isinstance(caption, dict) else None,
        "username": safe_str((media.get("user") or {}).get("username")),
    }


_MEDIA_TYPE_NAMES = {1: "Image", 2: "Video", 8: "Sidecar"}
# Instagram hashtags must contain at least one non-numeric character, so
# "#1" in a caption ("ranked #1") is not a real hashtag - require one letter
# or underscore to avoid capturing purely numeric tokens.
_HASHTAG_RE = re.compile(r"#(\w*[^\W\d]\w*)", re.UNICODE)
# Same as instagram_decodo._MENTION_RE: usernames may contain dots but never
# end with one, so "@herbalife." in a caption must capture "herbalife".
_MENTION_RE = re.compile(r"@([A-Za-z0-9_](?:[A-Za-z0-9_.]*[A-Za-z0-9_])?)")
# DASH manifest carries the duration when `video_duration` is absent,
# e.g. mediaPresentationDuration="PT0H0M30.033S".
_MPD_DURATION_RE = re.compile(
    r'mediaPresentationDuration="PT(?:(\d+)H)?(?:(\d+)M)?([\d.]+)S"'
)


def _duration_from_video_url(url: str) -> float | None:
    """Instagram CDN video URLs embed the duration in the base64 ``efg`` query
    param (JSON with a ``duration_s`` field). Coarse (integer seconds) but a
    useful fallback when the media object omits video_duration/dash manifest."""
    if not url:
        return None
    try:
        efg = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("efg", [None])[0]
        if not efg:
            return None
        padded = efg + "=" * (-len(efg) % 4)
        blob = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8", "ignore"))
        dur = safe_float(blob.get("duration_s"))
        return round(dur, 3) if dur else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def _video_duration(media: dict[str, Any], cover: dict[str, Any]) -> float | None:
    direct = safe_float(media.get("video_duration") or cover.get("video_duration"))
    if direct:
        return round(direct, 3)
    m = _MPD_DURATION_RE.search(
        safe_str(media.get("video_dash_manifest") or cover.get("video_dash_manifest")) or ""
    )
    if m:
        hours, minutes, seconds = int(m.group(1) or 0), int(m.group(2) or 0), float(m.group(3))
        return round(hours * 3600 + minutes * 60 + seconds, 3)
    videos = media.get("video_versions") or cover.get("video_versions") or []
    return _duration_from_video_url(safe_str(videos[0].get("url")) if videos else "")


def _location_from_media(media: dict[str, Any]) -> dict[str, Any] | None:
    loc = media.get("location")
    if not isinstance(loc, dict):
        return None
    name = safe_str(loc.get("name"))
    lid = safe_str(loc.get("pk") or loc.get("id"))
    if not name and not lid:
        return None
    out: dict[str, Any] = {"id": lid, "name": name}
    lat = safe_float(loc.get("lat") or loc.get("latitude"))
    lng = safe_float(loc.get("lng") or loc.get("longitude"))
    if lat is not None:
        out["latitude"] = lat
    if lng is not None:
        out["longitude"] = lng
    return out


def _music_from_media(media: dict[str, Any]) -> dict[str, Any] | None:
    """Audio attribution from clips_metadata (licensed track or original sound)."""
    clips = media.get("clips_metadata") if isinstance(media.get("clips_metadata"), dict) else {}
    music_info = clips.get("music_info") if isinstance(clips.get("music_info"), dict) else {}
    original = (
        clips.get("original_sound_info")
        if isinstance(clips.get("original_sound_info"), dict)
        else {}
    )
    asset = (
        music_info.get("music_asset_info")
        if isinstance(music_info.get("music_asset_info"), dict)
        else {}
    )
    audio_id = safe_str(
        asset.get("audio_cluster_id")
        or asset.get("audio_asset_id")
        or music_info.get("audio_asset_id")
        or original.get("audio_asset_id")
        or original.get("audio_id")
    )
    title = safe_str(
        asset.get("title")
        or music_info.get("song_name")
        or original.get("original_audio_title")
    )
    artist = None
    for block in (music_info, original, asset):
        ig_artist = block.get("ig_artist") if isinstance(block, dict) else None
        if isinstance(ig_artist, dict):
            artist = safe_str(ig_artist.get("username") or ig_artist.get("full_name"))
            if artist:
                break
    if not artist:
        artist = safe_str(asset.get("display_artist"))
    if not audio_id and not title:
        return None
    return {"id": audio_id, "title": title, "artist": artist}


def map_post_from_media(media: dict[str, Any], *, shortcode: str | None = None) -> dict[str, Any]:
    """Map a Polaris / api/v1 media dict to the public post shape.

    Additive fields (isPaidPartnership, music, location, previewComments, …)
    are included when Instagram exposes them. Play counts are often absent on
    the logged-out media endpoint — callers may backfill ``engagement.views``
    from the owner's feed (see ``enrich_posts_from_author_feeds``).
    """
    from app.services.instagram_decodo import strip_null_post_fields

    code = safe_str(media.get("code")) or shortcode or ""
    caption_obj = media.get("caption")
    caption = safe_str(caption_obj.get("text")) if isinstance(caption_obj, dict) else None
    user = media.get("user") if isinstance(media.get("user"), dict) else {}
    username = safe_str(user.get("username"))
    owner_id = safe_str(user.get("pk") or user.get("pk_id") or user.get("id"))
    media_pk = safe_str(media.get("pk") or media.get("pk_id") or media.get("id"))
    if media_pk and "_" in media_pk:
        media_pk = media_pk.split("_", 1)[0]
    if media_pk and not media_pk.isdigit():
        media_pk = None

    cover = (media.get("carousel_media") or [media])[0]
    videos = cover.get("video_versions") or []
    images = (cover.get("image_versions2") or {}).get("candidates") or []

    taken_at = safe_int(media.get("taken_at"))
    published = (
        datetime.fromtimestamp(taken_at, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if taken_at
        else None
    )

    media_type = safe_int(media.get("media_type")) or 0
    is_video = media_type == 2
    product = safe_str(media.get("product_type")) or ("clips" if is_video else None)
    plays = safe_int(media.get("play_count"))
    ig_plays = safe_int(media.get("ig_play_count") or media.get("view_count"))
    likes = hidden_count(media.get("like_count"))
    views, plays_field = pick_video_views(
        view_count=ig_plays,
        play_count=plays,
        likes=likes,
        is_video=is_video,
    )

    music = _music_from_media(media)
    location = _location_from_media(media)
    post_url = (
        f"https://www.instagram.com/{'reel' if is_video or product in {'clips', 'reel', 'reels'} else 'p'}/{code}/"
        if code
        else None
    )
    preview_raw = media.get("preview_comments") or []
    preview_comments = []
    if isinstance(preview_raw, list) and post_url:
        for raw in preview_raw[:5]:
            if isinstance(raw, dict):
                mapped = _map_preview_comment(raw, post_url=post_url)
                if mapped:
                    preview_comments.append(mapped)

    affiliate = media.get("affiliate_info")
    is_affiliate = bool(affiliate) if affiliate not in (None, [], {}, False) else False
    is_ad = bool(media.get("is_ad") or media.get("ad_id") or media.get("injected"))
    is_paid = media.get("is_paid_partnership")
    if is_paid is None and media.get("sponsor_tags"):
        is_paid = True

    author: dict[str, Any] = {
        "id": owner_id,
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "url": f"https://instagram.com/{username}" if username else None,
        "verified": user.get("is_verified"),
        "profileImage": safe_str(user.get("profile_pic_url")),
        "followers": safe_int(user.get("follower_count")),
        "postCount": safe_int(user.get("media_count")),
        "private": user.get("is_private"),
    }

    post: dict[str, Any] = {
        "platform": "instagram",
        "url": post_url or (f"https://www.instagram.com/p/{code}/" if code else None),
        # Public id prefers numeric media pk when present; shortcode stays for URLs.
        "id": media_pk or code or shortcode,
        "shortcode": code or shortcode or None,
        "mediaId": media_pk,
        "postType": _MEDIA_TYPE_NAMES.get(media_type),
        "productType": product,
        "caption": caption,
        "description": caption,
        "publishedAt": published,
        "durationSeconds": _video_duration(media, cover),
        "thumbnailUrl": safe_str(images[0].get("url")) if images else None,
        "videoUrl": safe_str(videos[0].get("url")) if videos else None,
        "author": author,
        "engagement": {
            "views": views,
            "plays": plays_field,
            "likes": likes,
            "comments": hidden_count(media.get("comment_count")),
        },
        "hashtags": dedupe_preserve(_HASHTAG_RE.findall(caption or "")),
        "mentions": dedupe_preserve(_MENTION_RE.findall(caption or "")),
        "isPaidPartnership": bool(is_paid) if is_paid is not None else False,
        "isAd": is_ad,
        "isAffiliate": is_affiliate,
        "accessibilityCaption": safe_str(media.get("accessibility_caption")),
        "location": location,
        "music": music,
        "musicId": (music or {}).get("id") if music else None,
        "previewComments": preview_comments or None,
    }
    return strip_null_post_fields(post)


async def fetch_post_details(shortcode: str) -> dict[str, Any] | None:
    """Full post/reel/carousel details in the /v1/instagram/details shape.

    Same upstream numbers as the Apify actor (both read Instagram's own
    data) at ~3-4s instead of an actor run. Returns None so the caller can
    fall back to Apify.
    """
    media = await _fetch_item(shortcode)
    if media is None:
        # Railway/datacenter often 401s Polaris; session GraphQL recovers.
        media = await _fetch_item_with_session(shortcode)
    if media is None:
        return None
    return map_post_from_media(media, shortcode=shortcode)


def _map_preview_comment(raw: dict[str, Any], *, post_url: str) -> dict[str, Any] | None:
    """Map Polaris ``preview_comments`` / XDTCommentDict → comments API row."""
    cid = safe_str(raw.get("pk") or raw.get("id"))
    text = (raw.get("text") or "").strip()
    if not cid and not text:
        return None
    user = raw.get("user") if isinstance(raw.get("user"), dict) else {}
    author = safe_str(user.get("username"))
    created = safe_int(raw.get("created_at") or raw.get("created_at_utc"))
    published = (
        datetime.fromtimestamp(created, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if created
        else None
    )
    liked = raw.get("edge_liked_by") if isinstance(raw.get("edge_liked_by"), dict) else {}
    children = (
        raw.get("preview_child_comments")
        or raw.get("child_comments")
        or raw.get("replies")
        or []
    )
    child_n = len(children) if isinstance(children, list) else 0
    like_count = safe_int(
        raw.get("comment_like_count")
        or raw.get("like_count")
        or raw.get("likesCount")
        or liked.get("count")
    )
    reply_count = safe_int(
        raw.get("child_comment_count")
        or raw.get("reply_count")
        or raw.get("repliesCount")
        or (child_n if child_n else None)
    )
    return {
        "id": cid,
        "url": f"{post_url.rstrip('/')}/c/{cid}/" if cid and post_url else None,
        "text": text,
        "author": author,
        "authorAvatarUrl": safe_str(user.get("profile_pic_url")),
        "authorIsVerified": bool(user.get("is_verified")) if user.get("is_verified") is not None else False,
        "likeCount": like_count,
        "publishedAt": published,
        "replyCount": reply_count,
    }


async def comments_native(url: str, *, limit: int = 50) -> dict[str, Any] | None:
    """Logged-out comments from Polaris media ``preview_comments``.

    Instagram only embeds ~2 preview comments on the public media payload.
    Full pagination (``PolarisPostCommentsPaginationQuery`` / ``api/v1/.../comments``)
    requires a real browser session or is soft-blocked (429 / login HTML).
    Returns a partial list plus ``totalComments`` / ``hasMore`` so callers can
    fall through to Apify when more rows are needed.
    """
    from app.utils.url import extract_instagram_shortcode

    shortcode = extract_instagram_shortcode(url)
    if not shortcode:
        return None
    media = await _fetch_item(shortcode)
    if media is None:
        return None
    previews = media.get("preview_comments") or []
    if not isinstance(previews, list) or not previews:
        # Confirmed empty thread vs. gated — if comment_count is 0, succeed empty.
        total = safe_int(media.get("comment_count")) or 0
        if total == 0:
            return {
                "platform": "instagram",
                "url": url,
                "totalReturned": 0,
                "totalComments": 0,
                "hasMore": False,
                "comments": [],
            }
        return None
    post_url = f"https://www.instagram.com/p/{shortcode}/"
    comments: list[dict[str, Any]] = []
    for raw in previews:
        if not isinstance(raw, dict):
            continue
        mapped = _map_preview_comment(raw, post_url=post_url)
        if mapped and mapped.get("text"):
            comments.append(mapped)
        if len(comments) >= limit:
            break
    if not comments:
        return None
    total = safe_int(media.get("comment_count")) or len(comments)
    return {
        "platform": "instagram",
        "url": url,
        "totalReturned": len(comments),
        "totalComments": total,
        "hasMore": total > len(comments),
        "comments": comments,
    }


def _normalize_ig_session_id(raw: str) -> str:
    """Decode URL-encoded session cookies (``%3A`` → ``:``) from env pastes."""
    value = (raw or "").strip()
    if not value:
        return ""
    if "%" in value:
        value = urllib.parse.unquote(value)
    return value.strip()


_SESSION_RR = itertools.count()


def _ig_session_pool() -> list[str]:
    """Unique normalized sessionids from ``IG_SESSION_IDS`` + ``IG_SESSION_ID``."""
    from app.core.config import get_settings

    settings = get_settings()
    parts: list[str] = []
    multi = (settings.IG_SESSION_IDS or "").strip()
    if multi:
        parts.extend(re.split(r"[\s,;]+", multi))
    single = (settings.IG_SESSION_ID or "").strip()
    if single:
        parts.append(single)
    out: list[str] = []
    seen: set[str] = set()
    for part in parts:
        sid = _normalize_ig_session_id(part)
        if not sid or sid in seen:
            continue
        seen.add(sid)
        out.append(sid)
    return out


def _cookies_for_session(session_id: str) -> dict[str, str]:
    cookies: dict[str, str] = {"sessionid": session_id}
    ds = session_id.split(":", 1)[0]
    if ds.isdigit():
        cookies["ds_user_id"] = ds
    return cookies


def _sessions_rotated(preferred: str | None = None) -> list[str]:
    """Round-robin start order; optional preferred session first."""
    pool = _ig_session_pool()
    if not pool:
        return []
    if preferred and preferred in pool:
        i = pool.index(preferred)
        return pool[i:] + pool[:i]
    i = next(_SESSION_RR) % len(pool)
    return pool[i:] + pool[:i]


def _pick_session() -> str | None:
    rotated = _sessions_rotated()
    return rotated[0] if rotated else None


async def _fetch_item_with_session(
    shortcode: str, session_id: str | None = None
) -> dict[str, Any] | None:
    """Polaris shortcode media via GraphQL using session cookies (pool failover).

    Logged-out GraphQL often 401s on datacenter IPs (e.g. Railway); the same
    doc_id succeeds when a valid session cookie is attached.
    """
    for sid in _sessions_rotated(session_id):
        item = await _fetch_item_with_one_session(shortcode, sid)
        if item is not None:
            return item
    return None


async def _fetch_item_with_one_session(
    shortcode: str, session_id: str
) -> dict[str, Any] | None:
    cookies = _cookies_for_session(session_id)
    tiers: list[str | None] = [None, "datacenter", "residential"]
    for tier in tiers:
        try:
            async with httpx.AsyncClient(
                timeout=15,
                proxy=proxy_for(tier) if tier else None,
                follow_redirects=True,
                cookies=cookies,
            ) as client:
                await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
                csrf = client.cookies.get("csrftoken")
                if not csrf:
                    continue
                resp = await client.post(
                    "https://www.instagram.com/graphql/query",
                    data={
                        "doc_id": _POST_DOC_ID,
                        "variables": json.dumps(
                            {
                                "shortcode": shortcode,
                                "__relay_internal__pv__PolarisAIGMMediaWebLabelEnabledrelayprovider": False,
                            },
                            separators=(",", ":"),
                        ),
                    },
                    headers={
                        "User-Agent": _UA,
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-IG-App-ID": _IG_APP_ID,
                        "X-CSRFToken": csrf,
                        "Accept": "application/json",
                        "Referer": f"https://www.instagram.com/p/{shortcode}/",
                    },
                )
        except httpx.HTTPError as exc:
            log.info(
                "ig_session_media_transport",
                tier=tier or "direct",
                ds_user=session_id.split(":", 1)[0][:12],
                error=str(exc)[:120],
            )
            continue
        if resp.status_code in (401, 403, 429):
            log.info(
                "ig_session_media_auth",
                tier=tier or "direct",
                status=resp.status_code,
                ds_user=session_id.split(":", 1)[0][:12],
            )
            break  # try next session in the pool
        if resp.status_code != 200:
            log.info(
                "ig_session_media_http",
                tier=tier or "direct",
                status=resp.status_code,
            )
            continue
        try:
            payload = resp.json()
        except ValueError:
            continue
        info = (payload.get("data") or {}).get(
            "xdt_api__v1__media__shortcode__web_info"
        ) or {}
        items = info.get("items") or []
        if items and isinstance(items[0], dict):
            return items[0]
    return None


async def comments_session_native(url: str, *, limit: int = 50) -> dict[str, Any] | None:
    """Full comment thread via ``api/v1/media/{pk}/comments/`` + session pool.

    Returns None when sessions are unset / invalid so callers can fall to Apify.
    """
    from app.utils.url import extract_instagram_shortcode

    sessions = _sessions_rotated()
    if not sessions or limit <= 0:
        return None
    shortcode = extract_instagram_shortcode(url)
    if not shortcode:
        return None
    # Prefer logged-out hydrate; on datacenter blocks fall back to session GraphQL.
    media = await _fetch_item(shortcode)
    if media is None:
        media = await _fetch_item_with_session(shortcode)
    if media is None:
        log.info("ig_comments_session_no_media", shortcode=shortcode)
        return None
    media_id = safe_str(media.get("pk") or media.get("id"))
    if not media_id:
        return None
    # ``id`` is sometimes ``{media_pk}_{user_id}``; comments API wants media pk.
    media_id = media_id.split("_", 1)[0]
    post_url = f"https://www.instagram.com/p/{shortcode}/"
    total = safe_int(media.get("comment_count")) or 0

    for session in sessions:
        comments: list[dict[str, Any]] = []
        seen: set[str] = set()
        min_id: str | None = None
        auth_failed = False
        for page in range(20):
            batch, next_min, more = await _fetch_comments_page(
                media_id, session_id=session, min_id=min_id, referer=post_url
            )
            if batch is None:
                if page == 0:
                    auth_failed = True
                break
            for raw in batch:
                mapped = _map_preview_comment(raw, post_url=post_url)
                if not mapped or not mapped.get("text"):
                    continue
                cid = mapped["id"] or mapped["text"]
                if cid in seen:
                    continue
                seen.add(cid)
                comments.append(mapped)
                if len(comments) >= limit:
                    break
            if len(comments) >= limit or not more or not next_min:
                break
            min_id = next_min

        if comments:
            return {
                "platform": "instagram",
                "url": url,
                "totalReturned": len(comments[:limit]),
                "totalComments": total or len(comments),
                "hasMore": (total or 0) > len(comments[:limit]),
                "comments": comments[:limit],
            }
        if not auth_failed:
            break  # got empty legitimately; don't burn the rest of the pool
    return None


async def _fetch_comments_page(
    media_id: str,
    *,
    session_id: str,
    min_id: str | None = None,
    referer: str = "https://www.instagram.com/",
) -> tuple[list[dict[str, Any]] | None, str | None, bool]:
    """One page of ``/api/v1/media/{id}/comments/``. ``(items, next_min_id, more)``.

    Requires ``Accept: application/json`` — without it Instagram returns the SPA
    HTML shell (200 text/html). Direct egress often works; proxies as fallback.
    """
    params: dict[str, Any] = {
        "can_support_threading": "true",
        "permalink_enabled": "false",
    }
    if min_id:
        params["min_id"] = min_id
    ds_user_id = session_id.split(":", 1)[0] if ":" in session_id else ""
    cookies = {"sessionid": session_id}
    if ds_user_id.isdigit():
        cookies["ds_user_id"] = ds_user_id
    # Direct first — residential IPs sometimes get HTML/challenge for session APIs.
    tiers: list[str | None] = [None, "datacenter", "residential"]
    for tier in tiers:
        try:
            async with httpx.AsyncClient(
                timeout=20,
                proxy=proxy_for(tier) if tier else None,
                follow_redirects=True,
                cookies=cookies,
            ) as client:
                await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
                csrf = client.cookies.get("csrftoken") or ""
                resp = await client.get(
                    f"https://www.instagram.com/api/v1/media/{media_id}/comments/",
                    params=params,
                    headers={
                        "User-Agent": _UA,
                        "X-IG-App-ID": _IG_APP_ID,
                        "X-CSRFToken": csrf,
                        "X-Requested-With": "XMLHttpRequest",
                        "X-ASBD-ID": "129477",
                        "Accept": "application/json",
                        "Referer": referer,
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                    },
                )
        except httpx.HTTPError as exc:
            log.info(
                "ig_comments_session_transport",
                tier=tier or "direct",
                error=str(exc)[:120],
            )
            continue
        if resp.status_code in (401, 403):
            log.info("ig_comments_session_auth", status=resp.status_code, tier=tier or "direct")
            return None, None, False
        if resp.status_code != 200:
            log.info(
                "ig_comments_session_http",
                status=resp.status_code,
                tier=tier or "direct",
            )
            continue
        body = (resp.text or "").lstrip()
        ctype = (resp.headers.get("content-type") or "").lower()
        if "json" not in ctype and not body.startswith("{"):
            log.info("ig_comments_session_non_json", tier=tier or "direct")
            continue
        try:
            payload = resp.json()
        except ValueError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("status") == "fail" and not payload.get("comments"):
            log.info(
                "ig_comments_session_fail",
                tier=tier or "direct",
                message=safe_str(payload.get("message"))[:80],
            )
            continue
        items = payload.get("comments") or payload.get("items") or []
        if not isinstance(items, list):
            continue
        next_min = safe_str(
            payload.get("next_min_id")
            or payload.get("min_id")
            or payload.get("next_max_id")
        ) or None
        more = bool(
            payload.get("has_more_comments")
            or payload.get("has_more")
            or payload.get("has_more_headload_comments")
            or next_min
        )
        return [i for i in items if isinstance(i, dict)], next_min, more
    return None, None, False


async def fetch_highlight_reel(highlight_id: str) -> dict[str, Any] | None:
    """Details for one Story Highlight album via the logged-out reels_media
    endpoint. ``highlight_id`` is the numeric id (no ``highlight:`` prefix).
    Datacenter IPs get the full tray here; residential often returns an empty
    tray, so try datacenter first. Returns the raw reel node or None.
    """
    reel_id = f"highlight:{highlight_id}"
    for tier in ("datacenter", "residential"):
        try:
            node = await _fetch_reels_media_once(tier, reel_id)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            log.info("ig_highlight_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        if node is not None:
            return node
    return None


async def _fetch_reels_media_once(tier: str, reel_id: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient(
        timeout=12, proxy=proxy_for(tier), follow_redirects=True
    ) as client:
        await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
        csrf = client.cookies.get("csrftoken")
        if not csrf:
            return None
        resp = await client.get(
            "https://www.instagram.com/api/v1/feed/reels_media/",
            params={"reel_ids": reel_id},
            headers={
                "User-Agent": _UA,
                "X-IG-App-ID": "936619743392459",
                "X-CSRFToken": csrf,
                "Referer": "https://www.instagram.com/",
            },
        )
        if resp.status_code != 200:
            log.info("ig_highlight_http_error", tier=tier, status=resp.status_code)
            return None
        payload = resp.json()
    reels = payload.get("reels")
    if not isinstance(reels, dict):
        return None
    node = reels.get(reel_id)
    return node if isinstance(node, dict) else None


def _map_story_item(item: dict[str, Any]) -> dict[str, Any]:
    media_type = safe_int(item.get("media_type"))
    is_video = media_type == 2
    videos = item.get("video_versions") or []
    images = (item.get("image_versions2") or {}).get("candidates") or []
    thumb = safe_str(images[0].get("url")) if images else None
    taken_at = safe_int(item.get("taken_at"))
    published = (
        datetime.fromtimestamp(taken_at, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if taken_at
        else None
    )
    mapped = {
        "type": _MEDIA_TYPE_NAMES.get(media_type or 0),
        "url": (safe_str(videos[0].get("url")) if videos else None) if is_video else thumb,
        "thumbnailUrl": thumb,
        "takenAt": published,
        "width": safe_int(item.get("original_width")),
        "height": safe_int(item.get("original_height")),
        "durationSeconds": _video_duration(item, item) if is_video else None,
    }
    return {k: v for k, v in mapped.items() if v is not None}


def map_highlight_reel(node: dict[str, Any]) -> dict[str, Any]:
    """Map a reels_media highlight node to the highlights-details shape."""
    cover = node.get("cover_media") or {}
    cover_url = (cover.get("cropped_image_version") or {}).get("url") or (
        cover.get("full_image_version") or {}
    ).get("url")
    raw_items = node.get("items") or []
    items = [_map_story_item(it) for it in raw_items if isinstance(it, dict)]
    media_count = safe_int(node.get("media_count"))
    return {
        "id": safe_str(node.get("id")),
        "title": safe_str(node.get("title")),
        "coverUrl": safe_str(cover_url),
        "itemCount": media_count if media_count is not None else (len(items) or None),
        "items": items,
    }


def map_feed_post(
    media: dict[str, Any],
    followers: int | None = None,
    profile_user_id: str | None = None,
) -> dict[str, Any]:
    """Map an api/v1 feed item to the channel-posts/reels list shape.

    ``followers`` is the requested profile's count; it only belongs on items
    that profile actually owns (collab posts in the feed are authored by a
    different account), hence the ``profile_user_id`` ownership check.
    """
    from app.services.instagram_decodo import strip_null_post_fields

    caption_obj = media.get("caption")
    caption = (safe_str(caption_obj.get("text")) if isinstance(caption_obj, dict) else "") or ""
    user = media.get("user") or {}
    username = safe_str(user.get("username"))
    shortcode = safe_str(media.get("code"))
    media_type = safe_int(media.get("media_type"))
    is_video = media_type == 2

    cover = (media.get("carousel_media") or [media])[0]
    videos = cover.get("video_versions") or []
    images = (cover.get("image_versions2") or {}).get("candidates") or []

    taken_at = safe_int(media.get("taken_at"))
    published = (
        datetime.fromtimestamp(taken_at, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if taken_at
        else None
    )

    owner_id = safe_str(user.get("pk") or user.get("pk_id") or user.get("id"))
    author: dict[str, Any] = {
        "id": owner_id,
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "url": f"https://instagram.com/{username}" if username else None,
        "verified": user.get("is_verified"),
        "profileImage": safe_str(user.get("profile_pic_url")) or None,
    }
    if followers is not None and (
        profile_user_id is None or owner_id is None or owner_id == profile_user_id
    ):
        author["followers"] = followers

    plays = safe_int(media.get("play_count"))
    ig_plays = safe_int(media.get("ig_play_count") or media.get("view_count"))
    likes = hidden_count(media.get("like_count"))
    views, plays_field = pick_video_views(
        view_count=ig_plays,
        play_count=plays,
        likes=likes,
        is_video=bool(is_video),
    )
    product = safe_str(media.get("product_type")) or ("clips" if is_video else None)

    return strip_null_post_fields(
        {
            "platform": "instagram",
            "url": f"https://www.instagram.com/{'reel' if is_video else 'p'}/{shortcode}/" if shortcode else None,
            "id": safe_str(media.get("pk") or media.get("id")),
            "shortcode": shortcode,
            "postType": _MEDIA_TYPE_NAMES.get(media_type or 0),
            "productType": product,
            "caption": caption,
            "description": caption,
            "publishedAt": published,
            "durationSeconds": _video_duration(media, cover),
            "thumbnailUrl": safe_str(images[0].get("url")) if images else None,
            "videoUrl": safe_str(videos[0].get("url")) if videos else None,
            "author": author,
            "engagement": {
                "views": views,
                "plays": plays_field,
                "likes": likes,
                "comments": hidden_count(media.get("comment_count")),
            },
            "hashtags": dedupe_preserve(_HASHTAG_RE.findall(caption)),
            "mentions": dedupe_preserve(_MENTION_RE.findall(caption)),
        }
    )


async def fetch_user_feed_page(
    user_id: str, max_id: str | None = None, count: int = 12
) -> tuple[list[dict[str, Any]], str | None, bool] | None:
    """One page of a profile's timeline via the logged-out api/v1 feed
    endpoint. Datacenter IPs get a flat 401 here, so this goes straight to
    the residential tier. Whether a residential IP gets 200 or 401 is
    per-session luck, so retry on a fresh session before giving up.
    Returns (raw items, next_max_id, more_available) or None on failure.
    """
    params: dict[str, Any] = {"count": max(1, min(count, 33))}
    if max_id:
        params["max_id"] = max_id
    degraded: tuple[list[dict[str, Any]], str | None, bool] | None = None
    for attempt in range(3):
        result = await _fetch_feed_once(user_id, params, attempt)
        if result is None:
            continue
        # Some sessions get a stripped feed variant whose clips carry no
        # video_duration/dash manifest. One fresh session usually fixes it,
        # but don't burn more than one extra request on cosmetics.
        if not _feed_page_degraded(result[0]):
            return result
        if degraded is not None:
            return result
        degraded = result
    return degraded


def _feed_page_degraded(items: list[dict[str, Any]]) -> bool:
    return any(
        safe_int(item.get("media_type")) == 2
        and not item.get("video_duration")
        and not item.get("video_dash_manifest")
        for item in items
    )


def _ig_session_cookies() -> dict[str, str]:
    """Round-robin session cookies for feed / usertags login walls."""
    session = _pick_session()
    return _cookies_for_session(session) if session else {}


async def _fetch_feed_once(
    user_id: str, params: dict[str, Any], attempt: int
) -> tuple[list[dict[str, Any]], str | None, bool] | None:
    # Prefer session+direct when available; rotate through the pool on auth fails.
    tiers: list[tuple[str | None, dict[str, str]]] = []
    for sid in _sessions_rotated():
        cks = _cookies_for_session(sid)
        tiers.append((None, cks))
        tiers.append(("residential", cks))
    tiers.append(("residential", {}))
    last_status: int | None = None
    for tier, cks in tiers:
        try:
            async with httpx.AsyncClient(
                timeout=15,
                proxy=proxy_for(tier) if tier else None,
                follow_redirects=True,
                cookies=cks,
            ) as client:
                await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
                resp = await client.get(
                    f"https://www.instagram.com/api/v1/feed/user/{user_id}/",
                    params=params,
                    headers={
                        "User-Agent": _UA,
                        "X-IG-App-ID": _IG_APP_ID,
                        "X-CSRFToken": client.cookies.get("csrftoken") or "",
                        "Accept": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                        "Referer": "https://www.instagram.com/",
                    },
                )
        except httpx.HTTPError as exc:
            log.info(
                "ig_feed_transport_error",
                attempt=attempt,
                tier=tier or "direct",
                error=str(exc)[:120],
            )
            continue
        last_status = resp.status_code
        if resp.status_code != 200:
            continue
        body = (resp.text or "").lstrip()
        if not body.startswith("{"):
            continue
        try:
            payload = resp.json()
        except ValueError:
            continue
        items = payload.get("items")
        if not isinstance(items, list):
            continue
        return items, safe_str(payload.get("next_max_id")) or None, bool(payload.get("more_available"))
    log.info("ig_feed_http_error", attempt=attempt, status=last_status)
    return None


async def fetch_usertags_page(
    user_id: str, max_id: str | None = None, count: int = 12
) -> tuple[list[dict[str, Any]], str | None, bool] | None:
    """One page of posts that tag ``user_id`` (``/api/v1/usertags/{id}/feed/``).

    Logged-out calls usually get the login HTML shell; ``IG_SESSION_ID`` unlocks
    JSON. Returns ``(raw items, next_max_id, more_available)`` or ``None``.
    """
    params: dict[str, Any] = {"count": max(1, min(count, 33))}
    if max_id:
        params["max_id"] = max_id
    for attempt in range(3):
        result = await _fetch_usertags_once(user_id, params, attempt)
        if result is not None:
            return result
    return None


async def _fetch_usertags_once(
    user_id: str, params: dict[str, Any], attempt: int
) -> tuple[list[dict[str, Any]], str | None, bool] | None:
    tiers: list[tuple[str | None, dict[str, str]]] = []
    for sid in _sessions_rotated():
        cks = _cookies_for_session(sid)
        tiers.append((None, cks))
        tiers.append(("residential", cks))
    tiers.append(("residential", {}))
    for tier, cks in tiers:
        try:
            async with httpx.AsyncClient(
                timeout=15,
                proxy=proxy_for(tier) if tier else None,
                follow_redirects=True,
                cookies=cks,
            ) as client:
                await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
                resp = await client.get(
                    f"https://www.instagram.com/api/v1/usertags/{user_id}/feed/",
                    params=params,
                    headers={
                        "User-Agent": _UA,
                        "X-IG-App-ID": _IG_APP_ID,
                        "X-CSRFToken": client.cookies.get("csrftoken") or "",
                        "Accept": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                        "Referer": "https://www.instagram.com/",
                    },
                )
        except httpx.HTTPError as exc:
            log.info(
                "ig_usertags_transport_error",
                attempt=attempt,
                tier=tier or "direct",
                error=str(exc)[:120],
            )
            continue
        if resp.status_code != 200:
            log.info(
                "ig_usertags_http_error",
                attempt=attempt,
                tier=tier or "direct",
                status=resp.status_code,
            )
            continue
        body = (resp.text or "").lstrip()
        ctype = (resp.headers.get("content-type") or "").lower()
        if "text/html" in ctype or body.startswith("<!DOCTYPE") or body.startswith("<html"):
            log.info("ig_usertags_login_wall", attempt=attempt, tier=tier or "direct")
            continue
        try:
            payload = resp.json()
        except ValueError:
            log.info("ig_usertags_non_json", attempt=attempt, tier=tier or "direct")
            continue
        items = payload.get("items")
        if not isinstance(items, list):
            continue
        return items, safe_str(payload.get("next_max_id")) or None, bool(payload.get("more_available"))
    return None


async def _fetch_item(shortcode: str) -> dict[str, Any] | None:
    for tier in _TIERS:
        try:
            media = await _fetch_via(tier, shortcode)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            log.info("ig_native_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        if media is not None:
            return media
    return None


async def _fetch_via(tier: str, shortcode: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient(
        timeout=10, proxy=proxy_for(tier), follow_redirects=True
    ) as client:
        # A GET to the homepage sets the csrftoken cookie the GraphQL
        # endpoint requires (cookie alone is rejected; header must match).
        await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
        csrf = client.cookies.get("csrftoken")
        if not csrf:
            return None
        resp = await client.post(
            "https://www.instagram.com/graphql/query",
            data={
                "doc_id": _POST_DOC_ID,
                "variables": json.dumps(
                    {
                        "shortcode": shortcode,
                        "__relay_internal__pv__PolarisAIGMMediaWebLabelEnabledrelayprovider": False,
                    },
                    separators=(",", ":"),
                ),
            },
            headers={
                "User-Agent": _UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-IG-App-ID": "936619743392459",
                "X-CSRFToken": csrf,
                "Referer": f"https://www.instagram.com/reel/{shortcode}/",
            },
        )
        if resp.status_code != 200:
            log.info("ig_native_http_error", tier=tier, status=resp.status_code)
            return None
        payload = resp.json()

    info = (payload.get("data") or {}).get("xdt_api__v1__media__shortcode__web_info") or {}
    items = info.get("items") or []
    if not items:
        return None
    return items[0]


# Instagram serves the classic server-rendered embed page (<html id="facebook">)
# only to non-browser clients; a modern Chrome UA gets the heavy React app shell.
_EMBED_UA = "curl/8.4.0"


async def fetch_embed_html(embed_url: str) -> str | None:
    """Fetch Instagram's self-contained embed page HTML for a post/reel/profile.

    ``embed_url`` is a fully-qualified .../embed/ (or /embed/captioned/) URL.
    Returns the rendered document (the ``<html id="facebook">`` embed page) or
    None if every proxy tier fails or Instagram returns the app shell instead.
    """
    for tier in _TIERS:
        try:
            html = await _fetch_embed_once(tier, embed_url)
        except (httpx.HTTPError, ValueError) as exc:
            log.info("ig_embed_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        if html is not None:
            return html
    return None


async def _fetch_embed_once(tier: str, embed_url: str) -> str | None:
    async with httpx.AsyncClient(
        timeout=12, proxy=proxy_for(tier), follow_redirects=True
    ) as client:
        resp = await client.get(embed_url, headers={"User-Agent": _EMBED_UA})
        if resp.status_code != 200:
            log.info("ig_embed_http_error", tier=tier, status=resp.status_code)
            return None
        html = resp.text
    # Reject the heavy React app shell; we only want the lightweight embed doc.
    if "EmbedFrame" not in html and 'id="facebook"' not in html:
        return None
    return html


# --- Profile lookup (logged-out) --------------------------------------------
_IG_APP_ID = "936619743392459"


async def _ig_web_get(tier: str, url: str, referer: str) -> dict[str, Any] | None:
    """GET an Instagram web api/v1 JSON endpoint logged-out (csrf + app id)."""
    async with httpx.AsyncClient(
        timeout=12, proxy=proxy_for(tier), follow_redirects=True
    ) as client:
        await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
        csrf = client.cookies.get("csrftoken")
        if not csrf:
            return None
        resp = await client.get(
            url,
            headers={
                "User-Agent": _UA,
                "X-IG-App-ID": _IG_APP_ID,
                "X-CSRFToken": csrf,
                "Referer": referer,
            },
        )
        if resp.status_code != 200:
            log.info("ig_web_http_error", tier=tier, status=resp.status_code)
            return None
        try:
            return resp.json()
        except ValueError:
            return None


async def resolve_username(user_id: str) -> str | None:
    """Map a numeric Instagram user id to its @username via users/{id}/info/.
    The logged-out response is minimal but always carries ``username``."""
    url = f"https://www.instagram.com/api/v1/users/{user_id}/info/"
    for tier in _TIERS:
        try:
            payload = await _ig_web_get(tier, url, "https://www.instagram.com/")
        except (httpx.HTTPError, ValueError) as exc:
            log.info("ig_userinfo_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        user = (payload or {}).get("user") if isinstance(payload, dict) else None
        username = safe_str((user or {}).get("username"))
        if username:
            return username
    return None


async def _fetch_web_profile_info_session(
    handle: str, session_id: str
) -> tuple[dict[str, Any] | None, bool]:
    """``web_profile_info`` with ``IG_SESSION_ID``.

    Returns ``(user, confirmed_404)``. A logged-in 404 means the handle is gone.
    """
    ds_user_id = session_id.split(":", 1)[0] if ":" in session_id else ""
    cookies: dict[str, str] = {"sessionid": session_id}
    if ds_user_id.isdigit():
        cookies["ds_user_id"] = ds_user_id
    url = (
        "https://www.instagram.com/api/v1/users/web_profile_info/"
        f"?username={urllib.parse.quote(handle)}"
    )
    referer = f"https://www.instagram.com/{handle}/"
    tiers: list[str | None] = [None, "datacenter", "residential"]
    saw_404 = False
    for tier in tiers:
        try:
            async with httpx.AsyncClient(
                timeout=20,
                proxy=proxy_for(tier) if tier else None,
                follow_redirects=True,
                cookies=cookies,
            ) as client:
                await client.get("https://www.instagram.com/", headers={"User-Agent": _UA})
                csrf = client.cookies.get("csrftoken") or ""
                resp = await client.get(
                    url,
                    headers={
                        "User-Agent": _UA,
                        "X-IG-App-ID": _IG_APP_ID,
                        "X-CSRFToken": csrf,
                        "X-Requested-With": "XMLHttpRequest",
                        "X-ASBD-ID": "129477",
                        "Accept": "*/*",
                        "Referer": referer,
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                    },
                )
        except httpx.HTTPError as exc:
            log.info(
                "ig_wpi_session_transport",
                tier=tier or "direct",
                error=str(exc)[:120],
            )
            continue
        if resp.status_code == 404:
            saw_404 = True
            log.info("ig_wpi_session_http", tier=tier or "direct", status=404)
            continue
        if resp.status_code != 200:
            log.info(
                "ig_wpi_session_http",
                tier=tier or "direct",
                status=resp.status_code,
                body=(resp.text or "")[:80],
            )
            continue
        try:
            payload = resp.json()
        except ValueError:
            continue
        user = (payload.get("data") or {}).get("user") or payload.get("user")
        if isinstance(user, dict) and (user.get("username") or user.get("id")):
            return user, False
    return None, saw_404


def _pick_ig_user_pk(window: str) -> str | None:
    """Pick a feed-compatible user pk from a profile HTML window.

    Prefer non-``17841…`` ids (those are XIG/Graph scoped) and shorter pks.
    """
    found = [m.group(1) for m in re.finditer(r'"id"\s*:\s*"?(\d{5,})"?', window)]
    found += [m.group(1) for m in re.finditer(r'"pk"\s*:\s*"?(\d{5,})"?', window)]
    if not found:
        return None
    ranked = sorted(
        set(found),
        key=lambda x: (x.startswith("17841"), len(x), x),
    )
    return ranked[0]


_COMPACT_COUNT_RE = re.compile(
    r"^\s*([\d.,]+)\s*([KMB])?\s*$",
    re.IGNORECASE,
)
_COMPACT_MULT = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
_OG_PROFILE_COUNTS_RE = re.compile(
    r"([\d.,]+[KMB]?)\s+Followers?,\s*([\d.,]+[KMB]?)\s+Following,\s*([\d.,]+[KMB]?)\s+Posts?",
    re.IGNORECASE,
)


def _parse_compact_count(value: str | None) -> int | None:
    """Parse ``32K`` / ``1,667`` / ``269M`` style counts from og:description."""
    if not value:
        return None
    m = _COMPACT_COUNT_RE.match(value.replace("\u00a0", " "))
    if not m:
        return None
    try:
        base = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    suffix = (m.group(2) or "").upper()
    return int(base * _COMPACT_MULT.get(suffix, 1))


def _external_url_from_bio_links(html: str) -> str | None:
    """First non-lynx URL from ``bio_links`` embedded in profile HTML."""
    idx = html.find('"bio_links"')
    if idx < 0:
        return None
    window = html[idx : idx + 4000]
    urls: list[str] = []
    for m in re.finditer(r'"url"\s*:\s*"((?:\\.|[^"\\])*)"', window):
        try:
            url = json.loads(f'"{m.group(1)}"')
        except ValueError:
            url = m.group(1).encode("utf-8").decode("unicode_escape", errors="ignore")
        url = (url or "").strip()
        if not url or not url.startswith("http"):
            continue
        if "l.instagram.com" in url or "instagram.com/_u/" in url:
            continue
        urls.append(url)
    if urls:
        return urls[0]
    # Fallback: unwrap lynx redirect ``?u=``.
    for m in re.finditer(r'"lynx_url"\s*:\s*"((?:\\.|[^"\\])*)"', window):
        try:
            lynx = json.loads(f'"{m.group(1)}"')
        except ValueError:
            continue
        if not lynx or "u=" not in lynx:
            continue
        q = urllib.parse.parse_qs(urllib.parse.urlparse(lynx).query).get("u") or []
        if q:
            return urllib.parse.unquote(q[0])
    return None


def _counts_from_og_description(html: str) -> tuple[int | None, int | None, int | None]:
    """``og:description`` → (followers, following, posts)."""
    m = re.search(
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        html,
        re.I,
    ) or re.search(
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
        html,
        re.I,
    )
    if not m:
        return None, None, None
    cm = _OG_PROFILE_COUNTS_RE.search(m.group(1))
    if not cm:
        return None, None, None
    return (
        _parse_compact_count(cm.group(1)),
        _parse_compact_count(cm.group(2)),
        _parse_compact_count(cm.group(3)),
    )


def parse_profile_from_html(html: str, handle: str) -> dict[str, Any] | None:
    """Best-effort user dict from a rendered profile page (Decodo / browser HTML).

    Used when ``web_profile_info`` is rate-limited or returns Instagram's
    ``laser.provider`` 400 for some business accounts.
    """
    if not html or not handle:
        return None
    want = handle.lstrip("@").lower()
    # Anchor on this profile's username — earlier "username" keys are often the viewer.
    anchors = list(
        re.finditer(rf'"username"\s*:\s*"{re.escape(want)}"', html, re.I)
    )
    if not anchors:
        return None

    og_followers, og_following, og_posts = _counts_from_og_description(html)
    external_from_links = _external_url_from_bio_links(html)

    def _from_window(window: str) -> dict[str, Any] | None:
        def _str(key: str) -> str | None:
            m = re.search(rf'"{key}"\s*:\s*"((?:\\.|[^"\\])*)"', window)
            if not m:
                return None
            try:
                return json.loads(f'"{m.group(1)}"')
            except ValueError:
                return m.group(1)

        def _int(key: str) -> int | None:
            m = re.search(rf'"{key}"\s*:\s*(\d+)', window)
            return int(m.group(1)) if m else None

        def _bool(key: str) -> bool | None:
            m = re.search(rf'"{key}"\s*:\s*(true|false)', window)
            if not m:
                return None
            return m.group(1) == "true"

        followers = _int("follower_count")
        if followers is None:
            m = re.search(
                r'"edge_followed_by"\s*:\s*\{\s*"count"\s*:\s*(\d+)',
                window,
            )
            followers = int(m.group(1)) if m else None
        following = _int("following_count")
        if following is None:
            m = re.search(r'"edge_follow"\s*:\s*\{\s*"count"\s*:\s*(\d+)', window)
            following = int(m.group(1)) if m else None
        media = _int("media_count") or _int("all_media_count")
        if media is None:
            m = re.search(
                r'"edge_owner_to_timeline_media"\s*:\s*\{\s*"count"\s*:\s*(\d+)',
                window,
            )
            media = int(m.group(1)) if m else None
        bio = _str("biography")
        full_name = _str("full_name")
        pic = _str("profile_pic_url_hd") or _str("profile_pic_url")
        external = _str("external_url")
        verified = _bool("is_verified")
        # HTML embeds both the feed ``pk`` (e.g. 3621456554) and an XIG/Graph
        # ``id`` (``17841…``). Feed / usertags APIs need the pk.
        uid = _pick_ig_user_pk(window)
        if followers is None and not bio and not full_name:
            return None
        return {
            "username": want,
            "full_name": full_name,
            "biography": bio,
            "follower_count": followers,
            "following_count": following,
            "media_count": media,
            "is_verified": verified,
            "profile_pic_url": pic,
            "external_url": external,
            "id": uid,
            "pk": uid,
        }

    fallback: dict[str, Any] | None = None
    parsed: dict[str, Any] | None = None
    for anchor in anchors:
        # follower_count often sits a few KB before the username key in the same node.
        start = max(0, anchor.start() - 4000)
        end = min(len(html), anchor.end() + 6000)
        candidate = _from_window(html[start:end])
        if not candidate:
            continue
        if candidate.get("follower_count") is not None:
            parsed = candidate
            break
        if fallback is None:
            fallback = candidate
    parsed = parsed or fallback
    if not parsed:
        return None

    # Logged-out HTML often omits media_count / external_url; og:description and
    # bio_links still expose them.
    if parsed.get("media_count") is None and og_posts is not None:
        parsed["media_count"] = og_posts
    if parsed.get("follower_count") is None and og_followers is not None:
        parsed["follower_count"] = og_followers
    if parsed.get("following_count") is None and og_following is not None:
        parsed["following_count"] = og_following
    if not parsed.get("external_url") and external_from_links:
        parsed["external_url"] = external_from_links
    return parsed


def profile_unavailable_html(html: str) -> bool:
    """True when Instagram's rendered profile page says the account is gone."""
    if not html:
        return False
    lower = html.lower()
    if "profile isn't available" in lower or "profile isn&#39;t available" in lower:
        return True
    if "sorry, this page isn't available" in lower:
        return True
    title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
    if title_m and "isn't available" in title_m.group(1).lower():
        return True
    return False


async def fetch_web_profile_info_via_decodo(
    username: str,
) -> tuple[dict[str, Any] | None, bool]:
    """Render the profile page via Decodo and parse counts / bio from HTML.

    Returns ``(user, confirmed_missing)``.
    """
    from app.services import decodo_fetch

    handle = username.lstrip("@")
    if not decodo_fetch.enabled() or not handle:
        return None, False
    got = await decodo_fetch.fetch_url(
        f"https://www.instagram.com/{handle}/",
        timeout=90.0,
        headless="html",
    )
    if not got:
        return None, False
    status, body = got
    if status == 404:
        return None, True
    if status != 200 or not body:
        return None, False
    if profile_unavailable_html(body):
        log.info("ig_wpi_decodo_unavailable", handle=handle)
        return None, True
    user = parse_profile_from_html(body, handle)
    if user:
        log.info(
            "ig_wpi_decodo_html_ok",
            handle=handle,
            followers=user.get("follower_count"),
        )
        return user, False
    log.info("ig_wpi_decodo_html_miss", handle=handle, length=len(body))
    return None, False


async def lookup_web_profile_info(
    username: str,
) -> tuple[dict[str, Any] | None, bool]:
    """Rich profile lookup.

    Returns ``(user, confirmed_missing)``. When ``confirmed_missing`` is True,
    callers should 404 instead of spending Apify credits on a dead handle.
    """
    from app.core.config import get_settings

    handle = username.lstrip("@")
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={urllib.parse.quote(handle)}"
    referer = f"https://www.instagram.com/{handle}/"
    for tier in _TIERS:
        try:
            payload = await _ig_web_get(tier, url, referer)
        except (httpx.HTTPError, ValueError) as exc:
            log.info("ig_wpi_tier_failed", tier=tier, error=str(exc)[:120])
            continue
        if not isinstance(payload, dict):
            continue
        user = (payload.get("data") or {}).get("user") or payload.get("user")
        if isinstance(user, dict) and (user.get("username") or user.get("id")):
            return user, False

    session_404 = False
    for sid in _sessions_rotated():
        user, session_404 = await _fetch_web_profile_info_session(handle, sid)
        if user is not None:
            return user, False
        if session_404:
            # Confirmed missing handle — no point burning the rest of the pool.
            break

    user, missing = await fetch_web_profile_info_via_decodo(handle)
    if user is not None:
        return user, False
    return None, bool(missing or session_404)


async def fetch_web_profile_info(username: str) -> dict[str, Any] | None:
    """Rich profile via users/web_profile_info/?username=.

    Order: logged-out proxy tiers → session pool (skips 429/login wall) →
    Decodo HTML parse (covers business accounts that 400 on WPI).
    """
    user, _missing = await lookup_web_profile_info(username)
    return user


def _edge_count(value: Any) -> int | None:
    if isinstance(value, dict):
        return safe_int(value.get("count"))
    return safe_int(value)


def _biography_with_entities(user: dict[str, Any]) -> dict[str, Any] | None:
    raw = user.get("biography_with_entities")
    if not isinstance(raw, dict):
        return None
    entities = raw.get("entities") if isinstance(raw.get("entities"), list) else []
    return {
        "rawText": safe_str(raw.get("raw_text") or raw.get("rawText") or user.get("biography")),
        "entities": entities,
    }


def _account_badges(user: dict[str, Any]) -> list[Any] | None:
    raw = user.get("account_badges") or user.get("accountBadges")
    if isinstance(raw, list):
        return raw
    return None


def _linked_fb_info(user: dict[str, Any]) -> dict[str, Any] | None:
    raw = user.get("linked_fb_info") or user.get("linkedFbInfo") or user.get("fb_profile_biolink")
    if isinstance(raw, dict) and raw:
        return {
            "url": safe_str(raw.get("url") or raw.get("link")),
            "id": safe_str(raw.get("id") or raw.get("fb_id") or raw.get("fbid")),
            "name": safe_str(raw.get("name") or raw.get("title")),
        }
    if isinstance(raw, str) and raw.strip():
        return {"url": raw.strip(), "id": None, "name": None}
    return None


def map_basic_profile(user: dict[str, Any]) -> dict[str, Any]:
    """Map a web_profile_info user node to Captapi camelCase profile shape.

    Same naming as ``/channel-details`` (displayName, followers, verified,
    externalUrl, …) plus richer basic-profile fields. Null/absent values are
    dropped so the JSON stays tidy.
    """
    from app.utils.media_urls import utc_now_iso

    username = safe_str(user.get("username"))
    pic = safe_str(user.get("profile_pic_url"))
    pic_hd = safe_str(user.get("profile_pic_url_hd"))
    # Some payloads nest HD as hd_profile_pic_url_info.url
    hd_info = user.get("hd_profile_pic_url_info")
    if not pic_hd and isinstance(hd_info, dict):
        pic_hd = safe_str(hd_info.get("url"))
    verified = user.get("is_verified")
    private = user.get("is_private")
    uid = safe_str(user.get("id") or user.get("pk"))
    followers = _edge_count(user.get("edge_followed_by") or user.get("follower_count"))
    following = _edge_count(user.get("edge_follow") or user.get("following_count"))
    post_count = _edge_count(
        user.get("edge_owner_to_timeline_media")
        or user.get("media_count")
        or user.get("all_media_count")
    )
    total_clips = safe_int(user.get("total_clips_count") or user.get("totalClipsCount"))
    category = safe_str(
        user.get("category_name")
        or user.get("categoryName")
        or user.get("business_category_name")
        or user.get("overall_category_name")
        or user.get("category")
        or user.get("category_enum")
    )
    bio_links = _bio_links(user)
    external = _external_url_from_user(user)
    pronouns = user.get("pronouns") if isinstance(user.get("pronouns"), list) else None
    badges = _account_badges(user)
    latest_reel = user.get("latest_reel_media")
    if latest_reel is not None and not isinstance(latest_reel, (int, float, str)):
        latest_reel = safe_str(latest_reel) or None

    out: dict[str, Any] = {
        "platform": "instagram",
        "url": f"https://instagram.com/{username}" if username else None,
        "id": uid,
        "pk": safe_str(user.get("pk") or uid),
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "bio": safe_str(user.get("biography")),
        "biographyWithEntities": _biography_with_entities(user),
        "followers": followers,
        "following": following,
        "postCount": post_count,
        "highlightReelCount": safe_int(user.get("highlight_reel_count")),
        "totalClipsCount": total_clips,
        "hasClips": bool(user.get("has_clips")) if user.get("has_clips") is not None else None,
        "isPrivate": False if private is None else bool(private),
        "verified": False if verified is None else bool(verified),
        "isBusinessAccount": (
            None
            if user.get("is_business_account") is None and user.get("is_business") is None
            else bool(
                user.get("is_business_account")
                if user.get("is_business_account") is not None
                else user.get("is_business")
            )
        ),
        "isProfessionalAccount": (
            None
            if user.get("is_professional_account") is None
            else bool(user.get("is_professional_account"))
        ),
        "isMemorialized": (
            None
            if user.get("is_memorialized") is None
            else bool(user.get("is_memorialized"))
        ),
        "accountType": safe_int(user.get("account_type") or user.get("accountType")),
        "categoryName": category,
        "shouldShowCategory": (
            None
            if user.get("should_show_category") is None
            else bool(user.get("should_show_category"))
        ),
        "profileImage": pic_hd or pic,
        "profileImageHd": pic_hd,
        "profileImageUrl": pic,
        "externalUrl": external,
        "fbid": safe_str(user.get("fbid") or user.get("fbid_v2")),
        "pronouns": pronouns,
        "bioLinks": bio_links,
        "accountBadges": badges,
        "transparencyLabel": user.get("transparency_label"),
        "transparencyProduct": user.get("transparency_product"),
        "showAccountTransparencyDetails": (
            None
            if user.get("show_account_transparency_details") is None
            else bool(user.get("show_account_transparency_details"))
        ),
        "isEmbedsDisabled": (
            None
            if user.get("is_embeds_disabled") is None
            else bool(user.get("is_embeds_disabled"))
        ),
        "isRegulatedC18": (
            None
            if user.get("is_regulated_c18") is None
            else bool(user.get("is_regulated_c18"))
        ),
        "showTextPostAppBadge": (
            None
            if user.get("show_text_post_app_badge") is None
            else bool(user.get("show_text_post_app_badge"))
        ),
        "removeMessageEntrypoint": (
            None
            if user.get("remove_message_entrypoint") is None
            else bool(user.get("remove_message_entrypoint"))
        ),
        "businessAddress": _business_address(user),
        "businessEmail": safe_str(user.get("business_email")),
        "businessPhoneNumber": safe_str(user.get("business_phone_number")),
        "businessContactMethod": safe_str(user.get("business_contact_method")),
        "linkedFbInfo": _linked_fb_info(user),
        "latestReelMedia": safe_int(latest_reel) if latest_reel is not None else None,
        "aiAgentType": user.get("ai_agent_type"),
        "fetchedAt": utc_now_iso(),
    }
    return {k: v for k, v in out.items() if v is not None}


def _external_url_from_user(user: dict[str, Any]) -> str | None:
    direct = safe_str(user.get("external_url"))
    if direct:
        return direct
    links = user.get("bio_links")
    if not isinstance(links, list):
        return None
    for link in links:
        if not isinstance(link, dict):
            continue
        url = safe_str(link.get("url"))
        if url and url.startswith("http") and "l.instagram.com" not in url:
            return url
        lynx = safe_str(link.get("lynx_url"))
        if lynx and "u=" in lynx:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(lynx).query).get("u") or []
            if q:
                return urllib.parse.unquote(q[0])
    return None


def _bio_links(user: dict[str, Any]) -> list[dict[str, Any]]:
    raw = user.get("bio_links")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for link in raw:
        if not isinstance(link, dict):
            continue
        url = safe_str(link.get("url"))
        if not url and safe_str(link.get("lynx_url")):
            lynx = safe_str(link.get("lynx_url")) or ""
            if "u=" in lynx:
                q = urllib.parse.parse_qs(urllib.parse.urlparse(lynx).query).get("u") or []
                if q:
                    url = urllib.parse.unquote(q[0])
        if not url:
            continue
        out.append(
            {
                "title": safe_str(link.get("title")),
                "url": url,
                "linkType": safe_str(link.get("link_type") or link.get("linkType")),
            }
        )
    return out


def _business_address(user: dict[str, Any]) -> dict[str, Any] | None:
    raw = user.get("business_address_json") or user.get("business_address")
    if isinstance(raw, str) and raw.strip():
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return None
    if not isinstance(raw, dict):
        return None
    city = safe_str(raw.get("city_name") or raw.get("cityName"))
    street = safe_str(
        raw.get("street_address")
        or raw.get("address_street")
        or raw.get("streetAddress")
        or raw.get("addressStreet")
    )
    zip_code = safe_str(raw.get("zip_code") or raw.get("zipCode"))
    lat = raw.get("latitude")
    lng = raw.get("longitude")
    if not any([city, street, zip_code, lat is not None, lng is not None]):
        return None
    return {
        "cityName": city,
        "cityId": safe_str(raw.get("city_id") or raw.get("cityId")),
        "streetAddress": street,
        "latitude": lat if isinstance(lat, (int, float)) else safe_float(lat),
        "longitude": lng if isinstance(lng, (int, float)) else safe_float(lng),
        "zipCode": zip_code,
    }


def map_channel_details(user: dict[str, Any], *, handle: str | None = None) -> dict[str, Any]:
    """Map a web_profile_info user node to the channel-details response shape.

    Existing keys (platform…externalUrl) stay stable for customers; newer fields
    are additive only.
    """
    from app.utils.media_urls import utc_now_iso

    username = safe_str(user.get("username")) or (handle or "").lstrip("@")
    pic = safe_str(user.get("profile_pic_url"))
    pic_hd = safe_str(user.get("profile_pic_url_hd"))
    verified = user.get("is_verified")
    private = user.get("is_private")
    followers = _edge_count(user.get("edge_followed_by") or user.get("follower_count"))
    following = _edge_count(user.get("edge_follow") or user.get("following_count"))
    post_count = _edge_count(
        user.get("edge_owner_to_timeline_media")
        or user.get("media_count")
        or user.get("all_media_count")
        or user.get("total_clips_count")
    )
    bio_links = _bio_links(user)
    external = _external_url_from_user(user)
    # Prefer HD for profileImage when available (previous behavior); expose both.
    profile_image = pic_hd or pic
    return {
        "platform": "instagram",
        "url": f"https://instagram.com/{username}" if username else None,
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "bio": safe_str(user.get("biography")),
        "followers": followers,
        "following": following,
        "postCount": post_count,
        "verified": False if verified is None else bool(verified),
        "profileImage": profile_image,
        "externalUrl": external,
        # --- additive (non-breaking) ---
        "id": safe_str(user.get("id") or user.get("pk")),
        "fbid": safe_str(user.get("fbid") or user.get("fbid_v2")),
        "isPrivate": False if private is None else bool(private),
        "isBusinessAccount": (
            None
            if user.get("is_business_account") is None
            else bool(user.get("is_business_account"))
        ),
        "isProfessionalAccount": (
            None
            if user.get("is_professional_account") is None
            else bool(user.get("is_professional_account"))
        ),
        "categoryName": safe_str(user.get("category_name") or user.get("category")),
        "bioLinks": bio_links,
        "profileImageHd": pic_hd,
        "businessAddress": _business_address(user),
        "followersIsApproximate": False,
        "followingIsApproximate": False,
        "postCountIsApproximate": False,
        "fetchedAt": utc_now_iso(),
    }


def map_profile_search_user(user: dict[str, Any]) -> dict[str, Any]:
    """Profile-search row: stable id + channel-details enrichment (resolver, not discovery).

    Still a single resolved account (name → @handle), but CRM-ready: numeric id,
    bio, links, category, business flags, following/postCount — so callers do not
    need a second channel-details call for the common enrichment fields.
    """
    from app.utils.formatters import strip_empty

    username = safe_str(user.get("username"))
    verified = user.get("is_verified")
    private = user.get("is_private")
    uid = safe_str(user.get("id") or user.get("pk"))
    pic = safe_str(user.get("profile_pic_url"))
    pic_hd = safe_str(user.get("profile_pic_url_hd"))
    hd_info = user.get("hd_profile_pic_url_info")
    if not pic_hd and isinstance(hd_info, dict):
        pic_hd = safe_str(hd_info.get("url"))
    category = safe_str(
        user.get("category_name")
        or user.get("categoryName")
        or user.get("business_category_name")
        or user.get("overall_category_name")
        or user.get("category")
    )
    bio_links = _bio_links(user)
    external = _external_url_from_user(user)
    is_business = user.get("is_business_account")
    if is_business is None:
        is_business = user.get("is_business")
    is_pro = user.get("is_professional_account")
    out: dict[str, Any] = {
        "id": uid,
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "url": f"https://instagram.com/{username}" if username else None,
        "bio": safe_str(user.get("biography")),
        "followers": _edge_count(user.get("edge_followed_by") or user.get("follower_count")),
        "following": _edge_count(user.get("edge_follow") or user.get("following_count")),
        "postCount": _edge_count(
            user.get("edge_owner_to_timeline_media")
            or user.get("media_count")
            or user.get("all_media_count")
        ),
        "verified": False if verified is None else bool(verified),
        # Keep ``private`` for back-compat; ``isPrivate`` matches channel-details.
        "private": False if private is None else bool(private),
        "isPrivate": False if private is None else bool(private),
        "isBusinessAccount": None if is_business is None else bool(is_business),
        "isProfessionalAccount": None if is_pro is None else bool(is_pro),
        "categoryName": category,
        "externalUrl": external,
        "bioLinks": bio_links,
        "profileImage": pic_hd or pic,
        "profileImageHd": pic_hd,
    }
    return strip_empty(out)


# Logged-out api/v1 tags / clips-music endpoints return login HTML. Decodo
# headless Explore/audio pages still emit /reel/{code}/ and /p/{code}/ links;
# Explore also embeds media as JSON ``"code":"SHORTCODE"`` without hrefs.
# We collect those shortcodes and hydrate via PolarisPostRootQuery.
# Explore/audio HTML often has href="/reel/CODE/… without a quote right after /.
_HREF_SHORTCODE_RE = re.compile(
    r'(?:href="|href=&quot;)/(?:reel|p)/([A-Za-z0-9_-]{5,})/',
    re.IGNORECASE,
)
_JSON_CODE_RE = re.compile(
    r'"(?:code|shortcode)"\s*:\s*"([A-Za-z0-9_-]{8,15})"',
)
_LOCALE_CODE_RE = re.compile(r"^[a-z]{2}[_-][A-Z]{2}$")
_AUDIO_ID_RE = re.compile(r"/reels/audio/(\d+)", re.IGNORECASE)

# Trending actor country name → Decodo geo ISO (best-effort Explore localization).
_TRENDING_GEO: dict[str, str] = {
    "United States": "US",
    "Canada": "CA",
    "United Kingdom": "GB",
    "Australia": "AU",
    "Germany": "DE",
    "France": "FR",
    "Italy": "IT",
    "Spain": "ES",
    "Netherlands": "NL",
    "Sweden": "SE",
    "Norway": "NO",
    "Denmark": "DK",
    "Finland": "FI",
    "Poland": "PL",
    "Portugal": "PT",
    "Brazil": "BR",
    "Mexico": "MX",
    "Argentina": "AR",
    "Chile": "CL",
    "Colombia": "CO",
    "Japan": "JP",
    "South Korea": "KR",
    "Singapore": "SG",
    "Hong Kong": "HK",
    "Taiwan": "TW",
    "India": "IN",
    "Indonesia": "ID",
    "Thailand": "TH",
    "Philippines": "PH",
    "Malaysia": "MY",
    "Vietnam": "VN",
    "United Arab Emirates": "AE",
    "Saudi Arabia": "SA",
    "Turkey": "TR",
    "South Africa": "ZA",
}


def _looks_like_shortcode(code: str) -> bool:
    if not code or len(code) < 8 or len(code) > 15:
        return False
    if _LOCALE_CODE_RE.fullmatch(code):
        return False
    # Locales / i18n keys sometimes slip into "code" fields (en_US, pt_BR…).
    if "_" in code and code.split("_", 1)[0].islower() and len(code.split("_", 1)[0]) == 2:
        return False
    return True


def shortcodes_from_html(html: str, *, limit: int = 50) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for code in _HREF_SHORTCODE_RE.findall(html or ""):
        # href shortcodes can be 5–15 chars; reject locale-shaped noise.
        if len(code) < 5 or _LOCALE_CODE_RE.fullmatch(code):
            continue
        if code in seen:
            continue
        seen.add(code)
        out.append(code)
        if len(out) >= limit:
            return out
    for code in _JSON_CODE_RE.findall(html or ""):
        if not _looks_like_shortcode(code) or code in seen:
            continue
        seen.add(code)
        out.append(code)
        if len(out) >= limit:
            break
    return out


async def fetch_shortcodes_via_decodo(
    url: str, *, limit: int = 50, geo: str | None = None
) -> list[str] | None:
    """JS-render ``url`` via Decodo and return Instagram shortcodes, or None."""
    from app.services import decodo_fetch

    if not decodo_fetch.enabled() or limit <= 0:
        return None
    got = await decodo_fetch.fetch_url(
        url, timeout=90.0, headless="html", geo=geo
    )
    if not got:
        return None
    status, body = got
    if status != 200 or not body:
        return None
    codes = shortcodes_from_html(body, limit=limit)
    if not codes:
        log.info("ig_decodo_shortcodes_empty", url=url[:120])
        return None
    log.info("ig_decodo_shortcodes_ok", url=url[:120], n=len(codes))
    return codes


async def hydrate_shortcodes(codes: list[str], *, limit: int) -> list[dict[str, Any]]:
    """Resolve shortcodes through Polaris (bounded concurrency)."""
    if not codes or limit <= 0:
        return []
    sem = asyncio.Semaphore(4)
    selected = codes[:limit]

    async def _one(code: str) -> dict[str, Any] | None:
        async with sem:
            return await fetch_post_details(code)

    rows = await asyncio.gather(*[_one(c) for c in selected])
    return [r for r in rows if r]


async def reels_by_audio_native(audio_id: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    """Reels that use ``audio_id`` via Decodo Explore audio page + Polaris hydrate.

    Listing itself is not available logged-out on api/v1; Apify remains fallthrough.
    """
    raw = (audio_id or "").strip()
    if not raw:
        return None
    if raw.startswith("http"):
        match = _AUDIO_ID_RE.search(raw)
        aid = match.group(1) if match else raw.rstrip("/").split("/")[-1]
    else:
        aid = raw
    if not aid.isdigit():
        return None
    page_url = f"https://www.instagram.com/reels/audio/{aid}/"
    codes = await fetch_shortcodes_via_decodo(page_url, limit=limit)
    if not codes:
        return None
    posts = await hydrate_shortcodes(codes, limit=limit)
    if not posts:
        return None
    for post in posts:
        code = safe_str(post.get("id"))
        if code:
            post["url"] = f"https://www.instagram.com/reel/{code}/"
        post["musicId"] = aid
        post["musicUrl"] = page_url
    return posts


def is_reel_post(post: dict[str, Any]) -> bool:
    """True for Reels/clips/videos — photos and carousels are excluded."""
    product = (safe_str(post.get("productType")) or "").lower()
    post_type = (safe_str(post.get("postType")) or "").lower()
    if product in {"clips", "reel", "reels"}:
        return True
    if post_type in {"video", "reel", "clips"}:
        return True
    if post.get("videoUrl") and post_type not in {"sidecar", "carousel", "album"}:
        return True
    return False


def _parse_published_at(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(int(value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    s = safe_str(value)
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _is_stale_explore_post(post: dict[str, Any], *, max_age_days: int = 180) -> bool:
    """Explore actors sometimes resurface years-old photos — not 'trending'."""
    published = _parse_published_at(post.get("publishedAt"))
    if published is None:
        return False
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - published
    return age.days > max_age_days


def _trending_ids(post: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return (numeric_media_id, shortcode) for a stable public contract."""
    shortcode = safe_str(post.get("shortcode") or post.get("shortCode"))
    media_id = safe_str(post.get("mediaId"))
    raw = safe_str(post.get("id"))
    if raw and "_" in raw:
        head, _, _tail = raw.partition("_")
        if head.isdigit():
            media_id = media_id or head
    elif raw and raw.isdigit():
        media_id = media_id or raw
    elif raw and not shortcode and not raw.isdigit():
        shortcode = raw
    url = safe_str(post.get("url")) or ""
    m = re.search(r"/(?:reel|p|tv)/([^/?#]+)/?", url, re.I)
    if m and not shortcode:
        shortcode = m.group(1)
    return media_id, shortcode


def _as_trending_reel(post: dict[str, Any]) -> dict[str, Any]:
    """Align Polaris post details with the trending-reels response shape."""
    media_id, shortcode = _trending_ids(post)
    product = safe_str(post.get("productType")) or "clips"
    url = safe_str(post.get("url"))
    if shortcode:
        url = f"https://www.instagram.com/reel/{shortcode}/"
    engagement = post.get("engagement") if isinstance(post.get("engagement"), dict) else {}
    author = post.get("author") if isinstance(post.get("author"), dict) else {}
    return {
        "platform": "instagram",
        "url": url,
        # Prefer numeric media id (matches channel-reels); shortcode for URLs.
        "id": media_id or shortcode,
        "shortcode": shortcode,
        "postType": "Video",
        "productType": product if product else "clips",
        "section": post.get("section"),
        "topic": post.get("topic"),
        "caption": post.get("caption"),
        "description": post.get("description") or post.get("caption"),
        "publishedAt": post.get("publishedAt"),
        "durationSeconds": post.get("durationSeconds"),
        "thumbnailUrl": post.get("thumbnailUrl"),
        "videoUrl": post.get("videoUrl"),
        "author": {
            "username": author.get("username"),
            "url": author.get("url"),
        },
        "engagement": {
            "views": engagement.get("views"),
            "likes": engagement.get("likes"),
            "comments": engagement.get("comments"),
        },
        "hashtags": dedupe_preserve(post.get("hashtags") or []),
        "mentions": dedupe_preserve(post.get("mentions") or []),
    }


async def trending_reels_native(
    country: str = "United States", *, limit: int = 20
) -> list[dict[str, Any]] | None:
    """Explore Reels via Decodo (optional geo) + Polaris hydrate.

    Scrapes Reels-first URLs, hydrates shortcodes, then **keeps only videos**
    (same contract as channel-reels). Photos/carousels are never returned —
    padding with Explore images made the docs lie. Apify remains fallthrough.
    """
    if limit <= 0:
        return []
    geo = _TRENDING_GEO.get((country or "").strip()) or None
    # Over-fetch: Explore HTML mixes photos; hydrate 401s some codes.
    fetch_n = min(200, max(limit * 5, limit + 40))
    urls = (
        "https://www.instagram.com/explore/reels/",
        "https://www.instagram.com/reels/",
        "https://www.instagram.com/explore/",
    )
    codes: list[str] = []
    seen: set[str] = set()
    for page_url in urls:
        got = await fetch_shortcodes_via_decodo(page_url, limit=fetch_n, geo=geo)
        if not got:
            continue
        for code in got:
            if code in seen:
                continue
            seen.add(code)
            codes.append(code)
            if len(codes) >= fetch_n:
                break
        if len(codes) >= fetch_n:
            break
    if not codes:
        return None
    posts = await hydrate_shortcodes(codes, limit=fetch_n)
    if not posts:
        return None
    reels: list[dict[str, Any]] = []
    for post in posts:
        if not is_reel_post(post):
            continue
        if _is_stale_explore_post(post):
            continue
        reels.append(_as_trending_reel(post))

    def _rank(row: dict[str, Any]) -> tuple[int, float]:
        eng = row.get("engagement") if isinstance(row.get("engagement"), dict) else {}
        likes = safe_int(eng.get("likes")) or 0
        published = _parse_published_at(row.get("publishedAt"))
        ts = published.timestamp() if published else 0.0
        return likes, ts

    reels.sort(key=_rank, reverse=True)
    out = reels[:limit]
    if not out:
        return None
    log.info(
        "ig_trending_native_ok",
        country=country,
        geo=geo,
        n=len(out),
        hydrated=len(posts),
        reels=len(reels),
    )
    return out


async def enrich_posts_from_author_feeds(
    posts: list[dict[str, Any]], *, max_authors: int = 12
) -> list[dict[str, Any]]:
    """Backfill ``engagement.views`` + author followers/postCount.

    Polaris media info (used by hydrate) returns real ``like_count`` but hides
    play counts logged-out. The owner's ``api/v1`` feed still exposes
    ``play_count`` / ``ig_play_count`` for recent posts — merge those in when
    the hashtag hit is still on the creator's timeline. Profile lookup fills
    ``author.followers`` / ``author.postCount`` for campaign sizing.
    """
    from app.services.instagram_decodo import strip_null_post_fields

    if not posts:
        return posts

    # username -> author id (prefer id from hydrated media)
    authors: list[tuple[str, str]] = []
    seen: set[str] = set()
    for post in posts:
        author = post.get("author") if isinstance(post.get("author"), dict) else {}
        username = safe_str(author.get("username"))
        uid = safe_str(author.get("id"))
        if not username or username in seen:
            continue
        seen.add(username)
        authors.append((username, uid or ""))
        if len(authors) >= max_authors:
            break

    if not authors:
        return posts

    sem = asyncio.Semaphore(3)
    play_by_code: dict[str, tuple[int | None, int | None]] = {}
    stats_by_user: dict[str, dict[str, Any]] = {}

    def _stats_from_profile(profile: dict[str, Any]) -> dict[str, Any]:
        return {
            "followers": _edge_count(
                profile.get("edge_followed_by") or profile.get("follower_count")
            ),
            "postCount": _edge_count(
                profile.get("edge_owner_to_timeline_media") or profile.get("media_count")
            ),
            "private": profile.get("is_private"),
            "id": safe_str(profile.get("id") or profile.get("pk")),
        }

    async def _one(username: str, user_id: str) -> None:
        async with sem:
            # Decodo HTML profile is the reliable path under WPI 429s; run it
            # alongside the feed so hashtag search stays within a few seconds.
            profile_task = asyncio.create_task(fetch_web_profile_info_via_decodo(username))
            uid = user_id
            if uid:
                page = await fetch_user_feed_page(uid, count=33)
                if page:
                    for item in page[0]:
                        code = safe_str(item.get("code"))
                        if not code:
                            continue
                        play_by_code[code] = (
                            safe_int(item.get("play_count")),
                            safe_int(item.get("ig_play_count") or item.get("view_count")),
                        )
            profile, _missing = await profile_task
            if isinstance(profile, dict):
                stats = _stats_from_profile(profile)
                stats_by_user[username] = stats
                if not uid and stats.get("id"):
                    uid = stats["id"]
                    page = await fetch_user_feed_page(uid, count=33)
                    if page:
                        for item in page[0]:
                            code = safe_str(item.get("code"))
                            if not code:
                                continue
                            play_by_code[code] = (
                                safe_int(item.get("play_count")),
                                safe_int(item.get("ig_play_count") or item.get("view_count")),
                            )
            elif username not in stats_by_user:
                # Last resort — full WPI ladder (slow / rate-limited).
                profile = await fetch_web_profile_info(username)
                if isinstance(profile, dict):
                    stats_by_user[username] = _stats_from_profile(profile)

    await asyncio.gather(*[_one(u, i) for u, i in authors])

    def _post_shortcode(post: dict[str, Any]) -> str | None:
        # Hydrated posts use shortcode as id; GraphQL nodes often use numeric id.
        code = safe_str(post.get("id") or post.get("shortcode") or post.get("shortCode"))
        if code and not code.isdigit() and code in play_by_code:
            return code
        url = safe_str(post.get("url")) or ""
        m = re.search(r"/(?:reel|p|tv)/([^/?#]+)/?", url, re.I)
        if m:
            return m.group(1)
        return code if code and code in play_by_code else None

    for post in posts:
        code = _post_shortcode(post)
        engagement = post.get("engagement") if isinstance(post.get("engagement"), dict) else {}
        # Prefer feed play counts whenever available — GraphQL video_view_count
        # often undercounts Reels and can sit below like_count.
        if code and code in play_by_code:
            plays, ig_plays = play_by_code[code]
            feed_views = plays or ig_plays
            likes = engagement.get("likes")
            if feed_views is not None:
                engagement["views"] = feed_views
            if (
                plays is not None
                and ig_plays is not None
                and plays != ig_plays
            ):
                engagement["plays"] = plays
            if likes is not None and engagement.get("views") is not None and likes > engagement["views"]:
                engagement["views"] = None
            post["engagement"] = engagement
        author = post.get("author") if isinstance(post.get("author"), dict) else {}
        username = safe_str(author.get("username"))
        stats = stats_by_user.get(username or "")
        if stats:
            if author.get("followers") is None and stats.get("followers") is not None:
                author["followers"] = stats["followers"]
            if author.get("postCount") is None and stats.get("postCount") is not None:
                author["postCount"] = stats["postCount"]
            if author.get("private") is None and stats.get("private") is not None:
                author["private"] = stats["private"]
            post["author"] = author
        mentions = post.get("mentions")
        if isinstance(mentions, list):
            post["mentions"] = dedupe_preserve(mentions)
        strip_null_post_fields(post)
    return posts


async def hashtag_posts_native(
    tag: str, *, limit: int = 20, reels_only: bool = False
) -> list[dict[str, Any]] | None:
    """Hashtag Explore via Decodo headless + Polaris hydrate (graphql fallthrough)."""
    name = (tag or "").lstrip("#").strip()
    if not name:
        return None
    # Pull extra shortcodes when filtering to reels — many tag grids mix photos.
    fetch_n = min(200, limit * 3 if reels_only else limit)
    page_url = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(name)}/"
    codes = await fetch_shortcodes_via_decodo(page_url, limit=fetch_n)
    if not codes:
        return None
    posts = await hydrate_shortcodes(codes, limit=fetch_n)
    if not posts:
        return None
    if reels_only:
        posts = [
            p
            for p in posts
            if (p.get("postType") == "Video")
            or (safe_str(p.get("productType")) in {"clips", "reel", "reels"})
            or bool(p.get("videoUrl"))
        ]
    posts = posts[:limit]
    if not posts:
        return None
    return await enrich_posts_from_author_feeds(posts)
