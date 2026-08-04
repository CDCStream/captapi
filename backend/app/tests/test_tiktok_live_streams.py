from __future__ import annotations

from app.services.tiktok_native import _extract_stream_qualities, _extract_stream_urls


def _sample_room_with_hls() -> dict:
    """Minimal liveRoom shaped like TikTok streamData (triple-nested JSON string)."""
    import json

    stream_data = {
        "data": {
            "hd": {
                "main": {
                    "flv": "https://pull.example/stream_hd.flv?sign=1",
                    "hls": "https://pull-hls.example/stream_hd/index.m3u8?sign=1",
                    "cmaf": "https://pull.example/stream_hd/index.mpd?sign=1",
                    "dash": "",
                    "lls": "https://pull.example/stream_hd.sdp?sign=1",
                    "sdk_params": json.dumps(
                        {"vbitrate": 1000000, "resolution": "720x1280", "VCodec": "h264"}
                    ),
                }
            }
        }
    }
    return {
        "streamData": {"pull_data": {"stream_data": json.dumps(stream_data)}},
        "hevcStreamData": {},
    }


def test_extract_stream_qualities_keeps_hls_cmaf_dash_lls() -> None:
    rows = _extract_stream_qualities(_sample_room_with_hls())
    assert len(rows) == 1
    row = rows[0]
    assert row["quality"] == "hd"
    assert row["codec"] == "h264"
    assert row["resolution"] == "720x1280"
    assert row["bitrate"] == 1000000
    assert row["flv"].endswith(".flv?sign=1")
    assert ".m3u8" in row["hls"]
    assert ".mpd" in row["cmaf"]
    assert row["dash"] == row["cmaf"]  # dash filled from cmaf when empty
    assert row["lls"].endswith(".sdp?sign=1")


def test_extract_stream_urls_prefers_hls_before_flv() -> None:
    urls = _extract_stream_urls(_sample_room_with_hls())
    assert any(".m3u8" in u for u in urls)
    assert urls[0].endswith("index.m3u8?sign=1") or ".m3u8" in urls[0]