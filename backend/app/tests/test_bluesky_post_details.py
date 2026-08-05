"""Bluesky post-details: facets, rich author, reply thread."""

from __future__ import annotations

from typing import Any

from app.routers import bluesky as bsky


def test_facets_prefer_full_uri_over_truncated_text():
    text = "read https://seattletimes.com/seattle-news/meet-jim... today"
    # Truncated display text bytes.
    start = text.index("https://")
    end = text.index(" today")
    record = {
        "text": text,
        "facets": [
            {
                "index": {"byteStart": start, "byteEnd": end},
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": "https://www.seattletimes.com/seattle-news/meet-jim-full-article/",
                    }
                ],
            },
            {
                "index": {"byteStart": 0, "byteEnd": 4},
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#mention",
                        "did": "did:plc:alice",
                    }
                ],
            },
            {
                "index": {"byteStart": 0, "byteEnd": 4},
                "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "atproto"}],
            },
        ],
    }
    facets = bsky._facets_from_record(record)
    assert facets["links"][0]["url"].endswith("meet-jim-full-article/")
    assert facets["links"][0]["url"] != facets["links"][0]["text"]
    assert facets["mentions"][0]["did"] == "did:plc:alice"
    assert facets["hashtags"] == ["atproto"]


def test_normalize_post_parent_root_and_langs():
    post = {
        "uri": "at://did:plc:a/app.bsky.feed.post/reply1",
        "cid": "cid1",
        "indexedAt": "2026-07-01T00:00:00.000Z",
        "likeCount": 1,
        "repostCount": 0,
        "replyCount": 0,
        "quoteCount": 0,
        "labels": [
            {
                "src": "did:plc:labeler",
                "uri": "at://did:plc:a/app.bsky.feed.post/reply1",
                "val": "porn",
                "cts": "2026-07-01T00:00:00.000Z",
            }
        ],
        "author": {
            "handle": "alice.bsky.social",
            "displayName": "Alice",
            "did": "did:plc:a",
            "avatar": "https://cdn/a.jpg",
            "createdAt": "2022-01-01T00:00:00.000Z",
            "labels": [
                {
                    "src": "did:plc:a",
                    "uri": "at://did:plc:a/app.bsky.actor.profile/self",
                    "val": "!no-unauthenticated",
                    "cts": "2023-01-01T00:00:00.000Z",
                }
            ],
            "verification": {"verifiedStatus": "none", "verifications": []},
        },
        "record": {
            "text": "a reply",
            "createdAt": "2026-07-01T00:00:00.000Z",
            "langs": ["en"],
            "reply": {
                "parent": {"uri": "at://did:plc:b/app.bsky.feed.post/parent1", "cid": "c"},
                "root": {"uri": "at://did:plc:b/app.bsky.feed.post/root1", "cid": "c"},
            },
        },
    }
    slim = bsky._normalize_post(post, rich_author=False)
    assert slim["isReply"] is True
    assert slim["parentUri"].endswith("/parent1")
    assert slim["rootUri"].endswith("/root1")
    assert slim["langs"] == ["en"]
    assert slim["labels"][0]["val"] == "porn"
    assert "verification" not in slim["author"]

    rich = bsky._normalize_post(post, rich_author=True)
    assert rich["author"]["createdAt"] == "2022-01-01T00:00:00.000Z"
    assert rich["author"]["labels"][0]["val"] == "!no-unauthenticated"
    assert rich["author"]["verification"]["verifiedStatus"] == "none"


def test_thread_node_nests_replies_to_depth():
    def _post(handle: str, rkey: str, text: str) -> dict[str, Any]:
        return {
            "uri": f"at://did:plc:{handle}/app.bsky.feed.post/{rkey}",
            "cid": f"cid-{rkey}",
            "indexedAt": "2026-07-01T00:00:00.000Z",
            "likeCount": 0,
            "repostCount": 0,
            "replyCount": 1,
            "quoteCount": 0,
            "author": {
                "handle": f"{handle}.bsky.social",
                "displayName": handle,
                "did": f"did:plc:{handle}",
                "avatar": "https://cdn/x.jpg",
                "createdAt": "2022-01-01T00:00:00.000Z",
            },
            "record": {"text": text, "createdAt": "2026-07-01T00:00:00.000Z", "langs": ["en"]},
        }

    thread = {
        "$type": "app.bsky.feed.defs#threadViewPost",
        "post": _post("root", "r0", "root post"),
        "replies": [
            {
                "$type": "app.bsky.feed.defs#threadViewPost",
                "post": _post("child", "c1", "first reply"),
                "replies": [
                    {
                        "$type": "app.bsky.feed.defs#threadViewPost",
                        "post": _post("grand", "g1", "nested"),
                        "replies": [],
                    }
                ],
            }
        ],
    }
    depth1 = bsky._normalize_thread_node(thread, depth=0, max_depth=1)
    assert depth1 is not None
    assert depth1["text"] == "root post"
    assert "verification" in depth1["author"]
    assert len(depth1["replies"]) == 1
    assert depth1["replies"][0]["text"] == "first reply"
    assert depth1["replies"][0]["replies"] == []

    depth2 = bsky._normalize_thread_node(thread, depth=0, max_depth=2)
    assert depth2 is not None
    assert depth2["replies"][0]["replies"][0]["text"] == "nested"
