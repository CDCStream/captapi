#"""Channel / trending Shorts card mapping (SC-parity fields)."""

from __future__ import annotations

from app.services.youtube_native import (
    _normalize_reel_item,
    _normalize_shorts_lockup,
    encode_reel_sequence_params,
    format_count_text,
    format_duration_hms,
    thumbnail_url_for_video_id,
)


def test_thumbnail_url_for_video_id():
    assert thumbnail_url_for_video_id("Df5Y-2ndQyU") == (
        "https://i.ytimg.com/vi/Df5Y-2ndQyU/maxresdefault.jpg"
    )
    assert thumbnail_url_for_video_id("bad") is None


def test_format_helpers():
    assert format_count_text(17066) == "17,066"
    assert format_duration_hms(37) == "00:00:37"
    assert format_duration_hms(75) == "00:01:15"


def test_normalize_shorts_lockup_uses_thumbnail_view_model_and_id_fallback():
    lk = {
        "entityId": "shorts-shelf-item-Df5Y-2ndQyU",
        "onTap": {
            "innertubeCommand": {
                "reelWatchEndpoint": {"videoId": "Df5Y-2ndQyU"},
            }
        },
        "overlayMetadata": {
            "primaryText": {"content": "Read My Book"},
            "secondaryText": {"content": "17K views"},
        },
        "thumbnailViewModel": {
            "thumbnailViewModel": {
                "image": {
                    "sources": [
                        {"url": "https://i.ytimg.com/vi/Df5Y-2ndQyU/sardefault.jpg", "width": 405},
                        {"url": "https://i.ytimg.com/vi/Df5Y-2ndQyU/oar2.jpg", "width": 720},
                    ]
                }
            }
        },
    }
    card = _normalize_shorts_lockup(lk)
    assert card is not None
    assert card["id"] == "Df5Y-2ndQyU"
    assert card["thumbnailUrl"]
    assert "Df5Y-2ndQyU" in card["thumbnailUrl"]
    assert card["viewCount"] == 17000
    assert card.get("viewCountIsApproximate") is True
    assert "viewCountInt" not in card
    assert "viewCountApproximate" not in card


def test_normalize_shorts_lockup_id_fallback_when_no_thumb_tree():
    lk = {
        "onTap": {
            "innertubeCommand": {
                "reelWatchEndpoint": {"videoId": "AAAAAAAAAAA"},
            }
        },
        "overlayMetadata": {
            "primaryText": {"content": "Hello"},
            "secondaryText": {"content": "1,234 views"},
        },
    }
    card = _normalize_shorts_lockup(lk)

    assert card is not None
    assert card["thumbnailUrl"] == thumbnail_url_for_video_id("AAAAAAAAAAA")
    assert card["viewCount"] == 1234
    assert card.get("viewCountIsApproximate") is False


def test_normalize_reel_item_thumb_fallback():
    card = _normalize_reel_item(
        {
            "videoId": "BBBBBBBBBBB",
            "headline": {"simpleText": "Legacy"},
            "viewCountText": {"simpleText": "9.8M views"},
        }
    )
    assert card is not None
    assert card["thumbnailUrl"] == thumbnail_url_for_video_id("BBBBBBBBBBB")
    assert card["viewCount"] == 9_800_000


def test_encode_reel_sequence_params_stable():
    token = encode_reel_sequence_params("f7y2XikE7sY")
    assert token.startswith("Cgt")
    assert len(token) > 10
