"""Smoke test for ALL YouTube endpoints against a single video URL.

Creates a temp API key for the first existing user, fires every endpoint
in parallel, prints PASS/FAIL with timing + response excerpt, then revokes
the key.
"""

from __future__ import annotations

import asyncio
import json
import time

import httpx

from app.core.config import get_settings
from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase

VIDEO_URL = "https://www.youtube.com/watch?v=gKHe12T6GMY&list=RDgKHe12T6GMY&start_radio=1"
BASE = "http://localhost:8000"


async def call(client: httpx.AsyncClient, name: str, path: str, params: dict) -> dict:
    started = time.perf_counter()
    try:
        r = await client.get(f"{BASE}{path}", params=params, timeout=120)
        elapsed = time.perf_counter() - started
        ok = 200 <= r.status_code < 300
        body = r.text
        try:
            parsed = json.loads(body)
            excerpt = json.dumps(parsed, ensure_ascii=False)[:200]
        except Exception:
            excerpt = body[:200]
        return {
            "name": name,
            "status": r.status_code,
            "ok": ok,
            "elapsed": round(elapsed, 2),
            "excerpt": excerpt,
        }
    except Exception as e:
        return {
            "name": name,
            "status": 0,
            "ok": False,
            "elapsed": round(time.perf_counter() - started, 2),
            "excerpt": f"EXCEPTION: {e}",
        }


async def main() -> None:
    sb = get_supabase()

    users = sb.auth.admin.list_users()
    if not users:
        print("No users found. Sign up first.")
        return
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
        "name": "smoke-test-temp",
    }).execute()
    api_key_id = ins.data[0]["id"]
    print(f"Created temp key: {prefix}... (id={api_key_id})")

    headers = {"Authorization": f"Bearer {plain}"}

    tests = [
        ("video-details",       "/v1/youtube/video-details",       {"url": VIDEO_URL}),
        ("transcript",          "/v1/youtube/transcript",          {"url": VIDEO_URL}),
        ("summarize",           "/v1/youtube/summarize",           {"url": VIDEO_URL}),
        ("comments",            "/v1/youtube/comments",            {"url": VIDEO_URL, "limit": 5}),
        ("video-download",      "/v1/youtube/video-download",      {"url": VIDEO_URL}),
        ("search",              "/v1/youtube/search",              {"q": "tech tutorial", "limit": 5}),
        ("shorts/transcript",   "/v1/youtube/shorts/transcript",   {"url": VIDEO_URL}),
        ("shorts/summarize",    "/v1/youtube/shorts/summarize",    {"url": VIDEO_URL}),
        ("shorts/video-details","/v1/youtube/shorts/video-details",{"url": VIDEO_URL}),
        ("shorts/comments",     "/v1/youtube/shorts/comments",     {"url": VIDEO_URL, "limit": 5}),
    ]

    print(f"\nRunning {len(tests)} endpoints in parallel...\n")
    started_all = time.perf_counter()
    async with httpx.AsyncClient(headers=headers) as client:
        results = await asyncio.gather(*[call(client, n, p, q) for n, p, q in tests])
    total = time.perf_counter() - started_all

    print(f"\n{'NAME':<24} {'STATUS':<8} {'TIME':<8} EXCERPT")
    print("-" * 110)
    pass_count = 0
    for r in results:
        icon = "PASS" if r["ok"] else "FAIL"
        if r["ok"]:
            pass_count += 1
        print(f"{r['name']:<24} {icon:<4} {r['status']:<3} {r['elapsed']:<7}s {r['excerpt']}")
    print("-" * 110)
    print(f"{pass_count}/{len(tests)} passed in {total:.1f}s total")

    print(f"\nRevoking temp key...")
    from datetime import datetime
    sb.table("api_keys").update({"revoked_at": datetime.utcnow().isoformat()}).eq(
        "id", api_key_id
    ).execute()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
