"""LinkedIn endpoints: person profile, company page, post details.

Public data only, via config-driven rental actors. Field mappings are
defensive across actor versions.
"""

from __future__ import annotations

import math
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.services import linkedin_native
from app.utils.formatters import first_present, safe_int, safe_str
from app.utils.text_transcript import TIMING_NONE, count_words, paragraph_text_segments
from app.utils.url import (
    detect_url_platform,
    extract_linkedin_company,
    extract_linkedin_profile,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_PROFILE = 2
CREDIT_DETAILS = 1
CREDIT_NATIVE = linkedin_native.CREDIT_LINKEDIN_NATIVE
RATE = 0.8


def _scaled(limit: int, minimum: int = 2) -> int:
    if limit <= 0:
        return 0
    return max(minimum, math.ceil(limit * RATE))


def _reject_linkedin_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "linkedin":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "linkedin", example),
        )


def _require_linkedin_profile_url(url: str) -> str:
    slug = extract_linkedin_profile(url)
    if not slug:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "linkedin", "https://www.linkedin.com/in/username"),
        )
    return slug


def _require_linkedin_company_url(url: str) -> str:
    slug = extract_linkedin_company(url)
    if not slug:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "linkedin", "https://www.linkedin.com/company/company-name"),
        )
    return slug


def _first(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not items:
        raise HTTPException(status_code=404, detail="Not found on LinkedIn")
    return items[0]


def _require_person_profile(data: dict[str, Any]) -> dict[str, Any]:
    """Reject Apify/native shells that have no identifying fields."""
    if data.get("name") or data.get("username"):
        return data
    raise HTTPException(status_code=404, detail="Profile not found")


def _require_company(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("name"):
        return data
    raise HTTPException(status_code=404, detail="Company not found")


def _is_masked_li_text(value: str | None) -> bool:
    """True when LinkedIn guest-masked a string as asterisks (``*******``)."""
    s = (value or "").strip()
    if not s:
        return False
    letters = sum(1 for c in s if c.isalpha())
    stars = s.count("*")
    if stars >= 6 and letters == 0:
        return True
    if stars >= 8 and letters <= 2:
        return True
    return False


def _text_or_restricted(value: Any) -> tuple[str | None, bool]:
    """Return ``(text, restricted)``. Masked guest copy → ``(None, True)``."""
    text = safe_str(value)
    if text and _is_masked_li_text(text):
        return None, True
    return text, False


def _first_list(*candidates: Any) -> list[Any]:
    for raw in candidates:
        if isinstance(raw, list) and raw:
            return raw
    return []


def _map_li_experience(raw: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        company = item.get("company") if isinstance(item.get("company"), dict) else {}
        member = item.get("member") if isinstance(item.get("member"), dict) else {}
        desc, restricted = _text_or_restricted(
            item.get("description")
            or item.get("summary")
            or member.get("description")
            or member.get("summary")
        )
        row: dict[str, Any] = {
            "title": safe_str(item.get("title") or item.get("position") or item.get("name")),
            "company": safe_str(
                item.get("company_name")
                or item.get("companyName")
                or company.get("name")
                or item.get("company")
            ),
            "url": safe_str(item.get("company_url") or item.get("url") or company.get("url")),
            "location": safe_str(item.get("location") or item.get("company_location")),
            "description": desc,
            "startDate": safe_str(item.get("start_date") or item.get("startDate")),
            "endDate": safe_str(item.get("end_date") or item.get("endDate")),
            "isCurrent": item.get("is_current")
            if item.get("is_current") is not None
            else item.get("isCurrent"),
        }
        if restricted:
            row["restricted"] = True
            row["description"] = None  # keep key — null ≠ ******* spam
        out.append({k: v for k, v in row.items() if v is not None or k == "description"})
    return [x for x in out if x.get("title") or x.get("company")]


def _map_li_education(raw: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        school = item.get("school") if isinstance(item.get("school"), dict) else {}
        desc, restricted = _text_or_restricted(
            item.get("description") or item.get("activities") or item.get("notes")
        )
        row: dict[str, Any] = {
            "name": safe_str(
                item.get("school_name")
                or item.get("schoolName")
                or school.get("name")
                or item.get("name")
            ),
            "url": safe_str(item.get("school_url") or item.get("url") or school.get("url")),
            "degree": safe_str(item.get("degree") or item.get("degree_name")),
            "field": safe_str(
                item.get("field_of_study") or item.get("fieldOfStudy") or item.get("field")
            ),
            "description": desc,
            "startDate": safe_str(item.get("start_date") or item.get("startDate")),
            "endDate": safe_str(item.get("end_date") or item.get("endDate")),
        }
        if restricted:
            row["restricted"] = True
        out.append({k: v for k, v in row.items() if v is not None})
    return [x for x in out if x.get("name")]


def _map_li_similar(raw: Any) -> list[dict[str, Any]]:
    """People-also-viewed / similar profiles — LinkedIn discovery graph."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        url = safe_str(
            item.get("url")
            or item.get("profile_url")
            or item.get("profileUrl")
            or item.get("linkedinUrl")
        )
        username = safe_str(
            item.get("public_identifier")
            or item.get("publicIdentifier")
            or item.get("username")
            or item.get("vanityName")
        )
        if not username and url and "/in/" in url:
            username = url.rstrip("/").split("/in/")[-1].split("?")[0] or None
        name = safe_str(item.get("full_name") or item.get("fullName") or item.get("name"))
        key = username or url or name
        if not key or key in seen:
            continue
        seen.add(key)
        row = {
            "name": name,
            "username": username,
            "url": url or (f"https://www.linkedin.com/in/{username}" if username else None),
            "headline": safe_str(item.get("headline") or item.get("occupation") or item.get("title")),
            "location": safe_str(
                item.get("location")
                if not isinstance(item.get("location"), dict)
                else (
                    item["location"].get("full")
                    or item["location"].get("city")
                    or item["location"].get("country")
                )
            ),
            "profileImage": safe_str(
                item.get("profile_picture_url")
                or item.get("profilePicture")
                or item.get("avatar")
                or item.get("photoUrl")
            ),
        }
        out.append({k: v for k, v in row.items() if v is not None})
    return out


def _map_li_named_section(
    raw: Any,
    *,
    name_keys: tuple[str, ...],
    extra_keys: tuple[tuple[str, tuple[str, ...]], ...] = (),
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        name = None
        for key in name_keys:
            name = safe_str(item.get(key))
            if name:
                break
        desc, restricted = _text_or_restricted(
            item.get("description") or item.get("summary") or item.get("text")
        )
        row: dict[str, Any] = {"name": name, "description": desc}
        for out_key, src_keys in extra_keys:
            for sk in src_keys:
                val = item.get(sk)
                if isinstance(val, (str, int, float, bool)):
                    row[out_key] = val if not isinstance(val, str) else safe_str(val)
                    break
                if isinstance(val, dict) and val.get("name"):
                    row[out_key] = safe_str(val.get("name"))
                    break
        if restricted:
            row["restricted"] = True
        row = {k: v for k, v in row.items() if v is not None}
        if row.get("name") or row.get("description"):
            out.append(row)
    return out


def _map_li_recommendations(raw: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        text, restricted = _text_or_restricted(
            item.get("text")
            or item.get("description")
            or item.get("recommendation")
            or item.get("recommendation_text")
        )
        recommender = (
            item.get("recommender")
            if isinstance(item.get("recommender"), dict)
            else (
                item.get("author") if isinstance(item.get("author"), dict) else {}
            )
        )
        row: dict[str, Any] = {
            "text": text,
            "name": safe_str(
                item.get("name")
                or item.get("recommender_name")
                or recommender.get("full_name")
                or recommender.get("name")
            ),
            "headline": safe_str(
                item.get("headline")
                or recommender.get("headline")
                or item.get("recommender_headline")
            ),
            "url": safe_str(
                item.get("url")
                or recommender.get("url")
                or recommender.get("profile_url")
            ),
            "relationship": safe_str(
                item.get("relationship")
                or item.get("relationship_type")
                or item.get("context")
            ),
        }
        if restricted:
            row["restricted"] = True
        row = {k: v for k, v in row.items() if v is not None}
        if row.get("text") or row.get("name"):
            out.append(row)
    return out


def _section_payload(p: dict[str, Any], info: dict[str, Any], *keys: str) -> list[Any]:
    cands: list[Any] = []
    for key in keys:
        cands.extend([p.get(key), info.get(key)])
        nested = p.get("sections") if isinstance(p.get("sections"), dict) else {}
        cands.append(nested.get(key))
    return _first_list(*cands)


def _normalize_profile(p: dict[str, Any]) -> dict[str, Any]:
    # apimaestro/linkedin-profile-detail nests everything under basic_info.
    info = p.get("basic_info") if isinstance(p.get("basic_info"), dict) else p
    location = info.get("location")
    if isinstance(location, dict):
        location = location.get("full") or location.get("city") or location.get("country")
    about_raw = safe_str(info.get("about") or p.get("summary") or p.get("about"))
    # Guard Apify/legacy paths that still echo SEO meta into about.
    # Never return the meta description (or its leading mash) as About.
    seo_about = bool(about_raw and linkedin_native._is_seo_description(about_raw))
    about_restricted = False
    if seo_about:
        about = None
    else:
        about, about_restricted = _text_or_restricted(about_raw)
    connections = safe_int(
        info.get("connection_count") or p.get("connections") or p.get("connectionsCount")
    )
    # Drop connections that match SEO "N connections on LinkedIn" privacy filler.
    # Empty / omitted connections is a LinkedIn logged-out platform limit — not a
    # Captapi bug (SC hits the same wall).
    seo_conn = linkedin_native._seo_connections_count(about_raw) if seo_about else None
    if seo_conn is not None and connections == seo_conn:
        connections = None
    current_company = safe_str(
        info.get("current_company") or p.get("companyName") or p.get("company")
    )
    if seo_about and about_raw and current_company:
        # Drop company only when it was clearly scraped from SEO "Experience: X".
        exp_m = re.search(r"Experience:\s*([^·\n|]{2,80})", about_raw, re.I)
        if exp_m and safe_str(exp_m.group(1).strip()) == current_company:
            current_company = None
    # Public HTML never exposes a reliable verified flag — omit the field.
    out: dict[str, Any] = {
        "platform": "linkedin",
        "type": "person",
        "url": safe_str(
            info.get("profile_url") or p.get("url") or p.get("profileUrl") or p.get("linkedinUrl")
        ),
        "username": safe_str(
            info.get("public_identifier") or p.get("publicIdentifier") or p.get("username")
        ),
        "name": safe_str(
            info.get("fullname")
            or p.get("fullName")
            or p.get("name")
            or f"{info.get('first_name', '')} {info.get('last_name', '')}".strip()
        ),
        "headline": safe_str(info.get("headline") or p.get("occupation")),
        "location": safe_str(location or p.get("locationName")),
        "about": about,
        "followers": safe_int(
            info.get("follower_count") or p.get("followers") or p.get("followerCount")
        ),
        "connections": connections,
        "profileImage": safe_str(
            info.get("profile_picture_url")
            or p.get("profilePicture")
            or p.get("photoUrl")
            or p.get("avatar")
        ),
        "currentCompany": current_company,
    }
    if about_restricted:
        out["aboutRestricted"] = True

    experience = _map_li_experience(
        _section_payload(p, info, "experience", "experiences", "work_experience")
    )
    education = _map_li_education(
        _section_payload(p, info, "education", "educations")
    )
    similar = _map_li_similar(
        _section_payload(
            p,
            info,
            "similarProfiles",
            "similar_profiles",
            "peopleAlsoViewed",
            "people_also_viewed",
            "related_profiles",
            "relatedProfiles",
        )
    )
    projects = _map_li_named_section(
        _section_payload(p, info, "projects", "project"),
        name_keys=("title", "name", "project_name"),
        extra_keys=(
            ("url", ("url", "link")),
            ("startDate", ("start_date", "startDate")),
            ("endDate", ("end_date", "endDate")),
        ),
    )
    publications = _map_li_named_section(
        _section_payload(p, info, "publications", "publication"),
        name_keys=("title", "name"),
        extra_keys=(
            ("url", ("url", "link")),
            ("publisher", ("publisher", "publisher_name")),
            ("date", ("date", "published_on", "publishedAt")),
        ),
    )
    articles = _map_li_named_section(
        _section_payload(p, info, "articles", "article", "posts", "recentPosts"),
        name_keys=("title", "name", "headline"),
        extra_keys=(
            ("url", ("url", "link", "article_url")),
            ("publishedAt", ("published_at", "publishedAt", "date")),
        ),
    )
    activity = _map_li_named_section(
        _section_payload(p, info, "activity", "activities", "recent_activity"),
        name_keys=("title", "name", "text"),
        extra_keys=(
            ("url", ("url", "link")),
            ("publishedAt", ("published_at", "publishedAt", "date")),
        ),
    )
    recommendations = _map_li_recommendations(
        _section_payload(p, info, "recommendations", "recommendation")
    )
    certifications = _map_li_named_section(
        _section_payload(p, info, "certifications", "certs", "licenses"),
        name_keys=("name", "title", "authority"),
        extra_keys=(
            ("authority", ("authority", "issuer", "company")),
            ("url", ("url", "link")),
            ("issuedAt", ("issued_at", "issue_date", "startDate")),
        ),
    )
    languages = _map_li_named_section(
        _section_payload(p, info, "languages", "language"),
        name_keys=("name", "language", "title"),
        extra_keys=(("proficiency", ("proficiency", "level", "fluency")),),
    )

    for key, value in (
        ("experience", experience),
        ("education", education),
        ("similarProfiles", similar),
        ("projects", projects),
        ("publications", publications),
        ("articles", articles),
        ("activity", activity),
        ("recommendations", recommendations),
        ("certifications", certifications),
        ("languages", languages),
    ):
        if value:
            out[key] = value
    return out


_PROFILE_SECTION_KEYS = (
    "experience",
    "education",
    "similarProfiles",
    "projects",
    "publications",
    "articles",
    "activity",
    "recommendations",
    "certifications",
    "languages",
)


def _merge_profile_sections(
    base: dict[str, Any], rich: dict[str, Any]
) -> dict[str, Any]:
    """Keep native identity fields; fill missing B2B sections from Apify."""
    out = dict(base)
    for key in _PROFILE_SECTION_KEYS:
        if not out.get(key) and rich.get(key):
            out[key] = rich[key]
    if not out.get("about") and rich.get("about"):
        out["about"] = rich["about"]
        if rich.get("aboutRestricted"):
            out["aboutRestricted"] = True
    for key in ("followers", "connections", "headline", "location", "currentCompany", "profileImage"):
        if out.get(key) is None and rich.get(key) is not None:
            out[key] = rich[key]
    return out


def _profile_needs_enrichment(profile: dict[str, Any] | None) -> bool:
    if not profile:
        return True
    return not profile.get("experience") and not profile.get("education")


def _company_size_label(info: dict[str, Any], stats: dict[str, Any]) -> str | None:
    """LinkedIn size band, e.g. ``10,001+ employees``."""
    labeled = safe_str(info.get("company_size_label") or info.get("companySize") or stats.get("size"))
    if labeled:
        return labeled
    rng = stats.get("employee_count_range") if isinstance(stats.get("employee_count_range"), dict) else {}
    start = safe_int(rng.get("start"))
    end = safe_int(rng.get("end"))
    if start is not None and end is not None:
        return f"{start:,}-{end:,} employees"
    if start is not None:
        return f"{start:,}+ employees"
    return None


def _map_company_funding(raw: Any) -> dict[str, Any] | None:
    """Normalize funding blob; return None when LinkedIn/Apify expose nothing useful."""
    if not isinstance(raw, dict) or not raw:
        return None
    latest = raw.get("latest_round") if isinstance(raw.get("latest_round"), dict) else {}
    last_round_in = raw.get("lastRound") if isinstance(raw.get("lastRound"), dict) else latest
    investors_in = raw.get("investors") if isinstance(raw.get("investors"), list) else []
    investors: list[dict[str, Any]] = []
    for inv in investors_in:
        if not isinstance(inv, dict):
            continue
        name = safe_str(inv.get("name"))
        if not name:
            continue
        investors.append(
            {
                "name": name,
                "crunchbaseUrl": safe_str(inv.get("crunchbaseUrl") or inv.get("crunchbase_url") or inv.get("url")),
            }
        )
    last_round = None
    lr_type = safe_str(last_round_in.get("type"))
    lr_date = safe_str(last_round_in.get("date"))
    lr_amount = safe_str(last_round_in.get("amount"))
    if lr_type or lr_date or lr_amount:
        last_round = {"type": lr_type, "date": lr_date, "amount": lr_amount}
    rounds = safe_int(
        raw.get("numberOfRounds") or raw.get("total_rounds") or raw.get("totalRounds")
    )
    crunchbase = safe_str(raw.get("crunchbase_url") or raw.get("crunchbaseUrl"))
    if rounds is None and not last_round and not investors and not crunchbase:
        return None
    return {
        "numberOfRounds": rounds,
        "lastRound": last_round,
        "investors": investors,
        "crunchbaseUrl": crunchbase,
    }


def _map_company_similar(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw:
        if isinstance(item, str):
            # Apify often ships bare company URN/ids — skip unresolvable ids.
            if item.isdigit() or item.startswith("urn:"):
                continue
            link = (
                item
                if item.startswith("http")
                else f"https://www.linkedin.com/company/{item.strip('/')}"
            )
            slug = item.rstrip("/").split("/")[-1]
            if slug.lower() in seen:
                continue
            seen.add(slug.lower())
            out.append({"name": slug.replace("-", " ").title(), "link": link, "image": None})
            continue
        if not isinstance(item, dict):
            continue
        link = safe_str(item.get("link") or item.get("url") or item.get("linkedin_url"))
        name = safe_str(item.get("name") or item.get("companyName"))
        if not link and not name:
            continue
        key = (link or name or "").lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "name": name,
                "link": link,
                "image": safe_str(item.get("image") or item.get("logo") or item.get("logoUrl")),
            }
        )
    return out


def _map_company_employees(raw: Any) -> list[dict[str, Any]]:
    """Featured employees (name/title/link) when upstream exposes them."""
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = safe_str(item.get("name") or item.get("fullName"))
        link = safe_str(item.get("link") or item.get("url") or item.get("profileUrl"))
        if not name and not link:
            continue
        out.append(
            {
                "name": name,
                "title": safe_str(item.get("title") or item.get("headline") or item.get("occupation")),
                "link": link,
            }
        )
    return out


def _normalize_company(c: dict[str, Any]) -> dict[str, Any]:
    # apimaestro/linkedin-company-detail splits data across basic_info /
    # stats / media / locations. Native fetch_company uses the same shape.
    info = c.get("basic_info") if isinstance(c.get("basic_info"), dict) else c
    stats = c.get("stats") if isinstance(c.get("stats"), dict) else {}
    media = c.get("media") if isinstance(c.get("media"), dict) else {}
    hq = (
        ((c.get("locations") or {}).get("headquarters") or {})
        if isinstance(c.get("locations"), dict)
        else {}
    )
    if not isinstance(hq, dict):
        hq = {}
    industries = info.get("industries")
    industry = industries[0] if isinstance(industries, list) and industries else info.get("industry")
    loc_city = safe_str(hq.get("city"))
    loc_state = safe_str(hq.get("state") or hq.get("geographicArea"))
    loc_country = safe_str(hq.get("country"))
    # Native sometimes packs "Ottawa, ON, CA" into city alone — split lightly.
    if loc_city and not loc_state and "," in loc_city:
        parts = [p.strip() for p in loc_city.split(",") if p.strip()]
        if parts:
            loc_city = safe_str(parts[0])
        if len(parts) >= 2:
            loc_state = safe_str(parts[1])
        if len(parts) >= 3:
            loc_country = safe_str(parts[2])
    hq_text = ", ".join(x for x in [loc_city, loc_state, loc_country] if x) or None
    founded_info = info.get("founded_info") if isinstance(info.get("founded_info"), dict) else {}
    founded = safe_int(
        founded_info.get("year")
        or info.get("founded")
        or c.get("founded")
        or c.get("foundedYear")
    )
    specialties_raw = info.get("specialties") or c.get("specialties") or []
    if isinstance(specialties_raw, str):
        specialties = linkedin_native._specialties_list(specialties_raw)
    elif isinstance(specialties_raw, list):
        specialties = [s for s in (safe_str(x) for x in specialties_raw) if s]
    else:
        specialties = []
    similar = _map_company_similar(
        c.get("similar_pages")
        or c.get("similarPages")
        or c.get("similar_companies")
        or c.get("similarCompanies")
    )
    employees_people = _map_company_employees(
        c.get("employees_sample")
        or c.get("employees")
        or c.get("featured_employees")
        or c.get("employeeHighlights")
    )
    # If `employees` was a bare count (legacy actor), don't treat it as people.
    if employees_people and all(e.get("name") is None and e.get("link") is None for e in employees_people):
        employees_people = []
    employee_count = safe_int(
        stats.get("employee_count")
        or c.get("employeeCount")
        or c.get("staffCount")
        or (c.get("employees") if not isinstance(c.get("employees"), list) else None)
    )
    funding = _map_company_funding(c.get("funding") or info.get("funding"))
    slogan = safe_str(c.get("tagline") or c.get("slogan") or info.get("tagline") or info.get("slogan"))
    organization_type = safe_str(
        info.get("organization_type")
        or info.get("organizationType")
        or c.get("organizationType")
        or c.get("companyType")
    )
    size = _company_size_label(info, stats)
    # Core identity; additive B2B keys always present so clients get one shape.
    out: dict[str, Any] = {
        "platform": "linkedin",
        "type": "company",
        "url": safe_str(info.get("linkedin_url") or c.get("url") or c.get("linkedinUrl")),
        "name": safe_str(info.get("name") or c.get("companyName")),
        "industry": safe_str(industry),
        "description": safe_str(info.get("description") or c.get("about")),
        "website": safe_str(info.get("website") or c.get("websiteUrl")),
        "followers": safe_int(stats.get("follower_count") or c.get("followers") or c.get("followerCount")),
        # employeeCount is the headcount; employees[] is featured people (SC shape).
        "employeeCount": employee_count,
        "employees": employees_people,
        # BC: legacy numeric `employees` readers should migrate to employeeCount.
        "size": size,
        "founded": founded,
        "organizationType": organization_type,
        "specialties": specialties,
        "headquarters": safe_str(hq_text or c.get("headquarters") or c.get("location")),
        "location": {
            "city": loc_city,
            "state": loc_state,
            "country": loc_country,
        },
        "slogan": slogan,
        "coverImage": safe_str(
            media.get("cover_url") or c.get("coverImage") or c.get("cover_url") or c.get("backgroundUrl")
        ),
        "logo": safe_str(media.get("logo_url") or c.get("logo") or c.get("logoUrl")),
        "funding": funding,
        "similarPages": similar,
    }
    return out


def _company_needs_enrichment(company: dict[str, Any] | None) -> bool:
    if not company:
        return True
    # Native guest HTML already covers specialties/similar/size/founded for many
    # pages; Apify still fills slogan/cover and (rarely) funding.
    return not (
        company.get("slogan")
        and company.get("coverImage")
        and company.get("organizationType")
        and company.get("specialties")
    )


def _merge_company(base: dict[str, Any], rich: dict[str, Any]) -> dict[str, Any]:
    """Prefer native identity; fill missing B2B fields from Apify."""
    out = dict(base)
    for key in (
        "industry",
        "description",
        "website",
        "followers",
        "employeeCount",
        "size",
        "founded",
        "organizationType",
        "headquarters",
        "slogan",
        "coverImage",
        "logo",
        "funding",
    ):
        if out.get(key) in (None, "", []) and rich.get(key) not in (None, "", []):
            out[key] = rich[key]
    if not out.get("specialties") and rich.get("specialties"):
        out["specialties"] = rich["specialties"]
    if not out.get("similarPages") and rich.get("similarPages"):
        out["similarPages"] = rich["similarPages"]
    if not out.get("employees") and rich.get("employees"):
        out["employees"] = rich["employees"]
    loc = out.get("location") if isinstance(out.get("location"), dict) else {}
    rich_loc = rich.get("location") if isinstance(rich.get("location"), dict) else {}
    out["location"] = {
        "city": loc.get("city") or rich_loc.get("city"),
        "state": loc.get("state") or rich_loc.get("state"),
        "country": loc.get("country") or rich_loc.get("country"),
    }
    if not out.get("headquarters"):
        hq = ", ".join(
            x for x in [out["location"].get("city"), out["location"].get("state"), out["location"].get("country")] if x
        ) or None
        out["headquarters"] = hq
    return out


def _normalize_post(p: dict[str, Any]) -> dict[str, Any]:
    post = p.get("post") if isinstance(p.get("post"), dict) else p
    author = p.get("author") or post.get("author") or {}
    if not isinstance(author, dict):
        author = {}
    created = post.get("created_at") if isinstance(post.get("created_at"), dict) else {}
    # apimaestro search rows: posted_at {date, timestamp}; automation-lab
    # company rows: flat datePublished.
    posted_at = p.get("posted_at") if isinstance(p.get("posted_at"), dict) else {}
    stats = p.get("stats") if isinstance(p.get("stats"), dict) else p
    # Do NOT fall back to top-level `headline` — on company JSON-LD rows that
    # field is the post title (e.g. "June"), not the author's job title.
    author_headline = safe_str(
        author.get("headline")
        or author.get("occupation")
        or p.get("authorHeadline")
        or p.get("author_headline")
    )
    # Guest HTML / SEO often stuffs "N followers" into headline — not a job title.
    if author_headline and "follower" in author_headline.lower():
        author_headline = None
    # Always key engagement — null when LinkedIn omits a metric (never invent 0).
    # Use first_present — `or` drops real zeros (shares/comments often 0).
    engagement = {
        "likes": safe_int(
            first_present(
                stats.get("likes"),
                stats.get("total_reactions"),
                stats.get("reactions"),
                p.get("numLikes"),
                p.get("num_likes"),
                p.get("likes"),
                p.get("reactionsCount"),
                p.get("reaction_count"),
                p.get("totalReactionCount"),
            )
        ),
        "comments": safe_int(
            first_present(
                stats.get("comments"),
                p.get("numComments"),
                p.get("num_comments"),
                p.get("comments"),
                p.get("commentsCount"),
                p.get("comment_count"),
            )
        ),
        "reposts": safe_int(
            first_present(
                stats.get("shares"),
                stats.get("reposts"),
                p.get("reposts"),
                p.get("numShares"),
                p.get("num_shares"),
                p.get("repostsCount"),
                p.get("repost_count"),
                p.get("share_count"),
            )
        ),
    }
    author_out: dict[str, Any] = {
        "name": safe_str(author.get("name") or p.get("authorName") or p.get("companyName")),
        "url": linkedin_native.canonicalize_linkedin_url(
            author.get("url") or author.get("profile_url") or p.get("authorUrl") or p.get("companyUrl")
        ),
    }
    # Public post HTML rarely exposes author job title — omit when unknown.
    if author_headline:
        author_out["headline"] = author_headline
    return {
        "platform": "linkedin",
        "type": "post",
        "url": safe_str(post.get("url") or p.get("url") or p.get("postUrl") or p.get("post_url")),
        "text": safe_str(post.get("text") or p.get("text") or p.get("content") or p.get("commentary")),
        "publishedAt": safe_str(
            created.get("date")
            or posted_at.get("date")
            or post.get("postedAt")
            or post.get("publishedAt")
            or p.get("datePublished")
            or p.get("date")
        ),
        "author": author_out,
        "engagement": engagement,
    }


_LI_ACTIVITY_RE = re.compile(r"activity[:-](\d{10,25})")


def _normalize_post_list_item(p: dict[str, Any], *, include_media: bool = True) -> dict[str, Any]:
    base = _normalize_post(p)
    post_id = safe_str(p.get("id") or p.get("urn") or p.get("post_id") or p.get("activity_id"))
    if not post_id:
        m = _LI_ACTIVITY_RE.search(base.get("url") or "")
        post_id = m.group(1) if m else None
    base["id"] = post_id
    if include_media:
        media = p.get("media") or p.get("images") or p.get("videos") or []
        if isinstance(media, dict):
            media = [media]
        base["media"] = media
    return base


def _normalize_company_post(p: dict[str, Any]) -> dict[str, Any]:
    """Normalize company-post rows from native / Apify actors into the shared shape."""
    row = dict(p) if isinstance(p, dict) else {}
    # vulnv/linkedin-company-posts uses post_text / date_posted / title.
    if not (row.get("text") or row.get("content") or row.get("commentary")):
        alt = row.get("post_text") or row.get("headline") or row.get("title")
        if alt:
            row["text"] = alt
    if not row.get("url"):
        row["url"] = row.get("postUrl") or row.get("post_url")
    if not row.get("id"):
        row["id"] = row.get("post_id") or row.get("urn") or row.get("activity_id")
    if not (
        row.get("publishedAt")
        or row.get("datePublished")
        or row.get("date")
        or (isinstance(row.get("postedAt"), dict) and row["postedAt"].get("date"))
    ):
        if row.get("date_posted") or row.get("published_at"):
            row["publishedAt"] = row.get("date_posted") or row.get("published_at")
    base = _normalize_post_list_item(row, include_media=False)
    author = base.get("author")
    if isinstance(author, dict):
        author.pop("headline", None)
        if not author.get("url"):
            author["url"] = safe_str(
                row.get("use_url") or row.get("author_company_url") or row.get("companyLinkedInUrl")
            )
        if not author.get("name"):
            author["name"] = safe_str(
                row.get("author_name") or row.get("companyName") or row.get("user_id")
            )
    return base


@router.get(
    "/profile",
    summary="LinkedIn person profile — experience, education, similarProfiles",
)
async def linkedin_profile(
    url: str = Query(..., description="LinkedIn profile URL, e.g. https://linkedin.com/in/slug"),
    cache: bool = Query(
        False,
        description="Set true to use the default cache TTL. Default false — always fetch fresh.",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    slug = _require_linkedin_profile_url(url)
    settings = get_settings()
    profile_url = f"https://www.linkedin.com/in/{slug}"

    async def _apify_profile(actor: str) -> dict[str, Any] | None:
        try:
            items = await get_apify().run_actor_sync(
                actor,
                {
                    "username": slug,
                    "url": profile_url,
                    "includeEmail": False,
                    "usernames": [slug],
                },
                max_items=1,
            )
        except Exception:  # noqa: BLE001
            return None
        if not items:
            return None
        return _normalize_profile(items[0] if isinstance(items[0], dict) else {})

    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/profile",
        platform="linkedin",
        resource_url=profile_url,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_raw = await linkedin_native.fetch_profile(slug)
            base = _normalize_profile(native_raw) if native_raw else None
            used_apify = False

            # Native HTML rarely exposes experience/education — enrich from Apify
            # instead of short-circuiting on a thin shell (B2B core fields).
            if _profile_needs_enrichment(base):
                rich = await _apify_profile(settings.APIFY_ACTOR_LINKEDIN_PROFILE)
                if rich and (rich.get("name") or rich.get("username")):
                    used_apify = True
                    base = _merge_profile_sections(base, rich) if base else rich

            if _profile_needs_enrichment(base):
                full = await _apify_profile(settings.APIFY_ACTOR_LINKEDIN_PROFILE_FULL)
                if full and (full.get("name") or full.get("username")):
                    used_apify = True
                    base = _merge_profile_sections(base, full) if base else full

            if not base:
                raise HTTPException(status_code=404, detail="Profile not found")

            if used_apify:
                ctx["source"] = "apify" if not native_raw else "hybrid"
                ctx["credits_override"] = CREDIT_PROFILE
            else:
                ctx["source"] = "direct"
            return _require_person_profile(base)

        data = await cached_or_run(
            endpoint="linkedin.profile",
            params={"slug": slug, "v": 7},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/company", summary="LinkedIn company page — funding, similarPages, specialties")
async def linkedin_company(
    url: str = Query(..., description="LinkedIn company URL, e.g. https://linkedin.com/company/slug"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    slug = _require_linkedin_company_url(url)
    settings = get_settings()
    company_url = f"https://www.linkedin.com/company/{slug}"

    async def _apify_company() -> dict[str, Any] | None:
        # apimaestro/linkedin-company-detail requires identifier: string[].
        # Wrong shapes silently scrape a default company (observed: YouTube).
        try:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_COMPANY,
                {"identifier": [slug]},
                max_items=1,
            )
        except Exception:  # noqa: BLE001
            return None
        if not items or not isinstance(items[0], dict):
            return None
        item = items[0]
        # Guard against actor default-company bleed.
        input_id = safe_str(item.get("input_identifier") or "").lower()
        uni = safe_str(((item.get("basic_info") or {}) if isinstance(item.get("basic_info"), dict) else {}).get("universal_name"))
        if input_id and input_id not in {slug.lower(), company_url.lower(), f"{company_url.lower()}/"}:
            if uni and uni.lower() != slug.lower():
                return None
        return _normalize_company(item)

    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/company",
        platform="linkedin",
        resource_url=company_url,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_raw = await linkedin_native.fetch_company(slug)
            base = _normalize_company(native_raw) if native_raw else None
            used_apify = False

            if _company_needs_enrichment(base):
                rich = await _apify_company()
                if rich and rich.get("name"):
                    used_apify = True
                    base = _merge_company(base, rich) if base else rich

            if not base:
                raise HTTPException(status_code=404, detail="Company not found")

            if used_apify:
                ctx["source"] = "apify" if not native_raw else "hybrid"
                ctx["credits_override"] = CREDIT_PROFILE
            else:
                ctx["source"] = "direct"
            return _require_company(base)

        data = await cached_or_run(
            endpoint="linkedin.company",
            params={"slug": slug, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/post-details", summary="LinkedIn post metadata + engagement")
async def linkedin_post_details(
    url: str = Query(..., description="LinkedIn post/activity URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_linkedin_platform_mismatch(url, "https://www.linkedin.com/posts/activity-123456789")
    if "linkedin.com" not in (url or ""):
        raise HTTPException(status_code=400, detail="Invalid LinkedIn post URL. Pass a LinkedIn URL like https://www.linkedin.com/posts/activity-123456789.")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/post-details",
        platform="linkedin",
        resource_url=url,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await linkedin_native.fetch_post(url)
            if native:
                ctx["source"] = "direct"
                return _normalize_post(native)

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_POST,
                {"post_urls": [url]},
                max_items=1,
            )
            ctx["source"] = "apify"
            ctx["credits_override"] = CREDIT_DETAILS
            return _normalize_post(_first(items))

        data = await cached_or_run(
            endpoint="linkedin.post-details",
            params={"url": url, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


_POST_VANITY_RE = re.compile(
    r"linkedin\.com/posts/([A-Za-z0-9%.-]+?)(?:_|-activity|-ugcPost)",
    re.I,
)


def _author_url_from_post_url(post_url: str | None) -> str | None:
    """Best-effort /in/{vanity} from personal ugcPost URLs when author.url is missing.

    Skips activity/company posts — vanity there is often a company slug, not /in/.
    """
    if not post_url or "ugcPost-" not in post_url:
        return None
    match = _POST_VANITY_RE.search(post_url)
    if not match:
        return None
    vanity = match.group(1).strip()
    if not vanity or vanity.lower() in {"feed", "news"}:
        return None
    return f"https://www.linkedin.com/in/{vanity}"


@router.get("/post-transcript", summary="LinkedIn post transcript / text extraction")
async def linkedin_post_transcript(
    url: str = Query(..., description="LinkedIn post/activity URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_linkedin_platform_mismatch(url, "https://www.linkedin.com/posts/activity-123456789")
    if "linkedin.com" not in (url or ""):
        raise HTTPException(status_code=400, detail="Invalid LinkedIn post URL. Pass a LinkedIn URL like https://www.linkedin.com/posts/activity-123456789.")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/post-transcript",
        platform="linkedin",
        resource_url=url,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await linkedin_native.fetch_post(url)
            if native:
                post = _normalize_post(native)
                ctx["source"] = "direct"
            else:
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_LINKEDIN_POST,
                    {"post_urls": [url]},
                    max_items=1,
                )
                post = _normalize_post(_first(items))
                ctx["source"] = "apify"
                ctx["credits_override"] = CREDIT_DETAILS
            text = linkedin_native.strip_comments_on_linkedin_suffix(post.get("text") or "") or ""
            if not text.strip():
                raise HTTPException(status_code=422, detail="No transcript text available for this LinkedIn post")
            # Text-only: omit start/duration/timestamp (timingSource is the discriminator).
            transcript, segments, read_secs = paragraph_text_segments(text)
            author = post.get("author") if isinstance(post.get("author"), dict) else {}
            author_out = dict(author) if author else {}
            if author_out.get("url"):
                author_out["url"] = linkedin_native.canonicalize_linkedin_url(author_out.get("url"))
            if not author_out.get("url"):
                derived = _author_url_from_post_url(post.get("url") or url)
                if derived:
                    author_out["url"] = derived
            # headline: only when LinkedIn/Apify expose a real job title — omit when unknown
            # (never invent from follower counts). Missing ≠ regression for guest ugcPost HTML.
            return {
                "platform": "linkedin",
                "url": post.get("url") or url,
                "transcript": transcript,
                # Text-only transcript — LinkedIn does not expose a speech
                # language. Key is always present (null) so clients can join
                # the same schema as Whisper transcript endpoints.
                "language": None,
                "timingSource": TIMING_NONE,
                "estimatedReadSeconds": read_secs,
                "transcriptSegments": segments,
                "wordCount": count_words(transcript),
                "segments": len(segments),
                "author": author_out or None,
                "publishedAt": post.get("publishedAt"),
            }

        data = await cached_or_run(
            endpoint="linkedin.post-transcript",
            params={"url": url, "v": 9},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


_LI_COMPANY_POSTS_MAX = 100
_LI_OFFSET_CURSOR_RE = re.compile(r"^\d{1,4}$")


def _parse_company_posts_cursor(cursor: str | None) -> int:
    if cursor is None or cursor == "":
        return 0
    if not _LI_OFFSET_CURSOR_RE.match(cursor):
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    offset = int(cursor)
    if offset >= _LI_COMPANY_POSTS_MAX:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    return offset


def _slice_company_posts_page(
    posts: list[dict[str, Any]], *, offset: int, limit: int
) -> dict[str, Any]:
    """Offset-page a fetched batch; nextCursor is the next offset string."""
    page = posts[offset : offset + limit]
    has_more = len(posts) > offset + limit
    return {
        "totalReturned": len(page),
        "posts": page,
        "nextCursor": str(offset + limit) if has_more else None,
        "hasMore": has_more,
    }


def _company_post_row_key(row: dict[str, Any]) -> str | None:
    """Stable id for merging native + Apify company-post rows."""
    if not isinstance(row, dict):
        return None
    for key in ("url", "postUrl", "post_url"):
        val = row.get(key)
        if val:
            m = _LI_ACTIVITY_RE.search(str(val))
            return m.group(1) if m else str(val)
    for key in ("id", "urn", "activity_id", "post_id"):
        if row.get(key) is not None:
            return str(row[key])
    basic = row.get("basic_info") if isinstance(row.get("basic_info"), dict) else None
    if basic and basic.get("url"):
        m = _LI_ACTIVITY_RE.search(str(basic["url"]))
        return m.group(1) if m else str(basic["url"])
    text = row.get("text") or row.get("content") or row.get("commentary")
    return str(text)[:120] if text else None


def _merge_company_post_rows(*batches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for batch in batches:
        for row in batch or []:
            key = _company_post_row_key(row)
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(row)
    return out


@router.get("/company-posts", summary="LinkedIn company posts")
async def linkedin_company_posts(
    url: str = Query(..., description="LinkedIn company URL, e.g. https://linkedin.com/company/slug"),
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the nextCursor "
            "value returned in the previous response (numeric offset, e.g. 20). "
            "A null nextCursor means the end of the list (max 100 posts)."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    slug = _require_linkedin_company_url(url)
    settings = get_settings()
    company_url = f"https://www.linkedin.com/company/{slug}"
    offset = _parse_company_posts_cursor(cursor)
    # +1 sentinel so we know whether another page exists without over-fetching.
    need = min(_LI_COMPANY_POSTS_MAX, offset + limit + 1)
    # Fetch a stable batch large enough for several cursor pages.
    batch_target = min(_LI_COMPANY_POSTS_MAX, max(need, 40))
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/company-posts",
        platform="linkedin",
        resource_url=company_url,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _fetch_batch() -> dict[str, Any]:
            # Native covers homepage embeds (~10); Apify/SERP extend for cursor depth.
            native = await linkedin_native.fetch_company_posts(slug, limit=batch_target)
            collected: list[dict[str, Any]] = list(native or [])
            used_apify = False
            if len(collected) < batch_target:
                # Prefer maxPosts (vulnv / data-slayer); keep maxPostsPerCompany for
                # legacy automation-lab actor compatibility.
                try:
                    items = await get_apify().run_actor_sync(
                        settings.APIFY_ACTOR_LI_COMPANY_POSTS,
                        {
                            "companyUrls": [company_url],
                            "maxPosts": batch_target,
                            "maxPostsPerCompany": batch_target,
                        },
                        max_items=batch_target,
                    )
                except ApifyError:
                    # Quota / actor outage must not 502 when native already has posts.
                    items = None
                if items:
                    merged = _merge_company_post_rows(collected, items)
                    if len(merged) > len(collected):
                        used_apify = True
                    collected = merged
                    if not collected:
                        collected = items
                        used_apify = True

            # When Apify is down/quota-hit, SERP can still deepen pagination.
            if len(collected) < batch_target:
                serp_rows = await linkedin_native.search_posts(
                    slug, sort="date", limit=min(40, batch_target)
                )
                if serp_rows:
                    slug_l = slug.lower()
                    company_hits: list[dict[str, Any]] = []
                    for row in serp_rows:
                        purl = str(row.get("url") or "").lower()
                        author = row.get("author") if isinstance(row.get("author"), dict) else {}
                        aurl = str(author.get("url") or "").lower()
                        if f"/posts/{slug_l}_" in purl or f"/company/{slug_l}" in aurl:
                            company_hits.append(row)
                    if company_hits:
                        collected = _merge_company_post_rows(collected, company_hits)

            if not collected:
                raise HTTPException(status_code=404, detail="No public posts found for this company")

            ctx["source"] = "apify" if used_apify else "direct"
            posts = [
                n
                for i in collected
                if (n := _normalize_company_post(i)).get("text") or n.get("url")
            ]
            # Stable order so offset cursors don't reshuffle across page fetches.
            posts.sort(
                key=lambda p: int(p["id"]) if str(p.get("id") or "").isdigit() else 0,
                reverse=True,
            )
            return {"company": slug, "posts": posts}

        # Cursor pages reuse the same batch (even when cache=false on page 1).
        batch = await cached_or_run(
            endpoint="linkedin.company-posts",
            params={"slug": slug, "batch": batch_target, "v": 12},
            runner=_fetch_batch,
            ctx=ctx,
            use_cache=cache or bool(cursor),
        )
        page = _slice_company_posts_page(batch.get("posts") or [], offset=offset, limit=limit)
        data = {"company": batch.get("company") or slug, **page}
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_NATIVE
        else:
            ctx["credits_override"] = _scaled(len(data["posts"]))
        return ApiResponse(data=data)


@router.get("/search-posts", summary="Search LinkedIn posts")
async def linkedin_search_posts(
    q: str = Query(..., min_length=2, description="Keyword to search in public LinkedIn posts"),
    sort: str = Query("relevance", pattern="^(relevance|date)$"),
    limit: int = Query(20, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/search-posts",
        platform="linkedin",
        resource_url=None,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # 1) SERP → Decodo post hydrate (LI content search is auth-walled).
            native = await linkedin_native.search_posts(q, sort=sort, limit=limit)
            if native:
                ctx["source"] = "direct"
                posts = [_normalize_post_list_item(i, include_media=False) for i in native[:limit]]
                return {"query": q, "sort": sort, "totalReturned": len(posts), "posts": posts}

            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_POST_SEARCH,
                {
                    "keyword": q,
                    "sort_type": sort,
                    "page_number": 1,
                    "date_filter": "",
                    "limit": limit,
                },
                max_items=limit,
            )
            ctx["source"] = "apify"
            # Search actor never returns media attachments.
            posts = [_normalize_post_list_item(i, include_media=False) for i in items[:limit]]
            return {"query": q, "sort": sort, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="linkedin.search-posts",
            params={"q": q, "sort": sort, "limit": limit, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_NATIVE
        else:
            ctx["credits_override"] = _scaled(len(data["posts"]))
        return ApiResponse(data=data)
