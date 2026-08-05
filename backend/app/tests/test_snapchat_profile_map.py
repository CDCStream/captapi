"""Snapchat profile mapper: unwrap protobuf wrappers, mediaType 0->image."""

from __future__ import annotations

import json
import re

from app.services import snapchat_native as sn


_PY_REPR = re.compile(r"^\{'")


def _walk_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_strings(v)
    elif isinstance(obj, str):
        yield obj


def test_val_unwraps_protobuf_wrapper():
    assert sn._val({"value": "029f2cc3-c0df-46c2-b610-485c137f9a0a"}) == (
        "029f2cc3-c0df-46c2-b610-485c137f9a0a"
    )
    assert sn._val("plain") == "plain"


def test_highlight_unwraps_id_and_title():
    raw = {
        "highlightId": {"value": "029f2cc3-c0df-46c2-b610-485c137f9a0a"},
        "storyTitle": {"value": "2025-26 NBA Finals"},
        "thumbnailUrl": {"value": "https://cdn/t.jpg"},
        "snapList": [
            {
                "snapIndex": 0,
                "snapId": {"value": "snap-a"},
                "snapMediaType": 0,
                "snapUrls": {
                    "mediaUrl": "https://cdn/a.jpg",
                    "mediaPreviewUrl": {"value": "https://cdn/p.jpg"},
                },
                "timestampInSec": {"value": "1780335408"},
            }
        ],
    }
    out = sn._highlight(raw)
    assert out is not None
    assert out["highlightId"] == "029f2cc3-c0df-46c2-b610-485c137f9a0a"
    assert out["storyTitle"] == "2025-26 NBA Finals"
    assert not _PY_REPR.match(out["highlightId"])
    assert not _PY_REPR.match(out["storyTitle"])
    for s in _walk_strings(out):
        assert not _PY_REPR.match(s), s


def test_media_type_image_and_video():
    image = sn._snap_row(
        {
            "snapIndex": 0,
            "snapId": {"value": "i1"},
            "snapMediaType": 0,
            "snapUrls": {"mediaUrl": "https://cdn/i.jpg"},
            "timestampInSec": {"value": "1"},
        }
    )
    video = sn._snap_row(
        {
            "snapIndex": 1,
            "snapId": {"value": "v1"},
            "snapMediaType": 1,
            "snapUrls": {"mediaUrl": "https://cdn/v.mp4"},
            "timestampInSec": {"value": "2"},
        }
    )
    assert image["snapMediaType"] == 0
    assert image["mediaType"] == "image"
    assert video["snapMediaType"] == 1
    assert video["mediaType"] == "video"


def test_story_snap_count_matches_list():
    raw = {
        "thumbnailUrl": {"value": "https://cdn/t.jpg"},
        "snapList": [
            {
                "snapIndex": 0,
                "snapId": {"value": "a"},
                "snapMediaType": 1,
                "snapUrls": {"mediaUrl": "https://cdn/a.mp4"},
                "timestampInSec": {"value": "10"},
            },
            {
                "snapIndex": 1,
                "snapId": {"value": "b"},
                "snapMediaType": 1,
                "snapUrls": {"mediaUrl": "https://cdn/b.mp4"},
                "timestampInSec": {"value": "11"},
            },
            {
                "snapIndex": 2,
                "snapId": {"value": "c"},
                "snapMediaType": 0,
                "snapUrls": {"mediaUrl": "https://cdn/c.jpg"},
                "timestampInSec": {"value": "12"},
            },
        ],
    }
    out = sn._story(raw)
    assert out["snapCount"] == 3
    assert len(out["snapList"]) == 3
    assert out["snapList"][2]["mediaType"] == "image"


def test_abs_url_adds_https():
    assert sn._abs_url("NBA.com") == "https://NBA.com"
    assert sn._abs_url("https://nba.com") == "https://nba.com"


def test_related_uses_avatar_and_url():
    rows = sn._related(
        [
            {
                "publicProfileInfo": {
                    "username": "team",
                    "title": "Team",
                    "profilePictureUrl": "https://cdn/a.jpg",
                    "badge": 1,
                }
            }
        ]
    )
    assert rows[0]["url"] == "https://www.snapchat.com/@team"
    assert rows[0]["avatar"] == "https://cdn/a.jpg"
    assert rows[0]["verified"] is True


def test_no_python_repr_in_serialized_highlights():
    mapped = sn._highlights(
        [
            {
                "highlightId": {"value": "abc"},
                "storyTitle": {"value": "Title"},
                "snapList": [],
            }
        ]
    )
    blob = json.dumps(mapped)
    assert "{'value'" not in blob
    assert mapped[0]["highlightId"] == "abc"
