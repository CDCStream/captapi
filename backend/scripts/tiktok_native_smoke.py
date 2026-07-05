"""Live smoke of TikTok native endpoints against production.

Mints a temp API key, calls the migrated endpoints, then reads back the
`requests.source` column to confirm they were served by the self-scraper
(direct) rather than Apify.
"""

import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import generate_api_key  # noqa: E402
from app.services.supabase_client import get_supabase  # noqa: E402

BASE = "https://api.captapi.com"

VIDEO = "https://www.tiktok.com/@mrbeast/video/7596844935442189598"
PROFILE = "https://www.tiktok.com/@khaby.lame"

CALLS = [
    ("video-details", "/v1/tiktok/video-details", {"url": VIDEO}),
    ("channel-details", "/v1/tiktok/channel-details", {"url": PROFILE}),
    ("profile-region", "/v1/tiktok/profile-region", {"url": PROFILE}),
]


def main() -> None:
    sb = get_supabase()
    user = sb.auth.admin.list_users()[0]
    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert(
        {"user_id": user.id, "key_hash": key_hash, "key_prefix": prefix, "name": "tiktok-native-smoke"}
    ).execute()
    key_id = ins.data[0]["id"]
    print(f"temp key created ({prefix}...)\n")

    try:
        headers = {"Authorization": f"Bearer {plain}"}
        with httpx.Client(timeout=120) as client:
            for name, path, params in CALLS:
                t0 = time.perf_counter()
                r = client.get(f"{BASE}{path}", params={**params, "_nocache": int(t0)}, headers=headers)
                el = time.perf_counter() - t0
                data = r.json().get("data", {}) if r.status_code == 200 else {}
                summary = ""
                if name == "video-details":
                    eng = data.get("engagement", {})
                    summary = f"views={eng.get('views')} likes={eng.get('likes')}"
                elif name == "channel-details":
                    summary = f"followers={data.get('followers')} posts={data.get('postCount')}"
                elif name == "profile-region":
                    summary = f"region={data.get('region')} lang={data.get('language')}"
                print(f"{name:<16} {r.status_code} {el:4.1f}s  {summary}")

        # Give the async request-log insert a moment, then read source column.
        time.sleep(3)
        print("\nsource column (last 3 tiktok rows):")
        rows = (
            sb.table("requests")
            .select("endpoint,source,cache_hit,status_code,created_at")
            .eq("api_key_id", key_id)
            .order("created_at", desc=True)
            .limit(6)
            .execute()
        )
        for row in rows.data:
            print(f"  {row['endpoint']:<32} source={row.get('source')} cache={row.get('cache_hit')} http={row.get('status_code')}")
    finally:
        sb.table("api_keys").delete().eq("id", key_id).execute()
        print("\ntemp key revoked")


if __name__ == "__main__":
    main()
