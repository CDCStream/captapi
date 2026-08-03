"""Shared cacheMaxAge query parsing (SC-compatible freshness windows)."""

from __future__ import annotations

from fastapi import HTTPException, Query

# SC cache_max_age: 1d / 3d / 7d / 14d / 30d
CACHE_MAX_AGE_SECONDS: dict[str, int] = {
    "1d": 86_400,
    "3d": 3 * 86_400,
    "7d": 7 * 86_400,
    "14d": 14 * 86_400,
    "30d": 30 * 86_400,
}

CACHE_MAX_AGE_DESC = (
    "Max age of a cached response: 1d, 3d, 7d, 14d, or 30d. "
    "When set, enables caching with that TTL (SC cache_max_age). "
    "Envelope includes cached + cachedAt on hits."
)


def parse_cache_max_age(value: str | None) -> int | None:
    """Return TTL seconds for a cacheMaxAge token, or None when unset."""
    if value is None:
        return None
    raw = str(value).strip().lower().replace("_", "").replace("-", "")
    aliases = {
        "1day": "1d",
        "3day": "3d",
        "3days": "3d",
        "7day": "7d",
        "7days": "7d",
        "14day": "14d",
        "14days": "14d",
        "30day": "30d",
        "30days": "30d",
        "24h": "1d",
    }
    key = aliases.get(raw, raw)
    if key not in CACHE_MAX_AGE_SECONDS:
        raise HTTPException(
            status_code=400,
            detail="cacheMaxAge must be one of: 1d, 3d, 7d, 14d, 30d",
        )
    return CACHE_MAX_AGE_SECONDS[key]


def resolve_cache_options(
    cache: bool,
    cache_max_age: str | None,
) -> tuple[bool, int | None]:
    """Return (use_cache, ttl_override).

    cacheMaxAge enables caching and sets the TTL. cache=true alone uses the
    endpoint default TTL. Both false/None means always fetch fresh.
    """
    ttl = parse_cache_max_age(cache_max_age)
    if ttl is not None:
        return True, ttl
    return bool(cache), None


def CacheMaxAgeQuery(default: str | None = None):  # noqa: N802
    return Query(default, description=CACHE_MAX_AGE_DESC)
