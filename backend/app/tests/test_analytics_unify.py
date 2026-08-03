#"""Unit tests for cross-platform analytics unify + YouTube row shaping."""

from __future__ import annotations

from app.routers import analytics as a


def test_youtube_handle_never_uses_display_name() -> None:
    assert a._youtube_handle({"channelName": "Rick Astley"}) is None
    assert a._youtube_handle({"channelHandle": "@RickAstleyYT"}) == "RickAstleyYT"
    assert a._youtube_handle({"channelUsername": "RickAstleyYT"}) == "RickAstleyYT"


def test_youtube_row_complete_requires_showcase_fields() -> None:
    thin = a._youtube_analytics_row(
        {"title": "x", "viewCount": 100, "channelName": "Rick Astley"},
        norm="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video_id="dQw4w9WgXcQ",
    )
    assert thin["author"]["username"] is None
    assert thin["author"]["displayName"] == "Rick Astley"
    assert not a._youtube_row_complete(thin)

    rich = a._youtube_analytics_row(
        {
            "title": "x",
            "viewCount": 100,
            "likeCount": 10,
            "commentCount": 2,
            "publishedAt": "2009-10-24T23:57:33-07:00",
            "channelHandle": "@RickAstleyYT",
            "channelName": "Rick Astley",
        },
        norm="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video_id="dQw4w9WgXcQ",
    )
    assert a._youtube_row_complete(rich)


def test_unify_engagement_rate_basis_and_utc_published_at() -> None:
    out = a._unify(
        {
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "id": "dQw4w9WgXcQ",
            "caption": "Never Gonna Give You Up",
            "publishedAt": "2009-10-24T23:57:33-07:00",
            "author": {
                "username": "RickAstleyYT",
                "displayName": "Rick Astley",
                "verified": None,
            },
            "engagement": {
                "views": 1000,
                "likes": 100,
                "comments": 20,
                "shares": None,
                "saves": None,
            },
        }
    )
    assert out["publishedAt"] == "2009-10-25T06:57:33.000Z"
    assert out["metrics"]["interactions"] == 120
    assert out["metrics"]["engagementRate"] == 0.12
    assert out["metrics"]["engagementRateBasis"] == "interactions/views"
    assert out["author"]["username"] == "RickAstleyYT"
    assert out["author"]["displayName"] == "Rick Astley"


def test_unify_strips_display_name_leaked_into_username() -> None:
    out = a._unify(
        {
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "id": "dQw4w9WgXcQ",
            "caption": "x",
            "publishedAt": None,
            "author": {"username": "Rick Astley", "displayName": "Rick Astley"},
            "engagement": {"views": 10, "likes": None, "comments": None},
        }
    )
    assert out["author"]["username"] is None
    assert out["author"]["displayName"] == "Rick Astley"
    assert out["metrics"]["engagementRate"] is None
    assert out["metrics"]["engagementRateBasis"] == "interactions/views"
