from __future__ import annotations

from app.routers.twitter import _normalize_tweet


def test_normalize_tweet_iso_and_identity() -> None:
    row = _normalize_tweet(
        {
            "id_str": "1",
            "full_text": "Hello #NASA and #SpaceX",
            "created_at": "Thu Apr 28 00:56:58 +0000 2022",
            "lang": "en",
            "favorite_count": 10,
            "reply_count": 1,
            "retweet_count": 2,
            "quote_count": 3,
            "view_count": 99,
            "bookmark_count": 4,
            "source": "<a href=\"https://twitter.com\">Twitter for iPhone</a>",
            "conversation_id_str": "1",
            "is_quote_status": False,
            "possibly_sensitive": False,
            "user": {
                "id_str": "44196397",
                "screen_name": "elonmusk",
                "name": "Elon Musk",
                "followers_count": 1,
                "verified": True,
            },
        }
    )
    assert row["publishedAt"] == "2022-04-28T00:56:58.000Z"
    assert row["hashtags"] == ["NASA", "SpaceX"]
    assert row["engagement"]["views"] == 99
    assert row["engagement"]["bookmarks"] == 4
    assert row["source"] == "Twitter for iPhone"
    assert row["conversationId"] == "1"
    assert row["author"]["id"] == "44196397"
    assert row["media"] == []
    assert row["isQuote"] is False
