"""Insert the Instagram Music Posts removal changelog entry into Supabase."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.supabase_client import get_supabase  # noqa: E402

ENTRY = {
    "published_at": "2026-07-15",
    "category": "improvement",
    "title": "Instagram Music Posts API retired",
    "description": (
        "The Instagram Music Posts API has been removed - it was a duplicate "
        "of the Instagram Reels By Audio ID API (same scraper, same data) at "
        "a higher price. Use Reels By Audio ID instead; it accepts both audio "
        "IDs and full audio page URLs."
    ),
    "items": [
        "GET /v1/instagram/music-posts no longer exists (returns 404)",
        "Migrate to GET /v1/instagram/reels-by-audio-id - pass your audio page URL or the numeric audio ID as audio_id",
        "Old docs links redirect to the Reels By Audio ID page automatically",
    ],
}

sb = get_supabase()
existing = (
    sb.table("changelog_entries").select("id").eq("title", ENTRY["title"]).execute()
)
if existing.data:
    print("entry already exists:", existing.data[0]["id"])
else:
    res = sb.table("changelog_entries").insert(ENTRY).execute()
    print("inserted:", res.data[0]["id"] if res.data else res)
