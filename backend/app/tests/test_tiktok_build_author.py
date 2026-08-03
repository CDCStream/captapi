from __future__ import annotations

from app.routers.tiktok import _tt_finalize_post
from app.services.tiktok_native import build_author, _map_aweme_post


def test_build_author_stable_keys_when_sparse() -> None:
    author = build_author({"unique_id": "khaby.lame", "nickname": "Khabane lame"})
    assert set(author) >= {
        "id",
        "secUid",
        "username",
        "displayName",
        "url",
        "followers",
        "verified",
        "profileImage",
    }
    assert author["username"] == "khaby.lame"
    assert author["followers"] is None
    assert author["verified"] is None


def test_build_author_reads_followers_and_verified() -> None:
    author = build_author(
        {"unique_id": "nasa", "verified": True, "follower_count": 100},
    )
    assert author["followers"] == 100
    assert author["verified"] is True


def test_finalize_keeps_null_followers() -> None:
    out = _tt_finalize_post(
        {
            "id": "1",
            "hashtags": [],
            "author": build_author({"unique_id": "u"}),
        }
    )
    assert "followers" in out["author"]
    assert out["author"]["followers"] is None
    assert out["author"]["verified"] is None


def test_map_aweme_author_has_followers_key() -> None:
    row = _map_aweme_post(
        {
            "aweme_id": "1",
            "desc": "hi",
            "author": {"unique_id": "u", "uid": "9", "sec_uid": "SEC"},
            "statistics": {"play_count": 1},
            "video": {"duration": 5, "cover": {"url_list": ["https://cdn.example/c.jpg"]}},
        }
    )
    assert row is not None
    assert row["author"]["followers"] is None
    assert row["author"]["id"] == "9"
    assert row["author"]["secUid"] == "SEC"


def test_finalize_engagement_defaults_missing_shares_to_zero() -> None:
    out = _tt_finalize_post(
        {
            "id": "1",
            "engagement": {"views": 10, "likes": 2, "comments": 1, "saves": 0},
            "hashtags": None,
        }
    )
    assert out["engagement"] == {
        "views": 10,
        "likes": 2,
        "comments": 1,
        "shares": 0,
        "saves": 0,
    }
    assert out["hashtags"] == []
    assert out["mentions"] == []
    assert out["isAd"] is False
    assert out["isPaidPartnership"] is False
