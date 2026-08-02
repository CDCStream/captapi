"""Upsert GitHub user enrichment + price cut changelog entry."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRY = {
    "published_at": "2026-08-02",
    "category": "feature",
    "title": "GitHub user: email + parity fields, 1 credit, free-API note",
    "description": (
        "GitHub user drops from 3 credits to 1 (matching ScrapeCreators) and adds email "
        "(when public), nodeId, apiUrl, hireable, and siteAdmin. type is now user or "
        "organization. Docs note that this wraps GitHub's free public REST API — use "
        "Captapi for one-key workflows; call api.github.com directly for GitHub-only jobs."
    ),
    "items": [
        "Price: 3 → 1 credit",
        "Additive email, nodeId, apiUrl, hireable, siteAdmin",
        "Honesty note: free GitHub API alternative for GitHub-only workloads",
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
