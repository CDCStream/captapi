"""Common output formatters."""

from __future__ import annotations


def seconds_to_timestamp(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    mm = int(seconds // 60)
    ss = int(seconds % 60)
    return f"{mm:02d}:{ss:02d}"


def safe_int(v) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def safe_float(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def safe_str(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def safe_list(v) -> list:
    if isinstance(v, list):
        return v
    return []
