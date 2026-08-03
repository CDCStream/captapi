from __future__ import annotations

from app.services.tiktok_native import _map_trend_video


def test_map_trend_video_has_published_at_and_caption() -> None:
    row = _map_trend_video(
        {
            "id": "7660991836407811358",
            "desc": "#gta #viral",
            "createTime": 1_720_000_000,
            "isAd": False,
            "author": {
                "id": "123",
                "secUid": "MS4wLjABAAAAtest",
                "uniqueId": "adamjones73",
                "nickname": "Adam",
            },
            "stats": {
                "playCount": 5400000,
                "diggCount": 823500,
                "commentCount": 4301,
                "shareCount": 147900,
                "collectCount": 12000,
            },
            "video": {
                "cover": "https://cdn.example/cover.jpg",
                "playAddr": {"urlList": ["https://cdn.example/play.mp4"]},
                "duration": 12,
            },
        },
        rank=1,
    )
    assert row is not None
    assert row["caption"] == "#gta #viral"
    assert "title" not in row
    assert row["publishedAt"] == "2024-07-03T09:46:40.000Z"
    assert row["createTime"] == 1_720_000_000
    assert row["mediaType"] == "video"
    assert row["videoUrl"] == "https://cdn.example/play.mp4"
    assert row["saves"] == 12000
    assert row["isAd"] is False
    assert row["authorId"] == "123"
    assert row["secUid"] == "MS4wLjABAAAAtest"
    assert row["rank"] == 1


def test_map_trend_video_detects_photo_posts() -> None:
    row = _map_trend_video(
        {
            "id": "1",
            "desc": "carousel",
            "createTime": 1_720_000_000,
            "awemeType": 150,
            "imagePost": {"images": [{}]},
            "author": {"uniqueId": "photo_user", "nickname": "P"},
            "stats": {"playCount": 10, "diggCount": 1},
            "video": {"cover": "https://cdn.example/c.jpg"},
        },
        rank=3,
    )
    assert row is not None
    assert row["mediaType"] == "photo"
    assert "/photo/" in (row.get("url") or "")
