"""TikTok Creative Center trend rankings (hashtags, songs, creators).

Public charts live on ``ads.tiktok.com/business/creativecenter/inspiration/popular``
and are served by signed ``creative_radar_api`` XHRs. Native path mirrors Top Ads:
Decodo headless + XHR capture. These charts expose real population totals,
``rank_diff``, and ``trend[]`` time series — not sample co-occurrence counts.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import structlog

from app.services.tiktok_creative_center import _parse_xhr_body
from app.utils.formatters import safe_float, safe_int, safe_str

log = structlog.get_logger(__name__)

HASHTAG_PAGE = (
    "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
)
SONG_PAGE = (
    "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pc/en"
)
CREATOR_PAGE = (
    "https://ads.tiktok.com/business/creativecenter/inspiration/popular/creator/pc/en"
)
# Popular videos chart (same family as SC tiktok/videos/popular).
VIDEO_PAGE = (
    "https://ads.tiktok.com/business/creativecenter/inspiration/popular/pc/en"
)

HASHTAG_LIST_PATH = "creative_radar_api/v1/popular_trend/hashtag/list"
SONG_LIST_PATH = "creative_radar_api/v1/popular_trend/sound/rank_list"
CREATOR_LIST_PATH = "creative_radar_api/v1/popular_trend/creator/list"
VIDEO_LIST_PATH = "creative_radar_api/v1/popular_trend/list"

TREND_PERIODS = frozenset({7, 30, 120})
RANK_TYPES = frozenset({"popular", "surging"})
# SC orderBy: like / hot / comment / repost → Creative Center order_by.
VIDEO_ORDER_BY = frozenset({"vv", "like", "comment", "repost"})


def normalize_trend_period(value: int | None) -> int:
    """Creative Center trend windows are 7 / 30 / 120 days (180 → 120)."""
    period = int(value or 7)
    if period == 180:
        period = 120
    if period not in TREND_PERIODS:
        raise ValueError("period must be 7, 30, or 120 days (180 maps to 120)")
    return period


def normalize_rank_type(value: str | None) -> str:
    raw = (value or "popular").strip().lower().replace("-", "_")
    if raw not in RANK_TYPES:
        raise ValueError("rankType must be popular or surging")
    return raw


def normalize_creator_sort(value: str | None) -> str:
    raw = (value or "follower").strip().lower()
    if raw == "popularity":
        raw = "follower"
    if raw not in {"follower", "engagement"}:
        raise ValueError("sort must be follower, engagement, or popularity")
    return raw


def normalize_video_order_by(value: str | None) -> str:
    """Map SC-style orderBy (hot/like/comment/repost) → CC ``order_by``."""
    raw = (value or "hot").strip().lower().replace("-", "_")
    aliases = {
        "hot": "vv",
        "vv": "vv",
        "view": "vv",
        "views": "vv",
        "play": "vv",
        "plays": "vv",
        "like": "like",
        "likes": "like",
        "comment": "comment",
        "comments": "comment",
        "repost": "repost",
        "reposts": "repost",
        "share": "repost",
        "shares": "repost",
    }
    mapped = aliases.get(raw)
    if mapped is None or mapped not in VIDEO_ORDER_BY:
        raise ValueError("orderBy must be hot, like, comment, or repost")
    return mapped


def _trend_points(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for pt in raw:
        if not isinstance(pt, dict):
            continue
        t = safe_int(pt.get("time") or pt.get("timestamp"))
        v = safe_float(pt.get("value"))
        if t is None and v is None:
            continue
        out.append({"time": t, "value": v})
    return out


def _growth_from_trend(trend: list[dict[str, Any]]) -> float | None:
    vals = [p["value"] for p in trend if p.get("value") is not None]
    if len(vals) < 2:
        return None
    first, last = vals[0], vals[-1]
    if first is None or last is None or first == 0:
        return None
    try:
        return round((float(last) - float(first)) / abs(float(first)), 4)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def normalize_trend_hashtag(
    row: dict[str, Any], *, country: str, period: int
) -> dict[str, Any] | None:
    name = safe_str(
        row.get("hashtag_name") or row.get("hashtagName") or row.get("name")
    )
    if not name:
        return None
    name = name.lstrip("#")
    trend = _trend_points(
        row.get("trend") or row.get("popularity") or row.get("popularityCurve")
    )
    industry = row.get("industry_info") if isinstance(row.get("industry_info"), dict) else {}
    country_info = (
        row.get("country_info") if isinstance(row.get("country_info"), dict) else {}
    )
    video_count = safe_int(
        row.get("publish_cnt") or row.get("publishCnt") or row.get("video_count")
    )
    total_plays = safe_int(
        row.get("video_views") or row.get("videoViews") or row.get("vv")
    )
    out: dict[str, Any] = {
        "rank": safe_int(row.get("rank")),
        "rankDiff": safe_int(
            row.get("rank_diff") if row.get("rank_diff") is not None else row.get("rankDiff")
        ),
        "rankDiffType": safe_int(
            row.get("rank_diff_type")
            if row.get("rank_diff_type") is not None
            else row.get("rankDiffType")
        ),
        "name": name,
        "hashtagId": safe_str(
            row.get("hashtag_id") or row.get("hashtagId") or row.get("id")
        ),
        "url": f"https://www.tiktok.com/tag/{name}",
        "videoCount": video_count,
        "totalPlays": total_plays,
        "trend": trend or None,
        "growthRate": _growth_from_trend(trend),
        "promoted": bool(row.get("promoted")) if row.get("promoted") is not None else None,
        "newOnBoard": bool(
            row.get("is_new") or row.get("new_on_board") or row.get("newOnBoard")
        )
        if (
            row.get("is_new") is not None
            or row.get("new_on_board") is not None
            or row.get("newOnBoard") is not None
        )
        else None,
        "industry": safe_str(
            industry.get("value") or industry.get("label") or row.get("industry")
        ),
        "industryId": safe_str(
            industry.get("id") or row.get("industry_id") or row.get("industryId")
        ),
        "country": safe_str(
            country_info.get("id") or country_info.get("value") or country
        ),
        "period": period,
        "source": "creative_center",
    }
    return {k: v for k, v in out.items() if v is not None}


def normalize_trend_song(
    row: dict[str, Any], *, country: str, period: int, rank_type: str
) -> dict[str, Any] | None:
    song_id = safe_str(
        row.get("song_id")
        or row.get("songId")
        or row.get("clip_id")
        or row.get("clipId")
        or row.get("id")
    )
    title = safe_str(
        row.get("title") or row.get("song_name") or row.get("songName") or row.get("name")
    )
    if not song_id and not title:
        return None
    trend = _trend_points(row.get("trend") or row.get("popularity"))
    author = row.get("author") if isinstance(row.get("author"), str) else None
    if author is None and isinstance(row.get("artists"), list) and row["artists"]:
        first = row["artists"][0]
        author = safe_str(first.get("name") if isinstance(first, dict) else first)
    if author is None:
        author = safe_str(
            row.get("artist_name") or row.get("artist") or row.get("authorName")
        )
    clip_id = safe_str(row.get("clip_id") or row.get("clipId"))
    cover = safe_str(
        row.get("cover")
        or row.get("cover_url")
        or row.get("coverUrl")
        or (
            row.get("cover_url_medium")
            if isinstance(row.get("cover_url_medium"), str)
            else None
        )
    )
    music_url = None
    if song_id:
        slug = (title or "sound").replace(" ", "-")
        music_url = f"https://www.tiktok.com/music/{slug}-{song_id}"
    related = row.get("related_items") or row.get("relatedItems") or []
    if not isinstance(related, list):
        related = []
    if_cml = row.get("if_cml") if row.get("if_cml") is not None else row.get("ifCml")
    out: dict[str, Any] = {
        "rank": safe_int(row.get("rank")),
        "rankDiff": safe_int(
            row.get("rank_diff") if row.get("rank_diff") is not None else row.get("rankDiff")
        ),
        "rankDiffType": safe_int(
            row.get("rank_diff_type")
            if row.get("rank_diff_type") is not None
            else row.get("rankDiffType")
        ),
        "songId": song_id,
        "clipId": clip_id,
        "title": title,
        "artist": author,
        "url": music_url,
        "coverUrl": cover,
        "durationSeconds": safe_float(row.get("duration") or row.get("durationSeconds")),
        "ifCml": bool(if_cml) if if_cml is not None else None,
        "commercialMusic": bool(if_cml) if if_cml is not None else None,
        "promoted": bool(row.get("promoted")) if row.get("promoted") is not None else None,
        "newOnBoard": bool(
            row.get("new_on_board") or row.get("newOnBoard") or row.get("is_new")
        )
        if (
            row.get("new_on_board") is not None
            or row.get("newOnBoard") is not None
            or row.get("is_new") is not None
        )
        else None,
        "trend": trend or None,
        "growthRate": _growth_from_trend(trend),
        "relatedItems": related or None,
        "country": country,
        "period": period,
        "rankType": rank_type,
        "source": "creative_center",
    }
    return {k: v for k, v in out.items() if v is not None}


def normalize_trend_creator(row: dict[str, Any], *, country: str) -> dict[str, Any] | None:
    author = row.get("author") if isinstance(row.get("author"), dict) else {}
    username = safe_str(
        row.get("unique_id")
        or row.get("uniqueId")
        or row.get("username")
        or row.get("handle")
        or author.get("unique_id")
        or author.get("uniqueId")
    )
    if not username:
        return None
    username = username.lstrip("@")
    tcm = row.get("tcm") if isinstance(row.get("tcm"), dict) else {}
    followers = safe_int(
        row.get("follower_cnt")
        or row.get("followerCnt")
        or row.get("followers")
        or row.get("follower_count")
        or tcm.get("follower_cnt")
    )
    eng = safe_float(
        row.get("interact_rate")
        or row.get("interactRate")
        or row.get("engagement_rate")
        or row.get("engagementRate")
        or tcm.get("interact_rate")
    )
    # CC often ships ER as 0–1 ratio; surface as percent when clearly a ratio.
    if eng is not None and 0 < eng <= 1:
        eng = round(eng * 100, 4)
    elif eng is not None:
        eng = round(eng, 4)
    avg_views = safe_int(
        row.get("video_views")
        or row.get("avg_views")
        or row.get("avgViews")
        or row.get("vv")
    )
    out: dict[str, Any] = {
        "rank": safe_int(row.get("rank")),
        "rankDiff": safe_int(
            row.get("rank_diff") if row.get("rank_diff") is not None else row.get("rankDiff")
        ),
        "id": safe_str(
            row.get("uid") or row.get("user_id") or row.get("id") or row.get("creator_id")
        ),
        "secUid": safe_str(row.get("sec_uid") or row.get("secUid")),
        "username": username,
        "displayName": safe_str(
            row.get("nick_name")
            or row.get("nickname")
            or row.get("displayName")
            or row.get("name")
        ),
        "url": f"https://www.tiktok.com/@{username}",
        "followers": followers,
        "engagementRate": eng,
        "engagementRateBasis": "creative_center" if eng is not None else None,
        "avgViews": avg_views,
        "likes": safe_int(row.get("liked_cnt") or row.get("likes") or row.get("heart")),
        "videos": safe_int(row.get("video_cnt") or row.get("videos") or row.get("aweme_count")),
        "verified": bool(row.get("verified")) if row.get("verified") is not None else None,
        "profileImage": safe_str(
            row.get("avatar")
            or row.get("avatar_url")
            or row.get("profileImage")
            or row.get("cover_url")
        ),
        "tcmId": safe_str(row.get("tcm_id") or row.get("tcmId") or tcm.get("tcm_id")),
        "audienceCountry": safe_str(
            row.get("audience_country")
            or row.get("audienceCountry")
            or row.get("creator_country")
        ),
        "country": country,
        "source": "creative_center",
    }
    return {k: v for k, v in out.items() if v is not None}


def _pagination(data: dict[str, Any]) -> dict[str, Any] | None:
    pag = data.get("pagination") if isinstance(data.get("pagination"), dict) else None
    if not pag:
        return None
    total = safe_int(
        pag.get("total") or pag.get("total_count") or pag.get("totalCount")
    )
    size = safe_int(pag.get("size") or pag.get("limit"))
    has_more = (
        bool(pag.get("has_more") if pag.get("has_more") is not None else pag.get("hasMore"))
        if (pag.get("has_more") is not None or pag.get("hasMore") is not None)
        else None
    )
    return {
        "page": safe_int(pag.get("page")),
        "size": size,
        "limit": size,
        "total": total,
        "totalCount": total,
        "hasMore": has_more,
        "has_more": has_more,
    }


def _list_from_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in (
        "list",
        "videos",
        "sounds",
        "sound_list",
        "creators",
        "items",
        "materials",
    ):
        raw = data.get(key)
        if isinstance(raw, list):
            return [r for r in raw if isinstance(r, dict)]
    return []


def normalize_trend_video(
    row: dict[str, Any],
    *,
    country: str,
    period: int,
    order_by: str,
    rank: int | None = None,
) -> dict[str, Any] | None:
    """Map Creative Center popular video row → trending-feed public shape."""
    vid = safe_str(
        row.get("item_id")
        or row.get("itemId")
        or row.get("id")
        or row.get("video_id")
        or row.get("videoId")
        or row.get("aweme_id")
    )
    url = safe_str(row.get("item_url") or row.get("itemUrl") or row.get("url"))
    if not url and vid:
        url = f"https://www.tiktok.com/@tiktok/video/{vid}"
    if not vid and not url:
        return None
    cover = safe_str(row.get("cover") or row.get("cover_url") or row.get("coverUrl"))
    caption = safe_str(row.get("title") or row.get("desc") or row.get("caption"))
    duration = safe_float(row.get("duration") or row.get("durationSeconds"))
    if duration is not None and duration > 1000:
        duration = duration / 1000.0
    region = safe_str(
        row.get("region") or row.get("country_code") or row.get("countryCode") or country
    )
    author = row.get("author") if isinstance(row.get("author"), dict) else {}
    uid = safe_str(
        author.get("unique_id")
        or author.get("uniqueId")
        or row.get("unique_id")
        or row.get("uniqueId")
    )
    if not uid and isinstance(row.get("author"), str):
        uid = safe_str(row.get("author"))
    out: dict[str, Any] = {
        "platform": "tiktok",
        "url": url,
        "id": vid,
        "caption": caption,
        "mediaType": "video",
        "durationSeconds": duration,
        "coverUrl": cover,
        "thumbnailUrl": cover,
        "author": uid,
        "authorId": safe_str(author.get("id") or author.get("uid") or row.get("uid")),
        "secUid": safe_str(author.get("sec_uid") or author.get("secUid")),
        "authorName": safe_str(
            author.get("nickname") or author.get("nick_name") or author.get("nickName")
        ),
        "views": safe_int(
            row.get("vv")
            or row.get("video_views")
            or row.get("play_count")
            or row.get("views")
        ),
        "likes": safe_int(row.get("like") or row.get("like_count") or row.get("likes")),
        "comments": safe_int(
            row.get("comment") or row.get("comment_count") or row.get("comments")
        ),
        "shares": safe_int(
            row.get("repost") or row.get("share_count") or row.get("shares")
        ),
        "saves": safe_int(row.get("collect_count") or row.get("saves")),
        "rank": rank if rank is not None else safe_int(row.get("rank")),
        "region": region,
        "countryCode": safe_str(
            row.get("country_code") or row.get("countryCode") or country
        ),
        "period": period,
        "orderBy": order_by,
        "source": "creative_center",
    }
    return {k: v for k, v in out.items() if v is not None}


async def _capture_trend_list(
    *,
    page_url: str,
    list_path: str,
    geo: str,
    timeout: float = 150.0,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None] | None:
    from app.services import decodo_fetch

    if not decodo_fetch.enabled():
        return None
    actions = [{"type": "wait", "timeout": 6}]
    got = await decodo_fetch.fetch_xhr(
        page_url,
        timeout=timeout,
        headless="html",
        browser_actions=actions,
        geo=geo if geo.isalpha() and len(geo) == 2 else "US",
    )
    if got is None:
        log.warning("tiktok_cc_trend_decodo_miss", page=page_url)
        return None
    _status, xhrs = got
    best: dict[str, Any] | None = None
    best_score = -1
    for item in xhrs:
        url = str(item.get("url") or "")
        if list_path not in url:
            continue
        status = item.get("status_code")
        if status is not None and status != 200:
            continue
        body = _parse_xhr_body(item)
        if not body:
            continue
        data = body.get("data") if isinstance(body.get("data"), dict) else {}
        rows = _list_from_data(data if isinstance(data, dict) else {})
        score = 5 + len(rows)
        if score > best_score:
            best_score = score
            best = item
    if not best or best_score < 5:
        log.warning(
            "tiktok_cc_trend_no_list_xhr",
            page=page_url,
            xhr_count=len(xhrs),
            path=list_path,
        )
        return None
    body = _parse_xhr_body(best)
    if not body:
        return None
    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    if not isinstance(data, dict):
        return None
    return _list_from_data(data), _pagination(data)


async def search_popular_hashtags(
    *,
    country: str = "US",
    period: int = 7,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "popular",
    new_on_board: bool = False,
    industry_id: str | None = None,
) -> dict[str, Any] | None:
    region = (country or "US").strip().upper() or "US"
    period_days = normalize_trend_period(period)
    params: dict[str, str] = {
        "period": str(period_days),
        "region": region,
        "page": str(max(1, page)),
        "limit": str(max(1, min(int(limit), 60))),
        "sort_by": (sort_by or "popular").strip().lower(),
    }
    if new_on_board:
        params["filter_by"] = "new_on_board"
    if industry_id:
        params["industry_id"] = industry_id.strip()
    page_url = f"{HASHTAG_PAGE}?{urlencode(params)}"
    captured = await _capture_trend_list(
        page_url=page_url, list_path=HASHTAG_LIST_PATH, geo=region
    )
    if captured is None:
        return None
    rows, pagination = captured
    hashtags = [
        h
        for h in (
            normalize_trend_hashtag(r, country=region, period=period_days) for r in rows
        )
        if h
    ][: max(0, min(int(limit), 60))]
    for i, row in enumerate(hashtags):
        row.setdefault("rank", i + 1)
    return {
        "country": region,
        "period": period_days,
        "page": max(1, page),
        "sortBy": params["sort_by"],
        "newOnBoard": bool(new_on_board),
        "source": "creative_center",
        "discovery": "creative_center",
        "rankBy": "creative_center_rank",
        "totalReturned": len(hashtags),
        "pagination": pagination,
        "hashtags": hashtags,
    }


async def search_popular_songs(
    *,
    country: str = "US",
    period: int = 7,
    page: int = 1,
    limit: int = 20,
    rank_type: str = "popular",
    new_on_board: bool = False,
    commercial_music: bool = False,
) -> dict[str, Any] | None:
    region = (country or "US").strip().upper() or "US"
    period_days = normalize_trend_period(period)
    rt = normalize_rank_type(rank_type)
    params: dict[str, str] = {
        "period": str(period_days),
        "region": region,
        "page": str(max(1, page)),
        "limit": str(max(1, min(int(limit), 20))),
        "rank_type": rt,
        "new_on_board": "true" if new_on_board else "false",
        "commercial_music": "true" if commercial_music else "false",
    }
    page_url = f"{SONG_PAGE}?{urlencode(params)}"
    captured = await _capture_trend_list(
        page_url=page_url, list_path=SONG_LIST_PATH, geo=region, timeout=180.0
    )
    if captured is None:
        return None
    rows, pagination = captured
    songs = [
        s
        for s in (
            normalize_trend_song(r, country=region, period=period_days, rank_type=rt)
            for r in rows
        )
        if s
    ][: max(0, min(int(limit), 20))]
    for i, row in enumerate(songs):
        row.setdefault("rank", i + 1)
    return {
        "country": region,
        "period": period_days,
        "page": max(1, page),
        "rankType": rt,
        "newOnBoard": bool(new_on_board),
        "commercialMusic": bool(commercial_music),
        "source": "creative_center",
        "totalReturned": len(songs),
        "pagination": pagination,
        "songs": songs,
        "note": (
            "TikTok Creative Center popular/surging sounds. "
            "This endpoint can take up to ~30 seconds."
        ),
    }


async def search_popular_videos(
    *,
    country: str = "US",
    period: int = 7,
    page: int = 1,
    limit: int = 20,
    order_by: str = "vv",
) -> dict[str, Any] | None:
    """Creative Center popular videos chart (SC ``videos/popular`` equivalent)."""
    region = (country or "US").strip().upper() or "US"
    period_days = normalize_trend_period(period)
    ob = normalize_video_order_by(order_by)
    lim = max(1, min(int(limit), 20))
    params: dict[str, str] = {
        "period": str(period_days),
        "region": region,
        "country_code": region,
        "page": str(max(1, page)),
        "limit": str(lim),
        "order_by": ob,
    }
    page_url = f"{VIDEO_PAGE}?{urlencode(params)}"
    captured = await _capture_trend_list(
        page_url=page_url, list_path=VIDEO_LIST_PATH, geo=region
    )
    if captured is None:
        return None
    rows, pagination = captured
    videos: list[dict[str, Any]] = []
    for i, raw in enumerate(rows):
        mapped = normalize_trend_video(
            raw,
            country=region,
            period=period_days,
            order_by=ob,
            rank=i + 1,
        )
        if mapped:
            videos.append(mapped)
        if len(videos) >= lim:
            break
    if not videos:
        return None
    return {
        "country": region,
        "countryCode": region,
        "period": period_days,
        "page": max(1, page),
        "orderBy": ob,
        "source": "creative_center",
        "discovery": "creative_center",
        "totalReturned": len(videos),
        "pagination": pagination
        or {
            "page": max(1, page),
            "limit": lim,
            "size": lim,
            "total": None,
            "totalCount": None,
            "hasMore": len(videos) >= lim,
            "has_more": len(videos) >= lim,
        },
        "results": videos,
    }


async def search_popular_creators(
    *,
    country: str = "US",
    page: int = 1,
    limit: int = 20,
    sort: str = "follower",
) -> dict[str, Any] | None:
    region = (country or "US").strip().upper() or "US"
    sort_by = normalize_creator_sort(sort)
    params: dict[str, str] = {
        "region": region,
        "page": str(max(1, page)),
        "limit": str(max(1, min(int(limit), 50))),
        "sort_by": sort_by,
        "creator_country": region,
    }
    page_url = f"{CREATOR_PAGE}?{urlencode(params)}"
    captured = await _capture_trend_list(
        page_url=page_url, list_path=CREATOR_LIST_PATH, geo=region
    )
    if captured is None:
        return None
    rows, pagination = captured
    creators = [
        c for c in (normalize_trend_creator(r, country=region) for r in rows) if c
    ][: max(0, min(int(limit), 50))]
    for i, row in enumerate(creators):
        row.setdefault("rank", i + 1)
    return {
        "platform": "tiktok",
        "country": region,
        "sort": sort_by,
        "page": max(1, page),
        "source": "creative_center",
        "totalReturned": len(creators),
        "pagination": pagination,
        "creators": creators,
        "note": (
            "Ranked from TikTok Creative Center creator chart "
            "(ads.tiktok.com/business/creativecenter). engagementRate is "
            "TikTok's official interact rate when exposed."
        ),
    }


def apify_trends_input(
    *,
    mode: str,
    country: str,
    period: int,
    limit: int,
    rank_type: str | None = None,
) -> dict[str, Any]:
    """Input for ``datapeak/tiktok-creative-center`` hashtags/songs modes."""
    payload: dict[str, Any] = {
        "mode": mode,
        "region": (country or "US").upper(),
        "period": str(period),
        "maxItems": max(1, min(int(limit), 100)),
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        },
    }
    if rank_type:
        payload["rankType"] = rank_type
        payload["rank_type"] = rank_type
    return payload
