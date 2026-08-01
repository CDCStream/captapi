"""Insert/update the cheaper list/search pricing changelog entry.

Also strips supplier-leaking "Apify-backed" wording from the live row if present.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.supabase_client import get_supabase  # noqa: E402

OLD_TITLE = "Cheaper pricing on native list and search endpoints"
ENTRY = {
    "published_at": "2026-07-29",
    "category": "improvement",
    "title": "Cheaper pricing on list and search endpoints",
    "description": (
        "Many list and search endpoints now bill a flat 2 credits per call "
        "instead of scaling per result. This covers YouTube comments, comment replies, "
        "channel videos, search, and channel playlists; TikTok top search and trending "
        "feed; Instagram hashtag search; Twitter/X user tweets and search; and Reddit "
        "subreddit posts, comments, transcript, search, and subreddit search. "
        "Other endpoints keep their existing per-call or per-result pricing — see each docs page."
    ),
    "items": [
        "YouTube comments, replies, channel videos, search, and playlists -> flat 2 credits",
        "TikTok top search and trending feed -> flat 2 credits",
        "Instagram hashtag search -> flat 2 credits",
        "Twitter/X user tweets and search -> flat 2 credits",
        "Reddit list, comments, transcript, and search endpoints -> flat 2 credits",
    ],
}

sb = get_supabase()
existing = (
    sb.table("changelog_entries")
    .select("id,title")
    .in_("title", [ENTRY["title"], OLD_TITLE])
    .execute()
)
if existing.data:
    row_id = existing.data[0]["id"]
    sb.table("changelog_entries").update(ENTRY).eq("id", row_id).execute()
    print("updated:", row_id)
else:
    res = sb.table("changelog_entries").insert(ENTRY).execute()
    print("inserted:", res.data[0]["id"] if res.data else res)
