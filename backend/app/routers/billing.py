"""Dodo Payments billing: checkout sessions, customer portal, webhooks."""

from __future__ import annotations

import json

import structlog
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from app.core.config import get_settings
from app.routers.auth_keys import _user_from_jwt
from app.services.dodo_client import get_dodo, resolve_pack, resolve_subscription
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
    sb = get_supabase()
    res = (
        sb.table("subscriptions")
        .select("dodo_customer_id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if res.data and res.data[0].get("dodo_customer_id"):
        return res.data[0]["dodo_customer_id"]
    return None


def _subscription_record(user_id: str) -> dict | None:
    sb = get_supabase()
    res = (
        sb.table("subscriptions")
        .select(
            "dodo_subscription_id, dodo_customer_id, status, plan, "
            "current_period_end, cancel_at_period_end"
        )
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


@router.post("/checkout", summary="Create a Dodo Payments checkout session")
async def create_checkout(
    body: CheckoutBody,
    authorization: str | None = Header(default=None),
):
    settings = get_settings()
    user_id = await _user_from_jwt(authorization)
    sb = get_supabase()

    item = (
        resolve_pack(body.pack)
        if body.pack
        else resolve_subscription(body.plan or "", body.cycle)
    )
    if not item:
        raise HTTPException(
            status_code=400,
            detail="Unknown or unconfigured product. Set the matching DODO_PRODUCT_* env var.",
        )

    user_res = sb.auth.admin.get_user_by_id(user_id)
    email = user_res.user.email if user_res and user_res.user else None

    customer_id = _existing_customer_id(user_id)
    customer = {"customer_id": customer_id} if customer_id else {"email": email}

    return_url = (
        body.success_url
        or f"{settings.APP_BASE_URL}/dashboard/billing?status=success"
    )

    metadata = {
        "user_id": user_id,
        "kind": item.kind,
        "credits": str(item.credits),
    }
    if item.plan:
        metadata["plan"] = item.plan

    try:
        session = get_dodo().checkout_sessions.create(
            product_cart=[{"product_id": item.product_id, "quantity": 1}],
            customer=customer,
            return_url=return_url,
            metadata=metadata,
        )
    except Exception as e:  # noqa: BLE001
        log.error("dodo_checkout_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Checkout failed: {e}") from e

    return {"id": session.session_id, "url": session.checkout_url}


@router.post("/portal", summary="Create a Dodo customer portal session")
async def create_portal(authorization: str | None = Header(default=None)):
    user_id = await _user_from_jwt(authorization)
    customer_id = _existing_customer_id(user_id)
    if not customer_id:
        raise HTTPException(status_code=404, detail="No billing customer found yet")
    try:
        portal = get_dodo().customers.customer_portal.create(customer_id=customer_id)
    except Exception as e:  # noqa: BLE001
        log.error("dodo_portal_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Portal failed: {e}") from e
    return {"url": getattr(portal, "link", None) or getattr(portal, "url", None)}


@router.get("/subscription", summary="Current subscription status")
async def get_subscription(authorization: str | None = Header(default=None)):
    user_id = await _user_from_jwt(authorization)
    record = _subscription_record(user_id)
    if not record or not record.get("dodo_subscription_id"):
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
    record = _subscription_record(user_id)
    sub_id = record.get("dodo_subscription_id") if record else None
    if not sub_id:
        raise HTTPException(status_code=404, detail="No active subscription")
    try:
        get_dodo().subscriptions.update(
            sub_id,
            cancel_at_next_billing_date=True,
            cancel_reason="cancelled_by_customer",
        )
    except Exception as e:  # noqa: BLE001
        log.error("dodo_cancel_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Cancel failed: {e}") from e

    get_supabase().table("subscriptions").update(
        {"cancel_at_period_end": True}
    ).eq("user_id", user_id).execute()
    return {"cancel_at_period_end": True}


@router.post("/subscription/reactivate", summary="Undo a scheduled cancellation")
async def reactivate_subscription(authorization: str | None = Header(default=None)):
    user_id = await _user_from_jwt(authorization)
    record = _subscription_record(user_id)
    sub_id = record.get("dodo_subscription_id") if record else None
    if not sub_id:
        raise HTTPException(status_code=404, detail="No active subscription")
    try:
        get_dodo().subscriptions.update(sub_id, cancel_at_next_billing_date=False)
    except Exception as e:  # noqa: BLE001
        log.error("dodo_reactivate_failed", error=str(e))
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
    user_id = await _user_from_jwt(authorization)
    record = _subscription_record(user_id)
    sub_id = record.get("dodo_subscription_id") if record else None
    if not sub_id:
        raise HTTPException(
            status_code=404,
            detail="No active subscription. Use checkout to start one.",
        )

    item = resolve_subscription(body.plan, body.cycle)
    if not item:
        raise HTTPException(
            status_code=400,
            detail="Unknown or unconfigured plan.",
        )
    if record.get("plan") == body.plan:
        raise HTTPException(status_code=400, detail="Already on this plan.")

    metadata = {
        "user_id": user_id,
        "kind": item.kind,
        "credits": str(item.credits),
        "plan": item.plan or body.plan,
    }
    try:
        get_dodo().subscriptions.change_plan(
            sub_id,
            product_id=item.product_id,
            proration_billing_mode="prorated_immediately",
            quantity=1,
            metadata=metadata,
        )
    except Exception as e:  # noqa: BLE001
        log.error("dodo_change_plan_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Plan change failed: {e}") from e

    # Reflect immediately: grant_credits SETS subscription_credits (no double-grant).
    sb = get_supabase()
    renews_at = record.get("current_period_end")
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
    sb.table("subscriptions").update({"plan": body.plan}).eq(
        "user_id", user_id
    ).execute()
    sb.table("credit_transactions").insert(
        {
            "user_id": user_id,
            "type": "subscription_grant",
            "amount": item.credits,
            "description": f"Plan changed to {body.plan}",
        }
    ).execute()
    return {"plan": body.plan, "credits": item.credits}


def _grant_subscription(sb, user_id: str, plan: str, credits: int, renews_at, data: dict):
    sb.rpc(
        "grant_credits",
        {
            "p_user_id": user_id,
            "p_subscription": credits,
            "p_topup": 0,
            "p_plan": plan,
            "p_renews_at": renews_at,
        },
    ).execute()
    customer = data.get("customer") or {}
    sb.table("subscriptions").upsert(
        {
            "user_id": user_id,
            "dodo_customer_id": customer.get("customer_id"),
            "dodo_subscription_id": data.get("subscription_id"),
            "status": data.get("status", "active"),
            "plan": plan,
            "current_period_end": renews_at,
            "cancel_at_period_end": bool(data.get("cancel_at_next_billing_date")),
        },
        on_conflict="user_id",
    ).execute()


@router.post("/webhook", summary="Dodo Payments webhook handler", include_in_schema=False)
async def dodo_webhook(request: Request):
    body = await request.body()
    headers = {
        "webhook-id": request.headers.get("webhook-id", ""),
        "webhook-signature": request.headers.get("webhook-signature", ""),
        "webhook-timestamp": request.headers.get("webhook-timestamp", ""),
    }
    try:
        get_dodo().webhooks.unwrap(body, headers=headers)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid signature") from e

    event = json.loads(body)
    etype = event.get("type", "")
    data = event.get("data") or {}
    meta = data.get("metadata") or {}
    user_id = meta.get("user_id")
    sb = get_supabase()
    log.info("dodo_webhook", type=etype, user_id=user_id)

    if not user_id:
        return {"received": True}

    credits = int(meta.get("credits", 0) or 0)
    plan = meta.get("plan")

    # --- Subscriptions ---------------------------------------------------
    if etype in ("subscription.active", "subscription.renewed"):
        if plan and credits:
            renews_at = data.get("next_billing_date")
            _grant_subscription(sb, user_id, plan, credits, renews_at, data)
            sb.table("credit_transactions").insert(
                {
                    "user_id": user_id,
                    "type": "subscription_grant",
                    "amount": credits,
                    "description": f"Subscription {etype.split('.')[1]}: {plan}",
                }
            ).execute()

    elif etype == "subscription.on_hold":
        sb.table("subscriptions").update({"status": "on_hold"}).eq(
            "user_id", user_id
        ).execute()

    elif etype in ("subscription.cancelled", "subscription.expired", "subscription.failed"):
        sb.table("subscriptions").update({"status": "canceled", "plan": "free"}).eq(
            "user_id", user_id
        ).execute()
        sb.table("credit_balances").update(
            {"plan": "free", "subscription_credits": 0}
        ).eq("user_id", user_id).execute()

    # --- One-time packs (PAYG) ------------------------------------------
    elif etype == "payment.succeeded":
        # Subscription invoices also emit payment.succeeded; skip those here
        # (handled by subscription.active / subscription.renewed).
        if not data.get("subscription_id") and credits:
            sb.rpc(
                "grant_credits",
                {
                    "p_user_id": user_id,
                    "p_subscription": 0,
                    "p_topup": credits,
                    "p_plan": None,
                    "p_renews_at": None,
                },
            ).execute()
            sb.table("credit_transactions").insert(
                {
                    "user_id": user_id,
                    "type": "topup",
                    "amount": credits,
                    "description": f"PAYG pack: {credits} credits",
                    "dodo_payment_id": data.get("payment_id"),
                }
            ).execute()

    return {"received": True}
