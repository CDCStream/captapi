"""Write the FastAPI OpenAPI schema to backend/openapi.snapshot.json.

This snapshot is the source of truth used by the catalog parity check
(scripts/check-catalog-parity.mts) so CI can validate the published catalogs
without a live server running.

Usage (from the backend/ directory, with the venv active):
    python scripts/dump_openapi.py
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402

OUT = ROOT / "openapi.snapshot.json"


def main() -> None:
    schema = app.openapi()
    OUT.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    paths = schema.get("paths", {})
    print(f"Wrote {OUT} ({len(paths)} paths)")


if __name__ == "__main__":
    main()
