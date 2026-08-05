"""Rumble duration schema: durationSeconds + durationText only."""

from __future__ import annotations

from app.routers import rumble
from app.services import rumble_video_native as native


def test_stamp_duration_from_clock_string() -> None:
    out = rumble._stamp_duration(
        {"duration": "1:26:25", "durationFormatted": "01:26:25"}
    )
    assert out["durationSeconds"] == 5185
    assert out["durationText"] == "1:26:25"
    assert "duration" not in out
    assert "durationFormatted" not in out


def test_stamp_duration_from_seconds() -> None:
    out = rumble._stamp_duration({"durationSeconds": 55})
    assert out["durationSeconds"] == 55
    assert out["durationText"] == "0:55"
    assert "duration" not in out
    assert "durationFormatted" not in out


def test_normalize_az_video_duration_pair() -> None:
    out = rumble._normalize_az_video(
        {
            "object_type": "video",
            "permalink_id": "v7cv2cc",
            "embed_id": "v7cv2cc",
            "title": "Sample",
            "duration": "1:26:25",
            "by": {"name": "Show", "url": "https://rumble.com/c/bongino"},
            "rumble_votes": {"num_votes_up": 10, "num_votes_down": 1},
            "comments": {"count": 3},
            "views": 100,
            "url": "https://rumble.com/v7cv2cc-sample.html",
            "upload_date": "2026-07-17T12:18:39+00:00",
        },
        include_description=False,
    )
    assert out["durationSeconds"] == 5185
    assert out["durationText"] == "1:26:25"
    assert "duration" not in out
    assert "durationFormatted" not in out
    assert "embedUrl" not in out
    assert "embedId" not in out


def test_normalize_az_keeps_distinct_embed_id() -> None:
    out = rumble._normalize_az_video(
        {
            "permalink_id": "v7cv2cc",
            "embed_id": "v7aoh22",
            "title": "Sample",
            "duration": 90,
            "by": {"name": "Show", "url": "https://rumble.com/c/bongino"},
            "url": "https://rumble.com/v7cv2cc-sample.html",
        },
        include_description=False,
    )
    assert out["embedId"] == "v7aoh22"
    assert out["embedUrl"] == "https://rumble.com/embed/v7aoh22/"
    assert out["durationSeconds"] == 90
    assert out["durationText"] == "1:30"


def test_apply_embedjs_drops_legacy_duration() -> None:
    card = {
        "id": "v7cv2cc",
        "duration": "1:26:25",
        "durationFormatted": "01:26:25",
    }
    native.apply_embedjs(card, {"duration": 5185, "video": "v7aoh22"})
    assert card["durationSeconds"] == 5185
    assert card["durationText"] == "1:26:25"
    assert "duration" not in card
    assert "durationFormatted" not in card
