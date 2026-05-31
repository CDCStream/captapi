"""Generic 'cache or call Apify' helper used by every endpoint."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from app.services.cache import (
    cache_get,
    cache_set,
    default_ttl_for,
    make_cache_key,
)


async def cached_or_run(
    endpoint: str,
    params: dict[str, Any],
    runner: Callable[[], Awaitable[dict[str, Any]]],
    ctx: dict[str, Any],
    ttl: int | None = None,
) -> dict[str, Any]:
    """
    Look up cache; if miss, run `runner()` and store result.
    Sets `ctx["cache_hit"] = True` on hit so credits are not billed.

    When `ttl` is not given, a TTL is chosen from the endpoint's time
    sensitivity (see `default_ttl_for`). A TTL <= 0 disables caching for that
    endpoint so time-varying data (e.g. like counts) is always fetched fresh.
    """
    effective_ttl = ttl if ttl is not None else default_ttl_for(endpoint)

    key = make_cache_key(endpoint, params)
    if effective_ttl > 0:
        cached = await cache_get(key)
        if cached is not None:
            ctx["cache_hit"] = True
            return cached

    result = await runner()
    if effective_ttl > 0:
        await cache_set(key, result, ttl=effective_ttl)
    return result
