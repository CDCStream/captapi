from app.utils.formatters import language_name_from_code
from app.services.youtube_native import _caption_track_name, _available_caption_languages


def test_language_name_from_code_common() -> None:
    assert language_name_from_code("en") == "English"
    assert language_name_from_code("en-US") == "English"
    assert language_name_from_code("tr") == "Turkish"
    assert language_name_from_code("zh-Hans") == "Chinese (Simplified)"
    assert language_name_from_code("iw") == "Hebrew"


def test_caption_track_name_falls_back_to_code() -> None:
    # ANDROID-style: languageCode present, name empty / unusable.
    assert _caption_track_name({"languageCode": "en", "name": {}}) == "English"
    assert _caption_track_name({"languageCode": "en", "name": {"runs": []}}) == "English"
    assert _caption_track_name({"languageCode": "de"}) == "German"


def test_caption_track_name_prefers_youtube_label() -> None:
    assert (
        _caption_track_name(
            {"languageCode": "en", "name": {"simpleText": "English (auto-generated)"}}
        )
        == "English (auto-generated)"
    )


def test_available_languages_never_null_name_for_known_codes() -> None:
    rows = _available_caption_languages(
        [{"languageCode": "en", "kind": "asr", "name": {}}, {"languageCode": "es"}]
    )
    by = {r["languageCode"]: r["languageName"] for r in rows}
    assert by["en"] == "English"
    assert by["es"] == "Spanish"