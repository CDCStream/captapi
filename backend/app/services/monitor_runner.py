"""Background scheduler that runs due monitors and delivers webhooks.

Every tick it picks monitors whose ``next_run_at`` has passed, replays their
endpoint in-process (through the normal auth/credit/cache pipeline, billed to
the monitor's owner) and POSTs items that were not seen on the previous run
to the monitor's webhook, signed with its per-monitor secret:

    X-Captapi-Signature: sha256=HMAC_SHA256(secret, f"{timestamp}.{body}")

The first successful run only records a baseline and does not fire.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
import structlog

from app.core.internal_token import mint_monitor_token
from app.services.supabase_client import get_supabase

log = structlog.get_logger(__name__)

TICK_SECONDS = 60
MAX_PER_TICK = 20
MAX_ITEMS_PER_DELIVERY = 50
MAX_SEEN_IDS = 1000
ENDPOINT_TIMEOUT = 180
WEBHOOK_TIMEOUT = 15

# Keys commonly used for stable item identity across our endpoints, in
# priority order. Falls back to a hash of the whole item.
ID_KEYS = ("id", "videoId", "postId", "commentId", "tweetId", "pinId", "adId", "adArchiveId", "permalink", "url", "link")
# Keys whose value holds the "list of items" in a response's data object.
LIST_KEYS = ("items", "posts", "videos", "comments", "results", "tweets", "pins", "ads", "reviews", "products", "channels", "users", "segments", "tracks", "episodes")


def extract_items(data: Any) -> list[dict[str, Any]]:
    """Best-effort: find the primary list of item dicts in a response payload."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if not isinstance(data, dict):
        return []
    for key in LIST_KEYS:
        val = data.get(key)
        if isinstance(val, list) and val and all(isinstance(x, dict) for x in val):
            return val
    # Fall back to the largest list-of-dicts value anywhere at the top level.
    best: list[dict[str, Any]] = []
    for val in data.values():
        if isinstance(val, list):
            dicts = [x for x in val if isinstance(x, dict)]
            if len(dicts) > len(best):
                best = dicts
    return best


def item_id(item: dict[str, Any]) -> str:
    for key in ID_KEYS:
        val = item.get(key)
        if isinstance(val, (str, int)) and str(val).strip():
            return f"{key}:{val}"
    blob = json.dumps(item, sort_keys=True, separators=(",", ":"), default=str)
    return "hash:" + hashlib.sha256(blob.encode()).hexdigest()[:24]


def sign_payload(secret: str, timestamp: str, body: str) -> str:
    return hmac.new(secret.encode(), f"{timestamp}.{body}".encode(), hashlib.sha256).hexdigest()


async def deliver_webhook(monitor: dict[str, Any], new_items: list[dict[str, Any]]) -> tuple[bool, str | None]:
    payload = {
        "event": "monitor.new_items",
        "monitor": {
            "id": monitor["id"],
            "name": monitor.get("name") or "",
            "endpoint": monitor["endpoint"],
            "params": monitor.get("params") or {},
        },
        "new_count": len(new_items),
        "items": new_items[:MAX_ITEMS_PER_DELIVERY],
        "fired_at": datetime.now(timezone.utc).isoformat(),
    }
    body = json.dumps(payload, separators=(",", ":"), default=str)
    ts = str(int(time.time()))
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "captapi-monitors/1.0",
        "X-Captapi-Monitor-Id": monitor["id"],
        "X-Captapi-Timestamp": ts,
        "X-Captapi-Signature": f"sha256={sign_payload(monitor['secret'], ts, body)}",
    }
    last_error: str | None = None
    for attempt in (1, 2):
        try:
            async with httpx.AsyncClient(timeout=WEBHOOK_TIMEOUT) as client:
                resp = await client.post(monitor["webhook_url"], content=body, headers=headers)
            if resp.status_code < 400:
                return True, None
            last_error = f"webhook returned {resp.status_code}"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)[:300]
        if attempt == 1:
            await asyncio.sleep(2)
    return False, last_error


async def run_monitor(app: Any, monitor: dict[str, Any]) -> None:
    sb = get_supabase()
    now = datetime.now(timezone.utc)
    next_run = now + timedelta(minutes=int(monitor["interval_minutes"]))
    updates: dict[str, Any] = {
        "last_run_at": now.isoformat(),
        "next_run_at": next_run.isoformat(),
        "updated_at": now.isoformat(),
    }

    try:
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://captapi.internal",
            timeout=httpx.Timeout(ENDPOINT_TIMEOUT),
        ) as client:
            resp = await client.get(
                monitor["endpoint"],
                params={k: v for k, v in (monitor.get("params") or {}).items() if v is not None},
                headers={
                    "Authorization": f"Bearer {mint_monitor_token(monitor['user_id'])}",
                    "Accept": "application/json",
                    "User-Agent": "captapi-monitors/1.0",
                },
            )
        if resp.status_code >= 400:
            detail = resp.text[:300]
            updates["last_status"] = "error"
            updates["last_error"] = f"endpoint returned {resp.status_code}: {detail}"
            if resp.status_code == 402:
                # Out of credits: pause instead of burning a failed run every interval.
                updates["active"] = False
                updates["last_error"] += " (monitor paused; reactivate after topping up)"
            sb.table("monitors").update(updates).eq("id", monitor["id"]).execute()
            log.warning("monitor_run_failed", monitor_id=monitor["id"], status=resp.status_code)
            return

        body = resp.json()
        items = extract_items(body.get("data"))
        ids = [item_id(x) for x in items]
        seen: list[str] = monitor.get("seen_ids") or []
        seen_set = set(seen)
        new_pairs = [(i, x) for i, x in zip(ids, items) if i not in seen_set]

        is_baseline = monitor.get("last_run_at") is None
        delivered_error: str | None = None
        if new_pairs and not is_baseline:
            ok, delivered_error = await deliver_webhook(monitor, [x for _, x in new_pairs])
            log.info(
                "monitor_fired",
                monitor_id=monitor["id"],
                new_items=len(new_pairs),
                delivered=ok,
            )

        updates["seen_ids"] = ([i for i, _ in new_pairs] + seen)[:MAX_SEEN_IDS]
        updates["last_status"] = "ok" if delivered_error is None else "webhook_error"
        updates["last_error"] = delivered_error
        sb.table("monitors").update(updates).eq("id", monitor["id"]).execute()
    except Exception as exc:  # noqa: BLE001
        updates["last_status"] = "error"
        updates["last_error"] = str(exc)[:300]
        try:
            sb.table("monitors").update(updates).eq("id", monitor["id"]).execute()
        except Exception:  # noqa: BLE001
            pass
        log.error("monitor_run_crashed", monitor_id=monitor["id"], error=str(exc))


async def monitor_loop(app: Any) -> None:
    log.info("monitor_loop_started")
    while True:
        try:
            sb = get_supabase()
            now_iso = datetime.now(timezone.utc).isoformat()
            res = (
                sb.table("monitors")
                .select("*")
                .eq("active", True)
                .lte("next_run_at", now_iso)
                .order("next_run_at")
                .limit(MAX_PER_TICK)
                .execute()
            )
            due = res.data or []
            if due:
                log.info("monitor_tick", due=len(due))
                await asyncio.gather(*(run_monitor(app, m) for m in due))
        except asyncio.CancelledError:
            log.info("monitor_loop_stopped")
            raise
        except Exception as exc:  # noqa: BLE001
            # Table missing (migration not applied yet) or transient DB error:
            # keep the loop alive, it costs one query per tick.
            log.warning("monitor_tick_failed", error=str(exc)[:300])
        await asyncio.sleep(TICK_SECONDS)
