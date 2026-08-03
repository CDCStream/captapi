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
    assert split["views"] == 293_700
    assert split["viewsInstagram"] == 235_383
    assert split["viewsFacebook"] == 58_317
    assert split["plays"] == 235_383


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
    assert eng["views"] == 293_700
    assert eng["viewsInstagram"] == 235_383
    assert eng["viewsFacebook"] == 58_317


def test_strip_keeps_instagram_facebook_view_keys_on_video() -> None:
    post = {
        "postType": "Video",
        "productType": "clips",
        "videoUrl": "https://cdn.example/r.mp4",
        "durationSeconds": 12,
        "engagement": {
            "views": 293_700,
            "viewsInstagram": 235_383,
            "viewsFacebook": 58_317,
            "likes": 100,
            "comments": 5,
            "plays": 235_383,
        },
    }
    out = decodo.strip_null_post_fields(post)
    assert out["engagement"]["views"] == 293_700
    assert out["engagement"]["viewsInstagram"] == 235_383
    assert out["engagement"]["viewsFacebook"] == 58_317