"""Upsert Facebook details additive fields changelog entry."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRY = {
    "published_at": "2026-08-01",
    "category": "feature",
    "title": "Richer Facebook details: author id, SD/HD, captions, music (non-breaking)",
    "description": (
        "Facebook details keeps every existing field (videoUrl, author.username, engagement), and adds "
        "stable author.id, feedbackId, captionsUrl, videoSdUrl/videoHdUrl, video dimensions, nested video{}, "
        "and music when Facebook exposes them. Docs note that some Reel view counts on the post page can lag "
        "the public Reels grid badge."
    ),
    "items": [
        "Additive author.id + feedbackId",
        "Additive captionsUrl, videoSdUrl/videoHdUrl, videoWidth/videoHeight, video{}, music{}",
        "Docs warning for Reel view-count badge mismatch vs profile Reels grid",
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