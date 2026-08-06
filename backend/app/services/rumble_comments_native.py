"""Native Rumble comments via Decodo JS-rendered HTML.

Datacenter / residential / Apify residential hit Cloudflare 403. Decodo
``headless=html`` returns the hydrated comment list with ``data-comment-id``
cards (author, text, votes, reply counts).
"""

from __future__ import annotations

import re
from html import unescape
from typing import Any

import structlog

from app.services import decodo_fetch
from app.services.rumble_video_native import to_utc_published_at
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

CREDIT_RUMBLE_COMMENTS_NATIVE = 2

_ITEM_START_RE = re.compile(
    r'<li class="comment-item[^"]*"\s+'
    r'data-comment-id="(\d+)"\s+'
    r'data-num-replies="(\d+)"\s+'
    r'data-username="([^"]+)"',
    re.I,
)
_TEXT_RE = re.compile(r'<p class="comment-text">(.*?)</p>', re.S | re.I)
_UPVOTES_RE = re.compile(
    r'rumbles-vote-up[\s\S]*?<span class="rumbles-up-votes">(\d+)</span>',
    re.I,
)
# Attribute names that carry a machine-readable timestamp (any order on the tag).
_TIME_ATTR_KEYS = ("datetime", "data-time", "data-timestamp", "data-unix", "data-ts")
_ATTR_RE = re.compile(
    r"""([^\s=/>]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""",
    re.I,
)
_TIME_TAG_RE = re.compile(r"<time\b([^>]*)>", re.I)
_META_TIME_TAG_RE = re.compile(
    r"<[^>]*\bcomments-meta-post-time\b[^>]*>",
    re.I,
)


def _strip_tags(raw: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", raw or "")).strip()


def _attrs_map(attr_blob: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _ATTR_RE.finditer(attr_blob or ""):
        key = (m.group(1) or "").lower()
        val = m.group(2) if m.group(2) is not None else m.group(3)
        if key and val is not None:
            out[key] = val
    return out


def _raw_from_attrs(attrs: dict[str, str]) -> str | None:
    for key in _TIME_ATTR_KEYS:
        raw = safe_str(attrs.get(key))
        if raw:
            return raw
    return None


def comment_published_raw(chunk: str) -> str | None:
    """Pull a machine-readable timestamp from a comment card HTML slice.

    Attribute order varies (``datetime`` before/after ``class``). Prefer any
    ``<time>`` tag, then a ``comments-meta-post-time`` wrapper. Never use
    ``title=`` / textContent display strings.
    """
    for m in _TIME_TAG_RE.finditer(chunk or ""):
        raw = _raw_from_attrs(_attrs_map(m.group(1)))
        if raw:
            return raw
    for m in _META_TIME_TAG_RE.finditer(chunk or ""):
        raw = _raw_from_attrs(_attrs_map(m.group(0)))
        if raw:
            return raw
    return None


def _is_nested(html: str, pos: int) -> bool:
    """True when the comment-item sits under a nested ``comments-2`` list."""
    before = html[:pos]
    last_ul = before.rfind("<ul")
    if last_ul < 0:
        return False
    opener = html[last_ul : last_ul + 64].lower()
    return "comments-2" in opener


def parse_comments_html(html: str, limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    starts = list(_ITEM_START_RE.finditer(html))
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, match in enumerate(starts):
        if _is_nested(html, match.start()):
            continue
        cid, num_replies, username = match.groups()
        if cid in seen:
            continue
        seen.add(cid)
        end = starts[idx + 1].start() if idx + 1 < len(starts) else min(len(html), match.end() + 4000)
        chunk = html[match.start() : end]
        text_m = _TEXT_RE.search(chunk)
        text = _strip_tags(text_m.group(1)) if text_m else ""
        if not text:
            continue
        up_m = _UPVOTES_RE.search(chunk)
        published = to_utc_published_at(comment_published_raw(chunk))
        out.append(
            {
                "platform": "rumble",
                "id": cid,
                "text": text,
                "author": {
                    "name": unescape(username),
                    "url": f"https://rumble.com/user/{unescape(username)}",
                    "verified": False,
                },
                "likes": safe_int(up_m.group(1)) if up_m else 0,
                "replyCount": safe_int(num_replies) or 0,
                "publishedAt": published,
            }
        )
        if len(out) >= limit:
            break
    return out


async def comments_native(url: str, limit: int) -> list[dict[str, Any]] | None:
    if limit <= 0:
        return []
    if not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body or "data-comment-id=" not in body:
        return None
    parsed = parse_comments_html(body, limit)
    return parsed if parsed else None
