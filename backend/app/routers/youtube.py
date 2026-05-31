"""YouTube + YouTube Shorts endpoints."""

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
from app.utils.formatters import safe_int, safe_list, safe_str
from app.utils.url import (
    extract_youtube_id,
    normalize_youtube_url,
)

router = APIRouter()

CREDIT_TRANSCRIPT = 1
CREDIT_SUMMARIZE = 3
CREDIT_VIDEO_DETAILS = 1
CREDIT_CHANNEL_DETAILS = 1
CREDIT_DOWNLOAD = 5

# YouTube list endpoints hit per-result Apify actors:
#   streamers/youtube-scraper          $2.40/1k with an Apify sub, $5/1k without
#   streamers/youtube-comments-scraper $0.90/1k results (comments)
# RATE_YT_VIDEO=1.2 stays profitable even at the no-subscription $5/1k price
# (1.2 x $0.0045 = $0.0054 > $0.005); with an Apify sub the margin is ~80%+.
# Charged via ctx["credits_override"] on the actual item count returned.
RATE_YT_VIDEO = 1.2
RATE_YT_COMMENTS = 0.4


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    return max(minimum, math.ceil(n * rate))


def _channel_tab_url(url: str, tab: str) -> str:
    """Build a channel sub-tab URL (videos / shorts / streams)."""
    base = (url or "").rstrip("/")
    for suffix in ("/videos", "/shorts", "/streams", "/featured"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}/{tab}"


def _video_card(v: dict) -> dict:
    return {
        "url": safe_str(v.get("url") or v.get("videoUrl")),
        "title": safe_str(v.get("title")) or "",
        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
        "durationSeconds": safe_int(v.get("duration")),
        "thumbnailUrl": safe_str(v.get("thumbnailUrl")),
        "channelName": safe_str(v.get("channelName") or v.get("channel")),
    }


# ---------- helpers -------------------------------------------------------
def _require_youtube_url(url: str) -> tuple[str, str]:
    vid = extract_youtube_id(url)
    if not vid:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    return vid, normalize_youtube_url(url)


# ---------- TRANSCRIPT ----------------------------------------------------
@router.get(
    "/transcript",
    summary="Get YouTube video transcript",
    description=f"Returns the full transcript with timestamps. Costs {CREDIT_TRANSCRIPT} credit.",
)
async def youtube_transcript(
    url: str = Query(..., description="YouTube video URL"),
    language: str | None = Query(None, description="ISO language code (en, tr, es...)"),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/transcript",
        platform="youtube",
        resource_url=norm_url,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            run_input: dict[str, Any] = {"videoUrl": norm_url}
            if language:
                run_input["language"] = language
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_TRANSCRIPT, run_input, max_items=1
            )
            if not items:
                raise HTTPException(status_code=404, detail="Transcript not available")
            item = items[0]
            segments_raw = item.get("data") or item.get("transcript") or item.get("segments") or []
            segments = []
            text_parts = []
            for s in segments_raw:
                text = (s.get("text") or "").strip()
                start = float(s.get("start") or s.get("offset") or 0.0)
                duration = float(s.get("duration") or s.get("dur") or 0.0)
                mm = int(start // 60)
                ss = int(start % 60)
                if text:
                    segments.append(
                        {
                            "text": text,
                            "start": start,
                            "duration": duration,
                            "timestamp": f"{mm:02d}:{ss:02d}",
                        }
                    )
                    text_parts.append(text)
            full = " ".join(text_parts)
            return {
                "url": norm_url,
                "videoId": vid,
                "title": safe_str(item.get("title")),
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
                "language": safe_str(item.get("language") or language),
            }

        data = await cached_or_run(
            endpoint="youtube.transcript",
            params={"url": norm_url, "language": language or ""},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


# ---------- SUMMARIZE -----------------------------------------------------
@router.get(
    "/summarize",
    summary="AI summary of a YouTube video",
    description=f"Transcript + GPT summary. Costs {CREDIT_SUMMARIZE} credits.",
)
async def youtube_summarize(
    url: str = Query(...),
    language: str | None = Query(None),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/summarize",
        platform="youtube",
        resource_url=norm_url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            tx_items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_TRANSCRIPT,
                {"videoUrl": norm_url},
                max_items=1,
            )
            if not tx_items:
                raise HTTPException(status_code=404, detail="Transcript not available")
            item = tx_items[0]
            title = safe_str(item.get("title")) or ""
            seg_raw = item.get("data") or item.get("transcript") or item.get("segments") or []
            transcript_text = " ".join(
                (s.get("text") or "").strip() for s in seg_raw
            ).strip()
            if not transcript_text:
                raise HTTPException(status_code=422, detail="Empty transcript")

            ai = await summarize_transcript(
                transcript_text, title=title, language=language or "en"
            )
            return {
                "url": norm_url,
                "videoId": vid,
                "title": title or None,
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
            }

        data = await cached_or_run(
            endpoint="youtube.summarize",
            params={"url": norm_url, "language": language or ""},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


# ---------- VIDEO DETAILS -------------------------------------------------
@router.get("/video-details", summary="YouTube video metadata + stats")
async def youtube_video_details(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/video-details",
        platform="youtube",
        resource_url=norm_url,
        base_credits=CREDIT_VIDEO_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            run_input = {"startUrls": [{"url": norm_url}], "maxResults": 1}
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_VIDEO, run_input, max_items=1
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not found")
            v = items[0]
            return {
                "url": norm_url,
                "id": vid,
                "title": safe_str(v.get("title")) or "",
                "description": safe_str(v.get("description") or v.get("text")),
                "channelName": safe_str(v.get("channelName") or v.get("channel")),
                "channelId": safe_str(v.get("channelId") or v.get("authorId")),
                "channelUrl": safe_str(v.get("channelUrl")),
                "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                "durationSeconds": safe_int(v.get("duration") or v.get("durationSeconds")),
                "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                "likeCount": safe_int(v.get("likes") or v.get("likeCount")),
                "commentCount": safe_int(v.get("commentsCount") or v.get("commentCount")),
                "thumbnailUrl": safe_str(v.get("thumbnailUrl") or (v.get("thumbnails") or [{}])[-1].get("url")),
                "tags": safe_list(v.get("tags")),
            }

        data = await cached_or_run(
            endpoint="youtube.video-details",
            params={"url": norm_url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


# ---------- COMMENTS ------------------------------------------------------
@router.get("/comments", summary="YouTube video comments (paginated)")
async def youtube_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_COMMENTS, 2)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/comments",
        platform="youtube",
        resource_url=norm_url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_COMMENTS,
                {"startUrls": [{"url": norm_url}], "maxComments": limit},
                max_items=limit,
            )
            comments = []
            for c in items[:limit]:
                comments.append(
                    {
                        "id": safe_str(c.get("cid") or c.get("commentId") or c.get("id")),
                        "author": safe_str(c.get("author") or c.get("authorName")),
                        "text": (
                            c.get("comment")
                            or c.get("text")
                            or c.get("content")
                            or ""
                        ).strip(),
                        "likeCount": safe_int(
                            c.get("voteCount") or c.get("votes") or c.get("likeCount")
                        ),
                        "publishedAt": safe_str(
                            c.get("publishedAt") or c.get("publishedTimeText")
                        ),
                        "replyCount": safe_int(
                            c.get("replyCount") or c.get("replies")
                        ),
                    }
                )
            return {
                "url": norm_url,
                "videoId": vid,
                "totalReturned": len(comments),
                "comments": comments,
            }

        data = await cached_or_run(
            endpoint="youtube.comments",
            params={"url": norm_url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["comments"]), RATE_YT_COMMENTS, 2)
        return ApiResponse(data=data)


# ---------- CHANNEL DETAILS -----------------------------------------------
@router.get("/channel-details", summary="YouTube channel info & stats")
async def youtube_channel_details(
    url: str = Query(..., description="Channel URL (youtube.com/@handle or /channel/UC...)"),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-details",
        platform="youtube",
        resource_url=url,
        base_credits=CREDIT_CHANNEL_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_CHANNEL,
                {"startUrls": [{"url": url}]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Channel not found")
            c = items[0]
            return {
                "url": url,
                "id": safe_str(c.get("channelId") or c.get("id")),
                "name": safe_str(c.get("channelName") or c.get("name")) or "",
                "description": safe_str(c.get("channelDescription") or c.get("description")),
                "subscriberCount": safe_int(c.get("subscriberCount") or c.get("numberOfSubscribers")),
                "videoCount": safe_int(c.get("videosCount") or c.get("videoCount")),
                "viewCount": safe_int(c.get("viewCount") or c.get("totalViews")),
                "thumbnailUrl": safe_str(c.get("avatarUrl") or c.get("thumbnailUrl")),
                "bannerUrl": safe_str(c.get("bannerUrl")),
                "country": safe_str(c.get("country")),
            }

        data = await cached_or_run(
            endpoint="youtube.channel-details",
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


# ---------- CHANNEL VIDEOS ------------------------------------------------
@router.get("/channel-videos", summary="List videos for a YouTube channel")
async def youtube_channel_videos(
    url: str = Query(...),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-videos",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": url}], "maxResults": limit},
                max_items=limit,
            )
            videos = []
            for v in items[:limit]:
                videos.append(
                    {
                        "url": safe_str(v.get("url") or v.get("videoUrl")),
                        "title": safe_str(v.get("title")) or "",
                        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                        "durationSeconds": safe_int(v.get("duration")),
                        "thumbnailUrl": safe_str(v.get("thumbnailUrl")),
                    }
                )
            return {"url": url, "totalReturned": len(videos), "videos": videos}

        data = await cached_or_run(
            endpoint="youtube.channel-videos",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["videos"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- PLAYLIST VIDEOS -----------------------------------------------
@router.get("/playlist-videos", summary="List videos in a YouTube playlist")
async def youtube_playlist_videos(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)

    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/playlist-videos",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": url}], "maxResults": limit, "type": "playlist"},
                max_items=limit,
            )
            videos = []
            for v in items[:limit]:
                videos.append(
                    {
                        "url": safe_str(v.get("url")),
                        "title": safe_str(v.get("title")) or "",
                        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                        "durationSeconds": safe_int(v.get("duration")),
                        "channelName": safe_str(v.get("channelName") or v.get("channel")),
                    }
                )
            return {"url": url, "totalReturned": len(videos), "videos": videos}

        data = await cached_or_run(
            endpoint="youtube.playlist-videos",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["videos"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- SEARCH --------------------------------------------------------
@router.get("/search", summary="Search YouTube videos by keyword")
async def youtube_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/search",
        platform="youtube",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"searchQueries": [q], "maxResults": limit, "maxResultsShorts": 0},
                max_items=limit,
            )
            results = []
            for v in items[:limit]:
                results.append(
                    {
                        "url": safe_str(v.get("url") or v.get("videoUrl")),
                        "title": safe_str(v.get("title")) or "",
                        "channelName": safe_str(v.get("channelName") or v.get("channel")),
                        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
                        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
                        "thumbnailUrl": safe_str(v.get("thumbnailUrl")),
                        "durationSeconds": safe_int(v.get("duration")),
                    }
                )
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="youtube.search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


# ---------- VIDEO DOWNLOAD ------------------------------------------------
@router.get("/video-download", summary="Get direct video download URLs")
async def youtube_video_download(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    vid, norm_url = _require_youtube_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/video-download",
        platform="youtube",
        resource_url=norm_url,
        base_credits=CREDIT_DOWNLOAD,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_DOWNLOAD,
                {"urls": [norm_url], "format": "all", "ttl": "none"},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Video not available")
            v = items[0]
            formats_raw = v.get("formats") or v.get("downloads") or []
            return {
                "url": norm_url,
                "videoId": vid,
                "title": safe_str(v.get("title")),
                "downloadUrl": safe_str(
                    v.get("downloadUrl")
                    or v.get("url")
                    or v.get("mediaUrl")
                    or (formats_raw[0].get("url") if formats_raw else None)
                ),
                "formats": formats_raw,
                "expiresAt": safe_str(v.get("expiresAt")),
            }

        data = await cached_or_run(
            endpoint="youtube.video-download",
            params={"url": norm_url},
            runner=_run,
            ctx=ctx,
            ttl=3600,
        )
        return ApiResponse(data=data)


# ---------- SHORTS (alias to same actors with Short URL handling) ---------
@router.get("/channel-shorts", summary="List Shorts for a YouTube channel")
async def youtube_channel_shorts(
    url: str = Query(..., description="Channel URL (youtube.com/@handle)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-shorts",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": _channel_tab_url(url, "shorts")}], "maxResults": limit},
                max_items=limit,
            )
            shorts = [_video_card(v) for v in items[:limit]]
            return {"url": url, "totalReturned": len(shorts), "shorts": shorts}

        data = await cached_or_run(
            endpoint="youtube.channel-shorts",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["shorts"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/channel-streams", summary="List live/past streams for a YouTube channel")
async def youtube_channel_streams(
    url: str = Query(..., description="Channel URL (youtube.com/@handle)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/channel-streams",
        platform="youtube",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": _channel_tab_url(url, "streams")}], "maxResults": limit},
                max_items=limit,
            )
            streams = [_video_card(v) for v in items[:limit]]
            return {"url": url, "totalReturned": len(streams), "streams": streams}

        data = await cached_or_run(
            endpoint="youtube.channel-streams",
            params={"url": url, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["streams"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/hashtag-search", summary="Search YouTube videos by hashtag")
async def youtube_hashtag_search(
    q: str = Query(..., min_length=2, description="Hashtag (with or without #)"),
    limit: int = Query(20, ge=1, le=200),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_YT_VIDEO, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/youtube/hashtag-search",
        platform="youtube",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            tag = q.lstrip("#")
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {
                    "startUrls": [{"url": f"https://www.youtube.com/hashtag/{tag}"}],
                    "maxResults": limit,
                },
                max_items=limit,
            )
            results = [_video_card(v) for v in items[:limit]]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="youtube.hashtag-search",
            params={"q": q, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_YT_VIDEO, 2)
        return ApiResponse(data=data)


@router.get("/shorts/transcript", summary="YouTube Shorts transcript")
async def shorts_transcript(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_transcript(url=url, language=None, caller=caller)


@router.get("/shorts/summarize", summary="YouTube Shorts AI summary")
async def shorts_summarize(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_summarize(url=url, language=None, caller=caller)


@router.get("/shorts/video-details", summary="YouTube Shorts metadata")
async def shorts_details(
    url: str = Query(...),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_video_details(url=url, caller=caller)


@router.get("/shorts/comments", summary="YouTube Shorts comments")
async def shorts_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    caller: ApiCaller = Depends(require_api_key),
):
    return await youtube_comments(url=url, limit=limit, caller=caller)
