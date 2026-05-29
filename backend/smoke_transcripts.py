"""Smart transcript smoke test: use our search APIs to find captioned content
dynamically, then test transcript/summarize on those URLs."""

from __future__ import annotations

import asyncio
import json
import sys
import time
from datetime import datetime

import httpx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase

BASE = "http://localhost:8000"

FACEBOOK_VIDEO_CANDIDATES = [
    "https://www.facebook.com/watch?v=10153231379946509",
    "https://www.facebook.com/BBCNews/videos/",
    "https://www.facebook.com/cnn/videos/",
]


async def main() -> None:
    sb = get_supabase()
    user = sb.auth.admin.list_users()[0]
    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert({
        "user_id": user.id,
        "key_hash": key_hash,
        "key_prefix": prefix,
        "name": "smoke-transcripts",
    }).execute()
    api_key_id = ins.data[0]["id"]
    print(f"Temp key: {prefix}...\n")

    headers = {"Authorization": f"Bearer {plain}"}
    async with httpx.AsyncClient(headers=headers, timeout=180) as client:

        print("=" * 80)
        print("STEP 1: Find captioned TikTok via /v1/tiktok/search")
        print("=" * 80)
        for query in ["english tutorial", "motivation speech", "podcast clip", "tedx"]:
            print(f"\n  Searching TikTok for: {query!r}")
            r = await client.get(f"{BASE}/v1/tiktok/search", params={"q": query, "limit": 5})
            if r.status_code != 200:
                print(f"  [search failed] {r.status_code} {r.text[:200]}")
                continue
            data = r.json()["data"]
            results = data.get("results", [])
            print(f"  Got {len(results)} results")
            tiktok_url = None
            for res in results:
                u = res.get("url")
                if u and "/video/" in u:
                    tiktok_url = u
                    print(f"  Trying: {u}")
                    tr = await client.get(
                        f"{BASE}/v1/tiktok/transcript", params={"url": u}
                    )
                    if tr.status_code == 200:
                        td = tr.json()["data"]
                        wc = td.get("wordCount", 0)
                        if wc > 5:
                            print(f"  [OK] TRANSCRIPT FOUND ({wc} words)")
                            print(f"    Excerpt: {td.get('transcript','')[:200]}")
                            sr = await client.get(
                                f"{BASE}/v1/tiktok/summarize", params={"url": u}
                            )
                            print(f"  [OK] Summarize: {sr.status_code} | {sr.text[:200]}")
                            tiktok_url = u
                            break
                    else:
                        print(f"  [no caption] {tr.status_code}")
            if tiktok_url and tr.status_code == 200 and tr.json()["data"].get("wordCount", 0) > 5:
                break

        print("\n" + "=" * 80)
        print("STEP 2: Find captioned Instagram Reel via /v1/instagram/reels-search")
        print("=" * 80)
        for query in ["learnenglishdaily", "englishspeak", "publicspeaking", "interviewtips"]:
            print(f"\n  Searching IG Reels for: {query!r}")
            r = await client.get(
                f"{BASE}/v1/instagram/reels-search", params={"q": query, "limit": 5}
            )
            if r.status_code != 200:
                print(f"  [search failed] {r.status_code} {r.text[:200]}")
                continue
            data = r.json()["data"]
            results = data.get("results", [])
            print(f"  Got {len(results)} results")
            found = False
            for res in results:
                u = res.get("url")
                if u and ("/reel/" in u or "/p/" in u):
                    print(f"  Trying: {u}")
                    tr = await client.get(
                        f"{BASE}/v1/instagram/transcript", params={"url": u}
                    )
                    if tr.status_code == 200:
                        td = tr.json()["data"]
                        wc = td.get("wordCount", 0)
                        if wc > 5:
                            print(f"  [OK] TRANSCRIPT FOUND ({wc} words)")
                            print(f"    Excerpt: {td.get('transcript','')[:200]}")
                            sr = await client.get(
                                f"{BASE}/v1/instagram/summarize", params={"url": u}
                            )
                            print(f"  [OK] Summarize: {sr.status_code} | {sr.text[:200]}")
                            found = True
                            break
                    else:
                        print(f"  [no caption] {tr.status_code}")
            if found:
                break

        print("\n" + "=" * 80)
        print("STEP 3: Test Facebook video transcript with known video URLs")
        print("=" * 80)
        for u in FACEBOOK_VIDEO_CANDIDATES:
            print(f"\n  Trying: {u}")
            tr = await client.get(f"{BASE}/v1/facebook/transcript", params={"url": u})
            if tr.status_code == 200:
                td = tr.json()["data"]
                wc = td.get("wordCount", 0)
                print(f"  [OK] TRANSCRIPT ({wc} words): {td.get('transcript','')[:200]}")
                sr = await client.get(f"{BASE}/v1/facebook/summarize", params={"url": u})
                print(f"  [OK] Summarize: {sr.status_code} | {sr.text[:200]}")
                break
            else:
                print(f"  [skip] {tr.status_code} {tr.text[:200]}")

    bal = sb.table("credit_balances").select("subscription_credits").eq(
        "user_id", user.id
    ).limit(1).execute()
    print(f"\nCredits remaining: {bal.data[0]['subscription_credits']}")

    sb.table("api_keys").update({"revoked_at": datetime.utcnow().isoformat()}).eq(
        "id", api_key_id
    ).execute()
    print("Temp key revoked. Done.")


if __name__ == "__main__":
    asyncio.run(main())
