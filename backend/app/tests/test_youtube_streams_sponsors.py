"""Tests for channel-streams Live-tab gate and SponsorBlock processing."""

from __future__ import annotations

from app.routers.youtube import _merged_coverage_seconds, _process_sponsor_segments
from app.services.youtube_native import _lockup_result_type, collect_playlist_cards


def test_channel_playlist_cards_include_id() -> None:
    data = {
        "lockupViewModel": {
            "contentType": "LOCKUP_CONTENT_TYPE_PLAYLIST",
            "contentId": "PLoSWVnSA9vG8example",
            "metadata": {
                "lockupMetadataViewModel": {
                    "title": {"content": "Example playlist"},
                }
            },
            "contentImage": {
                "sources": [{"url": "https://i.ytimg.com/vi/x/hqdefault.jpg"}],
            },
        }
    }
    # walk_find expects nested trees; wrap so the lockup is discoverable.
    rows = collect_playlist_cards({"contents": [data]})
    assert rows
    assert rows[0]["id"] == "PLoSWVnSA9vG8example"
    assert "list=PLoSWVnSA9vG8example" in rows[0]["url"]


def test_lockup_types_from_published_labels() -> None:
    assert _lockup_result_type("Streamed 1 hour ago") == "stream"
    assert _lockup_result_type("Scheduled for 8/12/26, 10:15 AM") == "upcoming"
    assert _lockup_result_type("4 days ago") == "video"


def test_sponsor_segments_sorted_min_votes_and_coverage() -> None:
    raw = [
        {"category": "selfpromo", "actionType": "skip", "segment": [554.515, 638.201], "votes": 1, "UUID": "outer"},
        {"category": "sponsor", "actionType": "skip", "segment": [600.675, 617.15], "votes": 0, "UUID": "inner-a"},
        {"category": "sponsor", "actionType": "skip", "segment": [555.65, 560.175], "votes": 0, "UUID": "inner-b"},
        {"category": "sponsor", "actionType": "skip", "segment": [621.375, 627.7], "votes": -1, "UUID": "rejected"},
        {"category": "selfpromo", "actionType": "skip", "segment": [567.302, 573.0], "votes": 0, "UUID": "inner-c"},
    ]
    segs, coverage = _process_sponsor_segments(raw, min_votes=0)
    assert [s["uuid"] for s in segs] == ["outer", "inner-b", "inner-c", "inner-a"]
    assert all(s.get("votes", 0) >= 0 for s in segs)
    assert "rejected" not in {s["uuid"] for s in segs}
    assert segs[0]["overlapsWith"]
    assert "inner-b" in segs[0]["overlapsWith"]
    assert coverage == _merged_coverage_seconds(segs)
    assert coverage == 83.686
    # Sum of durations double-counts; coverage must be smaller.
    summed = sum(s["durationSeconds"] for s in segs)
    assert coverage < summed
