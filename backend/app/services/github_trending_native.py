"""Scrape github.com/trending ? stars gained in a time window.

GitHub has no official Trending API. REST /search/repositories sorted by
stars returns all-time most-starred repos, not the trending page. This
module parses the public SSR HTML for rank, language, stars, forks, and
starsGained (the window metric that defines "trending").
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import httpx
import structlog

from app.utils.formatters import safe_int, safe_str, strip_empty

log = structlog.get_logger(__name__)

CREDIT_GITHUB_TRENDING_NATIVE = 2

_SINCE = {"daily", "weekly", "monthly"}
_ARTICLE_RE = re.compile(r'<article class="Box-row[^"]*"[^>]*>(.*?)</article>', re.S)
_DEV_ARTICLE_RE = re.compile(
    r'<article class="Box-row[^"]*"[^>]*id="pa-([^"]+)"[^>]*>(.*?)</article>',
    re.S,
)
_H2_HREF_RE = re.compile(r'<h2[^>]*>\s*<a[^>]+href="(/[^"]+)"', re.S)
_LANG_RE = re.compile(r'itemprop="programmingLanguage"[^>]*>([^<]+)', re.I)
_DESC_RE = re.compile(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', re.S)
_DESC_RE_FALLBACK = re.compile(r"<p[^>]*>(.*?)</p>", re.S)
_STARS_RE = re.compile(r'/stargazers"[^>]*>.*?([\d,]+)\s*</a>', re.S)
_FORKS_RE = re.compile(r'/forks"[^>]*>.*?([\d,]+)\s*</a>', re.S)
_GAINED_RE = re.compile(
    r"([\d,]+)\s+stars\s+(today|this week|this month)",
    re.I,
)
_TAG_RE = re.compile(r"<[^>]+>")


def _comma_int(raw: str | None) -> int | None:
    if not raw:
        return None
    return safe_int(raw.replace(",", ""))


def _strip_html(raw: str) -> str:
    return re.sub(r"\s+", " ", _TAG_RE.sub("", raw or "")).strip()


def parse_trending_html(html: str, *, since: str) -> list[dict[str, Any]]:
    """Parse Box-row articles from a github.com/trending HTML body."""
    out: list[dict[str, Any]] = []
    for rank, body in enumerate(_ARTICLE_RE.findall(html or ""), start=1):
        href_m = _H2_HREF_RE.search(body)
        if not href_m:
            continue
        path = href_m.group(1).strip().strip("/")
        parts = [p for p in path.split("/") if p]
        if len(parts) < 2:
            continue
        owner, name = parts[0], parts[1]
        full_name = f"{owner}/{name}"
        lang_m = _LANG_RE.search(body)
        desc_m = _DESC_RE.search(body) or _DESC_RE_FALLBACK.search(body)
        stars_m = _STARS_RE.search(body)
        forks_m = _FORKS_RE.search(body)
        gained_m = _GAINED_RE.search(body)
        row = strip_empty(
            {
                "platform": "github",
                "type": "repository",
                "rank": rank,
                "name": name,
                "fullName": full_name,
                "url": f"https://github.com/{full_name}",
                "description": _strip_html(desc_m.group(1)) if desc_m else None,
                "owner": owner,
                "ownerUrl": f"https://github.com/{owner}",
                "language": safe_str(lang_m.group(1).strip()) if lang_m else None,
                "stars": _comma_int(stars_m.group(1) if stars_m else None),
                "forks": _comma_int(forks_m.group(1) if forks_m else None),
                "starsGained": _comma_int(gained_m.group(1) if gained_m else None),
                "since": since,
            }
        )
        out.append(row)
    return out


def _trending_url(*, since: str, language: str | None) -> str:
    base = "https://github.com/trending"
    if language:
        base = f"{base}/{quote(language.strip().lower())}"
    return f"{base}?since={since}"


async def _fetch_html(url: str) -> str | None:
    """Prefer Decodo when configured; otherwise plain HTTP (SSR is enough)."""
    try:
        from app.services import decodo_fetch

        if decodo_fetch.enabled():
            got = await decodo_fetch.fetch_url(url, timeout=60.0)
            if got and got[0] == 200 and got[1]:
                return got[1]
    except Exception as exc:  # noqa: BLE001
        log.info("github_trending_decodo_fail", error=str(exc)[:160])

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        async with httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and resp.text:
            return resp.text
        log.info("github_trending_http_status", status=resp.status_code)
    except Exception as exc:  # noqa: BLE001
        log.info("github_trending_http_fail", error=str(exc)[:160])
    return None


def parse_trending_developers_html(html: str, *, since: str) -> list[dict[str, Any]]:
    """Parse github.com/trending/developers cards (not REST user search)."""
    out: list[dict[str, Any]] = []
    for rank, (login, body) in enumerate(_DEV_ARTICLE_RE.findall(html or ""), start=1):
        login_n = safe_str(login)
        if not login_n:
            continue
        name_m = re.search(r"<h1[^>]*>\s*<a[^>]*>([^<]+)</a>", body, re.S)
        avatar_m = re.search(r'<img[^>]+src="(https://avatars[^"]+)"', body)
        repos = re.findall(r'href="/([\w.-]+/[\w.-]+)"', body)
        popular = repos[0] if repos else None
        desc_m = re.search(
            r'class="f6 color-fg-muted[^"]*"[^>]*>\s*([^<]+)',
            body,
        )
        avatar = safe_str(avatar_m.group(1) if avatar_m else None)
        if avatar:
            avatar = avatar.replace("&amp;", "&")
        row = strip_empty(
            {
                "platform": "github",
                "type": "developer",
                "rank": rank,
                "login": login_n,
                "name": _strip_html(name_m.group(1)) if name_m else None,
                "url": f"https://github.com/{login_n}",
                "avatar": avatar,
                "popularRepo": popular,
                "popularRepoUrl": f"https://github.com/{popular}" if popular else None,
                "popularRepoDescription": _strip_html(desc_m.group(1)) if desc_m else None,
                "since": since,
            }
        )
        out.append(row)
    return out


async def trending_repositories_native(
    *,
    since: str = "daily",
    language: str | None = None,
    limit: int = 25,
) -> list[dict[str, Any]] | None:
    """Return trending repos from github.com/trending (not REST star search)."""
    since_n = (since or "daily").strip().lower()
    if since_n not in _SINCE:
        since_n = "daily"
    url = _trending_url(since=since_n, language=language)
    html = await _fetch_html(url)
    if not html:
        return None
    rows = parse_trending_html(html, since=since_n)
    if not rows:
        log.info("github_trending_empty", url=url)
        return None
    log.info("github_trending_ok", url=url, n=len(rows))
    return rows[: max(1, min(limit, 100))]


async def trending_developers_native(
    *,
    since: str = "daily",
    language: str | None = None,
    limit: int = 25,
) -> list[dict[str, Any]] | None:
    """Return trending developers from github.com/trending/developers."""
    since_n = (since or "daily").strip().lower()
    if since_n not in _SINCE:
        since_n = "daily"
    base = "https://github.com/trending/developers"
    if language:
        base = f"{base}/{quote(language.strip().lower())}"
    url = f"{base}?since={since_n}"
    html = await _fetch_html(url)
    if not html:
        return None
    rows = parse_trending_developers_html(html, since=since_n)
    if not rows:
        log.info("github_trending_developers_empty", url=url)
        return None
    log.info("github_trending_developers_ok", url=url, n=len(rows))
    return rows[: max(1, min(limit, 100))]
