"""Supabase client singleton (uses service_role for backend operations)."""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Callable, TypeVar

import httpcore
import httpx
import structlog
from supabase import Client, ClientOptions, create_client

from app.core.config import get_settings

log = structlog.get_logger(__name__)

T = TypeVar("T")

_TRANSIENT = (
    httpx.RemoteProtocolError,
    httpx.ConnectError,
    httpx.ReadError,
    httpx.WriteError,
    httpcore.RemoteProtocolError,
    httpcore.ConnectError,
)


def _httpx_client() -> httpx.Client:
    # Supabase/edge often terminates idle HTTP/2 connections with
    # PROTOCOL_ERROR (httpx/httpcore RemoteProtocolError: ConnectionTerminated).
    # Force HTTP/1.1 + transport retries — workaround from supabase-py#1064.
    transport = httpx.HTTPTransport(
        retries=3,
        http2=False,
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=30.0,
        ),
    )
    return httpx.Client(
        transport=transport,
        timeout=httpx.Timeout(60.0, connect=10.0),
    )


@lru_cache
def get_supabase() -> Client:
    settings = get_settings()
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
        options=ClientOptions(httpx_client=_httpx_client()),
    )


def sb_execute(fn: Callable[[], T], *, attempts: int = 3, label: str = "supabase") -> T:
    """Run a sync PostgREST call with retries on transient connection drops."""
    last: BaseException | None = None
    for i in range(attempts):
        try:
            return fn()
        except _TRANSIENT as exc:
            last = exc
            if i + 1 >= attempts:
                break
            delay = 0.05 * (2**i)
            log.warning(
                "supabase_transient_retry",
                label=label,
                attempt=i + 1,
                error=str(exc),
                sleep=delay,
            )
            time.sleep(delay)
    assert last is not None
    raise last
