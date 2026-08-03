from __future__ import annotations

from app.services.instagram_native import (
    _coauthors_from_media,
    _mashup_from_media,
    _music_from_media,
    _pick_audio_music_meta,
)


def test_music_from_media_trend_signals() -> None:
    music = _music_from_media(
        {
            "clips_metadata": {
                "music_info": {
                    "music_asset_info": {
                        "audio_cluster_id": "1392969992841787",
                        "audio_asset_id": "aaa",
                        "music_canonical_id": "18455463055100927",
                        "title": "Freakin' Out",
                        "display_artist": "Dexter and The Moonrocks",
                        "duration_in_ms": 217897,
                        "audio_type": "licensed_music",
                        "is_explicit": False,
                        "has_lyrics": True,
                        "cover_artwork_uri": "https://cdn.example/cover.jpg",
                        "artist_id": "42",
                    },
                    "music_consumption_info": {
                        "is_trending_in_clips": True,
                        "trend_rank": 3,
                        "previous_trend_rank": 7,
                    },
                }
            }
        }
    )
    assert music is not None
    assert music["id"] == "1392969992841787"
    assert music["clusterId"] == "1392969992841787"
    assert music["canonicalId"] == "18455463055100927"
    assert music["title"] == "Freakin' Out"
    assert music["artist"] == "Dexter and The Moonrocks"
    assert music["durationMs"] == 217897
    assert music["audioType"] == "licensed_music"
    assert music["isTrendingInClips"] is True
    assert music["trendRank"] == 3
    assert music["previousTrendRank"] == 7
    assert music["isExplicit"] is False
    assert music["hasLyrics"] is True
    assert music["coverUrl"] == "https://cdn.example/cover.jpg"


def test_coauthors_and_mashup() -> None:
    media = {
        "coauthor_producers": [
            {
                "pk": "1",
                "username": "collab",
                "full_name": "Collab User",
                "is_verified": True,
                "profile_pic_url": "https://cdn.example/a.jpg",
            }
        ],
        "clips_metadata": {
            "mashup_info": {
                "has_been_mashed_up": True,
                "non_privacy_filtered_mashups_media_count": 12,
            }
        },
    }
    co = _coauthors_from_media(media)
    assert len(co) == 1
    assert co[0]["username"] == "collab"
    mash = _mashup_from_media(media)
    assert mash == {"hasBeenMashedUp": True, "mashupCount": 12}


def test_pick_audio_music_prefers_trending() -> None:
    picked = _pick_audio_music_meta(
        [
            {"music": {"id": "1", "title": "a"}},
            {"music": {"id": "2", "isTrendingInClips": True, "trendRank": 1}},
        ]
    )
    assert picked is not None
    assert picked["id"] == "2"
    assert picked["isTrendingInClips"] is True