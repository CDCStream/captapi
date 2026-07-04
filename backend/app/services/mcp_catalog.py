"""Catalog of every Captapi endpoint exposed as a hosted MCP tool.

Loaded from ``mcp_catalog.json``, which is generated from the npm MCP
catalog (``packages/captapi-mcp/src/catalog.ts``) by
``scripts/gen-hosted-mcp-catalog.mts`` — so the hosted (remote, HTTP) MCP
server always advertises the exact same tools, parameters, credit costs and
descriptions as the published ``@captapi/mcp`` package. Regenerate the JSON
whenever the npm catalog changes:

    npx tsx scripts/gen-hosted-mcp-catalog.mts
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

Platform = str


@dataclass(frozen=True)
class ToolParam:
    name: str
    type: str  # "string" | "number" | "boolean"
    required: bool
    description: str


@dataclass(frozen=True)
class Endpoint:
    tool: str
    platform: Platform
    name: str
    path: str
    credits: int
    summary: str
    params: tuple[ToolParam, ...]


def _load() -> list[Endpoint]:
    raw = json.loads(
        (Path(__file__).parent / "mcp_catalog.json").read_text(encoding="utf-8")
    )
    return [
        Endpoint(
            tool=row["tool"],
            platform=row["platform"],
            name=row["name"],
            path=row["path"],
            credits=row["credits"],
            summary=row["summary"],
            params=tuple(
                ToolParam(
                    name=p["name"],
                    type=p["type"],
                    required=p["required"],
                    description=p["description"],
                )
                for p in row["params"]
            ),
        )
        for row in raw
    ]


ENDPOINTS: list[Endpoint] = _load()

BY_TOOL: dict[str, Endpoint] = {e.tool: e for e in ENDPOINTS}


def describe(e: Endpoint) -> str:
    """A concise, agent-facing description (summary + cost) for an endpoint."""
    plural = "" if e.credits == 1 else "s"
    return (
        f"{e.summary} Costs ~{e.credits} credit{plural}; "
        "cached results are free, failures are never charged."
    )


def tool_input_schema(e: Endpoint) -> dict:
    """JSON Schema (draft-07 style) describing the tool's input parameters."""
    properties: dict[str, dict] = {}
    required: list[str] = []
    for p in e.params:
        if p.type == "number":
            schema: dict = {"type": "integer", "minimum": 1, "description": p.description}
        elif p.type == "boolean":
            schema = {"type": "boolean", "description": p.description}
        else:
            schema = {"type": "string", "description": p.description}
            if p.name == "url":
                schema["format"] = "uri"
        properties[p.name] = schema
        if p.required:
            required.append(p.name)
    out: dict = {"type": "object", "properties": properties, "additionalProperties": False}
    if required:
        out["required"] = required
    return out
