"""API key generation, hashing, and verification."""

import hashlib
import secrets

import bcrypt

API_KEY_PREFIX_LIVE = "capt_live_"
API_KEY_PREFIX_TEST = "capt_test_"
API_KEY_BODY_BYTES = 24


def generate_api_key(env: str = "development") -> tuple[str, str, str]:
    """
    Generate a new API key.

    Returns
    -------
    plain_key : str        The full key to show user once (capt_live_...).
    key_hash  : str        Hash to store in DB.
    key_prefix: str        First 12 chars for display ("capt_live_ab").
    """
    prefix = API_KEY_PREFIX_LIVE if env == "production" else API_KEY_PREFIX_TEST
    body = secrets.token_urlsafe(API_KEY_BODY_BYTES).replace("-", "").replace("_", "")[:32]
    plain = f"{prefix}{body}"
    return plain, hash_api_key(plain), plain[:12]


def hash_api_key(plain_key: str) -> str:
    """Use SHA-256 (deterministic) so we can index it and look it up in O(1).
    bcrypt would be ideal but would require scanning all rows on every request."""
    return hashlib.sha256(plain_key.encode()).hexdigest()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
