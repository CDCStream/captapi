"""Instagram author shape + tagged-feed freshness + stale trending filter."""

from __future__ import annotations

from datetime import datetime, timezone

from app.routers import instagram as ig
from app.services import instagram_decodo as decodo
from app.services import instagram_native as native


def test_build_ig_author_stable_keys() -> None:
    author = decodo.build_ig_author(
        {
            "id": "99",
            "username": "natgeo",
            "full_name": "National Geographic",
            "is_verified": True,
            "profile_pic_url": "https://cdn.example/a.jpg",
            "follower_count": 1000,
        }
    )
    assert author["username"] == "natgeo"
    assert author["displayName"] == "National Geographic"
    assert author["verified"] is True
    assert author["profileImage"] == "https://cdn.example/a.jpg"
    assert author["url"] == "https://instagram.com/natgeo"


def test_merge_ig_author_fills_gaps() -> None:
    merged = decodo.merge_ig_author(
        {"username": "fan", "url": "https://instagram.com/fan"},
        {"verified": False, "profileImage": "https://cdn.example/f.jpg", "followers": 12},
    )
    assert merged["verified"] is False
    assert merged["profileImage"] == "https://cdn.example/f.jpg"
    assert merged["followers"] == 12


def test_tagged_feed_freshness_stale_2018() -> None:
    posts = [
        {"publishedAt": "2018-12-07T18:04:27Z"},
        {"publishedAt": "2018-12-07T17:02:28Z"},
    ]
    meta = ig._tagged_feed_freshness(posts)
    assert meta["staleFeed"] is True
    assert meta["newestPublishedAt"].startswith("2018-12-07")
    assert "archived" in (meta.get("note") or "").lower() or "365" in (meta.get("note") or "")


def test_tagged_feed_freshness_recent() -> None:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    meta = ig._tagged_feed_freshness([{"publishedAt": now}])
    assert meta["staleFeed"] is False
    assert "note" not in meta


def test_stale_explore_missing_published_at() -> None:
    assert native._is_stale_explore_post({"publishedAt": None}) is True


def test_stale_explore_old_date() -> None:
    assert native._is_stale_explore_post({"publishedAt": "2018-10-10T00:00:00Z"}) is True


def test_graphql_post_uses_build_ig_author() -> None:
    post = decodo._post(
        {
            "shortcode": "XYZ",
            "is_video": True,
            "__typename": "GraphVideo",
            "product_type": "clips",
            "like_count": 100,
            "video_play_count": 5000,
            "edge_media_to_comment": {"count": 10},
            "owner": {
                "id": "1",
                "username": "creator",
                "full_name": "Creator",
                "is_verified": True,
                "profile_pic_url": "https://cdn.example/c.jpg",
            },
            "taken_at_timestamp": 1_700_000_000,
        }
    )
    assert post["author"]["verified"] is True
    assert post["author"]["profileImage"] == "https://cdn.example/c.jpg"
    assert post["engagement"]["likes"] == 100
    assert post["engagement"]["views"] == 5000
