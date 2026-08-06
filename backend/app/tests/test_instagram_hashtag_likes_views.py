"""Hashtag GraphQL must not map play totals into engagement.likes."""

from __future__ import annotations

import asyncio
from typing import Any

from app.services import instagram_decodo as decodo
from app.services import instagram_native as native


def test_resolve_preview_like_is_views_not_likes_on_video() -> None:
    """Audit case: millions in edge_media_preview_like, no like_count."""
    likes, play_count, video_view_count = decodo.resolve_graphql_likes_and_plays(
        {
            "is_video": True,
            "edge_media_preview_like": {"count": 3_657_742},
            "edge_media_to_comment": {"count": 8609},
            "product_type": "clips",
        },
        is_video=True,
    )
    assert likes is None
    assert play_count == 3_657_742
    assert video_view_count == 3_657_742


def test_resolve_flattened_likes_trap_low_ratio() -> None:
    """143:1 view:comment still must not become likes (audit result #5)."""
    likes, play_count, _ = decodo.resolve_graphql_likes_and_plays(
        {
            "likes": 2_199_099,
            "comment_count": 15_403,
            "product_type": "clips",
        },
        is_video=True,
    )
    assert likes is None
    assert play_count == 2_199_099


def test_resolve_true_like_count_wins() -> None:
    likes, play_count, video_view_count = decodo.resolve_graphql_likes_and_plays(
        {
            "like_count": 12_345,
            "edge_media_preview_like": {"count": 3_000_000},
            "video_view_count": 3_000_000,
            "comment_count": 200,
        },
        is_video=True,
    )
    assert likes == 12_345
    # Preview matches video_view_count ? reclaim as play signal.
    assert play_count == 3_000_000
    assert video_view_count == 3_000_000


def test_resolve_image_still_uses_preview_as_likes() -> None:
    likes, play_count, _ = decodo.resolve_graphql_likes_and_plays(
        {"edge_media_preview_like": {"count": 420}, "comment_count": 8},
        is_video=False,
    )
    assert likes == 420
    assert play_count is None


def test_post_mapper_engagement_views_not_likes() -> None:
    post = decodo._post(
        {
            "shortcode": "ABC123",
            "is_video": True,
            "__typename": "GraphVideo",
            "product_type": "clips",
            "edge_media_preview_like": {"count": 17_998_863},
            "edge_media_to_comment": {"count": 15_192},
            "owner": {"username": "landon_paschall", "id": "1"},
            "edge_media_to_caption": {
                "edges": [{"node": {"text": "Those were the best times"}}]
            },
            "taken_at_timestamp": 1_700_000_000,
        }
    )
    eng = post["engagement"]
    assert "likes" not in eng or eng.get("likes") is None
    assert eng.get("views") == 17_998_863
    assert eng.get("comments") == 15_192


def test_enrich_overlays_feed_like_count(monkeypatch) -> None:
    posts: list[dict[str, Any]] = [
        {
            "id": "REELCODE",
            "url": "https://www.instagram.com/reel/REELCODE/",
            "postType": "Video",
            "productType": "clips",
            "author": {"username": "sugat_vlogs", "id": "42"},
            # GraphQL trap already cleared likes; views from preview reclaim.
            "engagement": {"views": 2_199_099, "comments": 15_403},
            "mentions": [],
        }
    ]

    async def fake_feed(user_id: str, max_id: str | None = None, count: int = 12):
        return (
            [
                {
                    "code": "REELCODE",
                    "play_count": 2_199_099,
                    "ig_play_count": 2_000_000,
                    "fb_play_count": 199_099,
                    "like_count": 18_420,
                    "comment_count": 15_403,
                    "media_type": 2,
                    "product_type": "clips",
                }
            ],
            None,
            False,
        )

    async def fake_profile_decodo(username: str):
        return None, True

    monkeypatch.setattr(native, "fetch_user_feed_page", fake_feed)
    monkeypatch.setattr(native, "fetch_web_profile_info_via_decodo", fake_profile_decodo)

    out = asyncio.run(native.enrich_posts_from_author_feeds(posts))
    eng = out[0]["engagement"]
    assert eng["likes"] == 18_420
    assert eng["views"] == 2_199_099
    assert eng["viewsSource"] == "instagram"
    assert "plays" not in eng
    assert "viewsInstagram" not in eng
