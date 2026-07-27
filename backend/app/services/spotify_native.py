"""Native Spotify search, entity details, and podcast episodes via Pathfinder.

Flow (no Apify, no residential proxy required in practice):
  1. Anonymous web-player access token (TOTP handshake + ThetaDev secrets)
  2. Pathfinder GraphQL persisted queries (search → hydrate)

Callers fall back to Apify when this returns None.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import re
import time
from typing import Any

import httpx

try:
    import pyotp
except ImportError:  # pragma: no cover - installed via pyproject
    pyotp = None  # type: ignore[assignment]

from app.services.http_fetch import DEFAULT_HEADERS

log = logging.getLogger(__name__)

_TOKEN_URL = "https://open.spotify.com/api/token"
_SECRETS_URL = (
    "https://code.thetadev.de/ThetaDev/spotify-secrets/raw/branch/main/secrets/secretDict.json"
)
_PATHFINDER = "https://api-partner.spotify.com/pathfinder/v1/query"
_OPEN = "https://open.spotify.com"

# Hardcoded fallbacks — refreshed at runtime from web-player JS when possible.
_FALLBACK_SECRETS: dict[str, list[int]] = {
    "61": [44, 55, 47, 42, 70, 40, 34, 114, 76, 74, 50, 111, 120, 97, 75, 76, 94, 102, 43, 69, 49, 120, 118, 80, 64, 78],
}
_FALLBACK_HASHES: dict[str, str] = {
    "assistedCurationSearch": "f78953bf9207d73493c27284103f5aeb6e728876d5793851bf79bc706127ff70",
    "decorateContextTracks": "383de00240775c39a6afe0b1055dc562b2a3930894201f9762f3fc32a74971c7",
    "decorateContextEpisodesOrChapters": "383de00240775c39a6afe0b1055dc562b2a3930894201f9762f3fc32a74971c7",
    "queryPodcastEpisodes": "06046f9b939d56c8eb7cdbb687da938de1164c006871aec91dc26e4dc7d8eb08",
    "queryShowMetadataV2": "40202837452991ffa80ced96987bc1a937e21d5a89df5bf1fb743110e4d6e93a",
    "getAlbum": "b9bfabef66ed756e5e13f68a942deb60bd4125ec1f1be8cc42769dc0259b4b10",
    "queryArtistOverview": "ae0e2958a4ab645b35ca19ac04d0495ae12d9c5d7b7286217674801a9aab281a",
}

_UA = {
    **DEFAULT_HEADERS,
    "Accept": "application/json",
    "Referer": f"{_OPEN}/",
    "Origin": _OPEN,
    "App-Platform": "WebPlayer",
}

_token: str | None = None
_token_expires_at: float = 0.0
_secrets: dict[str, list[int]] | None = None
_secrets_fetched_at: float = 0.0
_hashes: dict[str, str] = dict(_FALLBACK_HASHES)
_hashes_fetched_at: float = 0.0

_SECRETS_MAX_AGE = 6 * 3600
_HASHES_MAX_AGE = 24 * 3600
_TOKEN_SKEW = 60.0


def _totp(secret_bytes: list[int]) -> str:
    if pyotp is None:
        raise RuntimeError("pyotp is required for Spotify native auth")
    # SpotAPI-compatible transform: join decimal digits, hex-encode, base32.
    transformed = [e ^ ((t % 33) + 9) for t, e in enumerate(secret_bytes)]
    joined = "".join(str(num) for num in transformed)
    secret = base64.b32encode(bytes.fromhex(joined.encode().hex())).decode().rstrip("=")
    return pyotp.TOTP(secret).now()


def _uri_to_url(uri: str) -> str | None:
    parts = (uri or "").split(":")
    if len(parts) >= 3 and parts[0] == "spotify":
        return f"{_OPEN}/{parts[1]}/{parts[2]}"
    return None


def _with_url(item: dict[str, Any]) -> dict[str, Any]:
    if item.get("url") or item.get("externalUrl") or item.get("shareUrl"):
        return item
    sharing = item.get("sharingInfo") if isinstance(item.get("sharingInfo"), dict) else {}
    if sharing.get("shareUrl"):
        return item
    url = _uri_to_url(str(item.get("uri") or ""))
    if url:
        out = dict(item)
        out["url"] = url
        return out
    return item


async def _load_secrets(client: httpx.AsyncClient) -> dict[str, list[int]]:
    global _secrets, _secrets_fetched_at
    if _secrets and (time.time() - _secrets_fetched_at) < _SECRETS_MAX_AGE:
        return _secrets
    try:
        resp = await client.get(_SECRETS_URL, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and data:
                cleaned = {str(k): list(v) for k, v in data.items() if isinstance(v, list)}
                if cleaned:
                    _secrets = cleaned
                    _secrets_fetched_at = time.time()
                    return _secrets
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        log.debug("spotify secrets fetch failed: %s", exc)
    _secrets = dict(_FALLBACK_SECRETS)
    _secrets_fetched_at = time.time()
    return _secrets


async def _refresh_hashes(client: httpx.AsyncClient) -> None:
    global _hashes, _hashes_fetched_at
    if (time.time() - _hashes_fetched_at) < _HASHES_MAX_AGE and _hashes_fetched_at:
        return
    try:
        home = await client.get(_OPEN + "/", timeout=15)
        srcs = re.findall(
            r'src="(https://open\.spotifycdn\.com/cdn/build/web-player/[^"]+\.js)"',
            home.text,
        )
        blob = ""
        for src in srcs[:3]:
            blob += (await client.get(src, timeout=20)).text
        found = dict(re.findall(r'\.l\("([^"]+)","query","([a-f0-9]{64})"', blob))
        if found:
            merged = dict(_FALLBACK_HASHES)
            for key in _FALLBACK_HASHES:
                if key in found:
                    merged[key] = found[key]
            _hashes = merged
            _hashes_fetched_at = time.time()
    except (httpx.HTTPError, ValueError) as exc:
        log.debug("spotify hash refresh failed: %s", exc)
        if not _hashes_fetched_at:
            _hashes_fetched_at = time.time()


async def _get_token(client: httpx.AsyncClient) -> str | None:
    global _token, _token_expires_at
    now = time.time()
    if _token and now < (_token_expires_at - _TOKEN_SKEW):
        return _token
    if pyotp is None:
        return None
    try:
        secrets = await _load_secrets(client)
        version = max(secrets, key=lambda k: int(k) if str(k).isdigit() else -1)
        code = _totp(secrets[version])
        await client.get(_OPEN + "/", timeout=15)
        resp = await client.get(
            _TOKEN_URL,
            params={
                "reason": "init",
                "productType": "web-player",
                "totp": code,
                "totpServer": code,
                "totpVer": str(version),
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        access = data.get("accessToken")
        if not access:
            return None
        exp_ms = data.get("accessTokenExpirationTimestampMs")
        _token = str(access)
        _token_expires_at = (float(exp_ms) / 1000.0) if exp_ms else (now + 3000)
        return _token
    except (httpx.HTTPError, ValueError, TypeError, RuntimeError) as exc:
        log.debug("spotify token failed: %s", exc)
        return None


async def _pathfinder(
    client: httpx.AsyncClient,
    token: str,
    operation: str,
    variables: dict[str, Any],
) -> dict[str, Any] | None:
    sha = _hashes.get(operation) or _FALLBACK_HASHES.get(operation)
    if not sha:
        return None
    try:
        resp = await client.get(
            _PATHFINDER,
            params={
                "operationName": operation,
                "variables": json.dumps(variables, separators=(",", ":")),
                "extensions": json.dumps(
                    {"persistedQuery": {"version": 1, "sha256Hash": sha}},
                    separators=(",", ":"),
                ),
            },
            headers={**_UA, "Authorization": f"Bearer {token}"},
            timeout=20,
        )
    except httpx.HTTPError:
        return None
    if resp.status_code != 200:
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    if payload.get("errors") and not payload.get("data"):
        return None
    data = payload.get("data")
    return data if isinstance(data, dict) else None


def _extract_uris(search_v2: dict[str, Any], kind: str) -> list[str]:
    block_key = {
        "track": "tracksV2",
        "album": "albumsV2",
        "artist": "artists",
        "episode": "episodes",
    }.get(kind)
    if not block_key:
        return []
    block = search_v2.get(block_key) or {}
    items = block.get("items") or block.get("itemsV2") or []
    out: list[str] = []
    for entry in items if isinstance(items, list) else []:
        if not isinstance(entry, dict):
            continue
        data = entry.get("data")
        if not isinstance(data, dict):
            item = entry.get("item")
            data = item.get("data") if isinstance(item, dict) else None
        uri = data.get("uri") if isinstance(data, dict) else None
        if isinstance(uri, str) and uri.startswith("spotify:"):
            out.append(uri)
    return out


async def _oembed(client: httpx.AsyncClient, uri: str) -> dict[str, Any] | None:
    url = _uri_to_url(uri)
    if not url:
        return None
    try:
        resp = await client.get(
            f"{_OPEN}/oembed",
            params={"url": url},
            headers=_UA,
            timeout=10,
        )
    except httpx.HTTPError:
        return None
    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    return _with_url(
        {
            "uri": uri,
            "url": url,
            "name": data.get("title"),
            "image": data.get("thumbnail_url"),
            "thumbnail_url": data.get("thumbnail_url"),
        }
    )


async def _hydrate_tracks(
    client: httpx.AsyncClient, token: str, uris: list[str]
) -> list[dict[str, Any]]:
    if not uris:
        return []
    data = await _pathfinder(client, token, "decorateContextTracks", {"uris": uris})
    tracks = (data or {}).get("tracks") or []
    out: list[dict[str, Any]] = []
    for track in tracks if isinstance(tracks, list) else []:
        if isinstance(track, dict) and track.get("uri"):
            out.append(_with_url(track))
    return out


async def _hydrate_episodes(
    client: httpx.AsyncClient, token: str, uris: list[str]
) -> list[dict[str, Any]]:
    if not uris:
        return []
    data = await _pathfinder(
        client, token, "decorateContextEpisodesOrChapters", {"uris": uris}
    )
    episodes = (data or {}).get("episodes") or []
    out: list[dict[str, Any]] = []
    for ep in episodes if isinstance(episodes, list) else []:
        if isinstance(ep, dict) and ep.get("uri"):
            # Publisher lives under podcastV2 — surface for _normalize artists.
            podcast = (ep.get("podcastV2") or {}).get("data") if isinstance(ep.get("podcastV2"), dict) else None
            if isinstance(podcast, dict) and isinstance(podcast.get("publisher"), dict):
                ep = dict(ep)
                ep["publisher"] = podcast["publisher"]
            out.append(_with_url(ep))
    return out


async def _hydrate_albums(
    client: httpx.AsyncClient, token: str, uris: list[str]
) -> list[dict[str, Any]]:
    async def one(uri: str) -> dict[str, Any] | None:
        data = await _pathfinder(
            client,
            token,
            "getAlbum",
            {"uri": uri, "locale": "", "offset": 0, "limit": 1},
        )
        album = (data or {}).get("albumUnion")
        if isinstance(album, dict) and album.get("__typename") == "Album":
            return _with_url(album)
        return await _oembed(client, uri)

    rows = await asyncio.gather(*[one(u) for u in uris])
    return [r for r in rows if isinstance(r, dict)]


async def _hydrate_artists(
    client: httpx.AsyncClient, token: str, uris: list[str]
) -> list[dict[str, Any]]:
    async def one(uri: str) -> dict[str, Any] | None:
        data = await _pathfinder(
            client,
            token,
            "queryArtistOverview",
            {"uri": uri, "locale": "", "includePrerelease": False},
        )
        artist = (data or {}).get("artistUnion")
        if isinstance(artist, dict) and artist.get("__typename") == "Artist":
            profile = artist.get("profile") if isinstance(artist.get("profile"), dict) else {}
            flat = dict(artist)
            flat["name"] = profile.get("name") or artist.get("name")
            if profile.get("biography") and not flat.get("biography"):
                flat["biography"] = profile.get("biography")
            return _with_url(flat)
        return await _oembed(client, uri)

    rows = await asyncio.gather(*[one(u) for u in uris])
    return [r for r in rows if isinstance(r, dict)]


async def _hydrate_podcasts(
    client: httpx.AsyncClient, token: str, episode_uris: list[str]
) -> list[dict[str, Any]]:
    """Pathfinder search has no shows bucket — derive unique shows from episodes."""
    episodes = await _hydrate_episodes(client, token, episode_uris)
    seen: set[str] = set()
    shows: list[dict[str, Any]] = []
    for ep in episodes:
        podcast = (ep.get("podcastV2") or {}).get("data") if isinstance(ep.get("podcastV2"), dict) else None
        if not isinstance(podcast, dict):
            continue
        uri = podcast.get("uri")
        if not isinstance(uri, str) or uri in seen:
            continue
        seen.add(uri)
        shows.append(_with_url(podcast))
    return shows


async def search_native(q: str, type_: str, limit: int) -> list[dict[str, Any]] | None:
    """Return raw items for ``_normalize``, or None to fall back to Apify."""
    kind = {
        "tracks": "track",
        "albums": "album",
        "artists": "artist",
        "episodes": "episode",
        "podcasts": "podcast",
    }.get(type_)
    if not kind:
        return None

    async with httpx.AsyncClient(timeout=25, follow_redirects=True, headers=_UA) as client:
        await _refresh_hashes(client)
        token = await _get_token(client)
        if not token:
            return None
        data = await _pathfinder(
            client,
            token,
            "assistedCurationSearch",
            {"term": q, "limit": max(limit, 1), "offset": 0},
        )
        search_v2 = (data or {}).get("searchV2")
        if not isinstance(search_v2, dict):
            return None

        if kind == "podcast":
            uris = _extract_uris(search_v2, "episode")[: max(limit * 2, limit)]
            items = await _hydrate_podcasts(client, token, uris)
            return items[:limit] or None

        uris = _extract_uris(search_v2, kind)[:limit]
        if not uris:
            return None

        if kind == "track":
            items = await _hydrate_tracks(client, token, uris)
        elif kind == "episode":
            items = await _hydrate_episodes(client, token, uris)
        elif kind == "album":
            items = await _hydrate_albums(client, token, uris)
        else:
            items = await _hydrate_artists(client, token, uris)

        return items[:limit] or None


def _show_uri(url_or_uri: str) -> str | None:
    value = (url_or_uri or "").strip()
    if value.startswith("spotify:show:"):
        return value
    m = re.search(r"(?:open\.spotify\.com/show/|spotify:show:)([A-Za-z0-9]+)", value)
    if m:
        return f"spotify:show:{m.group(1)}"
    if re.fullmatch(r"[A-Za-z0-9]{22}", value):
        return f"spotify:show:{value}"
    return None


async def podcast_episodes_native(
    url_or_uri: str, limit: int
) -> tuple[dict[str, Any], list[dict[str, Any]]] | None:
    """Return ``(podcast_raw, episode_raws)`` or None."""
    show_uri = _show_uri(url_or_uri)
    if not show_uri:
        return None

    async with httpx.AsyncClient(timeout=25, follow_redirects=True, headers=_UA) as client:
        await _refresh_hashes(client)
        token = await _get_token(client)
        if not token:
            return None

        meta_task = _pathfinder(
            client,
            token,
            "queryShowMetadataV2",
            {
                "uri": show_uri,
                "includeContentCapabilityTrait": False,
                "includeEpisodeContentRatingsV2": False,
            },
        )
        eps_task = _pathfinder(
            client,
            token,
            "queryPodcastEpisodes",
            {
                "uri": show_uri,
                "offset": 0,
                "limit": limit,
                "includeEpisodeContentRatingsV2": False,
            },
        )
        meta_data, eps_data = await asyncio.gather(meta_task, eps_task)

        podcast_union = (meta_data or {}).get("podcastUnionV2") or (eps_data or {}).get(
            "podcastUnionV2"
        )
        if not isinstance(podcast_union, dict) or podcast_union.get("__typename") == "NotFound":
            return None

        podcast = _with_url(dict(podcast_union))
        if not podcast.get("uri"):
            podcast["uri"] = show_uri

        v2 = (eps_data or {}).get("podcastUnionV2") or {}
        episodes_block = v2.get("episodesV2") if isinstance(v2, dict) else None
        items = (episodes_block or {}).get("items") if isinstance(episodes_block, dict) else []
        rows: list[dict[str, Any]] = []
        for entry in items if isinstance(items, list) else []:
            if not isinstance(entry, dict):
                continue
            entity = entry.get("entity") if isinstance(entry.get("entity"), dict) else None
            data = entity.get("data") if isinstance(entity, dict) else None
            row = data if isinstance(data, dict) else entry
            if isinstance(row, dict) and row.get("__typename") == "Episode":
                if isinstance(entity, dict) and entity.get("_uri") and not row.get("uri"):
                    row = dict(row)
                    row["uri"] = entity["_uri"]
                rows.append(_with_url(row))

        if not rows and podcast.get("__typename") != "Podcast":
            return None
        return podcast, rows[:limit]


def _entity_uri(url_or_uri: str, kind: str) -> str | None:
    """Normalize URL/URI/ID to ``spotify:{kind}:{id}``.

    ``kind`` is the Spotify URI type: artist, track, album, show.
    """
    value = (url_or_uri or "").strip()
    if not value:
        return None
    if value.startswith(f"spotify:{kind}:"):
        return value
    m = re.search(
        rf"(?:open\.spotify\.com/{re.escape(kind)}/|spotify:{re.escape(kind)}:)([A-Za-z0-9]+)",
        value,
        re.I,
    )
    if m:
        return f"spotify:{kind}:{m.group(1)}"
    if re.fullmatch(r"[A-Za-z0-9]{22}", value):
        return f"spotify:{kind}:{value}"
    return None


async def details_native(
    kind: str, url_or_uri: str, *, episode_limit: int = 1
) -> dict[str, Any] | None:
    """Hydrate one entity for ``_normalize``. ``kind``: artist|track|album|podcast.

    Returns None when Pathfinder auth/query fails (caller may oembed/Apify).
    """
    uri_kind = {"artist": "artist", "track": "track", "album": "album", "podcast": "show"}.get(
        kind
    )
    if not uri_kind:
        return None
    uri = _entity_uri(url_or_uri, uri_kind)
    if not uri:
        return None

    async with httpx.AsyncClient(timeout=25, follow_redirects=True, headers=_UA) as client:
        await _refresh_hashes(client)
        token = await _get_token(client)
        if not token:
            return None

        if kind == "track":
            rows = await _hydrate_tracks(client, token, [uri])
            return rows[0] if rows else None
        if kind == "album":
            rows = await _hydrate_albums(client, token, [uri])
            return rows[0] if rows else None
        if kind == "artist":
            rows = await _hydrate_artists(client, token, [uri])
            return rows[0] if rows else None
        if kind == "podcast":
            meta = await _pathfinder(
                client,
                token,
                "queryShowMetadataV2",
                {
                    "uri": uri,
                    "includeContentCapabilityTrait": False,
                    "includeEpisodeContentRatingsV2": False,
                },
            )
            podcast_union = (meta or {}).get("podcastUnionV2")
            if not isinstance(podcast_union, dict) or podcast_union.get("__typename") == "NotFound":
                packed = await podcast_episodes_native(uri, max(1, episode_limit))
                if packed is None:
                    return None
                return packed[0]
            podcast = _with_url(dict(podcast_union))
            if not podcast.get("uri"):
                podcast["uri"] = uri
            has_total = podcast.get("totalEpisodes") is not None or (
                isinstance(podcast.get("episodesV2"), dict)
                and podcast["episodesV2"].get("totalCount") is not None
            )
            if not has_total:
                eps = await _pathfinder(
                    client,
                    token,
                    "queryPodcastEpisodes",
                    {
                        "uri": uri,
                        "offset": 0,
                        "limit": max(1, min(episode_limit, 50)),
                        "includeEpisodeContentRatingsV2": False,
                    },
                )
                v2 = (eps or {}).get("podcastUnionV2") or {}
                block = v2.get("episodesV2") if isinstance(v2, dict) else None
                if isinstance(block, dict):
                    podcast["episodesV2"] = block
            return podcast
        return None

