"""Self-scraped TikTok data from public web pages + mobile aweme APIs (no Apify).

TikTok web pages embed a ``__UNIVERSAL_DATA_FOR_REHYDRATION__`` JSON blob with
``webapp.video-detail`` (full video stats) and ``webapp.user-detail`` (full
profile stats). Fetching MUST go through the datacenter proxy tier: direct
requests from server IPs get an empty shell page without the blob.

List data (profile posts, comments) is NOT in the blob — the *web* XHR
endpoints need signed params — but TikTok's *mobile* aweme endpoints serve
logged-out lists with plain device params over a US residential IP.

Every function returns data in the exact shapes the router already emits, or
``None`` on failure so callers can fall back (or raise) as they choose.
"""

from __future__ import annotations

import asyncio
import json
import random
import re
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.http_fetch import fetch as proxy_fetch
from app.services.http_fetch import proxy_for
from app.utils.formatters import (
    duration_seconds,
    normalize_language_code,
    safe_float,
    safe_int,
    safe_str,
)

# TikTok often returns ISO-639-2 (eng) instead of ISO-639-1 (en).
_ISO639_2_TO_1 = {
    "eng": "en",
    "spa": "es",
    "fra": "fr",
    "deu": "de",
    "tur": "tr",
    "por": "pt",
    "ita": "it",
    "nld": "nl",
    "jpn": "ja",
    "kor": "ko",
    "zho": "zh",
    "ara": "ar",
    "hin": "hi",
    "rus": "ru",
    "ind": "id",
    "vie": "vi",
    "tha": "th",
    "pol": "pl",
}


def _normalize_tt_lang(value: str | None) -> str | None:
    code = normalize_language_code(value)
    if not code:
        return None
    return _ISO639_2_TO_1.get(code, code)

TT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.tiktok.com/",
}

_UNIVERSAL_RE = re.compile(
    r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', re.DOTALL
)


async def _fetch_scope(url: str) -> dict[str, Any] | None:
    """GET a TikTok page and return the ``__DEFAULT_SCOPE__`` dict."""
    from app.services import decodo_fetch

    async def _parse(text: str) -> dict[str, Any] | None:
        m = _UNIVERSAL_RE.search(text or "")
        if not m:
            return None
        try:
            data = json.loads(m.group(1))
        except ValueError:
            return None
        scope = data.get("__DEFAULT_SCOPE__")
        return scope if isinstance(scope, dict) else None

    for tier in ("datacenter", "residential"):
        for _ in range(2):  # occasional empty shell; one retry is cheap
            try:
                resp = await proxy_fetch(url, tier=tier, headers=TT_HEADERS, timeout=18)
            except httpx.HTTPError:
                break
            if resp.status_code >= 400:
                break
            scope = await _parse(resp.text)
            if scope is not None:
                return scope

    if decodo_fetch.enabled():
        got = await decodo_fetch.fetch_url(url, timeout=60.0, headless="html", geo="US")
        if got and got[0] == 200:
            scope = await _parse(got[1])
            if scope is not None:
                return scope
    return None


def _stat(stats_v2: dict[str, Any], stats: dict[str, Any], key: str) -> int | None:
    """statsV2 carries exact counts as strings; legacy stats rounds big ones."""
    return safe_int(stats_v2.get(key) if stats_v2.get(key) is not None else stats.get(key))


def coerce_stats_v2(stats: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize TikTok statsV2 string counts (e.g. \"1623\") to ints."""
    out: dict[str, Any] = {}
    for key, value in (stats or {}).items():
        if isinstance(value, bool):
            out[key] = value
            continue
        if isinstance(value, (int, float)):
            out[key] = int(value)
            continue
        parsed = safe_int(value)
        out[key] = parsed if parsed is not None else value
    return out


def _iso(create_time: Any) -> str | None:
    ts = safe_int(create_time)
    if not ts:
        return None
    # Match the Apify path's createTimeISO format (…T00:45:18.000Z) so publishedAt
    # is identical whichever source serves the request. TikTok timestamps are
    # whole seconds, so milliseconds are always .000.
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


async def video_details_native(url: str) -> dict[str, Any] | None:
    from app.utils.media_urls import earliest_cdn_expires_at, utc_now_iso

    scope = await _fetch_scope(url)
    if not scope:
        return None
    vd = scope.get("webapp.video-detail") or {}
    if vd.get("statusCode") != 0:
        return None  # deleted / private / region-locked -> let the actor try
    item = (vd.get("itemInfo") or {}).get("itemStruct") or {}
    if not item.get("id"):
        return None

    stats_v2 = item.get("statsV2") or {}
    stats = item.get("stats") or {}
    author = item.get("author") or {}
    author_stats = item.get("authorStats") or {}
    video = item.get("video") or {}
    music = item.get("music") or {}
    status = item.get("status") if isinstance(item.get("status"), dict) else {}
    username = safe_str(author.get("uniqueId"))
    fetched_at = utc_now_iso()

    hashtags = _collect_hashtags(item, safe_str(item.get("desc")))
    mentions = _collect_mentions(item)

    aweme_type = safe_int(item.get("awemeType") or item.get("aweme_type"))
    image_post = item.get("imagePost") or item.get("image_post") or item.get("image_post_info")
    shoot_tab = (safe_str(item.get("shootTabName") or item.get("shoot_tab_name")) or "").lower()
    if image_post or shoot_tab == "photo" or aweme_type in (150, 51, 68):
        media_type = "photo"
    else:
        media_type = "video"

    def _addr_url(addr: Any) -> str | None:
        if isinstance(addr, dict):
            return safe_str((addr.get("urlList") or [None])[0]) or safe_str(addr.get("uri"))
        return safe_str(addr)

    play_url = _addr_url(video.get("playAddr"))
    # Web itemStruct downloadAddr is watermarked; true no-watermark usually needs
    # a mobile aweme path (Phase 2). Surface both keys honestly.
    download_url = _addr_url(video.get("downloadAddr"))
    download_no_wm = _addr_url(
        video.get("downloadAddrNoWatermark")
        or video.get("downloadNoWatermarkAddr")
        or video.get("playAddrNoWatermark")
    )
    thumbnail_url = safe_str(video.get("cover") or video.get("originCover"))
    profile_image = safe_str(author.get("avatarLarger") or author.get("avatarMedium"))
    author_id = safe_str(author.get("id") or author.get("uid"))
    author_sec = safe_str(author.get("secUid"))
    author_region = safe_str(author.get("region") or item.get("authorRegion"))

    music_title = safe_str(music.get("title"))
    is_original = bool(music.get("original")) or (
        bool(music_title) and music_title.strip().lower() in {"original sound", "original sound -"}
    )
    # Exact counts live in statsV2; legacy stats often rounds large play counts.
    engagement_approx = not bool(stats_v2.get("playCount") or stats_v2.get("diggCount"))

    return {
        "platform": "tiktok",
        "url": f"https://www.tiktok.com/@{username}/video/{item['id']}" if username else url,
        "id": safe_str(item.get("id")),
        "caption": safe_str(item.get("desc")),
        "publishedAt": _iso(item.get("createTime")),
        "durationSeconds": duration_seconds(video.get("duration")),
        "thumbnailUrl": thumbnail_url,
        "mediaType": media_type,
        "width": safe_int(video.get("width")),
        "height": safe_int(video.get("height")),
        "videoUrl": play_url,
        "downloadUrl": download_url,
        "downloadUrlNoWatermark": download_no_wm,
        "hasWatermark": bool(download_url) and not download_no_wm,
        "mediaUrlsExpireAt": earliest_cdn_expires_at(
            play_url, download_url, download_no_wm, thumbnail_url, profile_image
        ),
        "authorId": author_id,
        "secUid": author_sec,
        "author": {
            **build_author(author, author_stats=author_stats, profile_image=profile_image),
            "followersAsOf": fetched_at,
            "region": author_region,
        },
        "engagement": {
            "views": _stat(stats_v2, stats, "playCount"),
            "likes": _stat(stats_v2, stats, "diggCount"),
            "comments": _stat(stats_v2, stats, "commentCount"),
            "shares": _stat(stats_v2, stats, "shareCount"),
            "saves": _stat(stats_v2, stats, "collectCount"),
            "isApproximate": engagement_approx,
        },
        "hashtags": hashtags,
        "mentions": mentions,
        "musicName": music_title,
        "musicId": safe_str(music.get("id") or music.get("idStr") or music.get("mid")),
        "musicAuthor": safe_str(music.get("authorName") or music.get("ownerNickname")),
        "isOriginalSound": is_original,
        "region": safe_str(item.get("locationCreated") or item.get("region")),
        "authorRegion": author_region,
        "isAd": bool(item.get("isAd")),
        "isCommerce": bool(
            item.get("isCommerce")
            or item.get("hasCommerceRight")
            or item.get("commercial_right_type")
            or item.get("commercialRightType")
        ),
        "isBrandedContent": bool(
            item.get("isBrandOrganic") or item.get("isBrandOrganicContent")
        ),
        "status": {
            "allowComment": None if status.get("allowComment") is None else bool(status.get("allowComment")),
            "allowShare": None if status.get("allowShare") is None else bool(status.get("allowShare")),
            "isPrivate": bool(
                status.get("privateStatus")
                or status.get("isPrivate")
                or item.get("forFriend")
            ),
            "isDeleted": bool(status.get("isDelete") or status.get("isDeleted")),
            "inReview": bool(status.get("inReviewing") or status.get("inReview")),
            "isProhibited": bool(status.get("isProhibited")),
        },
        "fetchedAt": fetched_at,
    }


async def fetch_video_bytes(url: str, max_bytes: int) -> bytes | None:
    """Download a TikTok video's media (watermarked) for transcription.

    The page's ``playAddr`` CDN URL only works with the cookies set by the
    page response (``tt_chain_token`` et al.) and from the same IP, so both
    requests must share one client + proxy connection.
    """
    proxy = proxy_for("datacenter")
    try:
        async with httpx.AsyncClient(
            timeout=30, follow_redirects=True, headers=TT_HEADERS, proxy=proxy
        ) as client:
            resp = await client.get(url)
            if resp.status_code >= 400:
                return None
            m = _UNIVERSAL_RE.search(resp.text)
            if not m:
                return None
            try:
                scope = json.loads(m.group(1)).get("__DEFAULT_SCOPE__") or {}
            except ValueError:
                return None
            item = ((scope.get("webapp.video-detail") or {}).get("itemInfo") or {}).get(
                "itemStruct"
            ) or {}
            video = item.get("video") or {}
            play = safe_str(video.get("playAddr") or video.get("downloadAddr"))
            if not play:
                return None
            media = await client.get(play, headers={**TT_HEADERS, "Range": "bytes=0-"})
            if media.status_code >= 400 or not media.content:
                return None
            if len(media.content) > max_bytes:
                return None
            return media.content
    except httpx.HTTPError:
        return None


# WebVTT cue timing: HH:MM:SS.mmm or MM:SS.mmm
_VTT_TS = re.compile(
    r"(?:(\d{2,}):)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(?:(\d{2,}):)?(\d{2}):(\d{2})\.(\d{3})"
)
_VTT_TAG_RE = re.compile(r"<[^>]+>")


def _vtt_timestamp_to_seconds(
    hours: str | None, minutes: str, seconds: str, millis: str
) -> float:
    return (
        int(hours or 0) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(millis) / 1000.0
    )


def _parse_webvtt(body: str) -> list[dict[str, Any]]:
    """Parse WebVTT cues into the API segment shape (start/duration/end/text)."""
    if not body or "-->" not in body:
        return []
    # Normalize newlines; drop BOM / WEBVTT header noise.
    text = body.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", text.strip())
    segments: list[dict[str, Any]] = []
    for block in blocks:
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        # Cue id line is optional; find the timing line.
        timing_idx = next((i for i, ln in enumerate(lines) if "-->" in ln), -1)
        if timing_idx < 0:
            continue
        m = _VTT_TS.search(lines[timing_idx])
        if not m:
            continue
        start = _vtt_timestamp_to_seconds(m.group(1), m.group(2), m.group(3), m.group(4))
        end = _vtt_timestamp_to_seconds(m.group(5), m.group(6), m.group(7), m.group(8))
        payload = " ".join(lines[timing_idx + 1 :])
        payload = _VTT_TAG_RE.sub("", payload)
        payload = (
            payload.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&nbsp;", " ")
            .strip()
        )
        if not payload:
            continue
        start_r = round(start, 3)
        end_r = round(max(end, start), 3)
        mm, ss = int(start_r // 60), int(start_r % 60)
        segments.append(
            {
                "text": payload,
                "start": start_r,
                "duration": round(max(end_r - start_r, 0), 3),
                "end": end_r,
                "timestamp": f"{mm:02d}:{ss:02d}",
            }
        )
    return segments


def _subtitle_tracks_from_video(video: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect caption track URLs from subtitleInfos and claInfo.captionInfos."""
    tracks: list[dict[str, Any]] = []

    for info in video.get("subtitleInfos") or []:
        if not isinstance(info, dict):
            continue
        url = safe_str(info.get("Url") or info.get("url"))
        if not url:
            continue
        fmt = (safe_str(info.get("Format") or info.get("format")) or "webvtt").lower()
        if "json" in fmt or fmt == "creator_caption":
            continue  # not WebVTT speech tracks
        lang = safe_str(
            info.get("LanguageCodeName")
            or info.get("languageCodeName")
            or info.get("LanguageCode")
            or info.get("language")
        )
        source = (safe_str(info.get("Source") or info.get("source")) or "").lower()
        tracks.append(
            {
                "url": url,
                "language": lang,
                "source": source,
                "format": fmt,
                "original": bool(
                    info.get("IsOriginalCaption")
                    or info.get("isOriginalCaption")
                    or source in {"asr", "auto", "mt_asr"}
                ),
            }
        )

    cla = video.get("claInfo") or {}
    if isinstance(cla, dict):
        for info in cla.get("captionInfos") or cla.get("captions") or []:
            if not isinstance(info, dict):
                continue
            url = safe_str(info.get("url") or info.get("Url"))
            if not url:
                url_list = info.get("urlList")
                if isinstance(url_list, list) and url_list:
                    url = safe_str(url_list[0])
            if not url:
                continue
            lang = safe_str(
                info.get("language")
                or info.get("languageCode")
                or info.get("LanguageCodeName")
            )
            tracks.append(
                {
                    "url": url,
                    "language": lang,
                    "source": (
                        safe_str(info.get("captionFormat") or info.get("source")) or ""
                    ).lower(),
                    "format": "webvtt",
                    "original": bool(
                        info.get("isAutoGenerated") or info.get("isOriginalCaption")
                    ),
                }
            )

    # Deduplicate by URL.
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for t in tracks:
        if t["url"] in seen:
            continue
        seen.add(t["url"])
        unique.append(t)
    return unique


def _pick_subtitle_track(
    tracks: list[dict[str, Any]], language: str | None
) -> dict[str, Any] | None:
    if not tracks:
        return None
    want = (language or "").strip().lower()
    if want:
        # Exact / prefix match on LanguageCodeName (e.g. en, en-US).
        for t in tracks:
            code = (t.get("language") or "").lower()
            if code == want or code.startswith(want + "-") or code.split("-")[0] == want:
                return t
    # Prefer original / ASR tracks, then any WebVTT.
    for t in tracks:
        if t.get("original"):
            return t
    for t in tracks:
        src = t.get("source") or ""
        if "asr" in src or src in {"1", "auto"}:
            return t
    return tracks[0]


def _transcript_proxy_candidates() -> list[str | None]:
    """Datacenter first, then Evomi US/NL residential (caption CDN soft-blocks)."""
    out: list[str | None] = []
    dc = proxy_for("datacenter")
    if dc:
        out.append(dc)
    for country in ("US", "NL"):
        rp = _residential_proxy(country)
        if rp and rp not in out:
            out.append(rp)
    if not out:
        out.append(None)
    return out


async def _transcript_once(
    url: str, language: str | None, proxy: str | None
) -> dict[str, Any] | None:
    """Page rehydration + WebVTT fetch on one client (shared cookies/IP)."""
    try:
        async with httpx.AsyncClient(
            timeout=20, follow_redirects=True, headers=TT_HEADERS, proxy=proxy
        ) as client:
            resp = await client.get(url)
            if resp.status_code >= 400:
                return None
            m = _UNIVERSAL_RE.search(resp.text)
            if not m:
                return None
            try:
                scope = json.loads(m.group(1)).get("__DEFAULT_SCOPE__") or {}
            except ValueError:
                return None
            vd = scope.get("webapp.video-detail") or {}
            status = vd.get("statusCode")
            if status is not None and status != 0:
                return None  # deleted / private / region-locked
            item = ((vd.get("itemInfo") or {}).get("itemStruct")) or {}
            if not item.get("id"):
                return None
            video = item.get("video") or {}
            track = _pick_subtitle_track(_subtitle_tracks_from_video(video), language)
            if not track:
                return None
            vtt_resp = await client.get(
                track["url"],
                headers={**TT_HEADERS, "Accept": "text/vtt,text/plain,*/*"},
            )
            if vtt_resp.status_code >= 400 or not vtt_resp.text:
                return None
            segments = _parse_webvtt(vtt_resp.text)
            if not segments:
                return None
            full = " ".join(s["text"] for s in segments).strip()
            if not full:
                return None
            return {
                "transcript": full,
                "transcriptSegments": segments,
                "language": _normalize_tt_lang(track.get("language")),
            }
    except httpx.HTTPError:
        return None


async def transcript_native(url: str, language: str | None = None) -> dict[str, Any] | None:
    """Pull TikTok's own caption track (WebVTT) without Apify or Whisper.

    Returns ``{transcript, transcriptSegments, language}`` or ``None`` when the
    video has no usable captions / page fetch fails. Callers fall through to
    Whisper.
    """
    for proxy in _transcript_proxy_candidates():
        result = await _transcript_once(url, language, proxy)
        if result:
            return result
    return None


async def _user_info(handle: str) -> dict[str, Any] | None:
    scope = await _fetch_scope(f"https://www.tiktok.com/@{handle}")
    if not scope:
        return None
    ui = (scope.get("webapp.user-detail") or {}).get("userInfo") or {}
    user = ui.get("user") or {}
    if not user.get("uniqueId"):
        return None
    return ui


async def channel_details_native(handle: str, url: str) -> dict[str, Any] | None:
    from app.utils.media_urls import utc_now_iso

    ui = await _user_info(handle)
    if ui is None:
        return None
    user = ui.get("user") or {}
    stats_v2 = ui.get("statsV2") or {}
    stats = ui.get("stats") or {}
    username = safe_str(user.get("uniqueId")) or handle
    bio_link_raw = user.get("bioLink")
    external_url: str | None = None
    bio_link_risk: Any = None
    if isinstance(bio_link_raw, dict):
        external_url = safe_str(bio_link_raw.get("link"))
        bio_link_risk = bio_link_raw.get("risk")
    elif bio_link_raw:
        external_url = safe_str(bio_link_raw)
    commerce = user.get("commerceUserInfo") or {}
    profile_image = safe_str(user.get("avatarLarger") or user.get("avatarMedium"))
    # Additive-only: keep the original 12 keys stable for existing parsers.
    return {
        "platform": "tiktok",
        "url": f"https://www.tiktok.com/@{username}",
        "username": username,
        "displayName": safe_str(user.get("nickname")),
        "bio": safe_str(user.get("signature")),
        "followers": _stat(stats_v2, stats, "followerCount"),
        "following": _stat(stats_v2, stats, "followingCount"),
        "likes": _stat(stats_v2, stats, "heartCount"),
        "postCount": _stat(stats_v2, stats, "videoCount"),
        "verified": user.get("verified"),
        "private": user.get("privateAccount"),
        "profileImage": profile_image,
        "externalUrl": external_url,
        "category": safe_str(commerce.get("category")),
        # --- additive identity / vetting / commerce ---
        "id": safe_str(user.get("id")),
        "secUid": safe_str(user.get("secUid")),
        "createTime": _iso(user.get("createTime")),
        "friendCount": _stat(stats_v2, stats, "friendCount"),
        "diggCount": _stat(stats_v2, stats, "diggCount"),
        "profileImageMedium": safe_str(user.get("avatarMedium")),
        "profileImageThumb": safe_str(user.get("avatarThumb")),
        "bioLinkRisk": bio_link_risk,
        "isCommerceUser": bool(commerce.get("commerceUser"))
        if commerce.get("commerceUser") is not None
        else None,
        "isSeller": user.get("ttSeller"),
        "isOrganization": user.get("isOrganization"),
        "isAdVirtual": user.get("isADVirtual"),
        "language": safe_str(user.get("language")),
        "commentSetting": user.get("commentSetting"),
        "duetSetting": user.get("duetSetting"),
        "stitchSetting": user.get("stitchSetting"),
        "downloadSetting": user.get("downloadSetting"),
        "followingVisibility": user.get("followingVisibility"),
        "uniqueIdModifyTime": _iso(user.get("uniqueIdModifyTime")),
        "nickNameModifyTime": _iso(user.get("nickNameModifyTime")),
        "fetchedAt": utc_now_iso(),
    }


# --- Comments (mobile aweme API, cursor-paginated) -------------------------
#
# Comments are NOT in the page's rehydration blob, and TikTok's *web* comment
# endpoint (www.tiktok.com/api/comment/list/) needs signed params (X-Bogus /
# msToken) and returns an empty body without them. The *mobile* aweme endpoint,
# however, serves logged-out comments with plain musical.ly device params and no
# signature — as long as the request exits from a residential IP (datacenter and
# some residential IPs get soft-blocked with status_code 2146). It is natively
# cursor-paginated: each page returns ``cursor`` (next offset), ``has_more``,
# and ``total``.
_TT_COMMENT_HOSTS = (
    "https://api22-normal-c-useast2a.tiktokv.com/aweme/v1/comment/list/",
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/comment/list/",
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/comment/list/",
    "https://api31-normal-useast2a.tiktokv.com/aweme/v1/comment/list/",
    "https://api.tiktokv.com/aweme/v1/comment/list/",
)
_TT_MOBILE_UA = (
    "com.zhiliaoapp.musically/2023600030 (Linux; U; Android 10; en; Pixel 4; "
    "Build/QQ3A.200805.001)"
)
_TT_COMMENT_PARAMS: dict[str, str] = {
    "aid": "1233",
    "device_id": "7318518857994389254",
    "iid": "7318518857994389254",
    "device_type": "Pixel 4",
    "device_platform": "android",
    "os_version": "10",
    "version_code": "230600",
    "app_name": "musical_ly",
    "channel": "googleplay",
    "region": "US",
    "sys_region": "US",
    "app_language": "en",
    "language": "en",
}


def _map_comment(c: dict[str, Any]) -> dict[str, Any] | None:
    cid = safe_str(c.get("cid") or c.get("id"))
    if not cid:
        return None
    user = c.get("user") if isinstance(c.get("user"), dict) else {}
    avatars = (user.get("avatar_thumb") or {}).get("url_list") or []
    # Stable commenter identity — handles rename/emoji display names.
    author_id = safe_str(user.get("uid") or user.get("id"))
    author_sec = safe_str(user.get("sec_uid") or user.get("secUid"))
    # Text-level language when TikTok sends comment_language; else the
    # commenter's account language (still useful for market listening).
    comment_language = safe_str(
        c.get("comment_language") or c.get("commentLanguage") or user.get("language")
    )
    reply_total = safe_int(
        c.get("reply_comment_total")
        or c.get("reply_comment_count")
        or c.get("reply_count")
        or c.get("replyCount")
    )
    if reply_total is None:
        nested = c.get("reply_comment")
        if isinstance(nested, list):
            reply_total = len(nested)
    like_count = safe_int(c.get("digg_count"))
    if like_count is None:
        like_count = safe_int(c.get("diggCount"))
    out: dict[str, Any] = {
        "id": cid,
        "text": (safe_str(c.get("text")) or "").strip(),
        # Keep username string (BC + still a useful key) — ids are additive.
        "author": safe_str(user.get("unique_id") or user.get("nickname")),
        "authorId": author_id,
        "authorSecUid": author_sec,
        "authorAvatarUrl": safe_str(avatars[0] if avatars else None),
        "commentLanguage": comment_language,
        "likeCount": like_count,
        "replyCount": reply_total,
        "publishedAt": _iso(c.get("create_time") or c.get("createTime")),
    }
    return {k: v for k, v in out.items() if v is not None}


def _residential_proxy(country: str = "US") -> str | None:
    """Residential proxy URL pinned to ``country`` (Evomi: ``pass_country-XX``).

    TikTok's mobile aweme APIs soft-block most exits; US (and often NL) are the
    geos that actually return data. Any existing ``_country-`` suffix on the
    password is replaced so callers can race multiple geos.
    """
    base = proxy_for("residential")
    if not base:
        return None
    try:
        scheme, rest = base.split("://", 1)
        creds, hostpart = rest.rsplit("@", 1)
        user, pwd = creds.split(":", 1)
    except ValueError:
        return base
    if "_country-" in pwd:
        pwd = pwd.split("_country-", 1)[0]
    return f"{scheme}://{user}:{pwd}_country-{country}@{hostpart}"


def _us_residential_proxy() -> str | None:
    """US-pinned residential proxy (comments path)."""
    return _residential_proxy("US")


async def _comment_once(
    host: str,
    params: dict[str, str],
    headers: dict[str, str],
    proxy: str | None = None,
) -> dict[str, Any] | None:
    """Single mobile-API request on a residential IP. None unless the response
    is a clean ``status_code == 0`` payload."""
    try:
        async with httpx.AsyncClient(
            timeout=12,
            follow_redirects=True,
            proxy=proxy or _us_residential_proxy(),
            headers=headers,
        ) as client:
            resp = await client.get(host, params=params)
    except httpx.HTTPError:
        return None
    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) and data.get("status_code") == 0 else None


def _comment_page_ok(page: dict[str, Any], *, expect_items: bool) -> bool:
    """Reject soft-block decoys: status_code 0 with an empty comment list."""
    comments = page.get("comments")
    if not isinstance(comments, list):
        return False
    if comments:
        return True
    return not expect_items


async def _comment_page(
    aweme_id: str, cursor: str, count: int, *, expect_items: bool = True
) -> dict[str, Any] | None:
    """One page of the mobile comment API, or None if every attempt is blocked.

    The residential pool rotates its exit IP per connection but a large share of
    IPs are soft-blocked (status_code 2146) at any moment, so we fire a batch of
    concurrent requests (each a fresh IP + geo) and take the first clean response.
    """
    headers = {"User-Agent": _TT_MOBILE_UA, "Accept": "application/json"}
    rounds = 5 if str(cursor) not in ("", "0") else 4
    concurrency = 16
    geos = ("US", "NL", "FR", "DE")

    async def _attempt(host: str, country: str) -> dict[str, Any] | None:
        did = str(random.randint(10**18, 10**19 - 1))
        params = {
            **_TT_COMMENT_PARAMS,
            "device_id": did,
            "iid": did,
            "aweme_id": aweme_id,
            "cursor": str(cursor),
            "count": str(max(1, min(count, 50))),
        }
        return await _comment_once(host, params, headers, _residential_proxy(country))

    for _ in range(rounds):
        tasks = [
            asyncio.create_task(
                _attempt(_TT_COMMENT_HOSTS[i % len(_TT_COMMENT_HOSTS)], geos[i % len(geos)])
            )
            for i in range(concurrency)
        ]
        try:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if res is not None and _comment_page_ok(res, expect_items=expect_items):
                    return res
        finally:
            for t in tasks:
                t.cancel()
        await asyncio.sleep(0.2)
    return None


async def _comment_page_via_signer(
    aweme_id: str, cursor: str, count: int, *, expect_items: bool = True
) -> dict[str, Any] | None:
    """Signed web ``/api/comment/list/`` when mobile aweme soft-blocks."""
    from app.services import tiktok_signer

    if not tiktok_signer.enabled() or not aweme_id:
        return None
    cur = str(cursor or "0")
    api = (
        "https://www.tiktok.com/api/comment/list/"
        f"?aid=1988&aweme_id={urllib.parse.quote(aweme_id)}"
        f"&count={max(1, min(count, 50))}&cursor={urllib.parse.quote(cur)}"
    )
    for _ in range(2):
        page = await tiktok_signer.fetch_api(api)
        if not isinstance(page, dict):
            continue
        # Web shape uses camelCase; normalize to mobile keys used by mapper.
        comments = page.get("comments") or page.get("comment_list") or page.get("commentList")
        if not isinstance(comments, list):
            continue
        normalized = {
            "status_code": 0,
            "comments": comments,
            "cursor": page.get("cursor"),
            "has_more": page.get("has_more")
            if "has_more" in page
            else page.get("hasMore"),
            "total": page.get("total") or page.get("totalCount"),
        }
        if _comment_page_ok(normalized, expect_items=expect_items):
            return normalized
    return None


async def comments_native(
    aweme_id: str, cursor: str | None, limit: int
) -> tuple[list[dict[str, Any]], str | None, int | None] | None:
    """Fetch up to ``limit`` comments starting at ``cursor`` (offset).

    Returns ``(comments, next_cursor, total)`` where ``next_cursor`` is the
    offset to resume from (``None`` once the thread is exhausted) and ``total``
    is the video's total comment count. Returns ``None`` if the very first page
    fails so the caller can fall back to the Apify actor.
    """
    collected: list[dict[str, Any]] = []
    cur = str(cursor) if cursor else "0"
    total: int | None = None
    max_pages = limit // 15 + 3
    for page_i in range(max_pages):
        if len(collected) >= limit:
            break
        want = min(30, limit - len(collected))
        # First page of a public video almost always has comments; empty soft-
        # block decoys must be rejected. Later pages may legitimately be empty.
        expect_items = page_i == 0 and cur in ("", "0")
        page = await _comment_page(aweme_id, cur, want, expect_items=expect_items)
        if page is None:
            page = await _comment_page_via_signer(
                aweme_id, cur, want, expect_items=expect_items
            )
        if page is None:
            # Total failure on the first page -> let the caller use Apify.
            # A later-page failure returns what we have plus the resume cursor.
            return None if not collected else (collected, cur, total)
        if total is None:
            total = safe_int(page.get("total"))
        for c in page.get("comments") or []:
            mapped = _map_comment(c)
            if mapped:
                collected.append(mapped)
        nxt = page.get("cursor")
        cur = str(nxt) if nxt is not None else cur
        if not page.get("has_more"):
            return collected, None, total
    return collected, cur, total


# Reply threads use the same mobile hosts with ``/comment/list/reply/``.
_TT_REPLY_HOSTS = tuple(
    h.replace("/comment/list/", "/comment/list/reply/") for h in _TT_COMMENT_HOSTS
)


def _map_reply(c: dict[str, Any]) -> dict[str, Any] | None:
    """Map a mobile reply row to the public comment-replies shape."""
    mapped = _map_comment(c)
    if mapped is None:
        return None
    user = c.get("user") if isinstance(c.get("user"), dict) else {}
    verified = user.get("is_verified") or user.get("verified")
    out: dict[str, Any] = {
        "id": mapped["id"],
        "text": mapped["text"],
        "author": mapped["author"],
        "authorId": mapped.get("authorId"),
        "authorSecUid": mapped.get("authorSecUid"),
        "authorName": safe_str(user.get("nickname") or user.get("nickName")),
        "commentLanguage": mapped.get("commentLanguage"),
        "likeCount": mapped.get("likeCount"),
        "publishedAt": mapped["publishedAt"],
        "verified": False if verified is None else bool(verified),
        "profileImage": mapped.get("authorAvatarUrl"),
    }
    return {k: v for k, v in out.items() if v is not None}


async def _reply_page(
    aweme_id: str, comment_id: str, cursor: str, count: int
) -> dict[str, Any] | None:
    """One page of replies under ``comment_id``, or None if every attempt is blocked."""
    did = str(random.randint(10**18, 10**19 - 1))
    params = {
        **_TT_COMMENT_PARAMS,
        "device_id": did,
        "iid": did,
        "aweme_id": aweme_id,
        "comment_id": str(comment_id),
        "cursor": str(cursor),
        "count": str(count),
    }
    headers = {"User-Agent": _TT_MOBILE_UA, "Accept": "application/json"}
    geos = ("US", "NL")
    for _ in range(2):
        tasks = [
            asyncio.create_task(
                _comment_once(
                    _TT_REPLY_HOSTS[i % len(_TT_REPLY_HOSTS)],
                    params,
                    headers,
                    _residential_proxy(geos[i % len(geos)]),
                )
            )
            for i in range(8)
        ]
        try:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if res is not None and isinstance(res.get("comments"), list):
                    return res
        finally:
            for t in tasks:
                t.cancel()
    return None


async def comment_replies_native(
    aweme_id: str, comment_id: str, cursor: str | None, limit: int
) -> tuple[list[dict[str, Any]], str | None, int | None] | None:
    """Fetch up to ``limit`` replies under ``comment_id`` starting at ``cursor``.

    Returns ``(replies, next_cursor, total)``. ``None`` on first-page failure so
    the router can fall back to Apify.
    """
    collected: list[dict[str, Any]] = []
    cur = str(cursor) if cursor else "0"
    total: int | None = None
    max_pages = max(3, limit // 15 + 2)
    for _ in range(max_pages):
        if len(collected) >= limit:
            break
        want = min(30, limit - len(collected))
        page = await _reply_page(aweme_id, comment_id, cur, want)
        if page is None:
            return None if not collected else (collected, cur, total)
        if total is None:
            total = safe_int(page.get("total"))
        for c in page.get("comments") or []:
            mapped = _map_reply(c)
            if mapped:
                collected.append(mapped)
                if len(collected) >= limit:
                    break
        nxt = page.get("cursor")
        cur = str(nxt) if nxt is not None else cur
        if not page.get("has_more"):
            return collected[:limit], None, total
    return collected[:limit], cur, total


async def profile_region_native(handle: str) -> dict[str, Any] | None:
    """Region/language signals from the profile page.

    Returns None when the page exposes neither region nor language, so the
    caller can fall back to the actor (which samples video caption language).
    """
    ui = await _user_info(handle)
    if ui is None:
        return None
    user = ui.get("user") or {}
    region = safe_str(user.get("region"))
    language = safe_str(user.get("language"))
    if not region and not language:
        return None
    stats_v2 = ui.get("statsV2") or {}
    stats = ui.get("stats") or {}
    username = safe_str(user.get("uniqueId")) or handle
    return {
        "platform": "tiktok",
        "username": username,
        "displayName": safe_str(user.get("nickname")),
        "url": f"https://www.tiktok.com/@{username}",
        "region": region,
        "language": language,
        "followers": _stat(stats_v2, stats, "followerCount"),
        "following": _stat(stats_v2, stats, "followingCount"),
        "likes": _stat(stats_v2, stats, "heartCount"),
        "videos": _stat(stats_v2, stats, "videoCount"),
        "verified": user.get("verified"),
        "private": user.get("privateAccount"),
        "profileImage": safe_str(user.get("avatarLarger") or user.get("avatarMedium")),
        # roomId/eventList/shortDramaCreator often arrive empty from TikTok itself
        # ("" / [] / {}); keep them in raw when present so live/event profiles still surface.
        "raw": {"user": user, "statsV2": coerce_stats_v2(stats_v2)},
    }


# --- Channel posts (mobile aweme/post API, cursor-paginated) ---------------
#
# Profile post lists are not in the rehydration blob, and the web
# ``/api/post/item_list/`` endpoint needs signed params. The mobile
# ``/aweme/v1/aweme/post/`` endpoint, however, returns logged-out post pages
# with ``sec_user_id`` + plain device params — same residential soft-block
# pattern as comments (empty body / status 2146). Pagination uses TikTok's
# own ``max_cursor`` timestamp cursor and ``has_more`` flag.
_TT_POST_HOSTS = (
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/post/",
    "https://api22-normal-c-useast2a.tiktokv.com/aweme/v1/aweme/post/",
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/post/",
    "https://api31-normal-useast2a.tiktokv.com/aweme/v1/aweme/post/",
    "https://api.tiktokv.com/aweme/v1/aweme/post/",
)


def _url_list_first(node: Any) -> str | None:
    if isinstance(node, dict):
        urls = node.get("url_list") or node.get("urlList") or []
        return safe_str(urls[0] if urls else None)
    return safe_str(node)


# Caption fallback only when text_extra / cha_list are absent. Regex over
# caption glues trailing emoji onto the tag ("#okaralover💪💪❤️").
_HASHTAG_RE = re.compile(r"#([^\s#]+)")
_HASHTAG_EMOJI_TRAIL_RE = re.compile(
    r"(?:"
    r"[\U0001F300-\U0001FAFF]"
    r"|[\U00002700-\U000027BF]"
    r"|[\U0001F600-\U0001F64F]"
    r"|[\U00002600-\U000026FF]"
    r"|[\U0000FE00-\U0000FE0F]"
    r"|[\U0000200D]"
    r"|[\U0001F1E0-\U0001F1FF]"
    r"|[\U0000E000-\U0000F8FF]"
    r")+$"
)


def _normalize_hashtag_name(raw: Any, *, from_regex: bool = False) -> str | None:
    name = safe_str(raw)
    if not name:
        return None
    name = name.lstrip("#").strip()
    if from_regex:
        name = _HASHTAG_EMOJI_TRAIL_RE.sub("", name).strip()
    return name or None


def normalize_hashtag_query(raw: str | None) -> str | None:
    """Strip ``#`` / whitespace; lowercase for stable matching."""
    tag = (raw or "").lstrip("#").strip()
    return tag.casefold() if tag else None


def item_has_hashtag(item: dict[str, Any], tag: str) -> bool:
    """True when the post is tagged with ``tag`` (structured fields or ``#tag`` in caption).

    Username / keyword matches do **not** count — a video from ``@comedy7092`` with
    empty hashtags is not a ``#comedy`` result.
    """
    want = normalize_hashtag_query(tag)
    if not want or not isinstance(item, dict):
        return False
    # Prefer already-mapped hashtags[] (strings or {name}).
    for h in item.get("hashtags") or []:
        name = h.get("name") if isinstance(h, dict) else h
        if normalize_hashtag_query(safe_str(name)) == want:
            return True
    # Raw TikTok / actor shapes before mapping.
    if want in _collect_hashtags(
        item,
        safe_str(item.get("caption") or item.get("desc") or item.get("text") or item.get("title")),
    ):
        return True
    caption = safe_str(
        item.get("caption") or item.get("desc") or item.get("text") or item.get("title")
    )
    if not caption:
        return False
    # Token match: #comedy but not #comedytime (word-ish boundary after tag).
    return bool(
        re.search(
            rf"(?i)(?:^|[^a-z0-9_])#{re.escape(want)}(?:$|[^a-z0-9_])",
            caption,
        )
    )


def _collect_hashtags(item: dict[str, Any], caption: str | None) -> list[str]:
    """Canonical hashtags from TikTok structured fields; caption is last resort.

    Prefer ``text_extra[].hashtag_name`` / ``cha_list`` / actor ``hashtags``.
    When any structured tag exists, skip caption regex entirely — that avoids
    emoji bleed, case doubles (``Latinus`` + ``latinus``), and dupes.
    Stored form is lowercase for stable counting.
    """
    seen: set[str] = set()
    out: list[str] = []

    def _add(raw: Any, *, from_regex: bool = False) -> bool:
        name = _normalize_hashtag_name(raw, from_regex=from_regex)
        if not name:
            return False
        key = name.casefold()
        if key in seen:
            return True
        seen.add(key)
        out.append(key)
        return True

    structured = False
    for te in item.get("text_extra") or item.get("textExtra") or []:
        if isinstance(te, dict) and _add(te.get("hashtag_name") or te.get("hashtagName")):
            structured = True
    for cha in item.get("cha_list") or item.get("chaList") or item.get("challenges") or []:
        if isinstance(cha, dict) and _add(
            cha.get("cha_name") or cha.get("chaName") or cha.get("title")
        ):
            structured = True
    for h in item.get("hashtags") or []:
        if isinstance(h, dict):
            if _add(h.get("name") or h.get("title") or h.get("hashtag_name")):
                structured = True
        elif _add(h):
            structured = True

    if not structured and caption:
        for tag in _HASHTAG_RE.findall(caption):
            _add(tag, from_regex=True)
    return out


def _collect_mentions(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Mentions from ``text_extra`` (userId / secUid / username + offsets).

    No caption-@ regex — TikTok's mention spans are often display names with
    spaces/emoji, not @handles. Structured rows carry stable ids.
    """
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for te in item.get("text_extra") or item.get("textExtra") or []:
        if not isinstance(te, dict):
            continue
        if te.get("hashtag_name") or te.get("hashtagName") or te.get("hashtag_id") or te.get(
            "hashtagId"
        ):
            continue
        user_id = safe_str(te.get("user_id") or te.get("userId"))
        sec = safe_str(te.get("sec_uid") or te.get("secUid"))
        username = safe_str(
            te.get("user_unique_id")
            or te.get("userUniqueId")
            or te.get("unique_id")
            or te.get("uniqueId")
        )
        if not (user_id or sec or username):
            continue
        key = sec or user_id or username.casefold()
        if key in seen:
            continue
        seen.add(key)
        row: dict[str, Any] = {
            "userId": user_id,
            "secUid": sec,
            "username": username,
            "start": safe_int(te.get("start")),
            "end": safe_int(te.get("end")),
        }
        out.append(row)
    return out


def _extract_photo_images(image_post: Any) -> list[str]:
    """URLs from ``image_post`` / ``image_post_info`` carousel payloads."""
    if not isinstance(image_post, dict):
        return []
    images = image_post.get("images") or image_post.get("imageList") or []
    if not isinstance(images, list):
        return []
    out: list[str] = []
    for img in images:
        if isinstance(img, str):
            url = safe_str(img)
        elif isinstance(img, dict):
            url = (
                _url_list_first(img.get("display_image") or img.get("displayImage"))
                or _url_list_first(
                    img.get("owner_watermark_image") or img.get("ownerWatermarkImage")
                )
                or _url_list_first(
                    img.get("user_watermark_image") or img.get("userWatermarkImage")
                )
                or _url_list_first(img.get("thumbnail"))
                or _url_list_first(img.get("imageURL") or img.get("imageUrl"))
                or safe_str(img.get("url"))
            )
        else:
            url = None
        if url and url not in out:
            out.append(url)
    return out


def author_verified_flag(author: dict[str, Any] | None) -> bool | None:
    """True/False when TikTok exposes a badge signal; None when the surface omits it.

    MUSIC_AWEME (music-posts) and similar list surfaces often ship author cards
    without ``verified`` / ``custom_verify``. Missing must stay ``null`` —
    ``false`` means "confirmed unverified" and causes false negatives
    (e.g. Khaby Lame). Prefer Channel Details when you need a definitive badge.
    """
    if not isinstance(author, dict):
        return None
    for key in ("verified", "is_verified", "isVerified"):
        if key in author and author.get(key) is not None:
            return bool(author.get(key))
    custom = author.get("custom_verify")
    enterprise = author.get("enterprise_verify_reason")
    if custom is not None or enterprise is not None:
        return bool(custom) or bool(enterprise)
    vtype = author.get("verification_type")
    if vtype is None:
        return None
    try:
        return int(vtype) != 0
    except (TypeError, ValueError):
        return bool(vtype)


# Stable post-author keys — always present (null when the surface omits data).
AUTHOR_NULLABLE_KEYS = ("id", "secUid", "followers", "verified")


def build_author(
    author: dict[str, Any] | None,
    *,
    author_stats: dict[str, Any] | None = None,
    profile_image: str | None = None,
) -> dict[str, Any]:
    """One author shape for every TikTok post list endpoint.

    MUSIC_AWEME often omits ``follower_count`` / badge fields — those stay
    ``null`` (key present). Never drop ``followers`` just because it is unknown;
    that made music-posts look like a different schema than top-search.
    """
    author = author if isinstance(author, dict) else {}
    stats = author_stats if isinstance(author_stats, dict) else {}
    username = safe_str(
        author.get("unique_id")
        or author.get("uniqueId")
        or author.get("name")
        or author.get("unique_name")
    )
    avatar = profile_image or (
        _url_list_first(author.get("avatar_larger") or author.get("avatarLarger"))
        or _url_list_first(author.get("avatar_medium") or author.get("avatarMedium"))
        or _url_list_first(author.get("avatar_thumb") or author.get("avatarThumb"))
        or safe_str(
            author.get("avatar")
            or author.get("avatarLarger")
            or author.get("originalAvatarUrl")
            or author.get("profileImage")
        )
    )
    return {
        "id": safe_str(
            author.get("uid") or author.get("id") or author.get("user_id") or author.get("userId")
        ),
        "secUid": safe_str(author.get("sec_uid") or author.get("secUid")),
        "username": username,
        "displayName": safe_str(
            author.get("nickname") or author.get("nickName") or author.get("displayName")
        ),
        "url": safe_str(author.get("profileUrl") or author.get("profile_url"))
        or (f"https://www.tiktok.com/@{username}" if username else None),
        "followers": safe_int(
            author.get("follower_count")
            or author.get("followerCount")
            or author.get("fans")
            or author.get("followers")
            or stats.get("follower_count")
            or stats.get("followerCount")
        ),
        "verified": author_verified_flag(author),
        "profileImage": avatar,
    }


def _map_aweme_post(item: dict[str, Any]) -> dict[str, Any] | None:
    """Map a mobile aweme row to the same post shape as video_details_native.

    Top search / hashtag feeds return both videos and photo carousels — keep
    ``mediaType`` / ``contentType`` / ``images`` so clients do not have to
    guess from a missing ``durationSeconds``.
    """
    aweme_id = safe_str(item.get("aweme_id") or item.get("id"))
    if not aweme_id:
        return None
    author = item.get("author") or {}
    if not isinstance(author, dict):
        author = {}
    stats = item.get("statistics") or item.get("stats") or {}
    if not isinstance(stats, dict):
        stats = {}
    video = item.get("video") or {}
    if not isinstance(video, dict):
        video = {}
    music = item.get("music") or {}
    if not isinstance(music, dict):
        music = {}
    author_stats = item.get("author_stats") or item.get("authorStats") or {}
    if not isinstance(author_stats, dict):
        author_stats = {}

    username = safe_str(author.get("unique_id") or author.get("uniqueId"))
    duration = safe_float(video.get("duration") or item.get("duration"))
    # Mobile aweme occasionally reports duration in milliseconds.
    if duration is not None and duration > 1000:
        duration = duration / 1000.0
    duration = duration_seconds(duration)

    caption = safe_str(item.get("desc"))
    hashtags = _collect_hashtags(item, caption)
    mentions = _collect_mentions(item)

    aweme_type = safe_int(item.get("aweme_type") or item.get("awemeType"))
    image_post = (
        item.get("image_post_info")
        or item.get("image_post")
        or item.get("imagePost")
    )
    shoot_tab = (
        safe_str(item.get("shoot_tab_name") or item.get("shootTabName")) or ""
    ).lower()
    # 150/51 = TikTok photo mode; 68 = slideshow / image-text (Douyin/TT).
    is_photo = bool(image_post) or shoot_tab == "photo" or aweme_type in (150, 51, 68)
    images = _extract_photo_images(image_post) if is_photo else []
    if is_photo:
        media_type = "photo"
        content_type = "multi_photo" if len(images) > 1 else "photo"
    else:
        media_type = "video"
        content_type = "video"

    avatar = (
        _url_list_first(author.get("avatar_larger") or author.get("avatarLarger"))
        or _url_list_first(author.get("avatar_medium") or author.get("avatarMedium"))
        or _url_list_first(author.get("avatar_thumb") or author.get("avatarThumb"))
    )
    cover = (
        _url_list_first(video.get("cover"))
        or _url_list_first(video.get("origin_cover") or video.get("originCover"))
        or _url_list_first(video.get("dynamic_cover") or video.get("dynamicCover"))
    )
    if not cover and isinstance(image_post, dict):
        cover = (
            _url_list_first(
                image_post.get("image_post_cover")
                or image_post.get("imagePostCover")
                or image_post.get("cover")
                or image_post.get("imageURL")
            )
            or (images[0] if images else None)
        )

    author_out = build_author(author, author_stats=author_stats, profile_image=avatar)
    kind = "photo" if is_photo else "video"
    url = (
        f"https://www.tiktok.com/@{username}/{kind}/{aweme_id}"
        if username
        else safe_str(item.get("share_url") or item.get("shareUrl"))
    )

    out: dict[str, Any] = {
        "platform": "tiktok",
        "url": url,
        "id": aweme_id,
        "caption": caption,
        "publishedAt": _iso(item.get("create_time") or item.get("createTime")),
        "durationSeconds": duration,
        "thumbnailUrl": cover,
        "mediaType": media_type,
        "contentType": content_type,
        "author": author_out,
        "engagement": {
            "views": safe_int(stats.get("play_count") or stats.get("playCount")) or 0,
            "likes": safe_int(stats.get("digg_count") or stats.get("diggCount")) or 0,
            "comments": safe_int(stats.get("comment_count") or stats.get("commentCount")) or 0,
            "shares": safe_int(stats.get("share_count") or stats.get("shareCount")) or 0,
            "saves": safe_int(stats.get("collect_count") or stats.get("collectCount")) or 0,
        },
        "hashtags": hashtags,
        "mentions": mentions,
        "musicName": safe_str(music.get("title")),
        "musicId": safe_str(music.get("id") or music.get("id_str") or music.get("mid")),
        "musicAuthor": safe_str(
            music.get("authorName")
            or music.get("author_name")
            or music.get("ownerNickname")
            or music.get("owner_nickname")
        ),
        "isAd": bool(item.get("is_ad") or item.get("isAd")),
        "isPaidPartnership": bool(
            item.get("is_paid_partnership")
            or item.get("isPaidPartnership")
            or item.get("is_paid_content")
            or item.get("isPaidContent")
        ),
    }
    if images:
        out["images"] = images
    return out


def _post_page_ok(page: dict[str, Any], *, expect_items: bool) -> bool:
    """Reject soft-block decoys: status_code 0 with an empty aweme_list.

    Blocked exits often answer with ``status_code == 0``, ``aweme_list: []``
    (sometimes echoing ``max_cursor``). A profile that has videos never
    legitimately returns an empty page — the last page still has items with
    ``has_more == 0`` — so empty payloads are always treated as a miss when
    ``expect_items`` is true.
    """
    awemes = page.get("aweme_list")
    if not isinstance(awemes, list):
        return False
    if awemes:
        return True
    return not expect_items


async def _post_page(
    sec_user_id: str, max_cursor: str, count: int, *, expect_items: bool
) -> dict[str, Any] | None:
    """One page of the mobile user-post API, or None if every attempt is blocked."""
    # ``max_cursor`` is the real pager; ``cursor`` is accepted as an alias on
    # some hosts. Deeper pages are softer-blocked, so we race harder for them.
    headers = {"User-Agent": _TT_MOBILE_UA, "Accept": "application/json"}
    # Soft-block rate is high; race more exits. US/NL are best; FR/DE help
    # occasionally. Caller may still fall through to signer / Decodo.
    rounds = 5 if max_cursor not in ("", "0") else 4
    concurrency = 16
    geos = ("US", "NL", "FR", "DE")

    async def _attempt(host: str, country: str) -> dict[str, Any] | None:
        did = str(random.randint(10**18, 10**19 - 1))
        # Both max_cursor and cursor must be set (including on page 2+); hosts
        # that only see max_cursor often return empty soft-block decoys.
        params = {
            **_TT_COMMENT_PARAMS,
            "device_id": did,
            "iid": did,
            "sec_user_id": sec_user_id,
            "count": str(max(1, min(count, 35))),
            "max_cursor": str(max_cursor),
            "min_cursor": "0",
            "cursor": str(max_cursor),
        }
        return await _comment_once(host, params, headers, _residential_proxy(country))

    for _ in range(rounds):
        tasks = [
            asyncio.create_task(
                _attempt(_TT_POST_HOSTS[i % len(_TT_POST_HOSTS)], geos[i % len(geos)])
            )
            for i in range(concurrency)
        ]
        try:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if res is not None and _post_page_ok(res, expect_items=expect_items):
                    return res
        finally:
            for t in tasks:
                t.cancel()
        await asyncio.sleep(0.2)
    return None


def _web_posts_as_aweme_page(page: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize web ``/api/post/item_list/`` JSON to the mobile aweme shape."""
    items = page.get("itemList") or page.get("item_list") or page.get("aweme_list")
    if not isinstance(items, list):
        return None
    cursor = page.get("cursor")
    if cursor is None:
        cursor = page.get("max_cursor") or page.get("maxCursor")
    has_more = page.get("hasMore")
    if has_more is None:
        has_more = page.get("has_more")
    return {
        "status_code": 0,
        "aweme_list": items,
        "max_cursor": cursor,
        "has_more": bool(has_more),
    }


async def _post_page_via_signer(
    sec_user_id: str, max_cursor: str, count: int, *, expect_items: bool
) -> dict[str, Any] | None:
    """Signed web ``/api/post/item_list/`` — works when mobile aweme soft-blocks."""
    from app.services import tiktok_signer

    if not tiktok_signer.enabled() or not sec_user_id:
        return None
    cur = str(max_cursor or "0")
    api = (
        "https://www.tiktok.com/api/post/item_list/"
        f"?aid=1988&count={max(1, min(count, 35))}"
        f"&cursor={urllib.parse.quote(cur)}"
        f"&secUid={urllib.parse.quote(sec_user_id)}"
    )
    for _ in range(2):
        page = await tiktok_signer.fetch_api(api)
        if not isinstance(page, dict):
            continue
        normalized = _web_posts_as_aweme_page(page)
        if normalized is not None and _post_page_ok(normalized, expect_items=expect_items):
            return normalized
    return None


async def _post_page_via_decodo(handle: str, *, expect_items: bool) -> dict[str, Any] | None:
    """First-page posts via Decodo capturing ``api/post/item_list`` XHR."""
    from app.services import decodo_fetch

    username = (handle or "").lstrip("@").strip()
    if not username or not decodo_fetch.enabled():
        return None
    url = f"https://www.tiktok.com/@{username}"
    fetched = None
    for _ in range(2):
        fetched = await decodo_fetch.fetch_url(
            url,
            timeout=120.0,
            target="universal",
            headless="html",
            geo="US",
            browser_actions=[
                {
                    "type": "fetch_resource",
                    "filter": "api/post/item_list",
                    "on_error": "error",
                }
            ],
        )
        if fetched is not None:
            break
    if fetched is None:
        return None
    _status, content = fetched
    try:
        payload = json.loads(content)
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    normalized = _web_posts_as_aweme_page(payload)
    if normalized is not None and _post_page_ok(normalized, expect_items=expect_items):
        return normalized
    return None


async def channel_posts_native(
    handle: str, cursor: str | None, limit: int
) -> tuple[list[dict[str, Any]], str | None] | None:
    """Fetch up to ``limit`` latest posts for ``handle``, starting at ``cursor``.

    ``cursor`` is TikTok's ``max_cursor`` (numeric timestamp string); omit / ``0``
    for the first page. Returns ``(posts, next_cursor)`` where ``next_cursor`` is
    ``None`` when the feed is exhausted. Returns ``None`` if the profile or the
    first page cannot be loaded.
    """
    ui = await _user_info(handle)
    if ui is None:
        return None
    user = ui.get("user") or {}
    sec = safe_str(user.get("secUid"))
    if not sec:
        return None
    stats_v2 = ui.get("statsV2") or {}
    stats = ui.get("stats") or {}
    video_count = _stat(stats_v2, stats, "videoCount") or 0
    expect_items = video_count > 0

    collected: list[dict[str, Any]] = []
    cur = str(cursor) if cursor else "0"
    max_pages = max(3, limit // 10 + 3)
    for page_i in range(max_pages):
        if len(collected) >= limit:
            break
        want = min(30, limit - len(collected))
        page = await _post_page(sec, cur, want, expect_items=expect_items)
        if page is None:
            page = await _post_page_via_signer(
                sec, cur, want, expect_items=expect_items
            )
        if page is None and page_i == 0 and cur in ("", "0"):
            page = await _post_page_via_decodo(handle, expect_items=expect_items)
        if page is None:
            return None if not collected else (collected, cur)
        for raw in page.get("aweme_list") or []:
            if not isinstance(raw, dict):
                continue
            mapped = _map_aweme_post(raw)
            if mapped:
                collected.append(mapped)
                if len(collected) >= limit:
                    break
        nxt = page.get("max_cursor")
        has_more = bool(page.get("has_more"))
        if not has_more:
            return collected[:limit], None
        cur = str(nxt) if nxt is not None else cur
        if len(collected) >= limit:
            return collected[:limit], cur
    return collected[:limit], (cur if collected else None)


# --- Audience geography (commenter region sampling) ------------------------
#
# TikTok never exposes a creator's follower geography publicly, but the mobile
# comment API returns each commenter's ``region`` (ISO-3166 alpha-2 country
# code). Sampling commenters across a creator's recent videos and tallying
# those regions yields an engagement-based audience-country breakdown — the
# same signal third-party "audience" endpoints surface. Video IDs come from the
# caller (or from ``channel_posts_native``).
async def audience_commenters_native(
    aweme_ids: list[str], target_total: int = 500, per_video: int = 150
) -> dict[str, list[str]] | None:
    """Collect commenter country codes + comment languages across videos.

    Fetches comment pages natively and pulls ``user.region`` and
    ``comment_language`` from each comment, stopping once ``target_total``
    region codes are gathered or the videos are exhausted. Returns
    ``{"regions": [...], "languages": [...]}`` (duplicates preserved for
    tallying) or ``None`` if every video's comments were blocked.
    """
    regions: list[str] = []
    languages: list[str] = []
    any_success = False
    for aweme_id in aweme_ids:
        if len(regions) >= target_total:
            break
        collected = 0
        cur = "0"
        for _ in range(per_video // 15 + 2):
            if collected >= per_video or len(regions) >= target_total:
                break
            want = min(30, per_video - collected)
            page = await _comment_page(aweme_id, cur, want)
            if page is None:
                break  # this video is blocked right now; try the next one
            any_success = True
            comments = page.get("comments") or []
            for c in comments:
                if not isinstance(c, dict):
                    continue
                user = c.get("user") or {}
                if not isinstance(user, dict):
                    user = {}
                code = safe_str(user.get("region"))
                if code:
                    regions.append(code.strip().upper())
                lang = normalize_language_code(
                    safe_str(
                        c.get("comment_language")
                        or c.get("commentLanguage")
                        or user.get("language")
                    )
                )
                if lang:
                    languages.append(lang)
            collected += len(comments)
            nxt = page.get("cursor")
            cur = str(nxt) if nxt is not None else cur
            if not page.get("has_more"):
                break
    if not any_success:
        return None
    return {"regions": regions, "languages": languages}


async def audience_regions_native(
    aweme_ids: list[str], target_total: int = 500, per_video: int = 150
) -> list[str] | None:
    """Back-compat wrapper — country codes only. Prefer ``audience_commenters_native``."""
    got = await audience_commenters_native(
        aweme_ids, target_total=target_total, per_video=per_video
    )
    if got is None:
        return None
    return got["regions"]


# --- Search suggestions (public web autocomplete) ---------------------------
#
# TikTok's logged-out search preview endpoint returns ``sug_list`` for a seed
# keyword. Same shape the Apify keywords-discovery actor scrapes; we hit it
# directly so a flaky actor doesn't 502 the whole route.
_TT_SUGGEST_URL = "https://www.tiktok.com/api/search/general/preview/"


async def search_suggestions_native(
    q: str,
    *,
    country: str = "US",
    language: str = "en-US",
    limit: int = 20,
) -> list[dict[str, Any]] | None:
    """Return raw suggestion rows (``suggestion``, ``rank``, …) or ``None``."""
    seed = (q or "").strip()
    if not seed:
        return None
    region = (country or "US").upper()
    lang = language or "en-US"
    params = {
        "aid": "1988",
        "app_name": "tiktok_web",
        "device_platform": "web_pc",
        "keyword": seed,
        "region": region,
        "priority_region": region,
    }
    headers = {
        **TT_HEADERS,
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.tiktok.com/search?q={seed}",
        "Accept-Language": lang,
    }
    body: dict[str, Any] | None = None
    for tier in ("datacenter", "residential"):
        try:
            resp = await proxy_fetch(
                _TT_SUGGEST_URL, tier=tier, headers=headers, params=params, timeout=20
            )
        except httpx.HTTPError:
            continue
        if resp.status_code >= 400:
            continue
        try:
            parsed = resp.json()
        except ValueError:
            continue
        if isinstance(parsed, dict) and isinstance(parsed.get("sug_list"), list):
            body = parsed
            break
    if body is None:
        return None

    out: list[dict[str, Any]] = []
    for idx, row in enumerate(body.get("sug_list") or [], start=1):
        if not isinstance(row, dict):
            continue
        word = safe_str(
            row.get("content")
            or (row.get("word_record") or {}).get("words_content")
            or row.get("word")
        )
        if not word:
            continue
        rank = safe_int((row.get("word_record") or {}).get("words_position"))
        out.append(
            {
                "seedKeyword": seed,
                "suggestion": word,
                "suggestionRank": (rank + 1) if rank is not None else idx,
                "region": region,
                "language": lang,
            }
        )
        if len(out) >= limit:
            break
    return out if out else None

# --- Music posts (mobile music/aweme API, cursor-paginated) -----------------
#
# Sound pages hydrate poorly without JS; the mobile ``/aweme/v1/music/aweme/``
# endpoint returns logged-out aweme rows for a ``music_id`` with the same
# residential soft-block pattern as channel posts / comments.
_TT_MUSIC_HOSTS = (
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/music/aweme/",
    "https://api22-normal-c-useast2a.tiktokv.com/aweme/v1/music/aweme/",
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/music/aweme/",
    "https://api31-normal-useast2a.tiktokv.com/aweme/v1/music/aweme/",
    "https://api.tiktokv.com/aweme/v1/music/aweme/",
)

_MUSIC_ID_RE = re.compile(r"(\d{6,})")


def parse_music_id(url_or_id: str) -> str | None:
    """Extract a TikTok music/sound id from a URL or bare numeric id."""
    raw = (url_or_id or "").strip()
    if not raw:
        return None
    if raw.isdigit() and len(raw) >= 6:
        return raw
    m = _MUSIC_ID_RE.search(raw)
    return m.group(1) if m else None


def _music_page_ok(page: dict[str, Any], *, expect_items: bool) -> bool:
    awemes = page.get("aweme_list")
    if not isinstance(awemes, list):
        return False
    if awemes:
        return True
    return not expect_items


async def _music_page(
    music_id: str, cursor: str, count: int, *, expect_items: bool
) -> dict[str, Any] | None:
    headers = {"User-Agent": _TT_MOBILE_UA, "Accept": "application/json"}
    rounds = 3 if cursor not in ("", "0") else 2
    concurrency = 12
    geos = ("US", "NL")

    async def _attempt(host: str, country: str) -> dict[str, Any] | None:
        did = str(random.randint(10**18, 10**19 - 1))
        params = {
            **_TT_COMMENT_PARAMS,
            "device_id": did,
            "iid": did,
            "music_id": music_id,
            "count": str(max(1, min(count, 30))),
            "cursor": str(cursor or "0"),
        }
        return await _comment_once(host, params, headers, _residential_proxy(country))

    for _ in range(rounds):
        tasks = [
            asyncio.create_task(
                _attempt(_TT_MUSIC_HOSTS[i % len(_TT_MUSIC_HOSTS)], geos[i % len(geos)])
            )
            for i in range(concurrency)
        ]
        try:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if res is not None and _music_page_ok(res, expect_items=expect_items):
                    return res
        finally:
            for t in tasks:
                t.cancel()
        await asyncio.sleep(0.15)
    return None


async def music_posts_native(music_id_or_url: str, limit: int) -> list[dict[str, Any]] | None:
    """Fetch up to ``limit`` videos that use a TikTok sound.

    Returns mapped post dicts (same shape as ``channel_posts_native``), or
    ``None`` when the first page cannot be loaded (caller falls back to Apify).
    """
    if limit <= 0:
        return []
    music_id = parse_music_id(music_id_or_url)
    if not music_id:
        return None

    collected: list[dict[str, Any]] = []
    cur = "0"
    max_pages = max(3, limit // 8 + 2)
    for page_i in range(max_pages):
        if len(collected) >= limit:
            break
        want = min(30, limit - len(collected))
        page = await _music_page(music_id, cur, want, expect_items=True)
        if page is None:
            return None if not collected else collected[:limit]
        for raw in page.get("aweme_list") or []:
            if not isinstance(raw, dict):
                continue
            mapped = _map_aweme_post(raw)
            if mapped:
                collected.append(mapped)
                if len(collected) >= limit:
                    break
        if not bool(page.get("has_more")):
            break
        nxt = page.get("cursor")
        if nxt is None:
            break
        cur = str(nxt)
        if page_i == 0 and not collected:
            return None
    return collected[:limit] if collected else None


async def _sec_uid_for_handle(handle: str) -> str | None:
    """Resolve ``secUid`` from the public profile rehydration blob."""
    scope = await _fetch_scope(f"https://www.tiktok.com/@{handle.lstrip('@')}")
    user = (((scope or {}).get("webapp.user-detail") or {}).get("userInfo") or {}).get(
        "user"
    ) or {}
    return safe_str(user.get("secUid") or user.get("sec_uid"))


def _map_connection_user(row: dict[str, Any]) -> dict[str, Any] | None:
    """Map ``/api/user/list/`` userList row → followers/followings shape."""
    user = row.get("user") if isinstance(row.get("user"), dict) else row
    if not isinstance(user, dict):
        return None
    stats = row.get("stats") if isinstance(row.get("stats"), dict) else {}
    username = safe_str(user.get("uniqueId") or user.get("unique_id"))
    if not username:
        return None
    avatar = (
        _url_list_first(user.get("avatarLarger") or user.get("avatar_larger"))
        or _url_list_first(user.get("avatarMedium") or user.get("avatar_medium"))
        or _url_list_first(user.get("avatarThumb") or user.get("avatar_thumb"))
        or safe_str(user.get("avatarLarger") or user.get("avatarMedium"))
    )
    return {
        "username": username,
        "displayName": safe_str(user.get("nickname") or user.get("nickName")),
        "bio": safe_str(user.get("signature")),
        "url": f"https://www.tiktok.com/@{username}",
        "followers": safe_int(
            stats.get("followerCount")
            or stats.get("follower_count")
            or user.get("followerCount")
        ),
        "following": safe_int(
            stats.get("followingCount")
            or stats.get("following_count")
            or user.get("followingCount")
        ),
        "verified": bool(user.get("verified")) if user.get("verified") is not None else None,
        "profileImage": avatar,
    }


async def user_connections_native(
    handle: str, *, mode: str, limit: int
) -> list[dict[str, Any]] | None:
    """Followers (scene=67) or followings (scene=21) via the signer sidecar.

    Returns mapped user rows, or ``None`` when the signer is unset / blocked.
    """
    from app.services import tiktok_signer

    if limit <= 0 or not tiktok_signer.enabled():
        return None
    scene = "67" if mode == "followers" else "21"
    sec = await _sec_uid_for_handle(handle)
    if not sec:
        return None

    collected: list[dict[str, Any]] = []
    min_cursor = "0"
    for _ in range(max(3, limit // 15 + 2)):
        if len(collected) >= limit:
            break
        count = min(30, limit - len(collected))
        api = (
            "https://www.tiktok.com/api/user/list/"
            f"?aid=1988&app_name=tiktok_web&device_platform=web_pc"
            f"&secUid={sec}&count={count}&minCursor={min_cursor}&maxCursor=0"
            f"&scene={scene}&user_is_login=false"
        )
        page = await tiktok_signer.fetch_api(api)
        if page is None:
            return None if not collected else collected[:limit]
        rows = page.get("userList") or []
        if not isinstance(rows, list) or not rows:
            break
        for row in rows:
            if not isinstance(row, dict):
                continue
            mapped = _map_connection_user(row)
            if mapped:
                collected.append(mapped)
            if len(collected) >= limit:
                break
        if not bool(page.get("hasMore")):
            break
        nxt = page.get("minCursor")
        if nxt is None:
            break
        min_cursor = str(nxt)
    return collected[:limit] if collected else None


def _map_search_sample_item(
    item: dict[str, Any], username: str | None
) -> dict[str, Any] | None:
    """Slim sample video from a search-user row's ``items[]`` (not full video-details)."""
    aweme_id = safe_str(item.get("aweme_id") or item.get("id"))
    if not aweme_id:
        return None
    stats = item.get("statistics") or item.get("stats") or {}
    if not isinstance(stats, dict):
        stats = {}
    video = item.get("video") or {}
    if not isinstance(video, dict):
        video = {}
    cover = (
        _url_list_first(video.get("cover"))
        or _url_list_first(video.get("origin_cover") or video.get("originCover"))
        or _url_list_first(video.get("dynamic_cover") or video.get("dynamicCover"))
        or safe_str(item.get("cover") or item.get("thumbnail"))
    )
    out: dict[str, Any] = {
        "id": aweme_id,
        "url": (
            f"https://www.tiktok.com/@{username}/video/{aweme_id}" if username else None
        ),
        "caption": safe_str(item.get("desc") or item.get("description")),
        "views": safe_int(stats.get("play_count") or stats.get("playCount")),
        "likes": safe_int(stats.get("digg_count") or stats.get("diggCount")),
        "thumbnailUrl": cover,
        "publishedAt": _iso(item.get("create_time") or item.get("createTime")),
    }
    return {k: v for k, v in out.items() if v not in (None, "", [])} or None


def _map_search_user(row: dict[str, Any]) -> dict[str, Any] | None:
    """Map ``/api/search/user/full/`` user_list row → search-users shape."""
    info = row.get("user_info") or row.get("user") or row
    if not isinstance(info, dict):
        return None
    username = safe_str(info.get("unique_id") or info.get("uniqueId"))
    if not username:
        return None
    avatar = (
        _url_list_first(info.get("avatar_medium") or info.get("avatarMedium"))
        or _url_list_first(info.get("avatar_larger") or info.get("avatarLarger"))
        or _url_list_first(info.get("avatar_thumb") or info.get("avatarThumb"))
        or safe_str(info.get("avatar_medium") or info.get("avatar_thumb"))
    )
    verified = info.get("custom_verify") or info.get("verification_type") or info.get("verified")
    uid = safe_str(
        info.get("uid") or info.get("user_id") or info.get("userId") or info.get("id")
    )
    sec_uid = safe_str(info.get("sec_uid") or info.get("secUid"))
    sample_items: list[dict[str, Any]] = []
    raw_items = row.get("items") or row.get("item_list") or row.get("itemList") or []
    if isinstance(raw_items, list):
        for entry in raw_items:
            if not isinstance(entry, dict):
                continue
            mapped = _map_search_sample_item(entry, username)
            if mapped:
                sample_items.append(mapped)

    out: dict[str, Any] = {
        "id": uid,
        "secUid": sec_uid,
        "username": username,
        "displayName": safe_str(info.get("nickname") or info.get("nickName")),
        "bio": safe_str(info.get("signature")),
        "url": f"https://www.tiktok.com/@{username}",
        "followers": safe_int(
            info.get("follower_count") or info.get("followerCount")
        ),
        "following": safe_int(
            info.get("following_count") or info.get("followingCount")
        ),
        "videos": safe_int(
            info.get("aweme_count")
            or info.get("video_count")
            or info.get("videoCount")
        ),
        "likes": safe_int(
            info.get("total_favorited")
            or info.get("heart_count")
            or info.get("heartCount")
        ),
        "verified": bool(verified) if verified not in (None, "", 0, "0") else False,
        "profileImage": avatar,
        "items": sample_items,
    }
    for key in ("id", "secUid", "following", "videos", "likes", "items"):
        if out.get(key) in (None, "", []):
            out.pop(key, None)
    return out


def _collect_search_users(rows: list[Any], *, limit: int) -> list[dict[str, Any]]:
    users: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        mapped = _map_search_user(row)
        if mapped:
            users.append(mapped)
        if len(users) >= limit:
            break
    return users


async def _search_users_via_general(
    seed: str, *, limit: int, cursor: int
) -> tuple[list[dict[str, Any]], bool, int | None] | None:
    """Fallback: pull type=4 user cards from ``/api/search/general/full/``.

    Railway IPs sometimes soft-block ``/search/user/full/`` (tiny empty JSON)
    while general search still returns large payloads with user cards.
    """
    from app.services import tiktok_signer

    api = (
        "https://www.tiktok.com/api/search/general/full/"
        f"?aid=1988&app_name=tiktok_web&device_platform=web_pc"
        f"&keyword={urllib.parse.quote(seed)}&offset={max(0, cursor)}"
        f"&count={max(12, min(limit * 2, 30))}&user_is_login=false"
    )
    page = await tiktok_signer.fetch_api(api)
    if page is None:
        return None
    users: list[dict[str, Any]] = []
    for row in page.get("data") or []:
        if not isinstance(row, dict) or row.get("type") != 4:
            continue
        card_users = row.get("user_list") or row.get("userList") or []
        if not isinstance(card_users, list):
            continue
        for mapped in _collect_search_users(card_users, limit=limit - len(users)):
            users.append(mapped)
        if len(users) >= limit:
            break
    if not users:
        return None
    has_more = bool(page.get("has_more") or page.get("hasMore"))
    next_cursor = safe_int(page.get("cursor"))
    return users, has_more, next_cursor


async def search_users_native(
    q: str, *, limit: int = 20, cursor: int = 0
) -> tuple[list[dict[str, Any]], bool, int | None] | None:
    """User search via signer ``/api/search/user/full/`` (+ general fallback)."""
    from app.services import tiktok_signer

    seed = (q or "").strip()
    if not seed or limit <= 0 or not tiktok_signer.enabled():
        return None
    api = (
        "https://www.tiktok.com/api/search/user/full/"
        f"?aid=1988&app_name=tiktok_web&device_platform=web_pc"
        f"&keyword={urllib.parse.quote(seed)}&cursor={max(0, cursor)}"
        f"&count={max(1, min(limit, 30))}&user_is_login=false"
    )
    page = None
    for _ in range(2):
        page = await tiktok_signer.fetch_api(api)
        if page is not None:
            rows = page.get("user_list") or page.get("userList") or []
            if isinstance(rows, list) and rows:
                break
        page = None
    if page is not None:
        rows = page.get("user_list") or page.get("userList") or []
        users = _collect_search_users(rows if isinstance(rows, list) else [], limit=limit)
        if users:
            has_more = bool(page.get("has_more") or page.get("hasMore"))
            next_cursor = safe_int(page.get("cursor"))
            return users, has_more, next_cursor
    return await _search_users_via_general(seed, limit=limit, cursor=cursor)


async def top_search_native(
    q: str, *, limit: int = 20, cursor: int = 0
) -> tuple[list[dict[str, Any]], bool, int | None] | None:
    """Mixed top search via signer ``/api/search/general/full/``.

    Returns videos **and** photo carousels when TikTok includes them in the
    general/top tab (not keyword-video-only search). TikTok may repeat the
    same id across pages — callers should dedupe if needed.
    """
    from app.services import tiktok_signer

    seed = (q or "").strip()
    if not seed or limit <= 0 or not tiktok_signer.enabled():
        return None
    collected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    offset = max(0, int(cursor or 0))
    has_more = False
    next_cursor: int | None = None
    for _ in range(max(2, limit // 10 + 1)):
        if len(collected) >= limit:
            break
        count = min(20, limit - len(collected))
        api = (
            "https://www.tiktok.com/api/search/general/full/"
            f"?aid=1988&app_name=tiktok_web&device_platform=web_pc"
            f"&keyword={urllib.parse.quote(seed)}&offset={offset}"
            f"&count={count}&user_is_login=false"
        )
        page = await tiktok_signer.fetch_api(api)
        if page is None:
            return None if not collected else (collected[:limit], has_more, next_cursor)
        rows = page.get("data") or []
        if not isinstance(rows, list) or not rows:
            has_more = False
            next_cursor = None
            break
        for row in rows:
            if not isinstance(row, dict):
                continue
            # General search nests the aweme under ``item``; some exits put
            # the aweme fields on the row itself.
            item = row.get("item") if isinstance(row.get("item"), dict) else None
            if item is None and (row.get("aweme_id") or row.get("id")):
                item = row
            if not item:
                continue
            mapped = _map_aweme_post(item)
            if not mapped:
                continue
            mid = safe_str(mapped.get("id"))
            if mid and mid in seen_ids:
                continue
            if mid:
                seen_ids.add(mid)
            collected.append(mapped)
            if len(collected) >= limit:
                break
        page_more = bool(page.get("has_more") or page.get("hasMore"))
        nxt = safe_int(page.get("cursor"))
        has_more = page_more and nxt is not None
        next_cursor = nxt if has_more else None
        if not has_more:
            break
        if nxt is None or nxt == offset:
            break
        offset = nxt
    if not collected:
        return None
    # If we filled ``limit`` but TikTok still has more, keep the cursor.
    if len(collected) >= limit and next_cursor is None and has_more is False:
        # Soft-signal more when we stopped because of our limit mid-page.
        pass
    return collected[:limit], has_more, next_cursor


async def hashtag_posts_native(
    hashtag: str, *, limit: int = 20
) -> tuple[list[dict[str, Any]], bool, int | None] | None:
    """First page of a TikTok hashtag feed via Decodo ``fetch_resource``.

    Opens ``/tag/{hashtag}`` in a headless browser and captures the signed
    ``/api/challenge/item_list/`` XHR TikTok itself fires. Returns
    ``(mapped_posts, has_more, next_cursor)`` or ``None`` so the caller can
    fall back to Apify. Deeper pages need a fresh signed request (Apify).
    """
    from app.services import decodo_fetch

    tag = (hashtag or "").lstrip("#").strip()
    if not tag or not decodo_fetch.enabled():
        return None
    url = f"https://www.tiktok.com/tag/{tag}"
    fetched = None
    for attempt in range(2):
        fetched = await decodo_fetch.fetch_url(
            url,
            timeout=150.0,
            target="universal",
            headless="html",
            browser_actions=[
                {
                    "type": "fetch_resource",
                    "filter": "api/challenge/item_list",
                    "on_error": "error",
                }
            ],
        )
        if fetched is not None:
            break
    if fetched is None:
        return None
    _status, content = fetched
    try:
        payload = json.loads(content)
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    raw_items = payload.get("itemList")
    if not isinstance(raw_items, list) or not raw_items:
        return None

    posts: list[dict[str, Any]] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        mapped = _map_aweme_post(raw)
        if mapped:
            posts.append(mapped)
        if len(posts) >= limit:
            break
    if not posts:
        return None

    has_more = bool(payload.get("hasMore"))
    next_cursor = safe_int(payload.get("cursor"))
    # Soft-cap: if we truncated to ``limit`` but TikTok still has more on this
    # page, surface hasMore so clients can page (via Apify for cursor > 0).
    if len(raw_items) > limit:
        has_more = True
        next_cursor = limit if next_cursor is None else next_cursor
    return posts, has_more, next_cursor


def _parse_music_extra(raw: Any) -> dict[str, Any] | None:
    """TikTok packs analysis metadata into a JSON string under ``extra``."""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except ValueError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _map_music_artist(row: dict[str, Any]) -> dict[str, Any] | None:
    uid = safe_str(row.get("uid") or row.get("id") or row.get("user_id"))
    handle = safe_str(row.get("handle") or row.get("unique_id") or row.get("uniqueId"))
    if not uid and not handle:
        return None
    avatar = _url_list_first(row.get("avatar")) or _url_list_first(row.get("avatar_thumb"))
    return {
        "id": uid,
        "uid": uid,
        "secUid": safe_str(row.get("sec_uid") or row.get("secUid")),
        "handle": handle.lstrip("@") if handle else None,
        "displayName": safe_str(row.get("nick_name") or row.get("nickname") or row.get("nickName")),
        "verified": bool(row.get("is_verified") or row.get("verified"))
        if row.get("is_verified") is not None or row.get("verified") is not None
        else None,
        "avatarUrl": avatar,
    }


def _usage_count_from_music(music: dict[str, Any]) -> int | None:
    """Videos using this sound. TikTok often sends ``0`` on music/aweme embeds —
    treat non-positive as unknown (null) rather than a fake zero."""
    if not isinstance(music, dict):
        return None
    for key in (
        "user_count",
        "userCount",
        "music_group_use_count",
        "music_ugid_use_count",
        "video_count",
        "videoCount",
        "use_count",
        "useCount",
    ):
        n = safe_int(music.get(key))
        if n is not None and n > 0:
            return n
    stats = music.get("stats") if isinstance(music.get("stats"), dict) else {}
    for key in ("videoCount", "video_count", "userCount", "user_count"):
        n = safe_int(stats.get(key))
        if n is not None and n > 0:
            return n
    return None


def _usage_count_from_scope(scope: dict[str, Any]) -> int | None:
    """Pull usage totals from a music page ``__DEFAULT_SCOPE__`` when present."""
    if not isinstance(scope, dict):
        return None
    # Common web shapes: webapp.music-detail → musicInfo.{music,stats}
    md = scope.get("webapp.music-detail") or scope.get("webapp.music-detail-page") or {}
    if not isinstance(md, dict):
        md = {}
    info = md.get("musicInfo") or md.get("music_info") or md
    if not isinstance(info, dict):
        info = {}
    for blob in (
        info.get("music"),
        info.get("stats"),
        info.get("statsV2"),
        info,
        md,
    ):
        n = _usage_count_from_music(blob) if isinstance(blob, dict) else None
        if n is not None:
            return n
    # Last resort: walk one level for nested music blobs with a use count.
    for value in scope.values():
        if not isinstance(value, dict):
            continue
        nested = value.get("musicInfo") or value.get("music") or value
        if isinstance(nested, dict):
            n = _usage_count_from_music(nested)
            if n is not None:
                return n
            stats = nested.get("stats") if isinstance(nested.get("stats"), dict) else None
            if stats:
                n = _usage_count_from_music(stats)
                if n is not None:
                    return n
    return None


_TT_MUSIC_DETAIL_HOSTS = (
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/music/detail/",
    "https://api22-normal-c-useast2a.tiktokv.com/aweme/v1/music/detail/",
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/music/detail/",
    "https://api.tiktokv.com/aweme/v1/music/detail/",
)


async def _music_detail_native(music_id: str) -> dict[str, Any] | None:
    """Fetch a fuller music object (often includes ``user_count``) via music/detail."""
    headers = {"User-Agent": _TT_MOBILE_UA, "Accept": "application/json"}
    geos = ("US", "NL")

    async def _attempt(host: str, country: str) -> dict[str, Any] | None:
        did = str(random.randint(10**18, 10**19 - 1))
        params = {
            **_TT_COMMENT_PARAMS,
            "device_id": did,
            "iid": did,
            "music_id": music_id,
        }
        return await _comment_once(host, params, headers, _residential_proxy(country))

    tasks = [
        asyncio.create_task(
            _attempt(_TT_MUSIC_DETAIL_HOSTS[i % len(_TT_MUSIC_DETAIL_HOSTS)], geos[i % len(geos)])
        )
        for i in range(8)
    ]
    try:
        for coro in asyncio.as_completed(tasks):
            res = await coro
            if not isinstance(res, dict):
                continue
            music = res.get("music_info") or res.get("music") or res.get("musicInfo")
            if isinstance(music, dict) and (
                music.get("id") or music.get("id_str") or music.get("title")
            ):
                return music
    finally:
        for t in tasks:
            t.cancel()
    return None


def normalize_song_details(
    music: dict[str, Any],
    *,
    url: str,
    music_id: str | None = None,
) -> dict[str, Any] | None:
    """Map a TikTok ``music`` object → ``/v1/tiktok/song-details`` shape."""
    if not isinstance(music, dict):
        return None
    mid = (
        safe_str(music.get("id_str") or music.get("id") or music.get("mid"))
        or music_id
    )
    title = safe_str(music.get("title"))
    if not mid and not title:
        return None

    is_original_sound = music.get("is_original_sound")
    is_original = music.get("is_original")
    original = is_original_sound if is_original_sound is not None else is_original
    if original is None and title:
        original = title.lower().startswith("original sound")

    cover_large = _url_list_first(music.get("cover_large"))
    cover_medium = _url_list_first(music.get("cover_medium"))
    cover_thumb = _url_list_first(music.get("cover_thumb"))
    cover = cover_large or cover_medium or cover_thumb
    play = _url_list_first(music.get("play_url"))

    artists: list[dict[str, Any]] = []
    seen_artist: set[str] = set()
    for raw in music.get("artists") or []:
        if not isinstance(raw, dict):
            continue
        mapped = _map_music_artist(raw)
        if not mapped:
            continue
        key = mapped.get("id") or mapped.get("handle") or ""
        if key and key in seen_artist:
            continue
        if key:
            seen_artist.add(key)
        artists.append(mapped)
    # Original sounds often omit artists[] — lift owner identity when present.
    if not artists:
        owner = _map_music_artist(
            {
                "uid": music.get("owner_id"),
                "sec_uid": music.get("sec_uid"),
                "handle": music.get("owner_handle"),
                "nick_name": music.get("owner_nickname") or music.get("author"),
                "avatar": music.get("avatar_medium") or music.get("avatar_thumb"),
                "is_verified": None,
            }
        )
        if owner and (owner.get("id") or owner.get("handle")):
            artists.append(owner)

    matched_raw = music.get("matched_song") if isinstance(music.get("matched_song"), dict) else None
    matched_song = None
    if matched_raw:
        chorus_raw = matched_raw.get("chorus_info") if isinstance(matched_raw.get("chorus_info"), dict) else None
        chorus_info = None
        if chorus_raw:
            start_ms = chorus_raw.get("start_ms")
            if start_ms is None:
                start_ms = chorus_raw.get("startMs")
            duration_ms = chorus_raw.get("duration_ms")
            if duration_ms is None:
                duration_ms = chorus_raw.get("durationMs")
            chorus_info = {
                "startMs": safe_int(start_ms),
                "durationMs": safe_int(duration_ms),
            }
        matched_song = {
            "id": safe_str(matched_raw.get("id") or matched_raw.get("id_str")),
            "title": safe_str(matched_raw.get("title")),
            "author": safe_str(matched_raw.get("author")),
            "fullDuration": safe_float(matched_raw.get("full_duration") or matched_raw.get("fullDuration")),
            "chorusInfo": chorus_info,
        }

    release_raw = (
        music.get("music_release_info")
        if isinstance(music.get("music_release_info"), dict)
        else None
    )
    music_release = None
    if release_raw:
        group_ts = safe_int(release_raw.get("group_release_date"))
        music_release = {
            "groupReleaseDate": _iso(group_ts) if group_ts else None,
            "groupReleaseTimestamp": group_ts,
            "isNewReleaseSong": bool(release_raw.get("is_new_release_song"))
            if release_raw.get("is_new_release_song") is not None
            else None,
        }

    extra_raw = _parse_music_extra(music.get("extra"))
    extra = None
    if extra_raw:
        beats = extra_raw.get("beats") if isinstance(extra_raw.get("beats"), dict) else None
        bpm = safe_float(extra_raw.get("bpm"))
        loudness = safe_float(extra_raw.get("loudness_lufs") or extra_raw.get("loudnessLufs"))
        peak = safe_float(extra_raw.get("amplitude_peak") or extra_raw.get("amplitudePeak"))
        # Only surface the analysis block when TikTok actually populated it.
        if bpm is not None or (loudness is not None and loudness != 0) or (
            peak is not None and peak != 0
        ) or (beats and any(beats.values())):
            extra = {
                "bpm": bpm,
                "loudnessLufs": loudness,
                "amplitudePeak": peak,
                "beats": beats or None,
            }

    create_ts = safe_int(music.get("create_time") or music.get("createTime"))
    album = safe_str(music.get("album"))
    dur = duration_seconds(music.get("duration") or music.get("durationSeconds"))
    # Top-level artist identity (original-sound owner or first credited artist).
    primary = artists[0] if artists else {}
    out: dict[str, Any] = {
        "platform": "tiktok",
        "url": url,
        "id": mid,
        "mid": safe_str(music.get("mid")) or mid,
        "title": title,
        "author": safe_str(music.get("author") or music.get("owner_nickname")),
        "artistId": safe_str(primary.get("id") or music.get("owner_id")),
        "authorSecUid": safe_str(
            primary.get("secUid") or music.get("sec_uid") or music.get("owner_sec_uid")
        ),
        "artists": artists,
        "original": bool(original) if original is not None else None,
        "isOriginal": bool(is_original) if is_original is not None else None,
        "isOriginalSound": bool(is_original_sound)
        if is_original_sound is not None
        else (bool(original) if original is not None else None),
        "isPgc": bool(music.get("is_pgc")) if music.get("is_pgc") is not None else None,
        "isAuthorArtist": bool(music.get("is_author_artist"))
        if music.get("is_author_artist") is not None
        else None,
        "isExplicit": bool(music.get("is_explicit") or music.get("isExplicit"))
        if music.get("is_explicit") is not None or music.get("isExplicit") is not None
        else None,
        "hasLyrics": bool(music.get("has_lyrics") or music.get("hasLyrics"))
        if music.get("has_lyrics") is not None or music.get("hasLyrics") is not None
        else None,
        "album": album or None,
        # durationSeconds is the canonical float (matches music-posts). Keep
        # duration as a back-compat alias of the same value.
        "durationSeconds": dur,
        "duration": dur,
        "coverUrl": cover,
        "cover": {
            "large": cover_large,
            "medium": cover_medium,
            "thumb": cover_thumb,
        },
        "playUrl": play,
        # Docs promise usage count — map user_count when TikTok exposes a real value.
        "usageCount": _usage_count_from_music(music),
        "createdAt": _iso(create_ts) if create_ts else None,
        "createTime": create_ts,
        "isCommerceMusic": bool(music.get("is_commerce_music"))
        if music.get("is_commerce_music") is not None
        else None,
        "hasCommerceRight": bool(music.get("has_commerce_right"))
        if music.get("has_commerce_right") is not None
        else None,
        "commercialRightType": safe_int(music.get("commercial_right_type")),
        "matchedSong": matched_song,
        "musicReleaseInfo": music_release,
        "extra": extra,
        "strongBeatUrl": _url_list_first(music.get("strong_beat_url"))
        or safe_str(
            (music.get("strong_beat_url") or {}).get("uri")
            if isinstance(music.get("strong_beat_url"), dict)
            else music.get("strong_beat_url")
        ),
        # Similar / rec lists need a separate music-detail web call (signer);
        # leave null rather than invent empty arrays.
        "similarMusic": None,
        "recList": None,
    }
    return out


async def song_details_native(music_id_or_url: str) -> dict[str, Any] | None:
    """Song/sound metadata from music/aweme (+ music/detail / web enrich for usage).

    Returns the /v1/tiktok/song-details shape, or ``None`` so the caller can
    fall back to Apify.
    """
    music_id = parse_music_id(music_id_or_url)
    if not music_id:
        return None

    url = (
        music_id_or_url
        if music_id_or_url.startswith("http")
        else f"https://www.tiktok.com/music/sound-{music_id}"
    )

    # Parallel: music/detail often has user_count; music/aweme has covers/play.
    detail_music, page = await asyncio.gather(
        _music_detail_native(music_id),
        _music_page(music_id, "0", 1, expect_items=True),
    )
    aweme_music: dict[str, Any] | None = None
    if isinstance(page, dict):
        page_music = page.get("music_info") or page.get("music")
        if isinstance(page_music, dict):
            aweme_music = page_music
        else:
            awemes = page.get("aweme_list") or []
            if awemes and isinstance(awemes[0], dict) and isinstance(
                awemes[0].get("music"), dict
            ):
                aweme_music = awemes[0]["music"]

    music = detail_music or aweme_music
    if not isinstance(music, dict):
        return None

    # Merge usage / cover / play from the other source when the primary omits them.
    secondary = aweme_music if music is detail_music else detail_music
    if isinstance(secondary, dict):
        merged = dict(music)
        for key in (
            "user_count",
            "music_group_use_count",
            "cover_large",
            "cover_medium",
            "cover_thumb",
            "play_url",
            "extra",
            "matched_song",
            "music_release_info",
            "artists",
        ):
            if merged.get(key) in (None, 0, "", [], {}) and secondary.get(key) not in (
                None,
                0,
                "",
                [],
                {},
            ):
                merged[key] = secondary[key]
        music = merged

    out = normalize_song_details(music, url=url, music_id=music_id)
    if out is None:
        return None

    if out.get("usageCount") is None:
        # Web music page sometimes exposes the "X videos" total even when
        # music/aweme embeds send user_count=0.
        scope = await _fetch_scope(url)
        usage = _usage_count_from_scope(scope) if scope else None
        if usage is not None:
            out["usageCount"] = usage

    return out


# TikTok ``liveRoom.status`` / ``user.status`` — 2 means currently live.
# Other codes (commonly 4) mean the last room payload is stale / ended; stream
# pull URLs may still be present but must not be treated as an active broadcast.
_TT_LIVE_STATUS_LIVE = 2


def _parse_stream_data_blob(blob: Any) -> dict[str, Any]:
    """Decode ``pull_data.stream_data`` (JSON string or dict) → quality map."""
    if not isinstance(blob, dict):
        return {}
    pull = blob.get("pull_data") if isinstance(blob.get("pull_data"), dict) else {}
    raw = pull.get("stream_data")
    parsed: Any = None
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = None
    elif isinstance(raw, dict):
        parsed = raw
    if not isinstance(parsed, dict):
        return {}
    data = parsed.get("data")
    return data if isinstance(data, dict) else {}


def _parse_sdk_params(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            got = json.loads(raw)
            return got if isinstance(got, dict) else {}
        except ValueError:
            return {}
    return {}


def _extract_stream_qualities(live_room: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse h264 + hevc streamData into quality rows (hd/sd/ld/origin/ao/…)."""
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for blob_key, default_codec in (("streamData", "h264"), ("hevcStreamData", "h265")):
        data = _parse_stream_data_blob(live_room.get(blob_key))
        if not data:
            continue
        for quality_name, quality in data.items():
            if not isinstance(quality, dict):
                continue
            q = safe_str(quality_name)
            if not q:
                continue
            main = quality.get("main") if isinstance(quality.get("main"), dict) else quality
            if not isinstance(main, dict):
                continue
            sdk = _parse_sdk_params(main.get("sdk_params"))
            codec = safe_str(sdk.get("VCodec") or sdk.get("vcodec") or default_codec) or default_codec
            key = (q, codec)
            if key in seen:
                continue
            seen.add(key)
            resolution = safe_str(sdk.get("resolution"))
            bitrate = safe_int(sdk.get("vbitrate") if sdk.get("vbitrate") is not None else sdk.get("bitrate"))
            row: dict[str, Any] = {
                "quality": q,
                "codec": codec,
                "resolution": resolution or None,
                "bitrate": bitrate,
                "flv": safe_str(main.get("flv")),
                "hls": safe_str(main.get("hls")),
                "dash": safe_str(main.get("dash")),
                "cmaf": safe_str(main.get("cmaf")),
            }
            rows.append({k: v for k, v in row.items() if v is not None and v != ""})
    return rows


def _extract_stream_urls(live_room: dict[str, Any]) -> list[str]:
    """Flat flv/hls/dash/cmaf URL list (compat); prefer ``streamQualities``."""
    urls: list[str] = []
    seen: set[str] = set()
    for row in _extract_stream_qualities(live_room):
        for k in ("flv", "hls", "dash", "cmaf"):
            u = safe_str(row.get(k))
            if u and u.startswith("http") and u not in seen:
                seen.add(u)
                urls.append(u)
    return urls


def _streams_by_quality(qualities: list[dict[str, Any]]) -> dict[str, Any] | None:
    """SC-style map keyed by quality (prefer h264 when both codecs exist)."""
    if not qualities:
        return None
    out: dict[str, Any] = {}
    for row in qualities:
        q = safe_str(row.get("quality"))
        if not q:
            continue
        codec = safe_str(row.get("codec")) or "h264"
        # First win, but let h264 replace a prior hevc entry for the same key.
        if q in out and codec not in ("h264", "avc"):
            continue
        entry = {k: v for k, v in row.items() if k != "quality" and v is not None and v != ""}
        out[q] = entry
    return out or None


async def _fetch_live_room_api(handle: str) -> dict[str, Any] | None:
    """Signer ``/api-live/user/room/`` — room meta + stream pull URLs."""
    from app.services import tiktok_signer

    if not handle or not tiktok_signer.enabled():
        return None
    api = (
        "https://www.tiktok.com/api-live/user/room/"
        f"?aid=1988&sourceType=54&uniqueId={urllib.parse.quote(handle)}"
    )
    page = await tiktok_signer.fetch_api(api)
    if not isinstance(page, dict):
        return None
    data = page.get("data")
    return data if isinstance(data, dict) else None


async def live_status_native(handle: str) -> dict[str, Any] | None:
    """Live status via ``api-live/user/room`` (streams) + profile fallback.

    ``isLive`` is authoritative and true only when ``liveRoom.status == 2``
    (or ``user.status == 2`` when the room node is missing). Other statuses
    still return the last room (title / counts / pull URLs) so clients can
    inspect history — but must key off ``isLive`` / ``status``, not a non-empty
    ``room``. Profile ``roomId`` is used only when the live API is unavailable.
    """
    username = (handle or "").lstrip("@").strip()
    if not username:
        return None

    live_api = await _fetch_live_room_api(username)
    ui = await _user_info(username)
    user = (ui or {}).get("user") if isinstance(ui, dict) else {}
    if not isinstance(user, dict):
        user = {}
    stats_v2 = (ui or {}).get("statsV2") if isinstance(ui, dict) else {}
    stats = (ui or {}).get("stats") if isinstance(ui, dict) else {}
    if not isinstance(stats_v2, dict):
        stats_v2 = {}
    if not isinstance(stats, dict):
        stats = {}

    api_user = (live_api or {}).get("user") if isinstance(live_api, dict) else {}
    if not isinstance(api_user, dict):
        api_user = {}
    api_stats = (live_api or {}).get("stats") if isinstance(live_api, dict) else {}
    if not isinstance(api_stats, dict):
        api_stats = {}
    live_room = (live_api or {}).get("liveRoom") if isinstance(live_api, dict) else {}
    if not isinstance(live_room, dict):
        live_room = {}

    username = (
        safe_str(api_user.get("uniqueId") or user.get("uniqueId")) or username
    )
    if not username and live_api is None and ui is None:
        return None

    profile_room_id = safe_str(user.get("roomId") or api_user.get("roomId"))
    room_status = safe_int(live_room.get("status"))
    user_status = safe_int(api_user.get("status") if api_user.get("status") is not None else user.get("status"))
    # Authoritative: numeric liveRoom.status (2 = live). Never treat a leftover
    # roomId / non-empty streamUrls as "currently live".
    if room_status is not None:
        is_live = room_status == _TT_LIVE_STATUS_LIVE
        status = room_status
    elif user_status is not None:
        is_live = user_status == _TT_LIVE_STATUS_LIVE
        status = user_status
    else:
        # Live API missing entirely — weak profile signal only.
        is_live = bool(profile_room_id) and live_api is None
        status = _TT_LIVE_STATUS_LIVE if is_live else None

    room_stats = live_room.get("liveRoomStats") if isinstance(live_room.get("liveRoomStats"), dict) else {}
    stream_qualities = _extract_stream_qualities(live_room) if live_room else []
    stream_urls = _extract_stream_urls(live_room) if live_room else []
    streams_map = _streams_by_quality(stream_qualities)
    game_tag = safe_int(live_room.get("gameTagId") or live_room.get("game_tag_id"))
    hash_tag = safe_int(live_room.get("hashTagId") or live_room.get("hash_tag_id"))
    live_sub = live_room.get("liveSubOnly")
    if live_sub is None:
        live_sub = live_room.get("live_sub_only")
    live_sub_only = None if live_sub is None else bool(safe_int(live_sub) if not isinstance(live_sub, bool) else live_sub)

    room: dict[str, Any] = {}
    if live_room:
        room = {
            "id": safe_str(
                live_room.get("roomId")
                or api_user.get("roomId")
                or profile_room_id
                or live_room.get("streamId")
            ),
            "streamId": safe_str(live_room.get("streamId")),
            "status": room_status if room_status is not None else status,
            "title": safe_str(live_room.get("title")),
            "startedAt": _iso(live_room.get("startTime")),
            "viewerCount": safe_int(room_stats.get("userCount") or live_room.get("userCount")),
            "totalEnterCount": safe_int(room_stats.get("enterCount") or live_room.get("enterCount")),
            "coverUrl": safe_str(live_room.get("coverUrl") or live_room.get("squareCoverImg")),
            "liveSubOnly": live_sub_only,
            "gameTagId": game_tag if game_tag else None,
            "hashTagId": hash_tag if hash_tag else None,
            "liveRoomMode": safe_int(live_room.get("liveRoomMode")),
            "streamUrls": stream_urls or None,
            "streamQualities": stream_qualities or None,
            "streams": streams_map,
        }
        room = {k: v for k, v in room.items() if v is not None and v != "" and v != []}
    elif profile_room_id and is_live:
        room = {"id": profile_room_id, "status": status}

    creator_id = safe_str(api_user.get("id") or user.get("id") or user.get("uid"))
    sec_uid = safe_str(api_user.get("secUid") or user.get("secUid") or user.get("sec_uid"))
    following = (
        safe_int(api_stats.get("followingCount"))
        or _stat(stats_v2, stats, "followingCount")
    )
    creator = {
        "id": creator_id,
        "secUid": sec_uid,
        "displayName": safe_str(api_user.get("nickname") or user.get("nickname")),
        "followers": safe_int(api_stats.get("followerCount"))
        or _stat(stats_v2, stats, "followerCount"),
        "following": following,
        "followingCount": following,
        "verified": (
            bool(api_user.get("verified"))
            if api_user.get("verified") is not None
            else (bool(user.get("verified")) if user.get("verified") is not None else None)
        ),
        "avatar": safe_str(
            api_user.get("avatarLarger")
            or api_user.get("avatarMedium")
            or user.get("avatarLarger")
            or user.get("avatarMedium")
            or user.get("avatarThumb")
        ),
        "bio": safe_str(api_user.get("signature") or user.get("signature")),
        "status": user_status,
    }
    creator = {k: v for k, v in creator.items() if v is not None and v != ""}

    out: dict[str, Any] = {
        "platform": "tiktok",
        "username": username,
        "isLive": is_live,
        "status": status,
        "creator": creator,
        "room": room,
    }
    return {k: v for k, v in out.items() if v is not None and v != {}}


def _map_trend_video(item: dict[str, Any], *, rank: int) -> dict[str, Any] | None:
    """Map ``/api/recommend/item_list/`` row → trending-feed public shape.

    ``rank`` is Captapi-specific (For You position) — keep it first-class.
    """
    author = item.get("author") if isinstance(item.get("author"), dict) else {}
    stats = item.get("stats") if isinstance(item.get("stats"), dict) else {}
    stats_v2 = item.get("statsV2") if isinstance(item.get("statsV2"), dict) else {}
    video = item.get("video") if isinstance(item.get("video"), dict) else {}
    uid = safe_str(author.get("uniqueId") or author.get("unique_id"))
    vid = safe_str(item.get("id") or item.get("videoId") or item.get("aweme_id"))
    if not vid:
        return None

    create_ts = safe_int(item.get("createTime") or item.get("create_time"))
    aweme_type = safe_int(item.get("awemeType") or item.get("aweme_type"))
    image_post = item.get("imagePost") or item.get("image_post") or item.get("image_post_info")
    shoot_tab = (safe_str(item.get("shootTabName") or item.get("shoot_tab_name")) or "").lower()
    is_photo = bool(image_post) or shoot_tab == "photo" or aweme_type in (150, 51, 68)
    media_type = "photo" if is_photo else "video"

    url = safe_str(item.get("webVideoUrl") or item.get("url"))
    if not url and uid:
        kind = "photo" if is_photo else "video"
        url = f"https://www.tiktok.com/@{uid}/{kind}/{vid}"

    cover = video.get("cover") or video.get("originCover") or item.get("cover")
    if isinstance(cover, dict):
        cover = _url_list_first(cover) or safe_str(cover.get("url"))
    else:
        cover = safe_str(cover)
    if not cover and isinstance(image_post, dict):
        cover = _url_list_first(image_post.get("cover") or image_post.get("imageURL"))

    play_url = _url_list_first(video.get("playAddr") or video.get("play_addr"))
    if not play_url and isinstance(video.get("playAddr"), str):
        play_url = safe_str(video.get("playAddr"))
    duration = safe_float(video.get("duration") or video.get("durationInSec"))
    # Some feeds return duration in ms.
    if duration is not None and duration > 1000:
        duration = duration / 1000.0
    duration = duration_seconds(duration)

    author_id = safe_str(author.get("id") or author.get("uid"))
    author_sec = safe_str(author.get("secUid") or author.get("sec_uid"))
    caption = safe_str(item.get("desc") or item.get("title") or item.get("text"))

    out: dict[str, Any] = {
        "platform": "tiktok",
        "url": url,
        "id": vid,
        # Same field name as channel-posts / video-details (not ``title``).
        "caption": caption,
        "publishedAt": _iso(create_ts),
        "createTime": create_ts,
        "mediaType": media_type,
        "durationSeconds": duration,
        "coverUrl": cover,
        "thumbnailUrl": cover,
        "videoUrl": play_url,
        "author": uid,
        "authorId": author_id,
        "secUid": author_sec,
        "authorName": safe_str(author.get("nickname") or author.get("nickName")),
        "views": _stat(stats_v2, stats, "playCount"),
        "likes": _stat(stats_v2, stats, "diggCount"),
        "comments": _stat(stats_v2, stats, "commentCount"),
        "shares": _stat(stats_v2, stats, "shareCount"),
        "saves": _stat(stats_v2, stats, "collectCount"),
        "isAd": bool(item.get("isAd") or item.get("is_ad")),
        # For You position — Captapi-only signal vs SC.
        "rank": rank,
    }
    return {k: v for k, v in out.items() if v is not None}


async def trending_feed_native(
    country: str = "US", *, limit: int = 20
) -> list[dict[str, Any]] | None:
    """For-You / recommend feed via signer ``/api/recommend/item_list/``.

    ``country`` is a region availability hint (content not banned in that
    market) — it does **not** guarantee creators from that country. Returns
    ranked rows in the ``/trending-feed`` shape, or ``None`` so the caller
    can fall back.
    """
    from app.services import tiktok_signer

    if limit <= 0 or not tiktok_signer.enabled():
        return None
    region = (country or "US").strip().upper() or "US"
    collected: list[dict[str, Any]] = []
    seen: set[str] = set()
    cursor = 0
    for _ in range(max(3, (limit // 10) + 2)):
        if len(collected) >= limit:
            break
        count = min(20, max(10, limit - len(collected)))
        api = (
            "https://www.tiktok.com/api/recommend/item_list/"
            f"?aid=1988&app_name=tiktok_web&device_platform=web_pc"
            f"&count={count}&cursor={cursor}&user_is_login=false"
            f"&region={region}&priority_region={region}"
            f"&carrier_region={region}&sys_region={region}"
        )
        page = await tiktok_signer.fetch_api(api)
        if page is None:
            return None if not collected else collected[:limit]
        items = page.get("itemList") or page.get("item_list") or []
        if not isinstance(items, list) or not items:
            break
        added = 0
        for item in items:
            if not isinstance(item, dict):
                continue
            mapped = _map_trend_video(item, rank=len(collected) + 1)
            if not mapped or not mapped.get("id") or mapped["id"] in seen:
                continue
            seen.add(mapped["id"])
            collected.append(mapped)
            added += 1
            if len(collected) >= limit:
                break
        if added == 0:
            break
        if not bool(page.get("hasMore") if page.get("hasMore") is not None else page.get("has_more")):
            break
        nxt = safe_int(page.get("cursor"))
        cursor = nxt if nxt is not None else cursor + len(items)
    return collected[:limit] if collected else None


_FOLLOWER_RANGES: dict[str, tuple[int, int | None]] = {
    "10k-100k": (10_000, 100_000),
    "100k-1m": (100_000, 1_000_000),
    "1m-10m": (1_000_000, 10_000_000),
    ">10m": (10_000_000, None),
}

# Documented on every popular-creators row — not lifetime likes/followers.
ENGAGEMENT_RATE_BASIS = "avgLikesPerVideo/followers"

_BIO_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)
_BIO_LINK_RE = re.compile(
    r"(?:https?://|www\.)[^\s]+"
    r"|(?:PayPal\.me|paypal\.me)/[^\s]+"
    r"|Cash\s*App\s*\$[A-Za-z0-9_]+"
    r"|\$[A-Za-z][A-Za-z0-9_]{2,}",
    re.IGNORECASE,
)


def creator_engagement_rate(
    likes: int | None, videos: int | None, followers: int | None
) -> float | None:
    """Percent ER: (likes / videos) / followers × 100.

    Lifetime likes÷followers is NOT engagement — it rewards account age / post
    volume. Null when any input is missing or non-positive.
    """
    if likes is None or videos is None or followers is None:
        return None
    if likes < 0 or videos <= 0 or followers <= 0:
        return None
    return round((likes / videos) / followers * 100, 4)


def extract_bio_contact(bio: str | None) -> dict[str, list[str]] | None:
    """Pull emails / payment links from a creator bio for outreach."""
    if not bio:
        return None
    emails = list(dict.fromkeys(_BIO_EMAIL_RE.findall(bio)))
    links: list[str] = []
    for m in _BIO_LINK_RE.finditer(bio):
        token = m.group(0).rstrip(".,);]")
        # Skip bare emails matched by the $ / link heuristics.
        if "@" in token and "://" not in token.lower() and not token.lower().startswith("www."):
            continue
        if token not in links:
            links.append(token)
    if not emails and not links:
        return None
    return {"emails": emails, "links": links}


async def popular_creators_native(
    country: str = "US",
    *,
    sort: str = "follower",
    follower_count: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]] | None:
    """Popular creators derived from the native For-You feed + profile hydrate.

    Creative Center's public creator ranking API is deprecated; this ranks
    creators appearing in ``recommend/item_list`` for ``country``, hydrates
    follower/like counts from profile rehydration, then sorts. Apify remains
    the fallthrough for Creative-Center-shaped lists.
    """
    feed = await trending_feed_native(country, limit=max(limit * 3, 40))
    if not feed:
        return None

    by_author: dict[str, dict[str, Any]] = {}
    for row in feed:
        username = safe_str(row.get("author"))
        if not username:
            continue
        slot = by_author.setdefault(
            username,
            {
                "username": username,
                "displayName": safe_str(row.get("authorName")),
                "views": 0,
                "posts": 0,
            },
        )
        slot["views"] += safe_int(row.get("views")) or 0
        slot["posts"] += 1
        if not slot.get("displayName") and row.get("authorName"):
            slot["displayName"] = safe_str(row.get("authorName"))

    if not by_author:
        return None

    # Hydrate the busiest authors first (most FYP appearances / views).
    candidates = sorted(
        by_author.values(),
        key=lambda s: (s["posts"], s["views"]),
        reverse=True,
    )[: max(limit * 2, limit)]

    creators: list[dict[str, Any]] = []
    for slot in candidates:
        ui = await _user_info(slot["username"])
        if ui is None:
            continue
        user = ui.get("user") or {}
        stats_v2 = ui.get("statsV2") or {}
        stats = ui.get("stats") or {}
        username = safe_str(user.get("uniqueId")) or slot["username"]
        followers = _stat(stats_v2, stats, "followerCount")
        if follower_count:
            bounds = _FOLLOWER_RANGES.get(follower_count.lower())
            if bounds and followers is not None:
                lo, hi = bounds
                if followers < lo or (hi is not None and followers >= hi):
                    continue
        likes = _stat(stats_v2, stats, "heartCount")
        videos = _stat(stats_v2, stats, "videoCount")
        avg_views = int(slot["views"] / slot["posts"]) if slot["posts"] else 0
        eng = creator_engagement_rate(likes, videos, followers)
        bio = safe_str(user.get("signature"))
        contact = extract_bio_contact(bio)
        # Creator locale from TikTok profile — never echo the feed `country` query.
        region = safe_str(user.get("region") or user.get("regionCode"))
        row: dict[str, Any] = {
            "id": safe_str(user.get("id") or user.get("uid")),
            "secUid": safe_str(user.get("secUid") or user.get("sec_uid")),
            "username": username,
            "displayName": safe_str(user.get("nickname")) or slot.get("displayName"),
            "url": f"https://www.tiktok.com/@{username}",
            "bio": bio,
            "followers": followers,
            "engagementRate": eng,
            "engagementRateBasis": ENGAGEMENT_RATE_BASIS,
            "likes": likes,
            "videos": videos,
            "avgViews": avg_views,
            "region": region,
            "verified": bool(user.get("verified")) if user.get("verified") is not None else None,
            "profileImage": safe_str(
                user.get("avatarLarger") or user.get("avatarMedium") or user.get("avatarThumb")
            ),
        }
        if contact:
            row["contact"] = contact
        creators.append(row)

    if not creators:
        return None

    sort_key = (sort or "follower").lower()
    if sort_key == "engagement":
        creators.sort(key=lambda c: (c.get("engagementRate") or 0, c.get("followers") or 0), reverse=True)
    elif sort_key == "popularity":
        creators.sort(key=lambda c: (c.get("avgViews") or 0, c.get("followers") or 0), reverse=True)
    else:
        creators.sort(key=lambda c: (c.get("followers") or 0, c.get("avgViews") or 0), reverse=True)

    out: list[dict[str, Any]] = []
    for i, c in enumerate(creators[:limit]):
        c["rank"] = i + 1
        out.append(c)
    return out


async def challenge_detail_native(hashtag: str) -> dict[str, Any] | None:
    """Population totals for a TikTok hashtag via ``/api/challenge/detail/``.

    Returns ``{hashtagId, name, videoCount, totalPlays, description}`` using
    ``statsV2`` (exact string counts). Legacy ``stats.videoCount`` is often 0
    even for huge tags — ignore it. Residential proxy required (datacenter
    returns an empty body).
    """
    tag = (hashtag or "").lstrip("#").strip()
    if not tag:
        return None
    url = (
        "https://www.tiktok.com/api/challenge/detail/"
        f"?challengeName={urllib.parse.quote(tag)}&language=en"
    )
    try:
        resp = await proxy_fetch(url, tier="residential", headers=TT_HEADERS, timeout=20)
    except httpx.HTTPError:
        return None
    if resp.status_code >= 400 or not (resp.text or "").strip():
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    info = payload.get("challengeInfo")
    if not isinstance(info, dict):
        return None
    challenge = info.get("challenge") if isinstance(info.get("challenge"), dict) else {}
    stats_v2 = info.get("statsV2") if isinstance(info.get("statsV2"), dict) else {}
    if not stats_v2 and isinstance(challenge.get("statsV2"), dict):
        stats_v2 = challenge["statsV2"]
    stats = info.get("stats") if isinstance(info.get("stats"), dict) else {}
    if not stats and isinstance(challenge.get("stats"), dict):
        stats = challenge["stats"]
    # Prefer statsV2 exact strings; fall back to stats only when V2 missing.
    video_count = safe_int(stats_v2.get("videoCount"))
    if video_count is None or video_count <= 0:
        video_count = safe_int(stats.get("videoCount"))
        if video_count is not None and video_count <= 0:
            video_count = None
    view_count = safe_int(stats_v2.get("viewCount"))
    if view_count is None or view_count <= 0:
        view_count = safe_int(stats.get("viewCount"))
        if view_count is not None and view_count <= 0:
            view_count = None
    hid = safe_str(challenge.get("id") or challenge.get("cid"))
    name = safe_str(challenge.get("title") or tag).lstrip("#").lower()
    if not hid and video_count is None and view_count is None:
        return None
    return {
        "hashtagId": hid,
        "name": name,
        "videoCount": video_count,
        "totalPlays": view_count,
        "description": safe_str(challenge.get("desc")) or None,
        # TikTok's public challenge/detail payload has no growth signal.
        "growthRate": None,
    }


async def enrich_hashtag_population_stats(
    rows: list[dict[str, Any]], *, concurrency: int = 8
) -> list[dict[str, Any]]:
    """Attach population videoCount/totalPlays/hashtagId from challenge/detail."""
    if not rows:
        return rows
    sem = asyncio.Semaphore(concurrency)

    async def _one(row: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            detail = await challenge_detail_native(row["name"])
        out = dict(row)
        if detail:
            out["hashtagId"] = detail.get("hashtagId")
            out["videoCount"] = detail.get("videoCount")
            out["totalPlays"] = detail.get("totalPlays")
            out["growthRate"] = detail.get("growthRate")
            if detail.get("description") and not out.get("description"):
                out["description"] = detail["description"]
        else:
            out.setdefault("hashtagId", None)
            out.setdefault("videoCount", None)
            out.setdefault("totalPlays", None)
            out.setdefault("growthRate", None)
        return out

    return list(await asyncio.gather(*[_one(r) for r in rows]))


async def popular_hashtags_native(
    query: str, *, limit: int = 20, n_videos: int = 25
) -> dict[str, Any] | None:
    """Related hashtags for a seed topic, with real TikTok population totals.

    Discovery is co-occurrence inside a sample of seed videos (hashtag page, or
    top-search when the seed tag is weak — e.g. default ``trending``). Sample
    tallies stay in ``sampleVideoCount`` / ``samplePlays``. Population
    ``videoCount`` / ``totalPlays`` come from ``/api/challenge/detail/``
    (statsV2). Final ``rank`` is by population videoCount among discovered tags.
    """
    seed = (query or "").lstrip("#").strip()
    if not seed:
        return None
    want = max(n_videos, limit)
    posts: list[dict[str, Any]] = []
    discovery_source = "hashtag_page"
    native = await hashtag_posts_native(seed, limit=want)
    if native is not None:
        posts, _has_more, _cursor = native
    if not posts:
        # ``trending`` / weak tags often soft-fail on challenge/item_list; search
        # still yields videos with co-occurring hashtags. Default query
        # ``trending`` is a keyword search seed — not TikTok's official chart.
        discovery_source = "top_search"
        searched = await top_search_native(seed, limit=want)
        if searched:
            posts, _more, _cur = searched
    if not posts:
        return None
    agg: dict[str, dict[str, int]] = {}
    for post in posts:
        tags = post.get("hashtags") or []
        if not isinstance(tags, list):
            continue
        plays = safe_int((post.get("engagement") or {}).get("views") or post.get("views")) or 0
        for t in tags:
            name = safe_str(t.get("name") if isinstance(t, dict) else t)
            if not name:
                continue
            name = name.lstrip("#").lower()
            if not name:
                continue
            slot = agg.setdefault(name, {"count": 0, "plays": 0})
            slot["count"] += 1
            slot["plays"] += plays
    if not agg:
        return None
    # Over-fetch candidates so enrichment + re-rank still fills ``limit``.
    candidate_n = min(len(agg), max(limit * 2, limit))
    by_sample = sorted(
        agg.items(), key=lambda kv: (kv[1]["count"], kv[1]["plays"]), reverse=True
    )[:candidate_n]
    sample_rows = [
        {
            "name": name,
            "url": f"https://www.tiktok.com/tag/{name}",
            "sampleVideoCount": slot["count"],
            "samplePlays": slot["plays"],
            # Legacy aliases kept null until population enrich — never echo sample
            # into videoCount/totalPlays (that was the silent bug).
            "videoCount": None,
            "totalPlays": None,
            "hashtagId": None,
            "growthRate": None,
        }
        for name, slot in by_sample
    ]
    enriched = await enrich_hashtag_population_stats(sample_rows)
    enriched.sort(
        key=lambda r: (
            r.get("videoCount") is not None,
            r.get("videoCount") or 0,
            r.get("sampleVideoCount") or 0,
            r.get("samplePlays") or 0,
        ),
        reverse=True,
    )
    hashtags = []
    for i, row in enumerate(enriched[:limit]):
        row = dict(row)
        row["rank"] = i + 1
        hashtags.append(row)
    return {
        "query": query,
        "discovery": "co_occurrence",
        "discoverySource": discovery_source,
        "sampleSize": len(posts),
        "rankBy": "videoCount",
        "totalReturned": len(hashtags),
        "hashtags": hashtags,
    }