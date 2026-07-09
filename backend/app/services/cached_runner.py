"""Generic 'cache or call Apify' helper used by every endpoint."""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from app.services.cache import (
    cache_get,
    cache_set,
    cache_try_lock,
    default_ttl_for,
    make_cache_key,
)

# How much longer the stale copy outlives the fresh TTL, and how long a
# background-refresh lock is held (guards against duplicate refreshes).
_STALE_TTL_FACTOR = 4
_REFRESH_LOCK_SECONDS = 300

# Strong references so in-flight refresh tasks aren't garbage-collected.
_refresh_tasks: set[asyncio.Task] = set()


async def cached_or_run(
    endpoint: str,
    params: dict[str, Any],
    runner: Callable[[], Awaitable[dict[str, Any]]],
    ctx: dict[str, Any],
    ttl: int | None = None,
    stale_while_revalidate: bool = False,
) -> dict[str, Any]:
    """
    Look up cache; if miss, run `runner()` and store result.
    Sets `ctx["cache_hit"] = True` on hit so credits are not billed.

    When `ttl` is not given, a TTL is chosen from the endpoint's time
    sensitivity (see `default_ttl_for`). A TTL <= 0 disables caching for that
    endpoint so time-varying data (e.g. like counts) is always fetched fresh.

    `stale_while_revalidate=True` keeps a longer-lived stale copy: when the
    fresh entry expires, the stale payload is returned immediately and a
    background task re-runs `runner()` to repopulate the cache. Meant for
    slow trending-style endpoints (200s+ actor runs) with low param
    cardinality, where making a caller wait minutes for a marginally fresher
    list is a bad trade.
    """
    effective_ttl = ttl if ttl is not None else default_ttl_for(endpoint)

    key = make_cache_key(endpoint, params)
    stale_key = key + ":stale"
    if effective_ttl > 0:
        cached = await cache_get(key)
        if cached is not None:
            ctx["cache_hit"] = True
            # Expose payload for optional response-body sampling (see
            # response_sampler.maybe_capture, called from billed_call).
            ctx["data"] = cached
            return cached
        if stale_while_revalidate:
            stale = await cache_get(stale_key)
            if stale is not None:
                ctx["cache_hit"] = True
                ctx["data"] = stale
                _spawn_refresh(key, stale_key, runner, effective_ttl)
                return stale

    result = await runner()
    ctx["data"] = result
    if effective_ttl > 0 and not _looks_empty(result):
        await cache_set(key, result, ttl=effective_ttl)
        if stale_while_revalidate:
            await cache_set(stale_key, result, ttl=effective_ttl * _STALE_TTL_FACTOR)

    # Free by-product: fresh fetches of tracked profile/post endpoints feed
    # the /v1/history time series (fire-and-forget, never blocks).
    from app.services.metric_history import maybe_record

    maybe_record(endpoint, params, result)
    return result


def _spawn_refresh(
    key: str,
    stale_key: str,
    runner: Callable[[], Awaitable[dict[str, Any]]],
    ttl: int,
) -> None:
    """Fire-and-forget cache repopulation after serving a stale payload."""

    async def _refresh() -> None:
        try:
            # First stale hit wins; concurrent requests skip the refresh.
            if not await cache_try_lock(key + ":refreshing", _REFRESH_LOCK_SECONDS):
                return
            result = await runner()
            if not _looks_empty(result):
                await cache_set(key, result, ttl=ttl)
                await cache_set(stale_key, result, ttl=ttl * _STALE_TTL_FACTOR)
        except Exception:  # noqa: BLE001 — stale copy already served; retry on next hit
            pass

    task = asyncio.create_task(_refresh())
    _refresh_tasks.add(task)
    task.add_done_callback(_refresh_tasks.discard)


def _looks_empty(result: Any) -> bool:
    """True for list-endpoint payloads with zero rows.

    Upstream actors occasionally return an empty dataset on a transient
    block/proxy failure; caching that would pin the endpoint to an empty
    response for the whole TTL. Skipping the cache write only costs a re-run
    on the next call.
    """
    return isinstance(result, dict) and result.get("totalReturned") == 0
