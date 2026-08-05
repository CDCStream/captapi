"""Twitch clip mapper: language, token unwrap, signed URLs, frameRate."""

from __future__ import annotations

import json

from app.services import twitch_native as tn


def _sample_clip(*, language: str = "ES") -> dict:
    token_payload = {
        "authorization": {"forbidden": False, "reason": ""},
        "clip_uri": "https://production.assets.clips.twitchcdn.net/x/landscape/h264/360/index.mp4",
        "clip_slug": "TestSlug",
        "device_id": "dev",
        "expires": 1785766190,
        "version": 2,
    }
    return {
        "id": "1",
        "slug": "TestSlug",
        "title": "clip",
        "createdAt": "2026-01-01T00:00:00Z",
        "viewCount": 10,
        "durationSeconds": 30,
        "language": language,
        "url": "https://clips.twitch.tv/TestSlug",
        "embedURL": "https://clips.twitch.tv/embed?clip=TestSlug",
        "thumbnailURL": "https://cdn/t.jpg",
        "isFeatured": False,
        "isPublished": True,
        "videoOffsetSeconds": 12,
        "game": {
            "id": "g",
            "name": "Just Chatting",
            "slug": "just-chatting",
            "boxArtURL": "https://cdn/{width}x{height}.jpg",
        },
        "curator": {
            "id": "c1",
            "login": "cutter",
            "displayName": "Cutter",
            "profileImageURL": "https://cdn/c.jpg",
        },
        "broadcaster": {
            "id": "b1",
            "login": "ibai",
            "displayName": "Ibai",
            "profileImageURL": "https://cdn/b.jpg",
            "roles": {"isPartner": True},
            "followers": {"totalCount": 100},
            "lastBroadcast": {"title": "live", "startedAt": "2026-01-01T00:00:00Z"},
        },
        "videoQualities": [
            {
                "quality": "1080",
                "frameRate": 60.02308654785156,
                "sourceURL": "https://production.assets.clips.twitchcdn.net/x/landscape/h264/1080/index.mp4",
            },
            {
                "quality": "360",
                "frameRate": 30.012901306152344,
                "sourceURL": "https://production.assets.clips.twitchcdn.net/x/landscape/h264/360/index.mp4",
            },
        ],
        "playbackAccessToken": {
            "signature": "abc123",
            "value": json.dumps(token_payload),
        },
    }


def test_language_lowercase_matches_profile_vods():
    clip = tn._map_clip(_sample_clip(language="ES"))
    vod = tn._video_node({"id": "9", "language": "ES", "title": "v"}, broadcaster="ibai")
    assert clip["language"] == "es"
    assert vod["language"] == "es"
    assert clip["language"] == vod["language"]


def test_playback_token_unwrapped_no_escaped_value():
    out = tn._map_clip(_sample_clip())
    tok = out["playbackAccessToken"]
    assert "value" not in tok
    assert tok["signature"] == "abc123"
    assert tok["expires"] == 1785766190
    assert tok["expiresAt"] == "2026-08-03T14:09:50Z"
    assert tok["clipUri"].endswith("/360/index.mp4")
    assert tok["clipSlug"] == "TestSlug"
    assert isinstance(tok.get("authorization"), dict)


def test_signed_video_url_uses_best_quality_not_token_clip_uri():
    out = tn._map_clip(_sample_clip())
    assert out["videoUrl"].endswith("/1080/index.mp4")
    assert "sig=abc123" in out["signedVideoUrl"]
    assert "token=" in out["signedVideoUrl"]
    assert "/1080/" in out["signedVideoUrl"]
    assert out["playbackAccessToken"]["clipUri"].endswith("/360/index.mp4")
    q0 = out["videoQualities"][0]
    assert q0["quality"] == "1080"
    assert q0["signedUrl"].startswith(q0["url"] + "?")


def test_frame_rate_rounded_to_2dp():
    out = tn._map_clip(_sample_clip())
    assert out["videoQualities"][0]["frameRate"] == 60.02
    assert out["videoQualities"][1]["frameRate"] == 30.01


def test_related_clips_pass_through():
    raw = _sample_clip()
    raw["_relatedClips"] = [{"slug": "Other", "title": "x", "language": "EN"}]
    out = tn._map_clip(raw)
    assert out["relatedClips"][0]["slug"] == "Other"
