"""Public API health status.

Aggregates the last 24h of the `requests` log into per-platform success
rates and response times. No auth required -- this powers captapi.com/status
so users can verify endpoint health before opening a support ticket.

Uses the `api_health_stats` SQL function when available (fast, exact) and
falls back to sampling the most recent request rows otherwise.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog
from fastapi import APIRouter

from app.services.supabase_client import get_supabase

log = structlog.get_logger(__name__)

router = APIRouter()

WINDOW_HOURS = 24
CACHE_SECONDS = 120
_cache: dict[str, Any] = {"at": 0.0, "data": None}

# 5xx = our problem (counts against health). 4xx = caller's problem
# (bad URL, insufficient credits, rate limit) and is reported separately.


def _rpc_stats(sb: Any) -> list[dict[str, Any]] | None:
    try:
        res = sb.rpc("api_health_stats", {"p_hours": WINDOW_HOURS}).execute()
        if isinstance(res.data, list):
            return res.data
    except Exception as exc:
        log.info("api_health_rpc_unavailable", error=str(exc)[:200])
    return None


def _sampled_stats(sb: Any) -> list[dict[str, Any]]:
    since = (datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)).isoformat()
    rows: list[dict[str, Any]] = []
    for page in range(5):  # at most 5000 most-recent rows
        res = (
            sb.table("requests")
            .select("platform, status_code, response_time_ms")
            .gte("created_at", since)
            .order("created_at", desc=True)
            .range(page * 1000, page * 1000 + 999)
            .execute()
        )
        chunk = res.data or []
        rows.extend(chunk)
        if len(chunk) < 1000:
            break

    grouped: dict[str, dict[str, Any]] = {}
    for r in rows:
        platform = r.get("platform") or "other"
        g = grouped.setdefault(platform, {"total": 0, "server_errors": 0, "ms_sum": 0, "ms_n": 0})
        g["total"] += 1
        if int(r.get("status_code") or 0) >= 500:
            g["server_errors"] += 1
        ms = r.get("response_time_ms")
        if isinstance(ms, (int, float)):
            g["ms_sum"] += ms
            g["ms_n"] += 1

    return [
        {
            "platform": platform,
            "total": g["total"],
            "server_errors": g["server_errors"],
            "avg_response_ms": round(g["ms_sum"] / g["ms_n"]) if g["ms_n"] else None,
        }
        for platform, g in grouped.items()
    ]


# Low-traffic guard: with only a handful of requests in the window, one or two
# stray failures would otherwise flip a platform straight to "outage". We add
# pseudo-successes (Bayesian shrinkage toward healthy) so the label only
# degrades when failures are statistically meaningful, and we never degrade on
# fewer than MIN_ERRORS server errors.
PSEUDO_SUCCESSES = 50
MIN_ERRORS = 3


def _health_label(total: int, errors: int) -> str:
    if total <= 0:
        return "no_data"
    if errors < MIN_ERRORS:
        return "operational"
    smoothed = (total - errors + PSEUDO_SUCCESSES) / (total + PSEUDO_SUCCESSES) * 100
    if smoothed >= 99.0:
        return "operational"
    if smoothed >= 90.0:
        return "degraded"
    return "outage"


@router.get("", summary="Public API health (last 24h, no auth required)")
async def api_status() -> dict[str, Any]:
    now = time.time()
    if _cache["data"] is not None and now - _cache["at"] < CACHE_SECONDS:
        return _cache["data"]

    sb = get_supabase()
    raw = _rpc_stats(sb)
    if raw is None:
        raw = _sampled_stats(sb)

    platforms = []
    total_all = 0
    errors_all = 0
    for row in sorted(raw, key=lambda r: -int(r.get("total") or 0)):
        total = int(row.get("total") or 0)
        errors = int(row.get("server_errors") or 0)
        if total == 0:
            continue
        rate = round((1 - errors / total) * 100, 2)
        avg_ms = row.get("avg_response_ms")
        platforms.append(
            {
                "platform": row.get("platform") or "other",
                "status": _health_label(total, errors),
                "success_rate": rate,
                "requests_24h": total,
                "avg_response_ms": int(avg_ms) if avg_ms is not None else None,
            }
        )
        total_all += total
        errors_all += errors

    overall_rate = round((1 - errors_all / total_all) * 100, 2) if total_all else None
    data = {
        "success": True,
        "data": {
            "overall": {
                "status": _health_label(total_all, errors_all),
                "success_rate": overall_rate,
                "requests_24h": total_all,
            },
            "platforms": platforms,
            "window_hours": WINDOW_HOURS,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    _cache["data"] = data
    _cache["at"] = now
    return data
