"""Kick Apify trending-reels refreshes for high-demand countries.

Usage:
  python backend/scripts/warm_instagram_trending_reels.py
  python backend/scripts/warm_instagram_trending_reels.py --countries "United States,Turkey"

Env:
  APIFY_TOKEN (required)
  APIFY_ACTOR_INSTAGRAM_TRENDING (optional)
  TRENDING_WARM_COUNTRIES — comma-separated override (optional)
  SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY — optional; when set, ranks
  countries from requests.resource_url = 'country:…' on trending-reels.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Avoid loading full Settings (needs many secrets) — only ApifyClient + country list.
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

from app.routers.instagram import _TRENDING_COUNTRIES  # noqa: E402
from app.services.apify_client import ApifyClient  # noqa: E402

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


async def _warm(countries: list[str], *, fetch_n: int = 100) -> int:
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
            print(f"skip {country}: already {active.get('status')} runId={active.get('id')}")
            continue
        run = await client.start_run(actor, {"max_results": fetch_n, "country": country})
        print(f"start {country}: runId={(run or {}).get('id')} status={(run or {}).get('status')}")
        if run:
            started += 1
    return started


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--countries",
        default=os.environ.get("TRENDING_WARM_COUNTRIES") or "",
        help="Comma-separated country names (default: usage-ranked or built-in set)",
    )
    parser.add_argument("--max-countries", type=int, default=12)
    args = parser.parse_args()

    countries = _parse_countries(args.countries)
    if not countries:
        countries = _countries_from_usage(limit=args.max_countries)
    if not countries:
        countries = _DEFAULT_WARM[: args.max_countries]

    print(f"warming {len(countries)} countries: {', '.join(countries)}")
    n = asyncio.run(_warm(countries))
    print(f"started {n} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
