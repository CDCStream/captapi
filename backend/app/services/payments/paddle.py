"""Paddle Billing provider (active merchant of record).

Talks to the Paddle Billing REST API with httpx and verifies webhooks with the
Paddle-Signature HMAC scheme — no SDK dependency. Checkout uses a server-created
Transaction whose id the frontend opens with Paddle.js (overlay checkout), so
card data never touches our servers.

Docs: https://developer.paddle.com/api-reference/overview
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time

import httpx
import structlog

from app.core.config import get_settings
from app.services.payments.base import (
    PACK_CREDITS,
    SUBSCRIPTION_CREDITS,
    CheckoutItem,
    CheckoutResult,
    WebhookEvent,
)

log = structlog.get_logger(__name__)

_BASE_URLS = {
    "sandbox": "https://sandbox-api.paddle.com",
    "production": "https://api.paddle.com",
}
# Reject webhooks whose timestamp is older than this (replay protection).
_MAX_SIGNATURE_AGE_SECONDS = 5 * 60

# Paddle subscription status -> our internal status.
_STATUS_MAP = {
    "active": "active",
    "trialing": "active",
    "past_due": "on_hold",
    "paused": "on_hold",
    "canceled": "canceled",
}


def _attr(name: str) -> str:
    return getattr(get_settings(), name, "") or ""


class PaddleProvider:
    name = "paddle"
    customer_col = "paddle_customer_id"
    subscription_col = "paddle_subscription_id"
    payment_col = "paddle_transaction_id"

    # --- HTTP plumbing ----------------------------------------------------
    def _base_url(self) -> str:
        return _BASE_URLS.get(get_settings().PADDLE_ENVIRONMENT, _BASE_URLS["sandbox"])

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        settings = get_settings()
        if not settings.PADDLE_API_KEY:
            raise RuntimeError("PADDLE_API_KEY is not configured")
        url = f"{self._base_url()}{path}"
        headers = {
            "Authorization": f"Bearer {settings.PADDLE_API_KEY}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=20.0) as client:
            resp = client.request(method, url, headers=headers, json=payload)
        if resp.status_code >= 400:
            log.error("paddle_api_error", method=method, path=path, status=resp.status_code, body=resp.text)
            raise RuntimeError(f"Paddle API {resp.status_code}: {resp.text}")
        return resp.json().get("data", {}) if resp.content else {}

    # --- Catalog ----------------------------------------------------------
    def resolve_subscription(self, plan: str, cycle: str) -> CheckoutItem | None:
        credits = SUBSCRIPTION_CREDITS.get(plan)
        if credits is None:
            return None
        suffix = "YEARLY" if cycle == "yearly" else "MONTHLY"
        price_id = _attr(f"PADDLE_PRICE_{plan.upper()}_{suffix}")
        if not price_id and cycle == "yearly":
            price_id = _attr(f"PADDLE_PRICE_{plan.upper()}_MONTHLY")
        if not price_id:
            return None
        return CheckoutItem(price_id=price_id, kind="subscription", plan=plan, credits=credits)

    def resolve_pack(self, pack: str) -> CheckoutItem | None:
        credits = PACK_CREDITS.get(pack)
        if credits is None:
            return None
        price_id = _attr(f"PADDLE_PRICE_PACK_{pack.upper()}")
        if not price_id:
            return None
        return CheckoutItem(price_id=price_id, kind="pack", plan=None, credits=credits)

    # --- Checkout / portal / lifecycle -----------------------------------
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
        # custom_data rides with the transaction and (for subscriptions) is
        # copied onto the subscription, so webhooks can trust the credit amount.
        payload: dict = {
            "items": [{"price_id": item.price_id, "quantity": 1}],
            "custom_data": {k: str(v) for k, v in metadata.items()},
        }
        if customer_id:
            payload["customer_id"] = customer_id
        data = self._request("POST", "/transactions", payload)
        return CheckoutResult(provider=self.name, transaction_id=data.get("id"))

    def create_portal(self, customer_id: str) -> str | None:
        data = self._request("POST", f"/customers/{customer_id}/portal-sessions", {})
        urls = data.get("urls") or {}
        general = urls.get("general") or {}
        return general.get("overview")

    def cancel(self, subscription_id: str) -> None:
        self._request(
            "POST",
            f"/subscriptions/{subscription_id}/cancel",
            {"effective_from": "next_billing_period"},
        )

    def reactivate(self, subscription_id: str) -> None:
        # Removing the scheduled change undoes a pending cancellation.
        self._request("PATCH", f"/subscriptions/{subscription_id}", {"scheduled_change": None})

    def change_plan(self, subscription_id: str, item: CheckoutItem, metadata: dict) -> None:
        self._request(
            "PATCH",
            f"/subscriptions/{subscription_id}",
            {
                "items": [{"price_id": item.price_id, "quantity": 1}],
                "proration_billing_mode": "prorated_immediately",
                "custom_data": {k: str(v) for k, v in metadata.items()},
            },
        )

    # --- Webhooks ---------------------------------------------------------
    def _verify_signature(self, body: bytes, sig_header: str) -> None:
        secret = get_settings().PADDLE_WEBHOOK_SECRET
        if not secret:
            raise RuntimeError("PADDLE_WEBHOOK_SECRET is not configured")
        parts = dict(
            p.split("=", 1) for p in sig_header.split(";") if "=" in p
        )
        ts = parts.get("ts")
        h1 = parts.get("h1")
        if not ts or not h1:
            raise ValueError("Malformed Paddle-Signature header")
        if abs(time.time() - int(ts)) > _MAX_SIGNATURE_AGE_SECONDS:
            raise ValueError("Paddle webhook timestamp too old")
        signed = f"{ts}:".encode() + body
        expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, h1):
            raise ValueError("Paddle webhook signature mismatch")

    def verify_and_parse(self, body: bytes, headers: dict[str, str]) -> WebhookEvent:
        self._verify_signature(body, headers.get("paddle-signature", ""))
        payload = json.loads(body)
        etype = payload.get("event_type", "")
        d = payload.get("data") or {}
        custom = d.get("custom_data") or {}
        user_id = custom.get("user_id")

        def _credits() -> int:
            try:
                return int(custom.get("credits") or 0)
            except (TypeError, ValueError):
                return 0

        if etype == "transaction.completed":
            subscription_id = d.get("subscription_id")
            customer_id = d.get("customer_id")
            if subscription_id:
                billing_period = d.get("billing_period") or {}
                return WebhookEvent(
                    action="grant_subscription",
                    user_id=user_id,
                    plan=custom.get("plan") or None,
                    credits=_credits(),
                    renews_at=billing_period.get("ends_at"),
                    customer_id=customer_id,
                    subscription_id=subscription_id,
                    status="active",
                    raw=d,
                )
            if _credits():
                return WebhookEvent(
                    action="grant_topup",
                    user_id=user_id,
                    credits=_credits(),
                    customer_id=customer_id,
                    payment_id=d.get("id"),
                    raw=d,
                )
            return WebhookEvent(action="ignore", user_id=user_id, raw=d)

        if etype in ("subscription.activated", "subscription.updated", "subscription.resumed"):
            scheduled = d.get("scheduled_change") or {}
            period = d.get("current_billing_period") or {}
            return WebhookEvent(
                action="status",
                user_id=user_id,
                plan=custom.get("plan") or None,
                status=_STATUS_MAP.get(d.get("status", ""), "active"),
                cancel_at_period_end=scheduled.get("action") == "cancel",
                renews_at=period.get("ends_at"),
                customer_id=d.get("customer_id"),
                subscription_id=d.get("id"),
                raw=d,
            )

        if etype == "subscription.canceled":
            return WebhookEvent(
                action="cancel",
                user_id=user_id,
                customer_id=d.get("customer_id"),
                subscription_id=d.get("id"),
                raw=d,
            )

        return WebhookEvent(action="ignore", user_id=user_id, raw=d)
