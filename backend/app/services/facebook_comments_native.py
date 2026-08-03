"""Native Facebook comments/replies via Decodo JS-rendered HTML.

Plain DC/residential GETs return 400 on post permalinks. Decodo
``headless=html`` hydrates ScheduledServerJS payloads that embed Comment
Relay nodes (legacy_fbid, body, author, depth, feedback with top_reactions).
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

# Facebook GraphQL reaction node ids → Captapi / SC camel-friendly keys.
# Source: public FB reaction enum used by Comet UFI (Like/Love/Care/…).
_REACTION_ID_TO_KEY: dict[str, str] = {
    "1635855486666999": "like",
    "1678524932434102": "love",
    "613557422527858": "care",
    "115940658764963": "haha",
    "478547315650144": "wow",
    "908563459236466": "sad",
    "444813342392137": "anger",
}

# SC's 10-type shape (temporary pride/thankful/confused stay 0 when FB omits them).
_REACTION_KEYS: tuple[str, ...] = (
    "like",
    "love",
    "care",
    "haha",
    "wow",
    "sad",
    "anger",
    "thankful",
    "pride",
    "confused",
)

_REACTION_NAME_ALIASES: dict[str, str] = {
    "like": "like",
    "love": "love",
    "care": "care",
    "haha": "haha",
    "wow": "wow",
    "sad": "sad",
    "sorry": "sad",
    "anger": "anger",
    "angry": "anger",
    "thankful": "thankful",
    "pride": "pride",
    "confused": "confused",
}


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


def _b64_encode(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def feedback_post_id(feedback_id: str | None) -> str | None:
    """Decode ``feedback:POSTID`` (raw or base64) → numeric post id."""
    raw = (feedback_id or "").strip()
    if not raw:
        return None
    decoded = _b64_decode(raw) or raw
    if decoded.startswith("feedback:"):
        tail = decoded.split(":", 1)[1]
        post = tail.split("_", 1)[0]
        return post if post.isdigit() else None
    if raw.isdigit():
        return raw
    return None


def resolve_comments_url(*, url: str | None, feedback_id: str | None) -> str:
    """Prefer an explicit post URL; otherwise build one from feedbackId."""
    if url and str(url).strip():
        return str(url).strip()
    post_id = feedback_post_id(feedback_id)
    if post_id:
        return f"https://www.facebook.com/{post_id}"
    raise ValueError("Pass url or feedbackId (from /v1/facebook/details).")


def post_feedback_id_from_comment_feedback(feedback_id: str | None) -> str | None:
    """Comment feedback ``feedback:POST_COMMENT`` → post-level feedback id (b64)."""
    post_id = feedback_post_id(feedback_id)
    if not post_id:
        return None
    return _b64_encode(f"feedback:{post_id}")


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


def _reaction_key_from_node(node: dict[str, Any]) -> str | None:
    rid = safe_str(node.get("id"))
    if rid and rid in _REACTION_ID_TO_KEY:
        return _REACTION_ID_TO_KEY[rid]
    for field in ("reaction_type", "localized_name", "name", "key"):
        raw = safe_str(node.get(field))
        if not raw:
            continue
        alias = _REACTION_NAME_ALIASES.get(raw.strip().lower())
        if alias:
            return alias
    return None


def empty_reactions() -> dict[str, int]:
    return {k: 0 for k in _REACTION_KEYS}


def reactions_from_feedback(feedback: dict[str, Any]) -> tuple[int, dict[str, int]]:
    """Return (reactionCount, reactions{}) from a Comment feedback node."""
    reactions = empty_reactions()
    top = feedback.get("top_reactions")
    if isinstance(top, dict):
        edges = top.get("edges")
        if isinstance(edges, list):
            for edge in edges:
                if not isinstance(edge, dict):
                    continue
                node = edge.get("node") if isinstance(edge.get("node"), dict) else {}
                key = _reaction_key_from_node(node)
                count = safe_int(edge.get("reaction_count")) or 0
                if key and count:
                    reactions[key] += count

    total = 0
    reactors = feedback.get("reactors")
    if isinstance(reactors, dict):
        total = safe_int(reactors.get("count") or reactors.get("count_reduced")) or 0
    summed = sum(reactions.values())
    if total <= 0:
        total = summed
    # Prefer the richer breakdown total when reactors collapses types oddly.
    if summed > total:
        total = summed
    return total, reactions


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


def _short_name(author: dict[str, Any], name: str | None) -> str | None:
    sn = safe_str(author.get("short_name") or author.get("shortName"))
    if sn:
        return sn
    if name:
        first = name.strip().split(None, 1)[0] if name.strip() else None
        return first
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
    author_name = safe_str(author.get("name"))
    author_id = safe_str(author.get("id"))
    gender = safe_str(author.get("gender"))
    avatar = _avatar(author)
    reaction_count, reactions = reactions_from_feedback(feedback)

    author_obj: dict[str, Any] = {
        "id": author_id,
        "name": author_name,
        "shortName": _short_name(author, author_name),
        "gender": gender,
        "url": author_url,
        "avatarUrl": avatar,
    }
    # Keep stable author object keys even when FB omits url/gender.
    author_clean = {k: v for k, v in author_obj.items() if v is not None}

    row: dict[str, Any] = {
        "id": cid,
        "url": safe_str(feedback.get("url")),
        "text": text,
        # Nested author (SC parity) — id is the stable pfbid / numeric identity.
        "author": author_clean,
        # Flat BC fields (pre-nested author clients).
        "authorUrl": author_url,
        "authorAvatarUrl": avatar,
        "likeCount": reaction_count,
        "reactionCount": reaction_count,
        "reactions": reactions,
        "publishedAt": _iso(node.get("created_time")),
    }
    if include_reply_count:
        row["replyCount"] = safe_int(replies.get("total_count") or replies.get("count")) or 0

    cleaned = strip_empty(row)
    # Always expose these for typed clients.
    cleaned["authorUrl"] = author_url
    cleaned["authorAvatarUrl"] = avatar
    cleaned["reactions"] = reactions
    cleaned["likeCount"] = reaction_count
    cleaned["reactionCount"] = reaction_count
    if include_reply_count:
        cleaned["replyCount"] = row["replyCount"]
    # Ensure author object survives strip_empty and keeps id when present.
    if author_clean:
        cleaned["author"] = author_clean
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


def _page_feedback_id(nodes: list[dict[str, Any]]) -> str | None:
    for node in nodes:
        feedback = node.get("feedback") if isinstance(node.get("feedback"), dict) else {}
        fid = post_feedback_id_from_comment_feedback(safe_str(feedback.get("id")))
        if fid:
            return fid
    return None


async def comments_native(url: str, limit: int) -> dict[str, Any] | None:
    """Top-level comments (depth == 0) for a public Facebook post."""
    if limit <= 0:
        return {"comments": [], "hasMore": False, "nextCursor": None, "feedbackId": None}
    html = await _fetch_html(url)
    if not html:
        return None
    nodes = _extract_comment_nodes(html)
    mapped: list[dict[str, Any]] = []
    for node in nodes:
        depth = safe_int(node.get("depth")) or 0
        if depth != 0:
            continue
        row = _map_comment(node, include_reply_count=True)
        if row:
            mapped.append(row)
    if not mapped:
        return None
    page = mapped[:limit]
    has_more = len(mapped) > limit
    return {
        "comments": page,
        "hasMore": has_more,
        # HTML first-page scrape — real GraphQL cursor paging is not wired yet.
        "nextCursor": None,
        "feedbackId": _page_feedback_id(nodes),
    }


async def comment_replies_native(
    url: str, comment_id: str, limit: int
) -> dict[str, Any] | None:
    """Direct replies to ``comment_id`` (depth >= 1, direct parent match)."""
    if limit <= 0:
        return {"replies": [], "hasMore": False, "nextCursor": None}
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
    if not mapped:
        return None
    page = mapped[:limit]
    return {
        "replies": page,
        "hasMore": len(mapped) > limit,
        "nextCursor": None,
    }
