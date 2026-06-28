"""Spotify public catalog endpoints backed by Apify actors."""

from __future__ import annotations

import math
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
    if not isinstance(items, list):
        return []
    out: list[str] = []
    for item in items:
        if isinstance(item, dict):
            name = item.get("name") or (item.get("profile") or {}).get("name")
            if name:
                out.append(str(name))
    return out


def _image(item: dict[str, Any]) -> str | None:
    images = item.get("images") or item.get("visuals", {}).get("avatarImage", {}).get("sources")
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict):
            return safe_str(first.get("url"))
    return safe_str(item.get("image") or item.get("thumbnail") or item.get("thumbnailUrl"))


def _normalize(item: dict[str, Any], kind: str) -> dict[str, Any]:
    stats = item.get("stats") or {}
    duration = item.get("duration") or {}
    album = item.get("albumOfTrack") or item.get("album") or {}
    tracks = item.get("tracks") or item.get("content") or {}
    episodes = item.get("episodes") or item.get("items") or tracks
    return {
        "platform": "spotify",
        "type": kind,
        "uri": safe_str(item.get("uri") or item.get("id")),
        "url": safe_str(item.get("url") or item.get("externalUrl") or item.get("shareUrl")),
        "name": safe_str(item.get("name") or item.get("title")),
        "description": safe_str(item.get("description") or item.get("subtitle")),
        "artists": _names(item.get("artists")),
        "album": safe_str(album.get("name") if isinstance(album, dict) else None),
        "durationMs": safe_int(duration.get("totalMilliseconds") if isinstance(duration, dict) else item.get("durationMs")),
        "playCount": safe_int(item.get("playcount") or item.get("playCount")),
        "followers": safe_int(stats.get("followers") or item.get("followers")),
        "monthlyListeners": safe_int(stats.get("monthlyListeners")),
        "releaseYear": safe_int((item.get("date") or {}).get("year") if isinstance(item.get("date"), dict) else None),
        "image": _image(item),
        "totalTracks": safe_int(tracks.get("totalCount") if isinstance(tracks, dict) else item.get("totalTracks")),
        "totalEpisodes": safe_int(episodes.get("totalCount") if isinstance(episodes, dict) else item.get("totalEpisodes")),
        "raw": item,
    }


async def _oembed_details(kind: str, uri: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
        resp = await client.get("https://open.spotify.com/oembed", params={"url": uri})
    if resp.status_code >= 400:
        raise HTTPException(status_code=404, detail="Spotify item not found")
    item = resp.json()
    return {
        "platform": "spotify",
        "type": kind,
        "uri": safe_str(uri),
        "url": safe_str(uri),
        "name": safe_str(item.get("title")),
        "description": "",
        "artists": [],
        "album": "",
        "durationMs": 0,
        "playCount": 0,
        "followers": 0,
        "monthlyListeners": 0,
        "releaseYear": 0,
        "image": safe_str(item.get("thumbnail_url")),
        "totalTracks": 0,
        "totalEpisodes": 0,
        "raw": item,
    }


async def _details(kind: str, uri: str, limit: int | None = None) -> dict[str, Any]:
    settings = get_settings()
    album_limit = limit if kind == "album" else 0
    podcast_limit = limit if kind == "podcast" else 0
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
    if not items:
        return await _oembed_details(kind, uri)
    return _normalize(items[0], kind)


@router.get("/artist", summary="Spotify artist details")
async def artist(
    url: str = Query(..., description="Spotify artist URL, URI, or ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "artist")
    async with billed_call(caller=caller, endpoint="/v1/spotify/artist", platform="spotify", resource_url=uri, base_credits=6) as ctx:
        data = await cached_or_run("spotify.artist", {"uri": uri}, lambda: _details("artist", uri), ctx, ttl=get_settings().CACHE_TTL_STATIC)
        return ApiResponse(data=data)


@router.get("/track", summary="Spotify track details")
async def track(
    url: str = Query(..., description="Spotify track URL, URI, or ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "track")
    async with billed_call(caller=caller, endpoint="/v1/spotify/track", platform="spotify", resource_url=uri, base_credits=6) as ctx:
        data = await cached_or_run("spotify.track", {"uri": uri}, lambda: _details("track", uri), ctx, ttl=get_settings().CACHE_TTL_STATIC)
        return ApiResponse(data=data)


@router.get("/album", summary="Spotify album details")
async def album(
    url: str = Query(..., description="Spotify album URL, URI, or ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "album")
    async with billed_call(caller=caller, endpoint="/v1/spotify/album", platform="spotify", resource_url=uri, base_credits=6) as ctx:
        data = await cached_or_run("spotify.album", {"uri": uri}, lambda: _details("album", uri, limit=1), ctx, ttl=get_settings().CACHE_TTL_STATIC)
        return ApiResponse(data=data)


@router.get("/podcast", summary="Spotify podcast/show details")
async def podcast(
    url: str = Query(..., description="Spotify show/podcast URL, URI, or ID"),
    limit: int = Query(20, ge=1, le=50),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "show")
    async with billed_call(caller=caller, endpoint="/v1/spotify/podcast", platform="spotify", resource_url=uri, base_credits=6) as ctx:
        data = await cached_or_run("spotify.podcast", {"uri": uri, "limit": limit}, lambda: _details("podcast", uri, limit), ctx, ttl=get_settings().CACHE_TTL_STATIC)
        return ApiResponse(data=data)


@router.get("/podcast-episodes", summary="Spotify podcast episodes")
async def podcast_episodes(
    url: str = Query(..., description="Spotify show/podcast URL, URI, or ID"),
    limit: int = Query(20, ge=1, le=50),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "show")
    cost = _scaled(limit)
    async with billed_call(caller=caller, endpoint="/v1/spotify/podcast-episodes", platform="spotify", resource_url=uri, base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _details("podcast", uri, limit)
            raw = data.get("raw") or {}
            episodes = raw.get("episodes") or raw.get("items") or raw.get("content") or {}
            items = episodes.get("items") if isinstance(episodes, dict) else episodes
            normalized = [_normalize(i, "episode") for i in items if isinstance(i, dict)] if isinstance(items, list) else []
            return {"platform": "spotify", "podcast": data, "totalReturned": len(normalized[:limit]), "episodes": normalized[:limit]}

        data = await cached_or_run("spotify.podcast-episodes", {"uri": uri, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["episodes"]))
        return ApiResponse(data=data)


@router.get("/search", summary="Search Spotify")
async def search(
    q: str = Query(..., min_length=2),
    type: str = Query("tracks", pattern="^(tracks|albums|artists|podcasts|episodes)$"),
    limit: int = Query(20, ge=1, le=50),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    search_type = {
        "tracks": "searchTracks",
        "albums": "searchAlbums",
        "artists": "searchArtists",
        "podcasts": "searchPodcasts",
        "episodes": "searchFullEpisodes",
    }[type]
    cost = _scaled(limit)
    async with billed_call(caller=caller, endpoint="/v1/spotify/search", platform="spotify", resource_url=f"spotify:search:{q}", base_credits=cost) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_SPOTIFY_SEARCH,
                {
                    "searchType": search_type,
                    "keyword": [q],
                    "proxyCountry": "US",
                    "tracks_search_limit": limit,
                    "albums_search_limit": limit,
                    "artists_search_limit": limit,
                    "podcasts_search_limit": limit,
                    "episodes_search_limit": limit,
                },
                max_items=limit,
            )
            results = [_normalize(i, type[:-1] if type.endswith("s") else type) for i in items[:limit]]
            return {"platform": "spotify", "query": q, "type": type, "totalReturned": len(results), "results": results}

        data = await cached_or_run("spotify.search", {"q": q, "type": type, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["results"]))
        return ApiResponse(data=data)
