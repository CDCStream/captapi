"""Instagram endpoints (Reels, Posts, Profiles)."""

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
from app.utils.formatters import safe_float, safe_int, safe_list, safe_str
from app.utils.url import extract_instagram_shortcode, extract_instagram_username

router = APIRouter()

CREDIT_TRANSCRIPT = 2
CREDIT_SUMMARIZE = 4
CREDIT_DETAILS = 1
CREDIT_CHANNEL = 1
CREDIT_SEARCH = 2
CREDIT_DOWNLOAD = 3

# Per-result rates calibrated to ~80% markup (rate = cost_per_result * 400 at a
# $0.0045/credit sell price) over verified Apify prices:
#   apify/instagram-scraper          $1.50/1k ($0.0015) -> posts/reels/search
#   apify/instagram-comment-scraper  $2.30/1k ($0.0023) -> comments
#   apify/instagram-tagged-scraper / reels-audio ~$0.0023 -> tagged / music
# Charged via ctx["credits_override"] on the actual item count.
RATE_IG_POSTS = 0.6
RATE_IG_RICH = 0.9


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    return max(minimum, math.ceil(n * rate))


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


def _normalize_audio_reel(item: dict) -> dict:
    """Map the reels-by-audio scraper output (capitalized keys) to our shape."""
    author = item.get("author") or {}
    username = author.get("username")
    return {
        "platform": "instagram",
        "url": safe_str(item.get("URL") or item.get("url")),
        "id": safe_str(item.get("Id") or item.get("id")),
        "caption": safe_str(item.get("caption")),
        "description": safe_str(item.get("caption")),
        "publishedAt": safe_str(item.get("postedAt")),
        "durationSeconds": safe_float(item.get("videoDuration")),
        "thumbnailUrl": safe_str(author.get("temporaryProfilePictureUrl")),
        "videoUrl": safe_str(item.get("videoTemporaryUrl") or item.get("storedVideoUrl")),
        "author": {
            "username": safe_str(username),
            "displayName": safe_str(author.get("fullname")),
            "url": f"https://instagram.com/{username}" if username else None,
            "followers": None,
            "verified": author.get("isVerified"),
            "profileImage": safe_str(author.get("temporaryProfilePictureUrl")),
        },
        "engagement": {
            "views": safe_int(item.get("playCount")),
            "likes": safe_int(item.get("likeCount")),
            "comments": safe_int(item.get("commentCount")),
        },
        "musicId": safe_str(item.get("musicId")),
        "musicUrl": safe_str(item.get("musicUrl")),
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
    cost = _scaled_credits(limit, RATE_IG_RICH, 2)
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
        ctx["credits_override"] = _scaled_credits(len(data["comments"]), RATE_IG_RICH, 2)
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
    cost = _scaled_credits(limit, RATE_IG_POSTS, 2)
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
                {
                    "directUrls": [f"https://www.instagram.com/{handle}/"],
                    "resultsLimit": limit,
                    "resultsType": "posts",
                },
                max_items=limit,
            )
            posts = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="instagram.channel-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_IG_POSTS, 2)
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
    cost = _scaled_credits(limit, RATE_IG_POSTS, 2)
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
                {
                    "directUrls": [f"https://www.instagram.com/{handle}/"],
                    "resultsLimit": limit,
                    "resultsType": "reels",
                },
                max_items=limit,
            )
            reels = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
            return {"url": url, "totalReturned": len(reels), "reels": reels}

        data = await cached_or_run(
            endpoint="instagram.channel-reels",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["reels"]), RATE_IG_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/reels-search", summary="Search Instagram Reels by hashtag")
async def instagram_reels_search(
    q: str = Query(..., min_length=2, description="Hashtag (without #) or keyword"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/reels-search",
        platform="instagram",
        resource_url=None,
        base_credits=cost,
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
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_IG_POSTS, CREDIT_SEARCH)
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


@router.get("/tagged-posts", summary="Posts an Instagram user is tagged in")
async def instagram_tagged_posts(
    url: str = Query(..., description="Instagram profile URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_instagram_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid profile URL")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_RICH, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/tagged-posts",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_TAGGED,
                {"username": [handle], "resultsLimit": limit},
                max_items=limit,
            )
            posts = [_normalize_post(i) for i in items[:limit] if not i.get("error")]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="instagram.tagged-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_IG_RICH, 2)
        return ApiResponse(data=data)


@router.get("/music-posts", summary="Posts/Reels using an Instagram audio")
async def instagram_music_posts(
    url: str = Query(..., description="Instagram audio/music page URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_RICH, 3)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/music-posts",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_AUDIO,
                {"audioUrls": [url], "maxResults": limit, "downloadVideos": False},
                max_items=limit,
            )
            posts = [
                _normalize_audio_reel(i)
                for i in items[:limit]
                if not i.get("error")
            ]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="instagram.music-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_IG_RICH, 3)
        return ApiResponse(data=data)


@router.get("/hashtag-search", summary="Search Instagram posts by hashtag")
async def instagram_hashtag_search(
    q: str = Query(..., min_length=2, description="Hashtag (without #)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/hashtag-search",
        platform="instagram",
        resource_url=None,
        base_credits=cost,
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
            endpoint="instagram.hashtag-search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_IG_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


def _normalize_ig_profile(item: dict) -> dict:
    username = item.get("username") or item.get("ownerUsername")
    return {
        "username": safe_str(username),
        "displayName": safe_str(item.get("fullName") or item.get("ownerFullName")),
        "url": f"https://instagram.com/{username}" if username else None,
        "followers": safe_int(item.get("followersCount")),
        "verified": item.get("verified") or item.get("isVerified"),
        "private": item.get("private") or item.get("isPrivate"),
        "profileImage": safe_str(item.get("profilePicUrl")),
    }


@router.get("/profile-search", summary="Search Instagram profiles by keyword")
async def instagram_profile_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/profile-search",
        platform="instagram",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM,
                {"search": q, "searchType": "user", "searchLimit": limit, "resultsType": "details"},
                max_items=limit,
            )
            users = [_normalize_ig_profile(i) for i in items[:limit] if i.get("username") or i.get("ownerUsername")]
            return {"query": q, "totalReturned": len(users), "users": users}

        data = await cached_or_run(
            endpoint="instagram.profile-search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["users"]), RATE_IG_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


def _highlight_payload(item: dict) -> dict:
    return {
        "id": safe_str(item.get("id") or item.get("highlightId")),
        "title": safe_str(item.get("title") or item.get("name")),
        "coverUrl": safe_str(item.get("coverUrl") or item.get("cover") or item.get("coverMediaUrl")),
        "itemCount": safe_int(item.get("itemCount") or item.get("mediaCount")),
    }


@router.get("/story-highlights", summary="List an Instagram profile's story highlights")
async def instagram_story_highlights(
    url: str = Query(..., description="Instagram profile URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_instagram_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid profile URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/story-highlights",
        platform="instagram",
        resource_url=url,
        base_credits=CREDIT_CHANNEL + 4,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_HIGHLIGHTS,
                {
                    "usernames": [handle],
                    "includeStories": False,
                    "includeHighlights": True,
                    "expandHighlightItems": False,
                },
                max_items=1,
            )
            highlights: list[dict[str, Any]] = []
            for row in items:
                raw = row.get("highlights") or row.get("highlightsList") or []
                if isinstance(raw, list):
                    highlights.extend(_highlight_payload(h) for h in raw if isinstance(h, dict))
            return {"url": url, "totalReturned": len(highlights), "highlights": highlights}

        data = await cached_or_run(
            endpoint="instagram.story-highlights",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/highlights-details", summary="Items inside an Instagram profile's highlights")
async def instagram_highlights_details(
    url: str = Query(..., description="Instagram profile URL"),
    limit: int = Query(10, ge=1, le=50, description="Max highlights to expand"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_instagram_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid profile URL")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_IG_RICH, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/highlights-details",
        platform="instagram",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_INSTAGRAM_HIGHLIGHTS,
                {
                    "usernames": [handle],
                    "includeStories": False,
                    "includeHighlights": True,
                    "expandHighlightItems": True,
                    "maxHighlightsPerUser": limit,
                },
                max_items=limit,
            )
            highlights: list[dict[str, Any]] = []
            for row in items:
                raw = row.get("highlights") or row.get("highlightsList") or []
                if not isinstance(raw, list):
                    continue
                for h in raw:
                    if not isinstance(h, dict):
                        continue
                    payload = _highlight_payload(h)
                    media = h.get("items") or h.get("media") or []
                    payload["items"] = [
                        {
                            "type": safe_str(m.get("type") or m.get("mediaType")),
                            "url": safe_str(m.get("url") or m.get("mediaUrl") or m.get("videoUrl") or m.get("imageUrl")),
                            "thumbnailUrl": safe_str(m.get("thumbnailUrl") or m.get("displayUrl")),
                            "takenAt": safe_str(m.get("takenAt") or m.get("timestamp")),
                        }
                        for m in (media if isinstance(media, list) else [])
                        if isinstance(m, dict)
                    ]
                    highlights.append(payload)
            return {"url": url, "totalReturned": len(highlights), "highlights": highlights}

        data = await cached_or_run(
            endpoint="instagram.highlights-details",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["highlights"]), RATE_IG_RICH, 5)
        return ApiResponse(data=data)


@router.get("/embed", summary="Embed HTML for an Instagram post/reel")
async def instagram_embed(
    url: str = Query(..., description="Instagram post or reel URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    shortcode = extract_instagram_shortcode(url)
    if not shortcode:
        raise HTTPException(status_code=400, detail="Invalid Instagram post/reel URL")
    # Pure string build — no Apify call, so this is a flat 1-credit endpoint.
    async with billed_call(
        caller=caller,
        endpoint="/v1/instagram/embed",
        platform="instagram",
        resource_url=url,
        base_credits=1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            permalink = f"https://www.instagram.com/p/{shortcode}/"
            html = (
                '<blockquote class="instagram-media" '
                f'data-instgrm-permalink="{permalink}" data-instgrm-version="14"></blockquote>'
                '<script async src="//www.instagram.com/embed.js"></script>'
            )
            return {
                "platform": "instagram",
                "url": url,
                "shortcode": shortcode,
                "permalink": permalink,
                "html": html,
            }

        data = await cached_or_run(
            endpoint="instagram.embed",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)
