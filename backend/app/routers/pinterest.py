"""Pinterest endpoints: pin details, user pins, search.

Backed by a config-driven Pinterest actor. Field mappings are defensive.
"""

from __future__ import annotations

import asyncio
import html
import math
import re
from typing import Any

import httpx
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
    extract_pinterest_pin_id,
    extract_pinterest_username,
    platform_mismatch_detail,
)

router = APIRouter()

CREDIT_DETAILS = 1
RATE = 0.5


def _scaled(n: int, rate: float, minimum: int) -> int:
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


def _image(item: dict[str, Any]) -> str | None:
    imgs = item.get("images") or item.get("image")
    if isinstance(imgs, dict):
        for key in ("orig", "736x", "564x", "474x"):
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
    board = item.get("board") if isinstance(item.get("board"), dict) else {}
    pin_id = item.get("id") or item.get("pinId") or item.get("pin_id")
    pin_url = item.get("url") or item.get("pinUrl") or item.get("pin_url")
    board_url = safe_str(item.get("boardUrl") or board.get("url"))
    if board_url and board_url.startswith("/"):
        board_url = f"https://www.pinterest.com{board_url}"
    return {
        "platform": "pinterest",
        "id": safe_str(pin_id),
        "url": safe_str(pin_url)
        or (f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else None),
        "title": safe_str(
            item.get("title")
            or item.get("grid_title")
            or item.get("closeup_unified_title")
            or item.get("gridTitle")
        ),
        "description": safe_str(
            item.get("description")
            or item.get("altText")
            or item.get("autoAltText")
            or item.get("alt_text")
        ),
        "destinationUrl": safe_str(
            item.get("link")
            or item.get("destinationUrl")
            or item.get("sourceLink")
            or item.get("linkUrl")
            or item.get("clickThroughUrl")
        ),
        "image": _image(item),
        "saves": safe_int(
            item.get("repin_count")
            or item.get("saveCount")
            or item.get("repinCount")
            or item.get("save_count")
            or item.get("saves")
            or item.get("reactionCount")
            or item.get("aggregateSaveCount")
        ),
        "comments": safe_int(
            item.get("comment_count")
            or item.get("commentCount")
            or item.get("commentsCount")
            or ((item.get("aggregated_pin_data") or {}).get("comment_count") if isinstance(item.get("aggregated_pin_data"), dict) else None)
        ),
        "publishedAt": safe_str(
            item.get("created_at")
            or item.get("createdAt")
            or item.get("createdDate")
            or item.get("date")
        ),
        "board": {
            "name": safe_str(item.get("boardName") or board.get("name")),
            "url": board_url,
        },
        "author": {
            "username": safe_str(
                pinner.get("username")
                or item.get("pinner_username")
                or item.get("creator")
                or item.get("creatorUsername")
            ),
            "displayName": safe_str(
                pinner.get("full_name")
                or pinner.get("fullName")
                or item.get("pinner_name")
                or item.get("creatorFullName")
                or item.get("creatorName")
            ),
            "followers": safe_int(
                pinner.get("follower_count")
                or pinner.get("followerCount")
                or item.get("creatorFollowerCount")
            ),
        },
    }


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


async def _enrich_sparse_pins(pins: list[dict[str, Any]], *, max_enrich: int = 10) -> list[dict[str, Any]]:
    """Fill title/saves/etc for stub actor rows via Pinterest's public pidgets API."""
    to_enrich = [p for p in pins if p.get("id") and not p.get("title")][:max_enrich]
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
        for key in ("title", "description", "destinationUrl", "saves", "comments", "publishedAt", "image"):
            if not merged.get(key) and detail.get(key):
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
    pinner = pin.get("pinner") or {}
    board = pin.get("board") or {}
    stats = ((pin.get("aggregated_pin_data") or {}).get("aggregated_stats")) or {}
    images = pin.get("images") or {}
    image = None
    for key in ("originals", "orig", "736x", "564x", "474x", "237x"):
        entry = images.get(key)
        if isinstance(entry, dict) and entry.get("url"):
            image = entry["url"]
            break
    if not image:
        # story pins keep images inside story_pin_data pages
        for page in ((pin.get("story_pin_data") or {}).get("pages")) or []:
            for block in (page.get("blocks") or []) if isinstance(page, dict) else []:
                block_images = ((block.get("image") or {}).get("images")) if isinstance(block, dict) else None
                if isinstance(block_images, dict):
                    for key in ("originals", "736x", "474x"):
                        entry = block_images.get(key)
                        if isinstance(entry, dict) and entry.get("url"):
                            image = entry["url"]
                            break
                if image:
                    break
            if image:
                break
    username = None
    profile_url = safe_str(pinner.get("profile_url"))
    if profile_url:
        username = profile_url.rstrip("/").rsplit("/", 1)[-1]
    board_url = safe_str(board.get("url"))
    rich = pin.get("rich_metadata") if isinstance(pin.get("rich_metadata"), dict) else {}
    rich_summary = pin.get("rich_summary") if isinstance(pin.get("rich_summary"), dict) else {}
    title = safe_str(
        rich.get("title")
        or pin.get("grid_title")
        or pin.get("closeup_unified_title")
        or rich_summary.get("display_name")
        or pin.get("title")
        or pin.get("description")
    )
    return {
        "platform": "pinterest",
        "id": safe_str(pin.get("id") or pin_id),
        "url": f"https://www.pinterest.com/pin/{pin_id}/",
        "title": title,
        "description": safe_str(
            pin.get("description") or pin.get("auto_alt_text") or pin.get("alt_text")
        ),
        "destinationUrl": safe_str(pin.get("link") or rich.get("url")),
        "image": safe_str(image),
        "isVideo": bool(pin.get("is_video")),
        "dominantColor": safe_str(pin.get("dominant_color")),
        "saves": safe_int(stats.get("saves") or pin.get("repin_count") or pin.get("share_count")),
        "comments": safe_int(
            pin.get("comment_count")
            or stats.get("comments")
            or ((pin.get("aggregated_pin_data") or {}).get("comment_count") if isinstance(pin.get("aggregated_pin_data"), dict) else None)
        ),
        "publishedAt": safe_str(pin.get("created_at")),
        "board": {
            "name": safe_str(board.get("name")),
            "url": f"https://www.pinterest.com{board_url}" if board_url and board_url.startswith("/") else board_url,
            "pinCount": safe_int(board.get("pin_count")),
            "followers": safe_int(board.get("follower_count")),
        },
        "author": {
            "username": safe_str(username),
            "displayName": safe_str(pinner.get("full_name")),
            "url": profile_url,
            "followers": safe_int(pinner.get("follower_count")),
            "pinCount": safe_int(pinner.get("pin_count")),
            "avatar": safe_str(pinner.get("image_small_url")),
        },
    }


async def _fetch_pin_page(url: str) -> dict[str, Any]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
    if resp.status_code >= 400:
        raise HTTPException(status_code=404, detail="Pin not found")

    page = resp.text
    pin_id = extract_pinterest_pin_id(str(resp.url)) or extract_pinterest_pin_id(url)
    title = _meta(page, "og:title") or _json_string(page, "title") or _html_title(page)
    description = (
        _meta(page, "og:description")
        or _meta(page, "description")
        or _json_string(page, "description")
    )
    image = _meta(page, "og:image")
    canonical = _meta(page, "og:url") or str(resp.url)
    if not (title or description or image):
        raise HTTPException(status_code=404, detail="Pin not found")

    return {
        "platform": "pinterest",
        "id": safe_str(pin_id),
        "url": safe_str(canonical),
        "title": safe_str(title),
        "description": safe_str(description),
        "destinationUrl": None,
        "image": safe_str(image),
        "saves": 0,
        "comments": 0,
        "publishedAt": None,
        "author": {"username": None, "displayName": None, "followers": 0},
    }


@router.get("/pin-details", summary="Pinterest pin metadata + stats")
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
                    return pidgets
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
                return _normalize_pin(items[0])
            return await _fetch_pin_page(url)

        data = await cached_or_run(
            endpoint="pinterest.pin-details",
            params={"url": url, "v": 2},
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
            items = await _run_pinterest_actor(
                {"mode": "userPins", "usernames": [username], "maxItems": limit}, limit
            )
            pins = _prefer_enriched([_normalize_pin(i) for i in items if i.get("recordType") != "board"])[:limit]
            pins = await _enrich_sparse_pins(pins)
            return {"username": username, "totalReturned": len(pins), "pins": pins}

        data = await cached_or_run(
            endpoint="pinterest.user-pins",
            params={"username": username, "limit": limit, "v": 3},
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
    return {
        "platform": "pinterest",
        "id": board_id,
        "name": safe_str(item.get("boardName") or item.get("name") or item.get("title")),
        "slug": slug,
        "url": url,
        "privacy": safe_str(item.get("privacy") or item.get("boardPrivacy")),
        "pinCount": safe_int(
            item.get("pinCount") or item.get("pin_count") or item.get("pinsCount") or item.get("pin_count_mod")
        ),
        "followers": safe_int(
            item.get("followerCount") or item.get("follower_count") or item.get("followers")
        ),
        "sectionCount": safe_int(item.get("sectionCount") or item.get("section_count")),
        "coverImage": safe_str(
            item.get("coverImageHdUrl")
            or item.get("coverImageUrl")
            or item.get("image_cover_url")
            or item.get("coverImage")
            or cover.get("url")
            or cover_orig.get("url")
        ),
        "createdAt": safe_str(item.get("createdDate") or item.get("created_at") or item.get("createdAt")),
        "owner": {
            "username": safe_str(
                owner.get("username")
                or item.get("ownerUsername")
                or item.get("creator")
                or username
            ),
            "displayName": safe_str(
                owner.get("full_name") or item.get("ownerName") or item.get("creatorFullName")
            ),
        },
    }


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
            items = await _run_pinterest_actor(
                {"mode": "userBoards", "usernames": [username], "maxItems": limit}, limit
            )
            boards = [_normalize_board(i, username) for i in items][:limit]
            return {"username": username, "totalReturned": len(boards), "boards": boards}

        data = await cached_or_run(
            endpoint="pinterest.user-boards",
            params={"username": username, "limit": limit, "v": 3},
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


@router.get("/board", summary="List pins inside a Pinterest board")
async def pinterest_board(
    url: str = Query(..., description="Pinterest board URL (.../username/board-name/)"),
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
            items = await _run_pinterest_actor(
                {"mode": "boardPins", "boardUrls": [url], "maxItems": limit}, limit
            )
            pins = _prefer_enriched([_normalize_pin(i) for i in items if i.get("recordType") != "board"])[:limit]
            pins = await _enrich_sparse_pins(pins)
            return {"board": url, "totalReturned": len(pins), "pins": pins}

        data = await cached_or_run(
            endpoint="pinterest.board",
            params={"url": url, "limit": limit, "v": 3},
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
            items = await _run_pinterest_actor(
                {"mode": "search", "keywords": [q], "maxItems": limit}, limit
            )
            results = _prefer_enriched([_normalize_pin(i) for i in items if i.get("recordType") != "board"])[:limit]
            return {"query": q, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            endpoint="pinterest.search",
            params={"q": q, "limit": limit, "v": 2},
            runner=_run,
            ctx=ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["results"]), RATE, 2)
        return ApiResponse(data=data)
