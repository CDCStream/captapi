"""Small link-in-bio public page endpoints."""

from __future__ import annotations

import html
import json
import re
import time
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
    "linkme": "https://link.me/danucd",
}

# Flat credit cost per platform. Link-in-bio JSON/HTML scrapes that return a
# full page are 1 credit (SC parity). Linkme still needs heavier HTML work.
CREDIT_PAGE = {
    "komi": 1,
    "pillar": 1,
    "linkbio": 1,
    "linkme": 1,
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

_PILLAR_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
_PILLAR_CLOUDINARY_CLOUD = "pillario"
# Public registration-role JWT is baked into Pillar's frontend bundle; refresh
# from the vendors chunk when stale.
_PILLAR_GQL_CACHE: dict[str, Any] = {"endpoint": None, "token": None, "fetched_at": 0.0}
_PILLAR_GQL_TTL_SEC = 6 * 3600

_PILLAR_SOCIAL_CHANNELS: dict[str, str] = {
    "INSTAGRAM": "instagram",
    "TIKTOK": "tiktok",
    "YOUTUBE": "youtube",
    "TWITTER": "twitter",
    "FACEBOOK": "facebook",
    "SNAPCHAT": "snapchat",
    "SPOTIFY": "spotify",
    "SOUNDCLOUD": "soundcloud",
    "LINKEDIN": "linkedin",
    "TWITCH": "twitch",
    "DISCORD": "discord",
    "PATREON": "patreon",
    "MEDIUM": "medium",
    "AMAZON": "amazon",
    "APPLE_APP_STORE": "appleAppStore",
    "GOOGLE_APP_STORE": "googleAppStore",
    "PINTEREST": "pinterest",
    "THREADS": "threads",
    "TELEGRAM": "telegram",
    "WHATSAPP": "whatsapp",
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
    # Linkme site chrome — never treat as creator links.
    "about.link.me",
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
    ("whatsapp", ("wa.me", "api.whatsapp.com", "whatsapp.com")),
    ("triller", ("triller.co",)),
)

# lnk.bio data-network → socials{} key (email stays top-level only).
_LINKBIO_NETWORKS: dict[str, str] = {
    "SOCIAL_FB": "facebook",
    "SOCIAL_TW": "twitter",
    "SOCIAL_IG": "instagram",
    "SOCIAL_TK": "tiktok",
    "SOCIAL_YT": "youtube",
    "SOCIAL_TRILLER": "triller",
    "CONTACT_SN": "snapchat",
    "SOCIAL_SN": "snapchat",
    "SOCIAL_WA": "whatsapp",
    "CONTACT_WA": "whatsapp",
    "SOCIAL_WHATSAPP": "whatsapp",
    "CONTACT_WHATSAPP": "whatsapp",
    "SOCIAL_EMAIL": "email",
    "CONTACT_EMAIL": "email",
    "SOCIAL_WEB": "website",
    "CONTACT_WEB": "website",
    "SOCIAL_SPOTIFY": "spotify",
    "SOCIAL_SOUNDCLOUD": "soundcloud",
    "SOCIAL_LINKEDIN": "linkedin",
    "SOCIAL_TWITCH": "twitch",
    "SOCIAL_PINTEREST": "pinterest",
    "SOCIAL_THREADS": "threads",
    "SOCIAL_DISCORD": "discord",
    "SOCIAL_TELEGRAM": "telegram",
}

_EMAIL_RE = re.compile(r"mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", re.IGNORECASE)


def _social_key_for_url(url: str) -> str | None:
    low = (url or "").lower()
    if not low:
        return None
    for key, hosts in _SOCIAL_HOSTS:
        if any(h in low for h in hosts):
            return key
    return None


def _partition_socials(
    candidates: list[dict[str, Any]],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Split social candidates into socials{} + other[] (nothing silently dropped).

    ``other[]`` holds typed/URL rows we could not map to a known socials key
    (e.g. niche networks). Email candidates are skipped — callers set top-level email.
    """
    socials: dict[str, str] = {}
    other: list[dict[str, Any]] = []
    for link in candidates:
        if not isinstance(link, dict):
            continue
        url = safe_str(link.get("url"))
        if not url:
            continue
        key = safe_str(link.get("socialKey")) or _social_key_for_url(url)
        type_hint = safe_str(link.get("type"))
        if not key and type_hint:
            key = _LINKBIO_NETWORKS.get(type_hint.upper())
        if key == "email" or url.lower().startswith("mailto:"):
            continue
        if key:
            if key not in socials:
                socials[key] = url
            continue
        row: dict[str, Any] = {"url": url}
        title = safe_str(link.get("title"))
        if title:
            row["title"] = title
        if type_hint:
            row["type"] = type_hint
        other.append(row)
    return socials, other


def _detect_socials(links: list[dict[str, Any]]) -> dict[str, str]:
    """Map link URLs to well-known social platforms (SC-parity `socials` block)."""
    socials, _other = _partition_socials(links)
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


def _anchor_label(attrs: str, inner: str) -> str | None:
    """Visible text, else title/aria-label on the <a> or a child icon."""
    text = re.sub(r"<[^>]+>", " ", inner or "")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    if text:
        return text
    for attr in ("title", "aria-label"):
        m = re.search(rf'\b{attr}=["\']([^"\']+)["\']', attrs or "", flags=re.IGNORECASE)
        if m:
            val = html.unescape(m.group(1)).strip()
            if val and val.lower() not in {"lnk", "link"}:
                return val
    m = re.search(r'<i[^>]+title=["\']([^"\']+)["\']', inner or "", flags=re.IGNORECASE)
    if m:
        val = html.unescape(m.group(1)).strip()
        if val:
            return val
    return None


def _anchor_links(page: str, page_url: str | None = None) -> list[dict[str, Any]]:
    """Fallback link extraction for server-rendered pages (e.g. lnk.bio) that
    don't ship a hydration blob. Pulls outbound <a href> targets, drops the
    platform's own nav/share links, and de-dupes."""
    seen: set[str] = set()
    links: list[dict[str, Any]] = []
    for match in re.finditer(
        r'<a\s([^>]*\bhref=["\'](https?://[^"\']+)["\'][^>]*)>(.*?)</a>',
        page,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        attrs, href_raw, inner = match.group(1), match.group(2), match.group(3)
        href = html.unescape(href_raw).strip()
        if _is_platform_noise_link(href, page_url):
            continue
        if href in seen:
            continue
        seen.add(href)
        url = safe_str(href)
        if not url:
            continue
        links.append(_link_item(url, title=safe_str(_anchor_label(attrs, inner))))
    return links[:200]


def _strip_page(data: dict[str, Any]) -> dict[str, Any]:
    """strip_empty, but keep links[].title even when null for a stable schema."""
    links = data.get("links")
    other = data.get("other")
    cleaned = strip_empty({k: v for k, v in data.items() if k not in ("links", "other")})
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
    if isinstance(other, list):
        cleaned["other"] = other
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


def _komi_socials(
    profile: dict[str, Any], data: dict[str, Any]
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Map Komi socialProfileLinks (+ website field) into socials{} + other[]."""
    candidates: list[dict[str, Any]] = []
    for link in profile.get("socialProfileLinks") or []:
        if not isinstance(link, dict):
            continue
        url = safe_str(link.get("link") or link.get("url"))
        if not url:
            continue
        type_hint = (safe_str(link.get("type")) or "").upper()
        key = _KOMI_SOCIAL_TYPES.get(type_hint) or _social_key_for_url(url)
        candidates.append(
            {
                "url": url,
                "type": type_hint or None,
                "socialKey": key,
                "title": safe_str(link.get("title") or link.get("label")),
            }
        )
    for candidate in (profile.get("website"), data.get("website")):
        if isinstance(candidate, dict):
            url = safe_str(candidate.get("url") or candidate.get("link"))
        else:
            url = safe_str(candidate)
        if url:
            candidates.append({"url": url, "socialKey": "website", "type": "WEBSITE"})
            break
    return _partition_socials(candidates)


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
    socials, other = _komi_socials(profile, data)
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
        "other": other,
        "email": safe_str(data.get("email") or profile.get("email")),
        "website": socials.get("website"),
    }
    # strip_empty drops "" — re-attach bio/description for SC-stable empty string.
    cleaned = strip_empty(
        {k: v for k, v in page.items() if k not in ("bio", "description", "links", "other")}
    )
    cleaned["bio"] = bio
    cleaned["description"] = bio
    cleaned["links"] = links
    cleaned["linkCount"] = len(links)
    cleaned["other"] = other
    return cleaned


def _pillar_username(value: str) -> str:
    """Accept pillar.io/user or bare username."""
    raw = (value or "").strip().rstrip("/")
    if "://" in raw:
        return raw.rsplit("/", 1)[-1].lstrip("@")
    return raw.lstrip("@")


def _pillar_cloudinary_url(value: str | None) -> str | None:
    """Resolve Pillar's cloudinary:public_id tokens to res.cloudinary.com URLs."""
    raw = safe_str(value)
    if not raw:
        return None
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if raw.startswith("cloudinary:"):
        public_id = raw[len("cloudinary:") :].lstrip("/")
        if not public_id:
            return None
        return f"https://res.cloudinary.com/{_PILLAR_CLOUDINARY_CLOUD}/image/upload/{public_id}"
    return raw


def _pillar_link_type(title: str | None, url: str | None) -> str | None:
    """SC uses lowercase title as type; prefer a host social key when obvious."""
    if url:
        detected = _detect_socials([{"url": url}])
        if detected:
            return next(iter(detected))
    if title:
        return title.strip().lower() or None
    return None


def _pillar_socials(
    banner_customizations: dict[str, Any] | None,
    influencer_socials: list[Any] | None,
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Merge banner.customizations.socials + influencer.socials → socials{} + other[]."""
    candidates: list[dict[str, Any]] = []
    custom = banner_customizations if isinstance(banner_customizations, dict) else {}
    custom_socials = custom.get("socials") if isinstance(custom.get("socials"), dict) else {}
    for channel, payload in custom_socials.items():
        channel_u = str(channel).upper()
        if isinstance(payload, dict):
            url = safe_str(payload.get("value") or payload.get("url"))
        else:
            url = safe_str(payload)
        if not url:
            continue
        candidates.append(
            {
                "url": url,
                "type": channel_u,
                "socialKey": _PILLAR_SOCIAL_CHANNELS.get(channel_u) or _social_key_for_url(url),
            }
        )
    for row in influencer_socials or []:
        if not isinstance(row, dict):
            continue
        channel_u = (safe_str(row.get("channel")) or "").upper()
        url = safe_str(row.get("url"))
        if not url:
            continue
        candidates.append(
            {
                "url": url,
                "type": channel_u or None,
                "socialKey": _PILLAR_SOCIAL_CHANNELS.get(channel_u) or _social_key_for_url(url),
            }
        )
    return _partition_socials(candidates)


def _pillar_map_links(raw_links: list[Any] | None) -> list[dict[str, Any]]:
    """Map shop_custom_link rows → links[{id,type,title,url,clicks,order}]."""
    out: list[dict[str, Any]] = []
    for row in raw_links or []:
        if not isinstance(row, dict):
            continue
        status = (safe_str(row.get("status")) or "").upper()
        if status == "DELETED":
            continue
        data = row.get("data") if isinstance(row.get("data"), dict) else {}
        url = safe_str(data.get("url"))
        if not url:
            continue
        # Platform self-promo / referral chrome — not creator content.
        if "pillar.io/referral" in url.lower():
            continue
        if data.get("visible") is False:
            continue
        title = safe_str(data.get("tagline") or data.get("title") or data.get("cta"))
        link: dict[str, Any] = {
            "id": safe_str(row.get("link_id")),
            "type": _pillar_link_type(title, url),
            "title": title,
            "url": url,
            "clicks": int(row["clicks"]) if isinstance(row.get("clicks"), int) else 0,
            "order": row.get("order") if isinstance(row.get("order"), int) else None,
        }
        thumb = _pillar_cloudinary_url(safe_str(data.get("thumbnail_image")))
        if thumb:
            link["thumbnail"] = thumb
        desc = safe_str(data.get("description"))
        if desc:
            link["description"] = desc
        out.append(link)
    # Stable sort: explicit order first, then nulls (SC keeps null order).
    out.sort(key=lambda x: (x.get("order") is None, x.get("order") if isinstance(x.get("order"), int) else 0))
    return out


def _pillar_map_products(raw_products: list[Any] | None) -> list[dict[str, Any]]:
    """Map shop_featured_product → products[{id,title,name,price,url,description,image}]."""
    out: list[dict[str, Any]] = []
    for row in raw_products or []:
        if not isinstance(row, dict):
            continue
        status = (safe_str(row.get("status")) or "").upper()
        if status == "DELETED":
            continue
        title = safe_str(row.get("name") or row.get("title"))
        url = safe_str(row.get("url"))
        if not title and not url:
            continue
        product: dict[str, Any] = {
            "id": safe_str(row.get("product_id") or row.get("id")),
            "title": title,
            "name": title,
            "url": url,
            "description": safe_str(row.get("description")),
            "image": safe_str(row.get("image")),
        }
        if row.get("price") is not None:
            product["price"] = row.get("price")
        if isinstance(row.get("order"), int):
            product["order"] = row["order"]
        if isinstance(row.get("show_price"), bool):
            product["showPrice"] = row["show_price"]
        out.append(product)
    return out


def _pillar_map_page(payload: dict[str, Any], *, page_key: str) -> dict[str, Any] | None:
    """Turn a Pillar GraphQL page payload into Captapi JSON."""
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    if not isinstance(data, dict):
        return None
    influencer = data.get("influencer") if isinstance(data.get("influencer"), dict) else None
    if not influencer:
        return None
    banner = data.get("banner") if isinstance(data.get("banner"), dict) else {}
    user = influencer.get("user") if isinstance(influencer.get("user"), dict) else {}
    custom = banner.get("customizations") if isinstance(banner.get("customizations"), dict) else {}

    username = (
        safe_str(banner.get("url_key"))
        or safe_str(page_key)
        or safe_str(influencer.get("alias"))
    )
    if not username:
        return None

    display = (
        safe_str(custom.get("user_alias"))
        or safe_str(user.get("full_name"))
        or " ".join(
            p for p in (safe_str(user.get("first_name")), safe_str(user.get("last_name"))) if p
        ).strip()
        or username
    )
    bio_raw = user.get("bio")
    bio = "" if bio_raw is None else (safe_str(bio_raw) or "")

    email = None
    email_social = custom.get("socials") if isinstance(custom.get("socials"), dict) else {}
    email_payload = email_social.get("EMAIL")
    if isinstance(email_payload, dict):
        email = safe_str(email_payload.get("value"))
    email = email or safe_str(user.get("email")) or safe_str(influencer.get("contact_email"))

    links = _pillar_map_links(data.get("links") if isinstance(data.get("links"), list) else [])
    products = _pillar_map_products(
        data.get("products") if isinstance(data.get("products"), list) else []
    )
    socials, other = _pillar_socials(
        custom, influencer.get("socials") if isinstance(influencer.get("socials"), list) else []
    )

    page = {
        "platform": "pillar",
        "id": safe_str(influencer.get("id")),
        "url": f"https://pillar.io/{username}",
        "username": username,
        "handle": username,
        "displayName": display,
        "name": display,  # deprecated alias of displayName
        "firstName": safe_str(user.get("first_name")),
        "lastName": safe_str(user.get("last_name")),
        "bio": bio,
        "description": bio,  # deprecated alias of bio
        "avatar": _pillar_cloudinary_url(safe_str(user.get("profile_image"))),
        "location": safe_str(custom.get("location")),
        "email": email,
        "linkCount": len(links),
        "links": links,
        "products": products,
        "socials": socials,
        "other": other,
    }
    cleaned = strip_empty(
        {
            k: v
            for k, v in page.items()
            if k not in ("bio", "description", "links", "products", "other")
        }
    )
    cleaned["bio"] = bio
    cleaned["description"] = bio
    cleaned["links"] = links
    cleaned["linkCount"] = len(links)
    cleaned["products"] = products
    cleaned["other"] = other
    return cleaned


async def _pillar_graphql_creds(*, page_url: str | None = None) -> tuple[str, str]:
    """Load Pillar Hasura endpoint + public JWT from the creator SPA bundle.

    The marketing homepage (pillar.io/) does not ship the Vue vendors chunk —
    any creator path (or /login) does.
    """
    now = time.time()
    cached_ep = _PILLAR_GQL_CACHE.get("endpoint")
    cached_tok = _PILLAR_GQL_CACHE.get("token")
    fetched_at = float(_PILLAR_GQL_CACHE.get("fetched_at") or 0)
    if (
        isinstance(cached_ep, str)
        and isinstance(cached_tok, str)
        and cached_ep
        and cached_tok
        and now - fetched_at < _PILLAR_GQL_TTL_SEC
    ):
        return cached_ep, cached_tok

    boot_url = page_url or "https://pillar.io/login"
    resp = await fetch_html(boot_url, timeout=30.0, prefer_impersonate=True)
    endpoint: str | None = None
    token: str | None = None
    async with httpx.AsyncClient(
        timeout=30,
        headers={"User-Agent": _PILLAR_UA, "Referer": "https://pillar.io/"},
        follow_redirects=True,
    ) as client:
        # Prefer the s-z vendors chunk (holds env constants); fall back to any vendors.
        srcs = re.findall(r'src="(/js/chunk-vendors[^"]+\.js)"', resp.text)
        ordered = sorted(srcs, key=lambda s: (0 if "s-z" in s else 1, s))
        for src in ordered:
            js = (await client.get(f"https://pillar.io{src}")).text
            if "VUE_APP_GRAPHQL_TOKEN" not in js:
                continue
            ep_m = re.search(r'VUE_APP_GRAPHQL_ENDPOINT:"([^"]+)"', js)
            tok_m = re.search(r'VUE_APP_GRAPHQL_TOKEN:"([^"]+)"', js)
            if ep_m and tok_m:
                host = ep_m.group(1).strip()
                endpoint = host if host.startswith("http") else f"https://{host}/v1/graphql"
                if not endpoint.endswith("/v1/graphql"):
                    endpoint = endpoint.rstrip("/") + "/v1/graphql"
                token = tok_m.group(1).strip()
                break
    if not endpoint or not token:
        # Fall back to last good creds if refresh failed mid-flight.
        if isinstance(cached_ep, str) and isinstance(cached_tok, str) and cached_ep and cached_tok:
            return cached_ep, cached_tok
        raise HTTPException(status_code=502, detail="Pillar GraphQL credentials unavailable")
    _PILLAR_GQL_CACHE["endpoint"] = endpoint
    _PILLAR_GQL_CACHE["token"] = token
    _PILLAR_GQL_CACHE["fetched_at"] = now
    return endpoint, token


async def _fetch_pillar(value: str) -> dict[str, Any] | None:
    """Pillar HTML is a Vue SPA; public Hasura GraphQL holds the page.

    Resolve slug via shop_banner.url_key / alias / builder slug, then load
    influencer + custom links (with clicks) + featured products + socials.
    """
    username = _pillar_username(value)
    if not username:
        return None
    page_url = f"https://pillar.io/{username}"
    endpoint, token = await _pillar_graphql_creds(page_url=page_url)
    headers = {
        "User-Agent": _PILLAR_UA,
        "Content-Type": "application/json",
        "Origin": "https://pillar.io",
        "Referer": page_url,
        "Authorization": f"Bearer {token}",
    }
    resolve_q = """
    query($key: String!) {
      byBanner: shop_banner(where: {url_key: {_ilike: $key}}, limit: 3) {
        influencer_id url_key
      }
      bySlug: shop_builder_item_url_slug(where: {slug: {_ilike: $key}}, limit: 3) {
        slug influencer_id
      }
      byAlias: users_influencer(where: {alias: {_ilike: $key}}, limit: 3) {
        id alias
      }
    }
    """
    page_q = """
    query($id: uuid!) {
      influencer: users_influencer_by_pk(id: $id) {
        id alias contact_email
        socials { channel handle url channel_name primary_connection }
        user {
          id first_name last_name full_name email bio profile_image title verified
        }
      }
      banner: shop_banner_by_pk(influencer_id: $id) {
        url_key clicks customizations
      }
      links: shop_custom_link(
        where: {influencer_id: {_eq: $id}}
        order_by: {order: asc_nulls_last}
      ) {
        link_id order clicks status data
      }
      products: shop_featured_product(
        where: {influencer_id: {_eq: $id}, status: {_neq: "DELETED"}}
        order_by: {order: asc_nulls_last}
      ) {
        product_id name description price url image order show_price brand_name brand_url status
      }
    }
    """
    async with httpx.AsyncClient(timeout=45, headers=headers) as client:
        resolved = await client.post(
            endpoint, json={"query": resolve_q, "variables": {"key": username}}
        )
        if resolved.status_code != 200:
            return None
        try:
            resolve_body = resolved.json()
        except json.JSONDecodeError:
            return None
        bags = resolve_body.get("data") if isinstance(resolve_body.get("data"), dict) else {}
        influencer_id: str | None = None
        page_key = username
        for bag_name in ("byBanner", "bySlug", "byAlias"):
            rows = bags.get(bag_name) if isinstance(bags, dict) else None
            if not isinstance(rows, list) or not rows:
                continue
            row = rows[0]
            if not isinstance(row, dict):
                continue
            influencer_id = safe_str(row.get("influencer_id") or row.get("id"))
            page_key = safe_str(row.get("url_key") or row.get("slug") or username) or username
            if influencer_id:
                break
        if not influencer_id:
            return None
        page_resp = await client.post(
            endpoint, json={"query": page_q, "variables": {"id": influencer_id}}
        )
        if page_resp.status_code != 200:
            return None
        try:
            page_body = page_resp.json()
        except json.JSONDecodeError:
            return None
        if page_body.get("errors"):
            return None
        return _pillar_map_page(page_body, page_key=page_key)


def _linkbio_username(value: str) -> str:
    raw = (value or "").strip().rstrip("/")
    if "://" in raw:
        return raw.rsplit("/", 1)[-1].lstrip("@")
    return raw.lstrip("@")


def _linkbio_network_title(network: str | None, fallback: str | None) -> str | None:
    if fallback:
        return fallback
    key = _LINKBIO_NETWORKS.get((network or "").upper())
    if not key:
        return None
    labels = {
        "facebook": "Facebook",
        "twitter": "Twitter",
        "instagram": "Instagram",
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "triller": "Triller",
        "snapchat": "Snapchat",
        "whatsapp": "WhatsApp",
        "website": "Website",
        "spotify": "Spotify",
        "soundcloud": "SoundCloud",
        "linkedin": "LinkedIn",
        "twitch": "Twitch",
        "pinterest": "Pinterest",
        "threads": "Threads",
        "discord": "Discord",
        "telegram": "Telegram",
    }
    return labels.get(key, key.title())


def _linkbio_parse_page(page: str, page_url: str) -> dict[str, Any] | None:
    """Parse lnk.bio HTML into identity + content links + social icons."""
    username = _linkbio_username(page_url)
    if not username:
        return None

    profile_id: str | None = None
    m_uid = re.search(
        r'data-type=["\']TYPE_PROFILEPIC["\'][^>]*data-uid=["\']([^"\']+)["\']',
        page,
        flags=re.IGNORECASE,
    ) or re.search(
        r'data-uid=["\']([^"\']+)["\'][^>]*data-type=["\']TYPE_PROFILEPIC["\']',
        page,
        flags=re.IGNORECASE,
    )
    if m_uid:
        profile_id = m_uid.group(1)
    if not profile_id:
        m_av = re.search(r"profilepics/(-?\d+)_", page)
        if m_av:
            profile_id = m_av.group(1)

    content_links: list[dict[str, Any]] = []
    social_candidates: list[dict[str, Any]] = []
    social_links: list[dict[str, Any]] = []
    seen_content: set[str] = set()
    seen_network: set[str] = set()

    for match in re.finditer(
        r'<a\s([^>]*\bhref=["\'](https?://[^"\']+)["\'][^>]*)>(.*?)</a>',
        page,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        attrs, href_raw, inner = match.group(1), match.group(2), match.group(3)
        href = html.unescape(href_raw).strip()
        if _is_platform_noise_link(href, page_url):
            continue
        url = safe_str(href)
        if not url:
            continue
        # Prefer data-url when present (canonical).
        m_data_url = re.search(r'\bdata-url=["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        if m_data_url:
            url = safe_str(html.unescape(m_data_url.group(1))) or url

        data_type = None
        m_type = re.search(r'\bdata-type=["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        if m_type:
            data_type = m_type.group(1)
        network = None
        m_net = re.search(r'\bdata-network=["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        if m_net:
            network = m_net.group(1)
        link_id = None
        m_id = re.search(r'\bdata-id=["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        if m_id:
            link_id = m_id.group(1)

        label = _anchor_label(attrs, inner)
        is_icon = bool(network) or "lb-icon-pub" in attrs
        is_content = (data_type or "").upper() in {
            "TYPE_BUTTON",
            "TYPE_BIOLINK",
            "TYPE_LINK",
        } or "pb-linkbox" in attrs
        is_username_cta = "pb-username" in attrs and not url.lower().startswith("https://lnk.bio/")

        if is_icon and network:
            social_key = _LINKBIO_NETWORKS.get(network.upper()) or _social_key_for_url(url)
            # First occurrence per social key / network = primary deep-links row
            # (skip family dupes and CONTACT_SN vs SOCIAL_SN doubles).
            net_key = (social_key or network).upper()
            if net_key in seen_network:
                continue
            seen_network.add(net_key)
            title = _linkbio_network_title(network, label)
            row = {
                "url": url,
                "title": title,
                "type": network,
                "socialKey": social_key,
                "id": safe_str(link_id),
            }
            social_candidates.append(row)
            if social_key != "email":
                social_links.append(
                    _link_item(url, title=title, link_id=safe_str(link_id), link_type=social_key or network)
                )
            continue

        if is_content or is_username_cta:
            if url in seen_content:
                continue
            seen_content.add(url)
            # TYPE_BUTTON / biolink title often lives only on the title= attr.
            if not label:
                label = _anchor_label(attrs, "")
            content_links.append(
                _link_item(
                    url,
                    title=safe_str(label),
                    link_id=safe_str(link_id),
                    link_type=safe_str(data_type) or ("USERNAME" if is_username_cta else None),
                )
            )

    # Fallback: if structured parse found nothing, use improved anchor scrape.
    if not content_links and not social_links:
        return None

    socials, other = _partition_socials(social_candidates)

    # Username CTAs (e.g. Jenna's @handle → Instagram) enrich socials{} without
    # treating every content biolink (YouTube playlist, campaign "website") as a social.
    for link in content_links:
        title = link.get("title") or ""
        ltype = (link.get("type") or "").upper()
        if ltype == "USERNAME" or title.startswith("@"):
            key = _social_key_for_url(link.get("url") or "")
            if key and key not in socials:
                socials[key] = link["url"]

    # Personal / official-website hero only (TYPE_BUTTON or explicit "official website").
    # Do not treat campaign biolinks titled "… Website" as the creator website field.
    website = socials.get("website")
    if not website:
        for link in content_links:
            title_l = (link.get("title") or "").lower()
            ltype = (link.get("type") or "").upper()
            if "official website" in title_l or title_l.startswith("official site"):
                website = link.get("url")
                break
            if ltype == "TYPE_BUTTON" and ("website" in title_l or "official site" in title_l):
                website = link.get("url")
                break
    if website and "website" not in socials:
        socials["website"] = website

    # WhatsApp / email may appear only as icon rows.
    email = None
    for cand in social_candidates:
        if cand.get("socialKey") == "email" or (cand.get("url") or "").lower().startswith("mailto:"):
            m = _EMAIL_RE.search(cand.get("url") or "")
            email = (m.group(1) if m else safe_str(cand.get("url"))) or email
    if not email:
        email = _detect_email(page, content_links + social_links)

    links = content_links + social_links
    avatar = _meta(page, "og:image") or _meta(page, "twitter:image")
    if avatar and "avatar.svg" in avatar.lower():
        avatar = None

    # Never synthesise displayName from @handle OG titles.
    raw_title = _meta(page, "og:title") or _meta(page, "twitter:title")
    display = None
    if raw_title:
        cleaned = _LINKBIO_TITLE_SUFFIX.sub("", raw_title).strip() or None
        if cleaned:
            handle = username.lstrip("@").lower()
            if cleaned.lstrip("@").lower() != handle and cleaned.lower() not in {
                "not found - lnk.bio",
                "not found",
            }:
                display = cleaned

    description = _meta(page, "og:description") or _meta(page, "description")
    if description and _LINKBIO_DESC_TEMPLATE.search(description):
        description = None

    return {
        "platform": "linkbio",
        "id": safe_str(profile_id),
        "url": f"https://lnk.bio/{username}",
        "username": username,
        "handle": username,
        "displayName": display,
        "name": display,  # deprecated alias — null when lnk.bio has no real name
        "description": safe_str(description),
        "avatar": safe_str(avatar),
        "email": email,
        "website": website,
        "whatsapp": socials.get("whatsapp"),
        "linkCount": len(links),
        "links": links,
        "socials": socials,
        "other": other,
    }


async def _fetch_linkbio(value: str) -> dict[str, Any] | None:
    """lnk.bio is server-rendered HTML with data-network social icons + pb-linkbox rows."""
    profile = _url("linkbio", value)
    try:
        resp = await fetch_html(profile, timeout=30.0, prefer_impersonate=True)
    except httpx.HTTPError:
        return None
    if resp.status_code == 404:
        return None
    if resp.status_code >= 400 or _is_cloudflare_block(resp.status_code, resp.text):
        return None
    parsed = _linkbio_parse_page(resp.text, str(resp.url))
    if not parsed:
        return None
    if not (parsed.get("username") or parsed.get("links")):
        return None
    return _strip_page(parsed)



_LINKME_MEDIA = "https://media.link.me/_resize/image/quality=90,format=webp/images"
_LINKME_WEB_TITLES: dict[str, str] = {
    "instagram": "instagram",
    "tiktok": "tiktok",
    "youtube": "youtube",
    "twitter": "twitter",
    "x": "twitter",
    "facebook": "facebook",
    "spotify": "spotify",
    "apple-music": "appleMusic",
    "apple music": "appleMusic",
    "soundcloud": "soundcloud",
    "twitch": "twitch",
    "threads": "threads",
    "linkedin": "linkedin",
    "snapchat": "snapchat",
    "pinterest": "pinterest",
    "discord": "discord",
    "telegram": "telegram",
    "whatsapp": "whatsapp",
    "patreon": "patreon",
}


def _linkme_extract_balanced(src: str, start: int) -> str:
    """Return the {...} literal starting at ``start`` (JS string-aware)."""
    if start >= len(src) or src[start] != "{":
        raise ValueError("expected object")
    depth = 0
    i = start
    in_str = False
    esc = False
    while i < len(src):
        ch = src[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return src[start : i + 1]
        i += 1
    raise ValueError("unbalanced object")


def _linkme_js_literal_to_json(text: str) -> Any:
    """TanStack $R dehydrated object → Python (via JSON)."""
    cleaned = re.sub(r"\$R\[\d+\]=", "", text)
    cleaned = cleaned.replace("!0", "true").replace("!1", "false")
    cleaned = re.sub(r"\bvoid 0\b", "null", cleaned)
    cleaned = re.sub(r"([{\[,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', cleaned)
    return json.loads(cleaned)


def _linkme_tsr_body(page: str) -> str | None:
    match = re.search(
        r'<script[^>]*class=["\']\$tsr["\'][^>]*>(.*?)</script>',
        page,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1) if match else None


def _linkme_parse_named_object(body: str, name: str) -> dict[str, Any] | None:
    match = re.search(rf"{re.escape(name)}:\$R\[\d+\]=", body)
    if not match:
        return None
    try:
        literal = _linkme_extract_balanced(body, match.end())
        data = _linkme_js_literal_to_json(literal)
    except (ValueError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _linkme_avatar(profile: dict[str, Any]) -> str | None:
    webp = safe_str(profile.get("profileImageWebp"))
    png = safe_str(profile.get("profileImage"))
    path = webp or png
    if not path:
        return None
    if path.startswith("http"):
        return path
    # webp-images/... already includes a prefix; png paths are under images/.
    if path.startswith("webp-images/"):
        return f"https://media.link.me/_resize/image/quality=90,format=webp/{path}"
    return f"{_LINKME_MEDIA}/{path.lstrip('/')}"


def _linkme_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return False


def _linkme_map_web_groups(groups: list[Any] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str], list[dict[str, Any]]]:
    """Return (webLinks[], social candidates, socials{}, other[])."""
    web_out: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for group in groups or []:
        if not isinstance(group, dict):
            continue
        title = safe_str(group.get("title")) or ""
        title_key = title.lower().replace("_", "-")
        social_key = _LINKME_WEB_TITLES.get(title_key) or _LINKME_WEB_TITLES.get(
            title_key.replace("-", " ")
        )
        entries: list[dict[str, Any]] = []
        for item in group.get("links") or []:
            if not isinstance(item, dict):
                continue
            value = safe_str(item.get("linkValue") or item.get("url"))
            if not value:
                continue
            entry = {
                "linkValue": value,
                "faceValue": safe_str(item.get("faceValue")),
                "baseUrl": safe_str(item.get("baseUrl")),
            }
            entries.append(strip_empty(entry) if isinstance(entry, dict) else entry)
            url = value if "://" in value or value.startswith("mailto:") else None
            if title.lower() == "email" or (value and "@" in value and "://" not in value):
                candidates.append(
                    {
                        "url": value if value.startswith("mailto:") else f"mailto:{value}",
                        "socialKey": "email",
                        "type": "EMAIL",
                        "title": title or "Email",
                    }
                )
            elif url:
                candidates.append(
                    {
                        "url": url,
                        "socialKey": social_key or _social_key_for_url(url),
                        "type": title or None,
                        "title": title or None,
                    }
                )
        if entries:
            web_out.append(
                strip_empty(
                    {
                        "title": title or None,
                        "linkId": group.get("linkId"),
                        "links": entries,
                    }
                )
            )
    socials, other = _partition_socials(candidates)
    return web_out, candidates, socials, other


def _linkme_map_featured(featured: dict[str, Any] | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not isinstance(featured, dict):
        return rows
    for item in featured.get("list") or []:
        if not isinstance(item, dict):
            continue
        url = safe_str(item.get("url") or item.get("link"))
        if not url or not url.startswith("http"):
            continue
        if _is_platform_noise_link(url):
            continue
        raw_id = item.get("id")
        rows.append(
            {
                "id": safe_str(raw_id) if raw_id is not None else None,
                "title": safe_str(item.get("title")),
                "url": url,
                "thumbnail": safe_str(item.get("thumbnail") or item.get("image")),
                "description": safe_str(item.get("description")),
            }
        )
    # Drop null-only extras via strip later; keep title even when null.
    out: list[dict[str, Any]] = []
    for row in rows:
        item = {
            "url": row["url"],
            "title": row.get("title"),
        }
        if row.get("id"):
            item["id"] = row["id"]
        if row.get("thumbnail"):
            item["thumbnail"] = row["thumbnail"]
        if row.get("description"):
            item["description"] = row["description"]
        out.append(item)
    return out


def _linkme_map_info_links(groups: list[Any] | None) -> tuple[list[dict[str, Any]], str | None]:
    info_out: list[dict[str, Any]] = []
    email: str | None = None
    for group in groups or []:
        if not isinstance(group, dict):
            continue
        title = safe_str(group.get("title"))
        entries: list[dict[str, Any]] = []
        for item in group.get("links") or []:
            if not isinstance(item, dict):
                continue
            value = safe_str(item.get("linkValue") or item.get("url"))
            if not value:
                continue
            entries.append(
                strip_empty(
                    {
                        "linkValue": value,
                        "faceValue": safe_str(item.get("faceValue")),
                    }
                )
            )
            if (title or "").lower() == "email" or ("@" in value and "://" not in value):
                email = email or value
        if entries:
            info_out.append(
                strip_empty({"title": title, "linkId": group.get("linkId"), "links": entries})
            )
    return info_out, email


def _linkme_parse_page(page: str, page_url: str) -> dict[str, Any] | None:
    """Parse Linkme TanStack ``$tsr`` dehydrated profile (not __NEXT_DATA__ / meta)."""
    body = _linkme_tsr_body(page)
    if not body:
        return None
    profile = _linkme_parse_named_object(body, "profile")
    if not profile or not safe_str(profile.get("username")):
        return None
    featured = _linkme_parse_named_object(body, "featuredLinks")
    username = safe_str(profile.get("username")) or ""
    first = safe_str(profile.get("firstName")) or ""
    last = safe_str(profile.get("lastName")) or ""
    display = " ".join(p for p in (first, last) if p).strip() or None
    bio = safe_str(profile.get("bio")) or ""
    links = _linkme_map_featured(featured)
    web_links, _cands, socials, other = _linkme_map_web_groups(
        profile.get("webLinks") if isinstance(profile.get("webLinks"), list) else []
    )
    # Featured CTAs that are social URLs fill gaps in socials{}.
    for link in links:
        url = safe_str(link.get("url"))
        if not url:
            continue
        key = _social_key_for_url(url)
        if key and key not in socials:
            socials[key] = url
    info_links, email = _linkme_map_info_links(
        profile.get("infoLinks") if isinstance(profile.get("infoLinks"), list) else []
    )
    stripe = profile.get("stripeStatus") if isinstance(profile.get("stripeStatus"), dict) else {}
    stripe_out = {
        "tipsEnabled": _linkme_truthy(stripe.get("tipsEnabled")),
        "stripeEnabled": _linkme_truthy(stripe.get("stripeEnabled")),
    }
    if safe_str(stripe.get("stripeAccountId")):
        stripe_out["stripeAccountId"] = safe_str(stripe.get("stripeAccountId"))

    total_links = profile.get("totalLinks")
    try:
        total_links_i = int(total_links) if total_links is not None else len(links)
    except (TypeError, ValueError):
        total_links_i = len(links)

    out = {
        "platform": "linkme",
        "id": safe_str(profile.get("id")),
        "url": f"https://link.me/{username}",
        "username": username,
        "handle": username,
        "displayName": display,
        "name": display,
        "firstName": first or None,
        "lastName": last or None,
        "bio": bio,
        "description": bio,
        "avatar": _linkme_avatar(profile),
        "isDefaultProfilePicture": _linkme_truthy(profile.get("isDefaultProfilePicture")),
        "profileVisitCount": safe_str(profile.get("profileVisitCount")),
        "verifiedAccount": _linkme_truthy(profile.get("verifiedAccount")),
        "isAmbassador": _linkme_truthy(profile.get("isAmbassador")),
        "isPrivate": _linkme_truthy(profile.get("isPrivate")),
        "createdAt": safe_str(profile.get("createdAt")),
        "updatedAt": safe_str(profile.get("updatedAt")),
        "totalLinks": total_links_i,
        "linkCount": len(links),
        "links": links,
        "webLinks": web_links,
        "infoLinks": info_links,
        "stripeStatus": stripe_out,
        "email": email,
        "socials": socials,
        "other": other,
        "chatId": safe_str(profile.get("chatID") or profile.get("chatId")),
    }
    cleaned = strip_empty(
        {
            k: v
            for k, v in out.items()
            if k
            not in (
                "bio",
                "description",
                "links",
                "webLinks",
                "infoLinks",
                "other",
                "stripeStatus",
                "isDefaultProfilePicture",
                "verifiedAccount",
                "isAmbassador",
                "isPrivate",
                "totalLinks",
                "linkCount",
            )
        }
    )
    # Keep booleans / counts / empty bio even when falsy — they are signals.
    cleaned["bio"] = bio
    cleaned["description"] = bio
    cleaned["links"] = links
    cleaned["linkCount"] = len(links)
    cleaned["totalLinks"] = total_links_i
    cleaned["webLinks"] = web_links
    cleaned["infoLinks"] = info_links
    cleaned["other"] = other
    cleaned["stripeStatus"] = stripe_out
    cleaned["isDefaultProfilePicture"] = _linkme_truthy(profile.get("isDefaultProfilePicture"))
    cleaned["verifiedAccount"] = _linkme_truthy(profile.get("verifiedAccount"))
    cleaned["isAmbassador"] = _linkme_truthy(profile.get("isAmbassador"))
    cleaned["isPrivate"] = _linkme_truthy(profile.get("isPrivate"))
    return cleaned


async def _fetch_linkme(value: str) -> dict[str, Any] | None:
    """Linkme is a TanStack SPA; profile JSON is dehydrated in ``$tsr``, not meta/footer."""
    profile_url = _url("linkme", value)
    try:
        resp = await fetch_html(profile_url, timeout=30.0, prefer_impersonate=True)
    except httpx.HTTPError:
        return None
    if resp.status_code == 404:
        return None
    if resp.status_code >= 400 or _is_cloudflare_block(resp.status_code, resp.text):
        return None
    parsed = _linkme_parse_page(resp.text, str(resp.url))
    if not parsed:
        return None
    return parsed


async def _fetch_page(platform: str, value: str) -> dict[str, Any]:
    if platform == "komi":
        komi = await _fetch_komi(value)
        if komi:
            return komi
    if platform == "pillar":
        pillar = await _fetch_pillar(value)
        if pillar:
            return pillar
    if platform == "linkbio":
        linkbio = await _fetch_linkbio(value)
        if linkbio:
            return linkbio
    if platform == "linkme":
        # Never fall through to meta/footer scrape — that returned Privacy/Terms
        # as creator links. Missing $tsr profile is a hard failure.
        linkme = await _fetch_linkme(value)
        if linkme:
            return linkme
        raise HTTPException(
            status_code=502,
            detail="Linkme profile data unavailable (SSR shell without dehydrated profile)",
        )
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
            {"url": profile, "v": 13, "cacheMaxAge": cache_max_age},
            lambda: _fetch_page(platform, profile),
            ctx,
            use_cache=use_cache,
            ttl=ttl,
        )
        if data.pop("_marketingShell", None) or not (data.get("username") or data.get("links")):
            raise HTTPException(status_code=404, detail=f"{platform.title()} page not found")
        # Pillar soft-404s used to return a marketing shell; GraphQL pages are real when
        # they carry links, products, or socials — empty shells still 404.
        if platform == "pillar" and not (
            data.get("links") or data.get("products") or data.get("socials")
        ):
            raise HTTPException(status_code=404, detail="Pillar page not found or has no public content")
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


@router.get(
    "/pillar/page",
    summary="Pillar page",
    description=(
        "Public Pillar page as clean JSON — identity (id, displayName, bio, location, email), "
        "socials{} (instagram/tiktok/youtube/twitter/spotify/patreon/discord/twitch/…), "
        "links[] with per-link clicks/id/type/order, and products[] (title, price, url, image). "
        "Flat 1 credit via Pillar's public GraphQL API (not HTML scrape)."
    ),
)
async def pillar_page(
    url: str = Query(..., description="Pillar page URL or username"),
    cache: bool = Query(False, description=_CACHE_DESC),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    return await _page(
        "pillar", url, caller, use_cache=use_cache, ttl=ttl, cache_max_age=cacheMaxAge
    )


@router.get(
    "/linkbio/page",
    summary="Linkbio page",
    description=(
        "Public lnk.bio page as clean JSON — id, handle, avatar, email/website/whatsapp when "
        "published, socials{} (incl. triller/website; SC often leaves these null), other[] for "
        "unmapped social networks, and links[] with titles from icon labels + content buttons. "
        "displayName/name are omitted when lnk.bio only exposes @handle. Flat 1 credit."
    ),
)
async def linkbio_page(
    url: str = Query(..., description="Linkbio (lnk.bio) page URL or username"),
    cache: bool = Query(False, description=_CACHE_DESC),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    return await _page(
        "linkbio", url, caller, use_cache=use_cache, ttl=ttl, cache_max_age=cacheMaxAge
    )


@router.get(
    "/linkme/profile",
    summary="Linkme profile",
    description=(
        "Public Linkme profile as clean JSON from the dehydrated SSR profile payload "
        "(not HTML meta/footer). Returns displayName/bio, avatar + isDefaultProfilePicture, "
        "profileVisitCount, totalLinks, verifiedAccount/isAmbassador/isPrivate, "
        "createdAt/updatedAt, featured links[], webLinks[] (social icons), infoLinks[] "
        "(email/contact), stripeStatus{tipsEnabled,stripeEnabled}, socials{}, and other[]. "
        "Flat 1 credit. Example: https://link.me/danucd."
    ),
)
async def linkme_profile(
    url: str = Query(..., description="Linkme profile URL or username (e.g. link.me/danucd)"),
    cache: bool = Query(False, description=_CACHE_DESC),
    cacheMaxAge: str | None = Query(None, description=CACHE_MAX_AGE_DESC),
    caller: ApiCaller = Depends(require_api_key),
):
    use_cache, ttl = resolve_cache_options(cache, cacheMaxAge)
    return await _page(
        "linkme", url, caller, use_cache=use_cache, ttl=ttl, cache_max_age=cacheMaxAge
    )
