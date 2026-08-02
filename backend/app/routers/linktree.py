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
from app.services.http_fetch import DEFAULT_HEADERS
from app.utils.formatters import safe_str
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

CREDIT_PAGE = 1

_EMAIL_RE = re.compile(
    r"mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
    re.IGNORECASE,
)


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
        if not isinstance(item, dict):
            if isinstance(item, str):
                candidates.append(item)
            continue
        stype = str(item.get("type") or "").upper()
        if stype in ("EMAIL_ADDRESS", "EMAIL", "PHONE", "WHATSAPP"):
            continue
        if item.get("url"):
            candidates.append(str(item["url"]))
    for link in links:
        candidates.extend(_iter_link_urls(link))
    for url in candidates:
        if not url or url.lower().startswith("mailto:"):
            continue
        low = url.lower()
        for key, hosts in _SOCIAL_HOSTS:
            if key not in accounts and any(h in low for h in hosts):
                accounts[key] = url
                break
    return accounts


def _iter_link_urls(link: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    if link.get("url"):
        urls.append(str(link["url"]))
    for child in link.get("links") or []:
        if isinstance(child, dict):
            urls.extend(_iter_link_urls(child))
    return urls


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


def _parent_id(item: dict[str, Any]) -> str | None:
    parent = item.get("parent")
    if parent is None or parent is False:
        return None
    if isinstance(parent, dict):
        pid = parent.get("id")
        return str(pid) if pid is not None else None
    if isinstance(parent, (int, str)) and str(parent).strip():
        return str(parent)
    return None


def _link_thumbnail(item: dict[str, Any]) -> str | None:
    thumb = safe_str(item.get("thumbnail") or item.get("thumbnailUrl"))
    if thumb:
        return thumb
    modifiers = item.get("modifiers") if isinstance(item.get("modifiers"), dict) else {}
    thumb = safe_str(modifiers.get("thumbnailUrl"))
    if thumb:
        return thumb
    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
    return safe_str(metadata.get("thumbnail") or metadata.get("image"))


def _normalize_link(item: dict[str, Any], *, parent_id: str | None = None) -> dict[str, Any]:
    raw_id = item.get("id")
    link_id = (safe_str(raw_id) or str(raw_id)) if raw_id is not None else None
    link: dict[str, Any] = {
        "title": safe_str(item.get("title")),
        "type": safe_str(item.get("type") or item.get("linkType")),
    }
    if link_id:
        link["id"] = link_id
    link_url = safe_str(item.get("url") or item.get("link"))
    thumb = _link_thumbnail(item)
    if link_url:
        link["url"] = link_url
    if thumb:
        link["thumbnail"] = thumb
    if parent_id:
        link["parentId"] = parent_id
    return {k: v for k, v in link.items() if v is not None}


def _extract_email(social_list: list[Any], page_html: str) -> str | None:
    for item in social_list:
        if not isinstance(item, dict):
            continue
        stype = str(item.get("type") or "").upper()
        url = str(item.get("url") or "")
        if stype in ("EMAIL_ADDRESS", "EMAIL") or url.lower().startswith("mailto:"):
            match = _EMAIL_RE.search(url)
            if match:
                return match.group(1)
            if "@" in url and not url.lower().startswith("http"):
                return url.strip()
    match = _EMAIL_RE.search(page_html or "")
    return match.group(1) if match else None


def _clean_socials(social_list: list[Any]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for item in social_list:
        if not isinstance(item, dict):
            continue
        row = {
            k: v
            for k, v in item.items()
            if not (k == "position" and v in (0, None))
        }
        # Keep type/url; drop empty noise.
        out: dict[str, Any] = {}
        if row.get("type") is not None:
            out["type"] = safe_str(row.get("type")) or row.get("type")
        if row.get("url"):
            out["url"] = safe_str(row.get("url")) or row.get("url")
        if out.get("type") or out.get("url"):
            cleaned.append(out)
    return cleaned


def _build_link_tree(raw_links: list[Any]) -> tuple[list[dict[str, Any]], int]:
    """Return root links (GROUP children nested under ``links``) and total count."""
    items: list[dict[str, Any]] = [x for x in raw_links if isinstance(x, dict)]
    ids = {str(item.get("id")) for item in items if item.get("id") is not None}
    by_parent: dict[str | None, list[dict[str, Any]]] = {}
    for item in items:
        pid = _parent_id(item)
        # Orphans (missing parent row) surface at the root so links aren't dropped.
        if pid is not None and pid not in ids:
            pid = None
        by_parent.setdefault(pid, []).append(item)

    def build(item: dict[str, Any], parent_id: str | None) -> dict[str, Any]:
        node = _normalize_link(item, parent_id=parent_id)
        item_id = str(item.get("id")) if item.get("id") is not None else None
        children_raw = by_parent.get(item_id) or []
        if children_raw:
            node["links"] = [build(child, item_id) for child in children_raw]
        return node

    roots = [build(item, None) for item in by_parent.get(None, [])]
    return roots, len(items)


def _normalize(data: dict[str, Any], url: str, page_html: str = "") -> dict[str, Any]:
    page = _page_props(data)
    account = page.get("account") or page.get("profile") or {}
    raw_links = page.get("links") or account.get("links") or page.get("buttons") or []
    if isinstance(raw_links, list) and len(raw_links) == 0:
        raw_links = account.get("links") or []
    socials = (
        page.get("socialLinks")
        or page.get("socials")
        or account.get("socialLinks")
        or account.get("socials")
        or []
    )
    username = safe_str(account.get("username") or account.get("profile") or page.get("username"))
    normalized_links, total_links = _build_link_tree(raw_links if isinstance(raw_links, list) else [])

    verticals = [v for v in (account.get("verticals") or []) if isinstance(v, str) and v.strip()]
    if not verticals and isinstance(account.get("pageMeta"), dict) and account["pageMeta"].get("vertical"):
        verticals = [str(account["pageMeta"]["vertical"])]
    if not verticals and account.get("seoPrimaryVertical"):
        verticals = [str(account["seoPrimaryVertical"])]

    link_platforms = [
        p for p in (account.get("linkPlatforms") or []) if isinstance(p, str) and p.strip()
    ]

    social_list = socials if isinstance(socials, list) else []
    cleaned_socials = _clean_socials(social_list)
    email = _extract_email(social_list, page_html)

    out: dict[str, Any] = {
        "platform": "linktree",
        "url": safe_str(url),
        "id": account.get("id"),
        "username": username,
        "name": _display_name(account, username),
        "description": safe_str(account.get("description") or account.get("bio")),
        "avatar": safe_str(
            account.get("avatarUrl")
            or account.get("profilePictureUrl")
            or account.get("customAvatar")
        ),
        "verified": bool(account.get("isVerified") or account.get("verified")),
        "verticals": verticals,
        "linkPlatforms": link_platforms,
        "timezone": safe_str(account.get("timezone")),
        "email": email,
        "linkCount": total_links,
        "links": normalized_links,
        # ``socials`` = icon list from Linktree (incl. EMAIL_ADDRESS).
        # ``socialAccounts`` = camelCase URL map for lookups (instagram/tiktok/…).
        "socials": cleaned_socials,
        "socialAccounts": _social_accounts(social_list, normalized_links),
    }
    for key in ("name", "description", "avatar", "timezone", "verticals", "linkPlatforms", "email"):
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
    async with billed_call(
        caller=caller,
        endpoint="/v1/linktree/page",
        platform="linktree",
        resource_url=profile,
        base_credits=CREDIT_PAGE,
    ) as ctx:

        async def _run() -> dict[str, Any]:
            headers = {
                **DEFAULT_HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://linktr.ee/",
            }
            async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
                resp = await client.get(profile)
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Linktree profile not found")
            if resp.status_code >= 400:
                raise HTTPException(status_code=502, detail="Linktree lookup failed")
            data = _normalize(_find_next_data(resp.text), str(resp.url), resp.text)
            if not data.get("links") and not data.get("username"):
                raise HTTPException(status_code=404, detail="Linktree profile not found")
            return data

        # bump cache key: tree links + email/verticals/platforms
        data = await cached_or_run("linktree.page", {"url": profile, "v": 4}, _run, ctx, use_cache=cache)
        return ApiResponse(data=data)
