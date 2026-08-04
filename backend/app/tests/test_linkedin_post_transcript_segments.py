"""Text-only transcript contract: null timings + char offsets."""

from app.routers.linkedin import _author_url_from_post_url
from app.utils.text_transcript import (
    TIMING_NONE,
    finalize_text_segments,
    paragraph_text_segments,
)


def test_paragraph_segments_null_timings_and_offsets():
    text = (
        "First paragraph with enough words here.\n"
        "\u00a0\n"
        "Second paragraph also has enough words.\n\n"
        "Third paragraph wraps the example up."
    )
    transcript, segs, read_secs = paragraph_text_segments(text)
    assert len(segs) == 3
    assert read_secs >= 1
    for i, seg in enumerate(segs):
        assert seg["index"] == i
        assert seg["start"] is None
        assert seg["duration"] is None
        assert seg["timestamp"] is None
        assert seg["wordCount"] >= 1
        assert transcript[seg["charStart"] : seg["charEnd"]] == seg["text"]


def test_bridgewater_style_splits():
    text = (
        "Instead of watching another Netflix series tonight, watch this talk from Bridgewater applied AI team.\n\n"
        "It is the clearest most practical look at how a top quant firm builds agents.\n\n"
        "Whether you have never shipped agents or you are already deep in systems.\n\n"
        "And together with this guide you can turn Claude into an analyst: https://lnkd.in/dCfFQXCh\n\n"
        "Bookmark it and watch the talk today."
    )
    transcript, segs, _ = paragraph_text_segments(text)
    assert len(segs) == 5
    assert "Netflix" in segs[0]["text"]
    assert transcript[segs[3]["charStart"] : segs[3]["charEnd"]] == segs[3]["text"]


def test_finalize_reddit_style_segments():
    raw = [
        {"speaker": "post", "text": "Title: Hello there"},
        {"speaker": "alice", "text": "Body text here"},
        {"speaker": "bob", "text": "bob: A comment reply"},
    ]
    transcript = "\n\n".join(s["text"] for s in raw)
    segs, read_secs = finalize_text_segments(transcript, raw)
    assert TIMING_NONE == "none"
    assert read_secs >= 1
    assert segs[0]["speaker"] == "post"
    assert segs[0]["start"] is None
    assert transcript[segs[2]["charStart"] : segs[2]["charEnd"]] == "bob: A comment reply"


def test_author_url_from_ugc_post_only():
    assert (
        _author_url_from_post_url(
            "https://www.linkedin.com/posts/linasbeliunas_instead-ugcPost-7490484891248291841-Nbnn/"
        )
        == "https://www.linkedin.com/in/linasbeliunas"
    )
    assert (
        _author_url_from_post_url(
            "https://www.linkedin.com/posts/microsoft_x-activity-7477715981667086336-x68i"
        )
        is None
    )