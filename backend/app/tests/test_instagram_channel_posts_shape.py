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
        "description": "a",
        "publishedAt": "2026-08-01T00:00:00Z",
        "durationSeconds": 12.5,
        "thumbnailUrl": "https://cdn.example/a.jpg",
        "videoUrl": "https://cdn.example/a.mp4",
        "hasAudio": True,
        "author": {
            "id": "1",
            "username": "golfzonleadbettereducation",
            "url": "https://www.instagram.com/golfzonleadbettereducation/",
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
        "location": {
            "id": "loc1",
            "name": "Course",
            "slug": "course",
            "hasPublicPage": True,
        },
    }
    feedish = {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/Da5-Oe-vSE_/",
        "id": "3943456622960779583",
        "shortcode": "Da5-Oe-vSE_",
        "postType": "Video",
        "productType": "clips",
        "caption": "b",
        "description": "b",
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
        "location": {
            "id": "loc2",
            "name": "Range",
            "latitude": 1.0,
            "longitude": 2.0,
        },
    }
    posts = decodo.finalise_channel_posts([graphqlish, feedish])
    keysets = {tuple(sorted(p.keys())) for p in posts}
    assert len(keysets) == 1
    assert set(posts[0].keys()) == set(decodo.IG_CHANNEL_POST_KEYS)

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
    loc_sets = {
        tuple(sorted(p["location"].keys()))
        for p in posts
        if isinstance(p.get("location"), dict)
    }
    assert loc_sets == {tuple(sorted(decodo.IG_LOCATION_KEYS))}
    assert posts[0]["location"]["latitude"] is None
    assert posts[1]["location"]["slug"] is None


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