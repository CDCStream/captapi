"""Tests for YouTube video-details degraded / partial-extraction signalling."""

from __future__ import annotations

from app.routers.youtube import (
    _finalise_youtube_video_details,
    _video_details_is_partial,
)


def test_partial_when_published_or_likes_missing() -> None:
    assert _video_details_is_partial({"publishedAt": None, "likeCount": 1}) is True
    assert _video_details_is_partial({"publishedAt": "2009-10-24", "likeCount": None}) is True
    assert _video_details_is_partial({"publishedAt": "2009-10-24", "likeCount": 1}) is False


def test_finalise_stamps_degraded_channel_posts_shape() -> None:
    healthy = _finalise_youtube_video_details(
        {"publishedAt": "2009-10-24T23:57:33-07:00", "likeCount": 19},
        path="android+watch",
        watch_attempts=1,
    )
    assert healthy["degraded"] is False
    assert healthy["degradedReason"] is None
    assert healthy["timings"]["path"] == "android+watch"
    assert healthy["timings"]["watchAttempts"] == 1

    partial = _finalise_youtube_video_details(
        {"publishedAt": None, "likeCount": None, "viewCount": 1},
        path="android",
        watch_attempts=2,
    )
    assert partial["degraded"] is True
    assert partial["degradedReason"] == "partial-extraction"
    assert partial["timings"]["watchAttempts"] == 2
