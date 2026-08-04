"""Text-only transcript contract: omit cue keys + char offsets."""

from app.routers.linkedin import _author_url_from_post_url, _normalize_post
from app.services.linkedin_native import (
    _post_from_social_ld,
    strip_comments_on_linkedin_suffix,
)
from app.utils.text_transcript import (
    TIMING_NONE,
    count_words,
    finalize_text_segments,
    paragraph_text_segments,
)


def test_paragraph_segments_omit_cue_keys():
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
        assert "start" not in seg
        assert "duration" not in seg
        assert "timestamp" not in seg
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


def test_finalize_reddit_style_segments_omit_cues():
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
    assert "start" not in segs[0]
    assert "duration" not in segs[0]
    assert "timestamp" not in segs[0]
    assert transcript[segs[2]["charStart"] : segs[2]["charEnd"]] == "bob: A comment reply"


def test_count_words_emoji_zero_url_one():
    # 17 words + 1 URL + 1 emoji → 18 (emoji is not a word; old split() reported 19).
    words = " ".join(f"w{i}" for i in range(17))
    text = f"{words} https://lnkd.in/dCfFQXCh 📊"
    assert count_words(text) == 18
    assert len(text.split()) == 19
    assert count_words("📊:") == 0
    assert count_words("hello 🚀 world") == 2


def test_strip_comments_on_linkedin_suffix():
    body = "Great post about agents and systems"
    dirty = f"{body} | 10 comments on LinkedIn"
    assert strip_comments_on_linkedin_suffix(dirty) == body
    assert strip_comments_on_linkedin_suffix(f"{body} | 1 comment on LinkedIn") == body
    assert strip_comments_on_linkedin_suffix(body) == body


def test_video_object_ld_keeps_date_published():
    block = {
        "@type": "VideoObject",
        "description": "Hello world from a ugcPost | 10 comments on LinkedIn",
        "datePublished": "2026-08-04T19:14:43.873Z",
        "creator": {"name": "Linas Beliūnas", "url": "https://www.linkedin.com/in/linasbeliunas"},
        "url": "https://www.linkedin.com/posts/linasbeliunas_x-ugcPost-7490484891248291841-Nbnn/",
    }
    post = _post_from_social_ld(block, fallback_url=block["url"])
    assert post is not None
    assert post["datePublished"] == "2026-08-04T19:14:43.873Z"
    assert post["text"] == "Hello world from a ugcPost"
    assert "comments on LinkedIn" not in (post["text"] or "")
    assert post["author"]["name"] == "Linas Beliūnas"
    assert "headline" not in post["author"]


def test_normalize_post_drops_followers_headline():
    row = _normalize_post(
        {
            "text": "hi",
            "datePublished": "2026-07-04T13:19:24Z",
            "author": {"name": "Microsoft", "headline": "28,652,029 followers"},
        }
    )
    assert "headline" not in row["author"]
    assert row["publishedAt"] == "2026-07-04T13:19:24Z"


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
