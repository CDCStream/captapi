"""Capture real docs examples for endpoints that still use generic placeholders.

Creates a temp API key, calls the live API (SMOKE_BASE, default
https://api.captapi.com) in two phases (phase 2 inputs are derived from
phase 1 responses, e.g. a tweet URL from user-tweets), writes successful
responses into api_snapshots.json and regenerates the frontend examples.

Usage:  python scripts/capture_snapshots_batch.py batch1
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.core.security import generate_api_key  # noqa: E402
from app.services.supabase_client import get_supabase  # noqa: E402

BASE = os.environ.get("SMOKE_BASE", "https://api.captapi.com")

# Trim huge lists so the generated docs file stays reasonable.
MAX_LIST = 5


def _truncate(value: Any, depth: int = 0) -> Any:
    if isinstance(value, list):
        return [_truncate(v, depth + 1) for v in value[:MAX_LIST if depth else 8]]
    if isinstance(value, dict):
        return {k: _truncate(v, depth + 1) for k, v in value.items()}
    return value


async def call(client: httpx.AsyncClient, slug: str, path: str, params: dict) -> tuple[str, dict]:
    started = time.perf_counter()
    try:
        r = await client.get(f"{BASE}{path}", params=params, timeout=300)
        elapsed = round(time.perf_counter() - started, 1)
        try:
            body = r.json()
        except Exception:  # noqa: BLE001
            body = {"raw": r.text[:300]}
        return slug, {"status": r.status_code, "elapsed": elapsed, "body": body}
    except Exception as e:  # noqa: BLE001
        return slug, {"status": 0, "elapsed": round(time.perf_counter() - started, 1), "body": {"error": str(e)}}


async def run_phase(client: httpx.AsyncClient, tests: list[tuple[str, str, dict]]) -> dict[str, dict]:
    results = await asyncio.gather(*(call(client, slug, path, params) for slug, path, params in tests))
    out = {}
    for slug, res in results:
        ok = 200 <= res["status"] < 300
        print(f"{'PASS' if ok else 'FAIL':4} {res['status']:>3} {res['elapsed']:>6}s  {slug}")
        if not ok:
            print(f"          {json.dumps(res['body'], ensure_ascii=False)[:220]}")
        out[slug] = res
    return out


def batch1_phase1() -> list[tuple[str, str, dict]]:
    return [
        ("twitter-profile", "/v1/twitter/profile", {"url": "https://x.com/nasa"}),
        ("twitter-user-tweets", "/v1/twitter/user-tweets", {"url": "https://x.com/nasa", "limit": 5}),
        ("twitter-search", "/v1/twitter/search", {"q": "artificial intelligence", "limit": 5}),
        ("twitter-community", "/v1/twitter/community", {"url": "https://x.com/i/communities/1493446837214187523"}),
        ("twitter-community-tweets", "/v1/twitter/community-tweets", {"url": "https://x.com/i/communities/1493446837214187523", "limit": 5}),
        ("linkedin-profile", "/v1/linkedin/profile", {"url": "https://www.linkedin.com/in/satyanadella"}),
        ("linkedin-company", "/v1/linkedin/company", {"url": "https://www.linkedin.com/company/microsoft"}),
        ("linkedin-company-posts", "/v1/linkedin/company-posts", {"url": "https://www.linkedin.com/company/microsoft", "limit": 5}),
        ("linkedin-search-posts", "/v1/linkedin/search-posts", {"q": "artificial intelligence", "limit": 5}),
        ("linkedin-ad-library-search-ads", "/v1/ad-library/linkedin/search-ads", {"q": "microsoft", "limit": 5}),
        ("reddit-subreddit-posts", "/v1/reddit/subreddit-posts", {"url": "r/space", "limit": 5}),
        ("reddit-subreddit-details", "/v1/reddit/subreddit-details", {"url": "r/space"}),
        ("reddit-search", "/v1/reddit/search", {"q": "james webb telescope", "limit": 5}),
        ("reddit-subreddit-search", "/v1/reddit/subreddit-search", {"url": "r/space", "q": "moon", "limit": 5}),
    ]


def batch1_phase2(p1: dict[str, dict]) -> list[tuple[str, str, dict]]:
    tests: list[tuple[str, str, dict]] = []

    def data_of(slug: str) -> dict:
        body = p1.get(slug, {}).get("body") or {}
        return body.get("data") or {}

    tweets = data_of("twitter-user-tweets").get("tweets") or data_of("twitter-user-tweets").get("posts") or []
    tweet_url = next((t.get("url") for t in tweets if isinstance(t, dict) and t.get("url")), None)
    if tweet_url:
        tests.append(("twitter-tweet-details", "/v1/twitter/tweet-details", {"url": tweet_url}))
        tests.append(("twitter-transcript", "/v1/twitter/transcript", {"url": tweet_url}))
    else:
        print("!! no tweet url from user-tweets; skipping tweet-details/transcript")

    li_posts = data_of("linkedin-company-posts").get("posts") or []
    li_url = next((p.get("url") for p in li_posts if isinstance(p, dict) and p.get("url")), None)
    if not li_url:
        srch = data_of("linkedin-search-posts").get("results") or data_of("linkedin-search-posts").get("posts") or []
        li_url = next((p.get("url") for p in srch if isinstance(p, dict) and p.get("url")), None)
    if li_url:
        tests.append(("linkedin-post-details", "/v1/linkedin/post-details", {"url": li_url}))
        tests.append(("linkedin-post-transcript", "/v1/linkedin/post-transcript", {"url": li_url}))
    else:
        print("!! no linkedin post url; skipping post-details/transcript")

    li_ads = data_of("linkedin-ad-library-search-ads").get("ads") or data_of("linkedin-ad-library-search-ads").get("results") or []
    ad_url = next((a.get("url") or a.get("adUrl") for a in li_ads if isinstance(a, dict) and (a.get("url") or a.get("adUrl"))), None)
    if ad_url:
        tests.append(("linkedin-ad-library-ad-details", "/v1/ad-library/linkedin/ad-details", {"url": ad_url}))
    else:
        print("!! no linkedin ad url; skipping ad-details")

    rd_posts = data_of("reddit-subreddit-posts").get("posts") or []
    rd_url = next((p.get("url") or p.get("permalink") for p in rd_posts if isinstance(p, dict) and (p.get("url") or p.get("permalink"))), None)
    if rd_url:
        tests.append(("reddit-post-details", "/v1/reddit/post-details", {"url": rd_url}))
        tests.append(("reddit-post-comments", "/v1/reddit/post-comments", {"url": rd_url, "limit": 5}))
        tests.append(("reddit-post-transcript", "/v1/reddit/post-transcript", {"url": rd_url, "limit": 5}))
    else:
        print("!! no reddit post url; skipping post endpoints")

    return tests


def batch2_phase1() -> list[tuple[str, str, dict]]:
    return [
        ("tiktok-profile-region", "/v1/tiktok/profile-region", {"url": "https://www.tiktok.com/@khaby.lame"}),
        ("tiktok-audience-demographics", "/v1/tiktok/audience-demographics", {"url": "https://www.tiktok.com/@khaby.lame"}),
        ("tiktok-search-suggestions", "/v1/tiktok/search-suggestions", {"q": "skincare", "limit": 5}),
        ("tiktok-live", "/v1/tiktok/live", {"url": "https://www.tiktok.com/@espn"}),
        ("tiktok-live-info", "/v1/tiktok/live-info", {"url": "https://www.tiktok.com/@espn"}),
        ("tiktok-popular-creators", "/v1/tiktok/popular-creators", {"country": "US", "limit": 5}),
        ("tiktok-shop-search", "/v1/tiktok-shop/shop-search", {"q": "phone case", "region": "US", "limit": 5}),
        ("tiktok-shop-user-showcase", "/v1/tiktok-shop/user-showcase", {"username": "jeffreestar", "limit": 5}),
        ("tiktok-ad-library-search", "/v1/ad-library/tiktok/search", {"q": "fashion", "limit": 5}),
        ("facebook-ad-library-search", "/v1/ad-library/facebook/search", {"q": "nike", "country": "US", "limit": 5}),
        ("facebook-ad-library-search-companies", "/v1/ad-library/facebook/search-companies", {"q": "nike", "limit": 5}),
        ("facebook-ad-library-company-ads", "/v1/ad-library/facebook/company-ads", {"url": "https://www.facebook.com/nike", "limit": 5}),
        ("google-ad-library-company-ads", "/v1/ad-library/google/company-ads", {"advertiser": "nike", "country": "US", "limit": 5}),
        ("google-ad-library-advertiser-search", "/v1/ad-library/google/advertiser-search", {"q": "nike", "limit": 5}),
        ("google-search", "/v1/google/search", {"q": "best project management software", "limit": 5}),
        ("threads-profile", "/v1/threads/profile", {"url": "@zuck"}),
        ("threads-user-posts", "/v1/threads/user-posts", {"url": "@zuck", "limit": 5}),
        ("threads-search", "/v1/threads/search", {"q": "artificial intelligence", "limit": 5}),
        ("threads-search-users", "/v1/threads/search-users", {"q": "tech", "limit": 5}),
        ("snapchat-user-profile", "/v1/snapchat/user-profile", {"url": "kyliejenner"}),
    ]


def batch2_phase2(p1: dict[str, dict]) -> list[tuple[str, str, dict]]:
    tests: list[tuple[str, str, dict]] = []

    def data_of(slug: str) -> dict:
        body = p1.get(slug, {}).get("body") or {}
        return body.get("data") or {}

    def first_of(slug: str, *list_keys: str) -> dict:
        d = data_of(slug)
        for key in list_keys:
            rows = d.get(key)
            if isinstance(rows, list) and rows:
                return next((r for r in rows if isinstance(r, dict)), {})
        return {}

    product = first_of("tiktok-shop-search", "products", "results")
    product_url = product.get("url") or product.get("productUrl")
    if product_url:
        tests.append(("tiktok-shop-product-details", "/v1/tiktok-shop/product-details", {"url": product_url}))
        tests.append(("tiktok-shop-product-reviews", "/v1/tiktok-shop/product-reviews", {"url": product_url, "limit": 5}))
    else:
        print("!! no tiktok shop product url")
    seller = product.get("seller") or {}
    store_url = (seller.get("url") if isinstance(seller, dict) else None) or product.get("shopUrl") or product.get("storeUrl")
    if store_url:
        tests.append(("tiktok-shop-products", "/v1/tiktok-shop/shop-products", {"url": store_url, "limit": 5}))
    else:
        print("!! no tiktok shop store url")

    tt_ad = first_of("tiktok-ad-library-search", "ads", "results")
    tt_ad_ref = tt_ad.get("url") or tt_ad.get("id")
    if tt_ad_ref:
        tests.append(("tiktok-ad-library-ad-details", "/v1/ad-library/tiktok/ad-details", {"url": str(tt_ad_ref)}))
    else:
        print("!! no tiktok ad id")

    fb_ad = first_of("facebook-ad-library-search", "ads", "results")
    fb_ad_ref = fb_ad.get("url") or fb_ad.get("id")
    if fb_ad_ref:
        tests.append(("facebook-ad-library-ad-details", "/v1/ad-library/facebook/ad-details", {"url": str(fb_ad_ref)}))
        tests.append(("facebook-ad-library-ad-transcript", "/v1/ad-library/facebook/ad-transcript", {"url": str(fb_ad_ref)}))
    else:
        print("!! no facebook ad id")

    g_ad = first_of("google-ad-library-company-ads", "ads", "results")
    g_ref = g_ad.get("url") or g_ad.get("adTransparencyUrl") or g_ad.get("id")
    if g_ref:
        tests.append(("google-ad-library-ad-details", "/v1/ad-library/google/ad-details", {"creative_id": str(g_ref)}))
    else:
        print("!! no google creative url")

    th_post = first_of("threads-user-posts", "posts", "threads")
    th_url = th_post.get("url") or th_post.get("postUrl")
    if th_url:
        tests.append(("threads-post-details", "/v1/threads/post-details", {"url": th_url}))
    else:
        print("!! no threads post url")

    return tests


BATCHES = {
    "batch1": (batch1_phase1, batch1_phase2),
    "batch2": (batch2_phase1, batch2_phase2),
}


async def main() -> None:
    batch = sys.argv[1] if len(sys.argv) > 1 else "batch1"
    phase1_fn, phase2_fn = BATCHES[batch]

    sb = get_supabase()
    users = sb.auth.admin.list_users()
    user = users[0]
    print(f"Target: {BASE} | user: {user.email}")
    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert(
        {"user_id": user.id, "key_hash": key_hash, "key_prefix": prefix, "name": f"capture-{batch}"}
    ).execute()
    key_id = ins.data[0]["id"]

    try:
        async with httpx.AsyncClient(headers={"Authorization": f"Bearer {plain}"}) as client:
            print("--- phase 1")
            p1 = await run_phase(client, phase1_fn())
            print("--- phase 2")
            p2 = await run_phase(client, phase2_fn(p1))
    finally:
        sb.table("api_keys").delete().eq("id", key_id).execute()
        print(f"Revoked temp key {prefix}…")

    snap_path = BACKEND / "api_snapshots.json"
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    updated = []
    for slug, res in {**p1, **p2}.items():
        body = res["body"]
        if not (200 <= res["status"] < 300) or not isinstance(body, dict) or not isinstance(body.get("data"), dict):
            continue
        snap[slug] = {
            "ok": True,
            "status": res["status"],
            "credits": (body.get("meta") or {}).get("creditsUsed"),
            "data": _truncate(body["data"]),
        }
        updated.append(slug)
    snap_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("snapshot updated:", ", ".join(sorted(updated)) or "(none)")

    import subprocess

    subprocess.run([sys.executable, "gen_examples.py"], cwd=BACKEND, check=True)


if __name__ == "__main__":
    asyncio.run(main())
