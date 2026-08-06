"""YouTube audio download + speech-to-text helpers for /audio-transcript.

Captions stay on /transcript. This module pulls audio (yt-dlp) and runs
Whisper-class ASR. Sync path is duration-capped under Cloudflare's 125s proxy
read timeout (see measured e2e in the router constants).
"""

from __future__ import annotations

import asyncio
import math
import tempfile
from pathlib import Path
from typing import Any

import structlog

from app.services.youtube_native import _player_android

log = structlog.get_logger(__name__)

_YT_AUDIO_FORMAT = "bestaudio[ext=m4a]/bestaudio/best"
_YT_AUDIO_BITRATE = "48"


def credits_for_duration(duration_seconds: float | int) -> int:
    """ceil(minutes) x 2 — OpenAI whisper-1 is ~$0.006/min; 2 credits ~= $0.009."""
    secs = max(0.0, float(duration_seconds or 0.0))
    minutes = max(1, math.ceil(secs / 60.0)) if secs > 0 else 1
    return minutes * 2


async def video_duration_seconds(video_id: str) -> int | None:
    """Cheap ANDROID player metadata — duration before any STT spend."""
    vid = (video_id or "").strip()
    if not vid:
        return None
    player = await _player_android(vid)
    if not isinstance(player, dict):
        return None
    status = ((player.get("playabilityStatus") or {}).get("status") or "").upper()
    details = player.get("videoDetails") if isinstance(player.get("videoDetails"), dict) else {}
    raw = details.get("lengthSeconds")
    try:
        length = int(raw) if raw is not None else 0
    except (TypeError, ValueError):
        length = 0
    if length <= 0:
        return None
    if status and status not in {"OK", "LIVE_STREAM_OFFLINE"}:
        sd = player.get("streamingData")
        if not sd and status in {"ERROR", "UNPLAYABLE", "LOGIN_REQUIRED"}:
            return None
    return length


def playability_blocks_audio(player: dict[str, Any] | None) -> str | None:
    """Return an error code when the video cannot be transcribed, else None."""
    if not isinstance(player, dict):
        return "video_unavailable"
    status = ((player.get("playabilityStatus") or {}).get("status") or "").upper()
    if status in {"OK", "LIVE_STREAM_OFFLINE", ""}:
        return None
    if status == "LOGIN_REQUIRED":
        return "login_required"
    if status == "UNPLAYABLE":
        reason = ((player.get("playabilityStatus") or {}).get("reason") or "").lower()
        if "private" in reason:
            return "private"
        if "age" in reason:
            return "age_restricted"
        return "unplayable"
    if status == "ERROR":
        return "video_unavailable"
    return "video_unavailable"


async def extract_audio_bytes(video_id: str) -> tuple[bytes, float, str]:
    """Download audio via yt-dlp -> (bytes, duration_seconds, filename)."""
    vid = (video_id or "").strip()
    if not vid:
        raise RuntimeError("missing_video_id")

    def _run() -> tuple[bytes, float, str]:
        import yt_dlp

        url = f"https://www.youtube.com/watch?v={vid}"
        with tempfile.TemporaryDirectory(prefix="yt-asr-") as tmp:
            outtmpl = str(Path(tmp) / f"{vid}.%(ext)s")
            opts: dict[str, Any] = {
                "format": _YT_AUDIO_FORMAT,
                "outtmpl": outtmpl,
                "quiet": True,
                "no_warnings": True,
                "noprogress": True,
                "noplaylist": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "m4a",
                        "preferredquality": _YT_AUDIO_BITRATE,
                    }
                ],
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            duration = float((info or {}).get("duration") or 0.0)
            path: Path | None = None
            for ext in (".m4a", ".mp3", ".webm", ".opus", ".mp4", ".aac"):
                candidate = Path(tmp) / f"{vid}{ext}"
                if candidate.exists() and candidate.stat().st_size > 0:
                    path = candidate
                    break
            if path is None:
                files = sorted(Path(tmp).glob(f"{vid}*"))
                path = files[0] if files else None
            if path is None or not path.exists():
                raise RuntimeError("audio_extract_empty")
            raw = path.read_bytes()
            if not raw:
                raise RuntimeError("audio_extract_empty")
            return raw, duration, path.name

    return await asyncio.to_thread(_run)


def segments_to_ms(whisper_segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map Whisper start/end seconds -> uniform {text,startMs,endMs}."""
    out: list[dict[str, Any]] = []
    for seg in whisper_segments:
        if not isinstance(seg, dict):
            continue
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        start = float(seg.get("start") or 0.0)
        end = float(seg.get("end") if seg.get("end") is not None else start)
        start_ms = int(round(max(start, 0.0) * 1000))
        end_ms = int(round(max(end, start) * 1000))
        out.append({"text": text, "startMs": start_ms, "endMs": end_ms})
    return out