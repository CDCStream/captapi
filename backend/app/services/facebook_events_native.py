"""Native Facebook events via Decodo JS-rendered HTML (no Apify).

Facebook returns 400 on plain datacenter/residential for /events pages.
Decodo headless=html hydrates ScheduledServerJS payloads that embed event
cards for page listings. Keyword discovery (/events/?q=...) is often
login-walled logged-out; we recover via Google SERP → event-details hydrate,
with Apify as the router fallthrough.
"""

from __future__ import annotations

import asyncio
import html as html_lib
import json
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo

import structlog

from app.services import decodo_fetch
from app.utils.formatters import safe_str

log = structlog.get_logger(__name__)

# Facebook day_time_sentence ends with a TZ abbreviation (CDT, EDT, …).
# Map to IANA so startDate keeps the calendar day the host advertised.
# Never map to Etc/* — fixed-offset zones do not observe DST (FE1).
_TZ_ABBREV_TO_IANA: dict[str, str] = {
    "UTC": "UTC",
    "GMT": "Europe/London",
    "BST": "Europe/London",
    "CET": "Europe/Berlin",
    "CEST": "Europe/Berlin",
    "WET": "Europe/Lisbon",
    "WEST": "Europe/Lisbon",
    "EET": "Europe/Bucharest",
    "EEST": "Europe/Bucharest",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "AKST": "America/Anchorage",
    "AKDT": "America/Anchorage",
    "HST": "Pacific/Honolulu",
    "HDT": "Pacific/Honolulu",
    "AST": "America/Halifax",
    "ADT": "America/Halifax",
    "NST": "America/St_Johns",
    "NDT": "America/St_Johns",
}

_tf: Any = None


def _timezone_finder() -> Any:
    """Lazy TimezoneFinder singleton (lat/lng → IANA)."""
    global _tf
    if _tf is None:
        from timezonefinder import TimezoneFinder

        _tf = TimezoneFinder()
    return _tf


def sanitize_iana_timezone(name: str | None) -> str | None:
    """Accept a real IANA zone; reject empty and fixed-offset ``Etc/*`` (FE1)."""
    raw = (name or "").strip()
    if not raw:
        return None
    if raw.startswith("Etc/"):
        return None
    try:
        ZoneInfo(raw)
    except Exception:  # noqa: BLE001
        return None
    return raw


def timezone_from_coords(latitude: Any, longitude: Any) -> str | None:
    """lat/lng → IANA. Returns None when unknown or would be Etc/*."""
    try:
        lat = float(latitude)
        lng = float(longitude)
    except (TypeError, ValueError):
        return None
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
        return None
    try:
        found = _timezone_finder().timezone_at(lng=lng, lat=lat)
    except Exception:  # noqa: BLE001
        return None
    return sanitize_iana_timezone(found)


def resolve_event_timezone(
    *,
    raw_timezone: str | None = None,
    sentence: str | None = None,
    latitude: Any = None,
    longitude: Any = None,
) -> str | None:
    """Pick a venue IANA zone — coords first, then abbrev / raw, never Etc/*.

    Order (FE1):
    1. lat/lng → IANA (venue ground truth; handles GMT vs Europe/London)
    2. Facebook/raw timezone when it is a real non-Etc zone
    3. Abbreviation from the display sentence (GMT → Europe/London)
    4. null — caller must not invent a fixed-offset stand-in
    """
    from_coords = timezone_from_coords(latitude, longitude)
    if from_coords:
        return from_coords
    for candidate in (
        sanitize_iana_timezone(raw_timezone),
        sanitize_iana_timezone(_timezone_from_sentence(sentence)),
    ):
        if candidate:
            return candidate
    return None

# One Decodo JS render is ~$0.001–0.01; flat 2 credits (~120% markup headroom).
CREDIT_FB_EVENTS_NATIVE = 2

_SCROLL_ACTIONS: list[dict[str, Any]] = [
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
    {"type": "scroll", "x": 0, "y": 2800},
    {"type": "wait", "wait_time_s": 2},
]

_EVENT_HREF_RE = re.compile(
    r'href="https://www\.facebook\.com/events/(\d{6,})/?["?]',
    re.IGNORECASE,
)
_NOISE_TITLES = {
    "events",
    "upcoming",
    "past",
    "hosting",
    "·",
    "see all",
    "log in",
    "sign up",
}


def page_events_url(page_url: str) -> str:
    base = (page_url or "").strip().rstrip("/")
    if not base:
        return base
    if base.lower().endswith("/events"):
        return base
    return f"{base}/events"


def search_events_url(q: str) -> str:
    # /events/search/?q= returns an empty shell; /events/?q= is the discovery UI
    # (often login-walled logged-out — may still be worth a Decodo attempt).
    return f"https://www.facebook.com/events/?q={quote_plus((q or '').strip())}"


def _extract_balanced_json(s: str, start: int) -> str | None:
    if start < 0 or start >= len(s) or s[start] not in "{[":
        return None
    open_ch, close_ch = ("{", "}") if s[start] == "{" else ("[", "]")
    depth = 0
    in_str = False
    esc = False
    for i in range(start, min(len(s), start + 2_500_000)):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return s[start : i + 1]
    return None


def _walk_events(obj: Any, found: list[dict[str, Any]], depth: int = 0) -> None:
    if depth > 40:
        return
    if isinstance(obj, dict):
        event_url = obj.get("eventUrl") or obj.get("event_url") or obj.get("url")
        eid = obj.get("id") or obj.get("event_id") or obj.get("eventId")
        name = obj.get("name") or obj.get("title")
        ts = obj.get("start_timestamp") or obj.get("startTimestamp")
        if (
            isinstance(event_url, str)
            and "/events/" in event_url
            and name
            and (ts is not None or obj.get("day_time_sentence"))
        ):
            found.append(obj)
        elif (
            eid
            and str(eid).isdigit()
            and len(str(eid)) >= 5
            and name
            and ts is not None
            and (obj.get("eventUrl") or obj.get("day_time_sentence") or obj.get("event_place") is not None)
        ):
            found.append(obj)
        for v in obj.values():
            _walk_events(v, found, depth + 1)
    elif isinstance(obj, list):
        for v in obj[:400]:
            _walk_events(v, found, depth + 1)


def _unescape_js_str(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except Exception:  # noqa: BLE001
        return value.replace("\\/", "/").replace('\\"', '"')


def _regex_fallback_events(html: str) -> list[dict[str, Any]]:
    """Recover cards when JSON blob walks miss nested name fields."""
    out: list[dict[str, Any]] = []
    for m in re.finditer(
        r'"eventUrl"\s*:\s*"(https:\\/\\/www\.facebook\.com\\/events\\/(\d+)\\/?)"',
        html,
    ):
        chunk = html[max(0, m.start() - 3500) : m.end() + 2500]
        name_m = re.search(r'"name"\s*:\s*"((?:\\.|[^"\\])*)"', chunk)
        ts_m = re.search(r'"start_timestamp"\s*:\s*(\d+)', chunk)
        dts_m = re.search(r'"day_time_sentence"\s*:\s*"((?:\\.|[^"\\])*)"', chunk)
        if not name_m or not (ts_m or dts_m):
            continue
        name = _unescape_js_str(name_m.group(1))
        if name.lower() in _NOISE_TITLES:
            continue
        eid = m.group(2)
        out.append(
            {
                "id": eid,
                "name": name,
                "eventUrl": f"https://www.facebook.com/events/{eid}/",
                "start_timestamp": int(ts_m.group(1)) if ts_m else None,
                "day_time_sentence": _unescape_js_str(dts_m.group(1)) if dts_m else None,
            }
        )
    return out


def _html_anchor_events(html: str) -> list[dict[str, Any]]:
    """Titles (and optional venue) from rendered ``/events/{id}/`` anchors.

    Relay JSON only embeds ~8 full cards; the scrolled DOM lists many more
    as plain links with adjacent text nodes.
    """
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in _EVENT_HREF_RE.finditer(html or ""):
        eid = m.group(1)
        if eid in seen:
            continue
        chunk = (html or "")[m.end() : m.end() + 700]
        texts = [
            html_lib.unescape(t).strip()
            for t in re.findall(r">([^<>]{2,160})<", chunk)
            if t and t.strip()
        ]
        cleaned: list[str] = []
        for t in texts:
            low = t.lower().strip()
            if low in _NOISE_TITLES or low.isdigit():
                continue
            if "going" in low or "interested" in low:
                continue
            if re.fullmatch(r"[\d,.\s]+", t):
                continue
            cleaned.append(t)
        if not cleaned:
            continue
        seen.add(eid)
        place_name = cleaned[1] if len(cleaned) > 1 else None
        # Second text is often a date sentence ("Sat, Aug 2") — keep as day_time.
        day_time = None
        venue = None
        if place_name:
            if re.search(
                r"\b(mon|tue|wed|thu|fri|sat|sun|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b",
                place_name,
                re.I,
            ) or re.search(r"\d{1,2}:\d{2}", place_name):
                day_time = place_name
            else:
                venue = place_name
        raw: dict[str, Any] = {
            "id": eid,
            "name": cleaned[0],
            "eventUrl": f"https://www.facebook.com/events/{eid}/",
            "day_time_sentence": day_time,
        }
        if venue:
            raw["event_place"] = {"contextual_name": venue}
        out.append(raw)
    return out


def extract_events_from_html(html: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for m in re.finditer(r"ScheduledServerJS", html or ""):
        start = (html or "").find("{", m.start())
        blob = _extract_balanced_json(html or "", start)
        if not blob or len(blob) < 200:
            continue
        try:
            data = json.loads(blob)
        except ValueError:
            continue
        _walk_events(data, found)
    if len(found) < 3:
        found.extend(_regex_fallback_events(html or ""))
    # DOM anchors fill the long-tail the Relay blobs omit.
    found.extend(_html_anchor_events(html or ""))

    by_id: dict[str, dict[str, Any]] = {}
    for raw in found:
        eid = str(raw.get("id") or raw.get("event_id") or "")
        if not eid.isdigit():
            url = str(raw.get("eventUrl") or raw.get("url") or "")
            m = re.search(r"/events/(\d+)", url)
            eid = m.group(1) if m else ""
        if not eid:
            continue
        prev = by_id.get(eid)
        if prev is None:
            by_id[eid] = raw
            continue
        # Prefer richer Relay cards (timestamp / place / cover) over anchors.
        prev_score = (
            (2 if prev.get("start_timestamp") or prev.get("startTimestamp") else 0)
            + (1 if prev.get("event_place") or prev.get("cover_photo") else 0)
            + (1 if prev.get("day_time_sentence") else 0)
        )
        raw_score = (
            (2 if raw.get("start_timestamp") or raw.get("startTimestamp") else 0)
            + (1 if raw.get("event_place") or raw.get("cover_photo") else 0)
            + (1 if raw.get("day_time_sentence") else 0)
        )
        if raw_score > prev_score or (
            raw_score == prev_score
            and len(json.dumps(raw, default=str)) > len(json.dumps(prev, default=str))
        ):
            # Merge missing name/place from the thinner record.
            merged = dict(prev)
            merged.update({k: v for k, v in raw.items() if v is not None})
            if not merged.get("name") and prev.get("name"):
                merged["name"] = prev["name"]
            by_id[eid] = merged
        else:
            # Keep rich prev; fill blanks from anchor.
            for key in ("name", "day_time_sentence", "event_place"):
                if prev.get(key) in (None, "", {}) and raw.get(key):
                    prev[key] = raw[key]
    items = list(by_id.values())
    items.sort(key=lambda e: int(e.get("start_timestamp") or e.get("startTimestamp") or 0) or 10**12)
    return items


def _cover_image(raw: dict[str, Any]) -> str | None:
    cover = raw.get("cover_photo") if isinstance(raw.get("cover_photo"), dict) else {}
    photo = cover.get("photo") if isinstance(cover.get("photo"), dict) else {}
    image = photo.get("image") if isinstance(photo.get("image"), dict) else {}
    uri = image.get("uri") or raw.get("imageUrl") or raw.get("image")
    return uri.strip() if isinstance(uri, str) and uri.strip() else None


def _place(raw: dict[str, Any]) -> dict[str, Any]:
    place = raw.get("event_place") if isinstance(raw.get("event_place"), dict) else {}
    if not place and isinstance(raw.get("location"), dict):
        place = raw["location"]
    nested = place.get("location") if isinstance(place.get("location"), dict) else {}
    name = place.get("contextual_name") or place.get("name") or place.get("location_name")
    city = place.get("city")
    if isinstance(city, dict):
        city = city.get("name") or city.get("contextual_name")
    # FreeformPlace often puts the venue in contextual_name with city null —
    # do not copy the venue title into city.
    lat = place.get("latitude")
    if lat is None:
        lat = nested.get("latitude")
    lon = place.get("longitude")
    if lon is None:
        lon = nested.get("longitude")
    return {
        "name": name,
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "countryCode": place.get("country_code") or place.get("countryCode") or nested.get("country_code"),
        "streetAddress": place.get("streetAddress")
        or place.get("address")
        or place.get("one_line_address")
        or raw.get("one_line_address"),
    }


def _social_counts(raw: dict[str, Any]) -> tuple[int | None, int | None]:
    """Parse going/interested from this event's social_context only.

    Never use ``event_connected_users_public_responded`` (friends-who-responded)
    or sibling suggested-event counts — those look like attendance but aren't.
    """
    social = raw.get("social_context") if isinstance(raw.get("social_context"), dict) else {}
    text = social.get("text") if isinstance(social.get("text"), str) else ""
    going = interested = None
    m_g = re.search(r"([\d,]+)\s+going", text, re.I)
    m_i = re.search(r"([\d,]+)\s+interested", text, re.I)
    if m_g:
        going = int(m_g.group(1).replace(",", ""))
    if m_i:
        interested = int(m_i.group(1).replace(",", ""))
    if going is None:
        going = _safe_int(raw.get("usersGoing") or raw.get("going_count") or raw.get("going"))
    if interested is None:
        interested = _safe_int(
            raw.get("usersInterested") or raw.get("interested_count") or raw.get("interested")
        )
    return going, interested


def _safe_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _clean_schedule_sentence(sentence: str | None) -> str:
    if not sentence:
        return ""
    return (
        sentence.replace("\u202f", " ")
        .replace("\u00a0", " ")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("–", "-")
        .replace("—", "-")
        .strip()
    )


def _timezone_from_sentence(sentence: str | None) -> str | None:
    cleaned = _clean_schedule_sentence(sentence)
    if not cleaned:
        return None
    m = re.search(r"\b([A-Z]{2,5})\s*$", cleaned)
    if not m:
        return None
    return sanitize_iana_timezone(_TZ_ABBREV_TO_IANA.get(m.group(1)))


_RELATIVE_SCHEDULE_RE = re.compile(
    r"^(happening\s+now|now|today|tomorrow|yesterday|"
    r"in\s+\d+\s*(minutes?|mins?|hours?|hrs?|days?)|"
    r"\d+\s*(minutes?|mins?|hours?|hrs?|days?)\s+ago)$",
    re.IGNORECASE,
)

_MONTH_MAP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def is_relative_schedule(sentence: str | None) -> bool:
    cleaned = _clean_schedule_sentence(sentence)
    if not cleaned:
        return False
    return bool(_RELATIVE_SCHEDULE_RE.match(cleaned))


def _parse_clock_token(token: str) -> tuple[int, int] | None:
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?$", token.strip(), re.I)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = (m.group(3) or "").upper()
    if ampm == "PM" and hour < 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return None
    return hour, minute


def parse_schedule_sentence(
    sentence: str | None,
    *,
    prefer_upcoming: bool = True,
) -> dict[str, str | None]:
    """Parse Facebook ``day_time_sentence`` → local startDate/endDate/timezone.

    Handles yearless cards (``Sun, Jul 26 at 7:30 PM EDT``) by assuming the
    current year in that zone, then rolling forward one year when the instant
    is already more than ~12h in the past (profile upcoming calendars).
    """
    cleaned = _clean_schedule_sentence(sentence)
    empty = {"startDate": None, "endDate": None, "timezone": None}
    if not cleaned or is_relative_schedule(cleaned):
        return empty

    tz_name = sanitize_iana_timezone(_timezone_from_sentence(cleaned))
    # Strip trailing TZ abbrev for date/time parsing.
    body = re.sub(r"\s+[A-Z]{2,5}$", "", cleaned).strip()

    month_pat = (
        r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?"
    )
    # US: "Wednesday, August 19, 2026 at 7:00 PM" / "Tue, Aug 4 at 8:00 PM"
    # EU/FB: "Tue, 4 Aug at 20:00" (day-first, 24h clock)
    m = re.search(
        rf"(?:(?P<month>{month_pat})\s+(?P<day>\d{{1,2}})|(?P<day2>\d{{1,2}})\s+(?P<month2>{month_pat}))"
        rf"(?:,?\s*(?P<year>\d{{4}}))?"
        rf"(?:\s+at\s+|\s+from\s+|\s+)"
        rf"(?P<start>\d{{1,2}}(?::\d{{2}})?\s*(?:AM|PM)?)"
        rf"(?:\s*[-to]+\s*(?P<end>\d{{1,2}}(?::\d{{2}})?\s*(?:AM|PM)?))?",
        body,
        re.I,
    )
    if not m:
        return {**empty, "timezone": tz_name}

    month_s = m.group("month") or m.group("month2")
    day_s = m.group("day") or m.group("day2")
    month = _MONTH_MAP.get((month_s or "").lower())
    if not month or not day_s:
        return {**empty, "timezone": tz_name}
    day = int(day_s)
    year_s = m.group("year")
    start_clock = _parse_clock_token(m.group("start"))
    if not start_clock:
        return {**empty, "timezone": tz_name}
    end_raw = m.group("end")
    end_clock = _parse_clock_token(end_raw) if end_raw else None

    # Share AM/PM: "7:00 - 8:30 PM" → start inherits PM.
    if end_raw and start_clock and "AM" not in m.group("start").upper() and "PM" not in m.group("start").upper():
        if "PM" in (end_raw or "").upper() or "AM" in (end_raw or "").upper():
            start_clock = _parse_clock_token(
                m.group("start") + " " + re.findall(r"AM|PM", end_raw, flags=re.I)[-1]
            )
            if not start_clock:
                return {**empty, "timezone": tz_name}

    tz = ZoneInfo(tz_name) if tz_name else timezone.utc
    now = datetime.now(tz)
    year = int(year_s) if year_s else now.year

    def _make(y: int, clock: tuple[int, int]) -> datetime:
        return datetime(y, month, day, clock[0], clock[1], 0, tzinfo=tz)

    try:
        start_dt = _make(year, start_clock)
    except ValueError:
        return {**empty, "timezone": tz_name}

    if not year_s and prefer_upcoming and start_dt < now - timedelta(hours=12):
        try:
            start_dt = _make(year + 1, start_clock)
            year = year + 1
        except ValueError:
            pass

    end_dt = None
    if end_clock:
        try:
            end_dt = _make(year, end_clock)
            if end_dt < start_dt:
                end_dt = end_dt + timedelta(days=1)
        except ValueError:
            end_dt = None

    return {
        "startDate": start_dt.isoformat(timespec="seconds"),
        "endDate": end_dt.isoformat(timespec="seconds") if end_dt else None,
        "timezone": tz_name,
    }


def _fmt_local_iso(ts: int | None, tz_name: str | None) -> str | None:
    if ts is None:
        return None
    try:
        utc_dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None
    if tz_name:
        try:
            return utc_dt.astimezone(ZoneInfo(tz_name)).isoformat(timespec="seconds")
        except Exception:  # noqa: BLE001
            pass
    return utc_dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def _fmt_utc_iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError, OSError):
        return None


def _duration_text(seconds: int | None, display: str | None = None) -> str | None:
    if isinstance(display, str) and display.strip():
        return display.strip()
    if seconds is None or seconds < 0:
        return None
    if seconds % 3600 == 0 and seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} hr" if hours == 1 else f"{hours} hrs"
    if seconds % 60 == 0:
        minutes = seconds // 60
        if minutes >= 60:
            h, m = divmod(minutes, 60)
            if m == 0:
                return f"{h} hr" if h == 1 else f"{h} hrs"
            return f"{h} hr {m} min" if h == 1 else f"{h} hrs {m} min"
        return f"{minutes} min"
    return f"{seconds} seconds"


def _coerce_is_past(flag: Any, start_date: str | None) -> bool | None:
    """Prefer Relay ``is_past``; otherwise derive from ``startDate`` vs now(UTC)."""
    if isinstance(flag, bool):
        return flag
    if not start_date:
        return None
    try:
        iso = start_date.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt < datetime.now(timezone.utc)
    except (TypeError, ValueError):
        return None


def _parse_json_object_after(html: str, key: str) -> dict[str, Any] | None:
    m = re.search(rf'"{re.escape(key)}"\s*:\s*\{{', html or "")
    if not m:
        return None
    blob = _extract_balanced_json(html or "", m.end() - 1)
    if not blob:
        return None
    try:
        data = json.loads(blob)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def enrich_raw_event_from_html(html: str, eid: str | None, raw: dict[str, Any]) -> dict[str, Any]:
    """Fill end time, host, categories, duration, coords from the event page HTML.

    The thin Relay card chosen by ``extract_events_from_html`` often omits these;
    details pages still embed them elsewhere in ScheduledServerJS.
    """
    out = dict(raw)
    body = html or ""
    if not body:
        return out

    if eid:
        # Prefer timestamps that appear near this event id (avoid sibling cards).
        window_hits: list[tuple[int, int]] = []
        for m in re.finditer(re.escape(str(eid)), body):
            chunk = body[max(0, m.start() - 400) : m.end() + 2500]
            ts_m = re.search(r'"start_timestamp"\s*:\s*(\d+)', chunk)
            et_m = re.search(r'"end_timestamp"\s*:\s*(\d+)', chunk)
            if ts_m and et_m:
                window_hits.append((int(ts_m.group(1)), int(et_m.group(1))))
        if window_hits:
            # Most common pair for this id wins.
            counts: dict[tuple[int, int], int] = {}
            for pair in window_hits:
                counts[pair] = counts.get(pair, 0) + 1
            start_ts, end_ts = max(counts.items(), key=lambda kv: kv[1])[0]
            out.setdefault("start_timestamp", start_ts)
            out.setdefault("end_timestamp", end_ts)
        else:
            et_m = re.search(r'"end_timestamp"\s*:\s*(\d+)', body)
            if et_m and out.get("end_timestamp") is None:
                out["end_timestamp"] = int(et_m.group(1))

    if out.get("end_timestamp") is None:
        et_m = re.search(r'"end_timestamp"\s*:\s*(\d+)', body)
        if et_m:
            out["end_timestamp"] = int(et_m.group(1))

    if not out.get("day_time_sentence"):
        dts = re.search(
            r'"day_time_sentence"\s*:\s*"((?:\\.|[^"\\])*)"',
            body,
        )
        if dts:
            out["day_time_sentence"] = _unescape_js_str(dts.group(1))

    if not out.get("display_duration"):
        dd = re.search(r'"display_duration"\s*:\s*"((?:\\.|[^"\\])*)"', body)
        if dd:
            out["display_duration"] = _unescape_js_str(dd.group(1))

    if out.get("is_past") is None:
        ip = re.search(r'"is_past"\s*:\s*(true|false)', body)
        if ip:
            out["is_past"] = ip.group(1) == "true"

    if not out.get("event_kind"):
        ek = re.search(r'"event_kind"\s*:\s*"([^"]+)"', body)
        if ek:
            out["event_kind"] = ek.group(1)

    if out.get("is_online") is None:
        io = re.search(r'"is_online"\s*:\s*(true|false)', body)
        if io:
            out["is_online"] = io.group(1) == "true"

    if out.get("is_canceled") is None:
        ic = re.search(r'"is_canceled"\s*:\s*(true|false)', body)
        if ic:
            out["is_canceled"] = ic.group(1) == "true"

    creator = out.get("event_creator") if isinstance(out.get("event_creator"), dict) else None
    if not creator:
        creator = _parse_json_object_after(body, "event_creator")
        if creator:
            out["event_creator"] = creator

    owner = out.get("page_as_owner") if isinstance(out.get("page_as_owner"), dict) else None
    if not owner:
        owner = _parse_json_object_after(body, "page_as_owner")
        if owner:
            out["page_as_owner"] = owner

    # Host URL + verified often sit next to the creator name, not inside the thin object.
    if creator and not creator.get("url"):
        name = creator.get("name")
        if isinstance(name, str) and name.strip():
            esc = re.escape(name)
            um = re.search(
                rf'"name"\s*:\s*"{esc}"[^}}]{{0,400}}"url"\s*:\s*"(https:\\/\\/www\.facebook\.com\\/[^"]+)"',
                body,
            )
            if not um:
                um = re.search(
                    rf'"name"\s*:\s*"{esc}"[^}}]{{0,400}}"url"\s*:\s*"(https://www\.facebook\.com/[^"]+)"',
                    body,
                )
            if um:
                creator["url"] = _unescape_js_str(um.group(1))
            vm = re.search(
                rf'"name"\s*:\s*"{esc}"[^}}]{{0,400}}"is_verified"\s*:\s*(true|false)',
                body,
            )
            if vm:
                creator["is_verified"] = vm.group(1) == "true"

    if not out.get("discovery_categories"):
        cats = re.search(r'"discovery_categories"\s*:\s*(\[[^\]]{0,2000}\])', body)
        if cats:
            try:
                parsed = json.loads(cats.group(1).replace("\\/", "/"))
                if isinstance(parsed, list):
                    out["discovery_categories"] = parsed
            except ValueError:
                pass

    if not out.get("one_line_address"):
        ola = re.search(r'"one_line_address"\s*:\s*"((?:\\.|[^"\\])*)"', body)
        if ola:
            out["one_line_address"] = _unescape_js_str(ola.group(1))

    # Full About-tab copy (OG description is usually a one-line stub).
    if not out.get("description") or len(str(out.get("description") or "")) < 80:
        edm = re.search(
            r'"event_description"\s*:\s*\{\s*"text"\s*:\s*"((?:\\.|[^"\\])*)"',
            body,
        )
        if edm:
            out["description"] = _unescape_js_str(edm.group(1))

    # Nested FreeformPlace.location{latitude,longitude} when the card omitted them.
    place = out.get("event_place") if isinstance(out.get("event_place"), dict) else {}
    nested = place.get("location") if isinstance(place.get("location"), dict) else {}
    if nested.get("latitude") is None:
        lm = re.search(
            r'"event_place"\s*:\s*\{[^}]{0,400}"location"\s*:\s*\{\s*"latitude"\s*:\s*([-\d.]+)\s*,\s*"longitude"\s*:\s*([-\d.]+)',
            body,
        )
        if lm:
            if not place:
                place = {}
            place["location"] = {
                "latitude": float(lm.group(1)),
                "longitude": float(lm.group(2)),
            }
            out["event_place"] = place

    # Tickets buy URL for this event.
    if not out.get("event_buy_ticket_url") and eid:
        tm = re.search(
            rf'"id"\s*:\s*"{re.escape(str(eid))}"[^}}]{{0,300}}"event_buy_ticket_url"\s*:\s*"((?:\\.|[^"\\])*)"',
            body,
        )
        if tm:
            out["event_buy_ticket_url"] = _unescape_js_str(tm.group(1))

    # Attendance: only trust social_context that shares a chunk with this event's
    # day_time_sentence (sibling suggested events also have going/interested).
    sentence = out.get("day_time_sentence")
    if isinstance(sentence, str) and sentence.strip() and not out.get("social_context"):
        # Match a short escaped prefix of the sentence inside JSON.
        needle = sentence[:40].replace("–", "\\u2013").replace("—", "\\u2014")
        needle = needle.replace("\u202f", "\\u202f")
        idx = body.find(needle) if needle else -1
        if idx < 0:
            # Fallback: unescaped search.
            idx = body.find(sentence[:40])
        if idx >= 0:
            chunk = body[max(0, idx - 200) : idx + 1200]
            sm = re.search(
                r'"social_context"\s*:\s*\{[^}]*"text"\s*:\s*"((?:\\.|[^"\\])*)"',
                chunk,
            )
            if sm:
                out["social_context"] = {"text": _unescape_js_str(sm.group(1))}

    return out


def _prefer_upcoming(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Stable partition: upcoming → unknown → past (never drop past entirely)."""
    upcoming: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    past: list[dict[str, Any]] = []
    for ev in events:
        flag = ev.get("isPast")
        if flag is None:
            start = (
                safe_str(ev.get("startDate"))
                or safe_str(ev.get("utcStartDate"))
                or safe_str(ev.get("start_date"))
            )
            flag = _coerce_is_past(None, start)
            if flag is not None:
                ev = {**ev, "isPast": flag}
        if flag is True:
            past.append(ev)
        elif flag is False:
            upcoming.append(ev)
        else:
            unknown.append(ev)
    return upcoming + unknown + past


def normalize_raw_event(raw: dict[str, Any]) -> dict[str, Any]:
    """Map Relay event card → Apify-like fields for router._normalize_event."""
    eid = str(raw.get("id") or raw.get("event_id") or "").strip()
    url = raw.get("eventUrl") or raw.get("event_url") or raw.get("url")
    if not url and eid:
        url = f"https://www.facebook.com/events/{eid}/"
    start_ts = raw.get("start_timestamp") or raw.get("startTimestamp")
    end_ts = raw.get("end_timestamp") or raw.get("endTimestamp")
    try:
        start_ts_i = int(start_ts) if start_ts is not None else None
    except (TypeError, ValueError):
        start_ts_i = None
    try:
        end_ts_i = int(end_ts) if end_ts is not None else None
    except (TypeError, ValueError):
        end_ts_i = None

    sentence = (
        raw.get("day_time_sentence")
        or raw.get("dateTimeSentence")
        or raw.get("startTime")
        or raw.get("start_time")
    )
    if isinstance(sentence, str) and is_relative_schedule(sentence):
        # "Happening now" is not cache-safe — prefer absolute formatted fields.
        sentence = (
            raw.get("start_time_formatted")
            or raw.get("dateTimeSentence")
            or raw.get("day_time_sentence")
        )
        if isinstance(sentence, str) and is_relative_schedule(sentence):
            sentence = None

    place = _place(raw)
    # Coords first (FE1) — never emit Etc/GMT as a stand-in for "unknown".
    tz_name = resolve_event_timezone(
        raw_timezone=raw.get("timezone") if isinstance(raw.get("timezone"), str) else None,
        sentence=sentence if isinstance(sentence, str) else None,
        latitude=place.get("latitude"),
        longitude=place.get("longitude"),
    )

    utc_start = _fmt_utc_iso(start_ts_i)
    local_start = _fmt_local_iso(start_ts_i, tz_name)
    local_end = _fmt_local_iso(end_ts_i, tz_name)

    # Yearless listing cards (profile-events) often have only the sentence.
    if not local_start and isinstance(sentence, str):
        parsed = parse_schedule_sentence(sentence, prefer_upcoming=True)
        local_start = parsed.get("startDate")  # type: ignore[assignment]
        if not local_end:
            local_end = parsed.get("endDate")  # type: ignore[assignment]
        if not tz_name:
            tz_name = sanitize_iana_timezone(parsed.get("timezone"))  # type: ignore[arg-type]
    if not local_start:
        local_start = utc_start

    duration_seconds: int | None = None
    if start_ts_i is not None and end_ts_i is not None and end_ts_i >= start_ts_i:
        duration_seconds = end_ts_i - start_ts_i
    duration = _duration_text(
        duration_seconds,
        safe_str(raw.get("display_duration") or raw.get("duration") or raw.get("durationText")),
    )
    going, interested = _social_counts(raw)
    is_online = raw.get("is_online")
    if is_online is None:
        is_online = raw.get("is_online_or_detected_online")

    # Categories from discovery_categories when present.
    categories: list[dict[str, Any]] = []
    raw_cats = raw.get("discovery_categories") or raw.get("categories") or []
    if isinstance(raw_cats, list):
        for c in raw_cats:
            if isinstance(c, str) and c.strip():
                categories.append({"label": c.strip(), "url": None})
            elif isinstance(c, dict):
                label = safe_str(c.get("label") or c.get("name"))
                if label:
                    categories.append(
                        {
                            "label": label,
                            "url": safe_str(c.get("uri") or c.get("url")),
                        }
                    )

    # eventType: category label when available (Comedy), else Relay event_kind.
    event_type = None
    if categories:
        event_type = categories[0].get("label")
    if not event_type:
        event_type = raw.get("eventType") or raw.get("event_kind") or raw.get("event_type")

    organizers: list[dict[str, Any]] = []
    creator = raw.get("event_creator") if isinstance(raw.get("event_creator"), dict) else {}
    owner = raw.get("page_as_owner") if isinstance(raw.get("page_as_owner"), dict) else {}
    host_name = safe_str(creator.get("name") or owner.get("name") or raw.get("organizedBy"))
    host_id = safe_str(creator.get("id") or owner.get("id"))
    host_url = safe_str(creator.get("url") or owner.get("url") or raw.get("organizerUrl"))
    host_verified = creator.get("is_verified")
    if host_verified is None:
        host_verified = owner.get("is_verified")
    if host_name or host_id or host_url:
        organizers.append(
            {
                "id": host_id,
                "name": host_name,
                "url": host_url,
                "isVerified": bool(host_verified) if host_verified is not None else False,
            }
        )
    elif isinstance(raw.get("organizers"), list):
        organizers = [o for o in raw["organizers"] if isinstance(o, dict)]

    tickets_info = raw.get("ticketsInfo") if isinstance(raw.get("ticketsInfo"), dict) else {}
    tickets_url = safe_str(
        raw.get("event_buy_ticket_url")
        or raw.get("ticketsUrl")
        or tickets_info.get("buyUrl")
        or raw.get("ticketUrl")
    )

    return {
        "id": eid or None,
        "event_id": eid or None,
        "url": url,
        "eventUrl": url,
        "name": raw.get("name") or raw.get("title"),
        "title": raw.get("name") or raw.get("title"),
        "description": raw.get("description"),
        # Local-offset ISO is canonical for startDate (calendar day matches startTime).
        "startDate": local_start,
        "endDate": local_end,
        "timezone": tz_name,
        # Keep UTC for debugging / older clients; router prefers startDate.
        "utcStartDate": utc_start,
        "start_date": local_start,
        "startTime": (sentence if isinstance(sentence, str) and sentence.strip() else None)
        or local_start,
        "dateTimeSentence": sentence if isinstance(sentence, str) else None,
        "duration": duration,
        "durationSeconds": duration_seconds,
        "isOnline": is_online,
        "is_online": is_online,
        "isPast": _coerce_is_past(
            raw.get("is_past") if raw.get("is_past") is not None else raw.get("isPast"),
            local_start or utc_start,
        ),
        "isCanceled": raw.get("is_canceled")
        if raw.get("is_canceled") is not None
        else raw.get("isCanceled"),
        "eventType": event_type,
        "imageUrl": _cover_image(raw),
        "image": _cover_image(raw),
        "usersGoing": going,
        "usersInterested": interested,
        "location": place,
        "location_name": place.get("name"),
        "location_city": place.get("city"),
        "organizers": organizers,
        "categories": categories,
        "discoveryCategories": categories,
        "ticketsUrl": tickets_url,
        "ticketsInfo": {"buyUrl": tickets_url} if tickets_url else None,
    }


def _html_event_signal(body: str) -> int:
    """Rough richness score — scrolled DOM usually wins over the Relay stub."""
    if not body:
        return 0
    return len(_EVENT_HREF_RE.findall(body)) + body.count("eventUrl") + body.count("start_timestamp")


async def _fetch_html(url: str, *, scroll: bool = True) -> str | None:
    if not decodo_fetch.enabled():
        return None
    # Scroll first so we don't settle for the ~8-card Relay stub. Decodo
    # sometimes wants ``target=universal`` for browser_actions; try both.
    attempts: list[tuple[list[dict[str, Any]] | None, str | None]] = []
    if scroll:
        attempts.append((_SCROLL_ACTIONS, "universal"))
        attempts.append((_SCROLL_ACTIONS, None))
        attempts.append((_SCROLL_ACTIONS[:4], None))
    attempts.append((None, None))

    candidates: list[str] = []
    for actions, target in attempts:
        got = await decodo_fetch.fetch_url(
            url,
            timeout=180.0 if actions else 120.0,
            headless="html",
            browser_actions=actions,
            target=target,
        )
        if not got:
            log.info(
                "facebook_events_fetch_miss",
                url=url[:120],
                scrolled=bool(actions),
                target=target,
            )
            continue
        status, body = got
        if status != 200 or not body:
            continue
        if "eventUrl" not in body and "/events/" not in body:
            continue
        score = _html_event_signal(body)
        log.info(
            "facebook_events_fetch_ok",
            url=url[:120],
            scrolled=bool(actions),
            target=target,
            score=score,
            chars=len(body),
        )
        candidates.append(body)
        if actions is not None and score >= 20:
            break
    if not candidates:
        return None
    return max(candidates, key=_html_event_signal)


async def fetch_page_events(page_url: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    if limit <= 0:
        return []
    url = page_events_url(page_url)
    html = await _fetch_html(url, scroll=True)
    if not html:
        return None
    raw = extract_events_from_html(html)
    if not raw:
        log.info("facebook_events_native_page_empty", url=url[:120])
        return None
    out: list[dict[str, Any]] = []
    for e in raw[: max(limit, 40)]:
        eid = str(e.get("id") or e.get("event_id") or "")
        # Same page HTML often embeds start/end timestamps the thin card omitted.
        enriched = enrich_raw_event_from_html(html, eid or None, e)
        out.append(normalize_raw_event(enriched))
    out = [e for e in out if e.get("id") and e.get("name")]
    out = out[:limit]
    if not out:
        return None
    log.info("facebook_events_native_page_ok", url=url[:120], n=len(out))
    return out


_SEARCH_STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "near",
    "events",
    "event",
}


def _query_tokens(q: str) -> list[str]:
    return [
        t
        for t in re.findall(r"[a-z0-9]{2,}", (q or "").lower())
        if t not in _SEARCH_STOPWORDS
    ]


def _event_haystack(raw: dict[str, Any]) -> str:
    place = raw.get("event_place") if isinstance(raw.get("event_place"), dict) else {}
    loc = raw.get("location") if isinstance(raw.get("location"), dict) else {}
    parts = [
        raw.get("name"),
        raw.get("title"),
        raw.get("description"),
        raw.get("day_time_sentence"),
        place.get("contextual_name"),
        place.get("name"),
        place.get("city"),
        loc.get("name"),
        loc.get("city"),
        raw.get("location_name"),
        raw.get("location_city"),
    ]
    return " ".join(str(p) for p in parts if p).lower()


def _event_matches_query(raw: dict[str, Any], tokens: list[str]) -> bool:
    if not tokens:
        return True
    hay = _event_haystack(raw)
    if not hay:
        return False
    # Short queries (topic + city): require every token. Longer queries: ≥70%.
    need = len(tokens) if len(tokens) <= 3 else max(2, int(round(len(tokens) * 0.7)))
    hits = sum(1 for t in tokens if t in hay)
    return hits >= need


# Place name → IANA zones + city tokens + optional lat/lng radius (FE4).
# ``location`` is a geo filter on the resolved event, not a title substring.
_PLACE_GEO: dict[str, dict[str, Any]] = {
    "london": {
        "timezones": {"Europe/London"},
        "city_tokens": {"london"},
        "lat": 51.5074,
        "lng": -0.1276,
        "radius_km": 60,
    },
    "paris": {
        "timezones": {"Europe/Paris"},
        "city_tokens": {"paris"},
        "lat": 48.8566,
        "lng": 2.3522,
        "radius_km": 50,
    },
    "amsterdam": {
        "timezones": {"Europe/Amsterdam"},
        "city_tokens": {"amsterdam"},
        "lat": 52.3676,
        "lng": 4.9041,
        "radius_km": 40,
    },
    "berlin": {
        "timezones": {"Europe/Berlin"},
        "city_tokens": {"berlin"},
        "lat": 52.52,
        "lng": 13.405,
        "radius_km": 50,
    },
    "chicago": {
        "timezones": {"America/Chicago"},
        "city_tokens": {"chicago"},
        "lat": 41.8781,
        "lng": -87.6298,
        "radius_km": 60,
    },
    "new york": {
        "timezones": {"America/New_York"},
        "city_tokens": {"new york", "nyc", "brooklyn", "manhattan", "queens"},
        "lat": 40.7128,
        "lng": -74.006,
        "radius_km": 50,
    },
    "nyc": {
        "timezones": {"America/New_York"},
        "city_tokens": {"new york", "nyc", "brooklyn", "manhattan", "queens"},
        "lat": 40.7128,
        "lng": -74.006,
        "radius_km": 50,
    },
    "los angeles": {
        "timezones": {"America/Los_Angeles"},
        "city_tokens": {"los angeles", "la", "hollywood"},
        "lat": 34.0522,
        "lng": -118.2437,
        "radius_km": 70,
    },
    "auckland": {
        "timezones": {"Pacific/Auckland"},
        "city_tokens": {"auckland"},
        "lat": -36.8509,
        "lng": 174.7645,
        "radius_km": 50,
    },
    "detroit": {
        "timezones": {"America/Detroit"},
        "city_tokens": {"detroit"},
        "lat": 42.3314,
        "lng": -83.0458,
        "radius_km": 50,
    },
}


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    from math import asin, cos, radians, sin, sqrt

    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * r * asin(sqrt(a))


def _place_geo_spec(location: str | None) -> dict[str, Any] | None:
    raw = (location or "").strip().lower()
    if not raw:
        return None
    if raw in _PLACE_GEO:
        return _PLACE_GEO[raw]
    # "London, UK" / "new york city"
    for key, spec in _PLACE_GEO.items():
        if key in raw or raw in key:
            return spec
    return None


def event_matches_location(ev: dict[str, Any], location: str | None) -> bool:
    """Geo filter: timezone / city / coords — not event-title substring (FE4)."""
    loc_q = (location or "").strip()
    if not loc_q:
        return True
    place = ev.get("location") if isinstance(ev.get("location"), dict) else {}
    tz = safe_str(ev.get("timezone"))
    city = " ".join(
        str(x)
        for x in (
            place.get("city"),
            place.get("name"),
            ev.get("location_city"),
            ev.get("location_name"),
            place.get("countryCode"),
        )
        if x
    ).lower()

    spec = _place_geo_spec(loc_q)
    if spec:
        zones = spec.get("timezones") or set()
        if tz and tz in zones:
            return True
        tokens = spec.get("city_tokens") or set()
        if any(t in city for t in tokens):
            return True
        try:
            elat = float(place.get("latitude"))
            elng = float(place.get("longitude"))
            clat = float(spec["lat"])
            clng = float(spec["lng"])
            if _haversine_km(elat, elng, clat, clng) <= float(spec.get("radius_km") or 50):
                return True
        except (TypeError, ValueError, KeyError):
            pass
        return False

    # Unknown place: match city/venue/timezone text only — never the event title.
    needle = loc_q.lower()
    hay = f"{city} {tz or ''}".lower()
    return needle in hay


def _event_in_date_range(
    ev: dict[str, Any],
    *,
    from_date: str | None,
    to_date: str | None,
) -> bool:
    """Filter by calendar day of startDate (YYYY-MM-DD bounds, inclusive)."""
    if not from_date and not to_date:
        return True
    start = safe_str(ev.get("startDate") or ev.get("utcStartDate") or ev.get("start_date"))
    if not start:
        return False
    day = start[:10]
    if from_date and day < from_date[:10]:
        return False
    if to_date and day > to_date[:10]:
        return False
    return True


def _event_ids_from_serp_html(html: str, *, limit: int = 40) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for eid in re.findall(r"facebook\.com/events/(\d{8,})", html or "", re.I):
        if eid in seen:
            continue
        seen.add(eid)
        ids.append(eid)
        if len(ids) >= limit:
            break
    return ids


async def _search_event_ids_via_serp(
    q: str, *, limit: int = 40, deadline: float | None = None
) -> list[str]:
    """SERP (via Decodo) site:facebook.com/events → event IDs.

    Google alone is flaky for this query; race Google (gl=US) + Yahoo + DDG.
    ``deadline`` is ``time.monotonic()`` wall — stop when budget is spent.
    """
    if not decodo_fetch.enabled():
        return []
    query = (q or "").strip()
    if len(query) < 2:
        return []
    num = min(30, max(10, limit))
    # Bias SERP toward upcoming listings without inventing dates.
    variants = [
        f"site:facebook.com/events {query}",
        f'site:facebook.com/events {query} comedy OR concert OR show',
    ]
    # Prefer DDG (often works without JS) then Yahoo then Google — short timeouts
    # so a dead SERP does not burn the whole search budget.
    sources: list[tuple[str, str | None]] = []
    for v in variants[:1]:
        q_enc = quote_plus(v)
        sources.extend(
            [
                (f"https://html.duckduckgo.com/html/?q={q_enc}", None),
                (f"https://search.yahoo.com/search?p={q_enc}&n={num}", "html"),
                (f"https://www.google.com/search?q={q_enc}&num={num}&hl=en&gl=us&pws=0", "html"),
            ]
        )
    seen: set[str] = set()
    ids: list[str] = []
    misses = 0
    for url, headless in sources:
        if deadline is not None and time.monotonic() >= deadline:
            break
        remaining = 12.0 if deadline is None else max(4.0, min(12.0, deadline - time.monotonic()))
        got = await decodo_fetch.fetch_url(
            url, timeout=remaining, headless=headless, geo="US"
        )
        if not got:
            misses += 1
            if misses >= 3 and not ids:
                break
            continue
        status, body = got
        if status != 200 or not body:
            misses += 1
            continue
        for eid in _event_ids_from_serp_html(body, limit=limit):
            if eid in seen:
                continue
            seen.add(eid)
            ids.append(eid)
            if len(ids) >= limit:
                break
        if len(ids) >= min(8, limit):
            break
    log.info("facebook_events_serp_ids", q=query[:80], n=len(ids))
    return ids


async def _hydrate_event_ids(
    ids: list[str], *, limit: int, tokens: list[str]
) -> list[dict[str, Any]]:
    if not ids or limit <= 0:
        return []
    sem = asyncio.Semaphore(3)
    selected = ids[: max(limit * 2, limit + 5)]

    async def _one(eid: str) -> dict[str, Any] | None:
        async with sem:
            return await fetch_event_details(f"https://www.facebook.com/events/{eid}/")

    rows = await asyncio.gather(*[_one(eid) for eid in selected])
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not row or not row.get("id") or not row.get("name"):
            continue
        eid = str(row["id"])
        if eid in seen:
            continue
        # Re-check relevance on hydrated fields (SERP titles can be noisy).
        if tokens and not _event_matches_query(row, tokens):
            continue
        seen.add(eid)
        out.append(row)
        if len(out) >= limit:
            break
    return out


async def fetch_search_events(
    q: str,
    *,
    limit: int = 20,
    location: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> list[dict[str, Any]] | None:
    """Keyword search: SERP → details, then relevance-filtered discovery.

    Logged-out /events/?q= often returns an unrelated feed; SERP is preferred.
    Discovery always runs when SERP is empty (even after SERP timeouts) so a
    dead Google/Yahoo hop cannot zero the whole endpoint.

    ``location`` is a geo filter on timezone / city / coords after hydrate (FE4)
    — not a required title/venue substring. SERP may still bias with the place
    name for discovery. ``from_date`` / ``to_date`` are YYYY-MM-DD bounds on
    local startDate.
    """
    if limit <= 0:
        return []
    query = (q or "").strip()
    if len(query) < 2:
        return None
    loc = (location or "").strip()
    # Topic tokens only — do not require "London" in the event title (FE4).
    tokens = _query_tokens(query)
    # Bias SERP toward the place without making it a hard haystack token.
    serp_q = f"{query} {loc}".strip() if loc else query
    # Over-fetch when geo-filtering so limit can still fill after the cut.
    fetch_limit = min(40, max(limit * 3, limit + 10)) if loc else limit
    # Reserve ~20s for discovery/page hydrate even if SERP is slow.
    deadline = time.monotonic() + 50.0
    serp_deadline = time.monotonic() + 18.0

    def _finalize(rows: list[dict[str, Any]], path: str) -> list[dict[str, Any]]:
        filtered = [
            e
            for e in rows
            if _event_in_date_range(e, from_date=from_date, to_date=to_date)
            and event_matches_location(e, loc)
        ]
        ranked = _prefer_upcoming(filtered)[:limit]
        log.info(
            "facebook_events_native_search_ok",
            q=query[:80],
            n=len(ranked),
            path=path,
            location=(loc[:40] if loc else None),
        )
        return ranked

    # 1) SERP → native event-details (query-relevant IDs).
    ids = await _search_event_ids_via_serp(
        serp_q, limit=min(40, max(15, fetch_limit * 2)), deadline=serp_deadline
    )
    if ids and time.monotonic() < deadline:
        hydrated = await _hydrate_event_ids(
            ids, limit=max(fetch_limit, 8), tokens=tokens
        )
        if hydrated:
            return _finalize(hydrated, "serp")

    # 2) Facebook discovery shell — always try when SERP missed (strict match).
    url = search_events_url(serp_q)
    html = await _fetch_html(url, scroll=False)
    if html:
        raw = extract_events_from_html(html)
        matched = [e for e in raw if _event_matches_query(e, tokens)]
        out = [normalize_raw_event(e) for e in matched]
        out = [e for e in out if e.get("id") and e.get("name")]
        if out:
            return _finalize(out, "discovery")

    log.info("facebook_events_native_search_empty", q=query[:80])
    return None


def _og_meta(html: str, key: str) -> str | None:
    pattern = rf'<meta\s+(?:property|name)=["\']{re.escape(key)}["\']\s+content=["\']([^"\']*)["\']'
    match = re.search(pattern, html or "", flags=re.IGNORECASE)
    if not match:
        pattern = rf'<meta\s+content=["\']([^"\']*)["\']\s+(?:property|name)=["\']{re.escape(key)}["\']'
        match = re.search(pattern, html or "", flags=re.IGNORECASE)
    return html_lib.unescape(match.group(1)).strip() if match else None


async def fetch_event_details(url: str) -> dict[str, Any] | None:
    """Single event page via Decodo headless HTML (richer than OG stub)."""
    target = (url or "").strip()
    if not target:
        return None
    eid_match = re.search(r"/events/(\d+)", target)
    eid = eid_match.group(1) if eid_match else None
    html = await _fetch_html(target, scroll=False)
    if not html:
        return None
    raw_list = extract_events_from_html(html)
    chosen: dict[str, Any] | None = None
    if eid:
        for raw in raw_list:
            rid = str(raw.get("id") or raw.get("event_id") or "")
            if rid == eid:
                chosen = raw
                break
            eurl = str(raw.get("eventUrl") or raw.get("url") or "")
            if eid in eurl:
                chosen = raw
                break
    if chosen is None and eid:
        # Related-event cards often pollute Relay; prefer OG for this URL's id.
        og_title = _og_meta(html, "og:title")
        if og_title and og_title.lower() not in _NOISE_TITLES:
            chosen = {
                "id": eid,
                "name": og_title,
                "eventUrl": f"https://www.facebook.com/events/{eid}/",
                "description": _og_meta(html, "og:description"),
                "cover_photo": {
                    "photo": {"image": {"uri": _og_meta(html, "og:image")}}
                },
            }
    if chosen is None and raw_list and not eid:
        chosen = raw_list[0]
    if not chosen:
        log.info("facebook_events_native_details_empty", url=target[:120])
        return None
    # Thin Relay cards miss end_timestamp / host / categories — hydrate from HTML.
    chosen = enrich_raw_event_from_html(html, eid, chosen)
    if not chosen.get("description"):
        chosen["description"] = _og_meta(html, "og:description")
    if not _cover_image(chosen):
        og_img = _og_meta(html, "og:image")
        if og_img:
            chosen["cover_photo"] = {"photo": {"image": {"uri": og_img}}}
    out = normalize_raw_event(chosen)
    if eid:
        # Never return a different event than the requested URL.
        out["id"] = eid
        out["event_id"] = eid
        out["url"] = f"https://www.facebook.com/events/{eid}/"
        out["eventUrl"] = out["url"]
    elif not out.get("url"):
        out["url"] = target
        out["eventUrl"] = target
    if not out.get("name"):
        return None
    log.info("facebook_events_native_details_ok", url=target[:120], id=out.get("id"))
    return out
