"""Authentication dependency.

Accepts either:
  1. `Authorization: Bearer capt_live_...` / `capt_test_...`  → API key (programmatic use)
  2. `Authorization: Bearer <Supabase JWT>`                  → Logged-in dashboard user
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import hash_api_key
from app.services.supabase_client import get_supabase

log = structlog.get_logger(__name__)

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Your API key (capt_live_… / capt_test_…) or a dashboard session token.",
)


@dataclass
class ApiCaller:
    user_id: str
    api_key_id: str | None
    plan: str
    subscription_credits: int
    topup_credits: int

    @property
    def total_credits(self) -> int:
        return self.subscription_credits + self.topup_credits


def _load_credits(user_id: str) -> dict:
    sb = get_supabase()
    bal = (
        sb.table("credit_balances")
        .select("subscription_credits, topup_credits, plan")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not bal.data:
        raise HTTPException(status_code=402, detail="No credit balance found")
    return bal.data[0]


async def _resolve_api_key(plain: str) -> ApiCaller:
    sb = get_supabase()
    key_hash = hash_api_key(plain)
    res = (
        sb.table("api_keys")
        .select("id, user_id, revoked_at")
        .eq("key_hash", key_hash)
        .limit(1)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    row = res.data[0]
    if row.get("revoked_at"):
        raise HTTPException(status_code=401, detail="API key has been revoked")

    b = _load_credits(row["user_id"])
    sb.table("api_keys").update({"last_used_at": datetime.utcnow().isoformat()}).eq(
        "id", row["id"]
    ).execute()

    return ApiCaller(
        user_id=row["user_id"],
        api_key_id=row["id"],
        plan=b.get("plan", "free"),
        subscription_credits=int(b.get("subscription_credits", 0)),
        topup_credits=int(b.get("topup_credits", 0)),
    )


async def _resolve_session_jwt(jwt: str) -> ApiCaller:
    """Verify a Supabase JWT and return the matching ApiCaller."""
    sb = get_supabase()
    try:
        result = sb.auth.get_user(jwt)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid session token") from e
    user = getattr(result, "user", None) if result is not None else None
    if not user or not getattr(user, "id", None):
        raise HTTPException(status_code=401, detail="Invalid session token")

    b = _load_credits(user.id)
    return ApiCaller(
        user_id=user.id,
        api_key_id=None,
        plan=b.get("plan", "free"),
        subscription_credits=int(b.get("subscription_credits", 0)),
        topup_credits=int(b.get("topup_credits", 0)),
    )


async def require_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> ApiCaller:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Missing Authorization header. Send 'Authorization: Bearer "
                "capt_live_...'. Create a key at "
                "https://captapi.com/dashboard/api-keys"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    plain = credentials.credentials.strip()

    if plain.startswith(("capt_live_", "capt_test_", "sk_live_", "sk_test_")):
        caller = await _resolve_api_key(plain)
    else:
        caller = await _resolve_session_jwt(plain)

    from app.core.rate_limit import enforce_rate_limit
    await enforce_rate_limit(caller)
    return caller


CallerDep = Depends(require_api_key)
