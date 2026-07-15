"""Async Apify Actor invocation wrapper with retry + timeout."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime, timezone
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

    async def _fetch_run_input(self, client: httpx.AsyncClient, run: dict[str, Any]) -> dict[str, Any]:
        store_id = run.get("defaultKeyValueStoreId")
        if not store_id:
            return {}
        try:
            resp = await client.get(
                f"{self.BASE}/key-value-stores/{store_id}/records/INPUT",
                params={"token": self.token},
            )
            if resp.status_code != 200:
                return {}
            data = resp.json()
        except (httpx.HTTPError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    async def dataset_items(self, dataset_id: str, max_items: int | None = None) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(
                    f"{self.BASE}/datasets/{dataset_id}/items",
                    params={"token": self.token, "clean": "1", **({"limit": max_items} if max_items else {})},
                )
                resp.raise_for_status()
                items = resp.json()
        except (httpx.HTTPError, ValueError):
            return []
        return items if isinstance(items, list) else []

    async def last_succeeded_run(
        self,
        actor_id: str,
        max_age_secs: float,
        input_match: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Most recent SUCCEEDED run that finished within ``max_age_secs``,
        optionally restricted to runs whose INPUT contains ``input_match``."""
        actor_path = actor_id.replace("/", "~")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE}/acts/{actor_path}/runs",
                    params={"token": self.token, "desc": 1, "limit": 10, "status": "SUCCEEDED"},
                )
                resp.raise_for_status()
                for run in (resp.json().get("data") or {}).get("items") or []:
                    finished = run.get("finishedAt")
                    if not (finished and run.get("defaultDatasetId")):
                        continue
                    finished_dt = datetime.fromisoformat(finished.replace("Z", "+00:00"))
                    if (datetime.now(timezone.utc) - finished_dt).total_seconds() > max_age_secs:
                        return None
                    if input_match:
                        run_input = await self._fetch_run_input(client, run)
                        if any(run_input.get(k) != v for k, v in input_match.items()):
                            continue
                    return run
        except httpx.HTTPError:
            return None
        return None

    async def last_succeeded_items(
        self,
        actor_id: str,
        max_age_secs: float,
        max_items: int | None = None,
        input_match: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Dataset items from the actor's most recent SUCCEEDED run, if it
        finished within ``max_age_secs``. Lets slow actors (runs > sync
        timeout) serve slightly stale data instead of failing."""
        run = await self.last_succeeded_run(actor_id, max_age_secs, input_match)
        if not run:
            return []
        return await self.dataset_items(run["defaultDatasetId"], max_items=max_items)

    async def start_run(self, actor_id: str, run_input: dict[str, Any]) -> dict[str, Any] | None:
        """Fire-and-forget actor run; returns the run object or None."""
        actor_path = actor_id.replace("/", "~")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.BASE}/acts/{actor_path}/runs",
                    params={"token": self.token},
                    json=run_input,
                )
                resp.raise_for_status()
                return (resp.json().get("data") or {}) or None
        except httpx.HTTPError:
            return None

    async def find_active_run(
        self, actor_id: str, input_match: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Newest READY/RUNNING run, optionally matching INPUT — used to join
        an in-flight run instead of paying for a duplicate."""
        actor_path = actor_id.replace("/", "~")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE}/acts/{actor_path}/runs",
                    params={"token": self.token, "desc": 1, "limit": 10},
                )
                resp.raise_for_status()
                for run in (resp.json().get("data") or {}).get("items") or []:
                    if run.get("status") not in ("READY", "RUNNING"):
                        continue
                    if input_match:
                        run_input = await self._fetch_run_input(client, run)
                        if any(run_input.get(k) != v for k, v in input_match.items()):
                            continue
                    return run
        except httpx.HTTPError:
            return None
        return None

    async def wait_for_run_items(
        self,
        run_id: str,
        wait_secs: float,
        max_items: int | None = None,
    ) -> list[dict[str, Any]]:
        """Poll a run until it finishes or ``wait_secs`` elapses; returns its
        dataset items on success, [] otherwise (the run keeps going)."""
        deadline = time.monotonic() + wait_secs
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return []
                    resp = await client.get(
                        f"{self.BASE}/actor-runs/{run_id}",
                        params={"token": self.token, "waitForFinish": int(min(60, max(1, remaining)))},
                    )
                    resp.raise_for_status()
                    run = resp.json().get("data") or {}
                    status = run.get("status")
                    if status == "SUCCEEDED":
                        dataset_id = run.get("defaultDatasetId")
                        if not dataset_id:
                            return []
                        return await self.dataset_items(dataset_id, max_items=max_items)
                    if status in ("FAILED", "ABORTED", "ABORTING", "TIMED-OUT"):
                        return []
        except httpx.HTTPError:
            return []

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
