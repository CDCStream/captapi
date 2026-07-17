"""Dodo Payments provider (dormant fallback).

Wraps the Dodo SDK behind the shared PaymentProvider interface. Kept so the
service can switch back to Dodo by setting PAYMENT_PROVIDER=dodo without any
code changes.
"""

from __future__ import annotations

import json

from app.core.config import get_settings
from app.services.dodo_client import get_dodo
from app.services.payments.base import (
    PACK_CREDITS,
    SUBSCRIPTION_CREDITS,
    CheckoutItem,
    CheckoutResult,
    WebhookEvent,
)


def _attr(name: str) -> str:
    return getattr(get_settings(), name, "") or ""


class DodoProvider:
    name = "dodo"
    customer_col = "dodo_customer_id"
    subscription_col = "dodo_subscription_id"
    payment_col = "dodo_payment_id"

    def resolve_subscription(self, plan: str, cycle: str) -> CheckoutItem | None:
        credits = SUBSCRIPTION_CREDITS.get(plan)
        if credits is None:
            return None
        suffix = "YEARLY" if cycle == "yearly" else "MONTHLY"
        product_id = _attr(f"DODO_PRODUCT_{plan.upper()}_{suffix}")
        if not product_id and cycle == "yearly":
            product_id = _attr(f"DODO_PRODUCT_{plan.upper()}_MONTHLY")
        if not product_id:
            return None
        return CheckoutItem(price_id=product_id, kind="subscription", plan=plan, credits=credits)

    def resolve_pack(self, pack: str) -> CheckoutItem | None:
        credits = PACK_CREDITS.get(pack)
        if credits is None:
            return None
        product_id = _attr(f"DODO_PRODUCT_PACK_{pack.upper()}")
        if not product_id:
            return None
        return CheckoutItem(price_id=product_id, kind="pack", plan=None, credits=credits)

    def create_checkout(
        self,
        *,
        item: CheckoutItem,
        user_id: str,
        email: str | None,
        customer_id: str | None,
        return_url: str,
        metadata: dict,
    ) -> CheckoutResult:
        customer = {"customer_id": customer_id} if customer_id else {"email": email}
        session = get_dodo().checkout_sessions.create(
            product_cart=[{"product_id": item.price_id, "quantity": 1}],
            customer=customer,
            return_url=return_url,
            metadata=metadata,
        )
        return CheckoutResult(provider=self.name, url=session.checkout_url)

    def create_portal(self, customer_id: str) -> str | None:
        portal = get_dodo().customers.customer_portal.create(customer_id=customer_id)
        return getattr(portal, "link", None) or getattr(portal, "url", None)

    def cancel(self, subscription_id: str) -> None:
        get_dodo().subscriptions.update(
            subscription_id,
            cancel_at_next_billing_date=True,
            cancel_reason="cancelled_by_customer",
        )

    def reactivate(self, subscription_id: str) -> None:
        get_dodo().subscriptions.update(subscription_id, cancel_at_next_billing_date=False)

    def change_plan(self, subscription_id: str, item: CheckoutItem, metadata: dict) -> None:
        get_dodo().subscriptions.change_plan(
            subscription_id,
            product_id=item.price_id,
            proration_billing_mode="prorated_immediately",
            quantity=1,
            metadata=metadata,
        )

    def verify_and_parse(self, body: bytes, headers: dict[str, str]) -> WebhookEvent:
        get_dodo().webhooks.unwrap(
            body,
            headers={
                "webhook-id": headers.get("webhook-id", ""),
                "webhook-signature": headers.get("webhook-signature", ""),
                "webhook-timestamp": headers.get("webhook-timestamp", ""),
            },
        )
        event = json.loads(body)
        etype = event.get("type", "")
        data = event.get("data") or {}
        meta = data.get("metadata") or {}
        user_id = meta.get("user_id")
        credits = int(meta.get("credits", 0) or 0)
        plan = meta.get("plan")
        customer = data.get("customer") or {}

        if etype in ("subscription.active", "subscription.renewed"):
            return WebhookEvent(
                action="grant_subscription",
                user_id=user_id,
                plan=plan,
                credits=credits,
                renews_at=data.get("next_billing_date"),
                customer_id=customer.get("customer_id"),
                subscription_id=data.get("subscription_id"),
                cancel_at_period_end=bool(data.get("cancel_at_next_billing_date")),
                status="active",
                raw=data,
            )
        if etype == "subscription.on_hold":
            return WebhookEvent(action="status", user_id=user_id, status="on_hold", raw=data)
        if etype in ("subscription.cancelled", "subscription.expired", "subscription.failed"):
            return WebhookEvent(action="cancel", user_id=user_id, raw=data)
        if etype == "payment.succeeded" and not data.get("subscription_id") and credits:
            return WebhookEvent(
                action="grant_topup",
                user_id=user_id,
                credits=credits,
                payment_id=data.get("payment_id"),
                raw=data,
            )
        return WebhookEvent(action="ignore", user_id=user_id, raw=data)
