"""Kwai public pages via Decodo HTML (schema.org JSON-LD + Nuxt SSR state). No Apify."""

from __future__ import annotations

import json
import re
from typing import Any

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(\{.*?\})</script>',
    re.S | re.I,
)
_DURATION_RE = re.compile(
    r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
    re.I,
)
_NUMERIC_USER_RE = re.compile(r"/user/(\d+)(?:/|$|\?)")
_NUXT_ASSIGN_RE = re.compile(r"(?:window\.)?__NUXT__\s*=\s*", re.I)


def _ld_blocks(html: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for match in _LD_RE.finditer(html or ""):
        raw = (match.group(1) or "").strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            out.append(data)
        elif isinstance(data, list):
            out.extend(x for x in data if isinstance(x, dict))
    return out


def _interaction_count(stats: Any, action: str) -> int | None:
    rows = stats if isinstance(stats, list) else ([stats] if isinstance(stats, dict) else [])
    needle = action.lower()
    for row in rows:
        if not isinstance(row, dict):
            continue
        itype = row.get("interactionType")
        label = ""
        if isinstance(itype, dict):
            label = str(itype.get("@type") or "")
        elif isinstance(itype, str):
            label = itype
        if needle in label.lower():
            return safe_int(row.get("userInteractionCount"))
    return None


def _duration_seconds(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    text = safe_str(value) or ""
    match = _DURATION_RE.fullmatch(text.strip())
    if not match:
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    total = hours * 3600 + minutes * 60 + seconds
    return total or None


def _thumb(value: Any) -> str | None:
    if isinstance(value, list) and value:
        return safe_str(value[0])
    return safe_str(value)


def _https(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("http://"):
        return "https://" + url[len("http://") :]
    return url


def _split_js_args(src: str) -> list[str]:
    parts: list[str] = []
    cur: list[str] = []
    in_str: str | None = None
    esc = False
    for ch in src:
        if in_str:
            cur.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            continue
        if ch in ("'", '"'):
            in_str = ch
            cur.append(ch)
            continue
        if ch == ",":
            parts.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())
    return parts


def _parse_js_literal(raw: str) -> Any:
    text = (raw or "").strip()
    if not text or text == "void 0" or text == "undefined":
        return None
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if re.fullmatch(r"-?\d+", text):
        try:
            return int(text)
        except ValueError:
            return text
    if re.fullmatch(r"-?\d+\.\d+", text):
        try:
            return float(text)
        except ValueError:
            return text
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        inner = text[1:-1]
        try:
            # JS string → JSON string (handles \u002F etc.)
            return json.loads('"' + inner.replace("\\'", "'").replace('"', '\\"') + '"')
        except json.JSONDecodeError:
            return (
                inner.encode("utf-8")
                .decode("unicode_escape", errors="replace")
                .replace("\\/", "/")
            )
    return text


def _extract_nuxt_iife(html: str) -> str | None:
    """Pull the balanced ``(function(...){...}(...))`` assigned to ``__NUXT__``."""
    match = _NUXT_ASSIGN_RE.search(html or "")
    if not match:
        return None
    i = match.end()
    while i < len(html) and html[i].isspace():
        i += 1
    if i >= len(html) or html[i] != "(":
        return None
    depth = 0
    in_str: str | None = None
    esc = False
    start = i
    for j in range(i, len(html)):
        ch = html[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            continue
        if ch in ("'", '"', "`"):
            in_str = ch
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return html[start : j + 1]
    return None


def _nuxt_env(html: str) -> tuple[str, dict[str, Any]] | None:
    body = _extract_nuxt_iife(html)
    if not body:
        return None
    body = body.strip().rstrip(";")
    iife = re.match(r"\(function\(([^)]*)\)\{([\s\S]*)\}\(([\s\S]*)\)\)$", body)
    if not iife:
        return None
    params = [p.strip() for p in iife.group(1).split(",") if p.strip()]
    args = _split_js_args(iife.group(3))
    env = {k: _parse_js_literal(v) for k, v in zip(params, args)}
    return iife.group(2), env


def _resolve_sym(env: dict[str, Any], sym: str | None) -> Any:
    if not sym:
        return None
    if sym in env:
        return env[sym]
    if re.fullmatch(r"-?\d+", sym):
        try:
            return int(sym)
        except ValueError:
            return sym
    if sym in ("true", "false", "null"):
        return _parse_js_literal(sym)
    return None


def _first_sym(body: str, *patterns: str) -> str | None:
    for pat in patterns:
        match = re.search(pat, body)
        if match:
            return match.group(1)
    return None


def _stubbish_count(value: int | None, *, public_posts: int | None) -> int | None:
    """Kwai SSR often stubs fan/follow to 1 even for large accounts — prefer null."""
    if value is None:
        return None
    if value == 1 and public_posts is not None and public_posts > 10:
        return None
    return value


def _gender(value: Any) -> str | None:
    text = safe_str(value)
    if not text:
        return None
    up = text.strip().upper()
    if up in {"U", "UNKNOWN", "N", "NONE", ""}:
        return None
    return up


def _numeric_id_from_same_as(same_as: Any) -> str | None:
    rows = same_as if isinstance(same_as, list) else ([same_as] if same_as else [])
    for row in rows:
        url = safe_str(row)
        if not url:
            continue
        match = _NUMERIC_USER_RE.search(url)
        if match:
            return match.group(1)
    return None


def _profile_from_nuxt(html: str) -> dict[str, Any] | None:
    parsed = _nuxt_env(html)
    if not parsed:
        return None
    body, env = parsed

    eid = safe_str(_resolve_sym(env, _first_sym(body, r"\beid:([A-Za-z_$][\w$]*)")))
    bio = safe_str(
        _resolve_sym(
            env,
            _first_sym(body, r"\buserText:([A-Za-z_$][\w$]*)", r"\buser_text:([A-Za-z_$][\w$]*)"),
        )
    )
    display = safe_str(
        _resolve_sym(
            env,
            _first_sym(body, r"\buser_name:([A-Za-z_$][\w$]*)", r"\buserName:([A-Za-z_$][\w$]*)"),
        )
    )
    handle = safe_str(
        _resolve_sym(
            env,
            _first_sym(body, r"\bkwai_id:([A-Za-z_$][\w$]*)", r"\bkwaiId:([A-Za-z_$][\w$]*)"),
        )
    )
    verified_raw = _resolve_sym(env, _first_sym(body, r"\bverified:([A-Za-z_$][\w$]*)"))
    verified_desc = safe_str(
        _resolve_sym(
            env,
            _first_sym(
                body,
                r"\bverified_desc:([A-Za-z_$][\w$]*)",
                r"\bverifiedDesc:([A-Za-z_$][\w$]*)",
                r"\bverifiedCopy:([A-Za-z_$][\w$]*)",
            ),
        )
    )
    verified_num = safe_int(
        _resolve_sym(
            env,
            _first_sym(body, r"\bverified_num:([A-Za-z_$][\w$]*)", r"\bverifiedNum:([A-Za-z_$][\w$]*)"),
        )
    )
    gender = _gender(_resolve_sym(env, _first_sym(body, r"\buser_sex:([A-Za-z_$][\w$]*)", r"\buserSex:([A-Za-z_$][\w$]*)")))
    user_id = safe_str(_resolve_sym(env, _first_sym(body, r"\buser_id:([A-Za-z_$][\w$]*)", r"\buserId:([A-Za-z_$][\w$]*)")))
    avatar = _https(
        safe_str(
            _resolve_sym(
                env,
                _first_sym(
                    body,
                    r"\bheadurl:([A-Za-z_$][\w$]*)",
                    r"\bheadUrl:([A-Za-z_$][\w$]*)",
                    r"\bavatar:([A-Za-z_$][\w$]*)",
                ),
            )
        )
    )
    url = _https(
        safe_str(
            _resolve_sym(
                env,
                _first_sym(body, r"\bprofileUrl:([A-Za-z_$][\w$]*)", r"\buser_profile_url:([A-Za-z_$][\w$]*)"),
            )
        )
    )
    if not url and handle:
        url = f"https://www.kwai.com/@{handle.lstrip('@')}"

    counts = re.search(
        r"fan:([A-Za-z_$][\w$]*),like:([A-Za-z_$0-9][\w$]*),photo:([A-Za-z_$][\w$]*),"
        r"follow:([A-Za-z_$][\w$]*),photo_public:([A-Za-z_$][\w$]*),"
        r"photo_private:([A-Za-z_$][\w$]*),liked:([A-Za-z_$][\w$]*)",
        body,
    )
    fan = follow = public_posts = private_posts = liked = None
    if counts:
        fan = safe_int(_resolve_sym(env, counts.group(1)))
        follow = safe_int(_resolve_sym(env, counts.group(4)))
        public_posts = safe_int(_resolve_sym(env, counts.group(5)))
        private_posts = safe_int(_resolve_sym(env, counts.group(6)))
        liked = safe_int(_resolve_sym(env, counts.group(7)))

    privacy = _resolve_sym(
        env,
        _first_sym(body, r"\bprivacy_user:([A-Za-z_$][\w$]*)", r"\bprivacyUser:([A-Za-z_$][\w$]*)"),
    )
    is_private: bool | None = None
    if privacy is not None:
        if isinstance(privacy, bool):
            is_private = privacy
        else:
            text = str(privacy).strip().lower()
            if text in {"1", "true", "yes"}:
                is_private = True
            elif text in {"0", "false", "no", '""', "''"}:
                is_private = False

    if not any((eid, handle, display, bio)):
        return None

    return {
        "id": eid,
        "eid": eid,
        "userId": user_id,
        "username": handle.lstrip("@") if handle else None,
        "name": display,
        "bio": bio,
        "url": url,
        "avatar": avatar,
        "verified": bool(verified_raw) if verified_raw is not None else None,
        "verifiedDescription": verified_desc,
        "verifiedNumber": verified_num,
        "gender": gender,
        "followersCount": _stubbish_count(fan, public_posts=public_posts),
        "followingCount": _stubbish_count(follow, public_posts=public_posts),
        "likesCount": liked,
        "videosCount": public_posts,
        "publicPostCount": public_posts,
        "privatePostCount": private_posts,
        "isPrivate": is_private,
    }


def _author_meta_from_person(person: dict[str, Any], fallback_url: str | None = None) -> dict[str, Any]:
    handle = safe_str(person.get("alternateName")) or safe_str(person.get("name"))
    url = _https(safe_str(person.get("url")) or fallback_url)
    if not url and handle:
        url = f"https://www.kwai.com/@{handle.lstrip('@')}"
    stats = person.get("interactionStatistic")
    agent = person.get("agentInteractionStatistic")
    videos = None
    if isinstance(agent, dict):
        videos = safe_int(agent.get("userInteractionCount"))
    eid = safe_str(person.get("identifier"))
    return {
        "id": eid,
        "eid": eid,
        "userId": _numeric_id_from_same_as(person.get("sameAs")),
        "username": handle.lstrip("@") if handle else None,
        "name": safe_str(person.get("name")),
        "bio": safe_str(person.get("description")),
        "url": url,
        "avatar": _https(safe_str(person.get("image"))),
        "followersCount": _interaction_count(stats, "FollowAction"),
        "likesCount": _interaction_count(stats, "LikeAction"),
        "videosCount": videos,
        "publicPostCount": videos,
    }


def _merge_profile(ld: dict[str, Any] | None, nuxt: dict[str, Any] | None) -> dict[str, Any] | None:
    if not ld and not nuxt:
        return None
    out: dict[str, Any] = {}
    for src in (ld or {}, nuxt or {}):
        for key, value in src.items():
            if value in (None, "", []):
                continue
            # Prefer LD follower/like/post counts when present (Nuxt fan/follow often stubbed).
            if key in ("followersCount", "likesCount", "videosCount", "publicPostCount") and out.get(key) not in (None, ""):
                continue
            if key in out and out[key] not in (None, "", []) and key not in (
                "bio",
                "verified",
                "verifiedDescription",
                "verifiedNumber",
                "gender",
                "followingCount",
                "privatePostCount",
                "isPrivate",
                "eid",
                "userId",
            ):
                # Keep first non-empty for identity fields; Nuxt wins for enrichment keys above via second pass.
                continue
            out[key] = value
    # Explicit enrichment: Nuxt overlays verification / privacy / following when set.
    if nuxt:
        for key in (
            "bio",
            "verified",
            "verifiedDescription",
            "verifiedNumber",
            "gender",
            "followingCount",
            "privatePostCount",
            "isPrivate",
            "eid",
            "userId",
            "avatar",
            "name",
            "username",
        ):
            if nuxt.get(key) not in (None, "", []):
                out[key] = nuxt[key]
        # Public posts: prefer Nuxt photo_public when both set (matches WriteAction usually).
        if nuxt.get("publicPostCount") is not None:
            out["publicPostCount"] = nuxt["publicPostCount"]
            out["videosCount"] = nuxt["publicPostCount"]
        if nuxt.get("likesCount") is not None and out.get("likesCount") is None:
            out["likesCount"] = nuxt["likesCount"]
        # Followers: keep LD when present; else Nuxt (already stub-filtered).
        if out.get("followersCount") is None and nuxt.get("followersCount") is not None:
            out["followersCount"] = nuxt["followersCount"]
    if out.get("id") is None and out.get("eid"):
        out["id"] = out["eid"]
    if out.get("eid") is None and out.get("id"):
        out["eid"] = out["id"]
    if not out.get("username") and not out.get("name"):
        return None
    return out


def _video_id(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"/(?:video|photo)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None


def _post_from_video_ld(video: dict[str, Any], *, profile_url: str | None = None) -> dict[str, Any] | None:
    url = safe_str(video.get("url"))
    if not url:
        return None
    creator = video.get("creator") if isinstance(video.get("creator"), dict) else {}
    person = creator.get("mainEntity") if isinstance(creator.get("mainEntity"), dict) else creator
    if not isinstance(person, dict):
        person = {}
    author = _author_meta_from_person(person, fallback_url=profile_url)
    stats = video.get("interactionStatistic")
    caption = safe_str(video.get("description"))
    if caption in (None, ".", "...", "…"):
        caption = safe_str(video.get("transcript")) or safe_str(video.get("name"))
    return {
        "id": _video_id(url),
        "url": url,
        "caption": caption,
        "transcript": safe_str(video.get("transcript")),
        "createTime": safe_str(video.get("uploadDate")),
        "duration": _duration_seconds(video.get("duration")),
        "thumb": _thumb(video.get("thumbnailUrl")),
        "playUrl": safe_str(video.get("contentUrl")),
        "viewCount": _interaction_count(stats, "WatchAction"),
        "likeCount": _interaction_count(stats, "LikeAction"),
        "commentCount": safe_int(video.get("commentCount")),
        "shareCount": _interaction_count(stats, "ShareAction"),
        "authorMeta": author,
        "status": "ok",
    }


async def _fetch_html(url: str) -> str | None:
    if not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=90.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body or len(body) < 500:
        return None
    return body


def _person_from_html(html: str) -> dict[str, Any] | None:
    for block in _ld_blocks(html):
        if block.get("@type") == "ProfilePage":
            entity = block.get("mainEntity")
            if isinstance(entity, dict) and entity.get("@type") == "Person":
                return entity
        if block.get("@type") == "Person":
            return block
    return None


async def fetch_profile(profile_url: str) -> dict[str, Any] | None:
    """Actor-shaped row with ``authorMeta`` for router ``_normalize_profile``."""
    html = await _fetch_html(profile_url)
    if not html:
        return None
    person = _person_from_html(html)
    ld = _author_meta_from_person(person, fallback_url=profile_url) if person else None
    nuxt = _profile_from_nuxt(html)
    author = _merge_profile(ld, nuxt)
    if not author:
        log.info("kwai_native_profile_empty", url=profile_url[:120])
        return None
    log.info(
        "kwai_native_profile_ok",
        username=author.get("username"),
        followers=author.get("followersCount"),
        verified=author.get("verified"),
    )
    return {"authorMeta": author, "status": "ok"}


async def fetch_user_posts(profile_url: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    """Posts from profile CollectionPage / ItemList JSON-LD."""
    if limit <= 0:
        return None
    html = await _fetch_html(profile_url)
    if not html:
        return None
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for block in _ld_blocks(html):
        if block.get("@type") == "BreadcrumbList":
            continue
        elements = block.get("itemListElement")
        if not isinstance(elements, list):
            continue
        for el in elements:
            if not isinstance(el, dict):
                continue
            # CollectionPage wraps VideoObject-like items directly.
            if el.get("@type") in ("ListItem", None) and not el.get("contentUrl") and not el.get("url"):
                continue
            row = _post_from_video_ld(el, profile_url=profile_url)
            if not row or not row.get("url"):
                continue
            key = str(row.get("id") or row["url"])
            if key in seen:
                continue
            seen.add(key)
            posts.append(row)
            if len(posts) >= limit:
                break
        if len(posts) >= limit:
            break
    if not posts:
        log.info("kwai_native_posts_empty", url=profile_url[:120])
        return None
    log.info("kwai_native_posts_ok", n=len(posts), url=profile_url[:120])
    return posts[:limit]


async def fetch_post(video_url: str) -> dict[str, Any] | None:
    """Single video page → actor-shaped post row."""
    html = await _fetch_html(video_url)
    if not html:
        return None
    for block in _ld_blocks(html):
        if block.get("@type") == "VideoObject" or block.get("contentUrl"):
            row = _post_from_video_ld(block, profile_url=None)
            if row and (row.get("playUrl") or row.get("thumb") or row.get("transcript")):
                log.info("kwai_native_post_ok", id=row.get("id"))
                return row
    log.info("kwai_native_post_empty", url=video_url[:120])
    return None
