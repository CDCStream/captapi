"""Upsert YouTube channel-details email + tags changelog entry."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRY = {
    "published_at": "2026-08-01",
    "category": "feature",
    "title": "YouTube channel-details: email + SEO tags (non-breaking)",
    "description": (
        "YouTube channel-details keeps every existing numeric/stats field, and adds email "
        "(from About/description when publicly exposed) and tags[] from channel SEO keywords. "
        "CAPTCHA-gated business emails stay null."
    ),
    "items": [
        "Additive email when present in channel About/description or mailto links",
        "Additive tags[] from channelMetadataRenderer keywords (list, not a comma string)",
        "Existing subscriberCount/videoCount/viewCount numbers, handle, verified, links unchanged",
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