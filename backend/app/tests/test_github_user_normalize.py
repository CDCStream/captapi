"""GitHub /user normalize - type casing + public email."""

from __future__ import annotations

from app.routers.github import _user


def test_user_preserves_user_type_and_omits_null_email():
    out = _user(
        {
            "login": "getify",
            "id": 150330,
            "node_id": "MDQ6VXNlcjE1MDMzMA==",
            "html_url": "https://github.com/getify",
            "url": "https://api.github.com/users/getify",
            "type": "User",
            "name": "Kyle Simpson",
            "company": "Getify Solutions",
            "blog": "http://getify.me",
            "location": "Austin, TX",
            "email": None,
            "bio": "bio",
            "avatar_url": "https://avatars.githubusercontent.com/u/150330?v=4",
            "public_repos": 74,
            "public_gists": 411,
            "followers": 1,
            "following": 3,
            "twitter_username": None,
            "hireable": True,
            "site_admin": False,
            "created_at": "2009-11-08T06:56:21Z",
            "updated_at": "2026-04-28T20:14:44Z",
        }
    )
    assert out["type"] == "User"
    assert "email" not in out
    assert "twitterUsername" not in out
    assert out["hireable"] is True
    assert out["siteAdmin"] is False


def test_organization_type_preserved():
    out = _user(
        {
            "login": "vercel",
            "id": 14985020,
            "type": "Organization",
            "html_url": "https://github.com/vercel",
            "url": "https://api.github.com/users/vercel",
            "name": "Vercel",
            "public_repos": 1,
            "public_gists": 0,
            "followers": 1,
            "following": 0,
            "site_admin": False,
        }
    )
    assert out["type"] == "Organization"
    assert out["login"] == "vercel"


def test_public_email_included():
    out = _user(
        {
            "login": "someone",
            "id": 1,
            "type": "User",
            "html_url": "https://github.com/someone",
            "url": "https://api.github.com/users/someone",
            "email": "a@example.com",
            "public_repos": 0,
            "public_gists": 0,
            "followers": 0,
            "following": 0,
            "site_admin": False,
        }
    )
    assert out["email"] == "a@example.com"
