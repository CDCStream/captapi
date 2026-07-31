"""LinkedIn profile/company must 404 on empty null shells."""

import pytest
from fastapi import HTTPException

from app.routers.linkedin import (
    _normalize_profile,
    _require_company,
    _require_person_profile,
)
from app.services.cached_runner import _looks_empty


def test_require_person_rejects_null_shell():
    shell = _normalize_profile({})
    assert shell["type"] == "person"
    assert shell["name"] is None
    with pytest.raises(HTTPException) as exc:
        _require_person_profile(shell)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Profile not found"


def test_require_person_accepts_named_profile():
    data = _require_person_profile(
        _normalize_profile({"basic_info": {"fullname": "Ada Lovelace", "public_identifier": "ada"}})
    )
    assert data["name"] == "Ada Lovelace"
    assert data["username"] == "ada"


def test_require_company_rejects_null_shell():
    with pytest.raises(HTTPException) as exc:
        _require_company({"platform": "linkedin", "type": "company", "name": None})
    assert exc.value.status_code == 404


def test_looks_empty_null_person_shell():
    assert _looks_empty(
        {
            "platform": "linkedin",
            "type": "person",
            "name": None,
            "username": None,
        }
    )
    assert not _looks_empty(
        {
            "platform": "linkedin",
            "type": "person",
            "name": "Ada",
            "username": "ada",
        }
    )
