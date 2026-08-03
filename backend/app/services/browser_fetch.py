"""TLS-impersonated HTTP fetches for Cloudflare-protected pages.

Plain httpx is fingerprint-blocked by some hosts (lnk.bio). curl_cffi with a
Chrome impersonation profile passes those checks. Falls back to httpx when
curl_cffi is unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.services.http_fetch import DEFAULT_HEADERS, proxy_for


@dataclass
class BrowserResponse:
    status_code: int
    text: str
    url: str


def _is_cloudflare_block(status_code: int, text: str) -> bool:
    head = (text or "")[:4000].lower()
    if status_code in {403, 503}:
        if "cloudflare" in head or "attention required" in head or "cf-ray" in head:
            return True
    return "attention required" in head and "cloudflare" in head


async def fetch_html(
    url: str,
    *,
    timeout: float = 30.0,
    headers: dict[str, str] | None = None,
    prefer_impersonate: bool = True,
) -> BrowserResponse:
    """GET HTML, preferring Chrome TLS impersonation when available."""
    merged = {
        **DEFAULT_HEADERS,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        **(headers or {}),
    }
    last: BrowserResponse | None = None

    if prefer_impersonate:
        try:
            from curl_cffi.requests import AsyncSession
        except ImportError:
            AsyncSession = None  # type: ignore[misc, assignment]
        if AsyncSession is not None:
            for impersonate in ("chrome131", "chrome124"):
                try:
                    async with AsyncSession() as session:
                        resp = await session.get(
                            url,
                            impersonate=impersonate,
                            timeout=timeout,
                            allow_redirects=True,
                            headers=merged,
                        )
                    out = BrowserResponse(
                        status_code=int(resp.status_code),
                        text=resp.text or "",
                        url=str(getattr(resp, "url", url)),
                    )
                    last = out
                    if out.status_code < 400 and not _is_cloudflare_block(
                        out.status_code, out.text
                    ):
                        return out
                except Exception:  # noqa: BLE001
                    continue

    for tier in ("residential", "none"):
        proxy = proxy_for(tier)  # type: ignore[arg-type]
        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers=merged,
                proxy=proxy,
            ) as client:
                resp = await client.get(url)
            out = BrowserResponse(
                status_code=resp.status_code,
                text=resp.text or "",
                url=str(resp.url),
            )
            last = out
            if out.status_code < 400 and not _is_cloudflare_block(out.status_code, out.text):
                return out
        except httpx.HTTPError:
            continue

    if last is not None:
        return last
    raise httpx.HTTPError(f"Failed to fetch {url}")


__all__ = ["BrowserResponse", "fetch_html", "_is_cloudflare_block"]