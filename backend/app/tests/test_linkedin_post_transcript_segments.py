"""LinkedIn post-transcript paragraph segmentation."""

from app.routers.linkedin import (
    _author_url_from_post_url,
    _paragraph_transcript_segments,
)


def test_splits_blank_line_paragraphs_including_nbsp():
    text = (
        "First paragraph with enough words here.\n"
        "\u00a0\n"
        "Second paragraph also has enough words.\n\n"
        "Third paragraph wraps the example up."
    )
    segs = _paragraph_transcript_segments(text)
    assert len(segs) == 3
    assert segs[0]["text"].startswith("First")
    assert segs[1]["text"].startswith("Second")
    assert segs[2]["text"].startswith("Third")
    assert segs[0]["start"] == 0
    assert segs[1]["start"] > 0
    assert segs[0]["duration"] > 0
    assert segs[0]["timestamp"] == "00:00"


def test_bridgewater_style_post_splits():
    text = (
        "Instead of watching another Netflix series tonight, watch this talk from Bridgewater applied AI team.\n\n"
        "It is the clearest most practical look at how a top quant firm builds agents.\n\n"
        "Whether you have never shipped agents or you are already deep in systems.\n\n"
        "And together with this guide you can turn Claude into an analyst: https://lnkd.in/dCfFQXCh\n\n"
        "Bookmark it and watch the talk today."
    )
    segs = _paragraph_transcript_segments(text)
    assert len(segs) == 5
    assert "Netflix" in segs[0]["text"]
    assert "lnkd.in" in segs[3]["text"]


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