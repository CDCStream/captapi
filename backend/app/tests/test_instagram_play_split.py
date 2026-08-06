from __future__ import annotations

from app.services import instagram_decodo as decodo


def test_split_play_counts_canonical_views() -> None:
    split = decodo.split_play_counts(
        play_count=293_700,
        ig_play_count=235_383,
        fb_play_count=58_317,
        likes=10_000,
        is_video=True,
    )
    # Prefer total play_count as engagement.views.
    assert split["views"] == 293_700
    assert split["viewsSource"] == "instagram"
    assert split["plays"] == 293_700  # deprecated alias
    assert "viewsInstagram" not in split
    assert "viewsFacebook" not in split


def test_split_play_counts_ig_only() -> None:
    split = decodo.split_play_counts(
        ig_play_count=235_383,
        likes=10_000,
        is_video=True,
    )
    assert split["views"] == 235_383
    assert split["viewsSource"] == "instagram"
    assert split["plays"] == 235_383


def test_split_play_counts_facebook_only() -> None:
    split = decodo.split_play_counts(
        fb_play_count=58_317,
        likes=10_000,
        is_video=True,
    )
    assert split["views"] == 58_317
    assert split["viewsSource"] == "facebook"


def test_split_play_counts_rejects_gql_undercount() -> None:
    """GraphQL video_view_count alone undercounts vs likes — null, not a lie."""
    split = decodo.split_play_counts(
        video_view_count=112_487,
        likes=485_567,
        is_video=True,
    )
    assert split["views"] is None
    assert split["viewsSource"] is None
    assert split["plays"] is None


def test_split_play_counts_gql_when_only_signal() -> None:
    split = decodo.split_play_counts(
        video_view_count=21_808,
        likes=3_487,
        is_video=True,
    )
    assert split["views"] == 21_808
    assert split["viewsSource"] == "instagram"


def test_split_play_counts_identical_signals() -> None:
    split = decodo.split_play_counts(
        play_count=1_157_752,
        video_view_count=1_157_752,
        ig_play_count=1_157_752,
        likes=117_977,
        is_video=True,
    )
    assert split["views"] == 1_157_752
    assert split["viewsSource"] == "instagram"
    assert split["plays"] == 1_157_752


def test_engagement_with_play_split_on_video() -> None:
    eng = decodo.engagement_with_play_split(
        {"likes": 100, "comments": 5},
        play_count=293_700,
        ig_play_count=235_383,
        fb_play_count=58_317,
        likes=100,
        is_video=True,
    )
    assert eng["views"] == 293_700
    assert eng["viewsSource"] == "instagram"
    assert eng["plays"] == 293_700
    assert "viewsInstagram" not in eng
    assert "viewsFacebook" not in eng


def test_engagement_keeps_null_views_on_video() -> None:
    eng = decodo.engagement_with_play_split(
        {"likes": 1_647_990, "comments": 50_177},
        play_count=None,
        likes=1_647_990,
        is_video=True,
    )
    assert eng["views"] is None
    assert eng["viewsSource"] is None
    assert eng["plays"] is None
    assert "viewsSource" in eng


def test_strip_keeps_null_view_keys_on_video() -> None:
    post = {
        "postType": "Video",
        "productType": "clips",
        "videoUrl": "https://cdn.example/r.mp4",
        "durationSeconds": 12.011,
        "engagement": {
            "views": None,
            "viewsSource": None,
            "likes": 100,
            "comments": 5,
            "plays": None,
            "viewsInstagram": None,
            "viewsFacebook": None,
        },
    }
    out = decodo.strip_null_post_fields(post)
    assert out["engagement"]["views"] is None
    assert out["engagement"]["viewsSource"] is None
    assert out["engagement"]["plays"] is None
    assert "viewsInstagram" not in out["engagement"]
    assert "viewsFacebook" not in out["engagement"]
    assert out["durationSeconds"] == 12.011


def test_strip_wires_discriminator_with_views() -> None:
    post = {
        "postType": "Video",
        "productType": "clips",
        "videoUrl": "https://cdn.example/r.mp4",
        "durationSeconds": 12,
        "engagement": {
            "views": 46_018,
            "viewsSource": None,  # must be filled
            "likes": 100,
            "comments": 5,
            "plays": 46_018,
            "viewsInstagram": 40_000,  # retired — dropped
        },
    }
    out = decodo.strip_null_post_fields(post)
    assert out["engagement"]["views"] == 46_018
    assert out["engagement"]["viewsSource"] == "instagram"
    assert out["engagement"]["plays"] == 46_018
    assert "viewsInstagram" not in out["engagement"]


def test_acceptance_no_100pct_null_engagement_key() -> None:
    rows = [
        decodo.engagement_with_play_split(
            {"likes": 10, "comments": 1}, play_count=100, likes=10, is_video=True
        ),
        decodo.engagement_with_play_split(
            {"likes": 20, "comments": 2}, play_count=None, likes=20, is_video=True
        ),
    ]
    # views/viewsSource/plays may be null on some rows, never on all if any row has data…
    # stricter: no key that is null on EVERY row that has the key.
    keys = set().union(*(r.keys() for r in rows))
    for k in keys:
        assert not all(r.get(k) is None for r in rows if k in r) or k in {
            # comments/likes always filled here; views may be null on row 2 only
        }
    assert rows[0]["views"] is not None and rows[0]["viewsSource"] is not None
    assert all(r["views"] is None or r["viewsSource"] is not None for r in rows)


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
