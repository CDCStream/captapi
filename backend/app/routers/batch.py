"""Batch execution: run up to 20 endpoint calls in one HTTP request.

POST /v1/batch with a list of GET requests; they run concurrently in-process
through the normal auth / credit / cache / rate-limit pipeline (each item is
billed exactly like a direct call, failures are not billed) and the response
preserves input order. Ideal for dashboards and agents that need many
profiles or posts at once without managing client-side concurrency.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.auth import ApiCaller, require_api_key
from app.schemas.common import ApiResponse
from app.services.mcp_catalog import ENDPOINTS

log = structlog.get_logger(__name__)

router = APIRouter()

MAX_BATCH_SIZE = 20
MAX_CONCURRENCY = 10
ITEM_TIMEOUT_SECONDS = 180
VALID_PATHS = {e.path for e in ENDPOINTS}


class BatchItem(BaseModel):
    path: str = Field(..., description="Captapi GET path, e.g. /v1/youtube/video-details")
    params: dict[str, Any] = Field(default_factory=dict)


class BatchRequest(BaseModel):
    requests: list[BatchItem] = Field(..., min_length=1, max_length=MAX_BATCH_SIZE)


@router.post("", summary=f"Run up to {MAX_BATCH_SIZE} endpoint calls in one request")
async def run_batch(
    body: BatchRequest,
    request: Request,
    caller: ApiCaller = Depends(require_api_key),
) -> ApiResponse:
    for item in body.requests:
        if item.path.strip() not in VALID_PATHS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "unknown_endpoint",
                    "message": f"'{item.path}' is not a Captapi endpoint path.",
                },
            )

    auth_header = request.headers.get("authorization") or f"Bearer {request.headers.get('x-api-key', '')}"
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    transport = httpx.ASGITransport(app=request.app, raise_app_exceptions=False)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://captapi.internal",
        timeout=httpx.Timeout(ITEM_TIMEOUT_SECONDS),
    ) as client:

        async def run_one(item: BatchItem) -> dict[str, Any]:
            async with semaphore:
                try:
                    resp = await client.get(
                        item.path.strip(),
                        params={k: v for k, v in item.params.items() if v is not None},
                        headers={"Authorization": auth_header, "Accept": "application/json"},
                    )
                    try:
                        payload = resp.json()
                    except Exception:  # noqa: BLE001
                        payload = {"success": False, "error": "non_json_response"}
                    return {
                        "path": item.path,
                        "params": item.params,
                        "status": resp.status_code,
                        "body": payload,
                    }
                except Exception as exc:  # noqa: BLE001
                    log.warning("batch_item_failed", path=item.path, error=str(exc)[:200])
                    return {
                        "path": item.path,
                        "params": item.params,
                        "status": 500,
                        "body": {"success": False, "error": "batch_item_error", "detail": str(exc)[:300]},
                    }

        results = await asyncio.gather(*(run_one(item) for item in body.requests))

    succeeded = sum(1 for r in results if r["status"] < 400)
    return ApiResponse(
        data={
            "total": len(results),
            "succeeded": succeeded,
            "failed": len(results) - succeeded,
            "results": list(results),
        }
    )
