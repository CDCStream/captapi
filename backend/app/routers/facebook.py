"""Facebook endpoints."""

from __future__ import annotations

import math
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
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
# Posts / group posts scrapers are billed per result (~$0.0015-0.002).
RATE_FB_POSTS = 0.6
# powerful_bachelor reels PPR actor is billed $3.90/1k ($0.0039). 1.6 credit/reel
# = ~80% markup (1.6 * $0.0045 = $0.0072 vs $0.0039).
RATE_FB_REELS = 1.6


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


def _normalize_reel(item: dict) -> dict:
    owner = item.get("video_owner") or {}
    dur_ms = item.get("playable_duration_in_ms")
    return {
        "platform": "facebook",
        "url": safe_str(item.get("permalink_url") or item.get("shareable_url")),
        "id": safe_str(item.get("video_id") or item.get("id")),
        "caption": safe_str(item.get("message") or item.get("caption")),
        "description": safe_str(item.get("message")),
        "publishedAt": safe_str(item.get("creation_time") or item.get("publishedAt")),
        "durationSeconds": (safe_float(dur_ms) / 1000.0) if dur_ms else safe_float(item.get("duration")),
        "audioTitle": safe_str(item.get("track_title")),
        "thumbnailUrl": safe_str(item.get("thumbnail_url") or item.get("preview_image_url")),
        "videoUrl": safe_str(item.get("video_url") or item.get("playable_url")),
        "author": {
            "username": safe_str(owner.get("profile_url") or owner.get("id")),
            "displayName": safe_str(owner.get("name")),
            "url": safe_str(owner.get("profile_url")),
            "verified": owner.get("is_verified"),
        },
        "engagement": {
            "views": safe_int(item.get("play_count") or item.get("view_count")),
            "likes": safe_int(item.get("like_count") or item.get("reaction_count")),
            "comments": safe_int(item.get("comment_count")),
            "shares": safe_int(item.get("share_count")),
        },
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
    cost = _scaled_credits(limit, RATE_FB_REELS, 2)
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
                {"profileUrls": [url], "maxResults": limit},
                max_items=limit,
            )
            reels = [_normalize_reel(i) for i in items[:limit] if not i.get("error")]
            return {"url": url, "totalReturned": len(reels), "reels": reels}

        data = await cached_or_run(
            endpoint="facebook.profile-reels",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["reels"]), RATE_FB_REELS, 2)
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
