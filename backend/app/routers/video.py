"""Raw video file transcription & summarization (Whisper)."""

from __future__ import annotations

import math

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.openai_client import summarize_transcript, transcribe_audio

router = APIRouter()


def _credits_for_duration(duration_seconds: float) -> int:
    minutes = max(1, math.ceil(duration_seconds / 60.0))
    return minutes


@router.post(
    "/transcript",
    summary="Transcribe an uploaded video/audio file via Whisper",
    description="1 credit per minute of audio. Max upload size and duration configured server-side.",
)
async def video_transcript(
    file: UploadFile = File(...),
    caller: ApiCaller = Depends(require_api_key),
):
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

    # Estimate cost optimistically by file size; charge actual after.
    # 1MB ~ 1 minute at 128kbps audio. We charge >=1 credit upfront and reconcile.
    est_minutes = max(1, len(raw) // (1024 * 1024))
    if est_minutes > settings.MAX_VIDEO_DURATION_MINUTES:
        raise HTTPException(
            status_code=413,
            detail=f"Estimated duration exceeds {settings.MAX_VIDEO_DURATION_MINUTES} minutes",
        )

    async with billed_call(
        caller=caller,
        endpoint="/v1/video/transcript",
        platform="video_file",
        resource_url=file.filename,
        base_credits=est_minutes,
    ) as ctx:
        result = await transcribe_audio(raw, filename=file.filename or "upload.mp4")
        actual_minutes = _credits_for_duration(result.get("duration", est_minutes * 60))
        if actual_minutes > settings.MAX_VIDEO_DURATION_MINUTES:
            raise HTTPException(
                status_code=413,
                detail=f"Audio duration exceeds {settings.MAX_VIDEO_DURATION_MINUTES} minutes",
            )
        ctx["credits_override"] = actual_minutes
        return ApiResponse(
            data={
                "filename": file.filename,
                "transcript": result["transcript"],
                "transcriptSegments": result["transcriptSegments"],
                "wordCount": result["wordCount"],
                "segments": result["segments"],
                "language": result.get("language"),
                "durationSeconds": result.get("duration"),
            }
        )


@router.post(
    "/summarize",
    summary="Transcribe + AI summary of an uploaded video/audio file",
    description="1 credit per minute of audio + 1 credit for the summary.",
)
async def video_summarize(
    file: UploadFile = File(...),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    max_bytes = settings.MAX_VIDEO_UPLOAD_MB * 1024 * 1024

    raw = await file.read()
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    est_minutes = max(1, len(raw) // (1024 * 1024))
    if est_minutes > settings.MAX_VIDEO_DURATION_MINUTES:
        raise HTTPException(status_code=413, detail="Duration exceeds limit")

    async with billed_call(
        caller=caller,
        endpoint="/v1/video/summarize",
        platform="video_file",
        resource_url=file.filename,
        base_credits=est_minutes + 1,
    ) as ctx:
        tx = await transcribe_audio(raw, filename=file.filename or "upload.mp4")
        actual_minutes = _credits_for_duration(tx.get("duration", est_minutes * 60))
        if actual_minutes > settings.MAX_VIDEO_DURATION_MINUTES:
            raise HTTPException(status_code=413, detail="Duration exceeds limit")

        text = tx.get("transcript", "")
        if not text:
            raise HTTPException(status_code=422, detail="Empty transcript, cannot summarize")

        ai = await summarize_transcript(text, language=tx.get("language") or "en")
        ctx["credits_override"] = actual_minutes + 1
        return ApiResponse(
            data={
                "filename": file.filename,
                "summary": ai["summary"],
                "keyPoints": ai["keyPoints"],
                "topics": ai["topics"],
                "sentiment": ai["sentiment"],
                "transcript": text,
                "wordCount": tx["wordCount"],
                "language": tx.get("language"),
                "durationSeconds": tx.get("duration"),
            }
        )
