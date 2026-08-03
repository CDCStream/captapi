from __future__ import annotations

from app.services import instagram_native as native
from app.routers import instagram as ig_router


def test_is_reel_post_rejects_photos_and_carousels() -> None:
    assert native.is_reel_post({"postType": "Image", "productType": "feed"}) is False
    assert native.is_reel_post({"postType": "Sidecar", "productType": "carousel_container"}) is False
    assert native.is_reel_post({"postType": "Video", "productType": "clips"}) is True
    assert native.is_reel_post({"postType": "Image", "videoUrl": "https://cdn/x.mp4"}) is True


def test_stale_explore_posts_dropped() -> None:
    assert native._is_stale_explore_post({"publishedAt": "2018-10-10T23:52:29Z"}) is True
    assert native._is_stale_explore_post({"publishedAt": "2026-07-01T00:00:00Z"}) is False


def test_normalize_trending_item_splits_composite_id() -> None:
    row = ig_router._normalize_trending_item(
        {
            "id": "3948507321457537241_25025320",
            "code": "DbL6n0ggXDZ",
            "username": "nasa",
            "is_video": True,
            "type": "clips",
            "caption": "Sound on @NASAHubble @NASAHubble",
            "plays": 13_000_000,
            "likes": 485_567,
            "comments": 2174,
            "date": "2026-07-24T18:46:42+00:00",
            "video_url": "https://cdn.example/reel.mp4",
            "url": "https://www.instagram.com/reel/DbL6n0ggXDZ/",
        }
    )
    assert row["id"] == "3948507321457537241"
    assert row["shortcode"] == "DbL6n0ggXDZ"
    assert row["postType"] == "Video"
    assert row["mentions"] == ["NASAHubble"]
    assert ig_router._filter_trending_reels_only([row]) == [row]


def test_filter_drops_photo_junk_from_docs_example() -> None:
    junk = ig_router._normalize_trending_item(
        {
            "id": "1887399283873099090_7177109026",
            "username": "_funtastic.tendo_",
            "is_video": False,
            "type": "feed",
            "caption": "old nicktoons collage",
            "likes": 38,
            "comments": 2,
            "date": "2018-10-10T23:52:29+00:00",
            "url": "https://www.instagram.com/p/BoxY6YYlS1S/",
        }
    )
    assert junk["postType"] == "Image"
    assert ig_router._filter_trending_reels_only([junk]) == []
