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


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    return max(minimum, math.ceil(n * rate))


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
