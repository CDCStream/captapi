from __future__ import annotations

from app.services import tiktok_creative_center_trends as cc


def test_normalize_trend_hashtag_population_not_sample() -> None:
    row = cc.normalize_trend_hashtag(
        {
            "hashtag_id": "7157084587318280197",
            "hashtag_name": "skincare",
            "publish_cnt": 56_953_998,
            "video_views": 954_780_316_160,
            "rank": 1,
            "rank_diff": 2,
            "rank_diff_type": 1,
            "trend": [
                {"time": 1739145600, "value": 0.4},
                {"time": 1739750400, "value": 0.6},
            ],
        },
        country="US",
        period=7,
    )
    assert row is not None
    assert row["videoCount"] == 56_953_998
    assert row["videoCount"] != 17
    assert row["totalPlays"] == 954_780_316_160
    assert row["rankDiff"] == 2
    assert len(row["trend"]) == 2
    assert row["growthRate"] == 0.5
    assert row["source"] == "creative_center"


def test_normalize_trend_song_commercial_flag() -> None:
    row = cc.normalize_trend_song(
        {
            "song_id": "7440101671265486864",
            "clip_id": "7439295283975702544",
            "title": "Test Song",
            "author": "Artist",
            "rank": 1,
            "rank_diff": 1,
            "if_cml": True,
            "promoted": False,
            "trend": [{"time": 1, "value": 0.15}],
        },
        country="US",
        period=7,
        rank_type="surging",
    )
    assert row is not None
    assert row["songId"] == "7440101671265486864"
    assert row["ifCml"] is True
    assert row["commercialMusic"] is True
    assert row["rankType"] == "surging"


def test_normalize_trend_creator_er_ratio_to_percent() -> None:
    row = cc.normalize_trend_creator(
        {
            "unique_id": "charlidamelio",
            "nick_name": "charli",
            "follower_cnt": 150_000_000,
            "interact_rate": 0.0413,
            "rank": 1,
            "uid": "123",
        },
        country="US",
    )
    assert row is not None
    assert row["username"] == "charlidamelio"
    assert row["engagementRate"] == 4.13
    assert row["engagementRateBasis"] == "creative_center"


def test_period_180_maps_to_120() -> None:
    assert cc.normalize_trend_period(180) == 120
    assert cc.normalize_trend_period(7) == 7


def test_normalize_video_order_by_aliases() -> None:
    assert cc.normalize_video_order_by("hot") == "vv"
    assert cc.normalize_video_order_by("like") == "like"
    assert cc.normalize_video_order_by("comment") == "comment"
    assert cc.normalize_video_order_by("repost") == "repost"
    assert cc.normalize_video_order_by("shares") == "repost"


def test_normalize_trend_video_sc_shape() -> None:
    row = cc.normalize_trend_video(
        {
            "id": "1",
            "item_id": "7123456789",
            "item_url": "https://www.tiktok.com/@x/video/7123456789",
            "region": "United States",
            "country_code": "US",
            "duration": 28,
            "cover": "https://example.com/c.jpg",
            "title": "Hello trend",
        },
        country="US",
        period=7,
        order_by="vv",
        rank=1,
    )
    assert row is not None
    assert row["id"] == "7123456789"
    assert row["caption"] == "Hello trend"
    assert row["rank"] == 1
    assert row["source"] == "creative_center"
    assert row["durationSeconds"] == 28
