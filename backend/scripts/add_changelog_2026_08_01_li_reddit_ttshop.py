"""Upsert LinkedIn / Reddit / TikTok Shop changelog entries."""
from __future__ import annotations
import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.services.supabase_client import get_supabase

ENTRIES = [
    {
        "published_at": "2026-08-01",
        "category": "fix",
        "title": "LinkedIn profile: stop treating SEO meta as About",
        "description": (
            "LinkedIn profile no longer copies og:description into about, and no longer invents "
            "connections/currentCompany from that SEO trailer (the Bill Gates 8 connections bug). "
            "about prefers JSON-LD Person description and is omitted when only SEO meta is available; "
            "connections matching the privacy/SEO placeholder are null."
        ),
        "items": [
            "about from JSON-LD only - SEO meta never returned as about",
            "connections matching SEO N connections on LinkedIn chrome -> null",
            "Additive experience[] / education[] when the Apify fallback returns them",
        ],
    },
    {
        "published_at": "2026-08-01",
        "category": "fix",
        "title": "Reddit comments: real ISO publishedAt + post context",
        "description": (
            "Reddit post-comments publishedAt is now ISO 8601 (was a stringified unix float like "
            "1785330725.0, which broke Date parsers). Existing flat comments + depth/parentId stay; "
            "response adds post, score/downs, authorFullname, and hasMore."
        ),
        "items": [
            "publishedAt is ISO 8601 UTC",
            "Additive score, downs, authorFullname, distinguished, controversiality",
            "post object + hasMore/nextCursor (cursor paging still deferred)",
        ],
    },
    {
        "published_at": "2026-08-01",
        "category": "feature",
        "title": "Richer TikTok Shop product-details (non-breaking)",
        "description": (
            "TikTok Shop product-details keeps price as a float + currency, and now returns seller "
            "id/url, originalPrice/discount, description, skus[], and optional region for the Apify "
            "path. Related affiliate videos remain best-effort when upstream provides them."
        ),
        "items": [
            "seller.id / seller.url restored (were stripped in details mode)",
            "originalPrice, discount, description, skus[], images[], region param",
            "Native path still bills 2 credits; Apify fallback remains 14",
        ],
    },
]


def upsert(entry: dict) -> None:
    sb = get_supabase()
    existing = sb.table("changelog_entries").select("id").eq("title", entry["title"]).limit(1).execute()
    if existing.data:
        row_id = existing.data[0]["id"]
        sb.table("changelog_entries").update(entry).eq("id", row_id).execute()
        print("updated:", entry["title"], row_id)
    else:
        res = sb.table("changelog_entries").insert(entry).execute()
        print("inserted:", entry["title"], res.data[0]["id"] if res.data else res)


if __name__ == "__main__":
    for e in ENTRIES:
        upsert(e)
