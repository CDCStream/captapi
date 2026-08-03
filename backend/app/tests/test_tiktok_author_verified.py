from __future__ import annotations

from app.routers.tiktok import _normalize_aweme, _tt_finalize_post
from app.services.tiktok_native import _map_aweme_post, author_verified_flag


def test_author_verified_flag_explicit_bool() -> None:
    assert author_verified_flag({'verified': True}) is True
    assert author_verified_flag({'verified': False}) is False
    assert author_verified_flag({'is_verified': True}) is True


def test_author_verified_flag_custom_verify() -> None:
    assert author_verified_flag({'custom_verify': 'Verified account'}) is True
    assert author_verified_flag({'custom_verify': ''}) is False
    assert author_verified_flag({'enterprise_verify_reason': 'Brand'}) is True


def test_author_verified_flag_unknown_is_null() -> None:
    assert author_verified_flag({}) is None
    assert author_verified_flag({'unique_id': 'khaby.lame', 'nickname': 'Khabane lame'}) is None
    assert author_verified_flag(None) is None


def test_map_aweme_music_surface_verified_null() -> None:
    # MUSIC_AWEME-style author cards omit badge fields -- must not invent false.
    row = _map_aweme_post(
        {
            "aweme_id": "7646812028874673439",
            "desc": "Thank you #comedy",
            "author": {
                "unique_id": "khaby.lame",
                "nickname": "Khabane lame",
                "uid": "1",
            },
            "statistics": {"play_count": 1, "digg_count": 1},
            "video": {
                "duration": 10,
                "cover": {"url_list": ["https://cdn.example/c.jpg"]},
            },
        }
    )
    assert row is not None
    assert row["author"]["verified"] is None
    out = _tt_finalize_post(row)
    assert out["author"]["verified"] is None


def test_map_aweme_keeps_explicit_false() -> None:
    row = _map_aweme_post(
        {
            "aweme_id": "1",
            "desc": "hi",
            "author": {"unique_id": "u", "verified": False},
            "statistics": {"play_count": 1},
            "video": {
                "duration": 5,
                "cover": {"url_list": ["https://cdn.example/c.jpg"]},
            },
        }
    )
    assert row is not None
    assert row["author"]["verified"] is False


def test_normalize_aweme_verified_null() -> None:
    out = _normalize_aweme(
        {
            "video_id": "1",
            "title": "hi",
            "author": {"unique_id": "khaby.lame", "nickname": "Khabane lame"},
            "digg_count": 1,
            "play_count": 1,
        }
    )
    assert out["author"]["verified"] is None
