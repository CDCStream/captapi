"""Small link-in-bio public page endpoints."""

from __future__ import annotations

import html
import json
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

BASES = {
    "komi": "https://komi.io",
    "pillar": "https://pillar.io",
    # ScrapeCreators' "Linkbio" endpoint targets lnk.bio (not linkbio.co/Instabio).
    "linkbio": "https://lnk.bio",
    "linkme": "https://link.me",
}
EXAMPLES = {
    "komi": "https://komi.io/username",
    "pillar": "https://pillar.io/username",
    "linkbio": "https://lnk.bio/username",
    "linkme": "https://link.me/username",
}

# lnk.bio (and similar) sprinkle their own nav/share links through the markup;
# these hosts must be filtered out so we only return the creator's real links.
_NAV_HOSTS = (
    "lnk.bio",
    "linkinbio.wiki",
    "facebook.com/sharer",
    "wa.me",
    "twitter.com/intent",
    "line.me/lineit",
    "story.kakao.com/share",
    "reddit.com/submit",
    "linkedin.com/sharing",
    "komi.io",
    "pillar.io",
    "link.me",
)


def _url(platform: str, value: str) -> str:
    value = (value or "").strip().rstrip("/")
    if value.startswith("http"):
        return value
    return f"{BASES[platform]}/{value.lstrip('@')}"


def _meta(page: str, name: str) -> str | None:
    esc = re.escape(name)
    patterns = [
        # content after property/name (e.g. <meta property="og:title" content="...">)
        rf'<meta[^>]+(?:property|name)=["\']{esc}["\'][^>]+content=["\']([^"\']*)',
        # content before property/name (e.g. <meta content="..." property="og:title">)
        rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']{esc}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page, flags=re.IGNORECASE)
        if match:
            return html.unescape(match.group(1)).strip()
    return None


def _next_data(page: str) -> dict[str, Any]:
    match = re.search(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', page, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError:
        return {}


def _walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _walk(value)


def _links(data: dict[str, Any]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    links = []
    for obj in _walk(data):
        raw_url = obj.get("url") or obj.get("link") or obj.get("href") or obj.get("targetUrl")
        if not isinstance(raw_url, str) or not raw_url.startswith("http"):
            continue
        if raw_url in seen:
            continue
        seen.add(raw_url)
        links.append(
            {
                "id": safe_str(obj.get("id") or obj.get("_id")),
                "title": safe_str(obj.get("title") or obj.get("name") or obj.get("label") or obj.get("text")),
                "url": safe_str(raw_url),
                "type": safe_str(obj.get("type") or obj.get("kind")),
                "thumbnail": safe_str(obj.get("thumbnail") or obj.get("image") or obj.get("imageUrl")),
            }
        )
    return links[:200]


def _anchor_links(page: str) -> list[dict[str, Any]]:
    """Fallback link extraction for server-rendered pages (e.g. lnk.bio) that
    don't ship a hydration blob. Pulls outbound <a href> targets, drops the
    platform's own nav/share links, and de-dupes."""
    seen: set[str] = set()
    links: list[dict[str, Any]] = []
    for match in re.finditer(r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', page, flags=re.IGNORECASE | re.DOTALL):
        href = html.unescape(match.group(1)).strip()
        low = href.lower()
        if any(nav in low for nav in _NAV_HOSTS):
            continue
        if href in seen:
            continue
        seen.add(href)
        text = re.sub(r"<[^>]+>", " ", match.group(2))
        text = re.sub(r"\s+", " ", html.unescape(text)).strip()
        links.append({"id": None, "title": safe_str(text) or None, "url": safe_str(href), "type": None, "thumbnail": None})
    return links[:200]


def _first_string(data: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for obj in _walk(data):
        for key in keys:
            value = obj.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


async def _fetch_page(platform: str, value: str) -> dict[str, Any]:
    profile = _url(platform, value)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
        resp = await client.get(profile)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail=f"{platform.title()} page not found")
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"{platform.title()} lookup failed")
    page = resp.text
    data = _next_data(page)
    links = _links(data)
    if not links:
        links = _anchor_links(page)
    title = _meta(page, "og:title") or _meta(page, "twitter:title") or _first_string(data, ("displayName", "name", "title", "username"))
    description = _meta(page, "og:description") or _meta(page, "description") or _first_string(data, ("bio", "description", "subtitle"))
    avatar = _meta(page, "og:image") or _meta(page, "twitter:image") or _first_string(data, ("avatar", "avatarUrl", "profilePicture", "imageUrl"))
    username = _first_string(data, ("username", "handle", "slug")) or str(resp.url).rstrip("/").rsplit("/", 1)[-1]
    return {
        "platform": platform,
        "url": safe_str(str(resp.url)),
        "username": safe_str(username),
        "name": safe_str(title),
        "description": safe_str(description),
        "avatar": safe_str(avatar),
        "linkCount": len(links),
        "links": links,
    }


async def _page(platform: str, url: str, caller: ApiCaller):
    detected = detect_url_platform(url)
    if detected and detected != platform:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, platform, EXAMPLES[platform]),
        )
    profile = _url(platform, url)
    async with billed_call(caller=caller, endpoint=f"/v1/{platform}/{'profile' if platform == 'linkme' else 'page'}", platform=platform, resource_url=profile, base_credits=4) as ctx:
        data = await cached_or_run(f"{platform}.page", {"url": profile}, lambda: _fetch_page(platform, profile), ctx)
        if not (data.get("username") or data.get("links")):
            raise HTTPException(status_code=404, detail=f"{platform.title()} page not found")
        return ApiResponse(data=data)


@router.get("/komi/page", summary="Komi page")
async def komi_page(url: str = Query(..., description="Komi page URL or username"), caller: ApiCaller = Depends(require_api_key)):
    return await _page("komi", url, caller)


@router.get("/pillar/page", summary="Pillar page")
async def pillar_page(url: str = Query(..., description="Pillar page URL or username"), caller: ApiCaller = Depends(require_api_key)):
    return await _page("pillar", url, caller)


@router.get("/linkbio/page", summary="Linkbio page")
async def linkbio_page(url: str = Query(..., description="Linkbio (lnk.bio) page URL or username"), caller: ApiCaller = Depends(require_api_key)):
    return await _page("linkbio", url, caller)


@router.get("/linkme/profile", summary="Linkme profile")
async def linkme_profile(url: str = Query(..., description="Linkme profile URL or username"), caller: ApiCaller = Depends(require_api_key)):
    return await _page("linkme", url, caller)
