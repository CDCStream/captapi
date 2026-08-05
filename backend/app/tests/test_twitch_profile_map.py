"""Twitch profile mapper: socials, thumbs, offline stream."""

from __future__ import annotations

from app.services import twitch_native as tn


def test_socials_from_panels_and_social_medias():
    u = {
        "channel": {
            "socialMedias": [
                {"name": "tiktok", "title": "TT", "url": "https://www.tiktok.com/@ibai"}
            ]
        },
        "panels": [
            {
                "id": "1",
                "linkURL": "https://www.instagram.com/ibaillanos/",
                "title": None,
            },
            {
                "id": "2",
                "linkURL": "https://twitter.com/IbaiLlanos",
                "title": "X",
            },
            {
                "id": "3",
                "linkURL": "https://www.youtube.com/channel/UCaY",
            },
        ],
    }
    socials = tn._socials_from_user(u)
    platforms = {s["platform"] for s in socials}
    assert "tiktok" in platforms
    assert "instagram" in platforms
    assert "twitter" in platforms
    assert "youtube" in platforms


def test_thumb_url_substitutes_placeholders():
    raw = "https://static-cdn.jtvnw.net/cf_vods/x/thumb/thumb0-{width}x{height}.jpg"
    assert tn._thumb_url(raw) == (
        "https://static-cdn.jtvnw.net/cf_vods/x/thumb/thumb0-320x180.jpg"
    )
    assert tn._thumb_template(raw) == raw
    assert tn._thumb_url("https://example.com/a.jpg") == "https://example.com/a.jpg"


def test_map_channel_stream_null_when_offline():
    u = {
        "id": "1",
        "login": "ibai",
        "displayName": "Ibai",
        "description": "bio",
        "createdAt": "2015-01-01T00:00:00Z",
        "profileImageURL": "https://cdn/a.jpg",
        "bannerImageURL": "https://cdn/b.jpg",
        "roles": {"isPartner": True, "isAffiliate": False},
        "followers": {"totalCount": 10},
        "stream": None,
        "lastBroadcast": {"title": "was live", "startedAt": "2026-01-01T00:00:00Z"},
        "panels": [{"linkURL": "https://www.instagram.com/ibaillanos/"}],
    }
    out = tn._map_channel(u, "ibai", recent=[], top_clips=[], schedule=[])
    assert out["isLive"] is False
    assert out["stream"] is None
    assert out["avatar"] == out["profileImage"]
    assert out["banner"] == out["bannerImage"]
    assert out["displayName"] == "Ibai"
    assert out["handle"] == "ibai"
    assert out["login"] == "ibai"
    assert out["socials"][0]["platform"] == "instagram"


def test_map_channel_stream_present_when_live():
    u = {
        "id": "1",
        "login": "ibai",
        "displayName": "Ibai",
        "roles": {},
        "followers": {"totalCount": 1},
        "stream": {
            "title": "LIVE",
            "viewersCount": 100,
            "createdAt": "2026-08-05T10:00:00Z",
            "previewImageURL": "https://cdn/live.jpg",
            "game": {"name": "Just Chatting", "boxArtURL": "https://cdn/g.jpg"},
        },
        "lastBroadcast": {},
    }
    out = tn._map_channel(u, "ibai")
    assert out["isLive"] is True
    assert out["stream"]["title"] == "LIVE"
    assert out["stream"]["viewers"] == 100
    assert out["stream"]["game"] == "Just Chatting"
