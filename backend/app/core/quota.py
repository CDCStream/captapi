"""Daily usage quotas (Redis-backed), separate from per-minute rate limits."""

from __future__ import annotations

import structlog
from fastapi import HTTPException, status

from app.services.cache import get_redis

log = structlog.get_logger(__name__)

DAY_SECONDS = 86_400


async def daily_count(scope: str, window_seconds: int = DAY_SECONDS) -> int:
    key = f"sk:quota:{scope}:{window_seconds}"
    try:
        raw = await get_redis().get(key)
        return int(raw or 0)
    except Exception as e:
        log.warning("daily_quota_read_failed", error=str(e), scope=scope)
        return 0


async def check_daily_quota(
    scope: str,
    *,
    limit: int,
    window_seconds: int = DAY_SECONDS,
    error: str = "daily_quota_exceeded",
    upgrade_url: str = "/dashboard/billing",
) -> None:
    """Raise 429 if `scope` has already used `limit` units in the window."""
    if limit <= 0:
        return
    count = await daily_count(scope, window_seconds)
    if count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": error,
                "limit": limit,
                "used": count,
                "window_seconds": window_seconds,
                "upgrade_url": upgrade_url,
            },
            headers={"Retry-After": str(window_seconds)},
        )


async def consume_daily_quota(
    scope: str,
    *,
    limit: int,
    window_seconds: int = DAY_SECONDS,
) -> int:
    """Increment the daily counter. Returns the new count (0 on Redis failure)."""
    if limit <= 0:
        return 0
    key = f"sk:quota:{scope}:{window_seconds}"
    try:
        r = get_redis()
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, window_seconds)
        return int(count)
    except Exception as e:
        log.warning("daily_quota_incr_failed", error=str(e), scope=scope)
        return 0
