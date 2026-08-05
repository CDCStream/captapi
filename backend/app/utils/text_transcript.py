"""Shared contract for text-only transcript endpoints.

timingSource:
  - "captions" — real cue times from a caption track or Whisper
  - "none"     — text-only post/discussion; no media timeline

When timingSource is "none", omit start / duration / timestamp entirely
(timingSource is the discriminator). Those keys are only for the future
"captions" branch. Reading-time lives only at top-level estimatedReadSeconds
(200 wpm).
"""

from __future__ import annotations

import re
from typing import Any

_PARAGRAPH_SPLIT_RE = re.compile(r"\n[\s\u00a0\u2007\u202f]*\n+")
_READ_WPM = 200.0
# Emoji / symbol runs — not words. URL tokens still count as one word.
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # misc pictographs / supplemental
    "\U00002700-\U000027BF"  # dingbats
    "\U00002600-\U000026FF"  # misc symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U0000FE0F"  # variation selector
    "\U0000200D"  # ZWJ
    "]+",
    flags=re.UNICODE,
)
_WORD_PUNCT_STRIP = ".,!?:;\"'`“”‘’()[]{}<>|/\\#"

TIMING_CAPTIONS = "captions"
TIMING_NONE = "none"


def normalize_transcript_text(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return cleaned.replace("\u00a0", " ").strip()


def count_words(text: str) -> int:
    """Count tokens that contain at least one letter or digit.

    Emoji-only leftovers and punctuation-only tokens (``&``, ``-``) are 0.
    URL tokens still count as 1.
    """
    n = 0
    for tok in (text or "").split():
        cleaned = _EMOJI_RE.sub("", tok).strip(_WORD_PUNCT_STRIP)
        if cleaned and any(ch.isalnum() for ch in cleaned):
            n += 1
    return n


def estimated_read_seconds(text: str, *, wpm: float = _READ_WPM) -> int:
    words = count_words(text)
    if words <= 0:
        return 0
    return max(1, round(words / wpm * 60.0))


def _split_paragraphs(cleaned: str) -> list[str]:
    parts = [p.strip() for p in _PARAGRAPH_SPLIT_RE.split(cleaned) if p.strip()]
    if len(parts) <= 1:
        lines = [ln.strip() for ln in cleaned.split("\n") if ln.strip()]
        substantial = [ln for ln in lines if count_words(ln) >= 6]
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


def caption_timing_fields(
    *, start: float | int, duration: float | int, timestamp: str
) -> dict[str, Any]:
    """Cue fields for timingSource='captions' only — never call for text posts."""
    return {"start": start, "duration": duration, "timestamp": timestamp}


def paragraph_text_segments(text: str) -> tuple[str, list[dict[str, Any]], int]:
    """Normalize text, split paragraphs, return (transcript, segments, estimatedReadSeconds).

    Segments omit start/duration/timestamp (timingSource is none).
    """
    transcript = normalize_transcript_text(text)
    if not transcript:
        return "", [], 0
    parts = _split_paragraphs(transcript)
    segments: list[dict[str, Any]] = []
    for i, part in enumerate(parts):
        segments.append(
            {
                "text": part,
                "index": i,
                "wordCount": count_words(part),
            }
        )
    attach_char_offsets(transcript, segments)
    return transcript, segments, estimated_read_seconds(transcript)


def finalize_text_segments(
    transcript: str,
    segments: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Assign index/wordCount/char offsets; omit cue keys (timingSource none)."""
    out: list[dict[str, Any]] = []
    for i, seg in enumerate(segments):
        text = seg.get("text") or ""
        row = {k: v for k, v in seg.items() if k not in {"start", "duration", "timestamp"}}
        row["text"] = text
        row["index"] = i
        row["wordCount"] = count_words(text)
        out.append(row)
    attach_char_offsets(transcript, out)
    return out, estimated_read_seconds(transcript)