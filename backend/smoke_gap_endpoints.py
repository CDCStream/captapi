"""LIVE smoke test for the same-platform gap endpoints (batch 1+2+3).

Picks the existing user with the most credits (via Supabase service role from
.env), creates a temp API key, fires every new gap endpoint against the live
API in parallel, prints PASS/FAIL with timing + response excerpt, then revokes
the key.

NOTE: makes REAL Apify calls and consumes REAL credits.

Run:  python smoke_gap_endpoints.py
      SMOKE_BASE=https://api.captapi.com  (default)
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime

import httpx

from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase

BASE = os.environ.get("SMOKE_BASE", "https://api.captapi.com")

# Representative live targets.
YT_VIDEO = "https://www.youtube.com/watch?v=kJQP7kiw5Fk"
REDDIT_SUB = "https://www.reddit.com/r/programming/"
PIN_BOARD = "https://www.pinterest.com/nasa/learn-with-nasa/"
PIN_PROFILE = "https://www.pinterest.com/nasa/"
FB_PROFILE = "https://www.facebook.com/nasa"
IG_PROFILE = "https://www.instagram.com/nasa/"
THREADS_Q = "ai"
TIKTOK_PROFILE = "https://www.tiktok.com/@charlidamelio"
TW_COMMUNITY = "https://x.com/i/communities/1493446837214187523"
FB_MARKET_ITEM = "https://www.facebook.com/marketplace/item/1007141702067295/"


async def call(client: httpx.AsyncClient, name: str, path: str, params: dict) -> dict:
    started = time.perf_counter()
    try:
        r = await client.get("{}{}".format(BASE, path), params=params, timeout=240)
        elapsed = time.perf_counter() - started
        ok = 200 <= r.status_code < 300
        body = r.text
        try:
            parsed = json.loads(body)
            excerpt = json.dumps(parsed, ensure_ascii=False)[:240]
        except Exception:
            excerpt = body[:240]
        return {"name": name, "status": r.status_code, "ok": ok, "elapsed": round(elapsed, 1), "excerpt": excerpt, "body": body}
    except Exception as e:  # noqa: BLE001
        return {"name": name, "status": 0, "ok": False, "elapsed": round(time.perf_counter() - started, 1), "excerpt": "EXCEPTION: {}".format(e), "body": ""}


async def main() -> None:
    sb = get_supabase()

    print("Target: {}".format(BASE))
    bals = sb.table("credit_balances").select("user_id, subscription_credits, topup_credits").execute()
    candidates = [b for b in (bals.data or []) if (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0) > 0]
    candidates.sort(key=lambda b: (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0), reverse=True)
    if not candidates:
        print("No user with positive credits found.")
        return
    user_id = candidates[0]["user_id"]
    b = candidates[0]
    print("Using user: {}".format(user_id))
    print("Credits available: {} sub + {} topup".format(b["subscription_credits"], b["topup_credits"]))

    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert({
        "user_id": user_id,
        "key_hash": key_hash,
        "key_prefix": prefix,
        "name": "smoke-gap-endpoints",
    }).execute()
    api_key_id = ins.data[0]["id"]
    print("Created temp key: {}... (id={})\n".format(prefix, api_key_id))

    headers = {"Authorization": "Bearer {}".format(plain)}

    tests = [
        # Batch 1
        ("YT video-sponsors", "/v1/youtube/video-sponsors", {"url": YT_VIDEO}),
        ("Reddit subreddit-details", "/v1/reddit/subreddit-details", {"url": REDDIT_SUB}),
        ("Pinterest board", "/v1/pinterest/board", {"url": PIN_BOARD, "limit": 5}),
        ("FB profile-photos", "/v1/facebook/profile-photos", {"url": FB_PROFILE, "limit": 5}),
        # Batch 2
        ("IG basic-profile", "/v1/instagram/basic-profile", {"userId": IG_PROFILE}),
        ("Reddit subreddit-search", "/v1/reddit/subreddit-search", {"url": REDDIT_SUB, "q": "rust", "limit": 5}),
        ("Threads search", "/v1/threads/search", {"q": THREADS_Q, "limit": 5}),
        ("Threads search-users", "/v1/threads/search-users", {"q": "nasa", "limit": 5}),
        ("TikTok live", "/v1/tiktok/live", {"url": TIKTOK_PROFILE}),
        ("Pinterest user-boards", "/v1/pinterest/user-boards", {"url": PIN_PROFILE, "limit": 5}),
        # Batch 3
        ("Twitter community", "/v1/twitter/community", {"url": TW_COMMUNITY}),
        ("Twitter community-tweets", "/v1/twitter/community-tweets", {"url": TW_COMMUNITY, "limit": 5}),
        ("FB marketplace-item", "/v1/facebook/marketplace-item", {"url": FB_MARKET_ITEM}),
        ("FB ad search-companies", "/v1/ad-library/facebook/search-companies", {"q": "nike", "limit": 5}),
    ]

    print("Running {} endpoints in parallel against live API...\n".format(len(tests)))
    started_all = time.perf_counter()
    async with httpx.AsyncClient(headers=headers) as client:
        results = await asyncio.gather(*[call(client, n, p, q) for n, p, q in tests])
    total = time.perf_counter() - started_all

    print("\n{:<26} {:<5} {:<5} {:<8} EXCERPT".format("NAME", "RES", "CODE", "TIME"))
    print("-" * 150)
    pass_count = 0
    for r in results:
        icon = "PASS" if r["ok"] else "FAIL"
        pass_count += 1 if r["ok"] else 0
        print("{:<26} {:<5} {:<5} {:<7}s {}".format(r["name"], icon, r["status"], r["elapsed"], r["excerpt"]))
    print("-" * 150)
    print("\n{}/{} passed in {:.1f}s total\n".format(pass_count, len(results), total))

    bal = sb.table("credit_balances").select("subscription_credits, topup_credits").eq("user_id", user_id).limit(1).execute()
    if bal.data:
        bb = bal.data[0]
        print("Credits remaining: {} sub + {} topup".format(bb["subscription_credits"], bb["topup_credits"]))

    print("\nRevoking temp key...")
    sb.table("api_keys").update({"revoked_at": datetime.utcnow().isoformat()}).eq("id", api_key_id).execute()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
