"""Generic 'cache or call Apify' helper used by every endpoint."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from app.services.cache import cache_get, cache_set, make_cache_key


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
    """
    key = make_cache_key(endpoint, params)
    cached = await cache_get(key)
    if cached is not None:
        ctx["cache_hit"] = True
        return cached

    result = await runner()
    await cache_set(key, result, ttl=ttl)
    return result
