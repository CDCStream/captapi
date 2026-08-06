"""Extra audio-transcript unit coverage: song repetition + duration guard."""

from __future__ import annotations

from app.routers import youtube as yt
from app.services.openai_client import _is_valid_transcript
from app.services import youtube_audio as ya


def test_song_like_repetition_keeps_timed_segments_valid() -> None:
    """Chorus word reuse must not invalidate a multi-segment Whisper timeline."""
    lines = [
        "We're no strangers to love",
        "You know the rules and so do I",
        "A full commitment's what I'm thinking of",
        "You wouldn't get this from any other guy",
        "Never gonna give you up",
        "Never gonna let you down",
        "Never gonna run around and desert you",
        "Never gonna make you cry",
    ]
    segs = [
        {
            "text": line,
            "start": float(i * 10),
            "end": float(i * 10 + 8),
            "duration": 8.0,
        }
        for i, line in enumerate(lines)
    ]
    result = {
        "transcript": " ".join(s["text"] for s in segs),
        "transcriptSegments": segs,
        "wordCount": len(" ".join(lines).split()),
        "segments": len(segs),
    }
    assert _is_valid_transcript(result) is True
    ms = ya.segments_to_ms(segs)
    assert len(ms) == 8
    assert all(s["endMs"] > s["startMs"] for s in ms)


def test_exact_segment_loop_still_rejected() -> None:
    segs = [
        {"text": "Ben de.", "start": float(i), "end": float(i) + 0.5, "duration": 0.5}
        for i in range(10)
    ]
    result = {
        "transcript": " ".join(s["text"] for s in segs),
        "transcriptSegments": segs,
        "wordCount": 20,
        "segments": 10,
    }
    assert _is_valid_transcript(result) is False


def test_sync_cap_constants() -> None:
    assert yt._YT_ASR_SYNC_MAX_SECONDS == 20 * 60
    assert yt._YT_ASR_HARD_DEADLINE_SECS == 110