"""Smoke tests for URL extraction helpers."""

from app.utils.url import (
    extract_facebook_page,
    extract_facebook_video_id,
    extract_instagram_shortcode,
    extract_instagram_username,
    extract_tiktok_id,
    extract_tiktok_username,
    extract_youtube_id,
    is_youtube_short,
    normalize_youtube_url,
)


def test_youtube_id_watch_url():
    assert extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_youtube_id_short_url():
    assert extract_youtube_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_youtube_id_shorts():
    assert extract_youtube_id("https://youtube.com/shorts/abcdefghijk") == "abcdefghijk"
    assert is_youtube_short("https://youtube.com/shorts/abcdefghijk") is True


def test_youtube_id_invalid():
    assert extract_youtube_id("https://example.com") is None


def test_normalize_youtube():
    assert normalize_youtube_url("https://youtu.be/dQw4w9WgXcQ") == \
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_tiktok_id():
    assert extract_tiktok_id("https://www.tiktok.com/@user/video/1234567890") == "1234567890"
    assert extract_tiktok_username("https://www.tiktok.com/@charlidamelio") == "charlidamelio"


def test_instagram():
    assert extract_instagram_shortcode("https://www.instagram.com/reel/Cabcdef123/") == "Cabcdef123"
    assert extract_instagram_shortcode("https://www.instagram.com/p/Cabcdef123/") == "Cabcdef123"
    assert extract_instagram_username("https://instagram.com/zuck/") == "zuck"
    assert extract_instagram_username("https://instagram.com/p/Cabcdef123/") is None


def test_facebook():
    assert extract_facebook_video_id("https://facebook.com/watch?v=1234567890") == "1234567890"
    assert extract_facebook_page("https://facebook.com/mypage") == "mypage"
