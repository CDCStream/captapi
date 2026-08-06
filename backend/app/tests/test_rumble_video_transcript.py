"""Rumble video transcript — VTT parse + language pick."""

from __future__ import annotations

from app.services import rumble_transcript as rt
from app.services.transcript_segments import parse_webvtt


ROLLING_VTT = """WEBVTT

NOTE rolling captions

1
00:00:00.160 --> 00:00:01.920
Hello world

00:00:01.920 --> 00:00:03.400
Hello world

00:00:03.400 --> 00:00:05.000
<c>Next</c> <i>line</i>
"""


def test_parse_webvtt_dedupes_rolling_captions() -> None:
    segs = parse_webvtt(ROLLING_VTT)
    assert segs == [
        {"text": "Hello world", "startMs": 160, "endMs": 1920},
        {"text": "Next line", "startMs": 3400, "endMs": 5000},
    ]
    shapes = {tuple(sorted(s.keys())) for s in segs}
    assert shapes == {("endMs", "startMs", "text")}
    assert all(isinstance(s["startMs"], int) for s in segs)
    assert all(s["endMs"] > s["startMs"] for s in segs)
    assert all(i == 0 or segs[i]["text"] != segs[i - 1]["text"] for i in range(len(segs)))


def test_pick_first_track_without_language() -> None:
    track, err, avail = rt.pick_caption_track(
        [{"code": "en-auto", "language": "English (auto)", "url": "https://x/a.vtt"}],
        None,
    )
    assert err is None
    assert track and track["code"] == "en-auto"
    assert avail == [{"code": "en-auto", "language": "English (auto)"}]


def test_pick_en_matches_en_auto() -> None:
    track, err, _ = rt.pick_caption_track(
        [{"code": "en-auto", "language": "English (auto)", "url": "https://x/a.vtt"}],
        "en",
    )
    assert err is None
    assert track and track["code"] == "en-auto"


def test_language_not_available() -> None:
    track, err, avail = rt.pick_caption_track(
        [{"code": "en-auto", "language": "English (auto)", "url": "https://x/a.vtt"}],
        "fr",
    )
    assert track is None
    assert err == "language_not_available"
    assert avail == [{"code": "en-auto", "language": "English (auto)"}]


def test_no_captions() -> None:
    track, err, avail = rt.pick_caption_track([], "en")
    assert track is None
    assert err == "no_captions"
    assert avail == []