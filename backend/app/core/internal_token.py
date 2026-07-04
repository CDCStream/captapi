"""Internal bearer tokens for first-party background jobs (monitor runs).

The scheduler needs to call API endpoints in-process *as a user* so that
credits, caching, and rate limits apply exactly like a direct call -- but
API keys are stored hashed, so it cannot replay one. Instead it mints a
short token derived from the Supabase service-role key. These tokens never
leave the process (they only travel through the in-process ASGI dispatch).
"""

from __future__ import annotations

import hashlib
import hmac

from app.core.config import get_settings

PREFIX = "capt_mon_"


def _sign(user_id: str) -> str:
    key = get_settings().SUPABASE_SERVICE_ROLE_KEY.encode()
    return hmac.new(key, f"captapi-monitor:{user_id}".encode(), hashlib.sha256).hexdigest()


def mint_monitor_token(user_id: str) -> str:
    return f"{PREFIX}{user_id}.{_sign(user_id)}"


def verify_monitor_token(token: str) -> str | None:
    """Return the user_id if the token is valid, else None."""
    if not token.startswith(PREFIX):
        return None
    rest = token[len(PREFIX):]
    user_id, _, sig = rest.rpartition(".")
    if not user_id or not sig:
        return None
    if not hmac.compare_digest(sig, _sign(user_id)):
        return None
    return user_id
