"""Instagram data through Decodo's managed Social Media Scraping API.

Only Decodo targets with a documented Instagram GraphQL equivalent are used.
Every public function returns ``None`` on transport, auth, parsing, or data
quality failure so the router can safely fall back to Apify.
"""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from typing import Any, Iterable

import httpx
import structlog

from app.core.config import get_settings
from app.utils.formatters import first_present, safe_float, safe_int, safe_str

log = structlog.get_logger(__name__)


def enabled() -> bool:
    settings = get_settings()
    if settings.DECODO_AUTH_TOKEN.strip():
        return True
    return bool(settings.DECODO_USERNAME.strip() and settings.DECODO_PASSWORD.strip())


def _auth_header() -> str | None:
    """Decodo accepts a single Basic token or base64(user:pass)."""
    settings = get_settings()
    token = settings.DECODO_AUTH_TOKEN.strip()
    if token:
        return token if token.lower().startswith("basic ") else f"Basic {token}"
    user = settings.DECODO_USERNAME.strip()
    password = settings.DECODO_PASSWORD.strip()
    if user and password:
        encoded = base64.b64encode(f"{user}:{password}".encode()).decode()
        return f"Basic {encoded}"
    return None


async def _scrape(target: str, params: dict[str, Any]) -> Any | None:
    """POST to Decodo /v2/scrape. ``params`` holds target-specific input
    (v2 GraphQL targets take ``query``; URL-based targets take ``url``)."""
    if not enabled():
        return None
    settings = get_settings()
    auth_header = _auth_header()
    if not auth_header:
        return None
    body: dict[str, Any] = {
        "target": target,
        "locale": settings.DECODO_LOCALE,
        **params,
    }
    if settings.DECODO_GEO:
        body["geo"] = settings.DECODO_GEO
    try:
        async with httpx.AsyncClient(timeout=75.0) as client:
            response = await client.post(
                f"{settings.DECODO_BASE.rstrip('/')}/scrape",
                json=body,
                headers={
                    "Accept": "application/json",
                    "Authorization": auth_header,
                },
            )
    except httpx.HTTPError as exc:
        log.warning("decodo_transport_error", target=target, error=str(exc))
        return None
    if response.status_code != 200:
        log.warning("decodo_http_error", target=target, status=response.status_code)
        return None
    try:
        payload = response.json()
    except ValueError:
        return None
    if isinstance(payload, dict):
        # v2 envelope: {"results": [{"content": ...}]}
        results = payload.get("results")
        if isinstance(results, list) and results and isinstance(results[0], dict):
            content = results[0].get("content")
            if isinstance(content, str):
                try:
                    return json.loads(content)
                except ValueError:
                    return None
            if content is not None:
                return content
        # legacy envelope: {"data": {"content": ...}}
        data = payload.get("data")
        if isinstance(data, dict) and data.get("content") is not None:
            content = data["content"]
            if isinstance(content, str):
                try:
                    return json.loads(content)
                except ValueError:
                    return None
            return content
    return payload


def _walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _first_dict(value: Any, *keys: str) -> dict[str, Any] | None:
    for item in _walk(value):
        for key in keys:
            candidate = item.get(key)
            if isinstance(candidate, dict):
                return candidate
    return None


def _edge_nodes(value: Any, *edge_keys: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in _walk(value):
        for key in edge_keys:
            edge = item.get(key)
            if not isinstance(edge, dict) or not isinstance(edge.get("edges"), list):
                continue
            for row in edge["edges"]:
                if not isinstance(row, dict) or not isinstance(row.get("node"), dict):
                    continue
                node = row["node"]
                identity = safe_str(node.get("id") or node.get("shortcode"))
                if identity and identity in seen:
                    continue
                if identity:
                    seen.add(identity)
                result.append(node)
    return result


def _count(value: Any) -> int | None:
    if isinstance(value, dict):
        return safe_int(value.get("count"))
    return safe_int(value)


def _iso_timestamp(value: Any) -> str | None:
    if isinstance(value, (int, float)):
        return (
            datetime.fromtimestamp(value, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
    return safe_str(value) or None


def _image_url(node: dict[str, Any]) -> str | None:
    resources = node.get("display_resources")
    if isinstance(resources, list) and resources:
        last = resources[-1]
        if isinstance(last, dict) and last.get("src"):
            return safe_str(last["src"])
    return safe_str(
        node.get("display_url")
        or node.get("thumbnail_src")
        or node.get("profile_pic_url_hd")
        or node.get("profile_pic_url")
    ) or None


def _caption(node: dict[str, Any]) -> str:
    edges = node.get("edge_media_to_caption")
    if isinstance(edges, dict) and isinstance(edges.get("edges"), list) and edges["edges"]:
        first = edges["edges"][0]
        if isinstance(first, dict) and isinstance(first.get("node"), dict):
            return safe_str(first["node"].get("text"))
    return safe_str(node.get("caption") or node.get("description"))


def _owner(node: dict[str, Any]) -> dict[str, Any]:
    value = node.get("owner")
    return value if isinstance(value, dict) else {}


# Instagram hashtags must contain at least one non-numeric character, so
# "#1" in a caption ("ranked #1") is not a real hashtag - require one letter
# or underscore to avoid capturing purely numeric tokens.
_HASHTAG_RE = re.compile(r"#(\w*[^\W\d]\w*)", re.UNICODE)
# Usernames may contain dots but never end with one, so "@kyliejenner." in a
# caption must capture "kyliejenner" without the trailing punctuation.
_MENTION_RE = re.compile(r"@([A-Za-z0-9_](?:[A-Za-z0-9_.]*[A-Za-z0-9_])?)")


def _canonical_profile_url(username: str | None) -> str | None:
    """``https://www.instagram.com/{user}/`` — join-safe with channel-details."""
    from app.utils.url import canonical_instagram_profile_url

    return canonical_instagram_profile_url(username)


def build_ig_author(
    user: dict[str, Any] | None = None,
    *,
    username: str | None = None,
    followers: int | None = None,
    post_count: int | None = None,
) -> dict[str, Any]:
    """One author shape for hashtag / reels / tagged / channel list items.

    Always emits the same keys when values exist: id, username, displayName,
    url (www + trailing slash), verified, avatar, followers, postCount,
    isPrivate. Callers that only have a lean owner still get username + url;
    enrich fills the rest.
    """
    src = user if isinstance(user, dict) else {}
    uname = safe_str(username or src.get("username"))
    verified = src.get("is_verified")
    if verified is None:
        verified = src.get("verified")
    private = src.get("is_private")
    if private is None:
        private = src.get("isPrivate")
    if private is None:
        private = src.get("private")
    followers_n = followers
    if followers_n is None:
        followers_n = _count(src.get("edge_followed_by")) or safe_int(
            src.get("follower_count") or src.get("followers")
        )
    posts_n = post_count
    if posts_n is None:
        posts_n = _count(src.get("edge_owner_to_timeline_media")) or safe_int(
            src.get("media_count") or src.get("post_count") or src.get("postCount")
        )
    out: dict[str, Any] = {
        "id": safe_str(src.get("id") or src.get("pk") or src.get("pk_id")),
        "username": uname,
        "displayName": safe_str(src.get("full_name") or src.get("displayName")),
        "url": _canonical_profile_url(uname),
        "verified": verified,
        "avatar": _image_url(src)
        or safe_str(
            src.get("profile_pic_url") or src.get("avatar") or src.get("profileImage")
        )
        or None,
        "followers": followers_n,
        "postCount": posts_n,
        "isPrivate": private,
    }
    return {k: v for k, v in out.items() if v is not None}


def merge_ig_author(
    author: dict[str, Any] | None, enrich: dict[str, Any] | None
) -> dict[str, Any]:
    """Fill missing author fields from a richer profile/stats dict."""
    base = dict(author) if isinstance(author, dict) else {}
    extra = enrich if isinstance(enrich, dict) else {}
    # Prefer isPrivate; accept legacy private from older enrich blobs.
    if base.get("isPrivate") is None and base.get("private") is not None:
        base["isPrivate"] = base.pop("private")
    elif "private" in base:
        base.pop("private", None)
    if extra.get("isPrivate") is None and extra.get("private") is not None:
        extra = {**extra, "isPrivate": extra["private"]}
    # Promote legacy profileImage → avatar before merge.
    if base.get("avatar") is None and base.get("profileImage") is not None:
        base["avatar"] = base.pop("profileImage")
    else:
        base.pop("profileImage", None)
    if extra.get("avatar") is None and extra.get("profileImage") is not None:
        extra = {**extra, "avatar": extra["profileImage"]}
    for key in (
        "id",
        "username",
        "displayName",
        "url",
        "verified",
        "avatar",
        "followers",
        "postCount",
        "isPrivate",
    ):
        if base.get(key) is None and extra.get(key) is not None:
            base[key] = extra[key]
    uname = safe_str(base.get("username"))
    if uname:
        base["url"] = _canonical_profile_url(uname)
    return {
        k: v
        for k, v in base.items()
        if v is not None and k not in ("private", "profileImage", "handle")
    }


def hidden_count(value: Any) -> int | None:
    """Normalize Instagram engagement counts.

    Instagram uses ``-1`` for hidden like counts — map that to ``None``.
    Missing values stay ``None`` too (never invent ``0``; silent zeros poison
    averages and engagement rates).
    """
    n = safe_int(value)
    if n is None or n < 0:
        return None
    return n


def dedupe_preserve(items: Iterable[Any] | None) -> list[str]:
    """Stable unique strings (caption @mentions often repeat)."""
    out: list[str] = []
    seen: set[str] = set()
    for raw in items or []:
        s = safe_str(raw)
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def feed_play_metrics(media: dict[str, Any] | None) -> tuple[int | None, int | None, int | None]:
    """Per-item play metrics from one api/v1 feed media dict.

    Never builds a parallel list of play_counts to zip onto posts — callers
    must pass the same ``media`` row they are mapping. Image/Sidecar rows
    (media_type ≠ 2) return ``(None, None, None)``.
    """
    if not isinstance(media, dict):
        return None, None, None
    media_type = safe_int(media.get("media_type"))
    if media_type is not None and media_type != 2:
        return None, None, None
    play_count = safe_int(media.get("play_count"))
    ig = safe_int(media.get("ig_play_count"))
    fb = safe_int(media.get("fb_play_count") or media.get("fbPlayCount"))
    # On clips feed, ``view_count`` is IG-only when total ``play_count`` exists.
    # Never use bare ``view_count`` alone — that is the GraphQL undercount trap.
    if ig is None and play_count is not None:
        vc = safe_int(media.get("view_count"))
        if vc is not None and 0 <= vc <= play_count:
            ig = vc
    return play_count, ig, fb


def split_play_counts(
    *,
    play_count: int | None = None,
    ig_play_count: int | None = None,
    fb_play_count: int | None = None,
    video_view_count: int | None = None,
    likes: int | None = None,
    is_video: bool = True,
) -> dict[str, Any]:
    """Collapse Instagram play/view signals into one canonical ``views``.

    Upstream may ship several aliases for the same reel:
      - ``play_count`` / ``video_play_count`` — total plays (preferred)
      - ``ig_play_count`` — Instagram-side plays
      - ``fb_play_count`` — Facebook cross-post plays
      - ``video_view_count`` — reach-style / GraphQL view (often undercounts)

    Public shape (reels block):
      - ``views`` — the platform count we expose; never null when any of the
        above was read (except GraphQL undercount rejects).
      - ``viewsSource`` — ``"instagram"`` | ``"facebook"`` | ``null``.
        Non-null whenever ``views`` is non-null.

    ``plays`` / ``viewsInstagram`` / ``viewsFacebook`` are not returned.
    """
    if not is_video:
        return {
            "views": None,
            "viewsSource": None,
        }

    total = safe_int(play_count)
    ig = safe_int(ig_play_count)
    fb = safe_int(fb_play_count)
    gql = safe_int(video_view_count)

    views: int | None = None
    views_source: str | None = None

    if total is not None:
        views, views_source = total, "instagram"
    elif ig is not None:
        views, views_source = ig, "instagram"
    elif fb is not None:
        views, views_source = fb, "facebook"
    elif gql is not None:
        # GraphQL alone undercounts many Reels vs likes — reject that lie.
        if likes is None or likes <= gql:
            views, views_source = gql, "instagram"

    if views is not None and views_source is None:
        views_source = "instagram"

    return {
        "views": views,
        "viewsSource": views_source if views is not None else None,
    }


def pick_video_views(
    *,
    view_count: int | None,
    play_count: int | None,
    likes: int | None,
    is_video: bool,
    ig_play_count: int | None = None,
    fb_play_count: int | None = None,
) -> tuple[int | None, int | None]:
    """Legacy ``(views, plays)`` helper — prefer :func:`split_play_counts`."""
    split = split_play_counts(
        play_count=play_count,
        ig_play_count=ig_play_count,
        fb_play_count=fb_play_count,
        video_view_count=view_count,
        likes=likes,
        is_video=is_video,
    )
    return split["views"], split.get("plays", split["views"])


def engagement_with_play_split(
    engagement: dict[str, Any] | None,
    *,
    play_count: int | None = None,
    ig_play_count: int | None = None,
    fb_play_count: int | None = None,
    video_view_count: int | None = None,
    likes: int | None = None,
    is_video: bool = True,
) -> dict[str, Any]:
    """Merge canonical views (+ viewsSource) into engagement."""
    out = dict(engagement or {})
    # Drop retired keys if a caller still passed them through.
    out.pop("viewsInstagram", None)
    out.pop("viewsFacebook", None)
    out.pop("plays", None)
    split = split_play_counts(
        play_count=play_count,
        ig_play_count=ig_play_count,
        fb_play_count=fb_play_count,
        video_view_count=video_view_count,
        likes=likes if likes is not None else hidden_count(out.get("likes")),
        is_video=is_video,
    )
    out["views"] = split["views"]
    if is_video:
        out["viewsSource"] = split["viewsSource"]
    else:
        out.pop("viewsSource", None)
    return out


def map_ig_location(loc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize Instagram location nodes (GraphQL / api/v1 / Apify)."""
    if not isinstance(loc, dict):
        return None
    name = safe_str(loc.get("name"))
    lid = safe_str(loc.get("pk") or loc.get("id"))
    if not name and not lid:
        return None
    out: dict[str, Any] = {"id": lid, "name": name}
    slug = safe_str(loc.get("slug"))
    if slug:
        out["slug"] = slug
    if loc.get("has_public_page") is not None:
        out["hasPublicPage"] = bool(loc.get("has_public_page"))
    lat = safe_float(loc.get("lat") or loc.get("latitude"))
    lng = safe_float(loc.get("lng") or loc.get("longitude"))
    if lat is not None:
        out["latitude"] = lat
    if lng is not None:
        out["longitude"] = lng
    address_json = safe_str(loc.get("address_json") or loc.get("addressJson"))
    if address_json:
        out["addressJson"] = address_json
        try:
            parsed = json.loads(address_json)
        except (TypeError, ValueError):
            parsed = None
        if isinstance(parsed, dict):
            address = {
                "streetAddress": safe_str(parsed.get("street_address")),
                "zipCode": safe_str(parsed.get("zip_code")),
                "cityName": safe_str(parsed.get("city_name")),
            }
            address = {k: v for k, v in address.items() if v}
            if address:
                out["address"] = address
    return {k: v for k, v in out.items() if v is not None}


# Canonical channel-posts / channel-reels list-item shape. GraphQL timeline
# rows and api/v1 feed rows used to emit different key sets in one array —
# finalise_* forces one contract (null fillers). Adding keys is fine; dropping
# any baseline key fails CI (see shelved_keysets/instagram-channel-post.keys.json).
IG_CHANNEL_POST_KEYS: tuple[str, ...] = (
    "platform",
    "url",
    "id",
    "shortcode",
    "mediaId",
    "postType",
    "productType",
    "caption",
    "publishedAt",
    "durationSeconds",
    "thumbnailUrl",
    "videoUrl",
    "hasAudio",
    "mediaCount",
    "children",
    "author",
    "engagement",
    "hashtags",
    "mentions",
    "isPaidPartnership",
    "isAd",
    "isAffiliate",
    "accessibilityCaption",
    "likeAndViewCountsDisabled",
    "commentsDisabled",
    "music",
    "musicId",
)
IG_CAROUSEL_CHILD_KEYS: tuple[str, ...] = (
    "id",
    "mediaType",
    "thumbnailUrl",
    "videoUrl",
)
IG_AUTHOR_KEYS: tuple[str, ...] = (
    "id",
    "username",
    "displayName",
    "url",
    "verified",
    "avatar",
    "followers",
    "postCount",
    "isPrivate",
)
IG_MUSIC_KEYS: tuple[str, ...] = (
    "id",
    "title",
    "artist",
    "clusterId",
    "assetId",
    "canonicalId",
    "artistId",
    "durationMs",
    "audioType",
    "coverUrl",
    "isTrendingInClips",
    "trendRank",
    "previousTrendRank",
    "isExplicit",
    "hasLyrics",
)
# channel-reels only: drop tautologies (postType/productType), caption twin
# (description), carousel children (reels are single-media), and dead nulls.
IG_CHANNEL_REEL_KEYS: tuple[str, ...] = (
    "platform",
    "url",
    "id",
    "shortcode",
    "mediaId",
    "caption",
    "publishedAt",
    "durationSeconds",
    "thumbnailUrl",
    "videoUrl",
    "hasAudio",
    "author",
    "engagement",
    "hashtags",
    "mentions",
    "isPaidPartnership",
    "isAd",
    "isAffiliate",
    "likeAndViewCountsDisabled",
    "music",
    "musicId",
)
IG_REEL_AUTHOR_KEYS: tuple[str, ...] = tuple(
    k for k in IG_AUTHOR_KEYS if k != "postCount"
)
IG_REEL_MUSIC_KEYS: tuple[str, ...] = tuple(
    k for k in IG_MUSIC_KEYS if k not in {"trendRank", "previousTrendRank"}
)
IG_LOCATION_KEYS: tuple[str, ...] = (
    "id",
    "name",
    "slug",
    "hasPublicPage",
    "latitude",
    "longitude",
)
IG_CHANNEL_USER_KEYS: tuple[str, ...] = (
    "id",
    "username",
    "displayName",
    "url",
    "verified",
    "isPrivate",
    "avatar",
    "followers",
    "postCount",
)

_SHORTCODE_IN_URL_RE = re.compile(r"/(?:p|reel|tv)/([^/?#]+)", re.I)


def _finalise_keys(keys: tuple[str, ...], obj: dict[str, Any] | None) -> dict[str, Any]:
    src = obj if isinstance(obj, dict) else {}
    return {k: src.get(k, None) for k in keys}


def shortcode_from_url(url: str | None) -> str | None:
    m = _SHORTCODE_IN_URL_RE.search(url or "")
    return safe_str(m.group(1)) if m else None


def canonical_post_ids(post: dict[str, Any]) -> dict[str, Any]:
    """Force ``id``/``shortcode`` = shortcode and ``mediaId`` = numeric pk."""
    shortcode = safe_str(post.get("shortcode")) or shortcode_from_url(safe_str(post.get("url")))
    media_id = safe_str(post.get("mediaId"))
    raw_id = safe_str(post.get("id"))
    if raw_id and raw_id.isdigit():
        media_id = media_id or raw_id
    elif raw_id and not shortcode:
        shortcode = raw_id
    if shortcode and shortcode.isdigit() and not media_id:
        # Numeric-only id with no shortcode yet — keep as mediaId, try URL.
        media_id = shortcode
        shortcode = shortcode_from_url(safe_str(post.get("url")))
    post["shortcode"] = shortcode
    post["id"] = shortcode or media_id
    post["mediaId"] = media_id if media_id and media_id.isdigit() else None
    return post


def finalise_channel_post(post: dict[str, Any] | None) -> dict[str, Any]:
    """One key set for every channel-posts / channel-reels list item."""
    src = dict(post or {})
    # Legacy author.private → isPrivate; profileImage → avatar (naming convention).
    author = src.get("author") if isinstance(src.get("author"), dict) else {}
    if author.get("isPrivate") is None and author.get("private") is not None:
        author = {**author, "isPrivate": author.get("private")}
    if author.get("avatar") in (None, "") and author.get("profileImage") not in (None, ""):
        author = {**author, "avatar": author.get("profileImage")}
    author = {k: v for k, v in author.items() if k not in ("private", "profileImage", "handle")}
    # Re-canonicalize — older mappers emitted https://instagram.com/x (no www).
    if author.get("username") or author.get("url"):
        author["url"] = _canonical_profile_url(
            safe_str(author.get("username")) or safe_str(author.get("url"))
        )
    src["author"] = _finalise_keys(IG_AUTHOR_KEYS, author)

    music = src.get("music")
    if isinstance(music, dict) and music:
        src["music"] = _finalise_keys(IG_MUSIC_KEYS, music)
        if src.get("musicId") is None:
            src["musicId"] = src["music"].get("id")
    else:
        src["music"] = None

    canonical_post_ids(src)

    is_video = (
        src.get("postType") == "Video"
        or safe_str(src.get("productType")) in {"clips", "reel", "reels"}
        or bool(src.get("videoUrl"))
    )
    eng_src = src.get("engagement") if isinstance(src.get("engagement"), dict) else {}
    eng: dict[str, Any] = {
        "likes": eng_src.get("likes"),
        "comments": eng_src.get("comments"),
        "views": eng_src.get("views"),
    }
    if is_video:
        views_source = eng_src.get("viewsSource")
        if eng["views"] is not None and not views_source:
            views_source = "instagram"
        eng["viewsSource"] = views_source
    src["engagement"] = eng

    if not isinstance(src.get("hashtags"), list):
        src["hashtags"] = []
    if not isinstance(src.get("mentions"), list):
        src["mentions"] = []

    raw_children = src.get("children") if isinstance(src.get("children"), list) else []
    children: list[dict[str, Any]] = []
    for child in raw_children:
        if not isinstance(child, dict):
            continue
        children.append(_finalise_keys(IG_CAROUSEL_CHILD_KEYS, child))
    media_count = safe_int(src.get("mediaCount"))
    if media_count is None or media_count < 1:
        media_count = len(children) if children else 1
    src["children"] = children
    src["mediaCount"] = media_count

    out = _finalise_keys(IG_CHANNEL_POST_KEYS, src)
    out["platform"] = out.get("platform") or "instagram"
    out["author"] = src["author"]
    out["engagement"] = src["engagement"]
    out["music"] = src["music"]
    out["hashtags"] = src["hashtags"]
    out["mentions"] = src["mentions"]
    out["children"] = children
    out["mediaCount"] = media_count
    return out


def finalise_channel_posts(posts: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return [finalise_channel_post(p) for p in (posts or []) if isinstance(p, dict)]


def finalise_channel_reel(post: dict[str, Any] | None) -> dict[str, Any]:
    """Lean reels list row — no caption twin, no constant Video/clips enums."""
    base = finalise_channel_post(post)
    author = base.get("author") if isinstance(base.get("author"), dict) else {}
    music = base.get("music")
    out = {k: base.get(k) for k in IG_CHANNEL_REEL_KEYS}
    out["author"] = _finalise_keys(IG_REEL_AUTHOR_KEYS, author)
    if isinstance(music, dict) and music:
        out["music"] = _finalise_keys(IG_REEL_MUSIC_KEYS, music)
        if out.get("musicId") is None:
            out["musicId"] = out["music"].get("id")
    else:
        out["music"] = None
    return out


def finalise_channel_reels(posts: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return [finalise_channel_reel(p) for p in (posts or []) if isinstance(p, dict)]


def finalise_channel_user(user: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(user, dict):
        return None
    src = dict(user)
    if src.get("isPrivate") is None and src.get("private") is not None:
        src["isPrivate"] = src.get("private")
    if src.get("avatar") in (None, "") and src.get("profileImage") not in (None, ""):
        src["avatar"] = src.get("profileImage")
    src.pop("private", None)
    src.pop("profileImage", None)
    src.pop("handle", None)
    src["url"] = _canonical_profile_url(
        safe_str(src.get("username")) or safe_str(src.get("url"))
    )
    return _finalise_keys(IG_CHANNEL_USER_KEYS, src)


def strip_null_post_fields(post: dict[str, Any]) -> dict[str, Any]:
    """Drop fields we can't fill instead of returning nulls: video-only
    fields (videoUrl) on images/carousels, hidden engagement counts (None)
    except ``engagement.views`` / ``viewsSource`` on videos, and author
    fields the source doesn't provide.

    ``durationSeconds`` stays on the object when present (null allowed) so
    array rows keep a uniform key set — never silently drop the key.

    Prefer ``finalise_channel_post`` on channel-posts / channel-reels responses
    so GraphQL + feed rows share one key set (null fillers, not drops).
    """
    if not post.get("videoUrl"):
        post.pop("videoUrl", None)
    engagement = post.get("engagement")
    eng_dict = engagement if isinstance(engagement, dict) else {}
    is_video = (
        post.get("postType") == "Video"
        or safe_str(post.get("productType")) in {"clips", "reel", "reels"}
        or bool(post.get("videoUrl"))
        # Trending strips constant postType — still a video when view keys exist.
        or "viewsSource" in eng_dict
    )
    # Keep durationSeconds key on videos (null ok); drop only on non-videos
    # that never had a meaningful duration.
    if "durationSeconds" in post or is_video:
        if post.get("durationSeconds") is None:
            post["durationSeconds"] = None
        else:
            try:
                post["durationSeconds"] = round(float(post["durationSeconds"]), 3)
            except (TypeError, ValueError):
                post["durationSeconds"] = None
    if not safe_str(post.get("productType")):
        post.pop("productType", None)
    if isinstance(engagement, dict):
        # Retired keys — never ship them again.
        engagement.pop("viewsInstagram", None)
        engagement.pop("viewsFacebook", None)
        engagement.pop("plays", None)
        likes = engagement.get("likes")
        views = engagement.get("views")
        views_source = engagement.get("viewsSource")
        # Discriminator must track views (never null while views is set).
        if views is not None and not views_source:
            views_source = "instagram"
        if views is None:
            views_source = None
        keep_null = {"views"}
        if is_video:
            keep_null |= {"viewsSource"}
        # Hidden counts: keep likes:null so clients can pair with
        # likeAndViewCountsDisabled (0 ≠ omitted ≠ hidden).
        if post.get("likeAndViewCountsDisabled"):
            keep_null |= {"likes", "viewsSource"}
            engagement.setdefault("likes", None)
        cleaned = {
            k: v
            for k, v in engagement.items()
            if (v is not None or k in keep_null)
            and k not in {"viewsInstagram", "viewsFacebook", "plays"}
        }
        cleaned["views"] = views
        if is_video:
            cleaned["viewsSource"] = views_source
        else:
            cleaned.pop("viewsSource", None)
        post["engagement"] = cleaned
    author = post.get("author")
    if isinstance(author, dict):
        post["author"] = {k: v for k, v in author.items() if v is not None}
    for key in (
        "location",
        "music",
        "accessibilityCaption",
        "musicId",
        "previewComments",
        "shortcode",
        "mediaId",
        "hasAudio",
        "coauthors",
        "mashupInfo",
    ):
        val = post.get(key)
        if val in (None, [], {}):
            post.pop(key, None)
    return post


def resolve_graphql_likes_and_plays(
    node: dict[str, Any], *, is_video: bool
) -> tuple[int | None, int | None, int | None]:
    """Separate likes from plays on Instagram GraphQL media nodes.

    Hashtag / Explore Reel cards often put the **view** total in
    ``edge_media_preview_like.count`` (or a flattened ``likes`` field) while
    omitting real ``like_count``. Treating that as likes inflates engagement
    ~50× and leaves ``engagement.views`` empty.

    Rule: for videos, only ``like_count`` (and aliases) count as likes.
    Preview / flattened ``likes`` are reclaimable as play totals when GraphQL
    omitted ``play_count``. Images/Sidecars still use preview as likes.

    Returns ``(likes, play_count, video_view_count)``.
    """
    # Authoritative like total (Polaris / api/v1 / richer GraphQL). Never use
    # edge_media_preview_like / flattened likes here for videos — those are
    # the hashtag Reel view trap.
    true_likes = hidden_count(
        first_present(
            node.get("like_count"),
            node.get("likeCount"),
            node.get("likes_count"),
        )
    )
    preview_like = hidden_count(
        first_present(
            _count(node.get("edge_media_preview_like")),
            _count(node.get("edge_liked_by")),
            node.get("likes"),
        )
    )
    play_count = safe_int(node.get("video_play_count") or node.get("play_count"))
    video_view_count = safe_int(node.get("video_view_count") or node.get("view_count"))

    if is_video:
        likes = true_likes
        if preview_like is not None and play_count is None:
            # No like_count → preview is the view total on hashtag Reel cards.
            # With like_count, only reclaim when preview ≈ video_view_count.
            if true_likes is None:
                play_count = preview_like
            elif (
                video_view_count is not None
                and video_view_count > 0
                and abs(preview_like - video_view_count) / video_view_count <= 0.05
            ):
                play_count = preview_like
        if video_view_count is None and play_count is not None and true_likes is None:
            # Keep video_view_count for split_play_counts fallthrough when
            # Instagram only stuffed the total into preview_like.
            video_view_count = play_count
        return likes, play_count, video_view_count

    likes = true_likes if true_likes is not None else preview_like
    return likes, play_count, video_view_count


def _post(node: dict[str, Any], profile: dict[str, Any] | None = None) -> dict[str, Any]:
    # Per-post nodes only carry a minimal owner ({id, username}); the full
    # author (name, verified, avatar, followers) lives on the profile object,
    # which is the same for every post in a channel listing. `profile` fills
    # those gaps when the caller knows the owning profile â€” but only when the
    # node is actually owned by that profile (collab posts can be owned by a
    # different account).
    owner = _owner(node)
    owner_username = safe_str(owner.get("username"))
    profile_username = safe_str((profile or {}).get("username"))
    if profile and (not owner_username or owner_username == profile_username):
        author = {**profile, **owner}
    else:
        author = owner
    username = safe_str(author.get("username") or node.get("user_posted"))
    shortcode = safe_str(node.get("shortcode") or node.get("code"))
    media_id = safe_str(node.get("id") or node.get("pk"))
    typename = safe_str(node.get("__typename"))
    is_video = bool(node.get("is_video")) or typename == "GraphVideo"
    is_sidecar = typename == "GraphSidecar"
    caption = _caption(node) or ""
    # GraphQL often undercounts plays vs api/v1 ``play_count`` — still emit
    # views when we have a signal; feed enrich upgrades totals when matched.
    # Never put view totals into ``likes`` (see resolve_graphql_likes_and_plays).
    likes, play_count, video_view_count = resolve_graphql_likes_and_plays(
        node, is_video=is_video
    )
    likes_disabled = node.get("like_and_view_counts_disabled")
    if likes_disabled is None:
        likes_disabled = node.get("likeAndViewCountsDisabled")
    if likes_disabled is not None:
        likes_disabled = bool(likes_disabled)
        if likes_disabled:
            likes = None
            play_count = None
            video_view_count = None
    ig_play_count = (
        None if likes_disabled else safe_int(node.get("ig_play_count"))
    )
    fb_play_count = (
        None
        if likes_disabled
        else safe_int(node.get("fb_play_count") or node.get("fbPlayCount"))
    )
    product = safe_str(node.get("product_type")) or ("clips" if is_video else None)
    children, media_count = _carousel_children_from_graphql(node)
    # Prefer shortcode as id; mediaId is always the numeric pk when known.
    result = {
        "platform": "instagram",
        "url": safe_str(node.get("url"))
        or (f"https://www.instagram.com/{'reel' if is_video else 'p'}/{shortcode}/" if shortcode else None),
        "id": shortcode or media_id,
        "shortcode": shortcode,
        "mediaId": media_id if media_id and str(media_id).isdigit() else None,
        "postType": "Sidecar" if is_sidecar else ("Video" if is_video else "Image"),
        "productType": product,
        "caption": caption,
        "publishedAt": _iso_timestamp(node.get("taken_at_timestamp") or node.get("date_posted")),
        "durationSeconds": safe_float(node.get("video_duration") or node.get("length")),
        "thumbnailUrl": _image_url(node),
        # Cover videoUrl is for single videos; carousel videos live in children[].
        "videoUrl": (safe_str(node.get("video_url")) or None) if is_video and not is_sidecar else None,
        "hasAudio": node.get("has_audio") if node.get("has_audio") is not None else None,
        "mediaCount": media_count,
        "children": children,
        "author": build_ig_author(author, username=username),
        "engagement": engagement_with_play_split(
            {
                "likes": likes,
                "comments": hidden_count(
                    first_present(
                        _count(node.get("edge_media_to_comment")),
                        node.get("comment_count"),
                        node.get("num_comments"),
                    )
                ),
            },
            play_count=play_count,
            ig_play_count=ig_play_count,
            fb_play_count=fb_play_count,
            video_view_count=video_view_count,
            likes=likes,
            is_video=is_video,
        ),
        "hashtags": dedupe_preserve(_HASHTAG_RE.findall(caption)),
        "mentions": dedupe_preserve(_MENTION_RE.findall(caption)),
        "isPaidPartnership": bool(node.get("is_paid_partnership"))
        if node.get("is_paid_partnership") is not None
        else False,
        "isAd": bool(node.get("is_ad") or node.get("ad_id")),
        "isAffiliate": bool(node.get("affiliate_info") or node.get("is_affiliate")),
        "accessibilityCaption": safe_str(node.get("accessibility_caption")),
        "likeAndViewCountsDisabled": likes_disabled,
        "commentsDisabled": (
            bool(node.get("comments_disabled"))
            if node.get("comments_disabled") is not None
            else None
        ),
    }
    music = node.get("clips_music_attribution_info")
    if isinstance(music, dict) and (
        music.get("audio_id") or music.get("song_name") or music.get("artist_name")
    ):
        result["music"] = {
            "id": safe_str(music.get("audio_id")),
            "title": safe_str(music.get("song_name")),
            "artist": safe_str(music.get("artist_name")),
        }
        result["musicId"] = result["music"].get("id")
    return strip_null_post_fields(result)


def _carousel_children_from_graphql(node: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    """GraphQL ``edge_sidecar_to_children`` → (children, mediaCount)."""
    edge = node.get("edge_sidecar_to_children")
    edges = edge.get("edges") if isinstance(edge, dict) else None
    if not isinstance(edges, list) or not edges:
        # Some scrapers flatten carousel children onto the node.
        flat = node.get("carousel_media") or node.get("children")
        if isinstance(flat, list) and flat:
            children: list[dict[str, Any]] = []
            for item in flat:
                if not isinstance(item, dict):
                    continue
                media = item.get("media") if isinstance(item.get("media"), dict) else item
                child = _graphql_child_node(media)
                if child:
                    children.append(child)
            return children, max(len(children), 1)
        return [], 1
    children = []
    for edge_item in edges:
        if not isinstance(edge_item, dict):
            continue
        child_node = edge_item.get("node") if isinstance(edge_item.get("node"), dict) else edge_item
        child = _graphql_child_node(child_node)
        if child:
            children.append(child)
    return children, max(len(children), 1)


def _graphql_child_node(node: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(node, dict):
        return None
    typename = safe_str(node.get("__typename"))
    is_video = bool(node.get("is_video")) or typename == "GraphVideo"
    child_id = safe_str(node.get("id") or node.get("pk"))
    if child_id and not child_id.isdigit():
        # Prefer numeric pk when shortcode leaked into id.
        child_id = safe_str(node.get("pk")) if safe_str(node.get("pk") or "").isdigit() else child_id
    return {
        "id": child_id,
        "mediaType": "video" if is_video else "image",
        "thumbnailUrl": _image_url(node),
        "videoUrl": (safe_str(node.get("video_url")) or None) if is_video else None,
    }


async def _profile(handle: str) -> dict[str, Any] | None:
    data = await _scrape(
        "instagram_graphql_profile",
        {"query": handle.strip().lstrip("@")},
    )
    user = _first_dict(data, "user")
    if user and (user.get("username") or user.get("id")):
        return user
    if isinstance(data, dict) and (data.get("username") or data.get("id")):
        return data
    return None


async def channel_details(handle: str) -> dict[str, Any] | None:
    # Keep field parity with instagram_native.map_channel_details (additive).
    from app.services.instagram_native import map_channel_details

    user = await _profile(handle)
    if not user:
        return None
    return map_channel_details(user, handle=handle)


async def profile_user(handle: str) -> dict[str, Any] | None:
    """Raw Instagram GraphQL user node for profile-search enrichment."""
    return await _profile(handle)


async def basic_profile(handle: str) -> dict[str, Any] | None:
    user = await _profile(handle)
    if not user:
        return None
    username = safe_str(user.get("username")) or handle
    return {
        "platform": "instagram",
        "id": safe_str(user.get("id")),
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "avatar": _image_url(user),
        "verified": user.get("is_verified"),
        "isPrivate": user.get("is_private"),
        "followers": _count(user.get("edge_followed_by")) or safe_int(user.get("followers")),
    }


def _channel_user_summary(user: dict[str, Any]) -> dict[str, Any]:
    """Lean profile block returned with channel-posts/reels (SC ``user{}`` parity)."""
    username = safe_str(user.get("username"))
    out: dict[str, Any] = {
        "id": safe_str(user.get("id") or user.get("pk")),
        "username": username,
        "displayName": safe_str(user.get("full_name")),
        "url": _canonical_profile_url(username),
        "verified": user.get("is_verified"),
        # Same key as nested author{} / channel-details (A21) — never ``private``.
        "isPrivate": user.get("is_private"),
        "avatar": _image_url(user),
        "followers": _count(user.get("edge_followed_by")) or safe_int(user.get("follower_count")),
        "postCount": _count(user.get("edge_owner_to_timeline_media"))
        or safe_int(user.get("media_count")),
    }
    return finalise_channel_user(out) or out


async def channel_posts(handle: str, limit: int) -> dict[str, Any] | None:
    """First timeline page. Returns {"items", "userId", "hasMore", "followers", "user"}
    so the router can build a feed cursor (``<media pk>_<user id>``) and
    continue through Instagram's api/v1 feed endpoint."""
    user = await _profile(handle)
    if not user:
        return None
    nodes = _edge_nodes(user, "edge_owner_to_timeline_media")
    posts = [_post(node, profile=user) for node in nodes]
    if not posts:
        return None
    timeline = user.get("edge_owner_to_timeline_media") or {}
    has_more = bool((timeline.get("page_info") or {}).get("has_next_page")) or len(posts) > limit
    return {
        "items": posts[:limit],
        "userId": safe_str(user.get("id")),
        "hasMore": has_more,
        "followers": _count(user.get("edge_followed_by")),
        "user": _channel_user_summary(user),
    }


async def channel_reels(handle: str, limit: int) -> dict[str, Any] | None:
    user = await _profile(handle)
    if not user:
        return None
    # The felix (IGTV) edge only carries legacy uploads that stop around
    # 2022, so leading with it buries an account's actual recent Reels.
    # Videos on the regular timeline come first; felix is a fallback for
    # accounts whose videos never hit the grid.
    def _videos(*edges: str) -> list[dict[str, Any]]:
        return [
            _post(node, profile=user)
            for node in _edge_nodes(user, *edges)
            if bool(node.get("is_video")) or node.get("__typename") == "GraphVideo"
        ]

    reels = _videos("edge_owner_to_timeline_media") or _videos("edge_felix_video_timeline")
    timeline = user.get("edge_owner_to_timeline_media") or {}
    has_more = bool((timeline.get("page_info") or {}).get("has_next_page")) or len(reels) > limit
    return {
        "items": reels[:limit],
        "userId": safe_str(user.get("id")),
        "hasMore": has_more,
        "followers": _count(user.get("edge_followed_by")),
        "user": _channel_user_summary(user),
    }


async def hashtag_medias(tag: str, limit: int, *, reels_only: bool = False) -> list[dict[str, Any]] | None:
    name = tag.lstrip("#").strip()
    if not name:
        return None
    data = await _scrape("instagram_graphql_hashtag", {"query": name})
    nodes = _edge_nodes(data, "edge_hashtag_to_top_posts", "edge_hashtag_to_media")
    if reels_only:
        nodes = [node for node in nodes if bool(node.get("is_video")) or node.get("__typename") == "GraphVideo"]
    return [_post(node) for node in nodes[:limit]] or None


async def video_download(url: str) -> dict[str, Any] | None:
    data = await _scrape("instagram_graphql_post", {"url": url})
    media = _first_dict(data, "shortcode_media", "xdt_shortcode_media")
    if not media:
        return None
    download_url = safe_str(media.get("video_url"))
    if not download_url:
        return None
    return {
        "platform": "instagram",
        "url": url,
        "downloadUrl": download_url,
        "thumbnailUrl": _image_url(media),
        "duration": safe_float(media.get("video_duration")),
    }
