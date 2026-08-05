"""Facebook endpoints."""

from __future__ import annotations

import html
import math
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services import (
    facebook_comments_native,
    facebook_details_native,
    facebook_events_native,
    facebook_group_posts_native,
    facebook_marketplace_location_native,
    facebook_marketplace_native,
    facebook_page_native,
    facebook_profile_photos_native,
    facebook_profile_posts_native,
    facebook_profile_reels_native,
)
from app.services.apify_client import ApifyClient, ApifyError, get_apify
from app.services.apify_proxy import fetch_via_residential
from app.services.cached_runner import cached_or_run
from app.services.openai_client import summarize_transcript
from app.utils.formatters import safe_float, safe_int, safe_str, strip_empty
from app.utils.url import (
    detect_url_platform,
    extract_facebook_page,
    extract_facebook_video_id,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_SUMMARIZE = 4
CREDIT_DETAILS = facebook_details_native.CREDIT_FB_DETAILS_NATIVE
CREDIT_PAGE_DETAILS = facebook_page_native.CREDIT_FB_PAGE_NATIVE

# apify/facebook-comments-scraper is billed per result ($1.50/1k = $0.0015).
# 0.6 credit/comment = ~80% markup (0.6 * $0.0045 = $0.0027 vs $0.0015).
RATE_FB_COMMENTS = 0.6
# Posts / reels / group posts scrapers are billed per result (~$0.0015-0.002).
RATE_FB_POSTS = 0.6
# Events billed at $13/1k = $0.013/event -> 2 credits/event.
RATE_FB_EVENTS = 2.0
CREDIT_FB_EVENTS_NATIVE = facebook_events_native.CREDIT_FB_EVENTS_NATIVE
CREDIT_FB_COMMENTS_NATIVE = facebook_comments_native.CREDIT_FB_COMMENTS_NATIVE
CREDIT_FB_MARKETPLACE_NATIVE = facebook_marketplace_native.CREDIT_FB_MARKETPLACE_NATIVE
CREDIT_FB_MARKETPLACE_ITEM_NATIVE = facebook_marketplace_native.CREDIT_FB_MARKETPLACE_ITEM_NATIVE
CREDIT_FB_PROFILE_POSTS_NATIVE = facebook_profile_posts_native.CREDIT_FB_PROFILE_POSTS_NATIVE
CREDIT_FB_PROFILE_REELS_NATIVE = facebook_profile_reels_native.CREDIT_FB_PROFILE_REELS_NATIVE
CREDIT_FB_GROUP_POSTS_NATIVE = facebook_group_posts_native.CREDIT_FB_GROUP_POSTS_NATIVE
CREDIT_FB_PROFILE_PHOTOS_NATIVE = facebook_profile_photos_native.CREDIT_FB_PROFILE_PHOTOS_NATIVE
CREDIT_FB_MARKETPLACE_LOCATION_NATIVE = facebook_marketplace_location_native.CREDIT_FB_MARKETPLACE_LOCATION_NATIVE


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    if n <= 0:
        return 0
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


def _fb_comment_author(
    *,
    name: str | None,
    author_id: str | None = None,
    gender: str | None = None,
    short_name: str | None = None,
    url: str | None = None,
    avatar_url: str | None = None,
) -> dict[str, Any]:
    """Nested author object (stable id / gender) plus flat BC url fields."""
    display = safe_str(name)
    short = safe_str(short_name)
    if not short and display:
        short = display.split(None, 1)[0]
    author: dict[str, Any] = {
        "id": safe_str(author_id),
        "name": display,
        "shortName": short,
        "gender": safe_str(gender),
        "url": safe_str(url),
        "avatarUrl": safe_str(avatar_url),
    }
    return {k: v for k, v in author.items() if v is not None}


def _fb_apify_reactions(item: dict[str, Any]) -> tuple[int, dict[str, int]]:
    """Best-effort reactions from Apify rows (often only a total)."""
    reactions = facebook_comments_native.empty_reactions()
    raw = item.get("reactions") if isinstance(item.get("reactions"), dict) else None
    if raw:
        for key in reactions:
            n = safe_int(raw.get(key) or raw.get(key.capitalize()) or raw.get(key.upper()))
            if n is not None:
                reactions[key] = n
        # Common Apify aliases
        for src, dst in (("angry", "anger"), ("Angry", "anger"), ("LIKE", "like")):
            n = safe_int(raw.get(src))
            if n is not None:
                reactions[dst] = max(reactions[dst], n)
    total = safe_int(
        item.get("likesCount")
        or item.get("likes")
        or item.get("reactionsCount")
        or item.get("reactionCount")
        or item.get("reaction_count")
    )
    summed = sum(reactions.values())
    if total is None or total < summed:
        total = summed
    if total and summed == 0:
        # Actor only gave a total — put it under like (unknown mix).
        reactions["like"] = total
    return total or 0, reactions


def _reply_payload(r: dict) -> dict:
    # On flat nested rows `commentId` is the parent's id; the reply's own
    # numeric id only lives in the commentUrl's reply_comment_id param.
    reply_id = None
    m = re.search(r"[?&]reply_comment_id=(\d+)", r.get("commentUrl") or "")
    if m:
        reply_id = m.group(1)
    author_url = safe_str(r.get("profileUrl"))
    avatar = safe_str(r.get("profilePicture"))
    name = safe_str(r.get("profileName") or r.get("authorName"))
    reaction_count, reactions = _fb_apify_reactions(r)
    author_raw = r.get("author") if isinstance(r.get("author"), dict) else {}
    author = _fb_comment_author(
        name=name,
        author_id=safe_str(r.get("authorId") or r.get("profileId") or author_raw.get("id")),
        gender=safe_str(r.get("gender") or author_raw.get("gender")),
        short_name=safe_str(
            r.get("shortName") or r.get("short_name") or author_raw.get("short_name") or author_raw.get("shortName")
        ),
        url=author_url,
        avatar_url=avatar,
    )
    return {
        "id": safe_str(reply_id or r.get("id") or r.get("commentId")),
        "url": safe_str(r.get("commentUrl")),
        "text": (r.get("text") or "").strip(),
        "author": author,
        "authorUrl": author_url,
        "authorAvatarUrl": avatar,
        "likeCount": reaction_count,
        "reactionCount": reaction_count,
        "reactions": reactions,
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


def _fb_unix_iso(raw: Any) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)) or (isinstance(raw, str) and str(raw).isdigit()):
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc).isoformat().replace("+00:00", ".000Z")
        except (OSError, OverflowError, ValueError):
            return None
    return safe_str(raw)


def _fb_external_link(item: dict) -> str | None:
    """Unwrap the first ExternalUrl from GraphQL message.ranges, if present."""
    message = item.get("message")
    ranges = message.get("ranges") if isinstance(message, dict) else None
    if not isinstance(ranges, list):
        return None
    for rng in ranges:
        if not isinstance(rng, dict):
            continue
        entity = rng.get("entity") or {}
        if not isinstance(entity, dict):
            continue
        if entity.get("__typename") != "ExternalUrl" and entity.get("__isEntity") != "ExternalUrl":
            continue
        wrapped = safe_str(entity.get("url") or entity.get("mobileUrl"))
        if not wrapped:
            continue
        # l.facebook.com/l.php?u=<encoded>
        m = re.search(r"[?&]u=([^&]+)", wrapped)
        if m:
            return safe_str(unquote(m.group(1)))
        return wrapped
    return None


def _fb_thumb_from_node(node: Any) -> str | None:
    """Pull a thumbnail URI out of a media / attachment node."""
    if not isinstance(node, dict):
        return None
    # Nested ``media`` wrapper (attachments[{media:{...}}]).
    nested = node.get("media")
    if isinstance(nested, dict):
        from_nested = _fb_thumb_from_node(nested)
        if from_nested:
            return from_nested
    for key in ("thumbnailUrl", "thumbnail"):
        val = node.get(key)
        if isinstance(val, str) and val:
            return val
        if isinstance(val, dict):
            uri = safe_str(val.get("uri") or val.get("url"))
            if uri:
                return uri
    for key in ("thumbnailImage", "preferred_thumbnail", "image", "photo_image"):
        val = node.get(key)
        if isinstance(val, dict):
            inner = val.get("image") if isinstance(val.get("image"), dict) else val
            if isinstance(inner, dict):
                uri = safe_str(inner.get("uri") or inner.get("url"))
                if uri:
                    return uri
    return None


def _fb_first_media_node(raw_media: Any) -> dict:
    """First usable media dict from ``media`` / ``attachments`` list-or-dict."""
    if isinstance(raw_media, list):
        for entry in raw_media:
            if not isinstance(entry, dict):
                continue
            nested = entry.get("media")
            if isinstance(nested, dict):
                return nested
            # Skip album/mediaset stubs that only carry a set URL.
            if entry.get("thumbnail") or entry.get("photo_image") or entry.get("image") or entry.get(
                "videoDeliveryLegacyFields"
            ):
                return entry
        first = raw_media[0] if raw_media and isinstance(raw_media[0], dict) else {}
        return first.get("media") if isinstance(first.get("media"), dict) else first
    if isinstance(raw_media, dict):
        return raw_media
    return {}


def _normalize_post(item: dict) -> dict:
    # Group posts carry their photos under `attachments` instead of `media`.
    # Reel rows from apify/facebook-posts-scraper often use the GraphQL
    # ``short_form_video_context`` shape instead of the classic post shape.
    short = item.get("short_form_video_context") if isinstance(item.get("short_form_video_context"), dict) else {}
    playback = short.get("playback_video") if isinstance(short.get("playback_video"), dict) else {}
    video_owner = short.get("video_owner") if isinstance(short.get("video_owner"), dict) else {}
    delegate = video_owner.get("delegate_page") if isinstance(video_owner.get("delegate_page"), dict) else {}
    display_pic = video_owner.get("displayPicture") if isinstance(video_owner.get("displayPicture"), dict) else {}
    short_delivery = (
        playback.get("videoDeliveryLegacyFields")
        or playback.get("video_delivery_legacy_fields")
        or {}
    )
    if not isinstance(short_delivery, dict):
        short_delivery = {}
    short_thumb = None
    pref = playback.get("preferred_thumbnail")
    if isinstance(pref, dict):
        img = pref.get("image") if isinstance(pref.get("image"), dict) else pref
        short_thumb = img.get("uri") if isinstance(img, dict) else None

    raw_media = item.get("media") or item.get("attachments")
    media = _fb_first_media_node(raw_media)
    # Album posts put a mediaset stub first; scan all attachments for a thumb.
    attachment_thumb = None
    if isinstance(raw_media, list):
        for entry in raw_media:
            attachment_thumb = _fb_thumb_from_node(entry)
            if attachment_thumb:
                break
    elif isinstance(raw_media, dict):
        attachment_thumb = _fb_thumb_from_node(raw_media)

    user = item.get("user") or {}
    delivery = media.get("videoDeliveryLegacyFields") or media.get("video_delivery_legacy_fields") or {}
    if not isinstance(delivery, dict):
        delivery = {}
    duration_ms = media.get("playable_duration_in_ms") or playback.get("playable_duration_in_ms")
    thumbnail = (
        safe_str(item.get("thumbnailUrl"))
        or attachment_thumb
        or short_thumb
        or _fb_thumb_from_node(media)
    )
    video_hd_url = safe_str(
        item.get("videoHdUrl")
        or delivery.get("browser_native_hd_url")
        or short_delivery.get("browser_native_hd_url")
        or playback.get("browser_native_hd_url")
        or playback.get("playable_url_quality_hd")
    )
    video_sd_url = safe_str(
        item.get("videoSdUrl")
        or delivery.get("browser_native_sd_url")
        or short_delivery.get("browser_native_sd_url")
        or playback.get("browser_native_sd_url")
        or playback.get("playable_url")
    )
    video_url = (
        item.get("videoUrl")
        or media.get("videoUrl")
        or video_hd_url
        or video_sd_url
    )
    video_width = safe_int(
        item.get("videoWidth")
        or media.get("original_width")
        or media.get("width")
        or playback.get("original_width")
        or playback.get("width")
    )
    video_height = safe_int(
        item.get("videoHeight")
        or media.get("original_height")
        or media.get("height")
        or playback.get("original_height")
        or playback.get("height")
    )
    captions_url = safe_str(
        item.get("captionsUrl")
        or item.get("captions_url")
        or media.get("captions_url")
        or playback.get("captions_url")
        or facebook_details_native._captions_url_from_video(playback)
        or facebook_details_native._captions_url_from_video(media)
    )
    music = item.get("music") if isinstance(item.get("music"), dict) else None
    if not music:
        music = facebook_details_native._music_from_short_form(short)
    feedback_id = safe_str(item.get("feedbackId") or item.get("feedback_id"))
    # Group scrapers put the *group* URL in facebookUrl/inputUrl. Prefer the
    # posting user's profile URL so author.username/url aren't the group page.
    author_url = safe_str(
        item.get("pageUrl")
        or user.get("profileUrl")
        or video_owner.get("url")
        or item.get("authorUrl")
        or item.get("userUrl")
    )
    groupish = False
    group_slug: str | None = None
    for candidate in (item.get("facebookUrl"), item.get("inputUrl"), item.get("url"), item.get("permalink")):
        text = str(candidate or "")
        if "/groups/" in text.lower():
            groupish = True
            m = re.search(r"/groups/([^/?#]+)", text, re.I)
            if m:
                group_slug = m.group(1).lower()
            break
    if author_url and "/groups/" in author_url.lower():
        # Never keep a group URL as the author profile.
        author_url = None
    if not author_url and not groupish:
        author_url = safe_str(item.get("facebookUrl") or item.get("inputUrl"))
    # Numeric FB user ids resolve as profile URLs; opaque pfbid tokens do not.
    user_id = safe_str(
        user.get("id")
        or video_owner.get("id")
        or delegate.get("id")
        or item.get("authorId")
        or item.get("pageId")
    )
    if not user_id and author_url:
        m = re.search(r"facebook\.com/(?:profile\.php\?id=)?(\d{5,})", author_url)
        if m:
            user_id = m.group(1)
    if not author_url and user_id and user_id.isdigit():
        author_url = f"https://www.facebook.com/{user_id}"

    def _author_handle(value: str | None) -> str | None:
        handle = safe_str(value)
        if not handle:
            return None
        # Group slug mistakenly stamped as pageUsername on hydrated group posts.
        if group_slug and handle.lower() == group_slug:
            return None
        if handle.lower() in {"groups", "people", "pages", "watch", "reel"}:
            return None
        return handle

    author_username = (
        _author_handle(item.get("pageUsername"))
        or _author_handle(user.get("username"))
        or _author_handle(delegate.get("uri_token"))
        or _author_handle(_fb_username_from_url(safe_str(video_owner.get("url"))))
        or _author_handle(_fb_username_from_url(author_url))
        or (user_id if user_id and user_id.isdigit() else None)
        or (
            None
            if groupish
            else _author_handle(_fb_username_from_url(item.get("facebookUrl") or item.get("inputUrl")))
        )
        or _author_handle(item.get("author") if isinstance(item.get("author"), str) else None)
    )
    # Classic posts: isPageVerified / user.verified (often absent).
    # Reels (short_form): video_owner.is_verified is the live GraphQL signal.
    verified = item.get("isPageVerified")
    if verified is None:
        verified = item.get("verified")
    if verified is None and isinstance(user, dict):
        verified = user.get("isVerified") or user.get("verified")
    if verified is None and video_owner:
        verified = video_owner.get("is_verified")
        if verified is None:
            verified = video_owner.get("isVerified") or video_owner.get("verified")

    message = item.get("message") if isinstance(item.get("message"), dict) else {}
    caption = safe_str(
        item.get("text")
        or item.get("description")
        or message.get("text")
    )
    published = safe_str(item.get("time") or item.get("publishedAt")) or _fb_unix_iso(
        item.get("creation_time") or playback.get("publish_time") or playback.get("creation_time")
    )
    likers = item.get("likers") if isinstance(item.get("likers"), dict) else {}
    post_url = safe_str(
        item.get("url")
        or item.get("postUrl")
        or short.get("shareable_url")
        or playback.get("permalink_url")
        or item.get("facebookUrl")
    )
    is_video = item.get("isVideo")
    if is_video is None:
        is_video = bool(short or video_url or "/reel/" in (post_url or "").lower())
    duration_seconds = safe_float(
        item.get("videoDuration")
        or media.get("duration")
        or playback.get("length_in_second")
        or (duration_ms / 1000 if isinstance(duration_ms, (int, float)) and duration_ms else None)
    )
    video_id = safe_str(playback.get("id") or media.get("id") or item.get("videoId"))
    video_view_count = safe_int(
        item.get("viewsCount") or item.get("videoViewCount") or item.get("videoPostViewCount")
    )
    # Missing engagement stays None — never invent 0 (silent zeros poison rates).
    shares_count = safe_int(
        item.get("shares")
        if item.get("shares") is not None
        else item.get("sharesCount")
        if item.get("sharesCount") is not None
        else item.get("share_count_reduced")
    )
    permalink = safe_str(item.get("permalink") or item.get("permalink_url") or post_url)
    out: dict[str, Any] = {
        "platform": "facebook",
        "url": post_url,
        "permalink": permalink,
        "id": safe_str(item.get("postId") or item.get("post_id") or item.get("id") or playback.get("id")),
        "caption": caption,
        "description": caption,
        "publishedAt": published,
        "durationSeconds": duration_seconds,
        "thumbnailUrl": safe_str(thumbnail),
        "videoUrl": safe_str(video_url),
        "author": {
            "id": user_id,
            "username": author_username,
            "displayName": safe_str(
                item.get("pageName") or user.get("name") or video_owner.get("name") or item.get("authorName")
            ),
            "shortName": safe_str(user.get("shortName") or user.get("short_name")),
            "url": author_url,
            "profileImage": safe_str(
                user.get("profilePic")
                or user.get("profilePicture")
                or display_pic.get("uri")
            ),
            "verified": bool(verified) if verified is not None else None,
        },
        "engagement": {
            "views": video_view_count,
            "likes": safe_int(
                item.get("likes")
                or item.get("likesCount")
                or item.get("reactionsCount")
                or likers.get("count")
            ),
            "comments": safe_int(
                item.get("comments")
                or item.get("commentsCount")
                or item.get("total_comment_count")
            ),
            "shares": shares_count,
        },
        "isVideo": bool(is_video),
        "link": safe_str(item.get("link")) or _fb_external_link(item),
    }
    # Additive media / identity fields (never rename videoUrl / author.username).
    if feedback_id:
        out["feedbackId"] = feedback_id
    if captions_url:
        out["captionsUrl"] = captions_url
    if video_sd_url:
        out["videoSdUrl"] = video_sd_url
    if video_hd_url:
        out["videoHdUrl"] = video_hd_url
    if video_width is not None:
        out["videoWidth"] = video_width
    if video_height is not None:
        out["videoHeight"] = video_height
    if video_view_count is not None:
        out["videoViewCount"] = video_view_count
    if music and (music.get("id") or music.get("trackTitle")):
        out["music"] = {
            "id": safe_str(music.get("id")),
            "type": safe_str(music.get("type")),
            "trackTitle": safe_str(music.get("trackTitle") or music.get("track_title")),
            "albumArt": safe_str(music.get("albumArt") or music.get("music_album_art") or music.get("album_art")),
        }
    if bool(is_video) and (video_url or video_sd_url or video_hd_url or captions_url or video_id):
        video_block = {
            "id": video_id,
            "sdUrl": video_sd_url,
            "hdUrl": video_hd_url,
            "url": safe_str(video_url),
            "width": video_width,
            "height": video_height,
            "durationSeconds": duration_seconds,
            "thumbnailUrl": safe_str(thumbnail),
            "captionsUrl": captions_url,
        }
        out["video"] = video_block
        out["videoDetails"] = {
            "sdUrl": video_sd_url,
            "hdUrl": video_hd_url,
            "thumbnailUrl": safe_str(thumbnail),
        }
    top_comments = item.get("topComments")
    if isinstance(top_comments, list) and top_comments:
        out["topComments"] = top_comments
    # Drop null author keys (e.g. group slug must not become username).
    if isinstance(out.get("author"), dict):
        out["author"] = {k: v for k, v in out["author"].items() if v is not None and v != ""}
    if isinstance(out.get("engagement"), dict):
        # Always expose views + shares (null when N/A / unknown) so mixed
        # post+reel pages keep one engagement shape for typed clients.
        eng = out["engagement"]
        views = eng.get("views")
        shares = eng.get("shares")
        cleaned = {k: v for k, v in eng.items() if v is not None}
        cleaned["views"] = views
        cleaned["shares"] = shares
        out["engagement"] = cleaned
    return out


def _unify_listing_authors(posts: list[dict[str, Any]], page_url: str) -> None:
    """One page must not appear as both ``nasa`` and ``NASA`` in the same page."""
    if not posts:
        return
    page_handle = _fb_username_from_url(page_url)
    scored: list[tuple[int, str]] = []
    for post in posts:
        author = post.get("author") if isinstance(post.get("author"), dict) else {}
        username = safe_str(author.get("username"))
        if not username:
            continue
        score = 0
        if author.get("verified"):
            score += 4
        if author.get("profileImage"):
            score += 2
        score += sum(1 for ch in username if ch.isupper())
        scored.append((score, username))
    canonical = None
    if scored:
        scored.sort(key=lambda t: t[0], reverse=True)
        canonical = scored[0][1]
    if page_handle:
        if canonical and canonical.lower() == page_handle.lower():
            # Prefer richer casing, but never disagree with the request URL when
            # the request URL itself has uppercase (facebook.com/NASA).
            if sum(ch.isupper() for ch in page_handle) >= sum(ch.isupper() for ch in canonical):
                canonical = page_handle
        elif not canonical:
            canonical = page_handle
    if not canonical:
        return
    canon_url = f"https://www.facebook.com/{canonical}"
    for post in posts:
        author = post.get("author") if isinstance(post.get("author"), dict) else None
        if not author:
            continue
        username = safe_str(author.get("username"))
        if username and username.lower() == canonical.lower():
            author["username"] = canonical
            url = safe_str(author.get("url"))
            if url and _fb_username_from_url(url) and _fb_username_from_url(url).lower() == canonical.lower():
                author["url"] = canon_url
        elif not username and page_handle and page_handle.lower() == canonical.lower():
            author["username"] = canonical
            if not author.get("url"):
                author["url"] = canon_url


def _finalize_fb_listing_item(item: dict[str, Any]) -> dict[str, Any]:
    """strip_empty but keep engagement.views / engagement.shares (may be null)."""
    eng = item.get("engagement") if isinstance(item.get("engagement"), dict) else {}
    views = eng.get("views")
    shares = eng.get("shares")
    out = strip_empty(item)
    out_eng = out.get("engagement") if isinstance(out.get("engagement"), dict) else {}
    out_eng["views"] = views
    out_eng["shares"] = shares
    out["engagement"] = out_eng
    return out


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _is_reel(item: dict) -> bool:
    u = (item.get("url") or item.get("postUrl") or "").lower()
    return "/reel/" in u or "/reels/" in u


def _currency_from_price(price_formatted: str | None, explicit: str | None = None) -> str | None:
    if explicit:
        return safe_str(explicit)
    text = (price_formatted or "").strip()
    if not text:
        return None
    symbols = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "₺": "TRY",
        "¥": "JPY",
        "₹": "INR",
        "A$": "AUD",
        "C$": "CAD",
    }
    for sym, code in symbols.items():
        if text.startswith(sym):
            return code
    m = re.match(r"^([A-Z]{3})\b", text)
    return m.group(1) if m else None


def _listing_created_at(item: dict) -> str | None:
    raw = item.get("creation_time") or item.get("created_time") or item.get("listed_at") or item.get("createdAt")
    if raw is None:
        return None
    if isinstance(raw, (int, float)) or (isinstance(raw, str) and raw.isdigit()):
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc).isoformat()
        except (OSError, OverflowError, ValueError):
            return None
    return safe_str(raw)


def _normalize_listing(item: dict) -> dict:
    photos = item.get("photos") if isinstance(item.get("photos"), list) else []
    photo_uris = [safe_str(p) for p in photos if isinstance(p, str) and p]
    if not photo_uris:
        photo_uris = _marketplace_photo_uris(item)
    primary = safe_str(item.get("primary_photo") or item.get("image") or item.get("imageUrl"))
    if primary and primary not in photo_uris:
        photo_uris.insert(0, primary)
    price_formatted = safe_str(item.get("price_formatted") or item.get("priceFormatted"))
    location = item.get("location") if isinstance(item.get("location"), dict) else {}
    return {
        "platform": "facebook",
        "id": safe_str(item.get("id")),
        "title": safe_str(item.get("title")),
        "url": safe_str(item.get("url")),
        "price": item.get("price"),
        "priceFormatted": price_formatted,
        "currency": _currency_from_price(price_formatted, safe_str(item.get("currency"))),
        "location": safe_str(item.get("location_display") or item.get("city") or location.get("name")),
        "city": safe_str(item.get("city") or location.get("city")),
        "state": safe_str(item.get("state") or location.get("state")),
        "latitude": item.get("latitude") if item.get("latitude") is not None else location.get("latitude"),
        "longitude": item.get("longitude") if item.get("longitude") is not None else location.get("longitude"),
        "isSold": item.get("is_sold"),
        "isLive": item.get("is_live"),
        "deliveryTypes": item.get("delivery_types") or [],
        "image": primary or (photo_uris[0] if photo_uris else None),
        "photos": photo_uris,
        "description": safe_str(
            (item.get("description").get("text") if isinstance(item.get("description"), dict) else item.get("description"))
            or (
                item.get("redacted_description").get("text")
                if isinstance(item.get("redacted_description"), dict)
                else item.get("redacted_description")
            )
        ),
        "createdAt": _listing_created_at(item),
    }


def _marketplace_photo_uris(item: dict) -> list[str]:
    """Pull image URIs from GraphQL listing photo fields when present."""
    uris: list[str] = []

    def _add(value: Any) -> None:
        uri = safe_str(value)
        if uri and uri not in uris:
            uris.append(uri)

    primary = item.get("primary_listing_photo")
    if isinstance(primary, dict):
        image = primary.get("image") if isinstance(primary.get("image"), dict) else {}
        _add(image.get("uri") or primary.get("uri") or primary.get("url"))
    _add(item.get("primary_photo") or item.get("image") or item.get("imageUrl"))

    listing_photos = item.get("listing_photos")
    if isinstance(listing_photos, dict):
        for edge in listing_photos.get("edges") or []:
            if not isinstance(edge, dict):
                continue
            node = edge.get("node") if isinstance(edge.get("node"), dict) else edge
            image = node.get("image") if isinstance(node.get("image"), dict) else {}
            _add(image.get("uri") or node.get("uri") or node.get("url"))
    elif isinstance(listing_photos, list):
        for photo in listing_photos:
            if isinstance(photo, str):
                _add(photo)
            elif isinstance(photo, dict):
                image = photo.get("image") if isinstance(photo.get("image"), dict) else {}
                _add(image.get("uri") or photo.get("uri") or photo.get("url"))

    for photo in item.get("photos") or []:
        if isinstance(photo, str):
            _add(photo)
        elif isinstance(photo, dict):
            _add(photo.get("uri") or photo.get("url") or photo.get("image"))
    return uris


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
    # The details actor never returns listing photos (no primary_listing_photo /
    # listing_photos across live samples) — omit image/photos rather than always-null.
    return {
        "platform": "facebook",
        "id": safe_str(item.get("id")),
        "url": safe_str(item.get("share_uri")) or url,
        "title": safe_str(item.get("marketplace_listing_title") or item.get("base_marketplace_listing_title")),
        "description": safe_str(desc.get("text")),
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
        "createdAt": created_iso,
    }


def _normalize_marketplace_location(item: dict) -> dict | None:
    """Legacy Apify row mapper — unused by the native location-search path.

    Prefer facebook_marketplace_location_native (Facebook cityPageId as id).
    """
    city = safe_str(item.get("city"))
    state = safe_str(item.get("state"))
    label = safe_str(item.get("location_display") or ", ".join(p for p in [city, state] if p))
    if not (label or city or state):
        return None
    city_page_id = safe_str(item.get("city_page_id") or item.get("cityPageId"))
    return strip_empty(
        {
            "id": city_page_id,
            "cityPageId": city_page_id,
            "name": label or city or state,
            "city": city,
            "state": state,
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
        }
    )


# US state abbreviations — used to pull city from free-form TEXT places.
_US_STATE_ABBR = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC",
}
_US_STATE_NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}
_STREET_SUFFIX = re.compile(
    r"\b(st|street|ave|avenue|rd|road|blvd|boulevard|dr|drive|ln|lane|way|ct|court|"
    r"pl|place|pkwy|parkway|hwy|highway|cir|circle|ter|terrace)\.?$",
    re.IGNORECASE,
)


def _looks_like_street_fragment(city: str) -> bool:
    """True when a candidate 'city' is still part of the street line."""
    s = city.strip()
    if not s or re.search(r"\d", s):
        return True
    if _STREET_SUFFIX.search(s):
        return True
    # Single generic tokens / directionals.
    if s.lower() in {"north", "south", "east", "west", "n", "s", "e", "w"}:
        return True
    return False


def _infer_city_from_text(*parts: str | None) -> str | None:
    """Best-effort City, ST from free-form address / location.name (no OpenAI)."""
    chunks = [s for s in (safe_str(p) for p in parts) if s]
    if not chunks:
        return None
    text = ", ".join(chunks)
    text = re.sub(r"[\r\n]+", ", ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Prefer "... City, ST[ ZIP]" with a real US state abbreviation.
    # Walk matches and keep the last valid one (city sits after street in US addresses).
    found: str | None = None
    for m in re.finditer(
        r"(?P<city>[A-Za-z][A-Za-z .'\-]{1,40}?),\s*(?P<st>[A-Za-z]{2})\b(?:\s+\d{5}(?:-\d{4})?)?",
        text,
    ):
        st = m.group("st").upper()
        if st not in _US_STATE_ABBR:
            continue
        city = m.group("city").strip(" ,")
        if _looks_like_street_fragment(city):
            continue
        found = f"{city}, {st}"
    if found:
        return found

    # "... City, Illinois 60018" / "... City, New York 14202"
    for m in re.finditer(
        r"(?P<city>[A-Za-z][A-Za-z .'\-]{1,40}?),\s*(?P<state>[A-Za-z][A-Za-z ]{2,20}?)\s+\d{5}\b",
        text,
    ):
        st = _US_STATE_NAMES.get(m.group("state").strip().lower())
        if not st:
            continue
        city = m.group("city").strip(" ,")
        if _looks_like_street_fragment(city):
            continue
        return f"{city}, {st}"
    return None


def _infer_city_from_ticket_url(url: str | None) -> str | None:
    """Pull City, ST from Ticketmaster-style slugs when address text is missing."""
    u = safe_str(url)
    if not u:
        return None
    try:
        nested = parse_qs(urlparse(u).query).get("u")
        if nested:
            u = unquote(nested[0])
    except Exception:  # noqa: BLE001
        pass
    path = urlparse(u).path.lower()
    # Ticketmaster spells NYC as "...-new-york-new-york-MM-DD-YYYY"
    if re.search(r"-new-york-new-york-\d{2}-\d{2}-\d{4}", path):
        return "New York, NY"
    m = re.search(r"-([a-z]+(?:-[a-z]+)*)-([a-z]{2})-\d{2}-\d{2}-\d{4}", path)
    if not m:
        return None
    st = m.group(2).upper()
    if st not in _US_STATE_ABBR:
        return None
    city = m.group(1).replace("-", " ").title()
    if _looks_like_street_fragment(city):
        return None
    return f"{city}, {st}"


def _event_local_dates(item: dict, start_time: str | None) -> tuple[str | None, str | None, str | None]:
    """Return (startDate, endDate, timezone) with local offset when possible.

    Prefer values already localized by the native path. Otherwise convert a UTC
    instant using the TZ abbreviation in ``startTime`` so the calendar day
    matches the host-facing sentence (CDT 7pm ≠ next UTC midnight). Yearless
    listing sentences (``Tue, Aug 4 at 8:00 PM EDT``) are parsed directly.
    """
    tz_name = safe_str(item.get("timezone")) or facebook_events_native._timezone_from_sentence(start_time)
    start_date = safe_str(item.get("startDate") or item.get("start_date"))
    end_date = safe_str(item.get("endDate") or item.get("end_date"))
    utc_start = safe_str(item.get("utcStartDate"))

    def _looks_utc_z(value: str | None) -> bool:
        if not value:
            return False
        return value.endswith("Z") or value.endswith("+00:00") or value.endswith("-00:00")

    # Re-localize UTC-only timestamps when we know the event timezone.
    if tz_name and (_looks_utc_z(start_date) or (not start_date and utc_start)):
        src = start_date or utc_start
        try:
            iso = src.replace("Z", "+00:00")
            dt = datetime.fromisoformat(iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            start_date = facebook_events_native._fmt_local_iso(int(dt.timestamp()), tz_name)
        except (TypeError, ValueError, OSError):
            pass

    # Parse absolute schedule sentence when timestamp path left us empty / UTC-only.
    if (not start_date or _looks_utc_z(start_date)) and start_time and not facebook_events_native.is_relative_schedule(start_time):
        parsed = facebook_events_native.parse_schedule_sentence(start_time, prefer_upcoming=True)
        if parsed.get("startDate"):
            # Prefer sentence wall-clock when it disagrees with a bare UTC Z day.
            if not start_date or _looks_utc_z(start_date):
                start_date = parsed["startDate"]
            if not end_date and parsed.get("endDate"):
                end_date = parsed["endDate"]
            if not tz_name:
                tz_name = parsed.get("timezone")

    if not start_date:
        start_date = utc_start

    if tz_name and end_date and _looks_utc_z(end_date):
        try:
            iso = end_date.replace("Z", "+00:00")
            dt = datetime.fromisoformat(iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            end_date = facebook_events_native._fmt_local_iso(int(dt.timestamp()), tz_name)
        except (TypeError, ValueError, OSError):
            pass

    # Apify sometimes only ships unix end / duration — honor when present.
    if not end_date:
        end_ts = item.get("end_timestamp") or item.get("endTimestamp")
        if end_ts is not None:
            try:
                end_date = facebook_events_native._fmt_local_iso(int(end_ts), tz_name)
            except (TypeError, ValueError):
                end_date = None
    return start_date, end_date, tz_name


def _normalize_event(item: dict) -> dict:
    """Map Facebook event actor rows into a stable response shape (same keys every time)."""
    loc = item.get("location") if isinstance(item.get("location"), dict) else {}
    tickets = item.get("ticketsInfo") if isinstance(item.get("ticketsInfo"), dict) else {}
    organizers = item.get("organizators") if isinstance(item.get("organizators"), list) else []
    if not organizers and isinstance(item.get("organizers"), list):
        organizers = item["organizers"]
    if not organizers and isinstance(item.get("hosts"), list):
        organizers = item["hosts"]
    location_name = item.get("location_name") or item.get("venue") or item.get("locationName")
    # Prefer human-readable time (apify dateTimeSentence / crawlerbros formatted_date)
    # over the ISO start_date fallback.
    start_time = safe_str(
        item.get("startTime")
        or item.get("dateTimeSentence")
        or item.get("formatted_date")
        or item.get("start_time")
        or item.get("startDateTime")
        or item.get("start_time_formatted")
    )
    if start_time and facebook_events_native.is_relative_schedule(start_time):
        # Cache-unsafe relative labels ("Happening now") — prefer absolute fields.
        alt = safe_str(
            item.get("start_time_formatted")
            or item.get("dateTimeSentence")
            or item.get("formatted_date")
        )
        start_time = alt if alt and not facebook_events_native.is_relative_schedule(alt) else None
    start_date, end_date, tz_name = _event_local_dates(item, start_time)
    if not start_time:
        start_time = start_date

    duration_seconds = safe_int(item.get("durationSeconds"))
    if duration_seconds is None and start_date and end_date:
        try:
            s = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            e = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            if s.tzinfo is None:
                s = s.replace(tzinfo=timezone.utc)
            if e.tzinfo is None:
                e = e.replace(tzinfo=timezone.utc)
            duration_seconds = max(0, int((e - s).total_seconds()))
        except (TypeError, ValueError):
            duration_seconds = None
    duration = safe_str(item.get("duration") or item.get("durationText") or item.get("display_duration"))
    if not duration and duration_seconds is not None:
        duration = facebook_events_native._duration_text(duration_seconds)

    # Apify puts the street on location.streetAddress (not location.address).
    street = safe_str(loc.get("streetAddress") or loc.get("address") or loc.get("one_line_address"))
    city = safe_str(loc.get("city") or loc.get("contextualName") or item.get("location_city"))
    loc_name = safe_str(loc.get("name") or location_name or item.get("location_name"))
    tickets_url = safe_str(
        tickets.get("buyUrl")
        or item.get("ticketsUrl")
        or item.get("ticketUrl")
        or item.get("ticket_url")
        or item.get("tickets_url")
        or item.get("event_buy_ticket_url")
    )
    # TEXT places / crawlerbros / venue-only pages often leave city null or bare;
    # recover "City, ST" from address text, then Ticketmaster-style ticket URLs.
    inferred_city = _infer_city_from_text(
        street,
        loc_name,
        safe_str(location_name),
        safe_str(item.get("address")),
        safe_str(item.get("location_name")),
    ) or _infer_city_from_ticket_url(tickets_url)
    if not city:
        city = inferred_city
    elif inferred_city and "," not in city and inferred_city.lower().startswith(city.lower()):
        city = inferred_city

    # address: real street only — never a bare city / venue-name echo.
    address = street or safe_str(item.get("address") or item.get("location_address"))
    if address and city and address.strip().lower() == city.strip().lower():
        address = None
    if address and loc_name and address.strip().lower() == loc_name.strip().lower():
        address = None

    # apify: discoveryCategories [{label,url}]; crawlerbros: categories ["Comedy"]
    raw_categories = item.get("discoveryCategories") or item.get("categories") or []
    categories: list[dict[str, Any]] = []
    if isinstance(raw_categories, list):
        for c in raw_categories:
            if isinstance(c, str):
                label = c.strip()
                if label:
                    categories.append({"label": label, "url": None})
            elif isinstance(c, dict):
                label = safe_str(c.get("label") or c.get("name"))
                if label:
                    categories.append(
                        {
                            "label": label,
                            "url": safe_str(c.get("uri") or c.get("url")),
                        }
                    )

    event_type = safe_str(item.get("eventType") or item.get("event_type") or item.get("type"))
    # Prefer discovery category (Comedy) over Relay privacy kind (PUBLIC_TYPE).
    if categories and (not event_type or event_type.upper().endswith("_TYPE")):
        event_type = categories[0]["label"]

    is_past = item.get("isPast") if item.get("isPast") is not None else item.get("is_past")
    if is_past is None:
        is_past = facebook_events_native._coerce_is_past(None, start_date)

    users_going = safe_int(
        item.get("usersGoing") or item.get("going_count") or item.get("going") or item.get("users_going")
    )
    users_interested = safe_int(
        item.get("usersInterested")
        or item.get("interested_count")
        or item.get("interested")
        or item.get("users_interested")
    )
    # responded = going + interested only. Never pass through Apify's
    # event_connected_users_public_responded (friends-who-responded ≠ total RSVPs).
    users_responded = None
    if users_going is not None or users_interested is not None:
        users_responded = (users_going or 0) + (users_interested or 0)

    organizers_out: list[dict[str, Any]] = []
    for o in organizers:
        if not isinstance(o, dict):
            continue
        verified = o.get("isVerified")
        if verified is None:
            verified = o.get("verified")
        organizers_out.append(
            {
                "id": safe_str(o.get("id")),
                "name": safe_str(o.get("name")),
                "url": safe_str(o.get("url")),
                "verified": bool(verified) if verified is not None else False,
            }
        )
    # Drop empty organizer shells.
    organizers_out = [o for o in organizers_out if o.get("id") or o.get("name") or o.get("url")]

    # Apify pads externalLinks with null slots (fixed-length scrapes); keep real URLs only.
    raw_links = item.get("externalLinks") or item.get("external_links") or []
    external_links = [
        link
        for link in (safe_str(x) for x in (raw_links if isinstance(raw_links, list) else []))
        if link
    ]
    country = safe_str(loc.get("countryCode") or loc.get("country_code") or item.get("countryCode"))
    if not country and city and re.search(r",\s*([A-Z]{2})\b", city):
        st = re.search(r",\s*([A-Z]{2})\b", city)
        if st and st.group(1) in _US_STATE_ABBR:
            country = "US"
    out: dict[str, Any] = {
        "platform": "facebook",
        "id": safe_str(item.get("id") or item.get("event_id") or item.get("eventId")),
        "url": safe_str(item.get("url") or item.get("event_url") or item.get("eventUrl")),
        "name": safe_str(item.get("name") or item.get("title")),
        "description": safe_str(item.get("description")),
        "startDate": start_date,
        "endDate": end_date,
        "timezone": tz_name,
        "startTime": start_time,
        "duration": duration,
        "durationSeconds": duration_seconds,
        "eventType": event_type,
        "isOnline": item.get("isOnline") if item.get("isOnline") is not None else item.get("is_online"),
        "isPast": is_past,
        "isCanceled": item.get("isCanceled") if item.get("isCanceled") is not None else item.get("is_canceled"),
        "address": address,
        "image": safe_str(item.get("imageUrl") or item.get("photo_url") or item.get("image")),
        "usersGoing": users_going,
        "usersInterested": users_interested,
        "usersResponded": users_responded,
        "location": {
            "name": loc_name,
            "city": city,
            "latitude": loc.get("latitude") if loc.get("latitude") is not None else item.get("latitude"),
            "longitude": loc.get("longitude") if loc.get("longitude") is not None else item.get("longitude"),
            "countryCode": country,
        },
        # organizers[] is canonical — no duplicate organizer string.
        "organizers": organizers_out,
        "ticketsUrl": tickets_url,
        "categories": categories,
        "externalLinks": external_links,
    }
    # Omit empties so native (Decodo) and Apify share the same sparse shape —
    # never emit null keys for fields upstream did not provide.
    loc_out = out["location"]
    if isinstance(loc_out, dict):
        for key in list(loc_out.keys()):
            if loc_out.get(key) in (None, "", [], {}):
                loc_out.pop(key, None)
        if not loc_out:
            out.pop("location", None)
    for key in list(out.keys()):
        if key == "location":
            continue
        if out.get(key) in (None, "", [], {}):
            out.pop(key, None)
    return out


@router.get("/details", summary="Facebook video/post details")
async def facebook_details(
    url: str = Query(...),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/page/posts/123")
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/details",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            raw = await facebook_details_native.details_native(url)
            if raw is None:
                raise HTTPException(status_code=404, detail="Post not found")
            ctx["source"] = "direct"
            return strip_empty(_normalize_post(raw))

        data = await cached_or_run(
            endpoint="facebook.details",
            params={"url": url, "v": 5},
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/summarize",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            raw = await facebook_details_native.details_native(url)
            if raw is None:
                raise HTTPException(status_code=404, detail="Post not found")
            text = (
                safe_str(raw.get("text"))
                or safe_str(raw.get("message"))
                or safe_str(raw.get("caption"))
                or ""
            ).strip()
            if not text:
                raise HTTPException(status_code=422, detail="No content to summarize")
            ai = await summarize_transcript(text, title=text[:200])
            ctx["source"] = "direct"
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
            params={"url": url, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Facebook post comments")
async def facebook_comments(
    url: str | None = Query(
        None,
        description="Facebook post or Reel URL. Omit when feedbackId is set.",
    ),
    feedbackId: str | None = Query(
        None,
        description=(
            "Post feedback id from /v1/facebook/details (base64 feedback:POSTID). "
            "Prefer when you already have it from details — skips needing the post URL. "
            "Also accepts feedback_id."
        ),
    ),
    feedback_id: str | None = Query(
        None,
        description="Snake_case alias for feedbackId (ScrapeCreators-compatible).",
        include_in_schema=False,
    ),
    limit: int = Query(
        50,
        ge=1,
        le=500,
        description="How many top-level comments to return (1–500). Flat 2 credits per call.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    fid = (feedbackId or feedback_id or "").strip() or None
    try:
        target = facebook_comments_native.resolve_comments_url(url=url, feedback_id=fid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if url and str(url).strip():
        _reject_facebook_platform_mismatch(url, "https://www.facebook.com/page/posts/123")
    settings = get_settings()
    # Flat fee: Decodo HTML path is cheap; Apify fallback is rare and covered
    # by the same 2-credit charge.
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/comments",
        platform="facebook",
        resource_url=target,
        base_credits=CREDIT_FB_COMMENTS_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await facebook_comments_native.comments_native(target, limit)
            if native is not None:
                ctx["source"] = "direct"
                out: dict[str, Any] = {
                    "platform": "facebook",
                    "url": target,
                    "totalReturned": len(native["comments"]),
                    "comments": native["comments"],
                    "hasMore": bool(native.get("hasMore")),
                    "nextCursor": native.get("nextCursor"),
                }
                if native.get("feedbackId") or fid:
                    out["feedbackId"] = native.get("feedbackId") or fid
                return out

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_COMMENTS,
                {"startUrls": [{"url": target}], "resultsLimit": limit},
                max_items=limit,
            )
            comments = []
            for c in items[:limit]:
                author_url = safe_str(c.get("profileUrl"))
                avatar = safe_str(c.get("profilePicture"))
                name = safe_str(c.get("profileName") or c.get("authorName"))
                reaction_count, reactions = _fb_apify_reactions(c)
                author_raw = c.get("author") if isinstance(c.get("author"), dict) else {}
                comments.append(
                    {
                        "id": safe_str(c.get("commentId") or c.get("id")),
                        "url": safe_str(c.get("commentUrl")),
                        "text": (c.get("text") or "").strip(),
                        "author": _fb_comment_author(
                            name=name,
                            author_id=safe_str(
                                c.get("authorId") or c.get("profileId") or author_raw.get("id")
                            ),
                            gender=safe_str(c.get("gender") or author_raw.get("gender")),
                            short_name=safe_str(
                                c.get("shortName")
                                or c.get("short_name")
                                or author_raw.get("short_name")
                                or author_raw.get("shortName")
                            ),
                            url=author_url,
                            avatar_url=avatar,
                        ),
                        "authorUrl": author_url,
                        "authorAvatarUrl": avatar,
                        "likeCount": reaction_count,
                        "reactionCount": reaction_count,
                        "reactions": reactions,
                        "publishedAt": safe_str(c.get("date") or c.get("publishedAt")),
                        "replyCount": safe_int(c.get("repliesCount") or c.get("commentsCount")) or 0,
                    }
                )
            ctx["source"] = "apify"
            out = {
                "platform": "facebook",
                "url": target,
                "totalReturned": len(comments),
                "comments": comments,
                "hasMore": len(items) >= limit,
                "nextCursor": None,
            }
            if fid:
                out["feedbackId"] = fid
            return out

        data = await cached_or_run(
            endpoint="facebook.comments",
            params={
                "url": (url or "").strip(),
                "feedbackId": fid or "",
                "limit": limit,
                "v": 5,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/page-details", summary="Facebook page info & stats")
async def facebook_page_details(
    url: str = Query(..., description="Facebook page URL, @handle, or page name"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_facebook_page(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/page-details",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_PAGE_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            data = await facebook_page_native.page_details_native(url)
            if data is None:
                raise HTTPException(status_code=404, detail="Page not found or not public")
            ctx["source"] = "direct"
            return data

        data = await cached_or_run(
            endpoint="facebook.page-details",
            params={"url": url, "v": 6},
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/profile-posts",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_FB_PROFILE_POSTS_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            raws = await facebook_profile_posts_native.profile_posts_native(url, limit)
            if raws is None:
                raise HTTPException(status_code=404, detail="Posts not found")
            posts = [_finalize_fb_listing_item(_normalize_post(i)) for i in raws]
            _unify_listing_authors(posts, url)
            ctx["source"] = "direct"
            return {
                "url": url,
                "totalReturned": len(posts),
                "posts": posts,
                "scrapedAt": _now_iso(),
            }

        data = await cached_or_run(
            endpoint="facebook.profile-posts",
            params={"url": url, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/profile-reels", summary="Latest Reels from a Facebook profile/page")
async def facebook_profile_reels(
    url: str = Query(..., description="Facebook profile/page URL, @handle, or page name"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_facebook_page(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/profile-reels",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_FB_PROFILE_REELS_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            raws = await facebook_profile_reels_native.profile_reels_native(url, limit)
            if raws is None:
                raise HTTPException(status_code=404, detail="Reels not found")
            reels = [_finalize_fb_listing_item(_normalize_post(i)) for i in raws]
            _unify_listing_authors(reels, url)
            ctx["source"] = "direct"
            return {
                "url": url,
                "totalReturned": len(reels),
                "reels": reels,
                "scrapedAt": _now_iso(),
            }

        data = await cached_or_run(
            endpoint="facebook.profile-reels",
            params={"url": url, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/group-posts", summary="Posts from a public Facebook group")
async def facebook_group_posts(
    url: str = Query(..., description="Public Facebook group URL"),
    limit: int = Query(20, ge=1, le=200),
    sortBy: str | None = Query(
        None,
        description=(
            "Feed sort: TOP_POSTS | RECENT_ACTIVITY | CHRONOLOGICAL (default) | "
            "CHRONOLOGICAL_LISTINGS. Passed to Facebook as sorting_setting."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/groups/group-name")
    sort_mode = facebook_group_posts_native._normalize_sort(sortBy)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/group-posts",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_FB_GROUP_POSTS_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            raws = await facebook_group_posts_native.group_posts_native(url, limit, sort_by=sort_mode)
            if raws is None:
                raise HTTPException(status_code=404, detail="Group posts not found")
            posts = [strip_empty(_normalize_post(i)) for i in raws]
            ctx["source"] = "direct"
            return {
                "url": url,
                "sortBy": sort_mode,
                "totalReturned": len(posts),
                "posts": posts,
            }

        data = await cached_or_run(
            endpoint="facebook.group-posts",
            params={"url": url, "limit": limit, "sortBy": sort_mode, "v": 8},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/comment-replies", summary="Replies to a Facebook comment")
async def facebook_comment_replies(
    url: str = Query(..., description="Facebook post URL the comment belongs to"),
    comment_id: str = Query(..., description="ID of the parent comment"),
    limit: int = Query(
        50,
        ge=1,
        le=500,
        description="How many direct replies to return (1–500). Flat 2 credits per call.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_facebook_platform_mismatch(url, "https://www.facebook.com/page/posts/123")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/comment-replies",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_FB_COMMENTS_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await facebook_comments_native.comment_replies_native(url, comment_id, limit)
            if native is not None:
                ctx["source"] = "direct"
                return {
                    "platform": "facebook",
                    "url": url,
                    "commentId": comment_id,
                    "totalReturned": len(native["replies"]),
                    "replies": native["replies"],
                    "hasMore": bool(native.get("hasMore")),
                    "nextCursor": native.get("nextCursor"),
                }

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
            page = replies[:limit]
            return {
                "platform": "facebook",
                "url": url,
                "commentId": comment_id,
                "totalReturned": len(page),
                "replies": page,
                "hasMore": len(replies) > limit,
                "nextCursor": None,
            }

        data = await cached_or_run(
            endpoint="facebook.comment-replies",
            params={"url": url, "comment_id": comment_id, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _normalize_photo(item: dict) -> dict:
    """Map Facebook photo rows. ``accessibilityCaption`` is alt-text, not a post caption.

    Facebook's /photos surface typically omits publish time and engagement — do
    not invent zeros. Prefer full-size ``image``; optional ``thumbnailUrl`` when
    a smaller CDN asset is present.
    """
    image = safe_str(
        item.get("imageUrl")
        or item.get("image_url")
        or item.get("image")
        or item.get("imageUri")
        or item.get("src")
    )
    thumb = safe_str(
        item.get("thumbnailUrl")
        or item.get("thumbnail")
        or item.get("thumbnail_url")
    )
    # Prefer explicit accessibility fields. Never treat legacy ``caption`` as a
    # user post — native path used to mislabel alt-text as caption.
    accessibility = safe_str(
        item.get("accessibilityCaption")
        or item.get("accessibility_caption")
        or item.get("altText")
        or item.get("alt_text")
        # Legacy native rows only — still alt-text, not a written caption.
        or item.get("caption")
        or item.get("text")
        or item.get("ocrText")
    )
    out: dict[str, Any] = {
        "platform": "facebook",
        "id": safe_str(item.get("id") or item.get("photoId") or item.get("photo_id")),
        "url": safe_str(item.get("url") or item.get("photoUrl") or item.get("postUrl")),
        "image": image,
        "accessibilityCaption": accessibility,
    }
    if thumb and thumb != image:
        out["thumbnailUrl"] = thumb
    published = safe_str(
        item.get("timestamp") or item.get("date") or item.get("publishedAt") or item.get("time")
    )
    if published:
        out["publishedAt"] = published
    likes = safe_int(
        item.get("likesCount") or item.get("likes") or item.get("reactionsCount") or item.get("reactionLikeCount")
    )
    if likes is not None:
        out["likes"] = likes
    comments = safe_int(item.get("commentsCount") or item.get("comments"))
    if comments is not None:
        out["comments"] = comments
    width = safe_int(item.get("width") or item.get("image_width") or item.get("imageWidth"))
    if width is not None:
        out["width"] = width
    height = safe_int(item.get("height") or item.get("image_height") or item.get("imageHeight"))
    if height is not None:
        out["height"] = height
    return out


@router.get(
    "/profile-photos",
    summary="Photos from a Facebook profile/page",
    description=(
        "Returns photo grid items with image URL and accessibilityCaption "
        "(Facebook alt-text — not a user-written post caption). Publish time "
        "and engagement are usually absent on this surface."
    ),
)
async def facebook_profile_photos(
    url: str = Query(..., description="Facebook profile/page URL, @handle, or page name"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_facebook_page(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/profile-photos",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_FB_PROFILE_PHOTOS_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            raws = await facebook_profile_photos_native.profile_photos_native(url, limit)
            if raws is None:
                raise HTTPException(status_code=404, detail="Photos not found")
            photos = [strip_empty(_normalize_photo(i)) for i in raws]
            ctx["source"] = "direct"
            return {
                "url": url,
                "totalReturned": len(photos),
                "photos": photos,
                "note": (
                    "accessibilityCaption is Facebook's image alt-text, not a "
                    "post caption. Date and engagement are usually unavailable "
                    "on the photos surface."
                ),
            }

        data = await cached_or_run(
            endpoint="facebook.profile-photos",
            params={"url": url, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/profile-events",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_FB_EVENTS_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # 1) Decodo JS-rendered page /events (DC/residential return 400).
            native = await facebook_events_native.fetch_page_events(url, limit=limit)
            if native:
                ctx["source"] = "direct"
                events = [_normalize_event(i) for i in native]
                return {"platform": "facebook", "url": url, "totalReturned": len(events), "events": events}

            # 2) Apify — prefer a recent snapshot before starting a 280s browser run.
            events_url = url.rstrip("/") + "/events"
            run_input = {"startUrls": [events_url], "maxEvents": limit}
            client = ApifyClient(timeout=280, max_attempts=1)
            cached_items = await client.last_succeeded_items(
                settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                max_age_secs=48 * 3600,
                max_items=limit,
                input_match={"startUrls": [events_url]},
            )
            if cached_items:
                if not await client.find_active_run(
                    settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                    input_match={"startUrls": [events_url]},
                ):
                    await client.start_run(settings.APIFY_ACTOR_FACEBOOK_EVENTS, run_input)
                events = [_normalize_event(i) for i in cached_items[:limit] if not i.get("error")]
                ctx["source"] = "apify"
                return {"platform": "facebook", "url": url, "totalReturned": len(events), "events": events}

            items = await client.run_actor_sync(
                settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                run_input,
                max_items=limit,
            )
            events = [_normalize_event(i) for i in items[:limit] if not i.get("error")]
            ctx["source"] = "apify"
            return {"platform": "facebook", "url": url, "totalReturned": len(events), "events": events}

        data = await cached_or_run(
            endpoint="facebook.profile-events",
            params={"url": url, "limit": limit, "v": 7},
            runner=_run,
            ctx=ctx,
            # Events actor runs take minutes (280s timeout); serve the last
            # list instantly after TTL expiry and refresh in the background.
            stale_while_revalidate=True,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_FB_EVENTS_NATIVE
        else:
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/marketplace-item",
        platform="facebook",
        resource_url=url,
        base_credits=CREDIT_FB_MARKETPLACE_ITEM_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await facebook_marketplace_native.marketplace_item_native(url)
            if native:
                ctx["source"] = "direct"
                return native
            raise HTTPException(status_code=404, detail="Listing not found")

        data = await cached_or_run(
            endpoint="facebook.marketplace-item",
            params={"url": url, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/marketplace-search", summary="Search Facebook Marketplace listings")
async def facebook_marketplace_search(
    q: str = Query(..., min_length=2, description="Product/keyword to search for"),
    location: str = Query(..., min_length=2, description="City or place name, e.g. 'Austin, TX'"),
    limit: int = Query(
        20,
        ge=1,
        le=200,
        description=(
            "How many listings to return (1–200). Flat 2 credits when details=false; "
            "with details=true billed as 2 + 2 per listing. "
            "First SSR/scroll page typically yields ~15–60 cards."
        ),
    ),
    minPrice: float | None = Query(None, ge=0, description="Minimum price in local currency units."),
    maxPrice: float | None = Query(None, ge=0, description="Maximum price in local currency units."),
    sortBy: str | None = Query(
        None,
        description=(
            "Sort: suggested (default), distance, creation_time, "
            "price_ascend, price_descend."
        ),
    ),
    daysSinceListed: str | None = Query(
        None,
        description="Recency filter: 1 (24h), 7, or 30 days.",
    ),
    condition: str | None = Query(
        None,
        description="Item condition: new, like_new, good, fair (comma-separated ok).",
    ),
    deliveryMethod: str | None = Query(
        None,
        description=(
            "Delivery filter: local_pickup, shipping, or all. "
            "Shipped listings (SHIPPING / SHIPPING_ONSITE) can appear nationwide "
            "outside radiusMiles — use local_pickup for nearby-only results. "
            "Each row includes isLocal / shipsOutsideRadius so you can tell."
        ),
    ),
    availability: str | None = Query(
        None,
        description="Availability: available (default), sold, or all.",
    ),
    radiusMiles: int | None = Query(
        None,
        description=(
            "Search radius in miles (1,2,5,10,20,40,60,80,100,250,500). Default ~40. "
            "Does not exclude nationwide shipped listings — see deliveryMethod=local_pickup."
        ),
    ),
    category: str | None = Query(
        None,
        description="Top-level Marketplace category slug, e.g. electronics, vehicles, home.",
    ),
    cursor: str | None = Query(
        None,
        description="Pagination cursor from a previous nextCursor (same query + filters).",
    ),
    details: bool = Query(
        False,
        description=(
            "When true, enrich each listing with description, condition, coordinates, "
            "and the full photo gallery via item pages (2 + 2 credits per listing). "
            "Default false → search cards at flat 2 credits (still includes cover photo)."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    filters = facebook_marketplace_native.normalize_filters(
        min_price=minPrice,
        max_price=maxPrice,
        sort_by=sortBy,
        days_since_listed=daysSinceListed,
        condition=condition,
        delivery_method=deliveryMethod,
        availability=availability,
        radius_miles=radiusMiles,
        category=category,
    )
    # Reserve max; override to actual returned count after the run.
    base = (
        facebook_marketplace_native.credits_for_details(limit)
        if details
        else CREDIT_FB_MARKETPLACE_NATIVE
    )
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/marketplace-search",
        platform="facebook",
        resource_url=None,
        base_credits=base,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            if details:
                page = await facebook_marketplace_native.marketplace_search_details_native(
                    q, location, limit, filters=filters or None, cursor=cursor
                )
            else:
                page = await facebook_marketplace_native.marketplace_search_native(
                    q, location, limit, filters=filters or None, cursor=cursor
                )
            if page is None:
                raise HTTPException(
                    status_code=502,
                    detail="Facebook Marketplace search temporarily unavailable",
                )
            ctx["source"] = "direct"
            listings = page.get("listings") or []
            return strip_empty(
                {
                    "query": q,
                    "location": location,
                    "filters": filters or None,
                    "totalReturned": len(listings),
                    "hasMore": bool(page.get("hasMore")),
                    "nextCursor": page.get("nextCursor"),
                    "listings": listings,
                }
            )

        data = await cached_or_run(
            endpoint="facebook.marketplace-search",
            params={
                "q": q,
                "location": location,
                "limit": limit,
                "details": details,
                "filters": filters,
                "cursor": cursor or "",
                "v": 7,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        if details:
            ctx["credits_override"] = facebook_marketplace_native.credits_for_details(
                len(data["listings"])
            )
        return ApiResponse(data=data)


@router.get(
    "/marketplace-location-search",
    summary="Resolve Facebook Marketplace locations",
    description=(
        "Disambiguate a city/place name into Marketplace hubs with lat/lng and "
        "Facebook cityPageId (same id search listings expose). marketplace-search "
        "already accepts a city string — use this when the name is ambiguous "
        "(Austin TX vs Austin MN) or you need coordinates / cityPageId before searching. "
        "Flat 2 credits."
    ),
)
async def facebook_marketplace_location_search(
    q: str = Query(
        ...,
        min_length=2,
        description=(
            "City/place query. Include a state for a single hit (e.g. 'Austin, TX'); "
            "bare names like 'Austin' may return multiple candidates for disambiguation."
        ),
    ),
    limit: int = Query(10, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/marketplace-location-search",
        platform="facebook",
        resource_url=None,
        base_credits=CREDIT_FB_MARKETPLACE_LOCATION_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            results = await facebook_marketplace_location_native.marketplace_location_search_native(
                q, limit=limit
            )
            if not results:
                raise HTTPException(status_code=404, detail="Marketplace location not found")
            ctx["source"] = "direct"
            return {"query": q, "totalReturned": len(results), "locations": results}

        data = await cached_or_run(
            endpoint="facebook.marketplace-location-search",
            params={"q": q, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)



@router.get("/event-search", summary="Search Facebook events by keyword/location")
async def facebook_event_search(
    q: str = Query(..., min_length=2, description="Topic and/or place, e.g. 'comedy Chicago'"),
    location: str | None = Query(
        None,
        description="Optional city/place filter tokens required in title/venue (e.g. Chicago).",
    ),
    from_date: str | None = Query(
        None,
        alias="from",
        description="Inclusive local start date filter YYYY-MM-DD.",
    ),
    to_date: str | None = Query(
        None,
        alias="to",
        description="Inclusive local start date filter YYYY-MM-DD.",
    ),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/facebook/event-search",
        platform="facebook",
        resource_url=None,
        base_credits=CREDIT_FB_EVENTS_NATIVE,
    ) as ctx:
        def _filter_apify(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
            tokens = facebook_events_native._query_tokens(
                f"{q} {(location or '').strip()}".strip()
            )
            out: list[dict[str, Any]] = []
            for i in items:
                if i.get("error"):
                    continue
                if tokens and not facebook_events_native._event_matches_query(i, tokens):
                    continue
                ev = _normalize_event(i)
                if not facebook_events_native._event_in_date_range(
                    ev, from_date=from_date, to_date=to_date
                ):
                    continue
                out.append(ev)
                if len(out) >= limit:
                    break
            return out

        async def _run() -> dict[str, Any]:
            # 1) Native — SERP → details, then relevance-filtered discovery.
            native = await facebook_events_native.fetch_search_events(
                q,
                limit=limit,
                location=location,
                from_date=from_date,
                to_date=to_date,
            )
            if native:
                ctx["source"] = "direct"
                events = [_normalize_event(i) for i in native]
                payload: dict[str, Any] = {
                    "query": q,
                    "totalReturned": len(events),
                    "events": events,
                }
                if location:
                    payload["location"] = location
                if from_date:
                    payload["from"] = from_date
                if to_date:
                    payload["to"] = to_date
                return payload

            # 2) Apify snapshot-first when native search is empty/login-walled.
            run_input = {"searchQueries": [q], "maxEvents": max(limit, 20)}
            apify = ApifyClient(timeout=280, max_attempts=1)
            cached_items = await apify.last_succeeded_items(
                settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                max_age_secs=48 * 3600,
                max_items=max(limit, 40),
                input_match={"searchQueries": [q]},
            )
            if cached_items:
                if not await apify.find_active_run(
                    settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                    input_match={"searchQueries": [q]},
                ):
                    await apify.start_run(settings.APIFY_ACTOR_FACEBOOK_EVENTS, run_input)
                events = _filter_apify(cached_items)
                ctx["source"] = "apify"
                return {"query": q, "totalReturned": len(events), "events": events}

            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                    run_input,
                    max_items=max(limit, 40),
                )
            except ApifyError:
                items = await apify.last_succeeded_items(
                    settings.APIFY_ACTOR_FACEBOOK_EVENTS,
                    max_age_secs=48 * 3600,
                    max_items=max(limit, 40),
                )
                if not items:
                    raise
            events = _filter_apify(items)
            ctx["source"] = "apify"
            return {"query": q, "totalReturned": len(events), "events": events}

        data = await cached_or_run(
            endpoint="facebook.event-search",
            params={
                "q": q,
                "limit": limit,
                "location": location or "",
                "from": from_date or "",
                "to": to_date or "",
                "v": 7,
            },
            runner=_run,
            ctx=ctx,
            stale_while_revalidate=True,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_FB_EVENTS_NATIVE
        else:
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
            # Decodo headless first (same path as event-search / profile-events).
            native = await facebook_events_native.fetch_event_details(url)
            if native:
                ctx["source"] = "direct"
                return _normalize_event(native)

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
            except Exception:  # noqa: BLE001
                pass
            if partial_event is None:
                try:
                    async with httpx.AsyncClient(timeout=6, follow_redirects=True, headers=headers) as client:
                        resp = await client.get(url)
                    if resp.status_code < 400:
                        partial_event = _partial_event_from_page(url, resp.text)
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
            params={"url": url, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
