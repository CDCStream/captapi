"""OpenAI wrappers: transcription (Whisper) + summarization (gpt-4o-mini)."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

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
        start = float(getattr(seg, "start", 0.0))
        end = float(getattr(seg, "end", start))
        mm = int(start // 60)
        ss = int(start % 60)
        segments.append(
            {
                "text": (getattr(seg, "text", "") or "").strip(),
                "start": start,
                "duration": max(end - start, 0.0),
                "timestamp": f"{mm:02d}:{ss:02d}",
            }
        )

    text = resp.text or ""
    return {
        "transcript": text,
        "transcriptSegments": segments,
        "wordCount": len(text.split()),
        "segments": len(segments),
        "language": getattr(resp, "language", None),
        "duration": float(getattr(resp, "duration", 0.0)),
    }
