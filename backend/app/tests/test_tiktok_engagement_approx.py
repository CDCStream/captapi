"""Per-counter engagement approximate flags (TV1)."""

from __future__ import annotations

from app.services.tiktok_native import (
    _engagement_with_approx,
    _tiktok_stat_looks_display_rounded,
)
from app.utils.media_urls import cdn_expires_at, earliest_cdn_expires_at


def test_display_rounded_ladder() -> None:
    assert _tiktok_stat_looks_display_rounded(18_000_000) is True
    assert _tiktok_stat_looks_display_rounded(1_700_000) is True
    assert _tiktok_stat_looks_display_rounded(17_500) is True
    assert _tiktok_stat_looks_display_rounded(17_400) is True
    assert _tiktok_stat_looks_display_rounded(67_849) is False
    assert _tiktok_stat_looks_display_rounded(999) is False


def test_engagement_per_counter_flags() -> None:
    stats = {
        "playCount": 18_000_000,
        "diggCount": 1_700_000,
        "commentCount": 17_500,
        "shareCount": 17_400,
        "collectCount": 67_849,
    }
    # Web itemStruct often echoes the same rounded ints into statsV2 strings.
    stats_v2 = {k: str(v) for k, v in stats.items()}
    eng = _engagement_with_approx(stats_v2, stats)
    assert eng["views"] == 18_000_000
    assert eng["viewsIsApproximate"] is True
    assert eng["likesIsApproximate"] is True
    assert eng["commentsIsApproximate"] is True
    assert eng["sharesIsApproximate"] is True
    assert eng["saves"] == 67_849
    assert eng["savesIsApproximate"] is False
    assert "isApproximate" not in eng


def test_engagement_exact_when_v2_differs() -> None:
    stats = {"playCount": 18_000_000, "diggCount": 1_700_000}
    stats_v2 = {"playCount": "18001234", "diggCount": "1700456"}
    eng = _engagement_with_approx(stats_v2, stats)
    assert eng["views"] == 18_001_234
    assert eng["viewsIsApproximate"] is False
    assert eng["likesIsApproximate"] is False


def test_cdn_expire_prefers_second_precision() -> None:
    # TikTok play URLs carry expire= (seconds). Prefer that over hour-floored x-expires.
    play = (
        "https://v16.tiktokcdn.com/x/?expire=1786388676"
        "&x-expires=1786388400"
    )
    assert cdn_expires_at(play) == "2026-08-10T19:04:36.000Z"
    download = "https://v16.tiktokcdn.com/y/?expire=1786388676"
    # video-details uses playback/download only; cover/avatar often floor to the hour.
    assert earliest_cdn_expires_at(play, download) == "2026-08-10T19:04:36.000Z"
