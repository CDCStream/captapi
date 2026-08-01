"""Upsert remaining 2026-08-01 changelog entries (IG channel-details + YT comments)."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.supabase_client import get_supabase  # noqa: E402

ENTRIES = [
    {
        "published_at": "2026-08-01",
        "category": "feature",
        "title": "Richer Instagram channel-details (non-breaking)",
        "description": (
            "Instagram channel-details keeps every existing field your integrations already parse, "
            "and adds the IDs and account flags needed for joins, outreach, and private-account detection. "
            "externalUrl and profileImage are unchanged; bioLinks and profileImageHd are additive."
        ),
        "items": [
            "New id and fbid for stable Instagram user identity",
            "isPrivate, isBusinessAccount, isProfessionalAccount, categoryName",
            "bioLinks[], profileImageHd, businessAddress when present, plus fetchedAt",
        ],
    },
    {
        "published_at": "2026-08-01",
        "category": "improvement",
        "title": "YouTube comments: author channel ID, publishedTime, heart fix",
        "description": (
            "YouTube comments responses now include authorChannelId and publishedTime "
            "(ISO when InnerTube provides it) alongside the existing author string and "
            "publishedTimeText. hasCreatorHeart no longer false-positives on inactive heart "
            "tooltips. Billing stays a flat 2 credits per call."
        ),
        "items": [
            "authorChannelId for stable commenter joins",
            "publishedTime ISO when available; publishedTimeText unchanged",
            "hasCreatorHeart only true when the creator actually hearted the comment",
        ],
    },
]

sb = get_supabase()
for entry in ENTRIES:
    existing = (
        sb.table("changelog_entries")
        .select("id")
        .eq("title", entry["title"])
        .limit(1)
        .execute()
    )
    if existing.data:
        row_id = existing.data[0]["id"]
        sb.table("changelog_entries").update(entry).eq("id", row_id).execute()
        print("updated:", entry["title"], row_id)
    else:
        res = sb.table("changelog_entries").insert(entry).execute()
        print("inserted:", entry["title"], res.data[0]["id"] if res.data else res)