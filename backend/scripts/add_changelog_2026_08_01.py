"""Insert 2026-08-01 changelog entries (video-details + envelope + dashboard)."""

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
        "title": "Richer YouTube and TikTok video-details responses",
        "description": (
            "YouTube and TikTok video-details now return the fields teams need for joins, "
            "media pipelines, and filtering — without dumping a raw platform blob. "
            "Existing keys are unchanged; new fields are additive."
        ),
        "items": [
            "YouTube: channelHandle, contentType/isShort, liveStatus, availableCaptions[], thumbnails[], descriptionLinks[], language and access flags, fetchedAt",
            "TikTok: authorId/secUid, musicId/musicAuthor/isOriginalSound, mediaType, videoUrl/downloadUrl/downloadUrlNoWatermark, mentions[], status flags, isAd/isCommerce, region/width/height, mediaUrlsExpireAt, fetchedAt",
            "TikTok engagement.isApproximate marks rounded legacy counters vs exact statsV2 counts",
        ],
    },
    {
        "published_at": "2026-08-01",
        "category": "improvement",
        "title": "Billing metadata in every successful JSON response",
        "description": (
            "Successful API responses now include cached, creditsUsed, requestId, fetchedAt, "
            "and cachedAt in the JSON body (in addition to the existing x-captapi-* headers). "
            "Use fetchedAt for time-series snapshots and requestId when contacting support."
        ),
        "items": [
            "Body fields: cached, creditsUsed, requestId, fetchedAt, cachedAt",
            "New response header: x-captapi-request-id",
            "cachedAt is set when the response was served from cache; otherwise null",
        ],
    },
    {
        "published_at": "2026-08-01",
        "category": "platform",
        "title": "Dashboard Tools page removed",
        "description": (
            "The in-dashboard free Tools section is gone so the product stays clearly API-first. "
            "Public free tools at /tools are unchanged. Bookmarked /dashboard/tools links redirect "
            "to the API Playground."
        ),
        "items": [
            "Removed Tools from the dashboard sidebar",
            "/dashboard/tools -> /dashboard/playground",
            "Marketing free tools at /tools remain available",
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
