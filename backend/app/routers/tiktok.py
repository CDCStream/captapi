"""TikTok endpoints."""

from __future__ import annotations

import asyncio
import math
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.core.quota import check_daily_quota, consume_daily_quota
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.services.openai_client import (
    WHISPER_MAX_BYTES,
    infer_region,
    summarize_transcript,
    transcribe_audio,
)
from app.services import tiktok_native
from app.utils.retry import retry_none
from app.core.cache_params import CACHE_MAX_AGE_DESC, resolve_cache_options
from app.services.tiktok_native import (
    AUTHOR_NULLABLE_KEYS,
    ENGAGEMENT_RATE_BASIS,
    audience_commenters_native,
    build_author,
    channel_details_native,
    channel_posts_native,
    coerce_stats_v2,
    comment_replies_native,
    creator_engagement_rate,
    extract_bio_contact,
    hydrate_creators_trust,
    _collect_hashtags,
    _collect_mentions,
    hashtag_posts_native,
    item_has_hashtag,
    normalize_hashtag_query,
    live_status_native,
    music_posts_native,
    popular_creators_native,
    enrich_hashtag_population_stats,
    popular_hashtags_native,
    profile_region_native,
    trending_feed_native,
    search_suggestions_native,
    search_users_native,
    normalize_song_details,
    song_details_native,
    top_search_native,
    user_connections_native,
    video_details_native,
)
from app.utils.countries import country_name
from app.utils.formatters import (
    duration_seconds,
    first_present,
    normalize_language_code,
    strip_empty,
    safe_float,
    safe_int,
    safe_list,
    safe_str,
)
from app.utils.url import (
    detect_url_platform,
    extract_tiktok_id,
    extract_tiktok_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_TRANSCRIPT = 2
CREDIT_SUMMARIZE = 4
CREDIT_VIDEO_DETAILS = 1
CREDIT_CHANNEL_DETAILS = 1
CREDIT_COMMENTS = 2  # native (TikTok's own API); flat fee, our cost ~$0
CREDIT_COMMENT_REPLIES = 2  # native comment/list/reply; flat fee, our cost ~$0
CREDIT_CHANNEL_POSTS = 2  # native aweme/post; flat fee, our cost ~$0
CREDIT_MUSIC_POSTS = 2  # native music/aweme; flat fee, our cost ~$0
# Native music/aweme song metadata (~$0); ScrapeCreators parity = 1 credit.
# Apify song actors stay at 2 (multiple fallbacks, real actor cost).
CREDIT_SONG_DETAILS_NATIVE = 1
CREDIT_SONG_DETAILS_APIFY = 2
CREDIT_SEARCH_SUGGESTIONS = 2  # native search preview; flat fee, our cost ~$0
CREDIT_PROFILE_REGION = 2  # native profile page + fast LLM region estimate
CREDIT_AUDIENCE = 3  # video list + native commenter sampling (12 videos)
CREDIT_SEARCH = 2

# Audience-country sampling for /audience-demographics: default videos / target
# commenters. Callers can raise ``videos`` (12|30|60) for a larger sample.
AUDIENCE_VIDEO_SAMPLE = 12
AUDIENCE_TARGET_TOTAL = 500
AUDIENCE_VIDEOS_ALLOWED = (12, 30, 60)


def _audience_credits(videos: int) -> int:
    """Scale credits with sample depth: 12→3, 30→5, 60→8."""
    if videos <= 12:
        return 3
    if videos <= 30:
        return 5
    return 8


def _audience_target_total(videos: int) -> int:
    """More videos → higher commenter target (soft cap 2000)."""
    return min(2000, max(AUDIENCE_TARGET_TOTAL, videos * 40))


def _sample_confidence(n: int) -> str:
    """Honest sample-strength label for commenter geography."""
    if n >= 1000:
        return "high"
    if n >= 400:
        return "medium"
    return "low"

# ---------------------------------------------------------------------------
# Per-result credit rates for list endpoints.
#
# These actors are billed by Apify PER RESULT, so our credit charge must scale
# with the number of items, otherwise margin collapses. Rates are chosen so
# that revenue (rate x $0.0045/credit) >= Apify per-result cost x 1.8 (~80%
# markup). The endpoint charges `ctx["credits_override"]` based on the actual
# number of items returned (never more than the upfront `limit` estimate).
# ---------------------------------------------------------------------------
# Verified Apify prices (Free/no-subscription tier = worst case for us). Sell
# price is $0.0045/credit, so an ~80% markup needs rate >= cost_per_result*400.
RATE_FOLLOWERS = 0.4       # clockworks followers-scraper  $1.00/1k ($0.001)
RATE_COMMENTS = 0.2        # clockworks comments-scraper   $0.50/1k ($0.0005)
RATE_CHANNEL_POSTS = 0.7   # clockworks tiktok-scraper     $1.70/1k ($0.0017)
RATE_USER_SEARCH = 0.4     # clockworks user search (per profile) — Apify fallback only
CREDIT_USER_SEARCH_NATIVE = 1  # signer /api/search/user/full/ — SC parity
# Trending/popular endpoints hit a third-party HTTP actor; cost not yet verified
# in the Apify console, so rates are conservative until confirmed.
RATE_TREND = 0.7
RATE_TREND_MARGIN = 1.4
# FYP sample + profile hydrate — flat when native succeeds. Apify Creative
# Center fallthrough stays per-result (RATE_TREND_MARGIN). SC bills ~1 credit
# for TCM-backed /creators/popular; we are not that source.
CREDIT_POPULAR_CREATORS_NATIVE = 2
# Creative Center trend charts (hashtags / songs / creators) — one Decodo XHR.
CREDIT_CC_TREND = 2

# Reply scraper crawls a video's comments to find one comment's replies, and is
# billed per ROW pushed (comment or reply) at $2.40/1k = $0.0024/row. We
# therefore bill on the actual crawl size, not the returned reply count, and cap
# the crawl so a viral video can't run up an unbounded bill.
REPLIES_MAX_COMMENTS = 40
REPLIES_MAX_ITEMS = 400
RATE_REPLIES_ROW = 1.0     # ~80% markup on $0.0024/row
CREDIT_REPLIES_MIN = 30


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    """Credits for `n` returned items at `rate` credits/item (with a floor)."""
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _require_tiktok_video_url(url: str) -> str:
    video_id = extract_tiktok_id(url)
    if not video_id:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                url,
                "tiktok",
                "https://www.tiktok.com/@user/video/1234567890",
            ),
        )
    return video_id


def _require_tiktok_profile(value: str) -> str:
    handle = extract_tiktok_username(value)
    if not handle:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                value,
                "tiktok",
                "https://www.tiktok.com/@username",
            ),
        )
    return handle


def _require_tiktok_music_url(url: str) -> str:
    """Accept only TikTok music/sound URLs — never video or profile links."""
    value = (url or "").strip()
    lowered = value.lower()
    detected = detect_url_platform(value) if value else None
    if detected and detected != "tiktok":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                value,
                "tiktok",
                "https://www.tiktok.com/music/original-sound-7300000000000000000",
            ),
        )
    if "/video/" in lowered or "/photo/" in lowered:
        raise HTTPException(
            status_code=400,
            detail="Expected a TikTok music/sound URL, not a video URL. Example: https://www.tiktok.com/music/original-sound-7300000000000000000",
        )
    if "/music/" in lowered or "music.tiktok.com" in lowered or "/sound/" in lowered:
        return value
    raise HTTPException(
        status_code=400,
        detail="Expected a TikTok music/sound URL. Example: https://www.tiktok.com/music/original-sound-7300000000000000000",
    )


def _is_real_popular_creator_items(items: list[dict[str, Any]]) -> bool:
    """Reject Creative Center keyword stubs (tiktok_trending, …) so fallback runs."""
    if not items:
        return False
    real = 0
    for item in items:
        if not isinstance(item, dict) or item.get("error"):
            continue
        nested = item.get("author") if isinstance(item.get("author"), dict) else {}
        handle = safe_str(
            item.get("creatorHandle")
            or nested.get("uniqueId")
            or nested.get("username")
            or item.get("uniqueId")
            or item.get("username")
            or item.get("handle")
        )
        if handle:
            handle = handle.lstrip("@").lower()
        display = (
            safe_str(
                item.get("name")
                or nested.get("nickname")
                or item.get("displayName")
                or item.get("nickname")
            )
            or ""
        ).lower()
        if "creator discovery" in display or "trending tiktok creator" in display:
            continue
        if handle and handle.startswith("tiktok_") and not (
            item.get("followerCount")
            or nested.get("followerCount")
            or item.get("followers")
            or item.get("creatorAvatarUrl")
        ):
            continue
        if handle:
            real += 1
    return real >= max(1, min(3, len(items) // 2))


# Residential proxy improves reliability of the dedicated comment/reply scraper
# on large or rate-limited videos (optional but recommended by the actor).
TIKTOK_RESIDENTIAL_PROXY = {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}


def _normalize_connection(item: dict) -> dict:
    """Map a Clockworks follower/following relationship row to our user shape.

    Each row exposes the connected profile under ``authorMeta`` plus a
    ``connectionType`` ("follower" / "following").
    """
    a = item.get("authorMeta") or {}
    username = a.get("name") or a.get("uniqueId")
    return {
        "username": safe_str(username),
        "displayName": safe_str(a.get("nickName") or a.get("nickname")),
        "bio": safe_str(a.get("signature")),
        "url": safe_str(a.get("profileUrl"))
        or (f"https://www.tiktok.com/@{username}" if username else None),
        "followers": safe_int(a.get("fans")),
        "following": safe_int(a.get("following")),
        "verified": a.get("verified"),
        "profileImage": safe_str(a.get("avatar") or a.get("originalAvatarUrl")),
    }


def _normalize_user(item: dict) -> dict:
    """Map a TikTok user-search result to our user shape.

    The search actor may nest the profile under ``authorMeta`` or expose it at
    the top level, so we look in both places.
    """
    a = item.get("authorMeta") or item.get("author") or item.get("user_info") or item
    stats = item.get("authorStats") or item.get("stats") or {}
    username = a.get("name") or a.get("uniqueId") or a.get("unique_id") or item.get("uniqueId")
    uid = safe_str(a.get("id") or a.get("uid") or a.get("user_id") or a.get("userId") or item.get("id"))
    sec_uid = safe_str(a.get("secUid") or a.get("sec_uid") or item.get("secUid"))
    out = {
        "id": uid,
        "secUid": sec_uid,
        "username": safe_str(username),
        "displayName": safe_str(a.get("nickName") or a.get("nickname")),
        "bio": safe_str(a.get("signature")),
        "url": safe_str(a.get("profileUrl"))
        or (f"https://www.tiktok.com/@{username}" if username else None),
        "followers": safe_int(
            a.get("fans") or a.get("followerCount") or a.get("follower_count") or stats.get("followerCount")
        ),
        "following": safe_int(
            a.get("following")
            or a.get("followingCount")
            or a.get("following_count")
            or stats.get("followingCount")
        ),
        "videos": safe_int(
            a.get("video")
            or a.get("videoCount")
            or a.get("aweme_count")
            or stats.get("videoCount")
        ),
        "likes": safe_int(
            a.get("heart")
            or a.get("heartCount")
            or a.get("total_favorited")
            or stats.get("heartCount")
        ),
        "verified": a.get("verified"),
        "profileImage": safe_str(a.get("avatar") or a.get("avatarLarger") or a.get("originalAvatarUrl")),
    }
    for key in ("id", "secUid", "following", "videos", "likes"):
        if out.get(key) in (None, "", []):
            out.pop(key, None)
    return out


def _normalize_profile_region(item: dict, handle: str) -> dict:
    user = item.get("user") or item.get("authorMeta") or item
    stats = item.get("stats") or item.get("authorStats") or {}
    raw = dict(item)
    if isinstance(raw.get("statsV2"), dict):
        raw["statsV2"] = coerce_stats_v2(raw["statsV2"])
    return {
        "platform": "tiktok",
        "username": safe_str(user.get("uniqueId") or user.get("name") or handle),
        "displayName": safe_str(user.get("nickname") or user.get("nickName")),
        "url": safe_str(user.get("profileUrl")) or f"https://www.tiktok.com/@{handle}",
        "region": safe_str(
            user.get("region")
            or user.get("country")
            or user.get("countryCode")
            or item.get("region")
            or item.get("country")
            or item.get("countryCode")
        ),
        "language": safe_str(
            user.get("language")
            or user.get("languageCode")
            or item.get("language")
            or item.get("languageCode")
            # Language of the sampled video caption — best public signal the
            # profile actor exposes.
            or item.get("textLanguage")
        ),
        "followers": safe_int(
            user.get("followerCount")
            or user.get("fans")
            or stats.get("followerCount")
            or stats.get("followers")
        ),
        "following": safe_int(user.get("followingCount") or user.get("following")),
        "likes": safe_int(
            first_present(user.get("heartCount"), user.get("heart"), user.get("likes"), stats.get("heartCount"))
        ),
        "videos": safe_int(first_present(user.get("videoCount"), user.get("video"), stats.get("videoCount"))),
        "verified": first_present(user.get("verified"), user.get("isVerified")),
        "private": first_present(user.get("privateAccount"), user.get("isPrivate")),
        "profileImage": safe_str(user.get("avatarLarger") or user.get("avatar") or user.get("avatarMedium")),
        "raw": raw,
    }


def _tt_published_iso(item: dict) -> str | None:
    """publishedAt as …T00:45:18.000Z. Prefer the actor's ISO string; otherwise
    convert the unix ``createTime`` (never stringify the raw integer)."""
    iso = safe_str(item.get("createTimeISO"))
    if iso:
        return iso
    ts = safe_int(item.get("createTime"))
    if ts:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    return None


def _tt_hashtags(item: dict, caption: str | None) -> list[str]:
    """Canonical hashtags via ``text_extra`` / structured fields (see native helper)."""
    return _collect_hashtags(item, caption)


def _tt_mentions(item: dict) -> list[dict[str, Any]]:
    return _collect_mentions(item)


_ENGAGEMENT_COUNT_KEYS = ("views", "likes", "comments", "shares", "saves")


def _tt_coerce_engagement(eng: Any) -> dict[str, int]:
    """Always emit the five engagement ints — missing/null → 0 (never omit shares)."""
    src = eng if isinstance(eng, dict) else {}
    return {k: safe_int(src.get(k)) or 0 for k in _ENGAGEMENT_COUNT_KEYS}


def _tt_finalize_post(post: dict[str, Any]) -> dict[str, Any]:
    """strip_empty, then restore stable keys clients rely on (0 / [] / null / false)."""
    author_in = post.get("author") if isinstance(post.get("author"), dict) else None
    keep_author_nulls = {
        k: None
        for k in AUTHOR_NULLABLE_KEYS
        if author_in is not None and k in author_in and author_in.get(k) is None
    }
    raw_engagement = post.get("engagement")
    raw_duration = post.get("durationSeconds")
    raw_is_ad = post.get("isAd")
    raw_is_paid = post.get("isPaidPartnership")
    out = strip_empty(post)
    out["engagement"] = _tt_coerce_engagement(out.get("engagement") or raw_engagement)
    if not isinstance(out.get("hashtags"), list):
        out["hashtags"] = []
    if not isinstance(out.get("mentions"), list):
        out["mentions"] = []
    if keep_author_nulls:
        author_out = out.get("author")
        if not isinstance(author_out, dict):
            author_out = {}
            out["author"] = author_out
        author_out.update(keep_author_nulls)
    # Always float seconds (12.0 not 12) — same type on top-search and music-posts.
    if raw_duration is not None:
        out["durationSeconds"] = duration_seconds(raw_duration)
    elif out.get("durationSeconds") is not None:
        out["durationSeconds"] = duration_seconds(out["durationSeconds"])
    out["isAd"] = bool(raw_is_ad) if raw_is_ad is not None else bool(out.get("isAd"))
    out["isPaidPartnership"] = (
        bool(raw_is_paid) if raw_is_paid is not None else bool(out.get("isPaidPartnership"))
    )
    return out


def _normalize(item: dict) -> dict:
    """Map raw TikTok actor output to our standard shape."""
    author = item.get("authorMeta") or item.get("author") or {}
    stats = item.get("stats") or {}
    music = item.get("musicMeta") or item.get("music") or {}
    if not isinstance(music, dict):  # aweme rows carry a plain mp3 URL here
        music = {}
    if not isinstance(author, dict):
        author = {}
    video_meta = item.get("videoMeta") or {}
    covers = safe_list(item.get("covers"))
    caption = safe_str(item.get("text") or item.get("desc"))
    # Metadata+stats only — CDN play URLs are IP/cookie-bound (usually 403),
    # so we omit videoUrl rather than always returning null.
    from app.services.tiktok_native import extract_shop_product_url

    author_region = safe_str(author.get("region") or author.get("regionCode"))
    author_out = build_author(author, author_stats=stats if isinstance(stats, dict) else None)
    if author_region:
        author_out["region"] = author_region
    out = {
        "platform": "tiktok",
        "url": safe_str(item.get("webVideoUrl") or item.get("url")),
        "id": safe_str(item.get("id") or item.get("videoId")),
        "caption": caption,
        "publishedAt": _tt_published_iso(item),
        "durationSeconds": duration_seconds(video_meta.get("duration") or item.get("duration")),
        "thumbnailUrl": safe_str(
            video_meta.get("coverUrl")
            or video_meta.get("originalCoverUrl")
            or (covers[0] if covers else None)
        ),
        "author": author_out,
        "engagement": _tt_coerce_engagement(
            {
                "views": item.get("playCount") or stats.get("playCount"),
                "likes": item.get("diggCount") or stats.get("diggCount"),
                "comments": item.get("commentCount") or stats.get("commentCount"),
                "shares": item.get("shareCount") or stats.get("shareCount"),
                "saves": item.get("collectCount") or stats.get("collectCount"),
            }
        ),
        "hashtags": _tt_hashtags(item, caption),
        "mentions": _tt_mentions(item),
        "musicName": _music_name(item, music),
        "region": safe_str(
            item.get("region") or item.get("locationCreated") or item.get("location_created")
        ),
        "authorRegion": author_region,
        "descLanguage": safe_str(
            item.get("descLanguage")
            or item.get("desc_language")
            or item.get("textLanguage")
            or item.get("text_language")
        ),
        "isAd": bool(item.get("isAd") or item.get("is_ad")),
        "isPaidPartnership": bool(
            item.get("isPaidPartnership")
            or item.get("is_paid_partnership")
            or item.get("isPaidContent")
            or item.get("is_paid_content")
        ),
    }
    shop = extract_shop_product_url(item) or safe_str(item.get("shopProductUrl") or item.get("shop_product_url"))
    if shop:
        out["shopProductUrl"] = shop
    if item.get("isEligibleForCommission") is not None or item.get("is_eligible_for_commission") is not None:
        out["isEligibleForCommission"] = bool(
            item.get("isEligibleForCommission")
            if item.get("isEligibleForCommission") is not None
            else item.get("is_eligible_for_commission")
        )
    return out


def _music_name_from_url(url: str | None) -> str | None:
    """Humanize a TikTok music URL slug: /music/<slug>-<id> → 'slug words'."""
    if not url:
        return None
    match = re.search(r"/music/([^/?#]+)", url, flags=re.IGNORECASE)
    if not match:
        return None
    slug = match.group(1)
    titled = re.match(r"^(.+)-(\d{6,})$", slug)
    if not titled:
        return None
    words = titled.group(1).replace("-", " ").strip()
    return words or None


def _music_name(item: dict, music: Any = None) -> str | None:
    """Resolve sound title from clockworks / aweme / musicMeta shapes."""
    if music is None:
        music = item.get("music")
    if isinstance(music, dict):
        name = safe_str(
            music.get("musicName")
            or music.get("title")
            or music.get("name")
            or music.get("album")
        )
        if name:
            return name
        nested = music.get("musicInfo") or music.get("music_info")
        if isinstance(nested, dict):
            name = safe_str(
                nested.get("musicName")
                or nested.get("title")
                or nested.get("name")
                or nested.get("album")
            )
            if name:
                return name
        for key in ("playUrl", "play_url", "url", "musicUrl", "music_url"):
            from_url = _music_name_from_url(safe_str(music.get(key)))
            if from_url:
                return from_url
    elif isinstance(music, str):
        if not music.startswith("http"):
            return safe_str(music)
        from_url = _music_name_from_url(music)
        if from_url:
            return from_url
    meta = item.get("musicMeta") if isinstance(item.get("musicMeta"), dict) else {}
    info = item.get("music_info") if isinstance(item.get("music_info"), dict) else {}
    music_info = item.get("musicInfo") if isinstance(item.get("musicInfo"), dict) else {}
    name = safe_str(
        item.get("musicName")
        or item.get("music_title")
        or item.get("musicTitle")
        or meta.get("musicName")
        or meta.get("title")
        or meta.get("album")
        or info.get("title")
        or info.get("name")
        or info.get("album")
        or music_info.get("musicName")
        or music_info.get("title")
        or music_info.get("name")
        or music_info.get("album")
    )
    if name:
        return name
    for candidate in (
        item.get("musicUrl"),
        item.get("music_url"),
        meta.get("musicUrl"),
        meta.get("playUrl"),
        info.get("play_url"),
        music_info.get("playUrl"),
        item.get("url"),
    ):
        from_url = _music_name_from_url(safe_str(candidate))
        if from_url:
            return from_url
    return None


def _normalize_aweme(item: dict) -> dict:
    """Map raw TikTok API "aweme" rows (powerai music-posts scraper) to our shape.

    These rows use snake_case TikTok-internal fields (digg_count, play_count,
    author.unique_id ...) instead of the clockworks shape `_normalize` expects.
    """
    author = item.get("author") or {}
    username = safe_str(author.get("unique_id"))
    video_id = safe_str(item.get("video_id"))
    create_time = item.get("create_time")
    published = None
    if isinstance(create_time, (int, float)) and create_time > 0:
        published = datetime.fromtimestamp(int(create_time), tz=timezone.utc).isoformat()
    caption = safe_str(item.get("title"))
    return {
        "platform": "tiktok",
        "url": f"https://www.tiktok.com/@{username}/video/{video_id}" if username and video_id else None,
        "id": video_id or safe_str(item.get("aweme_id")),
        "caption": caption,
        "publishedAt": published,
        "durationSeconds": duration_seconds(item.get("duration")),
        "thumbnailUrl": safe_str(item.get("cover") or item.get("origin_cover")),
        "author": build_author(
            author if isinstance(author, dict) else None,
            profile_image=safe_str(author.get("avatar")) if isinstance(author, dict) else None,
        ),
        "engagement": _tt_coerce_engagement(
            {
                "views": item.get("play_count"),
                "likes": item.get("digg_count"),
                "comments": item.get("comment_count"),
                "shares": item.get("share_count"),
                "saves": item.get("collect_count"),
            }
        ),
        "hashtags": _tt_hashtags(item, caption),
        "mentions": _tt_mentions(item),
        "musicName": _music_name(item),
        "musicId": safe_str(item.get("music_id") or item.get("musicId")),
        "isAd": bool(item.get("is_ad") or item.get("isAd")),
        "isPaidPartnership": bool(
            item.get("is_paid_partnership") or item.get("isPaidPartnership")
        ),
    }


def _normalize_music_post(item: dict) -> dict:
    is_aweme = bool(item.get("aweme_id") or ("digg_count" in item and "play_count" in item))
    return _tt_finalize_post(_normalize_aweme(item) if is_aweme else _normalize(item))


def _tiktok_music_id(value: str) -> str | None:
    match = re.search(r"(\d{6,})(?:\?|$)", value)
    return match.group(1) if match else None


def _tiktok_music_candidates(settings: Any, url: str, limit: int) -> list[tuple[str, dict[str, Any]]]:
    music_id = _tiktok_music_id(url)
    candidates: list[tuple[str, dict[str, Any]]] = []
    if music_id:
        candidates.append(
            (
                settings.APIFY_ACTOR_TIKTOK_MUSIC_POSTS,
                {"music_id": music_id, "maxResults": limit},
            )
        )
    candidates.extend(
        [
            (
                settings.APIFY_ACTOR_TIKTOK_MUSIC,
                {
                    "sounds": [music_id or url],
                    "maxVideosPerSound": limit,
                    "includeSoundSummary": False,
                    "includeVideoFields": True,
                    "stopOnError": False,
                },
            ),
            (
                settings.APIFY_ACTOR_TIKTOK_MUSIC_FALLBACK,
                {"musics": [url], "resultsPerPage": limit, "shouldDownloadVideos": False},
            ),
        ]
    )
    return candidates


def _normalize_suggestion(item: dict, seed: str) -> dict:
    suggestion = (
        item.get("suggestion")
        or item.get("keyword")
        or item.get("query")
        or item.get("text")
        or item.get("searchTerm")
    )
    suggestion = safe_str(suggestion)
    # Always build the search URL ourselves: TikTok's search does not resolve
    # %20-encoded spaces, so we use + (quote_plus). The actor's own searchUrl
    # uses %20 and returns no results, so we ignore it.
    search_url = f"https://www.tiktok.com/search?q={quote_plus(suggestion)}" if suggestion else ""
    return {
        "seed": safe_str(item.get("seedKeyword") or item.get("seed") or item.get("sourceKeyword") or seed),
        "suggestion": suggestion,
        "rank": safe_int(item.get("suggestionRank") or item.get("rank") or item.get("position")),
        "searchUrl": search_url,
        "region": safe_str(item.get("region")),
        "language": safe_str(item.get("language")),
    }


def _normalize_creator(item: dict) -> dict:
    # Trends scraper emits flat creatorHandle/followerCount; other actors nest under user/author.
    nested = item.get("user") if isinstance(item.get("user"), dict) else None
    if not nested:
        nested = item.get("author") if isinstance(item.get("author"), dict) else {}
    # Prefer flat Creative Center keys before nested (empty {} must not block fallthrough).
    handle = safe_str(
        item.get("creatorHandle")
        or nested.get("uniqueId")
        or nested.get("username")
        or nested.get("handle")
        or item.get("uniqueId")
        or item.get("username")
        or item.get("handle")
    )
    if handle:
        handle = handle.lstrip("@")
    # Creative Center trending rows report 0 for counts they don't publish;
    # surface those as unknown instead of a literal zero.
    followers = safe_int(
        item.get("followerCount")
        or nested.get("followerCount")
        or item.get("followers")
        or item.get("followersCount")
    )
    likes = safe_int(
        item.get("likeCount")
        or nested.get("heartCount")
        or nested.get("likeCount")
        or item.get("likes")
        or item.get("likesCount")
    )
    videos = safe_int(item.get("videoCount") or nested.get("videoCount"))
    verified = item.get("verified")
    if verified is None:
        verified = nested.get("verified") if nested.get("verified") is not None else nested.get("isVerified")
    # Prefer our formula when likes/videos/followers exist — never trust actor "growth" as ER.
    eng = creator_engagement_rate(likes, videos, followers)
    if eng is None:
        raw_eng = item.get("engagementRate") or item.get("engagement_rate")
        eng = safe_float(raw_eng)
    bio = safe_str(item.get("bio") or nested.get("signature") or nested.get("bio"))
    contact = extract_bio_contact(bio)
    # Creator locale only — never the request's feed country echo.
    region = safe_str(
        nested.get("region")
        or item.get("region")
        or item.get("creatorRegion")
    )
    out = {
        "rank": safe_int(item.get("rank")),
        "id": safe_str(nested.get("id") or nested.get("uid") or item.get("id")),
        "secUid": safe_str(nested.get("secUid") or nested.get("sec_uid") or item.get("secUid")),
        "username": handle,
        "displayName": safe_str(
            item.get("name")
            or nested.get("nickname")
            or nested.get("displayName")
            or item.get("nickname")
            or item.get("displayName")
        ),
        "url": safe_str(item.get("profileUrl") or nested.get("profileUrl") or item.get("url"))
        or (f"https://www.tiktok.com/@{handle}" if handle else None),
        "bio": bio,
        "followers": followers,
        "engagementRate": eng,
        "engagementRateBasis": ENGAGEMENT_RATE_BASIS,
        "likes": likes,
        "videos": videos,
        "region": region,
        "verified": verified,
        "profileImage": safe_str(
            item.get("creatorAvatarUrl")
            or nested.get("avatarLarger")
            or nested.get("avatar")
            or item.get("avatar")
            or item.get("avatarUrl")
        ),
    }
    if contact:
        out["contact"] = contact
    return strip_empty(out)


@router.get("/video-details", summary="TikTok video metadata + stats")
async def tiktok_video_details(
    url: str = Query(...),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_tiktok_video_url(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/video-details",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_VIDEO_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Native-only: parse the video page's embedded JSON (~2s).
            native = await video_details_native(url)
            if native is not None and native["engagement"].get("views") is not None:
                ctx["source"] = "direct"
                return native
            raise HTTPException(status_code=404, detail="Video not found")

        data = await cached_or_run(
            endpoint="tiktok.video-details",
            params={"url": url, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


async def _fetch_tiktok_transcript(
    url: str, language: str | None = None
) -> tuple[str, list[dict[str, Any]], str | None, str]:
    """Return (full transcript, timestamped segments, language, source).

    Cascade (no Apify):
      1. Native TikTok WebVTT caption track (proxy only) → source ``direct``
      2. Native MP4 download + our Whisper → source ``openai``
    """
    # 1) Free/fast: TikTok's own subtitleInfos / claInfo WebVTT.
    native = await tiktok_native.transcript_native(url, language=language)
    if native and native.get("transcript"):
        return (
            native["transcript"],
            native.get("transcriptSegments") or [],
            safe_str(native.get("language")),
            "direct",
        )

    # 2) Caption-less videos: download media + our Whisper.
    raw = await tiktok_native.fetch_video_bytes(url, max_bytes=WHISPER_MAX_BYTES)
    if raw:
        result = await transcribe_audio(raw, filename="tiktok.mp4", language=language)
        if result["transcript"]:
            return (
                result["transcript"],
                result["transcriptSegments"],
                safe_str(result.get("language")),
                "openai",
            )

    # Distinguish missing video (404) vs no usable speech/captions (422).
    details = await video_details_native(url)
    if details is None:
        raise HTTPException(status_code=404, detail="Video not found")
    raise HTTPException(status_code=422, detail="No speech/captions available for this TikTok")


@router.get("/transcript", summary="TikTok video transcript (via auto-captions)")
async def tiktok_transcript(
    request: Request,
    url: str = Query(...),
    language: str | None = Query(
        None,
        description="Optional ISO-639-1 hint (e.g. 'tr') to pin the speech language",
        max_length=8,
    ),
    cache: bool = Query(
        True,
        description=(
            "Serve from the 24h shared cache when available (0 credits on hit). "
            "Default true — set false to always fetch fresh."
        ),
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_tiktok_video_url(url)
    lang = (language or "").strip().lower() or None
    settings = get_settings()

    # Public free-tool proxy: daily per-client cap (counts every successful try).
    anon_client = _anon_tool_client(request, settings.TOOL_PROXY_SECRET)
    if anon_client:
        await check_daily_quota(
            f"anon.tiktok.transcript:{anon_client}",
            limit=settings.ANON_TIKTOK_TRANSCRIPT_DAILY,
            error="anon_daily_limit",
            upgrade_url="/signup",
        )

    # Free plan: separate low daily quota on billable (non-cache) transcript calls.
    free_quota = (
        settings.FREE_TIKTOK_TRANSCRIPT_DAILY
        if (caller.plan or "").lower() == "free" and not anon_client
        else 0
    )
    if free_quota:
        await check_daily_quota(
            f"free.tiktok.transcript:{caller.user_id}",
            limit=free_quota,
            error="free_transcript_daily_quota",
            upgrade_url="/dashboard/billing",
        )

    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/transcript",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_TRANSCRIPT,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            full, segments, detected, source = await _fetch_tiktok_transcript(
                url, language=lang
            )
            ctx["source"] = source
            # Additive body field for RAG weighting. Existing keys unchanged.
            if source == "direct":
                public_source = "captions"
            elif source == "openai":
                public_source = "whisper"
            else:
                public_source = source
            return {
                "platform": "tiktok",
                "url": url,
                "transcript": full,
                "transcriptSegments": segments,
                "wordCount": len(full.split()),
                "segments": len(segments),
                "language": normalize_language_code(detected),
                "source": public_source,
            }

        data = await cached_or_run(
            endpoint="tiktok.transcript",
            params={"url": url, "language": lang, "v": 8},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )

        if anon_client:
            await consume_daily_quota(
                f"anon.tiktok.transcript:{anon_client}",
                limit=settings.ANON_TIKTOK_TRANSCRIPT_DAILY,
            )
        elif free_quota and not ctx.get("cache_hit"):
            await consume_daily_quota(
                f"free.tiktok.transcript:{caller.user_id}",
                limit=free_quota,
            )

        return ApiResponse(data=data)


def _anon_tool_client(request: Request, secret: str) -> str | None:
    """Return the anon client id when the request is from the trusted tool proxy."""
    if not secret:
        return None
    if request.headers.get("x-captapi-tool-secret") != secret:
        return None
    client = (request.headers.get("x-captapi-client") or "").strip()
    return client[:128] if client else None


@router.get("/summarize", summary="AI summary of a TikTok video")
async def tiktok_summarize(
    url: str = Query(...),
    language: str | None = Query(
        None,
        description="Optional ISO-639-1 code (e.g. 'tr'): pins the speech language and sets the summary output language",
        max_length=8,
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_tiktok_video_url(url)
    lang = (language or "").strip().lower() or None
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/summarize",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_SUMMARIZE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            text, _segments, _detected, source = await _fetch_tiktok_transcript(
                url, language=lang
            )
            ctx["source"] = source
            ai = await summarize_transcript(text, language=lang or "en")
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
            params={"url": url, "language": lang, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/comments", summary="Comments on a TikTok video (text, author, likes, timestamp) with cursor pagination")
async def tiktok_comments(
    url: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    cursor: str | None = Query(
        None,
        description="Leave empty for the first page; then pass the nextCursor value returned in the previous response (a numeric offset, e.g. 50).",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    aweme_id = _require_tiktok_video_url(url)
    if cursor is not None and not cursor.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    settings = get_settings()
    # Flat fee: comments are served natively from TikTok's own API (our cost is
    # ~$0), so a single low charge covers any page size instead of per-result.
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/comments",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_COMMENTS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: TikTok's own cursor-paginated mobile comment API (no actor
            # cost). Soft-block exits get one short retry before Apify / 502.
            native = await retry_none(
                lambda: tiktok_native.comments_native(aweme_id, cursor, limit),
                attempts=2,
                delay=0.45,
            )
            if native is not None:
                comments, next_cursor, total = native
                # Soft-empty first page (no comments, unknown/zero total) is often
                # a dead/private aweme id — don't accept it as success yet.
                soft_empty = (
                    not cursor
                    and not comments
                    and (total is None or total == 0)
                    and next_cursor is None
                )
                if not soft_empty:
                    ctx["source"] = "direct"
                    payload = {
                        "platform": "tiktok",
                        "url": url,
                        "totalComments": total,
                        "totalReturned": len(comments),
                        "comments": comments,
                        "nextCursor": next_cursor,
                        "hasMore": next_cursor is not None,
                    }
                    return {k: v for k, v in payload.items() if v is not None}
                # Confirmed empty thread on a real video: keep native success.
                if total == 0:
                    vd = await video_details_native(url)
                    if vd is not None:
                        ctx["source"] = "direct"
                        return {
                            "platform": "tiktok",
                            "url": url,
                            "totalComments": 0,
                            "totalReturned": 0,
                            "comments": [],
                            "nextCursor": None,
                            "hasMore": False,
                        }

            # The Apify actor is not cursor-based, so it only serves the first
            # page; deeper pages require the native path above.
            if cursor:
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch the next page. Retry shortly.",
                )
            apify = get_apify()
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_TIKTOK_COMMENTS,
                    {"postURLs": [url], "commentsPerPost": limit},
                    max_items=limit,
                )
            except ApifyError:
                items = []
            comments = []
            for c in items[:limit]:
                if not isinstance(c, dict):
                    continue
                user = c.get("user") if isinstance(c.get("user"), dict) else {}
                row: dict[str, Any] = {
                    "id": safe_str(c.get("cid") or c.get("id")),
                    "text": (c.get("text") or "").strip(),
                    "author": safe_str(
                        c.get("uniqueId") or user.get("uniqueId") or user.get("unique_id") or c.get("authorName")
                    ),
                    "authorId": safe_str(
                        c.get("uid") or c.get("authorId") or user.get("uid") or user.get("id")
                    ),
                    "authorSecUid": safe_str(
                        c.get("secUid")
                        or c.get("sec_uid")
                        or user.get("secUid")
                        or user.get("sec_uid")
                    ),
                    "authorAvatarUrl": safe_str(
                        c.get("avatarThumbnail") or user.get("avatarThumb") or user.get("avatar_thumb")
                    ),
                    "commentLanguage": safe_str(
                        c.get("commentLanguage")
                        or c.get("comment_language")
                        or user.get("language")
                    ),
                    "likeCount": safe_int(c.get("diggCount") or c.get("likeCount") or c.get("digg_count")),
                    "replyCount": safe_int(
                        c.get("replyCommentTotal")
                        or c.get("reply_comment_total")
                        or c.get("replyCount")
                        or c.get("reply_count")
                    ),
                    "publishedAt": safe_str(c.get("createTimeISO") or c.get("createTime")),
                }
                comments.append({k: v for k, v in row.items() if v is not None})
            if not comments:
                raise HTTPException(status_code=404, detail="Video not found or has no comments")
            ctx["source"] = "apify"
            # Do not claim the thread is exhausted — Apify cannot page.
            return {
                "platform": "tiktok",
                "url": url,
                "totalReturned": len(comments),
                "comments": comments,
                "nextCursor": None,
                "hasMore": None,
                "degraded": True,
            }

        data = await cached_or_run(
            endpoint="tiktok.comments",
            params={"url": url, "limit": limit, "cursor": cursor or "", "v": 8},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/channel-details",
    summary="TikTok profile — createTime, bioLink.risk, Shop/commerce, contact",
)
async def tiktok_channel_details(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the default cache TTL. Default false — always fetch fresh."),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/channel-details",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_CHANNEL_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Native-only: parse the profile page's embedded JSON.
            native = await channel_details_native(handle, url)
            if native is not None and native.get("followers") is not None:
                ctx["source"] = "direct"
                return native
            raise HTTPException(status_code=404, detail="Profile not found")

        data = await cached_or_run(
            endpoint="tiktok.channel-details",
            params={"url": url, "v": 4, "cacheMaxAge": cacheMaxAge},
            runner=_run,
            ctx=ctx,
            use_cache=use_cache,
            ttl=ttl,
        )
        return ApiResponse(data=data)


def _pct(n: int, total: int) -> float:
    return round(n / total * 100, 2) if total else 0.0


def _tally_locations(codes: list[str]) -> list[dict[str, Any]]:
    """Turn ISO country codes into a ranked breakdown with numeric percentages."""
    counts = Counter(codes)
    total = sum(counts.values())
    if not total:
        return []
    out: list[dict[str, Any]] = []
    for code, n in counts.most_common():
        pct = _pct(n, total)
        out.append(
            {
                "country": country_name(code),
                "countryCode": code,
                "count": n,
                "percentage": pct,
                "percentageText": f"{pct:.2f}%",
            }
        )
    return out


def _tally_languages(codes: list[str]) -> list[dict[str, Any]]:
    """Turn language codes into a ranked breakdown with numeric percentages."""
    counts = Counter(codes)
    total = sum(counts.values())
    if not total:
        return []
    out: list[dict[str, Any]] = []
    for lang, n in counts.most_common():
        pct = _pct(n, total)
        out.append(
            {
                "language": lang,
                "count": n,
                "percentage": pct,
                "percentageText": f"{pct:.2f}%",
            }
        )
    return out


def _top_n_with_other(
    items: list[dict[str, Any]], *, limit: int | None, sample_size: int
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Keep the top ``limit`` buckets; fold the remainder into ``other``."""
    if limit is None or limit <= 0 or len(items) <= limit:
        return items, None
    head = items[:limit]
    rest = sum(int(x.get("count") or 0) for x in items[limit:])
    if rest <= 0:
        return head, None
    pct = _pct(rest, sample_size)
    return head, {"count": rest, "percentage": pct, "percentageText": f"{pct:.2f}%"}


async def _fetch_audience_demographics(
    handle: str, settings: Any, *, video_sample: int, target_total: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    """Sample commenter countries + languages across a creator's recent videos.

    Prefer native channel posts for video IDs; fall back to the profile actor
    when TikTok soft-blocks the post list. Commenter signals come from TikTok's
    native comment API (``user.region`` + ``comment_language``).
    """
    aweme_ids: list[str] = []
    native_posts = await channel_posts_native(handle, None, video_sample)
    if native_posts is not None:
        aweme_ids = [safe_str(p.get("id")) for p in native_posts[0] if safe_str(p.get("id"))]
    if not aweme_ids:
        items = await get_apify().run_actor_sync(
            settings.APIFY_ACTOR_TIKTOK,
            {"profiles": [handle], "resultsPerPage": video_sample, "shouldDownloadVideos": False},
            max_items=video_sample,
        )
        aweme_ids = [safe_str(i.get("id") or i.get("videoId")) for i in (items or [])]
        aweme_ids = [a for a in aweme_ids if a]
    if not aweme_ids:
        return [], [], 0
    got = await audience_commenters_native(aweme_ids, target_total=target_total)
    if got is None:
        return [], [], len(aweme_ids)
    return (
        _tally_locations(got.get("regions") or []),
        _tally_languages(got.get("languages") or []),
        len(aweme_ids),
    )


async def _resolve_region(data: dict[str, Any]) -> None:
    """Populate ``region`` with the best available country signal.

    TikTok almost never exposes an account's ``region`` on any public surface,
    so when it's missing we fill ``region`` with a gpt-4o-mini guess of the
    creator's likely country from public cues (bio, display name, language).
    ``regionSource`` records where the value came from ("tiktok" when authoritative,
    "inferred" when estimated) and ``regionConfidence`` grades the estimate.
    """
    if data.get("region"):
        data["regionConfidence"] = None
        data["regionSource"] = "tiktok"
        return
    raw = data.get("raw") or {}
    user = raw.get("user") or raw.get("authorMeta") or {}
    bio = safe_str(user.get("signature"))
    est = await infer_region(
        username=data.get("username"),
        display_name=data.get("displayName"),
        bio=bio,
        language=data.get("language"),
    )
    data["region"] = (est or {}).get("region")
    data["regionConfidence"] = (est or {}).get("confidence")
    data["regionSource"] = "inferred"


@router.get("/profile-region", summary="TikTok creator region, language & core stats")
async def tiktok_profile_region(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/profile-region",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/@{handle}",
        base_credits=CREDIT_PROFILE_REGION,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: profile page JSON. Returns None when it exposes neither
            # region nor language, in which case the actor's caption-language
            # sampling is still worth the cost.
            native = await profile_region_native(handle)
            if native is not None:
                ctx["source"] = "direct"
                base = native
            else:
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_TIKTOK_PROFILE,
                    {"profiles": [handle], "resultsPerPage": 1},
                    max_items=1,
                )
                if not items:
                    raise HTTPException(status_code=404, detail="Profile not found")
                ctx["source"] = "apify"
                base = _normalize_profile_region(items[0], handle)

            await _resolve_region(base)
            return base

        data = await cached_or_run(
            endpoint="tiktok.profile-region",
            params={"handle": handle, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _normalize_live(item: dict[str, Any], handle: str) -> dict[str, Any]:
    """Map live actor output — supports nested liveRoom* and flat snake_case rows."""
    from app.services.tiktok_native import (
        _TT_LIVE_STATUS_LIVE,
        _extract_stream_qualities,
        _extract_stream_urls,
        _streams_by_quality,
    )

    user = item.get("liveRoomUserInfo") if isinstance(item.get("liveRoomUserInfo"), dict) else {}
    room = item.get("liveRoom") if isinstance(item.get("liveRoom"), dict) else {}
    room_status = safe_int(room.get("status") if room.get("status") is not None else item.get("status"))
    user_status = safe_int(user.get("status") if user.get("status") is not None else item.get("user_status"))
    if room_status is not None:
        is_live = room_status == _TT_LIVE_STATUS_LIVE
        status = room_status
    elif item.get("is_live") is not None or item.get("isLive") is not None:
        is_live = bool(item.get("is_live") if item.get("is_live") is not None else item.get("isLive"))
        status = _TT_LIVE_STATUS_LIVE if is_live else (user_status if user_status is not None else None)
    elif user_status is not None:
        is_live = user_status == _TT_LIVE_STATUS_LIVE
        status = user_status
    else:
        is_live = False
        status = None

    stream_urls = (
        item.get("stream_urls")
        or item.get("streamUrls")
        or room.get("stream_urls")
        or room.get("streamUrls")
        or []
    )
    if not isinstance(stream_urls, list):
        stream_urls = []
    qualities = _extract_stream_qualities(room) if room else []
    if not stream_urls and qualities:
        stream_urls = _extract_stream_urls(room)
    streams_map = _streams_by_quality(qualities)
    game_tag = safe_int(room.get("gameTagId") or room.get("game_tag_id") or item.get("gameTagId"))
    hash_tag = safe_int(room.get("hashTagId") or room.get("hash_tag_id") or item.get("hashTagId"))
    live_sub = room.get("liveSubOnly") if room.get("liveSubOnly") is not None else item.get("liveSubOnly")
    live_sub_only = None if live_sub is None else bool(safe_int(live_sub) if not isinstance(live_sub, bool) else live_sub)
    following = safe_int(
        user.get("followingCount")
        or item.get("following_count")
        or item.get("followingCount")
    )
    creator_id = safe_str(user.get("id") or user.get("uid") or item.get("uid") or item.get("user_id"))
    sec_uid = safe_str(user.get("secUid") or user.get("sec_uid") or item.get("secUid") or item.get("sec_uid"))

    return strip_empty(
        {
            "platform": "tiktok",
            "username": safe_str(
                user.get("uniqueId") or item.get("unique_id") or item.get("handle") or handle
            ),
            "isLive": is_live,
            "status": status,
            "creator": {
                "id": creator_id,
                "secUid": sec_uid,
                "displayName": safe_str(user.get("nickname") or item.get("nickname")),
                "followers": safe_int(user.get("followerCount") or item.get("follower_count")),
                "following": following,
                "followingCount": following,
                "verified": user.get("verified") if user.get("verified") is not None else item.get("verified"),
                "avatar": safe_str(
                    user.get("avatarUrl")
                    or user.get("avatarThumb")
                    or item.get("avatar_url")
                    or item.get("avatarUrl")
                ),
                "bio": safe_str(user.get("signature") or item.get("bio") or item.get("signature")),
                "status": user_status,
            },
            "room": {
                "id": safe_str(
                    room.get("roomId")
                    or room.get("room_id")
                    or item.get("roomId")
                    or item.get("room_id")
                    or user.get("roomId")
                    or room.get("id")
                    or room.get("streamId")
                ),
                "streamId": safe_str(room.get("streamId") or item.get("streamId")),
                "status": room_status if room_status is not None else status,
                "title": safe_str(room.get("title") or item.get("room_title") or item.get("title")),
                "startedAt": safe_str(room.get("started_at") or item.get("started_at") or item.get("startedAt")),
                "viewerCount": safe_int(
                    room.get("viewer_count") or item.get("viewer_count") or item.get("viewerCount")
                ),
                "totalEnterCount": safe_int(
                    room.get("total_enter_count")
                    or item.get("total_enter_count")
                    or item.get("totalEnterCount")
                ),
                "likeCount": safe_int(room.get("like_count") or item.get("like_count") or item.get("likeCount")),
                "coverUrl": safe_str(room.get("cover_url") or item.get("cover_url") or item.get("coverUrl")),
                "liveSubOnly": live_sub_only,
                "gameTagId": game_tag if game_tag else None,
                "hashTagId": hash_tag if hash_tag else None,
                "streamUrls": stream_urls or None,
                "streamQualities": qualities or None,
                "streams": streams_map,
            },
        }
    )


@router.get("/live", summary="TikTok live status + room info for a creator")
async def tiktok_live(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/live",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/@{handle}/live",
        base_credits=CREDIT_CHANNEL_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await live_status_native(handle)
            # Offline status is complete natively. When live, prefer Apify only
            # if we still lack a room id (shouldn't happen) — otherwise ship
            # native isLive + creator (+ room.id / best-effort enrich).
            if native is not None and (not native.get("isLive") or (native.get("room") or {}).get("id")):
                ctx["source"] = "direct"
                return native

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_LIVE,
                {"handles": [handle], "include_stream_urls": True},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Creator not found")
            item = items[0]
            if item.get("error"):
                raise HTTPException(status_code=404, detail="Creator not found")
            ctx["source"] = "apify"
            return _normalize_live(item, handle)

        data = await cached_or_run(
            endpoint="tiktok.live",
            params={"handle": handle, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/live-info", summary="TikTok live room info for a creator")
async def tiktok_live_info(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    # ScrapeCreators exposes both Live and Live Info. Our live endpoint already
    # returns status plus full room details, so this route is an explicit alias
    # with its own billing/cache key for compatibility.
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/live-info",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/@{handle}/live",
        base_credits=7,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await live_status_native(handle)
            # Prefer native whenever we have stream URLs (or a definitive offline).
            native_streams = ((native or {}).get("room") or {}).get("streamUrls") or []
            if native is not None and (not native.get("isLive") or native_streams):
                ctx["source"] = "direct"
                return strip_empty(
                    {
                        **native,
                        "streamUrls": native_streams,
                    }
                )
            # Still-live but no pull URLs yet — Apify for full room media.
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_LIVE,
                {"handles": [handle], "include_stream_urls": True},
                max_items=1,
            )
            if not items:
                if native is not None:
                    ctx["source"] = "direct"
                    return strip_empty(
                        {
                            **native,
                            "streamUrls": (native.get("room") or {}).get("streamUrls") or [],
                        }
                    )
                raise HTTPException(status_code=404, detail="Creator not found")
            item = items[0]
            if item.get("error"):
                if native is not None:
                    ctx["source"] = "direct"
                    return strip_empty(
                        {
                            **native,
                            "streamUrls": (native.get("room") or {}).get("streamUrls") or [],
                        }
                    )
                raise HTTPException(status_code=404, detail="Creator not found")
            normalized = _normalize_live(item, handle)
            ctx["source"] = "apify"
            return strip_empty(
                {
                    **normalized,
                    "streamUrls": (normalized.get("room") or {}).get("streamUrls") or [],
                    "raw": item,
                }
            )

        data = await cached_or_run(
            endpoint="tiktok.live-info",
            params={"handle": handle, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/search-suggestions", summary="TikTok search/autocomplete suggestions")
async def tiktok_search_suggestions(
    q: str = Query(..., min_length=1, description="Seed keyword to expand into autocomplete suggestions, e.g. skincare."),
    country: str = Query("US", min_length=2, max_length=2, description="Two-letter ISO country code that localizes the suggestions to a market, e.g. US, GB, DE. Default US."),
    language: str = Query("en-US", description="Interface language for the suggestions, e.g. en-US or de-DE. Default en-US."),
    limit: int = Query(20, ge=1, le=100, description="Upper bound on how many suggestions to return (1-100, default 20). TikTok only surfaces a limited number of real autocomplete suggestions per keyword, so you'll often get fewer than the limit."),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    # Flat fee: native search preview is ~$0; Apify fallback is rare and covered
    # by the same 2-credit charge.
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/search-suggestions",
        platform="tiktok",
        resource_url=None,
        base_credits=CREDIT_SEARCH_SUGGESTIONS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Native first — TikTok's public search preview. Apify actor is a
            # fallback when every proxy tier is blocked.
            native_rows = await search_suggestions_native(
                q, country=country, language=language, limit=limit
            )
            items: list[dict[str, Any]]
            if native_rows:
                ctx["source"] = "direct"
                items = native_rows
            else:
                try:
                    items = await get_apify().run_actor_sync(
                        settings.APIFY_ACTOR_TIKTOK_SEARCH_SUGGESTIONS,
                        {
                            "keywords": [q],
                            "maxSuggestionsPerKeyword": limit,
                            "region": country.upper(),
                            "language": language,
                            "includeAlphabetExpansions": False,
                        },
                        max_items=limit,
                    )
                except ApifyError as exc:
                    raise HTTPException(
                        status_code=502,
                        detail="Failed to fetch search suggestions. Retry shortly.",
                    ) from exc
                ctx["source"] = "apify"

            suggestions = [
                s for s in (_normalize_suggestion(i, q) for i in items[:limit])
                if s.get("suggestion")
            ]
            for idx, s in enumerate(suggestions, start=1):
                if s.get("rank") is None:
                    s["rank"] = idx
                if not s.get("region"):
                    s["region"] = country.upper()
                if not s.get("language"):
                    s["language"] = language
            return {
                "platform": "tiktok",
                "query": q,
                "totalReturned": len(suggestions),
                "suggestions": suggestions,
            }

        data = await cached_or_run(
            endpoint="tiktok.search-suggestions",
            params={"q": q, "country": country.upper(), "language": language, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/popular-creators",
    summary="Popular TikTok creators (Creative Center)",
    description=(
        "TikTok Creative Center creator chart "
        "(ads.tiktok.com/business/creativecenter/inspiration/popular/creator). "
        "engagementRate is TikTok's official interact rate when exposed "
        "(engagementRateBasis=creative_center). Falls back to For You feed "
        "hydrate, then Apify. Flat 2 credits on Creative Center / FYP native."
    ),
)
async def tiktok_popular_creators(
    country: str = Query("US", min_length=2, max_length=2),
    sort: str = Query("follower", pattern="^(follower|engagement|popularity)$"),
    follower_count: str | None = Query(None, description="Optional range: 10k-100k, 100k-1m, 1m-10m, >10m (FYP/Apify fallthrough)"),
    page: int = Query(1, ge=1, le=20, description="Creative Center page (default 1)."),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the default cache TTL. Default false — always fetch fresh."),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    from app.services import tiktok_creative_center_trends as cc_trends

    settings = get_settings()
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    # Reserve Apify worst-case; native path overrides to flat CREDIT_CC_TREND.
    cost = _scaled_credits(limit, RATE_TREND_MARGIN, CREDIT_CC_TREND)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/popular-creators",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            cc = await cc_trends.search_popular_creators(
                country=country.upper(),
                page=page,
                limit=limit,
                sort=sort,
            )
            if cc and cc.get("creators"):
                ctx["source"] = "direct"
                creators = await hydrate_creators_trust(list(cc["creators"]))
                cc = {**cc, "creators": creators, "totalReturned": len(creators)}
                return cc

            native = await popular_creators_native(
                country.upper(),
                sort=sort,
                follower_count=follower_count,
                limit=limit,
            )
            if native:
                ctx["source"] = "direct"
                return {
                    "platform": "tiktok",
                    "country": country.upper(),
                    "sort": sort,
                    "source": "fyp",
                    "totalReturned": len(native),
                    "creators": native,
                    "note": (
                        "Creative Center unavailable — ranked from this market's "
                        "For You feed + profile hydrate. engagementRate uses "
                        f"{ENGAGEMENT_RATE_BASIS}."
                    ),
                }

            run_input: dict[str, Any] = {
                "trendType": "creator",
                "countryCode": country.upper(),
                "maxResults": limit,
            }
            fallback_input: dict[str, Any] = {
                "creator_country": country.upper(),
                "sort_by": "avg_views" if sort == "popularity" else sort,
                "maxResults": limit,
                "limit": min(limit, 50),
            }
            if follower_count:
                range_map = {"10k-100k": "1", "100k-1m": "2", "1m-10m": "3", ">10m": "4"}
                fallback_input["audience_count"] = range_map.get(follower_count.lower(), follower_count)
            items, _actor = await get_apify().run_with_fallback(
                [
                    (settings.APIFY_ACTOR_TIKTOK_POPULAR_CREATORS, run_input),
                    (settings.APIFY_ACTOR_TIKTOK_POPULAR_CREATORS_FALLBACK, fallback_input),
                ],
                max_items=limit,
                is_valid=_is_real_popular_creator_items,
            )
            creators = [
                c
                for c in (_normalize_creator(i) for i in items[:limit])
                if c.get("username")
                and "creator discovery" not in (c.get("displayName") or "").lower()
            ]
            if not creators:
                raise HTTPException(status_code=404, detail="No popular creators found for this country")
            creators = await hydrate_creators_trust(creators)
            ctx["source"] = "apify"
            return {
                "platform": "tiktok",
                "country": country.upper(),
                "sort": sort,
                "source": "apify",
                "totalReturned": len(creators),
                "creators": creators,
                "note": "Apify fallthrough — Creative Center + FYP unavailable.",
            }

        data = await cached_or_run(
            endpoint="tiktok.popular-creators",
            params={
                "country": country.upper(),
                "sort": sort,
                "follower_count": follower_count or "",
                "page": page,
                "limit": limit,
                "v": 10,
                "cacheMaxAge": cacheMaxAge,
            },
            runner=_run,
            ctx=ctx,
            use_cache=use_cache,
            ttl=ttl,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_CC_TREND
        else:
            ctx["credits_override"] = _scaled_credits(
                len(data["creators"]), RATE_TREND_MARGIN, CREDIT_CC_TREND
            )
        return ApiResponse(data=data)


@router.get(
    "/audience-demographics",
    summary="TikTok commenter countries + languages (engagement sample)",
    description=(
        "TikTok does not publish follower geography. This endpoint samples "
        "people commenting on the creator's recent videos and tallies "
        "commenter country (user.region) and comment language. Percentages "
        "are numeric and sum to ~100% across audienceLocations (+ other when "
        "countriesLimit truncates). Use videos=12|30|60 for sample depth "
        "(credits 3/5/8). Reflects who engages — not a full follower census."
    ),
)
async def tiktok_audience_demographics(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    videos: int = Query(
        AUDIENCE_VIDEO_SAMPLE,
        description="How many recent videos to sample comments from (12, 30, or 60). Credits: 3 / 5 / 8.",
    ),
    countriesLimit: int | None = Query(
        None,
        ge=1,
        le=100,
        description=(
            "Max countries to return in audienceLocations. Remainder is folded "
            "into other{count,percentage}. Omit to return every country in the sample."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    if videos not in AUDIENCE_VIDEOS_ALLOWED:
        raise HTTPException(
            status_code=400,
            detail=f"videos must be one of {list(AUDIENCE_VIDEOS_ALLOWED)}",
        )
    video_sample = videos
    target_total = _audience_target_total(video_sample)
    credits = _audience_credits(video_sample)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/audience-demographics",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/@{handle}",
        base_credits=credits,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # TikTok never publishes follower geography, but every commenter's
            # country IS exposed on its own comment API. Sampling commenters
            # across the creator's recent videos yields an engagement-based
            # audience-country breakdown — computed natively, no audience actor.
            locations, languages, videos_sampled = await _fetch_audience_demographics(
                handle,
                settings,
                video_sample=video_sample,
                target_total=target_total,
            )
            if videos_sampled == 0:
                raise HTTPException(status_code=404, detail="Profile not found or has no public videos")
            sample_size = sum(int(loc["count"]) for loc in locations)
            total_countries = len(locations)
            shown, other = _top_n_with_other(
                locations, limit=countriesLimit, sample_size=sample_size
            )
            lang_sample = sum(int(x["count"]) for x in languages)
            ctx["source"] = "direct"
            return {
                "platform": "tiktok",
                "username": handle,
                "url": f"https://www.tiktok.com/@{handle}",
                "basis": "commenters",
                "videosSampled": videos_sampled,
                "videosRequested": video_sample,
                "sampleSize": sample_size,
                "totalCountries": total_countries,
                "confidence": _sample_confidence(sample_size),
                "audienceLocations": shown,
                "other": other,
                "audienceLanguages": languages,
                "languageSampleSize": lang_sample,
            }

        data = await cached_or_run(
            endpoint="tiktok.audience-demographics",
            params={
                "handle": handle,
                "videos": video_sample,
                "countriesLimit": countriesLimit or "",
                "v": 4,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = credits
        return ApiResponse(data=data)


@router.get(
    "/channel-posts",
    summary="Latest videos from a TikTok profile (cursor-paginated)",
    description=(
        "Returns a creator's most recent public videos as structured JSON — "
        "caption, engagement (views/likes/comments/shares/saves), thumbnail, "
        "hashtags, sound name, and author profile. Accepts a profile URL, "
        "@handle, or username. Prefers TikTok's native mobile post API "
        "(cursor pagination via nextCursor / hasMore); falls back to our "
        "data-collection pool on the first page if every residential exit is "
        "soft-blocked. Flat 2 credits per call."
    ),
)
async def tiktok_channel_posts(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    limit: int = Query(
        20,
        ge=1,
        le=200,
        description="How many latest videos to return (1–200). Newest first. Flat 2 credits per call.",
    ),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the "
            "nextCursor value returned in the previous response (TikTok's "
            "max_cursor timestamp, e.g. 1783614676000)."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    if cursor is not None and not cursor.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    # Flat fee: native path is ~$0 (same model as comments).
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/channel-posts",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_CHANNEL_POSTS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await retry_none(
                lambda: channel_posts_native(handle, cursor, limit),
                attempts=2,
                delay=0.45,
            )
            if native is not None:
                posts, next_cursor = native
                ctx["source"] = "direct"
                return {
                    "url": url,
                    "totalReturned": len(posts),
                    "posts": posts,
                    "nextCursor": next_cursor,
                    "hasMore": next_cursor is not None,
                }

            # Native-only feed (including first page). Ask the client to retry.
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch channel posts. Retry shortly.",
            )

        data = await cached_or_run(
            endpoint="tiktok.channel-posts",
            params={"url": url, "limit": limit, "cursor": cursor or "", "v": 10},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/comment-replies", summary="Replies to a TikTok comment (cursor-paginated)")
async def tiktok_comment_replies(
    url: str = Query(..., description="URL of the TikTok video the comment belongs to"),
    comment_id: str = Query(..., description="ID of the parent comment"),
    limit: int = Query(50, ge=1, le=500),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the "
            "nextCursor value returned in the previous response."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    aweme_id = _require_tiktok_video_url(url)
    if cursor is not None and not str(cursor).isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    settings = get_settings()
    # Flat fee: native reply path is ~$0. Apify crawl fallback is rare and
    # covered by the same 2-credit charge (same model as /comments).
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/comment-replies",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_COMMENT_REPLIES,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await comment_replies_native(aweme_id, comment_id, cursor, limit)
            if native is not None:
                replies, next_cursor, total = native
                ctx["source"] = "direct"
                return {
                    "platform": "tiktok",
                    "url": url,
                    "commentId": comment_id,
                    "totalReturned": len(replies),
                    "totalReplies": total,
                    "replies": replies,
                    "nextCursor": next_cursor,
                    "hasMore": next_cursor is not None,
                }

            if cursor:
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch the next page. Retry shortly.",
                )

            apify = get_apify()
            fast_input = {
                "videoUrls": [url],
                "maxCommentsPerVideo": REPLIES_MAX_COMMENTS,
                "includeReplies": True,
                "maxRepliesPerComment": min(limit, 500),
            }
            legacy_input = {
                "videoUrls": [url],
                "maxComments": REPLIES_MAX_COMMENTS,
                "includeReplies": True,
                "maxRepliesPerComment": min(limit, 500),
                "includeAuthorInfo": True,
                "sort": "top",
                "proxyConfiguration": TIKTOK_RESIDENTIAL_PROXY,
            }
            items, _actor = await apify.run_with_fallback(
                [
                    (settings.APIFY_ACTOR_TIKTOK_COMMENT_REPLIES_FAST, fast_input),
                    (settings.APIFY_ACTOR_TIKTOK_COMMENT_REPLIES, legacy_input),
                ],
                max_items=REPLIES_MAX_ITEMS,
            )
            replies: list[dict[str, Any]] = []
            for r in items:
                parent_id = safe_str(
                    r.get("parentCommentId")
                    or r.get("parentId")
                    or r.get("repliesToId")
                    or r.get("replyToCommentId")
                )
                if parent_id != comment_id:
                    nested = r.get("replies") or r.get("_replies") or []
                    if isinstance(nested, list) and safe_str(r.get("id") or r.get("cid")) == comment_id:
                        for child in nested:
                            verified = child.get("replyAuthorVerified") or child.get("verified")
                            reply_row = {
                                "id": safe_str(child.get("replyId") or child.get("cid") or child.get("id")),
                                "text": (child.get("replyText") or child.get("text") or child.get("body") or "").strip(),
                                "author": safe_str(child.get("replyAuthorUsername") or child.get("author") or child.get("uniqueId")),
                                "authorId": safe_str(child.get("uid") or child.get("authorId") or child.get("userId")),
                                "authorSecUid": safe_str(child.get("secUid") or child.get("sec_uid") or child.get("authorSecUid")),
                                "authorName": safe_str(child.get("replyAuthorNickname") or child.get("authorName") or child.get("nickname")),
                                "commentLanguage": safe_str(child.get("commentLanguage") or child.get("comment_language")),
                                "likeCount": safe_int(child.get("replyLikeCount") or child.get("likeCount") or child.get("likes")),
                                "publishedAt": safe_str(child.get("replyCreateTime") or child.get("createdAt") or child.get("createTimeISO")),
                                "verified": False if verified is None else bool(verified),
                                "profileImage": safe_str(child.get("replyAuthorAvatar") or child.get("avatar")),
                            }
                            replies.append({k: v for k, v in reply_row.items() if v is not None})
                            if len(replies) >= limit:
                                break
                    continue
                verified = r.get("replyAuthorVerified") or r.get("verified")
                reply_row = {
                    "id": safe_str(r.get("replyId") or r.get("cid") or r.get("id")),
                    "text": (r.get("replyText") or r.get("text") or r.get("body") or "").strip(),
                    "author": safe_str(r.get("replyAuthorUsername") or r.get("uniqueId") or r.get("author")),
                    "authorId": safe_str(r.get("uid") or r.get("userId") or r.get("authorUid")),
                    "authorSecUid": safe_str(r.get("secUid") or r.get("sec_uid") or r.get("authorSecUid")),
                    "authorName": safe_str(r.get("replyAuthorNickname") or r.get("authorName") or r.get("nickname") or r.get("author")),
                    "commentLanguage": safe_str(r.get("commentLanguage") or r.get("comment_language")),
                    "likeCount": safe_int(r.get("replyLikeCount") or r.get("likeCount") or r.get("likes")),
                    "publishedAt": safe_str(r.get("replyCreateTime") or r.get("createdAt") or r.get("createTimeISO")),
                    "verified": False if verified is None else bool(verified),
                    "profileImage": safe_str(r.get("replyAuthorAvatar") or r.get("avatar") or r.get("authorAvatarUrl")),
                }
                replies.append({k: v for k, v in reply_row.items() if v is not None})
                if len(replies) >= limit:
                    break
            ctx["source"] = "apify"
            return {
                "platform": "tiktok",
                "url": url,
                "commentId": comment_id,
                "totalReturned": len(replies),
                "totalReplies": None,
                "replies": replies,
                "nextCursor": None,
                "hasMore": False,
            }

        data = await cached_or_run(
            endpoint="tiktok.comment-replies",
            params={"url": url, "comment_id": comment_id, "limit": limit, "cursor": cursor or "", "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/user-followers", summary="List a TikTok user's followers")
async def tiktok_user_followers(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FOLLOWERS, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/user-followers",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await user_connections_native(handle, mode="followers", limit=limit)
            if native is not None:
                ctx["source"] = "direct"
                return {"url": url, "totalReturned": len(native), "followers": native}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_FOLLOWERS,
                {
                    "profiles": [handle],
                    "maxFollowersPerProfile": limit,
                    "maxFollowingPerProfile": 0,
                },
                max_items=limit,
            )
            users = [
                _normalize_connection(i)
                for i in items
                if i.get("connectionType") == "follower"
            ][:limit]
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(users), "followers": users}

        data = await cached_or_run(
            endpoint="tiktok.user-followers",
            params={"url": url, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["followers"]), RATE_FOLLOWERS, 5)
        return ApiResponse(data=data)


@router.get("/user-followings", summary="List who a TikTok user follows")
async def tiktok_user_followings(
    url: str = Query(..., description="TikTok profile URL, @handle, or username"),
    limit: int = Query(50, ge=1, le=500),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_tiktok_profile(url)
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_FOLLOWERS, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/user-followings",
        platform="tiktok",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await user_connections_native(handle, mode="followings", limit=limit)
            if native is not None:
                ctx["source"] = "direct"
                return {"url": url, "totalReturned": len(native), "followings": native}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK_FOLLOWINGS,
                {
                    "profiles": [handle],
                    "maxFollowersPerProfile": 0,
                    "maxFollowingPerProfile": limit,
                },
                max_items=limit,
            )
            users = [
                _normalize_connection(i)
                for i in items
                if i.get("connectionType") == "following"
            ][:limit]
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(users), "followings": users}

        data = await cached_or_run(
            endpoint="tiktok.user-followings",
            params={"url": url, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["followings"]), RATE_FOLLOWERS, 5)
        return ApiResponse(data=data)


@router.get("/music-posts", summary="Posts using a TikTok sound/music")
async def tiktok_music_posts(
    url: str = Query(..., description="TikTok music/sound URL"),
    limit: int = Query(
        20,
        ge=1,
        le=200,
        description="How many videos using this sound to return (1–200). Flat 2 credits per call.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_tiktok_music_url(url)
    settings = get_settings()
    # Flat fee: native music/aweme is ~$0; Apify fallback is rare and covered
    # by the same 2-credit charge (same model as channel-posts / comments).
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/music-posts",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_MUSIC_POSTS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            music_id = _tiktok_music_id(url)

            def _stamp_sound(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
                sound_title = next((p.get("musicName") for p in posts if p.get("musicName")), None)
                if not sound_title:
                    sound_title = _music_name_from_url(url)
                for post in posts:
                    if sound_title and not post.get("musicName"):
                        post["musicName"] = sound_title
                    # Echo the requested sound id onto every row (MUSIC_AWEME often omits it).
                    if music_id and not post.get("musicId"):
                        post["musicId"] = music_id
                return posts

            native = await music_posts_native(url, limit)
            if native is not None:
                posts = _stamp_sound([_tt_finalize_post(p) for p in native])
                ctx["source"] = "direct"
                return {"url": url, "totalReturned": len(posts), "posts": posts}

            apify = get_apify()
            items, _actor = await apify.run_with_fallback(
                _tiktok_music_candidates(settings, url, limit),
                max_items=limit,
            )
            posts = _stamp_sound([_normalize_music_post(i) for i in items[:limit]])
            ctx["source"] = "apify"
            return {"url": url, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="tiktok.music-posts",
            params={"url": url, "limit": limit, "v": 12},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/top-search", summary="Top mixed TikTok search results for a keyword")
async def tiktok_top_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=200),
    cursor: int = Query(
        0,
        ge=0,
        description=(
            "Pagination cursor. Leave 0 for the first page; then pass the "
            "nextCursor from the previous response. TikTok may return duplicates."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    """TikTok's Top/General search tab — videos and photo carousels when present.

    Unlike hashtag/keyword video-only scrapers, results can include photo
    carousels (``contentType: multi_photo`` + ``images[]``). Hashtags are
    lowercase-deduped; ``hashtags`` is always an array (possibly empty).
    TikTok itself may repeat items across pages.
    """
    # Native-only search — flat fee (same model as channel-posts).
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/top-search",
        platform="tiktok",
        resource_url=None,
        base_credits=CREDIT_SEARCH,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await top_search_native(q, limit=limit, cursor=cursor)
            if native is not None:
                rows, has_more, next_cursor = native
                results = [_tt_finalize_post(p) for p in rows]
                ctx["source"] = "direct"
                return {
                    "query": q,
                    "totalReturned": len(results),
                    "hasMore": has_more,
                    "nextCursor": next_cursor,
                    "results": results,
                }
            raise HTTPException(
                status_code=502,
                detail="TikTok search temporarily unavailable",
            )

        data = await cached_or_run(
            endpoint="tiktok.top-search",
            params={"q": q, "limit": limit, "cursor": cursor, "v": 8},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/search/hashtag",
    summary="TikTok videos posted under a hashtag (tag/challenge feed)",
    description=(
        "Returns videos from TikTok's /tag/{name} challenge feed — not keyword "
        "or username search. Each result must carry the requested hashtag in "
        "structured tags or as #tag in the caption; @comedy… accounts without "
        "#comedy are dropped. region only chooses the proxy exit country — it "
        "does not filter results by country. Cursor pagination via nextCursor / "
        "hasMore (nextCursor null = last page)."
    ),
)
async def tiktok_search_by_hashtag(
    q: str = Query(..., min_length=2, description="Hashtag to search for (with or without the leading #)."),
    limit: int = Query(20, ge=1, le=100, description="Number of videos to return per page."),
    cursor: int = Query(
        0,
        ge=0,
        description="Pagination offset. Pass the `nextCursor` from the previous response to fetch the next page.",
    ),
    region: str = Query(
        "US",
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country the scraping proxy is routed through. This only sets the proxy location — it does not restrict results to that country.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    region_code = region.strip().upper()
    tag = normalize_hashtag_query(q)
    if not tag:
        raise HTTPException(status_code=400, detail="Expected a hashtag (e.g. comedy or #comedy)")
    cost = _scaled_credits(limit, RATE_CHANNEL_POSTS, CREDIT_SEARCH)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/search/hashtag",
        platform="tiktok",
        resource_url=f"https://www.tiktok.com/tag/{tag}",
        base_credits=cost,
    ) as ctx:
        def _keep_tagged(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return [r for r in rows if item_has_hashtag(r, tag)]

        async def _run() -> dict[str, Any]:
            # Primary: Decodo opens /tag/{name} and captures signed
            # /api/challenge/item_list/ (real challenge feed). Over-fetch a bit
            # then require the hashtag so keyword bleed never ships.
            if cursor == 0:
                native = await hashtag_posts_native(tag, limit=max(limit * 2, limit))
                if native is not None:
                    posts, has_more, _tt_cursor = native
                    results = _keep_tagged([_tt_finalize_post(p) for p in posts])[:limit]
                    if results:
                        ctx["source"] = "direct"
                        return {
                            "query": q,
                            "hashtag": tag,
                            "totalReturned": len(results),
                            "hasMore": has_more or len(posts) > limit,
                            "nextCursor": limit if (has_more or len(posts) > limit) else None,
                            "results": results,
                        }

            apify = get_apify()
            # Prefer the tag page URL. The ``hashtags: [q]`` actor input has been
            # observed to return keyword/username matches (e.g. @comedy7092 with
            # no #comedy) — never trust that path without the hashtag filter.
            want = cursor + max(limit * 3, limit)
            tag_url = f"https://www.tiktok.com/tag/{tag}"
            items: list[dict[str, Any]] = []
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_TIKTOK,
                    {
                        "startUrls": [tag_url],
                        "resultsPerPage": want,
                        "shouldDownloadVideos": False,
                        "proxyConfiguration": {
                            "useApifyProxy": True,
                            "apifyProxyCountry": region_code,
                        },
                    },
                    max_items=want,
                )
            except Exception:  # noqa: BLE001
                items = []
            if not items:
                try:
                    items = await apify.run_actor_sync(
                        settings.APIFY_ACTOR_TIKTOK,
                        {
                            "hashtags": [tag],
                            "resultsPerPage": want,
                            "shouldDownloadVideos": False,
                            "proxyConfiguration": {
                                "useApifyProxy": True,
                                "apifyProxyCountry": region_code,
                            },
                        },
                        max_items=want,
                    )
                except Exception:  # noqa: BLE001
                    items = []

            mapped = [_normalize(i) for i in (items or []) if isinstance(i, dict)]
            tagged = _keep_tagged(mapped)
            page = tagged[cursor : cursor + limit]
            has_more = len(tagged) > cursor + limit
            if not page:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"No videos found under #{tag}. "
                        "This endpoint only returns the TikTok tag/challenge feed, "
                        "not keyword or username search."
                    ),
                )
            ctx["source"] = "apify"
            return {
                "query": q,
                "hashtag": tag,
                "totalReturned": len(page),
                "hasMore": has_more,
                "nextCursor": (cursor + limit) if has_more else None,
                "results": page,
            }

        data = await cached_or_run(
            endpoint="tiktok.search-hashtag",
            params={"q": tag, "limit": limit, "cursor": cursor, "region": region_code, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["results"]), RATE_CHANNEL_POSTS, CREDIT_SEARCH)
        return ApiResponse(data=data)


@router.get("/search/users", summary="Search TikTok users by keyword")
async def tiktok_search_users(
    q: str = Query(..., min_length=2, description="Search query matched against usernames, display names and bios."),
    limit: int = Query(20, ge=1, le=100, description="Number of users to return per page."),
    cursor: int = Query(
        0,
        ge=0,
        description="Pagination offset. Pass the `nextCursor` from the previous response to fetch the next page.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    # Upfront reserve Apify worst-case; native path overrides to 1 credit.
    cost = _scaled_credits(limit, RATE_USER_SEARCH, 5)
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/search/users",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await search_users_native(q, limit=limit, cursor=cursor)
            if native is not None:
                users, has_more, next_cursor = native
                ctx["source"] = "direct"
                return {
                    "query": q,
                    "totalReturned": len(users),
                    "hasMore": has_more,
                    "nextCursor": next_cursor if has_more else None,
                    "users": users,
                }

            apify = get_apify()
            want = cursor + limit
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TIKTOK,
                {
                    "searchQueries": [q],
                    "searchSection": "/user",
                    "maxProfilesPerQuery": want,
                    "resultsPerPage": want,
                },
                max_items=want,
            )
            page = items[cursor : cursor + limit]
            users = [_normalize_user(i) for i in page]
            has_more = len(items) > cursor + limit
            ctx["source"] = "apify"
            return {
                "query": q,
                "totalReturned": len(users),
                "hasMore": has_more,
                "nextCursor": (cursor + limit) if has_more else None,
                "users": users,
            }

        data = await cached_or_run(
            endpoint="tiktok.search-users",
            params={"q": q, "limit": limit, "cursor": cursor, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_USER_SEARCH_NATIVE
        else:
            ctx["credits_override"] = _scaled_credits(len(data["users"]), RATE_USER_SEARCH, 5)
        return ApiResponse(data=data)


def _song_from_apify_music(music: dict[str, Any], *, url: str, url_id: str | None) -> dict[str, Any] | None:
    """Best-effort map of Apify sound/music actor rows into song-details shape."""
    if not isinstance(music, dict):
        return None
    # Prefer the shared normalizer when the actor already returns TikTok-shaped keys.
    normalized = normalize_song_details(music, url=url, music_id=url_id)
    if normalized and normalized.get("title"):
        # Overlay usageCount from common actor aliases when native-shaped count is missing.
        if normalized.get("usageCount") is None:
            for key in (
                "user_count",
                "userCount",
                "videoCount",
                "video_count",
                "musicVideoCount",
                "videosCount",
            ):
                n = safe_int(music.get(key))
                if n is not None and n > 0:
                    normalized["usageCount"] = n
                    break
        return normalized

    title = safe_str(
        music.get("title")
        or music.get("musicName")
        or music.get("soundTitle")
        or music.get("name")
    )
    if not title:
        return None
    usage = None
    for key in (
        "user_count",
        "userCount",
        "videoCount",
        "video_count",
        "musicVideoCount",
        "videosCount",
    ):
        n = safe_int(music.get(key))
        if n is not None and n > 0:
            usage = n
            break
    original = music.get("musicOriginal")
    if original is None:
        original = music.get("is_original_sound")
    if original is None:
        original = bool(title.lower().startswith("original sound"))
    cover = safe_str(
        music.get("coverLarge")
        or music.get("cover_large")
        or music.get("coverMedium")
        or music.get("coverUrl")
        or music.get("cover")
        or music.get("soundCoverUrl")
    )
    return {
        "platform": "tiktok",
        "url": url,
        "id": url_id
        or safe_str(music.get("musicId") or music.get("soundId") or music.get("id") or music.get("id_str")),
        "mid": safe_str(music.get("mid"))
        or url_id
        or safe_str(music.get("musicId") or music.get("id")),
        "title": title,
        "author": safe_str(
            music.get("musicAuthor")
            or music.get("authorName")
            or music.get("soundAuthor")
            or music.get("artist")
            or music.get("author")
        ),
        "artists": [],
        "original": bool(original) if original is not None else None,
        "isOriginalSound": bool(original) if original is not None else None,
        "album": safe_str(music.get("album") or music.get("soundAlbum")) or None,
        "durationSeconds": duration_seconds(
            music.get("duration") or music.get("durationSeconds") or music.get("soundDuration")
        ),
        "duration": duration_seconds(
            music.get("duration") or music.get("durationSeconds") or music.get("soundDuration")
        ),
        "coverUrl": cover,
        "cover": {
            "large": safe_str(music.get("coverLarge") or music.get("cover_large")),
            "medium": safe_str(music.get("coverMedium") or music.get("cover_medium")),
            "thumb": safe_str(music.get("coverThumb") or music.get("cover_thumb")),
        },
        "playUrl": safe_str(music.get("playUrl") or music.get("audioUrl") or music.get("play_url")),
        "usageCount": usage,
        "createdAt": None,
        "createTime": safe_int(music.get("create_time") or music.get("createTime")),
        "isCommerceMusic": None,
        "hasCommerceRight": None,
        "commercialRightType": None,
        "matchedSong": None,
        "musicReleaseInfo": None,
        "extra": None,
        "strongBeatUrl": None,
        "similarMusic": None,
        "recList": None,
    }


@router.get("/song-details", summary="Details of a TikTok sound/song")
async def tiktok_song_details(
    url: str = Query(..., description="TikTok music/sound URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    url = _require_tiktok_music_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/song-details",
        platform="tiktok",
        resource_url=url,
        base_credits=CREDIT_SONG_DETAILS_APIFY,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Primary: music/aweme mobile API (~1-3s). Same metadata the sound
            # page uses; Apify actors stay as fallback for soft-blocked exits.
            native = await song_details_native(url)
            if native is not None and native.get("title"):
                ctx["source"] = "direct"
                return native

            apify = get_apify()
            # The TikTok music URL ends with the numeric sound id; parse it here
            # because apidojo returns the id as a JS number (precision loss).
            m = re.search(r"/music/[^/]*?(\d{6,})|/sound/[^/]*?(\d{6,})|(\d{6,})(?:\?|$)", url)
            url_id = next((g for g in (m.groups() if m else ()) if g), None)

            async def _play_url_from_clockworks() -> str | None:
                # apidojo/coregent omit the CDN audio URL; clockworks exposes playUrl.
                try:
                    cw_items = await apify.run_actor_sync(
                        settings.APIFY_ACTOR_TIKTOK_MUSIC_FALLBACK,
                        {
                            "musics": [url],
                            "resultsPerPage": 1,
                            "shouldDownloadVideos": False,
                        },
                        max_items=1,
                    )
                except Exception:  # noqa: BLE001
                    return None
                if not cw_items:
                    return None
                music = cw_items[0].get("musicMeta") or cw_items[0].get("music") or cw_items[0]
                return safe_str(music.get("playUrl") or music.get("audioUrl"))

            async def _enrich_play_url(payload: dict[str, Any]) -> dict[str, Any]:
                if payload.get("playUrl"):
                    return payload
                play_url = await _play_url_from_clockworks()
                if play_url:
                    payload["playUrl"] = play_url
                return payload

            # Fast path: apidojo music scraper (~9s, has duration + cover).
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_TIKTOK_SONG,
                    {"startUrls": [url], "maxItems": 1},
                    max_items=1,
                )
            except Exception:  # noqa: BLE001
                items = []
            if items:
                song = items[0].get("song") or items[0].get("music") or items[0]
                mapped = _song_from_apify_music(song, url=url, url_id=url_id)
                if mapped and mapped.get("title"):
                    ctx["source"] = "apify"
                    return await _enrich_play_url(mapped)

            # apidojo failed: the remaining fallbacks are independent actors, so
            # race them concurrently instead of cascading (worst case used to be
            # 3 more sequential actor runs). Costs one possibly-redundant run
            # only on this already-failing path.
            async def _summary_fallback() -> dict[str, Any] | None:
                # Summary-only sound scraper: no video crawling.
                try:
                    summary_items = await apify.run_actor_sync(
                        settings.APIFY_ACTOR_TIKTOK_SONG_FAST_FALLBACK,
                        {
                            "sounds": [url_id or url],
                            # The actor rejects 0 ("must be >= 1"), so ask for
                            # the minimum even though we only want the summary.
                            "maxVideosPerSound": 1,
                            "includeSoundSummary": True,
                            "includeVideoFields": False,
                        },
                        max_items=1,
                    )
                except Exception:  # noqa: BLE001
                    return None
                if not summary_items:
                    return None
                item = summary_items[0]
                music = item.get("sound") or item.get("music") or item.get("summary") or item
                return _song_from_apify_music(music, url=url, url_id=url_id)

            async def _clockworks_fallback() -> dict[str, Any] | None:
                # Prefer clockworks (has playUrl) over coregent summary.
                try:
                    items, _actor = await apify.run_with_fallback(
                        [
                            (
                                settings.APIFY_ACTOR_TIKTOK_MUSIC_FALLBACK,
                                {
                                    "musics": [url],
                                    "resultsPerPage": 1,
                                    "shouldDownloadVideos": False,
                                },
                            ),
                            (
                                settings.APIFY_ACTOR_TIKTOK_MUSIC,
                                {
                                    "sounds": [url_id or url],
                                    "maxVideosPerSound": 1,
                                    "includeSoundSummary": True,
                                    "includeVideoFields": False,
                                },
                            ),
                        ],
                        max_items=1,
                    )
                except Exception:  # noqa: BLE001
                    return None
                if not items:
                    return None
                music = (
                    items[0].get("musicMeta")
                    or items[0].get("music")
                    or items[0].get("sound")
                    or items[0].get("summary")
                    or items[0]
                )
                return _song_from_apify_music(music, url=url, url_id=url_id)

            summary_result, clockworks_result = await asyncio.gather(
                _summary_fallback(), _clockworks_fallback()
            )
            if clockworks_result and clockworks_result.get("playUrl"):
                result = clockworks_result
            else:
                result = summary_result or clockworks_result
            if not result:
                raise HTTPException(status_code=404, detail="Song not found")
            ctx["source"] = "apify"
            return await _enrich_play_url(result)

        data = await cached_or_run(
            endpoint="tiktok.song-details",
            params={"url": url, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_SONG_DETAILS_NATIVE
        else:
            ctx["credits_override"] = CREDIT_SONG_DETAILS_APIFY
        return ApiResponse(data=data)


@router.get(
    "/trending-feed",
    summary="TikTok trending feed (For You or Creative Center popular)",
    description=(
        "Default: For You / recommend feed with engagement, rank, and author. "
        "Pass orderBy, period, page, or countryCode to switch to TikTok Creative "
        "Center popular videos (SC videos/popular filters) — same rich item shape "
        "when hydration succeeds, plus pagination.totalCount (typically 500)."
    ),
)
async def tiktok_trending_feed(
    country: str = Query(
        "US",
        min_length=2,
        max_length=2,
        description=(
            "ISO country code (alias of countryCode). For You: region-availability "
            "hint. Creative Center mode: chart market."
        ),
    ),
    countryCode: str | None = Query(
        None,
        min_length=2,
        max_length=2,
        description="Alias of country (SC-compatible). Wins when both are set.",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=200,
        description="Max items (default 20). Creative Center caps at 20/page. Flat 2 credits.",
    ),
    orderBy: str | None = Query(
        None,
        description=(
            "Creative Center sort: hot (views), like, comment, repost. "
            "When set (or period/page>1), uses the popular-videos chart instead of For You."
        ),
    ),
    period: int | None = Query(
        None,
        description="Creative Center lookback days: 7, 30, or 120 (180→120). Triggers chart mode.",
    ),
    page: int = Query(
        1,
        ge=1,
        le=25,
        description="Creative Center page (default 1). page>1 triggers chart mode.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    from app.services import tiktok_creative_center_trends as cc_trends
    from app.utils.media_urls import utc_now_iso

    region = (countryCode or country or "US").strip().upper()
    chart_mode = bool(orderBy) or period is not None or page > 1
    order_by_cc = "vv"
    period_days = 7
    if chart_mode:
        try:
            order_by_cc = cc_trends.normalize_video_order_by(orderBy or "hot")
            period_days = cc_trends.normalize_trend_period(period if period is not None else 7)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/trending-feed",
        platform="tiktok",
        resource_url=None,
        base_credits=CREDIT_SEARCH,
    ) as ctx:
        async def _hydrate_cc(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
            """Best-effort video-details overlay so CC rows keep Captapi richness."""
            sem = asyncio.Semaphore(4)

            async def one(row: dict[str, Any]) -> dict[str, Any]:
                url = safe_str(row.get("url"))
                if not url:
                    return row
                async with sem:
                    try:
                        detail = await video_details_native(url)
                    except Exception:  # noqa: BLE001
                        return row
                if not detail:
                    return row
                eng = detail.get("engagement") if isinstance(detail.get("engagement"), dict) else {}
                author = detail.get("author") if isinstance(detail.get("author"), dict) else {}
                merged = {
                    **row,
                    "caption": detail.get("caption") or row.get("caption"),
                    "publishedAt": detail.get("publishedAt") or row.get("publishedAt"),
                    "createTime": detail.get("createTime") or row.get("createTime"),
                    "mediaType": detail.get("mediaType") or row.get("mediaType"),
                    "durationSeconds": detail.get("durationSeconds")
                    if detail.get("durationSeconds") is not None
                    else row.get("durationSeconds"),
                    "coverUrl": detail.get("thumbnailUrl") or row.get("coverUrl"),
                    "thumbnailUrl": detail.get("thumbnailUrl") or row.get("thumbnailUrl"),
                    "videoUrl": detail.get("videoUrl") or row.get("videoUrl"),
                    "author": author.get("username") or row.get("author"),
                    "authorId": author.get("id") or row.get("authorId"),
                    "secUid": author.get("secUid") or row.get("secUid"),
                    "authorName": author.get("displayName") or row.get("authorName"),
                    "views": eng.get("views") if eng.get("views") is not None else row.get("views"),
                    "likes": eng.get("likes") if eng.get("likes") is not None else row.get("likes"),
                    "comments": eng.get("comments")
                    if eng.get("comments") is not None
                    else row.get("comments"),
                    "shares": eng.get("shares")
                    if eng.get("shares") is not None
                    else row.get("shares"),
                    "saves": eng.get("saves") if eng.get("saves") is not None else row.get("saves"),
                    "isAd": bool(detail.get("isAd")) if detail.get("isAd") is not None else row.get("isAd"),
                }
                return {k: v for k, v in merged.items() if v is not None}

            return list(await asyncio.gather(*(one(r) for r in rows)))

        async def _run() -> dict[str, Any]:
            scraped = utc_now_iso()
            if chart_mode:
                cc = await cc_trends.search_popular_videos(
                    country=region,
                    period=period_days,
                    page=page,
                    limit=min(limit, 20),
                    order_by=order_by_cc,
                )
                if cc and cc.get("results"):
                    ctx["source"] = "direct"
                    results = await _hydrate_cc(list(cc["results"]))
                    return {
                        "country": region,
                        "countryCode": region,
                        "period": period_days,
                        "page": page,
                        "orderBy": order_by_cc,
                        "source": "creative_center",
                        "totalReturned": len(results),
                        "pagination": cc.get("pagination"),
                        "results": results,
                        "scrapedAt": scraped,
                        "fetchedAt": scraped,
                    }
                # Chart miss → For You fallthrough (still honor country).
            native = await trending_feed_native(region, limit=limit)
            if native:
                ctx["source"] = "direct"
                out: dict[str, Any] = {
                    "country": region,
                    "countryCode": region,
                    "source": "for_you",
                    "totalReturned": len(native),
                    "results": native,
                    "scrapedAt": scraped,
                    "fetchedAt": scraped,
                }
                if chart_mode:
                    out["period"] = period_days
                    out["page"] = page
                    out["orderBy"] = order_by_cc
                    out["note"] = (
                        "Creative Center chart unavailable; returned For You feed "
                        "for the same country."
                    )
                return out
            raise HTTPException(
                status_code=502,
                detail="TikTok trending feed temporarily unavailable",
            )

        data = await cached_or_run(
            endpoint="tiktok.trending-feed",
            params={
                "country": region,
                "limit": limit,
                "orderBy": order_by_cc if chart_mode else None,
                "period": period_days if chart_mode else None,
                "page": page if chart_mode else 1,
                "v": 5,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/popular-hashtags",
    summary="TikTok Creative Center popular hashtags",
    description=(
        "Official TikTok Creative Center hashtag chart "
        "(ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag). "
        "videoCount / totalPlays are Creative Center population totals — not "
        "sample tallies. Also returns rankDiff, trend[] time series, and "
        "growthRate derived from trend. Pass query for legacy co-occurrence "
        "related-tag discovery (challenge/detail enrich). Flat 2 credits on "
        "the Creative Center path."
    ),
)
async def tiktok_popular_hashtags(
    country: str = Query(
        "US",
        min_length=2,
        max_length=2,
        description="Two-letter ISO country code for the Creative Center chart. Default US.",
    ),
    period: int = Query(
        7,
        description="Lookback window in days: 7, 30, or 120 (180 maps to 120). Default 7.",
    ),
    page: int = Query(1, ge=1, le=20, description="Creative Center page (default 1)."),
    sort_by: str = Query(
        "popular",
        alias="sortBy",
        description="Chart sort: popular (default).",
    ),
    new_on_board: bool = Query(
        False,
        alias="newOnBoard",
        description="If true, only hashtags newly on the Top 100 board.",
    ),
    industry_id: str | None = Query(
        None,
        alias="industryId",
        description="Optional Creative Center industry_id filter.",
    ),
    query: str | None = Query(
        None,
        description=(
            "Optional niche seed for legacy co-occurrence discovery. When set "
            "(and not \"trending\"), skips the Creative Center chart and finds "
            "related tags from seed videos + challenge/detail enrich."
        ),
    ),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    from app.services import tiktok_creative_center_trends as cc_trends
    from app.utils.media_urls import utc_now_iso

    settings = get_settings()
    seed = (query or "").lstrip("#").strip()
    use_cooccurrence = bool(seed) and seed.lower() != "trending"
    n_videos = max(limit, 25)
    cost = (
        _scaled_credits(n_videos, RATE_TREND, CREDIT_SEARCH)
        if use_cooccurrence
        else CREDIT_CC_TREND
    )
    try:
        period_days = cc_trends.normalize_trend_period(period)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/popular-hashtags",
        platform="tiktok",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            if not use_cooccurrence:
                cc = await cc_trends.search_popular_hashtags(
                    country=country.upper(),
                    period=period_days,
                    page=page,
                    limit=limit,
                    sort_by=sort_by,
                    new_on_board=new_on_board,
                    industry_id=industry_id,
                )
                if cc and cc.get("hashtags"):
                    ctx["source"] = "direct"
                    cc["fetchedAt"] = utc_now_iso()
                    return cc
                # Apify Creative Center trends fallthrough.
                try:
                    items, _actor = await get_apify().run_with_fallback(
                        [
                            (
                                settings.APIFY_ACTOR_TIKTOK_CREATIVE_CENTER_TRENDS,
                                cc_trends.apify_trends_input(
                                    mode="hashtags",
                                    country=country.upper(),
                                    period=period_days,
                                    limit=limit,
                                ),
                            )
                        ],
                        max_items=limit,
                    )
                except Exception:  # noqa: BLE001
                    items = []
                if items:
                    hashtags = []
                    for i, raw in enumerate(items[:limit]):
                        if not isinstance(raw, dict):
                            continue
                        mapped = cc_trends.normalize_trend_hashtag(
                            raw, country=country.upper(), period=period_days
                        )
                        if mapped:
                            mapped.setdefault("rank", i + 1)
                            hashtags.append(mapped)
                    if hashtags:
                        ctx["source"] = "apify"
                        return {
                            "country": country.upper(),
                            "period": period_days,
                            "page": page,
                            "source": "apify",
                            "discovery": "creative_center",
                            "rankBy": "creative_center_rank",
                            "fetchedAt": utc_now_iso(),
                            "totalReturned": len(hashtags),
                            "hashtags": hashtags,
                        }

            # Legacy / related-tag path (or CC miss with a seed).
            seed_q = seed or "trending"
            native_payload = await popular_hashtags_native(
                seed_q, limit=limit, n_videos=n_videos
            )
            if native_payload and native_payload.get("hashtags"):
                ctx["source"] = "direct"
                native_payload["fetchedAt"] = utc_now_iso()
                return native_payload

            apify = get_apify()
            items, _actor = await apify.run_with_fallback(
                [
                    (
                        settings.APIFY_ACTOR_TIKTOK_TREND_DISCOVERY,
                        {
                            "searchQueries": [],
                            "hashtags": [seed_q],
                            "resultsPerQuery": n_videos,
                            "includeVideos": True,
                            "includeHashtags": False,
                            "sortBy": "popular",
                            "proxyConfiguration": {"useApifyProxy": True},
                        },
                    ),
                    (
                        settings.APIFY_ACTOR_TIKTOK,
                        {
                            "hashtags": [seed_q],
                            "resultsPerPage": n_videos,
                            "shouldDownloadVideos": False,
                        },
                    ),
                ],
                max_items=n_videos,
            )
            agg: dict[str, dict[str, int]] = {}
            sample_videos = 0
            for v in items:
                if v.get("recordType") and v.get("recordType") != "video":
                    continue
                sample_videos += 1
                tags = v.get("hashtags") or v.get("challenges")
                if not isinstance(tags, list):
                    tags = []
                stats = v.get("stats") or {}
                plays = safe_int(v.get("playCount") or stats.get("playCount")) or 0
                for t in tags:
                    name = safe_str(t.get("name") if isinstance(t, dict) else t)
                    if not name:
                        continue
                    name = name.lstrip("#").lower()
                    if not name:
                        continue
                    slot = agg.setdefault(name, {"count": 0, "plays": 0})
                    slot["count"] += 1
                    slot["plays"] += plays
            candidate_n = min(len(agg), max(limit * 2, limit))
            by_sample = sorted(
                agg.items(), key=lambda kv: (kv[1]["count"], kv[1]["plays"]), reverse=True
            )[:candidate_n]
            sample_rows = [
                {
                    "name": name,
                    "url": f"https://www.tiktok.com/tag/{name}",
                    "sampleVideoCount": slot["count"],
                    "samplePlays": slot["plays"],
                    "videoCount": None,
                    "totalPlays": None,
                    "hashtagId": None,
                    "growthRate": None,
                }
                for name, slot in by_sample
            ]
            enriched = await enrich_hashtag_population_stats(sample_rows)
            enriched.sort(
                key=lambda r: (
                    r.get("videoCount") is not None,
                    r.get("videoCount") or 0,
                    r.get("sampleVideoCount") or 0,
                    r.get("samplePlays") or 0,
                ),
                reverse=True,
            )
            hashtags = []
            for i, row in enumerate(enriched[:limit]):
                row = dict(row)
                row["rank"] = i + 1
                hashtags.append(row)
            ctx["source"] = "apify"
            return {
                "query": seed_q,
                "discovery": "co_occurrence",
                "discoverySource": "apify_hashtag_videos",
                "sampleSize": sample_videos,
                "rankBy": "videoCount",
                "fetchedAt": utc_now_iso(),
                "totalReturned": len(hashtags),
                "hashtags": hashtags,
            }

        data = await cached_or_run(
            endpoint="tiktok.popular-hashtags",
            params={
                "country": country.upper(),
                "period": period_days,
                "page": page,
                "sortBy": sort_by,
                "newOnBoard": new_on_board,
                "industryId": industry_id or "",
                "query": seed,
                "limit": limit,
                "v": 5,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        if data.get("discovery") == "creative_center" or data.get("source") == "creative_center":
            ctx["credits_override"] = CREDIT_CC_TREND
        else:
            ctx["credits_override"] = cost
        return ApiResponse(data=data)


@router.get(
    "/popular-songs",
    summary="TikTok Creative Center popular / surging songs",
    description=(
        "Official TikTok Creative Center sound chart "
        "(ads.tiktok.com/business/creativecenter/inspiration/popular/music). "
        "Filters: rankType=popular|surging, newOnBoard, commercialMusic "
        "(Commercial Music Library / ifCml), country, period (7/30/120), page. "
        "Each song includes rankDiff, trend[] time series, and growthRate. "
        "Can take up to ~30 seconds. Flat 2 credits."
    ),
)
async def tiktok_popular_songs(
    country: str = Query("US", min_length=2, max_length=2),
    period: int = Query(7, description="Lookback days: 7, 30, or 120 (180→120)."),
    page: int = Query(1, ge=1, le=20),
    rank_type: str = Query(
        "popular",
        alias="rankType",
        description="popular (chart) or surging (rising).",
    ),
    new_on_board: bool = Query(
        False,
        alias="newOnBoard",
        description="Only sounds newly on the Top 100 board.",
    ),
    commercial_music: bool = Query(
        False,
        alias="commercialMusic",
        description="Only Commercial Music Library–cleared sounds (brand-safe).",
    ),
    limit: int = Query(20, ge=1, le=20),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    from app.services import tiktok_creative_center_trends as cc_trends
    from app.utils.media_urls import utc_now_iso

    settings = get_settings()
    try:
        period_days = cc_trends.normalize_trend_period(period)
        rt = cc_trends.normalize_rank_type(rank_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    async with billed_call(
        caller=caller,
        endpoint="/v1/tiktok/popular-songs",
        platform="tiktok",
        resource_url=None,
        base_credits=CREDIT_CC_TREND,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            cc = await cc_trends.search_popular_songs(
                country=country.upper(),
                period=period_days,
                page=page,
                limit=limit,
                rank_type=rt,
                new_on_board=new_on_board,
                commercial_music=commercial_music,
            )
            if cc and cc.get("songs"):
                ctx["source"] = "direct"
                cc["fetchedAt"] = utc_now_iso()
                return cc

            try:
                items, _actor = await get_apify().run_with_fallback(
                    [
                        (
                            settings.APIFY_ACTOR_TIKTOK_CREATIVE_CENTER_TRENDS,
                            cc_trends.apify_trends_input(
                                mode="songs",
                                country=country.upper(),
                                period=period_days,
                                limit=limit,
                                rank_type=rt,
                            ),
                        )
                    ],
                    max_items=limit,
                )
            except Exception:  # noqa: BLE001
                items = []
            songs = []
            for i, raw in enumerate(items[:limit]):
                if not isinstance(raw, dict):
                    continue
                mapped = cc_trends.normalize_trend_song(
                    raw, country=country.upper(), period=period_days, rank_type=rt
                )
                if mapped:
                    mapped.setdefault("rank", i + 1)
                    songs.append(mapped)
            if not songs:
                raise HTTPException(
                    status_code=503,
                    detail="Creative Center popular songs unavailable right now. Retry shortly.",
                )
            ctx["source"] = "apify"
            return {
                "country": country.upper(),
                "period": period_days,
                "page": page,
                "rankType": rt,
                "newOnBoard": new_on_board,
                "commercialMusic": commercial_music,
                "source": "apify",
                "fetchedAt": utc_now_iso(),
                "totalReturned": len(songs),
                "songs": songs,
                "note": "Apify Creative Center fallthrough. Can take up to ~30 seconds.",
            }

        data = await cached_or_run(
            endpoint="tiktok.popular-songs",
            params={
                "country": country.upper(),
                "period": period_days,
                "page": page,
                "rankType": rt,
                "newOnBoard": new_on_board,
                "commercialMusic": commercial_music,
                "limit": limit,
                "v": 1,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = CREDIT_CC_TREND
        return ApiResponse(data=data)
