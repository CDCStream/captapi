"""Smoke test for ALL endpoints across YouTube / TikTok / Instagram / Facebook.

Creates a temp API key, fires every endpoint in parallel, prints results.
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime

import httpx

from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase

BASE = "http://localhost:8000"

YOUTUBE_VIDEO = "https://www.youtube.com/watch?v=gKHe12T6GMY"
YOUTUBE_CHANNEL = "https://www.youtube.com/@MrBeast"
YOUTUBE_PLAYLIST = "https://www.youtube.com/playlist?list=PLM4u6gbmK0Y6BVTwsCwWqz2yh4HpRG6c2"

TIKTOK_VIDEO = "https://www.tiktok.com/@charlidamelio/video/7228896391451037994"
TIKTOK_PROFILE = "https://www.tiktok.com/@charlidamelio"

INSTAGRAM_POST = "https://www.instagram.com/p/CY4qkbDONkU/"
INSTAGRAM_REEL = "https://www.instagram.com/reel/CzKZqfdN5j8/"
INSTAGRAM_PROFILE = "https://www.instagram.com/nasa/"

FACEBOOK_PAGE = "https://www.facebook.com/Meta"
FACEBOOK_POST = "https://www.facebook.com/Meta/posts/pfbid02kJZ5Q5kBpRfh3qN5wHGcQXLfRZNbCSWXP9rmZxnHt1XzqRGm2wXTAPb1WXrQjqzkl"


async def call(client: httpx.AsyncClient, name: str, path: str, params: dict) -> dict:
    started = time.perf_counter()
    try:
        r = await client.get(f"{BASE}{path}", params=params, timeout=180)
        elapsed = time.perf_counter() - started
        ok = 200 <= r.status_code < 300
        body = r.text
        try:
            parsed = json.loads(body)
            excerpt = json.dumps(parsed, ensure_ascii=False)[:180]
        except Exception:
            excerpt = body[:180]
        return {
            "name": name,
            "status": r.status_code,
            "ok": ok,
            "elapsed": round(elapsed, 1),
            "excerpt": excerpt,
        }
    except Exception as e:
        return {
            "name": name,
            "status": 0,
            "ok": False,
            "elapsed": round(time.perf_counter() - started, 1),
            "excerpt": f"EXCEPTION: {e}",
        }


async def main() -> None:
    sb = get_supabase()

    users = sb.auth.admin.list_users()
    user = users[0]
    user_id = user.id
    print(f"Using user: {user.email} ({user_id})")

    bal = sb.table("credit_balances").select("subscription_credits, topup_credits").eq(
        "user_id", user_id
    ).limit(1).execute()
    if bal.data:
        b = bal.data[0]
        print(f"Credits available: {b['subscription_credits']} sub + {b['topup_credits']} topup")

    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert({
        "user_id": user_id,
        "key_hash": key_hash,
        "key_prefix": prefix,
        "name": "smoke-test-all",
    }).execute()
    api_key_id = ins.data[0]["id"]
    print(f"Created temp key: {prefix}... (id={api_key_id})\n")

    headers = {"Authorization": f"Bearer {plain}"}

    tests = [
        # ---------- TIKTOK ----------
        ("TT video-details",      "/v1/tiktok/video-details",     {"url": TIKTOK_VIDEO}),
        ("TT transcript",         "/v1/tiktok/transcript",        {"url": TIKTOK_VIDEO}),
        ("TT summarize",          "/v1/tiktok/summarize",         {"url": TIKTOK_VIDEO}),
        ("TT comments",           "/v1/tiktok/comments",          {"url": TIKTOK_VIDEO, "limit": 5}),
        ("TT channel-details",    "/v1/tiktok/channel-details",   {"url": TIKTOK_PROFILE}),
        ("TT search",             "/v1/tiktok/search",            {"q": "comedy", "limit": 3}),
        ("TT video-download",     "/v1/tiktok/video-download",    {"url": TIKTOK_VIDEO}),
        # ---------- INSTAGRAM ----------
        ("IG details",            "/v1/instagram/details",        {"url": INSTAGRAM_POST}),
        ("IG transcript",         "/v1/instagram/transcript",     {"url": INSTAGRAM_REEL}),
        ("IG summarize",          "/v1/instagram/summarize",      {"url": INSTAGRAM_REEL}),
        ("IG comments",           "/v1/instagram/comments",       {"url": INSTAGRAM_REEL, "limit": 5}),
        ("IG channel-details",    "/v1/instagram/channel-details",{"url": INSTAGRAM_PROFILE}),
        ("IG channel-posts",      "/v1/instagram/channel-posts",  {"url": INSTAGRAM_PROFILE, "limit": 5}),
        ("IG channel-reels",      "/v1/instagram/channel-reels",  {"url": INSTAGRAM_PROFILE, "limit": 5}),
        ("IG reels-search",       "/v1/instagram/reels-search",   {"q": "travel", "limit": 5}),
        ("IG video-download",     "/v1/instagram/video-download", {"url": INSTAGRAM_REEL + "?v=2"}),
        # ---------- FACEBOOK ----------
        ("FB details",            "/v1/facebook/details",         {"url": FACEBOOK_POST}),
        ("FB transcript",         "/v1/facebook/transcript",      {"url": FACEBOOK_POST}),
        ("FB summarize",          "/v1/facebook/summarize",       {"url": FACEBOOK_POST}),
        ("FB comments",           "/v1/facebook/comments",        {"url": FACEBOOK_POST, "limit": 5}),
        ("FB page-details",       "/v1/facebook/page-details",    {"url": FACEBOOK_PAGE}),
    ]

    print(f"Running {len(tests)} endpoints in parallel...\n")
    started_all = time.perf_counter()
    async with httpx.AsyncClient(headers=headers) as client:
        results = await asyncio.gather(*[call(client, n, p, q) for n, p, q in tests])
    total = time.perf_counter() - started_all

    print(f"\n{'NAME':<24} {'RES':<5} {'CODE':<5} {'TIME':<7} EXCERPT")
    print("-" * 130)
    pass_count = 0
    for r in results:
        icon = "PASS" if r["ok"] else "FAIL"
        if r["ok"]:
            pass_count += 1
        print(f"{r['name']:<24} {icon:<4} {r['status']:<4} {r['elapsed']:<6}s {r['excerpt']}")
    print("-" * 130)
    print(f"\n{pass_count}/{len(tests)} passed in {total:.1f}s total\n")

    bal = sb.table("credit_balances").select("subscription_credits, topup_credits").eq(
        "user_id", user_id
    ).limit(1).execute()
    if bal.data:
        b = bal.data[0]
        print(f"Credits remaining: {b['subscription_credits']} sub + {b['topup_credits']} topup")

    print(f"\nRevoking temp key...")
    sb.table("api_keys").update({"revoked_at": datetime.utcnow().isoformat()}).eq(
        "id", api_key_id
    ).execute()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
