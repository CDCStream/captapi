from __future__ import annotations

from app.routers import facebook as fb
from app.services import facebook_details_native as details


def test_engagement_ignores_unmatched_zero_shares() -> None:
    post_id = "111"
    blobs = [
        {
            # Noise from another post on the listing page.
            "share_count_reduced": 0,
            "total_comment_count": 0,
        },
        {
            "id": f"feedback:{post_id}",
            "url": f"https://www.facebook.com/nasa/posts/pfbid123",
            "share_count_reduced": "240",
            "total_comment_count": 12,
            "reactors": {"count": 50},
        },
    ]
    eng = details._engagement_for_post(blobs, post_id)
    assert eng["shares"] == 240
    assert eng["comments"] == 12


def test_engagement_does_not_invent_zero_from_noise() -> None:
    eng = details._engagement_for_post([{"share_count_reduced": 0}], "999")
    assert eng["shares"] is None


def test_unify_listing_authors_collapses_case() -> None:
    posts = [
        {"author": {"username": "nasa", "url": "https://www.facebook.com/nasa"}},
        {
            "author": {
                "username": "NASA",
                "url": "https://www.facebook.com/NASA",
                "verified": True,
                "profileImage": "https://cdn/x.jpg",
            }
        },
    ]
    fb._unify_listing_authors(posts, "https://www.facebook.com/NASA")
    assert posts[0]["author"]["username"] == "NASA"
    assert posts[1]["author"]["username"] == "NASA"


def test_finalize_keeps_null_views_and_shares() -> None:
    item = {
        "platform": "facebook",
        "id": "1",
        "author": {"username": "NASA"},
        "engagement": {"views": None, "likes": 10, "comments": 1, "shares": None},
    }
    out = fb._finalize_fb_listing_item(item)
    assert out["engagement"]["views"] is None
    assert out["engagement"]["shares"] is None
    assert out["engagement"]["likes"] == 10
