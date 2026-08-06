"""Unit tests for Top Ads list parsing + truncated early-exit."""

from __future__ import annotations

from app.services import tiktok_creative_center as cc


def test_materials_from_list_body_has_more() -> None:
    body = {
        "code": 0,
        "data": {
            "materials": [{"id": "1", "ad_title": "a"}, {"id": "2"}],
            "pagination": {"has_more": True, "page": 1, "size": 20, "total_count": 40},
        },
    }
    rows, has_more = cc._materials_from_list_body(body)
    assert [r["id"] for r in rows] == ["1", "2"]
    assert has_more is True


def test_filter_and_truncate_marks_short_page() -> None:
    rows = [{"id": str(i), "ad_title": f"ad{i}", "brand_name": "x"} for i in range(5)]
    out = cc._filter_and_truncate(
        rows,
        want=20,
        has_more=True,
        q=None,
        match="any",
        industry=None,
        objective=None,
        ad_format=None,
    )
    assert out["truncated"] is True
    assert len(out["rows"]) == 5
    assert out["hasMore"] is True


def test_filter_and_truncate_full_page_not_truncated() -> None:
    rows = [{"id": str(i), "ad_title": f"ad{i}", "brand_name": "x"} for i in range(3)]
    out = cc._filter_and_truncate(
        rows,
        want=3,
        has_more=True,
        q=None,
        match="any",
        industry=None,
        objective=None,
        ad_format=None,
    )
    assert out["truncated"] is False
    assert len(out["rows"]) == 3


def test_filter_and_truncate_empty_after_keyword_not_truncated() -> None:
    """totalReturned=0 after filter must never report truncated=true (T3)."""
    rows = [{"id": "1", "ad_title": "Landlord tips", "brand_name": "Rent"}]
    out = cc._filter_and_truncate(
        rows,
        want=20,
        has_more=True,
        q="casino",
        match="any",
        industry=None,
        objective=None,
        ad_format=None,
    )
    assert out["rows"] == []
    assert out["truncated"] is False
    assert out["candidatesScanned"] == 1
    assert out["filteredOut"] == 1


def test_decodo_timeout_is_hard_safety_net() -> None:
    assert 60.0 <= cc.DECODO_TIMEOUT_SECONDS <= 75.0