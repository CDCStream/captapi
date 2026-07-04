"""One-shot smoke test for the generated SDKs against the live API.

Creates a temp API key, exercises the Python SDK (sync) directly and prints
the key so the TS SDK can be tested from Node, then revokes the key when
stdin receives a line (or after --auto for fully scripted runs).

Run from backend/:  python scripts/sdk_smoke.py [--auto]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "captapi-python"))

from app.core.security import generate_api_key  # noqa: E402
from app.services.supabase_client import get_supabase  # noqa: E402

from captapi import Captapi, CaptapiError  # noqa: E402

BASE = "https://api.captapi.com"


def main() -> None:
    sb = get_supabase()
    user = sb.auth.admin.list_users()[0]
    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert(
        {"user_id": user.id, "key_hash": key_hash, "key_prefix": prefix, "name": "sdk-smoke"}
    ).execute()
    key_id = ins.data[0]["id"]
    print(f"temp key created ({prefix}...)")

    try:
        client = Captapi(api_key=plain, base_url=BASE)
        res = client.youtube.video_details(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        data = res["data"]
        print("PY OK youtube.video_details:", data.get("title"), "| views:", data.get("viewCount"))

        try:
            client.youtube.video_details(url="https://www.tiktok.com/@nba")
            print("PY FAIL: expected CaptapiError for cross-platform URL")
        except CaptapiError as e:
            print(f"PY OK error surfaced: status={e.status_code} code={e.code}")

        if "--auto" not in sys.argv:
            print(f"\nTS_KEY={plain}")
            print("press enter to revoke...")
            input()
    finally:
        sb.table("api_keys").delete().eq("id", key_id).execute()
        print("temp key revoked")


if __name__ == "__main__":
    main()
