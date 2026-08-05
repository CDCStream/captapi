"""Cross-platform analytics: one unified metrics shape for any post.

This is the read-side "data layer" companion to social publishing tools. Give
any public YouTube / TikTok / Instagram / Facebook post, video, or reel URL and
get back the *same* normalized metrics object regardless of platform, so an
analytics dashboard or AI agent never has to special-case each network.
"""

from __future__ import annotations

import asyncio
from contextvars import ContextVar
from datetime import datetime, timezone
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
from app.routers.reddit import _fetch_reddit_post_resilient as _rd_fetch_resilient
from app.routers.reddit import _is_comment as _rd_is_comment
from app.routers.reddit import _normalize_post as _rd_normalize
from app.routers.reddit import _require_reddit_post_url as _rd_require_post
from app.routers.rumble import _normalize_video as _rb_normalize
from app.routers.threads import _normalize_post as _th_normalize
from app.routers.tiktok import _normalize as _tiktok_normalize
from app.routers.twitter import _normalize_tweet as _tw_normalize
from app.routers.youtube import _video_details_native as _yt_video_details_native
from app.schemas.common import ApiResponse
from app.services import facebook_details_native
from app.services import instagram_native
from app.services import linkedin_native
from app.services import pinterest_native
from app.services import rumble_video_native
from app.services import threads_native
from app.services import tiktok_native
from app.services import twitter_native
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import (
    extract_bluesky_post,
    extract_instagram_shortcode,
    extract_pinterest_pin_id,
    extract_tweet_id,
    extract_youtube_id,
    normalize_youtube_url,
)

# Stamped by per-platform fetchers so billed_call can set X-Captapi-Source.
_analytics_source: ContextVar[str | None] = ContextVar("analytics_source", default=None)

router = APIRouter()

CREDIT_POST_ANALYTICS = 1
MAX_COMPARE = 10
# Post-level engagementRate is always interactions / views (ratio). Creator
# charts (e.g. TikTok popular-creators) use a different basis — never compare
# those numbers to this field without reading engagementRateBasis.
ENGAGEMENT_RATE_BASIS = "interactions/views"
# Bump when unified metrics shape or YouTube enrich policy changes.
ANALYTICS_CACHE_VERSION = 9


def _mark_source(source: str) -> None:
    _analytics_source.set(source)


def _published_at_utc_z(value: Any) -> str | None:
    """Normalize timestamps to UTC ``YYYY-MM-DDTHH:MM:SS.mmmZ`` when parseable."""
    s = safe_str(value)
    if not s:
        return None
    raw = s.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return s
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    ms = dt.microsecond // 1000
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{ms:03d}Z"


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


def _youtube_handle(v: dict[str, Any]) -> str | None:
    """YouTube @handle only — never echo the channel display name into username."""
    handle = safe_str(v.get("channelHandle") or v.get("channelUsername") or v.get("handle"))
    if not handle:
        return None
    return handle.lstrip("@")


def _youtube_analytics_row(v: dict[str, Any], *, norm: str, video_id: str | None) -> dict[str, Any]:
    thumbs = v.get("thumbnails")
    thumb = safe_str(
        v.get("thumbnailUrl")
        or (thumbs[-1].get("url") if isinstance(thumbs, list) and thumbs else None)
    )
    display = safe_str(v.get("channelName") or v.get("channel") or v.get("author"))
    username = _youtube_handle(v)
    verified = v.get("channelVerified")
    if not isinstance(verified, bool):
        verified = v.get("verified") if isinstance(v.get("verified"), bool) else None
    comments = safe_int(
        v.get("commentsCount") or v.get("commentCount") or v.get("comment_count")
    )
    # YouTube often exposes comments as compact UI text ("2.4M"). When the
    # upstream flag is missing, treat present comment counts as approximate
    # (same default as youtube/video-details).
    if comments is None:
        comments_approx: bool | None = None
    elif isinstance(v.get("commentCountIsApproximate"), bool):
        comments_approx = v["commentCountIsApproximate"]
    else:
        comments_approx = True
    views = safe_int(v.get("viewCount") or v.get("views") or v.get("view_count"))
    views_approx = (
        bool(v["viewCountIsApproximate"])
        if isinstance(v.get("viewCountIsApproximate"), bool) and views is not None
        else False
        if views is not None
        else None
    )
    return {
        "platform": "youtube",
        "url": norm,
        "id": video_id or safe_str(v.get("id") or v.get("videoId")),
        "caption": safe_str(v.get("title")),
        "publishedAt": safe_str(v.get("date") or v.get("publishedAt") or v.get("uploadDate")),
        "thumbnailUrl": thumb,
        "durationSeconds": safe_int(v.get("durationSeconds") or v.get("duration")),
        "author": {
            "username": username,
            "displayName": display,
            "url": safe_str(v.get("channelUrl")),
            "verified": verified,
        },
        "engagement": {
            "views": views,
            "likes": safe_int(v.get("likes") or v.get("likeCount") or v.get("like_count")),
            "comments": comments,
            # Stable keys; YouTube has no public share/save counts.
            "shares": None,
            "saves": None,
            "viewsIsApproximate": views_approx,
            "commentsIsApproximate": comments_approx,
        },
    }


def _youtube_row_complete(row: dict[str, Any]) -> bool:
    """True when the showcase metrics (likes, comments, date, handle) are present.

    Thin ANDROID player responses often ship views + title only; those must not
    short-circuit Apify or the docs example looks like a half-built product.
    """
    eng = row.get("engagement") or {}
    author = row.get("author") or {}
    return (
        eng.get("likes") is not None
        and eng.get("comments") is not None
        and bool(row.get("publishedAt"))
        and bool(author.get("username"))
    )


def _twitter_analytics_row(n: dict[str, Any]) -> dict[str, Any]:
    eng = n.get("engagement") or {}
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


def _reddit_analytics_row(n: dict[str, Any]) -> dict[str, Any]:
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


def _threads_analytics_row(n: dict[str, Any]) -> dict[str, Any]:
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


async def _fetch_youtube(url: str) -> dict[str, Any]:
    # Prefer the enriched video-details native path; if watch-page enrich fails
    # (429 / thin ANDROID), fall through to Apify so likes/comments/handle land.
    norm = normalize_youtube_url(url)
    video_id = extract_youtube_id(url)
    native_row: dict[str, Any] | None = None
    if video_id:
        native = await _yt_video_details_native(video_id, norm)
        if native and (native.get("title") or native.get("viewCount") is not None):
            native_row = _youtube_analytics_row(native, norm=norm, video_id=video_id)
            if _youtube_row_complete(native_row):
                _mark_source("direct")
                return native_row

    settings = get_settings()
    try:
        items = await get_apify().run_actor_sync(
            settings.APIFY_ACTOR_YOUTUBE_VIDEO,
            {"startUrls": [{"url": norm}], "maxResults": 1},
            max_items=1,
        )
    except Exception:  # noqa: BLE001 — keep thin native rather than 502
        items = None
    if items:
        apify_row = _youtube_analytics_row(items[0], norm=norm, video_id=video_id)
        if _youtube_row_complete(apify_row) or native_row is None:
            _mark_source("apify")
            return apify_row
    if native_row is not None:
        _mark_source("direct")
        return native_row
    raise HTTPException(status_code=404, detail="Video not found")


async def _fetch_tiktok(url: str) -> dict[str, Any]:
    native = await tiktok_native.video_details_native(url)
    if native and native.get("id"):
        _mark_source("direct")
        return native
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_TIKTOK,
        {"postURLs": [url], "resultsPerPage": 1, "shouldDownloadVideos": False},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Video not found")
    _mark_source("apify")
    return _tiktok_normalize(items[0])


async def _fetch_instagram(url: str) -> dict[str, Any]:
    shortcode = extract_instagram_shortcode(url)
    if shortcode:
        native = await instagram_native.fetch_post_details(shortcode)
        if native and native.get("id"):
            _mark_source("direct")
            return native
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_INSTAGRAM_POST,
        {"directUrls": [url], "resultsLimit": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Post not found")
    _mark_source("apify")
    return _ig_normalize(items[0])


async def _fetch_facebook(url: str) -> dict[str, Any]:
    native = await facebook_details_native.details_native(url)
    if native:
        _mark_source("direct")
        return _fb_normalize(native)
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_FACEBOOK_POSTS,
        {"startUrls": [{"url": url}], "resultsLimit": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Post not found")
    _mark_source("apify")
    return _fb_normalize(items[0])


async def _fetch_twitter(url: str) -> dict[str, Any]:
    tweet_id = extract_tweet_id(url)
    if tweet_id:
        syn = await twitter_native.tweet_result(tweet_id)
        if syn:
            _mark_source("direct")
            return _twitter_analytics_row(_tw_normalize(syn))
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_TWITTER_TWEET,
        {"startUrls": [url], "maxItems": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Tweet not found")
    _mark_source("apify")
    return _twitter_analytics_row(_tw_normalize(items[0]))


async def _fetch_reddit(url: str) -> dict[str, Any]:
    try:
        post_id = _rd_require_post(url)
        post, _comments = await _rd_fetch_resilient(url, post_id, limit=1)
        _mark_source("direct")
        return _reddit_analytics_row(_rd_normalize(post))
    except HTTPException:
        raise
    except Exception:  # noqa: BLE001 — fall through to Apify
        pass
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_REDDIT,
        {"startUrls": [{"url": url}], "type": "posts", "maxItems": 1},
        max_items=2,
    )
    posts = [i for i in items if not _rd_is_comment(i)]
    if not posts:
        raise HTTPException(status_code=404, detail="Post not found")
    _mark_source("apify")
    return _reddit_analytics_row(_rd_normalize(posts[0]))


async def _fetch_threads(url: str) -> dict[str, Any]:
    native = await threads_native.post_details(url)
    if native and native.get("code"):
        _mark_source("direct")
        return _threads_analytics_row(_th_normalize(native))
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_THREADS,
        {"urls": [url], "resultsType": "details", "resultsLimit": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Post not found")
    _mark_source("apify")
    return _threads_analytics_row(_th_normalize(items[0]))


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
    _mark_source("direct")
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


def _linkedin_analytics_row(n: dict[str, Any]) -> dict[str, Any]:
    eng = n.get("engagement") or {}
    return {
        "platform": "linkedin",
        "url": n.get("url"),
        "id": n.get("id"),
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


def _pinterest_analytics_row(n: dict[str, Any]) -> dict[str, Any]:
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


def _rumble_analytics_row(n: dict[str, Any]) -> dict[str, Any]:
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
            "comments": n.get("comments"),
            "shares": None,
            "saves": None,
        },
    }


async def _fetch_linkedin(url: str) -> dict[str, Any]:
    native = await linkedin_native.fetch_post(url)
    if native:
        _mark_source("direct")
        return _linkedin_analytics_row(_li_normalize(native))
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_LINKEDIN_POST,
        {"url": url},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Post not found")
    _mark_source("apify")
    return _linkedin_analytics_row(_li_normalize(items[0]))


async def _fetch_pinterest(url: str) -> dict[str, Any]:
    pin_id = extract_pinterest_pin_id(url)
    if pin_id:
        native = await pinterest_native.fetch_pin_info(pin_id)
        if native:
            _mark_source("direct")
            return _pinterest_analytics_row(_pin_normalize(native))
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_PINTEREST,
        {"startUrls": [{"url": url}], "maxItems": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Pin not found")
    _mark_source("apify")
    return _pinterest_analytics_row(_pin_normalize(items[0]))


async def _fetch_rumble(url: str) -> dict[str, Any]:
    native = await rumble_video_native.video_details_native(url)
    if native and native.get("title"):
        # Native already returns the router video shape.
        _mark_source("direct")
        return _rumble_analytics_row(native)
    settings = get_settings()
    items = await get_apify().run_actor_sync(
        settings.APIFY_ACTOR_RUMBLE,
        {"startUrls": [{"url": url}], "maxItems": 1},
        max_items=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="Video not found")
    _mark_source("apify")
    return _rumble_analytics_row(_rb_normalize(items[0]))


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
    """Collapse a per-platform normalized post into one consistent metrics shape.

    Schema is stable: metrics always includes views/likes/comments/shares/saves/
    interactions/engagementRate/engagementRateBasis (+ approximate flags when
    a count is present); author always includes verified. Unavailable values
    are null — keys are never omitted.
    """
    eng = n.get("engagement") or {}
    views = eng.get("views")
    likes = eng.get("likes")
    comments = eng.get("comments")
    shares = eng.get("shares")
    saves = eng.get("saves")
    engagement_vals = [x for x in (likes, comments, shares, saves) if isinstance(x, int)]
    interactions = sum(engagement_vals) if engagement_vals else None
    # Never invent 0.0 engagement when every numerator is missing — a fake
    # rate misleads clients. Rate still computes from likes+comments alone.
    engagement_rate = (
        round(interactions / views, 4)
        if isinstance(views, int)
        and views > 0
        and isinstance(interactions, int)
        and engagement_vals
        else None
    )
    views_approx = eng.get("viewsIsApproximate") if views is not None else None
    comments_approx = eng.get("commentsIsApproximate") if comments is not None else None
    likes_approx = eng.get("likesIsApproximate") if likes is not None else None
    shares_approx = eng.get("sharesIsApproximate") if shares is not None else None
    saves_approx = eng.get("savesIsApproximate") if saves is not None else None
    # Derived totals inherit uncertainty from any approximate numerator that
    # contributed (and from views when the rate uses them).
    if interactions is None:
        interactions_approx: bool | None = None
    else:
        interactions_approx = bool(
            (isinstance(likes, int) and likes_approx)
            or (isinstance(comments, int) and comments_approx)
            or (isinstance(shares, int) and shares_approx)
            or (isinstance(saves, int) and saves_approx)
        )
    author = dict(n.get("author") or {})
    if "verified" not in author or not isinstance(author.get("verified"), bool):
        author["verified"] = None
    # username must stay a handle — never duplicate displayName into it.
    display = safe_str(author.get("displayName") or author.get("name"))
    username = safe_str(author.get("username") or author.get("handle"))
    if username and display and username.lower() == display.lower():
        # Likely a display-name leak (YouTube thin path). Drop username.
        if not username.startswith("@") and " " in username:
            author["username"] = None
    return {
        "platform": n.get("platform"),
        "url": n.get("url"),
        "id": n.get("id"),
        "title": n.get("title") or n.get("caption"),
        "publishedAt": _published_at_utc_z(n.get("publishedAt")),
        "durationSeconds": n.get("durationSeconds"),
        "thumbnailUrl": n.get("thumbnailUrl"),
        "author": author,
        "metrics": {
            "views": views,
            "viewsIsApproximate": (
                bool(views_approx) if isinstance(views_approx, bool) else False if views is not None else None
            ),
            "likes": likes,
            "comments": comments,
            "commentsIsApproximate": (
                bool(comments_approx)
                if isinstance(comments_approx, bool)
                else False
                if comments is not None
                else None
            ),
            "shares": shares,
            "saves": saves,
            "interactions": interactions,
            "interactionsIsApproximate": interactions_approx,
            "engagementRate": engagement_rate,
            "engagementRateBasis": ENGAGEMENT_RATE_BASIS,
        },
    }


@router.get(
    "/post",
    summary="Cross-platform post analytics (unified metrics)",
    description=(
        "Cross-platform post analytics for 11 networks (YouTube, TikTok, "
        "Instagram, Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest, "
        "LinkedIn, Rumble) — not the full Captapi catalog (Kwai, Twitch, "
        "Spotify, Snapchat, and others are out of scope). Platform is "
        "auto-detected from the URL; mix freely. Returns one normalized "
        f"metrics object including engagementRate with engagementRateBasis="
        f"{ENGAGEMENT_RATE_BASIS}. Compact UI counts (e.g. YouTube '2.4M' "
        "comments) set commentsIsApproximate / interactionsIsApproximate. "
        f"Costs {CREDIT_POST_ANALYTICS} credit."
    ),
)
async def post_analytics(
    url: str = Query(
        ...,
        description=(
            "Public post/video/reel URL from one of 11 supported platforms "
            "(YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, "
            "Bluesky, Pinterest, LinkedIn, Rumble). Platform is auto-detected "
            "— cross-platform URLs are the point of this endpoint."
        ),
    ),
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
            _analytics_source.set(None)
            n = await _FETCHERS[platform](url)
            ctx["source"] = _analytics_source.get() or "direct"
            return _unify(n)

        data = await cached_or_run(
            endpoint=f"analytics.post.{platform}",
            params={"url": url, "v": ANALYTICS_CACHE_VERSION},
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
        "Fetches the same unified metrics object as /v1/analytics/post for up to "
        "10 comma-separated URLs in one call (any mix of platforms). Each result "
        "includes platform, status (ok|error), and metrics.views/likes/comments/"
        "shares/saves/interactions/engagementRate (engagementRateBasis="
        f"{ENGAGEMENT_RATE_BASIS}). Failed URLs also appear in failed[] with a "
        "reason. Bills 1 credit per successfully resolved URL that is not served "
        "from cache (same per-URL cache as post analytics). No bulk discount vs "
        "calling /post N times — the win is one HTTP round-trip."
    ),
)
async def compare_analytics(
    urls: str = Query(
        ...,
        description="Comma-separated post URLs (up to 10), any mix of platforms",
    ),
    cache: bool = Query(
        False,
        description="Set true to use the 24h per-URL cache (shared with /v1/analytics/post). Default false — always fetch fresh.",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    url_list = [u.strip() for u in urls.split(",") if u.strip()][:MAX_COMPARE]
    if not url_list:
        raise HTTPException(status_code=400, detail="Provide at least one URL")

    base = len(url_list) * CREDIT_POST_ANALYTICS
    settings = get_settings()

    async with billed_call(
        caller=caller,
        endpoint="/v1/analytics/compare",
        platform="multi",
        resource_url=None,
        base_credits=base,
    ) as ctx:
        async def _one(u: str) -> tuple[dict[str, Any], bool]:
            """Return (row, cache_hit). cache_hit only when a resolved row came from cache."""
            p = _detect_platform(u)
            if not p:
                return {
                    "url": u,
                    "platform": None,
                    "status": "error",
                    "error": "unsupported_url",
                }, False

            async def _run() -> dict[str, Any]:
                _analytics_source.set(None)
                n = await _FETCHERS[p](u)
                return _unify(n)

            sub_ctx: dict[str, Any] = {}
            try:
                # Share the post-analytics cache key so compare(cache=true) after
                # /post on the same URL is a free hit.
                row = await cached_or_run(
                    endpoint=f"analytics.post.{p}",
                    params={"url": u, "v": ANALYTICS_CACHE_VERSION},
                    runner=_run,
                    ctx=sub_ctx,
                    ttl=settings.CACHE_TTL_DYNAMIC,
                    use_cache=cache,
                )
                return {**row, "status": "ok"}, bool(sub_ctx.get("cache_hit"))
            except HTTPException as e:
                reason = str(e.detail) if e.detail else "fetch_failed"
                return {
                    "url": u,
                    "platform": p,
                    "status": "error",
                    "error": reason,
                }, False
            except Exception:
                return {
                    "url": u,
                    "platform": p,
                    "status": "error",
                    "error": "fetch_failed",
                }, False

        pairs = list(await asyncio.gather(*[_one(u) for u in url_list]))
        results: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        resolved_count = 0
        fresh = 0
        for row, hit in pairs:
            results.append(row)
            if row.get("status") == "ok" and not row.get("error"):
                resolved_count += 1
                if not hit:
                    fresh += 1
            else:
                failed.append(
                    {
                        "url": row.get("url"),
                        "platform": row.get("platform"),
                        "reason": row.get("error") or "fetch_failed",
                    }
                )
        # Cache hits are free (same as /analytics/post). All-failed batches still
        # record a minimal 1-credit charge for the work attempted.
        if resolved_count == 0:
            ctx["credits_override"] = 1
        else:
            ctx["credits_override"] = fresh * CREDIT_POST_ANALYTICS
        if fresh == 0 and resolved_count:
            ctx["cache_hit"] = True
        return ApiResponse(
            data={
                "count": len(results),
                "resolved": resolved_count,
                "failedCount": len(failed),
                "results": results,
                "failed": failed,
            }
        )
