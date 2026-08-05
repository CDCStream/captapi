"""GitHub followers/following cards + repositories sort params."""

from __future__ import annotations

from app.routers.github import (
    GITHUB_GRAPH_RATE,
    _encode_page_cursor,
    _gh_user_card,
    _repo,
    _scaled,
)


def test_gh_user_card_has_id_and_type():
    out = _gh_user_card(
        {
            "id": 206,
            "login": "sprsquish",
            "type": "User",
            "html_url": "https://github.com/sprsquish",
            "avatar_url": "https://avatars.githubusercontent.com/u/206?v=4",
        }
    )
    assert out == {
        "id": 206,
        "login": "sprsquish",
        "type": "User",
        "url": "https://github.com/sprsquish",
        "avatar": "https://avatars.githubusercontent.com/u/206?v=4",
    }


def test_gh_user_card_organization():
    out = _gh_user_card({"id": 1, "login": "vercel", "type": "Organization", "html_url": "https://github.com/vercel"})
    assert out["type"] == "Organization"


def test_graph_rate_cheaper_than_list():
    assert _scaled(30, GITHUB_GRAPH_RATE) == 3
    assert _scaled(30, 0.4) == 12


def test_repo_list_omits_watchers_without_subscribers():
    out = _repo(
        {
            "name": "libgit2",
            "full_name": "torvalds/libgit2",
            "html_url": "https://github.com/torvalds/libgit2",
            "fork": True,
            "stargazers_count": 370,
            "forks_count": 28,
            "watchers_count": 370,
            "open_issues_count": 1,
            "owner": {"login": "torvalds", "html_url": "https://github.com/torvalds", "type": "User"},
            "language": "C",
            "default_branch": "main",
            "archived": False,
            "topics": [],
        }
    )
    assert out["isFork"] is True
    assert "parent" not in out
    assert "watchers" not in out
    assert out["stars"] == 370


def test_opaque_cursor_repos():
    cur = _encode_page_cursor(2, kind="repos")
    assert cur != "2"
