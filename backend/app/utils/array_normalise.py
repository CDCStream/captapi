"""Normalise object arrays so every row shares the same key set.

Absent keys become null -- never missing. Safe default for typed clients:
can only add nulls, never drop data. Endpoints may still declare an explicit
canonical key list; this catches everything else before JSON serialisation.
"""

from __future__ import annotations

from typing import Any


def _is_plain_object(value: Any) -> bool:
    return isinstance(value, dict)


def normalise_object_arrays(node: Any) -> Any:
    """Recursively pad object-array rows to the union of keys present.

    Applies when node is a list of length > 1 whose every element is a
    plain object. Nested lists/dicts are walked the same way.
    """
    if isinstance(node, list):
        if len(node) > 1 and all(_is_plain_object(x) for x in node):
            union: list[str] = []
            seen: set[str] = set()
            for obj in node:
                for k in obj.keys():
                    if k not in seen:
                        seen.add(k)
                        union.append(k)
            padded = [{k: obj.get(k, None) for k in union} for obj in node]
            return [normalise_object_arrays(obj) for obj in padded]
        return [normalise_object_arrays(x) for x in node]
    if _is_plain_object(node):
        return {k: normalise_object_arrays(v) for k, v in node.items()}
    return node