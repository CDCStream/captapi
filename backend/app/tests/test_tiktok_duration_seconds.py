from __future__ import annotations

from app.routers.tiktok import _tt_finalize_post
from app.services.tiktok_native import _map_aweme_post
from app.utils.formatters import duration_seconds


def test_duration_seconds_always_float() -> None:
    assert duration_seconds(47) == 47.0
    assert isinstance(duration_seconds(47), float)
    assert duration_seconds(29.5341) == 29.534
    assert duration_seconds(None) is None


def test_finalize_coerces_duration_to_float() -> None:
    out = _tt_finalize_post({"id": "1", "durationSeconds": 47, "hashtags": []})
    assert out["durationSeconds"] == 47.0
    assert isinstance(out["durationSeconds"], float)


def test_map_aweme_duration_is_float() -> None:
    row = _map_aweme_post(
        {
            "aweme_id": "1",
            "desc": "hi",
            "author": {"unique_id": "u"},
            "statistics": {"play_count": 1},
            "video": {"duration": 13, "cover": {"url_list": ["https://cdn.example/c.jpg"]}},
        }
    )
    assert row is not None
    assert row["durationSeconds"] == 13.0
    assert isinstance(row["durationSeconds"], float)
