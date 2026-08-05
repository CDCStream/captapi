"""Unit tests for SoundCloud track/artist normalize shapes."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.routers import soundcloud as sc
from app.services import soundcloud_native as native


def test_track_nested_artist_and_media_flags():
    item = {
        "id": 1,
        "title": "Test",
        "permalink_url": "https://soundcloud.com/nasa/x",
        "playback_count": 10,
        "likes_count": 2,
        "reposts_count": 1,
        "comment_count": 0,
        "download_count": 0,
        "downloadable": True,
        "streamable": True,
        "license": "all-rights-reserved",
        "created_at": "2026-07-20T14:01:49Z",
        "user": {
            "id": 112904040,
            "username": "NASA",
            "permalink": "nasa",
            "permalink_url": "https://soundcloud.com/nasa",
            "avatar_url": "https://i1.sndcdn.com/x.jpg",
            "followers_count": 100,
            "verified": True,
        },
        "tagList": ["nasa"],
    }
    out = sc._track(
        item,
        media={
            "streamUrl": "https://cf-media.sndcdn.com/x.mp3",
            "hlsUrl": "https://playback.example/x.m3u8",
            "mediaUrlsExpireAt": "2026-08-05T21:00:00Z",
        },
    )
    assert out["artist"]["id"] == "112904040"
    assert out["artist"]["handle"] == "nasa"
    assert out["streamUrl"].endswith(".mp3")
    assert out["downloadable"] is True
    assert "downloadUrl" not in out
    assert "artistFollowers" not in out


def test_artist_subscription_tier_handle_links():
    user = {
        "id": 2976616,
        "username": "Flume",
        "permalink": "flume",
        "permalink_url": "https://soundcloud.com/flume",
        "verified": True,
        "badges": {"pro": False, "creator_mid_tier": False, "pro_unlimited": True, "verified": True},
        "creator_subscription": {"product": {"id": "creator-pro-unlimited"}},
        "followers_count": 1,
        "followings_count": 2,
        "track_count": 3,
        "playlist_count": 4,
        "likes_count": 5,
        "created_at": None,
    }
    out = sc._artist(
        user,
        "https://soundcloud.com/flume",
        external_links=[{"url": "https://dumb.store/", "network": "personal", "title": "DUMB Store"}],
    )
    assert out["handle"] == "flume"
    assert out["username"] == "Flume"
    assert out["subscriptionTier"] == "pro-unlimited"
    assert out["verified"] is True
    assert "badges" not in out
    assert "creatorSubscription" not in out
    assert out["externalLinks"][0]["url"].startswith("https://")
    assert "createdAt" not in out


def test_track_list_omits_artist():
    item = {
        "id": 1,
        "title": "Test",
        "permalink_url": "https://soundcloud.com/nasa/x",
        "user": {
            "id": 112904040,
            "username": "NASA",
            "permalink": "nasa",
            "permalink_url": "https://soundcloud.com/nasa",
            "followers_count": 100,
            "verified": True,
        },
    }
    out = sc._track(item, include_artist=False)
    assert "artist" not in out
    assert out["title"] == "Test"


def test_opaque_tracks_cursor_roundtrip():
    token = sc._encode_tracks_cursor("112904040", "2026-07-13T13:25:32.000Z,tracks,00000000002359662548")
    assert "soundcloud.com" not in token
    assert "112904040" not in token
    offset = sc._decode_tracks_cursor(token, expected_user_id="112904040")
    assert offset == "2026-07-13T13:25:32.000Z,tracks,00000000002359662548"
    with pytest.raises(HTTPException) as exc:
        sc._decode_tracks_cursor(token, expected_user_id="999")
    assert exc.value.status_code == 400


def test_legacy_next_href_cursor_extracts_offset_only():
    legacy = (
        "https://api-v2.soundcloud.com/users/112904040/tracks?"
        "offset=2026-07-13T13%3A25%3A32.000Z%2Ctracks%2C00000000002359662548&limit=5"
    )
    assert "api-v2" in legacy
    offset = sc._decode_tracks_cursor(legacy, expected_user_id="112904040")
    assert offset == "2026-07-13T13:25:32.000Z,tracks,00000000002359662548"
    assert native.offset_from_next_href(legacy) == offset


def test_subscription_tier_free():
    assert sc._subscription_tier({}, None) == "free"
    assert sc._subscription_tier({}, {"pro": True, "creatorMidTier": False, "proUnlimited": False}) == "pro"