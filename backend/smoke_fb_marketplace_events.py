"""LIVE smoke test for Facebook Marketplace + Events endpoints.

Creates a temp API key for the first existing user (via Supabase service role
from .env), fires the 3 new Facebook endpoints against the live API, prints
PASS/FAIL with timing + response excerpt, then revokes the key.

NOTE: makes REAL Apify calls and consumes REAL credits.

Run:  python smoke_fb_marketplace_events.py
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
    # Pick a user that actually has credits so we can exercise the Apify calls.
    bals = sb.table("credit_balances").select("user_id, subscription_credits, topup_credits").execute()
    candidates = [b for b in (bals.data or []) if (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0) > 0]
    candidates.sort(key=lambda b: (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0), reverse=True)
    if not candidates:
        print("No user with positive credits found.")
        return
    user_id = candidates[0]["user_id"]
    print("Using user: {}".format(user_id))
    b = candidates[0]
    print("Credits available: {} sub + {} topup".format(b["subscription_credits"], b["topup_credits"]))

    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert({
        "user_id": user_id,
        "key_hash": key_hash,
        "key_prefix": prefix,
        "name": "smoke-fb-marketplace-events",
    }).execute()
    api_key_id = ins.data[0]["id"]
    print("Created temp key: {}... (id={})\n".format(prefix, api_key_id))

    headers = {"Authorization": "Bearer {}".format(plain)}
    results = []

    async with httpx.AsyncClient(headers=headers) as client:
        # 1) Marketplace search
        r1 = await call(client, "FB marketplace-search", "/v1/facebook/marketplace-search", {"q": "bike", "location": "Austin, TX", "limit": 5})
        results.append(r1)

        # 2) Event search
        r2 = await call(client, "FB event-search", "/v1/facebook/event-search", {"q": "comedy", "limit": 5})
        results.append(r2)

        # 3) Event details - reuse an event URL discovered by the search above.
        event_url = None
        try:
            events = json.loads(r2["body"]).get("data", {}).get("events") or []
            for e in events:
                if e.get("url"):
                    event_url = e["url"]
                    break
        except Exception:
            pass
        print("Discovered event url for details: {}\n".format(event_url))
        if event_url:
            r3 = await call(client, "FB event-details", "/v1/facebook/event-details", {"url": event_url})
            results.append(r3)
        else:
            results.append({"name": "FB event-details", "status": 0, "ok": False, "elapsed": 0.0, "excerpt": "SKIPPED: no event url from search", "body": ""})

    print("\n{:<24} {:<5} {:<5} {:<8} EXCERPT".format("NAME", "RES", "CODE", "TIME"))
    print("-" * 140)
    pass_count = 0
    for r in results:
        icon = "PASS" if r["ok"] else "FAIL"
        pass_count += 1 if r["ok"] else 0
        print("{:<24} {:<5} {:<5} {:<7}s {}".format(r["name"], icon, r["status"], r["elapsed"], r["excerpt"]))
    print("-" * 140)
    print("\n{}/{} passed\n".format(pass_count, len(results)))

    bal = sb.table("credit_balances").select("subscription_credits, topup_credits").eq("user_id", user_id).limit(1).execute()
    if bal.data:
        b = bal.data[0]
        print("Credits remaining: {} sub + {} topup".format(b["subscription_credits"], b["topup_credits"]))

    print("\nRevoking temp key...")
    sb.table("api_keys").update({"revoked_at": datetime.utcnow().isoformat()}).eq("id", api_key_id).execute()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
