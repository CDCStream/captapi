"""Native Facebook comments/replies via Decodo JS-rendered HTML.

Plain DC/residential GETs return 400 on post permalinks. Decodo
``headless=html`` hydrates ScheduledServerJS payloads that embed Comment
Relay nodes (legacy_fbid, body, author, depth, feedback).
"""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str, strip_empty

log = structlog.get_logger(__name__)

# One Decodo JS render is ~$0.001-0.01; flat 2 credits (~120% markup headroom).
CREDIT_FB_COMMENTS_NATIVE = 2

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)


def _iso(ts: Any) -> str | None:
    if isinstance(ts, (int, float)) and ts > 0:
        try:
            return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
        except (OSError, OverflowError, ValueError):
            return None
    return None


def _b64_decode(value: str) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    pad = "=" * (-len(raw) % 4)
    try:
        return base64.b64decode(raw + pad).decode("utf-8", "replace")
    except Exception:
        return None


def _parent_comment_id(node: dict[str, Any]) -> str | None:
    parent = node.get("comment_direct_parent")
    if not isinstance(parent, dict):
        return None
    # Usually a base64 GraphQL id: comment:{postId}_{commentId}
    for key in ("id", "legacy_fbid"):
        val = safe_str(parent.get(key))
        if not val:
            continue
        if val.isdigit():
            return val
        decoded = _b64_decode(val) or val
        if decoded.startswith("comment:"):
            tail = decoded.split("_", 1)[-1]
            if tail.isdigit():
                return tail
        m = re.search(r"_(\d+)$", decoded)
        if m:
            return m.group(1)
    return None


def _like_count(feedback: dict[str, Any]) -> int:
    reactors = feedback.get("reactors")
    if isinstance(reactors, dict):
        n = safe_int(reactors.get("count") or reactors.get("count_reduced"))
        if n is not None:
            return n
    top = feedback.get("top_reactions")
    if isinstance(top, dict):
        edges = top.get("edges")
        if isinstance(edges, list):
            total = 0
            for edge in edges:
                if isinstance(edge, dict):
                    total += safe_int(edge.get("reaction_count")) or 0
            return total
    return 0


def _avatar(author: dict[str, Any]) -> str | None:
    for key in (
        "profile_picture_depth_0",
        "profile_picture_depth_0_increased",
        "profile_picture_depth_1",
        "profile_picture",
    ):
        pic = author.get(key)
        if isinstance(pic, dict):
            uri = safe_str(pic.get("uri"))
            if uri:
                return uri
    return None


def _map_comment(node: dict[str, Any], *, include_reply_count: bool) -> dict[str, Any] | None:
    cid = safe_str(node.get("legacy_fbid"))
    body = node.get("body") if isinstance(node.get("body"), dict) else {}
    text = body.get("text")
    if not cid or not isinstance(text, str):
        return None
    author = node.get("author") if isinstance(node.get("author"), dict) else {}
    feedback = node.get("feedback") if isinstance(node.get("feedback"), dict) else {}
    replies = feedback.get("replies_fields") if isinstance(feedback.get("replies_fields"), dict) else {}
    author_url = safe_str(author.get("url"))
    row: dict[str, Any] = {
        "id": cid,
        "url": safe_str(feedback.get("url")),
        "text": text,
        "author": safe_str(author.get("name")),
        "authorUrl": author_url,
        "authorAvatarUrl": _avatar(author),
        "likeCount": _like_count(feedback),
        "publishedAt": _iso(node.get("created_time")),
    }
    if include_reply_count:
        row["replyCount"] = safe_int(replies.get("total_count") or replies.get("count")) or 0
    cleaned = strip_empty(row)
    # Always expose authorUrl for typed clients (null when FB omits profile url).
    cleaned["authorUrl"] = author_url
    return cleaned


def _walk_comments(obj: Any, found: list[dict[str, Any]], depth: int = 0) -> None:
    if depth > 40:
        return
    if isinstance(obj, dict):
        if obj.get("__typename") == "Comment" and isinstance(obj.get("body"), dict):
            found.append(obj)
        for value in obj.values():
            _walk_comments(value, found, depth + 1)
    elif isinstance(obj, list):
        for value in obj:
            _walk_comments(value, found, depth + 1)


def _extract_comment_nodes(html: str) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for match in _SCRIPT_RE.finditer(html):
        raw = match.group(1)
        if '"__typename":"Comment"' not in raw:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        _walk_comments(data, nodes)
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for node in nodes:
        cid = safe_str(node.get("legacy_fbid"))
        if not cid or cid in seen:
            continue
        seen.add(cid)
        out.append(node)
    return out


async def _fetch_html(url: str) -> str | None:
    if not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body:
        return None
    if '"__typename":"Comment"' not in body and "legacy_fbid" not in body:
        return None
    return body


def _with_comment_id(url: str, comment_id: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["comment_id"] = comment_id
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


async def comments_native(url: str, limit: int) -> list[dict[str, Any]] | None:
    """Top-level comments (depth == 0) for a public Facebook post."""
    if limit <= 0:
        return []
    html = await _fetch_html(url)
    if not html:
        return None
    mapped: list[dict[str, Any]] = []
    for node in _extract_comment_nodes(html):
        depth = safe_int(node.get("depth")) or 0
        if depth != 0:
            continue
        row = _map_comment(node, include_reply_count=True)
        if row:
            mapped.append(row)
        if len(mapped) >= limit:
            break
    return mapped if mapped else None


async def comment_replies_native(
    url: str, comment_id: str, limit: int
) -> list[dict[str, Any]] | None:
    """Direct replies to ``comment_id`` (depth >= 1, direct parent match)."""
    if limit <= 0:
        return []
    cid = (comment_id or "").strip()
    if not cid:
        return None
    # Focused permalink surfaces more of the reply thread than the bare post.
    html = await _fetch_html(_with_comment_id(url, cid))
    if html is None:
        html = await _fetch_html(url)
    if not html:
        return None
    mapped: list[dict[str, Any]] = []
    for node in _extract_comment_nodes(html):
        depth = safe_int(node.get("depth")) or 0
        if depth < 1:
            continue
        if _parent_comment_id(node) != cid:
            continue
        row = _map_comment(node, include_reply_count=False)
        if row:
            mapped.append(row)
        if len(mapped) >= limit:
            break
    return mapped if mapped else None
