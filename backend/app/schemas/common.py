"""Shared response envelopes."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    # Populated by BillingHeaderMiddleware from request_meta (optional on
    # the model so routers can keep returning ApiResponse(data=...)).
    cached: bool | None = None
    creditsUsed: int | None = None
    requestId: str | None = None
    fetchedAt: str | None = None
    cachedAt: str | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Any | None = None


class UsageInfo(BaseModel):
    creditsUsed: int
    creditsRemaining: int
    cacheHit: bool = False


class CreditBalance(BaseModel):
    plan: str
    monthlyQuota: int | None = None
    subscriptionCredits: int
    topupCredits: int
    totalCredits: int
    subscriptionRenewsAt: str | None = None
