"""Payment provider selection.

The active merchant of record is chosen by settings.PAYMENT_PROVIDER. The
billing router only ever talks to `get_provider()`.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.services.payments.base import (
    PACK_CREDITS,
    SUBSCRIPTION_CREDITS,
    CheckoutItem,
    CheckoutResult,
    PaymentProvider,
    WebhookEvent,
)


@lru_cache
def get_provider() -> PaymentProvider:
    provider = get_settings().PAYMENT_PROVIDER
    if provider == "dodo":
        from app.services.payments.dodo import DodoProvider

        return DodoProvider()
    from app.services.payments.paddle import PaddleProvider

    return PaddleProvider()


__all__ = [
    "get_provider",
    "PaymentProvider",
    "CheckoutItem",
    "CheckoutResult",
    "WebhookEvent",
    "SUBSCRIPTION_CREDITS",
    "PACK_CREDITS",
]
