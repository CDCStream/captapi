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


def test_streams_from_media_dedupes_1080_and_skips_audio() -> None:
    streams = native._streams_from_media(
        {
            "mp4": {
                "1080": {
                    "url": "https://cdn.example/haa.mp4?expire=2000000000",
                    "meta": {"bitrate": 3985, "w": 1920, "h": 1080},
                },
                "1081": {
                    "url": "https://cdn.example/aaa.mp4?expire=2000000000",
                    "meta": {"bitrate": 8051, "w": 1920, "h": 1080},
                },
                "480": {
                    "url": "https://cdn.example/caa.mp4",
                    "meta": {"bitrate": 1005, "w": 854, "h": 480},
                },
            },
            "audio": {
                "192": {
                    "url": "https://cdn.example/gaa.aac",
                    "meta": {"bitrate": 192, "w": 0, "h": 0},
                }
            },
        }
    )
    qualities = [s["quality"] for s in streams]
    assert qualities.count("1080p") == 1
    assert "1081p" not in qualities
    assert "192k" not in qualities
    assert all(s["type"] != "audio" for s in streams)
    # Higher bitrate 1081 key wins and keeps expiresAt.
    top = next(s for s in streams if s["quality"] == "1080p")
    assert top["url"].endswith("aaa.mp4?expire=2000000000")
    assert top["expiresAt"] == "2033-05-18T03:33:20.000Z"


def test_votes_compact_marks_likes_approximate() -> None:
    html = 'title="15.5K Likes | 194 Dislikes"'
    likes, dislikes, approx = native._votes_from_html(html)
    assert likes == 15500
    assert dislikes == 194
    assert approx is True


def test_normalize_az_always_emits_is_live() -> None:
    out = rumble._normalize_az_video(
        {
            "permalink_id": "vfresh",
            "title": "Just posted",
            "duration": 72,
            "views": 0,
            "url": "https://rumble.com/vfresh-just-posted.html",
            "by": {"name": "Show", "url": "https://rumble.com/c/bongino"},
        },
        include_description=False,
    )
    assert out["isLive"] is False
    assert out["type"] == "video"
