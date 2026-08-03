from __future__ import annotations

from app.routers import youtube as yt


def test_long_form_not_a_short() -> None:
    assert (
        yt._is_youtube_short_payload(
            {"durationSeconds": 2971, "viewCount": 1},
            input_url="https://www.youtube.com/shorts/DXVHmGoCTco",
        )
        is False
    )


def test_classic_short_watch_url() -> None:
    assert (
        yt._is_youtube_short_payload(
            {"durationSeconds": 45, "viewCount": 1},
            input_url="https://www.youtube.com/watch?v=abc",
        )
        is True
    )


def test_shorts_eligible_under_three_minutes() -> None:
    assert (
        yt._is_youtube_short_payload(
            {"durationSeconds": 120, "isShortsEligible": True, "viewCount": 1},
            input_url="https://www.youtube.com/watch?v=abc",
        )
        is True
    )


def test_two_minute_watch_without_signal_rejected() -> None:
    assert (
        yt._is_youtube_short_payload(
            {"durationSeconds": 120, "viewCount": 1},
            input_url="https://www.youtube.com/watch?v=abc",
        )
        is False
    )


def test_stamp_short_fields() -> None:
    out = yt._stamp_short_fields(
        {"title": "x", "durationSeconds": 30, "url": "https://www.youtube.com/watch?v=abcdefghijk"},
        "abcdefghijk",
    )
    assert out["isShort"] is True
    assert out["contentType"] == "short"
    assert out["url"] == "https://www.youtube.com/shorts/abcdefghijk"
