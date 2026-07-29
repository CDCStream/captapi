"""Generic URL fetch through Decodo's universal Web Scraping API.

Some upstreams (notably Reddit) block every datacenter and residential proxy
range we control, but respond normally to Decodo's managed scraping pool.
This helper exposes that pool as a plain (status_code, body) fetch so routers
can slot it into their fallback cascades.
"""

from __future__ import annotations

import base64
import json
from typing import Any

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger(__name__)


def enabled() -> bool:
    settings = get_settings()
    if settings.DECODO_AUTH_TOKEN.strip():
        return True
    return bool(settings.DECODO_USERNAME.strip() and settings.DECODO_PASSWORD.strip())


def _auth_header() -> str | None:
    settings = get_settings()
    token = settings.DECODO_AUTH_TOKEN.strip()
    if token:
        return token if token.lower().startswith("basic ") else f"Basic {token}"
    user = settings.DECODO_USERNAME.strip()
    password = settings.DECODO_PASSWORD.strip()
    if user and password:
        encoded = base64.b64encode(f"{user}:{password}".encode()).decode()
        return f"Basic {encoded}"
    return None


async def fetch_url(
    url: str,
    timeout: float = 30.0,
    *,
    headless: str | None = None,
    browser_actions: list[dict[str, Any]] | None = None,
    target: str | None = None,
    xhr: bool = False,
    geo: str | None = None,
) -> tuple[int, str] | None:
    """Fetch ``url`` via Decodo. Returns ``(upstream_status, body_text)`` or
    ``None`` when Decodo is unconfigured / errored, so callers can fall back.

    Pass ``headless="html"`` to enable JavaScript rendering (needed for Meta /
    LinkedIn Ad Library pages that hydrate search results client-side).
    Optional ``browser_actions`` runs Decodo interactions (scroll/wait) first.
    ``target="universal"`` is required for most ``browser_actions`` payloads.
    ``xhr=True`` returns captured XHR JSON (as a string) instead of HTML.
    ``geo`` is an optional ISO country code for localized egress (e.g. ``US``).
    """
    auth_header = _auth_header()
    if not auth_header:
        return None
    settings = get_settings()
    body: dict[str, Any] = {"url": url}
    if target:
        body["target"] = target
    if headless:
        body["headless"] = headless
    if xhr:
        body["xhr"] = True
    if browser_actions:
        body["browser_actions"] = browser_actions
    if geo:
        body["geo"] = geo.strip().upper()
    elif settings.DECODO_GEO:
        body["geo"] = settings.DECODO_GEO
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.DECODO_BASE.rstrip('/')}/scrape",
                json=body,
                headers={"Accept": "application/json", "Authorization": auth_header},
            )
    except httpx.HTTPError as exc:
        log.warning("decodo_fetch_transport_error", url=url, error=str(exc))
        return None
    if response.status_code != 200:
        log.warning("decodo_fetch_http_error", url=url, status=response.status_code)
        return None
    try:
        payload = response.json()
    except ValueError:
        return None
    # Failed scrape tasks return HTTP 200 with status=failed and no results.
    if isinstance(payload, dict) and payload.get("status") == "failed":
        log.warning(
            "decodo_fetch_task_failed",
            url=url,
            status_code=payload.get("status_code"),
            message=str(payload.get("message") or "")[:160],
        )
        return None
    results = payload.get("results") if isinstance(payload, dict) else None
    if not (isinstance(results, list) and results and isinstance(results[0], dict)):
        return None
    result = results[0]
    status = result.get("status_code")
    content = result.get("content")
    if not isinstance(status, int) or not isinstance(content, str):
        return None
    return status, content


async def fetch_json(url: str, timeout: float = 30.0) -> tuple[int, Any] | None:
    """Like :func:`fetch_url` but parses the body as JSON. Returns ``None`` on
    any failure including unparseable bodies (except for error statuses, where
    the body is returned as-is since callers only need the status)."""
    fetched = await fetch_url(url, timeout=timeout)
    if fetched is None:
        return None
    status, body = fetched
    try:
        return status, json.loads(body)
    except ValueError:
        if status >= 400:
            return status, None
        return None
