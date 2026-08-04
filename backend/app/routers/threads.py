"""Threads (Meta) endpoints: profile, user posts, post details.

Backed by a config-driven Threads actor. Field mappings are defensive because
Threads payloads vary across actor versions (snake_case and camelCase aliases).
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
from app.services import threads_native as native
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str, strip_empty
from app.utils.url import (
    detect_url_platform,
    extract_threads_post_code,
    normalize_threads_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
CREDIT_PROFILE = 1
RATE = 0.7


def _scaled(n: int, rate: float, minimum: int) -> int:
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _reject_threads_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "threads":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "threads", example),
        )


def _require_threads_handle(value: str) -> str:
    _reject_threads_platform_mismatch(value, "https://www.threads.net/@username")
    handle = normalize_threads_username(value)
    if not handle:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "threads", "https://www.threads.net/@username"),
        )
    return handle


def _require_threads_post_url(url: str) -> str:
    code = extract_threads_post_code(url)
    if not code:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "threads", "https://www.threads.net/@user/post/POST_ID"),
        )
    return code


def _user(u: dict[str, Any], *, include_profile_image: bool = True) -> dict[str, Any]:
    """Author/user card for posts & search.

    Follower counts are omitted — post/search actors never return them
    (use /profile). Search modes also omit profileImage (same reason).
    """
    username = u.get("username") or u.get("userName") or u.get("user_name")
    pic_hd = u.get("hd_profile_pic_url_info") if isinstance(u.get("hd_profile_pic_url_info"), dict) else {}
    out: dict[str, Any] = {
        "username": safe_str(username),
        "displayName": safe_str(u.get("full_name") or u.get("fullName") or u.get("name")),
        "verified": u.get("is_verified") or u.get("isVerified"),
    }
    if include_profile_image:
        out["profileImage"] = safe_str(
            u.get("profile_pic_url")
            or u.get("profilePicUrl")
            or u.get("profile_pic_url_hd")
            or u.get("profile_picture_url")
            or u.get("profilePictureUrl")
            or u.get("avatar")
            or pic_hd.get("url")
        )
    return out


def _post_media(item: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    media = item.get("media")
    if isinstance(media, list):
        for m in media:
            if isinstance(m, dict) and m.get("url"):
                urls.append(m["url"])
            elif isinstance(m, str):
                urls.append(m)
    for key in ("video_url", "image_url"):
        if item.get(key) and item[key] not in urls:
            urls.append(item[key])
    return urls


def _normalize_post(item: dict[str, Any], *, include_author_image: bool = True) -> dict[str, Any]:
    user = item.get("user") or item.get("author") or item
    code = item.get("code") or item.get("shortcode") or item.get("post_code")
    author_name = (user.get("username") or user.get("userName")) if isinstance(user, dict) else None
    # Prefer the @user/post/CODE canonical form: /t/CODE links are rejected by
    # the media-downloader actor that post-details falls back to.
    if code and author_name:
        canonical = f"https://www.threads.net/@{author_name}/post/{code}"
    elif code:
        canonical = f"https://www.threads.net/t/{code}"
    else:
        canonical = None
    return {
        "platform": "threads",
        "id": safe_str(item.get("pk") or item.get("id") or item.get("post_id") or item.get("postId")),
        "code": safe_str(code),
        "url": canonical or safe_str(item.get("url") or item.get("post_url")),
        "text": safe_str(item.get("caption") or item.get("text") or item.get("caption_text")),
        "publishedAt": safe_str(
            item.get("taken_at") or item.get("date") or item.get("published_on") or item.get("publishedAt")
        ),
        "author": _user(user, include_profile_image=include_author_image),
        "engagement": {
            "likes": safe_int(item.get("like_count") or item.get("likeCount") or item.get("likes")),
            "replies": safe_int(
                item.get("reply_count")
                or item.get("replyCount")
                or item.get("direct_reply_count")
                or item.get("replies")
            ),
            "reposts": safe_int(item.get("repost_count") or item.get("repostCount") or item.get("reposts")),
            "quotes": safe_int(item.get("quote_count") or item.get("quoteCount")),
        },
        "media": _post_media(item),
    }


def _bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _bio_links(item: dict[str, Any]) -> list[dict[str, Any]]:
    raw = item.get("bio_links") if isinstance(item.get("bio_links"), list) else item.get("bioLinks")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for link in raw:
        if not isinstance(link, dict):
            continue
        url = safe_str(link.get("url"))
        if not url:
            continue
        verified = link.get("is_verified")
        if verified is None:
            verified = link.get("verified")
        if verified is None:
            verified = link.get("isVerified")
        out.append(
            {
                "url": url,
                "verified": _bool_or_none(verified),
                "linkId": safe_str(link.get("link_id") or link.get("linkId")),
            }
        )
    return out


def _bio_fragments(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize Meta ``text_app_biography.text_fragments`` into a flat list."""
    raw = item.get("text_app_biography")
    if raw is None:
        raw = item.get("textAppBiography")
    if raw is None:
        raw = item.get("bioFragments")
    fragments: Any = None
    if isinstance(raw, list):
        fragments = raw
    elif isinstance(raw, dict):
        nested = raw.get("text_fragments") or raw.get("textFragments") or raw
        if isinstance(nested, dict):
            fragments = nested.get("fragments") or nested.get("text_fragments")
        elif isinstance(nested, list):
            fragments = nested
    if not isinstance(fragments, list):
        return []
    out: list[dict[str, Any]] = []
    for frag in fragments:
        if not isinstance(frag, dict):
            continue
        frag_type = safe_str(
            frag.get("fragment_type") or frag.get("fragmentType") or frag.get("type")
        )
        plaintext = safe_str(
            frag.get("plaintext") or frag.get("text") or frag.get("display_text")
        )
        link = frag.get("link_fragment") or frag.get("linkFragment") or frag.get("link")
        href = None
        display = None
        if isinstance(link, dict):
            href = safe_str(link.get("uri") or link.get("url") or link.get("href"))
            display = safe_str(link.get("display_text") or link.get("displayText") or link.get("text"))
        mention = frag.get("mention_fragment") or frag.get("mentionFragment") or frag.get("mention")
        mention_user = None
        if isinstance(mention, dict):
            mention_user = safe_str(
                mention.get("username") or mention.get("name") or mention.get("text")
            )
        tag = frag.get("tag_fragment") or frag.get("tagFragment") or frag.get("tag")
        tag_name = None
        if isinstance(tag, dict):
            tag_name = safe_str(tag.get("name") or tag.get("tag_name") or tag.get("text"))
        elif isinstance(tag, str):
            tag_name = safe_str(tag)
        row = {
            "type": frag_type or "plaintext",
            "text": plaintext or display or mention_user or tag_name,
            "url": href,
            "mention": mention_user,
            "tag": tag_name,
        }
        if row["text"] or row["url"]:
            out.append({k: v for k, v in row.items() if v is not None})
    return out


def _profile_image_versions(item: dict[str, Any]) -> list[dict[str, Any]]:
    raw = (
        item.get("hd_profile_pic_versions")
        if isinstance(item.get("hd_profile_pic_versions"), list)
        else item.get("hdProfilePicVersions")
    )
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        url = safe_str(row.get("url"))
        if not url:
            continue
        out.append(
            {
                "url": url,
                "width": safe_int(row.get("width")),
                "height": safe_int(row.get("height")),
            }
        )
    return out


def _normalize_profile(item: dict[str, Any]) -> dict[str, Any]:
    username = item.get("username") or item.get("userName")
    verified = item.get("is_verified")
    if verified is None:
        verified = item.get("isVerified")
    threads_only = item.get("is_threads_only_user")
    if threads_only is None:
        threads_only = item.get("isThreadsOnlyUser")
    is_private = item.get("text_post_app_is_private")
    if is_private is None:
        is_private = item.get("isPrivate")
    onboarded = item.get("has_onboarded_to_text_post_app")
    if onboarded is None:
        onboarded = item.get("hasOnboardedToTextPostApp")
    transparency = item.get("transparency_label")
    if transparency is None:
        transparency = item.get("transparencyLabel")
    if isinstance(transparency, dict):
        transparency = safe_str(
            transparency.get("label") or transparency.get("title") or transparency.get("name")
        )
    else:
        transparency = safe_str(transparency)

    versions = _profile_image_versions(item)
    profile_image = safe_str(item.get("profile_pic_url") or item.get("profilePicUrl"))
    if not profile_image and versions:
        # Prefer the largest width when the actor only shipped versions[].
        best = max(versions, key=lambda row: row.get("width") or 0)
        profile_image = best.get("url")

    display_name = safe_str(
        item.get("full_name")
        or item.get("fullName")
        or item.get("displayName")
        or item.get("name")
    )
    private = _bool_or_none(is_private)

    # Legacy core fields still go through strip_empty; additive keys are always
    # present (null / []) so clients never special-case missing keys.
    out = strip_empty(
        {
            "platform": "threads",
            "username": safe_str(username),
            "url": safe_str(item.get("url"))
            or (f"https://www.threads.net/@{username}" if username else None),
            "id": safe_str(item.get("pk") or item.get("id") or item.get("userId") or item.get("user_id")),
            # displayName matches TikTok/IG/YouTube; name kept for BC.
            "displayName": display_name,
            "name": display_name,
            "bio": safe_str(item.get("biography") or item.get("bio")),
            "verified": bool(verified) if verified is not None else None,
            "followers": safe_int(
                item.get("follower_count") or item.get("followerCount") or item.get("followers")
            ),
            "profileImage": profile_image,
        }
    )
    if display_name:
        out.setdefault("displayName", display_name)
        out.setdefault("name", display_name)
    out.update(
        {
            "isThreadsOnlyUser": _bool_or_none(threads_only),
            # private matches TikTok; isPrivate matches Instagram.
            "private": private,
            "isPrivate": private,
            "bioLinks": _bio_links(item),
            "bioFragments": _bio_fragments(item),
            "transparencyLabel": transparency,
            "profileImageVersions": versions,
            "hasOnboarded": _bool_or_none(onboarded),
        }
    )
    return out


def _normalize_post_download(item: dict[str, Any]) -> dict[str, Any]:
    result = item.get("result") if isinstance(item.get("result"), dict) else item
    media = result.get("medias") if isinstance(result.get("medias"), list) else []
    first_media = media[0] if media and isinstance(media[0], dict) else {}
    return {
        "platform": "threads",
        "id": safe_str(first_media.get("id")),
        "code": safe_str(extract_threads_post_code(result.get("url") or item.get("url") or "")),
        "url": safe_str(result.get("url") or item.get("url")),
        "text": safe_str(result.get("title") or first_media.get("caption")),
        "publishedAt": None,
        "author": {
            "username": safe_str(result.get("author")),
            "displayName": safe_str(result.get("author")),
            "verified": None,
            "profileImage": None,
        },
        "engagement": {"likes": 0, "replies": 0, "reposts": 0, "quotes": 0},
        "media": media,
    }


@router.get(
    "/profile",
    summary="Threads profile details & stats",
    description=(
        "Public Threads profile as clean JSON: username, displayName (+ name), bio, "
        "followers, verified, profileImage, plus isThreadsOnlyUser, private/isPrivate, "
        "bioLinks[] (url + Meta verified + linkId), bioFragments[], transparencyLabel, "
        "profileImageVersions[], and hasOnboarded. Flat 1 credit. "
        "isThreadsOnlyUser / transparencyLabel are null when Meta omits them on web hydrate."
    ),
)
async def threads_profile(
    url: str = Query(..., description="Threads profile URL or @handle"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_threads_handle(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/profile",
        platform="threads",
        resource_url=f"https://www.threads.net/@{handle}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Hydrated Threads profile HTML first (Decodo headless → Relay JSON).
            native_profile = await native.profile_by_handle(handle)
            if native_profile and native_profile.get("username"):
                ctx["source"] = "direct"
                return _normalize_profile(native_profile)

            apify = get_apify()
            # The automation-lab scraper has a dedicated profile mode with
            # followers/bio/verified; the user-media actor only emits posts.
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_SEARCH,
                {"mode": "profile", "usernames": [handle]},
                max_items=1,
            )
            if not items:
                raise HTTPException(status_code=404, detail="Profile not found")
            ctx["source"] = "apify"
            return _normalize_profile(items[0])

        data = await cached_or_run(
            endpoint="threads.profile",
            params={"handle": handle, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/user-posts", summary="List recent posts for a Threads profile")
async def threads_user_posts(
    url: str = Query(..., description="Threads profile URL or @handle"),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    handle = _require_threads_handle(url)
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/user-posts",
        platform="threads",
        resource_url=f"https://www.threads.net/@{handle}",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Hydrated profile HTML embeds recent thread_items (soft-capped).
            native_items = await native.user_posts(handle, limit=limit)
            if native_items:
                ctx["source"] = "direct"
                posts = [_normalize_post(i) for i in native_items][:limit]
                return {"handle": handle, "totalReturned": len(posts), "posts": posts}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS,
                {"username": handle, "maxPosts": limit},
                max_items=limit,
            )
            if not items:
                raise HTTPException(status_code=404, detail="No posts found")
            ctx["source"] = "apify"
            posts = [_normalize_post(i) for i in items][:limit]
            return {"handle": handle, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="threads.user-posts",
            params={"handle": handle, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search", summary="Search public Threads posts by keyword")
async def threads_search(
    q: str = Query(..., min_length=2, description="Keyword or phrase to search public Threads posts"),
    limit: int = Query(25, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/search",
        platform="threads",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Hydrated /search HTML embeds matching thread_items (soft-capped).
            native_items = await native.search(q, limit=limit)
            if native_items:
                ctx["source"] = "direct"
                results = [_normalize_post(i, include_author_image=False) for i in native_items][:limit]
                return {"query": q, "totalReturned": len(results), "results": results}

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_SEARCH,
                {"mode": "search", "searchQueries": [q], "maxPosts": limit},
                max_items=limit,
            )
            if not items:
                raise HTTPException(status_code=404, detail="No posts found")
            ctx["source"] = "apify"
            results = [_normalize_post(i, include_author_image=False) for i in items][:limit]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="threads.search",
            params={"q": q, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search-users", summary="Find Threads users / creators by keyword")
async def threads_search_users(
    q: str = Query(..., min_length=2, description="Keyword to find Threads users or creators"),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/search-users",
        platform="threads",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Native: distinct authors from hydrated search HTML (soft-capped).
            native_users = await native.search_users(q, limit=limit)
            if native_users:
                ctx["source"] = "direct"
                users = [
                    {
                        "username": u.get("username"),
                        "displayName": u.get("full_name"),
                        "url": u.get("url") or f"https://www.threads.net/@{u.get('username')}",
                        "verified": u.get("is_verified"),
                    }
                    for u in native_users
                    if u.get("username")
                ][:limit]
                return {"query": q, "totalReturned": len(users), "users": users}

            apify = get_apify()
            # Fallthrough: derive distinct authors from Apify keyword search.
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_SEARCH,
                {"mode": "search", "searchQueries": [q], "maxPosts": limit * 4},
                max_items=limit * 8,
            )
            seen: set[str] = set()
            users: list[dict[str, Any]] = []
            for item in items:
                if item.get("type") == "profile":
                    continue
                # Search actors omit avatar/follower fields; keep the card lean.
                u = _user(item.get("user") or item.get("author") or item, include_profile_image=False)
                uname = u.get("username")
                if not uname or uname in seen:
                    continue
                seen.add(uname)
                users.append(
                    {
                        "username": uname,
                        "displayName": u.get("displayName"),
                        "url": f"https://www.threads.net/@{uname}",
                        "verified": u.get("verified"),
                    }
                )
                if len(users) >= limit:
                    break
            if not users:
                raise HTTPException(status_code=404, detail="No users found")
            ctx["source"] = "apify"
            return {"query": q, "totalReturned": len(users), "users": users}

        data = await cached_or_run(
            endpoint="threads.search-users",
            params={"q": q, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["users"]), RATE, 2)
        return ApiResponse(data=data)


_POST_AUTHOR_RE = re.compile(r"@([A-Za-z0-9._]+)/post/")


@router.get("/post-details", summary="Threads post metadata + engagement")
async def threads_post_details(
    url: str = Query(..., description="Threads post URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    code = _require_threads_post_url(url)
    settings = get_settings()
    author_match = _POST_AUTHOR_RE.search(url or "")
    author = author_match.group(1) if author_match else None
    async with billed_call(
        caller=caller,
        endpoint="/v1/threads/post-details",
        platform="threads",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Hydrated permalink HTML embeds the post under thread_items.
            native_post = await native.post_details(url)
            if native_post and native_post.get("code"):
                ctx["source"] = "direct"
                return _normalize_post(native_post)

            apify = get_apify()
            # When the URL names the author, the posts-mode scraper gives full
            # engagement + text; the downloader fallback only has media.
            if author:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_THREADS,
                    {"username": author, "maxPosts": 25},
                    max_items=25,
                )
                match = next(
                    (
                        i
                        for i in items
                        if (i.get("post_code") or i.get("code") or i.get("shortcode")) == code
                    ),
                    None,
                )
                if match:
                    ctx["source"] = "apify"
                    return _normalize_post(match)
            dl_url = f"https://www.threads.com/@{author}/post/{code}" if author else url
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_THREADS_POST,
                {"links": [dl_url], "proxyConfiguration": {"useApifyProxy": False}},
                max_items=1,
            )
            result = (items[0].get("result") or {}) if items else {}
            if not items or (isinstance(result, dict) and result.get("error")):
                raise HTTPException(status_code=404, detail="Post not found")
            ctx["source"] = "apify"
            return _normalize_post_download(items[0])

        data = await cached_or_run(
            endpoint="threads.post-details",
            params={"url": url, "v": 4},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
