"""Cross-endpoint Rumble regression guards (date / key-set / raw maps)."""

from __future__ import annotations

import base64
import json
import re
from typing import Any

from app.routers import rumble
from app.services import rumble_comments_native as comments_native
from app.services import rumble_video_native as native
from app.utils.media_urls import cdn_expires_at

ISO = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?(Z|[+-]\d{2}:\d{2})$"
)


def _walk(obj: Any, path: str = "$"):
    if isinstance(obj, dict):
        yield path, obj
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")
        return
    else:
        return
    for k, v in obj.items():
        yield from _walk(v, f"{path}.{k}")


def _assert_no_all_null_fields(body: Any) -> None:
    """No media/comment array field may be null on 100% of rows.

    Top-level video cards intentionally sparse-null optional engagement fields.
    ``expiresAt`` on unsigned video-details streams is documented as null.
    """

    def _check(obj: Any, path: str = "$") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                _check(v, f"{path}.{k}")
        elif isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
            mediaish = path.endswith(
                (".streams", ".audioStreams", ".captions", ".comments")
            )
            if mediaish:
                keys = set().union(*(x.keys() for x in obj))
                for key in keys:
                    if (
                        key == "expiresAt"
                        and path.endswith((".streams", ".audioStreams", ".captions"))
                        and ".videos[" not in path
                    ):
                        # Unsigned video-details CDN — null is correct.
                        continue
                    # Audio rows keep width/height/quality null by design.
                    if path.endswith(".audioStreams") and key in {
                        "width",
                        "height",
                        "quality",
                    }:
                        continue
                    vals = [x.get(key) for x in obj]
                    if vals and all(v is None for v in vals):
                        raise AssertionError(
                            f"field {key!r} is null on 100% of rows at {path}"
                        )
            for i, v in enumerate(obj):
                _check(v, f"{path}[{i}]")

    _check(body)


def _assert_rumble_guards(body: Any) -> None:
    for path, node in _walk(body):
        if not isinstance(node, dict):
            continue
        for k, v in node.items():
            if isinstance(v, str) and re.search(r"(At|Date)$", k):
                assert ISO.match(v), f"non-ISO date at {path}.{k}: {v!r}"
        keys = list(node.keys())
        if len(keys) > 1 and all(re.fullmatch(r"\d+", k) for k in keys):
            raise AssertionError(f"raw upstream map leaked at {path}: {keys}")

    def _check_arrays(obj: Any, path: str = "$") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                _check_arrays(v, f"{path}.{k}")
        elif isinstance(obj, list):
            if len(obj) > 1 and isinstance(obj[0], dict):
                # Canonical keys must be present on every row. Optional extras
                # (embedId/embedUrl) may differ — omit means not applicable.
                if path.endswith(".results"):
                    required = set(rumble.RUMBLE_ITEM_KEYS)
                elif path.endswith(".videos"):
                    required = set(rumble.RUMBLE_CHANNEL_ITEM_KEYS)
                elif path.endswith(".comments"):
                    required = {
                        "platform",
                        "id",
                        "text",
                        "author",
                        "likes",
                        "replyCount",
                        "publishedAt",
                    }
                elif path.endswith(".audioStreams"):
                    required = set(native.STREAM_KEYS)
                elif path.endswith(".streams"):
                    # Channel listing: lean signed-URL shape. Details: full meta.
                    if ".videos[" in path:
                        required = set(native.CHANNEL_STREAM_KEYS)
                    else:
                        required = set(native.STREAM_KEYS)
                elif path.endswith(".captions"):
                    required = set(native.CAPTION_KEYS)
                else:
                    required = None
                if required is not None:
                    for o in obj:
                        if isinstance(o, dict):
                            missing = required - set(o.keys())
                            assert not missing, f"missing keys at {path}: {missing}"
                            if path.endswith(
                                (".streams", ".audioStreams", ".captions")
                            ):
                                assert set(o.keys()) == required, (
                                    f"extra/missing keys at {path}: "
                                    f"{set(o.keys()) ^ required}"
                                )
                else:
                    sigs = {tuple(sorted(o.keys())) for o in obj if isinstance(o, dict)}
                    assert len(sigs) == 1, f"uneven key sets at {path}: {sigs}"
            for i, v in enumerate(obj):
                _check_arrays(v, f"{path}[{i}]")

    _check_arrays(body)
    _assert_no_all_null_fields(body)


def _jwt_url(exp: int = 2_000_000_000) -> str:
    header = (
        base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode())
        .decode()
        .rstrip("=")
    )
    payload = (
        base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode())
        .decode()
        .rstrip("=")
    )
    tok = f"{header}.{payload}.sig"
    return f"https://cdn.example/play/{tok}"


def test_guard_search_rows_uniform() -> None:
    rows = [
        rumble._normalize_video(
            {
                "id": "a",
                "url": "https://rumble.com/va-a.html",
                "title": "A",
                "channel": "Show",
                "channelUrl": "https://rumble.com/c/show",
                "channelVerified": True,
                "likes": 1,
                "dislikes": 0,
                "comments": 2,
                "duration": "1:00",
                "publishedAt": "2026-07-17T08:18:39-04:00",
            }
        ),
        rumble._normalize_video(
            {"id": "b", "url": "https://rumble.com/vb-b.html", "title": "B"}
        ),
        rumble._normalize_video(
            {
                "id": "c",
                "url": "https://rumble.com/vc-c.html",
                "title": "C",
                "likes": 5,
            }
        ),
    ]
    _assert_rumble_guards({"results": rows})
    assert len({frozenset(r.keys()) for r in rows}) == 1


def test_guard_channel_videos_lean_streams() -> None:
    jwt_a = _jwt_url(2_000_000_000)
    jwt_b = _jwt_url(2_100_000_000)
    rows = [
        rumble._normalize_az_video(
            {
                "permalink_id": "v1",
                "title": "One",
                "duration": 10,
                "url": "https://rumble.com/v1-one.html",
                "by": {"name": "Show", "url": "https://rumble.com/c/bongino"},
                "views": 10,
                "videos": [
                    {"url": jwt_a, "type": "mp4"},
                    {"url": jwt_b, "type": "mp4"},
                ],
            },
            include_description=False,
        ),
        rumble._normalize_az_video(
            {
                "permalink_id": "v2",
                "title": "Two",
                "duration": 20,
                "url": "https://rumble.com/v2-two.html",
                "by": {},
                "views": 0,
                "rumble_votes": {"num_votes_up": 1, "num_votes_down": 0},
            },
            include_description=False,
        ),
    ]
    _assert_rumble_guards({"videos": rows})
    assert len({frozenset(r.keys()) for r in rows}) == 1
    streams = rows[0]["streams"]
    assert streams
    assert all(set(s.keys()) == set(native.CHANNEL_STREAM_KEYS) for s in streams)
    assert all(s["type"] == "video/mp4" for s in streams)
    assert all(ISO.match(s["expiresAt"] or "") for s in streams)
    assert streams[0]["expiresAt"] == "2033-05-18T03:33:20.000Z"


def test_cdn_expires_at_jwt_payload() -> None:
    url = _jwt_url(1_784_753_172)
    assert cdn_expires_at(url) == "2026-07-22T20:46:12.000Z"
    q = f"https://cdn.example/x.mp4?token={url.rsplit('/', 1)[-1]}"
    assert cdn_expires_at(q) == "2026-07-22T20:46:12.000Z"


def test_comment_title_published_at() -> None:
    """U1 — live DOM uses title= on a.comments-meta-post-time (no datetime)."""
    cases = [
        (
            '<li class="comment-item" data-comment-id="1" data-num-replies="0" '
            'data-username="a"><p class="comment-text">Hi</p>'
            '<a class="comments-meta-post-time whitespace-nowrap" '
            'href="#comment-1" title="Friday, July 17, 2026 08:33 AM -04">'
            "2 weeks ago</a></li>"
        ),
        (
            '<li class="comment-item" data-comment-id="2" data-num-replies="0" '
            'data-username="b"><p class="comment-text">Yo</p>'
            '<a class="comments-meta-post-time" href="#comment-2" '
            'title="Friday, July 17, 2026 04:42 PM -04">2 weeks ago</a></li>'
        ),
        (
            '<li class="comment-item" data-comment-id="3" data-num-replies="0" '
            'data-username="c"><p class="comment-text">Ep</p>'
            '<a class="comments-meta-post-time" data-time="1721214792">'
            "July 17</a></li>"
        ),
        (
            # Prefer datetime when present (future-proof); title is fallback.
            '<li class="comment-item" data-comment-id="4" data-num-replies="0" '
            'data-username="d"><p class="comment-text">Wrap</p>'
            '<a class="comments-meta-post-time" '
            'datetime="2026-07-19T12:00:00Z" '
            'title="Saturday, July 19, 2026 08:00 AM -04">July 19</a></li>'
        ),
    ]
    comments = []
    for html in cases:
        comments.extend(
            rumble._normalize_comment(c)
            for c in comments_native.parse_comments_html(html, limit=10)
        )
    assert len(comments) == 4
    assert all(ISO.match(c["publishedAt"] or "") for c in comments)
    assert comments[0]["publishedAt"] == "2026-07-17T12:33:00+00:00"
    assert comments[1]["publishedAt"] == "2026-07-17T20:42:00+00:00"
    assert all("createdAt" not in c for c in comments)
    _assert_rumble_guards({"comments": comments})


def test_guard_comments_iso_dates() -> None:
    html = (
        '<li class="comment-item" data-comment-id="1" data-num-replies="0" '
        'data-username="a"><p class="comment-text">Hi</p>'
        '<a class="comments-meta-post-time" href="#comment-1" '
        'title="Friday, July 17, 2026 08:33 AM -04">2 weeks ago</a></li>'
        '<li class="comment-item" data-comment-id="2" data-num-replies="0" '
        'data-username="b"><p class="comment-text">Yo</p>'
        '<a class="comments-meta-post-time" href="#comment-2" '
        'title="Monday, July 20, 2026 07:48 PM -04">2 weeks ago</a></li>'
    )
    comments = [
        rumble._normalize_comment(c)
        for c in comments_native.parse_comments_html(html, limit=10)
    ]
    _assert_rumble_guards({"comments": comments})
    assert all(ISO.match(c["publishedAt"]) for c in comments)
    assert comments[1]["publishedAt"] == "2026-07-20T23:48:00+00:00"
    assert all("createdAt" not in c for c in comments)


def test_guard_video_details_streams_uniform() -> None:
    card: dict[str, Any] = {
        "id": "v7cv2cc",
        "streams": [],
        "publishedAt": "2026-07-17T12:18:39+00:00",
    }
    native.apply_embedjs(
        card,
        {
            "video": "v7aoh22",
            "ua": {
                "mp4": {
                    "1080": {
                        "url": "https://cdn.example/a.mp4?expire=2000000000",
                        "meta": {"bitrate": 3985, "w": 1920, "h": 1080, "size": 1},
                    },
                    "1081": {
                        "url": "https://cdn.example/b.mp4?expire=2000000000",
                        "meta": {"bitrate": 8051, "w": 1920, "h": 1080, "size": 2},
                    },
                    "480": {
                        "url": "https://cdn.example/c.mp4?expire=2000000000",
                        "meta": {"bitrate": 1005, "w": 854, "h": 480, "size": 3},
                    },
                    # Metadata-less junk (U2) — must be dropped, not labeled 480p.
                    "481": {"url": "https://cdn.example/junk.mp4"},
                    # Timeline leak into mp4 bucket — drop (no h / wrong strip).
                    "180": {"url": "https://cdn.example/timeline.jpg"},
                },
                "audio": {
                    "192": {
                        "url": "https://cdn.example/c.aac?e=2000000000",
                        "meta": {"bitrate": 192, "w": 0, "h": 0, "size": 9000},
                    }
                },
                "timeline": {
                    "180": {
                        "url": "https://cdn.example/timeline.jpg",
                        "meta": {"bitrate": 0, "w": 180, "h": 180},
                    }
                },
            },
            "cc": {"en-auto": {"language": "English (auto)", "path": "/CwcHA.vtt"}},
        },
    )
    assert "media" not in card
    streams = card["streams"]
    assert len(streams) == 3
    assert all(set(s.keys()) == set(native.STREAM_KEYS) for s in streams)
    assert all(s["type"] == "video/mp4" for s in streams)
    assert streams[0]["height"] >= streams[-1]["height"]
    assert all(
        s["height"] is None or native.quality_from_height(s["height"]) == s["quality"]
        for s in streams
    )
    pairs = {(s["quality"], s["bitrateKbps"]) for s in streams}
    assert len(pairs) == len(streams)
    track_url = card["thumbnailTrack"]["url"]
    assert all(s["url"] != track_url for s in streams)
    assert all(s.get("expiresAt") for s in streams)

    audio = card["audioStreams"]
    assert len(audio) == 1
    assert audio[0]["width"] is None and audio[0]["height"] is None
    assert audio[0]["quality"] is None
    assert audio[0]["bitrateKbps"] == 192
    assert audio[0]["type"] == "audio/aac"
    assert set(audio[0].keys()) == set(native.STREAM_KEYS)

    assert isinstance(card.get("captions"), list)
    assert set(card["captions"][0].keys()) == set(native.CAPTION_KEYS)
    assert card["captions"][0]["url"].startswith("https://")
    _assert_rumble_guards(card)
