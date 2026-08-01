"""Self-scraped YouTube data from public pages + InnerTube (no Apify).

Every function returns data in the exact shapes the routers already emit, or
``None``/``[]`` on failure so callers can fall back to the Apify actors.

Approach:
- List pages (search results, channel tabs, hashtag pages) embed
  ``ytInitialData``; we parse the video renderers straight out of it and follow
  one continuation via InnerTube when the caller wants more than one page.
- Channel metadata comes from the channel page (``channelMetadataRenderer``)
  plus the About popup fetched through InnerTube ``browse``.
- Transcripts come from InnerTube ANDROID player caption tracks (direct egress
  first — proxy IPs often get LOGIN_REQUIRED; web watch timedtext needs a PoT).
- Community posts come from the channel ``/posts`` tab ``ytInitialData`` plus
  InnerTube browse continuations.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from typing import Any, Iterator
from urllib.parse import parse_qs, urlparse

import httpx

from app.services.http_fetch import fetch as proxy_fetch, post_json, proxy_for
from app.utils.formatters import safe_int, safe_list, safe_str

YT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
# CONSENT/SOCS skip the EU consent wall; PREF pins English so count/date text
# parses predictably.
YT_COOKIES: dict[str, str] = {"CONSENT": "YES+1", "SOCS": "CAI", "PREF": "hl=en&gl=US"}

_INNERTUBE_CLIENT_VERSION = "2.20250313.00.00"
_INNERTUBE_CONTEXT = {
    "client": {
        "clientName": "WEB",
        "clientVersion": _INNERTUBE_CLIENT_VERSION,
        "hl": "en",
        "gl": "US",
    }
}
# Channel tab browse ``params`` (protobuf) — same values yt-dlp / web UI use.
_CHANNEL_TAB_PARAMS: dict[str, str] = {
    "videos": "EgZ2aWRlb3PyBgQKAjoA",
    "shorts": "EgZzaG9ydHPyBgUKA5oBAA%3D%3D",
    "streams": "EgdzdHJlYW1z8gYECgJ6AA%3D%3D",
    "playlists": "EglwbGF5bGlzdHPyBgQKAkIA",
    "about": "EgVhYm91dPIGBAoCEgA%3D",
}
# Shorts filter for InnerTube ``search`` (same as ``sp=EgIYAQ==`` on /results).
_SEARCH_SHORTS_PARAMS = "EgIYAQ=="

_JSON_DECODER = json.JSONDecoder()


def extract_initial_json(html: str, var_name: str) -> dict[str, Any] | None:
    """Pull an embedded ``var X = {...};`` blob out of a YouTube page.

    The objects are megabytes long with trailing script on the same line, so a
    regex can't find the closing brace; ``raw_decode`` reads exactly one JSON
    value from the opening ``{``.
    """
    for anchor in (f"var {var_name} = ", f'window["{var_name}"] = ', f"{var_name} = "):
        idx = html.find(anchor)
        if idx == -1:
            continue
        start = html.find("{", idx)
        if start == -1:
            continue
        try:
            obj, _ = _JSON_DECODER.raw_decode(html, start)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def text_of(node: Any) -> str | None:
    """Extract text from YouTube's ``{simpleText}`` / ``{runs: [{text}]}`` /
    ``{content}`` shapes."""
    if node is None:
        return None
    if isinstance(node, str):
        return node or None
    if isinstance(node, dict):
        if node.get("simpleText"):
            return str(node["simpleText"])
        if node.get("content"):
            return str(node["content"])
        runs = node.get("runs")
        if isinstance(runs, list):
            joined = "".join(str(r.get("text") or "") for r in runs if isinstance(r, dict))
            return joined or None
    return None


_COUNT_RE = re.compile(r"([\d.,]+)\s*([KMB])?", re.IGNORECASE)
_MULT = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}


def parse_count_text(value: Any) -> int | None:
    """Parse '1,234,567 views', '1.2M views', '123K', 'No views' -> int."""
    s = text_of(value) if not isinstance(value, str) else value
    if not s:
        return None
    if "no views" in s.lower():
        return 0
    m = _COUNT_RE.search(s.replace("\u00a0", " "))
    if not m:
        return None
    num, suffix = m.group(1), (m.group(2) or "").upper()
    try:
        base = float(num.replace(",", ""))
    except ValueError:
        return None
    return int(base * _MULT.get(suffix, 1))


def walk_find(node: Any, key: str) -> Iterator[dict[str, Any]]:
    """Yield every dict found under ``key`` anywhere in the tree."""
    if isinstance(node, dict):
        found = node.get(key)
        if isinstance(found, dict):
            yield found
        for v in node.values():
            yield from walk_find(v, key)
    elif isinstance(node, list):
        for v in node:
            yield from walk_find(v, key)


def _duration_text_seconds(value: Any) -> int | None:
    s = text_of(value)
    if not s or not re.fullmatch(r"\d+(?::\d{1,2}){0,2}", s.strip()):
        return None
    total = 0
    for part in s.strip().split(":"):
        total = total * 60 + int(part)
    return total


def _best_thumb(node: Any) -> str | None:
    """Last (largest) thumbnail URL from ``{thumbnails: [...]}`` or
    ``{sources: [...]}``."""
    if not isinstance(node, dict):
        return None
    arr = node.get("thumbnails") or node.get("sources")
    if isinstance(arr, list) and arr and isinstance(arr[-1], dict):
        return safe_str(arr[-1].get("url"))
    for v in node.values():
        found = _best_thumb(v) if isinstance(v, dict) else None
        if found:
            return found
    return None


def normalize_video_renderer(vr: dict[str, Any]) -> dict[str, Any] | None:
    """``videoRenderer`` (search / channel tabs / hashtag) -> our video card."""
    video_id = safe_str(vr.get("videoId"))
    if not video_id:
        return None
    view_count = parse_count_text(vr.get("viewCountText"))
    if view_count is None:
        view_count = parse_count_text(vr.get("shortViewCountText"))
    return {
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": text_of(vr.get("title")) or "",
        "publishedAt": text_of(vr.get("publishedTimeText")),
        "viewCount": view_count,
        "durationSeconds": _duration_text_seconds(vr.get("lengthText")),
        "thumbnailUrl": _best_thumb(vr.get("thumbnail")),
        "channelName": text_of(vr.get("ownerText") or vr.get("longBylineText") or vr.get("shortBylineText")),
    }


def _normalize_shorts_lockup(lk: dict[str, Any]) -> dict[str, Any] | None:
    """``shortsLockupViewModel`` (2024+ shorts shelf) -> our video card."""
    on_tap = lk.get("onTap") or {}
    video_id = safe_str(
        (((on_tap.get("innertubeCommand") or {}).get("reelWatchEndpoint")) or {}).get("videoId")
    )
    if not video_id:
        entity = safe_str(lk.get("entityId"))
        m = re.search(r"([\w-]{11})$", entity or "")
        video_id = m.group(1) if m else None
    if not video_id:
        return None
    overlay = lk.get("overlayMetadata") or {}
    return {
        "url": f"https://www.youtube.com/shorts/{video_id}",
        "title": text_of((overlay.get("primaryText") or {})) or "",
        "publishedAt": None,
        "viewCount": parse_count_text(overlay.get("secondaryText")),
        "durationSeconds": None,
        "thumbnailUrl": _best_thumb(lk.get("thumbnail")),
        "channelName": None,
    }


def _normalize_reel_item(r: dict[str, Any]) -> dict[str, Any] | None:
    """Legacy ``reelItemRenderer`` -> our video card."""
    video_id = safe_str(r.get("videoId"))
    if not video_id:
        return None
    return {
        "url": f"https://www.youtube.com/shorts/{video_id}",
        "title": text_of(r.get("headline")) or "",
        "publishedAt": None,
        "viewCount": parse_count_text(r.get("viewCountText")),
        "durationSeconds": None,
        "thumbnailUrl": _best_thumb(r.get("thumbnail")),
        "channelName": None,
    }


def _normalize_video_lockup(lk: dict[str, Any]) -> dict[str, Any] | None:
    """``lockupViewModel`` video card used on modern channel tabs."""
    if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO":
        return None
    video_id = safe_str(lk.get("contentId"))
    if not video_id:
        ctx = ((lk.get("rendererContext") or {}).get("commandContext") or {}).get("onTap") or {}
        video_id = safe_str(((ctx.get("innertubeCommand") or {}).get("watchEndpoint") or {}).get("videoId"))
    if not video_id:
        return None

    meta = (lk.get("metadata") or {}).get("lockupMetadataViewModel") or {}
    title = text_of(meta.get("title")) or ""
    rows = (((meta.get("metadata") or {}).get("contentMetadataViewModel") or {}).get("metadataRows")) or []
    parts: list[str] = []
    for row in rows:
        for part in row.get("metadataParts") or []:
            txt = text_of(part.get("text"))
            if txt:
                parts.append(txt)

    # Metadata parts vary by page variant: ["Channel", "1.1M views", "2 days ago"]
    # or the compact form ["Channel", "1.7M", "5d ago"] without the word "views".
    channel_name = None
    view_count = None
    published_at = None
    for txt in parts:
        low = txt.lower()
        stripped = txt.strip()
        if view_count is None and (
            "view" in low or re.fullmatch(r"[\d.,]+\s*[KMB]?", stripped, re.IGNORECASE)
        ):
            view_count = parse_count_text(txt)
        elif published_at is None and any(
            word in low for word in ("ago", "premiere", "streamed", "scheduled")
        ):
            published_at = txt
        elif channel_name is None:
            channel_name = txt

    duration = None
    for badge in walk_find(lk.get("contentImage"), "thumbnailBadgeViewModel"):
        duration = _duration_text_seconds(badge.get("text"))
        if duration is not None:
            break

    return {
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": title,
        "publishedAt": published_at,
        "viewCount": view_count,
        "durationSeconds": duration,
        "thumbnailUrl": _best_thumb(lk.get("contentImage")),
        "channelName": channel_name,
    }


def _normalize_playlist_video(pv: dict[str, Any]) -> dict[str, Any] | None:
    """``playlistVideoRenderer`` on /playlist pages -> our video card."""
    video_id = safe_str(pv.get("videoId"))
    if not video_id:
        return None
    view_count = None
    published_at = None
    for run in (pv.get("videoInfo") or {}).get("runs") or []:
        txt = safe_str(run.get("text")) or ""
        low = txt.lower()
        if "view" in low:
            view_count = parse_count_text(txt)
        elif "ago" in low or "streamed" in low:
            published_at = txt
    secs = safe_str(pv.get("lengthSeconds"))
    duration = int(secs) if secs and secs.isdigit() else _duration_text_seconds(pv.get("lengthText"))
    return {
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": text_of(pv.get("title")) or "",
        "publishedAt": published_at,
        "viewCount": view_count,
        "durationSeconds": duration,
        "thumbnailUrl": _best_thumb(pv.get("thumbnail")),
        "channelName": text_of(pv.get("shortBylineText")),
    }


def collect_video_cards(data: Any, *, shorts: bool = False) -> list[dict[str, Any]]:
    """All video cards in a ytInitialData tree / continuation payload."""
    cards: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(card: dict[str, Any] | None) -> None:
        if card and card["url"] not in seen:
            seen.add(card["url"])
            cards.append(card)

    if shorts:
        for lk in walk_find(data, "shortsLockupViewModel"):
            add(_normalize_shorts_lockup(lk))
        for r in walk_find(data, "reelItemRenderer"):
            add(_normalize_reel_item(r))
        # Some Shorts tabs / filtered search still emit video lockups.
        for vr in walk_find(data, "videoRenderer"):
            card = normalize_video_renderer(vr)
            if card:
                vid = card["url"].rsplit("v=", 1)[-1]
                card["url"] = f"https://www.youtube.com/shorts/{vid}"
                add(card)
        for lk in walk_find(data, "lockupViewModel"):
            card = _normalize_video_lockup(lk)
            if card:
                vid = card["url"].rsplit("v=", 1)[-1]
                card["url"] = f"https://www.youtube.com/shorts/{vid}"
                add(card)
    else:
        for vr in walk_find(data, "videoRenderer"):
            add(normalize_video_renderer(vr))
        for pv in walk_find(data, "playlistVideoRenderer"):
            add(_normalize_playlist_video(pv))
        for lk in walk_find(data, "lockupViewModel"):
            add(_normalize_video_lockup(lk))
    return cards


def find_continuation_tokens(data: Any) -> list[str]:
    """All continuation tokens in document order (deduped)."""
    out: list[str] = []
    seen: set[str] = set()
    for c in walk_find(data, "continuationCommand"):
        token = safe_str(c.get("token"))
        if token and token not in seen:
            seen.add(token)
            out.append(token)
    return out


def find_continuation_token(data: Any) -> str | None:
    tokens = find_continuation_tokens(data)
    return tokens[0] if tokens else None


def _proxy_tiers() -> list[str]:
    """Datacenter first (cheap/fast); residential if configured."""
    tiers: list[str] = ["datacenter"]
    if proxy_for("residential"):
        tiers.append("residential")
    return tiers


def _player_tiers() -> list[str]:
    """Egress order for InnerTube ``player`` / timedtext.

    Proxy IPs often get ``LOGIN_REQUIRED`` ("confirm you're not a bot") while
    the host's own IP still returns ``OK`` + caption tracks. Try direct first,
    then the configured proxy pools.
    """
    tiers: list[str] = ["none"]
    for t in _proxy_tiers():
        if t not in tiers:
            tiers.append(t)
    return tiers


async def fetch_page_data(url: str, *, timeout: float = 12.0) -> tuple[dict[str, Any] | None, str]:
    """GET a YouTube page and return (ytInitialData, raw html)."""
    last_html = ""
    for tier in _proxy_tiers():
        try:
            resp = await proxy_fetch(
                url, tier=tier, headers=YT_HEADERS, cookies=YT_COOKIES, timeout=timeout  # type: ignore[arg-type]
            )
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        last_html = resp.text or ""
        data = extract_initial_json(last_html, "ytInitialData")
        if data is not None:
            return data, last_html
    return None, last_html


async def innertube(endpoint: str, body: dict[str, Any], *, timeout: float = 12.0) -> dict[str, Any] | None:
    """POST to InnerTube (web client). ``endpoint``: search | browse | next."""
    for tier in _proxy_tiers():
        try:
            resp = await post_json(
                f"https://www.youtube.com/youtubei/v1/{endpoint}",
                {"context": _INNERTUBE_CONTEXT, **body},
                tier=tier,  # type: ignore[arg-type]
                headers={
                    **YT_HEADERS,
                    "X-Youtube-Client-Name": "1",
                    "X-Youtube-Client-Version": _INNERTUBE_CLIENT_VERSION,
                },
                params={"prettyPrint": "false"},
                timeout=timeout,
            )
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        try:
            data = resp.json()
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


async def _paginate(
    first_page: Any,
    *,
    limit: int,
    continuation_endpoint: str,
    shorts: bool = False,
    max_hops: int = 8,
) -> list[dict[str, Any]]:
    """Cards from the initial tree plus InnerTube continuations up to limit."""
    cards = collect_video_cards(first_page, shorts=shorts)
    pending = find_continuation_tokens(first_page)
    hops = 0
    while pending and len(cards) < limit and hops < max_hops:
        token = pending.pop(0)
        payload = await innertube(continuation_endpoint, {"continuation": token})
        if payload is None:
            continue
        new_cards = collect_video_cards(payload, shorts=shorts)
        existing = {c["url"] for c in cards}
        added = [c for c in new_cards if c["url"] not in existing]
        hops += 1
        if not added:
            # Wrong token (shelf / related) — try the next candidate.
            for nxt in find_continuation_tokens(payload):
                if nxt not in pending:
                    pending.append(nxt)
            continue
        cards.extend(added)
        pending = find_continuation_tokens(payload) + pending
        # Dedupe pending while preserving order.
        seen_tok: set[str] = set()
        uniq: list[str] = []
        for t in pending:
            if t not in seen_tok:
                seen_tok.add(t)
                uniq.append(t)
        pending = uniq
    return cards[:limit]


async def resolve_channel_id(url: str) -> str | None:
    """Resolve ``UC…`` from a channel URL, @handle, or bare channel id."""
    raw = (url or "").strip()
    if not raw:
        return None
    if re.fullmatch(r"UC[\w-]{20,}", raw):
        return raw
    m = re.search(r"youtube\.com/channel/(UC[\w-]+)", raw)
    if m:
        return m.group(1)
    # Need a page (or redirect) for @handles / custom URLs.
    page = raw if "://" in raw else f"https://www.youtube.com/{raw.lstrip('/')}"
    data, html = await fetch_page_data(page, timeout=15.0)
    if data:
        meta = next(walk_find(data, "channelMetadataRenderer"), {}) or {}
        cid = safe_str(meta.get("externalId"))
        if cid:
            return cid
    if html:
        found = re.search(r'"externalId":"(UC[\w-]+)"', html) or re.search(
            r'"channelId":"(UC[\w-]+)"', html
        )
        if found:
            return found.group(1)
    return None


# ---------------------------------------------------------------- search ---
async def search_native(q: str, limit: int) -> list[dict[str, Any]]:
    from urllib.parse import quote

    query = (q or "").strip()
    if not query:
        return []
    # InnerTube search avoids HTML 429s on /results.
    data = await innertube("search", {"query": query}, timeout=15)
    if data is not None:
        cards = await _paginate(data, limit=limit, continuation_endpoint="search")
        if cards:
            return cards
    data, _ = await fetch_page_data(
        f"https://www.youtube.com/results?search_query={quote(query)}"
    )
    if data is None:
        return []
    return await _paginate(data, limit=limit, continuation_endpoint="search")


async def search_shorts_native(q: str, limit: int) -> list[dict[str, Any]] | None:
    """Shorts-filtered YouTube search via InnerTube, then HTML ``sp=EgIYAQ==``."""
    from urllib.parse import quote

    seed = (q or "").strip() or "trending"
    data = await innertube(
        "search", {"query": seed, "params": _SEARCH_SHORTS_PARAMS}, timeout=15
    )
    if data is not None:
        cards = await _paginate(
            data, limit=limit, continuation_endpoint="search", shorts=True
        )
        if cards:
            return cards
    data, _ = await fetch_page_data(
        f"https://www.youtube.com/results?search_query={quote(seed)}&sp=EgIYAQ%3D%3D"
    )
    if data is None:
        return None
    cards = await _paginate(data, limit=limit, continuation_endpoint="search", shorts=True)
    return cards if cards else None


# ---------------------------------------------------------------- playlist -
async def playlist_native(url: str, limit: int) -> dict[str, Any] | None:
    """Videos (plus title/channel) straight from a /playlist page."""
    data, _ = await fetch_page_data(url)
    if data is None:
        return None
    videos = await _paginate(data, limit=limit, continuation_endpoint="browse")
    if not videos:
        return None

    title = None
    channel = None
    for meta in walk_find(data, "playlistMetadataRenderer"):
        title = safe_str(meta.get("title"))
        break
    for header in walk_find(data, "playlistHeaderRenderer"):
        title = title or text_of(header.get("title"))
        channel = text_of(header.get("ownerText"))
        break
    if channel is None:
        channel = videos[0].get("channelName")
    return {"title": title, "channelName": channel, "videos": videos}


# ---------------------------------------------------- channel tab lists ---
def _channel_title_from_data(data: Any) -> str | None:
    """Channel display name from browse / channel-page ytInitialData."""
    if not data:
        return None
    meta = next(walk_find(data, "channelMetadataRenderer"), None) or {}
    title = safe_str(meta.get("title"))
    if title:
        return title
    # pageHeaderViewModel.title.dynamicTextViewModel.text.content
    for ph in walk_find(data, "pageHeaderViewModel"):
        dyn = ((ph.get("title") or {}).get("dynamicTextViewModel") or {}).get("text")
        title = safe_str(text_of(dyn))
        if title:
            return title
    return None


def _fill_missing_channel_name(
    cards: list[dict[str, Any]], channel_name: str | None
) -> list[dict[str, Any]]:
    """Channel tabs omit byline; stamp the owning channel onto each card."""
    if not channel_name:
        return cards
    for card in cards:
        if not card.get("channelName"):
            card["channelName"] = channel_name
    return cards


async def channel_tab_native(
    tab_url: str,
    limit: int,
    *,
    shorts: bool = False,
    tab: str | None = None,
) -> list[dict[str, Any]]:
    """Videos / streams / shorts tab of a channel.

    Prefers InnerTube ``browse`` with known tab ``params`` (works when the
    HTML tab is 429'd). Falls back to ``ytInitialData`` on the tab URL.
    """
    tab_key = (tab or "").strip().lower()
    if not tab_key:
        low = (tab_url or "").rstrip("/").lower()
        for name in ("shorts", "streams", "videos", "playlists"):
            if low.endswith("/" + name):
                tab_key = name
                break
    params = _CHANNEL_TAB_PARAMS.get(tab_key) if tab_key else None
    if params:
        channel_id = await resolve_channel_id(tab_url)
        if channel_id:
            data = await innertube(
                "browse",
                {"browseId": channel_id, "params": params},
                timeout=18,
            )
            if data is not None:
                cards = await _paginate(
                    data, limit=limit, continuation_endpoint="browse", shorts=shorts
                )
                if cards:
                    return _fill_missing_channel_name(
                        cards, _channel_title_from_data(data)
                    )
    data, _ = await fetch_page_data(tab_url, timeout=15.0)
    if data is None:
        return []
    cards = await _paginate(data, limit=limit, continuation_endpoint="browse", shorts=shorts)
    return _fill_missing_channel_name(cards, _channel_title_from_data(data))


def collect_playlist_cards(data: Any) -> list[dict[str, Any]]:
    """``LOCKUP_CONTENT_TYPE_PLAYLIST`` rows from a channel playlists tab."""
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for lk in walk_find(data, "lockupViewModel"):
        if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_PLAYLIST":
            continue
        pid = safe_str(lk.get("contentId"))
        if not pid or pid in seen:
            continue
        seen.add(pid)
        meta = (lk.get("metadata") or {}).get("lockupMetadataViewModel") or {}
        title = text_of(meta.get("title")) or ""
        video_count = None
        for badge in walk_find(lk, "thumbnailBadgeViewModel"):
            video_count = parse_count_text(badge.get("text"))
            if video_count is not None:
                break
        if video_count is None:
            blob = json.dumps(lk)
            m = re.search(r"([\d,.]+)\s+videos?", blob)
            if m:
                video_count = safe_int(m.group(1).replace(",", ""))
        rows.append(
            {
                "url": f"https://www.youtube.com/playlist?list={pid}",
                "title": title,
                "videoCount": video_count,
                "thumbnailUrl": _best_thumb(lk.get("contentImage")),
            }
        )
    return rows


async def channel_playlists_native(channel_url: str, limit: int) -> list[dict[str, Any]]:
    """Channel playlists via InnerTube browse, then HTML tab parse."""
    if limit <= 0:
        return []
    channel_id = await resolve_channel_id(channel_url)
    params = _CHANNEL_TAB_PARAMS["playlists"]
    if channel_id:
        data = await innertube(
            "browse",
            {"browseId": channel_id, "params": params},
            timeout=18,
        )
        if data is not None:
            rows = collect_playlist_cards(data)
            if rows:
                return rows[:limit]
    # HTML fallthrough (proxy-aware).
    base = (channel_url or "").rstrip("/")
    for suffix in (
        "/videos",
        "/shorts",
        "/streams",
        "/playlists",
        "/featured",
        "/posts",
        "/community",
    ):
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)]
            break
    data, _ = await fetch_page_data(f"{base}/playlists", timeout=15.0)
    if data is None:
        return []
    return collect_playlist_cards(data)[:limit]


# ---------------------------------------------------------------- hashtag --
async def hashtag_native(tag: str, limit: int) -> list[dict[str, Any]]:
    from urllib.parse import quote

    name = (tag or "").lstrip("#").strip()
    if not name:
        return []
    data, _ = await fetch_page_data(f"https://www.youtube.com/hashtag/{quote(name)}")
    if data is None:
        return []
    return await _paginate(data, limit=limit, continuation_endpoint="browse")


# --------------------------------------------------------- channel details --
_ABOUT_PARAMS = _CHANNEL_TAB_PARAMS["about"]


async def channel_details_native(url: str) -> dict[str, Any] | None:
    """Channel metadata from the channel page + the About popup (InnerTube)."""
    data, html = await fetch_page_data(url)
    if not html:
        return None

    meta: dict[str, Any] = {}
    if data:
        meta = next(walk_find(data, "channelMetadataRenderer"), {}) or {}
    channel_id = safe_str(meta.get("externalId"))
    if not channel_id:
        m = re.search(r'"externalId":"(UC[\w-]+)"', html) or re.search(r'"channelId":"(UC[\w-]+)"', html)
        channel_id = m.group(1) if m else None
    if not channel_id:
        return None

    name = safe_str(meta.get("title"))
    description = safe_str(meta.get("description"))
    avatar = _best_thumb(meta.get("avatar"))
    vanity = safe_str(meta.get("vanityChannelUrl"))
    handle = None
    if vanity and "@" in vanity:
        handle = "@" + vanity.split("@", 1)[1]

    subscriber_count = None
    video_count = None
    banner = None
    if data:
        page_blob = json.dumps(data, ensure_ascii=False)
        header_html = json.dumps(data.get("header") or {}, ensure_ascii=False)
        m = re.search(r"([\d.,]+[KMB]?) subscribers", header_html) or re.search(
            r"([\d.,]+[KMB]?) subscribers", page_blob
        )
        if m:
            subscriber_count = parse_count_text(m.group(1))
        m = re.search(r"([\d.,]+[KMB]?) videos?", header_html) or re.search(
            r"([\d.,]+[KMB]?) videos?", page_blob
        )
        if m:
            video_count = parse_count_text(m.group(1))
        banner = _best_thumb((data.get("header") or {}))

    # About popup: exact view count, joined date, country, links.
    view_count = None
    joined = None
    country = None
    links: list[dict[str, str]] = []
    # Channel page metadata also embeds primaryLinks (often present when the
    # About popup returns an empty links array).
    for link in meta.get("primaryLinks") or []:
        if not isinstance(link, dict):
            continue
        nav = link.get("navigationEndpoint") or {}
        link_url = safe_str(
            (nav.get("urlEndpoint") or {}).get("url")
            or (nav.get("commandMetadata") or {}).get("webCommandMetadata", {}).get("url")
        )
        if link_url and link_url.startswith("/"):
            link_url = f"https://www.youtube.com{link_url}"
        # YouTube wraps external URLs in a redirector — unwrap when present.
        if link_url and "q=" in link_url and "youtube.com/redirect" in link_url:
            q = parse_qs(urlparse(link_url).query).get("q") or []
            if q:
                link_url = q[0]
        link_title = text_of(link.get("title"))
        if link_url:
            links.append({"text": safe_str(link_title) or "", "url": safe_str(link_url) or ""})
    # About fields: InnerTube about-tab params often return the main channel
    # browse without aboutChannelViewModel. Prefer that when present, else
    # fetch /about (ytInitialData still embeds the about view model).
    about: dict[str, Any] | None = None
    about_payload = await innertube(
        "browse", {"browseId": channel_id, "params": _ABOUT_PARAMS}
    )
    if about_payload:
        about = next(walk_find(about_payload, "aboutChannelViewModel"), None)
    if about is None:
        about_data, about_html = await fetch_page_data(
            f"https://www.youtube.com/channel/{channel_id}/about",
            timeout=15,
        )
        if about_data:
            about = next(walk_find(about_data, "aboutChannelViewModel"), None)
        if about is None and about_html:
            html = about_html  # use /about HTML for regex fallbacks below

    if about:
        view_count = parse_count_text(about.get("viewCountText"))
        joined = safe_str(text_of(about.get("joinedDateText")))
        if joined:
            joined = re.sub(r"^joined\s+", "", joined, flags=re.I).strip() or joined
        country = safe_str(text_of(about.get("country"))) or safe_str(about.get("country"))
        if subscriber_count is None:
            subscriber_count = parse_count_text(about.get("subscriberCountText"))
        if video_count is None:
            video_count = parse_count_text(about.get("videoCountText"))
        if not description:
            description = safe_str(text_of(about.get("description")))
        about_links: list[dict[str, str]] = []
        for link in about.get("links") or []:
            view_model = link.get("channelExternalLinkViewModel") or {}
            link_title = text_of(view_model.get("title"))
            link_url = text_of(view_model.get("link"))
            if link_url:
                about_links.append({"text": safe_str(link_title) or "", "url": safe_str(link_url) or ""})
        if about_links:
            links = about_links

    # Last-resort fallbacks from page HTML / metadata JSON.
    if view_count is None:
        m = re.search(r"([\d.,]+[KMB]?)\s+views", html, re.I)
        if m:
            view_count = parse_count_text(m.group(1))
    if country is None:
        country = safe_str(meta.get("country")) or None
        if country is None:
            m = re.search(r'"country"\s*:\s*"([^"]+)"', html)
            if m:
                country = safe_str(m.group(1))
    if joined is None:
        m = re.search(r"Joined\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", html)
        if m:
            joined = safe_str(m.group(1))
        else:
            m = re.search(
                r'"joinedDateText"\s*:\s*\{\s*"content"\s*:\s*"Joined\s+([^"]+)"',
                html,
            ) or re.search(
                r'"joinedDateText"[^}]*?"simpleText"\s*:\s*"Joined\s+([^"]+)"',
                html,
            )
            if m:
                joined = safe_str(m.group(1))

    if not links:
        links = _links_from_html(html)

    verified = None
    if data:
        header_blob = json.dumps(data.get("header") or {})
        verified = "CHECK_CIRCLE" in header_blob or '"BADGE_STYLE_TYPE_VERIFIED"' in header_blob

    # SEO keywords from channelMetadataRenderer (comma/space string or list).
    tags = _channel_tags(meta.get("keywords"))
    if not tags and html:
        m = re.search(r'"keywords"\s*:\s*"([^"]+)"', html)
        if m:
            tags = _channel_tags(m.group(1))

    # Business email when the creator put it in the About/description text or
    # a mailto: link. YouTube's CAPTCHA "View email address" reveal is not scraped.
    email = _email_from_texts(description, *(link.get("url") for link in links))
    if email is None and html:
        email = _email_from_texts(html[:200_000])

    return {
        "url": f"https://www.youtube.com/channel/{channel_id}",
        "id": channel_id,
        "name": name or "",
        "handle": handle,
        "description": description,
        "subscriberCount": subscriber_count,
        "videoCount": video_count,
        "viewCount": view_count,
        "thumbnailUrl": avatar,
        "bannerUrl": banner,
        "country": country,
        "joinedDate": joined,
        "verified": verified,
        "links": links,
        "email": email,
        "tags": tags,
    }


_EMAIL_RE = re.compile(
    r"(?:mailto:)?([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})",
    re.I,
)
# Skip obvious non-contact noise from page chrome / tracking.
_EMAIL_BLOCKLIST = {
    "noreply@",
    "no-reply@",
    "donotreply@",
    "@youtube.com",
    "@google.com",
    "@sentry.io",
    "@example.com",
}


def _channel_tags(raw: Any) -> list[str]:
    """Normalize channel SEO keywords to a clean string list."""
    if raw is None:
        return []
    if isinstance(raw, list):
        out: list[str] = []
        for item in raw:
            s = safe_str(item)
            if s:
                out.append(s)
        return out
    text = safe_str(raw) or ""
    if not text:
        return []
    # YouTube usually comma-separates; fall back to whitespace for rare shapes.
    parts = re.split(r"\s*,\s*", text) if "," in text else text.split()
    return [p.strip() for p in parts if p and p.strip()]


def _email_from_texts(*texts: Any) -> str | None:
    """First plausible contact email from description / mailto links."""
    for text in texts:
        if not text or not isinstance(text, str):
            continue
        for m in _EMAIL_RE.finditer(text):
            addr = (m.group(1) or "").strip().lower()
            if not addr or len(addr) > 120:
                continue
            if any(bad in addr for bad in _EMAIL_BLOCKLIST):
                continue
            return addr
    return None


_SOCIAL_LINK_RE = re.compile(
    r"https?://(?:www\.)?"
    r"(instagram\.com|twitter\.com|x\.com|facebook\.com|tiktok\.com|twitch\.tv|"
    r"linkedin\.com|discord\.gg|discord\.com)"
    r"/[^\s\"'<>\\]+",
    re.I,
)
_SOCIAL_LABELS = {
    "instagram.com": "Instagram",
    "twitter.com": "Twitter",
    "x.com": "Twitter",
    "facebook.com": "Facebook",
    "tiktok.com": "TikTok",
    "twitch.tv": "Twitch",
    "linkedin.com": "LinkedIn",
    "discord.gg": "Discord",
    "discord.com": "Discord",
}


def _links_from_html(html: str) -> list[dict[str, str]]:
    """Fallback social links from channel HTML when About/primaryLinks are empty."""
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for m in _SOCIAL_LINK_RE.finditer(html or ""):
        raw = m.group(0).rstrip(").,];")
        host = m.group(1).lower()
        # Dedupe by host so description noise doesn't flood the list.
        if host in seen:
            continue
        seen.add(host)
        out.append({"text": _SOCIAL_LABELS.get(host, host), "url": raw})
    return out


# ------------------------------------------------------------- transcript --
# Caption URLs served on the web watch page require a proof-of-origin token
# since ~2025 and return empty bodies to plain HTTP clients. The ANDROID
# InnerTube client still hands out working (signed) timedtext URLs.
# Keep this on a version that still returns captionTracks (newer clients 400).
_ANDROID_CLIENT_VERSION = "20.10.38"
_ANDROID_CONTEXT = {
    "client": {
        "clientName": "ANDROID",
        "clientVersion": _ANDROID_CLIENT_VERSION,
        "androidSdkVersion": 30,
        "hl": "en",
        "gl": "US",
    }
}
_ANDROID_HEADERS = {
    "User-Agent": (
        f"com.google.android.youtube/{_ANDROID_CLIENT_VERSION} "
        "(Linux; U; Android 11) gzip"
    ),
    "X-Youtube-Client-Name": "3",
    "X-Youtube-Client-Version": _ANDROID_CLIENT_VERSION,
}


async def _player_innertube(
    video_id: str,
    *,
    context: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, Any] | None, str | None]:
    """InnerTube ``player`` across tiers (direct → DC → residential).

    Returns ``(player, tier)``. Skips ``LOGIN_REQUIRED`` / empty-caption bot
    walls so a later tier can still succeed.
    """
    fallback: tuple[dict[str, Any], str] | None = None
    for tier in _player_tiers():
        try:
            resp = await post_json(
                "https://www.youtube.com/youtubei/v1/player",
                {
                    "context": context,
                    "videoId": video_id,
                    "contentCheckOk": True,
                    "racyCheckOk": True,
                },
                tier=tier,  # type: ignore[arg-type]
                headers=headers,
                params={"prettyPrint": "false"},
                timeout=15,
            )
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        try:
            data = resp.json()
        except ValueError:
            continue
        if not isinstance(data, dict) or not data:
            continue
        status = ((data.get("playabilityStatus") or {}).get("status") or "").upper()
        tracks = _caption_tracks(data) if status == "OK" else []
        if status == "OK" and tracks:
            return data, tier
        if status == "OK" and fallback is None:
            fallback = (data, tier)
        # LOGIN_REQUIRED / ERROR: keep trying other egress IPs.
    if fallback:
        return fallback
    return None, None


async def _player_android(video_id: str) -> dict[str, Any] | None:
    player, _tier = await _player_innertube(
        video_id, context=_ANDROID_CONTEXT, headers=_ANDROID_HEADERS
    )
    return player


async def _player_android_with_tier(
    video_id: str,
) -> tuple[dict[str, Any] | None, str | None]:
    return await _player_innertube(
        video_id, context=_ANDROID_CONTEXT, headers=_ANDROID_HEADERS
    )


def _parse_timedtext(body: str) -> list[dict[str, Any]]:
    """Parse a timedtext payload: json3 events or srv3 XML ``<p t= d=>``."""
    stripped = body.strip()
    segments: list[dict[str, Any]] = []
    if stripped.startswith("{"):
        try:
            payload = json.loads(stripped)
        except ValueError:
            return []
        for ev in payload.get("events") or []:
            segs = ev.get("segs")
            if not segs:
                continue
            text = "".join(s.get("utf8") or "" for s in segs).replace("\n", " ").strip()
            if not text:
                continue
            segments.append(
                {
                    "text": text,
                    "start": float(ev.get("tStartMs") or 0) / 1000.0,
                    "duration": float(ev.get("dDurationMs") or 0) / 1000.0,
                }
            )
        return segments
    try:
        root = ET.fromstring(stripped)
    except ET.ParseError:
        return []
    for p in root.iter("p"):
        text = "".join(p.itertext()).replace("\n", " ").strip()
        if not text:
            continue
        segments.append(
            {
                "text": text,
                "start": float(p.get("t") or 0) / 1000.0,
                "duration": float(p.get("d") or 0) / 1000.0,
            }
        )
    return segments


def _with_timedtext_fmt(url: str, fmt: str) -> str:
    if not url:
        return url
    if re.search(r"[?&]fmt=", url):
        return re.sub(r"([?&])fmt=[^&]*", rf"\1fmt={fmt}", url)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}fmt={fmt}"


async def _fetch_timedtext(
    base_url: str,
    *,
    headers: dict[str, str],
    prefer_tier: str | None = None,
) -> list[dict[str, Any]]:
    """GET a caption URL across proxy tiers and fmt variants.

    Prefer the same egress that produced the player response — caption
    ``baseUrl`` tokens can be sensitive to IP changes.
    """
    tiers = list(_player_tiers())
    if prefer_tier:
        tiers = [prefer_tier] + [t for t in tiers if t != prefer_tier]
    for fmt in ("json3", "srv3"):
        url = _with_timedtext_fmt(base_url, fmt)
        for tier in tiers:
            try:
                cap = await proxy_fetch(url, tier=tier, headers=headers, timeout=15)  # type: ignore[arg-type]
            except httpx.HTTPError:
                continue
            if cap.status_code >= 400 or not (cap.text or "").strip():
                continue
            segments = _parse_timedtext(cap.text)
            if segments:
                return segments
    return []


def _caption_tracks(player: dict[str, Any]) -> list[dict[str, Any]]:
    return list(
        ((player.get("captions") or {}).get("playerCaptionsTracklistRenderer") or {}).get(
            "captionTracks"
        )
        or []
    )


def _caption_track_name(track: dict[str, Any]) -> str | None:
    name = track.get("name")
    if isinstance(name, dict):
        return safe_str(name.get("simpleText") or name.get("content"))
    return safe_str(name)


def _available_caption_languages(tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for t in tracks:
        code = safe_str(t.get("languageCode"))
        if not code:
            continue
        is_asr = t.get("kind") == "asr"
        # Keep manual + ASR tracks for the same language as separate options.
        key = f"{code}:{'asr' if is_asr else 'manual'}"
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "languageCode": code,
                "languageName": _caption_track_name(t),
                "isAutoGenerated": is_asr,
            }
        )
    return out


def _rank_caption_tracks(
    tracks: list[dict[str, Any]], language: str | None
) -> list[dict[str, Any]]:
    def score(t: dict[str, Any]) -> tuple[int, int]:
        code = (t.get("languageCode") or "").lower()
        is_asr = 1 if t.get("kind") == "asr" else 0
        if language:
            want = language.lower()[:2]
            match = 0 if code.startswith(want) else 1
        else:
            match = 0 if code.startswith("en") else 1
        return (match, is_asr)

    return sorted(tracks, key=score)


async def transcript_native(norm_url: str, language: str | None) -> dict[str, Any] | None:
    """Transcript via InnerTube ANDROID caption tracks (timedtext).

    Tries every caption track (lang-ranked) and fmt=json3/srv3 across egress
    tiers (direct first — proxy IPs often trip YouTube bot-check) before
    giving up so callers hit Apify less often.
    """
    m = re.search(r"(?:v=|shorts/|youtu\.be/)([\w-]{11})", norm_url)
    if not m:
        return None
    video_id = m.group(1)

    player, player_tier = await _player_android_with_tier(video_id)
    if not player:
        return None
    if ((player.get("playabilityStatus") or {}).get("status")) != "OK":
        return None
    tracks = _caption_tracks(player)
    if not tracks:
        return None

    available = _available_caption_languages(tracks)
    ranked = _rank_caption_tracks(tracks, language)
    attempts: list[tuple[dict[str, Any], bool]] = [(t, False) for t in ranked]
    if language:
        want = language.lower()[:2]
        if not any((t.get("languageCode") or "").lower().startswith(want) for t in ranked):
            attempts.append((ranked[0], True))

    for track, use_tlang in attempts:
        base_url = safe_str(track.get("baseUrl"))
        if not base_url:
            continue
        url = f"{base_url}&tlang={language}" if use_tlang and language else base_url
        segments = await _fetch_timedtext(
            url, headers=_ANDROID_HEADERS, prefer_tier=player_tier
        )
        if not segments:
            continue
        title = safe_str((player.get("videoDetails") or {}).get("title"))
        return {
            "segments": segments,
            "title": title,
            "language": safe_str(
                language if use_tlang else (track.get("languageCode") or language)
            ),
            "isAutoGenerated": track.get("kind") == "asr",
            "isTranslated": bool(use_tlang),
            "availableLanguages": available,
        }
    return None



# ---------------------------------------------------------- video details --
def _youtube_thumbnails(thumbs: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for t in thumbs:
        if not isinstance(t, dict):
            continue
        url = safe_str(t.get("url"))
        if not url:
            continue
        out.append(
            {
                "url": url,
                "width": safe_int(t.get("width")),
                "height": safe_int(t.get("height")),
            }
        )
    return out


def _youtube_available_captions(player: dict[str, Any]) -> list[dict[str, Any]]:
    from app.utils.media_urls import cdn_expires_at

    out: list[dict[str, Any]] = []
    for t in _caption_tracks(player):
        if not isinstance(t, dict):
            continue
        code = safe_str(t.get("languageCode"))
        if not code:
            continue
        name = t.get("name")
        language_name = None
        if isinstance(name, dict):
            language_name = safe_str(name.get("simpleText")) or text_of(name)
        else:
            language_name = safe_str(name)
        base_url = safe_str(t.get("baseUrl"))
        row: dict[str, Any] = {
            "languageCode": code,
            "languageName": language_name,
            "kind": safe_str(t.get("kind")) or "standard",
            "baseUrl": base_url,
            "expiresAt": cdn_expires_at(base_url),
        }
        out.append(row)
    return out


def build_youtube_video_details(
    *,
    player: dict[str, Any],
    video_id: str,
    norm_url: str,
    like_count: int | None = None,
    comment_count: int | None = None,
    fetched_at: str | None = None,
) -> dict[str, Any] | None:
    """Normalize an InnerTube player payload into the public video-details shape."""
    from app.utils.media_urls import (
        channel_handle_from_profile_url,
        description_links,
        live_status_from_youtube,
        utc_now_iso,
    )

    if ((player.get("playabilityStatus") or {}).get("status")) != "OK":
        return None
    details = player.get("videoDetails") or {}
    if not details.get("title"):
        return None
    micro = (player.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    thumbs = (details.get("thumbnail") or {}).get("thumbnails") or []
    thumbnails = _youtube_thumbnails(thumbs if isinstance(thumbs, list) else [])
    channel_id = safe_str(details.get("channelId"))
    length = details.get("lengthSeconds") or micro.get("lengthSeconds")
    try:
        duration_seconds = int(length) if length is not None else None
    except (TypeError, ValueError):
        duration_seconds = None
    if duration_seconds is None:
        approx = details.get("approxDurationMs") or micro.get("approxDurationMs")
        try:
            duration_seconds = int(int(approx) / 1000) if approx is not None else None
        except (TypeError, ValueError):
            duration_seconds = None

    owner_profile = safe_str(micro.get("ownerProfileUrl"))
    channel_handle = channel_handle_from_profile_url(owner_profile)
    live_status = live_status_from_youtube(details)
    is_short = bool(
        "/shorts/" in (norm_url or "")
        or details.get("isShortsEligible")
        or (duration_seconds is not None and duration_seconds <= 60 and "shorts" in (norm_url or "").lower())
    )
    if live_status == "live":
        content_type = "live"
    elif is_short:
        content_type = "short"
    else:
        content_type = "video"

    playability = player.get("playabilityStatus") or {}
    reason = (safe_str(playability.get("reason")) or "").lower()
    is_members_only = "members" in reason or "member" in reason
    live_broadcast = micro.get("liveBroadcastDetails")
    if not isinstance(live_broadcast, dict):
        live_broadcast = details.get("liveBroadcastDetails")
    if not isinstance(live_broadcast, dict):
        live_broadcast = {}

    description = safe_str(details.get("shortDescription"))
    return {
        "url": norm_url,
        "id": video_id,
        "title": safe_str(details.get("title")) or "",
        "description": description,
        "descriptionLinks": description_links(description),
        "channelName": safe_str(details.get("author") or micro.get("ownerChannelName")),
        "channelId": channel_id,
        "channelHandle": channel_handle,
        "channelUrl": (
            owner_profile
            if owner_profile
            else (f"https://www.youtube.com/channel/{channel_id}" if channel_id else None)
        ),
        "publishedAt": safe_str(micro.get("publishDate") or micro.get("uploadDate")),
        "durationSeconds": duration_seconds,
        "viewCount": safe_int(details.get("viewCount")),
        "likeCount": like_count,
        "commentCount": comment_count,
        "thumbnailUrl": thumbnails[-1]["url"] if thumbnails else None,
        "thumbnails": thumbnails,
        "genre": safe_str(micro.get("category")),
        "categoryId": safe_str(details.get("categoryId") or micro.get("categoryId")),
        "tags": safe_list(details.get("keywords")),
        "contentType": content_type,
        "isShort": is_short,
        "liveStatus": live_status,
        "scheduledStartTime": safe_str(live_broadcast.get("startTimestamp")),
        "actualStartTime": safe_str(live_broadcast.get("actualStartTime")),
        "concurrentViewers": safe_int(details.get("concurrentViewers")),
        "defaultLanguage": safe_str(details.get("defaultLanguage")),
        "defaultAudioLanguage": safe_str(details.get("defaultAudioLanguage")),
        "isFamilySafe": None if micro.get("isFamilySafe") is None else bool(micro.get("isFamilySafe")),
        "isPrivate": bool(details.get("isPrivate")),
        "isUnlisted": bool(details.get("isUnlisted")),
        "isAgeRestricted": bool(
            details.get("isCrawlable") is False
            or "age" in reason
            or playability.get("desktopLegacyAgeGateReason") is not None
        ),
        "isMembersOnly": is_members_only,
        "availableCaptions": _youtube_available_captions(player),
        "chapters": [],  # filled later via InnerTube next when available
        "fetchedAt": fetched_at or utc_now_iso(),
        "viewCountIsApproximate": False,
    }


async def video_details_native(video_id: str, norm_url: str) -> dict[str, Any] | None:
    """Metadata/stats via InnerTube ANDROID player (watch HTML is often 429)."""
    player = await _player_android(video_id)
    if not player:
        return None
    return build_youtube_video_details(player=player, video_id=video_id, norm_url=norm_url)

# --------------------------------------------------------------- comments --
def _comment_author_avatar(author: dict[str, Any]) -> str | None:
    direct = safe_str(author.get("avatarThumbnailUrl") or author.get("avatarUrl"))
    if direct:
        return direct
    # Newer InnerTube nests avatars under avatar.image.sources[].
    avatar = author.get("avatar") if isinstance(author.get("avatar"), dict) else {}
    image = avatar.get("image") if isinstance(avatar.get("image"), dict) else {}
    sources = image.get("sources") if isinstance(image.get("sources"), list) else []
    if sources and isinstance(sources[0], dict):
        return safe_str(sources[0].get("url"))
    thumbs = author.get("thumbnails") if isinstance(author.get("thumbnails"), list) else []
    if thumbs and isinstance(thumbs[0], dict):
        return safe_str(thumbs[0].get("url"))
    return _best_thumb(author.get("avatar")) or _best_thumb(author.get("thumbnail"))


def _comment_author_channel_id(author: dict[str, Any]) -> str | None:
    for key in ("channelId", "externalChannelId", "browseId"):
        v = safe_str(author.get(key))
        if v and (v.startswith("UC") or len(v) >= 18):
            return v
    for nest_key in ("channelCommand", "frameworkUpdates", "navigationEndpoint"):
        nest = author.get(nest_key)
        if not isinstance(nest, dict):
            continue
        browse = (
            ((nest.get("innertubeCommand") or {}).get("browseEndpoint") or {})
            if nest_key == "channelCommand"
            else (nest.get("browseEndpoint") or {})
        )
        if not isinstance(browse, dict):
            browse = ((nest.get("command") or {}).get("browseEndpoint") or {})
        v = safe_str(browse.get("browseId"))
        if v and v.startswith("UC"):
            return v
    channel_url = safe_str(author.get("channelUrl") or author.get("canonicalBaseUrl"))
    if channel_url and "/channel/" in channel_url:
        return channel_url.rstrip("/").split("/channel/")[-1] or None
    return None


def _comment_published_time(props: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return (publishedTimeText, publishedTime ISO or None)."""
    text = text_of(props.get("publishedTime")) or safe_str(props.get("publishedTimeText"))
    iso: str | None = None
    for key in (
        "publishedTimeSeconds",
        "publishedTimestamp",
        "timestamp",
        "createTime",
        "publishedAt",
    ):
        raw = props.get(key)
        if isinstance(raw, str) and "T" in raw and ("Z" in raw or "+" in raw):
            iso = raw
            break
        ts = safe_int(raw)
        if ts and ts > 1_000_000_000:
            from datetime import datetime, timezone

            iso = datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.000Z"
            )
            break
    return text, iso


def _has_creator_heart(toolbar: dict[str, Any]) -> bool:
    """True only when the creator actually hearted the comment.

    ``heartActiveTooltip`` is often a non-empty UI string even when inactive,
    so ``bool(tooltip)`` false-positives — require an explicit heart object or
    tooltip language that says the comment was hearted.
    """
    if toolbar.get("creatorHeart") or toolbar.get("isHeartedByCreator"):
        return True
    tip = toolbar.get("heartActiveTooltip")
    if not isinstance(tip, str):
        tip = text_of(tip) or ""
    t = tip.strip().lower()
    if not t:
        return False
    return any(
        needle in t
        for needle in (
            "hearted",
            "hearts this",
            "loved by",
            "❤",
            "❤️",
        )
    )


def _comment_payload_to_api(p: dict[str, Any]) -> dict[str, Any] | None:
    props = p.get("properties") or {}
    author = p.get("author") or {}
    toolbar = p.get("toolbar") or {}
    if not isinstance(author, dict):
        author = {}
    if not isinstance(toolbar, dict):
        toolbar = {}
    if not isinstance(props, dict):
        props = {}
    cid = safe_str(props.get("commentId"))
    text = text_of(props.get("content"))
    if not cid or text is None:
        return None
    like_count = parse_count_text(toolbar.get("likeCountLiked") or toolbar.get("likeCountNotliked") or toolbar.get("likeCountA11y"))
    published_text, published_iso = _comment_published_time(props)
    return {
        "id": cid,
        "author": safe_str(author.get("displayName")),
        "authorChannelId": _comment_author_channel_id(author),
        "authorAvatarUrl": _comment_author_avatar(author),
        "authorIsVerified": bool(author.get("isVerified")),
        "authorIsChannelOwner": bool(author.get("isCreator")),
        "text": text.strip(),
        "likeCount": like_count or 0,
        "replyCount": safe_int(toolbar.get("replyCount")) or parse_count_text(toolbar.get("replyCountA11y")) or 0,
        "hasCreatorHeart": _has_creator_heart(toolbar),
        "publishedTimeText": published_text,
        "publishedTime": published_iso,
    }


def _comment_payloads(data: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for payload in walk_find(data, "commentEntityPayload"):
        row = _comment_payload_to_api(payload)
        if row and row["id"] not in seen:
            seen.add(row["id"])
            rows.append(row)
    return rows


def _comments_section_token(data: Any) -> str | None:
    """Pick the comments-section continuation token, not the watch-next feed."""
    first = None
    for c in walk_find(data, "continuationCommand"):
        token = safe_str(c.get("token"))
        if token and first is None:
            first = token
        if token and "comments-section" in token:
            return token
    return first


def _comments_total(data: Any) -> int | None:
    """Best-effort total from comments header / engagement panel."""
    for header in walk_find(data, "commentsHeaderRenderer"):
        for key in ("countText", "commentsCount", "headerText"):
            n = parse_count_text(text_of(header.get(key)))
            if n is not None:
                return n
    # Current InnerTube ``next`` shape: engagementPanelTitleHeaderRenderer
    # with title "Comments" and contextualInfo like "2.4M" / "10M".
    for header in walk_find(data, "engagementPanelTitleHeaderRenderer"):
        title = (text_of(header.get("title")) or "").strip().lower()
        if title and title not in ("comments", "comment"):
            continue
        for key in ("contextualInfo", "subtitle", "countText", "headerText"):
            n = parse_count_text(text_of(header.get(key)))
            if n is not None:
                return n
    return None


async def comment_count_native(video_id: str) -> int | None:
    """Resolve comment count via InnerTube ``next`` engagement panel."""
    if not video_id:
        return None
    boot = await innertube("next", {"videoId": video_id}, timeout=15)
    if boot is None:
        return None
    return _comments_total(boot)


async def _comments_entry_token(norm_url: str) -> tuple[str | None, int | None]:
    """Resolve the comments-section continuation + optional total.

    Prefer InnerTube ``next`` with ``videoId`` — watch-page HTML is frequently
    429'd on datacenter IPs. Fall back to ytInitialData when needed.
    """
    # Lazy import avoids a circular dependency with app.utils.url.
    from app.utils.url import extract_youtube_id

    vid = extract_youtube_id(norm_url)
    if vid:
        boot = await innertube("next", {"videoId": vid}, timeout=15)
        if boot is not None:
            token = _comments_section_token(boot)
            if token:
                return token, _comments_total(boot)

    data, _ = await fetch_page_data(norm_url, timeout=12)
    if data is None:
        return None, None
    return _comments_section_token(data), _comments_total(data)


async def comments_native(
    norm_url: str,
    limit: int,
    *,
    cursor: str | None = None,
) -> dict[str, Any] | None:
    """Top-level comments via InnerTube continuation tokens.

    Pass ``cursor`` (previous ``nextCursor``) to fetch the next page. Without a
    cursor we bootstrap via InnerTube ``next`` (videoId), not the watch HTML.
    """
    token = cursor or None
    total_comments: int | None = None
    if not token:
        token, total_comments = await _comments_entry_token(norm_url)
    if not token:
        return None

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    # ~20 comments per InnerTube hop; keep a small buffer for empty pages.
    max_hops = max(8, (limit // 15) + 3)
    hops = 0
    while token and len(rows) < limit and hops < max_hops:
        payload = await innertube("next", {"continuation": token}, timeout=15)
        if payload is None:
            break
        if total_comments is None:
            total_comments = _comments_total(payload)
        for row in _comment_payloads(payload):
            if row["id"] not in seen:
                seen.add(row["id"])
                rows.append(row)
                if len(rows) >= limit:
                    break
        token = find_continuation_token(payload)
        hops += 1

    if not rows:
        return None
    next_cursor = token if token else None
    return {
        "comments": rows[:limit],
        "totalComments": total_comments,
        "nextCursor": next_cursor,
    }


def _reply_continuation_for_thread(thread: dict[str, Any], comment_id: str) -> str | None:
    vm = (((thread.get("commentViewModel") or {}).get("commentViewModel")) or {})
    if safe_str(vm.get("commentId")) != comment_id:
        return None
    replies = thread.get("replies") or {}
    return find_continuation_token(replies)


async def comment_replies_native(norm_url: str, comment_id: str, limit: int) -> list[dict[str, Any]]:
    """Paginate reply continuations for ``comment_id`` (no hard ~20 cap)."""
    token, _ = await _comments_entry_token(norm_url)
    if not token:
        return []

    reply_token = None
    hops = 0
    while token and not reply_token and hops < 6:
        payload = await innertube("next", {"continuation": token}, timeout=15)
        if payload is None:
            break
        for thread in walk_find(payload, "commentThreadRenderer"):
            reply_token = _reply_continuation_for_thread(thread, comment_id)
            if reply_token:
                break
        token = find_continuation_token(payload)
        hops += 1

    if not reply_token:
        return []

    replies: list[dict[str, Any]] = []
    seen: set[str] = set()
    token = reply_token
    max_hops = max(8, (limit // 15) + 3)
    hops = 0
    while token and len(replies) < limit and hops < max_hops:
        payload = await innertube("next", {"continuation": token}, timeout=15)
        if payload is None:
            break
        for row in _comment_payloads(payload):
            rid = row["id"]
            if rid in seen:
                continue
            seen.add(rid)
            row["replyToId"] = comment_id
            replies.append(row)
            if len(replies) >= limit:
                break
        token = find_continuation_token(payload)
        hops += 1
    return replies[:limit]


# --------------------------------------------------------- community posts --
def _normalize_community_post(post: dict[str, Any]) -> dict[str, Any] | None:
    """Shape matching ``/v1/youtube/community-posts`` list items."""
    if not isinstance(post, dict):
        return None
    post_id = safe_str(post.get("postId"))
    if not post_id:
        return None
    text = text_of(post.get("contentText")) or ""
    images: list[str] = []
    linked: list[dict[str, Any]] = []
    post_type = "text"
    attachment = post.get("backstageAttachment") or {}
    for renderer in walk_find(attachment, "backstageImageRenderer"):
        url = _best_thumb({"thumbnails": ((renderer.get("image") or {}).get("thumbnails") or [])})
        if not url:
            thumbs = (renderer.get("image") or {}).get("thumbnails") or []
            if thumbs and isinstance(thumbs[-1], dict):
                url = safe_str(thumbs[-1].get("url"))
        if url:
            if url.startswith("//"):
                url = "https:" + url
            images.append(url)
            post_type = "image"
    for key in ("videoRenderer", "compactVideoRenderer", "gridVideoRenderer"):
        for vr in walk_find(attachment, key):
            vid = safe_str(vr.get("videoId"))
            if not vid:
                continue
            linked.append(
                {
                    "videoId": vid,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "title": text_of(vr.get("title")),
                }
            )
            post_type = "video"
    # Deduplicate images while preserving order.
    seen_img: set[str] = set()
    uniq_images: list[str] = []
    for img in images:
        if img not in seen_img:
            seen_img.add(img)
            uniq_images.append(img)
    hashtags = re.findall(r"#(\w+)", text)
    return {
        "id": post_id,
        "author": text_of(post.get("authorText")),
        "text": text.strip(),
        "likeCount": text_of(post.get("voteCount")),
        "hashtags": hashtags,
        "linkedVideos": linked,
        "publishedTime": text_of(post.get("publishedTimeText")),
        "postType": post_type,
        "images": uniq_images,
        "sourceUrl": f"https://www.youtube.com/post/{post_id}",
    }


def _collect_community_posts(data: Any) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in walk_find(data, "backstagePostRenderer"):
        item = _normalize_community_post(raw)
        if not item:
            continue
        pid = item["id"]
        if pid in seen:
            continue
        seen.add(pid)
        posts.append(item)
    return posts


def _posts_tab_url(channel_url: str) -> str:
    base = (channel_url or "").strip().rstrip("/")
    # Strip existing tab suffixes.
    for suffix in ("/posts", "/community", "/videos", "/shorts", "/streams", "/playlists", "/about"):
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}/posts"


async def community_posts_native(channel_url: str, limit: int = 20) -> list[dict[str, Any]] | None:
    """Channel community posts from the public ``/posts`` tab + continuations."""
    capped = max(1, min(int(limit or 20), 200))
    tab = _posts_tab_url(channel_url)
    data, _ = await fetch_page_data(tab)
    if data is None:
        return None
    posts = _collect_community_posts(data)
    token = find_continuation_token(data)
    hops = 0
    while token and len(posts) < capped and hops < 8:
        payload = await innertube("browse", {"continuation": token})
        if payload is None:
            break
        existing = {p["id"] for p in posts}
        added = [p for p in _collect_community_posts(payload) if p["id"] not in existing]
        if not added:
            break
        posts.extend(added)
        token = find_continuation_token(payload)
        hops += 1
    if not posts:
        return None
    return posts[:capped]

