"""Age / gender / nationality inference endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_float, safe_int, safe_str

router = APIRouter()


def _names(name: str, names: str | None) -> list[str]:
    raw = names or name
    out = [p.strip() for p in raw.split(",") if p.strip()]
    return out[:100]


def _normalize(item: dict[str, Any]) -> dict[str, Any]:
    countries = item.get("countries") or item.get("nationalities") or item.get("country") or []
    if isinstance(countries, dict):
        countries = [countries]
    return {
        "name": safe_str(item.get("name") or item.get("firstName")),
        "age": safe_int(item.get("age") or item.get("estimatedAge")),
        "ageCount": safe_int(item.get("ageCount") or item.get("age_count")),
        "gender": safe_str(item.get("gender")),
        "genderProbability": safe_float(item.get("genderProbability") or item.get("gender_probability") or item.get("probability")),
        "genderCount": safe_int(item.get("genderCount") or item.get("gender_count")),
        "nationality": safe_str(item.get("nationality") or item.get("countryId") or item.get("country_id")),
        "countries": countries if isinstance(countries, list) else [],
        "raw": item,
    }


async def _run_lookup(name: str, names: str | None) -> dict[str, Any]:
    parsed = _names(name, names)
    if not parsed:
        raise HTTPException(status_code=400, detail="Provide at least one name")
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_AGE_GENDER,
        {"names": parsed, "maxItems": len(parsed), "modes": ["age", "gender", "nationality"]},
        max_items=len(parsed),
    )
    results = [_normalize(i) for i in items]
    return {"platform": "age_gender", "totalReturned": len(results), "results": results}


@router.get("", summary="Get age and gender from name")
async def get_age_gender(
    name: str = Query(..., min_length=1, description="First name, or fallback when names is omitted"),
    names: str | None = Query(None, description="Optional comma-separated list of names"),
    caller: ApiCaller = Depends(require_api_key),
):
    parsed = _names(name, names)
    async with billed_call(caller=caller, endpoint="/v1/age-gender", platform="age_gender", resource_url=None, base_credits=max(4, len(parsed) * 4)) as ctx:
        data = await cached_or_run("age-gender.get", {"names": ",".join(parsed), "v": 2}, lambda: _run_lookup(name, names), ctx)
        return ApiResponse(data=data)


@router.get("/get", summary="Get age and gender from name")
async def get_age_gender_alias(
    name: str = Query(..., min_length=1),
    names: str | None = Query(None),
    caller: ApiCaller = Depends(require_api_key),
):
    return await get_age_gender(name=name, names=names, caller=caller)
