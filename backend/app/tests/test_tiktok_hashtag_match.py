from __future__ import annotations

from app.services.tiktok_native import item_has_hashtag, normalize_hashtag_query


def test_normalize_hashtag_query() -> None:
    assert normalize_hashtag_query("#Comedy") == "comedy"
    assert normalize_hashtag_query("  comedy  ") == "comedy"


def test_item_has_hashtag_structured() -> None:
    assert item_has_hashtag({"hashtags": ["comedy", "funny"]}, "comedy")
    assert item_has_hashtag({"hashtags": [{"name": "Comedy"}]}, "#comedy")
    assert not item_has_hashtag({"hashtags": ["funnyvideos", "funny"]}, "comedy")


def test_item_has_hashtag_caption_token() -> None:
    assert item_has_hashtag({"caption": "lol #comedy night"}, "comedy")
    assert not item_has_hashtag({"caption": "lol #comedytime"}, "comedy")
    # Username-only match must not pass.
    assert not item_has_hashtag(
        {
            "caption": "hello world",
            "hashtags": [],
            "author": {"username": "comedy7092"},
        },
        "comedy",
    )


def test_item_has_hashtag_rejects_keyword_bleed_example() -> None:
    # Real audit case: tagged funny* but not comedy.
    post = {
        "hashtags": [
            "funnyvideos",
            "funny",
            "indiafunny",
            "trendingfunny",
            "videofunny",
            "sitcomfunny",
            "funnysitcom",
        ],
        "caption": "#funnyvideos #funny #indiafunny",
        "author": {"username": "comedyfunj"},
    }
    assert not item_has_hashtag(post, "comedy")