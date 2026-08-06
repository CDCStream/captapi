"""Shelved-endpoint key-set guard — silently dropping fields fails CI."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.rumble_video_details import (
    RUMBLE_VIDEO_DETAILS_KEYS,
    finalise_video_details,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "shelved_keysets"


def _load_keys(name: str) -> list[str]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_rumble_video_details_baseline_has_31_keys() -> None:
    baseline = _load_keys("rumble-video-details.keys.json")
    assert len(baseline) >= 31
    assert "captions" in baseline
    assert "embedUrl" in baseline
    assert "embedId" in baseline
    assert "audioStreams" in baseline
    assert "thumbnailTrack" in baseline
    assert list(RUMBLE_VIDEO_DETAILS_KEYS) == baseline


def test_finalise_video_details_never_shrinks_baseline() -> None:
    baseline = _load_keys("rumble-video-details.keys.json")
    # Simulate the Apify-slim regression (no captions / embed / media tracks).
    slim = {
        "platform": "rumble",
        "id": "v7cv2cc",
        "url": "https://rumble.com/v7cv2cc-x.html",
        "title": "Now I Can Finally Talk About It",
        "durationSeconds": 5185,
        "streams": [],
    }
    out = finalise_video_details(slim)
    lost = [k for k in baseline if k not in out]
    assert lost == []
    assert isinstance(out["captions"], list)
    assert isinstance(out["audioStreams"], list)
    assert "embedUrl" in out
    assert "thumbnailTrack" in out


def test_finalise_preserves_fixture_rich_fields() -> None:
    rich = {
        "id": "v7cv2cc",
        "embedId": "v7aoh22",
        "embedUrl": "https://rumble.com/embed/v7aoh22/",
        "title": "x",
        "description": "d",
        "width": 1920,
        "height": 1080,
        "likesIsApproximate": True,
        "captions": [
            {
                "code": "en-auto",
                "language": "English (auto)",
                "url": "https://example.com/a.vtt",
                "expiresAt": None,
            }
        ],
        "audioStreams": [{"url": "https://example.com/a.aac", "type": "audio/aac"}],
        "thumbnailTrack": {"url": "https://example.com/t.jpg", "type": "image"},
        "streams": [
            {
                "url": "https://example.com/v.mp4",
                "type": "video/mp4",
                "quality": "1080p",
                "width": 1920,
                "height": 1080,
                "bitrateKbps": 8000,
                "sizeBytes": 1,
                "expiresAt": None,
            }
        ],
    }
    out = finalise_video_details(rich)
    assert out["embedUrl"] == "https://rumble.com/embed/v7aoh22/"
    assert out["embedId"] == "v7aoh22"
    assert len(out["captions"]) == 1
    assert out["audioStreams"] and out["thumbnailTrack"]
    assert out["width"] == 1920 and out["height"] == 1080