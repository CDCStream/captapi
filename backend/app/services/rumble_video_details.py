"""Shared Rumble video-details card resolution + canonical key set."""

from __future__ import annotations

from typing import Any

# Shelved Session-2h shape for GET /v1/rumble/video-details (fixture v7cv2cc).
# CI fails if a response drops any of these keys. Adding keys is fine.
RUMBLE_VIDEO_DETAILS_KEYS: tuple[str, ...] = (
    "platform",
    "id",
    "numericId",
    "embedId",
    "url",
    "type",
    "embedUrl",
    "shareUrl",
    "title",
    "description",
    "channel",
    "channelUrl",
    "channelHandle",
    "channelFollowers",
    "channelVerified",
    "views",
    "likes",
    "likesIsApproximate",
    "dislikes",
    "comments",
    "durationSeconds",
    "durationText",
    "publishedAt",
    "thumbnail",
    "width",
    "height",
    "captions",
    "isLive",
    "streams",
    "audioStreams",
    "thumbnailTrack",
)


def finalise_video_details(card: dict[str, Any] | None) -> dict[str, Any]:
    """Force the shelved video-details key set.

    - ``captions`` / ``audioStreams`` / ``streams`` are always lists (possibly empty).
    - ``thumbnailTrack`` stays keyed (null when Rumble ships no sprite).
    - Optional scalars stay keyed as null when unknown — never silently dropped.
    """
    src = dict(card or {})
    src.pop("media", None)
    src.pop("duration", None)
    src.pop("durationFormatted", None)

    out: dict[str, Any] = {}
    for key in RUMBLE_VIDEO_DETAILS_KEYS:
        if key == "captions":
            caps = src.get("captions")
            out[key] = list(caps) if isinstance(caps, list) else []
        elif key == "audioStreams":
            rows = src.get("audioStreams")
            out[key] = list(rows) if isinstance(rows, list) else []
        elif key == "streams":
            rows = src.get("streams")
            out[key] = list(rows) if isinstance(rows, list) else []
        elif key == "thumbnailTrack":
            track = src.get("thumbnailTrack")
            out[key] = track if isinstance(track, dict) and track.get("url") else None
        elif key == "platform":
            out[key] = src.get("platform") or "rumble"
        else:
            out[key] = src.get(key, None)
    return out