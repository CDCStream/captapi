from __future__ import annotations

from app.services.tiktok_native import _collect_hashtags, _map_aweme_post
from app.routers.tiktok import _tt_hashtags, _tt_finalize_post


def test_hashtags_casefold_structured_plus_caption() -> None:
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


def test_tt_hashtags_casefold() -> None:
    tags = _tt_hashtags(
        {"hashtags": ["Latinus", "latinus"]},
        "#Latinus #NASA",
    )
    assert tags == ["latinus", "nasa"]


def test_finalize_keeps_empty_hashtags() -> None:
    out = _tt_finalize_post({"id": "1", "caption": "hi", "hashtags": []})
    assert out["hashtags"] == []


def test_map_aweme_photo_carousel() -> None:
    row = _map_aweme_post(
        {
            "aweme_id": "99",
            "desc": "slides #NASA",
            "aweme_type": 150,
            "create_time": 1_720_000_000,
            "author": {"unique_id": "nasa", "nickname": "NASA", "uid": "1", "sec_uid": "MS4"},
            "statistics": {"play_count": 100, "digg_count": 10},
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
    assert "images" not in row