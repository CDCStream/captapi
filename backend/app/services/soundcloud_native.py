"""Native SoundCloud data via the public api-v2 (free, no account).

SoundCloud's own web app talks to ``api-v2.soundcloud.com`` using a
``client_id`` embedded in its JS bundles. We scrape that id from the homepage
bundles, cache it in-process, and refresh it once when it stops being
accepted (they rotate it every few weeks). All lookups go through
``/resolve`` which accepts canonical soundcloud.com URLs.

Returns raw api-v2 objects (snake_case) — the router's mappers already
understand those field names. On any failure callers fall back to Apify.
"""

from __future__ import annotations

import re
import time
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx

_UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_API = "https://api-v2.soundcloud.com"

_client_id: str | None = None
_client_id_fetched_at: float = 0.0
# Re-scrape at most daily; a working id is reused until it 401/403s.
_CLIENT_ID_MAX_AGE = 24 * 3600


async def _scrape_client_id(client: httpx.AsyncClient) -> str | None:
    try:
        home = await client.get("https://soundcloud.com/")
        scripts = re.findall(r'src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"', home.text)
        # The id usually lives in one of the last bundles; search backwards.
        for src in reversed(scripts):
            js = await client.get(src)
            m = re.search(r'client_id[=:]"([A-Za-z0-9]{32})"', js.text)
            if m:
                return m.group(1)
    except httpx.HTTPError:
        pass
    return None


async def _get_client_id(client: httpx.AsyncClient, *, force: bool = False) -> str | None:
    global _client_id, _client_id_fetched_at
    if not force and _client_id and (time.time() - _client_id_fetched_at) < _CLIENT_ID_MAX_AGE:
        return _client_id
    fresh = await _scrape_client_id(client)
    if fresh:
        _client_id = fresh
        _client_id_fetched_at = time.time()
    return _client_id


async def _get(client: httpx.AsyncClient, url: str, params: dict[str, Any] | None) -> Any | None:
    """GET an api-v2 URL with client_id injection and one refresh retry."""
    cid = await _get_client_id(client)
    if not cid:
        return None
    for attempt in (1, 2):
        try:
            resp = await client.get(url, params={**(params or {}), "client_id": cid})
        except httpx.HTTPError:
            return None
        if resp.status_code in (401, 403) and attempt == 1:
            cid = await _get_client_id(client, force=True)
            if not cid:
                return None
            continue
        if resp.status_code != 200:
            return None
        try:
            return resp.json()
        except ValueError:
            return None
    return None


async def _api_get(path: str, params: dict[str, Any]) -> Any | None:
    async with httpx.AsyncClient(timeout=15, headers=_UA, follow_redirects=True) as client:
        return await _get(client, f"{_API}{path}", params)


async def resolve(url: str) -> dict[str, Any] | None:
    """Resolve a soundcloud.com URL to its api-v2 object (user/track/...)."""
    data = await _api_get("/resolve", {"url": url})
    return data if isinstance(data, dict) else None


def offset_from_next_href(next_href: str | None) -> str | None:
    """Extract SoundCloud's pagination ``offset`` from an api-v2 ``next_href``.

    Callers must never return the raw ``next_href`` (it leaks api-v2 host + user id).
    """
    if not next_href or not isinstance(next_href, str):
        return None
    qs = parse_qs(urlparse(next_href).query)
    vals = qs.get("offset") or []
    return vals[0] if vals and vals[0] else None


async def user_tracks(
    user_id: int | str,
    limit: int,
    *,
    offset: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    """One page of a user's tracks (newest first) plus the next offset token.

    Uses api-v2 linked partitioning. Pass ``offset`` decoded from a previous
    response's opaque ``nextCursor`` — never a raw ``next_href`` URL.
    Returns ``(rows, next_offset)`` where ``next_offset`` is SoundCloud's
    opaque offset string (or None when exhausted).
    """
    rows: list[dict[str, Any]] = []
    next_offset: str | None = None
    params: dict[str, Any] = {
        "limit": min(max(limit, 1), 200),
        "linked_partitioning": 1,
    }
    if offset:
        params["offset"] = offset
    async with httpx.AsyncClient(timeout=15, headers=_UA, follow_redirects=True) as client:
        page = await _get(client, f"{_API}/users/{user_id}/tracks", params)
        if isinstance(page, dict):
            batch = [r for r in (page.get("collection") or []) if isinstance(r, dict)]
            rows.extend(batch[:limit])
            next_offset = offset_from_next_href(
                page.get("next_href") if isinstance(page.get("next_href"), str) else None
            )
    return rows[:limit], next_offset


def prep_track_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Adapt an api-v2 track row for the router's ``_track`` mapper.

    - ``tag_list`` comes as one quoted string; the mapper expects a list.
    - ``isrc`` lives under ``publisher_metadata`` in api-v2.
    """
    raw = dict(raw)
    tags_raw = raw.get("tag_list")
    if isinstance(tags_raw, str) and tags_raw.strip():
        pairs = re.findall(r'"([^"]+)"|(\S+)', tags_raw)
        raw["tagList"] = [a or b for a, b in pairs]
    pub = raw.get("publisher_metadata")
    if isinstance(pub, dict) and pub.get("isrc") and not raw.get("isrc"):
        raw["isrc"] = pub["isrc"]
    return raw


def _user_urn(user: dict[str, Any] | int | str) -> str | None:
    if isinstance(user, dict):
        urn = user.get("urn")
        if isinstance(urn, str) and urn.startswith("soundcloud:users:"):
            return urn
        uid = user.get("id")
        if uid is not None:
            return f"soundcloud:users:{uid}"
        return None
    if user is None or user == "":
        return None
    return f"soundcloud:users:{user}"


async def user_web_profiles(user_id: int | str | dict[str, Any]) -> list[dict[str, Any]]:
    """Public profile social/website links (api-v2 ``/users/{urn}/web-profiles``)."""
    urn = _user_urn(user_id)
    if not urn:
        return []
    data = await _api_get(f"/users/{urn}/web-profiles", {})
    if not isinstance(data, list):
        return []
    out: list[dict[str, Any]] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        url = row.get("url")
        if not isinstance(url, str) or not url.strip():
            continue
        item = {
            "url": url.strip(),
            "network": row.get("network") if isinstance(row.get("network"), str) else None,
            "title": row.get("title") if isinstance(row.get("title"), str) else None,
            "username": row.get("username") if isinstance(row.get("username"), str) else None,
        }
        out.append({k: v for k, v in item.items() if v not in (None, "")})
    return out


async def _resolve_transcoding_url(
    client: httpx.AsyncClient, transcoding_url: str
) -> tuple[str | None, int | None]:
    """Hit a media/transcoding URL → signed CDN url + optional unix expiry."""
    data = await _get(client, transcoding_url, {})
    if not isinstance(data, dict):
        return None, None
    url = data.get("url")
    if not isinstance(url, str) or not url.strip():
        return None, None
    expires: int | None = None
    m = re.search(r"[?&]expires=(\d+)", url)
    if m:
        try:
            expires = int(m.group(1))
        except ValueError:
            expires = None
    return url.strip(), expires


async def resolve_media_urls(track: dict[str, Any]) -> dict[str, Any]:
    """Mint signed ``streamUrl`` / ``hlsUrl`` (and ``downloadUrl`` when public).

    ``streamable`` / ``downloadable`` on the track are SoundCloud permission flags;
    this resolves playable CDN URLs when the public api-v2 allows it. Signed URLs
    expire — see ``mediaUrlsExpireAt``.
    """
    media = track.get("media") if isinstance(track.get("media"), dict) else {}
    transcodings = [t for t in (media.get("transcodings") or []) if isinstance(t, dict)]
    progressive = next(
        (
            t
            for t in transcodings
            if (t.get("format") or {}).get("protocol") == "progressive" and t.get("url")
        ),
        None,
    )
    hls = next(
        (
            t
            for t in transcodings
            if (t.get("format") or {}).get("protocol") == "hls" and t.get("url")
        ),
        None,
    )
    # Prefer higher-quality HLS (aac_160k) when several exist.
    hls_candidates = [
        t
        for t in transcodings
        if (t.get("format") or {}).get("protocol") == "hls" and t.get("url")
    ]
    if hls_candidates:
        hls = sorted(
            hls_candidates,
            key=lambda t: (0 if "160" in str(t.get("preset") or "") else 1, str(t.get("preset") or "")),
        )[0]

    stream_url: str | None = None
    hls_url: str | None = None
    download_url: str | None = None
    expires_unix: int | None = None

    async with httpx.AsyncClient(timeout=15, headers=_UA, follow_redirects=True) as client:
        if progressive and isinstance(progressive.get("url"), str):
            stream_url, exp = await _resolve_transcoding_url(client, progressive["url"])
            if exp:
                expires_unix = exp
        if hls and isinstance(hls.get("url"), str):
            hls_url, exp = await _resolve_transcoding_url(client, hls["url"])
            if exp and (expires_unix is None or exp < expires_unix):
                expires_unix = exp
        # Public download (rare without OAuth — try only when flagged downloadable).
        if track.get("downloadable") and track.get("id") is not None:
            cid = await _get_client_id(client)
            if cid:
                try:
                    resp = await client.get(
                        f"{_API}/tracks/{track['id']}/download",
                        params={"client_id": cid},
                        follow_redirects=False,
                    )
                except httpx.HTTPError:
                    resp = None
                if resp is not None:
                    loc = resp.headers.get("location") or resp.headers.get("Location")
                    if resp.status_code in (301, 302, 303, 307, 308) and loc:
                        download_url = loc
                    elif resp.status_code == 200:
                        try:
                            body = resp.json()
                        except ValueError:
                            body = None
                        if isinstance(body, dict) and isinstance(body.get("redirectUri"), str):
                            download_url = body["redirectUri"]
                        elif isinstance(body, dict) and isinstance(body.get("url"), str):
                            download_url = body["url"]

    out: dict[str, Any] = {}
    if stream_url:
        out["streamUrl"] = stream_url
    if hls_url:
        out["hlsUrl"] = hls_url
    if download_url:
        out["downloadUrl"] = download_url
    if expires_unix:
        from datetime import datetime, timezone

        out["mediaUrlsExpireAt"] = datetime.fromtimestamp(expires_unix, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    return out
