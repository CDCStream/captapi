"""Unit tests for Facebook Marketplace location resolve (cityPageId as id)."""

from __future__ import annotations

from app.services import facebook_marketplace_location_native as loc


def test_city_page_id_from_hub_html():
    html = (
        '<script>{"city_page":{"__typename":"MarketplaceCityPage","id":"109791499039942"}}</script>'
    )
    assert loc._city_page_id(html) == "109791499039942"


def test_city_page_id_alt_typename_order():
    html = '{"id":"109791499039942","__typename":"MarketplaceCityPage"}'
    assert loc._city_page_id(html) == "109791499039942"


def test_location_row_uses_city_page_id_not_pipe_key():
    row = loc._location_row(
        city="Austin",
        state="TX",
        name="Austin, TX",
        lat=30.2677,
        lng=-97.7475,
        city_page_id="109791499039942",
        slug="austin",
    )
    assert row["id"] == "109791499039942"
    assert row["cityPageId"] == "109791499039942"
    assert "|" not in str(row.get("id") or "")


def test_location_row_omits_fabricated_id_when_missing():
    row = loc._location_row(
        city="Austin",
        state="MN",
        name="Austin, MN",
        lat=43.6666,
        lng=-92.9746,
        city_page_id=None,
        slug="austin-minnesota",
    )
    assert "id" not in row
    assert "cityPageId" not in row
    assert row["slug"] == "austin-minnesota"


def test_parse_city_state():
    assert loc._parse_city_state("Austin, TX") == ("Austin", "TX")
    assert loc._parse_city_state("Austin TX") == ("Austin", "TX")
    assert loc._parse_city_state("Austin") == ("Austin", None)
