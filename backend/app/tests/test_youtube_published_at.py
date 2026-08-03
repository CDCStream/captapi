"""Tests for YouTube relative -> ISO publishedAt coercion."""

from __future__ import annotations

from datetime import datetime, timezone

from app.services.youtube_native import (
    approximate_iso_from_relative,
    coerce_published_fields,
    published_fields,
)

NOW = datetime(2026, 8, 2, 12, 0, 0, tzinfo=timezone.utc)


def test_approximate_iso_from_relative_common_labels() -> None:
    assert approximate_iso_from_relative("4 days ago", now=NOW) == "2026-07-29T12:00:00.000Z"
    assert approximate_iso_from_relative("1 month ago", now=NOW) == "2026-07-03T12:00:00.000Z"
    assert approximate_iso_from_relative("5d ago", now=NOW) == "2026-07-28T12:00:00.000Z"
    assert approximate_iso_from_relative("Streamed 3 days ago", now=NOW) == "2026-07-30T12:00:00.000Z"


def test_published_fields_splits_iso_and_text() -> None:
    iso, text = published_fields("4 days ago")
    assert iso and iso.endswith("Z") and "T" in iso
    assert text == "4 days ago"
    iso2, text2 = published_fields("2026-07-27T22:52:21.000Z")
    assert iso2 == "2026-07-27T22:52:21.000Z"
    assert text2 is None


def test_coerce_never_leaves_relative_in_published_at() -> None:
    card = {"publishedAt": "4 days ago", "title": "x"}
    out = coerce_published_fields(card)
    assert out["publishedAt"] and "ago" not in out["publishedAt"]
    assert out["publishedTimeText"] == "4 days ago"
    # Already ISO stays
    card2 = {"publishedAt": "2026-07-27T22:52:21.000Z", "publishedTimeText": "4 days ago"}
    out2 = coerce_published_fields(card2)
    assert out2["publishedAt"] == "2026-07-27T22:52:21.000Z"
    assert out2["publishedTimeText"] == "4 days ago"
