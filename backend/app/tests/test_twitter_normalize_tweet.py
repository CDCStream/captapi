from __future__ import annotations

from app.routers.twitter import _merge_tweet_row, _normalize_profile, _normalize_tweet


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
            "source": '<a href="https://twitter.com">Twitter for iPhone</a>',
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
    assert row["isRetweet"] is False
    assert row["author"]["followers"] == 1
    assert set(row["engagement"]) == {
        "views",
        "likes",
        "replies",
        "retweets",
        "quotes",
        "bookmarks",
    }


def test_normalize_tweet_keeps_null_engagement_keys() -> None:
    row = _normalize_tweet(
        {
            "id_str": "2",
            "full_text": "no views here",
            "created_at": "Thu Apr 28 00:56:58 +0000 2022",
            "favorite_count": 10,
            "reply_count": 1,
            "retweet_count": 2,
            "quote_count": 3,
            "user": {"screen_name": "a", "name": "A"},
        }
    )
    assert row["publishedAt"] == "2022-04-28T00:56:58.000Z"
    assert row["engagement"]["views"] is None
    assert row["engagement"]["bookmarks"] is None
    assert row["engagement"]["likes"] == 10
    assert row["hashtags"] == []


def test_merge_tweet_row_fills_syndication_gaps() -> None:
    base = {
        "id_str": "99",
        "favorite_count": 10,
        "conversation_count": 2,
        "user": {"screen_name": "nasa", "verified": True},
    }
    richer = {
        "id_str": "99",
        "retweet_count": 7,
        "quote_count": 3,
        "reply_count": 2,
        "user": {"followers_count": 50, "id_str": "1"},
    }
    merged = _merge_tweet_row(base, richer)
    assert merged["retweet_count"] == 7
    assert merged["quote_count"] == 3
    assert merged["reply_count"] == 2
    assert merged["user"]["followers_count"] == 50
    out = _normalize_tweet(merged)
    assert out["engagement"]["retweets"] == 7
    assert out["engagement"]["quotes"] == 3
    assert out["author"]["followers"] == 50
    assert out["isRetweet"] is False


def test_normalize_profile_display_name_and_verified() -> None:
    row = _normalize_profile(
        {
            "id": "11348282",
            "userName": "NASA",
            "name": "NASA",
            "description": "Space",
            "isBlueVerified": True,
            "is_identity_verified": False,
            "followers": 1,
            "following": 1,
            "statusesCount": 1,
            "website": "http://www.nasa.gov/",
            "createdAt": "2007-12-19T20:20:32.000Z",
        }
    )
    assert row["displayName"] == "NASA"
    assert row["name"] == "NASA"
    assert row["verified"] is True
    assert row["website"] == "http://www.nasa.gov/"


def test_normalize_profile_verified_key_when_unknown() -> None:
    row = _normalize_profile({"userName": "nobody", "name": "Nobody"})
    assert row["verified"] is False
    assert row["displayName"] == "Nobody"
