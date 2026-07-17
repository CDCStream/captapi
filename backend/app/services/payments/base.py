"""Provider-agnostic payment types shared by the billing router.

The billing router talks to a single active `PaymentProvider` (selected by
`settings.PAYMENT_PROVIDER`). Each provider maps its own checkout/webhook
shapes onto these normalized types so the router's DB logic stays identical
regardless of which merchant of record is live.

Credits and plan names are the source of truth here and are sent to the
provider as checkout metadata / custom data, so webhooks grant the correct
amount without trusting the client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

# Credits granted per plan (per billing cycle) and per one-time pack.
SUBSCRIPTION_CREDITS: dict[str, int] = {"starter": 2_000, "pro": 6_000, "business": 20_000}
PACK_CREDITS: dict[str, int] = {"starter": 2_000, "growth": 10_000, "scale": 50_000}


@dataclass(frozen=True)
class CheckoutItem:
    """A resolved purchasable: a provider price/product id + what it grants."""

    price_id: str
    kind: str  # "subscription" | "pack"
    plan: str | None  # plan name for subscriptions, None for packs
    credits: int


@dataclass
class CheckoutResult:
    """What the /checkout endpoint returns to the client.

    Redirect providers (Dodo) return a hosted `url`. Overlay providers (Paddle)
    return a `transaction_id` the frontend opens with Paddle.js.
    """

    provider: str
    url: str | None = None
    transaction_id: str | None = None


@dataclass
class WebhookEvent:
    """A normalized billing webhook, ready for the router to apply to the DB."""

    action: str  # "grant_subscription" | "grant_topup" | "cancel" | "status" | "ignore"
    user_id: str | None = None
    plan: str | None = None
    credits: int = 0
    renews_at: str | None = None
    status: str | None = None  # our internal status: active | on_hold | canceled
    cancel_at_period_end: bool = False
    customer_id: str | None = None
    subscription_id: str | None = None
    payment_id: str | None = None
    raw: dict = field(default_factory=dict)


@runtime_checkable
class PaymentProvider(Protocol):
    """Interface every merchant-of-record integration implements."""

    name: str
    # Column names on the `subscriptions` / `credit_transactions` tables that
    # store this provider's ids (keeps historical data separated per provider).
    customer_col: str
    subscription_col: str
    payment_col: str

    def resolve_subscription(self, plan: str, cycle: str) -> CheckoutItem | None: ...

    def resolve_pack(self, pack: str) -> CheckoutItem | None: ...

    def create_checkout(
        self,
        *,
        item: CheckoutItem,
        user_id: str,
        email: str | None,
        customer_id: str | None,
        return_url: str,
        metadata: dict,
    ) -> CheckoutResult: ...

    def create_portal(self, customer_id: str) -> str | None: ...

    def cancel(self, subscription_id: str) -> None: ...

    def reactivate(self, subscription_id: str) -> None: ...

    def change_plan(self, subscription_id: str, item: CheckoutItem, metadata: dict) -> None: ...

    def verify_and_parse(self, body: bytes, headers: dict[str, str]) -> WebhookEvent: ...
