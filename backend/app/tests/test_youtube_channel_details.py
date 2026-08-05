from __future__ import annotations

from app.services.youtube_native import (
    _absolute_http_url,
    _channel_banner_url,
    _channel_tags,
    _parse_joined_at,
)


def test_channel_tags_quote_aware_keeps_multiword():
    raw = (
        '"medical facts" neuroscience anatomy "psychology facts" '
        '"USA science facts" mdct "manjit mandal"'
    )
    tags = _channel_tags(raw)
    assert "medical facts" in tags
    assert "psychology facts" in tags
    assert "USA science facts" in tags
    assert "manjit mandal" in tags
    assert "neuroscience" in tags
    assert '"medical' not in tags
    assert 'facts"' not in tags
    assert tags.count("USA science facts") == 1


def test_channel_tags_list_passthrough():
    assert _channel_tags(["a", "b c", None, ""]) == ["a", "b c"]


def test_absolute_http_url_adds_scheme():
    assert _absolute_http_url("instagram.com/foo") == "https://instagram.com/foo"
    assert _absolute_http_url("https://x.com/y") == "https://x.com/y"
    assert _absolute_http_url("/channel/UC123") == "https://www.youtube.com/channel/UC123"
    assert _absolute_http_url("//facebook.com/z") == "https://facebook.com/z"


def test_parse_joined_at_iso():
    assert _parse_joined_at("Jul 31, 2017") == "2017-07-31"
    assert _parse_joined_at("Joined Feb 19, 2012") == "2012-02-19"
    assert _parse_joined_at("2017-07-31") == "2017-07-31"


def test_banner_null_when_only_avatar_in_header():
    avatar = (
        "https://yt3.googleusercontent.com/"
        "wbR6xQZHjrw4cYVuTkbSLo2zpugbijJyVk2bpAaKQx2Lvia0H_aE8zZP9yA6lI4WtocJs4grJl4="
        "s900-c-k-c0x00ffffff-no-rj"
    )
    data = {
        "header": {
            "pageHeaderRenderer": {
                "content": {
                    "pageHeaderViewModel": {
                        "image": {
                            "sources": [
                                {"url": avatar.replace("s900", "s160")},
                            ]
                        }
                    }
                }
            }
        }
    }
    assert _channel_banner_url(data, avatar=avatar) is None


def test_banner_from_c4_tabbed_header():
    banner = (
        "https://yt3.googleusercontent.com/"
        "BANNERFILEID1234567890abcdefghijkl="
        "w2560-fcrop64=1,00000000ffffffff-k-c0xffffffff-no-nd-rj"
    )
    avatar = (
        "https://yt3.googleusercontent.com/"
        "AVATARFILEID1234567890abcdefghijkl="
        "s900-c-k-c0x00ffffff-no-rj"
    )
    data = {
        "header": {
            "c4TabbedHeaderRenderer": {
                "banner": {"thumbnails": [{"url": banner}]},
                "avatar": {"thumbnails": [{"url": avatar}]},
            }
        }
    }
    assert _channel_banner_url(data, avatar=avatar) == banner
