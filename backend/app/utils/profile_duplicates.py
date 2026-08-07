"""Reject duplicate non-boolean profile fields (alias twins)."""

from __future__ import annotations

import json
from typing import Any

PROFILE_ALIAS_TWINS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("username", ("handle",)),
    ("displayName", ("name",)),
    ("bio", ("description",)),
    ("avatar", ("profileImage", "profileImageHd", "thumbnailUrl")),
    ("banner", ("bannerUrl", "bannerImage")),
    ("followers", ("subscriberCount",)),
    ("postCount", ("videoCount", "posts", "tweetCount")),
    ("isPrivate", ("private",)),
    ("createdAt", ("joinedAt",)),
)

_DISPLAY_DATE_KEYS = frozenset({"joinedDate"})
_BOOLEAN_OR_FLAG_SUFFIXES = ("IsApproximate",)


def _is_whitelisted_boolish(key: str, value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if key.endswith(_BOOLEAN_OR_FLAG_SUFFIXES):
        return True
    return False


def drop_alias_twins(card: dict[str, Any] | None) -> dict[str, Any]:
    """Keep preferred keys; drop deprecated aliases (and joinedDate)."""
    out = dict(card) if isinstance(card, dict) else {}
    for k in _DISPLAY_DATE_KEYS:
        out.pop(k, None)

    for preferred, aliases in PROFILE_ALIAS_TWINS:
        alias_val = None
        for a in aliases:
            if a in out:
                if alias_val is None:
                    alias_val = out.get(a)
                out.pop(a, None)
        if preferred not in out or out.get(preferred) in (None, ""):
            if alias_val not in (None, ""):
                if preferred == "username" and isinstance(alias_val, str):
                    out[preferred] = alias_val[1:] if alias_val.startswith("@") else alias_val
                else:
                    out[preferred] = alias_val
        elif preferred == "username" and isinstance(out.get(preferred), str):
            u = out["username"]
            if u.startswith("@"):
                out["username"] = u[1:]

    display = out.get("displayName")
    first = out.get("firstName")
    last = out.get("lastName")
    if first is not None and display is not None and first == display and not last:
        out.pop("firstName", None)

    return out


def duplicate_non_boolean_keys(data: dict[str, Any]) -> list[tuple[str, str, Any]]:
    """Return (key_a, key_b, value) pairs that violate the one-concept rule."""
    keys = list(data.keys())
    dups: list[tuple[str, str, Any]] = []
    for i, ka in enumerate(keys):
        va = data[ka]
        if va is None or _is_whitelisted_boolish(ka, va):
            continue
        if isinstance(va, (dict, list)):
            continue
        sa = json.dumps(va, sort_keys=True, default=str)
        for kb in keys[i + 1 :]:
            vb = data[kb]
            if vb is None or _is_whitelisted_boolish(kb, vb):
                continue
            if isinstance(vb, (dict, list)):
                continue
            if json.dumps(vb, sort_keys=True, default=str) == sa:
                dups.append((ka, kb, va))
    return dups