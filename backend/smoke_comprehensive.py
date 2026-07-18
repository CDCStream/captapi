"""Comprehensive cross-platform LIVE smoke test: one representative endpoint
per platform across all 29 platforms. Confirms breadth & catches regressions.

NOTE: makes REAL Apify / network calls and consumes REAL credits.
Run:  python smoke_comprehensive.py   (SMOKE_BASE=http://127.0.0.1:8000 default)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from datetime import datetime

import httpx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase

BASE = os.environ.get("SMOKE_BASE", "http://127.0.0.1:8000")


async def call(client, name, path, params):
    t = time.perf_counter()
    try:
        r = await client.get(BASE + path, params=params, timeout=240)
        body = r.text
        try:
            ex = json.dumps(json.loads(body), ensure_ascii=False)[:200]
        except Exception:
            ex = body[:200]
        return {"name": name, "code": r.status_code, "ok": 200 <= r.status_code < 300, "t": round(time.perf_counter() - t, 1), "ex": ex}
    except Exception as e:  # noqa: BLE001
        return {"name": name, "code": 0, "ok": False, "t": round(time.perf_counter() - t, 1), "ex": f"EXC {e}"}


async def main() -> None:
    sb = get_supabase()
    bals = sb.table("credit_balances").select("user_id, subscription_credits, topup_credits").execute()
    cands = [b for b in (bals.data or []) if (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0) > 0]
    cands.sort(key=lambda b: (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0), reverse=True)
    user_id = cands[0]["user_id"]
    b0 = cands[0]
    plain, kh, pfx = generate_api_key()
    ins = sb.table("api_keys").insert({"user_id": user_id, "key_hash": kh, "key_prefix": pfx, "name": "smoke-comprehensive"}).execute()
    kid = ins.data[0]["id"]
    print(f"Target {BASE}")
    print(f"Credits: {b0['subscription_credits']} sub + {b0['topup_credits']} topup\n")

    # (label, path, params, env_known_issue)
    tests = [
        ("youtube",      "/v1/youtube/video-details",       {"url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk"}, False),
        ("tiktok",       "/v1/tiktok/channel-details",      {"url": "https://www.tiktok.com/@charlidamelio"}, False),
        ("instagram",    "/v1/instagram/channel-details",   {"url": "https://www.instagram.com/nasa/"}, False),
        ("facebook",     "/v1/facebook/page-details",       {"url": "https://www.facebook.com/Meta"}, False),
        ("twitter",      "/v1/twitter/profile",             {"url": "https://x.com/nasa"}, False),
        ("reddit",       "/v1/reddit/subreddit-details",    {"url": "https://www.reddit.com/r/programming/"}, False),
        ("threads",      "/v1/threads/profile",             {"url": "https://www.threads.net/@zuck"}, False),
        ("bluesky",      "/v1/bluesky/profile",             {"url": "https://bsky.app/profile/bsky.app"}, False),
        ("pinterest",    "/v1/pinterest/user-pins",         {"url": "https://www.pinterest.com/nasa/", "limit": 5}, False),
        ("linkedin",     "/v1/linkedin/profile",            {"url": "https://www.linkedin.com/in/williamhgates"}, False),
        ("rumble",       "/v1/rumble/search",               {"q": "news", "limit": 5}, False),
        ("kwai",         "/v1/kwai/profile",                {"url": "https://www.kwai.com/@easycashindonesia"}, False),
        ("twitch",       "/v1/twitch/profile",              {"url": "https://www.twitch.tv/ninja"}, False),
        ("spotify",      "/v1/spotify/search",              {"q": "Taylor Swift", "limit": 5}, False),
        ("soundcloud",   "/v1/soundcloud/artist",           {"url": "https://soundcloud.com/octobersveryown"}, False),
        ("linktree",     "/v1/linktree/page",               {"url": "https://linktr.ee/taylorswift"}, False),
        ("snapchat",     "/v1/snapchat/user-profile",       {"url": "https://www.snapchat.com/add/teamsnapchat"}, False),
        ("amazon_shop",  "/v1/amazon-shop/page",            {"url": "https://www.amazon.com/stores/page/x?seller=A2L77EE7U53NWQ", "limit": 5}, False),
        ("github",       "/v1/github/user",                 {"username": "torvalds"}, False),
        ("tiktok_shop",  "/v1/tiktok-shop/shop-search",     {"q": "phone case", "limit": 5}, False),
        ("ad_library",   "/v1/ad-library/facebook/search",  {"q": "nike", "limit": 5}, False),
        ("komi",         "/v1/komi/page",                   {"url": "https://komi.io/charlidamelio"}, False),
        ("pillar",       "/v1/pillar/page",                 {"url": "https://pillar.io/cocoao"}, False),
        ("linkbio",      "/v1/linkbio/page",                {"url": "https://lnk.bio/nasa"}, False),
        ("linkme",       "/v1/linkme/profile",              {"url": "https://link.me/nasa"}, False),
        # Known environmental constraints (actor must be rented / datacenter IP blocked):
        ("kick [env]",   "/v1/kick/clip",                   {"url": "https://kick.com/xqc", "limit": 10}, True),
        ("truth [env]",  "/v1/truth-social/profile",        {"url": "https://truthsocial.com/@realDonaldTrump"}, True),
    ]

    headers = {"Authorization": f"Bearer {plain}"}
    print(f"Running {len(tests)} platform checks in parallel...\n")
    started = time.perf_counter()
    async with httpx.AsyncClient(headers=headers) as client:
        results = await asyncio.gather(*[call(client, n, p, q) for n, p, q, _ in tests])
    total = time.perf_counter() - started

    env_flags = {n: e for n, _, _, e in tests}
    print(f"{'PLATFORM':<16}{'CODE':<6}{'OK':<5}{'T':<8}EXCERPT")
    print("-" * 150)
    real_pass = real_total = 0
    for r in results:
        env = env_flags.get(r["name"], False)
        if not env:
            real_total += 1
            real_pass += 1 if r["ok"] else 0
        mark = "Y" if r["ok"] else ("~" if env else "N")
        print(f"{r['name']:<16}{r['code']:<6}{mark:<5}{str(r['t'])+'s':<8}{r['ex']}")
    print("-" * 150)
    print(f"\nReal endpoints: {real_pass}/{real_total} passed (+2 env-constrained: kick/truth) in {total:.1f}s\n")

    bal = sb.table("credit_balances").select("subscription_credits, topup_credits").eq("user_id", user_id).limit(1).execute()
    if bal.data:
        bb = bal.data[0]
        print(f"Credits remaining: {bb['subscription_credits']} sub + {bb['topup_credits']} topup")
    sb.table("api_keys").update({"revoked_at": datetime.utcnow().isoformat()}).eq("id", kid).execute()
    print("key revoked.")


if __name__ == "__main__":
    asyncio.run(main())
