"""Monitors: scheduled watches with webhook alerts.

Point a monitor at any list-returning Captapi GET endpoint (subreddit posts,
channel videos, comments, ad-library searches, ...). The scheduler re-runs it
on your interval and POSTs *new* items to your webhook with an HMAC-signed
payload -- turning the pull-based API into a push-based alert feed.

Each scheduled run bills credits exactly like calling the endpoint directly.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets as pysecrets
import time
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.auth import ApiCaller, CallerDep
from app.schemas.common import ApiResponse
from app.services.mcp_catalog import ENDPOINTS
from app.services.supabase_client import get_supabase

log = structlog.get_logger(__name__)

router = APIRouter()

MAX_MONITORS_PER_USER = 20
MIN_INTERVAL_MINUTES = 15
VALID_PATHS = {e.path for e in ENDPOINTS}


class MonitorCreate(BaseModel):
    name: str = Field("", max_length=120)
    endpoint: str = Field(..., description="Captapi GET path, e.g. /v1/reddit/subreddit-posts")
    params: dict[str, Any] = Field(default_factory=dict)
    interval_minutes: int = Field(60, ge=MIN_INTERVAL_MINUTES, le=24 * 60)
    webhook_url: str = Field(..., description="HTTPS URL that receives new-item payloads")
    secret: str | None = Field(None, min_length=16, max_length=128, description="HMAC secret; generated if omitted")


class MonitorUpdate(BaseModel):
    name: str | None = Field(None, max_length=120)
    params: dict[str, Any] | None = None
    interval_minutes: int | None = Field(None, ge=MIN_INTERVAL_MINUTES, le=24 * 60)
    webhook_url: str | None = None
    active: bool | None = None


def _validate_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip()
    if endpoint not in VALID_PATHS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unknown_endpoint",
                "message": f"'{endpoint}' is not a Captapi endpoint path. "
                "Use one of the documented GET paths, e.g. /v1/reddit/subreddit-posts.",
            },
        )
    return endpoint


def _validate_webhook(url: str) -> str:
    url = url.strip()
    if not url.startswith("https://") or "captapi.com" in url.split("/")[2].lower():
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_webhook_url", "message": "webhook_url must be an external https:// URL."},
        )
    return url


def _public(row: dict[str, Any], include_secret: bool = False) -> dict[str, Any]:
    out = {
        "id": row["id"],
        "name": row.get("name") or "",
        "endpoint": row["endpoint"],
        "params": row.get("params") or {},
        "interval_minutes": row["interval_minutes"],
        "webhook_url": row["webhook_url"],
        "active": row["active"],
        "last_run_at": row.get("last_run_at"),
        "next_run_at": row.get("next_run_at"),
        "last_status": row.get("last_status"),
        "last_error": row.get("last_error"),
        "created_at": row.get("created_at"),
    }
    if include_secret:
        out["secret"] = row["secret"]
    return out


def _get_owned(monitor_id: str, caller: ApiCaller) -> dict[str, Any]:
    sb = get_supabase()
    res = sb.table("monitors").select("*").eq("id", monitor_id).eq("user_id", caller.user_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return res.data[0]


@router.post("", summary="Create a monitor")
async def create_monitor(body: MonitorCreate, caller: ApiCaller = CallerDep) -> ApiResponse:
    sb = get_supabase()
    endpoint = _validate_endpoint(body.endpoint)
    webhook_url = _validate_webhook(body.webhook_url)

    existing = sb.table("monitors").select("id", count="exact").eq("user_id", caller.user_id).execute()
    if (existing.count or 0) >= MAX_MONITORS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail={"error": "monitor_limit", "message": f"Maximum {MAX_MONITORS_PER_USER} monitors per account."},
        )

    row = {
        "user_id": caller.user_id,
        "name": body.name or endpoint.rsplit("/", 1)[-1],
        "endpoint": endpoint,
        "params": {k: v for k, v in body.params.items() if v is not None},
        "interval_minutes": body.interval_minutes,
        "webhook_url": webhook_url,
        "secret": body.secret or f"whsec_{pysecrets.token_hex(24)}",
    }
    ins = sb.table("monitors").insert(row).execute()
    created = ins.data[0]
    log.info("monitor_created", monitor_id=created["id"], endpoint=endpoint, user_id=caller.user_id)
    # The secret is returned on create (and via GET by the owner) so it can be
    # stored in the receiving service to verify X-Captapi-Signature.
    return ApiResponse(data=_public(created, include_secret=True))


@router.get("", summary="List your monitors")
async def list_monitors(caller: ApiCaller = CallerDep) -> ApiResponse:
    sb = get_supabase()
    res = (
        sb.table("monitors")
        .select("*")
        .eq("user_id", caller.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return ApiResponse(data={"monitors": [_public(r) for r in res.data or []]})


@router.get("/{monitor_id}", summary="Get one monitor (includes webhook secret)")
async def get_monitor(monitor_id: str, caller: ApiCaller = CallerDep) -> ApiResponse:
    return ApiResponse(data=_public(_get_owned(monitor_id, caller), include_secret=True))


@router.patch("/{monitor_id}", summary="Update a monitor")
async def update_monitor(monitor_id: str, body: MonitorUpdate, caller: ApiCaller = CallerDep) -> ApiResponse:
    row = _get_owned(monitor_id, caller)
    updates: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if body.name is not None:
        updates["name"] = body.name
    if body.params is not None:
        updates["params"] = {k: v for k, v in body.params.items() if v is not None}
        updates["seen_ids"] = []  # params changed -> re-baseline instead of flooding
        updates["last_run_at"] = None
    if body.interval_minutes is not None:
        updates["interval_minutes"] = body.interval_minutes
    if body.webhook_url is not None:
        updates["webhook_url"] = _validate_webhook(body.webhook_url)
    if body.active is not None:
        updates["active"] = body.active
        if body.active:
            updates["next_run_at"] = datetime.now(timezone.utc).isoformat()

    sb = get_supabase()
    res = sb.table("monitors").update(updates).eq("id", row["id"]).execute()
    return ApiResponse(data=_public(res.data[0]))


@router.delete("/{monitor_id}", summary="Delete a monitor")
async def delete_monitor(monitor_id: str, caller: ApiCaller = CallerDep) -> ApiResponse:
    row = _get_owned(monitor_id, caller)
    get_supabase().table("monitors").delete().eq("id", row["id"]).execute()
    return ApiResponse(data={"deleted": True, "id": row["id"]})


@router.post("/{monitor_id}/test", summary="Send a signed test payload to your webhook")
async def test_monitor(monitor_id: str, caller: ApiCaller = CallerDep) -> ApiResponse:
    row = _get_owned(monitor_id, caller)
    payload = {
        "event": "monitor.test",
        "monitor": {"id": row["id"], "name": row.get("name") or "", "endpoint": row["endpoint"]},
        "new_count": 1,
        "items": [{"id": "test-item", "note": "This is a Captapi webhook delivery test."}],
        "fired_at": datetime.now(timezone.utc).isoformat(),
    }
    body = json.dumps(payload, separators=(",", ":"))
    ts = str(int(time.time()))
    sig = hmac.new(row["secret"].encode(), f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                row["webhook_url"],
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "captapi-monitors/1.0",
                    "X-Captapi-Monitor-Id": row["id"],
                    "X-Captapi-Timestamp": ts,
                    "X-Captapi-Signature": f"sha256={sig}",
                },
            )
        return ApiResponse(data={"delivered": resp.status_code < 400, "webhook_status": resp.status_code})
    except Exception as exc:  # noqa: BLE001
        return ApiResponse(data={"delivered": False, "error": str(exc)[:300]})
