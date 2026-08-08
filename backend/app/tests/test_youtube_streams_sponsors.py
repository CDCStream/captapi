"""Tests for channel-streams Live-tab gate and SponsorBlock processing."""

from __future__ import annotations

from app.routers.youtube import (
    _merged_coverage_seconds,
    _process_sponsor_segments,
    _sponsorblock_envelope,
)
from app.services.youtube_native import (
    _lockup_result_type,
    _normalize_community_post,
    apply_channel_stream_row,
    collect_playlist_cards,
    finalize_channel_list_card,
    format_duration_hms,
    stream_live_status,
)


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
    assert "videoCount" not in rows[0]
    assert "totalVideos" in rows[0]


def test_lockup_types_from_published_labels() -> None:
    assert _lockup_result_type("Streamed 1 hour ago") == "stream"
    assert _lockup_result_type("Scheduled for 8/12/26, 10:15 AM") == "upcoming"
    assert _lockup_result_type("4 days ago") == "video"
    assert _lockup_result_type(None, badges=["LIVE"]) == "live"


def test_zero_duration_is_null_not_midnight() -> None:
    assert format_duration_hms(0) is None
    row = finalize_channel_list_card(
        vid="abcdefghijk",
        details={
            "title": "lofi",
            "durationSeconds": 0,
            "viewCount": 100,
            "viewCountIsApproximate": False,
            "channelId": "UCxxxxxxxxxxxxxxxxxxxxxx",
            "channelName": "Lofi Girl",
        },
        shelf={"type": "video", "publishedTimeText": "Streamed 2 days ago"},
        content_type="video",
    )
    assert row["durationSeconds"] is None
    assert row["durationFormatted"] is None


def test_stream_live_status_and_row_semantics() -> None:
    assert stream_live_status(details={"liveStatus": "live"}) == "live"
    assert stream_live_status(details={"liveStatus": "upcoming"}) == "upcoming"
    assert stream_live_status(details={"liveStatus": "ended"}) == "past"
    assert stream_live_status(details=None, shelf_type="video") == "past"

    row = apply_channel_stream_row(
        {
            "type": "video",
            "durationSeconds": 0,
            "durationFormatted": "00:00:00",
        },
        details={"liveStatus": "ended"},
        shelf={"type": "video"},
    )
    assert row["liveStatus"] == "past"
    assert row["type"] == "stream"
    assert row["durationSeconds"] is None
    assert row["durationFormatted"] is None

    live = apply_channel_stream_row(
        {"type": "live", "durationSeconds": None},
        details={"liveStatus": "live"},
        shelf={"type": "live"},
    )
    assert live["liveStatus"] == "live"
    assert live["type"] == "stream"


def test_sponsorblock_envelope_always_has_duration_and_license() -> None:
    empty = _sponsorblock_envelope(
        vid="dQw4w9WgXcQ",
        video_duration=212,
        min_votes=0,
        segments=[],
        coverage=0.0,
    )
    assert empty["videoDurationSeconds"] == 212
    assert empty["totalReturned"] == 0
    assert empty["source"] == "sponsorblock"
    assert empty["sourceUrl"] == "https://sponsor.ajay.app/"
    assert empty["license"] == "CC BY-NC-SA 4.0"
    assert empty["segments"] == []


def test_community_post_edited_and_no_poll_nulls() -> None:
    post = {
        "postId": "UgkxImage",
        "contentText": {"runs": [{"text": "hello"}]},
        "publishedTimeText": {"simpleText": "2 months ago (edited)"},
        "voteCount": {"simpleText": "732K"},
        "authorText": {"runs": [{"text": "MrBeast"}]},
        "authorEndpoint": {
            "browseEndpoint": {
                "browseId": "UCX6OQ3DkcsbYNE6H8uQQuVA",
                "canonicalBaseUrl": "/@MrBeast",
            }
        },
        "backstageAttachment": {
            "backstageImageRenderer": {
                "image": {"thumbnails": [{"url": "https://example.com/a.jpg"}]},
            }
        },
    }
    row = _normalize_community_post(post)
    assert row is not None
    assert row["isEdited"] is True
    assert row["publishedTimeText"] == "2 months ago"
    assert "(edited)" not in (row["publishedTimeText"] or "")
    assert "sourceUrl" not in row
    assert "pollOptions" not in row
    assert "totalVotes" not in row
    assert "totalVotesIsApproximate" not in row


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
