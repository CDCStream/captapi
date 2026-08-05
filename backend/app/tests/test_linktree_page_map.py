"""Linktree page mapper: string ids, PRODUCT url, socialAccounts."""

from __future__ import annotations

import asyncio

from app.routers import linktree as lt


def test_top_level_id_is_string():
    data = {
        "props": {
            "pageProps": {
                "account": {
                    "id": 15278008,
                    "username": "miguelangeles",
                    "name": "Miguel Angeles",
                    "isVerified": True,
                    "verticals": ["music_artist"],
                    "linkPlatforms": ["SPOTIFY"],
                },
                "links": [],
                "socialLinks": [],
            }
        }
    }
    out = lt._normalize(data, "https://linktr.ee/miguelangeles")
    assert out["id"] == "15278008"
    assert isinstance(out["id"], str)
    assert out["displayName"] == "Miguel Angeles"
    assert out["name"] == "Miguel Angeles"
    assert out.get("handle") == "miguelangeles"


def test_product_url_from_shop_url():
    item = {
        "id": 233892723,
        "title": "MERCH",
        "type": "PRODUCT",
        "url": "",
        "thumbnail": "https://ugc.production.linktr.ee/hat.jpeg",
        "context": {
            "products": [
                {
                    "shopUrl": "https://irlangel.com",
                    "url": "",
                    "title": "Jersey",
                }
            ]
        },
    }
    out = lt._normalize_link(item)
    assert out["id"] == "233892723"
    assert out["url"] == "https://irlangel.com"
    assert "url" in out


def test_product_url_null_when_no_destination():
    out = lt._normalize_link({"id": 1, "title": "MERCH", "type": "PRODUCT", "url": ""})
    assert out["url"] is None
    assert "url" in out


def test_social_accounts_skips_email():
    socials = [
        {"type": "INSTAGRAM", "url": "https://www.instagram.com/miguelangeles/"},
        {"type": "EMAIL_ADDRESS", "url": "mailto:miguel@irlangel.com"},
        {"type": "YOUTUBE", "url": "https://www.youtube.com/watch?v=xiFUzOJaiC4"},
    ]
    accounts, other = lt._social_accounts(socials, [])
    assert isinstance(other, list)
    assert "email" not in accounts
    assert accounts["instagram"].endswith("miguelangeles/")
    assert "youtube" in accounts


def test_resolve_youtube_watch_to_channel():
    channel = asyncio.run(
        lt._resolve_youtube_channel("https://www.youtube.com/watch?v=xiFUzOJaiC4")
    )
    assert "/@" in channel or "/channel/" in channel
    assert "watch?v=" not in channel


def test_social_accounts_other_unmapped_type():
    accounts, other = lt._social_accounts(
        [
            {"type": "INSTAGRAM", "url": "https://www.instagram.com/x/"},
            {"type": "EMAIL_ADDRESS", "url": "mailto:x@y.com"},
            {"type": "CUSTOM_APP", "url": "https://custom.example/x"},
        ],
        [],
    )
    assert "instagram" in accounts
    assert any(o.get("type") == "CUSTOM_APP" for o in other)
