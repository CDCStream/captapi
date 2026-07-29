"""Reddit endpoints (subreddit posts, post details, comments, search).

Native-first via Reddit public JSON / OAuth; Decodo for blocked post fetches.
"""

from __future__ import annotations

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
from app.utils.formatters import first_present, safe_int, safe_str
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


def _normalize_post(item: dict[str, Any]) -> dict[str, Any]:
    thumbnail = safe_str(item.get("thumbnailUrl") or item.get("thumbnail"))
    if thumbnail in _THUMB_PLACEHOLDERS:
        thumbnail = None
    return {
        "platform": "reddit",
        "id": safe_str(item.get("id") or item.get("parsedId")),
        "url": safe_str(item.get("canonical_url") or item.get("url")),
        "title": safe_str(item.get("title")),
        "text": safe_str(item.get("body") or item.get("text")),
        "subreddit": safe_str(item.get("communityName") or item.get("subreddit") or item.get("parsedCommunityName")),
        "author": safe_str(item.get("username") or item.get("author")),
        "upvotes": safe_int(first_present(item.get("upVotes"), item.get("score"), item.get("ups"))),
        "comments": safe_int(
            first_present(item.get("numberOfComments"), item.get("numComments"), item.get("num_comments"))
        ),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created") or item.get("created_utc")),
        "flair": safe_str(item.get("flair")),
        "nsfw": first_present(item.get("over18"), item.get("nsfw"), item.get("over_18")),
        "thumbnail": thumbnail,
    }


def _normalize_comment(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": safe_str(item.get("id")),
        "author": safe_str(item.get("username") or item.get("author")),
        "text": safe_str(item.get("body") or item.get("text")),
        "upvotes": safe_int(first_present(item.get("upVotes"), item.get("score"), item.get("ups"))),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created") or item.get("created_utc")),
        "url": safe_str(item.get("url") or item.get("permalink")),
        "parentId": safe_str(item.get("parentId") or item.get("parent_id")),
        "depth": safe_int(item.get("depth")),
        "isSubmitter": first_present(item.get("isSubmitter"), item.get("is_submitter")),
        # Reddit may send edited as False or a timestamp; coerce to bool, keep False.
        "edited": bool(item.get("edited")) if item.get("edited") is not None else None,
        "stickied": bool(item.get("stickied")) if item.get("stickied") is not None else None,
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


async def _fetch_reddit_json_url(url: str, limit: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
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


def _parse_reddit_post_payload(data: Any, limit: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Normalize a ``/comments/<id>.json`` payload (shared by the direct and
    Decodo fetch paths)."""
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
        "score": raw_post.get("score") or raw_post.get("ups"),
        "numComments": raw_post.get("num_comments"),
        "created": created,
        "flair": raw_post.get("link_flair_text"),
        "nsfw": raw_post.get("over_18"),
        "thumbnail": raw_post.get("thumbnail"),
    }

    comments: list[dict[str, Any]] = []

    def walk(children: list[dict[str, Any]]) -> None:
        for child in children:
            if child.get("kind") != "t1":
                continue
            raw = child.get("data") or {}
            comments.append({
                "id": raw.get("id"),
                "author": raw.get("author"),
                "body": raw.get("body"),
                "score": raw.get("score") or raw.get("ups"),
                "created": raw.get("created_utc"),
                "url": f"https://www.reddit.com{raw.get('permalink')}" if raw.get("permalink") else None,
                "parent_id": raw.get("parent_id"),
                "depth": raw.get("depth"),
                "is_submitter": raw.get("is_submitter"),
                "edited": raw.get("edited"),
                "stickied": raw.get("stickied"),
            })
            replies = raw.get("replies")
            reply_children = ((replies or {}).get("data") or {}).get("children") if isinstance(replies, dict) else []
            if isinstance(reply_children, list) and len(comments) < limit:
                walk(reply_children)

    comment_listing = data[1] if len(data) > 1 else {}
    walk(((comment_listing.get("data") or {}).get("children") or []))
    return _normalize_post(post), [_normalize_comment(c) for c in comments[:limit]]


async def _fetch_reddit_json_post(url: str, post_id: str, limit: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
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


def _epoch_to_iso(value: Any) -> Any:
    if isinstance(value, (int, float)) and value > 0:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).isoformat()
    return value


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


async def _fetch_reddit_post_decodo(post_id: str, limit: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
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
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
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
            created = raw.get("created_utc")
            if isinstance(created, (int, float)):
                created = datetime.fromtimestamp(int(created), tz=timezone.utc).isoformat()
            thumb = raw.get("thumbnail")
            if thumb in {"self", "default", "nsfw", "spoiler", "image"}:
                thumb = None
            posts.append(
                _normalize_post(
                    {
                        "id": raw.get("id"),
                        "url": f"https://www.reddit.com{raw.get('permalink')}" if raw.get("permalink") else raw.get("url"),
                        "title": raw.get("title"),
                        "body": raw.get("selftext"),
                        "subreddit": raw.get("subreddit"),
                        "author": raw.get("author"),
                        "score": raw.get("score") or raw.get("ups"),
                        "numComments": raw.get("num_comments"),
                        "created": created,
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


@router.get("/subreddit-posts", summary="List recent posts in a subreddit (cursor-paginated)")
async def subreddit_posts(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    limit: int = Query(25, ge=1, le=200),
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-posts",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=CREDIT_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            posts, next_cursor = await _reddit_listing_json(
                f"/r/{sub}/new.json", {}, limit, after=cursor
            )
            if posts:
                ctx["source"] = "direct"
                return {
                    "subreddit": sub,
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
            params={"sub": sub, "limit": limit, "cursor": cursor or "", "v": 3},
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


async def _subreddit_details_native(sub: str) -> dict[str, Any] | None:
    """Fetch subreddit info from public ``about.json`` (no Apify actor).

    Only the OAuth path (oauth.reddit.com, works from datacenter IPs) is
    tried: Reddit 403-blocks anonymous requests from datacenter AND
    residential proxies alike (fingerprint-based, measured 0/16 success), so
    proxied retries are pure wasted latency. Returns None on failure so the
    caller falls back to the actor.
    """
    payload: Any = None
    oauth = await _reddit_oauth_headers()
    if oauth:
        try:
            resp = await proxy_fetch(
                f"https://oauth.reddit.com/r/{sub}/about",
                tier="none", headers=oauth,
                params={"raw_json": "1"}, timeout=10,
            )
            if resp.status_code < 400:
                payload = resp.json()
        except (httpx.HTTPError, ValueError):
            payload = None

    if payload is None and decodo_fetch.enabled():
        fetched = await decodo_fetch.fetch_json(
            f"https://www.reddit.com/r/{sub}/about.json?raw_json=1", timeout=25.0,
        )
        if fetched is not None and fetched[0] < 400:
            payload = fetched[1]

    if not isinstance(payload, dict):
        return None
    data = payload.get("data") or {}
    if not (data.get("display_name") or data.get("subscribers") is not None):
        return None

    return {
        "platform": "reddit",
        "name": safe_str(data.get("display_name")),
        "url": f"https://www.reddit.com/r/{data.get('display_name')}",
        "title": safe_str(data.get("title")),
        "description": safe_str(data.get("public_description") or data.get("description")),
        "members": safe_int(data.get("subscribers")),
        "category": safe_str(data.get("advertiser_category")),
        "language": safe_str(data.get("lang")),
        "type": safe_str(data.get("subreddit_type")),
        "createdAt": safe_str(data.get("created_utc")),
        "nsfw": bool(data.get("over18")),
        "icon": _clean_reddit_image(data.get("community_icon") or data.get("icon_img")),
        "banner": _clean_reddit_image(data.get("banner_background_image") or data.get("banner_img")),
    }


@router.get("/subreddit-details", summary="Subreddit info & member stats")
async def subreddit_details(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
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
            # Native-only: public about.json (~1s).
            native = await _subreddit_details_native(sub)
            if native is not None:
                ctx["source"] = "direct"
                return native
            raise HTTPException(status_code=404, detail="Subreddit not found")

        data = await cached_or_run(
            endpoint="reddit.subreddit-details",
            params={"sub": sub, "v": 3},
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
            post, _ = await _fetch_reddit_post_resilient(url, post_id, limit=1, ctx=ctx)
            return post

        data = await cached_or_run(
            endpoint="reddit.post-details",
            params={"url": url, "v": 4},
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
            _, comments = await _fetch_reddit_post_resilient(url, post_id, limit=limit, ctx=ctx)
            return {"totalReturned": len(comments), "comments": comments}

        data = await cached_or_run(
            endpoint="reddit.post-comments",
            params={"url": url, "limit": limit, "v": 5},
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
                post, comments = await _fetch_reddit_post_resilient(url, post_id, limit=max(limit, 1), ctx=ctx)
            except HTTPException as exc:
                if exc.status_code in {502, 503, 504}:
                    raise HTTPException(
                        status_code=422,
                        detail="No transcript text available for this Reddit post",
                    ) from exc
                raise
            segments: list[dict[str, Any]] = []
            parts: list[str] = []
            title = (post.get("title") or "").strip()
            body = (post.get("text") or "").strip()
            if title:
                parts.append(f"Title: {title}")
                segments.append({"speaker": "post", "text": title, "start": 0, "duration": 0, "timestamp": "00:00"})
            if body:
                parts.append(body)
                segments.append({"speaker": post.get("author") or "post", "text": body, "start": 0, "duration": 0, "timestamp": "00:00"})
            for c in comments:
                text = (c.get("text") or "").strip()
                if not text:
                    continue
                speaker = c.get("author") or "comment"
                line = f"{speaker}: {text}"
                parts.append(line)
                segments.append({"speaker": speaker, "text": text, "start": 0, "duration": 0, "timestamp": "00:00"})
            transcript = "\n\n".join(parts).strip()
            if not transcript:
                raise HTTPException(status_code=422, detail="No transcript text available for this Reddit post")
            return {
                "platform": "reddit",
                "url": post.get("url") or url,
                "post": post,
                "transcript": transcript,
                "transcriptSegments": segments,
                "wordCount": len(transcript.split()),
                "segments": len(segments),
                "commentsIncluded": len(comments),
            }

        data = await cached_or_run(
            endpoint="reddit.post-transcript",
            params={"url": url, "limit": limit, "v": 5},
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
                {"q": q, "restrict_sr": "1", "sort": "relevance"},
                limit,
                after=cursor,
            )
            if results:
                ctx["source"] = "direct"
                return {
                    "subreddit": sub,
                    "query": q,
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
            params={"sub": sub, "q": q, "limit": limit, "cursor": cursor or "", "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/search", summary="Search Reddit posts site-wide by keyword (cursor-paginated)")
async def reddit_search(
    q: str = Query(..., min_length=2, description="Keyword or phrase to search Reddit posts site-wide"),
    limit: int = Query(25, ge=1, le=200),
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/search",
        platform="reddit",
        resource_url=None,
        base_credits=CREDIT_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            results, next_cursor = await _reddit_listing_json(
                "/search.json", {"q": q, "sort": "relevance"}, limit, after=cursor
            )
            if results:
                ctx["source"] = "direct"
                return {
                    "query": q,
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
            params={"q": q, "limit": limit, "cursor": cursor or "", "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
