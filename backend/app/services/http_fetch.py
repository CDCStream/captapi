"""Proxy-aware HTTP client for self-scraping.

Direct scrapers (YouTube, Reddit, ...) use this instead of talking to
upstreams straight from the datacenter IP, which platforms block. The proxy
pool is configured via env (see ``Settings.PROXY_*``):

    PROXY_DATACENTER_URL   cheap pool for lenient targets (YouTube, Reddit)
    PROXY_RESIDENTIAL_URL  pricier pool for strict targets / on block

Nothing configured -> requests go out directly (fine for local dev and for
targets that don't block datacenter IPs).

The Apify residential proxy (``apify_proxy.fetch_via_residential``) stays as a
last-resort fallback and is not replaced here.
"""

from __future__ import annotations

from typing import Literal

import httpx

from app.core.config import get_settings

ProxyTier = Literal["none", "datacenter", "residential"]

# A realistic desktop-Chrome fingerprint. Reused so scrapers look consistent.
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def proxy_for(tier: ProxyTier) -> str | None:
    """Return the configured proxy URL for a tier, or None if unset."""
    settings = get_settings()
    if tier == "datacenter":
        return getattr(settings, "PROXY_DATACENTER_URL", "") or None
    if tier == "residential":
        return getattr(settings, "PROXY_RESIDENTIAL_URL", "") or None
    return None


async def fetch(
    url: str,
    *,
    tier: ProxyTier = "datacenter",
    headers: dict[str, str] | None = None,
    params: dict[str, object] | None = None,
    cookies: dict[str, str] | None = None,
    timeout: float = 15.0,
    follow_redirects: bool = True,
) -> httpx.Response:
    """GET ``url`` through the proxy tier (falls back to direct if unset).

    Raises the usual ``httpx`` errors; callers decide how to handle status
    codes and whether to escalate to a stricter tier or to Apify.
    """
    merged = {**DEFAULT_HEADERS, **(headers or {})}
    proxy = proxy_for(tier)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=follow_redirects,
        headers=merged,
        cookies=cookies,
        proxy=proxy,
    ) as client:
        return await client.get(url, params=params)


async def fetch_json(
    url: str,
    *,
    tier: ProxyTier = "datacenter",
    headers: dict[str, str] | None = None,
    params: dict[str, object] | None = None,
    timeout: float = 15.0,
) -> object:
    """GET + parse JSON. Raises on non-2xx or invalid JSON."""
    resp = await fetch(url, tier=tier, headers=headers, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
