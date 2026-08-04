"""Pinterest endpoints: pin details, user pins, search.

Backed by a config-driven Pinterest actor. Field mappings are defensive.
"""

from __future__ import annotations

import asyncio
import html
import json
import math
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import get_apify
from app.services.cached_runner import cached_or_run
from app.services import pinterest_native as native
from app.utils.formatters import safe_int, safe_str, strip_empty
from app.utils.url import (
    detect_url_platform,
    extract_pinterest_pin_id,
    extract_pinterest_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
RATE = 0.5


def _scaled(n: int, rate: float, minimum: int) -> int:
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _reject_pinterest_platform_mismatch(value: str, example: str) -> None:
    detected = detect_url_platform(value)
    if detected and detected != "pinterest":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "pinterest", example),
        )


def _require_pinterest_pin_url(url: str) -> str:
    pin_id = extract_pinterest_pin_id(url)
    if not pin_id:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(url, "pinterest", "https://www.pinterest.com/pin/123456789/"),
        )
    return pin_id


def _require_pinterest_username(value: str) -> str:
    _reject_pinterest_platform_mismatch(value, "https://www.pinterest.com/username/")
    username = extract_pinterest_username(value)
    if not username:
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "pinterest", "https://www.pinterest.com/username/"),
        )
    return username


def _html_text(v: Any) -> str | None:
    """safe_str + HTML entity decode (Pinterest often returns &amp; in names/links)."""
    s = safe_str(v)
    if not s:
        return None
    return html.unescape(s).strip() or None


def _created_at_iso(value: Any) -> str | None:
    """Normalize Pinterest dates to ISO-8601 UTC (accepts ISO or RFC 2822)."""
    s = safe_str(value)
    if not s:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?", s):
        return s if s.endswith("Z") else f"{s}Z" if "T" in s else s
    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError, IndexError, OverflowError):
        pass
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        return s


def _board_scoped_followers(item: dict[str, Any]) -> int | None:
    """Board follower count — never Pinterest's account-scoped board.follower_count.

    Logged-out board blobs (pidgets pin.board, Redux boards map) expose
    ``follower_count`` that is identical across every board on a profile
    (account-scale). Only explicitly board-scoped keys are trusted.
    """
    return safe_int(
        item.get("boardFollowerCount")
        or item.get("board_follower_count")
        or item.get("boardFollowers")
    )


def _synthesize_originals_url(image_url: str | None) -> str | None:
    """Rewrite a sized pinimg URL to /originals/ when possible."""
    u = safe_str(image_url)
    if not u or "pinimg.com" not in u:
        return None
    if "/originals/" in u:
        return u
    rewritten = re.sub(r"/(\d+x)/", "/originals/", u, count=1)
    return rewritten if rewritten != u else None


def _images_variants(images: Any) -> dict[str, Any]:
    """Map pidgets/Apify image dict → {size: {url,width,height}}."""
    if not isinstance(images, dict):
        return {}
    out: dict[str, Any] = {}
    for key, entry in images.items():
        if not isinstance(key, str):
            continue
        if isinstance(entry, dict) and entry.get("url"):
            out[key] = strip_empty(
                {
                    "url": safe_str(entry.get("url")),
                    "width": safe_int(entry.get("width")),
                    "height": safe_int(entry.get("height")),
                }
            )
        elif isinstance(entry, str) and entry.strip():
            out[key] = {"url": entry.strip()}
    if "originals" not in out and "orig" not in out:
        for key in ("736x", "564x", "474x", "237x", "236x"):
            entry = out.get(key)
            if isinstance(entry, dict):
                orig = _synthesize_originals_url(entry.get("url"))
                if orig:
                    out["originals"] = {"url": orig}
                    break
    return out


def _best_image_url(
    images: dict[str, Any] | None,
    fallback: str | None = None,
    *,
    prefer_originals: bool = False,
) -> str | None:
    """Pick a display image. Default prefers sized CDN URLs (stable for clients);
    originals stay available under ``images.originals``."""
    if isinstance(images, dict):
        keys = (
            ("originals", "orig", "736x", "564x", "474x", "237x", "236x")
            if prefer_originals
            else ("736x", "564x", "474x", "237x", "236x", "originals", "orig")
        )
        for key in keys:
            entry = images.get(key)
            if isinstance(entry, dict) and entry.get("url"):
                return safe_str(entry["url"])
            if isinstance(entry, str):
                return safe_str(entry)
    return safe_str(fallback)


def _person_from_pidget(user: Any) -> dict[str, Any]:
    """Normalize pinner / native_creator into a clean person object."""
    if not isinstance(user, dict):
        return {}
    profile_url = _html_text(user.get("profile_url") or user.get("url"))
    username = _html_text(user.get("username"))
    if not username and profile_url:
        username = profile_url.rstrip("/").rsplit("/", 1)[-1] or None
    verified = user.get("is_verified_merchant")
    if not isinstance(verified, bool):
        verified = user.get("isVerifiedMerchant")
    if not isinstance(verified, bool):
        verified = None
    return strip_empty(
        {
            "id": safe_str(user.get("id") or user.get("entityId")),
            "username": username,
            "displayName": _html_text(
                user.get("full_name") or user.get("fullName") or user.get("displayName")
            ),
            "url": profile_url,
            "followers": safe_int(user.get("follower_count") or user.get("followerCount")),
            "pinCount": safe_int(user.get("pin_count") or user.get("pinCount")),
            "avatar": safe_str(
                user.get("image_small_url")
                or user.get("imageSmallUrl")
                or user.get("avatar")
            ),
            "avatarMedium": safe_str(
                user.get("image_medium_url") or user.get("imageMediumUrl")
            ),
            "avatarLarge": safe_str(
                user.get("image_large_url") or user.get("imageLargeUrl")
            ),
            "isVerifiedMerchant": verified,
            "about": _html_text(user.get("about")),
        }
    )


def _image(item: dict[str, Any]) -> str | None:
    imgs = item.get("images") or item.get("image")
    if isinstance(imgs, dict):
        mapped = _images_variants(imgs) if any(isinstance(v, (dict, str)) for v in imgs.values()) else {}
        best = _best_image_url(mapped)
        if best:
            return best
        for key in ("orig", "originals", "736x", "564x", "474x"):
            v = imgs.get(key)
            if isinstance(v, dict) and v.get("url"):
                return safe_str(v["url"])
            if isinstance(v, str):
                return safe_str(v)
        if imgs.get("url"):
            return safe_str(imgs["url"])
    return safe_str(item.get("imageUrl") or item.get("image_url") or item.get("thumbnail"))


def _normalize_pin(item: dict[str, Any]) -> dict[str, Any]:
    pinner = item.get("pinner") or item.get("user") or {}
    if not isinstance(pinner, dict):
        pinner = {}
    native_creator = item.get("native_creator") or item.get("nativeCreator") or item.get("originPinner")
    board = item.get("board") if isinstance(item.get("board"), dict) else {}
    pin_id = item.get("id") or item.get("pinId") or item.get("pin_id")
    pin_url = item.get("url") or item.get("pinUrl") or item.get("pin_url")
    board_url = safe_str(item.get("boardUrl") or board.get("url"))
    if board_url and board_url.startswith("/"):
        board_url = f"https://www.pinterest.com{board_url}"
    link = _html_text(
        item.get("link")
        or item.get("destinationUrl")
        or item.get("sourceLink")
        or item.get("linkUrl")
        or item.get("clickThroughUrl")
    )
    images = _images_variants(item.get("images")) if isinstance(item.get("images"), dict) else {}
    image = _image(item) or _best_image_url(images)
    created = _created_at_iso(
        item.get("created_at")
        or item.get("createdAt")
        or item.get("createdDate")
        or item.get("date")
        or item.get("publishedAt")
    )
    author = _person_from_pidget(pinner)
    if not author.get("username"):
        author = strip_empty(
            {
                **author,
                "username": safe_str(
                    item.get("pinner_username")
                    or item.get("creator")
                    or item.get("creatorUsername")
                ),
                "displayName": author.get("displayName")
                or _html_text(
                    item.get("pinner_name")
                    or item.get("creatorFullName")
                    or item.get("creatorName")
                ),
                "followers": author.get("followers")
                or safe_int(item.get("creatorFollowerCount")),
            }
        )
    origin = _person_from_pidget(native_creator)
    agg = item.get("aggregated_pin_data") if isinstance(item.get("aggregated_pin_data"), dict) else {}
    stats = agg.get("aggregated_stats") if isinstance(agg.get("aggregated_stats"), dict) else {}
    saves = safe_int(
        stats.get("saves")
        or item.get("saveCount")
        or item.get("saves")
        or item.get("aggregateSaveCount")
        or item.get("repin_count")
        or item.get("repinCount")
    )
    # Ensure originals variant exists (deterministic pinimg /originals/ rewrite).
    if images and "originals" not in images and "orig" not in images and image:
        orig_u = _synthesize_originals_url(image)
        if orig_u:
            images["originals"] = {"url": orig_u}
    elif not images and image:
        orig_u = _synthesize_originals_url(image)
        images = {"originals": {"url": orig_u}} if orig_u else {}
    image_original = None
    if isinstance(images.get("originals"), dict):
        image_original = safe_str(images["originals"].get("url"))
    elif isinstance(images.get("orig"), dict):
        image_original = safe_str(images["orig"].get("url"))
    if not image_original:
        image_original = _synthesize_originals_url(image)

    rich = item.get("rich_summary") if isinstance(item.get("rich_summary"), dict) else {}
    rich_type = _html_text(
        rich.get("type_name")
        or rich.get("typeName")
        or item.get("richPinType")
        or item.get("rich_pin_type")
    )

    out = strip_empty(
        {
            "platform": "pinterest",
            "id": safe_str(pin_id),
            "url": safe_str(pin_url)
            or (f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else None),
            "title": _html_text(
                item.get("title")
                or item.get("grid_title")
                or item.get("closeup_unified_title")
                or item.get("gridTitle")
                or item.get("headline")
                or rich.get("display_name")
                or rich.get("title")
            ),
            "description": _html_text(
                item.get("description")
                or item.get("altText")
                or item.get("autoAltText")
                or item.get("auto_alt_text")
                or item.get("alt_text")
            ),
            "seoAltText": _html_text(
                item.get("seoAltText") or item.get("seo_alt_text") or item.get("auto_alt_text")
            ),
            "richPinType": rich_type,
            "link": link,
            "destinationUrl": link,
            "domain": _html_text(item.get("domain")),
            "image": image,
            "images": images or None,
            "isVideo": bool(item.get("is_video") or item.get("isVideo"))
            if item.get("is_video") is not None or item.get("isVideo") is not None
            else None,
            "dominantColor": safe_str(item.get("dominant_color") or item.get("dominantColor")),
            "repinCount": safe_int(item.get("repin_count") or item.get("repinCount")),
            "shareCount": safe_int(item.get("share_count") or item.get("shareCount")),
            "reactionCount": safe_int(
                item.get("total_reaction_count")
                or item.get("totalReactionCount")
                or item.get("reactionCount")
            ),
            "comments": safe_int(
                item.get("comment_count")
                or item.get("commentCount")
                or item.get("commentsCount")
                or agg.get("comment_count")
            ),
            "createdAt": created,
            "publishedAt": created,
            "board": {
                "name": _html_text(item.get("boardName") or board.get("name")),
                "url": board_url,
                "pinCount": safe_int(board.get("pin_count") or board.get("pinCount")),
                # Not board.follower_count — that field is account-scoped on logged-out hydrates.
                "followers": _board_scoped_followers(board),
                "privacy": _html_text(board.get("privacy") or board.get("board_privacy")),
                "collaborative": (
                    bool(board.get("collaborative") or board.get("is_collaborative"))
                    if board.get("collaborative") is not None
                    or board.get("is_collaborative") is not None
                    else None
                ),
            },
            "author": author,
            "originAuthor": origin or None,
        }
    )
    # Always key primary engagement + full-res image (list clients depend on them).
    out["saves"] = saves
    out["imageOriginal"] = image_original
    if images:
        out["images"] = images
    return out


# The router's run-input format (mode/keywords/usernames/boardUrls) targets
# this actor. If the deployment env pins APIFY_ACTOR_PINTEREST to an older
# actor (e.g. thirdwatch), runs "succeed" with zero rows - so always fall back
# to the actor the input schema was written for.
_PINTEREST_ACTOR_FALLBACK = "crawlerbros/pinterest-scraper-pro"


async def _run_pinterest_actor(run_input: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    """Run the Pinterest actor, retrying empty runs (intermittent proxy
    blocks) and falling back to the schema-matching actor."""
    apify = get_apify()
    actors = [get_settings().APIFY_ACTOR_PINTEREST]
    if _PINTEREST_ACTOR_FALLBACK not in actors:
        actors.append(_PINTEREST_ACTOR_FALLBACK)
    for actor in actors:
        for _attempt in range(2):
            try:
                items = await apify.run_actor_sync(actor, run_input, max_items=limit)
            except Exception:  # noqa: BLE001
                items = []
            if items:
                return items
    return []


def _prefer_enriched(pins: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Push fully-enriched pins first; the actor occasionally emits bare
    id/url stubs when a pin's detail fetch fails mid-run."""
    enriched = [p for p in pins if p.get("title") or p.get("image")]
    sparse = [p for p in pins if not (p.get("title") or p.get("image"))]
    return enriched + sparse


def _slim_list_author(author: Any) -> dict[str, Any]:
    """Per-pin author on board/user-pins lists (full card hoisted to top-level)."""
    if not isinstance(author, dict):
        return {}
    return strip_empty(
        {
            "username": author.get("username"),
            "displayName": author.get("displayName"),
        }
    )


async def _enrich_sparse_pins(pins: list[dict[str, Any]], *, max_enrich: int = 10) -> list[dict[str, Any]]:
    """Fill title/saves/etc for stub actor rows via Pinterest's public pidgets API."""
    to_enrich = [
        p
        for p in pins
        if p.get("id") and (not p.get("title") or p.get("saves") is None or not p.get("imageOriginal"))
    ][:max_enrich]
    if not to_enrich:
        return pins
    details = await asyncio.gather(
        *[_fetch_pin_pidgets(str(p["id"])) for p in to_enrich],
        return_exceptions=True,
    )
    by_id: dict[str, dict[str, Any]] = {}
    for pin, detail in zip(to_enrich, details):
        if isinstance(detail, dict) and detail.get("id"):
            by_id[str(detail["id"])] = detail
    out: list[dict[str, Any]] = []
    for pin in pins:
        detail = by_id.get(str(pin.get("id") or ""))
        if not detail:
            out.append(pin)
            continue
        merged = {**pin}
        for key in (
            "title",
            "description",
            "seoAltText",
            "richPinType",
            "link",
            "destinationUrl",
            "domain",
            "saves",
            "repinCount",
            "shareCount",
            "reactionCount",
            "comments",
            "createdAt",
            "publishedAt",
            "image",
            "imageOriginal",
            "images",
            "isVideo",
            "dominantColor",
            "originAuthor",
        ):
            if merged.get(key) in (None, "", {}, []) and detail.get(key) not in (None, "", {}, []):
                merged[key] = detail[key]
        if isinstance(merged.get("author"), dict) and isinstance(detail.get("author"), dict):
            for key, value in detail["author"].items():
                if value and not merged["author"].get(key):
                    merged["author"][key] = value
        if isinstance(merged.get("board"), dict) and isinstance(detail.get("board"), dict):
            for key, value in detail["board"].items():
                if value and not merged["board"].get(key):
                    merged["board"][key] = value
        out.append(merged)
    return out


def _meta(page: str, key: str) -> str | None:
    pattern = rf'<meta\s+(?:property|name)=["\']{re.escape(key)}["\']\s+content=["\']([^"\']+)["\']'
    match = re.search(pattern, page, flags=re.IGNORECASE)
    if not match:
        pattern = rf'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']{re.escape(key)}["\']'
        match = re.search(pattern, page, flags=re.IGNORECASE)
    return html.unescape(match.group(1)).strip() if match else None


def _html_title(page: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", page, flags=re.IGNORECASE | re.DOTALL)
    return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip() if match else None


def _json_string(page: str, key: str) -> str | None:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*"([^"]+)"', page)
    if not match:
        return None
    try:
        return html.unescape(match.group(1).encode("utf-8").decode("unicode_escape")).strip()
    except UnicodeDecodeError:
        return html.unescape(match.group(1)).strip()


def _json_ld_pin(page: str) -> dict[str, Any]:
    """Extract SocialMediaPosting JSON-LD from a pin page (title/desc/date/image)."""
    for match in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        page,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        raw = match.group(1).strip()
        if "SocialMediaPosting" not in raw and "ImageObject" not in raw:
            continue
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            continue
        if isinstance(data, list):
            data = next((d for d in data if isinstance(d, dict)), None)
        if not isinstance(data, dict):
            continue
        author = data.get("author") if isinstance(data.get("author"), dict) else {}
        image = data.get("image")
        image_url = None
        if isinstance(image, str):
            image_url = image
        elif isinstance(image, list) and image:
            image_url = image[0] if isinstance(image[0], str) else None
        elif isinstance(image, dict):
            image_url = image.get("url")
        saves = None
        for stat in data.get("interactionStatistic") or []:
            if not isinstance(stat, dict):
                continue
            if safe_str(stat.get("description")) == "Saves" or "LikeAction" in str(
                stat.get("interactionType")
            ):
                saves = safe_int(stat.get("userInteractionCount"))
                break
        return strip_empty(
            {
                "title": _html_text(data.get("headline") or data.get("name")),
                "description": _html_text(data.get("articleBody") or data.get("description")),
                "createdAt": _created_at_iso(data.get("datePublished")),
                "image": safe_str(image_url),
                "saves": saves,
                "authorName": _html_text(author.get("name")),
                "authorUsername": _html_text(author.get("alternateName")),
                "authorUrl": _html_text(author.get("url")),
            }
        )
    return {}


def _page_pin_extras(page: str) -> dict[str, Any]:
    """Pull seoAltText / engagement counts / RFC createdAt from pin HTML JSON."""
    def _num(key: str) -> int | None:
        m = re.search(rf'"{re.escape(key)}"\s*:\s*(\d+)', page)
        return safe_int(m.group(1)) if m else None

    seo = _json_string(page, "seoAltText")
    created_rfc = _json_string(page, "createdAt")
    return strip_empty(
        {
            "seoAltText": _html_text(seo),
            "createdAt": _created_at_iso(created_rfc),
            "repinCount": _num("repinCount"),
            "shareCount": _num("shareCount"),
            "reactionCount": _num("totalReactionCount"),
        }
    )


async def _enrich_pin_from_page(pin_id: str, base: dict[str, Any]) -> dict[str, Any]:
    """Fill title/description/createdAt/seoAltText/reactions from the public pin page.

    Pidgets omit created_at and often blank description; the pin HTML carries
    JSON-LD + seoAltText / shareCount / totalReactionCount.
    """
    url = safe_str(base.get("url")) or f"https://www.pinterest.com/pin/{pin_id}/"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
            resp = await client.get(url)
    except httpx.HTTPError:
        return base
    if resp.status_code >= 400 or not resp.text:
        return base

    page = resp.text
    ld = _json_ld_pin(page)
    extras = _page_pin_extras(page)
    out = dict(base)

    for key in ("title", "description", "seoAltText"):
        if not out.get(key) and (ld.get(key) or extras.get(key)):
            out[key] = ld.get(key) or extras.get(key)

    created = ld.get("createdAt") or extras.get("createdAt")
    if created:
        out["createdAt"] = created
        out["publishedAt"] = created

    for key in ("repinCount", "shareCount", "reactionCount"):
        if out.get(key) is None and extras.get(key) is not None:
            out[key] = extras[key]

    if not out.get("saves") and ld.get("saves") is not None:
        out["saves"] = ld["saves"]

    # Prefer JSON-LD originals image when present.
    if ld.get("image"):
        images = dict(out.get("images") or {}) if isinstance(out.get("images"), dict) else {}
        if "/originals/" in ld["image"] or "originals" not in images:
            images["originals"] = {"url": ld["image"]}
            out["images"] = images
            # Keep existing sized `image` if we already have one; else use originals.
            if not out.get("image"):
                out["image"] = ld["image"]

    author = dict(out.get("author") or {}) if isinstance(out.get("author"), dict) else {}
    if not author.get("displayName") and ld.get("authorName"):
        author["displayName"] = ld["authorName"]
    if not author.get("username") and ld.get("authorUsername"):
        author["username"] = ld["authorUsername"]
    if not author.get("url") and ld.get("authorUrl"):
        author["url"] = ld["authorUrl"]
    if author:
        out["author"] = author

    return strip_empty(out)


async def _fetch_pin_pidgets(pin_id: str) -> dict[str, Any] | None:
    """Pinterest's public widget API returns full pin metadata (stats, pinner,
    board, images) without auth; use it before falling back to OG scraping."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        try:
            resp = await client.get(
                "https://widgets.pinterest.com/v3/pidgets/pins/info/",
                params={"pin_ids": pin_id},
            )
        except httpx.HTTPError:
            return None
    if resp.status_code != 200:
        return None
    try:
        rows = (resp.json() or {}).get("data") or []
    except ValueError:
        return None
    if not rows or not isinstance(rows[0], dict):
        return None
    pin = rows[0]
    board = pin.get("board") if isinstance(pin.get("board"), dict) else {}
    agg = pin.get("aggregated_pin_data") if isinstance(pin.get("aggregated_pin_data"), dict) else {}
    stats = agg.get("aggregated_stats") if isinstance(agg.get("aggregated_stats"), dict) else {}
    images = _images_variants(pin.get("images"))
    if not images:
        # story pins keep images inside story_pin_data pages
        for page in ((pin.get("story_pin_data") or {}).get("pages")) or []:
            for block in (page.get("blocks") or []) if isinstance(page, dict) else []:
                block_images = (
                    ((block.get("image") or {}).get("images")) if isinstance(block, dict) else None
                )
                if isinstance(block_images, dict):
                    images = _images_variants(block_images)
                    if images:
                        break
            if images:
                break
    image = _best_image_url(images)
    board_url = safe_str(board.get("url"))
    if board_url and board_url.startswith("/"):
        board_url = f"https://www.pinterest.com{board_url}"
    rich = pin.get("rich_metadata") if isinstance(pin.get("rich_metadata"), dict) else {}
    rich_summary = pin.get("rich_summary") if isinstance(pin.get("rich_summary"), dict) else {}
    link = _html_text(pin.get("link") or rich.get("url"))
    # Prefer a real title; do not fall back to a whitespace-only description.
    title = _html_text(
        rich.get("title")
        or pin.get("grid_title")
        or pin.get("closeup_unified_title")
        or rich_summary.get("display_name")
        or pin.get("title")
    )
    description = _html_text(pin.get("description"))
    seo_alt = _html_text(pin.get("auto_alt_text") or pin.get("alt_text") or pin.get("seoAltText"))
    created = _created_at_iso(pin.get("created_at") or pin.get("createdAt"))
    author = _person_from_pidget(pin.get("pinner"))
    origin = _person_from_pidget(pin.get("native_creator") or pin.get("origin_pinner"))
    return strip_empty(
        {
            "platform": "pinterest",
            "id": safe_str(pin.get("id") or pin_id),
            "url": f"https://www.pinterest.com/pin/{pin_id}/",
            "title": title,
            "description": description,
            "seoAltText": seo_alt,
            "link": link,
            "destinationUrl": link,
            "domain": _html_text(pin.get("domain")),
            "image": safe_str(image),
            "images": images or None,
            "isVideo": bool(pin.get("is_video")),
            "dominantColor": safe_str(pin.get("dominant_color")),
            "saves": safe_int(stats.get("saves") or pin.get("repin_count")),
            "repinCount": safe_int(pin.get("repin_count")),
            "shareCount": safe_int(pin.get("share_count")),
            "reactionCount": safe_int(
                pin.get("total_reaction_count") or pin.get("totalReactionCount")
            ),
            "comments": safe_int(
                pin.get("comment_count") or stats.get("comments") or agg.get("comment_count")
            ),
            "createdAt": created,
            "publishedAt": created,
            "board": {
                "name": _html_text(board.get("name")),
                "url": board_url,
                "pinCount": safe_int(board.get("pin_count")),
                # Not board.follower_count — account-scoped on logged-out hydrates.
                "followers": _board_scoped_followers(board),
            },
            "author": author,
            "originAuthor": origin or None,
        }
    )


async def _fetch_pin_page(url: str) -> dict[str, Any]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
    if resp.status_code >= 400:
        raise HTTPException(status_code=404, detail="Pin not found")

    page = resp.text
    pin_id = extract_pinterest_pin_id(str(resp.url)) or extract_pinterest_pin_id(url)
    ld = _json_ld_pin(page)
    extras = _page_pin_extras(page)
    title = (
        ld.get("title")
        or _meta(page, "og:title")
        or _json_string(page, "title")
        or _html_title(page)
    )
    description = (
        ld.get("description")
        or _meta(page, "og:description")
        or _meta(page, "description")
        or _json_string(page, "description")
    )
    image = ld.get("image") or _meta(page, "og:image")
    canonical = _meta(page, "og:url") or str(resp.url)
    created = ld.get("createdAt") or extras.get("createdAt")
    if not (title or description or image):
        raise HTTPException(status_code=404, detail="Pin not found")

    images = {}
    if image and "/originals/" in image:
        images["originals"] = {"url": image}
    return strip_empty(
        {
            "platform": "pinterest",
            "id": safe_str(pin_id),
            "url": safe_str(canonical),
            "title": _html_text(title),
            "description": _html_text(description),
            "seoAltText": extras.get("seoAltText"),
            "image": safe_str(image),
            "images": images or None,
            "saves": ld.get("saves") if ld.get("saves") is not None else 0,
            "repinCount": extras.get("repinCount"),
            "shareCount": extras.get("shareCount"),
            "reactionCount": extras.get("reactionCount"),
            "comments": 0,
            "createdAt": created,
            "publishedAt": created,
            "author": strip_empty(
                {
                    "username": ld.get("authorUsername"),
                    "displayName": ld.get("authorName"),
                    "url": ld.get("authorUrl"),
                }
            ),
        }
    )


@router.get(
    "/pin-details",
    summary="Pinterest pin metadata + stats",
    description=(
        "Returns title, description, seoAltText, link, ISO createdAt, board, "
        "author (pinner), originAuthor (native creator), saves/repin/share/reaction "
        "counts, and image plus sized images including originals. Flat 1 credit."
    ),
)
async def pin_details(
    url: str = Query(..., description="Pinterest pin URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _require_pinterest_pin_url(url)
    settings = get_settings()
    async with billed_call(
        caller=caller,
        endpoint="/v1/pinterest/pin-details",
        platform="pinterest",
        resource_url=url,
        base_credits=CREDIT_DETAILS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            pin_id = extract_pinterest_pin_id(url)
            if pin_id:
                pidgets = await _fetch_pin_pidgets(pin_id)
                if pidgets:
                    ctx["source"] = "direct"
                    # Page hydrate fills createdAt / title / seoAltText / reactions
                    # that pidgets omit — still one credit, same endpoint.
                    return await _enrich_pin_from_page(pin_id, pidgets)
            apify = get_apify()
            try:
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_PINTEREST,
                    {"mode": "pinDetail", "pinUrls": [url], "maxItems": 1},
                    max_items=1,
                )
            except Exception:
                items = []
            if items:
                ctx["source"] = "apify"
                normalized = _normalize_pin(items[0])
                if pin_id and (
                    not normalized.get("createdAt")
                    or not normalized.get("title")
                    or not normalized.get("seoAltText")
                ):
                    return await _enrich_pin_from_page(pin_id, normalized)
                return normalized
            ctx["source"] = "direct"
            return await _fetch_pin_page(url)

        data = await cached_or_run(
            endpoint="pinterest.pin-details",
            params={"url": url, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/user-pins", summary="List pins for a Pinterest profile")
async def user_pins(
    url: str = Query(..., description="Pinterest profile URL or username"),
    limit: int = Query(25, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _require_pinterest_username(url)
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/pinterest/user-pins",
        platform="pinterest",
        resource_url=f"https://www.pinterest.com/{username}/",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_items = await native.user_pins_native(username, limit=limit)
            if native_items:
                ctx["source"] = "direct"
                pins = _prefer_enriched([_normalize_pin(i) for i in native_items])[:limit]
                pins = await _enrich_sparse_pins(pins)
                return {"username": username, "totalReturned": len(pins), "pins": pins}

            items = await _run_pinterest_actor(
                {"mode": "userPins", "usernames": [username], "maxItems": limit}, limit
            )
            pins = _prefer_enriched([_normalize_pin(i) for i in items if i.get("recordType") != "board"])[:limit]
            pins = await _enrich_sparse_pins(pins)
            if not pins:
                raise HTTPException(status_code=404, detail="No pins found")
            ctx["source"] = "apify"
            return {"username": username, "totalReturned": len(pins), "pins": pins}

        data = await cached_or_run(
            endpoint="pinterest.user-pins",
            params={"username": username, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["pins"]), RATE, 2)
        return ApiResponse(data=data)


def _normalize_board(item: dict[str, Any], username: str | None = None) -> dict[str, Any]:
    raw_url = item.get("boardUrl") or item.get("url")
    url = safe_str(raw_url)
    if url and url.startswith("/"):
        url = f"https://www.pinterest.com{url}"
    owner = item.get("owner") if isinstance(item.get("owner"), dict) else {}
    slug = safe_str(item.get("boardSlug") or item.get("slug"))
    # Sparse actor rows only expose slug/name/url — derive a stable id from the URL path.
    board_id = safe_str(item.get("id") or item.get("boardId"))
    if not board_id and url:
        parts = [p for p in url.rstrip("/").split("/") if p]
        if len(parts) >= 2:
            board_id = f"{parts[-2]}/{parts[-1]}"
    cover = item.get("cover") if isinstance(item.get("cover"), dict) else {}
    cover_images = cover.get("images") if isinstance(cover.get("images"), dict) else {}
    cover_orig = cover_images.get("orig") if isinstance(cover_images.get("orig"), dict) else {}
    cover_hd = cover_images.get("474x") if isinstance(cover_images.get("474x"), dict) else {}
    # Prefer HD cover (474x) over 200x150 thumbnail.
    cover_image = safe_str(
        item.get("image_cover_hd_url")
        or item.get("coverImageHdUrl")
        or item.get("image_cover_url")
        or item.get("coverImageUrl")
        or item.get("coverImage")
        or cover_hd.get("url")
        or cover.get("url")
        or cover_orig.get("url")
        or item.get("image_thumbnail_url")
    )
    owner_username = safe_str(
        owner.get("username")
        or item.get("ownerUsername")
        or item.get("creator")
        or username
    )
    owner_display = safe_str(
        owner.get("full_name")
        or owner.get("fullName")
        or owner.get("displayName")
        or item.get("ownerName")
        or item.get("creatorFullName")
    )
    # Core identity through strip_empty; additive analytics keys always present
    # so list clients never see two shapes in one response.
    out = strip_empty(
        {
            "platform": "pinterest",
            "id": board_id,
            "name": safe_str(item.get("boardName") or item.get("name") or item.get("title")),
            "slug": slug,
            "url": url,
        }
    )
    out.update(
        {
            "description": safe_str(item.get("description") or item.get("boardDescription")),
            "privacy": safe_str(item.get("privacy") or item.get("boardPrivacy")),
            "pinCount": safe_int(
                item.get("pinCount")
                or item.get("pin_count")
                or item.get("pinsCount")
                or item.get("pin_count_mod")
            ),
            # Board-scoped followers only — never account-scale board.follower_count.
            "followers": _board_scoped_followers(item),
            "sectionCount": safe_int(item.get("sectionCount") or item.get("section_count")),
            "coverImage": cover_image,
            "createdAt": _created_at_iso(
                item.get("createdDate") or item.get("created_at") or item.get("createdAt")
            ),
            "owner": {
                "username": owner_username,
                "displayName": owner_display,
            },
        }
    )
    return out


@router.get("/user-boards", summary="List the boards on a Pinterest profile")
async def pinterest_user_boards(
    url: str = Query(..., description="Pinterest profile URL or username"),
    limit: int = Query(25, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    username = _require_pinterest_username(url)
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/pinterest/user-boards",
        platform="pinterest",
        resource_url=f"https://www.pinterest.com/{username}/",
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_items = await native.user_boards_native(username, limit=limit)
            if native_items:
                ctx["source"] = "direct"
                boards = [_normalize_board(i, username) for i in native_items][:limit]
                return {"username": username, "totalReturned": len(boards), "boards": boards}

            items = await _run_pinterest_actor(
                {"mode": "userBoards", "usernames": [username], "maxItems": limit}, limit
            )
            boards = [_normalize_board(i, username) for i in items][:limit]
            if not boards:
                raise HTTPException(status_code=404, detail="No boards found")
            ctx["source"] = "apify"
            return {"username": username, "totalReturned": len(boards), "boards": boards}

        data = await cached_or_run(
            endpoint="pinterest.user-boards",
            params={"username": username, "limit": limit, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["boards"]), RATE, 2)
        return ApiResponse(data=data)


def _is_board_url(url: str) -> bool:
    return bool(
        re.match(
            r"^https?://(?:[a-z]{2,3}\.)?pinterest\.[a-z.]+/[^/]+/[^/]+/?",
            (url or "").strip(),
            flags=re.IGNORECASE,
        )
    )


def _board_list_payload(board_url: str, pins: list[dict[str, Any]]) -> dict[str, Any]:
    """Board list response: hoist full author once; slim per-pin author."""
    top_author: dict[str, Any] | None = None
    board_name: str | None = None
    board_canonical = board_url
    for pin in pins:
        if top_author is None and isinstance(pin.get("author"), dict) and pin["author"].get("username"):
            top_author = dict(pin["author"])
        b = pin.get("board") if isinstance(pin.get("board"), dict) else {}
        if not board_name and b.get("name"):
            board_name = safe_str(b.get("name"))
        if b.get("url"):
            board_canonical = safe_str(b.get("url")) or board_canonical
    slim_pins: list[dict[str, Any]] = []
    for pin in pins:
        row = dict(pin)
        if isinstance(row.get("author"), dict):
            row["author"] = _slim_list_author(row["author"])
        slim_pins.append(row)
    out: dict[str, Any] = {
        "board": board_canonical,
        "totalReturned": len(slim_pins),
        "pins": slim_pins,
    }
    if board_name:
        out["boardName"] = board_name
    if top_author:
        out["author"] = top_author
    return out


@router.get(
    "/board",
    summary="List pins inside a Pinterest board",
    description=(
        "Pins on a public board: saves (repin metric), title when exposed, "
        "image + imageOriginal + images{}, destinationUrl, top-level author{} "
        "(pinner) with slim per-pin author. Flat ~0.5 credits/pin (min 2). "
        "Native pidgets soft-cap ~50–100 pins; no cursor yet."
    ),
)
async def pinterest_board(
    url: str = Query(
        ...,
        description="Pinterest board URL (.../username/board-name/), not a /pin/ URL.",
    ),
    limit: int = Query(25, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    _reject_pinterest_platform_mismatch(url, "https://www.pinterest.com/username/board-name/")
    if not _is_board_url(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest board URL")
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/pinterest/board",
        platform="pinterest",
        resource_url=url,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native_items = await native.board_pins_native(url, limit=limit)
            if native_items:
                ctx["source"] = "direct"
                pins = _prefer_enriched([_normalize_pin(i) for i in native_items])[:limit]
                pins = await _enrich_sparse_pins(pins, max_enrich=min(limit, 15))
                return _board_list_payload(url, pins)

            items = await _run_pinterest_actor(
                {"mode": "boardPins", "boardUrls": [url], "maxItems": limit}, limit
            )
            pins = _prefer_enriched([_normalize_pin(i) for i in items if i.get("recordType") != "board"])[:limit]
            pins = await _enrich_sparse_pins(pins, max_enrich=min(limit, 15))
            if not pins:
                raise HTTPException(status_code=404, detail="No pins found")
            ctx["source"] = "apify"
            return _board_list_payload(url, pins)

        data = await cached_or_run(
            endpoint="pinterest.board",
            params={"url": url, "limit": limit, "v": 6},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["pins"]), RATE, 2)
        return ApiResponse(data=data)


@router.get("/search", summary="Search Pinterest pins by keyword")
async def pinterest_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, ge=1, le=200),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    cost = _scaled(limit, RATE, 2)
    async with billed_call(
        caller=caller,
        endpoint="/v1/pinterest/search",
        platform="pinterest",
        resource_url=None,
        base_credits=cost,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            # 1) SERP → pidgets (logged-out Pinterest search HTML is empty).
            native_items = await native.search_pins_native(q, limit=limit)
            if native_items:
                ctx["source"] = "direct"
                results = _prefer_enriched([_normalize_pin(i) for i in native_items])[:limit]
                results = await _enrich_sparse_pins(results, max_enrich=limit)
                return {"query": q, "totalReturned": len(results), "results": results}

            items = await _run_pinterest_actor(
                {"mode": "search", "keywords": [q], "maxItems": limit}, limit
            )
            ctx["source"] = "apify"
            results = _prefer_enriched([_normalize_pin(i) for i in items if i.get("recordType") != "board"])[:limit]
            results = await _enrich_sparse_pins(results)
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="pinterest.search",
            params={"q": q, "limit": limit, "v": 5},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        if ctx.get("source") == "direct":
            ctx["credits_override"] = max(1, _scaled(len(data["results"]), RATE, 1))
        else:
            ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
