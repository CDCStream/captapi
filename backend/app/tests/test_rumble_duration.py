"""Rumble duration schema: durationSeconds + durationText only."""

from __future__ import annotations

from app.routers import rumble
from app.services import rumble_video_native as native


def test_stamp_duration_from_clock_string() -> None:
    out = rumble._stamp_duration(
        {"duration": "1:26:25", "durationFormatted": "01:26:25"}
    )
    assert out["durationSeconds"] == 5185
    assert out["durationText"] == "1:26:25"
    assert "duration" not in out
    assert "durationFormatted" not in out


def test_stamp_duration_from_seconds() -> None:
    out = rumble._stamp_duration({"durationSeconds": 55})
    assert out["durationSeconds"] == 55
    assert out["durationText"] == "0:55"
    assert "duration" not in out
    assert "durationFormatted" not in out


def test_normalize_az_video_duration_pair() -> None:
    out = rumble._normalize_az_video(
        {
            "object_type": "video",
            "permalink_id": "v7cv2cc",
            "embed_id": "v7cv2cc",
            "title": "Sample",
            "duration": "1:26:25",
            "by": {"name": "Show", "url": "https://rumble.com/c/bongino"},
            "rumble_votes": {"num_votes_up": 10, "num_votes_down": 1},
            "comments": {"count": 3},
            "views": 100,
            "url": "https://rumble.com/v7cv2cc-sample.html",
            "upload_date": "2026-07-17T12:18:39+00:00",
        },
        include_description=False,
    )
    assert out["durationSeconds"] == 5185
    assert out["durationText"] == "1:26:25"
    assert "duration" not in out
    assert "durationFormatted" not in out
    assert "embedUrl" not in out
    assert "embedId" not in out


def test_normalize_az_keeps_distinct_embed_id() -> None:
    out = rumble._normalize_az_video(
        {
            "permalink_id": "v7cv2cc",
            "embed_id": "v7aoh22",
            "title": "Sample",
            "duration": 90,
            "by": {"name": "Show", "url": "https://rumble.com/c/bongino"},
            "url": "https://rumble.com/v7cv2cc-sample.html",
        },
        include_description=False,
    )
    assert out["embedId"] == "v7aoh22"
    assert out["embedUrl"] == "https://rumble.com/embed/v7aoh22/"
    assert out["durationSeconds"] == 90
    assert out["durationText"] == "1:30"


def test_apply_embedjs_drops_legacy_duration() -> None:
    card = {
        "id": "v7cv2cc",
        "duration": "1:26:25",
        "durationFormatted": "01:26:25",
    }
    native.apply_embedjs(card, {"duration": 5185, "video": "v7aoh22"})
    assert card["durationSeconds"] == 5185
    assert card["durationText"] == "1:26:25"
    assert "duration" not in card
    assert "durationFormatted" not in card


def test_streams_from_media_uses_height_keeps_bitrate_variants() -> None:
    media = {
        "mp4": {
            "240": {
                "url": "https://cdn.example/baa.mp4?expire=2000000000",
                "meta": {"bitrate": 400, "w": 640, "h": 360},
            },
            "1080": {
                "url": "https://cdn.example/haa.mp4?expire=2000000000",
                "meta": {"bitrate": 3985, "w": 1920, "h": 1080},
            },
            "1081": {
                "url": "https://cdn.example/aaa.mp4?expire=2000000000",
                "meta": {"bitrate": 8051, "w": 1920, "h": 1080},
            },
            "480": {
                "url": "https://cdn.example/caa.mp4",
                "meta": {"bitrate": 1005, "w": 854, "h": 480},
            },
            "360": {
                "url": "https://cdn.example/daa.mp4",
                "meta": {"bitrate": 600, "w": 640, "h": 360},
            },
            "720": {
                "url": "https://cdn.example/eaa.mp4",
                "meta": {"bitrate": 2000, "w": 1280, "h": 720},
            },
        },
        "audio": {
            "192": {
                "url": "https://cdn.example/gaa.aac",
                "meta": {"bitrate": 192, "w": 0, "h": 0},
            }
        },
        "timeline": {
            "180": {
                "url": "https://cdn.example/timeline.jpg",
                "meta": {"bitrate": 0, "w": 180, "h": 180},
            }
        },
    }
    streams = native._streams_from_media(media)
    assert len(streams) == 6
    assert all(set(s.keys()) == set(native.STREAM_KEYS) for s in streams)
    assert all(s["type"] == "video/mp4" for s in streams)
    assert all(native.quality_from_height(s["height"]) == s["quality"] for s in streams)
    assert [s["quality"] for s in streams].count("1080p") == 2
    assert "1081p" not in [s["quality"] for s in streams]
    # Upstream key "240" with h=360 → 360p (not 240p).
    assert any(s["quality"] == "360p" and s["url"].endswith("baa.mp4?expire=2000000000") for s in streams)
    assert all(not str(s.get("type") or "").startswith("audio") for s in streams)
    bitrates_1080 = sorted(
        s["bitrateKbps"] for s in streams if s["quality"] == "1080p"
    )
    assert bitrates_1080 == [3985, 8051]
    audio = native._audio_streams_from_media(media)
    assert len(audio) == 1
    assert audio[0]["type"] == "audio/aac"
    assert audio[0]["bitrateKbps"] == 192
    assert audio[0]["width"] is None and audio[0]["height"] is None
    assert audio[0]["quality"] is None
    track = native._thumbnail_track_from_media(media)
    assert track and track["url"].endswith("timeline.jpg")
    # apply_embedjs must not leak media keyed maps.
    card: dict = {"id": "v7cv2cc", "streams": []}
    native.apply_embedjs(
        card,
        {
            "video": "v7aoh22",
            "ua": {"mp4": media["mp4"], "audio": media["audio"], "timeline": media["timeline"]},
        },
    )
    assert "media" not in card
    assert len(card["streams"]) == 6
    assert all(s["url"] != track["url"] for s in card["streams"])


def test_votes_compact_marks_likes_approximate() -> None:
    html = 'title="15.5K Likes | 194 Dislikes"'
    likes, dislikes, approx = native._votes_from_html(html)
    assert likes == 15500
    assert dislikes == 194
    assert approx is True


def test_normalize_az_always_emits_is_live() -> None:
    out = rumble._normalize_az_video(
        {
            "permalink_id": "vfresh",
            "title": "Just posted",
            "duration": 72,
            "views": 0,
            "url": "https://rumble.com/vfresh-just-posted.html",
            "by": {"name": "Show", "url": "https://rumble.com/c/bongino"},
        },
        include_description=False,
    )
    assert out["isLive"] is False
    assert out["type"] == "video"
    # Zero views with no engagement can stay 0 (truly unwatched).
    assert out["views"] == 0


def test_honest_views_zero_with_engagement_is_null() -> None:
    assert native.honest_views(0, likes=26, comments=3) is None
    assert native.honest_views(0, likes=0, comments=0) == 0
    assert native.honest_views(12, likes=26, comments=3) == 12
    assert native.honest_views(None, likes=1) is None


def test_to_utc_published_at_normalizes_offset() -> None:
    assert (
        native.to_utc_published_at("2026-07-17T08:18:39-04:00")
        == "2026-07-17T12:18:39+00:00"
    )
    assert (
        native.to_utc_published_at("2026-07-17T12:18:39+00:00")
        == "2026-07-17T12:18:39+00:00"
    )
    # Display title= strings must never leak.
    assert native.to_utc_published_at("Friday, July 17, 2026 08:33 AM -04") is None


def test_normalize_video_search_shape_and_utc() -> None:
    out = rumble._normalize_video(
        {
            "id": "vsearch1",
            "url": "https://rumble.com/vsearch1-clip.html",
            "title": "Clip",
            "channel": "Show",
            "channelUrl": "https://rumble.com/c/bongino",
            "views": 0,
            "likes": 26,
            "comments": 3,
            "duration": "1:26:25",
            "publishedAt": "2026-07-17T08:18:39-04:00",
            "thumbnail": "https://cdn.example/t.jpg",
        }
    )
    assert out["channelHandle"] == "bongino"
    assert out["isLive"] is False
    assert out["type"] == "video"
    assert out["shareUrl"] == "https://rumble.com/share/vsearch1"
    assert out["durationSeconds"] == 5185
    assert out["durationText"] == "1:26:25"
    assert out["publishedAt"] == "2026-07-17T12:18:39+00:00"
    assert out["views"] is None
    assert "duration" not in out
    # Uniform key set even when scrape fields are missing on siblings.
    sparse = rumble._normalize_video(
        {"id": "v2", "url": "https://rumble.com/v2-x.html", "title": "X"}
    )
    assert set(out.keys()) == set(sparse.keys()) == set(rumble.RUMBLE_ITEM_KEYS)
    assert sparse["channel"] is None
    assert sparse["dislikes"] is None


def test_normalize_comment_iso_published_at() -> None:
    from app.services import rumble_comments_native as comments_native

    html = """
    <li class="comment-item" data-comment-id="1" data-num-replies="0" data-username="alice">
      <p class="comment-text">Hello</p>
      <span class="rumbles-vote-up"><span class="rumbles-up-votes">2</span></span>
      <time class="comments-meta-post-time" datetime="2026-07-17T08:33:12-04:00"
        title="Friday, July 17, 2026 08:33 AM -04">July 17, 2026</time>
    </li>
    """
    raw = comments_native.parse_comments_html(html, limit=5)
    assert raw[0]["publishedAt"] == "2026-07-17T12:33:12+00:00"
    out = rumble._normalize_comment(raw[0])
    assert out["publishedAt"] == "2026-07-17T12:33:12+00:00"
    assert "createdAt" not in out  # single field — not a null-padded alias
    # title= display must not win if somehow passed in.
    bad = rumble._normalize_comment(
        {"id": "9", "text": "x", "createdAt": "Friday, July 17, 2026 08:33 AM -04"}
    )
    assert bad["publishedAt"] is None
    assert "createdAt" not in bad
    # datetime before class still resolves (U1).
    flipped = comments_native.parse_comments_html(
        '<li class="comment-item" data-comment-id="8" data-num-replies="0" '
        'data-username="z"><p class="comment-text">Z</p>'
        '<time datetime="2026-07-17T08:33:12-04:00" class="comments-meta-post-time">'
        "July 17</time></li>",
        limit=5,
    )
    assert flipped[0]["publishedAt"] == "2026-07-17T12:33:12+00:00"


def test_normalize_az_nulls_impossible_zero_views() -> None:
    out = rumble._normalize_az_video(
        {
            "permalink_id": "vfresh",
            "title": "Just posted",
            "duration": 72,
            "views": 0,
            "url": "https://rumble.com/vfresh-just-posted.html",
            "by": {"name": "Show", "url": "https://rumble.com/c/bongino"},
            "rumble_votes": {"num_votes_up": 26, "num_votes_down": 0},
            "comments": {"count": 3},
        },
        include_description=False,
    )
    assert out["views"] is None
    assert out["likes"] == 26
    assert out["comments"] == 3
