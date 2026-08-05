"""Account / usage / limits endpoints (called by dashboard + customer apps)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
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


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _used_this_period(user_id: str, since: datetime | None) -> int:
    """Sum credits_used since ``since`` (or the last 30 days when unset)."""
    try:
        sb = get_supabase()
        start = since or (datetime.now(timezone.utc) - timedelta(days=30))
        # Normalize to ISO date for the gte filter (matches daily-usage pattern).
        since_iso = start.date().isoformat() if hasattr(start, "date") else str(start)[:10]
        reqs = (
            sb.table("requests")
            .select("credits_used, created_at")
            .eq("user_id", user_id)
            .gte("created_at", since_iso)
            .limit(5000)
            .execute()
        )
        return sum(int(row.get("credits_used") or 0) for row in (reqs.data or []))
    except Exception:  # noqa: BLE001 — never fail balance on usage sum
        log.warning("balance_used_this_period_failed", user_id=user_id)
        return 0


def _key_name(api_key_id: str | None) -> str | None:
    if not api_key_id:
        return None
    try:
        res = (
            get_supabase()
            .table("api_keys")
            .select("name")
            .eq("id", api_key_id)
            .limit(1)
            .execute()
        )
        if not res.data:
            return None
        return res.data[0].get("name")
    except Exception:  # noqa: BLE001
        return None


def _balance_payload(row: dict | None, caller: ApiCaller) -> dict:
    """Public balance shape — camelCase (+ snake_case aliases for one release)."""
    b = row or {}
    subscription = b.get("subscription_credits", caller.subscription_credits) or 0
    topup = b.get("topup_credits", caller.topup_credits) or 0
    plan = b.get("plan", caller.plan)
    renews = b.get("subscription_renews_at")
    renews_dt = _parse_dt(renews) if isinstance(renews, str) else None
    monthly_quota = PLAN_QUOTAS.get(plan, 100)
    used = _used_this_period(caller.user_id, renews_dt)
    rate_limit = get_settings().rate_limit_for_plan(plan)
    key_name = _key_name(caller.api_key_id)
    payload = {
        "plan": plan,
        "monthlyQuota": monthly_quota,
        "subscriptionCredits": subscription,
        "topupCredits": topup,
        "totalCredits": subscription + topup,
        "subscriptionRenewsAt": renews,
        # Alerting helpers
        "usedThisMonth": used,
        "quotaResetsAt": renews,  # same instant as subscriptionRenewsAt when set
        "keyName": key_name,
        "rateLimitPerMinute": rate_limit,
        # Remaining RPM is enforced in Redis per window — not snapshotted here.
        "rateLimitRemaining": None,
    }
    # Deprecated snake_case aliases (one release) — prefer camelCase.
    payload.update(
        {
            "monthly_quota": payload["monthlyQuota"],
            "subscription_credits": payload["subscriptionCredits"],
            "topup_credits": payload["topupCredits"],
            "total_credits": payload["totalCredits"],
            "subscription_renews_at": payload["subscriptionRenewsAt"],
        }
    )
    return payload


def _request_row(row: dict) -> dict:
    """Map a ``requests`` DB row to the public camelCase shape.

    ``resource`` is the logged identifier — a public URL when the call had one,
    otherwise an internal cache key (e.g. ``instagram_user:handle``). ``resourceUrl``
    is a deprecated alias of the same value for one release.
    """
    resource = row.get("resource_url")
    return {
        "requestId": row.get("id"),
        "endpoint": row.get("endpoint"),
        "platform": row.get("platform"),
        "resource": resource,
        # Deprecated alias — prefer ``resource`` (not always a URL).
        "resourceUrl": resource,
        "creditsUsed": row.get("credits_used") or 0,
        "cacheHit": bool(row.get("cache_hit")),
        "statusCode": row.get("status_code"),
        "responseTimeMs": row.get("response_time_ms"),
        "errorMessage": row.get("error_message"),
        "createdAt": row.get("created_at"),
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
        .select(
            "id, endpoint, platform, resource_url, credits_used, cache_hit, "
            "status_code, response_time_ms, error_message, created_at"
        )
        .eq("user_id", caller.user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return ApiResponse(
        data={
            "balance": _balance_payload(b, caller),
            "recentRequests": [_request_row(r) for r in (reqs.data or [])],
        }
    )


@router.get(
    "/balance",
    summary="Get credit balance",
    description=(
        "Live credit balance for the calling API key — never cached. camelCase "
        "fields are canonical; snake_case aliases are emitted for one release. "
        "Includes usedThisMonth, quotaResetsAt, keyName, and rateLimitPerMinute "
        "for usage alerting. 0 credits."
    ),
)
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


@router.get(
    "/request-history",
    summary="Get request history",
    description=(
        "Live (never cached) request log for the calling key owner — 0 credits. "
        "Each row includes requestId (same UUID as the response envelope / "
        "x-captapi-request-id header) for support matching. Filter with "
        "endpoint, statusCode, since, and until. resource is a URL or an "
        "internal cache key — not always a URL."
    ),
)
async def get_request_history(
    limit: int = Query(50, ge=1, le=500, description="Max rows (default 50, max 500). Free."),
    endpoint: str | None = Query(
        None,
        description="Exact Captapi path filter, e.g. /v1/instagram/basic-profile",
    ),
    statusCode: int | None = Query(
        None,
        ge=100,
        le=599,
        description="Filter by HTTP status code (e.g. 500 for 5xx investigation).",
    ),
    since: str | None = Query(
        None,
        description="Inclusive lower bound on createdAt (ISO date or datetime).",
    ),
    until: str | None = Query(
        None,
        description="Exclusive upper bound on createdAt (ISO date or datetime).",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    q = (
        get_supabase()
        .table("requests")
        .select(
            "id, endpoint, platform, resource_url, credits_used, cache_hit, "
            "status_code, response_time_ms, error_message, created_at"
        )
        .eq("user_id", caller.user_id)
    )
    ep_filter = (endpoint or "").strip()
    if ep_filter:
        q = q.eq("endpoint", ep_filter)
    if statusCode is not None:
        q = q.eq("status_code", statusCode)
    since_s = (since or "").strip()
    if since_s:
        q = q.gte("created_at", since_s)
    until_s = (until or "").strip()
    if until_s:
        q = q.lt("created_at", until_s)
    reqs = q.order("created_at", desc=True).limit(limit).execute()
    rows = [_request_row(r) for r in (reqs.data or [])]
    return ApiResponse(
        data={
            "totalReturned": len(rows),
            "filters": {
                "endpoint": ep_filter or None,
                "statusCode": statusCode,
                "since": since_s or None,
                "until": until_s or None,
                "limit": limit,
            },
            "requests": rows,
        }
    )


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
        bucket = buckets.setdefault(
            day,
            {
                "date": day,
                "requests": 0,
                "creditsUsed": 0,
                "successfulRequests": 0,
                "failedRequests": 0,
            },
        )
        bucket["requests"] += 1
        bucket["creditsUsed"] += row.get("credits_used") or 0
        if (row.get("status_code") or 0) < 400:
            bucket["successfulRequests"] += 1
        else:
            bucket["failedRequests"] += 1
    usage = [buckets[k] for k in sorted(buckets)]
    return ApiResponse(
        data={
            "days": days,
            "totalRequests": sum(d["requests"] for d in usage),
            "totalCreditsUsed": sum(d["creditsUsed"] for d in usage),
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
            {
                "endpoint": endpoint,
                "platform": row.get("platform"),
                "requests": 0,
                "creditsUsed": 0,
                "successfulRequests": 0,
                "failedRequests": 0,
            },
        )
        route["requests"] += 1
        route["creditsUsed"] += row.get("credits_used") or 0
        if (row.get("status_code") or 0) < 400:
            route["successfulRequests"] += 1
        else:
            route["failedRequests"] += 1
    ranked = sorted(routes.values(), key=lambda r: (r["requests"], r["creditsUsed"]), reverse=True)[:limit]
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
            "monthlyQuota": plan_quota,
            "subscriptionCreditsRemaining": caller.subscription_credits,
            "topupCreditsRemaining": caller.topup_credits,
            "totalCreditsRemaining": caller.total_credits,
            "rateLimitPerMinute": get_settings().rate_limit_for_plan(caller.plan),
        }
    )
