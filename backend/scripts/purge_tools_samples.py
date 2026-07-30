"""One-off: delete response_samples rows for the tools@captapi.com service user.

Reads SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY from backend/.env and calls the
PostgREST API directly (stdlib only). Prints the row count before deleting.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

TOOLS_USER_ID = "111dc024-18cf-4a81-8041-827e1c684a41"


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def main() -> None:
    env = load_env(Path(__file__).resolve().parents[1] / ".env")
    base = env["SUPABASE_URL"].rstrip("/")
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }

    # Count rows first.
    count_req = urllib.request.Request(
        f"{base}/rest/v1/response_samples?user_id=eq.{TOOLS_USER_ID}&select=id",
        headers={**headers, "Prefer": "count=exact", "Range": "0-0"},
    )
    with urllib.request.urlopen(count_req) as resp:
        content_range = resp.headers.get("Content-Range", "0-0/0")
    total = content_range.split("/")[-1]
    print(f"response_samples rows for tools user: {total}")

    if total in ("0", "*"):
        print("nothing to delete")
        return

    delete_req = urllib.request.Request(
        f"{base}/rest/v1/response_samples?user_id=eq.{TOOLS_USER_ID}",
        headers={**headers, "Prefer": "count=exact"},
        method="DELETE",
    )
    with urllib.request.urlopen(delete_req) as resp:
        deleted_range = resp.headers.get("Content-Range", "?")
        print(f"delete status: {resp.status}, content-range: {deleted_range}")

    # Verify.
    with urllib.request.urlopen(count_req) as resp:
        content_range = resp.headers.get("Content-Range", "0-0/0")
    print(f"remaining rows: {content_range.split('/')[-1]}")


if __name__ == "__main__":
    main()
