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
from app.utils.formatters import safe_int, safe_str, strip_empty

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
_TIME_RE = re.compile(
    r'comments-meta-post-time[^>]*title="([^"]+)"',
    re.I,
)


def _strip_tags(raw: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", raw or "")).strip()


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
        time_m = _TIME_RE.search(chunk)
        out.append(
            strip_empty(
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
                    "createdAt": safe_str(time_m.group(1) if time_m else None),
                }
            )
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
