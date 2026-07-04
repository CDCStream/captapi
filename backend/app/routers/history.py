"""Metric history: follower/engagement time series for tracked resources.

Captapi records countable metrics (followers, views, likes, ...) every time
a tracked profile/post endpoint is fetched fresh (see
app/services/metric_history.py). This endpoint returns that series so you
can chart growth without building your own snapshot pipeline.

The series starts accumulating from the first time a resource is fetched
through the API -- point it at profiles you care about (or set up a monitor)
and history builds itself.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.metric_history import TRACKED_ENDPOINTS
from app.services.supabase_client import get_supabase

router = APIRouter()

CREDIT_HISTORY = 1


def _to_internal_name(endpoint: str) -> str:
    """Accept both '/v1/youtube/channel-details' and 'youtube.channel-details'."""
    name = endpoint.strip()
    if name.startswith("/"):
        name = name.removeprefix("/v1/").replace("/", ".", 1)
    if name not in TRACKED_ENDPOINTS:
        tracked_paths = sorted(f"/v1/{n.replace('.', '/', 1)}" for n in TRACKED_ENDPOINTS)
        raise HTTPException(
            status_code=400,
            detail={
                "error": "untracked_endpoint",
                "message": f"History is not recorded for '{endpoint}'.",
                "tracked_endpoints": tracked_paths,
            },
        )
    return name


@router.get("", summary="Metric time series for a profile or post")
async def metric_history(
    endpoint: str = Query(..., description="Tracked endpoint path, e.g. /v1/youtube/channel-details"),
    url: str = Query(..., description="The same URL you pass to that endpoint"),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(200, ge=1, le=1000),
    caller: ApiCaller = Depends(require_api_key),
):
    name = _to_internal_name(endpoint)
    async with billed_call(
        caller=caller,
        endpoint="/v1/history",
        platform=name.split(".", 1)[0],
        resource_url=url,
        base_credits=CREDIT_HISTORY,
    ) as ctx:
        sb = get_supabase()
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        query = (
            sb.table("metric_history")
            .select("resource, metrics, captured_at")
            .eq("endpoint", name)
            .gte("captured_at", since)
            .order("captured_at", desc=False)
            .limit(limit)
        )
        exact = query.eq("resource", url.strip()).execute()
        rows = exact.data or []
        if not rows:
            # Tolerate trailing-slash / scheme variations of the same resource.
            trimmed = url.strip().rstrip("/").removeprefix("https://").removeprefix("http://").removeprefix("www.")
            if len(trimmed) >= 8:
                fuzzy = (
                    sb.table("metric_history")
                    .select("resource, metrics, captured_at")
                    .eq("endpoint", name)
                    .gte("captured_at", since)
                    .ilike("resource", f"%{trimmed}%")
                    .order("captured_at", desc=False)
                    .limit(limit)
                    .execute()
                )
                rows = fuzzy.data or []

        data = {
            "endpoint": f"/v1/{name.replace('.', '/', 1)}",
            "resource": rows[0]["resource"] if rows else url,
            "windowDays": days,
            "totalReturned": len(rows),
            "points": [
                {"capturedAt": r["captured_at"], "metrics": r["metrics"]}
                for r in rows
            ],
        }
        ctx["data"] = data
        return ApiResponse(data=data)
