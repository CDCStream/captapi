"""Cross-platform analytics: one unified metrics shape for any post.

This is the read-side "data layer" companion to social publishing tools. Give
any public YouTube / TikTok / Instagram / Facebook post, video, or reel URL and
get back the *same* normalized metrics object regardless of platform, so an
analytics dashboard or AI agent never has to special-case each network.
"""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.routers.bluesky import _normalize_post as _bs_normalize
from app.routers.bluesky import _xrpc as _bs_xrpc
from app.routers.facebook import _normalize_post as _fb_normalize
from app.routers.instagram import _normalize_post as _ig_normalize
from app.routers.linkedin import _normalize_post as _li_normalize
from app.routers.pinterest import _normalize_pin as _pin_normalize
from app.routers.reddit import _is_comment as _rd_is_comment
from app.routers.reddit import _normalize_post as _rd_normalize
from app.routers.rumble import _normalize_video as _rb_normalize
from app.routers.threads import _normalize_post as _th_normalize
from app.routers.tiktok import _normalize as _tiktok_normalize
from app.routers.twitter import _normalize_tweet as _tw_normalize
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import (
    extract_bluesky_post,
    extract_youtube_id,
    normalize_youtube_url,
)

router = APIRouter()

CREDIT_POST_ANALYTICS = 1
MAX_COMPARE = 10


def _detect_platform(url: str) -> str | None:
    """Best-effort platform detection from a post/video/reel URL."""
    u = (url or "").lower()
    if extract_youtube_id(url) or "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    if "tiktok.com" in u:
        return "tiktok"
    if "instagram.com" in u:
        return "instagram"
    if "facebook.com" in u or "fb.watch" in u:
        return "facebook"
    if "twitter.com" in u or "x.com" in u:
        return "twitter"
    if "reddit.com" in u:
        return "reddit"
    if "threads.net" in u or "threads.com" in u:
        return "threads"
    if "bsky.app" in u:
        return "bluesky"
    if "pinterest." in u or "pin.it" in u:
        return "pinterest"
    if "linkedin.com" in u:
        return "linkedin"
    if "rumble.com" in u:
        return "rumble"
    return None


async def _fetch_youtube(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    norm = normalize_youtube_url(url)
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_YOUTUBE_VIDEO,
        {"startUrls": [{"url": norm}], "maxResults": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Video not found")
    v = items[0]
    thumbs = v.get("thumbnails")
    thumb = safe_str(
        v.get("thumbnailUrl")
        or (thumbs[-1].get("url") if isinstance(thumbs, list) and thumbs else None)
    )
    return {
        "platform": "youtube",
        "url": norm,
        "id": safe_str(extract_youtube_id(url)),
        "caption": safe_str(v.get("title")),
        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
        "thumbnailUrl": thumb,
        "author": {
            "username": safe_str(v.get("channelName") or v.get("channel")),
            "displayName": safe_str(v.get("channelName") or v.get("channel")),
            "url": safe_str(v.get("channelUrl")),
            "verified": None,
        },
        "engagement": {
            "views": safe_int(v.get("viewCount") or v.get("views")),
            "likes": safe_int(v.get("likes") or v.get("likeCount")),
            "comments": safe_int(v.get("commentsCount") or v.get("commentCount")),
        },
    }


async def _fetch_tiktok(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_TIKTOK,
        {"postURLs": [url], "resultsPerPage": 1, "shouldDownloadVideos": False},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Video not found")
    return _tiktok_normalize(items[0])


async def _fetch_instagram(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_INSTAGRAM_POST,
        {"directUrls": [url], "resultsLimit": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Post not found")
    return _ig_normalize(items[0])


async def _fetch_facebook(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_FACEBOOK_POSTS,
        {"startUrls": [{"url": url}], "resultsLimit": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Post not found")
    return _fb_normalize(items[0])


async def _fetch_twitter(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_TWITTER_TWEET,
        {"startUrls": [url], "maxItems": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Tweet not found")
    n = _tw_normalize(items[0])
    eng = n.get("engagement") or {}
    # Map Twitter-native engagement onto the shared metric names.
    retweets = eng.get("retweets") if isinstance(eng.get("retweets"), int) else 0
    quotes = eng.get("quotes") if isinstance(eng.get("quotes"), int) else 0
    return {
        "platform": "twitter",
        "url": n.get("url"),
        "id": n.get("id"),
        "title": n.get("text"),
        "publishedAt": n.get("publishedAt"),
        "thumbnailUrl": None,
        "author": n.get("author") or {},
        "engagement": {
            "views": eng.get("views"),
            "likes": eng.get("likes"),
            "comments": eng.get("replies"),
            "shares": retweets + quotes,
            "saves": eng.get("bookmarks"),
        },
    }


async def _fetch_reddit(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_REDDIT,
        {"startUrls": [{"url": url}], "type": "posts", "maxItems": 1},
        max_items=2,
    )
    posts = [i for i in items if not _rd_is_comment(i)]
    if not posts:
        raise HTTPException(status_code=404, detail="Post not found")
    n = _rd_normalize(posts[0])
    return {
        "platform": "reddit",
        "url": n.get("url"),
        "id": n.get("id"),
        "title": n.get("title"),
        "publishedAt": n.get("publishedAt"),
        "thumbnailUrl": n.get("thumbnail"),
        "author": {"username": n.get("author")},
        "engagement": {
            "views": None,
            "likes": n.get("upvotes"),
            "comments": n.get("comments"),
            "shares": None,
            "saves": None,
        },
    }


async def _fetch_threads(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_THREADS,
        {"urls": [url], "resultsType": "details", "resultsLimit": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Post not found")
    n = _th_normalize(items[0])
    eng = n.get("engagement") or {}
    return {
        "platform": "threads",
        "url": n.get("url"),
        "id": n.get("id"),
        "title": n.get("text"),
        "publishedAt": n.get("publishedAt"),
        "thumbnailUrl": None,
        "author": n.get("author") or {},
        "engagement": {
            "views": None,
            "likes": eng.get("likes"),
            "comments": eng.get("replies"),
            "shares": eng.get("reposts"),
            "saves": None,
        },
    }


async def _fetch_bluesky(url: str) -> dict[str, Any]:
    parsed = extract_bluesky_post(url)
    if not parsed:
        raise HTTPException(status_code=400, detail="Provide a Bluesky post URL")
    handle, rkey = parsed
    did = handle
    if not did.startswith("did:"):
        profile = await _bs_xrpc("app.bsky.actor.getProfile", {"actor": handle})
        did = profile.get("did") or handle
    data = await _bs_xrpc(
        "app.bsky.feed.getPosts",
        {"uris": f"at://{did}/app.bsky.feed.post/{rkey}"},
    )
    posts = data.get("posts") or []
    if not posts:
        raise HTTPException(status_code=404, detail="Post not found")
    n = _bs_normalize(posts[0])
    eng = n.get("engagement") or {}
    return {
        "platform": "bluesky",
        "url": url,
        "id": n.get("cid"),
        "title": n.get("text"),
        "publishedAt": n.get("publishedAt"),
        "thumbnailUrl": None,
        "author": n.get("author") or {},
        "engagement": {
            "views": None,
            "likes": eng.get("likes"),
            "comments": eng.get("replies"),
            "shares": eng.get("reposts"),
            "saves": None,
        },
    }


async def _fetch_linkedin(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_LINKEDIN_POST,
        {"url": url},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Post not found")
    n = _li_normalize(items[0])
    eng = n.get("engagement") or {}
    return {
        "platform": "linkedin",
        "url": n.get("url"),
        "id": None,
        "title": n.get("text"),
        "publishedAt": n.get("publishedAt"),
        "thumbnailUrl": None,
        "author": n.get("author") or {},
        "engagement": {
            "views": None,
            "likes": eng.get("likes"),
            "comments": eng.get("comments"),
            "shares": eng.get("reposts"),
            "saves": None,
        },
    }


async def _fetch_pinterest(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_PINTEREST,
        {"startUrls": [{"url": url}], "maxItems": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Pin not found")
    n = _pin_normalize(items[0])
    return {
        "platform": "pinterest",
        "url": n.get("url"),
        "id": n.get("id"),
        "title": n.get("title"),
        "publishedAt": n.get("publishedAt"),
        "thumbnailUrl": n.get("image"),
        "author": n.get("author") or {},
        "engagement": {
            "views": None,
            "likes": None,
            "comments": n.get("comments"),
            "shares": None,
            "saves": n.get("saves"),
        },
    }


async def _fetch_rumble(url: str) -> dict[str, Any]:
    settings = get_settings()
    apify = get_apify()
    items = await apify.run_actor_sync(
        settings.APIFY_ACTOR_RUMBLE,
        {"startUrls": [{"url": url}], "maxItems": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Video not found")
    n = _rb_normalize(items[0])
    return {
        "platform": "rumble",
        "url": n.get("url"),
        "id": n.get("id"),
        "title": n.get("title"),
        "publishedAt": n.get("publishedAt"),
        "thumbnailUrl": n.get("thumbnail"),
        "author": {"displayName": n.get("channel"), "url": n.get("channelUrl")},
        "engagement": {
            "views": n.get("views"),
            "likes": n.get("likes"),
            "comments": None,
            "shares": None,
            "saves": None,
        },
    }


_FETCHERS: dict[str, Callable[[str], Awaitable[dict[str, Any]]]] = {
    "youtube": _fetch_youtube,
    "tiktok": _fetch_tiktok,
    "instagram": _fetch_instagram,
    "facebook": _fetch_facebook,
    "twitter": _fetch_twitter,
    "reddit": _fetch_reddit,
    "threads": _fetch_threads,
    "bluesky": _fetch_bluesky,
    "pinterest": _fetch_pinterest,
    "linkedin": _fetch_linkedin,
    "rumble": _fetch_rumble,
}


def _unify(n: dict[str, Any]) -> dict[str, Any]:
    """Collapse a per-platform normalized post into one consistent metrics shape."""
    eng = n.get("engagement") or {}
    views = eng.get("views")
    likes = eng.get("likes")
    comments = eng.get("comments")
    shares = eng.get("shares")
    saves = eng.get("saves")
    interactions = sum(
        x for x in (likes, comments, shares, saves) if isinstance(x, int)
    )
    engagement_rate = (
        round(interactions / views, 4)
        if isinstance(views, int) and views > 0
        else None
    )
    return {
        "platform": n.get("platform"),
        "url": n.get("url"),
        "id": n.get("id"),
        "title": n.get("title") or n.get("caption"),
        "publishedAt": n.get("publishedAt"),
        "durationSeconds": n.get("durationSeconds"),
        "thumbnailUrl": n.get("thumbnailUrl"),
        "author": n.get("author") or {},
        "metrics": {
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "interactions": interactions,
            "engagementRate": engagement_rate,
        },
    }


@router.get(
    "/post",
    summary="Cross-platform post analytics (unified metrics)",
    description=(
        "Detects the platform from the URL (YouTube, TikTok, Instagram, "
        "Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, "
        f"Rumble) and returns one normalized metrics object. Costs "
        f"{CREDIT_POST_ANALYTICS} credit."
    ),
)
async def post_analytics(
    url: str = Query(..., description="A public post, video, or reel URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    platform = _detect_platform(url)
    if not platform:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unrecognized URL. Provide a public post/video/reel URL from "
                "YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, "
                "Threads, Bluesky, Pinterest, LinkedIn, or Rumble."
            ),
        )

    async with billed_call(
        caller=caller,
        endpoint="/v1/analytics/post",
        platform=platform,
        resource_url=url,
        base_credits=CREDIT_POST_ANALYTICS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            n = await _FETCHERS[platform](url)
            return _unify(n)

        data = await cached_or_run(
            endpoint=f"analytics.post.{platform}",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            ttl=get_settings().CACHE_TTL_DYNAMIC,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/compare",
    summary="Compare metrics across multiple posts and platforms",
    description=(
        "Fetches unified metrics for up to 10 comma-separated URLs in one call "
        "(any mix of platforms). Bills 1 credit per successfully resolved URL."
    ),
)
async def compare_analytics(
    urls: str = Query(
        ...,
        description="Comma-separated post URLs (up to 10), any mix of platforms",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    url_list = [u.strip() for u in urls.split(",") if u.strip()][:MAX_COMPARE]
    if not url_list:
        raise HTTPException(status_code=400, detail="Provide at least one URL")

    base = len(url_list) * CREDIT_POST_ANALYTICS

    async with billed_call(
        caller=caller,
        endpoint="/v1/analytics/compare",
        platform="multi",
        resource_url=None,
        base_credits=base,
    ) as ctx:
        async def _one(u: str) -> dict[str, Any]:
            p = _detect_platform(u)
            if not p:
                return {"url": u, "error": "unsupported_url"}
            try:
                n = await _FETCHERS[p](u)
                return _unify(n)
            except HTTPException as e:
                return {"url": u, "platform": p, "error": str(e.detail)}
            except Exception:
                return {"url": u, "platform": p, "error": "fetch_failed"}

        results = list(await asyncio.gather(*[_one(u) for u in url_list]))
        resolved = [r for r in results if not r.get("error")]
        # Bill only for URLs we actually resolved (floor of 1 so a fully failed
        # batch still records a minimal charge for the work attempted).
        ctx["credits_override"] = max(1, len(resolved) * CREDIT_POST_ANALYTICS)
        return ApiResponse(
            data={
                "count": len(results),
                "resolved": len(resolved),
                "results": results,
            }
        )
