"""Fire-and-forget response-body sampling for correctness auditing.

When ``LOG_RESPONSE_BODIES`` is on, a fraction (``LOG_RESPONSE_SAMPLE_RATE``) of
endpoint responses is copied into ``public.response_samples`` so we can later
evaluate scraper output quality (e.g. compare native vs Apify field coverage,
optionally with AI). Writes run on a background thread task and never block or
fail the request. Bodies larger than ``LOG_RESPONSE_MAX_BYTES`` are recorded as
truncated (metadata only, no payload) to keep the table light.

Meant to be temporary: flip the flag off and drop the table when done.
"""

from __future__ import annotations

import asyncio
import json
import random
from typing import Any

import structlog

from app.core.config import get_settings
from app.services.supabase_client import get_supabase

log = structlog.get_logger(__name__)

# Keep references to in-flight tasks so they aren't garbage-collected mid-write.
_tasks: set[asyncio.Task[Any]] = set()


def _insert_sync(row: dict[str, Any]) -> None:
    get_supabase().table("response_samples").insert(row).execute()


async def _write(row: dict[str, Any]) -> None:
    try:
        await asyncio.to_thread(_insert_sync, row)
    except Exception as exc:  # noqa: BLE001 -- table missing / transient DB error
        log.info("response_sample_skip", endpoint=row.get("endpoint"), error=str(exc)[:200])


def maybe_capture(
    *,
    user_id: str | None,
    api_key_id: str | None,
    endpoint: str,
    platform: str | None,
    resource_url: str | None,
    source: str | None,
    status_code: int,
    response_time_ms: int,
    cache_hit: bool,
    data: Any,
) -> None:
    """Schedule a sampled response-body write. Never raises, never blocks.

    Only fires when the feature flag is on, the sample-rate lottery passes, and
    we actually have a response body to store.
    """
    settings = get_settings()
    if not settings.LOG_RESPONSE_BODIES or data is None:
        return
    if random.random() > settings.LOG_RESPONSE_SAMPLE_RATE:
        return

    row: dict[str, Any] = {
        "user_id": user_id,
        "api_key_id": api_key_id,
        "endpoint": endpoint,
        "platform": platform,
        "resource_url": resource_url,
        "source": source,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "cache_hit": cache_hit,
        "truncated": False,
        "response_json": None,
    }

    # Size-cap on the serialized body; oversized payloads are logged as
    # metadata-only so we can still see which endpoints blow the budget.
    try:
        encoded = json.dumps(data, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return
    if len(encoded.encode("utf-8")) > settings.LOG_RESPONSE_MAX_BYTES:
        row["truncated"] = True
    else:
        row["response_json"] = data

    try:
        task = asyncio.get_running_loop().create_task(_write(row))
    except RuntimeError:
        return  # no running loop (sync/test context) -- skip silently
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
