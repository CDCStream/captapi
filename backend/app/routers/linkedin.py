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
from app.services import linkedin_native
from app.utils.formatters import first_present, safe_int, safe_str
from app.utils.url import (
    detect_url_platform,
    extract_linkedin_company,
    extract_linkedin_profile,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_PROFILE = 2
CREDIT_DETAILS = 1
CREDIT_NATIVE = linkedin_native.CREDIT_LINKEDIN_NATIVE
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


def _require_person_profile(data: dict[str, Any]) -> dict[str, Any]:
    """Reject Apify/native shells that have no identifying fields."""
    if data.get("name") or data.get("username"):
        return data
    raise HTTPException(status_code=404, detail="Profile not found")


def _require_company(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("name"):
        return data
    raise HTTPException(status_code=404, detail="Company not found")


def _normalize_profile(p: dict[str, Any]) -> dict[str, Any]:
    # apimaestro/linkedin-profile-detail nests everything under basic_info.
    info = p.get("basic_info") if isinstance(p.get("basic_info"), dict) else p
    location = info.get("location")
    if isinstance(location, dict):
        location = location.get("full") or location.get("city") or location.get("country")
    # Public HTML never exposes a reliable verified flag — omit the field.
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
    # Public company pages don't expose a reliable verified flag or cover URL
    # in our native/Apify shapes — omit those fields.
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
        "logo": safe_str(media.get("logo_url") or c.get("logo") or c.get("logoUrl")),
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
    # Use first_present — `or` drops real zeros (shares/comments often 0).
    engagement = {
        k: v
        for k, v in {
            "likes": safe_int(
                first_present(
                    stats.get("likes"),
                    stats.get("total_reactions"),
                    p.get("numLikes"),
                    p.get("reactionsCount"),
                )
            ),
            "comments": safe_int(
                first_present(stats.get("comments"), p.get("numComments"), p.get("commentsCount"))
            ),
            "reposts": safe_int(
                first_present(
                    stats.get("shares"),
                    p.get("reposts"),
                    p.get("numShares"),
                    p.get("repostsCount"),
                )
            ),
        }.items()
        if v is not None
    }
    author_out: dict[str, Any] = {
        "name": safe_str(author.get("name") or p.get("authorName") or p.get("companyName")),
        "url": safe_str(
            author.get("url") or author.get("profile_url") or p.get("authorUrl") or p.get("companyUrl")
        ),
    }
    # Public post HTML rarely exposes author job title — omit when unknown.
    if author_headline:
        author_out["headline"] = author_headline
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
        "author": author_out,
    }
    if engagement:
        out["engagement"] = engagement
    return out


_LI_ACTIVITY_RE = re.compile(r"activity[:-](\d{10,25})")


def _normalize_post_list_item(p: dict[str, Any], *, include_media: bool = True) -> dict[str, Any]:
    base = _normalize_post(p)
    post_id = safe_str(p.get("id") or p.get("urn") or p.get("post_id") or p.get("activity_id"))
    if not post_id:
        m = _LI_ACTIVITY_RE.search(base.get("url") or "")
        post_id = m.group(1) if m else None
    base["id"] = post_id
    if include_media:
        media = p.get("media") or p.get("images") or p.get("videos") or []
        if isinstance(media, dict):
            media = [media]
        base["media"] = media
    return base


def _normalize_company_post(p: dict[str, Any]) -> dict[str, Any]:
    """Normalize company-post rows from native / Apify actors into the shared shape."""
    row = dict(p) if isinstance(p, dict) else {}
    # vulnv/linkedin-company-posts uses post_text / date_posted / title.
    if not (row.get("text") or row.get("content") or row.get("commentary")):
        alt = row.get("post_text") or row.get("headline") or row.get("title")
        if alt:
            row["text"] = alt
    if not row.get("url"):
        row["url"] = row.get("postUrl") or row.get("post_url")
    if not row.get("id"):
        row["id"] = row.get("post_id") or row.get("urn") or row.get("activity_id")
    if not (
        row.get("publishedAt")
        or row.get("datePublished")
        or row.get("date")
        or (isinstance(row.get("postedAt"), dict) and row["postedAt"].get("date"))
    ):
        if row.get("date_posted") or row.get("published_at"):
            row["publishedAt"] = row.get("date_posted") or row.get("published_at")
    base = _normalize_post_list_item(row, include_media=False)
    author = base.get("author")
    if isinstance(author, dict):
        author.pop("headline", None)
        if not author.get("url"):
            author["url"] = safe_str(
                row.get("use_url") or row.get("author_company_url") or row.get("companyLinkedInUrl")
            )
        if not author.get("name"):
            author["name"] = safe_str(
                row.get("author_name") or row.get("companyName") or row.get("user_id")
            )
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
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await linkedin_native.fetch_profile(slug)
            if native:
                ctx["source"] = "direct"
                return _require_person_profile(_normalize_profile(native))

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_PROFILE,
                {"username": slug, "url": f"https://www.linkedin.com/in/{slug}"},
                max_items=1,
            )
            ctx["source"] = "apify"
            ctx["credits_override"] = CREDIT_PROFILE
            return _require_person_profile(_normalize_profile(_first(items)))

        data = await cached_or_run(
            endpoint="linkedin.profile",
            params={"slug": slug, "v": 5},
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
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await linkedin_native.fetch_company(slug)
            if native:
                ctx["source"] = "direct"
                return _require_company(_normalize_company(native))

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_COMPANY,
                {"company": slug, "url": f"https://www.linkedin.com/company/{slug}"},
                max_items=1,
            )
            ctx["source"] = "apify"
            ctx["credits_override"] = CREDIT_PROFILE
            return _require_company(_normalize_company(_first(items)))

        data = await cached_or_run(
            endpoint="linkedin.company",
            params={"slug": slug, "v": 5},
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
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await linkedin_native.fetch_post(url)
            if native:
                ctx["source"] = "direct"
                return _normalize_post(native)

            apify = get_apify()
            items = await apify.run_actor_sync(
                settings.APIFY_ACTOR_LINKEDIN_POST,
                {"post_urls": [url]},
                max_items=1,
            )
            ctx["source"] = "apify"
            ctx["credits_override"] = CREDIT_DETAILS
            return _normalize_post(_first(items))

        data = await cached_or_run(
            endpoint="linkedin.post-details",
            params={"url": url, "v": 3},
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
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await linkedin_native.fetch_post(url)
            if native:
                post = _normalize_post(native)
                ctx["source"] = "direct"
            else:
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_LINKEDIN_POST,
                    {"post_urls": [url]},
                    max_items=1,
                )
                post = _normalize_post(_first(items))
                ctx["source"] = "apify"
                ctx["credits_override"] = CREDIT_DETAILS
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
            params={"url": url, "v": 3},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


_LI_COMPANY_POSTS_MAX = 100
_LI_OFFSET_CURSOR_RE = re.compile(r"^\d{1,4}$")


def _parse_company_posts_cursor(cursor: str | None) -> int:
    if cursor is None or cursor == "":
        return 0
    if not _LI_OFFSET_CURSOR_RE.match(cursor):
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    offset = int(cursor)
    if offset >= _LI_COMPANY_POSTS_MAX:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    return offset


def _slice_company_posts_page(
    posts: list[dict[str, Any]], *, offset: int, limit: int
) -> dict[str, Any]:
    """Offset-page a fetched batch; nextCursor is the next offset string."""
    page = posts[offset : offset + limit]
    has_more = len(posts) > offset + limit
    return {
        "totalReturned": len(page),
        "posts": page,
        "nextCursor": str(offset + limit) if has_more else None,
        "hasMore": has_more,
    }


def _company_post_row_key(row: dict[str, Any]) -> str | None:
    """Stable id for merging native + Apify company-post rows."""
    if not isinstance(row, dict):
        return None
    for key in ("url", "postUrl", "post_url"):
        val = row.get(key)
        if val:
            m = _LI_ACTIVITY_RE.search(str(val))
            return m.group(1) if m else str(val)
    for key in ("id", "urn", "activity_id", "post_id"):
        if row.get(key) is not None:
            return str(row[key])
    basic = row.get("basic_info") if isinstance(row.get("basic_info"), dict) else None
    if basic and basic.get("url"):
        m = _LI_ACTIVITY_RE.search(str(basic["url"]))
        return m.group(1) if m else str(basic["url"])
    text = row.get("text") or row.get("content") or row.get("commentary")
    return str(text)[:120] if text else None


def _merge_company_post_rows(*batches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for batch in batches:
        for row in batch or []:
            key = _company_post_row_key(row)
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(row)
    return out


@router.get("/company-posts", summary="LinkedIn company posts")
async def linkedin_company_posts(
    url: str = Query(..., description="LinkedIn company URL, e.g. https://linkedin.com/company/slug"),
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Pagination cursor. Leave empty for the first page; then pass the nextCursor "
            "value returned in the previous response (numeric offset, e.g. 20). "
            "A null nextCursor means the end of the list (max 100 posts)."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    slug = _require_linkedin_company_url(url)
    settings = get_settings()
    company_url = f"https://www.linkedin.com/company/{slug}"
    offset = _parse_company_posts_cursor(cursor)
    # +1 sentinel so we know whether another page exists without over-fetching.
    need = min(_LI_COMPANY_POSTS_MAX, offset + limit + 1)
    async with billed_call(
        caller=caller,
        endpoint="/v1/linkedin/company-posts",
        platform="linkedin",
        resource_url=company_url,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # Native covers homepage embeds (~10); Apify can return more for active
            # pages (e.g. printi). Merge both so cursor paging isn't capped early.
            native = await linkedin_native.fetch_company_posts(slug, limit=need)
            collected: list[dict[str, Any]] = list(native or [])
            used_apify = False
            apify_target = min(
                _LI_COMPANY_POSTS_MAX,
                max(need, 30 if len(collected) < _LI_COMPANY_POSTS_MAX else need),
            )
            if len(collected) < apify_target:
                # Prefer maxPosts (vulnv / data-slayer); keep maxPostsPerCompany for
                # legacy automation-lab actor compatibility.
                items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_LI_COMPANY_POSTS,
                    {
                        "companyUrls": [company_url],
                        "maxPosts": apify_target,
                        "maxPostsPerCompany": apify_target,
                    },
                    max_items=apify_target,
                )
                if items:
                    merged = _merge_company_post_rows(collected, items)
                    if len(merged) > len(collected):
                        used_apify = True
                    collected = merged
                    if not collected:
                        collected = items
                        used_apify = True

            ctx["source"] = "apify" if used_apify else "direct"
            posts = [
                n
                for i in collected
                if (n := _normalize_company_post(i)).get("text") or n.get("url")
            ]
            page = _slice_company_posts_page(posts, offset=offset, limit=limit)
            return {"company": slug, **page}

        data = await cached_or_run(
            endpoint="linkedin.company-posts",
            params={"slug": slug, "limit": limit, "cursor": cursor or "", "v": 9},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_NATIVE
        else:
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
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # 1) SERP → Decodo post hydrate (LI content search is auth-walled).
            native = await linkedin_native.search_posts(q, sort=sort, limit=limit)
            if native:
                ctx["source"] = "direct"
                posts = [_normalize_post_list_item(i, include_media=False) for i in native[:limit]]
                return {"query": q, "sort": sort, "totalReturned": len(posts), "posts": posts}

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
            ctx["source"] = "apify"
            # Search actor never returns media attachments.
            posts = [_normalize_post_list_item(i, include_media=False) for i in items[:limit]]
            return {"query": q, "sort": sort, "totalReturned": len(posts), "posts": posts}

        data = await cached_or_run(
            endpoint="linkedin.search-posts",
            params={"q": q, "sort": sort, "limit": limit, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = CREDIT_NATIVE
        else:
            ctx["credits_override"] = _scaled(len(data["posts"]))
        return ApiResponse(data=data)
