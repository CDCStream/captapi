"""Hosted (remote) MCP server over Streamable HTTP.

Lets AI agents (Cursor, Claude, VS Code, …) connect to Captapi with just a
URL — no `npx`, no local install. The client speaks MCP's JSON-RPC 2.0 over
HTTP POST; this server is stateless (no session id) and tools-only.

Auth: the caller supplies their Captapi API key via the
`Authorization: Bearer capt_live_...` header (or `x-api-key`). Each
`tools/call` is dispatched in-process to the real REST endpoint, so auth,
credit deduction, caching and rate limits behave exactly like a direct API
call — there is no separate code path to keep in sync.
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import get_settings
from app.services.mcp_catalog import BY_TOOL, ENDPOINTS, describe, tool_input_schema

router = APIRouter()
log = structlog.get_logger(__name__)

# Protocol versions we know how to speak. We echo back the client's requested
# version when we support it, otherwise fall back to our latest.
SUPPORTED_PROTOCOL_VERSIONS = {"2024-11-05", "2025-03-26", "2025-06-18"}
LATEST_PROTOCOL_VERSION = "2025-06-18"

SERVER_INFO = {"name": "captapi", "title": "Captapi", "version": __version__}

INSTRUCTIONS = (
    "Captapi exposes structured data from 27 platforms — YouTube, TikTok, "
    "Instagram, Facebook, X/Twitter, Reddit, Threads, Bluesky, Pinterest, "
    "LinkedIn, Rumble, Twitch, Spotify, GitHub, TikTok Shop, ad libraries, "
    "link-in-bio pages and more (transcripts, AI summaries, comments, stats, "
    "search). "
    "Authenticate by sending your Captapi API key in the 'Authorization: Bearer "
    "capt_live_...' header. Create a key at https://captapi.com/dashboard/api-keys. "
    "Each tool maps 1:1 to a REST endpoint and costs credits (cached results are "
    "free, failed calls are never charged)."
)


# --- JSON-RPC helpers ------------------------------------------------------

def _result(msg_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id: Any, code: int, message: str, data: Any = None) -> dict:
    err: dict = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": msg_id, "error": err}


def _extract_api_key(request: Request) -> str | None:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            return token
    xkey = request.headers.get("x-api-key")
    return xkey.strip() if xkey and xkey.strip() else None


def _tools_list() -> list[dict]:
    return [
        {
            "name": e.tool,
            "description": describe(e),
            "inputSchema": tool_input_schema(e),
        }
        for e in ENDPOINTS
    ]


def _text_result(text: str, is_error: bool = False) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


async def _call_tool(request: Request, name: str, arguments: dict) -> dict:
    endpoint = BY_TOOL.get(name)
    if endpoint is None:
        return _text_result(f"Unknown tool: {name}", is_error=True)

    api_key = _extract_api_key(request)
    if not api_key:
        return _text_result(
            "No API key provided. Configure this MCP server with your Captapi key "
            "via the 'Authorization: Bearer capt_live_...' header (or 'x-api-key'). "
            "Create one at https://captapi.com/dashboard/api-keys.",
            is_error=True,
        )

    params: dict[str, str] = {}
    for p in endpoint.params:
        value = arguments.get(p.name)
        if value is not None and value != "":
            params[p.name] = str(value)

    # Dispatch in-process to the real REST endpoint so all auth / credit /
    # cache / rate-limit logic runs exactly once, identically to a direct call.
    settings = get_settings()
    transport = httpx.ASGITransport(app=request.app, raise_app_exceptions=False)
    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://captapi.internal",
            timeout=httpx.Timeout(settings.MCP_TOOL_TIMEOUT_SECONDS),
        ) as client:
            resp = await client.get(
                endpoint.path,
                params=params,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json",
                    "User-Agent": f"captapi-mcp-hosted/{__version__}",
                },
            )
    except Exception as exc:  # noqa: BLE001
        log.error("mcp_tool_dispatch_failed", tool=name, error=str(exc))
        return _text_result(f"Internal error calling Captapi: {exc}", is_error=True)

    body = resp.text
    if resp.status_code >= 400:
        hint = ""
        if resp.status_code == 401:
            hint = " Check that your Captapi API key is valid and not revoked."
        elif resp.status_code == 402:
            hint = " You are out of credits. Top up at https://captapi.com/dashboard/billing."
        elif resp.status_code == 429:
            hint = " Rate limit reached — slow down or upgrade your plan."
        return _text_result(
            f"Captapi request failed (HTTP {resp.status_code}): {body}.{hint}",
            is_error=True,
        )

    return _text_result(body, is_error=False)


async def _handle_message(request: Request, msg: Any) -> dict | None:
    """Handle one JSON-RPC message. Returns a response dict, or None for
    notifications (which must not produce a response)."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
        return _error(None, -32600, "Invalid Request")

    method = msg.get("method")
    msg_id = msg.get("id")
    is_notification = "id" not in msg

    if method == "initialize":
        params = msg.get("params") or {}
        requested = params.get("protocolVersion")
        version = requested if requested in SUPPORTED_PROTOCOL_VERSIONS else LATEST_PROTOCOL_VERSION
        return _result(
            msg_id,
            {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": INSTRUCTIONS,
            },
        )

    if method == "ping":
        return _result(msg_id, {})

    if method == "tools/list":
        return _result(msg_id, {"tools": _tools_list()})

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(name, str):
            return _error(msg_id, -32602, "Invalid params: 'name' is required")
        result = await _call_tool(request, name, arguments)
        return _result(msg_id, result)

    # Notifications (e.g. notifications/initialized) get no response.
    if is_notification:
        return None

    return _error(msg_id, -32601, f"Method not found: {method}")


async def _dispatch(request: Request) -> Response:
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(_error(None, -32700, "Parse error"), status_code=400)

    if isinstance(payload, list):
        responses = []
        for msg in payload:
            r = await _handle_message(request, msg)
            if r is not None:
                responses.append(r)
        if not responses:
            return Response(status_code=202)
        return JSONResponse(responses)

    response = await _handle_message(request, payload)
    if response is None:
        return Response(status_code=202)
    status = 200
    if "error" in response and response["error"].get("code") == -32700:
        status = 400
    return JSONResponse(response, status_code=status)


@router.post("")
async def mcp_post(request: Request) -> Response:
    return await _dispatch(request)


@router.post("/")
async def mcp_post_slash(request: Request) -> Response:
    return await _dispatch(request)


@router.get("")
async def mcp_get() -> Response:
    # We don't offer a server-initiated SSE stream (stateless, tools-only).
    return Response(status_code=405, headers={"Allow": "POST"})


@router.get("/")
async def mcp_get_slash() -> Response:
    return Response(status_code=405, headers={"Allow": "POST"})
