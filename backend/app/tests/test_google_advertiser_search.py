"""Google advertiser-search ranking + Google ad schema null keys."""

from __future__ import annotations

from app.routers import ad_library as al
from app.services import google_ads_native as g


def test_suggestion_queries_expand_nike() -> None:
    qs = g._suggestion_queries("nike")
    assert "nike" in qs
    assert any("inc" in q.lower() for q in qs)


def test_rank_prefers_nike_inc_for_us() -> None:
    rows = [
        {"id": "AR1", "name": "NIKE SRL", "adsCount": 100},
        {"id": "AR2", "name": "Nike, Inc.", "adsCount": 5000},
        {"id": "AR3", "name": "Nike Retail BV", "adsCount": 200},
    ]
    ranked = g._rank_advertisers(rows, query="nike", country="US")
    assert ranked[0]["id"] == "AR2"
    assert ranked[0]["name"] == "Nike, Inc."


def test_google_normalize_keeps_null_keys() -> None:
    out = al._normalize_ad(
        {
            "creativeId": "CR1",
            "advertiserId": "AR16735076323512287233",
            "advertiserName": "Nike, Inc.",
            "adFormat": "image",
            "firstShown": "2022-11-30T00:00:00.000Z",
            "lastShown": "2026-07-26T00:00:00.000Z",
            "media": ["https://tpc.googlesyndication.com/simgad/x.jpg"],
        },
        "google_ad_library",
    )
    assert out["text"] is None
    assert out["headline"] is None
    assert out["cta"] is None
    assert "landingUrl" in out
    assert out["advertiser"]["id"] == "AR16735076323512287233"
    assert out["countries"] == []
    assert out["textIsTemplate"] is False


def test_google_countries_iso_and_dki_flag() -> None:
    out = al._normalize_ad(
        {
            "creativeId": "CR9",
            "advertiserId": "AR1",
            "advertiserName": "Nike Retail BV",
            "text": "Discover {KeyWord:Nike Shoes} Online",
            "headline": "{KeyWord:Nike Vomero}",
            "country": "Malta, United Arab Emirates, United States, Czechia",
            "impressions": "7000-8000",
        },
        "google_ad_library",
    )
    assert out["textIsTemplate"] is True
    assert out["country"] is None  # multi-region → null + countries[]
    assert out["countries"] == ["MT", "AE", "US", "CZ"]
    assert out["impressions"] == "7000-8000"


def test_google_detail_identity_rejects_wrong_entity() -> None:
    ok = al._google_detail_identity(
        {
            "creativeId": "CR13596485266373083137",
            "advertiserId": "AR16735076323512287233",
            "advertiserName": "Nike, Inc.",
            "text": "hi",
        },
        advertiser_id="AR16735076323512287233",
        creative="CR13596485266373083137",
    )
    assert ok is not None
    assert ok["id"] == "CR13596485266373083137"
    assert ok["advertiser"]["id"] == "AR16735076323512287233"

    bad = al._google_detail_identity(
        {
            "creativeId": "CR08395356613392728065",
            "advertiserId": "AR18378488041124659201",
            "advertiserName": "Nike Retail BV",
        },
        advertiser_id="AR16735076323512287233",
        creative="CR13596485266373083137",
    )
    assert bad is None


def test_linkedin_advertiser_id_from_url_and_countries() -> None:
    out = al._normalize_ad(
        {
            "id": "1456323573",
            "headline": "Hello",
            "text": "Body",
            "advertiserName": "ScriptRunner",
            "advertiserUrl": "https://www.linkedin.com/company/3509299",
            "advertiserLogo": "https://media.licdn.com/logo.png",
            "impressionsByCountry": [
                {"country": "United States", "impressions": "97%"},
                {"country": "Canada", "impressions": "3%"},
            ],
            "startDate": "2026-07-28",
            "endDate": "2026-08-02",
        },
        "linkedin_ad_library",
    )
    assert out["advertiser"]["id"] == "3509299"
    assert out["advertiser"]["logo"] == "https://media.licdn.com/logo.png"
    assert out["countries"] == ["US", "CA"]
    assert out["firstShown"] == "2026-07-28"
    assert "spend" in out and out["spend"] is None
