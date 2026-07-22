"""Linktree public page endpoint."""

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


def _profile_url(value: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "linktree":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "linktree", "https://linktr.ee/username"),
        )
    value = (value or "").strip().rstrip("/")
    if value.startswith("http"):
        return value
    return f"https://linktr.ee/{value.lstrip('@')}"


def _find_next_data(page: str) -> dict[str, Any]:
    match = re.search(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        page,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise HTTPException(status_code=404, detail="Linktree profile not found")
    try:
        return json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Linktree profile parse failed") from exc


def _page_props(data: dict[str, Any]) -> dict[str, Any]:
    props = data.get("props") or {}
    page_props = props.get("pageProps") or {}
    if "account" in page_props or "links" in page_props:
        return page_props
    for value in page_props.values():
        if isinstance(value, dict) and ("account" in value or "links" in value):
            return value
    return page_props


_SOCIAL_HOSTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("instagram", ("instagram.com",)),
    ("tiktok", ("tiktok.com",)),
    ("youtube", ("youtube.com", "youtu.be")),
    ("twitter", ("twitter.com", "x.com")),
    ("facebook", ("facebook.com", "fb.com")),
    ("snapchat", ("snapchat.com",)),
    ("spotify", ("open.spotify.com", "spotify.com")),
    ("soundcloud", ("soundcloud.com",)),
    ("appleMusic", ("music.apple.com",)),
    ("linkedin", ("linkedin.com",)),
    ("twitch", ("twitch.tv",)),
    ("pinterest", ("pinterest.com",)),
    ("threads", ("threads.net", "threads.com")),
)


def _social_accounts(social_links: list[Any], links: list[dict[str, Any]]) -> dict[str, str]:
    """Resolve well-known platforms to URLs (SC-parity: instagram/tiktok/... keys)."""
    accounts: dict[str, str] = {}
    candidates: list[str] = []
    for item in social_links:
        if isinstance(item, dict) and item.get("url"):
            candidates.append(str(item["url"]))
        elif isinstance(item, str):
            candidates.append(item)
    candidates.extend(link.get("url") or "" for link in links)
    for url in candidates:
        low = url.lower()
        for key, hosts in _SOCIAL_HOSTS:
            if key not in accounts and any(h in low for h in hosts):
                accounts[key] = url
                break
    return accounts


def _display_name(account: dict[str, Any], username: str | None) -> str | None:
    """Prefer an explicit name; fall back to pageTitle when it isn't just @username."""
    name = safe_str(account.get("name") or account.get("displayName"))
    if name:
        return name
    page_title = safe_str(account.get("pageTitle"))
    if not page_title:
        return None
    handle = (username or "").lstrip("@").lower()
    if page_title.lstrip("@").lower() == handle:
        return None
    return page_title


def _normalize(data: dict[str, Any], url: str) -> dict[str, Any]:
    page = _page_props(data)
    account = page.get("account") or page.get("profile") or {}
    links = page.get("links") or page.get("buttons") or []
    socials = page.get("socialLinks") or page.get("socials") or account.get("socialLinks") or []
    username = safe_str(account.get("username") or account.get("profile") or page.get("username"))
    normalized_links: list[dict[str, Any]] = []
    for item in links if isinstance(links, list) else []:
        if not isinstance(item, dict):
            continue
        link: dict[str, Any] = {
            "id": safe_str(item.get("id")),
            "title": safe_str(item.get("title")),
            "type": safe_str(item.get("type") or item.get("linkType")),
        }
        # GROUP rows never have a destination URL/thumbnail upstream — omit empties.
        link_url = safe_str(item.get("url") or item.get("link"))
        thumb = safe_str(item.get("thumbnail") or item.get("thumbnailUrl"))
        if link_url:
            link["url"] = link_url
        if thumb:
            link["thumbnail"] = thumb
        normalized_links.append(link)

    verticals = [v for v in (account.get("verticals") or []) if isinstance(v, str)]
    if not verticals and isinstance(account.get("pageMeta"), dict) and account["pageMeta"].get("vertical"):
        verticals = [str(account["pageMeta"]["vertical"])]

    social_list = socials if isinstance(socials, list) else []
    # Drop always-zero social positions — Linktree sends 0 for every icon.
    cleaned_socials: list[Any] = []
    for item in social_list:
        if isinstance(item, dict):
            row = {k: v for k, v in item.items() if not (k == "position" and v in (0, None))}
            cleaned_socials.append(row)
        else:
            cleaned_socials.append(item)

    out: dict[str, Any] = {
        "platform": "linktree",
        "url": safe_str(url),
        "id": account.get("id"),
        "username": username,
        "name": _display_name(account, username),
        "description": safe_str(account.get("description") or account.get("bio")),
        "avatar": safe_str(account.get("avatarUrl") or account.get("profilePictureUrl")),
        "verified": bool(account.get("isVerified") or account.get("verified")),
        "verticals": verticals,
        "timezone": safe_str(account.get("timezone")),
        "linkCount": len(normalized_links),
        "links": normalized_links,
        "socials": cleaned_socials,
        "socialAccounts": _social_accounts(social_list, normalized_links),
    }
    for key in ("name", "description", "avatar", "timezone", "verticals"):
        if out.get(key) in (None, "", []):
            out.pop(key, None)
    return out


@router.get("/page", summary="Linktree page")
async def linktree_page(
    url: str = Query(..., description="Linktree profile URL or username"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    profile = _profile_url(url)
    async with billed_call(caller=caller, endpoint="/v1/linktree/page", platform="linktree", resource_url=profile, base_credits=4) as ctx:
        async def _run() -> dict[str, Any]:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
            async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
                resp = await client.get(profile)
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Linktree profile not found")
            if resp.status_code >= 400:
                raise HTTPException(status_code=502, detail="Linktree lookup failed")
            data = _normalize(_find_next_data(resp.text), str(resp.url))
            if not data.get("links") and not data.get("username"):
                raise HTTPException(status_code=404, detail="Linktree profile not found")
            return data

        data = await cached_or_run("linktree.page", {"url": profile, "v": 3}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)
