"""Self-scraped YouTube data from public pages + InnerTube (no Apify).

Every function returns data in the exact shapes the routers already emit, or
``None``/``[]`` on failure so callers can fall back to the Apify actors.

Approach:
- List pages (search results, channel tabs, hashtag pages) embed
  ``ytInitialData``; we parse the video renderers straight out of it and follow
  one continuation via InnerTube when the caller wants more than one page.
- Channel metadata comes from the channel page (``channelMetadataRenderer``)
  plus the About popup fetched through InnerTube ``browse``.
- Transcripts come from InnerTube ANDROID player caption tracks (the web watch
  page's timedtext URLs need a proof-of-origin token and return empty bodies).
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from typing import Any, Iterator

import httpx

from app.services.http_fetch import fetch as proxy_fetch, post_json
from app.utils.formatters import safe_int, safe_str

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

_INNERTUBE_CONTEXT = {
    "client": {"clientName": "WEB", "clientVersion": "2.20240701.00.00", "hl": "en", "gl": "US"}
}

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
    else:
        for vr in walk_find(data, "videoRenderer"):
            add(normalize_video_renderer(vr))
        for pv in walk_find(data, "playlistVideoRenderer"):
            add(_normalize_playlist_video(pv))
        for lk in walk_find(data, "lockupViewModel"):
            add(_normalize_video_lockup(lk))
    return cards


def find_continuation_token(data: Any) -> str | None:
    for c in walk_find(data, "continuationCommand"):
        token = safe_str(c.get("token"))
        if token:
            return token
    return None


async def fetch_page_data(url: str, *, timeout: float = 12.0) -> tuple[dict[str, Any] | None, str]:
    """GET a YouTube page and return (ytInitialData, raw html)."""
    try:
        resp = await proxy_fetch(
            url, tier="datacenter", headers=YT_HEADERS, cookies=YT_COOKIES, timeout=timeout
        )
    except httpx.HTTPError:
        return None, ""
    if resp.status_code >= 400:
        return None, ""
    return extract_initial_json(resp.text, "ytInitialData"), resp.text


async def innertube(endpoint: str, body: dict[str, Any], *, timeout: float = 12.0) -> dict[str, Any] | None:
    """POST to InnerTube (web client). ``endpoint``: search | browse | next."""
    try:
        resp = await post_json(
            f"https://www.youtube.com/youtubei/v1/{endpoint}",
            {"context": _INNERTUBE_CONTEXT, **body},
            tier="datacenter",
            headers={**YT_HEADERS, "X-Youtube-Client-Name": "1", "X-Youtube-Client-Version": "2.20240701.00.00"},
            params={"prettyPrint": "false"},
            timeout=timeout,
        )
    except httpx.HTTPError:
        return None
    if resp.status_code >= 400:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


async def _paginate(
    first_page: Any,
    *,
    limit: int,
    continuation_endpoint: str,
    shorts: bool = False,
    max_hops: int = 6,
) -> list[dict[str, Any]]:
    """Cards from the initial tree plus InnerTube continuations up to limit."""
    cards = collect_video_cards(first_page, shorts=shorts)
    token = find_continuation_token(first_page)
    hops = 0
    while token and len(cards) < limit and hops < max_hops:
        payload = await innertube(continuation_endpoint, {"continuation": token})
        if payload is None:
            break
        new_cards = collect_video_cards(payload, shorts=shorts)
        existing = {c["url"] for c in cards}
        added = [c for c in new_cards if c["url"] not in existing]
        if not added:
            break
        cards.extend(added)
        token = find_continuation_token(payload)
        hops += 1
    return cards[:limit]


# ---------------------------------------------------------------- search ---
async def search_native(q: str, limit: int) -> list[dict[str, Any]]:
    from urllib.parse import quote

    data, _ = await fetch_page_data(
        f"https://www.youtube.com/results?search_query={quote(q)}"
    )
    if data is None:
        return []
    return await _paginate(data, limit=limit, continuation_endpoint="search")


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
async def channel_tab_native(tab_url: str, limit: int, *, shorts: bool = False) -> list[dict[str, Any]]:
    """Videos / streams / shorts tab of a channel."""
    data, _ = await fetch_page_data(tab_url)
    if data is None:
        return []
    return await _paginate(data, limit=limit, continuation_endpoint="browse", shorts=shorts)


# ---------------------------------------------------------------- hashtag --
async def hashtag_native(tag: str, limit: int) -> list[dict[str, Any]]:
    from urllib.parse import quote

    data, _ = await fetch_page_data(f"https://www.youtube.com/hashtag/{quote(tag)}")
    if data is None:
        return []
    return await _paginate(data, limit=limit, continuation_endpoint="browse")


# --------------------------------------------------------- channel details --
_ABOUT_PARAMS = "EgVhYm91dPIGBAoCEgA%3D"


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
    about_payload = await innertube(
        "browse", {"browseId": channel_id, "params": _ABOUT_PARAMS}
    )
    if about_payload:
        about = next(walk_find(about_payload, "aboutChannelViewModel"), None)
        if about:
            view_count = parse_count_text(about.get("viewCountText"))
            joined = safe_str(text_of(about.get("joinedDateText")))
            if joined:
                joined = joined.replace("Joined ", "")
            country = safe_str(text_of(about.get("country")))
            if subscriber_count is None:
                subscriber_count = parse_count_text(about.get("subscriberCountText"))
            if video_count is None:
                video_count = parse_count_text(about.get("videoCountText"))
            if not description:
                description = safe_str(text_of(about.get("description")))
            for link in about.get("links") or []:
                view_model = link.get("channelExternalLinkViewModel") or {}
                link_title = text_of(view_model.get("title"))
                link_url = text_of(view_model.get("link"))
                if link_url:
                    links.append({"text": safe_str(link_title) or "", "url": safe_str(link_url) or ""})

    verified = None
    if data:
        header_blob = json.dumps(data.get("header") or {})
        verified = "CHECK_CIRCLE" in header_blob or '"BADGE_STYLE_TYPE_VERIFIED"' in header_blob

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
    }


# ------------------------------------------------------------- transcript --
# Caption URLs served on the web watch page require a proof-of-origin token
# since ~2025 and return empty bodies to plain HTTP clients. The ANDROID
# InnerTube client still hands out working (signed) timedtext URLs.
_ANDROID_CONTEXT = {
    "client": {
        "clientName": "ANDROID",
        "clientVersion": "20.10.38",
        "androidSdkVersion": 30,
        "hl": "en",
        "gl": "US",
    }
}
_ANDROID_HEADERS = {
    "User-Agent": "com.google.android.youtube/20.10.38 (Linux; U; Android 11) gzip",
    "X-Youtube-Client-Name": "3",
    "X-Youtube-Client-Version": "20.10.38",
}


async def _player_android(video_id: str) -> dict[str, Any] | None:
    try:
        resp = await post_json(
            "https://www.youtube.com/youtubei/v1/player",
            {
                "context": _ANDROID_CONTEXT,
                "videoId": video_id,
                "contentCheckOk": True,
                "racyCheckOk": True,
            },
            tier="datacenter",
            headers=_ANDROID_HEADERS,
            params={"prettyPrint": "false"},
            timeout=12,
        )
    except httpx.HTTPError:
        return None
    if resp.status_code >= 400:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


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


async def transcript_native(norm_url: str, language: str | None) -> dict[str, Any] | None:
    """Transcript via InnerTube ANDROID caption tracks (timedtext).

    Returns ``{segments: [{text, start, duration}], title, language}`` or None
    (no captions / fetch failed) so the caller can fall back to actors.
    """
    m = re.search(r"(?:v=|shorts/|youtu\.be/)([\w-]{11})", norm_url)
    if not m:
        return None
    player = await _player_android(m.group(1))
    if not player:
        return None
    if ((player.get("playabilityStatus") or {}).get("status")) != "OK":
        return None

    tracks = (
        ((player.get("captions") or {}).get("playerCaptionsTracklistRenderer") or {}).get("captionTracks")
        or []
    )
    if not tracks:
        return None

    def track_score(t: dict[str, Any]) -> tuple[int, int]:
        code = (t.get("languageCode") or "").lower()
        is_asr = 1 if t.get("kind") == "asr" else 0
        if language:
            match = 0 if code.startswith(language.lower()[:2]) else 1
        else:
            match = 0 if code.startswith("en") else 1
        return (match, is_asr)

    track = sorted(tracks, key=track_score)[0]
    base_url = track.get("baseUrl")
    if not base_url:
        return None
    if language and not (track.get("languageCode") or "").lower().startswith(language.lower()[:2]):
        # Requested language not among tracks; ask timedtext to translate.
        base_url += f"&tlang={language}"

    try:
        cap = await proxy_fetch(base_url, tier="datacenter", headers=_ANDROID_HEADERS, timeout=12)
    except httpx.HTTPError:
        return None
    if cap.status_code >= 400 or not cap.text.strip():
        return None

    segments = _parse_timedtext(cap.text)
    if not segments:
        return None

    title = None
    details = player.get("videoDetails") or {}
    if details.get("title"):
        title = safe_str(details["title"])
    return {
        "segments": segments,
        "title": title,
        "language": safe_str(language or track.get("languageCode")),
    }


# --------------------------------------------------------------- comments --
def _comment_payload_to_api(p: dict[str, Any]) -> dict[str, Any] | None:
    props = p.get("properties") or {}
    author = p.get("author") or {}
    toolbar = p.get("toolbar") or {}
    cid = safe_str(props.get("commentId"))
    text = text_of(props.get("content"))
    if not cid or text is None:
        return None
    like_count = parse_count_text(toolbar.get("likeCountLiked") or toolbar.get("likeCountNotliked") or toolbar.get("likeCountA11y"))
    return {
        "id": cid,
        "author": safe_str(author.get("displayName")),
        "authorAvatarUrl": safe_str(author.get("avatarThumbnailUrl")),
        "authorIsVerified": bool(author.get("isVerified")),
        "authorIsChannelOwner": bool(author.get("isCreator")),
        "text": text.strip(),
        "likeCount": like_count or 0,
        "replyCount": safe_int(toolbar.get("replyCount")) or parse_count_text(toolbar.get("replyCountA11y")) or 0,
        "hasCreatorHeart": bool(toolbar.get("heartActiveTooltip")),
        "publishedTimeText": safe_str(props.get("publishedTime")),
        "replyToId": None,
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
    """Best-effort total from commentsHeaderRenderer count text."""
    for header in walk_find(data, "commentsHeaderRenderer"):
        for key in ("countText", "commentsCount", "headerText"):
            n = parse_count_text(text_of(header.get(key)))
            if n is not None:
                return n
    return None


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
    payload = await innertube("next", {"continuation": reply_token}, timeout=15)
    if payload is None:
        return []
    replies = _comment_payloads(payload)
    for r in replies:
        r["replyToId"] = comment_id
    return replies[:limit]
