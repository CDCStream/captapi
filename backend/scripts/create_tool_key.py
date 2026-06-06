"""Create (or refresh) the API key that powers the public free tools.

Creates a dedicated Supabase user, sets its credit balance to an exact amount,
mints a `capt_live_` API key, and prints the plaintext key ONCE. Idempotent:
re-running resets the balance to the requested amount and adds a fresh key.

Usage (from the backend/ directory, with .env present):

    python -m scripts.create_tool_key                 # 20000 credits, defaults
    python -m scripts.create_tool_key --credits 20000 --email tools@captapi.com

Put the printed key into Vercel as CAPTAPI_TOOL_API_KEY.
"""

from __future__ import annotations

import argparse
import secrets

from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase


def find_or_create_user(sb, email: str, password: str) -> str:
    try:
        res = sb.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )
        if getattr(res, "user", None) and res.user.id:
            print(f"  created auth user: {email}")
            return res.user.id
    except Exception as exc:  # noqa: BLE001 — likely "already registered"
        print(f"  create_user failed ({exc}); looking up existing user…")

    # Fall back to finding the existing user by email.
    page = sb.auth.admin.list_users()
    users = page if isinstance(page, list) else getattr(page, "users", []) or []
    for u in users:
        if getattr(u, "email", None) == email:
            print(f"  found existing auth user: {email}")
            return u.id
    raise SystemExit(f"Could not create or find user {email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the public free-tools API key.")
    parser.add_argument("--email", default="tools@captapi.com")
    parser.add_argument("--credits", type=int, default=20000)
    parser.add_argument("--plan", default="business")
    parser.add_argument("--name", default="Public Free Tools")
    args = parser.parse_args()

    sb = get_supabase()

    print("1/3  Ensuring dedicated user…")
    password = secrets.token_urlsafe(24)
    user_id = find_or_create_user(sb, args.email, password)

    print(f"2/3  Setting balance to {args.credits} credits (plan={args.plan})…")
    sb.table("credit_balances").upsert(
        {
            "user_id": user_id,
            "subscription_credits": 0,
            "topup_credits": args.credits,
            "plan": args.plan,
        },
        on_conflict="user_id",
    ).execute()

    print("3/3  Minting capt_live_ API key…")
    plain, key_hash, prefix = generate_api_key("production")
    res = (
        sb.table("api_keys")
        .insert(
            {
                "user_id": user_id,
                "key_hash": key_hash,
                "key_prefix": prefix,
                "name": args.name,
            }
        )
        .execute()
    )
    if not res.data:
        raise SystemExit("Failed to insert API key row.")

    print("\n" + "=" * 60)
    print("  API KEY (shown once — copy it now):\n")
    print(f"    {plain}\n")
    print(f"  user:    {args.email}")
    print(f"  credits: {args.credits} (plan: {args.plan})")
    print("\n  Add to Vercel env:")
    print(f"    CAPTAPI_TOOL_API_KEY={plain}")
    print("=" * 60)


if __name__ == "__main__":
    main()
