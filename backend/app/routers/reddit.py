"""Reddit endpoints (subreddit posts, post details, comments, search).

Native-first via Reddit public JSON / OAuth; Decodo for blocked post fetches.
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode, urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services import decodo_fetch
from app.services.http_fetch import fetch as proxy_fetch
from app.services.cached_runner import cached_or_run
from app.utils.formatters import first_present, safe_float, safe_int, safe_str
from app.utils.text_transcript import TIMING_NONE, count_words, finalize_text_segments
from app.utils.url import (
    detect_url_platform,
    extract_reddit_post_id,
    extract_subreddit,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
# Native public JSON / OAuth / Decodo lists — flat 2 (Apify fallthrough removed).
CREDIT_LIST = 2


def _reject_reddit_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "reddit":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "reddit", example),
        )


def _require_subreddit(value: str) -> str:
    _reject_reddit_platform_mismatch(value, "https://www.reddit.com/r/python")
    sub = extract_subreddit(value)
    if not sub:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "reddit", "https://www.reddit.com/r/python"),
        )
    return sub


def _require_reddit_post_url(url: str) -> str:
    post_id = extract_reddit_post_id(url)
    if not post_id:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                url,
                "reddit",
                "https://www.reddit.com/r/python/comments/post_id/title/",
            ),
        )
    return post_id


def _is_comment(item: dict[str, Any]) -> bool:
    dt = (item.get("dataType") or item.get("type") or item.get("kind") or "").lower()
    return dt == "comment" or item.get("body") is not None and item.get("title") is None


def _is_post(item: dict[str, Any]) -> bool:
    """True only for real post rows.

    The trudax actor also emits `dataType: "community"` rows (t5_...) for the
    subreddit itself; those must not leak into post lists.
    """
    dt = (item.get("dataType") or item.get("type") or item.get("kind") or "").lower()
    if dt:
        return dt == "post"
    return (safe_str(item.get("id")) or "").startswith("t3_") or (
        item.get("title") is not None and not _is_comment(item)
    )


_THUMB_PLACEHOLDERS = {"self", "default", "nsfw", "spoiler", "image"}


def _epoch_to_iso(value: Any) -> str | None:
    """Unix seconds (int/float/digit-string) → catalog ISO ``…000Z``. Never echo raw epochs."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and value > 0:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    if isinstance(value, str):
        s = value.strip()
        if re.fullmatch(r"\d+(?:\.\d+)?", s):
            try:
                return _epoch_to_iso(float(s))
            except (ValueError, OverflowError):
                return None
        # Normalize already-parsed ISO strings to the same ``…Z`` shape.
        if "T" in s:
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            except ValueError:
                return None
    return None


# Reddit /search.json sort values. ``comment_count`` is the ScrapeCreators alias
# for Reddit's ``comments``.
_SEARCH_SORTS = {
    "relevance": "relevance",
    "hot": "hot",
    "top": "top",
    "new": "new",
    "comments": "comments",
    "comment_count": "comments",
}
_SEARCH_TIMEFRAMES = {"hour", "day", "week", "month", "year", "all"}


def _resolve_search_sort_timeframe(
    sort: str | None, timeframe: str | None
) -> tuple[str, str | None]:
    """Return ``(reddit_sort, t_param_or_none)`` for site/subreddit search."""
    sort_key = (sort or "relevance").strip().lower()
    reddit_sort = _SEARCH_SORTS.get(sort_key)
    if not reddit_sort:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort. Use relevance, new, top, hot, comments, "
                "or comment_count."
            ),
        )
    resolved_t: str | None = None
    # Reddit honors ``t`` for top/comments (and sometimes hot); always accept
    # an explicit timeframe, default ``all`` when sort needs a window.
    if reddit_sort in {"top", "comments"} or timeframe:
        t_raw = (timeframe or ("all" if reddit_sort in {"top", "comments"} else None))
        if t_raw is not None:
            t_raw = t_raw.strip().lower()
            if t_raw not in _SEARCH_TIMEFRAMES:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid timeframe. Use hour, day, week, month, year, or all.",
                )
            resolved_t = t_raw
    return reddit_sort, resolved_t


def _reddit_vote_fields(item: dict[str, Any]) -> dict[str, Any]:
    """Map Reddit vote fields without inventing score from ups/downs.

    Public JSON almost always sends ``downs: 0`` (fuzzing). ``score`` is the
    authoritative net score when Reddit exposes it. New posts with
    ``hide_score`` return score/ups as 0 while ``upvote_ratio`` may still be set
    — that is Reddit, not ``ups - downs``.
    """
    score = safe_int(item.get("score"))
    ups = safe_int(first_present(item.get("ups"), item.get("upVotes")))
    # Mirror score only when ups is omitted — never overwrite a real 0.
    if ups is None:
        ups = score
    downs = safe_int(item.get("downs"))
    hide = first_present(
        item.get("hide_score"),
        item.get("scoreHidden"),
        item.get("score_hidden"),
    )
    return {
        "upvotes": ups,
        "score": score,
        "downs": downs,
        "upvoteRatio": safe_float(item.get("upvoteRatio") or item.get("upvote_ratio")),
        "scoreHidden": bool(hide) if hide is not None else None,
    }


def _normalize_post(item: dict[str, Any]) -> dict[str, Any]:
    thumbnail = safe_str(item.get("thumbnailUrl") or item.get("thumbnail"))
    if thumbnail in _THUMB_PLACEHOLDERS:
        thumbnail = None
    published = _epoch_to_iso(item.get("createdAt") or item.get("created") or item.get("created_utc"))
    if not isinstance(published, str):
        published = safe_str(published)
    votes = _reddit_vote_fields(item)
    is_video = first_present(item.get("isVideo"), item.get("is_video"))
    post_id = safe_str(item.get("id") or item.get("parsedId"))
    fullname = safe_str(item.get("name"))
    if not fullname and post_id:
        fullname = post_id if post_id.startswith("t3_") else f"t3_{post_id}"
    return {
        "platform": "reddit",
        "id": post_id,
        "name": fullname,
        "url": safe_str(item.get("canonical_url") or item.get("url")),
        "title": safe_str(item.get("title")),
        "text": safe_str(item.get("body") or item.get("text") or item.get("selftext")),
        "subreddit": safe_str(item.get("communityName") or item.get("subreddit") or item.get("parsedCommunityName")),
        "author": safe_str(item.get("username") or item.get("author")),
        "authorFullname": safe_str(item.get("authorFullname") or item.get("author_fullname")),
        **votes,
        "comments": safe_int(
            first_present(item.get("numberOfComments"), item.get("numComments"), item.get("num_comments"))
        ),
        "subscriberCount": safe_int(
            item.get("subscriberCount") or item.get("subreddit_subscribers")
        ),
        "totalAwardsReceived": safe_int(
            item.get("totalAwardsReceived") or item.get("total_awards_received")
        ),
        "isVideo": bool(is_video) if is_video is not None else None,
        "publishedAt": published,
        "flair": safe_str(item.get("flair") or item.get("link_flair_text")),
        "nsfw": first_present(item.get("over18"), item.get("nsfw"), item.get("over_18")),
        "thumbnail": thumbnail,
    }


def _normalize_comment(item: dict[str, Any]) -> dict[str, Any]:
    published = item.get("createdAt") or item.get("created") or item.get("created_utc")
    published = _epoch_to_iso(published)
    if not isinstance(published, str):
        published = safe_str(published)
    score = safe_int(first_present(item.get("score"), item.get("ups"), item.get("upVotes")))
    ups = safe_int(first_present(item.get("ups"), item.get("upVotes"), score))
    return {
        "id": safe_str(item.get("id")),
        "author": safe_str(item.get("username") or item.get("author")),
        "authorFullname": safe_str(item.get("authorFullname") or item.get("author_fullname")),
        "text": safe_str(item.get("body") or item.get("text")),
        # Keep upvotes for existing clients; prefer true ups when Reddit sends them.
        "upvotes": ups,
        "score": score,
        "downs": safe_int(item.get("downs")),
        "publishedAt": published,
        "url": safe_str(item.get("url") or item.get("permalink")),
        "parentId": safe_str(item.get("parentId") or item.get("parent_id")),
        "depth": safe_int(item.get("depth")),
        "isSubmitter": first_present(item.get("isSubmitter"), item.get("is_submitter")),
        # Reddit may send edited as False or a timestamp; coerce to bool, keep False.
        "edited": bool(item.get("edited")) if item.get("edited") is not None else None,
        "stickied": bool(item.get("stickied")) if item.get("stickied") is not None else None,
        "distinguished": safe_str(item.get("distinguished")),
        "controversiality": safe_int(item.get("controversiality")),
        "subreddit": safe_str(item.get("subreddit")),
    }


def _reddit_json_url_variants(url: str, post_id: str) -> list[str]:
    parsed = urlparse(url if "://" in url else f"https://www.reddit.com/comments/{post_id}")
    path = parsed.path or f"/comments/{post_id}"
    if not path.endswith(".json"):
        path = path.rstrip("/") + ".json"
    return [
        f"https://www.reddit.com/comments/{post_id}.json",
        f"https://www.reddit.com{path}",
        f"https://old.reddit.com{path}",
        f"https://oauth.reddit.com{path}",
    ]


_reddit_oauth_token: str | None = None
_reddit_oauth_expiry: float = 0.0


async def _reddit_oauth_headers() -> dict[str, str] | None:
    """Application-only OAuth token for oauth.reddit.com (works from
    datacenter IPs). Returns None when no app credentials are configured."""
    global _reddit_oauth_token, _reddit_oauth_expiry
    settings = get_settings()
    if not (settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET):
        return None
    import time

    if _reddit_oauth_token and time.time() < _reddit_oauth_expiry - 60:
        return {"Authorization": f"Bearer {_reddit_oauth_token}", "User-Agent": "CaptapiBot/1.0 (+https://captapi.com)"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": "CaptapiBot/1.0 (+https://captapi.com)"},
            )
        payload = resp.json()
        token = payload.get("access_token")
        if not token:
            return None
        _reddit_oauth_token = token
        _reddit_oauth_expiry = time.time() + float(payload.get("expires_in") or 3600)
        return {"Authorization": f"Bearer {token}", "User-Agent": "CaptapiBot/1.0 (+https://captapi.com)"}
    except (httpx.HTTPError, ValueError):
        return None


async def _fetch_reddit_json_url(
    url: str, limit: int
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    headers = {"User-Agent": "CaptapiBot/1.0 (+https://captapi.com)"}
    if "oauth.reddit.com" in url:
        oauth = await _reddit_oauth_headers()
        if not oauth:
            raise HTTPException(status_code=502, detail="Reddit upstream error")
        headers = oauth
    params = {"raw_json": "1", "limit": max(limit, 1)}
    resp: httpx.Response | None = None
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
            resp = await client.get(url, params=params)
    except httpx.HTTPError:
        resp = None
    # No proxy retry: Reddit 403s both datacenter and residential proxies
    # (fingerprint-based blocking, measured 0/16 success), so a failed direct
    # attempt goes straight to the Apify actor fallback instead of burning
    # seconds on doomed proxied retries.
    if resp is None:
        raise HTTPException(status_code=502, detail="Reddit upstream error")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Post not found")
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail="Reddit upstream error")

    return _parse_reddit_post_payload(resp.json(), limit)


def _parse_reddit_post_payload(
    data: Any, limit: int
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    """Normalize a ``/comments/<id>.json`` payload (shared by the direct and
    Decodo fetch paths). Returns ``(post, comments, has_more)``."""
    if not isinstance(data, list) or not data:
        raise HTTPException(status_code=404, detail="Post not found")
    post_children = (data[0].get("data") or {}).get("children") or []
    if not post_children:
        raise HTTPException(status_code=404, detail="Post not found")
    raw_post = post_children[0].get("data") or {}
    created = raw_post.get("created_utc")
    if isinstance(created, (int, float)):
        created = datetime.fromtimestamp(int(created), tz=timezone.utc).isoformat()
    post = {
        "id": raw_post.get("id"),
        "url": f"https://www.reddit.com{raw_post.get('permalink')}" if raw_post.get("permalink") else raw_post.get("url"),
        "title": raw_post.get("title"),
        "body": raw_post.get("selftext"),
        "subreddit": raw_post.get("subreddit"),
        "author": raw_post.get("author"),
        "author_fullname": raw_post.get("author_fullname"),
        # Prefer Reddit's score key even when 0 (hide_score) — never ``or ups``.
        "score": raw_post.get("score"),
        "ups": raw_post.get("ups"),
        "downs": raw_post.get("downs"),
        "upvote_ratio": raw_post.get("upvote_ratio"),
        "hide_score": raw_post.get("hide_score"),
        "numComments": raw_post.get("num_comments"),
        "subreddit_subscribers": raw_post.get("subreddit_subscribers"),
        "created": created,
        "flair": raw_post.get("link_flair_text"),
        "nsfw": raw_post.get("over_18"),
        "thumbnail": raw_post.get("thumbnail"),
        "is_video": raw_post.get("is_video"),
    }

    comments: list[dict[str, Any]] = []
    has_more = False

    def walk(children: list[dict[str, Any]]) -> None:
        nonlocal has_more
        for child in children:
            kind = child.get("kind")
            if kind == "more":
                has_more = True
                continue
            if kind != "t1":
                continue
            raw = child.get("data") or {}
            comments.append({
                "id": raw.get("id"),
                "author": raw.get("author"),
                "author_fullname": raw.get("author_fullname"),
                "body": raw.get("body"),
                "score": raw.get("score"),
                "ups": raw.get("ups"),
                "downs": raw.get("downs"),
                "created": _epoch_to_iso(raw.get("created_utc")),
                "url": f"https://www.reddit.com{raw.get('permalink')}" if raw.get("permalink") else None,
                "parent_id": raw.get("parent_id"),
                "depth": raw.get("depth"),
                "is_submitter": raw.get("is_submitter"),
                "edited": raw.get("edited"),
                "stickied": raw.get("stickied"),
                "distinguished": raw.get("distinguished"),
                "controversiality": raw.get("controversiality"),
                "subreddit": raw.get("subreddit"),
            })
            replies = raw.get("replies")
            reply_children = ((replies or {}).get("data") or {}).get("children") if isinstance(replies, dict) else []
            if isinstance(reply_children, list) and len(comments) < limit:
                walk(reply_children)
            elif isinstance(reply_children, list) and reply_children:
                has_more = True

    comment_listing = data[1] if len(data) > 1 else {}
    walk(((comment_listing.get("data") or {}).get("children") or []))
    trimmed = comments[:limit]
    if len(comments) > limit:
        has_more = True
    return _normalize_post(post), [_normalize_comment(c) for c in trimmed], has_more


async def _fetch_reddit_json_post(
    url: str, post_id: str, limit: int
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    """Fetch a post and comments from Reddit public JSON variants before actor fallback."""
    last_error: HTTPException | None = None
    seen: set[str] = set()
    variants = _reddit_json_url_variants(url, post_id)
    settings = get_settings()
    if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
        # OAuth works reliably from datacenter IPs; try it first to avoid
        # burning time on the blocked anonymous variants.
        variants.sort(key=lambda u: 0 if "oauth.reddit.com" in u else 1)
    for candidate in variants:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            return await _fetch_reddit_json_url(candidate, limit)
        except HTTPException as exc:
            if exc.status_code not in {502, 503, 504}:
                raise
            last_error = exc
    raise last_error or HTTPException(status_code=502, detail="Reddit upstream error")


# Reddit's public JSON is datacenter-blocked, so post endpoints always land on
# an actor. The two actors run back-to-back in the resilient cascade; with the
# global 120s sync timeout a deleted/blocked post could burn ~250s before
# failing (measured). Cap each actor so the whole cascade stays well under a
async def _reddit_post_exists_decodo(post_id: str) -> bool | None:
    """Authoritative existence probe via ``api/info.json`` through Decodo
    (~3s measured). Returns None when the probe itself failed.

    This matters for dead posts: ``comments/<id>.json`` 404s make Decodo
    retry internally for ~35s, and the Apify actors burn ~75s each before
    timing out — but info.json returns 200 with an empty listing instantly.
    """
    fetched = await decodo_fetch.fetch_json(
        f"https://www.reddit.com/api/info.json?id=t3_{post_id}&raw_json=1",
        timeout=20.0,
    )
    if fetched is None or fetched[0] != 200 or not isinstance(fetched[1], dict):
        return None
    children = ((fetched[1].get("data") or {}).get("children")) or []
    return len(children) > 0


async def _fetch_reddit_post_decodo(
    post_id: str, limit: int
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    """Post + comments via Decodo's scraping pool (~1-3s measured; Reddit
    doesn't fingerprint-block it, unlike our datacenter/residential proxies).

    Raises 404 fast for dead/deleted posts (info.json probe) so the cascade
    exits in seconds as a client error instead of burning ~150s of doomed
    actor runs that surface as 5xx on the status page.
    """
    exists = await _reddit_post_exists_decodo(post_id)
    if exists is False:
        raise HTTPException(status_code=404, detail="Post not found")
    fetched = await decodo_fetch.fetch_json(
        f"https://www.reddit.com/comments/{post_id}.json?raw_json=1&limit={max(limit, 1)}",
        timeout=15.0,
    )
    if fetched is None:
        raise HTTPException(status_code=502, detail="Reddit upstream error")
    status, payload = fetched
    if status == 404:
        raise HTTPException(status_code=404, detail="Post not found")
    if status >= 400 or payload is None:
        raise HTTPException(status_code=502, detail="Reddit upstream error")
    return _parse_reddit_post_payload(payload, limit)


async def _fetch_reddit_post_resilient(
    url: str,
    post_id: str,
    limit: int,
    ctx: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    try:
        result = await _fetch_reddit_json_post(url, post_id, limit)
        if ctx is not None:
            ctx["source"] = "direct"
        return result
    except HTTPException as exc:
        if exc.status_code not in {502, 503, 504}:
            raise
    # Decodo second: fast, cheap, and its 404 is authoritative (dead post →
    # fail in ~2s as a client error instead of ~150s of actor timeouts that
    # show up as 5xx on the status page).
    if decodo_fetch.enabled():
        try:
            result = await _fetch_reddit_post_decodo(post_id, limit)
            if ctx is not None:
                ctx["source"] = "direct"
            return result
        except HTTPException as exc:
            if exc.status_code not in {502, 503, 504}:
                raise
    raise HTTPException(
        status_code=502,
        detail="Reddit upstream error, please retry",
    )


async def _reddit_listing_json(
    path: str,
    params: dict[str, Any],
    limit: int,
    *,
    after: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    """Fetch a Reddit public JSON listing (search or subreddit feed) natively.

    Returns ``([], None)`` on any upstream problem so callers can fall back to
    the actor. Unlike the trudax lite actor, the public JSON includes scores and
    comment counts, so posts come back with full engagement data.
    """
    headers = {"User-Agent": "CaptapiBot/1.0 (+https://captapi.com)"}
    query = {"raw_json": "1", "limit": max(limit, 1), **params}
    if after:
        query["after"] = after

    async def _attempt_direct(base: str) -> Any | None:
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(f"{base}{path}", params=query)
        except httpx.HTTPError:
            return None
        if resp.status_code >= 400:
            return None
        try:
            return resp.json()
        except ValueError:
            return None

    async def _attempt_decodo() -> Any | None:
        if not decodo_fetch.enabled():
            return None
        qs = urlencode(query)
        fetched = await decodo_fetch.fetch_json(f"https://www.reddit.com{path}?{qs}", timeout=25.0)
        if fetched is None or fetched[0] >= 400:
            return None
        return fetched[1]

    attempts = [
        lambda: _attempt_direct("https://www.reddit.com"),
        lambda: _attempt_direct("https://old.reddit.com"),
        # Decodo's pool isn't fingerprint-blocked by Reddit (direct requests
        # from Railway usually are), so it rescues listings before the actor.
        _attempt_decodo,
    ]
    for attempt in attempts:
        payload = await attempt()
        if payload is None:
            continue
        listing = (payload.get("data") or {}) if isinstance(payload, dict) else {}
        children = listing.get("children") or []
        posts: list[dict[str, Any]] = []
        for child in children:
            raw = child.get("data") if isinstance(child, dict) else None
            if not isinstance(raw, dict) or child.get("kind") != "t3":
                continue
            thumb = raw.get("thumbnail")
            if thumb in {"self", "default", "nsfw", "spoiler", "image"}:
                thumb = None
            posts.append(
                _normalize_post(
                    {
                        "id": raw.get("id"),
                        "name": raw.get("name"),
                        "url": (
                            f"https://www.reddit.com{raw.get('permalink')}"
                            if raw.get("permalink")
                            else raw.get("url")
                        ),
                        "title": raw.get("title"),
                        "body": raw.get("selftext"),
                        "subreddit": raw.get("subreddit"),
                        "author": raw.get("author"),
                        "author_fullname": raw.get("author_fullname"),
                        "score": raw.get("score"),
                        "ups": raw.get("ups"),
                        "downs": raw.get("downs"),
                        "upvote_ratio": raw.get("upvote_ratio"),
                        "hide_score": raw.get("hide_score"),
                        "numComments": raw.get("num_comments"),
                        "subreddit_subscribers": raw.get("subreddit_subscribers"),
                        "total_awards_received": raw.get("total_awards_received"),
                        "is_video": raw.get("is_video"),
                        "created": raw.get("created_utc"),
                        "flair": raw.get("link_flair_text"),
                        "nsfw": raw.get("over_18"),
                        "thumbnail": thumb,
                    }
                )
            )
        if posts:
            next_after = safe_str(listing.get("after")) or None
            return posts[:limit], next_after
    return [], None


_SUBREDDIT_SORTS = {
    "best": "hot",  # subreddit "best" is Reddit hot
    "hot": "hot",
    "new": "new",
    "top": "top",
    "rising": "rising",
    "controversial": "controversial",
}
_SUBREDDIT_TIMEFRAMES = {"hour", "day", "week", "month", "year", "all"}


@router.get("/subreddit-posts", summary="List posts in a subreddit (cursor-paginated)")
async def subreddit_posts(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    limit: int = Query(25, ge=1, le=200),
    sort: str = Query(
        "new",
        description="Feed sort: best|hot|new|top|rising (default new).",
    ),
    timeframe: str | None = Query(
        None,
        description=(
            "For sort=top (or controversial): hour|day|week|month|year|all. "
            "Default day when sort=top and timeframe is omitted."
        ),
    ),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the "
            "nextCursor value returned in the previous response (Reddit's after fullname)."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = _require_subreddit(url)
    sort_key = (sort or "new").strip().lower()
    path_sort = _SUBREDDIT_SORTS.get(sort_key)
    if not path_sort:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort. Use best, hot, new, top, or rising.",
        )
    listing_params: dict[str, Any] = {}
    resolved_timeframe: str | None = None
    if path_sort in {"top", "controversial"}:
        t_raw = (timeframe or "day").strip().lower()
        if t_raw not in _SUBREDDIT_TIMEFRAMES:
            raise HTTPException(
                status_code=400,
                detail="Invalid timeframe. Use hour, day, week, month, year, or all.",
            )
        listing_params["t"] = t_raw
        resolved_timeframe = t_raw

    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-posts",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=CREDIT_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            posts, next_cursor = await _reddit_listing_json(
                f"/r/{sub}/{path_sort}.json",
                listing_params,
                limit,
                after=cursor,
            )
            if posts:
                ctx["source"] = "direct"
                return {
                    "subreddit": sub,
                    "sort": sort_key,
                    "timeframe": resolved_timeframe,
                    "totalReturned": len(posts),
                    "nextCursor": next_cursor,
                    "hasMore": bool(next_cursor),
                    "posts": posts,
                }
            if cursor:
                raise HTTPException(
                    status_code=400,
                    detail="Cursor pagination is only available on the native Reddit feed. Start a new request without cursor.",
                )
            raise HTTPException(
                status_code=502,
                detail="Subreddit feed temporarily unavailable",
            )

        data = await cached_or_run(
            endpoint="reddit.subreddit-posts",
            params={
                "sub": sub,
                "limit": limit,
                "sort": sort_key,
                "timeframe": resolved_timeframe or "",
                "cursor": cursor or "",
                "v": 4,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _clean_reddit_image(value: Any) -> str | None:
    """Reddit image URLs in about.json are HTML-escaped and carry query junk."""
    s = safe_str(value)
    if not s:
        return None
    s = s.replace("&amp;", "&")
    return s.split("?")[0] if s.startswith("http") else s


async def _reddit_subreddit_json(sub: str, path_suffix: str) -> Any | None:
    """Fetch ``/r/{sub}{path_suffix}`` via OAuth, else Decodo ``.json``.

    ``path_suffix`` examples: ``/about``, ``/about/rules``.
    """
    oauth = await _reddit_oauth_headers()
    if oauth:
        try:
            resp = await proxy_fetch(
                f"https://oauth.reddit.com/r/{sub}{path_suffix}",
                tier="none",
                headers=oauth,
                params={"raw_json": "1"},
                timeout=10,
            )
            if resp.status_code < 400:
                return resp.json()
        except (httpx.HTTPError, ValueError):
            pass

    if decodo_fetch.enabled():
        fetched = await decodo_fetch.fetch_json(
            f"https://www.reddit.com/r/{sub}{path_suffix}.json?raw_json=1",
            timeout=25.0,
        )
        if fetched is not None and fetched[0] < 400:
            return fetched[1]
    return None


def _normalize_subreddit_rules(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    raw = payload.get("rules")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        name = safe_str(row.get("short_name") or row.get("violation_reason"))
        if not name and not row.get("description"):
            continue
        out.append(
            {
                "name": name,
                "description": safe_str(row.get("description")),
                "kind": safe_str(row.get("kind")),
                "violationReason": safe_str(row.get("violation_reason")),
                "priority": safe_int(row.get("priority")),
            }
        )
    return out


async def _subreddit_details_native(sub: str) -> dict[str, Any] | None:
    """Fetch subreddit info from public about + rules (no Apify actor).

    OAuth (oauth.reddit.com) first — Reddit 403-blocks anonymous datacenter
    hits. Decodo fallback for about/rules JSON. Returns None on about failure.
    """
    about_payload, rules_payload = await asyncio.gather(
        _reddit_subreddit_json(sub, "/about"),
        _reddit_subreddit_json(sub, "/about/rules"),
    )

    if not isinstance(about_payload, dict):
        return None
    data = about_payload.get("data") or {}
    if not (data.get("display_name") or data.get("subscribers") is not None):
        return None

    display = safe_str(data.get("display_name")) or sub
    # Reddit ``name`` is the stable t5_… fullname; bare ``id`` is base36 without prefix.
    subreddit_id = safe_str(data.get("name"))
    if not subreddit_id and data.get("id"):
        subreddit_id = f"t5_{data.get('id')}"

    return {
        "platform": "reddit",
        "id": subreddit_id,
        "name": display,
        "url": f"https://www.reddit.com/r/{display}",
        "title": safe_str(data.get("title")),
        "description": safe_str(data.get("public_description") or data.get("description")),
        "members": safe_int(data.get("subscribers")),
        # Currently online (Reddit active_user_count) — NOT weekly uniques.
        # ScrapeCreators' weekly_active_users often looks like this same field mislabeled.
        "activeUsers": safe_int(
            data.get("active_user_count")
            or data.get("accounts_active")
            or data.get("accounts_active_count")
        ),
        "category": safe_str(data.get("advertiser_category")),
        "language": safe_str(data.get("lang")),
        "type": safe_str(data.get("subreddit_type")),
        "createdAt": _epoch_to_iso(data.get("created_utc") or data.get("created")),
        "nsfw": bool(data.get("over18")),
        "submitText": safe_str(data.get("submit_text")),
        "rules": _normalize_subreddit_rules(rules_payload),
        "icon": _clean_reddit_image(data.get("community_icon") or data.get("icon_img")),
        "banner": _clean_reddit_image(data.get("banner_background_image") or data.get("banner_img")),
    }


@router.get(
    "/subreddit-details",
    summary="Subreddit info, rules, and member stats",
    description=(
        "Public subreddit card: id (t5_…), title, description, members, "
        "activeUsers (currently online), rules[], submitText, ISO createdAt, "
        "nsfw/type/language/category, icon/banner. Flat 1 credit. Subreddit "
        "names are case-insensitive (AskReddit and askreddit both resolve)."
    ),
)
async def subreddit_details(
    url: str = Query(
        ...,
        description=(
            "Subreddit URL, r/name, or bare name (case-insensitive), "
            "e.g. r/technology or AskReddit."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = _require_subreddit(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-details",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await _subreddit_details_native(sub)
            if native is not None:
                ctx["source"] = "direct"
                return native
            raise HTTPException(status_code=404, detail="Subreddit not found")

        data = await cached_or_run(
            endpoint="reddit.subreddit-details",
            params={"sub": sub, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/post-details", summary="Reddit post metadata + stats")
async def post_details(
    url: str = Query(..., description="Reddit post URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    post_id = _require_reddit_post_url(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/post-details",
        platform="reddit",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            post, _, _ = await _fetch_reddit_post_resilient(url, post_id, limit=1, ctx=ctx)
            return post

        data = await cached_or_run(
            endpoint="reddit.post-details",
            params={"url": url, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/post-comments", summary="Comments on a Reddit post")
async def post_comments(
    url: str = Query(..., description="Reddit post URL"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    post_id = _require_reddit_post_url(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/post-comments",
        platform="reddit",
        resource_url=url,
        base_credits=CREDIT_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            post, comments, has_more = await _fetch_reddit_post_resilient(
                url, post_id, limit=limit, ctx=ctx
            )
            return {
                "totalReturned": len(comments),
                "limit": limit,
                "hasMore": has_more,
                "nextCursor": None,
                "post": post,
                "comments": comments,
            }

        data = await cached_or_run(
            endpoint="reddit.post-comments",
            params={"url": url, "limit": limit, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/post-transcript", summary="Reddit post transcript / discussion text")
async def post_transcript(
    url: str = Query(..., description="Reddit post URL"),
    limit: int = Query(50, ge=0, le=200, description="Max comments to include in the transcript"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    post_id = _require_reddit_post_url(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/post-transcript",
        platform="reddit",
        resource_url=url,
        base_credits=CREDIT_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            try:
                # Native JSON first; Decodo when Reddit blocks the datacenter IP.
                post, comments, _ = await _fetch_reddit_post_resilient(
                    url, post_id, limit=max(limit, 1), ctx=ctx
                )
            except HTTPException as exc:
                if exc.status_code in {502, 503, 504}:
                    raise HTTPException(
                        status_code=422,
                        detail="No transcript text available for this Reddit post",
                    ) from exc
                raise
            # Discussion text only — no media timeline. Segment text must be an
            # exact substring of transcript (charStart:charEnd == text).
            raw_segments: list[dict[str, Any]] = []
            title = (post.get("title") or "").strip()
            body = (post.get("text") or "").strip()
            if title:
                raw_segments.append({"speaker": "post", "text": f"Title: {title}"})
            if body:
                raw_segments.append(
                    {"speaker": post.get("author") or "post", "text": body}
                )
            for c in comments:
                text = (c.get("text") or "").strip()
                if not text:
                    continue
                speaker = c.get("author") or "comment"
                raw_segments.append({"speaker": speaker, "text": f"{speaker}: {text}"})
            transcript = "\n\n".join(s["text"] for s in raw_segments).strip()
            if not transcript:
                raise HTTPException(status_code=422, detail="No transcript text available for this Reddit post")
            segments, read_secs = finalize_text_segments(transcript, raw_segments)
            return {
                "platform": "reddit",
                "url": post.get("url") or url,
                "post": post,
                "transcript": transcript,
                "timingSource": TIMING_NONE,
                "estimatedReadSeconds": read_secs,
                "transcriptSegments": segments,
                "wordCount": count_words(transcript),
                "segments": len(segments),
                "commentsIncluded": len(comments),
            }

        data = await cached_or_run(
            endpoint="reddit.post-transcript",
            params={"url": url, "limit": limit, "v": 8},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/subreddit-search", summary="Search posts within a specific subreddit (cursor-paginated)")
async def subreddit_search(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, ge=1, le=200),
    sort: str = Query(
        "relevance",
        description=(
            "Search sort: relevance|new|top|hot|comments (alias: comment_count). "
            "Default relevance."
        ),
    ),
    timeframe: str | None = Query(
        None,
        description=(
            "Time window for sort=top or sort=comments: hour|day|week|month|year|all. "
            "Default all when those sorts are used and timeframe is omitted."
        ),
    ),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the "
            "nextCursor value returned in the previous response."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = _require_subreddit(url)
    reddit_sort, resolved_t = _resolve_search_sort_timeframe(sort, timeframe)
    sort_key = (sort or "relevance").strip().lower()
    if sort_key == "comment_count":
        sort_key = "comments"
    listing: dict[str, Any] = {"q": q, "restrict_sr": "1", "sort": reddit_sort}
    if resolved_t:
        listing["t"] = resolved_t
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-search",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=CREDIT_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            results, next_cursor = await _reddit_listing_json(
                f"/r/{sub}/search.json",
                listing,
                limit,
                after=cursor,
            )
            if results:
                ctx["source"] = "direct"
                return {
                    "subreddit": sub,
                    "query": q,
                    "sort": sort_key,
                    "timeframe": resolved_t,
                    "totalReturned": len(results),
                    "nextCursor": next_cursor,
                    "hasMore": bool(next_cursor),
                    "results": results,
                }
            if cursor:
                raise HTTPException(
                    status_code=400,
                    detail="Cursor pagination is only available on the native Reddit search. Start a new request without cursor.",
                )
            raise HTTPException(
                status_code=502,
                detail="Subreddit search temporarily unavailable",
            )

        data = await cached_or_run(
            endpoint="reddit.subreddit-search",
            params={
                "sub": sub,
                "q": q,
                "limit": limit,
                "sort": sort_key,
                "timeframe": resolved_t or "",
                "cursor": cursor or "",
                "v": 4,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/search", summary="Search Reddit posts site-wide by keyword (cursor-paginated)")
async def reddit_search(
    q: str = Query(..., min_length=2, description="Keyword or phrase to search Reddit posts site-wide"),
    limit: int = Query(25, ge=1, le=200),
    sort: str = Query(
        "relevance",
        description=(
            "Search sort: relevance|new|top|hot|comments (alias: comment_count). "
            "Default relevance."
        ),
    ),
    timeframe: str | None = Query(
        None,
        description=(
            "Time window for sort=top or sort=comments: hour|day|week|month|year|all. "
            "Default all when those sorts are used and timeframe is omitted. "
            "Example: sort=new for chronology, or sort=top&timeframe=week for last week."
        ),
    ),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the "
            "nextCursor value returned in the previous response."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    reddit_sort, resolved_t = _resolve_search_sort_timeframe(sort, timeframe)
    sort_key = (sort or "relevance").strip().lower()
    if sort_key == "comment_count":
        sort_key = "comments"
    listing: dict[str, Any] = {"q": q, "sort": reddit_sort}
    if resolved_t:
        listing["t"] = resolved_t
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/search",
        platform="reddit",
        resource_url=None,
        base_credits=CREDIT_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            results, next_cursor = await _reddit_listing_json(
                "/search.json", listing, limit, after=cursor
            )
            if results:
                ctx["source"] = "direct"
                return {
                    "query": q,
                    "sort": sort_key,
                    "timeframe": resolved_t,
                    "totalReturned": len(results),
                    "nextCursor": next_cursor,
                    "hasMore": bool(next_cursor),
                    "results": results,
                }
            if cursor:
                raise HTTPException(
                    status_code=400,
                    detail="Cursor pagination is only available on the native Reddit search. Start a new request without cursor.",
                )
            raise HTTPException(
                status_code=502,
                detail="Reddit search temporarily unavailable",
            )

        data = await cached_or_run(
            endpoint="reddit.search",
            params={
                "q": q,
                "limit": limit,
                "sort": sort_key,
                "timeframe": resolved_t or "",
                "cursor": cursor or "",
                "v": 5,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
