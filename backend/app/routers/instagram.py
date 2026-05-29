"""Instagram endpoints (Reels, Posts, Profiles)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.services.openai_client import summarize_transcript
from app.utils.formatters import safe_float, safe_int, safe_list, safe_str
from app.utils.url import extract_instagram_shortcode, extract_instagram_username

router = APIRouter()

CREDIT_TRANSCRIPT = 2
CREDIT_SUMMARIZE = 4
CREDIT_DETAILS = 1
CREDIT_COMMENTS_BASE = 2
CREDIT_CHANNEL = 1
CREDIT_CHANNEL_POSTS_BASE = 2
CREDIT_CHANNEL_REELS_BASE = 2
CREDIT_SEARCH = 2
CREDIT_DOWNLOAD = 3


def _normalize_post(item: dict) -> dict:
    author = item.get("ownerUsername") or (item.get("owner") or {}).get("username")
    return {
        "platform": "instagram",
        "url": safe_str(item.get("url") or item.get("permalink")),
        "id": safe_str(item.get("id") or item.get("shortCode")),
        "caption": safe_str(item.get("caption")),
        "description": safe_str(item.get("caption")),
        "publishedAt": safe_str(item.get("timestamp") or item.get("takenAt")),
        "durationSeconds": safe_float(item.get("videoDuration") or item.get("duration")),
        "thumbnailUrl": safe_str(item.get("displayUrl") or item.get("thumbnailUrl")),
        "videoUrl": safe_str(item.get("videoUrl")),
        "author": {
            "username": safe_str(author),
            "displayName": safe_str(item.get("ownerFullName") or (item.get("owner") or {}).get("fullName")),
            "url": f"https://instagram.com/{author}" if author else None,
            "followers": safe_int((item.get("owner") or {}).get("followerCount")),
            "verified": (item.get("owner") or {}).get("isVerified"),
            "profileImage": safe_str((item.get("owner") or {}).get("profilePicUrl")),
        },
        "engagement": {
            "views": safe_int(item.get("videoViewCount") or item.get("videoPlayCount")),
            "likes": safe_int(item.get("likesCount") or item.get("likeCount")),
            "comments": safe_int(item.get("commentsCount") or item.get("commentCount")),
        },
        "hashtags": safe_list(item.get("hashtags")),
    }


@router.get("/details", summary="Instagram post/reel details")
async def instagram_details(
    url: str = Query(..., description="Instagram post or reel URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_instagram_shortcode(url):
        raise HTTPException(status_code=400, detail="Invalid Instagram post/reel URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/details",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_POST,
                {"directUrls": [url], "resultsLimit": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Post not found")
            return _normalize_post(items[0])

        data = await cached_or_run(
            endpoint="instagram.details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/transcript", summary="Instagram Reel transcript")
async def instagram_transcript(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_instagram_shortcode(url):
        raise HTTPException(status_code=400, detail="Invalid Instagram URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/transcript",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_REEL,
                {"directUrls": [url], "shouldDownloadSubtitles": True, "resultsLimit": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Reel not found")
            item = items[0]
            subs = item.get("subtitles") or []
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
            full = " ".join(parts) or safe_str(item.get("caption")) or ""
            if not full:
                raise HTTPException(status_code=422, detail="No transcript available")
            return {
                "platform": "instagram",
                "url": url,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
            }

        data = await cached_or_run(
            endpoint="instagram.transcript",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/summarize", summary="AI summary of Instagram Reel")
async def instagram_summarize(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/summarize",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_REEL,
                {"directUrls": [url], "shouldDownloadSubtitles": True, "resultsLimit": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Reel not found")
            item = items[0]
            subs = item.get("subtitles") or []
            parts = []
            if isinstance(subs, list):
                for s in subs:
                    text = ((s.get("text") if isinstance(s, dict) else str(s)) or "").strip()
                    if text:
                        parts.append(text)
            text = (" ".join(parts) or safe_str(item.get("caption")) or "").strip()
            if not text:
                raise HTTPException(status_code=422, detail="No content to summarize")
            ai = await summarize_transcript(text, title=safe_str(item.get("caption")))
            return {
                "platform": "instagram",
                "url": url,
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
            }

        data = await cached_or_run(
            endpoint="instagram.summarize",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Instagram post/reel comments")
async def instagram_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = max(CREDIT_COMMENTS_BASE, (limit + 99) // 100 * 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/comments",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_COMMENT,
                {"directUrls": [url], "resultsLimit": limit},
                max_items=limit,
            )
            comments = []
            for c in items[:limit]:
                comments.append(
                    {
                        "id": safe_str(c.get("id")),
                        "text": (c.get("text") or "").strip(),
                        "author": safe_str(c.get("ownerUsername") or c.get("owner", {}).get("username")),
                        "likeCount": safe_int(c.get("likesCount") or c.get("likeCount")),
                        "publishedAt": safe_str(c.get("timestamp")),
                        "replyCount": safe_int(c.get("replyCount") or c.get("repliesCount")),
                    }
                )
            return {
                "platform": "instagram",
                "url": url,
                "totalReturned": len(comments),
                "comments": comments,
            }

        data = await cached_or_run(
            endpoint="instagram.comments",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/channel-details", summary="Instagram profile info")
async def instagram_channel_details(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_instagram_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid Instagram profile URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/channel-details",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_CHANNEL,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_PROFILE,
                {"usernames": [handle]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Profile not found")
            p = items[0]
            return {
                "platform": "instagram",
                "url": f"https://instagram.com/{handle}",
                "username": safe_str(p.get("username") or handle),
                "displayName": safe_str(p.get("fullName")),
                "bio": safe_str(p.get("biography")),
                "followers": safe_int(p.get("followersCount")),
                "following": safe_int(p.get("followsCount")),
                "postCount": safe_int(p.get("postsCount")),
                "verified": p.get("verified"),
                "profileImage": safe_str(p.get("profilePicUrl") or p.get("profilePicUrlHD")),
                "externalUrl": safe_str(p.get("externalUrl")),
            }

        data = await cached_or_run(
            endpoint="instagram.channel-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/channel-posts", summary="Latest posts from an Instagram profile")
async def instagram_channel_posts(
    url: str = Query(...),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_instagram_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid profile URL")
    settings = get_settings()
    cost = max(CREDIT_CHANNEL_POSTS_BASE, (limit + 49) // 50)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/channel-posts",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM,
                {"username": [handle], "resultsLimit": limit, "resultsType": "posts"},
                max_items=limit,
            )
            posts = [_normalize_post(i) for i in items[:limit]]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="instagram.channel-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/channel-reels", summary="Latest Reels from an Instagram profile")
async def instagram_channel_reels(
    url: str = Query(...),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_instagram_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid profile URL")
    settings = get_settings()
    cost = max(CREDIT_CHANNEL_REELS_BASE, (limit + 49) // 50)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/channel-reels",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM,
                {"username": [handle], "resultsLimit": limit, "resultsType": "reels"},
                max_items=limit,
            )
            reels = [_normalize_post(i) for i in items[:limit]]
            return {"url": url, "totalReturned": len(reels), "reels": reels}

        data = await cached_or_run(
            endpoint="instagram.channel-reels",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/reels-search", summary="Search Instagram Reels by hashtag")
async def instagram_reels_search(
    q: str = Query(..., min_length=2, description="Hashtag (without #) or keyword"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/reels-search",
        platform="instagram",
        resource_url=None,
        base_credits=CREDIT_SEARCH,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            tag = q.lstrip("#")
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM,
                {
                    "directUrls": [f"https://www.instagram.com/explore/tags/{tag}/"],
                    "resultsLimit": limit,
                    "resultsType": "posts",
                },
                max_items=limit,
            )
            results = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="instagram.reels-search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/video-download", summary="Direct video URL for Instagram Reel")
async def instagram_video_download(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/video-download",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_DOWNLOAD,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_REEL,
                {"directUrls": [url], "resultsLimit": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Reel not found")
            v = items[0]
            return {
                "platform": "instagram",
                "url": url,
                "downloadUrl": safe_str(v.get("videoUrl")),
                "thumbnailUrl": safe_str(v.get("displayUrl") or v.get("thumbnailUrl")),
                "duration": safe_float(v.get("videoDuration")),
            }

        data = await cached_or_run(
            endpoint="instagram.video-download",
            params={"url": url},
            runner=_run,
            ctx=ctx,
            ttl=3600,
        )
        return ApiResponse(data=data)
