"""Spotify public catalog endpoints backed by Apify actors."""

from __future__ import annotations

import math
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

RATE = 1.15


def _scaled(n: int, rate: float = RATE, minimum: int = 2) -> int:
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _url(value: str, kind: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "spotify":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "spotify", f"https://open.spotify.com/{kind}/ID"),
        )
    value = (value or "").strip()
    if value.startswith("spotify:") or "open.spotify.com/" in value:
        return value
    return f"https://open.spotify.com/{kind}/{value}"


def _names(items: Any) -> list[str]:
    if isinstance(items, dict):
        items = items.get("items")
    if isinstance(items, str):
        return [part.strip() for part in items.split(",") if part.strip()]
    if not isinstance(items, list):
        return []
    out: list[str] = []
    for item in items:
        if isinstance(item, dict):
            name = item.get("name") or (item.get("profile") or {}).get("name")
            if name:
                out.append(str(name))
        elif isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _image(item: dict[str, Any]) -> str | None:
    header = item.get("headerImage")
    header_sources = (header.get("data") or {}).get("sources") if isinstance(header, dict) else None
    cover = item.get("coverArt")
    cover_sources = cover.get("sources") if isinstance(cover, dict) else None
    images = (
        item.get("images")
        or item.get("visuals", {}).get("avatarImage", {}).get("sources")
        or cover_sources
        or header_sources
    )
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict):
            return safe_str(first.get("url"))
    return safe_str(item.get("image") or item.get("thumbnail") or item.get("thumbnailUrl"))


def _year_of(value: Any) -> int | None:
    if isinstance(value, dict):
        value = value.get("year") or value.get("isoString")
    match = re.search(r"\b(\d{4})\b", str(value or ""))
    return safe_int(match.group(1)) if match else None


def _episodes_v2(item: dict[str, Any]) -> dict[str, Any]:
    """Unwrap the podcast's episodes GraphQL envelope
    (episodes.data.podcastUnionV2.episodesV2)."""
    block = item.get("episodes")
    if not isinstance(block, dict):
        return {}
    union = (block.get("data") or {}).get("podcastUnionV2") if isinstance(block.get("data"), dict) else None
    v2 = (union or {}).get("episodesV2")
    if isinstance(v2, dict):
        return v2
    return block


# Fields that never apply to a given entity type — omit rather than null.
_OMIT_BY_KIND: dict[str, frozenset[str]] = {
    "artist": frozenset(
        {"artists", "album", "durationMs", "playCount", "releaseYear", "totalTracks", "totalEpisodes"}
    ),
    "track": frozenset({"followers", "monthlyListeners", "totalTracks", "totalEpisodes"}),
    "album": frozenset(
        {"album", "durationMs", "playCount", "followers", "monthlyListeners", "totalEpisodes"}
    ),
    "podcast": frozenset(
        {"album", "durationMs", "playCount", "followers", "monthlyListeners", "releaseYear", "totalTracks"}
    ),
    # Episode creators/play counts are almost never present in this actor payload.
    "episode": frozenset(
        {
            "album",
            "artists",
            "playCount",
            "followers",
            "monthlyListeners",
            "totalTracks",
            "totalEpisodes",
        }
    ),
}

# Drop when empty so sparse search/details payloads don't ship noise keys.
_OMIT_IF_EMPTY = frozenset(
    {
        "description",
        "artists",
        "album",
        "durationMs",
        "playCount",
        "followers",
        "monthlyListeners",
        "releaseYear",
        "totalTracks",
        "totalEpisodes",
        "image",
    }
)


def _strip_empty_keys(value: Any) -> Any:
    """Drop null/empty keys from actor raw payloads (search often ships null dates)."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, child in value.items():
            cleaned = _strip_empty_keys(child)
            if cleaned in (None, "", []):
                continue
            out[key] = cleaned
        return out
    if isinstance(value, list):
        return [_strip_empty_keys(child) for child in value]
    return value


def _normalize(item: dict[str, Any], kind: str) -> dict[str, Any]:
    stats = item.get("stats") or {}
    duration = item.get("duration") or {}
    album = item.get("albumOfTrack") or item.get("album") or {}
    tracks = item.get("tracksV2") or item.get("tracks") or item.get("content") or {}
    episodes = _episodes_v2(item) or item.get("items") or tracks

    if isinstance(duration, dict):
        duration_ms = safe_int(duration.get("totalMilliseconds"))
    else:
        duration_ms = safe_int(duration)
    duration_ms = duration_ms or safe_int(item.get("durationMs"))

    release_year = (
        _year_of(item.get("date"))
        or _year_of(item.get("releaseDate"))
        or (_year_of(album.get("date")) if isinstance(album, dict) else None)
    )

    description = safe_str(item.get("description") or item.get("subtitle"))
    biography = item.get("biography")
    if not description and isinstance(biography, dict):
        description = safe_str(biography.get("text"))

    artists = _names(item.get("artists"))
    if not artists:
        artists = _names(item.get("firstArtist")) + _names(item.get("otherArtists"))
    if not artists:
        publisher = item.get("publisher")
        if isinstance(publisher, dict) and publisher.get("name"):
            artists = [str(publisher["name"])]

    sharing = item.get("sharingInfo") if isinstance(item.get("sharingInfo"), dict) else {}

    out: dict[str, Any] = {
        "platform": "spotify",
        "type": kind,
        "uri": safe_str(item.get("uri") or item.get("id")),
        "url": safe_str(item.get("url") or item.get("externalUrl") or item.get("shareUrl") or sharing.get("shareUrl")),
        "name": safe_str(item.get("name") or item.get("title")),
        "description": description,
        "artists": artists,
        "album": safe_str(album.get("name") if isinstance(album, dict) else None) or safe_str(item.get("albumName")),
        "durationMs": duration_ms,
        "playCount": safe_int(item.get("playcount") or item.get("playCount")),
        "followers": safe_int(stats.get("followers") or item.get("followers")),
        "monthlyListeners": safe_int(stats.get("monthlyListeners") or item.get("monthlyListeners")),
        "releaseYear": release_year,
        "image": _image(item)
        or safe_str(item.get("albumArt"))
        or (_image(album) if isinstance(album, dict) else None),
        "totalTracks": safe_int(tracks.get("totalCount") if isinstance(tracks, dict) else item.get("totalTracks")),
        "totalEpisodes": safe_int(episodes.get("totalCount") if isinstance(episodes, dict) else item.get("totalEpisodes")),
        "raw": _strip_empty_keys(item),
    }
    for key in _OMIT_BY_KIND.get(kind, frozenset()):
        out.pop(key, None)
    for key in _OMIT_IF_EMPTY:
        if key in out and out[key] in (None, "", []):
            out.pop(key, None)
    return out


async def _oembed_details(kind: str, uri: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
        resp = await client.get("https://open.spotify.com/oembed", params={"url": uri})
    if resp.status_code >= 400:
        raise HTTPException(status_code=404, detail="Spotify item not found")
    item = resp.json()
    payload = dict(item)
    payload.update(
        {
            "uri": uri,
            "url": uri,
            "name": item.get("title"),
            "image": item.get("thumbnail_url"),
        }
    )
    return _normalize(payload, kind)


async def _details(kind: str, uri: str, limit: int | None = None) -> dict[str, Any]:
    settings = get_settings()
    # The actor's *_get_limit fields require a minimum of 1 - passing 0 fails
    # input validation and every call used to drop to the bare oembed fallback.
    album_limit = max(1, limit or 1) if kind == "album" else 1
    podcast_limit = max(1, limit or 1) if kind == "podcast" else 1
    run_input: dict[str, Any] = {
        "getDetailsType": kind,
        "spotifyUris": [uri],
        "proxyCountry": "US",
        "albums_get_offset": 0,
        "albums_get_limit": album_limit,
        "podcasts_get_offset": 0,
        "podcasts_get_limit": podcast_limit,
        "podcasts_includeRecommended": False,
        "episodes_includeRecommended": False,
    }
    try:
        items = await get_apify().run_actor_sync(
            settings.APIFY_ACTOR_SPOTIFY_DETAILS,
            run_input,
            max_items=1,
        )
    except (ApifyError, httpx.HTTPError):
        return await _oembed_details(kind, uri)
    if not items or items[0].get("error"):
        return await _oembed_details(kind, uri)
    return _normalize(items[0], kind)


@router.get("/artist", summary="Spotify artist details")
async def artist(
    url: str = Query(..., description="Spotify artist URL, URI, or ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "artist")
    async with billed_call(caller=caller, endpoint="/v1/spotify/artist", platform="spotify", resource_url=uri, base_credits=6) as ctx:
        data = await cached_or_run("spotify.artist", {"uri": uri, "v": 6}, lambda: _details("artist", uri), ctx, ttl=get_settings().CACHE_TTL_STATIC, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/track", summary="Spotify track details")
async def track(
    url: str = Query(..., description="Spotify track URL, URI, or ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "track")
    async with billed_call(caller=caller, endpoint="/v1/spotify/track", platform="spotify", resource_url=uri, base_credits=6) as ctx:
        data = await cached_or_run("spotify.track", {"uri": uri, "v": 7}, lambda: _details("track", uri), ctx, ttl=get_settings().CACHE_TTL_STATIC, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/album", summary="Spotify album details")
async def album(
    url: str = Query(..., description="Spotify album URL, URI, or ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "album")
    async with billed_call(caller=caller, endpoint="/v1/spotify/album", platform="spotify", resource_url=uri, base_credits=6) as ctx:
        data = await cached_or_run("spotify.album", {"uri": uri, "v": 6}, lambda: _details("album", uri, limit=1), ctx, ttl=get_settings().CACHE_TTL_STATIC, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/podcast", summary="Spotify podcast/show details")
async def podcast(
    url: str = Query(..., description="Spotify show/podcast URL, URI, or ID"),
    limit: int = Query(20, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "show")
    async with billed_call(caller=caller, endpoint="/v1/spotify/podcast", platform="spotify", resource_url=uri, base_credits=6) as ctx:
        data = await cached_or_run("spotify.podcast", {"uri": uri, "limit": limit, "v": 6}, lambda: _details("podcast", uri, limit), ctx, ttl=get_settings().CACHE_TTL_STATIC, use_cache=cache)
        return ApiResponse(data=data)


@router.get("/podcast-episodes", summary="Spotify podcast episodes")
async def podcast_episodes(
    url: str = Query(..., description="Spotify show/podcast URL, URI, or ID"),
    limit: int = Query(20, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "show")
    cost = _scaled(limit)
    async with billed_call(caller=caller, endpoint="/v1/spotify/podcast-episodes", platform="spotify", resource_url=uri, base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _details("podcast", uri, limit)
            raw = data.get("raw") or {}
            episodes = _episodes_v2(raw) or raw.get("items") or raw.get("content") or {}
            items = episodes.get("items") if isinstance(episodes, dict) else episodes
            rows: list[dict[str, Any]] = []
            for entry in items if isinstance(items, list) else []:
                if not isinstance(entry, dict):
                    continue
                # episodesV2 wraps each episode as {entity: {data: {...}}}
                entity = (entry.get("entity") or {}).get("data") if isinstance(entry.get("entity"), dict) else None
                rows.append(entity if isinstance(entity, dict) else entry)
            normalized = [_normalize(i, "episode") for i in rows]
            return {"platform": "spotify", "podcast": data, "totalReturned": len(normalized[:limit]), "episodes": normalized[:limit]}

        data = await cached_or_run("spotify.podcast-episodes", {"uri": uri, "limit": limit, "v": 6}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["episodes"]))
        return ApiResponse(data=data)


@router.get("/search", summary="Search Spotify")
async def search(
    q: str = Query(..., min_length=2),
    type: str = Query("tracks", pattern="^(tracks|albums|artists|podcasts|episodes)$"),
    limit: int = Query(20, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit)
    async with billed_call(caller=caller, endpoint="/v1/spotify/search", platform="spotify", resource_url=f"spotify:search:{q}", base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            if type in ("tracks", "albums", "artists"):
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_SPOTIFY_SEARCH,
                    {"mode": "search", "searchTerms": [q], "searchType": type, "maxResults": limit},
                    max_items=limit,
                )
            else:
                # Podcast/episode search is only offered by the apiharvest
                # all-types actor.
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_SPOTIFY_SEARCH_ALL,
                    {
                        "searchType": "searchPodcasts" if type == "podcasts" else "searchFullEpisodes",
                        "keyword": [q],
                        "proxyCountry": "US",
                        "podcasts_search_limit": limit,
                        "episodes_search_limit": limit,
                    },
                    max_items=limit,
                )
            kind = type[:-1] if type.endswith("s") else type
            results = [_normalize(i, kind) for i in items[:limit] if not i.get("error")]
            return {"platform": "spotify", "query": q, "type": type, "totalReturned": len(results), "results": results}

        data = await cached_or_run("spotify.search", {"q": q, "type": type, "limit": limit, "v": 6}, _run, ctx, use_cache=cache)
        ctx["credits_override"] = _scaled(len(data["results"]))
        return ApiResponse(data=data)
