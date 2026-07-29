"""Native LinkedIn public pages via Decodo headless HTML (no Apify).

Company / profile / post URLs hydrate enough OG + JSON-LD for basic details.
Keyword search uses Google/DDG SERP → post hydrate; Apify remains fallthrough.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from urllib.parse import quote_plus, unquote

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_int, safe_str

log = structlog.get_logger(__name__)

CREDIT_LINKEDIN_NATIVE = 1

_OG_RE = re.compile(
    r'<meta\s+(?:property|name)=["\']([^"\']+)["\']\s+content=["\']([^"\']*)["\']',
    re.I,
)
_OG_RE_ALT = re.compile(
    r'<meta\s+content=["\']([^"\']*)["\']\s+(?:property|name)=["\']([^"\']+)["\']',
    re.I,
)
_FOLLOWERS_RE = re.compile(r"([\d,.\s]+)\s+followers", re.I)
_CONNECTIONS_RE = re.compile(r"([\d,.]+)\+?\s+connections?", re.I)
_EXPERIENCE_RE = re.compile(r"Experience:\s*([^·\n|]{2,80})", re.I)
_EMPLOYEES_RE = re.compile(r"([\d,.\s]+)\s+employees", re.I)
_COMMENTS_OG_RE = re.compile(r"([\d,]+)\s+comments?", re.I)
_REACTIONS_RE = re.compile(r"([\d,.]+)\s+Reactions?", re.I)
_ACTIVITY_RE = re.compile(r"activity[:-](\d{10,25})", re.I)


def _og_map(html: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _OG_RE.finditer(html or ""):
        out[m.group(1).lower()] = unquote(m.group(2).replace("&amp;", "&"))
    for m in _OG_RE_ALT.finditer(html or ""):
        out[m.group(2).lower()] = unquote(m.group(1).replace("&amp;", "&"))
    return out


def _parse_count(raw: str | None) -> int | None:
    if not raw:
        return None
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def _ld_blocks(html: str) -> list[Any]:
    blocks: list[Any] = []
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html or "",
        re.S | re.I,
    ):
        raw = (m.group(1) or "").strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        if isinstance(data, list):
            blocks.extend(data)
        elif isinstance(data, dict) and isinstance(data.get("@graph"), list):
            blocks.extend(data["@graph"])
        else:
            blocks.append(data)
    return blocks


def _is_login_wall(html: str, og: dict[str, str]) -> bool:
    title = (og.get("og:title") or "").lower()
    if "linkedin login" in title or title in {"linkedin", "sign in"}:
        return True
    head = (html or "")[:8000].lower()
    return "authwall" in head and "og:title" not in head


async def _fetch_html(url: str) -> str | None:
    if not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=90.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body or len(body) < 2000:
        return None
    return body


def _logo_url(org: dict[str, Any]) -> str | None:
    logo = org.get("logo")
    if isinstance(logo, dict):
        return safe_str(logo.get("contentUrl") or logo.get("url"))
    return safe_str(logo)


def _unescape_html(value: str | None) -> str | None:
    if not value:
        return value
    return (
        value.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def _connections_from_text(*texts: str | None) -> int | None:
    """Parse ``8 connections`` / ``500+ connections`` from OG / page copy."""
    for text in texts:
        m = _CONNECTIONS_RE.search(text or "")
        if not m:
            continue
        n = _parse_count(m.group(1))
        if n is not None:
            return n
    return None


def _company_from_works_for(person: dict[str, Any]) -> str | None:
    wf = person.get("worksFor")
    items = wf if isinstance(wf, list) else ([wf] if isinstance(wf, dict) else [])
    for item in items:
        if not isinstance(item, dict):
            continue
        name = safe_str(item.get("name"))
        if name:
            return name.strip()
    return None


async def fetch_profile(slug: str) -> dict[str, Any] | None:
    """Public person profile → shape for ``_normalize_profile``."""
    handle = (slug or "").strip().strip("/")
    if not handle:
        return None
    url = f"https://www.linkedin.com/in/{handle}/"
    html = await _fetch_html(url)
    if not html:
        return None
    og = _og_map(html)
    if _is_login_wall(html, og):
        log.info("linkedin_native_profile_authwall", slug=handle)
        return None

    # Prefer the richest Person node — many blocks only nest a thin
    # ``author: {name, url}`` without worksFor / address / follower stats.
    person: dict[str, Any] = {}
    best_score = -1
    for block in _ld_blocks(html):
        if not isinstance(block, dict):
            continue
        candidates: list[dict[str, Any]] = []
        if block.get("@type") == "Person":
            candidates.append(block)
        author = block.get("author")
        if isinstance(author, dict) and author.get("@type") == "Person":
            candidates.append(author)
        for cand in candidates:
            score = sum(
                1
                for key in ("worksFor", "address", "interactionStatistic", "jobTitle", "description")
                if cand.get(key)
            )
            if score > best_score:
                best_score = score
                person = cand

    title = og.get("og:title") or ""
    # "Satya Nadella - Chairman and CEO at Microsoft | LinkedIn"
    name = safe_str(person.get("name"))
    headline = None
    if " | LinkedIn" in title:
        core = title.split(" | LinkedIn", 1)[0].strip()
        if " - " in core:
            left, right = core.split(" - ", 1)
            name = name or left.strip()
            headline = right.strip()
        else:
            name = name or core
    headline = _unescape_html(headline)
    about = _unescape_html(og.get("og:description") or safe_str(person.get("description")))
    followers_m = _FOLLOWERS_RE.search(about or "") or _FOLLOWERS_RE.search(html)
    # Best-effort extras from JSON-LD / title — omit when unknown (no fake data).
    location = None
    addr = person.get("address")
    if isinstance(addr, dict):
        location = safe_str(
            addr.get("addressLocality")
            or addr.get("addressRegion")
            or addr.get("addressCountry")
        )
    elif isinstance(addr, str):
        location = safe_str(addr)
    current_company = _company_from_works_for(person)
    if not current_company and headline and " at " in headline:
        current_company = safe_str(headline.rsplit(" at ", 1)[-1])
    if not current_company and about:
        exp = _EXPERIENCE_RE.search(about)
        if exp:
            current_company = safe_str(exp.group(1).strip())

    out = {
        "url": safe_str(person.get("url")) or url.rstrip("/"),
        "basic_info": {
            "profile_url": safe_str(person.get("url")) or url.rstrip("/"),
            "public_identifier": handle,
            "fullname": name,
            "headline": headline,
            "about": about,
            "location": location,
            "current_company": current_company,
            "connection_count": _connections_from_text(about, html),
            "follower_count": _parse_count(followers_m.group(1) if followers_m else None),
            "profile_picture_url": og.get("og:image"),
        },
    }
    # Prefer JSON-LD FollowAction count when the HTML "followers" scrape is tiny/wrong.
    stats = person.get("interactionStatistic")
    if isinstance(stats, dict) and "FollowAction" in str(stats.get("interactionType") or ""):
        ld_followers = safe_int(stats.get("userInteractionCount"))
        if ld_followers is not None and (
            out["basic_info"]["follower_count"] is None
            or ld_followers > (out["basic_info"]["follower_count"] or 0)
        ):
            out["basic_info"]["follower_count"] = ld_followers
    if not out["basic_info"]["fullname"]:
        return None
    log.info("linkedin_native_profile_ok", slug=handle)
    return out


async def fetch_company(slug: str) -> dict[str, Any] | None:
    """Public company page → shape for ``_normalize_company``."""
    handle = (slug or "").strip().strip("/")
    if not handle:
        return None
    url = f"https://www.linkedin.com/company/{handle}/"
    html = await _fetch_html(url)
    if not html:
        return None
    og = _og_map(html)
    if _is_login_wall(html, og):
        log.info("linkedin_native_company_authwall", slug=handle)
        return None

    org: dict[str, Any] = {}
    for block in _ld_blocks(html):
        if isinstance(block, dict) and block.get("@type") == "Organization":
            org = block
            break

    name = safe_str(org.get("name"))
    if not name and og.get("og:title"):
        name = og["og:title"].split(" | LinkedIn", 1)[0].strip()
    followers_m = _FOLLOWERS_RE.search(og.get("og:description") or "") or _FOLLOWERS_RE.search(
        html
    )
    employees = org.get("numberOfEmployees")
    employee_count = None
    if isinstance(employees, dict):
        employee_count = safe_int(employees.get("value"))
    elif employees is not None:
        employee_count = safe_int(employees)
    if employee_count is None:
        em = _EMPLOYEES_RE.search(html)
        employee_count = _parse_count(em.group(1) if em else None)

    if not name:
        return None
    industry = None
    inds = org.get("industry") or org.get("knowsAbout")
    if isinstance(inds, list) and inds:
        industry = safe_str(inds[0] if not isinstance(inds[0], dict) else inds[0].get("name"))
    elif isinstance(inds, str):
        industry = safe_str(inds)
    hq = None
    addr = org.get("address")
    if isinstance(addr, dict):
        hq = ", ".join(
            x
            for x in (
                safe_str(addr.get("addressLocality")),
                safe_str(addr.get("addressRegion")),
                safe_str(addr.get("addressCountry")),
            )
            if x
        ) or None
    out = {
        "basic_info": {
            "name": name,
            "linkedin_url": safe_str(org.get("url")) or url.rstrip("/"),
            "description": safe_str(org.get("description")) or og.get("og:description"),
            "website": safe_str(org.get("sameAs"))
            if isinstance(org.get("sameAs"), str)
            else None,
            "industry": industry,
            "industries": [industry] if industry else None,
        },
        "stats": {
            "follower_count": _parse_count(followers_m.group(1) if followers_m else None),
            "employee_count": employee_count,
        },
        "media": {
            "logo_url": _logo_url(org) or og.get("og:image"),
            "cover_url": og.get("twitter:image") if og.get("twitter:image") != og.get("og:image") else None,
        },
        "locations": {"headquarters": {"city": hq}} if hq else {},
    }
    log.info("linkedin_native_company_ok", slug=handle)
    return out


def _stats_from_interaction(block: dict[str, Any]) -> dict[str, int]:
    """Map schema.org interactionStatistic → likes / comments / shares."""
    out: dict[str, int] = {}
    stats = block.get("interactionStatistic")
    items = stats if isinstance(stats, list) else ([stats] if isinstance(stats, dict) else [])
    for item in items:
        if not isinstance(item, dict):
            continue
        itype = str(item.get("interactionType") or "")
        n = safe_int(item.get("userInteractionCount"))
        if n is None:
            continue
        if "LikeAction" in itype:
            out["likes"] = n
        elif "CommentAction" in itype:
            out["comments"] = n
        elif "ShareAction" in itype:
            out["shares"] = n
    if "comments" not in out:
        n = safe_int(block.get("commentCount"))
        if n is not None:
            out["comments"] = n
    if "comments" not in out:
        comments = block.get("comment")
        if isinstance(comments, list):
            out["comments"] = len(comments)
    return out


def _post_from_social_ld(block: dict[str, Any], *, fallback_url: str) -> dict[str, Any] | None:
    text = safe_str(block.get("articleBody") or block.get("text") or block.get("headline"))
    url = safe_str(block.get("url") or block.get("@id") or fallback_url)
    if not text and not url:
        return None
    author = block.get("author") if isinstance(block.get("author"), dict) else {}
    activity = None
    m = _ACTIVITY_RE.search(url or "")
    if m:
        activity = m.group(1)
    author_out: dict[str, Any] = {
        "name": safe_str(author.get("name")),
        "url": safe_str(author.get("url")),
    }
    # Public post LD almost never includes job title; keep when present.
    headline = safe_str(author.get("jobTitle") or author.get("description"))
    if headline:
        author_out["headline"] = headline
    return {
        "id": activity,
        "url": url,
        "text": text,
        "datePublished": safe_str(block.get("datePublished")),
        "author": author_out,
        "stats": _stats_from_interaction(block),
    }


async def fetch_post(url: str) -> dict[str, Any] | None:
    """Single post page → shape for ``_normalize_post``."""
    target = (url or "").strip()
    if "linkedin.com" not in target:
        return None
    html = await _fetch_html(target)
    if not html:
        return None
    og = _og_map(html)
    if _is_login_wall(html, og):
        log.info("linkedin_native_post_authwall", url=target[:120])
        return None

    chosen: dict[str, Any] | None = None
    for block in _ld_blocks(html):
        if not isinstance(block, dict):
            continue
        t = block.get("@type")
        types = t if isinstance(t, list) else [t]
        if any(
            x in {"SocialMediaPosting", "DiscussionForumPosting", "Article"} for x in types
        ):
            chosen = _post_from_social_ld(block, fallback_url=target)
            if chosen and chosen.get("text"):
                break
            chosen = chosen or _post_from_social_ld(block, fallback_url=target)

    if chosen is None:
        text = og.get("og:description")
        title = og.get("og:title") or ""
        if not text and not title:
            return None
        comments_m = _COMMENTS_OG_RE.search(title)
        author_name = None
        if " | " in title:
            # "July | Microsoft | 39 comments"
            parts = [p.strip() for p in title.split("|")]
            if len(parts) >= 2 and "comment" not in parts[1].lower():
                author_name = parts[1]
        chosen = {
            "url": target,
            "text": text or title.split("|", 1)[0].strip(),
            "datePublished": None,
            "author": {"name": author_name, "url": None},
            "stats": {
                "comments": _parse_count(comments_m.group(1) if comments_m else None),
            },
        }
    else:
        stats = chosen.setdefault("stats", {})
        if stats.get("comments") is None:
            comments_m = _COMMENTS_OG_RE.search(og.get("og:title") or "")
            n = _parse_count(comments_m.group(1) if comments_m else None)
            if n is not None:
                stats["comments"] = n
        if stats.get("likes") is None:
            reactions_m = _REACTIONS_RE.search(html or "")
            n = _parse_count(reactions_m.group(1) if reactions_m else None)
            if n is not None:
                stats["likes"] = n

    if not chosen.get("text"):
        return None
    log.info("linkedin_native_post_ok", url=target[:120])
    return chosen


async def fetch_company_posts(slug: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    """Company homepage JSON-LD posts (thin vs Apify; Apify remains fallthrough)."""
    handle = (slug or "").strip().strip("/")
    if not handle or limit <= 0:
        return None
    url = f"https://www.linkedin.com/company/{handle}/"
    html = await _fetch_html(url)
    if not html:
        return None
    og = _og_map(html)
    if _is_login_wall(html, og):
        return None

    posts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for block in _ld_blocks(html):
        if not isinstance(block, dict):
            continue
        if block.get("@type") != "DiscussionForumPosting":
            continue
        row = _post_from_social_ld(block, fallback_url=url)
        if not row or not row.get("text"):
            continue
        key = row.get("url") or row.get("text")
        if not key or key in seen:
            continue
        seen.add(key)
        posts.append(row)
        if len(posts) >= limit:
            break

    if not posts:
        log.info("linkedin_native_company_posts_empty", slug=handle)
        return None
    log.info("linkedin_native_company_posts_ok", slug=handle, n=len(posts))
    return posts



def _post_urls_from_serp_html(html: str, *, limit: int = 40) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for url in re.findall(
        r"https://(?:www\.)?linkedin\.com/posts/[A-Za-z0-9_%\-.]+",
        html or "",
        re.I,
    ):
        clean = url.split("?")[0].rstrip(").,;'\"")
        if clean in seen:
            continue
        if "activity" not in clean.lower():
            continue
        seen.add(clean)
        urls.append(clean)
        if len(urls) >= limit:
            break
    return urls


async def _search_post_urls_via_serp(
    q: str, *, sort: str = "relevance", limit: int = 40
) -> list[str]:
    """Google + DuckDuckGo site:linkedin.com/posts → post URLs."""
    if not decodo_fetch.enabled():
        return []
    query = quote_plus(f"site:linkedin.com/posts {q}")
    sources = [
        f"https://www.google.com/search?q={query}&num={min(30, max(10, limit))}"
        + ("&tbs=sbd:1" if sort == "date" else ""),
        f"https://html.duckduckgo.com/html/?q={query}",
    ]
    seen: set[str] = set()
    urls: list[str] = []
    for url in sources:
        got = await decodo_fetch.fetch_url(url, timeout=90.0, headless="html")
        if not got:
            continue
        status, body = got
        if status != 200 or not body:
            continue
        for post_url in _post_urls_from_serp_html(body, limit=limit):
            if post_url in seen:
                continue
            seen.add(post_url)
            urls.append(post_url)
            if len(urls) >= limit:
                break
        if len(urls) >= min(8, limit):
            break
    log.info("linkedin_native_search_serp", q=q[:80], n=len(urls), sort=sort)
    return urls


async def search_posts(
    q: str, *, sort: str = "relevance", limit: int = 20
) -> list[dict[str, Any]] | None:
    """Keyword post search via SERP → Decodo post hydrate.

    LinkedIn's own content search is auth-walled logged-out.
    """
    query = (q or "").strip()
    if len(query) < 2 or limit <= 0:
        return None
    sort_key = "date" if (sort or "").lower() == "date" else "relevance"
    urls = await _search_post_urls_via_serp(
        query, sort=sort_key, limit=min(40, max(15, limit * 2))
    )
    if not urls:
        return None

    sem = asyncio.Semaphore(3)
    selected = urls[: max(limit * 2, limit + 5)]

    async def _one(post_url: str) -> dict[str, Any] | None:
        async with sem:
            return await fetch_post(post_url)

    rows = await asyncio.gather(*[_one(u) for u in selected])
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not row or not row.get("text"):
            continue
        key = safe_str(row.get("url") or row.get("id") or row.get("text"))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(row)
        if len(out) >= limit:
            break
    if not out:
        log.info("linkedin_native_search_empty", q=query[:80])
        return None
    log.info("linkedin_native_search_ok", q=query[:80], n=len(out), sort=sort_key)
    return out
