"""Credit deduction & request logging."""

from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any

import structlog
from fastapi import HTTPException

from app.core.auth import ApiCaller
from app.services.response_sampler import maybe_capture
from app.services.supabase_client import get_supabase

log = structlog.get_logger(__name__)

# Per-request billing metadata, published by billed_call and read by the
# response-header middleware (app/main.py) so clients (e.g. the playground) can
# see how a call was served without a DB round-trip. Set once per request in
# the same async context that produces the response.
request_meta: ContextVar[dict[str, Any] | None] = ContextVar(
    "captapi_request_meta", default=None
)

# Keep references to in-flight background log tasks so they aren't GC'd early.
_log_tasks: set[asyncio.Task[Any]] = set()

# Measurement-window endpoints: publish one flat price and charge that on every
# successful path. credits_computed still records what the path would have cost
# so the subsidy (computed − charged) can drive a later reprice.
# Rule: extended <10% keep flat; 10–30% raise flat; >30% fix native path.
PUBLISHED_FLAT: dict[str, int] = {
    "/v1/facebook/event-search": 2,
    "/v1/facebook/profile-events": 2,
    "/v1/truth-social/user-posts": 2,
    "/v1/twitter/community-tweets": 2,
    "/v1/tiktok-shop/shop-search": 2,
    "/v1/tiktok-shop/product-details": 2,
    "/v1/threads/search": 2,
    "/v1/threads/search-users": 1,
    "/v1/threads/user-posts": 2,
}

_SOURCE_PUBLIC = {
    "direct": "native",
    "native": "native",
    "apify": "extended",
    "apify-fallback": "extended",
    "extended": "extended",
}

_DEGRADED_PUBLIC = {
    "apify-fallback": "extended",
    "apify-timeout": "extended-timeout",
    "apify-timeout-served-stale": "extended-timeout-served-stale",
    "extended": "extended",
    "extended-timeout": "extended-timeout",
    "extended-timeout-served-stale": "extended-timeout-served-stale",
}

_PATH_PUBLIC = {
    "apify": "extended",
    "apify-cache": "extended-cache",
    "apify_timeout": "extended-timeout",
    "extended": "extended",
    "extended-cache": "extended-cache",
    "extended-timeout": "extended-timeout",
    "direct": "native",
    "native": "native",
}


def public_source(source: str | None) -> str | None:
    """Customer-facing fetch path — never name infrastructure suppliers."""
    if source is None:
        return None
    return _SOURCE_PUBLIC.get(source, source)


def public_degraded_reason(reason: str | None) -> str | None:
    if reason is None:
        return None
    return _DEGRADED_PUBLIC.get(reason, reason)


def public_timings_path(path: str | None) -> str | None:
    if path is None:
        return None
    return _PATH_PUBLIC.get(path, path)


def rewrite_public_path_fields(data: dict[str, Any] | None) -> None:
    """Mutate response data in place: source / degradedReason / timings.path."""
    if not isinstance(data, dict):
        return
    if "source" in data and data["source"] is not None:
        data["source"] = public_source(str(data["source"]))
    if "degradedReason" in data and data["degradedReason"] is not None:
        data["degradedReason"] = public_degraded_reason(str(data["degradedReason"]))
    if "fetchPath" in data and data["fetchPath"] is not None:
        # ad-library already uses native|fallback — map legacy only.
        fp = str(data["fetchPath"])
        if fp in ("apify", "fallback"):
            data["fetchPath"] = "extended" if fp == "apify" else fp
    timings = data.get("timings")
    if isinstance(timings, dict) and timings.get("path") is not None:
        timings["path"] = public_timings_path(str(timings["path"]))


def resolve_credits(
    *,
    endpoint: str,
    status_code: int,
    cache_hit: bool,
    bill_on_cache_hit: bool,
    credits_override: Any,
    credits_computed: Any,
    base_credits: int,
) -> tuple[int, int]:
    """Return (credits_charged, credits_computed).

    On published-flat endpoints, charge min(computed, published) so the label
    and the meter always agree. Failures and free cache hits stay 0.
    """
    if status_code >= 400:
        computed = int(credits_computed) if credits_computed is not None else 0
        return 0, computed

    if cache_hit and not bill_on_cache_hit:
        computed = int(credits_computed) if credits_computed is not None else 0
        return 0, computed

    # Explicit 0 (empty result) must win — never force the published flat.
    if credits_override is not None and int(credits_override) == 0:
        return 0, 0

    if credits_computed is not None:
        computed = int(credits_computed)
    elif credits_override is not None:
        computed = int(credits_override)
    else:
        computed = int(base_credits)

    published = PUBLISHED_FLAT.get(endpoint)
    if published is not None:
        if computed <= 0:
            return 0, computed
        return min(computed, published), computed

    if credits_override is not None:
        return int(credits_override), computed
    return int(base_credits), computed


def _schedule_background(coro: Any) -> None:
    """Run a coroutine fire-and-forget on the current loop, or inline if none."""
    try:
        task = asyncio.get_running_loop().create_task(coro)
    except RuntimeError:
        return
    _log_tasks.add(task)
    task.add_done_callback(_log_tasks.discard)


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
    request_id: str | None = None,
    credits_computed: int | None = None,
    result_count: int | None = None,
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
        if request_id:
            row["id"] = request_id
        # Optional columns — omit when unset so older schemas keep working.
        if source:
            row["source"] = source
        if credits_computed is not None:
            row["credits_computed"] = credits_computed
        if result_count is not None:
            row["result_count"] = result_count
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
            ctx["credits_computed"] = n  # uncapped path cost (measurement window)
            ctx["result_count"] = n      # list size for subsidy reports
    """
    # Preflight against the published price when capped — never reserve the
    # uncapped extended-path worst case (that blocked low-balance callers).
    reserve = PUBLISHED_FLAT.get(endpoint, base_credits)
    if caller.total_credits < reserve:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "insufficient_credits",
                "required": reserve,
                "available": caller.total_credits,
                "upgrade_url": "/dashboard/billing",
            },
        )

    started = time.perf_counter()
    ctx: dict[str, Any] = {
        "cache_hit": False,
        "credits_override": None,
        "credits_computed": None,
        "result_count": None,
        "source": None,
    }
    status_code = 200
    error: str | None = None
    deduct_failed = False
    billed_amount = reserve
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
        bill_on_cache_hit = bool(ctx.get("bill_on_cache_hit"))
        credits_used, credits_computed = resolve_credits(
            endpoint=endpoint,
            status_code=status_code,
            cache_hit=cache_hit,
            bill_on_cache_hit=bill_on_cache_hit,
            credits_override=ctx.get("credits_override"),
            credits_computed=ctx.get("credits_computed"),
            base_credits=base_credits,
        )
        billed_amount = credits_used

        if credits_used > 0 and status_code < 400:
            ok = deduct_credits(caller.user_id, credits_used)
            if not ok:
                billed_amount = credits_used
                credits_used = 0
                status_code = 402
                deduct_failed = True
                error = "insufficient_credits"

        # Keep source on billed cache hits so dashboards can still see "cache".
        if cache_hit:
            source = public_source(ctx.get("source")) or "cache"
        else:
            source = public_source(ctx.get("source"))
        request_id = str(uuid.uuid4())
        fetched_at = None
        data_obj = ctx.get("data")
        if isinstance(data_obj, dict):
            fetched_at = data_obj.get("fetchedAt")
            rewrite_public_path_fields(data_obj)

        result_count = ctx.get("result_count")
        if result_count is not None:
            try:
                result_count = int(result_count)
            except (TypeError, ValueError):
                result_count = None

        # Publish billing metadata for the response-header middleware. Runs in
        # the same context that serializes the response, so the middleware sees
        # it on http.response.start.
        request_meta.set(
            {
                "source": source,
                "credits": credits_used,
                "credits_computed": credits_computed,
                "cache_hit": cache_hit,
                "status": status_code,
                "request_id": request_id,
                "fetched_at": fetched_at,
            }
        )

        log.info(
            "request_billed",
            endpoint=endpoint,
            path=source,
            result_count=result_count,
            credits_computed=credits_computed,
            credits_charged=credits_used,
            latency_ms=elapsed_ms,
            status_code=status_code,
            cache_hit=cache_hit,
        )

        # Offload the request/credit inserts to a background task so the DB
        # round-trips don't block the response the client is waiting on.
        _schedule_background(
            asyncio.to_thread(
                log_request,
                caller=caller,
                endpoint=endpoint,
                platform=platform,
                resource_url=resource_url,
                credits_used=credits_used,
                cache_hit=cache_hit,
                status_code=status_code,
                response_time_ms=elapsed_ms,
                error_message=error,
                source=source,
                request_id=request_id,
                credits_computed=credits_computed,
                result_count=result_count,
            )
        )

        # Optional response-body capture for funnel / auditing (fire-and-forget).
        maybe_capture(
            user_id=caller.user_id,
            api_key_id=caller.api_key_id,
            endpoint=endpoint,
            platform=platform,
            resource_url=resource_url,
            source=source,
            status_code=status_code,
            response_time_ms=elapsed_ms,
            cache_hit=cache_hit,
            data=ctx.get("data"),
            request_id=request_id,
        )

    if deduct_failed:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "insufficient_credits",
                "required": billed_amount,
                "available": caller.total_credits,
                "upgrade_url": "/dashboard/billing",
            },
        )
