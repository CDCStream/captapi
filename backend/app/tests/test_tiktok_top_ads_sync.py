"""TikTok Top Ads - sync wait for real upstream JSON (no background warm)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.routers import ad_library as al


def test_timeout_error_is_503_upstream_timeout() -> None:
    exc = al._tiktok_ad_timeout_http(90)
    assert exc.status_code == 503
    assert exc.headers["Retry-After"] == str(al._TIKTOK_AD_RETRY_AFTER_SECS)
    assert exc.detail["error"]["code"] == "upstream_timeout"
    assert exc.detail["error"]["retryAfterSeconds"] == al._TIKTOK_AD_RETRY_AFTER_SECS
    assert "warming" not in exc.detail["error"]
    assert "120" in exc.detail["message"]


def test_apify_timeout_constant_under_cloudflare_read_timeout() -> None:
    # Cloudflare Proxy Read Timeout default is 125s; 90s leaves headroom.
    assert 60.0 <= al._TIKTOK_AD_APIFY_TIMEOUT_SECS <= 120.0
    assert al._TIKTOK_AD_APIFY_TIMEOUT_SECS < 125.0


def test_bill_ads_apify_scales_per_result() -> None:
    ctx: dict = {"source": "apify"}
    al._bill_ads(ctx, [{"id": "1"}, {"id": "2"}, {"id": "3"}], flat=2, apify_rate=1.0)
    assert ctx["credits_override"] == 3


def test_bill_ads_empty_is_free() -> None:
    ctx: dict = {"source": "apify"}
    al._bill_ads(ctx, [], flat=2, apify_rate=1.0)
    assert ctx["credits_override"] == 0


def test_bill_ads_native_flat() -> None:
    ctx: dict = {"source": "direct"}
    al._bill_ads(ctx, [{"id": "1"}] * 20, flat=2, apify_rate=1.0)
    assert ctx["credits_override"] == 2


def test_run_actor_fast_maps_timeout_to_503() -> None:
    client = MagicMock()
    client.run_actor_sync = AsyncMock(side_effect=al.ApifyError("upstream timeout after 90s"))

    async def _run() -> None:
        with patch.object(al, "ApifyClient", return_value=client):
            with pytest.raises(HTTPException) as raised:
                await al._run_actor_fast("actor/top-ads", {"countryCode": "NL"}, 9, timeout=90.0)
            assert raised.value.status_code == 503
            assert raised.value.detail["error"]["code"] == "upstream_timeout"

    asyncio.run(_run())
