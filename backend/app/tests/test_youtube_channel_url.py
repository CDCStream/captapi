from __future__ import annotations

from app.services.youtube_native import _finalize_short_list_card
from app.utils.media_urls import (
    canonicalize_youtube_channel_url,
    channel_handle_from_profile_url,
    decode_youtube_handle,
)


def test_decode_percent_encoded_handle() -> None:
    raw = "@%D0%9B%D0%B5%D0%B3%D0%B5%D0%BD%D0%B4%D0%B0%D1%80%D0%BD%D1%8B%D0%B5%D0%BC%D0%BE%D0%BC%D0%B5%D0%BD%D1%82%D1%8B%D0%B3%D0%BE%D0%BB%D0%BE%D1%81%D0%B0"
    assert decode_youtube_handle(raw) == "@Легендарныемоментыголоса"
    assert channel_handle_from_profile_url(
        f"http://www.youtube.com/{raw}"
    ) == "@Легендарныемоментыголоса"


def test_canonicalize_forces_https_and_at_handle() -> None:
    assert (
        canonicalize_youtube_channel_url("http://www.youtube.com/@trueheartx")
        == "https://www.youtube.com/@trueheartx"
    )
    assert (
        canonicalize_youtube_channel_url(
            "http://www.youtube.com/channel/UCjyw08840PE8WPrGgA0bUmw",
            channel_id="UCjyw08840PE8WPrGgA0bUmw",
            handle=None,
        )
        == "https://www.youtube.com/channel/UCjyw08840PE8WPrGgA0bUmw"
    )
    assert (
        canonicalize_youtube_channel_url(
            None,
            channel_id="UCabc",
            handle="@TrueHeartX",
        )
        == "https://www.youtube.com/@TrueHeartX"
    )


def test_finalize_short_list_card_canonical_shape() -> None:
    card = _finalize_short_list_card(
        "uXLx0qnL7Ps",
        {
            "title": "DONT CHECK THE SOUND",
            "viewCount": 112098870,
            "viewCountIsApproximate": False,
            "durationSeconds": 32,
            "commentCount": 11000,
            "commentCountIsApproximate": True,
            "channelId": "UCjyw08840PE8WPrGgA0bUmw",
            "channelName": "Top Ranks King",
            "channelHandle": None,
            "channelUrl": "https://www.youtube.com/channel/UCjyw08840PE8WPrGgA0bUmw",
            "thumbnailUrl": "https://i.ytimg.com/vi/uXLx0qnL7Ps/sd2.jpg",
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/uXLx0qnL7Ps/sd2.jpg",
                    "width": 640,
                    "height": 480,
                }
            ],
            "publishedAt": "2024-01-01T00:00:00Z",
            "genre": "Entertainment",
        },
    )
    assert "channelId" not in card
    assert "channelUrl" not in card
    assert "viewCountInt" not in card
    assert "commentCountInt" not in card
    assert "durationMs" not in card
    assert "badges" not in card
    assert card["channel"]["url"].startswith("https://")
    assert "thumbnail" not in card["channel"]
    assert card["viewCountIsApproximate"] is False
    assert card["commentCountIsApproximate"] is True
    assert "oardefault" in card["thumbnailUrl"] or "maxresdefault" in card["thumbnailUrl"]
