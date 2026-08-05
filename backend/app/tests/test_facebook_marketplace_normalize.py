"""Unit tests for Facebook Marketplace normalize helpers."""

from __future__ import annotations

from app.services import facebook_marketplace_native as m


def test_listing_status_sold_beats_live():
    assert m.listing_status(is_sold=True, is_pending=False, is_live=True) == "sold"
    assert m.listing_status(is_sold=False, is_pending=True, is_live=True) == "pending"
    assert m.listing_status(is_sold=False, is_pending=False, is_live=True) == "available"
    assert m.listing_status(is_sold=False, is_pending=False, is_live=False) == "unavailable"


def test_annotate_ships_outside_radius():
    row = {
        "city": "Fresno",
        "state": "CA",
        "location": "Fresno, CA",
        "deliveryTypes": ["IN_PERSON", "SHIPPING_ONSITE"],
    }
    out = m.annotate_search_locality(
        row, origin_city="Austin", origin_state="TX", radius_miles=500
    )
    assert out["isLocal"] is False
    assert out["shipsOutsideRadius"] is True


def test_annotate_local_city_match():
    row = {
        "city": "Austin",
        "state": "TX",
        "location": "Austin, TX",
        "deliveryTypes": ["IN_PERSON"],
    }
    out = m.annotate_search_locality(row, origin_city="Austin", origin_state="TX")
    assert out["isLocal"] is True
    assert "shipsOutsideRadius" not in out


def test_map_listing_drops_viewer_seller_and_singleton_photos():
    node = {
        "id": "1",
        "marketplace_listing_title": "Chair",
        "listing_price": {
            "amount": "50",
            "formatted_amount_zeros_stripped": "$50",
            "amount_with_offset_in_currency": "5000",
            "currency": "USD",
        },
        "location": {
            "reverse_geocode": {
                "city": "Benson",
                "state": "AZ",
                "city_page": {"id": "9"},
            }
        },
        "is_sold": False,
        "is_live": True,
        "is_pending": False,
        "is_hidden": False,
        "is_viewer_seller": False,
        "delivery_types": ["IN_PERSON", "SHIPPING_ONSITE"],
        "primary_listing_photo": {"image": {"uri": "https://example.com/a.jpg"}},
        "creation_time": 1720000000,
    }
    out = m._map_listing(node)
    assert out is not None
    assert out["status"] == "available"
    assert "isViewerSeller" not in out
    assert "isLive" not in out
    assert out["image"] == "https://example.com/a.jpg"
    assert "photos" not in out
    assert out["priceAmount"] == 5000


def test_map_item_seller_and_status_sold():
    node = {
        "id": "222",
        "marketplace_listing_title": "Desk",
        "listing_price": {
            "amount": "125",
            "formatted_amount_zeros_stripped": "$125",
            "amount_with_offset_in_currency": "12500",
            "currency": "USD",
        },
        "location_text": {"text": "Arlington, VA"},
        "location": {"latitude": 38.8, "longitude": -77.0},
        "is_sold": True,
        "is_live": True,
        "is_pending": False,
        "marketplace_listing_seller": {"id": "99", "name": "Jane"},
        "listing_photos": [{"image": {"uri": "https://example.com/1.jpg"}}, {"image": {"uri": "https://example.com/2.jpg"}}],
        "delivery_types": ["IN_PERSON"],
    }
    out = m._map_item_detail(node, "https://www.facebook.com/marketplace/item/222/")
    assert out is not None
    assert out["status"] == "sold"
    assert out["isSold"] is True
    assert "isPublished" not in out
    assert out["seller"]["id"] == "99"
    assert out["seller"]["name"] == "Jane"
    assert out["city"] == "Arlington"
    assert out["state"] == "VA"
    assert out["priceAmount"] == 12500
    assert len(out["photos"]) == 2