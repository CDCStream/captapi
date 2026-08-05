from __future__ import annotations

from app.routers import youtube as yt


def test_long_form_not_a_short() -> None:
    assert (
        yt._is_youtube_short_payload(
            {"durationSeconds": 2971, "viewCount": 1},
            input_url="https://www.youtube.com/shorts/DXVHmGoCTco",
        )
        is False
    )


def test_classic_short_watch_url() -> None:
    assert (
        yt._is_youtube_short_payload(
            {"durationSeconds": 45, "viewCount": 1},
            input_url="https://www.youtube.com/watch?v=abc",
        )
        is True
    )


def test_shorts_eligible_under_three_minutes() -> None:
    assert (
        yt._is_youtube_short_payload(
            {"durationSeconds": 120, "isShortsEligible": True, "viewCount": 1},
            input_url="https://www.youtube.com/watch?v=abc",
        )
        is True
    )


def test_two_minute_watch_without_signal_rejected() -> None:
    assert (
        yt._is_youtube_short_payload(
            {"durationSeconds": 120, "viewCount": 1},
            input_url="https://www.youtube.com/watch?v=abc",
        )
        is False
    )


def test_stamp_short_fields() -> None:
    out = yt._stamp_short_fields(
        {
            "title": "x",
            "durationSeconds": 30,
            "commentCount": 11000,
            "genre": None,
            "categoryId": None,
            "url": "https://www.youtube.com/watch?v=abcdefghijk",
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/abcdefghijk/hq2.jpg",
                    "width": 480,
                    "height": 360,
                }
            ],
        },
        "abcdefghijk",
    )
    assert out["isShort"] is True
    assert out["contentType"] == "short"
    assert out["platform"] == "youtube"
    assert out["url"] == "https://www.youtube.com/shorts/abcdefghijk"
    assert out["durationFormatted"] == "00:00:30"
    assert out["commentCountIsApproximate"] is True
    assert "genre" not in out
    assert "categoryId" not in out
    assert "oardefault.jpg" in (out.get("thumbnailUrl") or "")


def test_merge_short_details_prefers_reel_microformat() -> None:
    from app.services.youtube_native import merge_short_player_details

    merged = merge_short_player_details(
        {
            "viewCount": 100,
            "publishedAt": None,
            "description": None,
            "channelHandle": None,
            "commentCount": 11000,
            "commentCountIsApproximate": True,
        },
        {
            "publishedAt": "2024-01-02T00:00:00Z",
            "description": "hi",
            "channelHandle": "@TopRanksKing",
            "thumbnails": [
                {"url": "https://i.ytimg.com/vi/x/oardefault.jpg", "width": 405, "height": 720}
            ],
            "thumbnailUrl": "https://i.ytimg.com/vi/x/oardefault.jpg",
        },
    )
    assert merged is not None
    assert merged["publishedAt"] == "2024-01-02T00:00:00Z"
    assert merged["description"] == "hi"
    assert merged["channelHandle"] == "@TopRanksKing"
    assert merged["viewCount"] == 100
    assert "oardefault" in (merged.get("thumbnailUrl") or "")


def test_normalize_trending_noop_query() -> None:
    assert yt._normalize_trending_topic_q("trending") is None
    assert yt._normalize_trending_topic_q("shorts") is None
    assert yt._normalize_trending_topic_q("fitness") == "fitness"
