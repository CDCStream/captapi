"""FE1 - Facebook event timezone: lat/lng to IANA, never Etc/*."""

from __future__ import annotations

from app.routers import facebook as fb
from app.services import facebook_events_native as native


def test_gmt_abbrev_maps_to_europe_london_not_etc():
    assert native._timezone_from_sentence(
        "Tuesday, December 17, 2024 at 7:00 PM - 10:30 PM GMT"
    ) == "Europe/London"
    assert native._timezone_from_sentence(
        "Wednesday, August 19, 2026 at 7:00 PM - 8:30 PM CDT"
    ) == "America/Chicago"


def test_sanitize_rejects_etc_zones():
    assert native.sanitize_iana_timezone("Etc/GMT") is None
    assert native.sanitize_iana_timezone("Etc/UTC") is None
    assert native.sanitize_iana_timezone("Europe/London") == "Europe/London"
    assert native.sanitize_iana_timezone("UTC") == "UTC"


def test_coords_resolve_london_and_chicago():
    assert native.timezone_from_coords(51.5074, -0.1276) == "Europe/London"
    assert native.timezone_from_coords(41.8781, -87.6298) == "America/Chicago"


def test_resolve_prefers_coords_over_wrong_abbrev():
    assert (
        native.resolve_event_timezone(
            raw_timezone="Etc/GMT",
            sentence="Tuesday, December 17, 2024 at 7:00 PM GMT",
            latitude=51.5074,
            longitude=-0.1276,
        )
        == "Europe/London"
    )


def test_resolve_null_when_unknown():
    assert (
        native.resolve_event_timezone(
            raw_timezone="Etc/GMT",
            sentence=None,
            latitude=None,
            longitude=None,
        )
        is None
    )


def test_normalize_event_never_emits_etc():
    out = fb._normalize_event(
        {
            "id": "1",
            "url": "https://www.facebook.com/events/1/",
            "name": "Comedy Night",
            "startDate": "2024-12-17T19:00:00+00:00",
            "timezone": "Etc/GMT",
            "startTime": "Tuesday, December 17, 2024 at 7:00 PM - 10:30 PM GMT",
            "location": {
                "name": "A Venue",
                "city": "London",
                "latitude": 51.5074,
                "longitude": -0.1276,
            },
        }
    )
    assert out["timezone"] == "Europe/London"
    assert not str(out["timezone"]).startswith("Etc/")


def test_normalize_event_null_timezone_without_coords_or_abbrev():
    out = fb._normalize_event(
        {
            "id": "2",
            "url": "https://www.facebook.com/events/2/",
            "name": "Mystery",
            "startDate": "2026-01-01T12:00:00Z",
            "timezone": "Etc/GMT",
            "location": {"name": "Somewhere"},
        }
    )
    assert out["timezone"] is None


def test_parse_schedule_gmt_uses_europe_london_dst():
    """August wall-clock in London is BST (UTC+1), not fixed GMT."""
    parsed = native.parse_schedule_sentence(
        "Tuesday, August 19, 2026 at 7:00 PM - 8:30 PM GMT",
        prefer_upcoming=False,
    )
    assert parsed["timezone"] == "Europe/London"
    assert parsed["startDate"] == "2026-08-19T19:00:00+01:00"
