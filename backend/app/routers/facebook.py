"""Facebook endpoints."""

from __future__ import annotations

import html
import math
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.apify_proxy import fetch_via_residential
from app.services.cached_runner import cached_or_run
from app.services.openai_client import summarize_transcript
from app.utils.formatters import safe_float, safe_int, safe_str
from app.utils.url import extract_facebook_page, extract_facebook_video_id

router = APIRouter()

CREDIT_TRANSCRIPT = 2
CREDIT_SUMMARIZE = 4
CREDIT_DETAILS = 1
CREDIT_PAGE_DETAILS = 1

# apify/facebook-comments-scraper is billed per result ($1.50/1k = $0.0015).
# 0.6 credit/comment = ~80% markup (0.6 * $0.0045 = $0.0027 vs $0.0015).
RATE_FB_COMMENTS = 0.6
# Posts / reels / group posts scrapers are billed per result (~$0.0015-0.002).
RATE_FB_POSTS = 0.6
# Marketplace listings billed at $4.50/1k = $0.0045/result -> 1 credit/listing.
RATE_FB_MARKETPLACE = 1.0
# Events billed at $13/1k = $0.013/event -> 2 credits/event.
RATE_FB_EVENTS = 2.0


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    return max(minimum, math.ceil(n * rate))


def _reply_payload(r: dict) -> dict:
    return {
        "id": safe_str(r.get("id") or r.get("commentId")),
        "text": (r.get("text") or "").strip(),
        "author": safe_str(r.get("profileName") or r.get("authorName")),
        "likeCount": safe_int(r.get("likesCount") or r.get("reactionsCount")),
        "publishedAt": safe_str(r.get("date") or r.get("publishedAt")),
    }


def _normalize_post(item: dict) -> dict:
    raw_media = item.get("media")
    if isinstance(raw_media, list):
        media = raw_media[0] if raw_media and isinstance(raw_media[0], dict) else {}
    elif isinstance(raw_media, dict):
        media = raw_media
    else:
        media = {}
    return {
        "platform": "facebook",
        "url": safe_str(item.get("url") or item.get("postUrl")),
        "id": safe_str(item.get("postId") or item.get("id")),
        "caption": safe_str(item.get("text") or item.get("description")),
        "description": safe_str(item.get("text")),
        "publishedAt": safe_str(item.get("time") or item.get("publishedAt")),
        "durationSeconds": safe_float(item.get("videoDuration") or media.get("duration")),
        "thumbnailUrl": safe_str(item.get("thumbnailUrl") or media.get("thumbnailUrl")),
        "videoUrl": safe_str(item.get("videoUrl") or media.get("videoUrl")),
        "author": {
            "username": safe_str(item.get("pageUsername") or item.get("author")),
            "displayName": safe_str(item.get("pageName") or item.get("authorName")),
            "url": safe_str(item.get("pageUrl") or item.get("authorUrl")),
            "verified": item.get("isPageVerified") or item.get("verified"),
        },
        "engagement": {
            "views": safe_int(item.get("viewsCount") or item.get("videoViewCount")),
            "likes": safe_int(item.get("likesCount") or item.get("reactionsCount")),
            "comments": safe_int(item.get("commentsCount")),
            "shares": safe_int(item.get("sharesCount")),
        },
    }


def _is_reel(item: dict) -> bool:
    u = (item.get("url") or item.get("postUrl") or "").lower()
    return "/reel/" in u or "/reels/" in u


def _normalize_listing(item: dict) -> dict:
    return {
        "platform": "facebook",
        "id": safe_str(item.get("id")),
        "title": safe_str(item.get("title")),
        "url": safe_str(item.get("url")),
        "price": item.get("price"),
        "priceFormatted": safe_str(item.get("price_formatted")),
        "currency": safe_str(item.get("currency")),
        "location": safe_str(item.get("location_display") or item.get("city")),
        "city": safe_str(item.get("city")),
        "state": safe_str(item.get("state")),
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
        "isSold": item.get("is_sold"),
        "isLive": item.get("is_live"),
        "deliveryTypes": item.get("delivery_types") or [],
        "image": safe_str(item.get("primary_photo")),
        "photos": item.get("photos") or [],
        "description": safe_str(item.get("description")),
        "createdAt": safe_str(item.get("creation_time")),
    }


def _normalize_marketplace_location(item: dict) -> dict | None:
    city = safe_str(item.get("city"))
    state = safe_str(item.get("state"))
    label = safe_str(item.get("location_display") or ", ".join(p for p in [city, state] if p))
    if not (label or city or state):
        return None
    key = "|".join(str(v or "").lower() for v in [label, city, state, item.get("latitude"), item.get("longitude")])
    return {
        "id": key,
        "name": label or city or state,
        "city": city,
        "state": state,
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
    }


def _normalize_event(item: dict) -> dict:
    loc = item.get("location") if isinstance(item.get("location"), dict) else {}
    tickets = item.get("ticketsInfo") if isinstance(item.get("ticketsInfo"), dict) else {}
    organizers = item.get("organizators") if isinstance(item.get("organizators"), list) else []
    return {
        "platform": "facebook",
        "id": safe_str(item.get("id")),
        "url": safe_str(item.get("url")),
        "name": safe_str(item.get("name")),
        "description": safe_str(item.get("description")),
        "startDate": safe_str(item.get("utcStartDate")),
        "startTime": safe_str(item.get("startTime") or item.get("dateTimeSentence")),
        "duration": safe_str(item.get("duration")),
        "eventType": safe_str(item.get("eventType")),
        "isOnline": item.get("isOnline"),
        "isPast": item.get("isPast"),
        "isCanceled": item.get("isCanceled"),
        "address": safe_str(item.get("address")),
        "image": safe_str(item.get("imageUrl")),
        "usersGoing": safe_int(item.get("usersGoing")),
        "usersInterested": safe_int(item.get("usersInterested")),
        "usersResponded": safe_int(item.get("usersResponded")),
        "location": {
            "name": safe_str(loc.get("name")),
            "city": safe_str(loc.get("city") or loc.get("contextualName")),
            "latitude": loc.get("latitude"),
            "longitude": loc.get("longitude"),
            "countryCode": safe_str(loc.get("countryCode")),
        },
        "organizer": safe_str(item.get("organizedBy")),
        "organizers": [
            {
                "id": safe_str(o.get("id")),
                "name": safe_str(o.get("name")),
                "url": safe_str(o.get("url")),
                "verified": o.get("isVerified"),
            }
            for o in organizers
            if isinstance(o, dict)
        ],
        "ticketsUrl": safe_str(tickets.get("buyUrl")),
        "categories": item.get("discoveryCategories") or [],
        "externalLinks": item.get("externalLinks") or [],
    }


@router.get("/details", summary="Facebook video/post details")
async def facebook_details(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/details",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_POSTS,
                {"startUrls": [{"url": url}], "resultsLimit": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Post not found")
            return _normalize_post(items[0])

        data = await cached_or_run(
            endpoint="facebook.details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/transcript", summary="Facebook video transcript")
async def facebook_transcript(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/transcript",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_POSTS,
                {"startUrls": [{"url": url}], "shouldDownloadSubtitles": True, "resultsLimit": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Post not found")
            item = items[0]
            subs = item.get("subtitles") or item.get("captions") or []
            segments = []
            parts = []
            if isinstance(subs, list):
                for s in subs:
                    text = ((s.get("text") if isinstance(s, dict) else str(s)) or "").strip()
                    start = float((s.get("start") if isinstance(s, dict) else 0) or 0)
                    dur = float((s.get("duration") if isinstance(s, dict) else 0) or 0)
                    if text:
                        mm = int(start // 60)
                        ss = int(start % 60)
                        segments.append(
                            {"text": text, "start": start, "duration": dur, "timestamp": f"{mm:02d}:{ss:02d}"}
                        )
                        parts.append(text)
            full = " ".join(parts) or safe_str(item.get("text")) or ""
            if not full:
                raise HTTPException(status_code=422, detail="No transcript available")
            return {
                "platform": "facebook",
                "url": url,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
            }

        data = await cached_or_run(
            endpoint="facebook.transcript",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/summarize", summary="AI summary of Facebook video/post")
async def facebook_summarize(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/summarize",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_POSTS,
                {"startUrls": [{"url": url}], "shouldDownloadSubtitles": True, "resultsLimit": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Post not found")
            item = items[0]
            subs = item.get("subtitles") or []
            parts = []
            if isinstance(subs, list):
                for s in subs:
                    text = ((s.get("text") if isinstance(s, dict) else str(s)) or "").strip()
                    if text:
                        parts.append(text)
            text = (" ".join(parts) or safe_str(item.get("text")) or "").strip()
            if not text:
                raise HTTPException(status_code=422, detail="No content to summarize")
            ai = await summarize_transcript(text, title=safe_str(item.get("text")))
            return {
                "platform": "facebook",
                "url": url,
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
            }

        data = await cached_or_run(
            endpoint="facebook.summarize",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Facebook post comments")
async def facebook_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FB_COMMENTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/comments",
        platform="facebook",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_COMMENTS,
                {"startUrls": [{"url": url}], "resultsLimit": limit},
                max_items=limit,
            )
            comments = []
            for c in items[:limit]:
                comments.append(
                    {
                        "id": safe_str(c.get("id") or c.get("commentId")),
                        "text": (c.get("text") or "").strip(),
                        "author": safe_str(c.get("profileName") or c.get("authorName")),
                        "likeCount": safe_int(c.get("likesCount") or c.get("reactionsCount")),
                        "publishedAt": safe_str(c.get("date") or c.get("publishedAt")),
                        "replyCount": safe_int(c.get("repliesCount")),
                    }
                )
            return {
                "platform": "facebook",
                "url": url,
                "totalReturned": len(comments),
                "comments": comments,
            }

        data = await cached_or_run(
            endpoint="facebook.comments",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["comments"]), RATE_FB_COMMENTS, 2)
        return ApiResponse(data=data)


@router.get("/page-details", summary="Facebook page info & stats")
async def facebook_page_details(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_facebook_page(url):
        raise HTTPException(status_code=400, detail="Invalid Facebook page URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/page-details",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_PAGE_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_PAGES,
                {"startUrls": [{"url": url}]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Page not found")
            p = items[0]
            return {
                "platform": "facebook",
                "url": url,
                "username": safe_str(p.get("pageUsername") or p.get("username")),
                "displayName": safe_str(p.get("pageName") or p.get("title")),
                "bio": safe_str(p.get("intro") or p.get("about")),
                "followers": safe_int(p.get("followersCount") or p.get("followers")),
                "likes": safe_int(p.get("likesCount") or p.get("likes")),
                "verified": p.get("verified") or p.get("isPageVerified"),
                "profileImage": safe_str(p.get("profilePictureUrl") or p.get("profilePicUrl")),
                "category": safe_str(p.get("category")),
                "website": safe_str(p.get("website")),
            }

        data = await cached_or_run(
            endpoint="facebook.page-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/profile-posts", summary="Latest posts from a Facebook profile/page")
async def facebook_profile_posts(
    url: str = Query(..., description="Facebook profile or page URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_facebook_page(url):
        raise HTTPException(status_code=400, detail="Invalid Facebook profile/page URL")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FB_POSTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/profile-posts",
        platform="facebook",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_POSTS,
                {"startUrls": [{"url": url}], "resultsLimit": limit},
                max_items=limit,
            )
            posts = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="facebook.profile-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_FB_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/profile-reels", summary="Latest Reels from a Facebook profile/page")
async def facebook_profile_reels(
    url: str = Query(..., description="Facebook profile or page URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_facebook_page(url):
        raise HTTPException(status_code=400, detail="Invalid Facebook profile/page URL")
    settings = get_settings()
    # Reels are a subset of the feed, so we over-fetch posts and filter. Cost is
    # driven by posts fetched, not reels returned.
    n_fetch = min(limit * 3, 100)
    cost = _scaled_credits(n_fetch, RATE_FB_POSTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/profile-reels",
        platform="facebook",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_REELS,
                {"startUrls": [{"url": url}], "resultsLimit": n_fetch},
                max_items=n_fetch,
            )
            reels = [
                _normalize_post(i)
                for i in items
                if not i.get("error") and _is_reel(i)
            ][:limit]
            return {"url": url, "totalReturned": len(reels), "reels": reels}

        data = await cached_or_run(
            endpoint="facebook.profile-reels",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = cost
        return ApiResponse(data=data)


@router.get("/group-posts", summary="Posts from a public Facebook group")
async def facebook_group_posts(
    url: str = Query(..., description="Public Facebook group URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FB_POSTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/group-posts",
        platform="facebook",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_GROUPS,
                {"startUrls": [{"url": url}], "resultsLimit": limit},
                max_items=limit,
            )
            posts = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="facebook.group-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_FB_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/comment-replies", summary="Replies to a Facebook comment")
async def facebook_comment_replies(
    url: str = Query(..., description="Facebook post URL the comment belongs to"),
    comment_id: str = Query(..., description="ID of the parent comment"),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FB_COMMENTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/comment-replies",
        platform="facebook",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_COMMENTS,
                {"startUrls": [{"url": url}], "resultsLimit": limit * 4, "includeNestedComments": True},
                max_items=limit * 4,
            )
            replies = []
            for c in items:
                parent = safe_str(c.get("parentCommentId") or c.get("replyToId") or c.get("commentParentId"))
                nested = c.get("replies") or c.get("nestedComments")
                if isinstance(nested, list) and safe_str(c.get("id") or c.get("commentId")) == comment_id:
                    for r in nested:
                        replies.append(_reply_payload(r))
                elif parent == comment_id:
                    replies.append(_reply_payload(c))
                if len(replies) >= limit:
                    break
            return {
                "platform": "facebook",
                "url": url,
                "commentId": comment_id,
                "totalReturned": len(replies[:limit]),
                "replies": replies[:limit],
            }

        data = await cached_or_run(
            endpoint="facebook.comment-replies",
            params={"url": url, "comment_id": comment_id, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["replies"]), RATE_FB_COMMENTS, 2)
        return ApiResponse(data=data)


def _normalize_photo(item: dict) -> dict:
    return {
        "platform": "facebook",
        "id": safe_str(item.get("id") or item.get("photoId") or item.get("photo_id")),
        "url": safe_str(item.get("url") or item.get("photoUrl") or item.get("postUrl")),
        "image": safe_str(
            item.get("imageUrl")
            or item.get("image")
            or item.get("imageUri")
            or item.get("src")
            or item.get("thumbnail")
        ),
        "caption": safe_str(item.get("caption") or item.get("text") or item.get("ocrText")),
        "publishedAt": safe_str(item.get("timestamp") or item.get("date") or item.get("publishedAt")),
        "likes": safe_int(item.get("likesCount") or item.get("reactionsCount")),
        "comments": safe_int(item.get("commentsCount")),
        "width": safe_int(item.get("width")),
        "height": safe_int(item.get("height")),
    }


@router.get("/profile-photos", summary="Photos from a Facebook profile/page")
async def facebook_profile_photos(
    url: str = Query(..., description="Facebook profile or page URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_facebook_page(url):
        raise HTTPException(status_code=400, detail="Invalid Facebook profile/page URL")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FB_POSTS, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/profile-photos",
        platform="facebook",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_PHOTOS,
                {"startUrls": [{"url": url}], "resultsLimit": limit},
                max_items=limit,
            )
            photos = [_normalize_photo(i) for i in items[:limit] if not i.get("error")]
            return {"url": url, "totalReturned": len(photos), "photos": photos}

        data = await cached_or_run(
            endpoint="facebook.profile-photos",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["photos"]), RATE_FB_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/profile-events", summary="Events from a Facebook profile/page")
async def facebook_profile_events(
    url: str = Query(..., description="Facebook profile or page URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_facebook_page(url):
        raise HTTPException(status_code=400, detail="Invalid Facebook profile/page URL")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FB_EVENTS, 4)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/profile-events",
        platform="facebook",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                {"startUrls": [url], "maxEvents": limit},
                max_items=limit,
            )
            events = [_normalize_event(i) for i in items[:limit] if not i.get("error")]
            return {"platform": "facebook", "url": url, "totalReturned": len(events), "events": events}

        data = await cached_or_run(
            endpoint="facebook.profile-events",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["events"]), RATE_FB_EVENTS, 4)
        return ApiResponse(data=data)


def _og_meta(page: str, key: str) -> str | None:
    pattern = rf'<meta\s+(?:property|name)=["\']{re.escape(key)}["\']\s+content=["\']([^"\']*)["\']'
    match = re.search(pattern, page, flags=re.IGNORECASE)
    if not match:
        pattern = rf'<meta\s+content=["\']([^"\']*)["\']\s+(?:property|name)=["\']{re.escape(key)}["\']'
        match = re.search(pattern, page, flags=re.IGNORECASE)
    return html.unescape(match.group(1)).strip() if match else None


@router.get("/marketplace-item", summary="Facebook Marketplace listing details")
async def facebook_marketplace_item(
    url: str = Query(..., description="Facebook Marketplace item URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    if "/marketplace/item/" not in (url or "").lower():
        raise HTTPException(status_code=400, detail="Invalid Facebook Marketplace item URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/marketplace-item",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            # Preferred: the marketplace actor when it accepts a direct item URL.
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_FACEBOOK_MARKETPLACE,
                    {"startUrls": [{"url": url}], "fetchItemDetails": True, "maxResultsPerQuery": 1},
                    max_items=1,
                )
            except Exception:
                items = []
            if items and not items[0].get("error"):
                return _normalize_listing(items[0])

            # Fallback: scrape OpenGraph metadata from the public listing page.
            # Facebook serves OG tags to residential IPs but login-walls
            # datacenter IPs, so try the Apify residential proxy first and fall
            # back to a direct fetch.
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
                )
            }
            resp = None
            try:
                resp = await fetch_via_residential(url, headers=headers, timeout=35)
            except Exception:  # noqa: BLE001
                resp = None

            def _og_fields(page: str) -> tuple[str | None, str | None, str | None]:
                return (
                    _og_meta(page, "og:title"),
                    _og_meta(page, "og:description"),
                    _og_meta(page, "og:image"),
                )

            title = description = image = None
            if resp is not None and resp.status_code < 400:
                title, description, image = _og_fields(resp.text)
            if not (title or description or image):
                async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
                    resp = await client.get(url)
                if resp.status_code >= 400:
                    raise HTTPException(status_code=404, detail="Listing not found")
                title, description, image = _og_fields(resp.text)
            if not (title or description or image):
                raise HTTPException(status_code=404, detail="Listing not found")
            page = resp.text
            item_id = None
            m = re.search(r"/marketplace/item/(\d+)", url)
            if m:
                item_id = m.group(1)
            return {
                "platform": "facebook",
                "id": safe_str(item_id),
                "url": safe_str(_og_meta(page, "og:url") or url),
                "title": safe_str(title),
                "description": safe_str(description),
                "image": safe_str(image),
                "price": None,
                "location": None,
                "photos": [image] if image else [],
            }

        data = await cached_or_run(
            endpoint="facebook.marketplace-item",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/marketplace-search", summary="Search Facebook Marketplace listings")
async def facebook_marketplace_search(
    q: str = Query(..., min_length=2, description="Product/keyword to search for"),
    location: str = Query(..., min_length=2, description="City or place name, e.g. 'Austin, TX'"),
    limit: int = Query(20, ge=1, le=200),
    details: bool = Query(False, description="Fetch full description, photos & coordinates per listing (slower, costs more)"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    rate = RATE_FB_MARKETPLACE * (2 if details else 1)
    cost = _scaled_credits(limit, rate, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/marketplace-search",
        platform="facebook",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_MARKETPLACE,
                {
                    "queries": [q],
                    "locationName": location,
                    "maxResultsPerQuery": limit,
                    "fetchItemDetails": details,
                },
                max_items=limit,
            )
            listings = [_normalize_listing(i) for i in items[:limit] if not i.get("error")]
            return {"query": q, "location": location, "totalReturned": len(listings), "listings": listings}

        data = await cached_or_run(
            endpoint="facebook.marketplace-search",
            params={"q": q, "location": location, "limit": limit, "details": details},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["listings"]), rate, 2)
        return ApiResponse(data=data)


@router.get("/marketplace-location-search", summary="Search Facebook Marketplace locations")
async def facebook_marketplace_location_search(
    q: str = Query(..., min_length=2, description="City/place search query, e.g. Austin"),
    limit: int = Query(10, ge=1, le=50),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/marketplace-location-search",
        platform="facebook",
        resource_url=None,
        base_credits=1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_MARKETPLACE,
                {
                    "queries": ["chair"],
                    "locationName": q,
                    "maxResultsPerQuery": min(max(limit, 5), 50),
                    "fetchItemDetails": False,
                },
                max_items=min(max(limit, 5), 50),
            )
            locations: dict[str, dict] = {}
            for item in items:
                if item.get("error"):
                    continue
                loc = _normalize_marketplace_location(item)
                if loc and loc["id"] not in locations:
                    locations[loc["id"]] = loc
            results = list(locations.values())[:limit]
            if not results:
                fallback = {"id": q.strip().lower(), "name": q.strip(), "city": q.strip(), "state": None, "latitude": None, "longitude": None}
                results = [fallback]
            return {"query": q, "totalReturned": len(results), "locations": results}

        data = await cached_or_run(
            endpoint="facebook.marketplace-location-search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/event-search", summary="Search Facebook events by keyword/location")
async def facebook_event_search(
    q: str = Query(..., min_length=2, description="Topic and/or place, e.g. 'comedy Chicago'"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FB_EVENTS, 4)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/event-search",
        platform="facebook",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                {"searchQueries": [q], "maxEvents": limit},
                max_items=limit,
            )
            events = [_normalize_event(i) for i in items[:limit] if not i.get("error")]
            return {"query": q, "totalReturned": len(events), "events": events}

        data = await cached_or_run(
            endpoint="facebook.event-search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["events"]), RATE_FB_EVENTS, 4)
        return ApiResponse(data=data)


@router.get("/event-details", summary="Facebook event details")
async def facebook_event_details(
    url: str = Query(..., description="Facebook event URL, e.g. https://facebook.com/events/ID"),
    caller: ApiCaller = Depends(require_api_key),
):
    if "/events/" not in url.lower():
        raise HTTPException(status_code=400, detail="Invalid Facebook event URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/event-details",
        platform="facebook",
        resource_url=url,
        base_credits=2,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                    {"startUrls": [url], "maxEvents": 1},
                    max_items=1,
                )
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=502, detail="Event lookup failed upstream") from exc
            if not items or items[0].get("error"):
                raise HTTPException(status_code=404, detail="Event not found")
            return _normalize_event(items[0])

        data = await cached_or_run(
            endpoint="facebook.event-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)
