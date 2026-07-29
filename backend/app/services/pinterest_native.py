"""Native Pinterest lookups via public pidgets API + Decodo HTML.

- User pins / board pins: ``api.pinterest.com/v3/pidgets/...`` (soft-capped ~50).
- User boards: Decodo-rendered ``/_boards/`` page (board cards in page JSON).
- Search: Google/DDG SERP → widgets pidgets hydrate (logged-out search HTML is empty).
"""

from __future__ import annotations

import json
import re
from html import unescape
from typing import Any
from urllib.parse import quote, urlparse

import httpx
import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

_UA = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)", "Accept": "application/json"}
_HANDLE_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _extract_json_object(source: str, brace_start: int) -> str | None:
    if brace_start < 0 or brace_start >= len(source) or source[brace_start] != "{":
        return None
    depth = 0
    in_str = False
    esc = False
    for idx in range(brace_start, len(source)):
        ch = source[idx]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start : idx + 1]
    return None


def normalize_username(value: str) -> str | None:
    raw = (value or "").strip().lstrip("@")
    if "://" in raw or "/" in raw:
        path = urlparse(raw if "://" in raw else f"https://www.pinterest.com/{raw}").path
        parts = [p for p in path.split("/") if p and not p.startswith("_")]
        raw = parts[0] if parts else ""
    raw = raw.strip("/")
    if not raw or not _HANDLE_RE.fullmatch(raw):
        return None
    return raw


def parse_board_url(url: str) -> tuple[str, str] | None:
    """Return ``(username, board_slug)`` from a board URL."""
    raw = (url or "").strip()
    if not raw:
        return None
    path = urlparse(raw if "://" in raw else f"https://www.pinterest.com/{raw}").path
    parts = [p for p in path.split("/") if p]
    if len(parts) < 2:
        return None
    user, slug = parts[0], parts[1]
    if slug.startswith("_"):
        return None
    if not _HANDLE_RE.fullmatch(user) or not _HANDLE_RE.fullmatch(slug):
        return None
    return user, slug


async def _pidgets_get(path: str) -> dict[str, Any] | None:
    url = f"https://api.pinterest.com/v3/pidgets/{path.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=25, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(url)
    except httpx.HTTPError as exc:
        log.info("pinterest_pidgets_fail", path=path, error=str(exc))
        return None
    if resp.status_code != 200:
        log.info("pinterest_pidgets_http", path=path, status=resp.status_code)
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    data = payload.get("data") if isinstance(payload, dict) else None
    return data if isinstance(data, dict) else None


async def user_pins_native(username: str, limit: int = 25) -> list[dict[str, Any]] | None:
    user = normalize_username(username)
    if not user:
        return None
    capped = max(1, min(int(limit or 25), 100))
    data = await _pidgets_get(f"users/{quote(user)}/pins/")
    if not data:
        return None
    pins = data.get("pins") if isinstance(data.get("pins"), list) else []
    out = [p for p in pins if isinstance(p, dict) and p.get("id")]
    if not out:
        return None
    log.info("pinterest_user_pins_native_ok", username=user, returned=min(len(out), capped))
    return out[:capped]


async def board_pins_native(board_url: str, limit: int = 25) -> list[dict[str, Any]] | None:
    parsed = parse_board_url(board_url)
    if not parsed:
        return None
    user, slug = parsed
    capped = max(1, min(int(limit or 25), 100))
    data = await _pidgets_get(f"boards/{quote(user)}/{quote(slug)}/pins/")
    if not data:
        return None
    pins = data.get("pins") if isinstance(data.get("pins"), list) else []
    out = [p for p in pins if isinstance(p, dict) and p.get("id")]
    # Attach board metadata when missing on pin rows.
    board = data.get("board") if isinstance(data.get("board"), dict) else {}
    for pin in out:
        if not isinstance(pin.get("board"), dict) and board:
            pin["board"] = board
    if not out:
        return None
    log.info("pinterest_board_pins_native_ok", board=f"{user}/{slug}", returned=min(len(out), capped))
    return out[:capped]


def parse_boards_html(html: str, username: str, limit: int = 25) -> list[dict[str, Any]]:
    """Extract board cards embedded in a profile ``/_boards/`` page."""
    if not html or not username:
        return []
    needle = f"/{username.strip().lower().strip('/')}/"
    capped = max(1, min(int(limit or 25), 200))
    boards: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in re.finditer(r'"url"\s*:\s*"(/[^"]+/)"', html):
        url = m.group(1)
        if needle not in url.lower():
            continue
        parts = [p for p in url.split("/") if p]
        if len(parts) != 2:
            continue
        if parts[0].lower() != username.lower() or parts[1].startswith("_"):
            continue
        brace = html.rfind("{", max(0, m.start() - 900), m.start())
        if brace < 0:
            continue
        raw = _extract_json_object(html, brace)
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(obj, dict) or obj.get("url") != url:
            continue
        if not (obj.get("name") or obj.get("id")):
            continue
        if url in seen:
            continue
        seen.add(url)
        boards.append(obj)
        if len(boards) >= capped:
            break
    return boards[:capped]


async def user_boards_native(username: str, limit: int = 25) -> list[dict[str, Any]] | None:
    user = normalize_username(username)
    if not user:
        return None
    capped = max(1, min(int(limit or 25), 200))

    # Fast path: unique boards from the public user-pins pidgets payload.
    data = await _pidgets_get(f"users/{quote(user)}/pins/")
    boards: list[dict[str, Any]] = []
    seen: set[str] = set()
    if data:
        for pin in data.get("pins") or []:
            if not isinstance(pin, dict):
                continue
            board = pin.get("board") if isinstance(pin.get("board"), dict) else None
            if not board:
                continue
            url = safe_str(board.get("url"))
            if not url:
                continue
            if url.startswith("/"):
                key = url
            else:
                key = urlparse(url).path or url
            parts = [p for p in (key or "").split("/") if p]
            if len(parts) >= 2 and parts[1].startswith("_"):
                continue
            if key in seen:
                continue
            seen.add(key)
            boards.append(board)
            if len(boards) >= capped:
                break

    # Enrich / extend via Decodo boards tab when available.
    if decodo_fetch.enabled():
        page = f"https://www.pinterest.com/{user}/_boards/"
        got = await decodo_fetch.fetch_url(page, timeout=90.0, headless="html")
        if got and got[0] == 200 and got[1]:
            html_boards = parse_boards_html(got[1], user, limit=capped)
            for board in html_boards:
                url = safe_str(board.get("url"))
                key = url if url and url.startswith("/") else (urlparse(url or "").path if url else None)
                if not key or key in seen:
                    # Prefer HTML board when we already have a sparse pidgets board.
                    if key and key in seen:
                        for i, existing in enumerate(boards):
                            eu = safe_str(existing.get("url"))
                            ek = eu if eu and eu.startswith("/") else (urlparse(eu or "").path if eu else None)
                            if ek == key and board.get("id") and not existing.get("id"):
                                boards[i] = {**existing, **board}
                    continue
                seen.add(key)
                boards.append(board)
                if len(boards) >= capped:
                    break

    if not boards:
        return None
    log.info("pinterest_user_boards_native_ok", username=user, returned=len(boards[:capped]))
    return boards[:capped]



def _pin_ids_from_serp_html(html: str, *, limit: int = 40) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for pid in re.findall(r"pinterest\.com/pin/(\d{6,})", html or "", re.I):
        if pid in seen:
            continue
        seen.add(pid)
        ids.append(pid)
        if len(ids) >= limit:
            break
    return ids


async def _search_pin_ids_via_serp(q: str, *, limit: int = 40) -> list[str]:
    if not decodo_fetch.enabled():
        return []
    query = quote(f"site:pinterest.com/pin {q}", safe="")
    sources = [
        f"https://www.google.com/search?q={query}&num={min(30, max(10, limit))}",
        f"https://html.duckduckgo.com/html/?q={query}",
    ]
    seen: set[str] = set()
    ids: list[str] = []
    for url in sources:
        got = await decodo_fetch.fetch_url(url, timeout=90.0, headless="html")
        if not got:
            continue
        status, body = got
        if status != 200 or not body:
            continue
        for pid in _pin_ids_from_serp_html(body, limit=limit):
            if pid in seen:
                continue
            seen.add(pid)
            ids.append(pid)
            if len(ids) >= limit:
                break
        if len(ids) >= min(10, limit):
            break
    log.info("pinterest_search_serp_ids", q=q[:80], n=len(ids))
    return ids


async def fetch_pin_info(pin_id: str) -> dict[str, Any] | None:
    """Public widgets pidgets pin info → Apify-like pin dict."""
    pid = (pin_id or "").strip()
    if not pid.isdigit():
        return None
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(
                "https://widgets.pinterest.com/v3/pidgets/pins/info/",
                params={"pin_ids": pid},
            )
    except httpx.HTTPError as exc:
        log.info("pinterest_pin_info_fail", pin_id=pid, error=str(exc))
        return None
    if resp.status_code != 200:
        return None
    try:
        rows = (resp.json() or {}).get("data") or []
    except ValueError:
        return None
    if not rows or not isinstance(rows[0], dict):
        return None
    pin = rows[0]
    # Keep raw pidgets shape; router._normalize_pin already understands it.
    if not pin.get("id"):
        pin["id"] = pid
    if not pin.get("url"):
        pin["url"] = f"https://www.pinterest.com/pin/{pid}/"
    return pin


async def search_pins_native(q: str, *, limit: int = 25) -> list[dict[str, Any]] | None:
    """Keyword pin search via Google/DDG SERP → pidgets hydrate.

    Logged-out Pinterest search HTML does not hydrate pin grids.
    """
    query = (q or "").strip()
    if len(query) < 2 or limit <= 0:
        return None
    ids = await _search_pin_ids_via_serp(query, limit=min(40, max(15, limit * 2)))
    if not ids:
        return None

    import asyncio

    sem = asyncio.Semaphore(6)
    selected = ids[: max(limit * 2, limit + 5)]

    async def _one(pid: str) -> dict[str, Any] | None:
        async with sem:
            return await fetch_pin_info(pid)

    rows = await asyncio.gather(*[_one(pid) for pid in selected])
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        pid = str(row.get("id") or "")
        if not pid or pid in seen:
            continue
        # Prefer rows with some substance.
        if not (row.get("grid_title") or row.get("description") or row.get("images")):
            continue
        seen.add(pid)
        out.append(row)
        if len(out) >= limit:
            break
    if not out:
        return None
    log.info("pinterest_search_native_ok", q=query[:80], n=len(out))
    return out
