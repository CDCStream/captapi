"""Optional TikTok web-signer sidecar (tiktok-signature /fetch).

Search, followers and followings need TikTok's browser-signed web APIs.
Unsigned mobile aweme calls soft-block; replaying a signed URL from another
IP returns empty bodies. The reliable path is to POST the API URL to a local
``tiktok-signature`` service ``/fetch`` endpoint, which executes the request
inside the same browser session that minted ``msToken`` / ``X-Bogus``.

Set ``TIKTOK_SIGNER_URL`` (e.g. ``http://127.0.0.1:8080``). When unset, callers
receive ``None`` and fall back to Apify.
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger(__name__)


def enabled() -> bool:
    return bool(get_settings().TIKTOK_SIGNER_URL.strip())


async def fetch_api(url: str, *, timeout: float = 60.0) -> dict[str, Any] | None:
    """Fetch a TikTok web API URL through the signer ``/fetch`` endpoint.

    Returns the inner ``data`` object (TikTok JSON body) or ``None``.
    """
    base = get_settings().TIKTOK_SIGNER_URL.strip().rstrip("/")
    if not base or not url:
        return None
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{base}/fetch", json={"url": url})
    except httpx.HTTPError as exc:
        log.info("tt_signer_transport_error", error=str(exc)[:160])
        return None
    if resp.status_code != 200:
        log.info("tt_signer_http_error", status=resp.status_code)
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    if not isinstance(payload, dict) or payload.get("status") != "ok":
        log.info(
            "tt_signer_bad_status",
            status=payload.get("status") if isinstance(payload, dict) else None,
        )
        return None
    data = payload.get("data")
    return data if isinstance(data, dict) else None
