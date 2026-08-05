"""TikTok Creative Center Top Ads normalization and relevance filter."""

from __future__ import annotations

import pytest

from app.services import tiktok_creative_center as cc


def test_resolve_industry_label_from_key() -> None:
    assert cc.resolve_industry_label("label_14104000000", "All Industries") == "Cosmetics"
    assert cc.resolve_industry_label("label_25100000000", "All Industries") == "Games"
    assert cc.resolve_industry_label("label_25302000000", None) == "Casino"


def test_top_ad_keyword_any_vs_all() -> None:
    row = {"ad_title": "Best online casino bonuses", "brand_name": "Lucky"}
    assert cc.top_ad_matches_query(row, "casino", match="any")
    assert cc.top_ad_matches_query(row, "casino poker", match="any")
    assert not cc.top_ad_matches_query(row, "casino poker", match="all")
    assert not cc.top_ad_matches_query(
        {"ad_title": "Being a landlord", "brand_name": "Rent Please!"},
        "casino",
        match="any",
    )
    assert cc.top_ad_matches_query(
        {"ad_title": "Play now", "industry_key": "label_25302000000"},
        "casino",
        match="any",
    )


def test_filter_soft_fallback_when_literal_empty() -> None:
    rows = [
        {"ad_id": "1", "ad_title": "Being a landlord", "brand_name": "Rent"},
        {"ad_id": "2", "ad_title": "Apartment tips", "brand_name": "Home"},
    ]
    filt = cc.filter_top_ads(rows, q="casino", match="any", soft_fallback=True)
    assert filt["matchedFrom"] == 2
    assert filt["literalMatches"] == 0
    assert filt["filteredOut"] == 0
    assert filt["matchBasis"] == "creative_center"
    assert len(filt["rows"]) == 2

    strict = cc.filter_top_ads(rows, q="casino", match="any", soft_fallback=False)
    assert strict["matchedFrom"] == 2
    assert strict["filteredOut"] == 2
    assert strict["rows"] == []
    assert strict["matchBasis"] == "any"


def test_filter_reports_matched_from() -> None:
    rows = [
        {"ad_id": "1", "ad_title": "Casino night", "brand_name": "Lucky"},
        {"ad_id": "2", "ad_title": "Landlord tips", "brand_name": "Rent"},
    ]
    filt = cc.filter_top_ads(rows, q="casino", match="any", soft_fallback=True)
    assert filt["matchedFrom"] == 2
    assert filt["literalMatches"] == 1
    assert filt["filteredOut"] == 1
    assert filt["matchBasis"] == "any"
    assert len(filt["rows"]) == 1


def test_normalize_top_ad_shape() -> None:
    out = cc.normalize_top_ad(
        {
            "ad_id": "7157957505971716098",
            "brand_name": "Rent Please!",
            "brand_id": "brand_123",
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
            "first_shown_date": "20260115",
            "last_shown_date": "20260201",
            "video_url": "https://v.example/a.mp4",
            "video_url_hd": "https://v.example/a.mp4",  # identical → omit urlHd
            "cover_url": "https://p.example/c.jpg",
            "video_id": "v1",
            "video_duration_seconds": 42.0,
            "video_width": 576,
            "video_height": 1024,
        },
        query_country="NL",
    )
    assert out["url"] == (
        "https://ads.tiktok.com/business/creativecenter/topads/"
        "7157957505971716098/pc/en"
    )
    assert out["industry"] == "Games"
    assert "adFormat" not in out  # Spark/Non-Spark echo dropped; isSparkAd kept
    assert out["isSparkAd"] is False
    assert "favorite" not in out
    assert "media" not in out
    assert "countries" not in out  # query-country echo dropped
    assert "urlHd" not in out["video"]
    assert out["likesIsApproximate"] is True
    assert out["advertiser"] == {"id": "brand_123", "name": "Rent Please!"}
    assert out["firstSeen"] == "2026-01-15T00:00:00.000Z"
    assert out["lastSeen"] == "2026-02-01T00:00:00.000Z"


def test_normalize_spark_falls_back_to_author() -> None:
    out = cc.normalize_top_ad(
        {
            "ad_id": "9",
            "brand_name": "Not Mention",
            "is_spark_ad": True,
            "ad_format": "Spark Ads",
            "author": {"id": "uid42", "unique_id": "creator_x", "nickname": "Creator X"},
            "countries": ["US", "CA"],
            "video_info": {
                "vid": "v9",
                "cover": "https://p.example/c.jpg",
                "video_url": {"720p": "https://v.example/a.mp4", "1080p": "https://v.example/hd.mp4"},
                "duration": 12,
            },
        },
        query_country="US",
    )
    assert out["brandName"] == "Creator X"
    assert out["advertiser"] == {"id": "uid42", "name": "Creator X"}
    assert out["isSparkAd"] is True
    assert "adFormat" not in out
    assert out["countries"] == ["US", "CA"]  # multi-country kept
    assert out["video"]["urlHd"] == "https://v.example/hd.mp4"
    assert out["firstSeen"] is None
    assert out["lastSeen"] is None


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
