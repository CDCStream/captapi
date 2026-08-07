"""PE1/PE4/PE5 -- one Event shape; eventType != visibility; startTime has a year."""

from __future__ import annotations

from app.routers import facebook as fb

_EVENT_KEYS = {
    "platform",
    "id",
    "url",
    "name",
    "description",
    "startDate",
    "endDate",
    "timezone",
    "startTime",
    "duration",
    "durationSeconds",
    "eventType",
    "visibility",
    "isOnline",
    "isPast",
    "isCanceled",
    "address",
    "image",
    "usersGoing",
    "usersInterested",
    "usersResponded",
    "location",
    "organizers",
    "ticketsUrl",
    "categories",
    "externalLinks",
}


def test_thin_profile_card_emits_full_event_shape_with_nulls():
    out = fb._normalize_event(
        {
            "id": "111",
            "url": "https://www.facebook.com/events/111/",
            "name": "MSG Show",
            "startDate": "2026-08-07T19:00:00-04:00",
            "timezone": "America/New_York",
            "startTime": "Fri, Aug 7 at 7:00 PM EDT",
            "eventType": "PUBLIC_TYPE",
            "event_kind": "PUBLIC_TYPE",
            "location": {"name": "Madison Square Garden", "city": "New York, NY"},
        }
    )
    assert set(out.keys()) == _EVENT_KEYS
    assert out["description"] is None
    assert out["endDate"] is None
    assert out["duration"] is None
    assert out["durationSeconds"] is None
    assert out["isOnline"] is None
    assert out["address"] is None
    assert out["image"] is None
    assert out["organizers"] == []
    assert out["ticketsUrl"] is None
    assert out["categories"] == []
    assert out["eventType"] is None
    assert out["visibility"] == "public"
    assert out["startTime"] is not None
    assert "2026" in out["startTime"]


def test_category_event_type_not_overwritten_by_visibility():
    out = fb._normalize_event(
        {
            "id": "222",
            "url": "https://www.facebook.com/events/222/",
            "name": "Comedy Night",
            "startDate": "2026-08-19T19:00:00-05:00",
            "endDate": "2026-08-19T20:30:00-05:00",
            "timezone": "America/Chicago",
            "startTime": "Wednesday, August 19, 2026 at 7:00 PM - 8:30 PM CDT",
            "eventType": "Comedy",
            "event_kind": "PUBLIC_TYPE",
            "categories": [{"label": "Comedy", "url": None}],
            "location": {"name": "The Laugh Factory", "city": "Chicago, IL"},
        }
    )
    assert out["eventType"] == "Comedy"
    assert out["visibility"] == "public"
    assert "2026" in out["startTime"]


def test_format_start_time_adds_year_to_yearless_sentence():
    stamp = fb._format_event_start_time(
        "2026-08-07T19:00:00-04:00",
        None,
        "America/New_York",
        "Fri, Aug 7 at 7:00 PM EDT",
    )
    assert stamp is not None
    assert "2026" in stamp
