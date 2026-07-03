"""GitHub public data endpoints.

Uses GitHub's public REST API directly. No Apify actor is needed for this
platform, which keeps these endpoints fast and cheap.
"""

from __future__ import annotations

from typing import Any

import math

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.cached_runner import cached_or_run
from app.utils.formatters import safe_int, safe_str

router = APIRouter()

GITHUB_API = "https://api.github.com"
GITHUB_LIST_RATE = 0.4
GITHUB_SEARCH_RATE = 0.6


def _scaled(limit: int, rate: float, minimum: int = 3) -> int:
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


async def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Captapi/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = get_settings().GITHUB_TOKEN
    if token:
        headers["Authorization"] = f"Bearer {token}"
    # follow_redirects: GitHub 301s renamed/transferred repos (e.g.
    # facebook/react) and returns a JSON stub instead of the data otherwise.
    async with httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True) as client:
        resp = await client.get(f"{GITHUB_API}{path}", params=params)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Not found on GitHub")
    if resp.status_code == 403:
        raise HTTPException(status_code=429, detail="GitHub public API rate limit reached")
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail="GitHub API error")
    return resp.json()


def _user(u: dict[str, Any]) -> dict[str, Any]:
    return {
        "platform": "github",
        "type": "user",
        "login": safe_str(u.get("login")),
        "id": safe_int(u.get("id")),
        "url": safe_str(u.get("html_url")),
        "name": safe_str(u.get("name")),
        "company": safe_str(u.get("company")),
        "blog": safe_str(u.get("blog")),
        "location": safe_str(u.get("location")),
        "bio": safe_str(u.get("bio")),
        "avatar": safe_str(u.get("avatar_url")),
        "publicRepos": safe_int(u.get("public_repos")),
        "followers": safe_int(u.get("followers")),
        "following": safe_int(u.get("following")),
        "createdAt": safe_str(u.get("created_at")),
    }


def _repo(r: dict[str, Any]) -> dict[str, Any]:
    owner = r.get("owner") or {}
    return {
        "platform": "github",
        "type": "repository",
        "name": safe_str(r.get("name")),
        "fullName": safe_str(r.get("full_name")),
        "url": safe_str(r.get("html_url")),
        "description": safe_str(r.get("description")),
        "owner": safe_str(owner.get("login")),
        "ownerUrl": safe_str(owner.get("html_url")),
        "language": safe_str(r.get("language")),
        "stars": safe_int(r.get("stargazers_count")),
        "forks": safe_int(r.get("forks_count")),
        "watchers": safe_int(r.get("watchers_count")),
        "openIssues": safe_int(r.get("open_issues_count")),
        "defaultBranch": safe_str(r.get("default_branch")),
        "pushedAt": safe_str(r.get("pushed_at")),
        "createdAt": safe_str(r.get("created_at")),
    }


def _event(e: dict[str, Any]) -> dict[str, Any]:
    repo = e.get("repo") or {}
    actor = e.get("actor") or {}
    return {
        "id": safe_str(e.get("id")),
        "type": safe_str(e.get("type")),
        "repo": safe_str(repo.get("name")),
        "actor": safe_str(actor.get("login")),
        "createdAt": safe_str(e.get("created_at")),
    }


def _pull(p: dict[str, Any]) -> dict[str, Any]:
    user = p.get("user") or {}
    return {
        "id": safe_int(p.get("id")),
        "number": safe_int(p.get("number")),
        "title": safe_str(p.get("title")),
        "state": safe_str(p.get("state")),
        "url": safe_str(p.get("html_url")),
        "author": safe_str(user.get("login")),
        "createdAt": safe_str(p.get("created_at")),
        "updatedAt": safe_str(p.get("updated_at")),
        "mergedAt": safe_str(p.get("merged_at")),
    }


@router.get("/user", summary="GitHub user profile")
async def github_user(
    username: str = Query(..., description="GitHub username or profile URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    async with billed_call(caller=caller, endpoint="/v1/github/user", platform="github", resource_url=f"https://github.com/{login}", base_credits=3) as ctx:
        async def _run() -> dict[str, Any]:
            return _user(await _get(f"/users/{login}"))

        return ApiResponse(data=await cached_or_run("github.user", {"login": login}, _run, ctx))


@router.get("/repositories", summary="List a GitHub user's repositories")
async def repositories(
    username: str = Query(..., description="GitHub username or profile URL"),
    limit: int = Query(30, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    async with billed_call(caller=caller, endpoint="/v1/github/repositories", platform="github", resource_url=f"https://github.com/{login}", base_credits=_scaled(limit, GITHUB_LIST_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _get(f"/users/{login}/repos", {"per_page": limit, "sort": "updated"})
            repos = [_repo(i) for i in items[:limit]]
            return {"username": login, "totalReturned": len(repos), "repositories": repos}

        data = await cached_or_run("github.repositories", {"login": login, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["repositories"]), GITHUB_LIST_RATE)
        return ApiResponse(data=data)


@router.get("/repository", summary="GitHub repository details")
async def repository(
    repo: str = Query(..., description="Repository URL or owner/name"),
    caller: ApiCaller = Depends(require_api_key),
):
    parts = _repo_parts(repo)
    if not parts:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository")
    owner, name = parts
    async with billed_call(caller=caller, endpoint="/v1/github/repository", platform="github", resource_url=f"https://github.com/{owner}/{name}", base_credits=3) as ctx:
        async def _run() -> dict[str, Any]:
            return _repo(await _get(f"/repos/{owner}/{name}"))

        return ApiResponse(data=await cached_or_run("github.repository", {"owner": owner, "name": name}, _run, ctx))


@router.get("/pull-requests", summary="List repository pull requests")
async def pull_requests(
    repo: str = Query(..., description="Repository URL or owner/name"),
    state: str = Query("open", pattern="^(open|closed|all)$"),
    limit: int = Query(30, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    parts = _repo_parts(repo)
    if not parts:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository")
    owner, name = parts
    async with billed_call(caller=caller, endpoint="/v1/github/pull-requests", platform="github", resource_url=f"https://github.com/{owner}/{name}", base_credits=_scaled(limit, GITHUB_LIST_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _get(f"/repos/{owner}/{name}/pulls", {"state": state, "per_page": limit})
            pulls = [_pull(i) for i in items[:limit]]
            return {"repository": f"{owner}/{name}", "totalReturned": len(pulls), "pullRequests": pulls}

        data = await cached_or_run("github.pull-requests", {"repo": f"{owner}/{name}", "state": state, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["pullRequests"]), GITHUB_LIST_RATE)
        return ApiResponse(data=data)


@router.get("/activity", summary="GitHub user public activity")
async def activity(
    username: str = Query(..., description="GitHub username or profile URL"),
    limit: int = Query(30, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    async with billed_call(caller=caller, endpoint="/v1/github/activity", platform="github", resource_url=f"https://github.com/{login}", base_credits=_scaled(limit, GITHUB_LIST_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _get(f"/users/{login}/events/public", {"per_page": limit})
            events = [_event(i) for i in items[:limit]]
            return {"username": login, "totalReturned": len(events), "events": events}

        data = await cached_or_run("github.activity", {"login": login, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["events"]), GITHUB_LIST_RATE)
        return ApiResponse(data=data)


@router.get("/followers", summary="List GitHub followers")
async def followers(
    username: str = Query(...),
    limit: int = Query(30, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    async with billed_call(caller=caller, endpoint="/v1/github/followers", platform="github", resource_url=f"https://github.com/{login}", base_credits=_scaled(limit, GITHUB_LIST_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _get(f"/users/{login}/followers", {"per_page": limit})
            users = [{"login": safe_str(i.get("login")), "url": safe_str(i.get("html_url")), "avatar": safe_str(i.get("avatar_url"))} for i in items[:limit]]
            return {"username": login, "totalReturned": len(users), "followers": users}

        data = await cached_or_run("github.followers", {"login": login, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["followers"]), GITHUB_LIST_RATE)
        return ApiResponse(data=data)


@router.get("/following", summary="List GitHub following")
async def following(
    username: str = Query(...),
    limit: int = Query(30, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    async with billed_call(caller=caller, endpoint="/v1/github/following", platform="github", resource_url=f"https://github.com/{login}", base_credits=_scaled(limit, GITHUB_LIST_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            items = await _get(f"/users/{login}/following", {"per_page": limit})
            users = [{"login": safe_str(i.get("login")), "url": safe_str(i.get("html_url")), "avatar": safe_str(i.get("avatar_url"))} for i in items[:limit]]
            return {"username": login, "totalReturned": len(users), "following": users}

        data = await cached_or_run("github.following", {"login": login, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["following"]), GITHUB_LIST_RATE)
        return ApiResponse(data=data)


@router.get("/contributions", summary="GitHub contribution summary")
async def contributions(
    username: str = Query(..., description="GitHub username or profile URL"),
    caller: ApiCaller = Depends(require_api_key),
):
    login = _username(username)
    if not login:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    async with billed_call(caller=caller, endpoint="/v1/github/contributions", platform="github", resource_url=f"https://github.com/{login}", base_credits=3) as ctx:
        async def _run() -> dict[str, Any]:
            events = await _get(f"/users/{login}/events/public", {"per_page": 100})
            repos = await _get(f"/users/{login}/repos", {"per_page": 100, "sort": "updated"})
            return {
                "username": login,
                "recentPublicEvents": len(events),
                "recentEventTypes": sorted({safe_str(e.get("type")) for e in events if e.get("type")}),
                "publicRepositoriesSampled": len(repos),
                "starsAcrossSampledRepos": sum(safe_int(r.get("stargazers_count")) for r in repos),
            }

        return ApiResponse(data=await cached_or_run("github.contributions", {"login": login}, _run, ctx))


@router.get("/trending-repositories", summary="Trending GitHub repositories")
async def trending_repositories(
    q: str = Query("stars:>1000", description="GitHub search query"),
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(caller=caller, endpoint="/v1/github/trending-repositories", platform="github", resource_url=None, base_credits=_scaled(limit, GITHUB_SEARCH_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _get("/search/repositories", {"q": q, "sort": "stars", "order": "desc", "per_page": limit})
            repos = [_repo(i) for i in (data.get("items") or [])[:limit]]
            return {"query": q, "totalReturned": len(repos), "repositories": repos}

        data = await cached_or_run("github.trending-repositories", {"q": q, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["repositories"]), GITHUB_SEARCH_RATE)
        return ApiResponse(data=data)


@router.get("/trending-developers", summary="Trending GitHub developers")
async def trending_developers(
    q: str = Query("followers:>1000", description="GitHub user search query"),
    limit: int = Query(20, ge=1, le=100),
    caller: ApiCaller = Depends(require_api_key),
):
    async with billed_call(caller=caller, endpoint="/v1/github/trending-developers", platform="github", resource_url=None, base_credits=_scaled(limit, GITHUB_SEARCH_RATE)) as ctx:
        async def _run() -> dict[str, Any]:
            data = await _get("/search/users", {"q": q, "sort": "followers", "order": "desc", "per_page": limit})
            users = [
                {"login": safe_str(i.get("login")), "url": safe_str(i.get("html_url")), "avatar": safe_str(i.get("avatar_url")), "score": i.get("score")}
                for i in (data.get("items") or [])[:limit]
            ]
            return {"query": q, "totalReturned": len(users), "developers": users}

        data = await cached_or_run("github.trending-developers", {"q": q, "limit": limit}, _run, ctx)
        ctx["credits_override"] = _scaled(len(data["developers"]), GITHUB_SEARCH_RATE)
        return ApiResponse(data=data)
