"""Reject duplicate non-boolean profile fields (alias twins)."""

from __future__ import annotations

import json
from typing import Any

PROFILE_ALIAS_TWINS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("username", ("handle", "mutableUsername")),
    ("displayName", ("name",)),
    ("bio", ("description",)),
    ("avatar", ("profileImage", "profileImageHd", "thumbnailUrl", "profilePictureUrl")),
    ("banner", ("bannerUrl", "bannerImage", "squareHeroImageUrl", "squareHeroImage")),
    ("followers", ("subscriberCount", "subscribers")),
    ("postCount", ("videoCount", "posts", "tweetCount")),
    ("isPrivate", ("private",)),
    ("createdAt", ("joinedAt",)),
    ("website", ("websiteUrl",)),
    ("url", ("webUrl", "profileUrl")),
    ("highlights", ("curatedHighlights",)),
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

    if "verified" in out and "isVerified" in out:
        out.pop("isVerified", None)

    # Drop leftover same-value twins (e.g. title == displayName on Snapchat).
    for a, b in (("displayName", "title"), ("snapcode", "snapcodeImageUrl")):
        if a in out and b in out and out.get(a) == out.get(b):
            out.pop(b, None)

    return out


def duplicate_non_boolean_keys(
    data: dict[str, Any],
    *,
    include_containers: bool = False,
) -> list[tuple[str, str, Any]]:
    """Return (key_a, key_b, value) pairs that violate the one-concept rule.

    By default skips dict/list values (profile scalars). Pass
    ``include_containers=True`` for the catalogue-wide audit that matches the
    auditor JS (JSON.stringify equality on every non-boolean key).
    """
    keys = list(data.keys())
    dups: list[tuple[str, str, Any]] = []
    for i, ka in enumerate(keys):
        va = data[ka]
        if va is None or _is_whitelisted_boolish(ka, va):
            continue
        if not include_containers and isinstance(va, (dict, list)):
            continue
        sa = json.dumps(va, sort_keys=True, default=str)
        for kb in keys[i + 1 :]:
            vb = data[kb]
            if vb is None or _is_whitelisted_boolish(kb, vb):
                continue
            if not include_containers and isinstance(vb, (dict, list)):
                continue
            if json.dumps(vb, sort_keys=True, default=str) == sa:
                dups.append((ka, kb, va))
    return dups


def _scalar_fingerprint(value: Any) -> str | None:
    """Fingerprint for correlation — scalars only (bool/int/float/str)."""
    if value is None or isinstance(value, (dict, list)):
        return None
    if isinstance(value, bool):
        return f"b:{value}"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"n:{value}"
    if isinstance(value, str):
        return f"s:{value}"
    return None


def correlated_field_pairs(
    rows: list[dict[str, Any]],
    *,
    min_rows: int = 5,
    min_distinct: int = 2,
) -> list[tuple[str, str]]:
    """Return (key_a, key_b) when two fields form a bijection across every row.

    Catches duplicate-*concept* pairs the identical-value scan misses — e.g.
    ``explicit: false`` ↔ ``contentRating: "NONE"`` — because the encodings
    differ. Requires at least ``min_distinct`` distinct values on each side so
    a constant column (same stamp on every row) does not pair with everything.
    """
    if len(rows) < min_rows:
        return []
    key_sets = [set(r.keys()) for r in rows if isinstance(r, dict)]
    if len(key_sets) < min_rows:
        return []
    common = set.intersection(*key_sets)
    candidates = sorted(
        k
        for k in common
        if all(_scalar_fingerprint(r.get(k)) is not None for r in rows)
    )
    hits: list[tuple[str, str]] = []
    for i, ka in enumerate(candidates):
        for kb in candidates[i + 1 :]:
            a_to_b: dict[str, set[str]] = {}
            b_to_a: dict[str, set[str]] = {}
            for row in rows:
                fa = _scalar_fingerprint(row.get(ka))
                fb = _scalar_fingerprint(row.get(kb))
                if fa is None or fb is None:
                    a_to_b = {}
                    break
                # Identical values are already covered by duplicate_non_boolean_keys.
                if fa == fb:
                    a_to_b = {}
                    break
                a_to_b.setdefault(fa, set()).add(fb)
                b_to_a.setdefault(fb, set()).add(fa)
            if not a_to_b:
                continue
            if len(a_to_b) < min_distinct or len(b_to_a) < min_distinct:
                continue
            if any(len(vs) != 1 for vs in a_to_b.values()):
                continue
            if any(len(vs) != 1 for vs in b_to_a.values()):
                continue
            hits.append((ka, kb))
    return hits