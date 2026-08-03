from __future__ import annotations

from app.routers.youtube import _yt_hashtag_result_card


def test_yt_hashtag_card_type_from_shorts_url() -> None:
    card = _yt_hashtag_result_card(
        {
            "id": "hwf0tDWlP7Q",
            "url": "https://www.youtube.com/shorts/hwf0tDWlP7Q",
            "title": "x",
            "durationSeconds": 19,
            "channelId": "UCabc",
            "channelName": "Ch",
        }
    )
    assert card["type"] == "short"
    assert card["id"] == "hwf0tDWlP7Q"
    assert card["channelId"] == "UCabc"


def test_yt_hashtag_card_type_watch() -> None:
    card = _yt_hashtag_result_card(
        {
            "type": "video",
            "id": "3iAiWIytqdw",
            "url": "https://www.youtube.com/watch?v=3iAiWIytqdw",
            "title": "Forever Young",
            "durationSeconds": 265,
        }
    )
    assert card["type"] == "video"