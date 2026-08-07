"""FE4 — Facebook event-search location is geo, not title substring."""

from __future__ import annotations

from app.services import facebook_events_native as native


def test_london_matches_europe_london_timezone():
    assert native.event_matches_location(
        {
            "timezone": "Europe/London",
            "location": {"name": "Soho Theatre", "city": None},
        },
        "London",
    )


def test_london_matches_coords_without_city_name():
    assert native.event_matches_location(
        {
            "timezone": None,
            "location": {
                "name": "Soho Theatre",
                "latitude": 51.5145,
                "longitude": -0.1320,
            },
        },
        "London",
    )


def test_london_rejects_chicago_event():
    assert not native.event_matches_location(
        {
            "timezone": "America/Chicago",
            "location": {"name": "The Laugh Factory", "city": "Chicago, IL"},
        },
        "London",
    )


def test_title_substring_alone_does_not_match():
    """Title containing London must not count — geo fields only."""
    assert not native.event_matches_location(
        {
            "name": "London Comedy Night in Berlin",
            "timezone": "Europe/Berlin",
            "location": {"name": "Quatsch Comedy Club", "city": "Berlin"},
        },
        "London",
    )


def test_empty_location_passes():
    assert native.event_matches_location({"timezone": "America/Chicago"}, None)
    assert native.event_matches_location({"timezone": "America/Chicago"}, "")
