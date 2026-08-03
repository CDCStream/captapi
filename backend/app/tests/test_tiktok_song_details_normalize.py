from __future__ import annotations

from app.services.tiktok_native import normalize_song_details



def test_normalize_song_duration_seconds_and_usage() -> None:
    music = {
        "id": "123",
        "title": "Test Sound",
        "author": "Alice",
        "owner_id": "999",
        "sec_uid": "ms-sec",
        "duration": 29.5341,
        "user_count": 12345,
        "create_time": 1700000000,
    }
    out = normalize_song_details(music, url="https://www.tiktok.com/music/test-123")
    assert out is not None
    assert out["durationSeconds"] == 29.534
    assert out["duration"] == 29.534
    assert out["usageCount"] == 12345
    assert out["artistId"] == "999"
    assert out["authorSecUid"] == "ms-sec"



def test_usage_zero_is_null() -> None:
    out = normalize_song_details(
        {"uid": "1", "title": "x", "duration": 10, "user_count": 0},
        url="https://www.tiktok.com/music/x-1",
    )
    assert out is not None
    assert out["usageCount"] is None
