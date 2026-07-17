"""Billing: checkout, customer portal, subscription lifecycle, and webhooks.

Provider-agnostic — the active merchant of record is selected by
settings.PAYMENT_PROVIDER (see app.services.payments). All DB writes here use
the active provider's id columns, so switching providers needs no changes here.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from app.core.config import get_settings
from app.routers.auth_keys import _user_from_jwt
from app.services.payments import SUBSCRIPTION_CREDITS, WebhookEvent, get_provider
from app.services.supabase_client import get_supabase

router = APIRouter()
log = structlog.get_logger(__name__)


class CheckoutBody(BaseModel):
    # Either a subscription (plan + cycle) or a one-time pack.
    plan: str | None = None  # "starter" | "pro" | "business"
    cycle: str = "monthly"  # "monthly" | "yearly"
    pack: str | None = None  # "starter" | "growth" | "scale"
    success_url: str | None = None


class ChangePlanBody(BaseModel):
    plan: str  # "starter" | "pro" | "business"
    cycle: str = "monthly"  # "monthly" | "yearly"


def _existing_customer_id(user_id: str) -> str | None:
    p = get_provider()
    sb = get_supabase()
    res = (
        sb.table("subscriptions")
        .select(p.customer_col)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if res.data and res.data[0].get(p.customer_col):
        return res.data[0][p.customer_col]
    return None


def _subscription_record(user_id: str) -> dict | None:
    p = get_provider()
    sb = get_supabase()
    res = (
        sb.table("subscriptions")
        .select(
            f"{p.subscription_col}, {p.customer_col}, status, plan, "
            "current_period_end, cancel_at_period_end"
        )
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def _subscription_id(record: dict | None) -> str | None:
    return record.get(get_provider().subscription_col) if record else None


@router.post("/checkout", summary="Create a checkout session")
async def create_checkout(
    body: CheckoutBody,
    authorization: str | None = Header(default=None),
):
    settings = get_settings()
    p = get_provider()
    user_id = await _user_from_jwt(authorization)
    sb = get_supabase()

    item = (
        p.resolve_pack(body.pack)
        if body.pack
        else p.resolve_subscription(body.plan or "", body.cycle)
    )
    if not item:
        raise HTTPException(
            status_code=400,
            detail="Unknown or unconfigured product. Check the matching price/product env var.",
        )

    user_res = sb.auth.admin.get_user_by_id(user_id)
    email = user_res.user.email if user_res and user_res.user else None
    customer_id = _existing_customer_id(user_id)

    return_url = (
        body.success_url or f"{settings.FRONTEND_URL}/dashboard/billing?status=success"
    )

    metadata = {
        "user_id": user_id,
        "kind": item.kind,
        "credits": str(item.credits),
    }
    if item.plan:
        metadata["plan"] = item.plan

    try:
        result = p.create_checkout(
            item=item,
            user_id=user_id,
            email=email,
            customer_id=customer_id,
            return_url=return_url,
            metadata=metadata,
        )
    except Exception as e:  # noqa: BLE001
        log.error("checkout_failed", provider=p.name, error=str(e))
        raise HTTPException(status_code=502, detail=f"Checkout failed: {e}") from e

    return {
        "provider": result.provider,
        "url": result.url,
        "transaction_id": result.transaction_id,
    }


@router.post("/portal", summary="Create a customer billing portal session")
async def create_portal(authorization: str | None = Header(default=None)):
    user_id = await _user_from_jwt(authorization)
    customer_id = _existing_customer_id(user_id)
    if not customer_id:
        raise HTTPException(status_code=404, detail="No billing customer found yet")
    try:
        url = get_provider().create_portal(customer_id)
    except Exception as e:  # noqa: BLE001
        log.error("portal_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Portal failed: {e}") from e
    return {"url": url}


@router.get("/subscription", summary="Current subscription status")
async def get_subscription(authorization: str | None = Header(default=None)):
    user_id = await _user_from_jwt(authorization)
    record = _subscription_record(user_id)
    if not record or not _subscription_id(record):
        return {"active": False, "plan": "free"}
    return {
        "active": record.get("status") == "active",
        "status": record.get("status"),
        "plan": record.get("plan"),
        "current_period_end": record.get("current_period_end"),
        "cancel_at_period_end": bool(record.get("cancel_at_period_end")),
    }


@router.post("/subscription/cancel", summary="Cancel at end of billing period")
async def cancel_subscription(authorization: str | None = Header(default=None)):
    user_id = await _user_from_jwt(authorization)
    sub_id = _subscription_id(_subscription_record(user_id))
    if not sub_id:
        raise HTTPException(status_code=404, detail="No active subscription")
    try:
        get_provider().cancel(sub_id)
    except Exception as e:  # noqa: BLE001
        log.error("cancel_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Cancel failed: {e}") from e

    get_supabase().table("subscriptions").update(
        {"cancel_at_period_end": True}
    ).eq("user_id", user_id).execute()
    return {"cancel_at_period_end": True}


@router.post("/subscription/reactivate", summary="Undo a scheduled cancellation")
async def reactivate_subscription(authorization: str | None = Header(default=None)):
    user_id = await _user_from_jwt(authorization)
    sub_id = _subscription_id(_subscription_record(user_id))
    if not sub_id:
        raise HTTPException(status_code=404, detail="No active subscription")
    try:
        get_provider().reactivate(sub_id)
    except Exception as e:  # noqa: BLE001
        log.error("reactivate_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Reactivate failed: {e}") from e

    get_supabase().table("subscriptions").update(
        {"cancel_at_period_end": False}
    ).eq("user_id", user_id).execute()
    return {"cancel_at_period_end": False}


@router.post("/subscription/change-plan", summary="Upgrade or downgrade the plan")
async def change_plan(
    body: ChangePlanBody,
    authorization: str | None = Header(default=None),
):
    p = get_provider()
    user_id = await _user_from_jwt(authorization)
    record = _subscription_record(user_id)
    sub_id = _subscription_id(record)
    if not sub_id:
        raise HTTPException(
            status_code=404,
            detail="No active subscription. Use checkout to start one.",
        )

    item = p.resolve_subscription(body.plan, body.cycle)
    if not item:
        raise HTTPException(status_code=400, detail="Unknown or unconfigured plan.")
    if record and record.get("plan") == body.plan:
        raise HTTPException(status_code=400, detail="Already on this plan.")

    metadata = {
        "user_id": user_id,
        "kind": item.kind,
        "credits": str(item.credits),
        "plan": item.plan or body.plan,
    }
    try:
        p.change_plan(sub_id, item, metadata)
    except Exception as e:  # noqa: BLE001
        log.error("change_plan_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Plan change failed: {e}") from e

    # Reflect immediately: grant_credits SETS subscription_credits (no double-grant).
    sb = get_supabase()
    renews_at = record.get("current_period_end") if record else None
    sb.rpc(
        "grant_credits",
        {
            "p_user_id": user_id,
            "p_subscription": item.credits,
            "p_topup": 0,
            "p_plan": body.plan,
            "p_renews_at": renews_at,
        },
    ).execute()
    sb.table("subscriptions").update({"plan": body.plan}).eq("user_id", user_id).execute()
    sb.table("credit_transactions").insert(
        {
            "user_id": user_id,
            "type": "subscription_grant",
            "amount": item.credits,
            "description": f"Plan changed to {body.plan}",
        }
    ).execute()
    return {"plan": body.plan, "credits": item.credits}


def _grant_subscription(sb, user_id: str, plan: str, credits: int, event: WebhookEvent) -> None:
    p = get_provider()
    sb.rpc(
        "grant_credits",
        {
            "p_user_id": user_id,
            "p_subscription": credits,
            "p_topup": 0,
            "p_plan": plan,
            "p_renews_at": event.renews_at,
        },
    ).execute()
    row = {
        "user_id": user_id,
        "status": event.status or "active",
        "plan": plan,
        "current_period_end": event.renews_at,
        "cancel_at_period_end": event.cancel_at_period_end,
    }
    if event.customer_id:
        row[p.customer_col] = event.customer_id
    if event.subscription_id:
        row[p.subscription_col] = event.subscription_id
    sb.table("subscriptions").upsert(row, on_conflict="user_id").execute()


def _resolve_user_id(event: WebhookEvent) -> str | None:
    if event.user_id:
        return event.user_id
    p = get_provider()
    sb = get_supabase()
    for col, value in ((p.subscription_col, event.subscription_id), (p.customer_col, event.customer_id)):
        if not value:
            continue
        res = sb.table("subscriptions").select("user_id").eq(col, value).limit(1).execute()
        if res.data:
            return res.data[0]["user_id"]
    return None


def _plan_from_db(user_id: str) -> str | None:
    res = (
        get_supabase()
        .table("subscriptions")
        .select("plan")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return res.data[0]["plan"] if res.data else None


@router.post("/webhook", summary="Payment provider webhook handler", include_in_schema=False)
async def billing_webhook(request: Request):
    p = get_provider()
    body = await request.body()
    headers = {k.lower(): v for k, v in request.headers.items()}
    try:
        event = p.verify_and_parse(body, headers)
    except Exception as e:  # noqa: BLE001
        log.warning("webhook_verify_failed", provider=p.name, error=str(e))
        raise HTTPException(status_code=401, detail="Invalid signature") from e

    if event.action == "ignore":
        return {"received": True}

    sb = get_supabase()
    user_id = _resolve_user_id(event)
    log.info("billing_webhook", provider=p.name, action=event.action, user_id=user_id)
    if not user_id:
        return {"received": True}

    if event.action == "grant_subscription":
        plan = event.plan or _plan_from_db(user_id)
        credits = event.credits or (SUBSCRIPTION_CREDITS.get(plan or "", 0))
        if plan and credits:
            _grant_subscription(sb, user_id, plan, credits, event)
            sb.table("credit_transactions").insert(
                {
                    "user_id": user_id,
                    "type": "subscription_grant",
                    "amount": credits,
                    "description": f"Subscription payment: {plan}",
                }
            ).execute()

    elif event.action == "grant_topup" and event.credits:
        sb.rpc(
            "grant_credits",
            {
                "p_user_id": user_id,
                "p_subscription": 0,
                "p_topup": event.credits,
                "p_plan": None,
                "p_renews_at": None,
            },
        ).execute()
        txn = {
            "user_id": user_id,
            "type": "topup",
            "amount": event.credits,
            "description": f"PAYG pack: {event.credits} credits",
        }
        if event.payment_id:
            txn[p.payment_col] = event.payment_id
        sb.table("credit_transactions").insert(txn).execute()

    elif event.action == "cancel":
        sb.table("subscriptions").update({"status": "canceled", "plan": "free"}).eq(
            "user_id", user_id
        ).execute()
        sb.table("credit_balances").update(
            {"plan": "free", "subscription_credits": 0}
        ).eq("user_id", user_id).execute()

    elif event.action == "status":
        update: dict = {}
        if event.status:
            update["status"] = event.status
        update["cancel_at_period_end"] = event.cancel_at_period_end
        if event.renews_at:
            update["current_period_end"] = event.renews_at
        sb.table("subscriptions").update(update).eq("user_id", user_id).execute()

    return {"received": True}
