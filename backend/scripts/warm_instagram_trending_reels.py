"""Warm Instagram trending-reels: kick Apify, build payload, write Redis.

Usage:
  python backend/scripts/warm_instagram_trending_reels.py
  python backend/scripts/warm_instagram_trending_reels.py --countries "United States,Turkey"

Env:
  APIFY_TOKEN (required)
  REDIS_URL (required to persist ready-to-serve snapshots)
  APIFY_ACTOR_INSTAGRAM_TRENDING (optional)
  TRENDING_WARM_COUNTRIES — comma-separated override (optional)
  SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY — optional usage ranking
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Avoid loading full Settings (needs many secrets) — stub the required ones.
os.environ.setdefault("SUPABASE_URL", os.environ.get("SUPABASE_URL") or "http://localhost")
os.environ.setdefault(
    "SUPABASE_SERVICE_ROLE_KEY",
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "warm-script",
)
os.environ.setdefault(
    "SUPABASE_ANON_KEY",
    os.environ.get("SUPABASE_ANON_KEY") or "warm-script",
)
os.environ.setdefault("APIFY_TOKEN", os.environ.get("APIFY_TOKEN") or "")
os.environ.setdefault("REDIS_URL", os.environ.get("REDIS_URL") or "")

from app.routers.instagram import (  # noqa: E402
    _TRENDING_COUNTRIES,
    store_trending_snapshot,
)
from app.services.apify_client import ApifyClient  # noqa: E402
from app.services import instagram_trending_snapshot as ig_snap  # noqa: E402

_DEFAULT_ACTOR = "agentx/instagram-trending-scraper"
_DEFAULT_WARM = [
    "United States",
    "United Kingdom",
    "Brazil",
    "India",
    "Turkey",
    "Germany",
    "France",
    "Mexico",
    "Indonesia",
    "Japan",
]
# Apify Explore runs are slow — wait long enough for SUCCEEDED before giving up.
_WAIT_SECS = 12 * 60
_POLL_SECS = 30


def _parse_countries(raw: str | None) -> list[str]:
    if not raw:
        return []
    allowed = {c.lower(): c for c in _TRENDING_COUNTRIES}
    out: list[str] = []
    seen: set[str] = set()
    for part in raw.split(","):
        name = allowed.get(part.strip().lower())
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _countries_from_usage(*, limit: int = 12) -> list[str]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key or url.startswith("http://localhost") or key == "warm-script":
        return []
    try:
        import httpx
    except ImportError:
        return []
    table = (
        f"{url.rstrip('/')}/rest/v1/requests"
        "?select=resource_url"
        "&endpoint=eq./v1/instagram/trending-reels"
        "&resource_url=like.country:*"
        "&order=created_at.desc"
        "&limit=500"
    )
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(table, headers=headers)
            if resp.status_code >= 400:
                return []
            rows = resp.json()
    except Exception:
        return []
    counts: dict[str, int] = {}
    for row in rows if isinstance(rows, list) else []:
        ru = (row or {}).get("resource_url") or ""
        if not ru.startswith("country:"):
            continue
        name = ru.split(":", 1)[1].strip()
        if name in _TRENDING_COUNTRIES:
            counts[name] = counts.get(name, 0) + 1
    return sorted(counts, key=lambda k: counts[k], reverse=True)[:limit]


async def _kick(countries: list[str], *, fetch_n: int = 100) -> int:
    actor = os.environ.get("APIFY_ACTOR_INSTAGRAM_TRENDING") or _DEFAULT_ACTOR
    token = os.environ.get("APIFY_TOKEN") or ""
    if not token:
        raise SystemExit("APIFY_TOKEN is required")
    client = ApifyClient(token=token, timeout=30, max_attempts=1)
    started = 0
    for country in countries:
        match = {"country": country}
        active = await client.find_active_run(actor, input_match=match)
        if active:
            print(f"skip-start {country}: already {active.get('status')} runId={active.get('id')}")
            continue
        run = await client.start_run(actor, {"max_results": fetch_n, "country": country})
        print(f"start {country}: runId={(run or {}).get('id')} status={(run or {}).get('status')}")
        if run:
            started += 1
    return started


async def _wait_and_store(countries: list[str]) -> tuple[int, int]:
    """Poll until each country has a ≤12h Apify run, then write Redis."""
    redis_url = os.environ.get("REDIS_URL") or ""
    if not redis_url:
        raise SystemExit(
            "REDIS_URL is required — warm job must write ready-to-serve snapshots"
        )
    stored = 0
    failed = 0
    deadline = time.monotonic() + _WAIT_SECS
    pending = list(countries)
    while pending and time.monotonic() < deadline:
        next_pending: list[str] = []
        for country in pending:
            try:
                payload = await store_trending_snapshot(country, enrich=True)
            except Exception as exc:  # noqa: BLE001
                print(f"store-error {country}: {exc}")
                next_pending.append(country)
                continue
            if payload and ig_snap.is_servable(payload):
                n = len(payload.get("reels") or [])
                print(
                    f"stored {country}: reels={n} "
                    f"snapshotAt={payload.get('snapshotAt')} "
                    f"ageHours={payload.get('ageHours')}"
                )
                stored += 1
            else:
                print(f"waiting {country}: no ≤12h video snapshot yet")
                next_pending.append(country)
        pending = next_pending
        if pending:
            await asyncio.sleep(_POLL_SECS)
    for country in pending:
        print(f"fail {country}: timed out waiting for usable Apify run")
        failed += 1
    return stored, failed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--countries",
        default=os.environ.get("TRENDING_WARM_COUNTRIES") or "",
        help="Comma-separated country names (default: usage-ranked or built-in set)",
    )
    parser.add_argument("--max-countries", type=int, default=12)
    parser.add_argument(
        "--kick-only",
        action="store_true",
        help="Only start Apify runs (do not wait / write Redis)",
    )
    args = parser.parse_args()

    countries = _parse_countries(args.countries)
    if not countries:
        countries = _countries_from_usage(limit=args.max_countries)
    if not countries:
        countries = _DEFAULT_WARM[: args.max_countries]

    print(f"warming {len(countries)} countries: {', '.join(countries)}")
    started = asyncio.run(_kick(countries))
    print(f"started {started} runs")
    if args.kick_only:
        return 0
    stored, failed = asyncio.run(_wait_and_store(countries))
    print(f"stored {stored}/{len(countries)} snapshots (failed={failed})")
    # Non-zero if nothing was stored — surfaces as a red Actions run.
    return 0 if stored > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
