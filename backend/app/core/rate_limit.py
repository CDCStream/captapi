"""Per-API-key rate limiting (token bucket via Redis INCR)."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.core.auth import ApiCaller
from app.core.config import get_settings
from app.services.cache import rate_limit_hit


async def enforce_rate_limit(caller: ApiCaller) -> None:
    settings = get_settings()
    limit = settings.rate_limit_for_plan(caller.plan)
    scope = f"key:{caller.api_key_id}" if caller.api_key_id else f"user:{caller.user_id}"
    blocked = await rate_limit_hit(
        scope=scope,
        limit=limit,
        window_seconds=60,
    )
    if blocked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "plan": caller.plan,
                "limit_per_minute": limit,
                "retry_after_seconds": 60,
            },
            headers={"Retry-After": "60"},
        )
