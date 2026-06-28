"""Async Apify Actor invocation wrapper with retry + timeout."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
import structlog
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings

log = structlog.get_logger(__name__)


class ApifyError(Exception):
    pass


class ApifyClient:
    BASE = "https://api.apify.com/v2"

    def __init__(
        self,
        token: str | None = None,
        timeout: float | None = None,
        max_attempts: int | None = None,
        retry_max_wait: float | None = None,
    ):
        settings = get_settings()
        self.token = token or settings.APIFY_TOKEN
        self.timeout = timeout or settings.APIFY_SYNC_TIMEOUT_SECONDS
        self.max_attempts = max_attempts or settings.APIFY_SYNC_MAX_ATTEMPTS
        self.retry_max_wait = retry_max_wait or settings.APIFY_SYNC_RETRY_MAX_WAIT_SECONDS

    async def run_actor_sync(
        self,
        actor_id: str,
        run_input: dict[str, Any],
        max_items: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Run actor synchronously and return dataset items.
        Uses Apify's `run-sync-get-dataset-items` endpoint.
        """
        actor_path = actor_id.replace("/", "~")
        url = f"{self.BASE}/acts/{actor_path}/run-sync-get-dataset-items"
        params: dict[str, Any] = {"token": self.token, "clean": "1"}
        if max_items:
            params["limit"] = max_items

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=self.retry_max_wait),
            retry=retry_if_exception_type((httpx.HTTPError, ApifyError)),
            reraise=True,
        ):
            with attempt:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        resp = await client.post(url, params=params, json=run_input)
                except httpx.TimeoutException as exc:
                    raise ApifyError(
                        f"Actor timeout after {self.timeout:g}s"
                    ) from exc

                if resp.status_code == 408:
                    raise ApifyError(f"Actor timeout after {self.timeout:g}s")
                if resp.status_code >= 500:
                    raise ApifyError(f"Apify server error: {resp.status_code}")
                if resp.status_code == 402:
                    raise ApifyError("Apify quota exhausted")
                if resp.status_code >= 400:
                    raise ApifyError(
                        f"Apify {resp.status_code}: {resp.text[:200]}"
                    )

                try:
                    data = resp.json()
                except Exception as e:
                    raise ApifyError(f"Invalid Apify JSON: {e}") from e

                if not isinstance(data, list):
                    raise ApifyError(f"Unexpected Apify response: {type(data)}")
                return data

        return []

    async def run_actor_first(
        self, actor_id: str, run_input: dict[str, Any]
    ) -> dict[str, Any] | None:
        items = await self.run_actor_sync(actor_id, run_input, max_items=1)
        return items[0] if items else None

    async def run_with_fallback(
        self,
        candidates: list[tuple[str, dict[str, Any]]],
        *,
        max_items: int | None = None,
        is_valid: Callable[[list[dict[str, Any]]], bool] | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Try each ``(actor_id, run_input)`` in order, returning the first run
        whose items pass ``is_valid`` (default: non-empty) along with the actor
        that produced them. Guards against a single third-party actor silently
        returning empty/erroring. Returns ``([], None)`` if every candidate
        fails.
        """
        check = is_valid or (lambda items: bool(items))
        last: list[dict[str, Any]] = []
        for actor_id, run_input in candidates:
            try:
                items = await self.run_actor_sync(actor_id, run_input, max_items=max_items)
            except (ApifyError, httpx.HTTPError):
                items = []
            if check(items):
                return items, actor_id
            last = items or last
        return last, None


_client: ApifyClient | None = None


def get_apify() -> ApifyClient:
    global _client
    if _client is None:
        _client = ApifyClient()
    return _client
