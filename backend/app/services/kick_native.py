"""Native Kick clips via Decodo (direct/DC/res return 403)."""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

import structlog

from app.services import decodo_fetch

log = structlog.get_logger(__name__)

# One Decodo JSON fetch is well under $0.01; flat 1 credit matches ScrapeCreators.
CREDIT_KICK_NATIVE = 1


def clips_api_url(channel_slug: str, *, limit: int = 20) -> str:
    slug = (channel_slug or "").strip().strip("/").rsplit("/", 1)[-1]
    lim = max(1, min(int(limit), 100))
    return f"https://kick.com/api/v2/channels/{quote(slug)}/clips?limit={lim}"


def clip_api_url(clip_id: str) -> str:
    cid = (clip_id or "").strip().strip("/")
    return f"https://kick.com/api/v2/clips/{quote(cid)}"


def _as_dict(body: str | bytes | dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(body, dict):
        return body
    text = body.decode("utf-8", errors="ignore") if isinstance(body, (bytes, bytearray)) else (body or "")
    try:
        payload = json.loads(text)
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None


def parse_clips_payload(body: str | bytes | dict[str, Any]) -> list[dict[str, Any]]:
    payload = _as_dict(body)
    if not payload:
        return []
    raw = payload.get("clips") or payload.get("data") or payload.get("items")
    if not isinstance(raw, list):
        return []
    return [c for c in raw if isinstance(c, dict)]


def parse_clip_payload(body: str | bytes | dict[str, Any]) -> dict[str, Any] | None:
    payload = _as_dict(body)
    if not payload:
        return None
    clip = payload.get("clip") if isinstance(payload.get("clip"), dict) else payload
    return clip if isinstance(clip, dict) and clip.get("id") else None


async def fetch_channel_clips(channel_slug: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    """Return raw Kick clip dicts, or None when Decodo/API fails (caller -> Apify)."""
    if limit <= 0:
        return []
    if not decodo_fetch.enabled():
        return None
    url = clips_api_url(channel_slug, limit=limit)
    got = await decodo_fetch.fetch_url(url, timeout=60.0)
    if not got:
        return None
    status, body = got
    if status != 200 or not body:
        log.info("kick_native_bad_status", status=status, url=url[:120])
        return None
    clips = parse_clips_payload(body)
    if not clips:
        log.info("kick_native_empty", url=url[:120])
        return None
    out = clips[:limit]
    log.info("kick_native_ok", channel=channel_slug[:40], n=len(out))
    return out


async def fetch_clip(clip_id: str) -> dict[str, Any] | None:
    """Single clip via ``/api/v2/clips/{id}`` (richer than the channel list row)."""
    cid = (clip_id or "").strip().strip("/")
    if not cid or not decodo_fetch.enabled():
        return None
    url = clip_api_url(cid)
    got = await decodo_fetch.fetch_url(url, timeout=60.0)
    if not got:
        return None
    status, body = got
    if status != 200 or not body:
        log.info("kick_native_clip_bad_status", status=status, url=url[:120])
        return None
    clip = parse_clip_payload(body)
    if not clip:
        log.info("kick_native_clip_empty", url=url[:120])
        return None
    log.info("kick_native_clip_ok", id=str(clip.get("id") or "")[:40])
    return clip
