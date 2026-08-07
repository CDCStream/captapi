"""Unit tests for Kwai post normalize: caption placeholders, transcript dedup, media."""

from __future__ import annotations

from app.routers import kwai as k
from app.utils.media_urls import cdn_expires_at


def test_placeholder_caption_is_empty_string():
    row = {
        "id": "1",
        "url": "https://www.kwai.com/@u/video/1",
        "caption": "...",
        "name": "U (u). Áudio original criado por U.",
        "transcript": "HELLO WORLDHELLO WORLD",
        "createTime": "2026-01-24T00:50:13Z",
        "duration": 10,
        "thumb": "https://example.com/t.webp",
        "playUrl": "https://aws-br-cdn.kwai.net/x.mp4?tag=1-1784753172-s-0-abc",
        "viewCount": 1,
        "likeCount": 2,
        "commentCount": 3,
        "shareCount": 4,
        "authorMeta": {
            "id": "eid",
            "username": "u",
            "name": "U",
            "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/x_t.jpg",
            "url": "https://www.kwai.com/@u",
        },
    }
    out = k._normalize_post(row)
    assert out["text"] == ""
    assert out["transcript"] == "HELLO WORLD"
    assert out["videoType"] == "mp4"
    assert out["mediaUrlsExpireAt"] == "2026-07-22T20:46:12.000Z"
    assert out["author"]["avatar"].endswith("_s.jpg")


def test_seo_title_not_used_as_caption():
    """Empty description + SEO name must not invent text (live fixture class)."""
    from app.services import kwai_native as native

    row = native._post_from_video_ld(
        {
            "@type": "VideoObject",
            "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5238962376325675745",
            "name": (
                "Topseriesfilmetv (topfilmeseseriesnatv). "
                "Áudio original criado por Topseriesfilmetv."
            ),
            "description": "",
            "contentUrl": "https://aws-br-cdn.kwai.net/x.mp4",
            "uploadDate": "2026-01-01T00:00:00Z",
        }
    )
    assert row is not None
    assert row["caption"] == ""
    assert "Áudio" in (row.get("name") or "")
    out = k._normalize_post(row, include_author=False)
    assert out["text"] == ""


def test_real_caption_verbatim():
    row = {
        "id": "2",
        "url": "https://www.kwai.com/@u/video/2",
        "caption": "#tag hello world",
        "name": "U (u). Áudio original criado por U.",
        "playUrl": "https://cdn.example/a.m3u8",
        "authorMeta": {"username": "u", "name": "U", "url": "https://www.kwai.com/@u"},
    }
    out = k._normalize_post(row, include_author=False)
    assert out["text"] == "#tag hello world"
    assert "transcript" not in out
    assert "author" not in out
    assert out["videoType"] == "hls"


def test_cdn_expires_at_kwai_tag():
    url = (
        "https://aws-br-cdn.kwai.net/upic/x.mp4?"
        "tag=1-1784753172-s-0-afgxvdpz8w-4a78f339bd4accdf"
    )
    assert cdn_expires_at(url) == "2026-07-22T20:46:12.000Z"


def test_author_card_and_list_hoist_helpers():
    meta = {
        "id": "eid",
        "username": "u",
        "name": "Name",
        "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/x_tw.webp",
        "url": "https://www.kwai.com/@u",
    }
    card = k._author_card(meta)
    assert card["avatar"].endswith("_s.jpg")
    assert card["displayName"] == "Name"
