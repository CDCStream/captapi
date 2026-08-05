"""Bluesky endpoints: profile, user posts, post details.

Uses the public AT-Protocol AppView API (public.api.bsky.app) directly — no
Apify actor and no auth required for public data, so these calls are cheap.
"""

from __future__ import annotations

import math
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.cache_params import CACHE_MAX_AGE_DESC, resolve_cache_options
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import (
    detect_url_platform,
    extract_bluesky_post,
    normalize_bluesky_handle,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
CREDIT_PROFILE = 1
RATE = 0.1


def _scaled(n: int, rate: float, minimum: int) -> int:
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _reject_bluesky_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "bluesky":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "bluesky", example),
        )


def _require_bluesky_actor(value: str) -> str:
    _reject_bluesky_platform_mismatch(value, "https://bsky.app/profile/user.bsky.social")
    actor = normalize_bluesky_handle(value)
    if not actor:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "bluesky", "https://bsky.app/profile/user.bsky.social"),
        )
    return actor


def _require_bluesky_post_url(url: str) -> tuple[str, str]:
    parsed = extract_bluesky_post(url)
    if not parsed:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(
                url,
                "bluesky",
                "https://bsky.app/profile/user.bsky.social/post/postid",
            ),
        )
    return parsed


async def _xrpc(method: str, params: dict[str, Any]) -> dict[str, Any]:
    base = get_settings().BLUESKY_API_BASE
    url = f"{base}/xrpc/{method}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
    if resp.status_code == 400:
        raise HTTPException(status_code=404, detail="Not found on Bluesky")
    if resp.status_code >= 500:
        raise HTTPException(status_code=502, detail="Bluesky upstream error")
    resp.raise_for_status()
    return resp.json()


def _author(a: dict[str, Any]) -> dict[str, Any]:
    return {
        "handle": safe_str(a.get("handle")),
        "displayName": safe_str(a.get("displayName")),
        "did": safe_str(a.get("did")),
        "avatar": safe_str(a.get("avatar")),
    }


def _web_url(post: dict[str, Any]) -> str | None:
    """Build the bsky.app permalink from the AT-URI rkey + author handle."""
    uri = post.get("uri") or ""
    handle = (post.get("author") or {}).get("handle")
    rkey = uri.rsplit("/", 1)[-1] if "/" in uri else None
    if handle and rkey:
        return f"https://bsky.app/profile/{handle}/post/{rkey}"
    return None


def _embed_external(external: dict[str, Any]) -> dict[str, Any]:
    thumb = external.get("thumb")
    thumb_url = None
    if isinstance(thumb, dict):
        thumb_url = safe_str(thumb.get("fullsize") or thumb.get("thumb") or thumb.get("ref"))
    elif isinstance(thumb, str):
        thumb_url = safe_str(thumb)
    return {
        "type": "external",
        "url": safe_str(external.get("uri")),
        "title": safe_str(external.get("title")),
        "description": safe_str(external.get("description")),
        "thumb": thumb_url,
    }


def _embed_images(images: list[Any]) -> dict[str, Any]:
    return {
        "type": "images",
        "images": [
            {
                "url": safe_str(i.get("fullsize") or i.get("thumb")),
                "alt": safe_str(i.get("alt")),
            }
            for i in images
            if isinstance(i, dict)
        ],
    }


def _embed_video(video: dict[str, Any]) -> dict[str, Any]:
    thumb = video.get("thumbnail") or video.get("thumb")
    return {
        "type": "video",
        "playlist": safe_str(video.get("playlist")),
        "thumbnail": safe_str(thumb) if not isinstance(thumb, dict) else safe_str(
            thumb.get("fullsize") or thumb.get("thumb")
        ),
        "alt": safe_str(video.get("alt")),
    }


def _quote_web_url(uri: str | None, handle: str | None) -> str | None:
    if not uri or not handle:
        return None
    rkey = uri.rsplit("/", 1)[-1] if "/" in uri else None
    if rkey:
        return f"https://bsky.app/profile/{handle}/post/{rkey}"
    return None


def _unwrap_record_view(record_embed: dict[str, Any]) -> dict[str, Any]:
    """Drill through record#view wrappers to viewRecord / notFound / blocked."""
    cur: dict[str, Any] = record_embed
    for _ in range(3):
        nested = cur.get("record")
        if not isinstance(nested, dict):
            break
        # Already a viewRecord (has author/value) — stop.
        if cur.get("author") is not None or isinstance(cur.get("value"), dict):
            break
        cur = nested
    return cur


def _embed_quote(record_embed: Any) -> dict[str, Any] | None:
    """Normalize ``app.bsky.embed.record#view`` → type quote with text/author/url."""
    if not isinstance(record_embed, dict):
        return None
    inner = _unwrap_record_view(record_embed)
    rtype = safe_str(inner.get("$type")) or ""
    if rtype.endswith("viewNotFound") or rtype.endswith("viewBlocked") or rtype.endswith(
        "viewDetached"
    ):
        return {
            "type": "quote",
            "uri": safe_str(inner.get("uri")),
            "url": None,
            "text": None,
            "author": None,
            "notFound": True if rtype.endswith("viewNotFound") else None,
            "blocked": True if rtype.endswith("viewBlocked") else None,
            "detached": True if rtype.endswith("viewDetached") else None,
        }
    uri = safe_str(inner.get("uri"))
    author_raw = inner.get("author") if isinstance(inner.get("author"), dict) else {}
    value = inner.get("value") if isinstance(inner.get("value"), dict) else {}
    text = safe_str(value.get("text") or inner.get("text"))
    handle = safe_str(author_raw.get("handle"))
    return {
        "type": "quote",
        "uri": uri,
        "url": _quote_web_url(uri, handle),
        "cid": safe_str(inner.get("cid")),
        "text": text,
        "author": _author(author_raw) if author_raw else None,
        "publishedAt": safe_str(value.get("createdAt") or inner.get("indexedAt")),
    }


def _post_embed(post: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize embeds to a single type namespace: external | images | video | quote."""
    embed = post.get("embed")
    if not isinstance(embed, dict):
        return None
    etype = safe_str(embed.get("$type")) or ""

    # Quote + media (images/external/video alongside a quoted post).
    if "recordWithMedia" in etype:
        media = embed.get("media") if isinstance(embed.get("media"), dict) else {}
        media_type = safe_str(media.get("$type")) or ""
        media_norm: dict[str, Any] | None = None
        if isinstance(media.get("external"), dict) or "external" in media_type:
            ext = media.get("external") if isinstance(media.get("external"), dict) else media
            media_norm = _embed_external(ext)
        elif isinstance(media.get("images"), list) or "images" in media_type:
            media_norm = _embed_images(media.get("images") or [])
        elif isinstance(media.get("video"), dict) or "video" in media_type:
            media_norm = _embed_video(media.get("video") if isinstance(media.get("video"), dict) else media)
        quote = _embed_quote(embed.get("record") or embed)
        if quote:
            quote["media"] = media_norm
            return quote
        return media_norm

    if "record" in etype and "recordWithMedia" not in etype:
        return _embed_quote(embed)

    if isinstance(embed.get("external"), dict) or "external" in etype:
        return _embed_external(embed.get("external") if isinstance(embed.get("external"), dict) else embed)

    images = embed.get("images")
    if isinstance(images, list) and images:
        return _embed_images(images)

    if isinstance(embed.get("video"), dict) or "video" in etype:
        return _embed_video(embed.get("video") if isinstance(embed.get("video"), dict) else embed)

    # Unknown embed — never leak raw lexicon NSIDs as type.
    return None


def _repost_reason(reason: Any) -> tuple[bool, dict[str, Any] | None, str | None]:
    """Parse feed-item ``reason`` → (isRepost, repostedBy, repostedAt)."""
    if not isinstance(reason, dict):
        return False, None, None
    rtype = safe_str(reason.get("$type")) or ""
    if "reasonRepost" not in rtype:
        return False, None, None
    by = reason.get("by") if isinstance(reason.get("by"), dict) else {}
    return True, _author(by) if by else None, safe_str(reason.get("indexedAt"))


def _normalize_post(post: dict[str, Any], *, reason: Any = None) -> dict[str, Any]:
    record = post.get("record") or {}
    author = post.get("author") or {}
    is_repost, reposted_by, reposted_at = _repost_reason(reason)
    out: dict[str, Any] = {
        "platform": "bluesky",
        "uri": safe_str(post.get("uri")),
        "url": _web_url(post),
        "cid": safe_str(post.get("cid")),
        "text": safe_str(record.get("text")),
        "publishedAt": safe_str(record.get("createdAt") or post.get("indexedAt")),
        "indexedAt": safe_str(post.get("indexedAt")),
        "author": _author(author),
        "isRepost": is_repost,
        "engagement": {
            "likes": safe_int(post.get("likeCount")),
            "reposts": safe_int(post.get("repostCount")),
            "replies": safe_int(post.get("replyCount")),
            "quotes": safe_int(post.get("quoteCount")),
        },
        "embed": _post_embed(post),
    }
    if is_repost:
        out["repostedBy"] = reposted_by
        out["repostedAt"] = reposted_at
    return out


def _normalize_feed_item(item: dict[str, Any]) -> dict[str, Any] | None:
    post = item.get("post")
    if not isinstance(post, dict):
        return None
    return _normalize_post(post, reason=item.get("reason"))


def _verification(p: dict[str, Any]) -> dict[str, Any]:
    """Map ``app.bsky.actor.getProfile`` verification to a stable shape."""
    raw = p.get("verification") if isinstance(p.get("verification"), dict) else {}
    items: list[dict[str, Any]] = []
    for v in raw.get("verifications") or []:
        if not isinstance(v, dict):
            continue
        items.append(
            {
                "issuer": safe_str(v.get("issuer")),
                "issuerHandle": safe_str(v.get("issuerHandle")),
                "issuerDisplayName": safe_str(v.get("issuerDisplayName")),
                "uri": safe_str(v.get("uri")),
                "isValid": bool(v.get("isValid")) if v.get("isValid") is not None else None,
                "createdAt": safe_str(v.get("createdAt")),
            }
        )
    return {
        "verifications": items,
        "verifiedStatus": safe_str(raw.get("verifiedStatus")),
        "trustedVerifierStatus": safe_str(raw.get("trustedVerifierStatus")),
    }


async def _enrich_verification_issuers(verification: dict[str, Any]) -> None:
    """Resolve issuer DIDs → handle + displayName (SC leaves raw DIDs only)."""
    items = verification.get("verifications")
    if not isinstance(items, list) or not items:
        return
    need = [
        safe_str(i.get("issuer"))
        for i in items
        if isinstance(i, dict) and i.get("issuer") and not i.get("issuerHandle")
    ]
    if not need:
        return
    # Dedup while preserving order.
    seen: set[str] = set()
    actors: list[str] = []
    for did in need:
        if did and did not in seen:
            seen.add(did)
            actors.append(did)
    try:
        data = await _xrpc("app.bsky.actor.getProfiles", {"actors": actors})
    except Exception:
        return
    by_did: dict[str, dict[str, Any]] = {}
    for prof in data.get("profiles") or []:
        if isinstance(prof, dict) and prof.get("did"):
            by_did[safe_str(prof.get("did"))] = prof
    for item in items:
        if not isinstance(item, dict):
            continue
        prof = by_did.get(safe_str(item.get("issuer")))
        if not prof:
            continue
        if not item.get("issuerHandle"):
            item["issuerHandle"] = safe_str(prof.get("handle"))
        if not item.get("issuerDisplayName"):
            item["issuerDisplayName"] = safe_str(prof.get("displayName"))


def _labels(p: dict[str, Any]) -> list[dict[str, Any]]:
    raw = p.get("labels")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for lab in raw:
        if not isinstance(lab, dict):
            continue
        out.append(
            {
                "src": safe_str(lab.get("src")),
                "uri": safe_str(lab.get("uri")),
                "cid": safe_str(lab.get("cid")),
                "val": safe_str(lab.get("val")),
                "neg": bool(lab.get("neg")) if lab.get("neg") is not None else None,
                "createdAt": safe_str(lab.get("cts") or lab.get("createdAt")),
                "expiresAt": safe_str(lab.get("exp") or lab.get("expiresAt")),
            }
        )
    return out


def _associated(p: dict[str, Any]) -> dict[str, Any]:
    """Profile association counts — feedgens/lists/labeler distinguish bots/services."""
    raw = p.get("associated") if isinstance(p.get("associated"), dict) else {}
    chat = raw.get("chat") if isinstance(raw.get("chat"), dict) else {}
    activity = (
        raw.get("activitySubscription")
        if isinstance(raw.get("activitySubscription"), dict)
        else {}
    )
    return {
        "lists": safe_int(raw.get("lists")),
        "feedgens": safe_int(raw.get("feedgens")),
        "starterPacks": safe_int(raw.get("starterPacks")),
        "labeler": bool(raw.get("labeler")) if raw.get("labeler") is not None else None,
        "chat": {
            "allowIncoming": safe_str(chat.get("allowIncoming")),
            "allowGroupInvites": safe_str(chat.get("allowGroupInvites")),
        }
        if chat
        else None,
        "activitySubscription": {
            "allowSubscriptions": safe_str(activity.get("allowSubscriptions")),
        }
        if activity
        else None,
    }


def _pinned_post(raw: Any) -> dict[str, Any] | None:
    """``com.atproto.repo.strongRef`` — content the account chose to feature."""
    if not isinstance(raw, dict):
        return None
    uri = safe_str(raw.get("uri"))
    cid = safe_str(raw.get("cid"))
    if not uri and not cid:
        return None
    out: dict[str, Any] = {}
    if uri:
        out["uri"] = uri
        # Best-effort web URL when the AT-URI is a standard app.bsky.feed.post.
        # at://did:plc:…/app.bsky.feed.post/RKEY
        parts = uri.split("/")
        if len(parts) >= 5 and parts[0] == "at:":
            rkey = parts[-1]
            # Web URL needs a handle — left as uri-only when unknown.
            out["rkey"] = rkey
    if cid:
        out["cid"] = cid
    return out


def _joined_via_starter_pack(raw: Any) -> dict[str, Any] | None:
    """``app.bsky.graph.defs#starterPackViewBasic`` (or a strongRef fallback)."""
    if not isinstance(raw, dict):
        return None
    uri = safe_str(raw.get("uri"))
    cid = safe_str(raw.get("cid"))
    record = raw.get("record") if isinstance(raw.get("record"), dict) else {}
    creator = raw.get("creator") if isinstance(raw.get("creator"), dict) else {}
    out: dict[str, Any] = {}
    if uri:
        out["uri"] = uri
    if cid:
        out["cid"] = cid
    name = safe_str(record.get("name") or raw.get("name"))
    if name:
        out["name"] = name
    if creator:
        ch = safe_str(creator.get("handle"))
        cd = safe_str(creator.get("did"))
        cn = safe_str(creator.get("displayName"))
        slim = {k: v for k, v in {"did": cd, "handle": ch, "displayName": cn}.items() if v}
        if slim:
            out["creator"] = slim
    return out or None


async def _normalize_profile(p: dict[str, Any]) -> dict[str, Any]:
    from app.utils.profile_core import stamp_profile_core

    handle = p.get("handle")
    verification = _verification(p)
    await _enrich_verification_issuers(verification)
    verified_status = (verification.get("verifiedStatus") or "").lower()
    did = safe_str(p.get("did"))
    display = safe_str(p.get("displayName"))
    posts = safe_int(p.get("postsCount"))
    out: dict[str, Any] = {
        "platform": "bluesky",
        "id": did,
        "did": did,
        "handle": safe_str(handle),
        "url": f"https://bsky.app/profile/{handle}" if handle else None,
        "displayName": display,
        "name": display,  # deprecated alias — prefer displayName
        "bio": safe_str(p.get("description")),
        "followers": safe_int(p.get("followersCount")),
        "following": safe_int(p.get("followsCount")),
        "postCount": posts,
        "posts": posts,  # deprecated alias — prefer postCount
        "avatar": safe_str(p.get("avatar")),
        "banner": safe_str(p.get("banner")),
        "verified": verified_status == "valid",
        "verification": verification,
        "labels": _labels(p),
        "associated": _associated(p),
        "createdAt": safe_str(p.get("createdAt")),
        "indexedAt": safe_str(p.get("indexedAt")),
    }
    pinned = _pinned_post(p.get("pinnedPost"))
    if pinned:
        out["pinnedPost"] = pinned
    joined = _joined_via_starter_pack(p.get("joinedViaStarterPack"))
    if joined:
        out["joinedViaStarterPack"] = joined
    return stamp_profile_core(out, platform="bluesky")


@router.get(
    "/profile",
    summary="Bluesky profile details & stats",
    description=(
        "Public Bluesky profile via AT Protocol app.bsky.actor.getProfile. Canonical "
        "profile core (displayName, avatar, postCount, …) plus deprecated name/posts "
        "aliases for one release; did, verification{} with issuer DIDs resolved to "
        "handle/display name, moderation labels[], associated{}, pinnedPost, and "
        "joinedViaStarterPack when present. Accepts cache / cacheMaxAge. Flat 1 credit."
    ),
)
async def bluesky_profile(
    url: str = Query(..., description="Bluesky profile URL, @handle, or handle"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    actor = _require_bluesky_actor(url)
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    async with billed_call(
        caller=caller,
        endpoint="/v1/bluesky/profile",
        platform="bluesky",
        resource_url=f"https://bsky.app/profile/{actor}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _xrpc("app.bsky.actor.getProfile", {"actor": actor})
            ctx["source"] = "direct"
            return await _normalize_profile(data)

        result = await cached_or_run(
            endpoint="bluesky.profile",
            params={"actor": actor, "v": 5, "cacheMaxAge": cacheMaxAge},
            runner=_run,
            ctx=ctx,
            use_cache=use_cache,
            ttl=ttl,
        )
        return ApiResponse(data=result)


_AUTHOR_FEED_FILTERS = frozenset(
    {
        "posts_with_replies",
        "posts_no_replies",
        "posts_with_media",
        "posts_and_author_threads",
        "posts_with_video",
    }
)


@router.get(
    "/user-posts",
    summary="Author feed from a Bluesky profile (posts + reposts, cursor-paginated)",
    description=(
        "Public author feed via app.bsky.feed.getAuthorFeed — the account's posts and "
        "reposts. Each row has isRepost / repostedBy / repostedAt when the item is a "
        "repost (author is then the original poster). Pass includeReposts=false to "
        "drop reposts. filter maps to Bluesky's feed filter (replies/media/threads — "
        "does not remove reposts). nextCursor is Bluesky's opaque cursor — pass it "
        "through; do not derive from publishedAt. ~0.1 credits per returned row."
    ),
)
async def bluesky_user_posts(
    url: str = Query(
        ...,
        description="Bluesky profile URL, @handle, or handle, e.g. https://bsky.app/profile/handle.bsky.social",
    ),
    limit: int = Query(25, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor from the previous response's nextCursor. "
            "Leave empty for the first page. Do not invent a cursor from publishedAt — "
            "the feed is ordered by feed time (reposts sort by repost time)."
        ),
    ),
    filter: str | None = Query(
        None,
        description=(
            "Bluesky getAuthorFeed filter: posts_with_replies (default), posts_no_replies, "
            "posts_with_media, posts_and_author_threads, or posts_with_video. Controls "
            "replies/media/threads — not reposts. Use includeReposts=false to drop reposts."
        ),
    ),
    includeReposts: bool = Query(
        True,
        description=(
            "When false, omit feed items that are reposts (reasonRepost). Default true — "
            "reposts are included and marked with isRepost / repostedBy / repostedAt."
        ),
    ),
    cache: bool = Query(
        False,
        description="Set true to use the 24h cache. Default false — always fetch fresh data.",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    actor = _require_bluesky_actor(url)
    feed_filter = (filter or "").strip() or None
    if feed_filter and feed_filter not in _AUTHOR_FEED_FILTERS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid filter. Use posts_with_replies, posts_no_replies, "
                "posts_with_media, posts_and_author_threads, or posts_with_video."
            ),
        )
    cost = _scaled(limit, RATE, 1)
    async with billed_call(
        caller=caller,
        endpoint="/v1/bluesky/user-posts",
        platform="bluesky",
        resource_url=f"https://bsky.app/profile/{actor}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # When stripping reposts, over-fetch so a dense-repost page can still fill limit.
            fetch_limit = (
                limit if includeReposts else min(100, max(limit * 2, limit))
            )
            params: dict[str, Any] = {"actor": actor, "limit": fetch_limit}
            if cursor:
                # Pass Bluesky's opaque cursor through — never reconstruct from publishedAt.
                params["cursor"] = cursor
            if feed_filter:
                params["filter"] = feed_filter
            data = await _xrpc("app.bsky.feed.getAuthorFeed", params)
            feed = data.get("feed") or []
            posts: list[dict[str, Any]] = []
            for item in feed:
                if not isinstance(item, dict):
                    continue
                row = _normalize_feed_item(item)
                if row is None:
                    continue
                if not includeReposts and row.get("isRepost"):
                    continue
                posts.append(row)
                if len(posts) >= limit:
                    break
            # Bluesky's own cursor only — never last publishedAt.
            next_cursor = safe_str(data.get("cursor")) or None
            return {
                "handle": actor,
                "filter": feed_filter,
                "includeReposts": includeReposts,
                "totalReturned": len(posts),
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "posts": posts,
            }

        result = await cached_or_run(
            endpoint="bluesky.user-posts",
            params={
                "actor": actor,
                "limit": limit,
                "cursor": cursor or "",
                "filter": feed_filter or "",
                "includeReposts": includeReposts,
                "v": 5,
            },
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(result["posts"]), RATE, 1)
        return ApiResponse(data=result)


@router.get("/post-details", summary="Bluesky post metadata + engagement")
async def bluesky_post_details(
    url: str = Query(..., description="Bluesky post URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    parsed = _require_bluesky_post_url(url)
    handle, rkey = parsed
    async with billed_call(
        caller=caller,
        endpoint="/v1/bluesky/post-details",
        platform="bluesky",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            did = handle
            if not did.startswith("did:"):
                profile = await _xrpc("app.bsky.actor.getProfile", {"actor": handle})
                did = profile.get("did") or handle
            at_uri = f"at://{did}/app.bsky.feed.post/{rkey}"
            data = await _xrpc("app.bsky.feed.getPosts", {"uris": at_uri})
            posts = data.get("posts") or []
            if not posts:
                raise HTTPException(status_code=404, detail="Post not found")
            return _normalize_post(posts[0])

        result = await cached_or_run(
            endpoint="bluesky.post-details",
            params={"handle": handle, "rkey": rkey, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=result)
