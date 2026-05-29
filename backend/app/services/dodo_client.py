"""Dodo Payments SDK wrapper + product catalog.

Pricing model (cost + margin):
  - Subscriptions: starter 2,000 / pro 6,000 / business 20,000 credits per cycle.
  - PAYG packs:    starter 2,000 / growth 10,000 / scale 50,000 credits (one-time).

Credits and plan names are the source of truth here and are passed to Dodo as
checkout metadata, so webhooks grant the correct amount without trusting the client.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from dodopayments import DodoPayments

from app.core.config import get_settings


@lru_cache
def get_dodo() -> DodoPayments:
    settings = get_settings()
    return DodoPayments(
        bearer_token=settings.DODO_PAYMENTS_API_KEY,
        environment=settings.DODO_PAYMENTS_ENVIRONMENT,
        webhook_key=settings.DODO_PAYMENTS_WEBHOOK_KEY,
    )


@dataclass(frozen=True)
class CheckoutItem:
    product_id: str
    kind: str  # "subscription" | "pack"
    plan: str | None  # plan name for subscriptions, None for packs
    credits: int


def _settings_attr(name: str) -> str:
    return getattr(get_settings(), name, "") or ""


def resolve_subscription(plan: str, cycle: str) -> CheckoutItem | None:
    """plan in {starter, pro, business}, cycle in {monthly, yearly}."""
    credits = {"starter": 2_000, "pro": 6_000, "business": 20_000}.get(plan)
    if credits is None:
        return None
    suffix = "YEARLY" if cycle == "yearly" else "MONTHLY"
    product_id = _settings_attr(f"DODO_PRODUCT_{plan.upper()}_{suffix}")
    # Fall back to the monthly product if a yearly one isn't configured yet.
    if not product_id and cycle == "yearly":
        product_id = _settings_attr(f"DODO_PRODUCT_{plan.upper()}_MONTHLY")
    if not product_id:
        return None
    return CheckoutItem(product_id=product_id, kind="subscription", plan=plan, credits=credits)


def resolve_pack(pack: str) -> CheckoutItem | None:
    """pack in {starter, growth, scale}."""
    credits = {"starter": 2_000, "growth": 10_000, "scale": 50_000}.get(pack)
    if credits is None:
        return None
    product_id = _settings_attr(f"DODO_PRODUCT_PACK_{pack.upper()}")
    if not product_id:
        return None
    return CheckoutItem(product_id=product_id, kind="pack", plan=None, credits=credits)
