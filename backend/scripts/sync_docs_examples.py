"""Align api_snapshots.json with current response schemas and regenerate docs examples."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

BACKEND = Path(__file__).resolve().parents[1]
SNAP_PATH = BACKEND / "api_snapshots.json"

CURSOR_SLUGS = {
    "bluesky-user-posts",
    "reddit-subreddit-posts",
    "reddit-search",
    "reddit-subreddit-search",
    "soundcloud-artist-tracks",
    "github-repositories",
    "github-pull-requests",
    "github-activity",
    "github-followers",
    "github-following",
    "truth-social-user-posts",
    "youtube-comments",
    "youtube-shorts-comments",
    "tiktok-comments",
    "tiktok-comment-replies",
    "tiktok-channel-posts",
    "tiktok-search-by-hashtag",
    "tiktok-search-users",
    "instagram-channel-posts",
    "instagram-channel-reels",
}

AD_LIBRARY_STRIP_SLUGS = {
    "tiktok-ad-library-search",
    "tiktok-ad-library-ad-details",
    "linkedin-ad-library-search-ads",
    "linkedin-ad-library-ad-details",
}

AD_OPTIONAL_KEYS = (
    "cta", "landingUrl", "firstShown", "lastShown",
    "impressions", "spend", "country", "headline",
)


def _data(entry: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(entry, dict) or not entry.get("ok"):
        return None
    data = entry.get("data")
    return data if isinstance(data, dict) else None


def _strip_null_keys(obj: dict[str, Any], keys: tuple[str, ...]) -> None:
    for key in keys:
        if obj.get(key) in (None, "", [], {}):
            obj.pop(key, None)


def _ensure_cursor(data: dict[str, Any]) -> bool:
    changed = False
    if "nextCursor" not in data:
        data["nextCursor"] = None
        changed = True
    if "hasMore" not in data:
        data["hasMore"] = data.get("nextCursor") is not None
        changed = True
    return changed


def _patch_twitter_profile(data: dict[str, Any]) -> bool:
    if data.get("isBlueVerified") is None and data.get("verified") is not None:
        data["isBlueVerified"] = bool(data["verified"])
        return True
    return False


def _patch_twitter_community_tweets(data: dict[str, Any]) -> bool:
    changed = False
    for tweet in data.get("tweets") or []:
        if isinstance(tweet, dict) and tweet.get("isReply") is None:
            tweet["isReply"] = False
            changed = True
    return changed


def _patch_linkedin_company_posts(data: dict[str, Any]) -> bool:
    changed = False
    months = {
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
    }
    for post in data.get("posts") or []:
        if not isinstance(post, dict):
            continue
        eng = post.get("engagement")
        if isinstance(eng, dict) and all(v is None for v in eng.values()):
            post.pop("engagement", None)
            changed = True
        author = post.get("author")
        if isinstance(author, dict):
            headline = author.get("headline")
            if isinstance(headline, str) and headline.strip().lower() in months:
                author["headline"] = None
                changed = True
    return changed


def _patch_facebook_photos(data: dict[str, Any]) -> bool:
    changed = False
    for photo in data.get("photos") or []:
        if not isinstance(photo, dict):
            continue
        for key in ("publishedAt", "likes", "comments", "width", "height"):
            if key in photo and photo.get(key) is None:
                photo.pop(key, None)
                changed = True
    return changed


def _patch_facebook_group_posts(data: dict[str, Any]) -> bool:
    changed = False
    for post in data.get("posts") or []:
        if not isinstance(post, dict):
            continue
        author = post.get("author")
        if isinstance(author, dict) and "/groups/" in str(author.get("url") or "").lower():
            author["url"] = None
            changed = True
    return changed


def _patch_ad(data: dict[str, Any]) -> bool:
    changed = False
    ads = data.get("ads")
    rows = ads if isinstance(ads, list) else [data]
    for ad in rows:
        if not isinstance(ad, dict):
            continue
        before = json.dumps(ad, sort_keys=True, default=str)
        _strip_null_keys(ad, AD_OPTIONAL_KEYS)
        adv = ad.get("advertiser")
        if isinstance(adv, dict):
            name = adv.get("name")
            if isinstance(name, str) and name.strip().lower() in {"not mention", "n/a", "unknown"}:
                adv.pop("name", None)
            for key in ("id", "name", "url", "logo"):
                if adv.get(key) in (None, "", []):
                    adv.pop(key, None)
        if json.dumps(ad, sort_keys=True, default=str) != before:
            changed = True
    return changed


def patch_snapshots(snap: dict[str, Any]) -> list[str]:
    touched: list[str] = []
    for slug, entry in snap.items():
        data = _data(entry)
        if data is None:
            continue
        changed = False
        if slug in CURSOR_SLUGS:
            changed = _ensure_cursor(data) or changed
        if slug == "twitter-profile":
            changed = _patch_twitter_profile(data) or changed
        if slug == "twitter-community-tweets":
            changed = _patch_twitter_community_tweets(data) or changed
        if slug == "linkedin-company-posts":
            changed = _patch_linkedin_company_posts(data) or changed
        if slug == "facebook-profile-photos":
            changed = _patch_facebook_photos(data) or changed
        if slug == "facebook-group-posts":
            changed = _patch_facebook_group_posts(data) or changed
        if slug in AD_LIBRARY_STRIP_SLUGS:
            changed = _patch_ad(data) or changed
        if changed:
            touched.append(slug)
    return touched


def main() -> None:
    snap = json.loads(SNAP_PATH.read_text(encoding="utf-8"))
    touched = patch_snapshots(snap)
    SNAP_PATH.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched {len(touched)} snapshots:", ", ".join(sorted(touched)) or "(none)")
    subprocess.run([sys.executable, "gen_examples.py"], cwd=BACKEND, check=True)


if __name__ == "__main__":
    main()