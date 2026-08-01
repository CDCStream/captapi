"""Upsert Facebook Ad Library search changelog entry."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRY = {
    "published_at": "2026-08-01",
    "category": "feature",
    "title": "Facebook Ad Library search: filters + richer ads (non-breaking)",
    "description": (
        "Facebook Ad Library search keeps every existing ad field your integrations already parse "
        "(including media[] and string spend/impressions), and adds the filters and structured fields "
        "needed for competitor intel. Default status is ACTIVE so results match what advertisers are running now."
    ),
    "items": [
        "New filters: status, media_type, ad_type, search_type, sort_by, start_date, end_date (max limit 200 documented)",
        "Additive ad fields: isActive, publisherPlatforms, cards[], images[], videos[], spendRange/impressionsRange, pageLikeCount, disclaimer/byline, fetchedAt",
        "searchResultsCount / hasMore / nextCursor on the response (cursor paging deferred); docs note spend/impressions are usually political/issue-only",
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