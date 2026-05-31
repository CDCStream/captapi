"""LIVE smoke test for the newly added endpoints against api.captapi.com.

Creates a temp API key for the first existing user (via Supabase service role
from .env), fires every NEW endpoint against the live API, prints PASS/FAIL
with timing + response excerpt, then revokes the key.

NOTE: this makes REAL Apify calls and consumes REAL credits. The new actors
(coregent followers/following, clockworks sound, apify tagged) must be
available in the deployed environment.

Run:  python smoke_new_live.py
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

TIKTOK_VIDEO = "https://www.tiktok.com/@charlidamelio/video/7228896391451037994"
TIKTOK_PROFILE = "https://www.tiktok.com/@charlidamelio"
TIKTOK_MUSIC = "https://www.tiktok.com/music/a-negroni-sbagliato-w-prosecco-l-hbo-max-7149523537730997035"

INSTAGRAM_PROFILE = "https://www.instagram.com/nasa/"
INSTAGRAM_AUDIO = "https://www.instagram.com/reels/audio/1053894982231129/"

YOUTUBE_CHANNEL = "https://www.youtube.com/@MrBeast"


async def call(client: httpx.AsyncClient, name: str, path: str, params: dict) -> dict:
    started = time.perf_counter()
    try:
        r = await client.get("{}{}".format(BASE, path), params=params, timeout=180)
        elapsed = time.perf_counter() - started
        ok = 200 <= r.status_code < 300
        body = r.text
        try:
            parsed = json.loads(body)
            excerpt = json.dumps(parsed, ensure_ascii=False)[:200]
        except Exception:
            excerpt = body[:200]
        return {"name": name, "status": r.status_code, "ok": ok, "elapsed": round(elapsed, 1), "excerpt": excerpt, "body": body}
    except Exception as e:  # noqa: BLE001
        return {"name": name, "status": 0, "ok": False, "elapsed": round(time.perf_counter() - started, 1), "excerpt": "EXCEPTION: {}".format(e), "body": ""}


async def main() -> None:
    sb = get_supabase()

    users = sb.auth.admin.list_users()
    if not users:
        print("No users found. Sign up first.")
        return
    user = users[0]
    user_id = user.id
    print("Target: {}".format(BASE))
    print("Using user: {} ({})".format(user.email, user_id))

    bal = sb.table("credit_balances").select("subscription_credits, topup_credits").eq("user_id", user_id).limit(1).execute()
    if bal.data:
        b = bal.data[0]
        print("Credits available: {} sub + {} topup".format(b["subscription_credits"], b["topup_credits"]))

    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert({
        "user_id": user_id,
        "key_hash": key_hash,
        "key_prefix": prefix,
        "name": "smoke-new-live",
    }).execute()
    api_key_id = ins.data[0]["id"]
    print("Created temp key: {}... (id={})\n".format(prefix, api_key_id))

    headers = {"Authorization": "Bearer {}".format(plain)}

    async with httpx.AsyncClient(headers=headers) as client:
        # comment-replies needs a real comment_id -> fetch one first.
        comment_id = None
        pre = await call(client, "TT comments (prefetch)", "/v1/tiktok/comments", {"url": TIKTOK_VIDEO, "limit": 5})
        try:
            cdata = json.loads(pre["body"]).get("data", {})
            comments = cdata.get("comments") or []
            if comments:
                comment_id = comments[0].get("id")
        except Exception:
            pass
        print("Prefetched comment_id: {}\n".format(comment_id))

        tests = [
            ("TT channel-posts", "/v1/tiktok/channel-posts", {"url": TIKTOK_PROFILE, "limit": 5}),
            ("TT user-followers", "/v1/tiktok/user-followers", {"url": TIKTOK_PROFILE, "limit": 10}),
            ("TT user-followings", "/v1/tiktok/user-followings", {"url": TIKTOK_PROFILE, "limit": 10}),
            ("TT music-posts", "/v1/tiktok/music-posts", {"url": TIKTOK_MUSIC, "limit": 5}),
            ("IG tagged-posts", "/v1/instagram/tagged-posts", {"url": INSTAGRAM_PROFILE, "limit": 5}),
            ("IG music-posts", "/v1/instagram/music-posts", {"url": INSTAGRAM_AUDIO, "limit": 5}),
            ("YT channel-shorts", "/v1/youtube/channel-shorts", {"url": YOUTUBE_CHANNEL, "limit": 5}),
            ("YT channel-streams", "/v1/youtube/channel-streams", {"url": YOUTUBE_CHANNEL, "limit": 5}),
            ("YT hashtag-search", "/v1/youtube/hashtag-search", {"q": "gaming", "limit": 5}),
        ]
        if comment_id:
            tests.insert(1, ("TT comment-replies", "/v1/tiktok/comment-replies", {"url": TIKTOK_VIDEO, "comment_id": comment_id, "limit": 10}))

        print("Running {} endpoints in parallel against live API...\n".format(len(tests)))
        started_all = time.perf_counter()
        results = await asyncio.gather(*[call(client, n, p, q) for n, p, q in tests])
        total = time.perf_counter() - started_all

    print("\n{:<22} {:<5} {:<5} {:<8} EXCERPT".format("NAME", "RES", "CODE", "TIME"))
    print("-" * 130)
    pass_count = 0
    for r in results:
        icon = "PASS" if r["ok"] else "FAIL"
        pass_count += 1 if r["ok"] else 0
        print("{:<22} {:<5} {:<5} {:<7}s {}".format(r["name"], icon, r["status"], r["elapsed"], r["excerpt"]))
    print("-" * 130)
    print("\n{}/{} passed in {:.1f}s total\n".format(pass_count, len(results), total))

    bal = sb.table("credit_balances").select("subscription_credits, topup_credits").eq("user_id", user_id).limit(1).execute()
    if bal.data:
        b = bal.data[0]
        print("Credits remaining: {} sub + {} topup".format(b["subscription_credits"], b["topup_credits"]))

    print("\nRevoking temp key...")
    sb.table("api_keys").update({"revoked_at": datetime.utcnow().isoformat()}).eq("id", api_key_id).execute()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
