"""Account / usage / limits endpoints (called by dashboard + customer apps)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, Query

from app.core.auth import ApiCaller, require_api_key
from app.schemas.common import ApiResponse
from app.services.email_client import send_welcome_email
from app.services.supabase_client import get_supabase

router = APIRouter()
log = structlog.get_logger(__name__)

PLAN_QUOTAS = {
    "free": 100,
    "starter": 2_000,
    "pro": 6_000,
    "business": 20_000,
}


def _balance_payload(row: dict | None, caller: ApiCaller) -> dict:
    b = row or {}
    subscription = b.get("subscription_credits", caller.subscription_credits) or 0
    topup = b.get("topup_credits", caller.topup_credits) or 0
    return {
        "plan": b.get("plan", caller.plan),
        "monthly_quota": PLAN_QUOTAS.get(b.get("plan", caller.plan), 100),
        "subscription_credits": subscription,
        "topup_credits": topup,
        "total_credits": subscription + topup,
        "subscription_renews_at": b.get("subscription_renews_at"),
    }


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@router.get("/usage", summary="Current credit balance + recent requests")
async def get_usage(
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    sb = get_supabase()
    bal = (
        sb.table("credit_balances")
        .select("plan, subscription_credits, topup_credits, subscription_renews_at")
        .eq("user_id", caller.user_id)
        .limit(1)
        .execute()
    )
    b = bal.data[0] if bal.data else {}

    reqs = (
        sb.table("requests")
        .select("endpoint, platform, resource_url, credits_used, cache_hit, status_code, response_time_ms, created_at")
        .eq("user_id", caller.user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return ApiResponse(
        data={
            "balance": _balance_payload(b, caller),
            "recent_requests": reqs.data or [],
        }
    )


@router.get("/balance", summary="Get credit balance")
async def get_credit_balance(caller: ApiCaller = Depends(require_api_key)):
    sb = get_supabase()
    bal = (
        sb.table("credit_balances")
        .select("plan, subscription_credits, topup_credits, subscription_renews_at")
        .eq("user_id", caller.user_id)
        .limit(1)
        .execute()
    )
    return ApiResponse(data=_balance_payload(bal.data[0] if bal.data else None, caller))


@router.get("/request-history", summary="Get request history")
async def get_request_history(
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    reqs = (
        get_supabase()
        .table("requests")
        .select("endpoint, platform, resource_url, credits_used, cache_hit, status_code, response_time_ms, error_message, created_at")
        .eq("user_id", caller.user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return ApiResponse(data={"totalReturned": len(reqs.data or []), "requests": reqs.data or []})


@router.get("/daily-usage", summary="Get daily credit usage")
async def get_daily_usage(
    days: int = Query(30, ge=1, le=365),
    caller: ApiCaller = Depends(require_api_key),
):
    since = datetime.now(timezone.utc) - timedelta(days=days - 1)
    reqs = (
        get_supabase()
        .table("requests")
        .select("endpoint, platform, credits_used, status_code, created_at")
        .eq("user_id", caller.user_id)
        .gte("created_at", since.date().isoformat())
        .order("created_at", desc=False)
        .limit(5000)
        .execute()
    )
    buckets: dict[str, dict] = {}
    for row in reqs.data or []:
        dt = _parse_dt(row.get("created_at"))
        day = (dt.date().isoformat() if dt else str(row.get("created_at", ""))[:10])
        bucket = buckets.setdefault(day, {"date": day, "requests": 0, "credits_used": 0, "successful_requests": 0, "failed_requests": 0})
        bucket["requests"] += 1
        bucket["credits_used"] += row.get("credits_used") or 0
        if (row.get("status_code") or 0) < 400:
            bucket["successful_requests"] += 1
        else:
            bucket["failed_requests"] += 1
    usage = [buckets[k] for k in sorted(buckets)]
    return ApiResponse(
        data={
            "days": days,
            "totalRequests": sum(d["requests"] for d in usage),
            "totalCreditsUsed": sum(d["credits_used"] for d in usage),
            "usage": usage,
        }
    )


@router.get("/most-used-routes", summary="Get most used API routes")
async def get_most_used_routes(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    since = datetime.now(timezone.utc) - timedelta(days=days - 1)
    reqs = (
        get_supabase()
        .table("requests")
        .select("endpoint, platform, credits_used, status_code, created_at")
        .eq("user_id", caller.user_id)
        .gte("created_at", since.date().isoformat())
        .limit(5000)
        .execute()
    )
    routes: dict[str, dict] = {}
    for row in reqs.data or []:
        endpoint = row.get("endpoint") or "unknown"
        route = routes.setdefault(
            endpoint,
            {"endpoint": endpoint, "platform": row.get("platform"), "requests": 0, "credits_used": 0, "successful_requests": 0, "failed_requests": 0},
        )
        route["requests"] += 1
        route["credits_used"] += row.get("credits_used") or 0
        if (row.get("status_code") or 0) < 400:
            route["successful_requests"] += 1
        else:
            route["failed_requests"] += 1
    ranked = sorted(routes.values(), key=lambda r: (r["requests"], r["credits_used"]), reverse=True)[:limit]
    return ApiResponse(data={"days": days, "totalReturned": len(ranked), "routes": ranked})


@router.post("/welcome", summary="Send the one-time welcome email (idempotent)")
async def send_welcome(caller: ApiCaller = Depends(require_api_key)):
    """Sends a welcome email once per user. Safe to call on every dashboard load."""
    sb = get_supabase()
    bal = (
        sb.table("credit_balances")
        .select("welcomed_at")
        .eq("user_id", caller.user_id)
        .limit(1)
        .execute()
    )
    if bal.data and bal.data[0].get("welcomed_at"):
        return ApiResponse(data={"sent": False, "reason": "already_sent"})

    user_res = sb.auth.admin.get_user_by_id(caller.user_id)
    user = user_res.user if user_res else None
    email = user.email if user else None
    if not email:
        return ApiResponse(data={"sent": False, "reason": "no_email"})

    meta = getattr(user, "user_metadata", None) or {}
    name = (
        meta.get("first_name")
        or meta.get("full_name")
        or meta.get("name")
        or email.split("@")[0]
    )
    sent = send_welcome_email(email, name)
    if sent:
        sb.table("credit_balances").update(
            {"welcomed_at": datetime.now(timezone.utc).isoformat()}
        ).eq("user_id", caller.user_id).execute()
        log.info("welcome_email_sent", user_id=caller.user_id)
    return ApiResponse(data={"sent": sent})


@router.get("/limits", summary="Plan quotas + remaining credits")
async def get_limits(caller: ApiCaller = Depends(require_api_key)):
    plan_quota = PLAN_QUOTAS.get(caller.plan, 100)
    return ApiResponse(
        data={
            "plan": caller.plan,
            "monthly_quota": plan_quota,
            "subscription_credits_remaining": caller.subscription_credits,
            "topup_credits_remaining": caller.topup_credits,
            "total_credits_remaining": caller.total_credits,
        }
    )
