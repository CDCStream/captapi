"""Tests for TikTok DSA Z1–Z4 fixes."""
from __future__ import annotations

from app.routers import ad_library as al
from app.services import tiktok_ads_native as tt


def test_tiktok_date_iso_is_calendar_day() -> None:
    assert al._tiktok_library_date_iso("07/29/2026") == "2026-07-29T00:00:00.000Z"
    assert (
        al._tiktok_library_date_iso("2026-07-29T16:19:11.000Z")
        == "2026-07-29T00:00:00.000Z"
    )
    # Epoch with wall-clock → midnight (never emit scrape time-of-day).
    assert al._tiktok_library_date_iso(1786033151000) == "2026-08-06T00:00:00.000Z"
    assert tt._ms_to_iso(1785283200000) == "2026-07-29T00:00:00.000Z"


def test_tiktok_search_omits_run_dates() -> None:
    out = al._finalise_tiktok_ad(
        al._normalize_ad(
            {
                "adId": "1",
                "advertiserName": "Brand",
                "text": "hello",
                "first_shown_date": "07/29/2026",
                "last_shown_date": "08/01/2026",
                "estimatedAudience": "0-1K",
                "library": "dsa",
                "country": "GB",
                "media": [],
            },
            "tiktok",
        ),
        surface="search",
    )
    assert "firstShown" not in out
    assert "lastShown" not in out
    assert out["text"] == "hello"
    assert out["headline"] is None
    assert out["cta"] is None
    assert set(out["advertiser"]) == set(al.TIKTOK_ADVERTISER_KEYS)


def test_tiktok_ads_uniform_keys() -> None:
    rows = [
        {
            "adId": "1",
            "advertiserName": "Brand",
            "text": "hello",
            "estimatedAudience": "0-1K",
            "library": "dsa",
            "country": "GB",
            "media": [],
        },
        {
            "adId": "2",
            "advertiserName": "Other",
            # no text/headline
            "library": "dsa",
            "country": "GB",
            "media": [{"url": "https://cdn.example/v.mp4", "type": "video/mp4"}],
        },
    ]
    ads = [
        al._finalise_tiktok_ad(al._normalize_ad(r, "tiktok"), surface="search")
        for r in rows
    ]
    shapes = {tuple(sorted(a.keys())) for a in ads}
    assert len(shapes) == 1
    assert ads[0]["text"] == "hello"
    assert ads[1]["text"] is None
    assert ads[1]["headline"] is None


def test_tiktok_rejects_numeric_advertiser_name() -> None:
    shaped = tt._to_normalize_shape(
        {
            "id": "1872034324356433",
            "name": "",
            "advertiser": {
                "name": "7510870833108090902",
                "adv_biz_ids": "7510870748832202753",
                "sponsor": "7510870833108090902",
                "registry_location": "Germany",
            },
        }
    )
    assert shaped["advertiserName"] is None
    # Prefer human label when present alongside numeric sponsor.
    shaped2 = tt._to_normalize_shape(
        {
            "id": "1872034324356433",
            "name": "alyalina535",
            "advertiser": {
                "name": "alyalina535",
                "adv_biz_ids": "7510870748832202753",
                "sponsor": "7510870833108090902",
                "registry_location": "Germany",
            },
        }
    )
    assert shaped2["advertiserName"] == "alyalina535"
    out = al._finalise_tiktok_ad(al._normalize_ad(shaped2, "tiktok"), surface="details")
    assert out["advertiser"]["name"] == "alyalina535"
    assert out["advertiser"]["id"] == "7510870748832202753"
    assert set(out["advertiser"]) == set(al.TIKTOK_ADVERTISER_KEYS)
    assert "firstShown" in out and "lastShown" in out


def test_tiktok_detail_advertiser_keys_match_search() -> None:
    row = {
        "adId": "1",
        "advertiserName": "Brand",
        "advertiserId": "1234567890123456789",
        "advertiserLocation": "Germany",
        "first_shown_date": "07/29/2026",
        "library": "dsa",
        "country": "GB",
        "media": [],
    }
    search = al._finalise_tiktok_ad(al._normalize_ad(row, "tiktok"), surface="search")
    detail = al._finalise_tiktok_ad(al._normalize_ad(row, "tiktok"), surface="details")
    assert set(search["advertiser"]) == set(detail["advertiser"]) == set(
        al.TIKTOK_ADVERTISER_KEYS
    )
