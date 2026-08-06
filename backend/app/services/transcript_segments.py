"""Shared transcript segment shape for caption + ASR endpoints.

Every transcript surface (YouTube captions, YouTube audio-transcript, Rumble
captions, …) must emit identical ``segments[]`` element keys:

    { "text": str, "startMs": int, "endMs": int }

Do not invent a parallel mapper per endpoint — that is how streams[] /
ad-library/search drifted.
"""

from __future__ import annotations

import re
from typing import Any

SEGMENT_KEYS: tuple[str, ...] = ("text", "startMs", "endMs")

_VTT_TS = re.compile(
    r"(?:(\d{2,}):)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(?:(\d{2,}):)?(\d{2}):(\d{2})\.(\d{3})"
)
_VTT_TAG_RE = re.compile(r"<[^>]+>")
_NOTE_BLOCK_RE = re.compile(r"(?im)^\s*NOTE(?:\s.*)?$")


def finalise_segment(partial: dict[str, Any]) -> dict[str, Any] | None:
    """Force the canonical three-key segment; drop empty / invalid cues."""
    text = " ".join(str(partial.get("text") or "").split()).strip()
    if not text:
        return None
    try:
        start_ms = int(partial.get("startMs"))
        end_ms = int(partial.get("endMs"))
    except (TypeError, ValueError):
        return None
    if start_ms < 0:
        start_ms = 0
    if end_ms <= start_ms:
        end_ms = start_ms + 1
    return {"text": text, "startMs": start_ms, "endMs": end_ms}


def finalise_segments(rows: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Uniform key set + drop consecutive identical text (rolling captions)."""
    out: list[dict[str, Any]] = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        seg = finalise_segment(row)
        if seg is None:
            continue
        if out and out[-1]["text"] == seg["text"]:
            # Rolling auto-captions repeat the previous line — keep the earlier
            # timing window and skip the duplicate.
            continue
        out.append(seg)
    return out


def segments_from_seconds(
    rows: list[dict[str, Any]] | None,
    *,
    start_key: str = "start",
    end_key: str = "end",
) -> list[dict[str, Any]]:
    """Map Whisper-style second floats → canonical ms segments."""
    partials: list[dict[str, Any]] = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        text = row.get("text")
        try:
            start = float(row.get(start_key) or 0.0)
            end_raw = row.get(end_key)
            end = float(end_raw) if end_raw is not None else start
        except (TypeError, ValueError):
            continue
        partials.append(
            {
                "text": text,
                "startMs": int(round(max(start, 0.0) * 1000)),
                "endMs": int(round(max(end, start) * 1000)),
            }
        )
    return finalise_segments(partials)


def _vtt_ts_to_ms(
    hours: str | None, minutes: str, seconds: str, millis: str
) -> int:
    return (
        int(hours or 0) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1000
        + int(millis)
    )


def parse_webvtt(body: str) -> list[dict[str, Any]]:
    """Parse WebVTT → canonical ``{text,startMs,endMs}`` segments.

    Strips WEBVTT header, NOTE blocks, cue ids, and inline tags. De-duplicates
    consecutive identical cue text (auto-caption rolling artefact).
    """
    if not body or "-->" not in body:
        return []
    text = body.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", text.strip())
    partials: list[dict[str, Any]] = []
    for block in blocks:
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        if lines[0].upper().startswith("WEBVTT"):
            continue
        if _NOTE_BLOCK_RE.match(lines[0]):
            continue
        timing_idx = next((i for i, ln in enumerate(lines) if "-->" in ln), -1)
        if timing_idx < 0:
            continue
        m = _VTT_TS.search(lines[timing_idx])
        if not m:
            continue
        start_ms = _vtt_ts_to_ms(m.group(1), m.group(2), m.group(3), m.group(4))
        end_ms = _vtt_ts_to_ms(m.group(5), m.group(6), m.group(7), m.group(8))
        payload = " ".join(lines[timing_idx + 1 :])
        payload = _VTT_TAG_RE.sub("", payload)
        payload = (
            payload.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&nbsp;", " ")
            .strip()
        )
        if not payload:
            continue
        partials.append({"text": payload, "startMs": start_ms, "endMs": end_ms})
    return finalise_segments(partials)


def join_segment_text(segments: list[dict[str, Any]]) -> str:
    return " ".join(s["text"] for s in segments if s.get("text"))