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
# Stored pre-normalized: lowercase, ASCII-folded, trailing ".!" stripped.
_WHISPER_HALLUCINATIONS = {
    "altyazi m.k",
    "altyazi: m.k",
    "izlediginiz icin tesekkurler",
    "izlediginiz icin tesekkur ederim",
    "thanks for watching",
    "thank you for watching",
    "subtitles by the amara.org community",
    "sous-titres realises para la communaute d'amara.org",
    "you",
    # Sound-effect labels, usually wrapped in music notes ("(müzik)").
    "muzik",
    "music",
    "musica",
    "musique",
    "intro music",
    "applause",
    "alkis",
    "laughter",
}

_HALLUCINATION_TRANSLATION = str.maketrans("ıİçÇşŞğĞüÜöÖéê", "iiccssgguuooee")


def _is_hallucinated_segment(text: str) -> bool:
    if not any(ch.isalpha() for ch in text):
        return True  # music notes / symbols only
    normalized = " ".join(text.translate(_HALLUCINATION_TRANSLATION).lower().split())
    normalized = normalized.strip("♪♫[]() ").rstrip(".!")
    return normalized in _WHISPER_HALLUCINATIONS


# Whisper's verbose_json reports the detected language as a full name; the
# `language` request parameter wants an ISO-639-1 code.
_LANG_NAME_TO_ISO = {
    "english": "en", "turkish": "tr", "spanish": "es", "french": "fr",
    "german": "de", "italian": "it", "portuguese": "pt", "dutch": "nl",
    "russian": "ru", "arabic": "ar", "hindi": "hi", "urdu": "ur",
    "japanese": "ja", "korean": "ko", "chinese": "zh", "indonesian": "id",
    "vietnamese": "vi", "thai": "th", "polish": "pl", "ukrainian": "uk",
    "romanian": "ro", "greek": "el", "czech": "cs", "swedish": "sv",
    "danish": "da", "norwegian": "no", "finnish": "fi", "hungarian": "hu",
    "hebrew": "he", "persian": "fa", "malay": "ms", "tagalog": "tl",
    "bulgarian": "bg", "croatian": "hr", "serbian": "sr", "slovak": "sk",
    "azerbaijani": "az", "kazakh": "kk", "bengali": "bn", "tamil": "ta",
    "telugu": "te", "marathi": "mr", "swahili": "sw", "catalan": "ca",
}


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

    async def _request(**extra: Any):
        return await client.audio.transcriptions.create(
            model=settings.OPENAI_MODEL_TRANSCRIPTION,
            file=(filename, file_bytes),
            response_format="verbose_json",
            timestamp_granularities=["segment"],
            **extra,
        )

    resp = await _request()
    result = _parse_verbose(resp)
    if _is_valid_transcript(result):
        return result

    # Whisper sometimes bails out after hallucinating on a music/silence
    # intro and misses speech that starts later; retries with the detected
    # language pinned and a raised temperature recover it. A retry can itself
    # degenerate into a repetition loop ("Ben de." x29), so each attempt is
    # validated before being trusted.
    iso = _LANG_NAME_TO_ISO.get((getattr(resp, "language", None) or "").lower())
    for temperature in (0.2, 0.4):
        extra: dict[str, Any] = {"temperature": temperature}
        if iso:
            extra["language"] = iso
        retry = _parse_verbose(await _request(**extra))
        if _is_valid_transcript(retry):
            log.info("whisper_retry_recovered_speech", language=iso, temperature=temperature)
            return retry

    # Last resort: gpt-4o-mini-transcribe is far more robust on clips whose
    # speech starts after a music intro. No segment timestamps, text only.
    try:
        alt = await client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=(filename, file_bytes),
        )
        alt_text = (getattr(alt, "text", None) or "").strip()
    except Exception:  # noqa: BLE001
        alt_text = ""
    if alt_text and not _is_hallucinated_segment(alt_text):
        log.info("whisper_fallback_4o_mini_recovered_speech")
        return {
            "transcript": alt_text,
            "transcriptSegments": [],
            "wordCount": len(alt_text.split()),
            "segments": 0,
            "language": getattr(resp, "language", None),
            "duration": float(getattr(resp, "duration", 0.0)),
        }

    # Nothing trustworthy: report no speech rather than hallucinated text.
    result["transcript"] = ""
    result["transcriptSegments"] = []
    result["wordCount"] = 0
    result["segments"] = 0
    return result


def _is_valid_transcript(result: dict[str, Any]) -> bool:
    if not result["transcript"]:
        return False
    segments = result["transcriptSegments"]
    if len(segments) >= 5:
        texts = [s["text"].lower() for s in segments]
        if len(set(texts)) / len(texts) < 0.34:
            return False  # repetition loop, not real speech
    return True


def _parse_verbose(resp: Any) -> dict[str, Any]:
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
