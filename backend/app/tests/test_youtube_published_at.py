"""Tests for YouTube relative -> ISO publishedAt coercion."""

from __future__ import annotations

from datetime import datetime, timezone

from app.services.youtube_native import (
    _comment_payload_to_api,
    _comment_published_time,
    _has_creator_heart,
    _resolve_youtube_category_id,
    approximate_iso_from_relative,
    coerce_published_fields,
    published_fields,
)

NOW = datetime(2026, 8, 2, 12, 0, 0, tzinfo=timezone.utc)


def test_approximate_iso_from_relative_common_labels() -> None:
    # Truncated to day — not fetch-time wall-clock seconds.
    assert approximate_iso_from_relative("4 days ago", now=NOW) == "2026-07-29T00:00:00.000Z"
    assert approximate_iso_from_relative("1 month ago", now=NOW) == "2026-07-03T00:00:00.000Z"
    assert approximate_iso_from_relative("5d ago", now=NOW) == "2026-07-28T00:00:00.000Z"
    assert approximate_iso_from_relative("Streamed 3 days ago", now=NOW) == "2026-07-30T00:00:00.000Z"


def test_hour_label_truncated_to_hour() -> None:
    assert (
        approximate_iso_from_relative("22 hours ago", now=NOW) == "2026-08-01T14:00:00.000Z"
    )


def test_day_label_stable_across_fetch_times_same_day() -> None:
    """Same relative day label + same UTC calendar day → identical truncated ISO."""
    a = approximate_iso_from_relative(
        "7 days ago",
        now=datetime(2026, 8, 8, 11, 26, 22, tzinfo=timezone.utc),
    )
    b = approximate_iso_from_relative(
        "7 days ago",
        now=datetime(2026, 8, 8, 23, 59, 59, tzinfo=timezone.utc),
    )
    assert a == b == "2026-08-01T00:00:00.000Z"


def test_published_fields_splits_iso_and_text() -> None:
    iso, text = published_fields("4 days ago")
    assert iso and iso.endswith("Z") and "T" in iso
    assert text == "4 days ago"
    iso2, text2 = published_fields("2026-07-27T22:52:21.000Z")
    assert iso2 == "2026-07-27T22:52:21.000Z"
    assert text2 is None


def test_coerce_never_leaves_relative_in_published_at() -> None:
    card = {"publishedAt": "4 days ago", "title": "x"}
    out = coerce_published_fields(card)
    assert out["publishedAt"] and "ago" not in out["publishedAt"]
    assert out["publishedTimeText"] == "4 days ago"
    # Already ISO stays
    card2 = {"publishedAt": "2026-07-27T22:52:21.000Z", "publishedTimeText": "4 days ago"}
    out2 = coerce_published_fields(card2)
    assert out2["publishedAt"] == "2026-07-27T22:52:21.000Z"


def test_inactive_heart_tooltip_by_channel_is_false() -> None:
    # Live InnerTube chrome on rickroll — tooltip on every comment, no real heart.
    assert _has_creator_heart({"heartActiveTooltip": "\u2764 by @RickAstleyYT"}) is False


def test_explicit_hearted_tooltip_is_true() -> None:
    assert _has_creator_heart({"heartActiveTooltip": "Hearted by @RickAstleyYT"}) is True


def test_creator_heart_renderer_with_thumbnail_is_true() -> None:
    assert (
        _has_creator_heart(
            {
                "creatorHeart": {
                    "creatorHeartRenderer": {
                        "creatorThumbnail": {
                            "thumbnails": [{"url": "https://yt3.ggpht.com/x"}]
                        }
                    }
                }
            }
        )
        is True
    )


def test_comment_published_time_approx_from_relative_including_edited() -> None:
    edited = "1 month ago " + "(edited)"
    text, iso, is_approx = _comment_published_time({"publishedTime": edited})
    assert text == edited
    assert iso is not None and "T" in iso and "ago" not in iso
    assert is_approx is True
    # Day precision — :00:00 not fetch-second :22.000
    assert iso.endswith("T00:00:00.000Z")


def test_comment_published_time_exact_not_flagged_approximate() -> None:
    text, iso, is_approx = _comment_published_time(
        {
            "publishedTimeText": "1 year ago",
            "publishedAt": "2025-01-15T10:11:12.000Z",
        }
    )
    assert iso == "2025-01-15T10:11:12.000Z"
    assert is_approx is False


def test_comment_payload_uses_published_time_approx_not_published_time() -> None:
    row = _comment_payload_to_api(
        {
            "properties": {
                "commentId": "UgkxTest",
                "content": {"content": "hello"},
                "publishedTime": "7 days ago",
            },
            "author": {"displayName": "Viewer"},
            "toolbar": {},
        }
    )
    assert row is not None
    assert "publishedTime" not in row
    assert row["publishedTimeText"] == "7 days ago"
    assert row["publishedTimeApprox"] is not None
    assert row["publishedTimeIsApproximate"] is True
    assert row["publishedTimeApprox"].endswith("T00:00:00.000Z")


def test_category_id_from_genre_when_id_missing() -> None:
    assert _resolve_youtube_category_id(None, "Music") == "10"
    assert _resolve_youtube_category_id("22", "People & Blogs") == "22"
    assert _resolve_youtube_category_id(None, None) is None


def test_community_poll_options_and_numeric_likes() -> None:
    from app.services.youtube_native import _normalize_community_post

    post = {
        "postId": "UgkxPollTest",
        "contentText": {"runs": [{"text": "Would you rather A or B?"}]},
        "publishedTimeText": {"simpleText": "2 weeks ago"},
        "voteCount": {"simpleText": "89K"},
        "authorText": {"runs": [{"text": "MrBeast"}]},
        "authorEndpoint": {
            "browseEndpoint": {
                "browseId": "UCX6OQ3DkcsbYNE6H8uQQuVA",
                "canonicalBaseUrl": "/@MrBeast",
            }
        },
        "backstageAttachment": {
            "pollRenderer": {
                "choices": [
                    {"text": {"runs": [{"text": "Option A"}]}},
                    {"text": {"runs": [{"text": "Option B"}]}},
                ],
                "totalVotes": {"simpleText": "1.6M votes"},
            }
        },
    }
    row = _normalize_community_post(post)
    assert row is not None
    assert row["postType"] == "poll"
    assert row["likeCount"] == 89000
    assert row["likeCountText"] == "89K"
    assert row["likeCountApproximate"] is True
    assert row["publishedTime"] and "T" in row["publishedTime"]
    assert row["publishedAt"] == row["publishedTime"]
    assert [o["text"] for o in row["pollOptions"]] == ["Option A", "Option B"]
    assert row["pollOptions"][0]["voteCount"] is None
    assert row["totalVotes"] == 1_600_000
    assert row["channel"]["id"] == "UCX6OQ3DkcsbYNE6H8uQQuVA"
