"""Country-level Redis snapshots for Instagram trending-reels.

Warm cron builds a ready-to-serve payload (mapped + filtered + enriched) and
writes it here. The request path reads this key for the hot path (<2s) and
never re-lists Apify runs or enriches authors on a snapshot hit.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from app.services.cache import cache_get, cache_set

log = structlog.get_logger(__name__)

# Bump when payload shape changes (plays removed, durationSeconds kept, …).
SNAPSHOT_VERSION = 19
# Hard serve cutoff — older snapshots are treated as missing.
MAX_AGE_SECS = 12 * 3600
# Soft stale flag inside the serve window (docs: ~6h refresh).
STALE_AFTER_SECS = 6 * 3600
# How many reels the warm job stores (request path slices to limit).
STORE_LIMIT = 100
# Redis TTL — slightly above hard cutoff so ageHours>12 can't linger as a hit.
REDIS_TTL_SECS = MAX_AGE_SECS + 3600


def snapshot_key(country: str) -> str:
    return f"sk:ig:trending:v{SNAPSHOT_VERSION}:{country}"


def iso_ms(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def age_seconds(snapshot_at: datetime | str | None) -> float | None:
    if snapshot_at is None:
        return None
    if isinstance(snapshot_at, str):
        try:
            snapshot_at = datetime.fromisoformat(snapshot_at.replace("Z", "+00:00"))
        except ValueError:
            return None
    if snapshot_at.tzinfo is None:
        snapshot_at = snapshot_at.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - snapshot_at).total_seconds())


def freshness_from_snapshot_at(snapshot_at: datetime | str | None) -> dict[str, Any]:
    age = age_seconds(snapshot_at)
    if age is None:
        return {"cached": False, "stale": False, "ageHours": 0}
    if isinstance(snapshot_at, datetime):
        stamp = iso_ms(snapshot_at)
    else:
        stamp = str(snapshot_at)
    return {
        "cached": True,
        "snapshotAt": stamp,
        "cachedAt": stamp,
        "stale": age > STALE_AFTER_SECS,
        "ageHours": round(age / 3600.0, 2),
    }


def is_servable(payload: dict[str, Any] | None) -> bool:
    """True when payload exists, has reels, and age ≤ hard cutoff."""
    if not isinstance(payload, dict):
        return False
    reels = payload.get("reels")
    if not isinstance(reels, list) or not reels:
        return False
    age = age_seconds(payload.get("snapshotAt") or payload.get("cachedAt"))
    if age is None:
        return False
    return age <= MAX_AGE_SECS


async def read_snapshot(country: str) -> dict[str, Any] | None:
    raw = await cache_get(snapshot_key(country))
    if not is_servable(raw):
        return None
    return raw


async def write_snapshot(country: str, payload: dict[str, Any]) -> None:
    """Persist a ready-to-serve payload. Caller must set snapshotAt."""
    if not isinstance(payload, dict) or not payload.get("reels"):
        log.warning("ig_trending_snapshot_skip_empty", country=country)
        return
    await cache_set(snapshot_key(country), payload, ttl=REDIS_TTL_SECS)
    log.info(
        "ig_trending_snapshot_written",
        country=country,
        n=len(payload.get("reels") or []),
        snapshotAt=payload.get("snapshotAt"),
        key=snapshot_key(country),
    )


def slice_payload(payload: dict[str, Any], limit: int) -> dict[str, Any]:
    """Return a copy sliced to limit with freshness recomputed from snapshotAt."""
    reels = list(payload.get("reels") or [])[: max(0, limit)]
    fresh = freshness_from_snapshot_at(payload.get("snapshotAt") or payload.get("cachedAt"))
    out = dict(payload)
    out["reels"] = reels
    out["totalReturned"] = len(reels)
    out.update(fresh)
    return out
