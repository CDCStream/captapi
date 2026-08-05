"""Bluesky user-posts: repost marking, quote embeds, opaque cursor paging."""

from __future__ import annotations

from typing import Any

from app.routers import bluesky as bsky


def _post(
    *,
    handle: str,
    did: str,
    rkey: str,
    text: str,
    created: str,
    likes: int = 1,
    embed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "uri": f"at://{did}/app.bsky.feed.post/{rkey}",
        "cid": f"cid-{rkey}",
        "indexedAt": created,
        "likeCount": likes,
        "repostCount": 0,
        "replyCount": 0,
        "quoteCount": 0,
        "author": {
            "handle": handle,
            "displayName": handle.split(".")[0].title(),
            "did": did,
            "avatar": f"https://cdn/{handle}.jpg",
        },
        "record": {"text": text, "createdAt": created},
        "embed": embed,
    }


def test_repost_reason_sets_is_repost_and_reposted_by():
    original = _post(
        handle="danabra.mov",
        did="did:plc:dan",
        rkey="ama1",
        text="ama about atproto",
        created="2026-07-13T12:02:47.424Z",
        likes=340,
    )
    item = {
        "post": original,
        "reason": {
            "$type": "app.bsky.feed.defs#reasonRepost",
            "by": {
                "handle": "jay.bsky.team",
                "displayName": "Jay",
                "did": "did:plc:jay",
                "avatar": "https://cdn/jay.jpg",
            },
            "indexedAt": "2026-07-17T10:00:00.000Z",
        },
    }
    row = bsky._normalize_feed_item(item)
    assert row is not None
    assert row["isRepost"] is True
    assert row["author"]["handle"] == "danabra.mov"
    assert row["repostedBy"]["handle"] == "jay.bsky.team"
    assert row["repostedBy"]["did"] == "did:plc:jay"
    assert row["repostedAt"] == "2026-07-17T10:00:00.000Z"
    assert row["engagement"]["likes"] == 340


def test_own_post_is_not_repost():
    item = {
        "post": _post(
            handle="jay.bsky.team",
            did="did:plc:jay",
            rkey="own1",
            text="hello",
            created="2026-07-10T00:00:00.000Z",
        )
    }
    row = bsky._normalize_feed_item(item)
    assert row is not None
    assert row["isRepost"] is False
    assert "repostedBy" not in row
    assert "repostedAt" not in row


def test_quote_embed_normalized_not_raw_nsid():
    embed = {
        "$type": "app.bsky.embed.record#view",
        "record": {
            "$type": "app.bsky.embed.record#viewRecord",
            "uri": "at://did:plc:alice/app.bsky.feed.post/q1",
            "cid": "cid-q1",
            "author": {
                "handle": "alice.bsky.social",
                "displayName": "Alice",
                "did": "did:plc:alice",
                "avatar": "https://cdn/alice.jpg",
            },
            "value": {
                "$type": "app.bsky.feed.post",
                "text": "quoted text here",
                "createdAt": "2026-06-01T00:00:00.000Z",
            },
            "indexedAt": "2026-06-01T00:00:01.000Z",
        },
    }
    post = _post(
        handle="jay.bsky.team",
        did="did:plc:jay",
        rkey="quote1",
        text="check this",
        created="2026-07-17T00:00:00.000Z",
        embed=embed,
    )
    row = bsky._normalize_post(post)
    assert row["embed"] is not None
    assert row["embed"]["type"] == "quote"
    assert "app.bsky" not in row["embed"]["type"]
    assert row["embed"]["text"] == "quoted text here"
    assert row["embed"]["author"]["handle"] == "alice.bsky.social"
    assert row["embed"]["url"] == "https://bsky.app/profile/alice.bsky.social/post/q1"
    assert row["embed"]["uri"].endswith("/q1")


def test_external_and_images_embed_types_stable():
    ext = bsky._normalize_post(
        _post(
            handle="a",
            did="did:plc:a",
            rkey="e1",
            text="link",
            created="2026-01-01T00:00:00.000Z",
            embed={
                "$type": "app.bsky.embed.external#view",
                "external": {
                    "uri": "https://example.com",
                    "title": "Ex",
                    "description": "Desc",
                    "thumb": "https://cdn/t.jpg",
                },
            },
        )
    )
    assert ext["embed"]["type"] == "external"
    assert ext["embed"]["url"] == "https://example.com"

    imgs = bsky._normalize_post(
        _post(
            handle="a",
            did="did:plc:a",
            rkey="i1",
            text="pics",
            created="2026-01-01T00:00:00.000Z",
            embed={
                "$type": "app.bsky.embed.images#view",
                "images": [{"fullsize": "https://cdn/1.jpg", "alt": "one"}],
            },
        )
    )
    assert imgs["embed"]["type"] == "images"
    assert imgs["embed"]["images"][0]["url"] == "https://cdn/1.jpg"


def test_opaque_cursor_paging_pages_share_no_uri():
    """Simulate two getAuthorFeed pages: cursor is opaque, uri sets disjoint."""
    page1_feed = [
        {
            "post": _post(
                handle="danabra.mov",
                did="did:plc:dan",
                rkey="r1",
                text="reposted ama",
                created="2026-07-13T12:02:47.424Z",
                likes=340,
            ),
            "reason": {
                "$type": "app.bsky.feed.defs#reasonRepost",
                "by": {
                    "handle": "jay.bsky.team",
                    "did": "did:plc:jay",
                    "displayName": "Jay",
                },
                "indexedAt": "2026-07-17T18:00:00.000Z",
            },
        },
        {
            "post": _post(
                handle="jay.bsky.team",
                did="did:plc:jay",
                rkey="p1",
                text="own post",
                created="2026-07-10T00:00:00.000Z",
            ),
        },
    ]
    page2_feed = [
        {
            "post": _post(
                handle="jay.bsky.team",
                did="did:plc:jay",
                rkey="p2",
                text="older",
                created="2026-06-26T14:25:33.024Z",
            ),
        },
    ]

    def page(feed: list[dict[str, Any]], cursor_out: str | None) -> dict[str, Any]:
        # Mirror endpoint: Bluesky cursor only — never last publishedAt.
        posts = [bsky._normalize_feed_item(i) for i in feed]
        posts = [p for p in posts if p]
        return {
            "posts": posts,
            "nextCursor": cursor_out,
            "hasMore": cursor_out is not None,
        }

    first = page(page1_feed, "opaque-cursor-page2")
    assert first["nextCursor"] == "opaque-cursor-page2"
    assert first["nextCursor"] != first["posts"][-1]["publishedAt"]
    assert first["posts"][0]["isRepost"] is True
    assert first["posts"][0]["repostedBy"]["handle"] == "jay.bsky.team"

    second = page(page2_feed, None)
    uris1 = {p["uri"] for p in first["posts"]}
    uris2 = {p["uri"] for p in second["posts"]}
    assert uris1.isdisjoint(uris2)
    assert len(uris1) + len(uris2) == 3
