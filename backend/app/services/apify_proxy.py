"""Helper for routing plain HTTP fetches through Apify's residential proxy.

Some public pages (Facebook Marketplace OpenGraph tags, etc.) are served fine
to residential IPs but blocked / login-walled for datacenter IPs. We reuse the
Apify account's residential proxy so server-side OpenGraph scrapes succeed.

The proxy password is fetched once from the Apify user record and cached.
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


async def fetch_via_residential(
    url: str, *, headers: dict[str, str] | None = None, timeout: float = 30.0
) -> httpx.Response | None:
    """Fetch ``url`` through the residential proxy. Returns None if unavailable."""
    proxy = await get_residential_proxy_url()
    if not proxy:
        return None
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True, headers=headers, proxy=proxy
    ) as client:
        return await client.get(url)
