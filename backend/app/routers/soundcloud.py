"""SoundCloud public data endpoints backed by native api-v2 (Apify fallthrough)."""

from __future__ import annotations

import base64
import json
import math
from typing import Any
from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.cache_params import CACHE_MAX_AGE_DESC, resolve_cache_options
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services import soundcloud_native as native
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

RATE = 1.4
CREDIT_ARTIST_TRACKS = 2  # native api-v2; flat fee, our cost ~$0


def _encode_tracks_cursor(user_id: str | int, offset: str) -> str:
    """Opaque nextCursor — never expose api-v2 next_href or bare user id."""
    payload = json.dumps(
        {"u": str(user_id), "o": offset},
        separators=(",", ":"),
    ).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def _decode_tracks_cursor(cursor: str | None, *, expected_user_id: str) -> str | None:
    """Return SoundCloud offset for ``expected_user_id``, or raise 400.

    Accepts opaque tokens. Legacy raw ``next_href`` URLs are tolerated once
    (offset extracted; host/path ignored) so in-flight clients keep paging.
    """
    raw = (cursor or "").strip()
    if not raw:
        return None

    # Legacy leak: full api-v2 URL — extract offset only, never fetch the URL.
    if raw.startswith("http"):
        parsed = urlparse(raw)
        host = (parsed.netloc or "").lower()
        if "soundcloud.com" not in host:
            raise HTTPException(
                status_code=400,
                detail="Invalid cursor. Pass nextCursor from the previous response.",
            )
        offset = native.offset_from_next_href(raw)
        if not offset:
            # Some old cursors used the URL as a pass-through without offset=
            qs = parse_qs(parsed.query)
            vals = qs.get("offset") or []
            offset = vals[0] if vals else None
        if not offset:
            raise HTTPException(
                status_code=400,
                detail="Invalid cursor. Pass nextCursor from the previous response.",
            )
        return offset

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
    uid = safe_str(data.get("u"))
    offset = safe_str(data.get("o"))
    if not uid or not offset:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass nextCursor from the previous response.",
        )
    if uid != str(expected_user_id):
        raise HTTPException(
            status_code=400,
            detail="Cursor does not match this artist. Start a new request without cursor.",
        )
    return offset


def _scaled(n: int, rate: float = RATE, minimum: int = 2) -> int:
    if n <= 0:
        return 0

    return max(minimum, math.ceil(n * rate))


def _profile_url(value: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "soundcloud":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "soundcloud", "https://soundcloud.com/artist"),
        )
    value = (value or "").strip().rstrip("/")
    if value.startswith("http"):
        return value
    return f"https://soundcloud.com/{value.lstrip('@')}"


_TRACK_OMIT_IF_EMPTY = frozenset(
    {
        "description",
        "genre",
        "releaseDate",
        "license",
        "isrc",
        "waveformUrl",
        "artwork",
        "tags",
        "streamUrl",
        "hlsUrl",
        "downloadUrl",
        "mediaUrlsExpireAt",
        "artist",
    }
)


def _artist_ref(user: dict[str, Any], *, fallback_url: str | None = None) -> dict[str, Any] | None:
    """Nested artist card for track rows — joinable into /soundcloud/artist."""
    if not isinstance(user, dict) or not user:
        return None
    aid = safe_str(user.get("id") or user.get("userId"))
    handle = safe_str(user.get("permalink"))
    name = safe_str(
        user.get("username") or user.get("fullName") or user.get("full_name") or user.get("name")
    )
    url = safe_str(
        user.get("permalinkUrl")
        or user.get("permalink_url")
        or (f"https://soundcloud.com/{handle}" if handle else fallback_url)
    )
    out = {
        "id": aid,
        "handle": handle,
        "name": name,
        "url": url,
        "avatar": safe_str(user.get("avatarUrl") or user.get("avatar_url")),
        "followers": safe_int(
            user.get("followersCount") or user.get("followers_count") or user.get("followers")
        ),
        "verified": bool(user.get("verified")),
    }
    return {k: v for k, v in out.items() if v not in (None, "", [])}


def _track(
    item: dict[str, Any],
    *,
    media: dict[str, Any] | None = None,
    include_artist: bool = True,
) -> dict[str, Any]:
    user = item.get("user") or item.get("artist") or item.get("publisher") or {}
    if not isinstance(user, dict):
        user = {}
    artist = _artist_ref(user) if include_artist else None
    media = media or {}
    out: dict[str, Any] = {
        "platform": "soundcloud",
        "id": safe_str(item.get("id") or item.get("trackId")),
        "url": safe_str(item.get("url") or item.get("permalinkUrl") or item.get("permalink_url")),
        "title": safe_str(item.get("title") or item.get("name")),
        "description": safe_str(item.get("description")),
        "genre": safe_str(item.get("genre")),
        "artist": artist,
        "durationMs": safe_int(item.get("duration") or item.get("durationMs")),
        "plays": safe_int(item.get("playbackCount") or item.get("playback_count") or item.get("plays")),
        "likes": safe_int(item.get("likesCount") or item.get("likes_count") or item.get("likes")),
        "reposts": safe_int(item.get("repostsCount") or item.get("reposts_count")),
        "downloads": safe_int(item.get("downloadCount") or item.get("download_count")),
        "comments": safe_int(item.get("commentCount") or item.get("comment_count") or item.get("comments")),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created_at") or item.get("publishedAt")),
        "releaseDate": safe_str(item.get("releaseDate") or item.get("release_date")),
        "license": safe_str(item.get("license")),
        "isrc": safe_str(item.get("isrc")),
        # Permission flags from SoundCloud (not a guarantee we minted a URL).
        "downloadable": bool(item.get("downloadable")),
        "streamable": bool(item.get("streamable")),
        "streamUrl": safe_str(media.get("streamUrl")),
        "hlsUrl": safe_str(media.get("hlsUrl")),
        "downloadUrl": safe_str(media.get("downloadUrl")),
        "mediaUrlsExpireAt": safe_str(media.get("mediaUrlsExpireAt")),
        "waveformUrl": safe_str(item.get("waveformUrl") or item.get("waveform_url")),
        "artwork": safe_str(item.get("artworkUrl") or item.get("artwork_url") or item.get("thumbnail")),
        "tags": [t for t in (item.get("tagList") or []) if isinstance(t, str)],
    }
    for key in _TRACK_OMIT_IF_EMPTY:
        if key in out and out[key] in (None, "", []):
            out.pop(key, None)
    return out


def _subscription_tier(user: dict[str, Any], badges: dict[str, bool] | None) -> str:
    """Canonical plan: pro-unlimited | pro | mid-tier | free."""
    sub = user.get("creator_subscription") or user.get("creatorSubscription")
    if not isinstance(sub, dict):
        subs = user.get("creator_subscriptions") or user.get("creatorSubscriptions")
        if isinstance(subs, list) and subs and isinstance(subs[0], dict):
            sub = subs[0]
    product_id = ""
    if isinstance(sub, dict):
        product = sub.get("product") if isinstance(sub.get("product"), dict) else {}
        product_id = (safe_str(product.get("id")) or "").lower()
    if "pro-unlimited" in product_id or "pro_unlimited" in product_id:
        return "pro-unlimited"
    if product_id.endswith("-pro") or product_id == "creator-pro" or product_id == "pro":
        return "pro"
    if "mid" in product_id:
        return "mid-tier"
    if badges:
        if badges.get("proUnlimited"):
            return "pro-unlimited"
        if badges.get("pro"):
            return "pro"
        if badges.get("creatorMidTier"):
            return "mid-tier"
    return "free"


def _badges_flags(raw: Any) -> dict[str, bool] | None:
    """Raw badge flags without verified (verified is top-level only)."""
    if not isinstance(raw, dict) or not raw:
        return None
    out = {
        "pro": bool(raw.get("pro")),
        "creatorMidTier": bool(raw.get("creator_mid_tier") or raw.get("creatorMidTier")),
        "proUnlimited": bool(raw.get("pro_unlimited") or raw.get("proUnlimited")),
    }
    # Omit if everything is false — subscriptionTier already says "free".
    if not any(out.values()):
        return None
    return out


def _artist(
    item: dict[str, Any],
    url: str,
    *,
    external_links: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    user = item.get("user") or item.get("artist") or item
    if not isinstance(user, dict):
        user = {}
    badge_flags = _badges_flags(user.get("badges"))
    verified = bool(user.get("verified"))
    if isinstance(user.get("badges"), dict) and "verified" in user["badges"]:
        verified = bool(user["badges"].get("verified") or user.get("verified"))
    handle = safe_str(user.get("permalink"))
    username = safe_str(user.get("username") or handle)
    out: dict[str, Any] = {
        "platform": "soundcloud",
        "id": safe_str(user.get("id") or user.get("userId")),
        "handle": handle,
        "url": safe_str(user.get("permalinkUrl") or user.get("permalink_url") or url),
        "username": username,
        "name": safe_str(user.get("fullName") or user.get("full_name") or user.get("name") or username),
        "description": safe_str(user.get("description") or user.get("bio")),
        "avatar": safe_str(user.get("avatarUrl") or user.get("avatar_url")),
        "city": safe_str(user.get("city")),
        "countryCode": safe_str(user.get("countryCode") or user.get("country_code")),
        "verified": verified,
        "subscriptionTier": _subscription_tier(user, badge_flags),
        "followers": safe_int(user.get("followersCount") or user.get("followers_count")),
        "followings": safe_int(user.get("followingsCount") or user.get("followings_count")),
        "trackCount": safe_int(user.get("trackCount") or user.get("track_count")),
        "playlistCount": safe_int(user.get("playlistCount") or user.get("playlist_count")),
        "likesCount": safe_int(user.get("likesCount") or user.get("likes_count")),
        "createdAt": safe_str(user.get("createdAt") or user.get("created_at")),
        "lastModified": safe_str(user.get("lastModified") or user.get("last_modified")),
        "externalLinks": external_links or [],
    }
    for key in (
        "description",
        "city",
        "countryCode",
        "createdAt",
        "lastModified",
        "handle",
        "name",
    ):
        if out.get(key) in (None, "", []):
            out.pop(key, None)
    if not out.get("externalLinks"):
        out.pop("externalLinks", None)
    return out


@router.get(
    "/artist",
    summary="SoundCloud artist profile",
    description=(
        "SoundCloud artist as clean JSON: id, handle (permalink slug), username, "
        "name, description, avatar, city/countryCode, verified, subscriptionTier "
        "(pro-unlimited|pro|mid-tier|free), followers/followings/trackCount/"
        "playlistCount/likesCount, externalLinks[{url,network,title}], createdAt "
        "when SoundCloud exposes it, and lastModified. Flat 1 credit. Accepts "
        "cache / cacheMaxAge."
    ),
)
async def artist(
    url: str = Query(..., description="SoundCloud artist URL or username"),
    cache: bool = Query(
        False,
        description=(
            "Set true to serve from the response cache (default TTL). Default false — "
            "always fetch fresh. Prefer cacheMaxAge when you need 1d–30d freshness control."
        ),
    ),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    profile = _profile_url(url)
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    async with billed_call(
        caller=caller,
        endpoint="/v1/soundcloud/artist",
        platform="soundcloud",
        resource_url=profile,
        base_credits=1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            resolved = await native.resolve(profile)
            if isinstance(resolved, dict) and resolved.get("kind") == "user":
                links = await native.user_web_profiles(resolved)
                ctx["source"] = "direct"
                return _artist(resolved, profile, external_links=links)

            settings = get_settings()
            try:
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_SOUNDCLOUD,
                    {"mode": "userUrl", "startUrls": [profile], "maxResults": 1, "includeUserDetails": True},
                    max_items=1,
                )
            except ApifyError:
                items = []
            item = items[0] if items and isinstance(items[0], dict) else None
            if not item:
                raise HTTPException(status_code=404, detail="SoundCloud artist not found")
            ctx["source"] = "apify"
            links: list[dict[str, Any]] = []
            uid = item.get("id") or (item.get("user") or {}).get("id")
            if uid:
                links = await native.user_web_profiles(uid)
            return _artist(item, profile, external_links=links)

        data = await cached_or_run(
            "soundcloud.artist",
            {"url": profile, "v": 6, "cacheMaxAge": cacheMaxAge},
            _run,
            ctx,
            ttl=ttl,
            use_cache=use_cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/artist-tracks",
    summary="SoundCloud artist tracks (cursor-paginated)",
    description=(
        "Tracks for one SoundCloud artist as clean JSON. Track rows match "
        "/soundcloud/track (title, plays/likes/…, license, artwork, tags) — "
        "without per-row artist{} (single-artist list). Top-level artistId + "
        "artist{} join to /soundcloud/artist. Opaque nextCursor (not an "
        "upstream URL). Flat 2 credits per call."
    ),
)
async def artist_tracks(
    url: str = Query(..., description="SoundCloud artist URL or username"),
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor from the previous response's nextCursor. "
            "Leave empty for the first page. Do not edit or invent values."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    profile = _profile_url(url)
    # Flat fee: native api-v2 is ~$0; Apify fallback is rare and covered by
    # the same 2-credit charge.
    async with billed_call(
        caller=caller,
        endpoint="/v1/soundcloud/artist-tracks",
        platform="soundcloud",
        resource_url=profile,
        base_credits=CREDIT_ARTIST_TRACKS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            resolved = await native.resolve(profile)
            if isinstance(resolved, dict) and resolved.get("kind") == "user" and resolved.get("id"):
                artist_id = safe_str(resolved["id"]) or str(resolved["id"])
                offset = _decode_tracks_cursor(cursor, expected_user_id=artist_id)
                rows, next_offset = await native.user_tracks(
                    resolved["id"], limit, offset=offset
                )
                if rows:
                    tracks = [
                        _track(native.prep_track_row(r), include_artist=False)
                        for r in rows
                    ][:limit]
                    next_cursor = (
                        _encode_tracks_cursor(artist_id, next_offset)
                        if next_offset
                        else None
                    )
                    artist = _artist_ref(resolved, fallback_url=profile)
                    ctx["source"] = "direct"
                    return {
                        "platform": "soundcloud",
                        "artistId": artist_id,
                        "artistUrl": safe_str(
                            (artist or {}).get("url") if artist else None
                        )
                        or profile,
                        "artist": artist,
                        "totalReturned": len(tracks),
                        "nextCursor": next_cursor,
                        "hasMore": next_cursor is not None,
                        "tracks": tracks,
                    }

            if cursor:
                raise HTTPException(
                    status_code=400,
                    detail="Cursor pagination is only available on the native SoundCloud path. Start a new request without cursor.",
                )
            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SOUNDCLOUD,
                {"mode": "userUrl", "startUrls": [profile], "maxResults": limit, "includeUserDetails": True},
                max_items=limit,
            )
            # includeUserDetails prepends the artist's user row to the dataset;
            # keep only real tracks (they always carry a title).
            track_items = [i for i in items if i.get("title") or i.get("name")]
            tracks = [
                _track(native.prep_track_row(i), include_artist=False) for i in track_items
            ][:limit]
            artist: dict[str, Any] | None = None
            artist_id: str | None = None
            for i in items:
                if isinstance(i, dict) and not (i.get("title") or i.get("name")):
                    artist = _artist_ref(i, fallback_url=profile)
                    artist_id = (artist or {}).get("id") if artist else None
                    break
            if not artist and track_items:
                user = track_items[0].get("user") if isinstance(track_items[0], dict) else None
                if isinstance(user, dict):
                    artist = _artist_ref(user, fallback_url=profile)
                    artist_id = (artist or {}).get("id") if artist else None
            ctx["source"] = "apify"
            out: dict[str, Any] = {
                "platform": "soundcloud",
                "artistUrl": profile,
                "totalReturned": len(tracks),
                "nextCursor": None,
                "hasMore": False,
                "tracks": tracks,
            }
            if artist_id:
                out["artistId"] = artist_id
            if artist:
                out["artist"] = artist
                if artist.get("url"):
                    out["artistUrl"] = artist["url"]
            return out

        data = await cached_or_run(
            "soundcloud.artist-tracks",
            {"url": profile, "limit": limit, "cursor": cursor or "", "v": 10},
            _run,
            ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/track",
    summary="SoundCloud track details",
    description=(
        "SoundCloud track as clean JSON: title, artist{id,handle,name,url,avatar,"
        "followers,verified}, plays/likes/reposts/comments/downloads, license, "
        "genre/tags, publishedAt, streamable/downloadable permission flags, and "
        "when the public api-v2 allows it — streamUrl (progressive MP3), hlsUrl, "
        "downloadUrl, plus mediaUrlsExpireAt for signed CDN links. waveformUrl is "
        "the waveform JSON, not audio. Flat 1 credit. Accepts cache / cacheMaxAge."
    ),
)
async def track(
    url: str = Query(..., description="SoundCloud track URL"),
    cache: bool = Query(
        False,
        description=(
            "Set true to serve from the response cache (default TTL). Default false — "
            "always fetch fresh. Prefer cacheMaxAge when you need 1d–30d freshness control."
        ),
    ),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    detected = detect_url_platform(url)
    if detected and detected != "soundcloud":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "soundcloud", "https://soundcloud.com/artist/track"),
        )
    if "soundcloud.com/" not in url:
        raise HTTPException(
            status_code=400,
            detail="Invalid SoundCloud track URL. Pass a SoundCloud URL like https://soundcloud.com/artist/track.",
        )
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    async with billed_call(
        caller=caller,
        endpoint="/v1/soundcloud/track",
        platform="soundcloud",
        resource_url=url,
        base_credits=1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            resolved = await native.resolve(url)
            if isinstance(resolved, dict) and resolved.get("kind") == "track":
                row = native.prep_track_row(resolved)
                media = await native.resolve_media_urls(row)
                ctx["source"] = "direct"
                return _track(row, media=media)

            settings = get_settings()
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SOUNDCLOUD,
                {"mode": "trackUrl", "startUrls": [url], "maxResults": 1, "includeUserDetails": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="SoundCloud track not found")
            row = native.prep_track_row(items[0])
            media = await native.resolve_media_urls(row)
            ctx["source"] = "apify"
            return _track(row, media=media)

        data = await cached_or_run(
            "soundcloud.track",
            {"url": url, "v": 6, "cacheMaxAge": cacheMaxAge},
            _run,
            ctx,
            ttl=ttl,
            use_cache=use_cache,
        )
        return ApiResponse(data=data)
