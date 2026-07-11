"""Create the Zapier review test account (integration-testing@zapier.com).

Zapier's publishing review requires a login with this exact email. The address
cannot receive mail, so the user is created via the Supabase admin API with the
email pre-confirmed. Also funds the account with top-up credits and mints an
API key so reviewers can connect immediately.

Run from backend/:  python scripts/create_zapier_review_account.py
Idempotent: re-running reuses the existing user and just refreshes funding.
"""

import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import generate_api_key  # noqa: E402
from app.services.supabase_client import get_supabase  # noqa: E402

EMAIL = "integration-testing@zapier.com"
CREDITS = 5000


def find_user(sb, email: str):
    page = 1
    while True:
        users = sb.auth.admin.list_users(page=page, per_page=100)
        if not users:
            return None
        for u in users:
            if (u.email or "").lower() == email:
                return u
        if len(users) < 100:
            return None
        page += 1


def main() -> None:
    sb = get_supabase()

    existing = find_user(sb, EMAIL)
    password = "Zap-" + secrets.token_urlsafe(12)

    if existing:
        user_id = existing.id
        sb.auth.admin.update_user_by_id(
            user_id, {"password": password, "email_confirm": True}
        )
        print(f"existing user reused: {user_id} (password reset)")
    else:
        res = sb.auth.admin.create_user(
            {
                "email": EMAIL,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"full_name": "Zapier Review"},
            }
        )
        user_id = res.user.id
        print(f"user created: {user_id}")

    # Fund the account (upsert keeps this idempotent).
    sb.table("credit_balances").upsert(
        {
            "user_id": user_id,
            "plan": "free",
            "topup_credits": CREDITS,
        },
        on_conflict="user_id",
    ).execute()
    print(f"credit_balances: topup_credits={CREDITS}")

    # Mint a live API key for the Zapier connection.
    plain, key_hash, prefix = generate_api_key("production")
    sb.table("api_keys").insert(
        {
            "user_id": user_id,
            "key_hash": key_hash,
            "key_prefix": prefix,
            "name": "Zapier review",
        }
    ).execute()

    print()
    print("=== Zapier 'Test account for us' form ===")
    print(f"Username : {EMAIL}")
    print(f"Password : {password}")
    print(f"API key  : {plain}")
    print("Login URL: https://captapi.com/login")


if __name__ == "__main__":
    main()
