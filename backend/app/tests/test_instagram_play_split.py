from __future__ import annotations

from app.services import instagram_decodo as decodo


def test_split_play_counts_three_way() -> None:
    split = decodo.split_play_counts(
        play_count=293_700,
        ig_play_count=235_383,
        fb_play_count=58_317,
        likes=10_000,
        is_video=True,
    )
    # No distinct video_view_count → views stays null (never echo plays).
    assert split["views"] is None
    assert split["viewsSource"] is None
    assert split["plays"] == 293_700
    assert split["viewsInstagram"] == 235_383
    assert split["viewsFacebook"] == 58_317


def test_split_play_counts_views_vs_plays_distinct() -> None:
    """SC-style Reel: video_view_count ≪ video_play_count (~2×)."""
    split = decodo.split_play_counts(
        play_count=46_018,
        video_view_count=21_808,
        likes=3_487,
        is_video=True,
    )
    assert split["views"] == 21_808
    assert split["viewsSource"] == "video_view_count"
    assert split["plays"] == 46_018


def test_split_play_counts_drops_identical_views_plays() -> None:
    """Same number labeled as both view_count and play_count → keep plays only."""
    split = decodo.split_play_counts(
        play_count=1_157_752,
        video_view_count=1_157_752,
        ig_play_count=1_157_752,
        likes=117_977,
        is_video=True,
    )
    assert split["plays"] == 1_157_752
    assert split["views"] is None
    assert split["viewsSource"] is None
    assert split["viewsInstagram"] == 1_157_752
    assert split["viewsFacebook"] is None


def test_split_play_counts_derives_facebook() -> None:
    split = decodo.split_play_counts(
        play_count=293_700,
        ig_play_count=235_383,
        likes=10_000,
        is_video=True,
    )
    assert split["viewsFacebook"] == 58_317


def test_engagement_with_play_split_on_video() -> None:
    eng = decodo.engagement_with_play_split(
        {"likes": 100, "comments": 5},
        play_count=293_700,
        ig_play_count=235_383,
        fb_play_count=58_317,
        likes=100,
        is_video=True,
    )
    assert eng["views"] is None
    assert eng["viewsSource"] is None
    assert eng["plays"] == 293_700
    assert eng["viewsInstagram"] == 235_383
    assert eng["viewsFacebook"] == 58_317


def test_engagement_keeps_null_plays_on_video() -> None:
    eng = decodo.engagement_with_play_split(
        {"likes": 1_647_990, "comments": 50_177},
        play_count=None,
        likes=1_647_990,
        is_video=True,
    )
    assert eng["views"] is None
    assert eng["viewsSource"] is None
    assert eng["plays"] is None
    assert "plays" in eng


def test_strip_keeps_null_play_keys_on_video() -> None:
    post = {
        "postType": "Video",
        "productType": "clips",
        "videoUrl": "https://cdn.example/r.mp4",
        "durationSeconds": 12,
        "engagement": {
            "views": None,
            "viewsSource": None,
            "viewsInstagram": None,
            "viewsFacebook": None,
            "likes": 100,
            "comments": 5,
            "plays": None,
        },
    }
    out = decodo.strip_null_post_fields(post)
    assert out["engagement"]["views"] is None
    assert out["engagement"]["viewsSource"] is None
    assert out["engagement"]["plays"] is None
    assert out["engagement"]["viewsInstagram"] is None


def test_strip_keeps_instagram_facebook_view_keys_on_video() -> None:
    post = {
        "postType": "Video",
        "productType": "clips",
        "videoUrl": "https://cdn.example/r.mp4",
        "durationSeconds": 12,
        "engagement": {
            "views": 21_808,
            "viewsSource": "video_view_count",
            "viewsInstagram": 235_383,
            "viewsFacebook": 58_317,
            "likes": 100,
            "comments": 5,
            "plays": 46_018,
        },
    }
    out = decodo.strip_null_post_fields(post)
    assert out["engagement"]["views"] == 21_808
    assert out["engagement"]["viewsSource"] == "video_view_count"
    assert out["engagement"]["plays"] == 46_018
    assert out["engagement"]["viewsInstagram"] == 235_383
    assert out["engagement"]["viewsFacebook"] == 58_317


def test_map_ig_location_address_json() -> None:
    loc = decodo.map_ig_location(
        {
            "id": "110103980565013",
            "name": "Central Park, New York City",
            "slug": "central-park-new-york-city",
            "has_public_page": True,
            "address_json": (
                '{"street_address": "5th Avenue & 59th Street", '
                '"zip_code": "10019", "city_name": "New York, New York"}'
            ),
        }
    )
    assert loc is not None
    assert loc["id"] == "110103980565013"
    assert loc["slug"] == "central-park-new-york-city"
    assert loc["hasPublicPage"] is True
    assert loc["address"]["zipCode"] == "10019"
    assert loc["address"]["cityName"] == "New York, New York"
