"""Top Ads Apify fast-fail + background cache warm."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.routers import ad_library as al


def test_timeout_error_marks_warming() -> None:
    exc = al._tiktok_ad_timeout_http(20, warming=True)
    assert exc.status_code == 503
    assert exc.headers["Retry-After"] == str(al._TIKTOK_AD_RETRY_AFTER_SECS)
    assert exc.detail["error"]["code"] == "upstream_timeout"
    assert exc.detail["error"]["retryAfterSeconds"] == al._TIKTOK_AD_RETRY_AFTER_SECS
    assert exc.detail["error"]["warming"] is True
    assert "background" in exc.detail["message"].lower()


def test_top_ads_apify_match_omits_limits() -> None:
    match = al._top_ads_apify_match(
        {
            "countryCode": "NL",
            "period": "180",
            "orderBy": "for_you",
            "keyword": "casino",
            "maxResults": 9,
            "maxItems": 9,
            "industry": "",
        }
    )
    assert match == {
        "countryCode": "NL",
        "period": "180",
        "orderBy": "for_you",
        "keyword": "casino",
    }


def test_run_top_ads_apify_warm_spawns_on_sync_timeout() -> None:
    mapped = {"totalReturned": 2, "ads": [{"id": "1"}, {"id": "2"}]}
    map_items = AsyncMock(return_value=mapped)

    client = MagicMock()
    client.last_succeeded_items = AsyncMock(return_value=[])
    client.find_active_run = AsyncMock(return_value=None)
    client.start_run = AsyncMock(return_value={"id": "run-1", "status": "RUNNING"})
    client.wait_for_run_items = AsyncMock(return_value=[])

    async def _run() -> None:
        with (
            patch.object(al, "ApifyClient", return_value=client),
            patch.object(al, "_spawn_apify_warm_to_cache") as spawn,
        ):
            with pytest.raises(HTTPException) as raised:
                await al._run_top_ads_apify_warm(
                    actor="actor/top-ads",
                    payload={
                        "countryCode": "NL",
                        "period": "180",
                        "orderBy": "for_you",
                        "keyword": "casino",
                    },
                    limit=9,
                    cache_endpoint="ad-library.tiktok.top-ads",
                    cache_params={"q": "casino", "country": "NL", "v": 4},
                    map_items=map_items,
                )
            assert raised.value.status_code == 503
            assert raised.value.detail["error"]["warming"] is True
            spawn.assert_called_once()
            assert spawn.call_args.kwargs["run_id"] == "run-1"
            map_items.assert_not_called()

    asyncio.run(_run())


def test_run_top_ads_apify_uses_snapshot() -> None:
    rows = [{"ad_id": "1", "ad_title": "Casino"}]
    mapped = {"totalReturned": 1, "ads": [{"id": "1"}]}
    map_items = AsyncMock(return_value=mapped)

    client = MagicMock()
    client.last_succeeded_items = AsyncMock(return_value=rows)
    client.find_active_run = AsyncMock()
    client.start_run = AsyncMock()

    async def _run() -> None:
        with patch.object(al, "ApifyClient", return_value=client):
            out = await al._run_top_ads_apify_warm(
                actor="actor/top-ads",
                payload={"countryCode": "NL", "period": "180", "orderBy": "for_you"},
                limit=3,
                cache_endpoint="ad-library.tiktok.top-ads",
                cache_params={"q": "", "country": "NL", "v": 4},
                map_items=map_items,
            )
        assert out == mapped
        client.start_run.assert_not_called()
        map_items.assert_awaited_once_with(rows)

    asyncio.run(_run())
