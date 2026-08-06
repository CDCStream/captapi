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


def test_keyword_requires_word_boundary() -> None:
    wheelchair = {
        "ad_title": "Best wheelchair accessories",
        "brand_name": "Mobility Co",
    }
    assert not cc.top_ad_matches_query(wheelchair, "hair", match="any")
    assert cc.top_ad_matches_query(
        {"ad_title": "Hair growth serum", "brand_name": "Glow"},
        "hair",
        match="any",
    )
    assert cc.token_in_haystack("casino", "online casino bonuses")
    assert not cc.token_in_haystack("hair", "wheelchair")


def test_filter_empty_when_no_literal_matches() -> None:
    """Never echo the unfiltered leaderboard as a keyword hit."""
    rows = [
        {"ad_id": "1", "ad_title": "Being a landlord", "brand_name": "Rent"},
        {"ad_id": "2", "ad_title": "Apartment tips", "brand_name": "Home"},
    ]
    filt = cc.filter_top_ads(rows, q="casino", match="any")
    assert filt["candidatesScanned"] == 2
    assert "matchedFrom" not in filt
    assert filt["literalMatches"] == 0
    assert filt["filteredOut"] == 2
    assert filt["rows"] == []
    assert filt["matchBasis"] == "any"


def test_filter_reports_candidates_scanned() -> None:
    rows = [
        {"ad_id": "1", "ad_title": "Casino night", "brand_name": "Lucky"},
        {"ad_id": "2", "ad_title": "Landlord tips", "brand_name": "Rent"},
    ]
    filt = cc.filter_top_ads(rows, q="casino", match="any")
    assert filt["candidatesScanned"] == 2
    assert filt["literalMatches"] == 1
    assert filt["filteredOut"] == 1
    assert filt["matchBasis"] == "any"
    assert len(filt["rows"]) == 1


def test_filter_omits_literal_matches_without_q() -> None:
    rows = [{"ad_id": "1", "ad_title": "Casino night", "brand_name": "Lucky"}]
    filt = cc.filter_top_ads(rows, q=None)
    assert filt["candidatesScanned"] == 1
    assert "literalMatches" not in filt
    assert filt["matchBasis"] == "none"


def test_matched_from_fields_provenance() -> None:
    ad = {
        "title": "Promote your brand today",
        "brandName": "Acme",
        "industry": "E-commerce",
        "tags": ["growth"],
        "objective": "Traffic",
    }
    assert cc.matched_from_fields(ad, "promote") == ["title"]
    assert "brandName" in cc.matched_from_fields(
        {**ad, "brandName": "Promote Co"}, "promote"
    )
    assert cc.matched_from_fields(ad, None) == []


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
    assert out["ctrTier"] == "below_50%"
    assert "favorite" not in out
    assert "media" not in out
    assert "countries" not in out  # query-country echo dropped
    assert "urlHd" not in out["video"]
    assert out["likesIsApproximate"] is True
    assert out["advertiser"] == {"id": "brand_123", "name": "Rent Please!"}
    assert out["brandName"] == "Rent Please!"
    # Creative Center list does not expose run dates — omit, do not null-pad.
    assert "firstSeen" not in out
    assert "lastSeen" not in out


def test_normalize_omits_null_optional_flags() -> None:
    out = cc.normalize_top_ad(
        {
            "ad_id": "9",
            "ad_title": "Clip",
            "ctr": 0.11,
            "cost_tier": 2,
            "advertiser": {"id": "a1", "name": "Brand From Nested"},
        }
    )
    assert "ctrTier" not in out
    assert "isSparkAd" not in out
    assert out["brandName"] == "Brand From Nested"
    assert out["advertiser"]["name"] == "Brand From Nested"
    assert "firstSeen" not in out


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
    assert "firstSeen" not in out
    assert "lastSeen" not in out


def test_list_shape_no_always_null_keys() -> None:
    """Acceptance: no key may be null on 100% of rows (T2/T4 hygiene)."""
    rows = [
        {
            "ad_id": "1",
            "ad_title": "Promote growth",
            "brand_name": "Acme",
            "brand_id": "b1",
            "ctr": 0.1,
            "cost_tier": 2,
            "likes": 1000,
            "industry_key": "label_25100000000",
            "objective": "Conversion",
        },
        {
            "ad_id": "2",
            "ad_title": "Other clip",
            "advertiser": {"id": "b2", "name": "Beta"},
            "ctr": 0.2,
            "cost_tier": 1,
            "likes": 2000,
            "industry_key": "label_14104000000",
            "objective": "Traffic",
        },
    ]
    ads = [cc.normalize_top_ad(r, query_country="NL") for r in rows]
    ads[0]["matchedFrom"] = cc.matched_from_fields(ads[0], "promote")
    assert ads[0]["matchedFrom"] == ["title"]
    assert "matchedFrom" not in ads[1]
    assert "firstSeen" not in ads[0]
    assert "ctrTier" not in ads[0]  # omitted when upstream withholds
    # Same form as the live acceptance check: no key null on every row.
    for k in ads[0]:
        assert not all(a.get(k) is None for a in ads)


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
    assert payload["proxyConfiguration"] == {
        "useApifyProxy": True,
        "apifyProxyGroups": ["SHADER"],
    }
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
