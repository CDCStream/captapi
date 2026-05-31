"""Redis-backed 24h cache with sha256 keys. Falls back gracefully if Redis is down."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from typing import Any

import redis.asyncio as redis
import structlog

from app.core.config import get_settings

log = structlog.get_logger(__name__)


@lru_cache
def get_redis() -> redis.Redis:
    settings = get_settings()
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def make_cache_key(endpoint: str, params: dict[str, Any]) -> str:
    """Stable cache key from endpoint + sorted params."""
    items = sorted((k, str(v)) for k, v in params.items() if v is not None)
    raw = endpoint + "?" + "&".join(f"{k}={v}" for k, v in items)
    return "sk:cache:" + hashlib.sha256(raw.encode()).hexdigest()


# Endpoints whose payload never changes once published -> safe to cache long.
_STATIC_KINDS = {"transcript", "summarize"}
# Endpoints returning short-lived signed media URLs.
_VOLATILE_KINDS = {"video-download"}


def default_ttl_for(endpoint: str) -> int:
    """Pick a cache TTL based on how time-sensitive an endpoint's data is.

    Endpoints carry engagement metrics (likes/views/followers/comments) that
    change over time, so they get the short DYNAMIC TTL (which can be set to 0
    to disable caching). Transcripts/summaries are immutable -> STATIC.
    """
    settings = get_settings()
    kind = endpoint.rsplit(".", 1)[-1]
    if kind in _STATIC_KINDS:
        return settings.CACHE_TTL_STATIC
    if kind in _VOLATILE_KINDS:
        return settings.CACHE_TTL_VOLATILE
    return settings.CACHE_TTL_DYNAMIC


async def cache_get(key: str) -> dict[str, Any] | None:
    try:
        raw = await get_redis().get(key)
        return json.loads(raw) if raw else None
    except Exception as e:
        log.warning("cache_get_failed", error=str(e), key=key)
        return None


async def cache_set(key: str, value: dict[str, Any], ttl: int | None = None) -> None:
    settings = get_settings()
    try:
        await get_redis().set(key, json.dumps(value), ex=ttl or settings.CACHE_TTL_SECONDS)
    except Exception as e:
        log.warning("cache_set_failed", error=str(e), key=key)


async def rate_limit_hit(scope: str, limit: int, window_seconds: int = 60) -> bool:
    """Sliding window rate limit using Redis INCR + EXPIRE.
    Returns True if request should be blocked (limit exceeded)."""
    key = f"sk:rl:{scope}:{window_seconds}"
    try:
        r = get_redis()
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, window_seconds)
        return count > limit
    except Exception as e:
        log.warning("rate_limit_check_failed", error=str(e))
        return False
