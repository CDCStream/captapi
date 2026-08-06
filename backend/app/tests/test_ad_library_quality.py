"""Tests for ad-library advertiser unify, TikTok relevance, ISO dates."""

from __future__ import annotations

from app.routers import ad_library as al
from app.services import facebook_ads_native as fb
from app.services import tiktok_ads_native as tt


def test_unify_advertisers_by_id_collapses_names() -> None:
    ads = [
        {"id": "1", "advertiser": {"id": "20531316728", "name": "Facebook"}},
        {
            "id": "2",
            "advertiser": {
                "id": "20531316728",
                "name": "Facebook App",
                "url": "https://www.facebook.com/facebook/",
            },
        },
        {"id": "3", "advertiser": {"id": "999", "name": "Other"}},
    ]
    al._unify_advertisers_by_id(ads)
    assert ads[0]["advertiser"]["name"] == "Facebook App"
    assert ads[1]["advertiser"]["name"] == "Facebook App"
    assert ads[0]["advertiser"]["url"] == "https://www.facebook.com/facebook/"
    assert ads[2]["advertiser"]["name"] == "Other"


def test_paginate_ads_cursor() -> None:
    ads = [{"id": str(i)} for i in range(5)]
    page, nxt, more = al._paginate_ads(ads, limit=2, cursor=None)
    assert [a["id"] for a in page] == ["0", "1"]
    assert more and nxt
    page2, nxt2, more2 = al._paginate_ads(ads, limit=2, cursor=nxt)
    assert [a["id"] for a in page2] == ["2", "3"]
    page3, nxt3, more3 = al._paginate_ads(ads, limit=2, cursor=nxt2)
    assert [a["id"] for a in page3] == ["4"]
    assert nxt3 is None and not more3


def test_tiktok_relevance_rejects_off_topic() -> None:
    # Whole-word: fashion must not match via substring inside unrelated copy.
    assert not tt.ad_matches_query(
        {"advertiserName": "alyalina535", "text": "Buna dimineata tuturor!"},
        "fashion",
    )
    assert tt.ad_matches_query(
        {"advertiserName": "Nike Europe", "text": "New fashion drop"},
        "fashion",
    )
    # hair ≠ wheelchair
    assert not tt.ad_matches_query(
        {"advertiserName": "Shop", "text": "best wheelchair deals"},
        "hair",
    )


def test_tiktok_date_iso() -> None:
    assert al._tiktok_library_date_iso("07/29/2026") == "2026-07-29T00:00:00.000Z"
    assert (
        al._tiktok_library_date_iso("2026-07-29T00:00:00.000Z")
        == "2026-07-29T00:00:00.000Z"
    )
    assert al._tiktok_library_date_iso(1786033151000) == "2026-08-06T16:19:11.000Z"


def test_tiktok_normalize_omits_withheld_keys() -> None:
    out = al._normalize_ad(
        {
            "adId": "1",
            "advertiserName": "Brand",
            "text": "hello",
            "first_shown_date": "07/29/2026",
            "estimatedAudience": "0-1K",
            "library": "dsa",
            "country": "GB",
            "media": [
                {
                    "url": "https://cdn.example/v.mp4?x-expires=1893456000",
                    "type": "video/mp4",
                    "width": None,
                    "height": None,
                    "durationSeconds": None,
                    "expiresAt": "2030-01-01T00:00:00.000Z",
                }
            ],
        },
        "tiktok",
    )
    assert out["platform"] == "tiktok"
    assert out["library"] == "dsa"
    assert out["country"] == "GB"
    assert out["text"] == "hello"
    assert "cta" not in out
    assert "landingUrl" not in out
    assert "spend" not in out
    assert out["impressions"] == "0-1K"
    assert "id" not in out["advertiser"]
    assert out["advertiser"]["name"] == "Brand"
    assert out["firstShown"] == "2026-07-29T00:00:00.000Z"
    assert isinstance(out["media"], list) and out["media"][0]["url"].startswith("http")
    assert out["media"][0].get("expiresAt")


def test_facebook_detail_delivery_schema() -> None:
    raw = {
        "ad_archive_id": "123",
        "page_id": "99",
        "page_name": "Brand",
        "publisher_platform": ["facebook", "instagram"],
        "collation_count": 4,
        "is_aaa_eligible": True,
        "demographic_distribution": [
            {"age": "25-34", "gender": "Female", "percentage": 0.3},
        ],
        "region_distribution": [{"region": "California", "percentage": 0.1}],
        "snapshot": {"body": {"text": "hi"}, "title": "t", "cta_text": "Shop"},
        "_detailFetch": True,
    }
    mapped = fb.to_normalize_shape(raw)
    mapped["_detailFetch"] = True
    out = al._normalize_ad(mapped, "facebook_ad_library")
    assert out["platforms"] == ["FACEBOOK", "INSTAGRAM"]
    assert out["publisherPlatforms"] == ["FACEBOOK", "INSTAGRAM"]
    assert out["demographicDistribution"][0]["age"] == "25-34"
    assert out["regionDistribution"][0]["region"] == "California"
    assert out["variantCount"] == 4
    assert out["isAaaEligible"] is True


def test_facebook_detail_null_delivery_keys() -> None:
    out = al._normalize_ad(
        {
            "adArchiveId": "1",
            "pageId": "2",
            "pageName": "X",
            "snapshot": {"body": {"text": "hi"}},
            "_detailFetch": True,
        },
        "facebook_ad_library",
    )
    assert "demographicDistribution" in out and out["demographicDistribution"] is None
    assert "regionDistribution" in out and out["regionDistribution"] is None
    assert "variantCount" in out and out["variantCount"] is None
    assert out["platforms"] == []


def test_tiktok_detail_reach_from_text_nodes() -> None:
    html = """
    <html><body>
    <div>Ad ID</div><div>1872402620173314</div>
    <div>Advertiser</div><div>Nike Europe</div>
    <div>First shown</div><div>07/29/2026</div>
    <div>Unique users seen</div><div>0-1K</div>
    <video src="https://library.tiktok.com/api/v1/cdn/x"></video>
    </body></html>
    """
    row = tt.extract_ad_details(html, ad_id="1872402620173314")
    assert row is not None
    assert row["estimatedAudience"] == "0-1K"
    assert row["impressions"] == "0-1K"
    assert row["advertiserName"] == "Nike Europe"

def test_fb_company_matches_query() -> None:
    assert al._fb_company_matches_query("Nike", "nike")
    assert al._fb_company_matches_query("Nike Training Club", "nike")
    assert not al._fb_company_matches_query("Sukeban World", "nike")
    assert not al._fb_company_matches_query("IControl: Easy Widgets Themes", "nike")


def test_fb_search_companies_ranks_nike() -> None:
    companies = [
        {
            "id": "1",
            "name": "Sukeban World",
            "url": "https://www.facebook.com/61551864263186/",
        },
        {
            "id": "15087023444",
            "name": "Nike",
            "url": "https://www.facebook.com/nike/",
        },
        {
            "id": "3",
            "name": "IControl: Easy Widgets Themes",
            "url": "https://www.facebook.com/61578892468353/",
        },
        {
            "id": "4",
            "name": "Nike Training Club",
            "url": "https://www.facebook.com/niketraining/",
        },
    ]
    ranked = al._rank_fb_companies(companies, "nike")
    assert [c["name"] for c in ranked] == ["Nike", "Nike Training Club"]


def test_fb_company_page_vs_profile_id() -> None:
    row = al._fb_company_from_advertiser(
        {
            "id": "146705838515566",
            "pageId": "146705838515566",
            "name": "Example",
            "url": "https://www.facebook.com/61551864263186/",
            "logo": "https://example.com/l.png",
        },
        country="US",
    )
    assert row["pageId"] == "146705838515566"
    assert row["advertiserId"] == "146705838515566"
    assert row["id"] == "146705838515566"
    assert row["profileId"] == "61551864263186"
    assert "view_all_page_id=146705838515566" in (row["libraryUrl"] or "")

def test_facebook_cta_type_exposed() -> None:
    out = al._normalize_ad(
        {
            "adArchiveId": "1",
            "pageId": "99",
            "pageName": "Brand",
            "isActive": True,
            "publisherPlatforms": ["FACEBOOK"],
            "snapshot": {
                "body": {"text": "hi"},
                "title": "t",
                "ctaText": "Shop now",
                "ctaType": "SHOP_NOW",
            },
        },
        "facebook_ad_library",
    )
    assert out["cta"] == "Shop now"
    assert out["ctaType"] == "SHOP_NOW"
    assert out["isActive"] is True
    assert out["publisherPlatforms"] == ["FACEBOOK"]


def test_linkedin_headline_not_advertiser_name() -> None:
    out = al._normalize_ad(
        {
            "id": "1",
            "headline": "Built to grow together",
            "text": "Built to grow together",
            "advertiserName": "Built to grow together",
            "advertiserUrl": "https://www.linkedin.com/company/1035",
            "startDate": "2025-08-10",
            "endDate": "2025-08-10",
        },
        "linkedin_ad_library",
    )
    assert out["advertiser"]["name"] is None
    assert out["advertiser"]["id"] == "1035"
    assert out["advertiserLinkedinPage"] == "https://www.linkedin.com/company/1035"
    assert out["startDate"] == "2025-08-10T00:00:00.000Z"

