"""channel-posts overlay must map play counts per shortcode/pk - never zip."""

from __future__ import annotations

import asyncio
from typing import Any

from app.routers import instagram as ig
from app.services import instagram_decodo as decodo


def test_overlay_matches_by_pk_and_skips_image_views(monkeypatch) -> None:
    posts = [
        {
            "id": "AAA",
            "shortcode": "AAA",
            "mediaId": "111",
            "postType": "Video",
            "productType": None,
            "engagement": {"likes": 100, "comments": 1, "views": None},
            "mentions": [],
        },
        {
            "id": "BBB",
            "shortcode": "BBB",
            "mediaId": "222",
            "postType": "Image",
            "productType": None,
            "engagement": {"likes": 50, "comments": 0, "views": None},
            "mentions": [],
        },
        {
            "id": "CCC",
            "shortcode": "CCC",
            "mediaId": "333",
            "postType": "Video",
            "productType": "clips",
            "engagement": {"likes": 485_567, "comments": 2174, "views": None},
            "mentions": [],
        },
    ]

    feed_items = [
        {
            "code": "AAA",
            "pk": "111",
            "media_type": 2,
            "product_type": "clips",
            "play_count": 51_078,
            "ig_play_count": 40_862,
            "fb_play_count": 10_216,
            "like_count": 10_645,
            "comment_count": 149,
            "video_duration": 72.1,
            "has_audio": True,
            "is_paid_partnership": False,
        },
        {
            "code": "BBB",
            "pk": "222",
            "media_type": 1,
            "like_count": 50,
            "comment_count": 0,
        },
        {
            "code": "CCC",
            "pk": "333",
            "media_type": 2,
            "play_count": 13_000_000,
            "ig_play_count": 12_500_000,
            "like_count": 485_567,
            "comment_count": 2174,
        },
    ]

    async def fake_feed(user_id: str, max_id: str | None = None, count: int = 12):
        assert user_id == "99"
        return feed_items, None, False

    monkeypatch.setattr(ig.instagram_native, "fetch_user_feed_page", fake_feed)

    out = asyncio.run(ig._overlay_feed_engagement(posts, "99"))
    assert out[0]["engagement"]["views"] == 51_078
    assert out[0]["engagement"]["viewsSource"] == "instagram"
    assert out[0]["engagement"]["plays"] == 51_078
    assert "viewsInstagram" not in out[0]["engagement"]
    assert out[0]["productType"] == "clips"
    assert out[0]["durationSeconds"] == 72.1
    assert out[0]["hasAudio"] is True
    assert out[0]["isPaidPartnership"] is False
    assert out[1]["engagement"]["views"] is None
    assert "viewsInstagram" not in out[1]["engagement"]
    assert out[2]["engagement"]["views"] == 13_000_000
    assert out[2]["engagement"]["likes"] == 485_567


def test_overlay_matches_numeric_id_without_shortcode(monkeypatch) -> None:
    posts: list[dict[str, Any]] = [
        {
            "id": "999888",
            "postType": "Video",
            "productType": "clips",
            "engagement": {"likes": 10, "comments": 1, "views": None},
            "mentions": [],
        }
    ]

    async def fake_feed(user_id: str, max_id: str | None = None, count: int = 12):
        return (
            [
                {
                    "pk": "999888",
                    "media_type": 2,
                    "play_count": 42_000,
                    "ig_play_count": 40_000,
                    "like_count": 10,
                    "comment_count": 1,
                }
            ],
            None,
            False,
        )

    monkeypatch.setattr(ig.instagram_native, "fetch_user_feed_page", fake_feed)
    out = asyncio.run(ig._overlay_feed_engagement(posts, "1"))
    assert out[0]["engagement"]["views"] == 42_000


def test_graphql_undercount_never_becomes_views() -> None:
    eng = decodo.engagement_with_play_split(
        {"likes": 485_567, "comments": 2174},
        play_count=None,
        ig_play_count=None,
        video_view_count=112_487,
        likes=485_567,
        is_video=True,
    )
    assert eng["views"] is None