from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.services.tiktok_native import (
    challenge_detail_native,
    enrich_hashtag_population_stats,
    popular_hashtags_native,
)


def test_challenge_detail_parses_stats_v2() -> None:
    async def _run() -> None:
        payload = {
            "challengeInfo": {
                "challenge": {"id": "504245", "title": "skincare", "desc": "x"},
                "stats": {"videoCount": 0, "viewCount": 954800000000},
                "statsV2": {"videoCount": "56953998", "viewCount": "954780316160"},
            },
            "statusCode": 0,
        }

        class _Resp:
            status_code = 200
            text = "{}"

            def json(self):
                return payload

        with patch(
            "app.services.tiktok_native.proxy_fetch",
            new=AsyncMock(return_value=_Resp()),
        ):
            got = await challenge_detail_native("skincare")
        assert got is not None
        assert got["hashtagId"] == "504245"
        assert got["videoCount"] == 56_953_998
        assert got["totalPlays"] == 954_780_316_160
        assert got["growthRate"] is None

    asyncio.run(_run())


def test_enrich_never_echoes_sample_into_population() -> None:
    async def _run() -> None:
        rows = [
            {
                "name": "skincare",
                "sampleVideoCount": 17,
                "samplePlays": 40_305_805,
                "videoCount": None,
                "totalPlays": None,
            }
        ]

        async def _detail(name: str):
            return {
                "hashtagId": "1",
                "name": name,
                "videoCount": 50_000_000,
                "totalPlays": 900_000_000_000,
                "growthRate": None,
            }

        with patch(
            "app.services.tiktok_native.challenge_detail_native",
            new=AsyncMock(side_effect=_detail),
        ):
            out = await enrich_hashtag_population_stats(rows)
        assert out[0]["sampleVideoCount"] == 17
        assert out[0]["videoCount"] == 50_000_000
        assert out[0]["videoCount"] != out[0]["sampleVideoCount"]

    asyncio.run(_run())


def test_popular_hashtags_ranks_by_population_not_sample() -> None:
    async def _run() -> None:
        posts = [
            {
                "hashtags": [{"name": "tiny"}, {"name": "huge"}],
                "engagement": {"views": 100},
            },
            {
                "hashtags": [{"name": "tiny"}],
                "engagement": {"views": 100},
            },
        ]

        async def _detail(name: str):
            return {
                "hashtagId": name,
                "name": name,
                "videoCount": 1 if name == "tiny" else 9_999_999,
                "totalPlays": 10 if name == "tiny" else 9_999_999_999,
                "growthRate": None,
            }

        with (
            patch(
                "app.services.tiktok_native.hashtag_posts_native",
                new=AsyncMock(return_value=(posts, False, None)),
            ),
            patch(
                "app.services.tiktok_native.challenge_detail_native",
                new=AsyncMock(side_effect=_detail),
            ),
        ):
            got = await popular_hashtags_native("skincare", limit=10, n_videos=10)
        assert got is not None
        assert got["sampleSize"] == 2
        assert got["discovery"] == "co_occurrence"
        assert got["hashtags"][0]["name"] == "huge"
        assert got["hashtags"][0]["rank"] == 1
        assert got["hashtags"][0]["videoCount"] == 9_999_999
        assert got["hashtags"][0]["sampleVideoCount"] == 1
        tiny = next(h for h in got["hashtags"] if h["name"] == "tiny")
        assert tiny["sampleVideoCount"] == 2
        assert tiny["videoCount"] == 1

    asyncio.run(_run())