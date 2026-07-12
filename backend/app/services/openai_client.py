"""OpenAI wrappers: transcription (Whisper) + summarization (gpt-4o-mini)."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

import httpx
import structlog
from openai import AsyncOpenAI

from app.core.config import get_settings

log = structlog.get_logger(__name__)


@lru_cache
def get_openai() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


SUMMARY_SYSTEM = """You are an expert at distilling video content into structured summaries.
Given a transcript, produce JSON with:
- "summary": 2-3 paragraph executive summary
- "keyPoints": array of 4-8 bullet points of the most important takeaways
- "topics": array of 3-8 short topic/keyword tags
- "sentiment": "positive" | "neutral" | "negative" | "mixed"

Respond ONLY with valid JSON, no markdown fencing."""


async def summarize_transcript(
    transcript: str,
    title: str | None = None,
    language: str = "en",
) -> dict[str, Any]:
    settings = get_settings()
    client = get_openai()

    truncated = transcript[:60_000]
    user_prompt = (
        f"Title: {title or 'Unknown'}\n"
        f"Language: {language}\n\n"
        f"Transcript:\n{truncated}"
    )

    resp = await client.chat.completions.create(
        model=settings.OPENAI_MODEL_SUMMARY,
        response_format={"type": "json_object"},
        temperature=0.3,
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or "{}"
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        log.warning("summarize_invalid_json", content=content[:200])
        parsed = {
            "summary": content[:500],
            "keyPoints": [],
            "topics": [],
            "sentiment": "neutral",
        }
    return {
        "summary": parsed.get("summary", ""),
        "keyPoints": parsed.get("keyPoints", []) or [],
        "topics": parsed.get("topics", []) or [],
        "sentiment": parsed.get("sentiment"),
    }


# whisper-1 rejects uploads over 25 MB; short-form videos are well under this.
WHISPER_MAX_BYTES = 25 * 1024 * 1024

# Phrases Whisper hallucinates on silence/music-only audio (learned from
# subtitle credits in its training data). Segments matching these are noise,
# not speech.
_WHISPER_HALLUCINATIONS = {
    "altyazi m.k.",
    "altyazi: m.k.",
    "izlediginiz icin tesekkurler",
    "izlediginiz icin tesekkur ederim",
    "thanks for watching",
    "thank you for watching",
    "subtitles by the amara.org community",
    "sous-titres realises para la communaute d'amara.org",
    "you",
}

_HALLUCINATION_TRANSLATION = str.maketrans("ıİçÇşŞğĞüÜöÖéê", "iiccssgguuooee")


def _is_hallucinated_segment(text: str) -> bool:
    normalized = " ".join(text.translate(_HALLUCINATION_TRANSLATION).lower().split())
    return normalized.rstrip(".!") in _WHISPER_HALLUCINATIONS or normalized in _WHISPER_HALLUCINATIONS


async def transcribe_video_url(video_url: str) -> dict[str, Any] | None:
    """Download a video by URL and Whisper-transcribe its audio.

    Returns the transcribe_audio dict, or None when the file can't be
    fetched / is too large (callers fall back to their actor cascade).
    """
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            resp = await client.get(video_url)
            if resp.status_code >= 400 or len(resp.content) > WHISPER_MAX_BYTES:
                return None
            raw = resp.content
    except httpx.HTTPError:
        return None
    if not raw:
        return None
    return await transcribe_audio(raw, filename="video.mp4")


async def transcribe_audio(file_bytes: bytes, filename: str) -> dict[str, Any]:
    settings = get_settings()
    client = get_openai()
    resp = await client.audio.transcriptions.create(
        model=settings.OPENAI_MODEL_TRANSCRIPTION,
        file=(filename, file_bytes),
        response_format="verbose_json",
        timestamp_granularities=["segment"],
    )
    segments = []
    for seg in (resp.segments or []):
        seg_text = (getattr(seg, "text", "") or "").strip()
        if not seg_text or _is_hallucinated_segment(seg_text):
            continue
        start = float(getattr(seg, "start", 0.0))
        end = float(getattr(seg, "end", start))
        mm = int(start // 60)
        ss = int(start % 60)
        segments.append(
            {
                "text": seg_text,
                "start": start,
                "duration": max(end - start, 0.0),
                "timestamp": f"{mm:02d}:{ss:02d}",
            }
        )

    # Rebuild the full text from the kept segments so filtered hallucinations
    # don't linger in the transcript. Empty -> genuinely no speech.
    if segments:
        text = " ".join(s["text"] for s in segments)
    elif resp.segments:
        text = ""  # everything was hallucination noise
    else:
        raw = (resp.text or "").strip()
        text = "" if _is_hallucinated_segment(raw) else raw
    return {
        "transcript": text,
        "transcriptSegments": segments,
        "wordCount": len(text.split()),
        "segments": len(segments),
        "language": getattr(resp, "language", None),
        "duration": float(getattr(resp, "duration", 0.0)),
    }
