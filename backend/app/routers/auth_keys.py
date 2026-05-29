"""API key management endpoints (called by the dashboard with Supabase JWT)."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase

router = APIRouter()


class CreateKeyBody(BaseModel):
    name: str = "Default"


async def _user_from_jwt(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing JWT")
    token = authorization.split(" ", 1)[1]
    sb = get_supabase()
    try:
        user = sb.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid JWT")
        return user.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth failed: {e}") from e


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API key (returns plaintext ONCE)",
)
async def create_api_key(
    body: CreateKeyBody,
    authorization: str | None = Header(default=None),
):
    user_id = await _user_from_jwt(authorization)
    settings = get_settings()
    plain, key_hash, prefix = generate_api_key(settings.APP_ENV)
    sb = get_supabase()
    res = (
        sb.table("api_keys")
        .insert(
            {
                "user_id": user_id,
                "key_hash": key_hash,
                "key_prefix": prefix,
                "name": body.name,
            }
        )
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=500, detail="Could not create key")
    row = res.data[0]
    return {
        "id": row["id"],
        "name": row["name"],
        "key": plain,  # show ONCE
        "prefix": row["key_prefix"],
        "created_at": row["created_at"],
        "warning": "Store this key securely. It will not be shown again.",
    }


@router.get("", summary="List active API keys for the authenticated user")
async def list_api_keys(authorization: str | None = Header(default=None)):
    user_id = await _user_from_jwt(authorization)
    sb = get_supabase()
    res = (
        sb.table("api_keys")
        .select("id, name, key_prefix, last_used_at, created_at, revoked_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"keys": res.data or []}


@router.delete("/{key_id}", summary="Revoke an API key")
async def revoke_api_key(
    key_id: str,
    authorization: str | None = Header(default=None),
):
    user_id = await _user_from_jwt(authorization)
    sb = get_supabase()
    res = (
        sb.table("api_keys")
        .update({"revoked_at": "now()"})
        .eq("id", key_id)
        .eq("user_id", user_id)
        .execute()
    )
    return {"revoked": bool(res.data)}
