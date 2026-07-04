"""Public API health status.

Reads the most recent `requests` log rows and evaluates each platform by its
latest responses, not a 24h average -- so a problem that was fixed an hour ago
does not keep the page yellow all day. No auth required; this powers
captapi.com/status so users can verify endpoint health before opening a
support ticket.

Only 5xx responses count against health (our problem). 4xx responses are the
caller's problem (bad URL, wrong query parameter, insufficient credits, rate
limit) and are treated as healthy system behavior.
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

# Health is decided by the platform's newest requests: how many of the most
# recent responses in a row were 5xx. The moment a request succeeds again the
# streak resets and the platform goes back to operational.
DEGRADED_STREAK = 1  # 1-2 trailing failures -> degraded
OUTAGE_STREAK = 3  # 3+ trailing failures -> outage


def _recent_rows(sb: Any) -> list[dict[str, Any]]:
    """Most recent request rows (newest first) from the last 24h."""
    since = (datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)).isoformat()
    rows: list[dict[str, Any]] = []
    for page in range(5):  # at most 5000 most-recent rows
        res = (
            sb.table("requests")
            .select("platform, status_code, response_time_ms, created_at")
            .gte("created_at", since)
            .order("created_at", desc=True)
            .range(page * 1000, page * 1000 + 999)
            .execute()
        )
        chunk = res.data or []
        rows.extend(chunk)
        if len(chunk) < 1000:
            break
    return rows


def _streak_label(failing_streak: int) -> str:
    if failing_streak >= OUTAGE_STREAK:
        return "outage"
    if failing_streak >= DEGRADED_STREAK:
        return "degraded"
    return "operational"


@router.get("", summary="Public API health (live, based on latest requests, no auth required)")
async def api_status() -> dict[str, Any]:
    now = time.time()
    if _cache["data"] is not None and now - _cache["at"] < CACHE_SECONDS:
        return _cache["data"]

    sb = get_supabase()
    rows = _recent_rows(sb)

    grouped: dict[str, dict[str, Any]] = {}
    for r in rows:  # newest first
        platform = r.get("platform") or "other"
        g = grouped.setdefault(
            platform,
            {"total": 0, "server_errors": 0, "ms_sum": 0, "ms_n": 0, "streak": 0, "streak_open": True},
        )
        g["total"] += 1
        is_server_error = int(r.get("status_code") or 0) >= 500
        if is_server_error:
            g["server_errors"] += 1
            if g["streak_open"]:
                g["streak"] += 1
        else:
            # A healthy response (2xx-4xx): everything newer than this row has
            # been counted; the failure streak, if any, is over.
            g["streak_open"] = False
        ms = r.get("response_time_ms")
        if isinstance(ms, (int, float)):
            g["ms_sum"] += ms
            g["ms_n"] += 1

    platforms = []
    total_all = 0
    for platform, g in sorted(grouped.items(), key=lambda kv: -kv[1]["total"]):
        total = g["total"]
        if total == 0:
            continue
        rate = round((1 - g["server_errors"] / total) * 100, 2)
        platforms.append(
            {
                "platform": platform,
                "status": _streak_label(g["streak"]),
                "success_rate": rate,
                "requests_24h": total,
                "avg_response_ms": round(g["ms_sum"] / g["ms_n"]) if g["ms_n"] else None,
            }
        )
        total_all += total

    worst = "no_data" if not platforms else "operational"
    for p in platforms:
        if p["status"] == "outage":
            worst = "outage"
            break
        if p["status"] == "degraded":
            worst = "degraded"

    data = {
        "success": True,
        "data": {
            "overall": {
                "status": worst,
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
