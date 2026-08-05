"""GitHub repository normalize + trending HTML parse."""

from __future__ import annotations

from app.routers.github import _repo
from app.services.github_trending_native import parse_trending_html


def test_watchers_uses_subscribers_not_watchers_count():
    out = _repo(
        {
            "name": "linux",
            "full_name": "torvalds/linux",
            "html_url": "https://github.com/torvalds/linux",
            "description": "Linux kernel source tree",
            "owner": {
                "login": "torvalds",
                "html_url": "https://github.com/torvalds",
                "avatar_url": "x",
                "type": "User",
            },
            "language": "C",
            "stargazers_count": 100,
            "forks_count": 10,
            "watchers_count": 100,
            "subscribers_count": 42,
            "open_issues_count": 3,
            "default_branch": "master",
            "license": {"spdx_id": "NOASSERTION", "name": "Other"},
            "topics": [],
            "fork": False,
            "archived": False,
            "size": 1,
            "visibility": "public",
            "has_issues": False,
            "has_discussions": False,
            "pushed_at": "2026-01-01T00:00:00Z",
            "created_at": "2011-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    )
    assert out["watchers"] == 42
    assert out["stars"] == 100
    assert out["watchers"] != out["stars"]
    assert "openIssues" not in out
    assert out["openIssuesAndPrs"] == 3
    assert "license" not in out
    assert out["licenseName"] == "Other"
    assert out["ownerType"] == "User"
    assert out["language"] == "C"


def test_list_payload_omits_watchers_without_subscribers():
    out = _repo(
        {
            "name": "linux",
            "full_name": "torvalds/linux",
            "html_url": "https://github.com/torvalds/linux",
            "owner": {
                "login": "torvalds",
                "html_url": "https://github.com/torvalds",
                "type": "User",
            },
            "stargazers_count": 100,
            "forks_count": 10,
            "watchers_count": 100,
            "open_issues_count": 3,
            "fork": False,
            "archived": False,
            "license": {"spdx_id": "MIT", "name": "MIT License"},
        }
    )
    assert "watchers" not in out
    assert out["license"] == "MIT"


def test_fork_includes_parent():
    out = _repo(
        {
            "name": "libgit2",
            "full_name": "torvalds/libgit2",
            "html_url": "https://github.com/torvalds/libgit2",
            "owner": {
                "login": "torvalds",
                "html_url": "https://github.com/torvalds",
                "type": "User",
            },
            "stargazers_count": 1,
            "forks_count": 0,
            "subscribers_count": 3,
            "open_issues_count": 0,
            "fork": True,
            "archived": False,
            "parent": {"full_name": "libgit2/libgit2"},
            "license": {"spdx_id": "GPL-2.0", "name": "GNU General Public License v2.0"},
        }
    )
    assert out["isFork"] is True
    assert out["parent"] == "libgit2/libgit2"
    assert out["watchers"] == 3


SAMPLE_ARTICLE = '''
<article class="Box-row">
  <h2>
    <a href="/cloudflare/computer">cloudflare / computer</a>
  </h2>
  <p class="col-9 color-fg-muted my-1 pr-4">
    Description here
  </p>
  <span itemprop="programmingLanguage">TypeScript</span>
  <a href="/cloudflare/computer/stargazers">
    <svg></svg>
        2,514</a>
  <a href="/cloudflare/computer/forks">
    <svg></svg>
        120</a>
  <span>796 stars today</span>
</article>
'''


def test_parse_trending_html_stars_gained():
    rows = parse_trending_html(SAMPLE_ARTICLE, since="daily")
    assert len(rows) == 1
    r = rows[0]
    assert r["fullName"] == "cloudflare/computer"
    assert r["language"] == "TypeScript"
    assert r["stars"] == 2514
    assert r["forks"] == 120
    assert r["starsGained"] == 796
    assert r["since"] == "daily"
    assert r["rank"] == 1
