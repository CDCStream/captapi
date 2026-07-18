"""Retest only the endpoints we just fixed: Kwai (numeric IDs), lnk.bio,
komi/pillar (graceful), and Kick (now 502 not 500)."""

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

KWAI_PROFILE = "https://www.kwai.com/@easycashindonesia"
KWAI_VIDEO = "https://www.kwai.com/@easycashindonesia/video/5238962376325675745"
LINKBIO = "https://lnk.bio/nasa"
KOMI = "https://komi.io/charlidamelio"
PILLAR = "https://pillar.io/cocoao"
LINKME = "https://link.me/nasa"
KICK = "https://kick.com/xqc"


async def call(client, name, path, params):
    t = time.perf_counter()
    try:
        r = await client.get(BASE + path, params=params, timeout=240)
        body = r.text
        try:
            ex = json.dumps(json.loads(body), ensure_ascii=False)[:300]
        except Exception:
            ex = body[:300]
        return {"name": name, "code": r.status_code, "ok": 200 <= r.status_code < 300, "t": round(time.perf_counter() - t, 1), "ex": ex}
    except Exception as e:  # noqa: BLE001
        return {"name": name, "code": 0, "ok": False, "t": round(time.perf_counter() - t, 1), "ex": f"EXC {e}"}


async def main() -> None:
    sb = get_supabase()
    bals = sb.table("credit_balances").select("user_id, subscription_credits, topup_credits").execute()
    cands = [b for b in (bals.data or []) if (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0) > 0]
    cands.sort(key=lambda b: (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0), reverse=True)
    user_id = cands[0]["user_id"]
    plain, kh, pfx = generate_api_key()
    ins = sb.table("api_keys").insert({"user_id": user_id, "key_hash": kh, "key_prefix": pfx, "name": "smoke-retest"}).execute()
    kid = ins.data[0]["id"]
    print(f"Target {BASE}, key {pfx}...\n")

    headers = {"Authorization": f"Bearer {plain}"}
    tests = [
        ("kwai profile", "/v1/kwai/profile", {"url": KWAI_PROFILE}),
        ("kwai user-posts", "/v1/kwai/user-posts", {"url": KWAI_PROFILE, "limit": 5}),
        ("kwai post", "/v1/kwai/post", {"url": KWAI_VIDEO}),
        ("linkbio (lnk.bio)", "/v1/linkbio/page", {"url": LINKBIO}),
        ("komi page", "/v1/komi/page", {"url": KOMI}),
        ("pillar page", "/v1/pillar/page", {"url": PILLAR}),
        ("linkme profile", "/v1/linkme/profile", {"url": LINKME}),
        ("kick clip (expect 502 graceful)", "/v1/kick/clip", {"url": KICK, "limit": 10}),
    ]
    async with httpx.AsyncClient(headers=headers) as client:
        results = await asyncio.gather(*[call(client, n, p, q) for n, p, q in tests])

    print(f"{'NAME':<34}{'CODE':<6}{'OK':<5}{'T':<7}EXCERPT")
    print("-" * 150)
    for r in results:
        print(f"{r['name']:<34}{r['code']:<6}{('Y' if r['ok'] else 'N'):<5}{str(r['t'])+'s':<7}{r['ex']}")

    sb.table("api_keys").update({"revoked_at": datetime.utcnow().isoformat()}).eq("id", kid).execute()
    print("\nkey revoked.")


if __name__ == "__main__":
    asyncio.run(main())
