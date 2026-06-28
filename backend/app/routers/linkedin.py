"""LinkedIn endpoints: person profile, company page, post details.

Public data only, via config-driven rental actors. Field mappings are
defensive across actor versions.
"""

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
    return {
        "platform": "linkedin",
        "type": "person",
        "url": safe_str(p.get("url") or p.get("profileUrl") or p.get("linkedinUrl")),
        "name": safe_str(p.get("fullName") or p.get("name")
                         or f"{p.get('firstName', '')} {p.get('lastName', '')}".strip()),
        "headline": safe_str(p.get("headline") or p.get("occupation")),
        "location": safe_str(p.get("location") or p.get("locationName")),
        "about": safe_str(p.get("about") or p.get("summary")),
        "followers": safe_int(p.get("followers") or p.get("followerCount")),
        "connections": safe_int(p.get("connections") or p.get("connectionsCount")),
        "profileImage": safe_str(p.get("profilePicture") or p.get("photoUrl") or p.get("avatar")),
        "currentCompany": safe_str(p.get("companyName") or p.get("company")),
    }


def _normalize_company(c: dict[str, Any]) -> dict[str, Any]:
    return {
        "platform": "linkedin",
        "type": "company",
        "url": safe_str(c.get("url") or c.get("linkedinUrl")),
        "name": safe_str(c.get("name") or c.get("companyName")),
        "industry": safe_str(c.get("industry")),
        "description": safe_str(c.get("description") or c.get("about")),
        "website": safe_str(c.get("website") or c.get("websiteUrl")),
        "followers": safe_int(c.get("followers") or c.get("followerCount")),
        "employees": safe_int(c.get("employeeCount") or c.get("staffCount") or c.get("companySize")),
        "headquarters": safe_str(c.get("headquarters") or c.get("location")),
        "logo": safe_str(c.get("logo") or c.get("logoUrl")),
    }


def _normalize_post(p: dict[str, Any]) -> dict[str, Any]:
    post = p.get("post") if isinstance(p.get("post"), dict) else p
    author = p.get("author") or post.get("author") or {}
    created = post.get("created_at") if isinstance(post.get("created_at"), dict) else {}
    stats = p.get("stats") if isinstance(p.get("stats"), dict) else p
    return {
        "platform": "linkedin",
        "type": "post",
        "url": safe_str(post.get("url") or p.get("url") or p.get("postUrl")),
        "text": safe_str(post.get("text") or p.get("text") or p.get("content") or p.get("commentary")),
        "publishedAt": safe_str(
            created.get("date")
            or post.get("postedAt")
            or post.get("publishedAt")
            or p.get("date")
        ),
        "author": {
            "name": safe_str(author.get("name") or p.get("authorName")),
            "headline": safe_str(author.get("headline")),
            "url": safe_str(author.get("url") or author.get("profile_url") or p.get("authorUrl")),
        },
        "engagement": {
            "likes": safe_int(
                stats.get("likes") or p.get("numLikes") or p.get("reactionsCount")
            ),
            "comments": safe_int(
                stats.get("comments") or p.get("numComments") or p.get("commentsCount")
            ),
            "reposts": safe_int(
                stats.get("shares") or p.get("reposts") or p.get("numShares") or p.get("repostsCount")
            ),
        },
    }


def _normalize_post_list_item(p: dict[str, Any]) -> dict[str, Any]:
    base = _normalize_post(p)
    base["id"] = safe_str(p.get("id") or p.get("urn") or p.get("post_id"))
    base["media"] = p.get("media") or p.get("images") or p.get("videos") or []
    return base


@router.get("/profile", summary="LinkedIn person profile details")
async def linkedin_profile(
    url: str = Query(..., description="LinkedIn profile URL, e.g. https://linkedin.com/in/slug"),
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
            params={"slug": slug},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/company", summary="LinkedIn company page details")
async def linkedin_company(
    url: str = Query(..., description="LinkedIn company URL, e.g. https://linkedin.com/company/slug"),
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
            params={"slug": slug},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/post-details", summary="LinkedIn post metadata + engagement")
async def linkedin_post_details(
    url: str = Query(..., description="LinkedIn post/activity URL"),
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
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/post-transcript", summary="LinkedIn post transcript / text extraction")
async def linkedin_post_transcript(
    url: str = Query(..., description="LinkedIn post/activity URL"),
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
            params={"url": url},
            runner=_run,
            ctx=ctx,
        )
        return ApiResponse(data=data)


@router.get("/company-posts", summary="LinkedIn company posts")
async def linkedin_company_posts(
    url: str = Query(..., description="LinkedIn company URL, e.g. https://linkedin.com/company/slug"),
    limit: int = Query(20, ge=1, le=100),
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
            params={"slug": slug, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]))
        return ApiResponse(data=data)


@router.get("/search-posts", summary="Search LinkedIn posts")
async def linkedin_search_posts(
    q: str = Query(..., min_length=2, description="Keyword to search in public LinkedIn posts"),
    sort: str = Query("relevance", pattern="^(relevance|date)$"),
    limit: int = Query(20, ge=1, le=50),
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
            params={"q": q, "sort": sort, "limit": limit},
            runner=_run,
            ctx=ctx,
        )
        ctx["credits_override"] = _scaled(len(data["posts"]))
        return ApiResponse(data=data)
