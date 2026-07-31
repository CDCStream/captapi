"""LinkedIn company-posts offset cursor helpers."""

import pytest
from fastapi import HTTPException

from app.routers.linkedin import (
    _parse_company_posts_cursor,
    _slice_company_posts_page,
)


def test_parse_cursor_defaults_and_offsets():
    assert _parse_company_posts_cursor(None) == 0
    assert _parse_company_posts_cursor("") == 0
    assert _parse_company_posts_cursor("20") == 20


def test_parse_cursor_rejects_invalid():
    with pytest.raises(HTTPException) as exc:
        _parse_company_posts_cursor("abc")
    assert exc.value.status_code == 400
    with pytest.raises(HTTPException):
        _parse_company_posts_cursor("100")


def test_slice_first_page_has_more():
    posts = [{"id": str(i)} for i in range(21)]
    page = _slice_company_posts_page(posts, offset=0, limit=20)
    assert page["totalReturned"] == 20
    assert page["hasMore"] is True
    assert page["nextCursor"] == "20"
    assert page["posts"][0]["id"] == "0"
    assert page["posts"][-1]["id"] == "19"


def test_slice_second_page_ends():
    posts = [{"id": str(i)} for i in range(25)]
    page = _slice_company_posts_page(posts, offset=20, limit=20)
    assert page["totalReturned"] == 5
    assert page["hasMore"] is False
    assert page["nextCursor"] is None
    assert [p["id"] for p in page["posts"]] == ["20", "21", "22", "23", "24"]
