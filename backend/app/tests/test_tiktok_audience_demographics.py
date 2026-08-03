from __future__ import annotations

from app.routers.tiktok import (
    _audience_credits,
    _pct,
    _sample_confidence,
    _tally_languages,
    _tally_locations,
    _top_n_with_other,
)


def test_tally_locations_numeric_percentage() -> None:
    # Same mix as the Khaby docs example (n=269).
    codes = ["PK"] * 70 + ["US"] * 33 + ["NG"] * 21 + ["SN"] * 8 + ["BD"] * 8 + ["IN"] * 129
    items = _tally_locations(codes)
    by_code = {x["countryCode"]: x for x in items}
    assert by_code["PK"]["percentage"] == 26.02
    assert by_code["PK"]["percentageText"] == "26.02%"
    assert isinstance(by_code["PK"]["percentage"], float)
    assert round(sum(x["percentage"] for x in items), 2) == 100.0


def test_top_n_with_other_folds_remainder() -> None:
    codes = ["PK"] * 70 + ["US"] * 33 + ["NG"] * 21 + ["SN"] * 8 + ["BD"] * 8 + ["IN"] * 129
    items = _tally_locations(codes)
    sample = sum(x["count"] for x in items)
    head, other = _top_n_with_other(items, limit=5, sample_size=sample)
    assert len(head) == 5
    assert other is not None
    # Top 5 by count leave one of the tied-8 countries in other.
    assert other["count"] == 8
    assert other["percentage"] == _pct(8, sample)
    assert sum(x["count"] for x in head) + other["count"] == sample



def test_tally_languages() -> None:
    items = _tally_languages(["en", "en", "ur", "en"])
    assert items[0]["language"] == "en"
    assert items[0]["count"] == 3
    assert items[0]["percentage"] == 75.0



def test_audience_credits_and_confidence() -> None:
    assert _audience_credits(12) == 3
    assert _audience_credits(30) == 5
    assert _audience_credits(60) == 8
    assert _sample_confidence(269) == "low"
    assert _sample_confidence(400) == "medium"
    assert _sample_confidence(1000) == "high"
