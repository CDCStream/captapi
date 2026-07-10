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
from app.services import twitter_native as native
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import first_present, safe_int, safe_list, safe_str
from app.utils.url import (
    detect_url_platform,
    extract_tweet_id,
    normalize_twitter_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_TWEET_DETAILS = 1
CREDIT_PROFILE = 1
# apidojo tweet-scraper is billed per result (~$0.0004-0.0008/result). 0.7
# credit/result keeps an ~80% markup at the $0.0045/credit sell price.
RATE_TWEET = 0.7


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    return max(minimum, math.ceil(n * rate))


def _reject_twitter_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "twitter":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "twitter", example),
        )


def _require_tweet_url(url: str) -> str:
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "twitter", "https://x.com/user/status/123456789"),
        )
    return tweet_id


def _require_twitter_handle(value: str) -> str:
    _reject_twitter_platform_mismatch(value, "https://x.com/username")
    handle = normalize_twitter_username(value)
    if not handle:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "twitter", "https://x.com/username"),
        )
    return handle


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


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return None


def _normalize_tweet(item: dict[str, Any]) -> dict[str, Any]:
    author = item.get("author") or item.get("user") or {}
    if not author and item.get("username"):
        # Community scraper rows are flat with user_* prefixed author fields.
        author = {
            "userName": item.get("username"),
            "name": item.get("user_name"),
            "followers": item.get("user_followers_count"),
            "verified": bool(_as_bool(item.get("user_verified")) or _as_bool(item.get("user_is_blue_verified"))),
            "profilePicture": item.get("user_profile_image_url"),
        }
    url = safe_str(item.get("url") or item.get("twitterUrl"))
    if not url:
        username = author.get("userName") if isinstance(author, dict) else None
        tweet_id = item.get("id") or item.get("id_str")
        if username and tweet_id:
            url = f"https://x.com/{username}/status/{tweet_id}"
    return {
        "platform": "twitter",
        "url": url,
        "id": safe_str(item.get("id") or item.get("id_str") or item.get("tweetId")),
        "text": safe_str(item.get("fullText") or item.get("text") or item.get("full_text")),
        "lang": safe_str(item.get("lang")),
        "publishedAt": safe_str(item.get("createdAt") or item.get("created_at")),
        "author": _author(author),
        "engagement": {
            "views": safe_int(first_present(item.get("viewCount"), item.get("views"))),
            "likes": safe_int(first_present(item.get("likeCount"), item.get("favoriteCount"), item.get("favorite_count"))),
            "replies": safe_int(first_present(item.get("replyCount"), item.get("reply_count"))),
            "retweets": safe_int(first_present(item.get("retweetCount"), item.get("retweet_count"))),
            "quotes": safe_int(first_present(item.get("quoteCount"), item.get("quote_count"))),
            "bookmarks": safe_int(first_present(item.get("bookmarkCount"), item.get("bookmark_count"))),
        },
        "isReply": first_present(item.get("isReply"), _as_bool(item.get("is_reply"))),
        "isRetweet": first_present(item.get("isRetweet"), _as_bool(item.get("is_retweet"))),
        "hashtags": [
            tag
            for tag in (
                (h.get("text") or h.get("tag") if isinstance(h, dict) else safe_str(h))
                for h in safe_list(item.get("hashtags") or (item.get("entities") or {}).get("hashtags"))
            )
            if tag
        ],
        "media": [
            safe_str(m.get("media_url_https") or m.get("url") or m) if isinstance(m, dict) else safe_str(m)
            for m in safe_list(item.get("media") or item.get("extendedEntities"))
        ],
    }


def _entities_website(item: dict[str, Any]) -> str | None:
    entities = item.get("entities")
    if not isinstance(entities, dict):
        return None
    urls = (entities.get("url") or {}).get("urls")
    if isinstance(urls, list) and urls and isinstance(urls[0], dict):
        return safe_str(urls[0].get("expanded_url") or urls[0].get("url"))
    return None


def _verified_flag(item: dict[str, Any]) -> bool | None:
    """True/False when the actor reports verification, None when unknown.

    Must not use `a or b` chains: `False or None` collapses a real
    "not verified" answer into null.
    """
    value = first_present(item.get("isVerified"), item.get("isBlueVerified"), item.get("verified"))
    return bool(value) if value is not None else None


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    username = item.get("userName") or item.get("screen_name") or item.get("username")
    verified = _verified_flag(item)
    # apidojo/twitter-user-scraper dropped the isBlueVerified key; on today's X
    # the isVerified flag IS the blue checkmark, so mirror it when absent.
    blue = first_present(item.get("isBlueVerified"), item.get("isVerified"))
    return {
        "platform": "twitter",
        "url": safe_str(item.get("url"))
        or (f"https://x.com/{username}" if username else None),
        "id": safe_str(item.get("id") or item.get("id_str")),
        "username": safe_str(username),
        "name": safe_str(item.get("name") or item.get("fullName")),
        "bio": safe_str(item.get("description") or item.get("bio")),
        "location": safe_str(item.get("location")),
        "verified": verified,
        "followers": safe_int(first_present(item.get("followers"), item.get("followersCount"))),
        "following": safe_int(first_present(item.get("following"), item.get("followingCount"), item.get("friendsCount"))),
        "tweetCount": safe_int(first_present(item.get("statusesCount"), item.get("tweetsCount"), item.get("statuses_count"))),
        "likesCount": safe_int(first_present(item.get("favouritesCount"), item.get("favourites_count"), item.get("likesCount"))),
        "mediaCount": safe_int(first_present(item.get("mediaCount"), item.get("media_count"))),
        "listedCount": safe_int(first_present(item.get("listedCount"), item.get("listed_count"))),
        "isBlueVerified": bool(blue) if blue is not None else None,
        "website": safe_str(item.get("website")) or _entities_website(item),
        "profileImage": safe_str(item.get("profilePicture") or item.get("profile_image_url_https")),
        "bannerImage": safe_str(item.get("coverPicture") or item.get("profile_banner_url")),
        "createdAt": safe_str(item.get("createdAt") or item.get("created_at")),
    }


@router.get("/tweet-details", summary="Tweet metadata + engagement stats")
async def twitter_tweet_details(
    url: str = Query(..., description="Public tweet URL, e.g. https://x.com/user/status/ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_tweet_url(url)
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
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/transcript", summary="Twitter/X tweet transcript / text extraction")
async def twitter_transcript(
    url: str = Query(..., description="Public tweet URL, e.g. https://x.com/user/status/ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    tweet_id = _require_tweet_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/transcript",
        platform="twitter",
        resource_url=url,
        base_credits=CREDIT_TWEET_DETAILS,
    ) as ctx:
        def _payload(text: str, tweet_url: str, tid: str | None, author: dict[str, Any] | None, published: str | None) -> dict[str, Any]:
            return {
                "platform": "twitter",
                "url": tweet_url or url,
                "tweetId": tid,
                "transcript": text,
                "transcriptSegments": [{"text": text, "start": 0, "duration": 0, "timestamp": "00:00"}],
                "wordCount": len(text.split()),
                "segments": 1,
                "author": author,
                "publishedAt": published,
            }

        async def _run() -> dict[str, Any]:
            # Transcript is text-only, so the free public syndication API is a
            # perfect fit; only fall back to the paid actor if it misses.
            syn = await native.tweet_result(tweet_id)
            if syn:
                text = (syn.get("text") or "").strip()
                if text:
                    u = syn.get("user") or {}
                    username = u.get("screen_name")
                    ctx["source"] = "direct"
                    return _payload(
                        text,
                        f"https://x.com/{username}/status/{tweet_id}" if username else url,
                        safe_str(syn.get("id_str")) or tweet_id,
                        _author(u),
                        safe_str(syn.get("created_at")),
                    )

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
            ctx["source"] = "apify"
            return _payload(text, tweet.get("url") or url, tweet.get("id"), tweet.get("author"), tweet.get("publishedAt"))

        data = await cached_or_run(
            endpoint="twitter.transcript",
            params={"url": url, "v": 3},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/profile", summary="Twitter/X profile details & stats")
async def twitter_profile(
    url: str = Query(..., description="Profile URL or @handle, e.g. https://x.com/username"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_twitter_handle(url)
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
            ctx["source"] = "apify"
            return _normalize_profile(items[0])

        data = await cached_or_run(
            endpoint="twitter.profile",
            params={"handle": handle, "v": 3},
            runner=_run,
            ctx=ctx,
            # The apidojo actor cold-starts at ~14s. Profiles are polled
            # repeatedly (monitoring dashboards) and follower counts drift
            # slowly, so serve the last copy instantly after the 1h TTL and
            # refresh in the background instead of making every caller wait.
            stale_while_revalidate=True,
        )
        return ApiResponse(data=data)


@router.get("/user-tweets", summary="List recent tweets for a profile")
async def twitter_user_tweets(
    url: str = Query(..., description="Profile URL or @handle"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_twitter_handle(url)
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
            params={"handle": handle, "limit": limit, "v": 2},
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
            params={"q": q, "limit": limit, "v": 2},
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
    _reject_twitter_platform_mismatch(url, "https://x.com/i/communities/123456789")
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
            banner = c.get("banner")
            if isinstance(banner, dict):
                banner = banner.get("url") or banner.get("media_url_https")
            return {
                "platform": "twitter",
                "id": safe_str(c.get("id") or c.get("community_id") or community_id),
                "url": f"https://x.com/i/communities/{community_id}",
                "name": safe_str(c.get("name") or c.get("title")),
                "description": safe_str(c.get("description")),
                "memberCount": safe_int(c.get("memberCount") or c.get("member_count") or c.get("members")),
                "moderatorCount": safe_int(c.get("moderatorCount") or c.get("moderator_count")),
                "createdAt": safe_str(
                    c.get("createdAt") or c.get("created_at_datetime") or c.get("created_at")
                ),
                "creator": safe_str(c.get("creator_username") or c.get("creatorUsername")),
                "joinPolicy": safe_str(c.get("join_policy") or c.get("joinPolicy")),
                "isNsfw": first_present(c.get("is_nsfw"), c.get("isNsfw")),
                "bannerImage": safe_str(
                    banner or c.get("bannerUrl") or c.get("banner_url") or c.get("coverImage")
                ),
                "rules": c.get("rules") or [],
            }

        data = await cached_or_run(
            endpoint="twitter.community",
            params={"community_id": community_id, "v": 2},
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
    _reject_twitter_platform_mismatch(url, "https://x.com/i/communities/123456789")
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
            params={"community_id": community_id, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["tweets"]), RATE_TWEET, 2)
        return ApiResponse(data=data)
