"""Native Facebook page details via Decodo JS-rendered HTML.

Public page profiles embed page meta (category, bio, cover/profile photos)
plus intro context items (website, email). Likes/following come from
og:description / page chrome text. No Apify.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str, strip_empty

log = structlog.get_logger(__name__)

CREDIT_FB_PAGE_NATIVE = 2

_SCRIPT_RE = re.compile(r"<script[^>]*>(\{.*?\})</script>", re.S)
_META_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']([^"\']+)["\'][^>]+content=["\']([^"\']*)["\']'
    r'|<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']([^"\']+)["\']',
    re.I,
)


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
        if "__typename" not in raw and "category_name" not in raw:
            continue
        try:
            blobs.append(json.loads(raw))
        except ValueError:
            continue
    return blobs


def _metas(html: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _META_RE.finditer(html):
        if m.group(1) is not None:
            prop, content = m.group(1), m.group(2)
        else:
            content, prop = m.group(3), m.group(4)
        if prop and content and prop not in out:
            out[prop] = (
                content.replace("&amp;", "&")
                .replace("&quot;", '"')
                .replace("&#039;", "'")
            )
    return out


def _parse_count(text: str | None) -> int | None:
    if not text:
        return None
    cleaned = str(text).strip().lower().replace(",", "").replace(" ", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([kmb])?", cleaned)
    if not m:
        return safe_int(re.sub(r"[^\d]", "", str(text)))
    num = float(m.group(1))
    suf = m.group(2)
    if suf == "k":
        num *= 1_000
    elif suf == "m":
        num *= 1_000_000
    elif suf == "b":
        num *= 1_000_000_000
    return int(num)


def _counts_from_text(html: str, og_desc: str | None) -> dict[str, Any]:
    """Parse distinct page metrics. Never copy likes ↔ followers.

    Logged-out HTML typically exposes exact likes (+ talking about) in
    ``og:description``, and a separate compact followers label in page
    chrome (e.g. ``28M followers``). Treating them as one field was wrong.
    """
    og = og_desc or ""
    blob = f"{og}\n{html}"
    likes = None
    followers = None
    following = None
    talking_about = None
    followers_approximate = False

    # Prefer og:description — exact likes / talking-about when present.
    m = re.search(r"([\d,.]+)\s*likes\b", og, re.I)
    if m:
        likes = _parse_count(m.group(1))
    m = re.search(r"([\d,.]+)\s*followers\b", og, re.I)
    if m:
        followers = _parse_count(m.group(1))
    m = re.search(r"([\d,.]+)\s*talking about", og, re.I)
    if m:
        talking_about = _parse_count(m.group(1))

    # Page chrome: compact followers ("28M followers") — require a real count
    # token so CSS/JSON keys like ``.followers`` do not match.
    if followers is None:
        for pat in (
            r">([\d,.]+(?:\.\d+)?\s*[kmbKMB]?)</(?:strong|span)>\s*followers\b",
            r'"text"\s*:\s*"([\d,.]+(?:\.\d+)?\s*[kmbKMB]?)\s*followers"',
            r"(?<![\w.])([\d,.]+(?:\.\d+)?[kmbKMB])\s*followers\b",
            r"(?<![\w.])([\d,]{3,})\s*followers\b",
        ):
            m = re.search(pat, html, re.I)
            if m:
                token = m.group(1).replace(" ", "")
                followers = _parse_count(token)
                if followers is not None:
                    followers_approximate = bool(re.search(r"[kmb]$", token, re.I))
                    break

    if likes is None:
        m = re.search(r"(?:^|[^\w.])([\d,.]+)\s*likes\b", blob, re.I)
        if m:
            likes = _parse_count(m.group(1))

    m = re.search(r"(?:^|[^\w.])([\d,.]+)\s*following\b", blob, re.I)
    if m:
        following = _parse_count(m.group(1))

    if talking_about is None:
        m = re.search(r"([\d,.]+)\s*talking about", blob, re.I)
        if m:
            talking_about = _parse_count(m.group(1))

    return {
        "likes": likes,
        "followers": followers,
        "following": following,
        "talkingAbout": talking_about,
        "followersIsApproximate": True if followers_approximate and followers is not None else None,
    }


def _username_from_url(url: str) -> str | None:
    path = urlparse(url).path or ""
    parts = [p for p in path.split("/") if p]
    skip = {"pages", "people", "profile.php", "pg", "public"}
    for part in parts:
        if part.lower() in skip or part.isdigit() or part.startswith("pfbid"):
            continue
        return part
    return None


def _normalize_website(value: str | None) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if text.startswith("http://") or text.startswith("https://"):
        return text
    if "." in text and " " not in text:
        return "https://" + text.lstrip("/")
    return text


def _context_texts(blobs: list[Any]) -> dict[str, list[str]]:
    """Collect intro context item titles by renderer type."""
    out: dict[str, list[str]] = {"email": [], "website": [], "category": [], "other": []}
    nodes: list[dict[str, Any]] = []
    _walk(
        blobs,
        lambda o: isinstance(o, dict)
        and o.get("__typename")
        in (
            "WebsiteContextItemRenderer",
            "ContextItemDefaultRenderer",
            "InfluencerCategoryContextItemRenderer",
        ),
        nodes,
        limit=40,
    )
    email_re = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
    for node in nodes:
        typename = node.get("__typename")
        ctx = node.get("context_item") if isinstance(node.get("context_item"), dict) else {}
        texts: list[str] = []
        for key in ("plaintext_title", "title", "subtitle"):
            block = ctx.get(key)
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                texts.append(block["text"])
            elif isinstance(block, str):
                texts.append(block)
        for text in texts:
            if not text:
                continue
            if email_re.fullmatch(text.strip()) or email_re.search(text):
                m = email_re.search(text)
                if m:
                    out["email"].append(m.group(0))
            elif typename == "WebsiteContextItemRenderer" or re.search(
                r"\.[a-z]{2,}(/|$)", text, re.I
            ):
                out["website"].append(text.strip())
            elif typename == "InfluencerCategoryContextItemRenderer" or text.lower().startswith(
                "page"
            ):
                out["category"].append(text.strip())
            else:
                out["other"].append(text.strip())
    return out


def _page_meta(blobs: list[Any]) -> dict[str, Any] | None:
    metas: list[dict[str, Any]] = []
    _walk(
        blobs,
        lambda o: isinstance(o, dict)
        and o.get("category_name")
        and o.get("name")
        and (o.get("profile_picture_uri") or o.get("profile_picture") or o.get("cover_photo")),
        metas,
        limit=10,
    )
    return metas[0] if metas else None


def _profile_user(blobs: list[Any], page_url: str) -> dict[str, Any] | None:
    users: list[dict[str, Any]] = []
    slug = (_username_from_url(page_url) or "").lower()
    _walk(
        blobs,
        lambda o: o.get("__typename") == "User"
        and o.get("url")
        and o.get("name")
        and (not slug or slug in str(o.get("url")).lower()),
        users,
        limit=20,
    )
    if not users:
        return None
    # Prefer the richest node (cover_photo / delegate_page).
    users.sort(
        key=lambda u: (
            1 if isinstance(u.get("cover_photo"), dict) else 0,
            1 if isinstance(u.get("delegate_page"), dict) else 0,
            1 if u.get("is_additional_profile_plus") else 0,
        ),
        reverse=True,
    )
    return users[0]


def _cover_uri(node: dict[str, Any] | None) -> str | None:
    if not isinstance(node, dict):
        return None
    cover = node.get("cover_photo")
    if not isinstance(cover, dict):
        return None
    photo = cover.get("photo") if isinstance(cover.get("photo"), dict) else cover
    if isinstance(photo, dict):
        image = photo.get("image") if isinstance(photo.get("image"), dict) else {}
        return safe_str(image.get("uri")) or safe_str(photo.get("uri"))
    return None


def _profile_uri(meta: dict[str, Any] | None, user: dict[str, Any] | None) -> str | None:
    if isinstance(meta, dict):
        uri = safe_str(meta.get("profile_picture_uri"))
        if uri:
            return uri
        pic = meta.get("profile_picture")
        if isinstance(pic, dict):
            uri = safe_str(pic.get("uri"))
            if uri:
                return uri
    if isinstance(user, dict):
        for key in ("profile_picture_for_sticky_bar", "profilePicLarge", "profile_picture"):
            pic = user.get(key)
            if isinstance(pic, dict):
                uri = safe_str(pic.get("uri"))
                if uri:
                    return uri
    return None


def _verified(blobs: list[Any], ctx: dict[str, list[str]]) -> bool | None:
    # Logged-out HTML rarely exposes is_verified on the page actor; confirmed
    # owner / Page chrome is the same signal Apify's pages scraper used.
    for text in ctx.get("other") or []:
        low = text.lower()
        if "responsible for this page" in low or "confirmed owner" in low:
            return True
    for text in ctx.get("category") or []:
        if text.lower().startswith("page"):
            return True
    users: list[dict[str, Any]] = []
    _walk(
        blobs,
        lambda o: isinstance(o, dict)
        and o.get("__typename") in ("User", "Page")
        and o.get("is_verified") is not None
        and "facebook.com/" in str(o.get("url") or ""),
        users,
        limit=20,
    )
    for user in users:
        if user.get("is_verified") is True:
            return True
    return None


async def page_details_native(url: str) -> dict[str, Any] | None:
    if not url or not decodo_fetch.enabled():
        return None
    # Keep the first attempt short so missing/private pages fail fast (<5–15s)
    # instead of burning ~120s before a 404. One longer retry covers slow HTML.
    html: str | None = None
    for timeout in (12.0, 45.0):
        got = await decodo_fetch.fetch_url(url, timeout=timeout, headless="html")
        if not got:
            continue
        status, body = got
        if status == 404:
            return None
        if status != 200 or not body:
            continue
        html = body
        break
    if not html:
        return None
    # Cheap negative signals before expensive blob parse.
    low = html.lower()
    if any(
        marker in low
        for marker in (
            "content isn't available",
            "this content isn't available",
            "page isn't available",
            "page not found",
            "log in to continue",
        )
    ) and "category_name" not in html and "pageID" not in html:
        return None
    if "facebook.com" not in html and "category_name" not in html:
        return None

    blobs = _load_blobs(html)
    meta_tags = _metas(html)
    og_url = meta_tags.get("og:url") or url
    og_title = meta_tags.get("og:title")
    og_desc = meta_tags.get("og:description")
    og_image = meta_tags.get("og:image")

    page_meta = _page_meta(blobs)
    user = _profile_user(blobs, og_url)
    ctx = _context_texts(blobs)
    counts = _counts_from_text(html, og_desc)

    full_name = (
        safe_str(page_meta.get("name") if page_meta else None)
        or safe_str(user.get("name") if user else None)
        or safe_str(og_title)
    )
    username = _username_from_url(og_url) or _username_from_url(url)
    # Short display name: username when it looks like a handle, else first
    # segment of the full title before " - ".
    display_name = username
    if full_name and " - " in full_name:
        short = full_name.split(" - ", 1)[0].strip()
        if short:
            display_name = short
    display_name = display_name or full_name or username
    if not display_name:
        log.info("facebook_page_native_empty", url=url[:120])
        return None

    category = safe_str(page_meta.get("category_name") if page_meta else None)
    if not category:
        for text in ctx.get("category") or []:
            # "Page · Government organization"
            if "·" in text:
                category = text.split("·", 1)[1].strip()
                break
            category = text
            break

    bio = None
    if page_meta and isinstance(page_meta.get("best_description"), dict):
        bio = safe_str(page_meta["best_description"].get("text"))
    if not bio and og_desc:
        # Strip leading "<Name>. N likes · …" chrome from og:description.
        bio = re.sub(
            r"^.*?\d[\d,.]*\s*(?:likes|followers).*?(?:talking about this\.\s*)?",
            "",
            og_desc,
            count=1,
            flags=re.I | re.S,
        ).strip() or None

    website = None
    for text in ctx.get("website") or []:
        website = _normalize_website(text)
        if website:
            break
    email = (ctx.get("email") or [None])[0]

    profile_image = _profile_uri(page_meta, user) or og_image
    cover_image = _cover_uri(page_meta) or _cover_uri(user)

    out = {
        "platform": "facebook",
        "url": safe_str(og_url) or url,
        "username": username,
        # displayName = short brand; fullName = page title. No duplicate ``name``.
        "displayName": display_name,
        "fullName": full_name or display_name,
        "bio": bio,
        "followers": counts["followers"],
        "followersIsApproximate": counts.get("followersIsApproximate"),
        "following": counts["following"],
        "likes": counts["likes"],
        "talkingAbout": counts.get("talkingAbout"),
        "verified": _verified(blobs, ctx),
        "profileImage": profile_image,
        "coverImage": cover_image,
        "category": category,
        "website": website,
        "email": email,
        # creation date is rarely present in logged-out HTML — omit when absent
        "createdAt": None,
    }
    cleaned = strip_empty(out)
    if not cleaned.get("url") or not cleaned.get("displayName"):
        return None
    log.info(
        "facebook_page_native_ok",
        url=(cleaned.get("url") or "")[:120],
        username=cleaned.get("username"),
        likes=cleaned.get("likes"),
    )
    return cleaned
