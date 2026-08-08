"""Playlist cursor: buffer leftover first-page ids so page-2 does not skip."""

from __future__ import annotations

from app.services.youtube_native import (
    _decode_playlist_cursor,
    _encode_playlist_cursor,
)


def test_playlist_cursor_round_trip_buffers_ids() -> None:
    cur = _encode_playlist_cursor(
        ids=["aaaaaaaaaaa", "bbbbbbbbbbb"],
        continuations=["tokA"],
        total_videos=200,
        playlist_id="PLtest",
    )
    assert cur and cur.startswith("yp1.")
    decoded = _decode_playlist_cursor(cur)
    assert decoded is not None
    assert decoded["ids"] == ["aaaaaaaaaaa", "bbbbbbbbbbb"]
    assert decoded["c"] == ["tokA"]
    assert decoded["tv"] == 200
    assert decoded["pid"] == "PLtest"


def test_playlist_cursor_empty_when_no_more() -> None:
    assert _encode_playlist_cursor(ids=[], continuations=[], total_videos=200) is None


def test_playlist_cursor_accepts_bare_innertube_token() -> None:
    decoded = _decode_playlist_cursor("rawContinuationToken")
    assert decoded is not None
    assert decoded["ids"] == []
    assert decoded["c"] == ["rawContinuationToken"]
