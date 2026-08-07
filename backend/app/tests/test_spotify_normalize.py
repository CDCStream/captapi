"""Unit tests for Spotify track/artist/album normalize shapes."""

from __future__ import annotations

from app.routers import spotify as sp


def _sample_track_payload() -> dict:
    return {
        "uri": "spotify:track:0V3wPSX9ygBnCm8psDIegu",
        "id": "0V3wPSX9ygBnCm8psDIegu",
        "name": "Anti-Hero",
        "playcount": "2037355549",
        "duration": {"totalMilliseconds": 200690},
        "contentRating": {"label": "NONE"},
        "trackNumber": 3,
        "firstArtist": {
            "items": [
                {
                    "id": "06HL4z0CvFAxyc27GXpf02",
                    "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
                    "profile": {"name": "Taylor Swift"},
                }
            ]
        },
        "albumOfTrack": {
            "id": "151w1FgRZfnKZA9FEcg9Z3",
            "uri": "spotify:album:151w1FgRZfnKZA9FEcg9Z3",
            "name": "Midnights",
            "date": {"isoString": "2022-10-21"},
        },
    }


def _sample_artist_payload() -> dict:
    return {
        "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
        "id": "06HL4z0CvFAxyc27GXpf02",
        "profile": {"name": "Taylor Swift", "biography": {"text": "Bio"}},
        "stats": {
            "followers": 100,
            "monthlyListeners": 1000,
            "worldRank": 6,
            "topCities": {
                "items": [
                    {
                        "city": "Jakarta",
                        "country": "ID",
                        "region": "JK",
                        "numberOfListeners": 500,
                    }
                ]
            },
        },
        "discography": {
            "topTracks": {
                "items": [
                    {
                        "uri": "spotify:track:0V3wPSX9ygBnCm8psDIegu",
                        "track": {
                            "uri": "spotify:track:0V3wPSX9ygBnCm8psDIegu",
                            "name": "Anti-Hero",
                            "playcount": "2037355549",
                            "contentRating": {"label": "NONE"},
                        },
                    }
                ]
            },
            "albums": {
                "totalCount": 33,
                "items": [
                    {
                        "releases": {
                            "items": [
                                {
                                    "uri": "spotify:album:a1",
                                    "name": "Album One",
                                    "date": {"isoString": "2022-01-01"},
                                }
                            ]
                        }
                    },
                    {
                        "releases": {
                            "items": [
                                {
                                    "uri": "spotify:album:a2",
                                    "name": "Album Two",
                                    "date": {"isoString": "2021-01-01"},
                                }
                            ]
                        }
                    },
                ],
            },
            "singles": {
                "totalCount": 79,
                "items": [
                    {
                        "releases": {
                            "items": [
                                {
                                    "uri": "spotify:album:s1",
                                    "name": "Single One",
                                }
                            ]
                        }
                    }
                ],
            },
        },
        "relatedContent": {"relatedArtists": {"items": []}},
        "goods": {"concerts": {"items": []}},
    }


def _sample_album_payload() -> dict:
    return {
        "uri": "spotify:album:151w1FgRZfnKZA9FEcg9Z3",
        "name": "Midnights",
        "date": {"isoString": "2022-10-21T00:00:00Z", "precision": "DAY"},
        "artists": {
            "items": [
                {
                    "id": "06HL4z0CvFAxyc27GXpf02",
                    "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
                    "profile": {"name": "Taylor Swift"},
                }
            ]
        },
        "tracksV2": {
            "totalCount": 2,
            "items": [
                {
                    "track": {
                        "uri": "spotify:track:5jQI2r1RdgtuT8S3iG8zFC",
                        "name": "Lavender Haze",
                        "playcount": "901032338",
                        "trackNumber": 1,
                        "discNumber": 1,
                        "duration": {"totalMilliseconds": 202395},
                        "contentRating": {"label": "EXPLICIT"},
                        "artists": {
                            "items": [
                                {
                                    "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
                                    "profile": {"name": "Taylor Swift"},
                                }
                            ]
                        },
                    }
                },
                {
                    "track": {
                        "uri": "spotify:track:0V3wPSX9ygBnCm8psDIegu",
                        "name": "Anti-Hero",
                        "playcount": "2037355549",
                        "trackNumber": 3,
                        "discNumber": 1,
                        "duration": {"totalMilliseconds": 200690},
                        "contentRating": {"label": "NONE"},
                        "artists": {
                            "items": [
                                {
                                    "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
                                    "profile": {"name": "Taylor Swift"},
                                }
                            ]
                        },
                    }
                },
            ],
        },
    }


def test_track_normalize_joins_playcount_explicit():
    out = sp._normalize(_sample_track_payload(), "track")
    assert out["playCount"] == 2037355549
    assert out["explicit"] is False
    assert out["artists"][0]["uri"] == "spotify:artist:06HL4z0CvFAxyc27GXpf02"
    assert out["album"]["uri"] == "spotify:album:151w1FgRZfnKZA9FEcg9Z3"
    assert out["releaseDate"] == "2022-10-21"
    assert "raw" in out  # route strips unless ?raw=true


def test_artist_normalize_discography_has_more_and_includes_raw_key():
    out = sp._normalize(_sample_artist_payload(), "artist")
    assert out["albumsCount"] == 33
    assert out["singlesCount"] == 79
    assert len(out["albums"]) == 2
    assert out["albumsHasMore"] is True
    assert out["singlesHasMore"] is True
    assert out["topCities"][0]["country"] == "ID"
    assert "raw" in out


def test_album_normalize_tracks_joins_release_date_explicit():
    out = sp._normalize(_sample_album_payload(), "album")
    assert len(out["tracks"]) == 2
    assert out["tracks"][0]["name"] == "Lavender Haze"
    assert out["tracks"][0]["id"] == "5jQI2r1RdgtuT8S3iG8zFC"
    assert out["tracks"][0]["playCount"] == 901032338
    assert out["tracks"][0]["explicit"] is True
    assert out["tracks"][0]["uri"].startswith("spotify:track:")
    assert out["tracks"][0]["artists"][0]["uri"].startswith("spotify:artist:")
    assert out["artists"][0]["uri"] == "spotify:artist:06HL4z0CvFAxyc27GXpf02"
    assert out["releaseDate"] == "2022-10-21T00:00:00Z"
    assert out["releaseYear"] == 2022
    assert out["explicit"] is True
    assert out["totalTracks"] == 2


def test_track_nineteen_plus_keeps_content_rating():
    """contentRating is not a 2-valued alias of explicit — NINETEEN_PLUS ≠ EXPLICIT."""
    payload = _sample_track_payload()
    payload["contentRating"] = {"label": "NINETEEN_PLUS"}
    out = sp._normalize(payload, "track")
    assert out["contentRating"] == "NINETEEN_PLUS"
    assert out["explicit"] is False


def test_search_apify_bare_id_becomes_canonical_uri():
    out = sp._normalize(
        {
            "uri": "1S7FNazOUQc21EaQyh5nJT",
            "name": "Nightmote - Lofi Remix",
            "albumName": "Nightmote (Lofi Remix)",
            "durationMs": 207620,
            "durationFormatted": "3:27",
            "isExplicit": False,
            "isPlayable": True,
            "scrapedAt": "2026-07-18T11:28:01.801Z",
            "searchTerm": "lofi beats",
        },
        "track",
    )
    assert out["uri"] == "spotify:track:1S7FNazOUQc21EaQyh5nJT"
    assert out["explicit"] is False
    assert out["playable"] is True
    assert out["durationFormatted"] == "3:27"
    # Normalize may still lift Apify scrapedAt; search strips it before return.
    assert out.get("scrapedAt") == "2026-07-18T11:28:01.801Z"
    assert "searchTerm" not in (out.get("raw") or {})


def _sample_episode_payload() -> dict:
    return {
        "uri": "spotify:episode:6sriD1voEkINLnr08M9nmw",
        "id": "6sriD1voEkINLnr08M9nmw",
        "name": "#2535 - Andrew Wilson",
        "description": "Bio",
        "htmlDescription": "<p>Bio</p>",
        "duration": {"totalMilliseconds": 1000},
        "releaseDate": {"isoString": "2026-07-16T17:00:00Z", "precision": "MINUTE"},
        "contentRating": {"label": "EXPLICIT"},
        "mediaTypes": ["AUDIO", "VIDEO"],
        "previewPlayback": {"audioPreview": {"cdnUrl": "https://p.scdn.co/mp3-preview/x.mp3"}},
        "audio": {"items": [{"url": "https://p.scdn.co/mp3-preview/a"}, {"url": "https://p.scdn.co/mp3-preview/b"}]},
        "transcripts": {"items": []},
        "restrictions": {"paywallContent": False},
        "playability": {"playable": True},
        "podcastV2": {"data": {"showTypes": ["SHOW_TYPE_EXCLUSIVE"], "uri": "spotify:show:x"}},
        "visualIdentity": {"squareCoverImage": {"extractedColorSet": {"highContrast": {}}}},
        "playedState": {"state": "NOT_STARTED"},
    }


def test_episode_normalize_lifts_previews_and_slims_raw():
    out = sp._normalize(_sample_episode_payload(), "episode")
    assert out["id"] == "6sriD1voEkINLnr08M9nmw"
    assert out["previewUrl"].endswith(".mp3")
    assert out["audioUrls"] == [
        "https://p.scdn.co/mp3-preview/a",
        "https://p.scdn.co/mp3-preview/b",
    ]
    assert out["releaseDate"] == "2026-07-16T17:00:00Z"
    assert out["releaseYear"] == 2026
    assert out["hasVideo"] is True
    assert out["explicit"] is True
    assert out["hasTranscripts"] is False
    assert out["paywallContent"] is False
    assert out["showTypes"] == ["SHOW_TYPE_EXCLUSIVE"]
    raw = out["raw"]
    assert "visualIdentity" not in raw
    assert "playedState" not in raw
    assert "podcastV2" not in raw
