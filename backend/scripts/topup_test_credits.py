"""Top up the smoke-test user's credit balance for snapshot capture runs."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.supabase_client import get_supabase  # noqa: E402

AMOUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

sb = get_supabase()
user = sb.auth.admin.list_users()[0]
bal = sb.table("credit_balances").select("subscription_credits, topup_credits").eq("user_id", user.id).limit(1).execute()
before = bal.data[0] if bal.data else {}
print(f"user: {user.email} | before: {before}")
sb.table("credit_balances").upsert(
    {"user_id": user.id, "topup_credits": AMOUNT},
    on_conflict="user_id",
).execute()
after = sb.table("credit_balances").select("subscription_credits, topup_credits").eq("user_id", user.id).limit(1).execute()
print(f"after: {after.data[0] if after.data else None}")
