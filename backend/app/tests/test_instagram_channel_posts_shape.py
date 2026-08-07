"""Uniform key-set + id contract for Instagram channel-posts list items."""

from __future__ import annotations

import json
from pathlib import Path

from app.services import instagram_decodo as decodo
from app.services import instagram_native as native

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "shelved_keysets"


def _load_keys(name: str) -> list[str]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_channel_post_baseline_matches_constant() -> None:
    baseline = _load_keys("instagram-channel-post.keys.json")
    assert list(decodo.IG_CHANNEL_POST_KEYS) == baseline
    assert list(decodo.IG_AUTHOR_KEYS) == _load_keys("instagram-channel-author.keys.json")


def test_finalise_unifies_graphql_and_feed_shapes() -> None:
    """Reproduce the customer bug: GraphQL row + feed row in one array."""
    graphqlish = {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/Dbsv8poug94/",
        "id": "Dbsv8poug94",
        "shortcode": "Dbsv8poug94",
        "mediaId": "3957749048613146488",
        "postType": "Video",
        "productType": "clips",
        "caption": "a",
        "publishedAt": "2026-08-01T00:00:00Z",
        "durationSeconds": 12.5,
        "thumbnailUrl": "https://cdn.example/a.jpg",
        "videoUrl": "https://cdn.example/a.mp4",
        "hasAudio": True,
        "mediaCount": 1,
        "children": [],
        "author": {
            "id": "1",
            "username": "golfzonleadbettereducation",
            "url": "https://instagram.com/golfzonleadbettereducation",
        },
        "engagement": {"likes": 10, "comments": 1, "views": 100, "viewsSource": "instagram"},
        "hashtags": [],
        "mentions": [],
        "isPaidPartnership": False,
        "isAd": False,
        "isAffiliate": False,
        "likeAndViewCountsDisabled": False,
        "commentsDisabled": False,
        "music": {"id": "m1", "title": "Song", "artist": "Artist"},
        "musicId": "m1",
    }
    feedish = {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/Da5-Oe-vSE_/",
        "id": "3943456622960779583",
        "shortcode": "Da5-Oe-vSE_",
        "postType": "Video",
        "productType": "clips",
        "caption": "b",
        "publishedAt": "2026-07-01T00:00:00Z",
        "durationSeconds": 8.0,
        "thumbnailUrl": "https://cdn.example/b.jpg",
        "videoUrl": "https://cdn.example/b.mp4",
        "author": {
            "id": "2",
            "username": "kerrodgraygolf",
            "displayName": "Kerrod",
            "url": "https://www.instagram.com/kerrodgraygolf/",
            "verified": False,
            "avatar": "https://cdn.example/p.jpg",
            "followers": 1000,
            "isPrivate": False,
        },
        "engagement": {"likes": 5, "comments": 0, "views": 50, "viewsSource": "instagram"},
        "hashtags": ["golf"],
        "mentions": [],
        "isPaidPartnership": False,
        "isAd": False,
        "isAffiliate": False,
        "music": {
            "id": "c1",
            "title": "Original",
            "artist": "kerrodgraygolf",
            "assetId": "a1",
            "coverUrl": "https://cdn.example/c.jpg",
            "audioType": "original",
            "clusterId": "c1",
            "hasLyrics": False,
            "durationMs": 15000,
            "isExplicit": False,
            "canonicalId": "can1",
            "isTrendingInClips": False,
        },
        "musicId": "c1",
    }
    posts = decodo.finalise_channel_posts([graphqlish, feedish])
    keysets = {tuple(sorted(p.keys())) for p in posts}
    assert len(keysets) == 1
    assert set(posts[0].keys()) == set(decodo.IG_CHANNEL_POST_KEYS)
    assert "description" not in posts[0]
    assert "location" not in posts[0]
    assert posts[0]["mediaCount"] == 1
    assert posts[0]["children"] == []
    assert posts[0]["author"]["url"] == "https://www.instagram.com/golfzonleadbettereducation/"

    assert posts[0]["id"] == "Dbsv8poug94"
    assert posts[1]["id"] == "Da5-Oe-vSE_"
    assert not posts[0]["id"].isdigit()
    assert not posts[1]["id"].isdigit()
    assert posts[0]["mediaId"] == "3957749048613146488"
    assert posts[1]["mediaId"] == "3943456622960779583"

    author_sets = {tuple(sorted(p["author"].keys())) for p in posts}
    assert author_sets == {tuple(sorted(decodo.IG_AUTHOR_KEYS))}
    assert posts[0]["author"]["postCount"] is None
    assert posts[0]["author"]["displayName"] is None

    music_sets = {
        tuple(sorted(p["music"].keys())) for p in posts if isinstance(p.get("music"), dict)
    }
    assert music_sets == {tuple(sorted(decodo.IG_MUSIC_KEYS))}


def test_finalise_parses_shortcode_from_reel_url() -> None:
    out = decodo.finalise_channel_post(
        {
            "id": "3943456622960779583",
            "url": "https://www.instagram.com/reel/Da5-Oe-vSE_/",
            "postType": "Video",
            "engagement": {"likes": 1, "comments": 0, "views": 9},
        }
    )
    assert out["id"] == "Da5-Oe-vSE_"
    assert out["shortcode"] == "Da5-Oe-vSE_"
    assert out["mediaId"] == "3943456622960779583"


def test_map_feed_post_emits_shortcode_id_and_media_id() -> None:
    mapped = native.map_feed_post(
        {
            "pk": "3943456622960779583",
            "code": "Da5-Oe-vSE_",
            "media_type": 2,
            "product_type": "clips",
            "taken_at": 1700000000,
            "like_count": 5,
            "comment_count": 1,
            "play_count": 50,
            "caption": {"text": "hello #golf"},
            "user": {"pk": "2", "username": "kerrodgraygolf", "is_private": False},
            "image_versions2": {"candidates": [{"url": "https://cdn.example/t.jpg"}]},
            "video_versions": [{"url": "https://cdn.example/v.mp4"}],
            "comments_disabled": False,
            "like_and_view_counts_disabled": False,
        },
        followers=1000,
        profile_user_id="2",
    )
    assert mapped["id"] == "Da5-Oe-vSE_"
    assert mapped["shortcode"] == "Da5-Oe-vSE_"
    assert mapped["mediaId"] == "3943456622960779583"
    final = decodo.finalise_channel_post(mapped)
    assert final["id"] == "Da5-Oe-vSE_"
    assert final["mediaId"] == "3943456622960779583"
    assert "commentsDisabled" in final
    assert "likeAndViewCountsDisabled" in final


def test_channel_user_uses_is_private_not_private() -> None:
    user = decodo._channel_user_summary(
        {
            "id": "9",
            "username": "kerrodgraygolf",
            "full_name": "Kerrod",
            "is_verified": False,
            "is_private": False,
            "edge_followed_by": {"count": 10},
            "edge_owner_to_timeline_media": {"count": 20},
        }
    )
    assert "private" not in user
    assert user["isPrivate"] is False
    assert set(user.keys()) == set(decodo.IG_CHANNEL_USER_KEYS)
    assert user["url"] == "https://www.instagram.com/kerrodgraygolf/"


def test_timeout_serves_stale_cache_when_present() -> None:
    """apify-timeout with a prior cache hit → labelled stale posts, not []."""
    import asyncio
    from unittest.mock import AsyncMock, patch

    from app.routers import instagram as ig
    from app.services.cache import make_cache_key

    stale_payload = {
        "url": "https://www.instagram.com/natgeo/",
        "totalReturned": 2,
        "posts": [
            {
                "id": "a",
                "shortcode": "a",
                "postType": "Image",
                "productType": "feed",
                "caption": "stale",
                "thumbnailUrl": "https://cdn.example/a.jpg",
                "engagement": {"likes": 1, "comments": 0, "views": None},
            }
        ],
        "nextCursor": None,
        "hasMore": False,
        "fetchedAt": "2026-08-06T14:22:10.118Z",
    }
    key = make_cache_key(
        "instagram.channel-posts",
        {"url": "natgeo", "limit": 20, "cursor": "", "v": 23},
    )

    async def _fake_get(k: str):
        if k == key:
            return stale_payload
        return None

    async def _run() -> None:
        # Minimal recreation of _timeout_result wiring via public finalise + peek.
        with patch("app.routers.instagram.cache_get", new=AsyncMock(side_effect=_fake_get)):
            hit = await ig.cache_get(key)
        assert hit is not None
        out = ig._finalise_channel_list_payload(
            {**hit, "cachedAt": hit["fetchedAt"]},
            degraded=True,
            degraded_reason="apify-timeout-served-stale",
        )
        assert out["degraded"] is True
        assert out["degradedReason"] == "apify-timeout-served-stale"
        assert out["cachedAt"] == "2026-08-06T14:22:10.118Z"
        assert len(out["posts"]) == 1

    asyncio.run(_run())


def test_finalise_payload_emits_uniform_envelope() -> None:
    from app.routers import instagram as ig

    healthy = ig._finalise_channel_list_payload(
        {"url": "https://www.instagram.com/nasa/", "posts": [], "totalReturned": 0},
        degraded=False,
    )
    assert healthy["degraded"] is False
    assert healthy["degradedReason"] is None
    assert healthy["user"] is None
    assert healthy["userId"] is None

    degraded = ig._finalise_channel_list_payload(
        {"url": "https://www.instagram.com/nasa/", "posts": [], "totalReturned": 0},
        degraded=True,
        degraded_reason="apify-fallback",
    )
    assert degraded["degraded"] is True
    assert degraded["degradedReason"] == "apify-fallback"
    assert degraded["user"] is None
    assert degraded["userId"] is None

    timed_out = ig._finalise_channel_list_payload(
        {"url": "https://www.instagram.com/nasa/", "posts": [], "totalReturned": 0},
        degraded=True,
        degraded_reason="apify-timeout",
    )
    assert timed_out["degradedReason"] == "apify-timeout"


def test_overlay_copies_accessibility_caption_from_feed() -> None:
    """GraphQL omits alt-text; feed overlay must backfill it (CP4)."""
    import asyncio
    from unittest.mock import AsyncMock, patch

    from app.routers import instagram as ig

    posts = [
        {
            "id": "DbbY9pdm6Q2",
            "shortcode": "DbbY9pdm6Q2",
            "postType": "Sidecar",
            "productType": "carousel_container",
            "caption": "x",
            "engagement": {"likes": 1, "comments": 0, "views": None},
            "children": [],
        }
    ]
    feed_row = {
        "code": "DbbY9pdm6Q2",
        "pk": "1",
        "media_type": 8,
        "product_type": "carousel_container",
        "accessibility_caption": (
            "Person in striped rugby shirt and fur hat sitting on grass at night."
        ),
        "like_count": 10,
        "comment_count": 2,
        "carousel_media": [],
    }

    async def _run() -> None:
        with patch.object(
            ig.instagram_native,
            "fetch_user_feed_page",
            new=AsyncMock(return_value=([feed_row], None, False)),
        ):
            out = await ig._overlay_feed_engagement(posts, "25025320")
        assert out[0]["accessibilityCaption"] == (
            "Person in striped rugby shirt and fur hat sitting on grass at night."
        )

    asyncio.run(_run())


def test_accessibility_caption_preserved_when_present() -> None:
    out = decodo.finalise_channel_post(
        {
            "id": "Acc1",
            "shortcode": "Acc1",
            "postType": "Image",
            "productType": "feed",
            "caption": "x",
            "thumbnailUrl": "https://cdn.example/a.jpg",
            "accessibilityCaption": "Person in striped rugby shirt and fur hat sitting on grass at night.",
            "engagement": {"likes": 1, "comments": 0, "views": None},
        }
    )
    assert out["accessibilityCaption"] == (
        "Person in striped rugby shirt and fur hat sitting on grass at night."
    )


def test_sidecar_without_children_media_count_is_null() -> None:
    """Unexpanded Sidecar must not fabricate mediaCount: 1 (looks complete)."""
    out = decodo.finalise_channel_post(
        {
            "id": "Side1",
            "shortcode": "Side1",
            "mediaId": "9",
            "postType": "Sidecar",
            "productType": "carousel_container",
            "caption": "album",
            "thumbnailUrl": "https://cdn.example/cover.jpg",
            "children": [],
            "engagement": {"likes": 1, "comments": 0, "views": None},
        }
    )
    assert out["postType"] == "Sidecar"
    assert out["children"] == []
    assert out["mediaCount"] is None


def test_apify_normalize_sidecar_without_slides_null_count() -> None:
    from app.routers import instagram as ig

    mapped = ig._normalize_post(
        {
            "type": "Sidecar",
            "shortCode": "ApifySide",
            "id": "99",
            "caption": "x",
            "displayUrl": "https://cdn.example/c.jpg",
            "ownerUsername": "nasa",
        }
    )
    final = decodo.finalise_channel_post(mapped)
    assert final["postType"] == "Sidecar"
    assert final["children"] == []
    assert final["mediaCount"] is None
    assert "description" not in final


def test_map_feed_post_emits_carousel_children() -> None:
    mapped = native.map_feed_post(
        {
            "pk": "111",
            "code": "CarouselABC",
            "media_type": 8,
            "product_type": "carousel_container",
            "taken_at": 1700000000,
            "like_count": 2,
            "comment_count": 0,
            "caption": {"text": "album"},
            "user": {"pk": "9", "username": "nasa"},
            "image_versions2": {"candidates": [{"url": "https://cdn.example/cover.jpg"}]},
            "carousel_media": [
                {
                    "pk": "201",
                    "media_type": 1,
                    "image_versions2": {"candidates": [{"url": "https://cdn.example/1.jpg"}]},
                },
                {
                    "pk": "202",
                    "media_type": 2,
                    "image_versions2": {"candidates": [{"url": "https://cdn.example/2.jpg"}]},
                    "video_versions": [{"url": "https://cdn.example/2.mp4"}],
                },
            ],
        }
    )
    assert mapped["postType"] == "Sidecar"
    assert mapped["mediaCount"] == 2
    assert len(mapped["children"]) == 2
    assert mapped["children"][0]["mediaType"] == "image"
    assert mapped["children"][0]["thumbnailUrl"] == "https://cdn.example/1.jpg"
    assert mapped["children"][0]["videoUrl"] is None
    assert mapped["children"][1]["mediaType"] == "video"
    assert mapped["children"][1]["videoUrl"] == "https://cdn.example/2.mp4"
    final = decodo.finalise_channel_post(mapped)
    assert final["mediaCount"] == 2
    assert len(final["children"]) == 2
    assert "description" not in final


def test_image_omits_views_source() -> None:
    out = decodo.finalise_channel_post(
        {
            "id": "AbC",
            "shortcode": "AbC",
            "mediaId": "1",
            "postType": "Image",
            "engagement": {"likes": 1, "comments": 0, "views": None},
        }
    )
    assert "viewsSource" not in out["engagement"]
    assert out["engagement"]["views"] is None


def test_finalise_channel_reel_drops_tautologies_and_dead_fields() -> None:
    out = decodo.finalise_channel_reel(
        {
            "id": "DbW4UlRF4mc",
            "shortcode": "DbW4UlRF4mc",
            "mediaId": "3951593428073548188",
            "postType": "Video",
            "productType": "clips",
            "caption": "hello",
            "description": "hello",
            "videoUrl": "https://cdn.example/a.mp4",
            "thumbnailUrl": "https://cdn.example/a.jpg",
            "author": {
                "id": "173560420",
                "username": "cristiano",
                "postCount": None,
            },
            "engagement": {"likes": 1, "comments": 0, "views": 10, "viewsSource": "instagram"},
            "accessibilityCaption": None,
            "commentsDisabled": None,
            "location": None,
            "music": {
                "id": "m1",
                "title": "x",
                "trendRank": None,
                "previousTrendRank": None,
            },
        }
    )
    assert set(out.keys()) == set(decodo.IG_CHANNEL_REEL_KEYS)
    assert "description" not in out
    assert "postType" not in out
    assert "productType" not in out
    assert "accessibilityCaption" not in out
    assert "commentsDisabled" not in out
    assert out["caption"] == "hello"
    assert "postCount" not in out["author"]
    assert "trendRank" not in out["music"]
    assert "previousTrendRank" not in out["music"]
    assert "location" not in out
    assert "children" not in out
    assert "mediaCount" not in out