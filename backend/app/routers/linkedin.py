"""LinkedIn endpoints: person profile, company page, post details.

Public data only, via config-driven rental actors. Field mappings are
defensive across actor versions.
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
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str
from app.utils.url import (
    detect_url_platform,
    extract_linkedin_company,
    extract_linkedin_profile,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_PROFILE = 2
CREDIT_DETAILS = 1
RATE = 0.8


def _scaled(limit: int, minimum: int = 2) -> int:
    if limit <= 0:
        return 0
    return max(minimum, math.ceil(limit * RATE))


def _reject_linkedin_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "linkedin":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "linkedin", example),
        )


def _require_linkedin_profile_url(url: str) -> str:
    slug = extract_linkedin_profile(url)
    if not slug:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "linkedin", "https://www.linkedin.com/in/username"),
        )
    return slug


def _require_linkedin_company_url(url: str) -> str:
    slug = extract_linkedin_company(url)
    if not slug:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "linkedin", "https://www.linkedin.com/company/company-name"),
        )
    return slug


def _first(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not items:
        raise HTTPException(status_code=404, detail="Not found on LinkedIn")
    return items[0]


def _normalize_profile(p: dict[str, Any]) -> dict[str, Any]:
    # apimaestro/linkedin-profile-detail nests everything under basic_info.
    info = p.get("basic_info") if isinstance(p.get("basic_info"), dict) else p
    location = info.get("location")
    if isinstance(location, dict):
        location = location.get("full") or location.get("city") or location.get("country")
    verified = info.get("is_verified")
    return {
        "platform": "linkedin",
        "type": "person",
        "url": safe_str(info.get("profile_url") or p.get("url") or p.get("profileUrl") or p.get("linkedinUrl")),
        "username": safe_str(info.get("public_identifier")),
        "name": safe_str(info.get("fullname") or p.get("fullName") or p.get("name")
                         or f"{info.get('first_name', '')} {info.get('last_name', '')}".strip()),
        "headline": safe_str(info.get("headline") or p.get("occupation")),
        "location": safe_str(location or p.get("locationName")),
        "about": safe_str(info.get("about") or p.get("summary")),
        "followers": safe_int(info.get("follower_count") or p.get("followers") or p.get("followerCount")),
        "connections": safe_int(info.get("connection_count") or p.get("connections") or p.get("connectionsCount")),
        "verified": verified if isinstance(verified, bool) else None,
        "profileImage": safe_str(
            info.get("profile_picture_url") or p.get("profilePicture") or p.get("photoUrl") or p.get("avatar")
        ),
        "currentCompany": safe_str(info.get("current_company") or p.get("companyName") or p.get("company")),
    }


def _normalize_company(c: dict[str, Any]) -> dict[str, Any]:
    # apimaestro/linkedin-company-detail splits data across basic_info /
    # stats / media / locations.
    info = c.get("basic_info") if isinstance(c.get("basic_info"), dict) else c
    stats = c.get("stats") if isinstance(c.get("stats"), dict) else {}
    media = c.get("media") if isinstance(c.get("media"), dict) else {}
    hq = ((c.get("locations") or {}).get("headquarters") or {}) if isinstance(c.get("locations"), dict) else {}
    industries = info.get("industries")
    industry = industries[0] if isinstance(industries, list) and industries else info.get("industry")
    hq_text = ", ".join(x for x in [hq.get("city"), hq.get("state"), hq.get("country")] if x) or None
    verified = info.get("is_verified")
    return {
        "platform": "linkedin",
        "type": "company",
        "url": safe_str(info.get("linkedin_url") or c.get("url") or c.get("linkedinUrl")),
        "name": safe_str(info.get("name") or c.get("companyName")),
        "industry": safe_str(industry),
        "description": safe_str(info.get("description") or c.get("about") or c.get("tagline")),
        "website": safe_str(info.get("website") or c.get("websiteUrl")),
        "followers": safe_int(stats.get("follower_count") or c.get("followers") or c.get("followerCount")),
        "employees": safe_int(
            stats.get("employee_count") or c.get("employeeCount") or c.get("staffCount") or c.get("companySize")
        ),
        "headquarters": safe_str(hq_text or c.get("headquarters") or c.get("location")),
        "verified": verified if isinstance(verified, bool) else None,
        "logo": safe_str(media.get("logo_url") or c.get("logo") or c.get("logoUrl")),
        "coverImage": safe_str(media.get("cover_url")),
    }


def _normalize_post(p: dict[str, Any]) -> dict[str, Any]:
    post = p.get("post") if isinstance(p.get("post"), dict) else p
    author = p.get("author") or post.get("author") or {}
    if not isinstance(author, dict):
        author = {}
    created = post.get("created_at") if isinstance(post.get("created_at"), dict) else {}
    # apimaestro search rows: posted_at {date, timestamp}; automation-lab
    # company rows: flat datePublished.
    posted_at = p.get("posted_at") if isinstance(p.get("posted_at"), dict) else {}
    stats = p.get("stats") if isinstance(p.get("stats"), dict) else p
    # Do NOT fall back to top-level `headline` — on company JSON-LD rows that
    # field is the post title (e.g. "June"), not the author's job title.
    author_headline = safe_str(
        author.get("headline")
        or author.get("occupation")
        or p.get("authorHeadline")
        or p.get("author_headline")
    )
    engagement = {
        "likes": safe_int(
            stats.get("likes") or stats.get("total_reactions") or p.get("numLikes") or p.get("reactionsCount")
        ),
        "comments": safe_int(
            stats.get("comments") or p.get("numComments") or p.get("commentsCount")
        ),
        "reposts": safe_int(
            stats.get("shares") or p.get("reposts") or p.get("numShares") or p.get("repostsCount")
        ),
    }
    out: dict[str, Any] = {
        "platform": "linkedin",
        "type": "post",
        "url": safe_str(post.get("url") or p.get("url") or p.get("postUrl") or p.get("post_url")),
        "text": safe_str(post.get("text") or p.get("text") or p.get("content") or p.get("commentary")),
        "publishedAt": safe_str(
            created.get("date")
            or posted_at.get("date")
            or post.get("postedAt")
            or post.get("publishedAt")
            or p.get("datePublished")
            or p.get("date")
        ),
        "author": {
            "name": safe_str(author.get("name") or p.get("authorName") or p.get("companyName")),
            "headline": author_headline,
            "url": safe_str(
                author.get("url") or author.get("profile_url") or p.get("authorUrl") or p.get("companyUrl")
            ),
        },
    }
    # automation-lab company-posts actor is JSON-LD only — no likes/comments.
    # Omit the empty engagement block instead of returning always-null keys.
    if any(v is not None for v in engagement.values()):
        out["engagement"] = engagement
    return out


_LI_ACTIVITY_RE = re.compile(r"activity[:-](\d{10,25})")


def _normalize_post_list_item(p: dict[str, Any]) -> dict[str, Any]:
    base = _normalize_post(p)
    post_id = safe_str(p.get("id") or p.get("urn") or p.get("post_id") or p.get("activity_id"))
    if not post_id:
        m = _LI_ACTIVITY_RE.search(base.get("url") or "")
        post_id = m.group(1) if m else None
    base["id"] = post_id
    media = p.get("media") or p.get("images") or p.get("videos") or []
    if isinstance(media, dict):
        media = [media]
    base["media"] = media
    return base


@router.get("/profile", summary="LinkedIn person profile details")
async def linkedin_profile(
    url: str = Query(..., description="LinkedIn profile URL, e.g. https://linkedin.com/in/slug"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    slug = _require_linkedin_profile_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/profile",
        platform="linkedin",
        resource_url=f"https://www.linkedin.com/in/{slug}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_PROFILE,
                {"username": slug, "url": f"https://www.linkedin.com/in/{slug}"},
                max_items=1,
            )
            return _normalize_profile(_first(items))

        data = await cached_or_run(
            endpoint="linkedin.profile",
            params={"slug": slug, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/company", summary="LinkedIn company page details")
async def linkedin_company(
    url: str = Query(..., description="LinkedIn company URL, e.g. https://linkedin.com/company/slug"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    slug = _require_linkedin_company_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/company",
        platform="linkedin",
        resource_url=f"https://www.linkedin.com/company/{slug}",
        base_credits=CREDIT_PROFILE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_COMPANY,
                {"company": slug, "url": f"https://www.linkedin.com/company/{slug}"},
                max_items=1,
            )
            return _normalize_company(_first(items))

        data = await cached_or_run(
            endpoint="linkedin.company",
            params={"slug": slug, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/post-details", summary="LinkedIn post metadata + engagement")
async def linkedin_post_details(
    url: str = Query(..., description="LinkedIn post/activity URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_linkedin_platform_mismatch(url, "https://www.linkedin.com/posts/activity-123456789")
    if "linkedin.com" not in (url or ""):
        raise HTTPException(status_code=400, detail="Invalid LinkedIn post URL. Pass a LinkedIn URL like https://www.linkedin.com/posts/activity-123456789.")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/post-details",
        platform="linkedin",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_POST,
                {"post_urls": [url]},
                max_items=1,
            )
            return _normalize_post(_first(items))

        data = await cached_or_run(
            endpoint="linkedin.post-details",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/post-transcript", summary="LinkedIn post transcript / text extraction")
async def linkedin_post_transcript(
    url: str = Query(..., description="LinkedIn post/activity URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_linkedin_platform_mismatch(url, "https://www.linkedin.com/posts/activity-123456789")
    if "linkedin.com" not in (url or ""):
        raise HTTPException(status_code=400, detail="Invalid LinkedIn post URL. Pass a LinkedIn URL like https://www.linkedin.com/posts/activity-123456789.")
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/post-transcript",
        platform="linkedin",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_POST,
                {"post_urls": [url]},
                max_items=1,
            )
            post = _normalize_post(_first(items))
            text = (post.get("text") or "").strip()
            if not text:
                raise HTTPException(status_code=422, detail="No transcript text available for this LinkedIn post")
            return {
                "platform": "linkedin",
                "url": post.get("url") or url,
                "transcript": text,
                "transcriptSegments": [{"text": text, "start": 0, "duration": 0, "timestamp": "00:00"}],
                "wordCount": len(text.split()),
                "segments": 1,
                "author": post.get("author"),
                "publishedAt": post.get("publishedAt"),
            }

        data = await cached_or_run(
            endpoint="linkedin.post-transcript",
            params={"url": url, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/company-posts", summary="LinkedIn company posts")
async def linkedin_company_posts(
    url: str = Query(..., description="LinkedIn company URL, e.g. https://linkedin.com/company/slug"),
    limit: int = Query(20, ge=1, le=100),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    slug = _require_linkedin_company_url(url)
    settings = get_settings()
    company_url = f"https://www.linkedin.com/company/{slug}"
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/company-posts",
        platform="linkedin",
        resource_url=company_url,
        base_credits=_scaled(limit),
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_COMPANY_POSTS,
                {"companyUrls": [company_url], "maxPostsPerCompany": limit},
                max_items=limit,
            )
            posts = [_normalize_post_list_item(i) for i in items[:limit]]
            return {"company": slug, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="linkedin.company-posts",
            params={"slug": slug, "limit": limit, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]))
        return ApiResponse(data=data)


@router.get("/search-posts", summary="Search LinkedIn posts")
async def linkedin_search_posts(
    q: str = Query(..., min_length=2, description="Keyword to search in public LinkedIn posts"),
    sort: str = Query("relevance", pattern="^(relevance|date)$"),
    limit: int = Query(20, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/search-posts",
        platform="linkedin",
        resource_url=None,
        base_credits=_scaled(limit),
    ) as ctx:
        async def _run() -> dict[str, Any]:
            items = await get_apify().run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_POST_SEARCH,
                {
                    "keyword": q,
                    "sort_type": sort,
                    "page_number": 1,
                    "date_filter": "",
                    "limit": limit,
                },
                max_items=limit,
            )
            posts = [_normalize_post_list_item(i) for i in items[:limit]]
            return {"query": q, "sort": sort, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="linkedin.search-posts",
            params={"q": q, "sort": sort, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]))
        return ApiResponse(data=data)
