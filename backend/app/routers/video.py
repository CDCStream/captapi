"""Raw video file transcription & summarization (Whisper)."""

from __future__ import annotations

import math
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.openai_client import summarize_transcript, transcribe_audio

router = APIRouter()

TimestampGranularity = Literal["segment", "word"]


def _credits_for_duration(duration_seconds: float) -> int:
    minutes = max(1, math.ceil(duration_seconds / 60.0))
    return minutes


async def _load_upload(file: UploadFile) -> bytes:
    settings = get_settings()
    max_bytes = settings.MAX_VIDEO_UPLOAD_MB * 1024 * 1024
    raw = await file.read()
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.MAX_VIDEO_UPLOAD_MB}MB limit",
        )
    return raw


def _check_est_minutes(raw: bytes) -> int:
    settings = get_settings()
    est_minutes = max(1, len(raw) // (1024 * 1024))
    if est_minutes > settings.MAX_VIDEO_DURATION_MINUTES:
        raise HTTPException(
            status_code=413,
            detail=f"Estimated duration exceeds {settings.MAX_VIDEO_DURATION_MINUTES} minutes",
        )
    return est_minutes


def _transcript_payload(
    *,
    filename: str | None,
    result: dict[str, Any],
    credits_charged: int,
) -> dict[str, Any]:
    duration = float(result.get("duration") or 0.0)
    text = (result.get("transcript") or "").strip()
    no_speech = not text
    return {
        "filename": filename,
        "transcript": text,
        "transcriptSegments": result.get("transcriptSegments") or [],
        "wordCount": result.get("wordCount") or 0,
        "segments": result.get("segments") or 0,
        "language": result.get("language"),
        # Canonical billing field (seconds). ``duration`` is an alias for the
        # same value so customers can verify per-minute charges.
        "durationSeconds": duration,
        "duration": duration,
        "creditsCharged": credits_charged,
        "noSpeech": no_speech,
    }


@router.post(
    "/transcript",
    summary="Transcribe an uploaded video/audio file via Whisper",
    description=(
        "POST multipart form field `file`. 1 credit per minute of audio "
        "(rounded up, minimum 1) — see durationSeconds / creditsCharged in the "
        "response. Max upload 200MB / 60 minutes (server config). Optional "
        "language (ISO-639-1 hint), translate=true (English), "
        "timestampGranularity=segment|word. Empty/no-speech audio returns "
        "transcript=\"\" with noSpeech=true (still billed for duration)."
    ),
)
async def video_transcript(
    file: UploadFile = File(..., description="Video or audio file to transcribe"),
    language: str | None = Form(
        None,
        description='ISO-639-1 language hint for Whisper, e.g. "en" or "tr". Omit to auto-detect.',
    ),
    translate: bool = Form(
        False,
        description="When true, translate speech to English (Whisper translations API).",
    ),
    timestampGranularity: TimestampGranularity = Form(
        "segment",
        description="segment (default) or word — word-level timings when Whisper exposes them.",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    raw = await _load_upload(file)
    est_minutes = _check_est_minutes(raw)
    lang = (language or "").strip().lower() or None

    async with billed_call(
        caller=caller,
        endpoint="/v1/video/transcript",
        platform="video_file",
        resource_url=file.filename,
        base_credits=est_minutes,
    ) as ctx:
        result = await transcribe_audio(
            raw,
            filename=file.filename or "upload.mp4",
            language=lang,
            translate=translate,
            timestamp_granularity=timestampGranularity,
        )
        actual_minutes = _credits_for_duration(result.get("duration", est_minutes * 60))
        if actual_minutes > settings.MAX_VIDEO_DURATION_MINUTES:
            raise HTTPException(
                status_code=413,
                detail=f"Audio duration exceeds {settings.MAX_VIDEO_DURATION_MINUTES} minutes",
            )
        ctx["credits_override"] = actual_minutes
        return ApiResponse(
            data=_transcript_payload(
                filename=file.filename,
                result=result,
                credits_charged=actual_minutes,
            )
        )


@router.post(
    "/summarize",
    summary="Transcribe + AI summary of an uploaded video/audio file",
    description=(
        "POST multipart form field `file` (not a query string). Returns AI "
        "summary/keyPoints/topics/sentiment PLUS the full Whisper transcript "
        "(transcript, transcriptSegments, language, durationSeconds, "
        "creditsCharged). Summary length scales with the transcript — short "
        "clips may be one paragraph / fewer bullets; longer audio aims for "
        "2–3 paragraphs and 4–8 key points (GPT-4o-mini). Billing: 1 credit "
        "per minute of audio (rounded up) + 1 for the summary. Same "
        "200MB / 60 min limits and Whisper controls as /v1/video/transcript. "
        "Empty/no-speech audio → HTTP 422."
    ),
)
async def video_summarize(
    file: UploadFile = File(..., description="Video or audio file to transcribe and summarize"),
    language: str | None = Form(
        None,
        description='ISO-639-1 language hint for Whisper, e.g. "en" or "tr". Omit to auto-detect.',
    ),
    translate: bool = Form(
        False,
        description="When true, translate speech to English before summarizing.",
    ),
    timestampGranularity: TimestampGranularity = Form(
        "segment",
        description="segment (default) or word.",
    ),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    raw = await _load_upload(file)
    est_minutes = _check_est_minutes(raw)
    lang = (language or "").strip().lower() or None

    async with billed_call(
        caller=caller,
        endpoint="/v1/video/summarize",
        platform="video_file",
        resource_url=file.filename,
        base_credits=est_minutes + 1,
    ) as ctx:
        tx = await transcribe_audio(
            raw,
            filename=file.filename or "upload.mp4",
            language=lang,
            translate=translate,
            timestamp_granularity=timestampGranularity,
        )
        actual_minutes = _credits_for_duration(tx.get("duration", est_minutes * 60))
        if actual_minutes > settings.MAX_VIDEO_DURATION_MINUTES:
            raise HTTPException(status_code=413, detail="Duration exceeds limit")

        text = (tx.get("transcript") or "").strip()
        if not text:
            raise HTTPException(
                status_code=422,
                detail="No speech detected — cannot summarize an empty transcript",
            )

        ai = await summarize_transcript(text, language=tx.get("language") or lang or "en")
        credits = actual_minutes + 1
        ctx["credits_override"] = credits
        payload = _transcript_payload(
            filename=file.filename,
            result=tx,
            credits_charged=credits,
        )
        payload.update(
            {
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
            }
        )
        return ApiResponse(data=payload)
