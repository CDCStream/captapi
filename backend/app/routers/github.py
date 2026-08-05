"""GitHub public data endpoints.

Uses GitHub's public REST API directly. No Apify actor is needed for this
platform, which keeps these endpoints fast and cheap.
"""

from __future__ import annotations

import asyncio
import base64
import json
import math
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.cached_runner import cached_or_run
from app.services import github_contributions_native, github_trending_native
from app.utils.formatters import safe_int, safe_str, strip_empty

router = APIRouter()

GITHUB_API = "https://api.github.com"
# Full repo / PR / activity rows (rich objects).
GITHUB_LIST_RATE = 0.4
# Sparse follower/following cards (id/login/type/url/avatar) — match Bluesky list unit price.
GITHUB_GRAPH_RATE = 0.1
GITHUB_SEARCH_RATE = 0.6
# GitHub caps /users/{u}/events/public at 90 events (also ~90 days).
GITHUB_PUBLIC_EVENTS_CEILING = 90
CREDIT_REPOSITORY = 1
CREDIT_TRENDING_REPOS = github_trending_native.CREDIT_GITHUB_TRENDING_NATIVE
CREDIT_TRENDING_DEVS = github_trending_native.CREDIT_GITHUB_TRENDING_NATIVE
CREDIT_CONTRIBUTIONS = github_contributions_native.CREDIT_GITHUB_CONTRIBUTIONS_NATIVE

_LINK_NEXT_RE = re.compile(r"<([^>]+)>;\s*rel=\"next\"", re.I)


def _scaled(limit: int, rate: float, minimum: int = 3) -> int:
    if limit <= 0:
        return 0
    return max(minimum, math.ceil(limit * rate))


def _repo_parts(value: str) -> tuple[str, str] | None:
    value = (value or "").strip().rstrip("/")
    if "github.com/" in value:
        value = value.split("github.com/", 1)[1]
    parts = [p for p in value.split("/") if p]
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def _username(value: str) -> str | None:
    value = (value or "").strip().rstrip("/")
    if "github.com/" in value:
        value = value.split("github.com/", 1)[1]
    value = value.strip("/")
    if not value or "/" in value:
        return None
    return value


def _gh_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Captapi/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = get_settings().GITHUB_TOKEN
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _get_response(
    path: str, params: dict[str, Any] | None = None
) -> tuple[Any, str | None]:
    """GET GitHub REST; return (json_body, Link header)."""
    # follow_redirects: GitHub 301s renamed/transferred repos (e.g.
    # facebook/react) and returns a JSON stub instead of the data otherwise.
    async with httpx.AsyncClient(timeout=30, headers=_gh_headers(), follow_redirects=True) as client:
        resp = await client.get(f"{GITHUB_API}{path}", params=params)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Not found on GitHub")
    if resp.status_code == 403:
        raise HTTPException(status_code=429, detail="GitHub public API rate limit reached")
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail="GitHub API error")
    return resp.json(), resp.headers.get("Link")


async def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    body, _link = await _get_response(path, params)
    return body


async def _get_list(
    path: str, params: dict[str, Any] | None = None
) -> tuple[list[dict[str, Any]], str | None]:
    """Like ``_get`` but guarantees a list + Link header for pagination."""
    payload, link = await _get_response(path, params)
    if isinstance(payload, list):
        return payload, link
    message = str(payload.get("message", "")) if isinstance(payload, dict) else ""
    if "rate limit" in message.lower():
        raise HTTPException(status_code=429, detail="GitHub public API rate limit reached")
    raise HTTPException(status_code=502, detail="GitHub API returned an unexpected payload")


def _encode_page_cursor(page: int, *, kind: str) -> str:
    """Opaque base64url cursor wrapping GitHub's page= (not a bare \"2\")."""
    raw = json.dumps({"v": 1, "k": kind, "p": page}, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_page_cursor(cursor: str | None, *, kind: str) -> int:
    if cursor is None or cursor == "":
        return 1
    # Legacy bare page numbers still accepted for one release.
    if str(cursor).isdigit() and int(cursor) >= 1:
        return int(cursor)
    pad = "=" * (-len(cursor) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor + pad).decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        ) from None
    if not isinstance(data, dict) or data.get("v") != 1 or data.get("k") != kind:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    page = data.get("p")
    if not isinstance(page, int) or page < 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor. Pass the nextCursor value from a previous response.",
        )
    return page


def _next_page_from_link(link: str | None) -> int | None:
    """Parse ``rel=\"next\"`` page from GitHub's Link header."""
    if not link:
        return None
    m = _LINK_NEXT_RE.search(link)
    if not m:
        return None
    q = parse_qs(urlparse(m.group(1)).query)
    pages = q.get("page") or []
    if pages and str(pages[0]).isdigit() and int(pages[0]) >= 1:
        return int(pages[0])
    return None


def _page_cursor(cursor: str | None) -> int:
    """Legacy helper — prefer ``_decode_page_cursor`` with a kind."""
    return _decode_page_cursor(cursor, kind="page")


def _user(u: dict[str, Any]) -> dict[str, Any]:
    """Normalize GitHub /users/{login} into Captapi camelCase.

    Mirrors the public REST payload. ``type`` keeps GitHub's casing
    (``User`` | ``Organization``). ``email`` is only set when the account made
    it public — omitted when null (not a private-email leak).
    """
    from app.utils.formatters import strip_empty

    raw_type = safe_str(u.get("type")) or "User"
    # Preserve User vs Organization — never force lowercase "user".
    if raw_type.lower() == "organization":
        gh_type = "Organization"
    else:
        gh_type = "User"
    hireable = u.get("hireable")
    if not isinstance(hireable, bool):
        hireable = None
    site_admin = u.get("site_admin")
    if not isinstance(site_admin, bool):
        site_admin = None
    return strip_empty(
        {
            "platform": "github",
            "type": gh_type,
            "login": safe_str(u.get("login")),
            "id": safe_int(u.get("id")),
            "nodeId": safe_str(u.get("node_id")),
            "url": safe_str(u.get("html_url")),
            "apiUrl": safe_str(u.get("url")),
            "name": safe_str(u.get("name")),
            "company": safe_str(u.get("company")),
            "blog": safe_str(u.get("blog")),
            "location": safe_str(u.get("location")),
            "email": safe_str(u.get("email")),
            "bio": safe_str(u.get("bio")),
            "avatar": safe_str(u.get("avatar_url")),
            "publicRepos": safe_int(u.get("public_repos")),
            "publicGists": safe_int(u.get("public_gists")),
            "followers": safe_int(u.get("followers")),
            "following": safe_int(u.get("following")),
            "twitterUsername": safe_str(u.get("twitter_username")),
            "hireable": hireable,
            "siteAdmin": site_admin,
            "createdAt": safe_str(u.get("created_at")),
            "updatedAt": safe_str(u.get("updated_at")),
        }
    )


def _license_fields(r: dict[str, Any]) -> tuple[str | None, str | None]:
    """SPDX id + human name. NOASSERTION/NONE → null SPDX (keep licenseName)."""
    lic = r.get("license") if isinstance(r.get("license"), dict) else None
    if not lic:
        return None, None
    spdx = safe_str(lic.get("spdx_id"))
    name = safe_str(lic.get("name"))
    if spdx in ("NOASSERTION", "NONE"):
        spdx = None
    return spdx, name


def _repo(r: dict[str, Any]) -> dict[str, Any]:
    """Normalize a GitHub repository object.

    ``watchers`` is ``subscribers_count`` (people watching for notifications).
    Never use REST ``watchers_count`` — that is a legacy alias of stargazers.
    List/search payloads omit subscribers_count; watchers is then omitted.
    ``openIssuesAndPrs`` is GitHub's open_issues_count (issues + open PRs).
    """
    owner = r.get("owner") or {}
    license_spdx, license_name = _license_fields(r)
    parent = r.get("parent") if isinstance(r.get("parent"), dict) else None
    # Only trust subscribers_count when the key is present (detail endpoint).
    watchers = safe_int(r["subscribers_count"]) if "subscribers_count" in r else None
    owner_type_raw = safe_str(owner.get("type"))
    if owner_type_raw and owner_type_raw.lower() == "organization":
        owner_type = "Organization"
    elif owner_type_raw:
        owner_type = "User"
    else:
        owner_type = None
    return strip_empty(
        {
            "platform": "github",
            "type": "repository",
            "name": safe_str(r.get("name")),
            "fullName": safe_str(r.get("full_name")),
            "url": safe_str(r.get("html_url")),
            "description": safe_str(r.get("description")),
            "owner": safe_str(owner.get("login")),
            "ownerUrl": safe_str(owner.get("html_url")),
            "ownerType": owner_type,
            "ownerAvatar": safe_str(owner.get("avatar_url")),
            "language": safe_str(r.get("language")),
            "stars": safe_int(r.get("stargazers_count")),
            "forks": safe_int(r.get("forks_count")),
            "watchers": watchers,
            "openIssuesAndPrs": safe_int(r.get("open_issues_count")),
            "defaultBranch": safe_str(r.get("default_branch")),
            "homepage": safe_str(r.get("homepage")),
            "license": license_spdx,
            "licenseName": license_name,
            "topics": [t for t in (r.get("topics") or []) if isinstance(t, str)],
            "isFork": bool(r.get("fork")),
            "parent": safe_str(parent.get("full_name")) if parent else None,
            "isArchived": bool(r.get("archived")),
            "size": safe_int(r.get("size")) if r.get("size") is not None else None,
            "visibility": safe_str(r.get("visibility")),
            "hasIssues": bool(r["has_issues"]) if "has_issues" in r else None,
            "hasDiscussions": bool(r["has_discussions"]) if "has_discussions" in r else None,
            "pushedAt": safe_str(r.get("pushed_at")),
            "createdAt": safe_str(r.get("created_at")),
            "updatedAt": safe_str(r.get("updated_at")),
        }
    )


def _account_type(raw: Any) -> str | None:
    """Normalize GitHub account type to User | Organization."""
    t = safe_str(raw)
    if not t:
        return None
    low = t.lower()
    if low == "organization":
        return "Organization"
    if low == "user":
        return "User"
    return t


def _gh_user_card(u: dict[str, Any] | None) -> dict[str, Any] | None:
    """Compact account card for followers/following/PR author rows."""
    if not isinstance(u, dict):
        return None
    login = safe_str(u.get("login"))
    if not login:
        return None
    return strip_empty(
        {
            "id": safe_int(u.get("id")),
            "login": login,
            "type": _account_type(u.get("type")),
            "url": safe_str(u.get("html_url")) or f"https://github.com/{login}",
            "avatar": safe_str(u.get("avatar_url")),
        }
    )


def _event_payload(etype: str | None, payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize GitHub event ``payload`` by type — not just the type name."""
    if not isinstance(payload, dict):
        return None
    et = etype or ""
    if et == "PushEvent":
        commits = []
        for c in payload.get("commits") or []:
            if not isinstance(c, dict):
                continue
            author = c.get("author") if isinstance(c.get("author"), dict) else {}
            commits.append(
                strip_empty(
                    {
                        "sha": safe_str(c.get("sha")),
                        "message": safe_str(c.get("message")),
                        "authorName": safe_str(author.get("name")),
                        "authorEmail": safe_str(author.get("email")),
                        "distinct": bool(c.get("distinct")) if "distinct" in c else None,
                    }
                )
            )
        return strip_empty(
            {
                "ref": safe_str(payload.get("ref")),
                "head": safe_str(payload.get("head")),
                "before": safe_str(payload.get("before")),
                "size": safe_int(payload.get("size")),
                "distinctSize": safe_int(payload.get("distinct_size")),
                "commits": commits or None,
            }
        )
    if et == "PullRequestEvent":
        pr = payload.get("pull_request") if isinstance(payload.get("pull_request"), dict) else {}
        return strip_empty(
            {
                "action": safe_str(payload.get("action")),
                "number": safe_int(pr.get("number")),
                "title": safe_str(pr.get("title")),
                "url": safe_str(pr.get("html_url")),
                "state": safe_str(pr.get("state")),
                "draft": bool(pr["draft"]) if isinstance(pr.get("draft"), bool) else None,
                "merged": bool(pr["merged"]) if isinstance(pr.get("merged"), bool) else None,
            }
        )
    if et == "IssuesEvent":
        issue = payload.get("issue") if isinstance(payload.get("issue"), dict) else {}
        return strip_empty(
            {
                "action": safe_str(payload.get("action")),
                "number": safe_int(issue.get("number")),
                "title": safe_str(issue.get("title")),
                "url": safe_str(issue.get("html_url")),
                "state": safe_str(issue.get("state")),
            }
        )
    if et in ("IssueCommentEvent", "PullRequestReviewCommentEvent", "CommitCommentEvent"):
        return strip_empty({"action": safe_str(payload.get("action"))})
    if et == "CreateEvent" or et == "DeleteEvent":
        return strip_empty(
            {
                "ref": safe_str(payload.get("ref")),
                "refType": safe_str(payload.get("ref_type")),
            }
        )
    if et == "WatchEvent" or et == "ForkEvent" or et == "PublicEvent":
        return strip_empty({"action": safe_str(payload.get("action"))})
    # Fallback: surface action when present so callers still get something.
    action = safe_str(payload.get("action"))
    return {"action": action} if action else None


def _event(e: dict[str, Any]) -> dict[str, Any]:
    """Normalize a public event. ``actor`` omitted — same as the username query."""
    repo = e.get("repo") or {}
    etype = safe_str(e.get("type"))
    payload = _event_payload(etype, e.get("payload") if isinstance(e.get("payload"), dict) else None)
    return strip_empty(
        {
            "id": safe_str(e.get("id")),
            "type": etype,
            "repo": safe_str(repo.get("name")),
            "repoUrl": (
                f"https://github.com/{safe_str(repo.get('name'))}"
                if safe_str(repo.get("name"))
                else None
            ),
            "payload": payload,
            "createdAt": safe_str(e.get("created_at")),
            "public": bool(e["public"]) if isinstance(e.get("public"), bool) else None,
        }
    )


def _pull(p: dict[str, Any]) -> dict[str, Any]:
    user = p.get("user") if isinstance(p.get("user"), dict) else {}
    head = p.get("head") if isinstance(p.get("head"), dict) else {}
    base = p.get("base") if isinstance(p.get("base"), dict) else {}
    labels = []
    for lab in p.get("labels") or []:
        if isinstance(lab, dict) and safe_str(lab.get("name")):
            labels.append(
                strip_empty(
                    {
                        "name": safe_str(lab.get("name")),
                        "color": safe_str(lab.get("color")),
                        "description": safe_str(lab.get("description")),
                    }
                )
            )
    reviewers = [
        c
        for c in (
            _gh_user_card(u) for u in (p.get("requested_reviewers") or []) if isinstance(u, dict)
        )
        if c
    ]
    assignees = [
        c
        for c in (_gh_user_card(u) for u in (p.get("assignees") or []) if isinstance(u, dict))
        if c
    ]
    return strip_empty(
        {
            "id": safe_int(p.get("id")),
            "number": safe_int(p.get("number")),
            "title": safe_str(p.get("title")),
            "state": safe_str(p.get("state")),
            "draft": bool(p["draft"]) if isinstance(p.get("draft"), bool) else None,
            "url": safe_str(p.get("html_url")),
            "author": _gh_user_card(user),
            "labels": labels or None,
            "assignees": assignees or None,
            "requestedReviewers": reviewers or None,
            "head": strip_empty(
                {
                    "ref": safe_str(head.get("ref")),
                    "sha": safe_str(head.get("sha")),
                    "label": safe_str(head.get("label")),
                }
            )
            or None,
            "base": strip_empty(
                {
                    "ref": safe_str(base.get("ref")),
                    "sha": safe_str(base.get("sha")),
                    "label": safe_str(base.get("label")),
                }
            )
            or None,
            "createdAt": safe_str(p.get("created_at")),
            "updatedAt": safe_str(p.get("updated_at")),
            "closedAt": safe_str(p.get("closed_at")),
            "mergedAt": safe_str(p.get("merged_at")),
        }
    )


CREDIT_USER = 1


@router.get(
    "/user",
    summary="GitHub user profile",
    description=(
        "Public profile from GitHub's REST /users/{username} API as clean camelCase JSON "
        "(login, name, email when public, bio, followers, repos, twitterUsername, …). "
        "Flat 1 credit. The same payload is available free from api.github.com with a "
        "personal access token (5,000 req/hour) — use Captapi when you want one key and "
        "the same shape as other platforms; call GitHub directly for GitHub-only workloads."
    ),
)
async def github_user(
    username: str = Query(..., description="GitHub username or profile URL"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    async with billed_call(
        caller=caller,
        endpoint="/v1/github/user",
        platform="github",
        resource_url=f"https://github.com/{login}",
        base_credits=CREDIT_USER,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            ctx["source"] = "direct"
            return _user(await _get(f"/users/{login}"))

        return ApiResponse(
            data=await cached_or_run(
                "github.user",
                {"login": login, "v": 5},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get(
    "/repositories",
    summary="List a GitHub user's repositories (cursor-paginated)",
    description=(
        "List repos from GitHub REST /users/{login}/repos. Supports sort="
        "created|updated|pushed|full_name (default updated), direction=asc|desc, "
        "and type=owner|member|all — all echoed in the response. Opaque nextCursor "
        "from the Link header. parent is omitted on this list (GitHub's list payload "
        "has no parent object) — call github/repository for fork upstream. watchers "
        "omitted here (no subscribers_count). ~0.4 credits/repo (min 3)."
    ),
)
async def repositories(
    username: str = Query(..., description="GitHub username or profile URL"),
    sort: str = Query(
        "updated",
        pattern="^(created|updated|pushed|full_name)$",
        description="created | updated | pushed | full_name. Not stars — GitHub's user-repos API has no stars sort.",
    ),
    direction: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Sort direction. Default desc.",
    ),
    repo_type: str = Query(
        "owner",
        pattern="^(all|owner|member)$",
        description="owner (default) | member | all — affiliation filter from GitHub.",
        alias="type",
    ),
    limit: int = Query(30, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor from a previous nextCursor (wraps GitHub Link page=). "
            "Leave empty for the first page."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    page = _decode_page_cursor(cursor, kind="repos")
    async with billed_call(caller=caller, endpoint="/v1/github/repositories", platform="github", resource_url=f"https://github.com/{login}", base_credits=_scaled(limit, GITHUB_LIST_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items, link = await _get_list(
                f"/users/{login}/repos",
                {
                    "per_page": limit,
                    "page": page,
                    "sort": sort,
                    "direction": direction,
                    "type": repo_type,
                },
            )
            repos = [_repo(i) for i in items[:limit]]
            next_page = _next_page_from_link(link)
            next_cursor = (
                _encode_page_cursor(next_page, kind="repos") if next_page is not None else None
            )
            return {
                "username": login,
                "sort": sort,
                "direction": direction,
                "type": repo_type,
                "totalReturned": len(repos),
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "repositories": repos,
            }

        data = await cached_or_run(
            "github.repositories",
            {
                "login": login,
                "sort": sort,
                "direction": direction,
                "type": repo_type,
                "limit": limit,
                "cursor": cursor or "",
                "v": 6,
            },
            _run,
            ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["repositories"]), GITHUB_LIST_RATE)
        return ApiResponse(data=data)


@router.get(
    "/repository",
    summary="GitHub repository details",
    description=(
        "Public repository metadata from GitHub REST /repos/{owner}/{repo} as camelCase JSON: "
        "stars, forks, watchers (subscribers_count — not the legacy watchers_count star alias), "
        "openIssuesAndPrs (issues + open PRs), license/licenseName (NOASSERTION → null SPDX), "
        "parent when isFork, size, visibility, hasIssues/hasDiscussions, ownerType. Flat 1 credit."
    ),
)
async def repository(
    repo: str = Query(..., description="Repository URL or owner/name"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    parts = _repo_parts(repo)
    if not parts:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository")
    owner, name = parts
    async with billed_call(
        caller=caller,
        endpoint="/v1/github/repository",
        platform="github",
        resource_url=f"https://github.com/{owner}/{name}",
        base_credits=CREDIT_REPOSITORY,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            ctx["source"] = "direct"
            return _repo(await _get(f"/repos/{owner}/{name}"))

        return ApiResponse(
            data=await cached_or_run(
                "github.repository",
                {"owner": owner, "name": name, "v": 3},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get(
    "/pull-requests",
    summary="List repository pull requests (cursor-paginated)",
    description=(
        "List PRs from GitHub REST /repos/{owner}/{repo}/pulls. Default state=open "
        "(pass state=closed|all to override — echoed in the response). Each row includes "
        "draft, labels, author{id,login,avatar,url}, head/base, assignees, "
        "requestedReviewers, closedAt/mergedAt. Opaque nextCursor from GitHub's Link header "
        "(not a bare page number)."
    ),
)
async def pull_requests(
    repo: str = Query(..., description="Repository URL or owner/name"),
    state: str = Query(
        "open",
        pattern="^(open|closed|all)$",
        description="open (default), closed, or all. Echoed as data.state.",
    ),
    limit: int = Query(30, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor from a previous nextCursor (wraps GitHub Link page=). "
            "Leave empty for the first page."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    parts = _repo_parts(repo)
    if not parts:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository")
    owner, name = parts
    page = _decode_page_cursor(cursor, kind="pulls")
    async with billed_call(caller=caller, endpoint="/v1/github/pull-requests", platform="github", resource_url=f"https://github.com/{owner}/{name}", base_credits=_scaled(limit, GITHUB_LIST_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items, link = await _get_list(
                f"/repos/{owner}/{name}/pulls",
                {"state": state, "per_page": limit, "page": page},
            )
            pulls = [_pull(i) for i in items[:limit]]
            next_page = _next_page_from_link(link)
            next_cursor = (
                _encode_page_cursor(next_page, kind="pulls") if next_page is not None else None
            )
            return {
                "repository": f"{owner}/{name}",
                "state": state,
                "totalReturned": len(pulls),
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "pullRequests": pulls,
            }

        data = await cached_or_run(
            "github.pull-requests",
            {"repo": f"{owner}/{name}", "state": state, "limit": limit, "cursor": cursor or "", "v": 4},
            _run,
            ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["pullRequests"]), GITHUB_LIST_RATE)
        return ApiResponse(data=data)


@router.get(
    "/activity",
    summary="GitHub user public activity (cursor-paginated)",
    description=(
        f"Recent public events from /users/{{login}}/events/public with normalized "
        f"payload per type (PushEvent commits/ref/size, PullRequestEvent action+PR, "
        f"IssuesEvent action+issue, …). GitHub caps this feed at "
        f"{GITHUB_PUBLIC_EVENTS_CEILING} events (also ~90 days) — eventCeiling is echoed "
        f"and hasMore stops at that limit. Opaque nextCursor from the Link header. "
        f"Actor is omitted (identical to username on this endpoint)."
    ),
)
async def activity(
    username: str = Query(..., description="GitHub username or profile URL, e.g. getify"),
    limit: int = Query(
        30,
        ge=1,
        le=GITHUB_PUBLIC_EVENTS_CEILING,
        description=f"Max events per page (1–{GITHUB_PUBLIC_EVENTS_CEILING}; upstream ceiling).",
    ),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor from a previous nextCursor. Leave empty for the first page. "
            f"Pagination stops after {GITHUB_PUBLIC_EVENTS_CEILING} events."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    page = _decode_page_cursor(cursor, kind="activity")
    # Refuse pages that start past the upstream ceiling.
    if (page - 1) * limit >= GITHUB_PUBLIC_EVENTS_CEILING:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cursor past GitHub's {GITHUB_PUBLIC_EVENTS_CEILING}-event public activity ceiling."
            ),
        )
    async with billed_call(caller=caller, endpoint="/v1/github/activity", platform="github", resource_url=f"https://github.com/{login}", base_credits=_scaled(limit, GITHUB_LIST_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            # Clamp page size so we never request past the ceiling.
            remaining = GITHUB_PUBLIC_EVENTS_CEILING - (page - 1) * limit
            per_page = max(1, min(limit, remaining))
            items, link = await _get_list(
                f"/users/{login}/events/public",
                {"per_page": per_page, "page": page},
            )
            events = [_event(i) for i in items[:per_page]]
            served = (page - 1) * limit + len(events)
            next_page = _next_page_from_link(link)
            if next_page is not None and served < GITHUB_PUBLIC_EVENTS_CEILING:
                next_cursor = _encode_page_cursor(next_page, kind="activity")
            else:
                next_cursor = None
            return {
                "username": login,
                "eventCeiling": GITHUB_PUBLIC_EVENTS_CEILING,
                "totalReturned": len(events),
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "events": events,
            }

        data = await cached_or_run(
            "github.activity",
            {"login": login, "limit": limit, "cursor": cursor or "", "v": 4},
            _run,
            ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["events"]), GITHUB_LIST_RATE)
        return ApiResponse(data=data)


@router.get(
    "/followers",
    summary="List GitHub followers (cursor-paginated)",
    description=(
        "Followers from /users/{login}/followers as {id, login, type, url, avatar}. "
        "~0.1 credits/row (min 3). Opaque Link cursor. No sampling parameter — paging a "
        "mega-account (e.g. ~250k followers) costs ~25k credits at this rate; for full "
        "archives call api.github.com directly. type is User or Organization."
    ),
)
async def followers(
    username: str = Query(..., description="GitHub username or profile URL"),
    limit: int = Query(30, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor from a previous nextCursor (wraps GitHub Link page=). "
            "Leave empty for the first page."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    page = _decode_page_cursor(cursor, kind="followers")
    async with billed_call(caller=caller, endpoint="/v1/github/followers", platform="github", resource_url=f"https://github.com/{login}", base_credits=_scaled(limit, GITHUB_GRAPH_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items, link = await _get_list(
                f"/users/{login}/followers", {"per_page": limit, "page": page}
            )
            users = [c for c in (_gh_user_card(i) for i in items[:limit]) if c]
            next_page = _next_page_from_link(link)
            next_cursor = (
                _encode_page_cursor(next_page, kind="followers") if next_page is not None else None
            )
            return {
                "username": login,
                "totalReturned": len(users),
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "followers": users,
            }

        data = await cached_or_run(
            "github.followers",
            {"login": login, "limit": limit, "cursor": cursor or "", "v": 5},
            _run,
            ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["followers"]), GITHUB_GRAPH_RATE)
        return ApiResponse(data=data)


@router.get(
    "/following",
    summary="List accounts a GitHub user follows (cursor-paginated)",
    description=(
        "Same shape and pricing as github/followers — /users/{login}/following as "
        "{id, login, type, url, avatar}. ~0.1 credits/row (min 3). Opaque Link cursor. "
        "No sampling parameter; large following lists are expensive to page fully."
    ),
)
async def following(
    username: str = Query(..., description="GitHub username or profile URL"),
    limit: int = Query(30, ge=1, le=100),
    cursor: str | None = Query(
        None,
        description=(
            "Opaque pagination cursor from a previous nextCursor (wraps GitHub Link page=). "
            "Leave empty for the first page."
        ),
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    page = _decode_page_cursor(cursor, kind="following")
    async with billed_call(caller=caller, endpoint="/v1/github/following", platform="github", resource_url=f"https://github.com/{login}", base_credits=_scaled(limit, GITHUB_GRAPH_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items, link = await _get_list(
                f"/users/{login}/following", {"per_page": limit, "page": page}
            )
            users = [c for c in (_gh_user_card(i) for i in items[:limit]) if c]
            next_page = _next_page_from_link(link)
            next_cursor = (
                _encode_page_cursor(next_page, kind="following") if next_page is not None else None
            )
            return {
                "username": login,
                "totalReturned": len(users),
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "following": users,
            }

        data = await cached_or_run(
            "github.following",
            {"login": login, "limit": limit, "cursor": cursor or "", "v": 5},
            _run,
            ctx,
            use_cache=cache,
        )
        ctx["credits_override"] = _scaled(len(data["following"]), GITHUB_GRAPH_RATE)
        return ApiResponse(data=data)


@router.get(
    "/contributions",
    summary="GitHub contribution graph",
    description=(
        "Last-year contribution calendar from github.com/users/{login}/contributions — "
        "totalContributions, from/to, currentStreak, and days[{date,count,level}]. "
        "This is the heatmap graph, not /users/{u}/events/public (that feed caps at 90 "
        "events / 90 days and is not a contribution metric). Flat 2 credits."
    ),
)
async def contributions(
    username: str = Query(..., description="GitHub username or profile URL, e.g. getify"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    async with billed_call(
        caller=caller,
        endpoint="/v1/github/contributions",
        platform="github",
        resource_url=f"https://github.com/{login}",
        base_credits=CREDIT_CONTRIBUTIONS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            data = await github_contributions_native.contributions_native(login)
            if not data:
                raise HTTPException(status_code=404, detail="Contribution calendar not found")
            ctx["source"] = data.get("source") or "github.com/users/.../contributions"
            return data

        return ApiResponse(
            data=await cached_or_run(
                "github.contributions",
                {"login": login, "v": 3},
                _run,
                ctx,
                use_cache=cache,
            )
        )


@router.get(
    "/trending-repositories",
    summary="GitHub trending repositories",
    description=(
        "Repos from github.com/trending ranked by stars gained in a window "
        "(since=daily|weekly|monthly) — not REST /search/repositories sorted by "
        "all-time stars. Each row includes starsGained and source "
        '"github.com/trending". Optional language slug (e.g. python). Flat 2 credits. '
        "The HTML page typically lists ~25 repos (no cursor; not the Search API 1000 cap)."
    ),
)
async def trending_repositories(
    since: str = Query(
        "daily",
        pattern="^(daily|weekly|monthly)$",
        description="Trending window on github.com/trending: daily, weekly, or monthly.",
    ),
    language: str | None = Query(
        None,
        description="Optional programming-language slug for /trending/{language} (e.g. python, typescript).",
    ),
    limit: int = Query(25, ge=1, le=100, description="Max rows to return (GitHub's page usually has ≤25)."),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    lang = (language or "").strip() or None
    async with billed_call(
        caller=caller,
        endpoint="/v1/github/trending-repositories",
        platform="github",
        resource_url=None,
        base_credits=CREDIT_TRENDING_REPOS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            rows = await github_trending_native.trending_repositories_native(
                since=since, language=lang, limit=limit
            )
            if not rows:
                raise HTTPException(
                    status_code=502,
                    detail="Could not load github.com/trending",
                )
            ctx["source"] = "github.com/trending"
            return {
                "source": "github.com/trending",
                "since": since,
                "language": lang,
                "totalReturned": len(rows),
                "repositories": rows,
            }

        data = await cached_or_run(
            "github.trending-repositories",
            {"since": since, "language": lang or "", "limit": limit, "v": 3},
            _run,
            ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/trending-developers",
    summary="GitHub trending developers",
    description=(
        "Developers from github.com/trending/developers ranked for a time window "
        "(since=daily|weekly|monthly) — not REST /search/users with followers:>1000. "
        "Each row: rank, login, name, avatar, popularRepo, plus followers/bio/company/"
        "location/publicRepos hydrated from GET /users/{login}. source is always "
        '"github.com/trending/developers". Flat 2 credits. No Search relevance score.'
    ),
)
async def trending_developers(
    since: str = Query(
        "daily",
        pattern="^(daily|weekly|monthly)$",
        description="Trending window on github.com/trending/developers: daily, weekly, or monthly.",
    ),
    language: str | None = Query(
        None,
        description="Optional programming-language slug for /trending/developers/{language}.",
    ),
    limit: int = Query(25, ge=1, le=100, description="Max rows (GitHub's page usually has ≤25)."),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    lang = (language or "").strip() or None
    async with billed_call(
        caller=caller,
        endpoint="/v1/github/trending-developers",
        platform="github",
        resource_url=None,
        base_credits=CREDIT_TRENDING_DEVS,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            rows = await github_trending_native.trending_developers_native(
                since=since, language=lang, limit=limit
            )
            if not rows:
                raise HTTPException(
                    status_code=502,
                    detail="Could not load github.com/trending/developers",
                )
            async def _hydrate(row: dict[str, Any]) -> dict[str, Any]:
                login = row.get("login")
                if not isinstance(login, str) or not login:
                    return row
                try:
                    u = await _get(f"/users/{login}")
                except HTTPException:
                    return row
                merged = dict(row)
                merged.update(
                    strip_empty(
                        {
                            "name": safe_str(u.get("name")) or row.get("name"),
                            "bio": safe_str(u.get("bio")),
                            "company": safe_str(u.get("company")),
                            "location": safe_str(u.get("location")),
                            "followers": safe_int(u.get("followers")),
                            "following": safe_int(u.get("following")),
                            "publicRepos": safe_int(u.get("public_repos")),
                            "ownerType": (
                                "Organization"
                                if (safe_str(u.get("type")) or "").lower() == "organization"
                                else "User"
                            ),
                        }
                    )
                )
                return merged

            enriched = list(await asyncio.gather(*[_hydrate(r) for r in rows]))
            ctx["source"] = "github.com/trending/developers"
            return {
                "source": "github.com/trending/developers",
                "since": since,
                "language": lang,
                "totalReturned": len(enriched),
                "developers": enriched,
            }

        data = await cached_or_run(
            "github.trending-developers",
            {"since": since, "language": lang or "", "limit": limit, "v": 3},
            _run,
            ctx,
            use_cache=cache,
        )
        return ApiResponse(data=data)
