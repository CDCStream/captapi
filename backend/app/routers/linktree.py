"""Linktree public page endpoint."""

from __future__ import annotations

import html
import json
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.cache_params import CACHE_MAX_AGE_DESC, resolve_cache_options
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services import decodo_fetch
from app.services.cached_runner import cached_or_run
from app.services.http_fetch import DEFAULT_HEADERS
from app.utils.formatters import safe_str
from app.utils.profile_core import stamp_profile_core
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

CREDIT_PAGE = 1

_EMAIL_RE = re.compile(
    r"mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
    re.IGNORECASE,
)
_YT_WATCH_RE = re.compile(
    r"(?:youtube\.com/watch\?(?:[^#]*&)?v=|youtu\.be/)([\w-]{6,})",
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
    ("whatsapp", ("wa.me", "api.whatsapp.com", "whatsapp.com")),
    ("triller", ("triller.co",)),
)


def _youtube_rank(url: str) -> int:
    """Lower is better — prefer channel/handle URLs over watch links."""
    low = (url or "").lower()
    if "/@" in low or "/channel/" in low or "/c/" in low or "/user/" in low:
        return 0
    if "watch?" in low or "youtu.be/" in low or "/shorts/" in low:
        return 2
    return 1


def _social_accounts(
    social_links: list[Any], links: list[dict[str, Any]]
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """HTTP social profile URLs for cross-endpoint joins + other[] leftovers.

    ``socials[]`` keeps the full icon list (including EMAIL_ADDRESS). Email/phone
    stay out of ``socialAccounts`` (use top-level ``email``). Typed icons we
    cannot map to a known key land in ``other[]`` so nothing disappears.
    """
    accounts: dict[str, str] = {}
    ranks: dict[str, int] = {}
    other: list[dict[str, Any]] = []
    typed_rows: list[tuple[str | None, str]] = []
    for item in social_links:
        if not isinstance(item, dict):
            if isinstance(item, str):
                typed_rows.append((None, item))
            continue
        stype = str(item.get("type") or "").upper() or None
        url = str(item.get("url") or "")
        if not url:
            continue
        if stype in ("EMAIL_ADDRESS", "EMAIL", "PHONE") or url.lower().startswith("mailto:"):
            continue
        typed_rows.append((stype, url))
    for link in links:
        for url in _iter_link_urls(link):
            typed_rows.append((None, url))

    seen_other: set[str] = set()
    for stype, url in typed_rows:
        if not url or url.lower().startswith("mailto:"):
            continue
        low = url.lower()
        matched: str | None = None
        if stype in ("WHATSAPP", "WHATS_APP"):
            matched = "whatsapp"
        elif stype in ("WEBSITE", "URL", "LINK"):
            matched = "website"
        else:
            for key, hosts in _SOCIAL_HOSTS:
                if any(h in low for h in hosts):
                    matched = key
                    break
        if matched:
            rank = _youtube_rank(url) if matched == "youtube" else 1
            prev = ranks.get(matched)
            if prev is None or rank < prev:
                accounts[matched] = url
                ranks[matched] = rank
            continue
        if stype and url not in seen_other:
            seen_other.add(url)
            other.append({"type": stype, "url": safe_str(url) or url})
    return accounts, other


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
    for bag_name in ("metadata", "metaData", "context"):
        bag = item.get(bag_name) if isinstance(item.get(bag_name), dict) else {}
        thumb = safe_str(bag.get("thumbnail") or bag.get("image") or bag.get("imageUrl"))
        if thumb:
            return thumb
    return None


def _product_destination(item: dict[str, Any]) -> str | None:
    """Best outbound URL for a PRODUCT row (Linktree often leaves url=\"\")."""
    for key in ("url", "link"):
        u = safe_str(item.get(key))
        if u:
            return u
    for bag_name in ("context", "metaData", "metadata"):
        bag = item.get(bag_name)
        if not isinstance(bag, dict):
            continue
        products = bag.get("products")
        if not isinstance(products, list):
            continue
        shop_urls: list[str] = []
        product_urls: list[str] = []
        for product in products:
            if not isinstance(product, dict):
                continue
            shop = safe_str(product.get("shopUrl"))
            if shop:
                shop_urls.append(shop)
            dest = safe_str(product.get("url") or product.get("cartDeepLinkUrl"))
            if dest:
                product_urls.append(dest)
        if shop_urls:
            # Prefer the storefront (stable join) over empty per-SKU urls.
            return shop_urls[0]
        if product_urls:
            return product_urls[0]
    return None


def _normalize_link(item: dict[str, Any], *, parent_id: str | None = None) -> dict[str, Any]:
    raw_id = item.get("id")
    link_id = (safe_str(raw_id) or str(raw_id)) if raw_id is not None else None
    link_type = safe_str(item.get("type") or item.get("linkType"))
    link: dict[str, Any] = {
        "title": safe_str(item.get("title")),
        "type": link_type,
    }
    if link_id:
        link["id"] = link_id

    link_url = safe_str(item.get("url") or item.get("link"))
    if not link_url and (link_type or "").upper() == "PRODUCT":
        link_url = _product_destination(item)
    # Always emit url on links — null when Linktree exposes no destination
    # (PRODUCT rows often have url:"" but shopUrl on nested products).
    link["url"] = link_url

    thumb = _link_thumbnail(item)
    if thumb:
        link["thumbnail"] = thumb
    if parent_id:
        link["parentId"] = parent_id
    return {k: v for k, v in link.items() if v is not None or k == "url"}


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


def _as_string_id(value: Any) -> str | None:
    if value is None:
        return None
    text = safe_str(value)
    if text:
        return text
    return str(value)


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
    display = _display_name(account, username)
    social_accounts, other = _social_accounts(social_list, normalized_links)

    out: dict[str, Any] = {
        "platform": "linktree",
        "url": safe_str(url),
        "id": _as_string_id(account.get("id")),
        "username": username,
        "handle": username,
        "displayName": display,
        "name": display,  # deprecated alias of displayName
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
        "website": social_accounts.get("website"),
        "linkCount": total_links,
        "links": normalized_links,
        # socials = Linktree icon list (incl. EMAIL_ADDRESS mailto).
        # socialAccounts = HTTP profile URLs for catalog joins (no email).
        # other = typed social icons that did not map into socialAccounts.
        "socials": cleaned_socials,
        "socialAccounts": social_accounts,
        "other": other,
    }
    stamp_profile_core(out, platform="linktree")
    for key in (
        "displayName",
        "name",
        "description",
        "bio",
        "avatar",
        "timezone",
        "verticals",
        "linkPlatforms",
        "email",
        "handle",
        "website",
    ):
        if out.get(key) in (None, "", []):
            out.pop(key, None)
    if not out.get("other"):
        out.pop("other", None)
    return out


async def _resolve_youtube_channel(url: str) -> str:
    """Turn a watch/shorts URL into the creator channel via YouTube oEmbed."""
    if not url:
        return url
    low = url.lower()
    if "/@" in low or "/channel/" in low or "/c/" in low or "/user/" in low:
        return url
    if not _YT_WATCH_RE.search(url) and "youtube.com" not in low and "youtu.be" not in low:
        return url
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
            resp = await client.get(
                "https://www.youtube.com/oembed",
                params={"url": url, "format": "json"},
            )
        if resp.status_code == 200:
            author = safe_str((resp.json() or {}).get("author_url"))
            if author:
                return author
    except (httpx.HTTPError, ValueError, TypeError):
        pass
    return url


async def _enrich_social_accounts(data: dict[str, Any]) -> None:
    accounts = data.get("socialAccounts")
    if not isinstance(accounts, dict):
        return
    yt = accounts.get("youtube")
    if isinstance(yt, str) and yt:
        accounts["youtube"] = await _resolve_youtube_channel(yt)


async def _fetch_page_html(profile: str) -> tuple[str, str]:
    """Return (final_url, html). Prefer direct; Decodo when blocked."""
    headers = {
        **DEFAULT_HEADERS,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://linktr.ee/",
    }
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
        resp = await client.get(profile)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Linktree profile not found")
    if resp.status_code < 400 and "__NEXT_DATA__" in (resp.text or ""):
        return str(resp.url), resp.text

    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(profile, timeout=60.0)
        if got and got[0] == 200 and got[1]:
            body = got[1] if isinstance(got[1], str) else got[1].decode("utf-8", "ignore")
            if "__NEXT_DATA__" in body:
                return profile, body

    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail="Linktree lookup failed")
    raise HTTPException(status_code=404, detail="Linktree profile not found")


@router.get(
    "/page",
    summary="Linktree page",
    description=(
        "Public Linktree page as clean JSON — typed links (incl. PRODUCT destinations), "
        "socials[] + socialAccounts{} for catalog joins, email, verticals. "
        "YouTube watch URLs in socialAccounts are resolved to the channel via oEmbed."
    ),
)
async def linktree_page(
    url: str = Query(..., description="Linktree profile URL or username"),
    cache: bool = Query(
        False,
        description=(
            "Set true to serve from the response cache (default TTL). Default false — always fetch fresh. "
            "Prefer cacheMaxAge when you need 1d–30d freshness control."
        ),
    ),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    profile = _profile_url(url)
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    async with billed_call(
        caller=caller,
        endpoint="/v1/linktree/page",
        platform="linktree",
        resource_url=profile,
        base_credits=CREDIT_PAGE,
    ) as ctx:

        async def _run() -> dict[str, Any]:
            final_url, page_html = await _fetch_page_html(profile)
            data = _normalize(_find_next_data(page_html), final_url, page_html)
            await _enrich_social_accounts(data)
            if not data.get("links") and not data.get("username"):
                raise HTTPException(status_code=404, detail="Linktree profile not found")
            return data

        data = await cached_or_run(
            "linktree.page",
            {"url": profile, "v": 5, "cacheMaxAge": cacheMaxAge},
            _run,
            ctx,
            use_cache=use_cache,
            ttl=ttl,
        )
        return ApiResponse(data=data)
