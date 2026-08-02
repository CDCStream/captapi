"""Upsert Pinterest pin-details enrichment changelog entry."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRY = {
    "published_at": "2026-08-02",
    "category": "feature",
    "title": "Pinterest pin-details: title, link, createdAt, originAuthor, images",
    "description": (
        "Pinterest pin-details keeps board{}, author{}, image, and saves, and adds the fields "
        "needed for commerce and creator intel: title/description/seoAltText, link/destinationUrl, "
        "ISO createdAt, originAuthor vs author (pinner), repinCount/shareCount/reactionCount, "
        "and images{} including originals."
    ),
    "items": [
        "Additive title, description, seoAltText, link/destinationUrl, domain",
        "Additive createdAt/publishedAt (ISO-8601 from pin page)",
        "Additive originAuthor + images{236x,564x,originals} + repin/share/reaction counts",
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
