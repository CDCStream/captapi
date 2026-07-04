"""Live smoke test for the TypeScript SDK: temp key -> node script -> revoke."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.security import generate_api_key  # noqa: E402
from app.services.supabase_client import get_supabase  # noqa: E402

NODE_TEST = """
const { Captapi, CaptapiError } = await import("file://" + process.env.SDK_DIST.replace(/\\\\/g, "/"));
const client = new Captapi({ apiKey: process.env.CAPTAPI_API_KEY, baseUrl: "https://api.captapi.com" });
const res = await client.youtube.videoDetails({ url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ" });
console.log("TS OK youtube.videoDetails:", res.data.title, "| views:", res.data.viewCount);
try {
  await client.youtube.videoDetails({ url: "https://www.tiktok.com/@nba" });
  console.log("TS FAIL: expected CaptapiError");
} catch (e) {
  console.log("TS OK error surfaced: status=" + e.status + " name=" + e.name);
}
"""


def main() -> None:
    sb = get_supabase()
    user = sb.auth.admin.list_users()[0]
    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert(
        {"user_id": user.id, "key_hash": key_hash, "key_prefix": prefix, "name": "sdk-smoke-ts"}
    ).execute()
    key_id = ins.data[0]["id"]
    print(f"temp key created ({prefix}...)")

    try:
        result = subprocess.run(
            ["node", "--input-type=module", "-e", NODE_TEST],
            env={
                "CAPTAPI_API_KEY": plain,
                "SDK_DIST": str(ROOT / "packages" / "captapi-sdk" / "dist" / "index.js"),
                "PATH": __import__("os").environ["PATH"],
                "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""),
            },
            capture_output=True,
            text=True,
            timeout=180,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr[:1000])
    finally:
        sb.table("api_keys").delete().eq("id", key_id).execute()
        print("temp key revoked")


if __name__ == "__main__":
    main()
