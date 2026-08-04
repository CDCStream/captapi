from __future__ import annotations

from app.services.tiktok_native import _collect_hashtags, _collect_mentions, _map_aweme_post
from app.routers.tiktok import _tt_hashtags, _tt_finalize_post


def test_hashtags_prefer_text_extra_over_caption_emoji() -> None:
    tags = _collect_hashtags(
        {
            "text_extra": [
                {"hashtag_name": "okaralover"},
                {"hashtag_name": "alichaiwala"},
                {"hashtag_name": "latinus"},
            ]
        },
        "Video #okaralover\U0001F4AA\U0001F4AA\u2764\ufe0f #alichaiwala\u2764\ufe0f\U0001F4AB #Latinus",
    )
    assert tags == ["okaralover", "alichaiwala", "latinus"]


def test_hashtags_casefold_structured_only() -> None:
    tags = _collect_hashtags(
        {
            "text_extra": [
                {"hashtag_name": "latinus"},
                {"hashtag_name": "informacionparati"},
            ]
        },
        "Video #Latinus #InformacionParaTi",
    )
    assert tags == ["latinus", "informacionparati"]


def test_hashtags_regex_fallback_strips_emoji() -> None:
    tags = _collect_hashtags({}, "#okaralover\U0001F4AA\U0001F4AA\u2764\ufe0f #comedy")
    assert tags == ["okaralover", "comedy"]


def test_tt_hashtags_casefold() -> None:
    tags = _tt_hashtags(
        {"hashtags": ["Latinus", "latinus"]},
        "#Latinus #NASA",
    )
    assert tags == ["latinus"]


def test_collect_mentions_from_text_extra() -> None:
    mentions = _collect_mentions(
        {
            "text_extra": [
                {"hashtag_name": "comedy"},
                {
                    "user_id": "123",
                    "sec_uid": "MS4wLjAB",
                    "user_unique_id": "kanwal",
                    "start": 10,
                    "end": 20,
                },
                {
                    "userId": "123",
                    "secUid": "MS4wLjAB",
                    "userUniqueId": "kanwal",
                },
            ]
        }
    )
    assert len(mentions) == 1
    assert mentions[0]["userId"] == "123"
    assert mentions[0]["secUid"] == "MS4wLjAB"
    assert mentions[0]["username"] == "kanwal"


def test_finalize_keeps_empty_hashtags_and_mentions() -> None:
    out = _tt_finalize_post({"id": "1", "caption": "hi", "hashtags": [], "mentions": []})
    assert out["hashtags"] == []
    assert out["mentions"] == []


def test_map_aweme_photo_carousel() -> None:
    row = _map_aweme_post(
        {
            "aweme_id": "99",
            "desc": "slides #NASA",
            "aweme_type": 150,
            "create_time": 1_720_000_000,
            "author": {"unique_id": "nasa", "nickname": "NASA", "uid": "1", "sec_uid": "MS4"},
            "statistics": {"play_count": 100, "digg_count": 10},
            "text_extra": [
                {"hashtag_name": "nasa"},
                {"user_id": "9", "sec_uid": "SEC", "user_unique_id": "esa"},
            ],
            "image_post_info": {
                "images": [
                    {"display_image": {"url_list": ["https://cdn.example/a.jpg"]}},
                    {"display_image": {"url_list": ["https://cdn.example/b.jpg"]}},
                ]
            },
            "video": {"cover": {"url_list": ["https://cdn.example/c.jpg"]}},
            "music": {"title": "original sound", "id": "123"},
        }
    )
    assert row is not None
    assert row["mediaType"] == "photo"
    assert row["contentType"] == "multi_photo"
    assert row["images"] == [
        "https://cdn.example/a.jpg",
        "https://cdn.example/b.jpg",
    ]
    assert "/photo/" in row["url"]
    assert row["hashtags"] == ["nasa"]
    assert row["mentions"][0]["username"] == "esa"
    assert row["isAd"] is False
    assert row["musicId"] == "123"


def test_map_aweme_video_has_content_type() -> None:
    row = _map_aweme_post(
        {
            "aweme_id": "1",
            "desc": "no tags here",
            "author": {"unique_id": "u"},
            "statistics": {"play_count": 1, "digg_count": 0},
            "video": {"duration": 12, "cover": {"url_list": ["https://cdn.example/c.jpg"]}},
        }
    )
    assert row is not None
    assert row["mediaType"] == "video"
    assert row["contentType"] == "video"
    assert row["hashtags"] == []
    assert row["mentions"] == []
    assert "images" not in row


def test_map_aweme_video_urls_and_no_description_dup() -> None:
    row = _map_aweme_post(
        {
            "aweme_id": "42",
            "desc": "hello #cat",
            "description": "should be dropped",
            "is_ad": False,
            "is_paid_partnership": True,
            "author": {
                "unique_id": "u",
                "uid": "9",
                "sec_uid": "SEC",
                "follower_count": 100,
            },
            "statistics": {
                "play_count": 10,
                "digg_count": 2,
                "download_count": 3,
                "repost_count": 1,
            },
            "video": {
                "duration": 12,
                "width": 1080,
                "height": 1920,
                "cover": {"url_list": ["https://cdn.example/c.jpg"]},
                "play_addr": {
                    "url_list": [
                        "https://v.example/play.mp4?x-expires=1893456000"
                    ]
                },
                "download_addr": {"url_list": ["https://v.example/dl.mp4"]},
                "download_no_watermark_addr": {
                    "url_list": ["https://v.example/nowm.mp4"]
                },
            },
            "shop_product_url": "https://www.tiktok.com/shop/pdp/1729494515984797858",
        }
    )
    assert row is not None
    assert row["videoUrl"] == "https://v.example/play.mp4?x-expires=1893456000"
    assert row["downloadUrl"] == "https://v.example/dl.mp4"
    assert row["downloadUrlNoWatermark"] == "https://v.example/nowm.mp4"
    assert row["hasWatermark"] is False
    assert row["mediaUrlsExpireAt"] == "2030-01-01T00:00:00.000Z"
    assert row["author"]["id"] == "9"
    assert row["author"]["secUid"] == "SEC"
    assert row["isPaidPartnership"] is True
    assert row["isAd"] is False
    assert row["engagement"]["downloads"] == 3
    assert row["engagement"]["reposts"] == 1
    assert "description" not in row
    assert row["shopProductUrl"] == "https://www.tiktok.com/shop/pdp/1729494515984797858"
