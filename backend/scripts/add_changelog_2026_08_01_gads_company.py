"""Upsert Google company-ads changelog entry."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRY = {
    "published_at": "2026-08-01",
    "category": "feature",
    "title": "Google company-ads: cursor paging, date filters, adsCountEstimate",
    "description": (
        "Google Ads Transparency company-ads keeps the 2-credit media[] response, and adds "
        "cursor pagination (nextCursor/hasMore), adsCountEstimate, region alias, and "
        "start_date/end_date overlap filters. Docs note public commercial creatives only — "
        "login-gated and political ads are out of scope."
    ),
    "items": [
        "Additive hasMore / nextCursor / adsCountEstimate",
        "New params: cursor, region, start_date, end_date (topic=all only)",
        "Honesty note: public ATC creatives only; shapes can vary",
    ],
}
sb = get_supabase()
existing = sb.table("changelog_entries").select("id").eq("title", ENTRY["title"]).limit(1).execute()
if existing.data:
    row_id = existing.data[0]["id"]
    sb.table("changelog_entries").update(ENTRY).eq("id", row_id).execute()
    print("updated:", row_id)
else:
    res = sb.table("changelog_entries").insert(ENTRY).execute()
    print("inserted:", res.data[0]["id"] if res.data else res)
