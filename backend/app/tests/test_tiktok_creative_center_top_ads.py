"""TikTok Creative Center Top Ads normalization and relevance filter."""

from __future__ import annotations

import pytest

from app.services import tiktok_creative_center as cc


def test_resolve_industry_label_from_key() -> None:
    assert cc.resolve_industry_label("label_14104000000", "All Industries") == "Cosmetics"
    assert cc.resolve_industry_label("label_25100000000", "All Industries") == "Games"
    assert cc.resolve_industry_label("label_25302000000", None) == "Casino"


def test_top_ad_keyword_rejects_unrelated() -> None:
    assert not cc.top_ad_matches_query(
        {"ad_title": "Being a landlord", "brand_name": "Rent Please!"},
        "casino",
    )
    assert cc.top_ad_matches_query(
        {"ad_title": "Best online casino bonuses", "brand_name": "Lucky"},
        "casino",
    )
    assert cc.top_ad_matches_query(
        {"ad_title": "Play now", "industry_key": "label_25302000000"},
        "casino",
    )


def test_normalize_top_ad_detail_url_and_industry() -> None:
    out = cc.normalize_top_ad(
        {
            "ad_id": "7157957505971716098",
            "brand_name": "Rent Please!",
            "ad_title": "Being a landlord",
            "likes": 60000,
            "ctr": 0.11,
            "ctr_tier": "below_50%",
            "is_spark_ad": False,
            "industry": "All Industries",
            "industry_key": "label_25100000000",
            "objective": "Conversion",
            "ad_format": "All Formats",
            "source_url": (
                "https://ads.tiktok.com/business/creativecenter/inspiration/"
                "topads/pc/en?period=180&region=NL&order_by=for_you&keyword=casino"
            ),
            "countries": ["NL"],
            "period_days": 180,
            "favorite": False,
            "video_url": "https://v.example/a.mp4",
            "video_url_hd": "https://v.example/a.mp4",
            "cover_url": "https://p.example/c.jpg",
            "video_id": "v1",
            "video_duration_seconds": 42.0,
            "video_width": 576,
            "video_height": 1024,
        }
    )
    assert out["url"] == (
        "https://ads.tiktok.com/business/creativecenter/topads/"
        "7157957505971716098/pc/en"
    )
    assert out["industry"] == "Games"
    assert out["adFormat"] == "Non-Spark Ads"
    assert "favorite" not in out
    assert out["video"]["urlHd"] is None
    assert out["likesIsApproximate"] is True


def test_apify_industry_maps_keys_and_rejects_unknown() -> None:
    assert cc.normalize_apify_industry(None) is None
    assert cc.normalize_apify_industry("All Industries") is None
    assert cc.normalize_apify_industry("Gaming") == "Gaming"
    assert cc.normalize_apify_industry("Games") == "Gaming"
    assert cc.normalize_apify_industry("label_25100000000") == "Gaming"
    assert cc.normalize_apify_industry("Cosmetics") == "Beauty & Personal Care"
    payload = cc.apify_input(
        country="NL",
        period=180,
        order_by="For You",
        limit=10,
        industry="label_25100000000",
        q="casino",
    )
    assert payload["industry"] == "Gaming"
    assert payload["keyword"] == "casino"
    with pytest.raises(ValueError, match="must be one of"):
        cc.normalize_apify_industry("not-a-real-industry-xyz")


def test_apify_objective_aliases() -> None:
    assert cc.normalize_apify_objective("Conversion") == "Conversions"
    assert cc.normalize_apify_objective("Video View") == "Video Views"
    with pytest.raises(ValueError, match="must be one of"):
        cc.normalize_apify_objective("Product Sales")


def test_fetch_limit_overfetches_for_keyword() -> None:
    assert cc.fetch_limit_for_query(10, None) == 10
    assert cc.fetch_limit_for_query(10, "casino") == 50
