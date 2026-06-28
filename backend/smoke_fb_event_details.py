"""Targeted LIVE retest for /v1/facebook/event-details after the startUrls fix."""

from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone

import httpx

from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase

BASE = os.environ.get("SMOKE_BASE", "https://api.captapi.com")
EVENT_URL = os.environ.get("EVENT_URL", "https://www.facebook.com/events/1654341112511079/")


async def main() -> None:
    sb = get_supabase()
    bals = sb.table("credit_balances").select("user_id, subscription_credits, topup_credits").execute()
    cands = [b for b in (bals.data or []) if (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0) > 0]
    cands.sort(key=lambda b: (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0), reverse=True)
    if not cands:
        print("No user with positive credits.")
        return
    user_id = cands[0]["user_id"]
    print("Target: {}  user: {}".format(BASE, user_id))

    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert({"user_id": user_id, "key_hash": key_hash, "key_prefix": prefix, "name": "smoke-fb-event-details"}).execute()
    api_key_id = ins.data[0]["id"]

    headers = {"Authorization": "Bearer {}".format(plain)}
    started = time.perf_counter()
    async with httpx.AsyncClient(headers=headers) as client:
        r = await client.get("{}/v1/facebook/event-details".format(BASE), params={"url": EVENT_URL}, timeout=240)
    elapsed = round(time.perf_counter() - started, 1)
    icon = "PASS" if 200 <= r.status_code < 300 else "FAIL"
    print("\nFB event-details  {}  {}  {}s".format(icon, r.status_code, elapsed))
    print(r.text[:600])

    sb.table("api_keys").update({"revoked_at": datetime.now(timezone.utc).isoformat()}).eq("id", api_key_id).execute()
    print("\nRevoked temp key.")


if __name__ == "__main__":
    asyncio.run(main())
