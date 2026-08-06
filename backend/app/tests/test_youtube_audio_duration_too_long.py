"""duration_too_long preflight — 0 credits, no STT."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.core.auth import ApiCaller
from app.routers import youtube as yt


def test_duration_too_long_rejects_before_stt() -> None:
    caller = ApiCaller(
        user_id="u",
        api_key_id="k",
        plan="pro",
        subscription_credits=10_000,
        topup_credits=0,
    )

    async def _call():
        with patch.object(
            yt.youtube_audio,
            "video_duration_seconds",
            new=AsyncMock(return_value=12752),
        ):
            with patch.object(
                yt.youtube_audio,
                "extract_audio_bytes",
                new=AsyncMock(side_effect=AssertionError("STT must not run")),
            ):
                await yt.youtube_audio_transcript(
                    url="https://www.youtube.com/watch?v=E2s8Ff4SkLY",
                    language=None,
                    maxCredits=None,
                    cache=False,
                    caller=caller,
                )

    with pytest.raises(HTTPException) as ei:
        asyncio.run(_call())
    assert ei.value.status_code == 400
    detail = ei.value.detail
    assert isinstance(detail, dict)
    assert detail["code"] == "duration_too_long"
    assert detail["durationSeconds"] == 12752
    assert detail["estimatedCredits"] == 426
    assert detail["syncMaxSeconds"] == yt._YT_ASR_SYNC_MAX_SECONDS