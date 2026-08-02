"""Upsert post-analytics YouTube metrics fix changelog entry."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRY = {
    "published_at": "2026-08-02",
    "category": "fix",
    "title": "Post analytics: YouTube likes, comments, publishedAt, engagementRate",
    "description": (
        "Cross-platform post analytics now uses the same enriched YouTube path as "
        "video-details, so likes, comments, publishedAt, and engagementRate populate "
        "instead of staying null when views alone were present. author.username prefers "
        "the channel handle; shares/saves remain null on YouTube (not publicly exposed)."
    ),
    "items": [
        "YouTube analytics reuses enriched video-details (likes/comments/publishedAt)",
        "author.username ← channelHandle when available; displayName stays channel name",
        "Docs/FAQ: same metrics shape; platform-missing fields stay null",
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
