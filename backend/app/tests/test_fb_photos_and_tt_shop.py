"""Facebook photo alt-text naming + TikTok shop/region mapping."""

from __future__ import annotations

from app.routers import facebook as fb
from app.services import facebook_profile_photos_native as photos
from app.services import tiktok_native as tt


def test_photo_node_uses_accessibility_caption_not_caption() -> None:
    row = photos._from_photo_node(
        {
            "id": "123",
            "__typename": "Photo",
            "accessibility_caption": "May be an image of basketball and text",
            "viewer_image": {"uri": "https://cdn.example/full.jpg", "width": 1200, "height": 800},
            "thumbnailImage": {"uri": "https://cdn.example/thumb.jpg"},
        }
    )
    assert row is not None
    assert "caption" not in row
    assert row["accessibilityCaption"] == "May be an image of basketball and text"
    assert row["thumbnailUrl"] == "https://cdn.example/thumb.jpg"


def test_normalize_photo_renames_legacy_caption() -> None:
    out = fb._normalize_photo(
        {
            "id": "1",
            "url": "https://www.facebook.com/photo.php?fbid=1",
            "image": "https://cdn.example/a.jpg",
            "caption": "A galaxy cluster in deep space.",
        }
    )
    assert out["accessibilityCaption"] == "A galaxy cluster in deep space."
    assert "caption" not in out


def test_extract_shop_product_url_from_pid() -> None:
    url = tt.extract_shop_product_url(
        {"anc_goods_list": [{"product_id": "1729494515984797858"}]}
    )
    assert url == "https://www.tiktok.com/shop/pdp/1729494515984797858"


def test_map_aweme_includes_region_and_shop() -> None:
    post = tt._map_aweme_post(
        {
            "aweme_id": "7545933721589910798",
            "desc": "best boys #friends",
            "create_time": 1756924658,
            "region": "DE",
            "desc_language": "en",
            "is_paid_partnership": False,
            "is_eligible_for_commission": True,
            "shop_product_url": "https://www.tiktok.com/shop/pdp/1729494515984797858",
            "author": {"unique_id": "branttakes", "region": "DE"},
            "statistics": {"play_count": 10, "digg_count": 1, "comment_count": 0, "share_count": 0, "collect_count": 0},
            "video": {"duration": 12, "cover": {"url_list": ["https://cdn.example/c.jpg"]}},
        }
    )
    assert post is not None
    assert post["locationCreated"] == "DE"
    assert "region" not in post
    assert post["authorRegion"] == "DE"
    assert post["author"]["region"] == "DE"
    assert post["shopProductUrl"] == "https://www.tiktok.com/shop/pdp/1729494515984797858"
    assert post["descLanguage"] == "en"
    assert post["isEligibleForCommission"] is True
    assert post["isPaidPartnership"] is False
