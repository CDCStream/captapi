"""Shared contract for text-only transcript endpoints.

timingSource:
  - "captions" — real cue times from a caption track or Whisper
  - "none"     — text-only post/discussion; no media timeline

When timingSource is "none", segment start/duration/timestamp are null
(keys kept for schema parity with the captions path). Reading-time lives
only at the top level as estimatedReadSeconds (200 wpm).
"""

from __future__ import annotations

import re
from typing import Any

_PARAGRAPH_SPLIT_RE = re.compile(r"\n[\s\u00a0\u2007\u202f]*\n+")
_READ_WPM = 200.0

TIMING_CAPTIONS = "captions"
TIMING_NONE = "none"


def normalize_transcript_text(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return cleaned.replace("\u00a0", " ").strip()


def estimated_read_seconds(text: str, *, wpm: float = _READ_WPM) -> int:
    words = len((text or "").split())
    if words <= 0:
        return 0
    return max(1, round(words / wpm * 60.0))


def _split_paragraphs(cleaned: str) -> list[str]:
    parts = [p.strip() for p in _PARAGRAPH_SPLIT_RE.split(cleaned) if p.strip()]
    if len(parts) <= 1:
        lines = [ln.strip() for ln in cleaned.split("\n") if ln.strip()]
        substantial = [ln for ln in lines if len(ln.split()) >= 6]
        if len(substantial) >= 2:
            return substantial
        return [cleaned] if cleaned else []
    return parts


def attach_char_offsets(transcript: str, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Set charStart/charEnd so transcript[charStart:charEnd] == segment text."""
    pos = 0
    for seg in segments:
        text = seg.get("text") or ""
        idx = transcript.find(text, pos)
        if idx < 0:
            idx = transcript.find(text)
        if idx < 0:
            idx = pos
        seg["charStart"] = idx
        seg["charEnd"] = idx + len(text)
        pos = seg["charEnd"]
    return segments


def null_timing_fields() -> dict[str, None]:
    return {"start": None, "duration": None, "timestamp": None}


def paragraph_text_segments(text: str) -> tuple[str, list[dict[str, Any]], int]:
    """Normalize text, split paragraphs, return (transcript, segments, estimatedReadSeconds)."""
    transcript = normalize_transcript_text(text)
    if not transcript:
        return "", [], 0
    parts = _split_paragraphs(transcript)
    segments: list[dict[str, Any]] = []
    for i, part in enumerate(parts):
        row: dict[str, Any] = {
            "text": part,
            "index": i,
            "wordCount": len(part.split()),
            **null_timing_fields(),
        }
        segments.append(row)
    attach_char_offsets(transcript, segments)
    return transcript, segments, estimated_read_seconds(transcript)


def finalize_text_segments(
    transcript: str,
    segments: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Assign index/wordCount/char offsets + null timings on pre-built text segments."""
    out: list[dict[str, Any]] = []
    for i, seg in enumerate(segments):
        text = seg.get("text") or ""
        row = dict(seg)
        row["text"] = text
        row["index"] = i
        row["wordCount"] = len(text.split())
        row.update(null_timing_fields())
        out.append(row)
    attach_char_offsets(transcript, out)
    return out, estimated_read_seconds(transcript)