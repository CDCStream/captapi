"""Unit tests for Truth Social account/post normalization."""

from __future__ import annotations

from app.routers import truth_social as ts

SPAN_WRAPPED_URL = (
    '<p>Read <a href="https://www.whitehouse.gov/election-integrity/">'
    '<span class="invisible">https://</span>'
    '<span class="ellipsis">www.whitehouse.gov/election-</span>'
    '<span class="invisible">integrity/</span></a></p>'
)


def test_status_at_iso_date_only():
    assert ts._status_at_iso("2026-08-02") == "2026-08-02T00:00:00.000Z"
    assert ts._status_at_iso("2026-08-02T12:34:56.000Z") == "2026-08-02T12:34:56.000Z"
    assert ts._status_at_iso(None) is None


def test_html_to_text_preserves_url_span_wraps():
    text = ts._html_to_text(SPAN_WRAPPED_URL)
    assert "https://www.whitehouse.gov/election-integrity/" in text
    assert "www. whitehouse" not in text
    assert "integr ity" not in text
    assert ts._extract_links(SPAN_WRAPPED_URL) == [
        {"url": "https://www.whitehouse.gov/election-integrity/"}
    ]


def test_missing_preview_url_null():
    assert ts._media_url("https://truthsocial.com/icons/missing.png") is None
    assert (
        ts._media_url("https://cdn.example.com/preview.jpg")
        == "https://cdn.example.com/preview.jpg"
    )


def test_normalize_post_links_card_media_external():
    raw = {
        "id": "1",
        "content": (
            '<p><a href="https://www.whitehouse.gov/election-integrity/">'
            "<span>www.</span><span>whitehouse.gov/</span></a></p>"
        ),
        "external_video_id": "v6surln",
        "upvotes_count": 3,
        "downvotes_count": 1,
        "favourites_count": 10,
        "replies_count": 2,
        "reblogs_count": 4,
        "language": "en",
        "sensitive": False,
        "card": {
            "url": "https://www.whitehouse.gov/election-integrity/",
            "title": "Election Integrity",
            "description": "...",
            "image": "https://example.com/i.jpg",
            "type": "link",
        },
        "media_attachments": [
            {
                "type": "video",
                "url": "https://cdn.example.com/v.mp4",
                "preview_url": "https://truthsocial.com/icons/missing.png",
                "meta": {
                    "original": {
                        "width": 1280,
                        "height": 720,
                        "duration": 12.5,
                        "bitrate": 1500000,
                        "frame_rate": "30/1",
                    },
                    "blurhash": "LEH~z",
                },
            }
        ],
        "account": {
            "id": "99",
            "username": "test",
            "acct": "test",
            "display_name": "T",
            "followers_count": 1,
            "following_count": 0,
            "statuses_count": 1,
            "locked": False,
            "bot": False,
            "group": False,
        },
    }
    full = ts._normalize_post(raw, author_mode="full")
    assert full["links"] == [{"url": "https://www.whitehouse.gov/election-integrity/"}]
    assert full["externalVideoId"] == "v6surln"
    assert full["externalVideoUrl"] == "https://rumble.com/v6surln"
    assert full["engagement"]["upvotes"] == 3
    assert full["engagement"]["downvotes"] == 1
    assert full["card"]["title"] == "Election Integrity"
    assert full["media"][0]["previewUrl"] is None
    assert full["media"][0]["meta"]["width"] == 1280
    assert full["media"][0]["durationSeconds"] == 12.5
    assert full["author"]["followers"] == 1

    slim = ts._normalize_post(raw, author_mode="slim")
    assert set(slim["author"].keys()) == {
        "id",
        "username",
        "displayName",
        "avatar",
        "verified",
    }
    assert "followers" not in slim["author"]


def test_scaled_posts_native_floor():
    assert ts._scaled_posts(1) == 2
    assert ts._scaled_posts(20) == 17


def test_normalize_post_chain_mentions_poll():
    """SC parity: reply/quote/reblog + structured mentions/tags/poll (shared mapper)."""
    raw = {
        "id": "100",
        "content": "<p>QT <a href=\"https://truthsocial.com/@other\">@other</a></p>",
        "in_reply_to_id": None,
        "in_reply_to_account_id": None,
        "quote_id": "50",
        "visibility": "public",
        "spoiler_text": "",
        "sponsored": False,
        "pinned": False,
        "group": False,
        "mentions": [
            {
                "id": "7",
                "username": "other",
                "acct": "other",
                "url": "https://truthsocial.com/@other",
            }
        ],
        "tags": [{"name": "election", "url": "https://truthsocial.com/tags/election"}],
        "poll": {
            "id": "p1",
            "expires_at": "2026-08-06T00:00:00.000Z",
            "expired": False,
            "multiple": False,
            "votes_count": 10,
            "options": [
                {"title": "Yes", "votes_count": 6},
                {"title": "No", "votes_count": 4},
            ],
        },
        "quote": {
            "id": "50",
            "content": "<p>Original</p>",
            "account": {
                "id": "8",
                "username": "source",
                "display_name": "Source",
                "followers_count": 9,
                "statuses_count": 1,
                "locked": False,
                "bot": False,
                "group": False,
            },
            "reblogs_count": 100,
            "favourites_count": 200,
            "replies_count": 3,
        },
        "reblog": None,
        "account": {
            "id": "99",
            "username": "test",
            "display_name": "T",
            "followers_count": 1,
            "statuses_count": 1,
            "locked": False,
            "bot": False,
            "group": False,
        },
    }
    out = ts._normalize_post(raw, author_mode="slim")
    assert out["quoteId"] == "50"
    assert out["quote"]["id"] == "50"
    assert out["quote"]["text"] == "Original"
    assert out["quote"]["engagement"]["reblogs"] == 100
    assert "followers" not in (out["quote"].get("author") or {})
    assert "inReplyToId" not in out
    assert "reblog" not in out
    assert out["mentions"] == [
        {
            "id": "7",
            "username": "other",
            "acct": "other",
            "url": "https://truthsocial.com/@other",
        }
    ]
    assert out["tags"] == [
        {"name": "election", "url": "https://truthsocial.com/tags/election"}
    ]
    assert out["poll"]["options"][0]["votes"] == 6
    assert out["visibility"] == "public"
    assert out["sponsored"] is False
    assert out["pinned"] is False
    assert out["group"] is False
    assert "spoilerText" not in out  # empty → omit
    # Session-only flags must stay out.
    assert "favourited" not in out
    assert "reblogged" not in out
    assert "bookmarked" not in out


def test_normalize_post_reblog_nested():
    raw = {
        "id": "200",
        "content": "",
        "reblogs_count": 0,
        "favourites_count": 0,
        "replies_count": 0,
        "reblog": {
            "id": "199",
            "content": "<p>Boosted truth</p>",
            "reblogs_count": 5000,
            "favourites_count": 9000,
            "replies_count": 100,
            "account": {
                "id": "1",
                "username": "real_author",
                "display_name": "Real",
                "followers_count": 1000,
                "statuses_count": 50,
                "locked": False,
                "bot": False,
                "group": False,
            },
        },
        "account": {
            "id": "2",
            "username": "booster",
            "display_name": "Booster",
            "followers_count": 10,
            "statuses_count": 3,
            "locked": False,
            "bot": False,
            "group": False,
        },
    }
    out = ts._normalize_post(raw, author_mode="slim")
    assert out["author"]["username"] == "booster"
    assert out["reblog"]["id"] == "199"
    assert out["reblog"]["text"] == "Boosted truth"
    assert out["reblog"]["engagement"]["likes"] == 9000
    assert out["reblog"]["author"]["username"] == "real_author"
    # No reblog-of-reblog nesting.
    assert "reblog" not in out["reblog"]
