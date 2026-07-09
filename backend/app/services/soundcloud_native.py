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


async def user_tracks(user_id: int | str, limit: int) -> list[dict[str, Any]]:
    """Most recent tracks of a user, newest first.

    Uses api-v2 cursor pagination (``next_href``) rather than a numeric
    offset, which SoundCloud pages unreliably. ``linked_partitioning=1``
    makes the API return the cursor URL.
    """
    rows: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=15, headers=_UA, follow_redirects=True) as client:
        url: str | None = f"{_API}/users/{user_id}/tracks"
        params: dict[str, Any] | None = {
            "limit": min(max(limit, 1), 200),
            "linked_partitioning": 1,
        }
        while url and len(rows) < limit:
            page = await _get(client, url, params)
            if not isinstance(page, dict):
                break
            batch = [r for r in (page.get("collection") or []) if isinstance(r, dict)]
            rows.extend(batch)
            # next_href already carries the cursor + query; don't re-add params.
            url = page.get("next_href")
            params = None
    return rows[:limit]


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
