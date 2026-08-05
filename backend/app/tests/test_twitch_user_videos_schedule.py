"""Twitch user-videos lean rows + schedule segment mapping."""

from __future__ import annotations

from app.services import twitch_native as tn


def test_video_node_lean_omits_channel_bloat():
    node = {
        "id": "1",
        "title": "vod",
        "language": "EN",
        "previewThumbnailURL": "https://cdn/thumb0-{width}x{height}.jpg",
        "broadcastType": "ARCHIVE",
        "game": {"id": "g", "name": "Just Chatting", "slug": "just-chatting"},
    }
    channel = {"id": "9", "username": "shroud"}
    fat = tn._video_node(node, broadcaster="shroud", profile_image="https://x", broadcaster_meta=channel)
    lean = tn._video_node(node, lean=True)
    assert "channel" in fat
    assert "broadcaster" in fat
    assert "channel" not in lean
    assert "broadcaster" not in lean
    assert "broadcasterProfileImage" not in lean
    assert lean["language"] == "en"
    assert "{width}" not in lean["thumbnail"]
    assert lean["thumbnailTemplate"] and "{width}" in lean["thumbnailTemplate"]


def test_map_schedule_segment_fields():
    seg = {
        "id": "seg1",
        "title": "One-shot",
        "startAt": "2026-08-07T02:00:00Z",
        "endAt": "2026-08-07T06:00:00Z",
        "isCancelled": False,
        "cancelledUntil": None,
        "firstOccurrenceDate": "2026-08-07T02:00:00Z",
        "repeatEndsAfterCount": 1,
        "categories": [{"id": "509664", "name": "Tabletop RPGs"}],
    }
    out = tn._map_schedule_segment(seg)
    assert out["id"] == "seg1"
    assert out["startedAt"] == "2026-08-07T02:00:00Z"
    assert out["endedAt"] == "2026-08-07T06:00:00Z"
    assert out["startAt"] == out["startedAt"]  # deprecated alias
    assert out["isRecurring"] is False
    assert out["isCancelled"] is False
    assert out["game"] == "Tabletop RPGs"
    assert out["gameId"] == "509664"
    assert "canceledUntil" not in out  # null stripped

    recurring = tn._map_schedule_segment(
        {
            **seg,
            "id": "seg2",
            "repeatEndsAfterCount": 0,
            "cancelledUntil": "2026-08-08T06:00:00Z",
            "isCancelled": True,
        }
    )
    assert recurring["isRecurring"] is True
    assert recurring["canceledUntil"] == "2026-08-08T06:00:00Z"
    assert recurring["isCancelled"] is True
