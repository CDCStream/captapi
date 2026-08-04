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
