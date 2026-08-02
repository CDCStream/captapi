"""Native Facebook post/reel details via Decodo JS-rendered HTML.

Public permalinks return ScheduledServerJS / Relay blobs that already carry
``creation_story.short_form_video_context`` (reels) or ``Story`` nodes (posts).
We hydrate those into the same raw shape ``_normalize_post`` understands —
no Apify.
"""

from __future__ import annotations

import base64
import json
import re
from typing import Any
from urllib.parse import unquote, urlparse

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

# One Decodo JS render; flat fee with ~120% markup headroom.
CREDIT_FB_DETAILS_NATIVE = 2

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)


def _walk(obj: Any, pred, out: list[Any], depth: int = 0, limit: int = 80) -> None:
    if depth > 45 or len(out) >= limit:
        return
    if isinstance(obj, dict):
        if pred(obj):
            out.append(obj)
        for value in obj.values():
            _walk(value, pred, out, depth + 1, limit)
    elif isinstance(obj, list):
        for value in obj:
            _walk(value, pred, out, depth + 1, limit)


def _load_blobs(html: str) -> list[Any]:
    blobs: list[Any] = []
    for match in _SCRIPT_RE.finditer(html):
        raw = match.group(1)
        if "__typename" not in raw and "short_form_video_context" not in raw:
            continue
        try:
            blobs.append(json.loads(raw))
        except ValueError:
            continue
    return blobs


def _b64_decode(value: str) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    pad = "=" * (-len(raw) % 4)
    try:
        return base64.b64decode(raw + pad).decode("utf-8", "replace")
    except Exception:
        return None


def _feedback_post_id(feedback_id: str | None) -> str | None:
    """``feedback:POSTID`` or ``feedback:POSTID_comment…`` → POSTID."""
    decoded = _b64_decode(feedback_id or "") or (feedback_id or "")
    if not decoded.startswith("feedback:"):
        return None
    tail = decoded.split(":", 1)[1]
    post = tail.split("_", 1)[0]
    return post if post.isdigit() else None


def _parse_count(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value or "").strip().lower().replace(",", "")
    if not text:
        return None
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([kmb])?", text)
    if not m:
        n = safe_int(text)
        return n
    num = float(m.group(1))
    suf = m.group(2)
    if suf == "k":
        num *= 1_000
    elif suf == "m":
        num *= 1_000_000
    elif suf == "b":
        num *= 1_000_000_000
    return int(num)


def _reaction_total(feedback: dict[str, Any]) -> int | None:
    for key in ("likers", "unified_reactors", "reactors"):
        block = feedback.get(key)
        if isinstance(block, dict):
            n = _parse_count(block.get("count") or block.get("count_reduced"))
            if n is not None:
                return n
    top = feedback.get("top_reactions")
    if isinstance(top, dict):
        edges = top.get("edges")
        if isinstance(edges, list) and edges:
            total = 0
            for edge in edges:
                if isinstance(edge, dict):
                    total += safe_int(edge.get("reaction_count")) or 0
            return total
    return _parse_count(feedback.get("reaction_count") or feedback.get("i18n_reaction_count"))


def _url_signals(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    path = unquote(parsed.path or "")
    out: dict[str, str] = {"path": path.rstrip("/")}
    m = re.search(r"/reel[s]?/(\d+)", path, re.I)
    if m:
        out["reel_id"] = m.group(1)
    m = re.search(r"/videos?/(\d+)", path, re.I)
    if m:
        out["video_id"] = m.group(1)
    m = re.search(r"/posts/(pfbid[\w]+|\d+)", path, re.I)
    if m:
        out["post_token"] = m.group(1)
    m = re.search(r"[?&]v=(\d+)", url)
    if m:
        out["watch_id"] = m.group(1)
    return out


def _meta_content(html: str, prop: str) -> str | None:
    patterns = (
        rf'<meta[^>]+property=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(prop)}["\']',
    )
    for pat in patterns:
        m = re.search(pat, html, re.I)
        if m:
            return (
                m.group(1)
                .replace("&amp;", "&")
                .replace("&#039;", "'")
                .replace("&quot;", '"')
            )
    return None


def _views_from_og_title(title: str | None) -> int | None:
    if not title:
        return None
    m = re.search(r"([\d.,]+\s*[KMB]?)\s*views", title, re.I)
    if not m:
        return None
    return _parse_count(m.group(1).replace(" ", ""))



def _post_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r"/(?:posts|videos|reel|reels)/[^/]*?(\d{10,})/?$", urlparse(url).path or "")
    if m:
        return m.group(1)
    m = re.search(r"/(\d{10,})/?$", urlparse(url).path or "")
    return m.group(1) if m else None


def _page_slug(url: str) -> str | None:
    path = urlparse(url).path or ""
    parts = [p for p in path.split("/") if p]
    skip = {
        "reel", "reels", "watch", "videos", "posts", "photo", "photos",
        "story.php", "permalink.php", "groups", "share",
    }
    for part in parts:
        low = part.lower()
        if low in skip or part.isdigit() or part.startswith("pfbid"):
            continue
        return part
    return None


def _story_message(story: dict[str, Any]) -> str | None:
    direct = story.get("message")
    if isinstance(direct, dict) and isinstance(direct.get("text"), str):
        return direct["text"]
    found: list[dict[str, Any]] = []
    _walk(
        story,
        lambda o: isinstance(o.get("message"), dict)
        and isinstance(o["message"].get("text"), str)
        and len(o["message"]["text"]) > 0,
        found,
        limit=20,
    )
    if not found:
        return None
    # Prefer the longest caption-like text (skip short UI crumbs).
    best = max(found, key=lambda o: len(o["message"]["text"]))
    return best["message"]["text"]


def _pick_creation_story(blobs: list[Any], signals: dict[str, str]) -> dict[str, Any] | None:
    stories: list[dict[str, Any]] = []
    _walk(
        blobs,
        lambda o: isinstance(o.get("creation_story"), dict)
        and isinstance(o["creation_story"].get("short_form_video_context"), dict),
        stories,
        limit=20,
    )
    if not stories:
        return None
    want = signals.get("reel_id") or signals.get("video_id") or signals.get("watch_id")
    if want:
        for wrap in stories:
            cs = wrap["creation_story"]
            sf = cs.get("short_form_video_context") or {}
            playback = sf.get("playback_video") if isinstance(sf, dict) else {}
            vid = safe_str((playback or {}).get("id") or (sf.get("video") or {}).get("id"))
            if vid == want or safe_str(cs.get("post_id")) == want:
                return cs
    return stories[0]["creation_story"]


def _pick_story(
    blobs: list[Any], signals: dict[str, str], *, og_url: str | None = None, page: str | None = None
) -> dict[str, Any] | None:
    stories: list[dict[str, Any]] = []
    _walk(
        blobs,
        lambda o: o.get("__typename") == "Story" and o.get("post_id") and o.get("permalink_url"),
        stories,
        limit=40,
    )
    if not stories:
        return None

    og_post_id = _post_id_from_url(og_url)

    def _score(st: dict[str, Any]) -> tuple[int, int, int]:
        permalink = safe_str(st.get("permalink_url")) or ""
        post_id = safe_str(st.get("post_id")) or ""
        msg = _story_message(st) or ""
        has_att = 1 if st.get("attachments") else 0
        id_hit = 10 if og_post_id and post_id == og_post_id else 0
        page_hit = 0
        if page and page.lower() in permalink.lower():
            page_hit = 3
        elif page:
            actors = st.get("actors") if isinstance(st.get("actors"), list) else []
            for actor in actors[:3]:
                if isinstance(actor, dict) and page.lower() in (safe_str(actor.get("url")) or "").lower():
                    page_hit = 2
                    break
        og_hit = 2 if og_url and (og_url.rstrip("/") in permalink.rstrip("/") or permalink.rstrip("/") in og_url.rstrip("/")) else 0
        token = signals.get("post_token")
        token_hit = 4 if token and token in permalink else 0
        return (id_hit + token_hit + og_hit + page_hit + has_att, len(msg), safe_int(st.get("creation_time")) or 0)

    stories.sort(key=_score, reverse=True)
    best = stories[0]
    # Reject comment-sidebar noise: require message or media/short_form.
    if not (_story_message(best) or best.get("attachments")):
        return None
    return best


def _engagement_for_post(blobs: list[Any], post_id: str | None) -> dict[str, Any]:
    # Missing counts stay None — never invent 0 (especially shares).
    out: dict[str, Any] = {"likes": None, "comments": None, "shares": None, "feedbackId": None}
    if not post_id:
        return out
    nodes: list[dict[str, Any]] = []
    _walk(
        blobs,
        lambda o: isinstance(o, dict)
        and (
            o.get("total_comment_count") is not None
            or o.get("share_count_reduced") is not None
            or isinstance(o.get("reactors"), dict)
            or isinstance(o.get("likers"), dict)
            or isinstance(o.get("unified_reactors"), dict)
            or isinstance(o.get("top_reactions"), dict)
            or isinstance(o.get("comment_rendering_instance"), dict)
        ),
        nodes,
        limit=120,
    )
    best_likes = -1
    for node in nodes:
        raw_fid = safe_str(node.get("id"))
        fid = _feedback_post_id(raw_fid)
        url = safe_str(node.get("url")) or ""
        # Skip per-comment feedback (…?comment_id=).
        if "comment_id=" in url:
            continue
        if fid and fid != post_id:
            continue
        if not fid and post_id not in (url or ""):
            # Still accept nodes that only expose counts without a feedback id
            # when they sit next to matching post context (reel hydration).
            if node.get("total_comment_count") is None and node.get("share_count_reduced") is None:
                continue

        likes = _reaction_total(node)
        comments = safe_int(node.get("total_comment_count"))
        if comments is None:
            cri = node.get("comment_rendering_instance")
            if isinstance(cri, dict):
                comments = safe_int((cri.get("comments") or {}).get("total_count"))
        if comments is None:
            crf = node.get("comment_rendering_instance_for_feed_location")
            if isinstance(crf, dict):
                comments = safe_int((crf.get("comments") or {}).get("total_count"))
        shares = _parse_count(node.get("share_count_reduced") or node.get("share_count"))

        if likes is not None and likes > best_likes:
            best_likes = likes
            out["likes"] = likes
            if raw_fid and (fid == post_id or not out.get("feedbackId")):
                out["feedbackId"] = raw_fid
        if comments is not None:
            out["comments"] = max(out["comments"] or 0, comments)
        if shares is not None:
            out["shares"] = max(out["shares"] or 0, shares)
        if out.get("feedbackId") is None and raw_fid and fid == post_id:
            out["feedbackId"] = raw_fid
    return out


def _iso_from_unix(raw: Any) -> str | None:
    if raw is None:
        return None
    try:
        ts = int(raw)
    except (TypeError, ValueError):
        return safe_str(raw)
    if ts <= 0:
        return None
    from datetime import datetime, timezone

    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", ".000Z")
    except (OSError, OverflowError, ValueError):
        return None


def _top_comments_from_obj(obj: Any, *, limit: int = 3) -> list[dict[str, Any]]:
    """Best-effort sample comments embedded next to a Story (when FB includes them)."""
    nodes: list[dict[str, Any]] = []
    _walk(
        obj,
        lambda o: o.get("__typename") == "Comment"
        and isinstance(o.get("body"), dict)
        and isinstance(o["body"].get("text"), str),
        nodes,
        limit=40,
    )
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in nodes:
        cid = safe_str(node.get("legacy_fbid") or node.get("id"))
        body = node.get("body") if isinstance(node.get("body"), dict) else {}
        text = body.get("text") if isinstance(body, dict) else None
        if not cid or cid in seen or not isinstance(text, str) or not text.strip():
            continue
        # Skip nested replies when depth is exposed.
        depth = safe_int(node.get("depth"))
        if depth is not None and depth > 0:
            continue
        seen.add(cid)
        author = node.get("author") if isinstance(node.get("author"), dict) else {}
        gender = safe_str(author.get("gender"))
        row: dict[str, Any] = {
            "id": cid,
            "text": text,
            "publishTime": _iso_from_unix(node.get("created_time")),
            "author": {
                "id": safe_str(author.get("id")),
                "name": safe_str(author.get("name")),
                "url": safe_str(author.get("url")),
            },
        }
        if gender:
            row["author"]["gender"] = gender
        out.append(row)
        if len(out) >= limit:
            break
    return out


def _actor_from_story(story: dict[str, Any]) -> dict[str, Any]:
    """Posting user/page — never the group node itself."""
    actors = story.get("actors") if isinstance(story.get("actors"), list) else []
    for cand in actors[:5]:
        if not isinstance(cand, dict):
            continue
        url = safe_str(cand.get("url")) or ""
        typename = safe_str(cand.get("__typename")) or ""
        if typename == "Group" or "/groups/" in url.lower():
            continue
        if cand.get("name") and (cand.get("id") or url):
            return cand
    found: list[dict[str, Any]] = []
    _walk(
        story,
        lambda o: o.get("__typename") in ("User", "Page")
        and o.get("name")
        and o.get("url")
        and "facebook.com" in str(o.get("url"))
        and "/groups/" not in str(o.get("url")).lower(),
        found,
        limit=10,
    )
    return found[0] if found else {}


def _music_from_short_form(sf: dict[str, Any]) -> dict[str, Any] | None:
    """Best-effort Reel audio / soundtrack block."""
    if not isinstance(sf, dict):
        return None
    candidates: list[dict[str, Any]] = []
    for key in ("audio", "music", "music_info", "track", "original_audio"):
        block = sf.get(key)
        if isinstance(block, dict):
            candidates.append(block)
    audio_asset = sf.get("audio_asset") if isinstance(sf.get("audio_asset"), dict) else None
    if audio_asset:
        candidates.append(audio_asset)
    for cand in candidates:
        nested = cand.get("audio_asset") if isinstance(cand.get("audio_asset"), dict) else cand
        if not isinstance(nested, dict):
            continue
        mid = safe_str(
            nested.get("id")
            or cand.get("id")
            or nested.get("audio_id")
            or cand.get("audio_id")
        )
        title = safe_str(
            nested.get("title")
            or nested.get("track_title")
            or cand.get("track_title")
            or cand.get("title")
            or nested.get("music_title")
        )
        art = None
        for art_key in ("music_album_art_uri", "album_art", "cover_art", "thumbnail_uri", "image"):
            val = nested.get(art_key) or cand.get(art_key)
            if isinstance(val, dict):
                art = safe_str(val.get("uri") or val.get("url"))
            else:
                art = safe_str(val)
            if art:
                break
        mtype = safe_str(nested.get("type") or cand.get("type") or nested.get("audio_type"))
        if mid or title:
            return {
                "id": mid,
                "type": mtype,
                "trackTitle": title,
                "albumArt": art,
            }
    return None


def _captions_url_from_video(video: dict[str, Any] | None) -> str | None:
    if not isinstance(video, dict):
        return None
    for key in ("captions_url", "captionsUrl", "caption_url"):
        val = safe_str(video.get(key))
        if val:
            return val
    locales = video.get("video_available_captions_locales") or video.get("captions")
    if isinstance(locales, list):
        for loc in locales:
            if not isinstance(loc, dict):
                continue
            val = safe_str(loc.get("captions_url") or loc.get("url") or loc.get("uri"))
            if val:
                return val
    return None


def _external_link_from_message(message: dict[str, Any] | None) -> str | None:
    if not isinstance(message, dict):
        return None
    for rng in message.get("ranges") or []:
        if not isinstance(rng, dict):
            continue
        entity = rng.get("entity") if isinstance(rng.get("entity"), dict) else {}
        for key in ("external_url", "url", "mobileUrl"):
            val = safe_str(entity.get(key))
            if val and "facebook.com" not in val:
                return val
    return None


def _from_creation_story(cs: dict[str, Any], blobs: list[Any], page_url: str) -> dict[str, Any]:
    sf = cs.get("short_form_video_context") if isinstance(cs.get("short_form_video_context"), dict) else {}
    post_id = safe_str(cs.get("post_id"))
    eng = _engagement_for_post(blobs, post_id)
    message = cs.get("message") if isinstance(cs.get("message"), dict) else {}
    playback = sf.get("playback_video") if isinstance(sf.get("playback_video"), dict) else {}
    video_owner = sf.get("video_owner") if isinstance(sf.get("video_owner"), dict) else {}
    item: dict[str, Any] = {
        "short_form_video_context": sf,
        "postId": post_id,
        "post_id": post_id,
        "creation_time": cs.get("creation_time"),
        "message": message,
        "text": message.get("text") if isinstance(message, dict) else None,
        "url": safe_str(sf.get("shareable_url"))
        or safe_str(playback.get("permalink_url"))
        or page_url,
        "facebookUrl": page_url,
        "likes": eng["likes"],
        "comments": eng["comments"],
        "shares": eng["shares"],
        "likesCount": eng["likes"],
        "commentsCount": eng["comments"],
        "sharesCount": eng["shares"],
        "feedbackId": eng.get("feedbackId"),
        "captionsUrl": _captions_url_from_video(playback),
        "music": _music_from_short_form(sf),
        "link": _external_link_from_message(message if isinstance(message, dict) else None),
        "isVideo": True,
        "attachments": cs.get("attachments"),
        "user": {
            "id": safe_str(video_owner.get("id")),
            "name": safe_str(video_owner.get("name")),
            "profileUrl": safe_str(video_owner.get("url")),
            "isVerified": video_owner.get("is_verified")
            if video_owner.get("is_verified") is not None
            else video_owner.get("isVerified"),
        },
    }
    return item


def _from_story(story: dict[str, Any], blobs: list[Any], page_url: str) -> dict[str, Any]:
    post_id = safe_str(story.get("post_id"))
    eng = _engagement_for_post(blobs, post_id)
    actor = _actor_from_story(story)
    message_text = _story_message(story)
    message = {"text": message_text} if message_text else None
    permalink = safe_str(story.get("permalink_url")) or page_url
    actor_url = safe_str(actor.get("url"))
    actor_id = safe_str(actor.get("id"))
    if not actor_id and actor_url:
        m = re.search(r"facebook\.com/(?:profile\.php\?id=)?(\d{5,})", actor_url)
        if m:
            actor_id = m.group(1)
    # Vanity handle only — never a /groups/{slug} segment.
    actor_username = None
    if actor_url and "/groups/" not in actor_url.lower():
        m = re.search(r"facebook\.com/([A-Za-z0-9.\-_]+)/?", actor_url)
        if m:
            handle = m.group(1)
            if handle.lower() not in {
                "profile.php", "people", "pages", "watch", "reel", "groups", "photo",
            } and not handle.isdigit():
                actor_username = handle
    item: dict[str, Any] = {
        "postId": post_id,
        "post_id": post_id,
        "creation_time": story.get("creation_time"),
        "message": message,
        "text": message_text,
        "url": permalink,
        "permalink": permalink,
        "facebookUrl": page_url,
        "pageUrl": actor_url,
        "pageName": safe_str(actor.get("name")),
        "pageUsername": actor_username,
        "user": {
            "id": actor_id,
            "name": safe_str(actor.get("name")),
            "profileUrl": actor_url,
            "username": actor_username,
            "shortName": safe_str(actor.get("short_name")),
            "isVerified": actor.get("is_verified")
            if actor.get("is_verified") is not None
            else actor.get("isVerified"),
            "profilePic": None,
        },
        "attachments": story.get("attachments"),
        "media": None,
        "likes": eng["likes"],
        "comments": eng["comments"],
        "shares": eng["shares"],
        "likesCount": eng["likes"],
        "commentsCount": eng["comments"],
        "sharesCount": eng["shares"],
        "feedbackId": eng.get("feedbackId"),
        "isVideo": False,
        "link": _external_link_from_message(message),
        "topComments": _top_comments_from_obj(story, limit=3),
    }
    # Thumbnail / video: prefer styles.attachment.media (has photo_image),
    # not the stub attachments[].media which is often just {id, __typename}.
    atts = story.get("attachments") if isinstance(story.get("attachments"), list) else []
    for att in atts:
        if not isinstance(att, dict):
            continue
        styles = att.get("styles") if isinstance(att.get("styles"), dict) else {}
        styled = styles.get("attachment") if isinstance(styles.get("attachment"), dict) else {}
        rich = styled.get("media") if isinstance(styled.get("media"), dict) else None
        stub = att.get("media") if isinstance(att.get("media"), dict) else None
        media = rich or stub
        if not isinstance(media, dict):
            continue
        item["media"] = media
        item["attachments"] = [{"media": media, "styles": styles}] if styles else [att]
        photo = media.get("photo_image") if isinstance(media.get("photo_image"), dict) else {}
        thumb = safe_str(photo.get("uri")) or safe_str((media.get("image") or {}).get("uri") if isinstance(media.get("image"), dict) else None)
        if thumb:
            item["thumbnailUrl"] = thumb
        if media.get("__typename") == "Video" or media.get("playable_duration_in_ms"):
            item["isVideo"] = True
        break
    # Optional short_form on reshared/attached video posts.
    sf_nodes: list[dict[str, Any]] = []
    _walk(
        story,
        lambda o: isinstance(o.get("short_form_video_context"), dict),
        sf_nodes,
        limit=5,
    )
    if sf_nodes:
        item["short_form_video_context"] = sf_nodes[0]["short_form_video_context"]
        item["isVideo"] = True
    return item


async def details_native(url: str) -> dict[str, Any] | None:
    """Return a raw post dict for ``_normalize_post``, or None on failure."""
    if not url or not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, html = got
    if status != 200 or not html:
        return None
    if "short_form_video_context" not in html and '"__typename":"Story"' not in html:
        log.info("facebook_details_native_empty", url=url[:120])
        return None

    blobs = _load_blobs(html)
    if not blobs:
        return None
    signals = _url_signals(url)
    og_url = _meta_content(html, "og:url")
    og_title = _meta_content(html, "og:title")
    views = _views_from_og_title(og_title)
    page = _page_slug(og_url or url)

    cs = _pick_creation_story(blobs, signals)
    if cs is not None:
        item = _from_creation_story(cs, blobs, url)
        if views is not None:
            item["viewsCount"] = views
            item["videoViewCount"] = views
        log.info(
            "facebook_details_native_reel_ok",
            url=url[:120],
            post_id=item.get("postId"),
            likes=item.get("likes"),
            views=views,
        )
        return item

    story = _pick_story(blobs, signals, og_url=og_url, page=page)
    if story is not None:
        item = _from_story(story, blobs, url)
        if not item.get("text") and not item.get("media") and not item.get("short_form_video_context"):
            return None
        # Page vanity is useful for /PageName/posts/… — never for /groups/{slug}/…
        # (that slug is the group, not the author; stamping it caused author.username=group).
        is_group_url = "/groups/" in (url or "").lower()
        if page and not is_group_url:
            item["pageUsername"] = page
            user = item.get("user") if isinstance(item.get("user"), dict) else {}
            if not user.get("username"):
                user["username"] = page
                item["user"] = user
        og_image = _meta_content(html, "og:image")
        if og_image and not item.get("thumbnailUrl"):
            item["thumbnailUrl"] = og_image
        if views is not None:
            item["viewsCount"] = views
            item["videoViewCount"] = views
        log.info(
            "facebook_details_native_story_ok",
            url=url[:120],
            post_id=item.get("postId"),
            likes=item.get("likes"),
        )
        return item

    log.info("facebook_details_native_no_node", url=url[:120])
    return None
