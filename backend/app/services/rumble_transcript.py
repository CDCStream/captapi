"""Rumble video caption transcript — fetch published .vtt, no STT.

Segments share the canonical shape from ``transcript_segments`` with
YouTube audio-transcript (and any future caption surface).
"""

from __future__ import annotations

from typing import Any

import httpx

from app.services.rumble_video_native import finalise_captions
from app.services.transcript_segments import join_segment_text, parse_webvtt
from app.utils.formatters import normalize_language_code, safe_str

CREDIT_TRANSCRIPT = 1


def available_languages(captions: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in finalise_captions(captions):
        out.append(
            {
                "code": safe_str(row.get("code")) or "und",
                "language": safe_str(row.get("language")) or safe_str(row.get("code")) or "und",
            }
        )
    return out


def pick_caption_track(
    captions: list[dict[str, Any]] | None,
    language: str | None,
) -> tuple[dict[str, Any] | None, str | None, list[dict[str, str]]]:
    """Return (track, error_code, availableLanguages).

    No ``language`` → first track. Mismatch → ``language_not_available``
    (never a silent fallback). Empty list → ``no_captions``.
    """
    tracks = finalise_captions(captions)
    avail = available_languages(tracks)
    if not tracks:
        return None, "no_captions", []
    if not language or not str(language).strip():
        return tracks[0], None, avail

    want = str(language).strip().lower()
    for track in tracks:
        if (safe_str(track.get("code")) or "").lower() == want:
            return track, None, avail

    want_base = normalize_language_code(want) or want.split("-")[0]
    matches: list[dict[str, Any]] = []
    for track in tracks:
        code = (safe_str(track.get("code")) or "").lower()
        code_base = normalize_language_code(code) or (code.split("-")[0] if code else "")
        if code_base == want_base:
            matches.append(track)
            continue
        name = (safe_str(track.get("language")) or "").lower()
        if want_base and want_base == normalize_language_code(name):
            matches.append(track)
    if matches:
        return matches[0], None, avail
    return None, "language_not_available", avail


async def fetch_vtt(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CaptapiBot/1.0)"}
    async with httpx.AsyncClient(timeout=45, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
    if resp.status_code >= 400:
        raise RuntimeError(f"vtt_http_{resp.status_code}")
    return resp.text


def build_transcript_payload(
    *,
    video_id: str | None,
    url: str,
    track: dict[str, Any],
    vtt_body: str,
    duration_seconds: int | None,
) -> dict[str, Any]:
    segments = parse_webvtt(vtt_body)
    payload: dict[str, Any] = {
        "platform": "rumble",
        "id": safe_str(video_id),
        "url": safe_str(url),
        "source": "captions",
        "language": safe_str(track.get("code")),
        "languageName": safe_str(track.get("language")) or safe_str(track.get("code")),
        "durationSeconds": int(duration_seconds) if duration_seconds is not None else None,
        "segments": segments,
        "text": join_segment_text(segments),
    }
    # Omit keys that would be null on every / most rows for this surface.
    if payload["durationSeconds"] is None:
        payload.pop("durationSeconds")
    if not payload["id"]:
        payload.pop("id")
    return payload