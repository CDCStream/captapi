"""Upsert compare-analytics docs/cache fix changelog entry."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRY = {
    "published_at": "2026-08-02",
    "category": "fix",
    "title": "Compare analytics: real unified metrics example + cache param",
    "description": (
        "Compare analytics docs no longer show placeholder example.com rows. The live "
        "example returns count/resolved/results[] with the same metrics object as post "
        "analytics (views, likes, comments, engagementRate, …). Adds cache=true "
        "(per-URL cache shared with /post; hits free) and honest billing copy — "
        "1 credit per resolved URL, no bulk discount."
    ),
    "items": [
        "Live snapshot example with two real YouTube URLs and full metrics{}",
        "Additive cache param (shared with /v1/analytics/post)",
        "Docs/FAQ: same shape as post analytics; no bulk credit discount",
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
