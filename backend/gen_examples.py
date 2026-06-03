"""Generate frontend/lib/api-examples.generated.ts from api_snapshots.json.

api_snapshots.json is captured live from production (one entry per endpoint
slug). Run this after refreshing those snapshots to rebake the docs examples.
"""
import json
import os

snap = json.load(open("api_snapshots.json", encoding="utf-8"))
examples = {
    slug: v["data"]
    for slug, v in sorted(snap.items())
    if v.get("ok") and isinstance(v.get("data"), dict)
}

body = json.dumps(examples, ensure_ascii=False, indent=2)
header = (
    "// AUTO-GENERATED — do not edit by hand.\n"
    "// Real example responses captured live from https://api.captapi.com.\n"
    "// Arrays are truncated to 2 items and long strings shortened for display.\n"
    "// Regenerate: python backend/gen_examples.py (source: backend/api_snapshots.json).\n\n"
    "export const API_EXAMPLES: Record<string, Record<string, unknown>> = "
)
out = header + body + ";\n"

dest = os.path.join("..", "frontend", "lib", "api-examples.generated.ts")
with open(dest, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
print(f"wrote {dest} with {len(examples)} examples")
print("slugs:", sorted(examples.keys()))
