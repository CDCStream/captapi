"""Parallel audience commenter sampling (AD1)."""
from __future__ import annotations

import asyncio
import time

from app.services import tiktok_native as tn


def test_audience_commenters_parallel_faster_than_serial(monkeypatch):
    ids = [f"v{i}" for i in range(8)]

    async def fake_page(aweme_id, cursor, count, *, expect_items=True, concurrency=16):
        await asyncio.sleep(0.15)
        return {
            "comments": [
                {"user": {"region": "US"}, "comment_language": "en"},
                {"user": {"region": "IT"}, "comment_language": "it"},
            ],
            "cursor": None,
            "has_more": False,
        }

    monkeypatch.setattr(tn, "_comment_page", fake_page)

    async def _run():
        return await tn.audience_commenters_native(
            ids, target_total=100, per_video=30, video_concurrency=8
        )

    t0 = time.perf_counter()
    got = asyncio.run(_run())
    parallel_ms = (time.perf_counter() - t0) * 1000
    assert got is not None
    assert len(got["regions"]) == 16
    # Serial would be ~8*150ms = 1200ms; parallel should finish well under 600ms.
    assert parallel_ms < 600, parallel_ms
