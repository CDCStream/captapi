from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

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
    # plays alone — views stays null (not a silent plays copy); viewsSource null.
    assert row["engagement"]["views"] is None
    assert row["engagement"]["viewsSource"] is None
    assert row["engagement"]["plays"] == 13_000_000
    assert row["engagement"]["likes"] == 485_567
    assert "description" not in row
    assert "topic" not in row
    assert "section" not in row
    assert row["author"]["url"] == "https://www.instagram.com/nasa/"
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


def test_unsupported_country_is_400_with_list() -> None:
    with pytest.raises(HTTPException) as exc:
        ig_router._normalize_trending_country("Narnia")
    assert exc.value.status_code == 400
    detail = exc.value.detail
    assert isinstance(detail, dict)
    assert detail["error"]["code"] == "unsupported_country"
    assert "United States" in detail["error"]["supportedCountries"]


def test_warming_error_is_machine_readable() -> None:
    exc = ig_router._trending_warming_http("United States")
    assert exc.status_code == 503
    assert exc.headers["Retry-After"] == "600"
    assert exc.detail["error"]["code"] == "warming"
    assert exc.detail["error"]["retryAfterSeconds"] == 600
    assert exc.detail["error"]["country"] == "United States"


def test_freshness_marks_stale_after_refresh_window() -> None:
    fresh = ig_router._trending_freshness(
        cached_at=datetime.now(timezone.utc) - timedelta(hours=2),
        from_snapshot=True,
    )
    assert fresh["cached"] is True
    assert fresh["stale"] is False
    assert fresh["ageHours"] < 6
    assert "snapshotAt" in fresh
    assert fresh["cachedAt"] == fresh["snapshotAt"]

    old = ig_router._trending_freshness(
        cached_at=datetime.now(timezone.utc) - timedelta(hours=32),
        from_snapshot=True,
    )
    assert old["cached"] is True
    assert old["stale"] is True
    assert old["ageHours"] >= 30

    native = ig_router._trending_freshness(cached_at=None, from_snapshot=False)
    assert native["cached"] is False
    assert "cachedAt" not in native
    assert "snapshotAt" not in native
    assert native["ageHours"] == 0


def test_trending_payload_includes_iso_country_code() -> None:
    payload = ig_router._trending_payload(
        [],
        country="United States",
        freshness={"cached": False, "stale": False, "ageHours": 0},
    )
    assert payload["country"] == "United States"
    assert payload["countryCode"] == "US"


def test_sync_wait_budget_is_gateway_safe() -> None:
    assert ig_router._TRENDING_SYNC_WAIT_SECS <= 15
