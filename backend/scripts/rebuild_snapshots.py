"""Rebuild api_snapshots.json entries for endpoints whose mappings were fixed.

Runs the same Apify actors the endpoints use and feeds raw items through the
routers' own (fixed) normalize helpers, so the refreshed docs examples are
exactly what production will return after deploy. Then regenerates
frontend/lib/api-examples.generated.ts via gen_examples.py.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.core.config import get_settings  # noqa: E402
from app.routers.facebook import _normalize_post as fb_post  # noqa: E402
from app.routers.facebook import _fb_username_from_url, _is_reel  # noqa: E402
from app.routers.instagram import _normalize_post as ig_post  # noqa: E402
from app.routers.tiktok import _normalize as tt_video  # noqa: E402
from app.routers.youtube import _duration_seconds  # noqa: E402
from app.services.apify_client import ApifyClient  # noqa: E402
from app.utils.formatters import safe_float, safe_int, safe_list, safe_str  # noqa: E402

settings = get_settings()
client = ApifyClient()

TT_PROFILE_URL = "https://www.tiktok.com/@khaby.lame"
TT_VIDEO_URL = "https://www.tiktok.com/@khaby.lame/video/7646812028874673439"
YT_CHANNEL_URL = "https://www.youtube.com/@MrBeast"
FB_PAGE_URL = "https://www.facebook.com/NASA"
FB_POST_URL = "https://www.facebook.com/NASA/posts/pfbid02skzNsrLf5atYZfzvzHAK9gHwDnZC5u4pDZMLQ1u3iJmfoA8tNsGpT7Uj6WPs6K3Rl"
IG_POST_URL = "https://www.instagram.com/p/DZFqdAxlkUG/"
IG_PROFILE_URL = "https://www.instagram.com/natgeo/"


async def actor(actor_id: str, run_input: dict, max_items: int) -> list[dict]:
    try:
        return await client.run_actor_sync(actor_id, run_input, max_items=max_items)
    except Exception as exc:  # noqa: BLE001
        print(f"ACTOR FAIL {actor_id}: {type(exc).__name__}: {exc}")
        return []


# --- payload builders (mirror endpoint return shapes) -----------------------

def tt_channel_details_payload(items: list[dict]) -> dict | None:
    if not items:
        return None
    p = items[0]
    a = p.get("authorMeta") or p
    stats = p.get("authorStats") or p.get("stats") or {}
    bio_link = a.get("bioLink")
    if isinstance(bio_link, dict):
        bio_link = bio_link.get("link")
    return {
        "platform": "tiktok",
        "url": safe_str(a.get("profileUrl")) or TT_PROFILE_URL,
        "username": safe_str(a.get("name") or a.get("uniqueId")),
        "displayName": safe_str(a.get("nickName") or a.get("nickname")),
        "bio": safe_str(a.get("signature") or a.get("bio")),
        "followers": safe_int(a.get("fans") or stats.get("followerCount")),
        "following": safe_int(a.get("following") or stats.get("followingCount")),
        "likes": safe_int(a.get("heart") or stats.get("heartCount")),
        "postCount": safe_int(a.get("video") or stats.get("videoCount")),
        "verified": a.get("verified"),
        "private": a.get("privateAccount"),
        "profileImage": safe_str(a.get("avatar") or a.get("avatarLarger") or a.get("originalAvatarUrl")),
        "externalUrl": safe_str(bio_link),
        "category": safe_str((a.get("commerceUserInfo") or {}).get("category")),
    }


def tt_download_payload(items: list[dict]) -> dict | None:
    if not items:
        return None
    item = items[0]
    video_meta = item.get("videoMeta") or {}
    media_urls = safe_list(item.get("mediaUrls"))
    download_url = safe_str(
        video_meta.get("downloadAddr")
        or (media_urls[0] if media_urls else None)
        or item.get("videoUrl")
        or item.get("downloadUrl")
    )
    if not download_url:
        return None
    return {
        "platform": "tiktok",
        "url": TT_VIDEO_URL,
        "downloadUrl": download_url,
        "noWatermarkUrl": safe_str(item.get("videoUrlNoWaterMark")) or download_url,
        "duration": safe_float(video_meta.get("duration")),
    }


def tt_comments_payload(items: list[dict]) -> dict | None:
    if not items:
        return None
    comments = []
    for c in items[:10]:
        user = c.get("user") or {}
        comments.append(
            {
                "id": safe_str(c.get("cid") or c.get("id")),
                "text": (c.get("text") or "").strip(),
                "author": safe_str(c.get("uniqueId") or user.get("uniqueId") or c.get("authorName")),
                "authorAvatarUrl": safe_str(c.get("avatarThumbnail") or user.get("avatarThumb")),
                "likeCount": safe_int(c.get("diggCount") or c.get("likeCount")) or 0,
                "publishedAt": safe_str(c.get("createTimeISO")),
                "replyCount": safe_int(c.get("replyCommentTotal")) or 0,
            }
        )
    return {"platform": "tiktok", "url": TT_VIDEO_URL, "totalReturned": len(comments), "comments": comments}


def yt_channel_details_payload(items: list[dict]) -> dict | None:
    if not items:
        return None
    c = items[0]
    links = [
        {"text": safe_str(link.get("text")), "url": safe_str(link.get("url"))}
        for link in safe_list(c.get("channelDescriptionLinks"))
        if isinstance(link, dict) and link.get("url")
    ]
    return {
        "url": safe_str(c.get("channelUrl")) or YT_CHANNEL_URL,
        "id": safe_str(c.get("channelId") or c.get("id")),
        "name": safe_str(c.get("channelName") or c.get("name")) or "",
        "handle": safe_str(c.get("channelUsername")),
        "description": safe_str(c.get("channelDescription") or c.get("description")),
        "subscriberCount": safe_int(c.get("subscriberCount") or c.get("numberOfSubscribers")),
        "videoCount": safe_int(c.get("channelTotalVideos") or c.get("videosCount") or c.get("videoCount")),
        "viewCount": safe_int(c.get("channelTotalViews") or c.get("viewCount") or c.get("totalViews")),
        "thumbnailUrl": safe_str(c.get("channelAvatarUrl") or c.get("avatarUrl") or c.get("thumbnailUrl")),
        "bannerUrl": safe_str(c.get("channelBannerUrl") or c.get("bannerUrl")),
        "country": safe_str(c.get("channelLocation") or c.get("country")),
        "joinedDate": safe_str(c.get("channelJoinedDate")),
        "verified": c.get("isChannelVerified"),
        "links": links,
    }


def yt_video_row(v: dict) -> dict:
    return {
        "url": safe_str(v.get("url") or v.get("videoUrl")),
        "title": safe_str(v.get("title")) or "",
        "publishedAt": safe_str(v.get("date") or v.get("publishedAt")),
        "viewCount": safe_int(v.get("viewCount") or v.get("views")),
        "durationSeconds": _duration_seconds(v.get("duration") or v.get("lengthSeconds")),
        "thumbnailUrl": safe_str(v.get("thumbnailUrl")),
    }


def fb_page_details_payload(items: list[dict]) -> dict | None:
    if not items:
        return None
    p = items[0]
    verified = p.get("verified") or p.get("isPageVerified")
    if verified is None and (p.get("confirmed_owner") or p.get("CONFIRMED_OWNER_LABEL")):
        verified = True
    return {
        "platform": "facebook",
        "url": safe_str(p.get("pageUrl") or p.get("facebookUrl")) or FB_PAGE_URL,
        "username": safe_str(
            p.get("pageUsername") or p.get("username") or _fb_username_from_url(p.get("pageUrl") or p.get("facebookUrl"))
        ),
        "displayName": safe_str(p.get("pageName") or p.get("title")),
        "fullName": safe_str(p.get("title")),
        "bio": safe_str(p.get("intro") or p.get("about")),
        "followers": safe_int(p.get("followersCount") or p.get("followers")),
        "following": safe_int(p.get("followings")),
        "likes": safe_int(p.get("likesCount") or p.get("likes")),
        "verified": verified,
        "profileImage": safe_str(p.get("profilePictureUrl") or p.get("profilePicUrl")),
        "coverImage": safe_str(p.get("coverPhotoUrl")),
        "category": safe_str(p.get("category")),
        "website": safe_str(p.get("website")),
        "email": safe_str(p.get("email")),
        "createdAt": safe_str(p.get("creation_date")),
    }


def fb_comments_payload(items: list[dict]) -> dict | None:
    if not items:
        return None
    comments = []
    for c in items[:10]:
        comments.append(
            {
                "id": safe_str(c.get("commentId") or c.get("id")),
                "url": safe_str(c.get("commentUrl")),
                "text": (c.get("text") or "").strip(),
                "author": safe_str(c.get("profileName") or c.get("authorName")),
                "authorUrl": safe_str(c.get("profileUrl")),
                "authorAvatarUrl": safe_str(c.get("profilePicture")),
                "likeCount": safe_int(c.get("likesCount") or c.get("reactionsCount")) or 0,
                "publishedAt": safe_str(c.get("date") or c.get("publishedAt")),
                "replyCount": safe_int(c.get("repliesCount") or c.get("commentsCount")) or 0,
            }
        )
    return {"platform": "facebook", "url": FB_POST_URL, "totalReturned": len(comments), "comments": comments}


def ig_comments_payload(items: list[dict]) -> dict | None:
    if not items:
        return None
    comments = []
    for c in items[:10]:
        owner = c.get("owner") or {}
        comments.append(
            {
                "id": safe_str(c.get("id")),
                "url": safe_str(c.get("commentUrl")),
                "text": (c.get("text") or "").strip(),
                "author": safe_str(c.get("ownerUsername") or owner.get("username")),
                "authorAvatarUrl": safe_str(c.get("ownerProfilePicUrl") or owner.get("profile_pic_url")),
                "authorIsVerified": bool(owner.get("is_verified")),
                "likeCount": safe_int(c.get("likesCount") or c.get("likeCount")) or 0,
                "publishedAt": safe_str(c.get("timestamp")),
                "replyCount": safe_int(c.get("replyCount") or c.get("repliesCount")) or 0,
            }
        )
    return {"platform": "instagram", "url": IG_POST_URL, "totalReturned": len(comments), "comments": comments}


async def main() -> None:
    async def run_all() -> dict[str, list[dict]]:
        coros = {
            "tt_profile": actor(
                settings.APIFY_ACTOR_TIKTOK_PROFILE, {"profiles": ["khaby.lame"], "resultsPerPage": 1}, 1
            ),
            "tt_download": actor(
                settings.APIFY_ACTOR_TIKTOK,
                {"postURLs": [TT_VIDEO_URL], "shouldDownloadVideos": True, "resultsPerPage": 1},
                1,
            ),
            "tt_channel_posts": actor(
                settings.APIFY_ACTOR_TIKTOK,
                {"profiles": ["khaby.lame"], "resultsPerPage": 5, "shouldDownloadVideos": False},
                5,
            ),
            "tt_search": actor(
                settings.APIFY_ACTOR_TIKTOK_SEARCH, {"searchQueries": ["skincare"], "resultsPerPage": 5}, 5
            ),
            "tt_comments": actor(
                settings.APIFY_ACTOR_TIKTOK_COMMENTS, {"postURLs": [TT_VIDEO_URL], "commentsPerPost": 10}, 10
            ),
            "yt_channel": actor(
                settings.APIFY_ACTOR_YOUTUBE_CHANNEL, {"startUrls": [{"url": YT_CHANNEL_URL}]}, 1
            ),
            "yt_channel_videos": actor(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"startUrls": [{"url": YT_CHANNEL_URL}], "maxResults": 5},
                5,
            ),
            "yt_search": actor(
                settings.APIFY_ACTOR_YOUTUBE_SEARCH,
                {"searchQueries": ["lofi hip hop"], "maxResults": 5, "maxResultsShorts": 0},
                5,
            ),
            "fb_post": actor(
                settings.APIFY_ACTOR_FACEBOOK_POSTS, {"startUrls": [{"url": FB_POST_URL}], "resultsLimit": 1}, 1
            ),
            "fb_page_posts": actor(
                settings.APIFY_ACTOR_FACEBOOK_POSTS, {"startUrls": [{"url": FB_PAGE_URL}], "resultsLimit": 12}, 12
            ),
            "fb_page": actor(settings.APIFY_ACTOR_FACEBOOK_PAGES, {"startUrls": [{"url": FB_PAGE_URL}]}, 1),
            "fb_comments": actor(
                settings.APIFY_ACTOR_FACEBOOK_COMMENTS, {"startUrls": [{"url": FB_POST_URL}], "resultsLimit": 10}, 10
            ),
            "ig_post": actor(
                settings.APIFY_ACTOR_INSTAGRAM_POST, {"directUrls": [IG_POST_URL], "resultsLimit": 1}, 1
            ),
            "ig_comments": actor(
                settings.APIFY_ACTOR_INSTAGRAM_COMMENT, {"directUrls": [IG_POST_URL], "resultsLimit": 10}, 10
            ),
            "ig_channel_posts": actor(
                settings.APIFY_ACTOR_INSTAGRAM_FALLBACK,
                {"directUrls": [IG_PROFILE_URL], "resultsLimit": 5, "resultsType": "posts"},
                5,
            ),
        }
        results = await asyncio.gather(*coros.values())
        return dict(zip(coros.keys(), results))

    raw = await run_all()

    payloads: dict[str, Any] = {}
    payloads["tiktok-channel-details"] = tt_channel_details_payload(raw["tt_profile"])
    if raw["tt_download"]:
        payloads["tiktok-video-details"] = tt_video(raw["tt_download"][0])
    if raw["tt_channel_posts"]:
        posts = [tt_video(i) for i in raw["tt_channel_posts"][:5]]
        payloads["tiktok-channel-posts"] = {"url": TT_PROFILE_URL, "totalReturned": len(posts), "posts": posts}
    if raw["tt_search"]:
        results = [tt_video(i) for i in raw["tt_search"][:5]]
        payloads["tiktok-search-by-hashtag"] = {
            "query": "skincare",
            "totalReturned": len(results),
            "hasMore": True,
            "nextCursor": 20,
            "results": results,
        }
    payloads["tiktok-comments"] = tt_comments_payload(raw["tt_comments"])
    payloads["youtube-channel-details"] = yt_channel_details_payload(raw["yt_channel"])
    if raw["yt_channel_videos"]:
        vids = [yt_video_row(v) for v in raw["yt_channel_videos"][:5]]
        payloads["youtube-channel-videos"] = {"url": YT_CHANNEL_URL, "totalReturned": len(vids), "videos": vids}
    if raw["yt_search"]:
        rows = []
        for v in raw["yt_search"][:5]:
            row = yt_video_row(v)
            row["channelName"] = safe_str(v.get("channelName") or v.get("channel"))
            rows.append(row)
        payloads["youtube-search"] = {"query": "lofi hip hop", "totalReturned": len(rows), "results": rows}
    if raw["fb_post"]:
        payloads["facebook-details"] = fb_post(raw["fb_post"][0])
    if raw["fb_page_posts"]:
        page_posts = [fb_post(i) for i in raw["fb_page_posts"] if not i.get("error")][:5]
        payloads["facebook-profile-posts"] = {"url": FB_PAGE_URL, "totalReturned": len(page_posts), "posts": page_posts}
        reels = [fb_post(i) for i in raw["fb_page_posts"] if not i.get("error") and _is_reel(i)][:2]
        if reels:
            payloads["facebook-profile-reels"] = {"url": FB_PAGE_URL, "totalReturned": len(reels), "reels": reels}
    payloads["facebook-page-details"] = fb_page_details_payload(raw["fb_page"])
    payloads["facebook-comments"] = fb_comments_payload(raw["fb_comments"])
    if raw["ig_post"]:
        payloads["instagram-details"] = ig_post(raw["ig_post"][0])
    payloads["instagram-comments"] = ig_comments_payload(raw["ig_comments"])
    if raw["ig_channel_posts"]:
        ig_posts = [ig_post(i) for i in raw["ig_channel_posts"] if not i.get("error")][:5]
        payloads["instagram-channel-posts"] = {"url": IG_PROFILE_URL, "totalReturned": len(ig_posts), "posts": ig_posts}

    snap_path = BACKEND / "api_snapshots.json"
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    updated, skipped = [], []
    for slug, data in payloads.items():
        if not data:
            skipped.append(slug)
            continue
        entry = snap.get(slug) or {"ok": True, "status": 200, "credits": None}
        entry["ok"] = True
        entry["status"] = 200
        entry["data"] = data
        snap[slug] = entry
        updated.append(slug)
    snap_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated:", ", ".join(sorted(updated)))
    if skipped:
        print("SKIPPED (no data):", ", ".join(sorted(skipped)))

    subprocess.run([sys.executable, "gen_examples.py"], cwd=BACKEND, check=True)


if __name__ == "__main__":
    asyncio.run(main())
