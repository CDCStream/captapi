"""Twitter / X endpoints (tweets, timelines, search, profiles).

Tweet details/transcript prefer the public syndication API; profile prefers
x.com HTML microdata (direct → Decodo). List endpoints still use apidojo Tweet
Scraper V2. Field mappings are defensive across native and actor shapes.
"""

from __future__ import annotations

import math
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services import twitter_native as native
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import first_present, safe_int, safe_list, safe_str, strip_empty
from app.utils.url import (
    detect_url_platform,
    extract_tweet_id,
    normalize_twitter_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_TWEET_DETAILS = 1
CREDIT_PROFILE = 1
# Native syndication/guest-token lists (user-tweets, search): flat 2.
CREDIT_TWEET_LIST = 2
# Community tweets still fall through to Apify; keep per-result rate.
# apidojo tweet-scraper ~$0.0004-0.0008/result → 0.7 credit/result (~80% markup).
RATE_TWEET = 0.7


def _scaled_credits(n: int, rate: float, minimum: int) -> int:
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _reject_twitter_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "twitter":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "twitter", example),
        )


def _require_tweet_url(url: str) -> str:
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "twitter", "https://x.com/user/status/123456789"),
        )
    return tweet_id


def _require_twitter_handle(value: str) -> str:
    _reject_twitter_platform_mismatch(value, "https://x.com/username")
    handle = normalize_twitter_username(value)
    if not handle:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "twitter", "https://x.com/username"),
        )
    return handle


def _author(a: dict[str, Any]) -> dict[str, Any]:
    username = a.get("userName") or a.get("screen_name") or a.get("username")
    verified = first_present(
        a.get("isVerified"),
        a.get("isBlueVerified"),
        a.get("is_blue_verified"),
        a.get("verified"),
    )
    return {
        "id": safe_str(a.get("id_str") or a.get("rest_id") or a.get("id") or a.get("userId")),
        "username": safe_str(username),
        "displayName": safe_str(a.get("name") or a.get("fullName")),
        "url": safe_str(a.get("url"))
        or (f"https://x.com/{username}" if username else None),
        "followers": safe_int(a.get("followers") or a.get("followersCount") or a.get("followers_count")),
        "verified": bool(verified) if verified is not None else None,
        "profileImage": safe_str(
            a.get("profilePicture") or a.get("profile_image_url_https") or a.get("profileImage")
        ),
    }


def _author_transcript(a: dict[str, Any] | None) -> dict[str, Any] | None:
    """Author for transcript — omit followers (syndication never provides them)."""
    if not isinstance(a, dict) or not a:
        return None
    # Accept raw syndication/actor user or already-normalized author.
    if "username" in a or "displayName" in a:
        out = {
            "username": safe_str(a.get("username")),
            "displayName": safe_str(a.get("displayName")),
            "url": safe_str(a.get("url")),
            "verified": a.get("verified"),
            "profileImage": safe_str(a.get("profileImage")),
        }
    else:
        full = _author(a)
        out = {
            "username": full.get("username"),
            "displayName": full.get("displayName"),
            "url": full.get("url"),
            "verified": full.get("verified"),
            "profileImage": full.get("profileImage"),
        }
    return out


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return None


def _tweet_is_reply(item: dict[str, Any]) -> bool | None:
    """Derive isReply across timeline + community actor field names."""
    explicit = first_present(item.get("isReply"), _as_bool(item.get("is_reply")))
    if explicit is not None:
        return bool(explicit)
    reply_to = item.get("in_reply_to_status_id") or item.get("inReplyToStatusId")
    if reply_to is not None:
        return bool(reply_to)
    # Badger community scraper uses snake_case engagement keys and omits
    # is_reply on root tweets — treat those as not-a-reply rather than null.
    if "view_count" in item or "favorite_count" in item:
        return False
    return None


def _tweet_is_retweet(item: dict[str, Any]) -> bool | None:
    explicit = first_present(item.get("isRetweet"), _as_bool(item.get("is_retweet")))
    if explicit is not None:
        return bool(explicit)
    if isinstance(item.get("retweeted_status"), dict):
        return True
    # Syndication timeline rows omit the flag on originals.
    if "favorite_count" in item or "retweet_count" in item:
        return False
    return None


def _nested_tweet(item: dict[str, Any]) -> dict[str, Any] | None:
    """Original tweet payload nested under a retweet/quote shell."""
    for key in ("retweet", "quote", "retweeted_status", "quoted_status", "quotedStatus"):
        nested = item.get(key)
        if isinstance(nested, dict) and nested:
            return nested
    return None


def _raw_hashtags(item: dict[str, Any]) -> list[Any]:
    entities = item.get("entities") if isinstance(item.get("entities"), dict) else {}
    return safe_list(item.get("hashtags") or entities.get("hashtags"))


_HASHTAG_FROM_TEXT = re.compile(r"(?<!\w)#([A-Za-z0-9_]+)")


def _tweet_hashtags(item: dict[str, Any]) -> list[str]:
    raw = _raw_hashtags(item)
    if not raw:
        nested = _nested_tweet(item)
        if nested:
            raw = _raw_hashtags(nested)
    tags: list[str] = []
    seen: set[str] = set()
    for h in raw:
        tag = (h.get("text") or h.get("tag")) if isinstance(h, dict) else safe_str(h)
        if not tag:
            continue
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        tags.append(tag.lstrip("#"))
    if tags:
        return tags
    # Syndication timeline often omits entities.hashtags — recover from text.
    text = safe_str(
        item.get("fullText") or item.get("text") or item.get("full_text")
    ) or ""
    for tag in _HASHTAG_FROM_TEXT.findall(text):
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        tags.append(tag)
    return tags


def _raw_media(item: dict[str, Any]) -> list[Any]:
    """Media list from top-level, syndication, extendedEntities, or entities.media."""
    direct = safe_list(item.get("media"))
    if direct:
        return direct
    # Syndication: mediaDetails[] / photos[] / video.poster
    details = safe_list(item.get("mediaDetails"))
    if details:
        return details
    photos = safe_list(item.get("photos"))
    if photos:
        return photos
    video = item.get("video")
    if isinstance(video, dict) and video.get("poster"):
        return [{"media_url_https": video.get("poster")}]
    for container_key in ("extendedEntities", "entities"):
        container = item.get(container_key)
        if isinstance(container, dict):
            media = safe_list(container.get("media"))
            if media:
                return media
    return []


def _tweet_media(item: dict[str, Any]) -> list[str]:
    """URL list; for retweets/quotes fall through to the nested original."""
    raw = _raw_media(item)
    if not raw:
        nested = _nested_tweet(item)
        if nested:
            raw = _raw_media(nested)
    urls: list[str] = []
    for m in raw:
        if isinstance(m, dict):
            # Prefer still/thumbnail URL over t.co permalink in `url`.
            u = safe_str(
                m.get("media_url_https")
                or m.get("mediaUrl")
                or m.get("media_url")
                or (m.get("url") if not str(m.get("url") or "").startswith("https://t.co/") else None)
                or m.get("url")
            )
        else:
            u = safe_str(m)
        if u:
            urls.append(u)
    return urls


def _strip_html_source(raw: Any) -> str | None:
    """``<a href=...>Twitter for iPhone</a>`` → ``Twitter for iPhone``."""
    text = safe_str(raw)
    if not text:
        return None
    cleaned = re.sub(r"<[^>]+>", "", text).strip()
    return cleaned or None


def _normalize_tweet(item: dict[str, Any]) -> dict[str, Any]:
    author = item.get("author") or item.get("user") or {}
    if not author and item.get("username"):
        # Community scraper rows are flat with user_* prefixed author fields.
        author = {
            "userName": item.get("username"),
            "name": item.get("user_name"),
            "followers": item.get("user_followers_count"),
            "verified": bool(_as_bool(item.get("user_verified")) or _as_bool(item.get("user_is_blue_verified"))),
            "profilePicture": item.get("user_profile_image_url"),
        }
    url = safe_str(item.get("url") or item.get("twitterUrl"))
    if not url:
        username = None
        if isinstance(author, dict):
            username = author.get("userName") or author.get("screen_name") or author.get("username")
        tweet_id = item.get("id_str") or item.get("id")
        if username and tweet_id:
            url = f"https://x.com/{username}/status/{tweet_id}"
    published_raw = first_present(item.get("createdAt"), item.get("created_at"))
    published = native._twitter_created_at_iso(published_raw) or safe_str(published_raw)
    hashtags = _tweet_hashtags(item)
    media = _tweet_media(item)
    is_quote = first_present(
        _as_bool(item.get("isQuote")),
        _as_bool(item.get("is_quote_status")),
        _as_bool(item.get("isQuoteStatus")),
    )
    possibly_sensitive = first_present(
        _as_bool(item.get("possiblySensitive")),
        _as_bool(item.get("possibly_sensitive")),
    )
    # Omit null engagement / author fields. Timeline syndication usually has
    # likes/replies/retweets/quotes; views/bookmarks/source often only on GraphQL
    # rows (search/community). Keep 0 when a source provides it.
    out = strip_empty({
        "platform": "twitter",
        "url": url,
        "id": safe_str(item.get("id_str") or item.get("id") or item.get("tweetId")),
        "text": safe_str(item.get("fullText") or item.get("text") or item.get("full_text")),
        "lang": safe_str(item.get("lang")),
        "publishedAt": published,
        "author": _author(author) if isinstance(author, dict) else None,
        "engagement": {
            # Community scraper uses snake_case view_count; GQL uses view_count;
            # timeline actors use camelCase viewCount.
            "views": safe_int(
                first_present(item.get("viewCount"), item.get("views"), item.get("view_count"))
            ),
            "likes": safe_int(
                first_present(item.get("likeCount"), item.get("favoriteCount"), item.get("favorite_count"))
            ),
            "replies": safe_int(
                first_present(
                    item.get("replyCount"),
                    item.get("reply_count"),
                    item.get("conversation_count"),
                )
            ),
            "retweets": safe_int(first_present(item.get("retweetCount"), item.get("retweet_count"))),
            "quotes": safe_int(first_present(item.get("quoteCount"), item.get("quote_count"))),
            "bookmarks": safe_int(first_present(item.get("bookmarkCount"), item.get("bookmark_count"))),
        },
        "isReply": _tweet_is_reply(item),
        "isRetweet": _tweet_is_retweet(item),
        "isQuote": is_quote,
        "possiblySensitive": possibly_sensitive,
        "conversationId": safe_str(
            item.get("conversationId")
            or item.get("conversation_id_str")
            or item.get("conversation_id")
        ),
        "source": _strip_html_source(item.get("source")),
    })
    # Always emit list keys so docs / clients see the contract (empty ≠ omitted).
    out["hashtags"] = hashtags
    out["media"] = media
    return out


def _entities_website(item: dict[str, Any]) -> str | None:
    entities = item.get("entities")
    if not isinstance(entities, dict):
        return None
    urls = (entities.get("url") or {}).get("urls")
    if isinstance(urls, list) and urls and isinstance(urls[0], dict):
        return safe_str(urls[0].get("expanded_url") or urls[0].get("url"))
    return None


def _verified_flag(item: dict[str, Any]) -> bool | None:
    """True/False when the actor reports verification, None when unknown.

    Must not use `a or b` chains: `False or None` collapses a real
    "not verified" answer into null.
    """
    value = first_present(item.get("isVerified"), item.get("isBlueVerified"), item.get("verified"))
    return bool(value) if value is not None else None


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    from app.services.tiktok_native import build_contact
    from app.utils.media_urls import utc_now_iso

    username = item.get("userName") or item.get("screen_name") or item.get("username")
    # Blue / legacy / identity stay independent — never use legacy.verified as blue.
    blue = first_present(item.get("isBlueVerified"), item.get("is_blue_verified"))
    legacy_v = first_present(
        item.get("isLegacyVerified"),
        item.get("is_legacy_verified"),
        (item.get("legacy") or {}).get("verified")
        if isinstance(item.get("legacy"), dict)
        else None,
    )
    identity = first_present(item.get("isIdentityVerified"), item.get("is_identity_verified"))
    affiliate = item.get("affiliate") if isinstance(item.get("affiliate"), dict) else None
    verified = None
    if blue is not None or legacy_v is not None or identity is not None or affiliate is not None:
        verified = bool(blue) or bool(legacy_v) or bool(identity) or bool(affiliate)
    elif item.get("verified") is not None:
        # Opaque aggregate from a thin source — keep as last resort only.
        verified = bool(item.get("verified"))

    verification = strip_empty(
        {
            "isBlueVerified": bool(blue) if blue is not None else None,
            "isLegacyVerified": bool(legacy_v) if legacy_v is not None else None,
            "isIdentityVerified": bool(identity) if identity is not None else None,
            "verifiedType": safe_str(item.get("verifiedType") or item.get("verified_type")),
            "reason": safe_str(item.get("verificationReason")),
            "verifiedSince": safe_str(item.get("verifiedSince")),
        }
    )

    pinned = item.get("pinnedTweetIds") or item.get("pinned_tweet_ids_str")
    if isinstance(pinned, list):
        pinned_ids = [str(x) for x in pinned if x is not None and str(x)]
    else:
        pinned_ids = None

    bio_urls = item.get("bioUrls")
    if not isinstance(bio_urls, list):
        # Fall back to legacy entities.description.urls when present.
        entities = item.get("entities") if isinstance(item.get("entities"), dict) else {}
        desc = entities.get("description") if isinstance(entities.get("description"), dict) else {}
        raw_urls = desc.get("urls") if isinstance(desc.get("urls"), list) else []
        bio_urls = []
        for u in raw_urls:
            if not isinstance(u, dict):
                continue
            expanded = safe_str(u.get("expanded_url") or u.get("expandedUrl") or u.get("url"))
            if not expanded:
                continue
            bio_urls.append(
                {
                    "url": safe_str(u.get("url")),
                    "expandedUrl": expanded,
                    "displayUrl": safe_str(u.get("display_url") or u.get("displayUrl")),
                }
            )
        if not bio_urls:
            bio_urls = None

    withheld = item.get("withheldInCountries") or item.get("withheld_in_countries")
    if not isinstance(withheld, list):
        withheld = None

    created = safe_str(item.get("createdAt") or item.get("created_at"))
    if created and "T" not in created:
        created = native._twitter_created_at_iso(created) or created

    tipjar = item.get("tipjarSettings") or item.get("tipjar_settings")
    if not isinstance(tipjar, dict):
        tipjar = None
    bio_text = safe_str(item.get("description") or item.get("bio"))
    contact = build_contact(
        bio=bio_text,
        tipjar=tipjar,
        bio_urls=bio_urls if isinstance(bio_urls, list) else None,
        links=[safe_str(item.get("website")) or _entities_website(item)]
        if (item.get("website") or _entities_website(item))
        else None,
    )

    display_name = safe_str(item.get("name") or item.get("fullName") or item.get("displayName"))
    out = strip_empty(
        {
            "platform": "twitter",
            "url": safe_str(item.get("url"))
            or (f"https://x.com/{username}" if username else None),
            "id": safe_str(item.get("id") or item.get("id_str")),
            "username": safe_str(username),
            # displayName matches TikTok/IG/YouTube; name kept for BC.
            "displayName": display_name,
            "name": display_name,
            "bio": bio_text,
            "location": safe_str(item.get("location")),
            "verified": verified,
            "isBlueVerified": bool(blue) if blue is not None else None,
            "isLegacyVerified": bool(legacy_v) if legacy_v is not None else None,
            "isIdentityVerified": bool(identity) if identity is not None else None,
            "verification": verification or None,
            "affiliate": affiliate,
            "followers": safe_int(first_present(item.get("followers"), item.get("followersCount"))),
            "following": safe_int(
                first_present(item.get("following"), item.get("followingCount"), item.get("friendsCount"))
            ),
            "fastFollowers": safe_int(
                first_present(item.get("fastFollowers"), item.get("fast_followers_count"))
            ),
            "normalFollowers": safe_int(
                first_present(item.get("normalFollowers"), item.get("normal_followers_count"))
            ),
            "tweetCount": safe_int(
                first_present(item.get("statusesCount"), item.get("tweetsCount"), item.get("statuses_count"))
            ),
            "likesCount": safe_int(
                first_present(item.get("favouritesCount"), item.get("favourites_count"), item.get("likesCount"))
            ),
            "mediaCount": safe_int(first_present(item.get("mediaCount"), item.get("media_count"))),
            "listedCount": safe_int(first_present(item.get("listedCount"), item.get("listed_count"))),
            "pinnedTweetIds": pinned_ids,
            "website": safe_str(item.get("website")) or _entities_website(item),
            "bioUrls": bio_urls,
            "contact": contact,
            "tipjarSettings": tipjar,
            "profileImage": safe_str(item.get("profilePicture") or item.get("profile_image_url_https")),
            "bannerImage": safe_str(item.get("coverPicture") or item.get("profile_banner_url")),
            "profileImageShape": safe_str(item.get("profileImageShape") or item.get("profile_image_shape")),
            "possiblySensitive": (
                bool(item.get("possiblySensitive"))
                if item.get("possiblySensitive") is not None
                else (
                    bool(item.get("possibly_sensitive"))
                    if item.get("possibly_sensitive") is not None
                    else None
                )
            ),
            "withheldInCountries": withheld,
            "highlightedTweets": safe_int(
                first_present(item.get("highlightedTweets"), item.get("highlighted_tweets"))
            ),
            "creatorSubscriptionsCount": safe_int(
                first_present(
                    item.get("creatorSubscriptionsCount"),
                    item.get("creator_subscriptions_count"),
                )
            ),
            "businessAffiliatesCount": safe_int(
                first_present(
                    item.get("businessAffiliatesCount"),
                    item.get("business_affiliates_count"),
                )
            ),
            "createdAt": created,
            "fetchedAt": utc_now_iso(),
        }
    )
    # Thin HTML fallbacks can omit verification bits — still promise the key.
    if "verified" not in out:
        out["verified"] = bool(verified) if verified is not None else False
    if display_name:
        out.setdefault("displayName", display_name)
        out.setdefault("name", display_name)
    return out


def _merge_tweet_row(base: dict[str, Any], richer: dict[str, Any]) -> dict[str, Any]:
    """Fill syndication gaps from a richer sibling row (user-tweets timeline)."""
    out = dict(base)
    for key in (
        "retweet_count",
        "quote_count",
        "reply_count",
        "favorite_count",
        "view_count",
        "bookmark_count",
        "source",
        "conversation_id_str",
        "conversation_id",
        "is_retweet",
        "is_quote_status",
        "retweeted_status",
        "lang",
        "full_text",
        "text",
    ):
        if out.get(key) is None and richer.get(key) is not None:
            out[key] = richer[key]
    base_user = out.get("user") if isinstance(out.get("user"), dict) else {}
    rich_user = richer.get("user") if isinstance(richer.get("user"), dict) else {}
    if rich_user:
        merged_user = dict(base_user)
        for key in (
            "followers_count",
            "followers",
            "id_str",
            "id",
            "screen_name",
            "name",
            "verified",
            "is_blue_verified",
            "profile_image_url_https",
        ):
            if merged_user.get(key) is None and rich_user.get(key) is not None:
                merged_user[key] = rich_user[key]
        out["user"] = merged_user
    return out


async def _enrich_tweet_details(syn: dict[str, Any]) -> dict[str, Any]:
    """Syndication tweet-result omits retweets/quotes/followers — pull from siblings.

    1) Author's popular timeline (same surface as user-tweets) when the id matches.
    2) Else profile_by_handle for author.followers only.
    """
    tid = safe_str(syn.get("id_str") or syn.get("id"))
    user = syn.get("user") if isinstance(syn.get("user"), dict) else {}
    handle = safe_str(user.get("screen_name") or user.get("username") or user.get("userName"))
    needs_counts = syn.get("retweet_count") is None or syn.get("quote_count") is None
    needs_followers = user.get("followers_count") is None and user.get("followers") is None
    if not handle or not tid:
        return syn
    out = syn
    if needs_counts or needs_followers:
        timeline = await native.user_tweets(handle, limit=100)
        if timeline:
            for row in timeline:
                if not isinstance(row, dict):
                    continue
                if safe_str(row.get("id_str") or row.get("id")) != tid:
                    continue
                out = _merge_tweet_row(out, row)
                break
    user = out.get("user") if isinstance(out.get("user"), dict) else {}
    if user.get("followers_count") is None and user.get("followers") is None:
        prof = await native.profile_by_handle(handle)
        if prof:
            followers = first_present(prof.get("followers"), prof.get("followersCount"))
            if followers is not None:
                merged_user = dict(user)
                merged_user["followers_count"] = followers
                if merged_user.get("id_str") is None and prof.get("id"):
                    merged_user["id_str"] = safe_str(prof.get("id"))
                out = dict(out)
                out["user"] = merged_user
    return out


@router.get(
    "/tweet-details",
    summary="Tweet metadata + engagement (likes/replies/retweets/quotes when exposed)",
    description=(
        "Public tweet as clean JSON: text, author (followers when exposed), "
        "engagement (likes, replies, retweets, quotes; views/bookmarks when "
        "Twitter exposes them), isReply / isRetweet, hashtags[], media[], "
        "ISO-8601 publishedAt. Flat 1 credit."
    ),
)
async def twitter_tweet_details(
    url: str = Query(..., description="Public tweet URL, e.g. https://x.com/user/status/ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    tweet_id = _require_tweet_url(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/tweet-details",
        platform="twitter",
        resource_url=url,
        base_credits=CREDIT_TWEET_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Syndication tweet-result + sibling hydrate (popular timeline / profile).
            syn = await native.tweet_result(tweet_id)
            if syn:
                ctx["source"] = "direct"
                enriched = await _enrich_tweet_details(syn)
                return _normalize_tweet(enriched)
            raise HTTPException(status_code=404, detail="Tweet not found")

        data = await cached_or_run(
            endpoint="twitter.tweet-details",
            params={"url": url, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/transcript", summary="Twitter/X tweet transcript / text extraction")
async def twitter_transcript(
    url: str = Query(..., description="Public tweet URL, e.g. https://x.com/user/status/ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    tweet_id = _require_tweet_url(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/transcript",
        platform="twitter",
        resource_url=url,
        base_credits=CREDIT_TWEET_DETAILS,
    ) as ctx:
        def _payload(text: str, tweet_url: str, tid: str | None, author: dict[str, Any] | None, published: str | None) -> dict[str, Any]:
            return {
                "platform": "twitter",
                "url": tweet_url or url,
                "tweetId": tid,
                "transcript": text,
                "transcriptSegments": [{"text": text, "start": 0, "duration": 0, "timestamp": "00:00"}],
                "wordCount": len(text.split()),
                "segments": 1,
                "author": _author_transcript(author),
                "publishedAt": published,
            }

        async def _run() -> dict[str, Any]:
            # Transcript is text-only via free public syndication (native-only).
            syn = await native.tweet_result(tweet_id)
            if syn:
                text = (syn.get("text") or "").strip()
                if text:
                    u = syn.get("user") or {}
                    username = u.get("screen_name")
                    ctx["source"] = "direct"
                    return _payload(
                        text,
                        f"https://x.com/{username}/status/{tweet_id}" if username else url,
                        safe_str(syn.get("id_str")) or tweet_id,
                        u,
                        safe_str(syn.get("created_at")),
                    )
                raise HTTPException(
                    status_code=422,
                    detail="No transcript text available for this tweet",
                )
            raise HTTPException(status_code=404, detail="Tweet not found")

        data = await cached_or_run(
            endpoint="twitter.transcript",
            params={"url": url, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/profile",
    summary="Twitter/X profile — blue/legacy/identity verification, tipjar, fastFollowers",
)
async def twitter_profile(
    url: str = Query(..., description="Profile URL or @handle, e.g. https://x.com/username"),
    cache: bool = Query(False, description="Set true to use the default cache TTL. Default false — always fetch fresh."),
    cacheMaxAge: str | None = Query(
        None,
        description=(
            "Max age of a cached response: 1d, 3d, 7d, 14d, or 30d. "
            "When set, enables caching with that TTL. Envelope includes cached + cachedAt."
        ),
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    from app.core.cache_params import resolve_cache_options

    handle = _require_twitter_handle(url)
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/profile",
        platform="twitter",
        resource_url=f"https://x.com/{handle}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Guest GraphQL UserByScreenName (rich verification + counts),
            # with HTML microdata fallback.
            native_profile = await native.profile_by_handle(handle)
            if native_profile:
                ctx["source"] = "direct"
                return _normalize_profile(native_profile)
            raise HTTPException(status_code=404, detail="Profile not found")

        data = await cached_or_run(
            endpoint="twitter.profile",
            params={"handle": handle, "v": 8, "cacheMaxAge": cacheMaxAge},
            runner=_run,
            ctx=ctx,
            # Profiles are polled repeatedly; follower counts drift slowly, so
            # serve the last copy instantly after TTL and refresh in background.
            stale_while_revalidate=True,
            use_cache=use_cache,
            ttl=ttl,
        )
        return ApiResponse(data=data)


@router.get(
    "/user-tweets",
    summary="Most popular public tweets for a profile (not chronological)",
    description=(
        "Returns the tweets Twitter's public timeline embed exposes for a "
        "profile — typically up to ~100 of the account's most popular posts, "
        "not a chronological / latest feed. Do not use this endpoint to detect "
        "new tweets. publishedAt is ISO-8601 UTC. Flat 2 credits per call."
    ),
)
async def twitter_user_tweets(
    url: str = Query(..., description="Profile URL or @handle"),
    limit: int = Query(
        20,
        ge=1,
        le=200,
        description=(
            "Max tweets to return (default 20, max 200). Twitter's public "
            "surface usually caps around ~100 popular posts — not latest."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_twitter_handle(url)
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/user-tweets",
        platform="twitter",
        resource_url=f"https://x.com/{handle}",
        base_credits=CREDIT_TWEET_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Public syndication timeline embed — popular posts (~100), not latest.
            native_items = await native.user_tweets(handle, limit=limit)
            if native_items:
                ctx["source"] = "direct"
                tweets = [_normalize_tweet(t) for t in native_items[:limit]]
                return {"handle": handle, "totalReturned": len(tweets), "tweets": tweets}
            raise HTTPException(status_code=404, detail="No tweets found")

        data = await cached_or_run(
            endpoint="twitter.user-tweets",
            params={"handle": handle, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/search", summary="Search public tweets on X by keyword")
async def twitter_search(
    q: str = Query(..., min_length=2, description="Keyword or phrase to search public tweets on X"),
    limit: int = Query(20, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/search",
        platform="twitter",
        resource_url=None,
        base_credits=CREDIT_TWEET_LIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Guest-token SearchTimeline (Top, native-only).
            native_items = await native.search(q, limit=limit, product="Top")
            if native_items:
                ctx["source"] = "direct"
                results = [_normalize_tweet(t) for t in native_items[:limit]]
                return {"query": q, "totalReturned": len(results), "results": results}
            raise HTTPException(
                status_code=502,
                detail="Twitter search temporarily unavailable",
            )

        data = await cached_or_run(
            endpoint="twitter.search",
            params={"q": q, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


def _extract_community_id(value: str) -> str | None:
    value = (value or "").strip()
    match = re.search(r"/communities/(\d+)", value)
    if match:
        return match.group(1)
    if value.isdigit():
        return value
    return None


@router.get("/community", summary="X (Twitter) community details")
async def twitter_community(
    url: str = Query(..., description="Community URL (x.com/i/communities/ID) or community ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_twitter_platform_mismatch(url, "https://x.com/i/communities/123456789")
    community_id = _extract_community_id(url)
    if not community_id:
        raise HTTPException(status_code=400, detail="Invalid X community URL or ID")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/community",
        platform="twitter",
        resource_url=f"https://x.com/i/communities/{community_id}",
        base_credits=1,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_community = await native.community(community_id)
            if native_community and native_community.get("name"):
                ctx["source"] = "direct"
                return strip_empty(native_community)

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_COMMUNITY,
                {"mode": "Get Community Detail", "community_id": community_id},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Community not found")
            ctx["source"] = "apify"
            c = items[0]
            banner = c.get("banner")
            if isinstance(banner, dict):
                banner = banner.get("url") or banner.get("media_url_https")
            return strip_empty({
                "platform": "twitter",
                "id": safe_str(c.get("id") or c.get("community_id") or community_id),
                "url": f"https://x.com/i/communities/{community_id}",
                "name": safe_str(c.get("name") or c.get("title")),
                "description": safe_str(c.get("description")),
                "memberCount": safe_int(c.get("memberCount") or c.get("member_count") or c.get("members")),
                "createdAt": safe_str(
                    c.get("createdAt") or c.get("created_at_datetime") or c.get("created_at")
                ),
                "creator": safe_str(c.get("creator_username") or c.get("creatorUsername")),
                "joinPolicy": safe_str(c.get("join_policy") or c.get("joinPolicy")),
                "isNsfw": first_present(c.get("is_nsfw"), c.get("isNsfw")),
                "bannerImage": safe_str(
                    banner or c.get("bannerUrl") or c.get("banner_url") or c.get("coverImage")
                ),
                "rules": c.get("rules") or [],
            })

        data = await cached_or_run(
            endpoint="twitter.community",
            params={"community_id": community_id, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/community-tweets", summary="Tweets posted in an X community")
async def twitter_community_tweets(
    url: str = Query(..., description="Community URL (x.com/i/communities/ID) or community ID"),
    limit: int = Query(25, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_twitter_platform_mismatch(url, "https://x.com/i/communities/123456789")
    community_id = _extract_community_id(url)
    if not community_id:
        raise HTTPException(status_code=400, detail="Invalid X community URL or ID")
    settings = get_settings()
    cost = _scaled_credits(limit, RATE_TWEET, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/twitter/community-tweets",
        platform="twitter",
        resource_url=f"https://x.com/i/communities/{community_id}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_items = await native.community_tweets(
                community_id, limit=limit, ranking_mode="Recency"
            )
            if native_items:
                ctx["source"] = "direct"
                tweets = [_normalize_tweet(t) for t in native_items[:limit]]
                return {"communityId": community_id, "totalReturned": len(tweets), "tweets": tweets}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_TWITTER_COMMUNITY,
                {
                    "mode": "Get Community Tweets",
                    "community_id": community_id,
                    "tweet_type": "Latest",
                    "max_results": limit,
                },
                max_items=limit,
            )
            if not items:
                raise HTTPException(status_code=404, detail="No tweets found")
            ctx["source"] = "apify"
            tweets = [_normalize_tweet(t) for t in items[:limit]]
            return {"communityId": community_id, "totalReturned": len(tweets), "tweets": tweets}

        data = await cached_or_run(
            endpoint="twitter.community-tweets",
            params={"community_id": community_id, "limit": limit, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled_credits(len(data["tweets"]), RATE_TWEET, 2)
        return ApiResponse(data=data)
