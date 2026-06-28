"""Twitter / X endpoints (tweets, timelines, search, profiles).

Backed by the apidojo Tweet Scraper V2 (tweets, search, per-handle timelines)
and the apidojo Twitter User Scraper (profiles). Field mappings are defensive —
both actors expose several aliases for the same value across versions.
"""

from __future__ import annotations

import math
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_list, safe_str
from app.utils.url import (
    extract_tweet_id,
    normalize_twitter_username,
)

router = APIRouter()

CREDIT_TWEET_DETAILS = 1
CREDIT_PROFILE = 1
# apidojo tweet-scraper is billed per result (~$0.0004-0.0008/result). 0.7
# credit/result keeps an ~80% markup at the $0.0045/credit sell price.
RATE_TWEET = 0.7


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


def _author(a: dict[str, Any]) -> dict[str, Any]:
    username = a.get("userName") or a.get("screen_name") or a.get("username")
    return {
        "username": safe_str(username),
        "displayName": safe_str(a.get("name") or a.get("fullName")),
        "url": safe_str(a.get("url"))
        or (f"https://x.com/{username}" if username else None),
        "followers": safe_int(a.get("followers") or a.get("followersCount")),
        "verified": a.get("isVerified") or a.get("isBlueVerified") or a.get("verified"),
        "profileImage": safe_str(a.get("profilePicture") or a.get("profile_image_url_https")),
    }


def _normalize_tweet(item: dict[str, Any]) -> dict[str, Any]:
    author = item.get("author") or item.get("user") or {}
    return {
        "platform": "twitter",
        "url": safe_str(item.get("url") or item.get("twitterUrl")),
        "id": safe_str(item.get("id") or item.get("id_str") or item.get("tweetId")),
        "text": safe_str(item.get("fullText") or item.get("text") or item.get("full_text")),
        "lang": safe_str(item.get("lang")),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created_at")),
        "author": _author(author),
        "engagement": {
            "views": safe_int(item.get("viewCount") or item.get("views")),
            "likes": safe_int(item.get("likeCount") or item.get("favoriteCount") or item.get("favorite_count")),
            "replies": safe_int(item.get("replyCount") or item.get("reply_count")),
            "retweets": safe_int(item.get("retweetCount") or item.get("retweet_count")),
            "quotes": safe_int(item.get("quoteCount")),
            "bookmarks": safe_int(item.get("bookmarkCount")),
        },
        "isReply": item.get("isReply"),
        "isRetweet": item.get("isRetweet"),
        "hashtags": [
            (h.get("text") if isinstance(h, dict) else h)
            for h in safe_list(item.get("hashtags") or (item.get("entities") or {}).get("hashtags"))
        ],
        "media": [
            safe_str(m.get("media_url_https") or m.get("url") or m) if isinstance(m, dict) else safe_str(m)
            for m in safe_list(item.get("media") or item.get("extendedEntities"))
        ],
    }


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    username = item.get("userName") or item.get("screen_name") or item.get("username")
    return {
        "platform": "twitter",
        "url": safe_str(item.get("url"))
        or (f"https://x.com/{username}" if username else None),
        "id": safe_str(item.get("id") or item.get("id_str")),
        "username": safe_str(username),
        "name": safe_str(item.get("name") or item.get("fullName")),
        "bio": safe_str(item.get("description") or item.get("bio")),
        "location": safe_str(item.get("location")),
        "verified": item.get("isVerified") or item.get("isBlueVerified") or item.get("verified"),
        "followers": safe_int(item.get("followers") or item.get("followersCount")),
        "following": safe_int(item.get("following") or item.get("followingCount") or item.get("friendsCount")),
        "tweetCount": safe_int(item.get("statusesCount") or item.get("tweetsCount") or item.get("statuses_count")),
        "profileImage": safe_str(item.get("profilePicture") or item.get("profile_image_url_https")),
        "bannerImage": safe_str(item.get("coverPicture") or item.get("profile_banner_url")),
        "createdAt": safe_str(item.get("createdAt") or item.get("created_at")),
    }


@router.get("/tweet-details", summary="Tweet metadata + engagement stats")
async def twitter_tweet_details(
    url: str = Query(..., description="Public tweet URL, e.g. https://x.com/user/status/ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_tweet_id(url):
        raise HTTPException(status_code=400, detail="Invalid tweet URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/tweet-details",
        platform="twitter",
        resource_url=url,
        base_credits=CREDIT_TWEET_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_TWEET,
                {"startUrls": [url], "maxItems": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Tweet not found")
            return _normalize_tweet(items[0])

        data = await cached_or_run(
            endpoint="twitter.tweet-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/transcript", summary="Twitter/X tweet transcript / text extraction")
async def twitter_transcript(
    url: str = Query(..., description="Public tweet URL, e.g. https://x.com/user/status/ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_tweet_id(url):
        raise HTTPException(status_code=400, detail="Invalid tweet URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/transcript",
        platform="twitter",
        resource_url=url,
        base_credits=CREDIT_TWEET_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_TWEET,
                {"startUrls": [url], "maxItems": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Tweet not found")
            tweet = _normalize_tweet(items[0])
            text = (tweet.get("text") or "").strip()
            if not text:
                raise HTTPException(status_code=422, detail="No transcript text available for this tweet")
            return {
                "platform": "twitter",
                "url": tweet.get("url") or url,
                "tweetId": tweet.get("id"),
                "transcript": text,
                "transcriptSegments": [{"text": text, "start": 0, "duration": 0, "timestamp": "00:00"}],
                "wordCount": len(text.split()),
                "segments": 1,
                "author": tweet.get("author"),
                "publishedAt": tweet.get("publishedAt"),
            }

        data = await cached_or_run(
            endpoint="twitter.transcript",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/profile", summary="Twitter/X profile details & stats")
async def twitter_profile(
    url: str = Query(..., description="Profile URL or @handle, e.g. https://x.com/username"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = normalize_twitter_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid Twitter/X profile URL or handle")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/profile",
        platform="twitter",
        resource_url=f"https://x.com/{handle}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_PROFILE,
                {"twitterHandles": [handle], "startUrls": [f"https://x.com/{handle}"], "maxItems": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Profile not found")
            return _normalize_profile(items[0])

        data = await cached_or_run(
            endpoint="twitter.profile",
            params={"handle": handle},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/user-tweets", summary="List recent tweets for a profile")
async def twitter_user_tweets(
    url: str = Query(..., description="Profile URL or @handle"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = normalize_twitter_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid Twitter/X profile URL or handle")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_TWEET, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/user-tweets",
        platform="twitter",
        resource_url=f"https://x.com/{handle}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_TWEET,
                {"twitterHandles": [handle], "maxItems": limit, "sort": "Latest"},
                max_items=limit,
            )
            tweets = [_normalize_tweet(t) for t in items[:limit]]
            return {"handle": handle, "totalReturned": len(tweets), "tweets": tweets}

        data = await cached_or_run(
            endpoint="twitter.user-tweets",
            params={"handle": handle, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["tweets"]), RATE_TWEET, 2)
        return ApiResponse(data=data)


@router.get("/search", summary="Search tweets by keyword")
async def twitter_search(
    q: str = Query(..., min_length=2, description="Search query or keywords"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_TWEET, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/search",
        platform="twitter",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_TWEET,
                {"searchTerms": [q], "maxItems": limit, "sort": "Top"},
                max_items=limit,
            )
            results = [_normalize_tweet(t) for t in items[:limit]]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="twitter.search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_TWEET, 2)
        return ApiResponse(data=data)


def _extract_community_id(value: str) -> str | None:
    value = (value or "").strip()
    match = re.search(r"/communities/(\d+)", value)
    if match:
        return match.group(1)
    if value.isdigit():
        return value
    return None


@router.get("/community", summary="X (Twitter) community details")
async def twitter_community(
    url: str = Query(..., description="Community URL (x.com/i/communities/ID) or community ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    community_id = _extract_community_id(url)
    if not community_id:
        raise HTTPException(status_code=400, detail="Invalid X community URL or ID")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/community",
        platform="twitter",
        resource_url=f"https://x.com/i/communities/{community_id}",
        base_credits=1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_COMMUNITY,
                {"mode": "Get Community Detail", "community_id": community_id},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Community not found")
            c = items[0]
            return {
                "platform": "twitter",
                "id": safe_str(c.get("id") or c.get("community_id") or community_id),
                "url": f"https://x.com/i/communities/{community_id}",
                "name": safe_str(c.get("name") or c.get("title")),
                "description": safe_str(c.get("description")),
                "memberCount": safe_int(c.get("memberCount") or c.get("member_count") or c.get("members")),
                "moderatorCount": safe_int(c.get("moderatorCount") or c.get("moderator_count")),
                "createdAt": safe_str(c.get("createdAt") or c.get("created_at")),
                "bannerImage": safe_str(c.get("bannerUrl") or c.get("banner_url") or c.get("coverImage")),
                "rules": c.get("rules") or [],
            }

        data = await cached_or_run(
            endpoint="twitter.community",
            params={"community_id": community_id},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/community-tweets", summary="Tweets posted in an X community")
async def twitter_community_tweets(
    url: str = Query(..., description="Community URL (x.com/i/communities/ID) or community ID"),
    limit: int = Query(25, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    community_id = _extract_community_id(url)
    if not community_id:
        raise HTTPException(status_code=400, detail="Invalid X community URL or ID")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_TWEET, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/community-tweets",
        platform="twitter",
        resource_url=f"https://x.com/i/communities/{community_id}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_COMMUNITY,
                {
                    "mode": "Get Community Tweets",
                    "community_id": community_id,
                    "tweet_type": "Latest",
                    "max_results": limit,
                },
                max_items=limit,
            )
            tweets = [_normalize_tweet(t) for t in items[:limit]]
            return {"communityId": community_id, "totalReturned": len(tweets), "tweets": tweets}

        data = await cached_or_run(
            endpoint="twitter.community-tweets",
            params={"community_id": community_id, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["tweets"]), RATE_TWEET, 2)
        return ApiResponse(data=data)
