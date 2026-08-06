from __future__ import annotations

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
            "duration": 12.011,
        }
    )
    assert row["id"] == "3948507321457537241"
    assert row["shortcode"] == "DbL6n0ggXDZ"
    assert row["postType"] == "Video"  # present pre-filter for is_reel_post
    assert row["mentions"] == ["NASAHubble"]
    # Canonical views = play count; viewsSource non-null whenever views is.
    assert row["engagement"]["views"] == 13_000_000
    assert row["engagement"]["viewsSource"] == "instagram"
    assert "plays" not in row["engagement"]
    assert "viewsInstagram" not in row["engagement"]
    assert row["engagement"]["likes"] == 485_567
    assert row["durationSeconds"] == 12.011
    assert "description" not in row
    assert "topic" not in row
    assert "section" not in row
    assert row["author"]["url"] == "https://www.instagram.com/nasa/"
    filtered = ig_router._filter_trending_reels_only([row])
    assert len(filtered) == 1
    assert "postType" not in filtered[0]
    assert "productType" not in filtered[0]


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


def test_scrape_failed_error_is_machine_readable() -> None:
    """Live scrape failure → 502; never a warming/snapshot fallback."""
    exc = ig_router._trending_scrape_failed_http("United States")
    assert exc.status_code == 502
    assert exc.detail["error"]["code"] == "scrape_failed"
    assert exc.detail["error"]["country"] == "United States"


def test_filtered_empty_error_is_distinct() -> None:
    exc = ig_router._trending_scrape_failed_http(
        "United States",
        code="filtered_empty",
        stages={"fetched": 12, "hydrated": 10, "afterReelFilter": 0},
    )
    assert exc.status_code == 502
    assert exc.detail["error"]["code"] == "filtered_empty"
    assert exc.detail["error"]["stages"]["fetched"] == 12
    assert "filters" in exc.detail["message"].lower()


def test_trending_payload_includes_iso_country_code() -> None:
    payload = ig_router._trending_payload([], country="United States", cached=False)
    assert payload["country"] == "United States"
    assert payload["countryCode"] == "US"
    assert payload["cached"] is False
    assert "2 credits" in payload["note"]
    assert "view count" in payload["note"]
    assert "snapshot" not in payload["note"].lower()
    assert "warming" not in payload["note"].lower()
    assert "apify" not in payload["note"].lower()


def test_trending_flat_credits() -> None:
    assert ig_router.CREDIT_TRENDING_REELS == 2


def test_slice_trending_payload() -> None:
    payload = {
        "reels": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
        "totalReturned": 3,
        "cached": False,
    }
    sliced = ig_router._slice_trending_payload(payload, 2)
    assert sliced["totalReturned"] == 2
    assert [r["id"] for r in sliced["reels"]] == ["1", "2"]


def test_live_budget_under_cloudflare() -> None:
    assert ig_router._TRENDING_HARD_DEADLINE_SECS <= 110
    assert ig_router._TRENDING_FLIGHT_WAIT_SECS < ig_router._TRENDING_HARD_DEADLINE_SECS
    assert ig_router._TRENDING_CACHE_TTL_SECS == 4 * 3600
    assert ig_router._TRENDING_STORE_LIMIT <= 40


def test_wire_trending_reel_drops_plays_keeps_duration() -> None:
    row = {
        "id": "1",
        "videoUrl": "https://cdn.example/a.mp4",
        "durationSeconds": None,
        "engagement": {
            "likes": 1,
            "comments": 0,
            "views": 100,
            "viewsSource": "instagram",
            "plays": 100,
        },
    }
    out = ig_router._wire_trending_reel(row)
    assert "plays" not in out["engagement"]
    assert out["durationSeconds"] is None
    assert out["engagement"]["views"] == 100
    assert out["engagement"]["viewsSource"] == "instagram"
    # Null/missing views → omit both views and viewsSource keys.
    bare = ig_router._wire_trending_reel(
        {"id": "2", "durationSeconds": None, "engagement": {"likes": 1, "comments": 0, "views": None}}
    )
    assert "views" not in bare["engagement"]
    assert "viewsSource" not in bare["engagement"]


def test_trending_engagement_acceptance() -> None:
    """No 100%-null engagement key; viewsSource tracks views; no plays."""
    rows = [
        ig_router._normalize_trending_item(
            {
                "id": "1_1",
                "code": "Aaa",
                "username": "a",
                "is_video": True,
                "type": "clips",
                "plays": 100,
                "likes": 10,
                "comments": 1,
                "date": "2026-07-24T18:46:42+00:00",
                "url": "https://www.instagram.com/reel/Aaa/",
                "video_url": "https://cdn.example/a.mp4",
                "duration": 12.011,
            }
        ),
        ig_router._normalize_trending_item(
            {
                "id": "2_1",
                "code": "Bbb",
                "username": "b",
                "is_video": True,
                "type": "clips",
                "likes": 20,
                "comments": 2,
                "date": "2026-07-24T18:46:42+00:00",
                "url": "https://www.instagram.com/reel/Bbb/",
                "video_url": "https://cdn.example/b.mp4",
                # duration omitted — key must still exist as null after wire
            }
        ),
    ]
    from app.services import instagram_decodo as decodo

    reels = [
        ig_router._wire_trending_reel(
            decodo.strip_null_post_fields(ig_router._filter_trending_reels_only([r])[0])
        )
        for r in rows
    ]
    assert all(
        r["engagement"].get("views") is None or r["engagement"].get("viewsSource") is not None
        for r in reels
    )
    # viewsSource is omitted when views is null (not a 100%-null key).
    assert reels[0]["engagement"].get("viewsSource") == "instagram"
    assert "viewsSource" not in reels[1]["engagement"]
    keys = set(reels[0]["engagement"]) | set(reels[1]["engagement"])
    assert "plays" not in keys
    for k in keys - {"views", "viewsSource"}:
        # Required engagement metrics must not be null on every row.
        assert not all(r["engagement"].get(k) is None for r in reels)
    assert reels[0]["durationSeconds"] == 12.011
    assert "durationSeconds" in reels[1]
    assert reels[1]["durationSeconds"] is None
    assert "postType" not in reels[0]
