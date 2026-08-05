"""Kick clip mapper: HLS typing, vod URLs, displayName."""

from __future__ import annotations

from app.routers.kick import _normalize_clip, _person


def test_person_display_name_canonical():
    out = _person({"id": 1, "slug": "xqc", "username": "xQc"})
    assert out is not None
    assert out["username"] == "xqc"
    assert out["displayName"] == "xQc"
    assert out["name"] == "xQc"  # deprecated alias
    assert out["url"] == "https://kick.com/xqc"


def test_normalize_hls_and_vod_urls():
    raw = {
        "id": "clip_01KZ0X5PGT228PY3QEB3RMR3YC",
        "title": "Vegas farming sadges",
        "created_at": "2026-08-02T09:36:01.061092Z",
        "started_at": "2026-08-02T05:45:57Z",
        "duration": 38,
        "view_count": 62,
        "likes_count": 0,
        "thumbnail_url": "https://clips.kick.com/clips/fb/clip_01KZ0X5PGT228PY3QEB3RMR3YC/thumbnail.webp",
        "video_url": "https://clips.kick.com/clips/fb/clip_01KZ0X5PGT228PY3QEB3RMR3YC/playlist.m3u8",
        "clip_url": "https://clips.kick.com/clips/fb/clip_01KZ0X5PGT228PY3QEB3RMR3YC/playlist.m3u8",
        "privacy": "CLIP_PRIVACY_PUBLIC",
        "is_mature": False,
        "livestream_id": "120226226",
        "vod_starts_at": 29450,
        "vod": {"id": "8faf0a05-dcdf-4ab1-8538-e87c6eef573e"},
        "category": {
            "id": 15,
            "name": "Just Chatting",
            "slug": "just-chatting",
            "parent_category": "irl",
            "banner": "https://files.kick.com/images/subcategories/15/banner/x",
        },
        "channel": {"id": 668, "slug": "xqc", "username": "xQc"},
        "creator": {"id": 7458058, "slug": "ghosteld", "username": "Ghosteld"},
        "liked": True,
    }
    out = _normalize_clip(raw)
    assert out["url"] == "https://kick.com/xqc/clips/clip_01KZ0X5PGT228PY3QEB3RMR3YC"
    assert out["videoType"] == "hls"
    assert out["hlsUrl"] == out["videoUrl"]
    assert out["videoUrl"].endswith("playlist.m3u8")
    assert "mp4Url" not in out
    assert out["privacy"] == "public"
    assert "liked" not in out
    assert out["vod"] == {
        "id": "8faf0a05-dcdf-4ab1-8538-e87c6eef573e",
        "url": "https://kick.com/xqc/videos/8faf0a05-dcdf-4ab1-8538-e87c6eef573e",
        "urlWithOffset": "https://kick.com/xqc/videos/8faf0a05-dcdf-4ab1-8538-e87c6eef573e?t=29450",
    }
    assert out["channel"]["displayName"] == "xQc"
    assert out["creator"]["displayName"] == "Ghosteld"


def test_normalize_does_not_treat_m3u8_as_page_url():
    """SC confuses clip_url (HLS) with the web page — we keep url as the Kick page."""
    raw = {
        "id": "clip_abc",
        "clip_url": "https://clips.kick.com/clips/fb/clip_abc/playlist.m3u8",
        "video_url": "https://clips.kick.com/clips/fb/clip_abc/playlist.m3u8",
        "channel": {"slug": "xqc", "username": "xQc"},
    }
    out = _normalize_clip(raw)
    assert out["url"] == "https://kick.com/xqc/clips/clip_abc"
    assert out["url"] != out["videoUrl"]
