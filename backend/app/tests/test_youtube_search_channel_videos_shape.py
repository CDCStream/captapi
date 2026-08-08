"""YS1–YS8 shape checks for YouTube search + channel-videos list cards."""

from __future__ import annotations

from app.services.youtube_native import (
    _normalize_channel_renderer,
    finalise_youtube_list_card,
    normalize_video_renderer,
)


def test_search_typed_partitions_are_disjoint() -> None:
    """Mirror router logic ? live must not also sit in videos[] (YS3)."""
    results = [
        {"type": "video", "id": "v1"},
        {"type": "live", "id": "l1"},
        {"type": "upcoming", "id": "u1"},
        {"type": "short", "id": "s1"},
        {"type": "channel", "id": "c1"},
        {"type": "playlist", "id": "p1"},
    ]
    videos = [r for r in results if r.get("type") == "video"]
    shorts = [r for r in results if r.get("type") == "short"]
    channels = [r for r in results if r.get("type") == "channel"]
    playlists = [r for r in results if r.get("type") == "playlist"]
    lives = [r for r in results if r.get("type") in {"live", "upcoming"}]
    shelves = [r for r in results if r.get("type") == "shelf"]
    typed = videos + shorts + channels + playlists + lives + shelves
    assert len(typed) == len(results)
    assert {r["id"] for r in videos} & {r["id"] for r in lives} == set()


def test_normalize_video_renderer_list_card_vocabulary() -> None:
    vr = {
        "videoId": "abcdefghijk",
        "title": {"runs": [{"text": "Hello"}]},
        "viewCountText": {"simpleText": "1,234 views"},
        "publishedTimeText": {"simpleText": "4 days ago"},
        "lengthText": {"simpleText": "3:21"},
        "ownerText": {
            "runs": [
                {
                    "text": "Creator",
                    "navigationEndpoint": {
                        "browseEndpoint": {
                            "browseId": "UCxxxxxxxxxxxxxxxxxxxxxx",
                            "canonicalBaseUrl": "/@Creator",
                        }
                    },
                }
            ]
        },
        "thumbnail": {"thumbnails": [{"url": "https://i.ytimg.com/vi/abcdefghijk/hqdefault.jpg"}]},
    }
    card = normalize_video_renderer(vr)
    assert card is not None
    out = finalise_youtube_list_card(card)
    assert "channelId" not in out
    assert "channelName" not in out
    assert "viewCountInt" not in out
    assert out["channel"]["id"] == "UCxxxxxxxxxxxxxxxxxxxxxx"
    assert out["viewCount"] == 1234
    assert out["viewCountIsApproximate"] is False
    assert out["publishedTimeApprox"] and out["publishedTimeIsApproximate"] is True
    assert "publishedAt" not in out


def test_exact_views_flag_is_false_not_null() -> None:
    out = finalise_youtube_list_card(
        {
            "viewCount": 296301,
            "viewCountText": "296,301 views",
            "viewCountInt": 296301,
            "channelId": "UCx",
            "channelName": "Name",
            "channel": {"id": "UCx", "title": "Name"},
            "publishedTimeApprox": "2026-01-01T00:00:00.000Z",
            "publishedTimeIsApproximate": False,
        }
    )
    assert out["viewCountIsApproximate"] is False
    assert "viewCountInt" not in out
    assert "channelId" not in out


def test_channel_renderer_subscriber_count_from_swapped_fields() -> None:
    """YouTube puts @handle in subscriberCountText and subs in videoCountText."""
    card = _normalize_channel_renderer(
        {
            "channelId": "UC7_gcs09iThXybpVgjHZ_7g",
            "title": {"simpleText": "PBS Space Time"},
            "subscriberCountText": {"simpleText": "@pbsspacetime"},
            "videoCountText": {
                "accessibility": {
                    "accessibilityData": {"label": "3.51 million subscribers"}
                },
                "simpleText": "3.51M subscribers",
            },
            "thumbnail": {"thumbnails": [{"url": "https://yt3.ggpht.com/x"}]},
            "navigationEndpoint": {
                "browseEndpoint": {
                    "browseId": "UC7_gcs09iThXybpVgjHZ_7g",
                    "canonicalBaseUrl": "/@pbsspacetime",
                }
            },
        }
    )
    assert card is not None
    out = finalise_youtube_list_card(card)
    assert out["subscriberCount"] == 3_510_000
    assert out["publishedTimeApprox"] is None
    assert out["publishedTimeIsApproximate"] is None
