"""GitHub pull-requests + activity normalize and opaque cursors."""

from __future__ import annotations

from app.routers.github import (
    _decode_page_cursor,
    _encode_page_cursor,
    _event,
    _next_page_from_link,
    _pull,
)


def test_opaque_cursor_not_bare_page():
    cur = _encode_page_cursor(2, kind="pulls")
    assert cur != "2"
    assert _decode_page_cursor(cur, kind="pulls") == 2
    assert _decode_page_cursor("3", kind="pulls") == 3  # legacy


def test_link_header_next_page():
    link = (
        '<https://api.github.com/repos/a/b/pulls?page=2>; rel="next", '
        '<https://api.github.com/repos/a/b/pulls?page=10>; rel="last"'
    )
    assert _next_page_from_link(link) == 2
    assert _next_page_from_link(None) is None


def test_pull_includes_draft_labels_author_head():
    out = _pull(
        {
            "id": 1,
            "number": 42,
            "title": "Fix bug",
            "state": "closed",
            "draft": False,
            "html_url": "https://github.com/a/b/pull/42",
            "user": {
                "id": 9,
                "login": "alice",
                "html_url": "https://github.com/alice",
                "avatar_url": "https://avatars.githubusercontent.com/u/9",
            },
            "labels": [{"name": "bug", "color": "ff0000", "description": "A bug"}],
            "assignees": [],
            "requested_reviewers": [
                {
                    "id": 8,
                    "login": "bob",
                    "html_url": "https://github.com/bob",
                    "avatar_url": "https://avatars.githubusercontent.com/u/8",
                }
            ],
            "head": {"ref": "fix", "sha": "aaa", "label": "a:fix"},
            "base": {"ref": "main", "sha": "bbb", "label": "a:main"},
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
            "closed_at": "2026-01-02T00:00:00Z",
            "merged_at": "2026-01-02T00:00:00Z",
        }
    )
    assert out["draft"] is False
    assert out["labels"][0]["name"] == "bug"
    assert out["author"]["login"] == "alice"
    assert out["author"]["id"] == 9
    assert out["head"]["ref"] == "fix"
    assert out["base"]["ref"] == "main"
    assert out["closedAt"]
    assert out["requestedReviewers"][0]["login"] == "bob"


def test_push_event_payload_has_commits_and_ref():
    out = _event(
        {
            "id": "1",
            "type": "PushEvent",
            "repo": {"name": "getify/foo"},
            "actor": {"login": "getify"},
            "public": True,
            "created_at": "2026-01-01T00:00:00Z",
            "payload": {
                "ref": "refs/heads/main",
                "size": 2,
                "distinct_size": 2,
                "head": "abc",
                "before": "def",
                "commits": [
                    {
                        "sha": "abc123",
                        "message": "hello",
                        "author": {"name": "Kyle", "email": "k@example.com"},
                        "distinct": True,
                    }
                ],
            },
        }
    )
    assert "actor" not in out
    assert out["type"] == "PushEvent"
    assert out["payload"]["ref"] == "refs/heads/main"
    assert out["payload"]["commits"][0]["message"] == "hello"
    assert out["payload"]["size"] == 2
