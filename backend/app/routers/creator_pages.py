"""Small link-in-bio public page endpoints."""

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
from app.services.browser_fetch import _is_cloudflare_block, fetch_html
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_str, strip_empty
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

# Flat credit cost per platform. Komi is a direct JSON API (profile + modules)
# — same class as Linktree (1). Pillar/Linkbio/Linkme still need HTML fetch.
CREDIT_PAGE = {
    "komi": 1,
    "pillar": 4,
    "linkbio": 4,
    "linkme": 4,
}

_KOMI_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Origin": "https://komi.io",
    "Referer": "https://komi.io/",
}

# Komi socialProfileLinks[].type → socials{} key (incl. website).
_KOMI_SOCIAL_TYPES: dict[str, str] = {
    "INSTAGRAM": "instagram",
    "TIKTOK": "tiktok",
    "YOUTUBE": "youtube",
    "TWITTER": "twitter",
    "FACEBOOK": "facebook",
    "SNAPCHAT": "snapchat",
    "SPOTIFY": "spotify",
    "APPLE_MUSIC": "appleMusic",
    "SOUNDCLOUD": "soundcloud",
    "LINKEDIN": "linkedin",
    "TWITCH": "twitch",
    "PINTEREST": "pinterest",
    "THREADS": "threads",
    "DISCORD": "discord",
    "TELEGRAM": "telegram",
    "WHATSAPP": "whatsapp",
    "WEBSITE": "website",
}

# lnk.bio (and similar) sprinkle their own nav/share links through the markup;
# these hosts must be filtered out so we only return the creator's real links.
# Only strip share/nav URLs — keep same-host creator CTAs (pillar.io / link.me
# pages often list outbound destinations on their own domain).
_NAV_HOSTS = (
    "lnk.bio/share",
    "lnk.bio/?ref=",
    "help.lnk.bio",
    "linkinbio.wiki",
    "facebook.com/sharer",
    "wa.me",
    "twitter.com/intent",
    "x.com/intent",
    "line.me/lineit",
    "story.kakao.com/share",
    "reddit.com/submit",
    "linkedin.com/sharing",
    # Recurring lnk.bio footer / partner promos injected on many pages.
    "cruciverba.io",
    "flag.red",
    "petrolprice.sg",
    "istmp.email",
    "mediakit.bio",
    "menoo.me",
)

_LINKBIO_TITLE_SUFFIX = re.compile(
    r"\s*(?:Lnk\.Bio\s*[·•\-]\s*link in bio|-\s*Link in Bio)\s*$",
    re.IGNORECASE,
)
_LINKBIO_DESC_TEMPLATE = re.compile(
    r"Lnk\.Bio|Profile and social media links for",
    re.IGNORECASE,
)

# Detected social-account keys, matched against link URLs (first match wins).
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
    ("discord", ("discord.gg", "discord.com")),
    ("telegram", ("t.me", "telegram.me")),
    ("whatsapp", ("wa.me", "whatsapp.com")),
)

_EMAIL_RE = re.compile(r"mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", re.IGNORECASE)


def _detect_socials(links: list[dict[str, Any]]) -> dict[str, str]:
    """Map link URLs to well-known social platforms (SC-parity `socials` block)."""
    socials: dict[str, str] = {}
    for link in links:
        url = (link.get("url") or "").lower()
        if not url:
            continue
        for key, hosts in _SOCIAL_HOSTS:
            if key not in socials and any(h in url for h in hosts):
                socials[key] = link["url"]
                break
    return socials


def _detect_email(page: str, links: list[dict[str, Any]]) -> str | None:
    match = _EMAIL_RE.search(page or "")
    if match:
        return match.group(1)
    for link in links:
        url = link.get("url") or ""
        m = _EMAIL_RE.search(url)
        if m:
            return m.group(1)
    return None


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


def _link_item(
    url: str,
    *,
    title: str | None = None,
    link_id: str | None = None,
    link_type: str | None = None,
    thumbnail: str | None = None,
) -> dict[str, Any]:
    """Stable link shape: url + title always present (title may be null)."""
    item: dict[str, Any] = {"url": url, "title": safe_str(title)}
    if link_id:
        item["id"] = link_id
    if link_type:
        item["type"] = link_type
    if thumbnail:
        item["thumbnail"] = thumbnail
    return item


def _links(data: dict[str, Any]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    links = []
    for obj in _walk(data):
        raw_url = (
            obj.get("url")
            or obj.get("link")
            or obj.get("href")
            or obj.get("targetUrl")
            or obj.get("destination")
            or obj.get("destinationUrl")
            or obj.get("redirectUrl")
        )
        if not isinstance(raw_url, str):
            continue
        raw_url = raw_url.strip()
        if raw_url.startswith("//"):
            raw_url = "https:" + raw_url
        if not raw_url.startswith("http"):
            continue
        low = raw_url.lower()
        if any(nav in low for nav in _NAV_HOSTS):
            continue
        if raw_url in seen:
            continue
        seen.add(raw_url)
        url = safe_str(raw_url)
        if not url:
            continue
        links.append(
            _link_item(
                url,
                title=safe_str(obj.get("title") or obj.get("name") or obj.get("label") or obj.get("text")),
                link_id=safe_str(obj.get("id") or obj.get("_id")),
                link_type=safe_str(obj.get("type") or obj.get("kind")),
                thumbnail=safe_str(obj.get("thumbnail") or obj.get("image") or obj.get("imageUrl")),
            )
        )
    return links[:200]


def _is_platform_noise_link(url: str, page_url: str | None = None) -> bool:
    """Drop lnk.bio chrome (home, self profile, ref) and known footer promos."""
    low = (url or "").lower()
    if any(nav in low for nav in _NAV_HOSTS):
        return True
    if re.match(r"^https?://(www\.)?lnk\.bio/?$", low):
        return True
    if page_url:
        base = page_url.rstrip("/").lower()
        if low.rstrip("/") == base:
            return True
    return False


def _anchor_links(page: str, page_url: str | None = None) -> list[dict[str, Any]]:
    """Fallback link extraction for server-rendered pages (e.g. lnk.bio) that
    don't ship a hydration blob. Pulls outbound <a href> targets, drops the
    platform's own nav/share links, and de-dupes."""
    seen: set[str] = set()
    links: list[dict[str, Any]] = []
    for match in re.finditer(r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', page, flags=re.IGNORECASE | re.DOTALL):
        href = html.unescape(match.group(1)).strip()
        if _is_platform_noise_link(href, page_url):
            continue
        if href in seen:
            continue
        seen.add(href)
        text = re.sub(r"<[^>]+>", " ", match.group(2))
        text = re.sub(r"\s+", " ", html.unescape(text)).strip()
        url = safe_str(href)
        if not url:
            continue
        links.append(_link_item(url, title=safe_str(text)))
    return links[:200]


def _strip_page(data: dict[str, Any]) -> dict[str, Any]:
    """strip_empty, but keep links[].title even when null for a stable schema."""
    links = data.get("links")
    cleaned = strip_empty({k: v for k, v in data.items() if k != "links"})
    if isinstance(links, list):
        cleaned["links"] = [
            _link_item(
                url,
                title=link.get("title"),
                link_id=link.get("id"),
                link_type=link.get("type"),
                thumbnail=link.get("thumbnail"),
            )
            for link in links
            if isinstance(link, dict) and (url := safe_str(link.get("url")))
        ]
        cleaned["linkCount"] = len(cleaned["links"])
    return cleaned


def _first_string(data: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for obj in _walk(data):
        for key in keys:
            value = obj.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _komi_username(value: str) -> str:
    """Accept komi.io/user, user.komi.io, or bare username."""
    raw = (value or "").strip().rstrip("/")
    if "://" in raw:
        host = raw.split("://", 1)[1].split("/", 1)[0].lower()
        if host.endswith(".komi.io") and host != "www.komi.io" and host != "api.komi.io":
            return host[: -len(".komi.io")].split(".")[0]
        return raw.rsplit("/", 1)[-1].lstrip("@")
    return raw.lstrip("@")


def _komi_socials(profile: dict[str, Any], data: dict[str, Any]) -> dict[str, str]:
    """Map Komi socialProfileLinks (+ website field) into socials{}."""
    socials: dict[str, str] = {}
    for link in profile.get("socialProfileLinks") or []:
        if not isinstance(link, dict):
            continue
        url = safe_str(link.get("link") or link.get("url"))
        if not url:
            continue
        key = _KOMI_SOCIAL_TYPES.get((safe_str(link.get("type")) or "").upper())
        if not key:
            # Unknown type — fall back to host detection (still skip if neither).
            detected = _detect_socials([{"url": url}])
            if detected:
                key = next(iter(detected))
                url = detected[key]
            else:
                continue
        if key not in socials:
            socials[key] = url
    for candidate in (profile.get("website"), data.get("website")):
        if isinstance(candidate, dict):
            url = safe_str(candidate.get("url") or candidate.get("link"))
        else:
            url = safe_str(candidate)
        if url and "website" not in socials:
            socials["website"] = url
            break
    return socials


def _komi_flatten_module_links(modules: list[Any]) -> list[dict[str, Any]]:
    """Flatten talent-profiles modules into SC-shaped LINK/PRODUCT rows.

    Komi nests content under GROUP → LINK|PRODUCT modules → items[{url,title,…}].
    Social icon rows live on socialProfileLinks and are NOT duplicated here.
    """
    out: list[dict[str, Any]] = []

    def walk(mod: dict[str, Any]) -> None:
        items = mod.get("items")
        if not isinstance(items, list) or not items:
            return
        first = items[0]
        # Leaf rows: items already carry outbound urls (LINK / PRODUCT / …).
        if isinstance(first, dict) and ("url" in first or "link" in first):
            mod_type = (safe_str(mod.get("type")) or "LINK").upper()
            for item in items:
                if not isinstance(item, dict):
                    continue
                url = safe_str(item.get("url") or item.get("link"))
                if not url:
                    continue
                title = safe_str(item.get("title") or item.get("name") or mod.get("name"))
                row: dict[str, Any] = {
                    "id": safe_str(item.get("id")),
                    "url": url,
                    "title": title,
                    "type": mod_type,
                }
                if isinstance(item.get("order"), int):
                    row["order"] = item["order"]
                if isinstance(item.get("visible"), bool):
                    row["visible"] = item["visible"]
                thumb = safe_str(item.get("thumbnail") or item.get("image"))
                if thumb:
                    row["thumbnail"] = thumb
                module_id = safe_str(item.get("moduleId") or mod.get("id"))
                if module_id:
                    row["moduleId"] = module_id
                version_id = safe_str(item.get("versionId"))
                if version_id:
                    row["versionId"] = version_id
                if item.get("price") is not None:
                    row["price"] = item.get("price")
                currency = safe_str(item.get("currency"))
                if currency:
                    row["currency"] = currency
                out.append(row)
            return
        # Nested modules (GROUP children, etc.).
        for child in items:
            if isinstance(child, dict) and (child.get("type") or child.get("items") is not None):
                walk(child)

    for mod in modules:
        if isinstance(mod, dict):
            walk(mod)
    return out


async def _fetch_komi(value: str) -> dict[str, Any] | None:
    """Komi HTML is a client-rendered shell; public JSON APIs hold the page.

    1) GET /api/talent/usernames/{username} — identity + socialProfileLinks
    2) GET /api/talent-profiles/{id}/modules — LINK/PRODUCT content (SKIMS, etc.)
    """
    username = _komi_username(value)
    if not username:
        return None
    async with httpx.AsyncClient(timeout=30, headers=_KOMI_HEADERS) as client:
        resp = await client.get(f"https://api.komi.io/api/talent/usernames/{username}")
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, dict):
            return None
        profile = data.get("talentProfile") if isinstance(data.get("talentProfile"), dict) else {}
        profile_id = safe_str(profile.get("id"))
        modules: list[Any] = []
        if profile_id:
            mod_resp = await client.get(
                f"https://api.komi.io/api/talent-profiles/{profile_id}/modules"
            )
            if mod_resp.status_code == 200:
                payload = mod_resp.json()
                if isinstance(payload, list):
                    modules = payload

    links = _komi_flatten_module_links(modules)
    socials = _komi_socials(profile, data)
    display = (
        safe_str(profile.get("displayName"))
        or safe_str(data.get("displayName"))
        or safe_str(data.get("username") or username)
    )
    # Keep empty bio as "" (SC always emits the field).
    bio_raw = profile.get("bio")
    if bio_raw is None:
        bio_raw = data.get("bio")
    bio = "" if bio_raw is None else (safe_str(bio_raw) or "")
    handle = safe_str(data.get("username") or username)
    page = {
        "platform": "komi",
        "id": profile_id,
        "url": f"https://komi.io/{handle or username}",
        "username": handle,
        "handle": handle,
        "displayName": display,
        "name": display,  # deprecated alias of displayName
        "firstName": safe_str(data.get("firstName") or profile.get("firstName")),
        "lastName": safe_str(data.get("lastName") or profile.get("lastName")),
        "bio": bio,
        "description": bio,  # deprecated alias of bio
        "avatar": safe_str(data.get("avatar") or profile.get("avatar")),
        "linkCount": len(links),
        "links": links,
        "socials": socials,
        "email": safe_str(data.get("email") or profile.get("email")),
    }
    # strip_empty drops "" — re-attach bio/description for SC-stable empty string.
    cleaned = strip_empty({k: v for k, v in page.items() if k not in ("bio", "description", "links")})
    cleaned["bio"] = bio
    cleaned["description"] = bio
    cleaned["links"] = links
    cleaned["linkCount"] = len(links)
    return cleaned


async def _fetch_page(platform: str, value: str) -> dict[str, Any]:
    if platform == "komi":
        komi = await _fetch_komi(value)
        if komi:
            return komi
    profile = _url(platform, value)
    # lnk.bio (and occasionally peers) sit behind Cloudflare bot checks that
    # reject plain httpx — browser_fetch uses Chrome TLS impersonation first.
    try:
        resp = await fetch_html(profile, timeout=30.0, prefer_impersonate=True)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"{platform.title()} lookup failed") from exc
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail=f"{platform.title()} page not found")
    if resp.status_code >= 400 or _is_cloudflare_block(resp.status_code, resp.text):
        raise HTTPException(status_code=502, detail=f"{platform.title()} lookup failed")
    page = resp.text
    page_url = resp.url
    data = _next_data(page)
    links = _links(data)
    if not links:
        links = _anchor_links(page, page_url=page_url)
    links = [link for link in links if not _is_platform_noise_link(link.get("url") or "", page_url)]
    title = _meta(page, "og:title") or _meta(page, "twitter:title") or _first_string(data, ("displayName", "name", "title", "username"))
    description = _meta(page, "og:description") or _meta(page, "description") or _first_string(data, ("bio", "description", "subtitle"))
    avatar = _meta(page, "og:image") or _meta(page, "twitter:image") or _first_string(data, ("avatar", "avatarUrl", "profilePicture", "imageUrl"))
    username = _first_string(data, ("username", "handle", "slug")) or page_url.rstrip("/").rsplit("/", 1)[-1]
    # Marketing / soft-404 shells often keep the path username but have no creator links
    # and use the product's own OG title (e.g. "Pillar - The All-In-One Toolkit…").
    name = safe_str(title)
    if platform == "linkbio" and name:
        name = _LINKBIO_TITLE_SUFFIX.sub("", name).strip() or None
    if platform == "linkbio" and description and _LINKBIO_DESC_TEMPLATE.search(description):
        # Auto-generated OG blurb, not a creator bio.
        description = None
    # Recycled / mismatched lnk.bio handles (e.g. /nasa serving another creator).
    path_user = (username or "").lstrip("@").lower()
    og_handle = None
    if name:
        m = re.search(r"@([\w.]+)", name)
        if m:
            og_handle = m.group(1).lower()
    mismatched = (
        platform == "linkbio"
        and bool(path_user)
        and (
            (og_handle and og_handle != path_user and path_user not in (name or "").lower())
            or (isinstance(name, str) and name.lower() in {"not found - lnk.bio", "not found"})
        )
    )
    marketing_shell = mismatched or (
        not links
        and isinstance(name, str)
        and (
            name.lower().startswith(f"{platform} -")
            or name.lower().startswith(f"{platform}:")
            or f"{platform} - the" in name.lower()
            or name.lower() in {platform, f"{platform}.io", f"{platform}.me", "lnk.bio"}
        )
    )
    # Default avatar SVG is not a real profile photo.
    if platform == "linkbio" and avatar and "avatar.svg" in avatar.lower():
        avatar = None
    return _strip_page(
        {
            "platform": platform,
            "url": safe_str(page_url),
            "username": None if marketing_shell else safe_str(username),
            "name": None if marketing_shell else name,
            "firstName": _first_string(data, ("firstName", "first_name")),
            "lastName": _first_string(data, ("lastName", "last_name")),
            "description": None if marketing_shell else safe_str(description),
            "avatar": None if marketing_shell else safe_str(avatar),
            "linkCount": len(links),
            "links": links,
            "socials": _detect_socials(links),
            "email": _detect_email(page, links),
            "_marketingShell": True if marketing_shell else None,
        }
    )


async def _page(
    platform: str,
    url: str,
    caller: ApiCaller,
    *,
    use_cache: bool = True,
    ttl: int | None = None,
    cache_max_age: str | None = None,
):
    detected = detect_url_platform(url)
    if detected and detected != platform:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, platform, EXAMPLES[platform]),
        )
    profile = _url(platform, url)
    credits = CREDIT_PAGE.get(platform, 4)
    async with billed_call(
        caller=caller,
        endpoint=f"/v1/{platform}/{'profile' if platform == 'linkme' else 'page'}",
        platform=platform,
        resource_url=profile,
        base_credits=credits,
    ) as ctx:
        data = await cached_or_run(
            f"{platform}.page",
            {"url": profile, "v": 10, "cacheMaxAge": cache_max_age},
            lambda: _fetch_page(platform, profile),
            ctx,
            use_cache=use_cache,
            ttl=ttl,
        )
        if data.pop("_marketingShell", None) or not (data.get("username") or data.get("links")):
            raise HTTPException(status_code=404, detail=f"{platform.title()} page not found")
        # Pillar soft-404s to a marketing shell with the path username but no creator links.
        if platform == "pillar" and not data.get("links"):
            raise HTTPException(status_code=404, detail="Pillar page not found or has no public links")
        return ApiResponse(data=data)


_CACHE_DESC = (
    "Set true to serve from the response cache (default TTL). Default false — always fetch fresh. "
    "Prefer cacheMaxAge when you need 1d–30d freshness control."
)


@router.get(
    "/komi/page",
    summary="Komi page",
    description=(
        "Public Komi page as clean JSON — identity (id, displayName, bio), socials{} "
        "(incl. website), and content links[] with id/thumbnail/order/visible plus "
        "price/currency on PRODUCT rows. Flat 1 credit (direct Komi JSON APIs)."
    ),
)
async def komi_page(
    url: str = Query(..., description="Komi page URL or username (komi.io/user or user.komi.io)"),
    cache: bool = Query(False, description=_CACHE_DESC),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    return await _page(
        "komi", url, caller, use_cache=use_cache, ttl=ttl, cache_max_age=cacheMaxAge
    )


@router.get("/pillar/page", summary="Pillar page")
async def pillar_page(url: str = Query(..., description="Pillar page URL or username"), cache: bool = Query(False, description=_CACHE_DESC), caller: ApiCaller = Depends(require_api_key)):
    return await _page("pillar", url, caller, use_cache=cache)


@router.get("/linkbio/page", summary="Linkbio page")
async def linkbio_page(url: str = Query(..., description="Linkbio (lnk.bio) page URL or username"), cache: bool = Query(False, description=_CACHE_DESC), caller: ApiCaller = Depends(require_api_key)):
    return await _page("linkbio", url, caller, use_cache=cache)


@router.get("/linkme/profile", summary="Linkme profile")
async def linkme_profile(url: str = Query(..., description="Linkme profile URL or username"), cache: bool = Query(False, description=_CACHE_DESC), caller: ApiCaller = Depends(require_api_key)):
    return await _page("linkme", url, caller, use_cache=cache)
