"""Account / usage / limits endpoints (called by dashboard + customer apps)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.auth import ApiCaller, require_api_key
from app.schemas.common import ApiResponse
from app.services.supabase_client import get_supabase

router = APIRouter()

PLAN_QUOTAS = {
    "free": 100,
    "starter": 2_000,
    "pro": 6_000,
    "business": 20_000,
}


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
            "balance": {
                "plan": b.get("plan", "free"),
                "subscription_credits": b.get("subscription_credits", 0),
                "topup_credits": b.get("topup_credits", 0),
                "total_credits": (b.get("subscription_credits", 0) or 0)
                + (b.get("topup_credits", 0) or 0),
                "subscription_renews_at": b.get("subscription_renews_at"),
            },
            "recent_requests": reqs.data or [],
        }
    )


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
