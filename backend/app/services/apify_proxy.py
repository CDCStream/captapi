"""Residential-proxy HTTP fetches for server-side scrapes.

Some public pages (Facebook Marketplace OpenGraph tags, Reddit JSON, Rumble
video pages, etc.) are served fine to residential IPs but blocked / login-walled
for datacenter IPs.

Preference order:
  1. Our own managed residential pool (``PROXY_RESIDENTIAL_URL``, e.g. Evomi /
     Webshare) — cheapest, no per-request Apify cost.
  2. Apify's residential proxy — fallback only, billed per GB on the Apify
     account. Used when our pool is unset or gets blocked.

The Apify proxy password is fetched once from the Apify user record and cached.
"""

from __future__ import annotations

import httpx

from app.core.config import get_settings

_proxy_password: str | None = None


async def get_residential_proxy_url() -> str | None:
    """Return an Apify residential proxy URL, or ``None`` if unavailable."""
    global _proxy_password
    settings = get_settings()
    token = getattr(settings, "APIFY_TOKEN", None)
    if not token:
        return None
    if _proxy_password is None:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(f"https://api.apify.com/v2/users/me?token={token}")
            _proxy_password = (
                resp.json().get("data", {}).get("proxy", {}).get("password") or ""
            )
        except Exception:  # noqa: BLE001
            _proxy_password = ""
    if not _proxy_password:
        return None
    return f"http://groups-RESIDENTIAL:{_proxy_password}@proxy.apify.com:8000"


def _own_residential_proxy() -> str | None:
    """Our self-managed residential gateway (Evomi/Webshare), if configured."""
    settings = get_settings()
    return (getattr(settings, "PROXY_RESIDENTIAL_URL", "") or "").strip() or None


# Statuses that indicate the proxy/IP was blocked rather than a genuine result;
# worth retrying through the next proxy candidate.
_BLOCK_STATUSES = frozenset({403, 429})


async def _get(url: str, proxy: str, headers: dict[str, str] | None, timeout: float) -> httpx.Response:
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True, headers=headers, proxy=proxy
    ) as client:
        return await client.get(url)


async def fetch_via_residential(
    url: str, *, headers: dict[str, str] | None = None, timeout: float = 30.0
) -> httpx.Response | None:
    """Fetch ``url`` through a residential proxy.

    Tries our own pool first (cheap), then falls back to Apify's residential
    proxy when ours is unset, errors, or returns a block status. Returns the
    best response obtained, or ``None`` if no proxy is available/reachable.
    """
    candidates: list[str] = []
    own = _own_residential_proxy()
    if own:
        candidates.append(own)
    apify = await get_residential_proxy_url()
    if apify:
        candidates.append(apify)
    if not candidates:
        return None

    last: httpx.Response | None = None
    for proxy in candidates:
        try:
            resp = await _get(url, proxy, headers, timeout)
        except httpx.HTTPError:
            continue
        last = resp
        if resp.status_code < 500 and resp.status_code not in _BLOCK_STATUSES:
            return resp
    return last
