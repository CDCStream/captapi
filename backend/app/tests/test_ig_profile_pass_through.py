from __future__ import annotations

from typing import Any

from app.services.instagram_native import (
    map_basic_profile,
    map_channel_details,
    map_post_from_media,
    map_profile_search_user,
)


def _user() -> dict:
    return {
        "id": "123",
        "username": "austinbbq",
        "full_name": "Austin BBQ",
        "biography": "Smoked meats",
        "is_verified": False,
        "is_private": False,
        "is_business_account": True,
        "category_name": "Entrepreneur",
        "fbid": "17841402777077586",
        "like_and_view_counts_disabled": True,
        "profile_pic_url": "https://example.com/a.jpg",
        "edge_followed_by": {"count": 1000},
        "edge_follow": {"count": 50},
        "edge_owner_to_timeline_media": {"count": 10},
        "business_address_json": {
            "city_name": "Austin, Texas",
            "city_id": 106224666074625,
            "latitude": 30.26759,
            "longitude": -97.74299,
            "street_address": None,
            "zip_code": None,
        },
        "edge_related_profiles": {
            "edges": [
                {
                    "node": {
                        "id": "9",
                        "username": "itsallykrinsky",
                        "full_name": "Ally",
                        "is_verified": True,
                        "profile_pic_url": "https://example.com/b.jpg",
                    }
                }
            ]
        },
    }


def test_basic_profile_pass_through_fields() -> None:
    out = map_basic_profile(_user())
    assert out["categoryName"] == "Entrepreneur"
    assert out["fbid"] == "17841402777077586"
    assert out["likeAndViewCountsDisabled"] is True
    assert out["businessAddress"]["cityName"] == "Austin, Texas"
    assert out["businessAddress"]["latitude"] == 30.26759
    assert out["relatedProfiles"][0]["username"] == "itsallykrinsky"
    assert out["relatedProfiles"][0]["verified"] is True


def test_channel_details_and_profile_search_parity() -> None:
    u = _user()
    ch = map_channel_details(u)
    assert ch["categoryName"] == "Entrepreneur"
    assert ch["fbid"] == "17841402777077586"
    assert ch["relatedProfiles"][0]["username"] == "itsallykrinsky"
    assert ch["likeAndViewCountsDisabled"] is True
    assert ch["url"] == "https://www.instagram.com/austinbbq/"
    assert ch["handle"] == "austinbbq"
    assert ch["avatar"]
    # Twin aliases dropped on channel-details (canonical handle/displayName/avatar).
    assert "profileImage" not in ch
    assert "username" not in ch
    assert "name" not in ch
    assert "private" not in ch
    assert ch["isPrivate"] is False
    assert ch["postCountIsApproximate"] is False
    assert ch["followersIsApproximate"] is False
    ps = map_profile_search_user(u)
    assert ps["platform"] == "instagram"
    assert ps["categoryName"] == "Entrepreneur"
    assert ps["fbid"] == "17841402777077586"
    assert ps["relatedProfiles"][0]["id"] == "9"
    assert ps["url"] == "https://www.instagram.com/austinbbq/"
    assert ps["handle"] == "austinbbq"
    assert ps["avatar"] == ps["profileImage"]
    assert "private" not in ps
    assert ps["isPrivate"] is False
    assert ch["url"] == ps["url"]


def test_channel_details_post_count_approx_from_og_compact() -> None:
    """og ``32K`` → postCount 32000 with postCountIsApproximate true."""
    from app.services.instagram_native import parse_profile_from_html

    # No media_count in JSON → fall back to og "32K". Exact follower_count stays.
    html = (
        '<meta property="og:description" content="1,234 Followers, 56 Following, 32K Posts" />'
        '{"username":"natgeo","full_name":"National Geographic","biography":"bio",'
        '"follower_count":1234,"following_count":56,"pk":"787132","id":"787132"}'
    )
    user = parse_profile_from_html(html, "natgeo")
    assert user is not None
    assert user.get("media_count") == 32000
    assert user.get("media_count_is_approximate") is True
    assert user.get("follower_count") == 1234
    assert not user.get("follower_count_is_approximate")
    out = map_channel_details(user, handle="natgeo")
    assert out["postCount"] == 32000
    assert out["postCountIsApproximate"] is True
    assert out["followersIsApproximate"] is False


def test_channel_details_exact_post_count_not_approximate() -> None:
    u = _user()
    u["edge_owner_to_timeline_media"] = {"count": 32847}
    out = map_channel_details(u)
    assert out["postCount"] == 32847
    assert out["postCountIsApproximate"] is False


def test_channel_details_no_duplicate_non_boolean_values() -> None:
    out = map_channel_details(_user())
    bool_keys = {
        "verified",
        "isPrivate",
        "isBusinessAccount",
        "isProfessionalAccount",
        "likeAndViewCountsDisabled",
        "followersIsApproximate",
        "followingIsApproximate",
        "postCountIsApproximate",
    }
    non_bool = {
        k: v
        for k, v in out.items()
        if k not in bool_keys and not isinstance(v, (bool, dict, list))
    }
    # Values that coincide by chance across different concepts are rare; the
    # twin-alias pairs are the regression we care about.
    for a, b in (("handle", "username"), ("displayName", "name"), ("avatar", "profileImage")):
        assert not (a in out and b in out and out.get(a) == out.get(b))
    seen: dict[Any, str] = {}
    for k, v in non_bool.items():
        if v in (None, "", 0):
            continue
        if v in seen:
            # Same URL appearing as url vs something else is fine; only flag
            # identical string/int pairs that look like alias twins.
            if {seen[v], k} <= {"handle", "username", "displayName", "name", "avatar", "profileImage"}:
                raise AssertionError(f"duplicate alias pair {seen[v]!r}/{k!r}={v!r}")
        seen[v] = k


def test_cdn_image_expires_at_from_oe() -> None:
    from app.services.instagram_native import cdn_image_expires_at

    url = (
        "https://scontent.cdninstagram.com/v/t51.xxx/x.jpg"
        "?stp=dst-jpg_s150x150&oe=6A78852D&_nc_ht=scontent.cdninstagram.com"
    )
    assert cdn_image_expires_at(url) == "2026-08-09T13:48:29Z"
    assert cdn_image_expires_at("https://example.com/a.jpg") is None


def test_post_likes_null_when_counts_disabled() -> None:
    media = {
        "code": "ABC123xy",
        "pk": "111",
        "media_type": 2,
        "product_type": "clips",
        "like_count": 0,
        "comment_count": 3,
        "like_and_view_counts_disabled": True,
        "play_count": 999,
        "user": {"username": "x", "pk": "1"},
        "caption": {"text": "hi"},
        "image_versions2": {"candidates": [{"url": "https://example.com/t.jpg"}]},
        "video_versions": [{"url": "https://example.com/v.mp4"}],
    }
    post = map_post_from_media(media)
    assert post["likeAndViewCountsDisabled"] is True
    assert post["engagement"]["likes"] is None
