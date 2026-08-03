from __future__ import annotations

from app.routers.linkedin import (
    _is_masked_li_text,
    _map_li_experience,
    _map_li_similar,
    _merge_profile_sections,
    _normalize_profile,
    _profile_needs_enrichment,
)


def test_masked_asterisk_description_is_restricted() -> None:
    assert _is_masked_li_text("******* ** * ****** ******") is True
    assert _is_masked_li_text("Built the payments platform at Acme") is False
    rows = _map_li_experience(
        [
            {
                "title": "Engineer",
                "company_name": "Acme",
                "member": {"description": "******* ** * ****** ****** **********"},
            }
        ]
    )
    assert len(rows) == 1
    assert rows[0]["description"] is None
    assert rows[0]["restricted"] is True


def test_normalize_profile_experience_education_similar() -> None:
    out = _normalize_profile(
        {
            "basic_info": {
                "fullname": "Ada Lovelace",
                "public_identifier": "ada",
                "about": "Mathematician",
            },
            "experience": [
                {
                    "title": "Analyst",
                    "company_name": "Babbage Co",
                    "description": "Wrote algorithms",
                    "is_current": False,
                }
            ],
            "education": [{"school_name": "University of London", "degree": "BA"}],
            "peopleAlsoViewed": [
                {
                    "full_name": "Charles Babbage",
                    "public_identifier": "charles-babbage",
                    "headline": "Inventor",
                }
            ],
        }
    )
    assert out["experience"][0]["company"] == "Babbage Co"
    assert out["education"][0]["name"] == "University of London"
    assert out["similarProfiles"][0]["username"] == "charles-babbage"
    assert out["similarProfiles"][0]["url"].endswith("/in/charles-babbage")


def test_merge_keeps_native_fills_sections() -> None:
    base = _normalize_profile(
        {"basic_info": {"fullname": "Ada", "public_identifier": "ada", "follower_count": 10}}
    )
    rich = _normalize_profile(
        {
            "basic_info": {"fullname": "Ada", "public_identifier": "ada"},
            "experience": [{"title": "Engineer", "company_name": "X"}],
        }
    )
    assert _profile_needs_enrichment(base) is True
    merged = _merge_profile_sections(base, rich)
    assert merged["followers"] == 10
    assert merged["experience"][0]["title"] == "Engineer"
