"""Rumble transcript error shapes — never 'Video not found' for no captions."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.routers import rumble as r


def test_raise_no_captions_shape() -> None:
    with pytest.raises(HTTPException) as ei:
        r._raise_rumble_transcript_unavailable(
            code="no_captions",
            available=[],
            language=None,
        )
    assert ei.value.status_code == 404
    detail = ei.value.detail
    assert isinstance(detail, dict)
    assert detail["code"] == "no_captions"
    assert detail["availableLanguages"] == []
    assert "Video not found" not in str(detail)


def test_raise_language_not_available_shape() -> None:
    with pytest.raises(HTTPException) as ei:
        r._raise_rumble_transcript_unavailable(
            code="language_not_available",
            available=[{"code": "en-auto", "language": "English (auto)"}],
            language="fr",
        )
    detail = ei.value.detail
    assert isinstance(detail, dict)
    assert detail["code"] == "language_not_available"
    assert detail["availableLanguages"][0]["code"] == "en-auto"