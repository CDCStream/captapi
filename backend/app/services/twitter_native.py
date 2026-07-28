"""Native Twitter/X lookups without Apify.

``cdn.syndication.twimg.com/tweet-result`` powers embedded tweets (text, author,
likes, replies, media). Public profile pages embed schema.org microdata
(``ProfilePage`` / ``Person`` + interaction counters) that a plain GET — or
Decodo when datacenter IPs are login-walled — can parse for follower / tweet
stats. Profile timelines come from the public syndication embed
(``syndication.twitter.com/srv/timeline-profile``) — typically ~20 recent posts.
Keyword search uses the public web client's guest-token GraphQL
``SearchTimeline`` (query id scraped from the current ``main.*.js`` bundle).
Communities use guest GraphQL ``CommunitiesFetchOneQuery`` /
``CommunityTweetsTimeline`` (with known query-id fallbacks).
"""

from __future__ import annotations

import json
import math
import re
import time
from datetime import datetime, timezone
from html import unescape
from typing import Any
from urllib.parse import urlparse

import httpx
import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

_UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
_BASE = "https://cdn.syndication.twimg.com/tweet-result"
_TIMELINE_BASE = "https://syndication.twitter.com/srv/timeline-profile/screen-name"
_SCRIPT_RE = re.compile(r"<script[^>]*>([\s\S]*?)</script>", re.I)
_HANDLE_RE = re.compile(r"^[A-Za-z0-9_]{1,15}$")
# Public web-client bearer embedded in x.com JS (not a user secret).
_PUBLIC_BEARER = (
    "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
    "%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
)
_MAIN_JS_RE = re.compile(
    r"https://abs\.twimg\.com/responsive-web/client-web/main\.[^\"']+\.js"
)
_SEARCH_META_RE = re.compile(
    r'queryId:"([A-Za-z0-9_-]+)",operationName:"SearchTimeline",'
    r'operationType:"query",metadata:\{featureSwitches:(\[[^\]]+\])'
)
_FALLBACK_SEARCH_QID = "BGd0T_j7oVwlW5U79tO_0A"
_SEARCH_META_TTL_S = 6 * 3600
_search_meta_cache: dict[str, Any] = {"qid": None, "features": None, "fetched_at": 0.0}
_FALSE_FEATURE_FLAGS = {
    "verified_phone_label_enabled",
    "tweet_awards_web_tipping_enabled",
    "creator_subscriptions_quote_tweet_preview_enabled",
    "responsive_web_enhance_cards_enabled",
    "responsive_web_media_download_video_enabled",
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled",
}
# Community ops live in lazy bundles; keep a short working fallback chain.
_COMMUNITY_DETAIL_QIDS = (
    "UlgIZeglRXC9tZBYlwV3Dw",
    "wYwM9x1NTCQKPx50Ih35Tg",
    "Mt033iulrkGz0nqtHmXZvQ",
)
_COMMUNITY_TWEETS_QIDS = (
    "PUinTHtCGWmECLX57lhRHA",
    "rDsqfuibxL_NXh33IiTvzQ",
    "rp4YNcEs-BXdkm1DA4PMhw",
)
_OG_TITLE_RE = re.compile(
    r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)
_OG_DESC_RE = re.compile(
    r'<meta[^>]+(?:property=["\']og:description["\']|name=["\']description["\'])[^>]+content=["\']([^"\']*)["\']',
    re.I,
)
_OG_IMAGE_RE = re.compile(
    r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)
_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"
_META_RE = re.compile(
    r"<meta[^>]+>",
    re.I,
)
_PROP_CONTENT_RE = re.compile(
    r"""itemprop=["']([^"']+)["'][^>]*content=["']([^"']*)["']"""
    r"|"
    r"""content=["']([^"']*)["'][^>]*itemprop=["']([^"']+)["']""",
    re.I,
)
_INTERACTION_RE = re.compile(
    r"""interactionType[^>]*content=["']([^"']+)["']"""
    r"""[\s\S]{0,400}?"""
    r"""userInteractionCount[^>]*content=["']([^"']+)["']""",
    re.I,
)
_IMAGE_URL_RE = re.compile(
    r"""itemprop=["'](?:contentUrl|thumbnailUrl|image)["'][^>]*content=["']([^"']+)["']"""
    r"|"
    r"""content=["']([^"']+)["'][^>]*itemprop=["'](?:contentUrl|thumbnailUrl|image)["']""",
    re.I,
)


def _token(tweet_id: str) -> str:
    """Reproduce the JS token the web embed derives from the tweet id.

    ``((id / 1e15) * pi).toString(36)`` with ``0`` and ``.`` stripped.
    """
    val = (int(tweet_id) / 1e15) * math.pi
    intpart = int(val)
    frac = val - intpart
    s = "" if intpart else "0"
    while intpart > 0:
        s = _DIGITS[intpart % 36] + s
        intpart //= 36
    s += "."
    for _ in range(12):
        frac *= 36
        d = int(frac)
        s += _DIGITS[d]
        frac -= d
    return s.replace("0", "").replace(".", "")


async def tweet_result(tweet_id: str, lang: str = "en") -> dict[str, Any] | None:
    """Fetch a tweet's public syndication record, or None on any failure."""
    if not tweet_id or not tweet_id.isdigit():
        return None
    try:
        async with httpx.AsyncClient(timeout=10, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(
                _BASE, params={"id": tweet_id, "token": _token(tweet_id), "lang": lang}
            )
    except httpx.HTTPError:
        return None
    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) and data.get("text") is not None else None


def _meta_pairs(html: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for tag in _META_RE.findall(html or ""):
        m = _PROP_CONTENT_RE.search(tag)
        if not m:
            continue
        if m.group(1) is not None:
            out.append((m.group(1), unescape(m.group(2) or "")))
        else:
            out.append((m.group(4), unescape(m.group(3) or "")))
    return out


def _profile_image(html: str) -> str | None:
    for m in _IMAGE_URL_RE.finditer(html or ""):
        uri = unescape(m.group(1) or m.group(2) or "")
        if "profile_images" in uri:
            return uri
    return None


def parse_profile_html(html: str, handle: str) -> dict[str, Any] | None:
    """Map x.com profile microdata → shape ``_normalize_profile`` understands."""
    if not html or "schema.org/ProfilePage" not in html and "schema.org/profilepage" not in html.lower():
        return None
    if "schema.org/Person" not in html and "schema.org/person" not in html.lower():
        return None

    lower = html.lower()
    start = lower.find("schema.org/profilepage")
    if start < 0:
        return None
    # Prefer the Person block when present.
    person_at = lower.find("schema.org/person", start)
    window = html[person_at : person_at + 20_000] if person_at >= 0 else html[start : start + 40_000]

    fields: dict[str, str] = {}
    for key, value in _meta_pairs(window):
        if key and value and key not in fields:
            fields[key] = value
    # Profile-level dateCreated / url sit outside Person.
    page_window = html[start : start + 8_000]
    for key, value in _meta_pairs(page_window):
        if key in ("dateCreated", "url") and key not in fields and value:
            fields[key] = value

    counters: dict[str, list[int]] = {}
    for m in _INTERACTION_RE.finditer(html):
        kind = (m.group(1) or "").rsplit("/", 1)[-1]
        n = safe_int(m.group(2))
        if not kind or n is None:
            continue
        counters.setdefault(kind, []).append(n)

    tweet_count = counters.get("WriteAction", [None])[0]
    follow_vals = counters.get("FollowAction") or []
    if len(follow_vals) >= 2:
        following, followers = sorted(follow_vals)[0], sorted(follow_vals)[-1]
    elif len(follow_vals) == 1:
        following, followers = None, follow_vals[0]
    else:
        following = followers = None

    username = safe_str(fields.get("additionalName") or handle)
    if username:
        username = username.lstrip("@")
    profile_url = safe_str(fields.get("url")) or (f"https://x.com/{username}" if username else None)
    website = None
    for key, value in _meta_pairs(window):
        if key == "sameAs" and value and "x.com" not in value.lower() and "twitter.com" not in value.lower():
            website = value
            break

    location = None
    loc_m = re.search(
        r"""itemprop=["']homeLocation["'][\s\S]{0,400}?itemprop=["']name["'][^>]*content=["']([^"']*)["']""",
        window,
        re.I,
    )
    if loc_m:
        location = unescape(loc_m.group(1))

    if not username and not fields.get("identifier"):
        return None

    return {
        "id": safe_str(fields.get("identifier")),
        "userName": username,
        "name": safe_str(fields.get("name")),
        "description": safe_str(fields.get("description")),
        "location": safe_str(location),
        "followers": followers,
        "following": following,
        "statusesCount": tweet_count,
        "website": safe_str(website),
        "profilePicture": safe_str(_profile_image(window) or _profile_image(html)),
        "createdAt": safe_str(fields.get("dateCreated")),
        "url": profile_url,
    }


async def _fetch_profile_html(handle: str) -> str | None:
    url = f"https://x.com/{handle}"
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and len(resp.text) > 5000:
            return resp.text
    except httpx.HTTPError as exc:
        log.info("twitter_profile_direct_fail", handle=handle, error=str(exc))

    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
        if got:
            status, body = got
            if status == 200 and body and len(body) > 5000:
                return body
    return None


def _normalize_handle(handle: str) -> str | None:
    raw = (handle or "").strip().lstrip("@")
    if "://" in raw or "/" in raw:
        path = urlparse(raw if "://" in raw else f"https://x.com/{raw}").path
        parts = [p for p in path.split("/") if p]
        raw = parts[0] if parts else ""
    raw = raw.lstrip("@")
    if not raw or not _HANDLE_RE.fullmatch(raw):
        return None
    return raw


async def profile_by_handle(handle: str) -> dict[str, Any] | None:
    """Fetch a public X profile via HTML microdata (direct, then Decodo)."""
    raw = _normalize_handle(handle)
    if not raw:
        return None
    html = await _fetch_profile_html(raw)
    if not html:
        return None
    parsed = parse_profile_html(html, raw)
    if parsed:
        log.info("twitter_profile_native_ok", handle=raw, followers=parsed.get("followers"))
    else:
        log.warning("twitter_profile_native_parse_miss", handle=raw, length=len(html))
    return parsed


async def _fetch_timeline_html(handle: str) -> str | None:
    url = f"{_TIMELINE_BASE}/{handle}"
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and len(resp.text) > 2000:
            return resp.text
        log.info(
            "twitter_timeline_direct_miss",
            handle=handle,
            status=resp.status_code,
            length=len(resp.text),
        )
    except httpx.HTTPError as exc:
        log.info("twitter_timeline_direct_fail", handle=handle, error=str(exc))

    # Static Next.js HTML with JSON in <script> — no JS render needed.
    # headless="html" often 613s on syndication; plain Decodo fetch works.
    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=120.0)
        if got:
            status, body = got
            if status == 200 and body and len(body) > 2000:
                return body
    return None


def parse_timeline_html(html: str) -> list[dict[str, Any]]:
    """Extract unique tweet objects from a syndication timeline-profile page."""
    best_entries: list[Any] | None = None
    best_len = 0
    for match in _SCRIPT_RE.finditer(html or ""):
        raw = (match.group(1) or "").strip()
        if not raw.startswith("{") or "timeline" not in raw:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        entries = (
            ((data.get("props") or {}).get("pageProps") or {}).get("timeline") or {}
        ).get("entries")
        if isinstance(entries, list) and len(entries) > best_len:
            best_entries = entries
            best_len = len(entries)
    if not best_entries:
        return []

    tweets: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in best_entries:
        if not isinstance(entry, dict):
            continue
        content = entry.get("content")
        if not isinstance(content, dict):
            continue
        tweet = content.get("tweet")
        if not isinstance(tweet, dict):
            continue
        tid = safe_str(tweet.get("id_str")) or safe_str(tweet.get("id"))
        if not tid or tid == "0" or tid in seen:
            continue
        seen.add(tid)
        # Syndication sometimes ships numeric id=0; keep id_str authoritative.
        out = dict(tweet)
        out["id_str"] = tid
        if out.get("retweeted_status") is not None:
            out["is_retweet"] = True
        tweets.append(out)
    return tweets


async def user_tweets(handle: str, limit: int = 20) -> list[dict[str, Any]] | None:
    """Recent public tweets via syndication timeline embed (direct → Decodo)."""
    raw = _normalize_handle(handle)
    if not raw:
        return None
    html = await _fetch_timeline_html(raw)
    if not html:
        return None
    tweets = parse_timeline_html(html)
    if not tweets:
        log.warning("twitter_timeline_native_parse_miss", handle=raw, length=len(html))
        return None
    capped = max(1, min(int(limit or 20), 200))
    out = tweets[:capped]
    log.info("twitter_timeline_native_ok", handle=raw, returned=len(out), available=len(tweets))
    return out


def _features_from_switches(switches: list[str]) -> dict[str, bool]:
    features = {name: (name not in _FALSE_FEATURE_FLAGS) for name in switches}
    # Always include common flags the endpoint expects even if metadata omits them.
    for name in (
        "rweb_tipjar_consumption_enabled",
        "responsive_web_graphql_exclude_directive_enabled",
        "creator_subscriptions_tweet_preview_api_enabled",
        "responsive_web_graphql_timeline_navigation_enabled",
        "communities_web_enable_tweet_community_results_fetch",
        "c9s_tweet_anatomy_moderator_badge_enabled",
        "articles_preview_enabled",
        "responsive_web_edit_tweet_api_enabled",
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled",
        "view_counts_everywhere_api_enabled",
        "longform_notetweets_consumption_enabled",
        "responsive_web_twitter_article_tweet_consumption_enabled",
        "freedom_of_speech_not_reach_fetch_enabled",
        "standardized_nudges_misinfo",
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled",
        "rweb_video_timestamps_enabled",
        "longform_notetweets_rich_text_read_enabled",
        "longform_notetweets_inline_media_enabled",
    ):
        features.setdefault(name, name not in _FALSE_FEATURE_FLAGS)
    for name in _FALSE_FEATURE_FLAGS:
        features[name] = False
    return features


async def _guest_token(client: httpx.AsyncClient) -> tuple[str, str] | None:
    """Return ``(guest_token, cookie_header)`` from a public x.com visit."""
    try:
        resp = await client.get("https://x.com/")
    except httpx.HTTPError as exc:
        log.info("twitter_guest_home_fail", error=str(exc))
        return None
    gt = resp.cookies.get("gt")
    if not gt:
        m = re.search(r"gt=(\d{15,})", resp.text or "")
        gt = m.group(1) if m else None
    if not gt:
        log.info("twitter_guest_token_miss", status=resp.status_code)
        return None
    cookie = "; ".join(f"{k}={v}" for k, v in resp.cookies.items())
    return gt, cookie


async def _resolve_main_js(client: httpx.AsyncClient) -> str | None:
    for url in (
        "https://x.com/explore",
        "https://x.com/search?q=a&src=typed_query&f=live",
        "https://x.com/",
    ):
        try:
            resp = await client.get(url)
        except httpx.HTTPError:
            continue
        m = _MAIN_JS_RE.search(resp.text or "")
        if m:
            return m.group(0)
    # Last resort: Decodo-rendered shell often embeds the main bundle URL.
    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(
            "https://x.com/search?q=a&src=typed_query&f=live",
            timeout=90.0,
            headless="html",
        )
        if got:
            _status, body = got
            m = _MAIN_JS_RE.search(body or "")
            if m:
                return m.group(0)
    return None


async def _load_search_meta(
    client: httpx.AsyncClient, *, force: bool = False
) -> tuple[str, dict[str, bool]]:
    now = time.time()
    cached_qid = _search_meta_cache.get("qid")
    cached_features = _search_meta_cache.get("features")
    fetched_at = float(_search_meta_cache.get("fetched_at") or 0)
    if (
        not force
        and cached_qid
        and isinstance(cached_features, dict)
        and now - fetched_at < _SEARCH_META_TTL_S
    ):
        return str(cached_qid), cached_features

    qid = _FALLBACK_SEARCH_QID
    features = _features_from_switches([])
    main_url = await _resolve_main_js(client)
    if main_url:
        try:
            resp = await client.get(main_url)
            if resp.status_code == 200 and resp.text:
                m = _SEARCH_META_RE.search(resp.text)
                if m:
                    qid = m.group(1)
                    try:
                        switches = json.loads(m.group(2))
                    except ValueError:
                        switches = []
                    if isinstance(switches, list):
                        features = _features_from_switches(
                            [s for s in switches if isinstance(s, str)]
                        )
        except httpx.HTTPError as exc:
            log.info("twitter_search_main_js_fail", error=str(exc))

    _search_meta_cache["qid"] = qid
    _search_meta_cache["features"] = features
    _search_meta_cache["fetched_at"] = now
    return qid, features


def _gql_user(user: dict[str, Any]) -> dict[str, Any]:
    core = user.get("core") if isinstance(user.get("core"), dict) else {}
    legacy = user.get("legacy") if isinstance(user.get("legacy"), dict) else {}
    rel = user.get("relationship_counts") if isinstance(user.get("relationship_counts"), dict) else {}
    avatar = user.get("avatar") if isinstance(user.get("avatar"), dict) else {}
    verification = user.get("verification") if isinstance(user.get("verification"), dict) else {}
    return {
        "screen_name": core.get("screen_name") or legacy.get("screen_name"),
        "name": core.get("name") or legacy.get("name"),
        "followers_count": rel.get("followers") or legacy.get("followers_count"),
        "is_blue_verified": user.get("is_blue_verified"),
        "verified": verification.get("verified") if "verified" in verification else legacy.get("verified"),
        "profile_image_url_https": avatar.get("image_url") or legacy.get("profile_image_url_https"),
    }


def _gql_result_to_tweet(result: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(result, dict) or not result:
        return None
    if result.get("__typename") == "TweetWithVisibilityResults":
        nested = result.get("tweet")
        if not isinstance(nested, dict):
            return None
        result = nested
    legacy = result.get("legacy") if isinstance(result.get("legacy"), dict) else {}
    tid = safe_str(legacy.get("id_str")) or safe_str(result.get("rest_id"))
    if not tid:
        return None
    user_result = (
        ((result.get("core") or {}).get("user_results") or {}).get("result")
        if isinstance(result.get("core"), dict)
        else None
    )
    user = _gql_user(user_result) if isinstance(user_result, dict) else {}
    views = result.get("views") if isinstance(result.get("views"), dict) else {}
    out: dict[str, Any] = {
        "id_str": tid,
        "full_text": legacy.get("full_text") or legacy.get("text"),
        "created_at": legacy.get("created_at"),
        "lang": legacy.get("lang"),
        "favorite_count": legacy.get("favorite_count"),
        "reply_count": legacy.get("reply_count"),
        "retweet_count": legacy.get("retweet_count"),
        "quote_count": legacy.get("quote_count"),
        "bookmark_count": legacy.get("bookmark_count"),
        "view_count": safe_int(views.get("count")),
        "entities": legacy.get("entities"),
        "extended_entities": legacy.get("extended_entities"),
        "in_reply_to_status_id": legacy.get("in_reply_to_status_id_str"),
        "user": user,
    }
    rt_shell = result.get("retweeted_status_result") or legacy.get("retweeted_status_result")
    if isinstance(rt_shell, dict):
        rt_result = rt_shell.get("result") if isinstance(rt_shell.get("result"), dict) else rt_shell
        rt_tweet = _gql_result_to_tweet(rt_result) if isinstance(rt_result, dict) else None
        if rt_tweet:
            out["retweeted_status"] = rt_tweet
            out["is_retweet"] = True
    return out


def _parse_timeline_instructions(
    instructions: Any,
) -> tuple[list[dict[str, Any]], str | None]:
    tweets: list[dict[str, Any]] = []
    seen: set[str] = set()
    cursor: str | None = None
    if not isinstance(instructions, list):
        return tweets, cursor
    for instruction in instructions:
        if not isinstance(instruction, dict):
            continue
        entries = list(instruction.get("entries") or [])
        entry = instruction.get("entry")
        if isinstance(entry, dict):
            entries.append(entry)
        for item in entries:
            if not isinstance(item, dict):
                continue
            eid = str(item.get("entryId") or "")
            content = item.get("content") if isinstance(item.get("content"), dict) else {}
            if "cursor-bottom" in eid:
                cursor = safe_str(content.get("value")) or cursor
                continue
            result = (
                ((content.get("itemContent") or {}).get("tweet_results") or {}).get("result")
                if isinstance(content.get("itemContent"), dict)
                else None
            )
            tweet = _gql_result_to_tweet(result) if isinstance(result, dict) else None
            if not tweet:
                continue
            tid = tweet.get("id_str")
            if not tid or tid in seen:
                continue
            seen.add(str(tid))
            tweets.append(tweet)
    return tweets, cursor


def _parse_search_timeline(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    instructions = (
        (((payload.get("data") or {}).get("search_by_raw_query") or {}).get("search_timeline") or {})
        .get("timeline")
        or {}
    ).get("instructions") or []
    return _parse_timeline_instructions(instructions)


def _guest_headers(guest_token: str, cookie: str, referer: str) -> dict[str, str]:
    return {
        **_UA,
        "authorization": _PUBLIC_BEARER,
        "content-type": "application/json",
        "x-guest-token": guest_token,
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "en",
        "Origin": "https://x.com",
        "Referer": referer,
        "cookie": cookie,
    }


async def _gql_post(
    client: httpx.AsyncClient,
    *,
    operation: str,
    qid: str,
    variables: dict[str, Any],
    features: dict[str, bool],
    guest_token: str,
    cookie: str,
    referer: str,
) -> tuple[int, dict[str, Any] | None]:
    url = f"https://api.x.com/graphql/{qid}/{operation}"
    try:
        resp = await client.post(
            url,
            headers=_guest_headers(guest_token, cookie, referer),
            json={"variables": variables, "queryId": qid, "features": features},
        )
    except httpx.HTTPError as exc:
        log.info("twitter_gql_post_fail", operation=operation, error=str(exc))
        return 0, None
    if resp.status_code != 200:
        return resp.status_code, None
    try:
        payload = resp.json()
    except ValueError:
        return resp.status_code, None
    return resp.status_code, payload if isinstance(payload, dict) else None


def _ms_to_iso(value: Any) -> str | None:
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return safe_str(value)
    if ms <= 0:
        return None
    # X ships community created_at in milliseconds.
    if ms > 10_000_000_000:
        ms = ms / 1000
    return datetime.fromtimestamp(ms, tz=timezone.utc).isoformat()


def _community_banner(result: dict[str, Any]) -> str | None:
    for key in ("custom_banner_media", "default_banner_media", "banner"):
        media = result.get(key)
        if not isinstance(media, dict):
            continue
        info = media.get("media_info") if isinstance(media.get("media_info"), dict) else media
        url = safe_str(
            info.get("original_img_url")
            or info.get("url")
            or info.get("media_url_https")
        )
        if url:
            return url
    return None


def _normalize_community_result(result: dict[str, Any], community_id: str) -> dict[str, Any] | None:
    if not isinstance(result, dict) or result.get("__typename") == "CommunityUnavailable":
        return None
    cid = safe_str(result.get("id_str") or result.get("rest_id") or community_id)
    if not cid:
        return None
    creator_user = ((result.get("creator_results") or {}).get("result") or {})
    creator_user = creator_user if isinstance(creator_user, dict) else {}
    creator_core = creator_user.get("core") if isinstance(creator_user.get("core"), dict) else {}
    creator_legacy = creator_user.get("legacy") if isinstance(creator_user.get("legacy"), dict) else {}
    creator_username = safe_str(
        creator_core.get("screen_name")
        or creator_legacy.get("screen_name")
        or result.get("creator_username")
        or result.get("creatorUsername")
    )
    rules_out: list[dict[str, str]] = []
    for rule in result.get("rules") or []:
        if not isinstance(rule, dict):
            continue
        name = safe_str(rule.get("name"))
        if not name:
            continue
        item: dict[str, str] = {"name": name}
        desc = safe_str(rule.get("description"))
        if desc:
            item["description"] = desc
        rules_out.append(item)
    return {
        "platform": "twitter",
        "id": cid,
        "url": f"https://x.com/i/communities/{cid}",
        "name": safe_str(result.get("name")),
        "description": safe_str(result.get("description")),
        "memberCount": safe_int(result.get("member_count") or result.get("memberCount")),
        "createdAt": _ms_to_iso(result.get("created_at") or result.get("createdAt")),
        "creator": creator_username,
        "joinPolicy": safe_str(result.get("join_policy") or result.get("joinPolicy")),
        "isNsfw": bool(result.get("is_nsfw") or result.get("isNsfw") or False),
        "bannerImage": _community_banner(result),
        "rules": rules_out,
    }


def parse_community_html(html: str, community_id: str) -> dict[str, Any] | None:
    """OG-tag fallback when GraphQL community detail is unavailable."""
    if not html or not community_id:
        return None
    title_m = _OG_TITLE_RE.search(html)
    desc_m = _OG_DESC_RE.search(html)
    image_m = _OG_IMAGE_RE.search(html)
    name = unescape(title_m.group(1)).strip() if title_m else None
    if name and name.endswith(" on X"):
        name = name[: -len(" on X")].strip()
    description = unescape(desc_m.group(1)).strip() if desc_m else None
    banner = unescape(image_m.group(1)).replace("&amp;", "&").strip() if image_m else None
    if not name and not description:
        return None
    return {
        "platform": "twitter",
        "id": community_id,
        "url": f"https://x.com/i/communities/{community_id}",
        "name": name,
        "description": description,
        "memberCount": None,
        "createdAt": None,
        "creator": None,
        "joinPolicy": None,
        "isNsfw": None,
        "bannerImage": banner,
        "rules": [],
    }


def _community_result_from_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    return (((payload.get("data") or {}).get("communityResults") or {}).get("result") or None)


def _community_timeline_instructions(payload: dict[str, Any]) -> list[Any]:
    result = _community_result_from_payload(payload)
    if not isinstance(result, dict):
        return []
    for key in ("ranked_community_timeline", "community_timeline", "timeline"):
        block = result.get(key)
        if isinstance(block, dict):
            timeline = block.get("timeline") if isinstance(block.get("timeline"), dict) else block
            instructions = timeline.get("instructions") if isinstance(timeline, dict) else None
            if isinstance(instructions, list):
                return instructions
    return []


async def community(community_id: str) -> dict[str, Any] | None:
    """Public community details via guest GraphQL (HTML OG fallback)."""
    cid = (community_id or "").strip()
    if not cid.isdigit():
        return None
    referer = f"https://x.com/i/communities/{cid}"
    try:
        async with httpx.AsyncClient(timeout=25, headers=_UA, follow_redirects=True) as client:
            guest = await _guest_token(client)
            if guest:
                guest_token, cookie = guest
                _, features = await _load_search_meta(client)
                for qid in _COMMUNITY_DETAIL_QIDS:
                    for operation in ("CommunitiesFetchOneQuery", "CommunityByRestId"):
                        status, payload = await _gql_post(
                            client,
                            operation=operation,
                            qid=qid,
                            variables={"communityId": cid},
                            features=features,
                            guest_token=guest_token,
                            cookie=cookie,
                            referer=referer,
                        )
                        if status == 404:
                            continue
                        if not payload:
                            continue
                        result = _community_result_from_payload(payload)
                        parsed = _normalize_community_result(result, cid) if isinstance(result, dict) else None
                        if parsed and parsed.get("name"):
                            log.info(
                                "twitter_community_native_ok",
                                community_id=cid,
                                members=parsed.get("memberCount"),
                                source="graphql",
                            )
                            return parsed
    except httpx.HTTPError as exc:
        log.info("twitter_community_native_fail", error=str(exc))

    # OG tags from Decodo / direct page — name + description + banner only.
    html: str | None = None
    try:
        async with httpx.AsyncClient(timeout=20, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(referer)
            if resp.status_code == 200 and len(resp.text) > 1000:
                html = resp.text
    except httpx.HTTPError:
        html = None
    if (not html or "og:title" not in html) and decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(referer, timeout=120.0, headless="html")
        if got and got[0] == 200 and got[1]:
            html = got[1]
    parsed = parse_community_html(html or "", cid)
    if parsed:
        log.info("twitter_community_native_ok", community_id=cid, source="html")
    return parsed


async def community_tweets(
    community_id: str,
    limit: int = 25,
    *,
    ranking_mode: str = "Recency",
) -> list[dict[str, Any]] | None:
    """Community timeline via guest GraphQL CommunityTweetsTimeline."""
    cid = (community_id or "").strip()
    if not cid.isdigit():
        return None
    capped = max(1, min(int(limit or 25), 200))
    ranking = "Relevance" if str(ranking_mode).lower() in {"relevance", "top"} else "Recency"
    referer = f"https://x.com/i/communities/{cid}"

    try:
        async with httpx.AsyncClient(timeout=25, headers=_UA, follow_redirects=True) as client:
            guest = await _guest_token(client)
            if not guest:
                return None
            guest_token, cookie = guest
            _, features = await _load_search_meta(client)

            working_qid: str | None = None
            tweets: list[dict[str, Any]] = []
            cursor: str | None = None
            for qid in _COMMUNITY_TWEETS_QIDS:
                status, payload = await _gql_post(
                    client,
                    operation="CommunityTweetsTimeline",
                    qid=qid,
                    variables={
                        "communityId": cid,
                        "count": min(capped, 20),
                        "displayLocation": "Community",
                        "rankingMode": ranking,
                        "withCommunity": True,
                    },
                    features=features,
                    guest_token=guest_token,
                    cookie=cookie,
                    referer=referer,
                )
                if status == 404 or not payload:
                    continue
                tweets, cursor = _parse_timeline_instructions(
                    _community_timeline_instructions(payload)
                )
                if tweets:
                    working_qid = qid
                    break
            else:
                log.info("twitter_community_tweets_miss", community_id=cid)
                return None

            collected = list(tweets)
            seen = {str(t.get("id_str")) for t in collected if t.get("id_str")}
            max_pages = min(10, (capped + 19) // 20 + 1)
            page = 1
            while len(collected) < capped and cursor and page < max_pages:
                status, payload = await _gql_post(
                    client,
                    operation="CommunityTweetsTimeline",
                    qid=working_qid or _COMMUNITY_TWEETS_QIDS[0],
                    variables={
                        "communityId": cid,
                        "count": min(capped - len(collected), 20),
                        "cursor": cursor,
                        "displayLocation": "Community",
                        "rankingMode": ranking,
                        "withCommunity": True,
                    },
                    features=features,
                    guest_token=guest_token,
                    cookie=cookie,
                    referer=referer,
                )
                page += 1
                if status != 200 or not payload:
                    break
                more, cursor = _parse_timeline_instructions(
                    _community_timeline_instructions(payload)
                )
                added = 0
                for tweet in more:
                    tid = str(tweet.get("id_str") or "")
                    if not tid or tid in seen:
                        continue
                    seen.add(tid)
                    collected.append(tweet)
                    added += 1
                    if len(collected) >= capped:
                        break
                if added == 0:
                    break

            if not collected:
                return None
            log.info(
                "twitter_community_tweets_native_ok",
                community_id=cid,
                returned=len(collected[:capped]),
                ranking=ranking,
            )
            return collected[:capped]
    except httpx.HTTPError as exc:
        log.info("twitter_community_tweets_native_fail", error=str(exc))
        return None


async def _search_page(
    client: httpx.AsyncClient,
    *,
    query: str,
    limit: int,
    product: str,
    guest_token: str,
    cookie: str,
    qid: str,
    features: dict[str, bool],
    cursor: str | None = None,
) -> tuple[list[dict[str, Any]], str | None, int]:
    variables: dict[str, Any] = {
        "rawQuery": query,
        "count": max(1, min(limit, 20)),
        "querySource": "typed_query",
        "product": product,
        "withGrokTranslatedBio": False,
    }
    if cursor:
        variables["cursor"] = cursor
    headers = {
        **_UA,
        "authorization": _PUBLIC_BEARER,
        "content-type": "application/json",
        "x-guest-token": guest_token,
        # Required for guest SearchTimeline on api.x.com (plain guest → empty 404).
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "en",
        "Origin": "https://x.com",
        "Referer": f"https://x.com/search?q={query}&src=typed_query&f=live",
        "cookie": cookie,
    }
    # Guest search is accepted on api.x.com; x.com/i/api often 403/404s the same payload.
    url = f"https://api.x.com/graphql/{qid}/SearchTimeline"
    resp = await client.post(
        url,
        headers=headers,
        json={"variables": variables, "queryId": qid, "features": features},
    )
    if resp.status_code != 200:
        return [], None, resp.status_code
    try:
        payload = resp.json()
    except ValueError:
        return [], None, resp.status_code
    if not isinstance(payload, dict):
        return [], None, resp.status_code
    tweets, next_cursor = _parse_search_timeline(payload)
    return tweets, next_cursor, resp.status_code


async def search(
    query: str,
    limit: int = 20,
    *,
    product: str = "Top",
) -> list[dict[str, Any]] | None:
    """Public keyword search via guest-token GraphQL SearchTimeline."""
    q = (query or "").strip()
    if len(q) < 2:
        return None
    capped = max(1, min(int(limit or 20), 200))
    product = "Latest" if str(product).lower() == "latest" else "Top"

    try:
        async with httpx.AsyncClient(timeout=25, headers=_UA, follow_redirects=True) as client:
            guest = await _guest_token(client)
            if not guest:
                return None
            guest_token, cookie = guest
            qid, features = await _load_search_meta(client)

            collected: list[dict[str, Any]] = []
            seen: set[str] = set()
            cursor: str | None = None
            max_pages = min(10, (capped + 19) // 20 + 1)

            for page in range(max_pages):
                page_tweets, cursor, status = await _search_page(
                    client,
                    query=q,
                    limit=capped - len(collected),
                    product=product,
                    guest_token=guest_token,
                    cookie=cookie,
                    qid=qid,
                    features=features,
                    cursor=cursor,
                )
                if status == 404 and page == 0:
                    # Query id rotated — refresh main.js once and retry.
                    qid, features = await _load_search_meta(client, force=True)
                    page_tweets, cursor, status = await _search_page(
                        client,
                        query=q,
                        limit=capped,
                        product=product,
                        guest_token=guest_token,
                        cookie=cookie,
                        qid=qid,
                        features=features,
                        cursor=None,
                    )
                if status != 200:
                    log.info("twitter_search_gql_miss", status=status, page=page, query=q[:80])
                    break
                added = 0
                for tweet in page_tweets:
                    tid = str(tweet.get("id_str") or "")
                    if not tid or tid in seen:
                        continue
                    seen.add(tid)
                    collected.append(tweet)
                    added += 1
                    if len(collected) >= capped:
                        break
                if len(collected) >= capped or not cursor or added == 0:
                    break

            if not collected:
                return None
            log.info(
                "twitter_search_native_ok",
                query=q[:80],
                returned=len(collected[:capped]),
                product=product,
            )
            return collected[:capped]
    except httpx.HTTPError as exc:
        log.info("twitter_search_native_fail", error=str(exc))
        return None
