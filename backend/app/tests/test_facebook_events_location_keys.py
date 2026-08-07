"""FE6 — event.location always has the same five keys."""

from __future__ import annotations

from app.routers import facebook as fb

_LOCATION_KEYS = {"name", "city", "latitude", "longitude", "countryCode"}


def test_location_key_set_identical_across_events():
    chicago = fb._normalize_event(
        {
            "id": "1",
            "url": "https://www.facebook.com/events/1/",
            "name": "Chicago Show",
            "startDate": "2026-08-19T19:00:00-05:00",
            "timezone": "America/Chicago",
            "startTime": "Wednesday, August 19, 2026 at 7:00 PM CDT",
            "location": {
                "name": "The Laugh Factory",
                "city": "Chicago, IL",
                "latitude": 41.9,
                "longitude": -87.6,
                "countryCode": "US",
            },
        }
    )
    london = fb._normalize_event(
        {
            "id": "2",
            "url": "https://www.facebook.com/events/2/",
            "name": "London Show",
            "startDate": "2024-12-17T19:00:00+00:00",
            "timezone": "Europe/London",
            "startTime": "Tuesday, December 17, 2024 at 7:00 PM GMT",
            "location": {
                "name": "Borough high street",
                "latitude": 51.5,
                "longitude": -0.09,
            },
        }
    )
    assert set(chicago["location"].keys()) == _LOCATION_KEYS
    assert set(london["location"].keys()) == _LOCATION_KEYS
    assert london["location"]["city"] is None
    assert london["location"]["countryCode"] is None
    assert chicago["location"]["city"] == "Chicago, IL"
