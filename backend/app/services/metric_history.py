"""Automatic metric time-series recording.

Every cache-miss fetch of a tracked endpoint stores its countable metrics
(followers, views, likes, ...) into `metric_history`, building follower/
engagement growth curves as a free by-product of normal API usage. Served
back via GET /v1/history. Recording is fire-and-forget and never blocks or
fails the request.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog

from app.services.supabase_client import get_supabase

log = structlog.get_logger(__name__)

# cached_or_run endpoint names worth a time series (profile + post metrics).
TRACKED_ENDPOINTS: frozenset[str] = frozenset(
    {
        "youtube.channel-details",
        "youtube.video-details",
        "tiktok.channel-details",
        "tiktok.video-details",
        "instagram.channel-details",
        "instagram.details",
        "facebook.page-details",
        "facebook.details",
        "twitter.profile",
        "twitter.tweet-details",
        "reddit.subreddit-details",
        "reddit.post-details",
        "threads.profile",
        "bluesky.profile",
        "linkedin.profile",
        "linkedin.post-details",
        "pinterest.pin-details",
        "rumble.video-details",
    }
)

METRIC_KEYS: frozenset[str] = frozenset(
    {
        "followers", "followersCount", "followerCount", "subscribers", "subscriberCount",
        "following", "followingCount", "friends", "friendsCount",
        "likes", "likeCount", "likesCount", "hearts", "heartCount",
        "views", "viewCount", "viewsCount", "plays", "playCount",
        "videos", "videoCount", "videosCount", "posts", "postCount", "postsCount",
        "members", "memberCount", "subscribersActive", "activeUserCount",
        "comments", "commentCount", "commentsCount",
        "shares", "shareCount", "sharesCount", "retweets", "retweetCount",
        "replies", "replyCount", "quotes", "quoteCount", "bookmarks", "bookmarkCount",
        "upvotes", "score", "upvoteRatio",
        "tweets", "tweetCount", "statusesCount", "mediaCount",
        "pins", "pinCount", "boards", "boardCount", "saves", "saveCount",
        "monthlyListeners", "listeners", "stars", "forks", "repos", "publicRepos",
    }
)

DEDUPE_HOURS = 6


def extract_metrics(data: Any) -> dict[str, float]:
    """Collect numeric metric fields from the top level and one nested level."""
    if not isinstance(data, dict):
        return {}
    out: dict[str, float] = {}

    def take(source: dict[str, Any]) -> None:
        for key, val in source.items():
            if key in METRIC_KEYS and isinstance(val, (int, float)) and not isinstance(val, bool):
                out.setdefault(key, val)

    take(data)
    for val in data.values():
        if isinstance(val, dict):
            take(val)
    return out


def _record_sync(endpoint: str, resource: str, metrics: dict[str, float]) -> None:
    sb = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=DEDUPE_HOURS)).isoformat()
    recent = (
        sb.table("metric_history")
        .select("id")
        .eq("endpoint", endpoint)
        .eq("resource", resource)
        .gte("captured_at", cutoff)
        .limit(1)
        .execute()
    )
    if recent.data:
        return
    sb.table("metric_history").insert(
        {"endpoint": endpoint, "resource": resource, "metrics": metrics}
    ).execute()


async def _record(endpoint: str, resource: str, metrics: dict[str, float]) -> None:
    try:
        await asyncio.to_thread(_record_sync, endpoint, resource, metrics)
    except Exception as exc:  # noqa: BLE001 -- table missing or transient DB error
        log.info("metric_history_skip", endpoint=endpoint, error=str(exc)[:200])


def maybe_record(endpoint: str, params: dict[str, Any], result: Any) -> None:
    """Schedule a history write for tracked endpoints. Never raises."""
    if endpoint not in TRACKED_ENDPOINTS:
        return
    resource = None
    for key in ("url", "username", "handle", "user", "q"):
        val = params.get(key)
        if isinstance(val, str) and val.strip():
            resource = val.strip()
            break
    if not resource:
        return
    metrics = extract_metrics(result)
    if not metrics:
        return
    try:
        asyncio.get_running_loop().create_task(_record(endpoint, resource, metrics))
    except RuntimeError:
        pass  # no running loop (sync/test context) -- skip silently
