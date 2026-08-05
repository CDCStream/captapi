"""Canonical cross-platform profile core."""

from __future__ import annotations

import asyncio

from app.routers.bluesky import (
    _joined_via_starter_pack,
    _labels,
    _normalize_profile,
    _pinned_post,
)
from app.utils.profile_core import CANONICAL_PROFILE_KEYS, stamp_profile_core


def test_stamp_promotes_legacy_aliases_to_canonical():
    card = stamp_profile_core(
        {
            "name": "Jay",
            "description": "bio text",
            "thumbnailUrl": "https://img/a.jpg",
            "bannerUrl": "https://img/b.jpg",
            "videoCount": 12,
            "subscriberCount": 1000,
            "username": "jay",
            "joinedAt": "2020-01-01",
            "channelId": "UCabc",
        },
        platform="youtube",
    )
    assert card["platform"] == "youtube"
    assert card["id"] == "UCabc"
    assert card["handle"] == "jay"
    assert card["displayName"] == "Jay"
    assert card["bio"] == "bio text"
    assert card["avatar"] == "https://img/a.jpg"
    assert card["banner"] == "https://img/b.jpg"
    assert card["followers"] == 1000
    assert card["postCount"] == 12
    assert card["createdAt"] == "2020-01-01"
    # Deprecated aliases re-emitted for YouTube.
    assert card["name"] == "Jay"
    assert card["thumbnailUrl"] == "https://img/a.jpg"
    assert card["bannerUrl"] == "https://img/b.jpg"
    assert card["videoCount"] == 12
    assert card["subscriberCount"] == 1000


def test_stamp_bluesky_keeps_posts_alias():
    card = stamp_profile_core(
        {
            "displayName": "Bluesky",
            "postCount": 99,
            "avatar": "https://cdn/a",
            "handle": "bsky.app",
            "id": "did:plc:x",
        },
        platform="bluesky",
    )
    assert card["displayName"] == "Bluesky"
    assert card["name"] == "Bluesky"
    assert card["postCount"] == 99
    assert card["posts"] == 99


def test_canonical_keys_documented():
    assert "displayName" in CANONICAL_PROFILE_KEYS
    assert "postCount" in CANONICAL_PROFILE_KEYS
    assert "avatar" in CANONICAL_PROFILE_KEYS


def test_pinned_post_and_joined_via():
    pinned = _pinned_post(
        {
            "uri": "at://did:plc:abc/app.bsky.feed.post/3kq",
            "cid": "bafyreiabc",
        }
    )
    assert pinned is not None
    assert pinned["uri"].endswith("/3kq")
    assert pinned["rkey"] == "3kq"
    assert pinned["cid"] == "bafyreiabc"

    joined = _joined_via_starter_pack(
        {
            "uri": "at://did:plc:x/app.bsky.graph.starterpack/1",
            "cid": "bafy",
            "record": {"name": "Cool pack"},
            "creator": {"did": "did:plc:y", "handle": "alice.bsky.social", "displayName": "Alice"},
        }
    )
    assert joined is not None
    assert joined["name"] == "Cool pack"
    assert joined["creator"]["handle"] == "alice.bsky.social"


def test_labels_full_shape():
    rows = _labels(
        {
            "labels": [
                {
                    "src": "did:plc:labeler",
                    "uri": "at://did:plc:subj/app.bsky.actor.profile/self",
                    "cid": "bafy1",
                    "val": "!hide",
                    "neg": False,
                    "cts": "2024-01-01T00:00:00.000Z",
                    "exp": "2025-01-01T00:00:00.000Z",
                }
            ]
        }
    )
    assert len(rows) == 1
    assert rows[0] == {
        "src": "did:plc:labeler",
        "uri": "at://did:plc:subj/app.bsky.actor.profile/self",
        "cid": "bafy1",
        "val": "!hide",
        "neg": False,
        "createdAt": "2024-01-01T00:00:00.000Z",
        "expiresAt": "2025-01-01T00:00:00.000Z",
    }


def test_normalize_profile_canonical_and_aliases():
    async def _run():
        return await _normalize_profile(
            {
                "did": "did:plc:oky5czdrnfjpqslsw2a5iclo",
                "handle": "jay.bsky.team",
                "displayName": "Jay",
                "description": "Founder",
                "followersCount": 10,
                "followsCount": 2,
                "postsCount": 5,
                "avatar": "https://cdn/a",
                "banner": "https://cdn/b",
                "createdAt": "2022-11-17T06:31:40.296Z",
                "indexedAt": "2026-03-29T21:16:33.460Z",
                "verification": {
                    "verifications": [
                        {
                            "issuer": "did:plc:z72i7hdynmk6r22z27h6tvur",
                            "issuerHandle": "bsky.app",
                            "issuerDisplayName": "Bluesky",
                            "uri": "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.graph.verification/x",
                            "isValid": True,
                            "createdAt": "2025-04-21T11:35:53.359Z",
                        }
                    ],
                    "verifiedStatus": "valid",
                    "trustedVerifierStatus": "none",
                },
                "pinnedPost": {
                    "uri": "at://did:plc:oky5czdrnfjpqslsw2a5iclo/app.bsky.feed.post/abc",
                    "cid": "bafypin",
                },
                "associated": {"lists": 0, "feedgens": 1, "starterPacks": 0, "labeler": False},
            }
        )

    out = asyncio.run(_run())
    assert out["platform"] == "bluesky"
    assert out["id"] == out["did"] == "did:plc:oky5czdrnfjpqslsw2a5iclo"
    assert out["displayName"] == "Jay"
    assert out["name"] == "Jay"
    assert out["postCount"] == 5
    assert out["posts"] == 5
    assert out["verified"] is True
    assert out["verification"]["verifications"][0]["issuerHandle"] == "bsky.app"
    assert out["pinnedPost"]["rkey"] == "abc"
    assert out["associated"]["feedgens"] == 1
