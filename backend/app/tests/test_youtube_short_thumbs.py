from __future__ import annotations

from app.services.youtube_native import (
    is_auto_frame_still_url,
    parse_count_text_meta,
    prefer_short_thumbnails,
)


def test_frame2_still_detection() -> None:
    assert is_auto_frame_still_url("https://i.ytimg.com/vi/abc/hq2.jpg")
    assert is_auto_frame_still_url("https://i.ytimg.com/vi/abc/mq2.jpg?sqp=1")
    assert is_auto_frame_still_url("https://i.ytimg.com/vi/abc/2.jpg")
    assert not is_auto_frame_still_url("https://i.ytimg.com/vi/abc/maxresdefault.jpg")
    assert not is_auto_frame_still_url("https://i.ytimg.com/vi/abc/oardefault.jpg")


def test_prefer_vertical_over_landscape() -> None:
    thumbs, url = prefer_short_thumbnails(
        "abcdefghijk",
        [
            {"url": "https://i.ytimg.com/vi/abcdefghijk/hq2.jpg", "width": 480, "height": 360},
            {"url": "https://i.ytimg.com/vi/abcdefghijk/oar2.jpg", "width": 405, "height": 720},
        ],
    )
    assert len(thumbs) == 1
    assert thumbs[0]["height"] == 720
    assert "oar2" in (url or "")


def test_frame2_only_falls_back_to_oardefault() -> None:
    thumbs, url = prefer_short_thumbnails(
        "abcdefghijk",
        [
            {"url": "https://i.ytimg.com/vi/abcdefghijk/hq2.jpg", "width": 480, "height": 360},
            {"url": "https://i.ytimg.com/vi/abcdefghijk/sd2.jpg", "width": 640, "height": 480},
        ],
    )
    assert "oardefault.jpg" in (url or "")
    assert any("maxresdefault" in (t.get("url") or "") for t in thumbs)


def test_parse_count_text_meta_marks_compact() -> None:
    n, approx = parse_count_text_meta("11K")
    assert n == 11000
    assert approx is True
    n2, approx2 = parse_count_text_meta("11,000")
    assert n2 == 11000
    assert approx2 is False
