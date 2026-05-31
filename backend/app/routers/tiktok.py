"""TikTok endpoints."""

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
from app.utils.url import extract_tiktok_id, extract_tiktok_username

router = APIRouter()

CREDIT_TRANSCRIPT = 2
CREDIT_SUMMARIZE = 4
CREDIT_VIDEO_DETAILS = 1
CREDIT_COMMENTS_BASE = 2
CREDIT_CHANNEL_DETAILS = 1
CREDIT_SEARCH = 2
CREDIT_DOWNLOAD = 3
CREDIT_CHANNEL_POSTS_BASE = 2
CREDIT_REPLIES_BASE = 2
CREDIT_FOLLOWERS_BASE = 2
CREDIT_MUSIC_POSTS_BASE = 2


# Residential proxy is required for the followers/followings relationship
# scraper; without it the actor only returns error records.
TIKTOK_RESIDENTIAL_PROXY = {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}


def _is_user_record(item: dict) -> bool:
    """Keep only real relationship rows (drop error/summary records)."""
    record_type = item.get("recordType")
    if record_type and record_type != "relationship":
        return False
    if item.get("isSummary"):
        return False
    return bool(item.get("username") or item.get("uniqueId"))


def _normalize_user(item: dict) -> dict:
    """Map a raw TikTok user object (follower / following list) to our shape."""
    stats = item.get("authorStats") or item.get("stats") or {}
    username = item.get("username") or item.get("uniqueId") or item.get("name") or item.get("nickName")
    verified = item.get("isVerified")
    if verified is None:
        verified = item.get("verified")
    return {
        "username": safe_str(username),
        "displayName": safe_str(item.get("displayName") or item.get("nickname") or item.get("nickName")),
        "bio": safe_str(item.get("bio") or item.get("signature")),
        "url": safe_str(item.get("profileUrl"))
        or (f"https://www.tiktok.com/@{username}" if username else None),
        "followers": safe_int(
            item.get("followersCount")
            or stats.get("followerCount")
            or item.get("followerCount")
            or item.get("fans")
        ),
        "verified": verified,
        "profileImage": safe_str(
            item.get("profilePictureUrl") or item.get("avatarLarger") or item.get("avatar")
        ),
    }


def _normalize(item: dict) -> dict:
    """Map raw TikTok actor output to our standard shape."""
    author = item.get("authorMeta") or item.get("author") or {}
    stats = item.get("stats") or {}
    music = item.get("musicMeta") or item.get("music") or {}
    return {
        "platform": "tiktok",
        "url": safe_str(item.get("webVideoUrl") or item.get("url")),
        "id": safe_str(item.get("id") or item.get("videoId")),
        "caption": safe_str(item.get("text") or item.get("desc")),
        "description": safe_str(item.get("text") or item.get("desc")),
        "publishedAt": safe_str(item.get("createTimeISO") or item.get("createTime")),
        "durationSeconds": safe_float(item.get("videoMeta", {}).get("duration") or item.get("duration")),
        "thumbnailUrl": safe_str(item.get("videoMeta", {}).get("coverUrl") or item.get("covers", [None])[0] if item.get("covers") else None),
        "videoUrl": safe_str(item.get("videoUrl") or item.get("video", {}).get("downloadAddr")),
        "author": {
            "username": safe_str(author.get("name") or author.get("uniqueId")),
            "displayName": safe_str(author.get("nickName") or author.get("nickname")),
            "url": safe_str(author.get("profileUrl")),
            "followers": safe_int(author.get("fans") or author.get("followers")),
            "verified": author.get("verified"),
            "profileImage": safe_str(author.get("avatar") or author.get("avatarLarger")),
        },
        "engagement": {
            "views": safe_int(item.get("playCount") or stats.get("playCount")),
            "likes": safe_int(item.get("diggCount") or stats.get("diggCount")),
            "comments": safe_int(item.get("commentCount") or stats.get("commentCount")),
            "shares": safe_int(item.get("shareCount") or stats.get("shareCount")),
            "saves": safe_int(stats.get("collectCount")),
        },
        "hashtags": [h.get("name") if isinstance(h, dict) else h for h in safe_list(item.get("hashtags"))],
        "musicName": safe_str(music.get("musicName") or music.get("title")),
    }


@router.get("/video-details", summary="TikTok video metadata + stats")
async def tiktok_video_details(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    if not extract_tiktok_id(url):
        raise HTTPException(status_code=400, detail="Invalid TikTok video URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/video-details",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_VIDEO_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {"postURLs": [url], "resultsPerPage": 1, "shouldDownloadVideos": False},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            return _normalize(items[0])

        data = await cached_or_run(
            endpoint="tiktok.video-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/transcript", summary="TikTok video transcript (via auto-captions)")
async def tiktok_transcript(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/transcript",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {"postURLs": [url], "resultsPerPage": 1, "shouldDownloadSubtitles": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            item = items[0]
            subs = item.get("subtitles") or item.get("captions") or []
            segments = []
            parts = []
            for s in subs if isinstance(subs, list) else []:
                text = (s.get("text") if isinstance(s, dict) else str(s)).strip()
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
                raise HTTPException(status_code=422, detail="No transcript available for this TikTok")
            return {
                "platform": "tiktok",
                "url": url,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
            }

        data = await cached_or_run(
            endpoint="tiktok.transcript",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/summarize", summary="AI summary of a TikTok video")
async def tiktok_summarize(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/summarize",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {"postURLs": [url], "resultsPerPage": 1, "shouldDownloadSubtitles": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            item = items[0]
            text = (
                " ".join(
                    (s.get("text") if isinstance(s, dict) else "")
                    for s in (item.get("subtitles") or [])
                )
                or safe_str(item.get("text"))
                or ""
            ).strip()
            if not text:
                raise HTTPException(status_code=422, detail="No transcript/caption available")
            ai = await summarize_transcript(text, title=safe_str(item.get("text")))
            return {
                "platform": "tiktok",
                "url": url,
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
            }

        data = await cached_or_run(
            endpoint="tiktok.summarize",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="TikTok video comments")
async def tiktok_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = max(CREDIT_COMMENTS_BASE, (limit + 99) // 100 * 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/comments",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_COMMENTS,
                {"postURLs": [url], "commentsPerPost": limit},
                max_items=limit,
            )
            comments = []
            for c in items[:limit]:
                user = c.get("user") or {}
                comments.append(
                    {
                        "id": safe_str(c.get("cid") or c.get("id")),
                        "text": (c.get("text") or "").strip(),
                        "author": safe_str(user.get("uniqueId") or c.get("authorName")),
                        "likeCount": safe_int(c.get("diggCount") or c.get("likeCount")),
                        "publishedAt": safe_str(c.get("createTimeISO")),
                        "replyCount": safe_int(c.get("replyCommentTotal")),
                    }
                )
            return {
                "platform": "tiktok",
                "url": url,
                "totalReturned": len(comments),
                "comments": comments,
            }

        data = await cached_or_run(
            endpoint="tiktok.comments",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/channel-details", summary="TikTok profile / channel info")
async def tiktok_channel_details(
    url: str = Query(..., description="https://tiktok.com/@username"),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_tiktok_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid TikTok profile URL")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/channel-details",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_CHANNEL_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_PROFILE,
                {"profiles": [handle], "resultsPerPage": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Profile not found")
            p = items[0]
            stats = p.get("authorStats") or p.get("stats") or {}
            return {
                "platform": "tiktok",
                "url": url,
                "username": safe_str(p.get("uniqueId") or handle),
                "displayName": safe_str(p.get("nickname") or p.get("nickName")),
                "bio": safe_str(p.get("signature") or p.get("bio")),
                "followers": safe_int(stats.get("followerCount") or p.get("fans")),
                "following": safe_int(stats.get("followingCount")),
                "postCount": safe_int(stats.get("videoCount")),
                "verified": p.get("verified"),
                "profileImage": safe_str(p.get("avatarLarger") or p.get("avatar")),
                "externalUrl": safe_str(p.get("bioLink", {}).get("link") if isinstance(p.get("bioLink"), dict) else None),
            }

        data = await cached_or_run(
            endpoint="tiktok.channel-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/search", summary="Search TikTok videos by hashtag/keyword")
async def tiktok_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/search",
        platform="tiktok",
        resource_url=None,
        base_credits=CREDIT_SEARCH,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_SEARCH,
                {"searchQueries": [q], "resultsPerPage": limit},
                max_items=limit,
            )
            results = [_normalize(i) for i in items[:limit]]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="tiktok.search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/video-download", summary="TikTok video download URL")
async def tiktok_video_download(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/video-download",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_DOWNLOAD,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {"postURLs": [url], "shouldDownloadVideos": True, "resultsPerPage": 1},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            item = items[0]
            return {
                "platform": "tiktok",
                "url": url,
                "downloadUrl": safe_str(item.get("videoUrl") or item.get("downloadUrl")),
                "noWatermarkUrl": safe_str(item.get("videoUrlNoWaterMark")),
                "duration": safe_float(item.get("videoMeta", {}).get("duration")),
            }

        data = await cached_or_run(
            endpoint="tiktok.video-download",
            params={"url": url},
            runner=_run,
            ctx=ctx,
            ttl=3600,
        )
        return ApiResponse(data=data)


@router.get("/channel-posts", summary="Latest posts from a TikTok profile")
async def tiktok_channel_posts(
    url: str = Query(..., description="https://tiktok.com/@username"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_tiktok_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid TikTok profile URL")
    settings = get_settings()
    cost = max(CREDIT_CHANNEL_POSTS_BASE, (limit + 49) // 50)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/channel-posts",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {"profiles": [handle], "resultsPerPage": limit, "shouldDownloadVideos": False},
                max_items=limit,
            )
            posts = [_normalize(i) for i in items[:limit]]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="tiktok.channel-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/comment-replies", summary="Replies to a TikTok comment")
async def tiktok_comment_replies(
    url: str = Query(..., description="URL of the TikTok video the comment belongs to"),
    comment_id: str = Query(..., description="ID of the parent comment"),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = max(CREDIT_REPLIES_BASE, (limit + 99) // 100 * 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/comment-replies",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_COMMENTS,
                {
                    "postURLs": [url],
                    "commentsPerPost": limit,
                    "maxRepliesPerComment": limit,
                },
                max_items=limit * 4,
            )
            replies = []
            for c in items:
                parent = safe_str(
                    c.get("repliesToId")
                    or c.get("parentCommentId")
                    or c.get("replyToId")
                )
                is_reply = bool(parent) and parent == comment_id
                # Some actors nest replies under the parent comment object.
                if not is_reply and safe_str(c.get("cid") or c.get("id")) == comment_id:
                    for r in c.get("replies") or c.get("replyComments") or []:
                        user = r.get("user") or {}
                        replies.append(
                            {
                                "id": safe_str(r.get("cid") or r.get("id")),
                                "text": (r.get("text") or "").strip(),
                                "author": safe_str(user.get("uniqueId") or r.get("authorName")),
                                "likeCount": safe_int(r.get("diggCount") or r.get("likeCount")),
                                "publishedAt": safe_str(r.get("createTimeISO")),
                            }
                        )
                    continue
                if is_reply:
                    user = c.get("user") or {}
                    replies.append(
                        {
                            "id": safe_str(c.get("cid") or c.get("id")),
                            "text": (c.get("text") or "").strip(),
                            "author": safe_str(user.get("uniqueId") or c.get("authorName")),
                            "likeCount": safe_int(c.get("diggCount") or c.get("likeCount")),
                            "publishedAt": safe_str(c.get("createTimeISO")),
                        }
                    )
            return {
                "platform": "tiktok",
                "url": url,
                "commentId": comment_id,
                "totalReturned": len(replies[:limit]),
                "replies": replies[:limit],
            }

        data = await cached_or_run(
            endpoint="tiktok.comment-replies",
            params={"url": url, "comment_id": comment_id, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/user-followers", summary="List a TikTok user's followers")
async def tiktok_user_followers(
    url: str = Query(..., description="https://tiktok.com/@username"),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_tiktok_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid TikTok profile URL")
    settings = get_settings()
    cost = max(CREDIT_FOLLOWERS_BASE, (limit + 99) // 100 * 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/user-followers",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_FOLLOWERS,
                {
                    "profiles": [handle],
                    "mode": "followers",
                    "maxItemsPerProfile": limit,
                    "proxyConfiguration": TIKTOK_RESIDENTIAL_PROXY,
                },
                max_items=limit,
            )
            users = [_normalize_user(i) for i in items if _is_user_record(i)][:limit]
            return {"url": url, "totalReturned": len(users), "followers": users}

        data = await cached_or_run(
            endpoint="tiktok.user-followers",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/user-followings", summary="List who a TikTok user follows")
async def tiktok_user_followings(
    url: str = Query(..., description="https://tiktok.com/@username"),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = extract_tiktok_username(url)
    if not handle:
        raise HTTPException(status_code=400, detail="Invalid TikTok profile URL")
    settings = get_settings()
    cost = max(CREDIT_FOLLOWERS_BASE, (limit + 99) // 100 * 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/user-followings",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_FOLLOWINGS,
                {
                    "profiles": [handle],
                    "mode": "following",
                    "maxItemsPerProfile": limit,
                    "proxyConfiguration": TIKTOK_RESIDENTIAL_PROXY,
                },
                max_items=limit,
            )
            users = [_normalize_user(i) for i in items if _is_user_record(i)][:limit]
            return {"url": url, "totalReturned": len(users), "followings": users}

        data = await cached_or_run(
            endpoint="tiktok.user-followings",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/music-posts", summary="Posts using a TikTok sound/music")
async def tiktok_music_posts(
    url: str = Query(..., description="TikTok music/sound URL"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = max(CREDIT_MUSIC_POSTS_BASE, (limit + 49) // 50)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/music-posts",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_MUSIC,
                {"musics": [url], "resultsPerPage": limit, "shouldDownloadVideos": False},
                max_items=limit,
            )
            posts = [_normalize(i) for i in items[:limit]]
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="tiktok.music-posts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)
