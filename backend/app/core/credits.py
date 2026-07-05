"""Credit deduction & request logging."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import HTTPException

from app.core.auth import ApiCaller
from app.services.supabase_client import get_supabase

log = structlog.get_logger(__name__)


def deduct_credits(user_id: str, amount: int) -> bool:
    """Atomically deduct `amount` credits via RPC. Returns True on success."""
    sb = get_supabase()
    res = sb.rpc("deduct_credits", {"p_user_id": user_id, "p_amount": amount}).execute()
    deducted = int(res.data or 0)
    return deducted == amount


def log_request(
    *,
    caller: ApiCaller,
    endpoint: str,
    platform: str | None,
    resource_url: str | None,
    credits_used: int,
    cache_hit: bool,
    status_code: int,
    response_time_ms: int,
    error_message: str | None = None,
    source: str | None = None,
) -> None:
    sb = get_supabase()
    try:
        row: dict[str, Any] = {
            "user_id": caller.user_id,
            "api_key_id": caller.api_key_id,
            "endpoint": endpoint,
            "platform": platform,
            "resource_url": resource_url,
            "credits_used": credits_used,
            "cache_hit": cache_hit,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "error_message": error_message,
        }
        # Only sent when set, so logging keeps working if the 0015 migration
        # (requests.source column) hasn't been applied yet.
        if source:
            row["source"] = source
        sb.table("requests").insert(row).execute()

        if credits_used > 0 and not cache_hit:
            sb.table("credit_transactions").insert(
                {
                    "user_id": caller.user_id,
                    "type": "usage",
                    "amount": -credits_used,
                    "description": f"{endpoint} ({platform or 'n/a'})",
                }
            ).execute()
    except Exception as e:
        log.error("log_request_failed", error=str(e))


@asynccontextmanager
async def billed_call(
    *,
    caller: ApiCaller,
    endpoint: str,
    platform: str,
    resource_url: str | None,
    base_credits: int,
):
    """
    Context manager that:
      1. Verifies caller has enough credits BEFORE work starts
      2. Deducts credits AFTER successful call (so failed calls don't bill)
      3. Logs the request with timing
    Usage:
        async with billed_call(...) as ctx:
            data = await scrape()
            ctx["data"] = data           # success
            ctx["cache_hit"] = bool      # mark cache hit -> 0 credit
    """
    if caller.total_credits < base_credits:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "insufficient_credits",
                "required": base_credits,
                "available": caller.total_credits,
                "upgrade_url": "/dashboard/billing",
            },
        )

    started = time.perf_counter()
    ctx: dict[str, Any] = {"cache_hit": False, "credits_override": None, "source": None}
    status_code = 200
    error: str | None = None
    try:
        yield ctx
    except HTTPException as e:
        status_code = e.status_code
        error = str(e.detail)[:500]
        raise
    except Exception as e:
        status_code = 500
        error = str(e)[:500]
        raise
    finally:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        cache_hit = bool(ctx.get("cache_hit"))
        credits_used = 0 if cache_hit else (ctx.get("credits_override") or base_credits)

        if credits_used > 0 and status_code < 400:
            ok = deduct_credits(caller.user_id, credits_used)
            if not ok:
                credits_used = 0
                status_code = 402

        log_request(
            caller=caller,
            endpoint=endpoint,
            platform=platform,
            resource_url=resource_url,
            credits_used=credits_used,
            cache_hit=cache_hit,
            status_code=status_code,
            response_time_ms=elapsed_ms,
            error_message=error,
            source=None if cache_hit else ctx.get("source"),
        )
