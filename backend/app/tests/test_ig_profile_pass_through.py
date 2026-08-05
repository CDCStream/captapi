from __future__ import annotations

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
    assert "private" not in ch
    assert ch["isPrivate"] is False
    ps = map_profile_search_user(u)
    assert ps["platform"] == "instagram"
    assert ps["categoryName"] == "Entrepreneur"
    assert ps["fbid"] == "17841402777077586"
    assert ps["relatedProfiles"][0]["id"] == "9"
    assert ps["url"] == "https://www.instagram.com/austinbbq/"
    assert "private" not in ps
    assert ps["isPrivate"] is False
    assert ch["url"] == ps["url"]


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
