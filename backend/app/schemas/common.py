"""Shared response envelopes."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Any | None = None


class UsageInfo(BaseModel):
    credits_used: int
    credits_remaining: int
    cache_hit: bool = False


class CreditBalance(BaseModel):
    plan: str
    subscription_credits: int
    topup_credits: int
    total_credits: int
    subscription_renews_at: str | None = None
