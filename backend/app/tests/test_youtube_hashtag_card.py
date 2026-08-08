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
            "viewCount": 1_200_000,
            "viewCountIsApproximate": True,
        }
    )
    assert card["type"] == "short"
    assert card["id"] == "hwf0tDWlP7Q"
    assert "channelId" not in card
    assert "channelName" not in card
    assert card["channel"]["id"] == "UCabc"
    assert card["channel"]["title"] == "Ch"
    assert card["channel"]["url"] == "https://www.youtube.com/channel/UCabc"
    assert card["viewCount"] == 1_200_000
    assert card["viewCountIsApproximate"] is True


def test_yt_hashtag_card_exact_views_flag_false() -> None:
    card = _yt_hashtag_result_card(
        {
            "type": "video",
            "id": "3iAiWIytqdw",
            "url": "https://www.youtube.com/watch?v=3iAiWIytqdw",
            "title": "Forever Young",
            "durationSeconds": 265,
            "viewCount": 42,
            "channel": {"id": "UCx", "title": "Name"},
        }
    )
    assert card["type"] == "video"
    assert card["channel"]["id"] == "UCx"
    assert "channelId" not in card
    assert card["viewCountIsApproximate"] is False


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
