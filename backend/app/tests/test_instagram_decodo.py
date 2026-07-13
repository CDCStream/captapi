from __future__ import annotations

import asyncio

from app.services import instagram_decodo as decodo


PROFILE = {
    "data": {
        "user": {
            "id": "42",
            "username": "captapi",
            "full_name": "Captapi",
            "biography": "Public data API",
            "is_verified": True,
            "is_private": False,
            "profile_pic_url": "https://cdn.example/avatar.jpg",
            "external_url": "https://captapi.com",
            "edge_followed_by": {"count": 1234},
            "edge_follow": {"count": 25},
            "edge_owner_to_timeline_media": {
                "count": 2,
                "edges": [
                    {
                        "node": {
                            "id": "p1",
                            "shortcode": "ABC",
                            "__typename": "GraphImage",
                            "is_video": False,
                            "display_url": "https://cdn.example/image.jpg",
                            "taken_at_timestamp": 1_700_000_000,
                            "edge_media_preview_like": {"count": 12},
                            "edge_media_to_comment": {"count": 3},
                            "edge_media_to_caption": {
                                "edges": [{"node": {"text": "hello"}}]
                            },
                            "owner": {"username": "captapi"},
                        }
                    },
                    {
                        "node": {
                            "id": "r1",
                            "shortcode": "REEL",
                            "__typename": "GraphVideo",
                            "is_video": True,
                            "display_url": "https://cdn.example/reel.jpg",
                            "video_url": "https://cdn.example/reel.mp4",
                            "owner": {"username": "captapi"},
                        }
                    },
                ],
            },
        }
    }
}


def test_post_mapper_preserves_public_contract() -> None:
    node = PROFILE["data"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]
    post = decodo._post(node)

    assert post["platform"] == "instagram"
    assert post["id"] == "p1"
    assert post["caption"] == "hello"
    assert post["postType"] == "Image"
    assert post["author"]["username"] == "captapi"
    # Image posts carry no video-only fields, and null engagement counts are
    # dropped rather than returned as null.
    assert post["engagement"] == {"likes": 12, "comments": 3}
    assert "videoUrl" not in post


def test_profile_and_timeline_functions(monkeypatch) -> None:
    async def fake_scrape(target: str, params: dict):
        assert target == "instagram_graphql_profile"
        assert params["query"] == "captapi"
        return PROFILE

    monkeypatch.setattr(decodo, "_scrape", fake_scrape)

    details = asyncio.run(decodo.channel_details("captapi"))
    posts = asyncio.run(decodo.channel_posts("captapi", 10))
    reels = asyncio.run(decodo.channel_reels("captapi", 10))

    assert details and details["followers"] == 1234
    assert details["postCount"] == 2
    # channel_posts returns a page envelope covering every post type; reels
    # keeps only videos.
    assert posts and [post["id"] for post in posts["items"]] == ["p1", "r1"]
    assert posts["userId"] == "42"
    assert reels and [reel["id"] for reel in reels["items"]] == ["r1"]


def test_hashtag_deduplicates_top_and_recent(monkeypatch) -> None:
    node = PROFILE["data"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]
    response = {
        "hashtag": {
            "edge_hashtag_to_top_posts": {"edges": [{"node": node}]},
            "edge_hashtag_to_media": {"edges": [{"node": node}]},
        }
    }

    async def fake_scrape(target: str, params: dict):
        return response

    monkeypatch.setattr(decodo, "_scrape", fake_scrape)
    posts = asyncio.run(decodo.hashtag_medias("api", 20))

    assert posts and len(posts) == 1
