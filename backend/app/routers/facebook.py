"""Facebook endpoints."""

from __future__ import annotations

import html
import math
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyClient, ApifyError, get_apify
from app.services.apify_proxy import fetch_via_residential
from app.services.cached_runner import cached_or_run
from app.services.openai_client import summarize_transcript
from app.utils.formatters import normalize_language_code, safe_float, safe_int, safe_str
from app.utils.url import (
    detect_url_platform,
    extract_facebook_page,
    extract_facebook_video_id,
    platform_mismatch_detail,
)

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
RATE_FB_MARKETPLACE = 1.4
# Events billed at $13/1k = $0.013/event -> 2 credits/event.
RATE_FB_EVENTS = 2.0


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    return max(minimum, math.ceil(n * rate))


def _reject_facebook_platform_mismatch(url: str, example: str) -> None:
    detected = detect_url_platform(url)
    if detected and detected != "facebook":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "facebook", example),
        )


def _require_facebook_page(url: str) -> str:
    """Validate a page URL, @handle, or bare page name; return a full URL."""
    page = extract_facebook_page(url)
    if not page:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "facebook", "https://www.facebook.com/page"),
        )
    if "facebook.com" in (url or "") or "fb.watch" in (url or ""):
        return url
    return f"https://www.facebook.com/{page}"


def _require_facebook_path(url: str, path: str, example: str, label: str) -> None:
    _reject_facebook_platform_mismatch(url, example)
    if path not in (url or "").lower():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Facebook {label} URL. Pass a Facebook URL like {example}.",
        )


def _reply_payload(r: dict) -> dict:
    # On flat nested rows `commentId` is the parent's id; the reply's own
    # numeric id only lives in the commentUrl's reply_comment_id param.
    reply_id = None
    m = re.search(r"[?&]reply_comment_id=(\d+)", r.get("commentUrl") or "")
    if m:
        reply_id = m.group(1)
    return {
        "id": safe_str(reply_id or r.get("id") or r.get("commentId")),
        "url": safe_str(r.get("commentUrl")),
        "text": (r.get("text") or "").strip(),
        "author": safe_str(r.get("profileName") or r.get("authorName")),
        "authorUrl": safe_str(r.get("profileUrl")),
        "authorAvatarUrl": safe_str(r.get("profilePicture")),
        "likeCount": safe_int(r.get("likesCount") or r.get("reactionsCount")) or 0,
        "publishedAt": safe_str(r.get("date") or r.get("publishedAt")),
    }


def _fb_username_from_url(value: str | None) -> str | None:
    """Extract the vanity handle from a facebook.com profile/page URL."""
    if not value:
        return None
    match = re.search(r"facebook\.com/([A-Za-z0-9.\-_]+)/?", value)
    if not match:
        return None
    handle = match.group(1)
    if handle in {"profile.php", "people", "pages", "watch", "reel", "groups"} or handle.isdigit():
        return None
    return handle


def _normalize_post(item: dict) -> dict:
    # Group posts carry their photos under `attachments` instead of `media`.
    raw_media = item.get("media") or item.get("attachments")
    if isinstance(raw_media, list):
        media = raw_media[0] if raw_media and isinstance(raw_media[0], dict) else {}
    elif isinstance(raw_media, dict):
        media = raw_media
    else:
        media = {}
    user = item.get("user") or {}
    delivery = media.get("videoDeliveryLegacyFields") or {}
    duration_ms = media.get("playable_duration_in_ms")
    media_thumb = media.get("thumbnail")
    if isinstance(media_thumb, dict):
        media_thumb = media_thumb.get("uri")
    thumbnail = (
        item.get("thumbnailUrl")
        or media.get("thumbnailUrl")
        or media_thumb
        or ((media.get("thumbnailImage") or {}).get("uri"))
        or (((media.get("preferred_thumbnail") or {}).get("image") or {}).get("uri"))
        or ((media.get("image") or {}).get("uri"))
        or ((media.get("photo_image") or {}).get("uri"))
    )
    video_url = (
        item.get("videoUrl")
        or media.get("videoUrl")
        or delivery.get("browser_native_hd_url")
        or delivery.get("browser_native_sd_url")
    )
    return {
        "platform": "facebook",
        "url": safe_str(item.get("url") or item.get("postUrl")),
        "id": safe_str(item.get("postId") or item.get("id")),
        "caption": safe_str(item.get("text") or item.get("description")),
        "description": safe_str(item.get("text")),
        "publishedAt": safe_str(item.get("time") or item.get("publishedAt")),
        "durationSeconds": safe_float(
            item.get("videoDuration")
            or media.get("duration")
            or (duration_ms / 1000 if isinstance(duration_ms, (int, float)) and duration_ms else None)
        ),
        "thumbnailUrl": safe_str(thumbnail),
        "videoUrl": safe_str(video_url),
        "author": {
            "username": safe_str(
                item.get("pageUsername")
                or _fb_username_from_url(item.get("facebookUrl") or item.get("inputUrl"))
                or item.get("author")
            ),
            "displayName": safe_str(item.get("pageName") or user.get("name") or item.get("authorName")),
            "url": safe_str(item.get("pageUrl") or user.get("profileUrl") or item.get("facebookUrl") or item.get("authorUrl")),
            "profileImage": safe_str(user.get("profilePic")),
            "verified": item.get("isPageVerified") or item.get("verified"),
        },
        "engagement": {
            "views": safe_int(item.get("viewsCount") or item.get("videoViewCount") or item.get("videoPostViewCount")),
            "likes": safe_int(item.get("likes") or item.get("likesCount") or item.get("reactionsCount")) or 0,
            "comments": safe_int(item.get("comments") or item.get("commentsCount")) or 0,
            "shares": safe_int(item.get("shares") or item.get("sharesCount")) or 0,
        },
        "isVideo": bool(item.get("isVideo")),
        "link": safe_str(item.get("link")),
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


def _normalize_marketplace_detail(item: dict, url: str) -> dict:
    """Map the raw GraphQL listing entity from the per-item details actor."""
    price = item.get("listing_price") if isinstance(item.get("listing_price"), dict) else {}
    desc = item.get("redacted_description") if isinstance(item.get("redacted_description"), dict) else {}
    loc_text = item.get("location_text") if isinstance(item.get("location_text"), dict) else {}
    coords = item.get("location") if isinstance(item.get("location"), dict) else {}
    condition = next(
        (
            a.get("label") or a.get("value")
            for a in item.get("attribute_data") or []
            if isinstance(a, dict) and a.get("attribute_name") == "Condition"
        ),
        None,
    )
    created = safe_int(item.get("creation_time"))
    created_iso = (
        datetime.fromtimestamp(created, tz=timezone.utc).isoformat() if created else None
    )
    try:
        amount = float(price.get("amount")) if price.get("amount") is not None else None
    except (TypeError, ValueError):
        amount = None
    return {
        "platform": "facebook",
        "id": safe_str(item.get("id")),
        "url": safe_str(item.get("share_uri")) or url,
        "title": safe_str(item.get("marketplace_listing_title") or item.get("base_marketplace_listing_title")),
        "description": safe_str(desc.get("text")),
        "image": None,
        "price": amount,
        "priceFormatted": safe_str(price.get("formatted_amount_zeros_stripped")),
        "currency": safe_str(price.get("currency")),
        "condition": safe_str(condition),
        "location": safe_str(loc_text.get("text")),
        "latitude": coords.get("latitude"),
        "longitude": coords.get("longitude"),
        "isSold": item.get("is_sold"),
        "isLive": item.get("is_live"),
        "deliveryTypes": item.get("delivery_types") or [],
        "photos": [],
        "createdAt": created_iso,
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
    location_name = item.get("location_name") or item.get("venue") or item.get("locationName")
    return {
        "platform": "facebook",
        "id": safe_str(item.get("id") or item.get("event_id") or item.get("eventId")),
        "url": safe_str(item.get("url") or item.get("event_url") or item.get("eventUrl")),
        "name": safe_str(item.get("name") or item.get("title")),
        "description": safe_str(item.get("description")),
        "startDate": safe_str(item.get("utcStartDate") or item.get("start_date") or item.get("startDate")),
        "startTime": safe_str(item.get("startTime") or item.get("dateTimeSentence") or item.get("start_time")),
        "duration": safe_str(item.get("duration")),
        "eventType": safe_str(item.get("eventType") or item.get("event_type")),
        "isOnline": item.get("isOnline") if item.get("isOnline") is not None else item.get("is_online"),
        "isPast": item.get("isPast") if item.get("isPast") is not None else item.get("is_past"),
        "isCanceled": item.get("isCanceled") if item.get("isCanceled") is not None else item.get("is_canceled"),
        "address": safe_str(item.get("address") or item.get("location_address")),
        "image": safe_str(item.get("imageUrl") or item.get("photo_url") or item.get("image")),
        "usersGoing": safe_int(item.get("usersGoing") or item.get("going_count")),
        "usersInterested": safe_int(item.get("usersInterested") or item.get("interested_count")),
        "usersResponded": safe_int(item.get("usersResponded") or item.get("responded_count")),
        "location": {
            "name": safe_str(loc.get("name") or location_name),
            "city": safe_str(loc.get("city") or loc.get("contextualName") or item.get("location_city")),
            "latitude": loc.get("latitude") or item.get("latitude"),
            "longitude": loc.get("longitude") or item.get("longitude"),
            "countryCode": safe_str(loc.get("countryCode")),
        },
        "organizer": safe_str(item.get("organizedBy") or item.get("organizer") or item.get("host")),
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
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/page/posts/123")
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
            ctx["source"] = "apify"
            return _normalize_post(items[0])

        data = await cached_or_run(
            endpoint="facebook.details",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/transcript", summary="Facebook video transcript")
async def facebook_transcript(
    url: str = Query(...),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/watch/?v=123")
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
            language = None
            # Primary: AI transcript extractor (works for /watch, /reel and
            # video post URLs; returns Whisper segments with timestamps).
            items: list[dict[str, Any]] = []
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_FACEBOOK_TRANSCRIPT,
                    {"facebookUrl": url},
                    max_items=1,
                )
            except Exception:  # noqa: BLE001
                items = []
            segments: list[dict[str, Any]] = []
            full = ""
            if items:
                item = items[0]
                for s in item.get("normalizedSegments") or []:
                    if not isinstance(s, dict):
                        continue
                    text = safe_str(s.get("text")).strip()
                    if not text:
                        continue
                    start = round(float(s.get("start") or 0), 3)
                    end = round(float(s.get("end") or 0), 3)
                    mm, ss = int(start // 60), int(start % 60)
                    segments.append(
                        {
                            "text": text,
                            "start": start,
                            "duration": round(max(end - start, 0), 3),
                            "end": round(max(end, start), 3),
                            "timestamp": f"{mm:02d}:{ss:02d}",
                        }
                    )
                full = (safe_str(item.get("transcript")) or " ".join(s["text"] for s in segments)).strip()
                language = normalize_language_code(safe_str(item.get("detected_language")))

            if not full:
                # Fallback for text-only posts: use the post body.
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_FACEBOOK_POSTS,
                    {"startUrls": [{"url": url}], "resultsLimit": 1},
                    max_items=1,
                )
                if not items:
                    raise HTTPException(status_code=404, detail="Post not found")
                full = safe_str(items[0].get("text")) or ""
                segments = []
            if not full:
                raise HTTPException(status_code=422, detail="No transcript available")
            ctx["source"] = "apify"
            return {
                "platform": "facebook",
                "url": url,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
                "language": language,
            }

        data = await cached_or_run(
            endpoint="facebook.transcript",
            params={"url": url, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/summarize", summary="AI summary of Facebook video/post")
async def facebook_summarize(
    url: str = Query(...),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/watch/?v=123")
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
            ctx["source"] = "apify"
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
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Facebook post comments")
async def facebook_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/page/posts/123")
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
            ctx["source"] = "apify"
            return {
                "platform": "facebook",
                "url": url,
                "totalReturned": len(comments),
                "comments": comments,
            }

        data = await cached_or_run(
            endpoint="facebook.comments",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["comments"]), RATE_FB_COMMENTS, 2)
        return ApiResponse(data=data)


@router.get("/page-details", summary="Facebook page info & stats")
async def facebook_page_details(
    url: str = Query(..., description="Facebook page URL, @handle, or page name"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_facebook_page(url)
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
            if p.get("error"):
                # The actor reports deleted/restricted pages as an error row
                # ({"error": "not_available", ...}); returning it would produce
                # an all-null 200 that then gets cached.
                raise HTTPException(status_code=404, detail="Page not found or not public")
            verified = p.get("verified") or p.get("isPageVerified")
            if verified is None and (p.get("confirmed_owner") or p.get("CONFIRMED_OWNER_LABEL")):
                # The pages scraper has no blue-badge flag; a confirmed Page
                # owner label is the closest verification signal it exposes.
                verified = True
            username = safe_str(
                p.get("pageUsername")
                or p.get("username")
                or _fb_username_from_url(p.get("pageUrl") or p.get("facebookUrl"))
            )
            page_name = safe_str(p.get("pageName"))
            if page_name and page_name.lower() in {"people", "pages", "profile", "home"}:
                # profile.php-style pages come back with a junk pageName (the
                # site section, e.g. "people"); the real name lives in title.
                page_name = None
            display_name = page_name or safe_str(p.get("title") or p.get("name"))
            if not display_name:
                # Safety net: the first info line reads "<Page name>. N likes".
                info = p.get("info")
                first_line = safe_str(info[0]) if isinstance(info, list) and info else None
                if first_line:
                    display_name = first_line.rsplit(".", 1)[0].strip() or None
            display_name = display_name or username
            ctx["source"] = "apify"
            return {
                "platform": "facebook",
                "url": safe_str(p.get("pageUrl") or p.get("facebookUrl")) or url,
                "username": username,
                "name": display_name,
                "displayName": display_name,
                "fullName": safe_str(p.get("title")) or display_name,
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

        data = await cached_or_run(
            endpoint="facebook.page-details",
            params={"url": url, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/profile-posts", summary="Latest posts from a Facebook profile/page")
async def facebook_profile_posts(
    url: str = Query(..., description="Facebook profile/page URL, @handle, or page name"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_facebook_page(url)
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
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="facebook.profile-posts",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_FB_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/profile-reels", summary="Latest Reels from a Facebook profile/page")
async def facebook_profile_reels(
    url: str = Query(..., description="Facebook profile/page URL, @handle, or page name"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_facebook_page(url)
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
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(reels), "reels": reels}

        data = await cached_or_run(
            endpoint="facebook.profile-reels",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = cost
        return ApiResponse(data=data)


@router.get("/group-posts", summary="Posts from a public Facebook group")
async def facebook_group_posts(
    url: str = Query(..., description="Public Facebook group URL"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/groups/group-name")
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
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="facebook.group-posts",
            params={"url": url, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["posts"]), RATE_FB_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/comment-replies", summary="Replies to a Facebook comment")
async def facebook_comment_replies(
    url: str = Query(..., description="Facebook post URL the comment belongs to"),
    comment_id: str = Query(..., description="ID of the parent comment"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/page/posts/123")
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
                # apify/facebook-comments-scraper emits nested comments as flat
                # rows: threadingDepth > 0, replyToCommentId points at the
                # parent, and commentId is also the top-level parent's id.
                depth = safe_int(c.get("threadingDepth")) or 0
                parent = safe_str(
                    c.get("parentCommentId")
                    or c.get("replyToId")
                    or c.get("commentParentId")
                    or c.get("replyToCommentId")
                    or (c.get("commentId") if depth > 0 else None)
                )
                nested = c.get("replies") or c.get("nestedComments")
                if isinstance(nested, list) and safe_str(c.get("id") or c.get("commentId")) == comment_id:
                    for r in nested:
                        replies.append(_reply_payload(r))
                elif parent == comment_id and depth > 0:
                    replies.append(_reply_payload(c))
                if len(replies) >= limit:
                    break
            ctx["source"] = "apify"
            return {
                "platform": "facebook",
                "url": url,
                "commentId": comment_id,
                "totalReturned": len(replies[:limit]),
                "replies": replies[:limit],
            }

        data = await cached_or_run(
            endpoint="facebook.comment-replies",
            params={"url": url, "comment_id": comment_id, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
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
    url: str = Query(..., description="Facebook profile/page URL, @handle, or page name"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_facebook_page(url)
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
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(photos), "photos": photos}

        data = await cached_or_run(
            endpoint="facebook.profile-photos",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["photos"]), RATE_FB_POSTS, 2)
        return ApiResponse(data=data)


@router.get("/profile-events", summary="Events from a Facebook profile/page")
async def facebook_profile_events(
    url: str = Query(..., description="Facebook profile/page URL, @handle, or page name"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_facebook_page(url)
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
            # The actor needs the page's /events listing (a bare page URL
            # yields nothing) and, being browser-based, can outlive the global
            # 120s sync timeout.
            events_url = url.rstrip("/") + "/events"
            items = await ApifyClient(timeout=280).run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                {"startUrls": [events_url], "maxEvents": limit},
                max_items=limit,
            )
            events = [_normalize_event(i) for i in items[:limit] if not i.get("error")]
            ctx["source"] = "apify"
            return {"platform": "facebook", "url": url, "totalReturned": len(events), "events": events}

        data = await cached_or_run(
            endpoint="facebook.profile-events",
            params={"url": url, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            # Events actor runs take minutes (280s timeout); serve the last
            # list instantly after TTL expiry and refresh in the background.
            stale_while_revalidate=True,
            use_cache=cache,
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


def _event_id(url: str) -> str | None:
    match = re.search(r"/events/(\d+)", url)
    return match.group(1) if match else None


def _partial_event_from_page(url: str, page: str) -> dict[str, Any] | None:
    title = _og_meta(page, "og:title")
    description = _og_meta(page, "og:description")
    image = _og_meta(page, "og:image")
    if not (title or description or image):
        return None
    return {
        "platform": "facebook",
        "id": safe_str(_event_id(url)),
        "url": safe_str(_og_meta(page, "og:url") or url),
        "name": safe_str(title),
        "description": safe_str(description),
        "image": safe_str(image),
        "startTime": None,
        "endTime": None,
        "location": None,
        "hosts": [],
    }


@router.get("/marketplace-item", summary="Facebook Marketplace listing details")
async def facebook_marketplace_item(
    url: str = Query(..., description="Facebook Marketplace item URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_facebook_path(
        url,
        "/marketplace/item/",
        "https://www.facebook.com/marketplace/item/123456789",
        "Marketplace item",
    )
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/marketplace-item",
        platform="facebook",
        resource_url=url,
        base_credits=17,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Fast path: scrape OpenGraph metadata from the public listing page.
            # Facebook serves OG tags to residential IPs but login-walls
            # datacenter IPs, so try the Apify residential proxy first and fall
            # back to a direct fetch. This avoids waiting on a full marketplace
            # actor run for single-item detail pages.
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
                )
            }
            resp = None
            try:
                resp = await fetch_via_residential(url, headers=headers, timeout=8)
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
                async with httpx.AsyncClient(timeout=6, follow_redirects=True, headers=headers) as client:
                    resp = await client.get(url)
                if resp.status_code < 400:
                    title, description, image = _og_fields(resp.text)
            item_id = None
            m = re.search(r"/marketplace/item/(\d+)", url)
            if m:
                item_id = m.group(1)

            if title or description or image:
                page = resp.text if resp is not None else ""
                ctx["source"] = "direct"
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

            # Fallback: per-item details actor (the search actor has no
            # single-listing mode - it requires keyword queries).
            apify = get_apify()
            items = []
            if item_id:
                try:
                    items = await apify.run_actor_sync(
                        settings.APIFY_ACTOR_FACEBOOK_MARKETPLACE_ITEM,
                        {"listingId": item_id},
                        max_items=1,
                    )
                except (ApifyError, httpx.HTTPError):
                    items = []
            if items and not items[0].get("error"):
                ctx["source"] = "apify"
                return _normalize_marketplace_detail(items[0], url)
            raise HTTPException(status_code=404, detail="Listing not found")

        data = await cached_or_run(
            endpoint="facebook.marketplace-item",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/marketplace-search", summary="Search Facebook Marketplace listings")
async def facebook_marketplace_search(
    q: str = Query(..., min_length=2, description="Product/keyword to search for"),
    location: str = Query(..., min_length=2, description="City or place name, e.g. 'Austin, TX'"),
    limit: int = Query(20, ge=1, le=200),
    details: bool = Query(False, description="Fetch full description, photos & coordinates per listing (slower, costs more)"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            ctx["source"] = "apify"
            return {"query": q, "location": location, "totalReturned": len(listings), "listings": listings}

        data = await cached_or_run(
            endpoint="facebook.marketplace-search",
            params={"q": q, "location": location, "limit": limit, "details": details, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["listings"]), rate, 2)
        return ApiResponse(data=data)


@router.get("/marketplace-location-search", summary="Search Facebook Marketplace locations")
async def facebook_marketplace_location_search(
    q: str = Query(..., min_length=2, description="City/place search query, e.g. Austin"),
    limit: int = Query(10, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/marketplace-location-search",
        platform="facebook",
        resource_url=None,
        base_credits=17,
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
            ctx["source"] = "apify"
            return {"query": q, "totalReturned": len(results), "locations": results}

        data = await cached_or_run(
            endpoint="facebook.marketplace-location-search",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/event-search", summary="Search Facebook events by keyword/location")
async def facebook_event_search(
    q: str = Query(..., min_length=2, description="Topic and/or place, e.g. 'comedy Chicago'"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
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
            # The official events scraper is browser-based and routinely needs
            # ~2-3 minutes; the global sync timeout (120s) cut it off mid-run.
            # When even 280s is not enough, reuse the latest successful run
            # instead of failing.
            apify = ApifyClient(timeout=280, max_attempts=1)
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                    {"searchQueries": [q], "maxEvents": limit},
                    max_items=limit,
                )
            except ApifyError:
                items = await apify.last_succeeded_items(
                    settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                    max_age_secs=48 * 3600,
                    max_items=limit,
                )
                if not items:
                    raise
            events = [_normalize_event(i) for i in items[:limit] if not i.get("error")]
            ctx["source"] = "apify"
            return {"query": q, "totalReturned": len(events), "events": events}

        data = await cached_or_run(
            endpoint="facebook.event-search",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            # Browser-based events actor takes 2-3 min (p95 ~101s); serve the
            # last result set instantly after TTL and refresh in the background
            # rather than making the caller wait minutes, same as profile-events.
            stale_while_revalidate=True,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["events"]), RATE_FB_EVENTS, 4)
        return ApiResponse(data=data)


@router.get("/event-details", summary="Facebook event details")
async def facebook_event_details(
    url: str = Query(..., description="Facebook event URL, e.g. https://facebook.com/events/ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_facebook_path(
        url,
        "/events/",
        "https://www.facebook.com/events/123456789",
        "event",
    )
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/event-details",
        platform="facebook",
        resource_url=url,
        base_credits=2,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
                )
            }
            partial_event: dict[str, Any] | None = None
            try:
                resp = await fetch_via_residential(url, headers=headers, timeout=8)
                if resp.status_code < 400:
                    partial_event = _partial_event_from_page(url, resp.text)
                    if partial_event:
                        ctx["source"] = "direct"
                        return partial_event
            except Exception:  # noqa: BLE001
                pass
            try:
                async with httpx.AsyncClient(timeout=6, follow_redirects=True, headers=headers) as client:
                    resp = await client.get(url)
                if resp.status_code < 400:
                    partial_event = _partial_event_from_page(url, resp.text)
                    if partial_event:
                        ctx["source"] = "direct"
                        return partial_event
            except Exception:  # noqa: BLE001
                pass

            apify = get_apify()
            items, _actor = await apify.run_with_fallback(
                [
                    (settings.APIFY_ACTOR_FACEBOOK_EVENT_DETAILS, {"eventUrls": [url]}),
                    (settings.APIFY_ACTOR_FACEBOOK_EVENT_DETAILS, {"eventUrls": [_event_id(url) or url]}),
                    (settings.APIFY_ACTOR_FACEBOOK_EVENTS, {"startUrls": [url], "maxEvents": 1}),
                    (settings.APIFY_ACTOR_FACEBOOK_EVENTS, {"startUrls": [{"url": url}], "maxEvents": 1}),
                ],
                max_items=1,
            )
            if not items or items[0].get("error"):
                if partial_event:
                    ctx["source"] = "direct"
                    return partial_event
                raise HTTPException(status_code=404, detail="Event not found")
            ctx["source"] = "apify"
            return _normalize_event(items[0])

        data = await cached_or_run(
            endpoint="facebook.event-details",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
