"""Generate frontend/lib/api-examples.generated.ts from api_snapshots.json.

api_snapshots.json is captured live from production (one entry per endpoint
slug). Run this after refreshing those snapshots to rebake the docs examples.

API_EXAMPLE_VARIANTS live in frontend/lib/api-example-variants.ts and are
intentionally NOT written here.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

# Strings that can break Next.js SSR when embedded in RSC flight / <script>
# payloads (literal closers terminate the document early → head-only HTML).
_POISON_RE = re.compile(r"</(?:script|body|html)\b", re.I)
_LONG_HTML_RE = re.compile(r"^\s*<!DOCTYPE\s+html|<html[\s>]", re.I)

# Most list fields truncate to 2 for page weight. Fields that docs promise by
# count (or that must match sibling counters like segments/totalReturned) keep
# a higher cap so examples do not lie.
_ARRAY_CAPS: dict[str, int] = {
    "keyPoints": 8,
    "topics": 8,
    "transcriptSegments": 8,
    "requests": 5,
}


def _array_cap(path: str) -> int:
    key = path.rsplit(".", 1)[-1] if path else ""
    return _ARRAY_CAPS.get(key, 2)


def _sanitize(value: Any, *, path: str = "") -> Any:
    if isinstance(value, dict):
        return {k: _sanitize(v, path=f"{path}.{k}" if path else k) for k, v in value.items()}
    if isinstance(value, list):
        cap = _array_cap(path)
        return [_sanitize(v, path=f"{path}[]") for v in value[:cap]]
    if isinstance(value, str):
        if _POISON_RE.search(value) or (_LONG_HTML_RE.search(value) and len(value) > 400):
            return (
                "[HTML omitted in docs — call the API for the full document. "
                "Docs examples must not embed raw HTML documents.]"
            )
        if len(value) > 1200:
            return value[:1100] + " …"
        return value
    return value


snap = json.load(open("api_snapshots.json", encoding="utf-8"))
examples = {
    slug: _sanitize(v["data"])
    for slug, v in sorted(snap.items())
    if v.get("ok") and isinstance(v.get("data"), dict)
}

body = json.dumps(examples, ensure_ascii=False, indent=2)
header = (
    "// AUTO-GENERATED — do not edit by hand.\n"
    "// Real example responses captured live from https://api.captapi.com.\n"
    "// Arrays truncated to 2 items by default (keyPoints/topics/"
    "transcriptSegments/requests keep higher caps); HTML stubbed for SSR.\n"
    "// Mode variants: frontend/lib/api-example-variants.ts (not overwritten).\n"
    "// Regenerate: python backend/gen_examples.py (source: backend/api_snapshots.json).\n\n"
    "export const API_EXAMPLES: Record<string, Record<string, unknown>> = "
)
out = header + body + ";\n"

dest = os.path.join("..", "frontend", "lib", "api-examples.generated.ts")
with open(dest, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
print(f"wrote {dest} with {len(examples)} examples")
print("slugs:", sorted(examples.keys()))
