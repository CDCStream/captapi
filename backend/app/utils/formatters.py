"""Common output formatters."""

from __future__ import annotations


def seconds_to_timestamp(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    mm = int(seconds // 60)
    ss = int(seconds % 60)
    return f"{mm:02d}:{ss:02d}"


def safe_int(v) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def safe_float(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def safe_str(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def safe_list(v) -> list:
    if isinstance(v, list):
        return v
    return []


def first_present(*values):
    """First value that is not None — unlike `a or b`, keeps 0 / False / ''."""
    for v in values:
        if v is not None:
            return v
    return None


_LANG_NAME_TO_ISO: dict[str, str] = {
    "afrikaans": "af", "albanian": "sq", "arabic": "ar", "armenian": "hy",
    "azerbaijani": "az", "basque": "eu", "belarusian": "be", "bengali": "bn",
    "bosnian": "bs", "bulgarian": "bg", "catalan": "ca", "chinese": "zh",
    "croatian": "hr", "czech": "cs", "danish": "da", "dutch": "nl",
    "english": "en", "estonian": "et", "filipino": "fil", "finnish": "fi",
    "french": "fr", "galician": "gl", "georgian": "ka", "german": "de",
    "greek": "el", "gujarati": "gu", "haitian creole": "ht", "hebrew": "he",
    "hindi": "hi", "hungarian": "hu", "icelandic": "is", "indonesian": "id",
    "irish": "ga", "italian": "it", "japanese": "ja", "kannada": "kn",
    "kazakh": "kk", "korean": "ko", "latvian": "lv", "lithuanian": "lt",
    "macedonian": "mk", "malay": "ms", "malayalam": "ml", "maltese": "mt",
    "marathi": "mr", "mongolian": "mn", "nepali": "ne", "norwegian": "no",
    "persian": "fa", "polish": "pl", "portuguese": "pt", "punjabi": "pa",
    "romanian": "ro", "russian": "ru", "serbian": "sr", "sinhala": "si",
    "slovak": "sk", "slovenian": "sl", "spanish": "es", "swahili": "sw",
    "swedish": "sv", "tamil": "ta", "telugu": "te", "thai": "th",
    "turkish": "tr", "ukrainian": "uk", "urdu": "ur", "uzbek": "uz",
    "vietnamese": "vi", "welsh": "cy",
}


def normalize_language_code(value: str | None) -> str | None:
    """Normalize a language value to an ISO 639-1 code (lowercase 2-3 letters).

    Handles: 'English' -> 'en', 'en-US' -> 'en', 'en' -> 'en', None -> None.
    """
    if not value:
        return None
    v = value.strip().lower()
    if not v:
        return None
    if len(v) <= 3:
        return v
    if "-" in v and len(v.split("-")[0]) <= 3:
        return v.split("-")[0]
    return _LANG_NAME_TO_ISO.get(v, v)
