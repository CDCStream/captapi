"""Reddit endpoints (subreddit posts, post details, comments, search).

Backed by the trudax "Reddit Scraper Lite" actor (config-driven slug). The
actor returns mixed post/comment items; we split them by ``dataType``.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
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
RATE = 0.4


def _scaled(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


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
        "edited": bool(item.get("edited")) or None,
        "stickied": bool(item.get("stickied")) or None,
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


async def _fetch_reddit_json_url(url: str, limit: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    headers = {"User-Agent": "CaptapiBot/1.0 (+https://captapi.com)"}
    params = {"raw_json": "1", "limit": max(limit, 1)}
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers=headers) as client:
            resp = await client.get(url, params=params)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Reddit upstream error") from exc
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Post not found")
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail="Reddit upstream error")

    data = resp.json()
    if not isinstance(data, list) or not data:
        raise HTTPException(status_code=404, detail="Post not found")
    post_children = (data[0].get("data") or {}).get("children") or []
    if not post_children:
        raise HTTPException(status_code=404, detail="Post not found")
    raw_post = post_children[0].get("data") or {}
    post = {
        "id": raw_post.get("id"),
        "url": f"https://www.reddit.com{raw_post.get('permalink')}" if raw_post.get("permalink") else raw_post.get("url"),
        "title": raw_post.get("title"),
        "body": raw_post.get("selftext"),
        "subreddit": raw_post.get("subreddit"),
        "author": raw_post.get("author"),
        "score": raw_post.get("score") or raw_post.get("ups"),
        "numComments": raw_post.get("num_comments"),
        "created": raw_post.get("created_utc"),
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
    for candidate in _reddit_json_url_variants(url, post_id):
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


async def _fetch_reddit_actor_post(url: str, limit: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_REDDIT,
        {
            "startUrls": [{"url": url}],
            "type": "posts",
            "maxItems": max(limit, 1),
        },
        max_items=max(limit, 1),
    )
    post_items = [i for i in items if not _is_comment(i)]
    comment_items = [i for i in items if _is_comment(i)]
    if not post_items and not comment_items:
        raise HTTPException(status_code=404, detail="Post not found")
    post = _normalize_post(post_items[0] if post_items else items[0])
    comments = [_normalize_comment(c) for c in comment_items[:limit]]
    return post, comments


async def _fetch_reddit_post_resilient(url: str, post_id: str, limit: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        return await _fetch_reddit_json_post(url, post_id, limit)
    except HTTPException as exc:
        if exc.status_code not in {502, 503, 504}:
            raise
    return await _fetch_reddit_actor_post(url, limit)


async def _reddit_listing_json(path: str, params: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    """Fetch a Reddit public JSON listing (search or subreddit feed) natively.

    Returns [] on any upstream problem so callers can fall back to the actor.
    Unlike the trudax lite actor, the public JSON includes scores and comment
    counts, so posts come back with full engagement data.
    """
    headers = {"User-Agent": "CaptapiBot/1.0 (+https://captapi.com)"}
    query = {"raw_json": "1", "limit": max(limit, 1), **params}
    for base in ("https://www.reddit.com", "https://old.reddit.com"):
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(f"{base}{path}", params=query)
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        try:
            payload = resp.json()
        except ValueError:
            continue
        children = ((payload.get("data") or {}).get("children") or []) if isinstance(payload, dict) else []
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
            return posts[:limit]
    return []


async def _reddit_search_actor(query: str, limit: int) -> list[dict[str, Any]]:
    """Score-rich actor fallback for listing endpoints (see config)."""
    settings = get_settings()
    try:
        items = await get_apify().run_actor_sync(
            settings.APIFY_ACTOR_REDDIT_SEARCH,
            {"queries": [query], "maxItems": limit},
            max_items=limit,
        )
    except Exception:  # noqa: BLE001 — fall through to the trudax actor
        return []
    return [_normalize_post(i) for i in items if _is_post(i)][:limit]


@router.get("/subreddit-posts", summary="List recent posts in a subreddit")
async def subreddit_posts(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = _require_subreddit(url)
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-posts",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            posts = await _reddit_listing_json(f"/r/{sub}/new.json", {}, limit)
            if not posts:
                posts = await _reddit_search_actor(f"r/{sub}", limit)
            if not posts:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_REDDIT,
                    {
                        "startUrls": [{"url": f"https://www.reddit.com/r/{sub}/"}],
                        "type": "posts",
                        "sort": "new",
                        "maxItems": limit,
                    },
                    max_items=limit,
                )
                posts = [_normalize_post(i) for i in items if _is_post(i)][:limit]
            return {"subreddit": sub, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="reddit.subreddit-posts",
            params={"sub": sub, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]), RATE, 2)
        return ApiResponse(data=data)


def _normalize_community(item: dict[str, Any]) -> dict[str, Any]:
    """Map a community-profile actor record to our response shape."""
    name = item.get("name") or item.get("display_name")
    return {
        "platform": "reddit",
        "name": safe_str(name),
        "url": (f"https://www.reddit.com/r/{name}" if name else None),
        "title": safe_str(item.get("title")),
        "description": safe_str(
            item.get("about")
            or item.get("public_description")
            or item.get("description")
        ),
        "members": safe_int(item.get("subscribers")),
        "activeUsers": safe_int(item.get("accounts_active") or item.get("active_user_count")),
        "category": safe_str(item.get("category") or item.get("advertiser_category")),
        "language": safe_str(item.get("language")),
        "type": safe_str(item.get("type") or item.get("subreddit_type")),
        "createdAt": safe_str(item.get("created") or item.get("created_utc")),
        "nsfw": bool(item.get("over_18") or item.get("over18")),
        "icon": safe_str(item.get("icon") or item.get("community_icon")),
        "banner": safe_str(item.get("banner") or item.get("banner_background_image")),
    }


@router.get("/subreddit-details", summary="Subreddit info & member stats")
async def subreddit_details(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = _require_subreddit(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-details",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_REDDIT_COMMUNITY,
                    {"community": sub},
                    max_items=1,
                )
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=502, detail="Subreddit lookup failed upstream") from exc
            if not items or not (items[0].get("name") or items[0].get("subscribers")):
                raise HTTPException(status_code=404, detail="Subreddit not found")
            return _normalize_community(items[0])

        data = await cached_or_run(
            endpoint="reddit.subreddit-details",
            params={"sub": sub},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/post-details", summary="Reddit post metadata + stats")
async def post_details(
    url: str = Query(..., description="Reddit post URL"),
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
            post, _ = await _fetch_reddit_post_resilient(url, post_id, limit=1)
            return post

        data = await cached_or_run(
            endpoint="reddit.post-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/post-comments", summary="Comments on a Reddit post")
async def post_comments(
    url: str = Query(..., description="Reddit post URL"),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    post_id = _require_reddit_post_url(url)
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/post-comments",
        platform="reddit",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            _, comments = await _fetch_reddit_post_resilient(url, post_id, limit=limit)
            return {"totalReturned": len(comments), "comments": comments}

        data = await cached_or_run(
            endpoint="reddit.post-comments",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["comments"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/post-transcript", summary="Reddit post transcript / discussion text")
async def post_transcript(
    url: str = Query(..., description="Reddit post URL"),
    limit: int = Query(50, ge=0, le=200, description="Max comments to include in the transcript"),
    caller: ApiCaller = Depends(require_api_key),
):
    post_id = _require_reddit_post_url(url)
    cost = _scaled(max(limit, 1), RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/post-transcript",
        platform="reddit",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            try:
                # Resilient variant: falls back to the actor when Reddit's
                # public JSON blocks the datacenter IP (as other reddit
                # endpoints already do).
                post, comments = await _fetch_reddit_post_resilient(url, post_id, limit=max(limit, 1))
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
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(max(data.get("commentsIncluded", 0), 1), RATE, 2)
        return ApiResponse(data=data)


@router.get("/subreddit-search", summary="Search posts within a specific subreddit")
async def subreddit_search(
    url: str = Query(..., description="Subreddit URL, r/name, or bare name"),
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    sub = _require_subreddit(url)
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/subreddit-search",
        platform="reddit",
        resource_url=f"https://www.reddit.com/r/{sub}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            results = await _reddit_listing_json(
                f"/r/{sub}/search.json", {"q": q, "restrict_sr": "1", "sort": "relevance"}, limit
            )
            if not results:
                results = await _reddit_search_actor(f"r/{sub} {q}", limit)
            if not results:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_REDDIT,
                    {
                        "searches": [q],
                        "searchCommunityName": sub,
                        "type": "posts",
                        "sort": "relevance",
                        "maxItems": limit,
                    },
                    max_items=limit,
                )
                results = [_normalize_post(i) for i in items if _is_post(i)][:limit]
            return {"subreddit": sub, "query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="reddit.subreddit-search",
            params={"sub": sub, "q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search", summary="Search Reddit posts by keyword")
async def reddit_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/reddit/search",
        platform="reddit",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            results = await _reddit_listing_json("/search.json", {"q": q, "sort": "relevance"}, limit)
            if not results:
                results = await _reddit_search_actor(q, limit)
            if not results:
                apify = get_apify()
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_REDDIT,
                    {"searches": [q], "type": "posts", "sort": "relevance", "maxItems": limit},
                    max_items=limit,
                )
                results = [_normalize_post(i) for i in items if _is_post(i)][:limit]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="reddit.search",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
