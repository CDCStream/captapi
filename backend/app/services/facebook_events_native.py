"""Native Facebook events via Decodo JS-rendered HTML (no Apify).

Facebook returns 400 on plain datacenter/residential for /events pages.
Decodo headless=html hydrates ScheduledServerJS payloads that embed event
cards for page listings and discovery search (/events/?q=...).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

import structlog

from app.services import decodo_fetch

log = structlog.get_logger(__name__)

# One Decodo JS render is ~$0.001–0.01; flat 2 credits (~120% markup headroom).
CREDIT_FB_EVENTS_NATIVE = 2

_EVENT_URL_RE = re.compile(
    r"https:\\/\\/www\.facebook\.com\\/events\\/(\d+)\\/?",
    re.IGNORECASE,
)


def page_events_url(page_url: str) -> str:
    base = (page_url or "").strip().rstrip("/")
    if not base:
        return base
    if base.lower().endswith("/events"):
        return base
    return f"{base}/events"


def search_events_url(q: str) -> str:
    # /events/search/?q= returns an empty shell; /events/?q= embeds result cards.
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
        if name.lower() in {"events", "upcoming", "past", "hosting"}:
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
        if len(found) >= 8:
            break
    if len(found) < 3:
        found.extend(_regex_fallback_events(html or ""))

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
        if prev is None or (raw.get("name") and not prev.get("name")) or len(json.dumps(raw, default=str)) > len(
            json.dumps(prev, default=str)
        ):
            by_id[eid] = raw
    # Prefer chronological order when timestamps exist.
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
    name = place.get("contextual_name") or place.get("name") or place.get("location_name")
    # FreeformPlace often puts the venue in contextual_name with city null —
    # do not copy the venue title into city.
    return {
        "name": name,
        "city": place.get("city"),
        "latitude": place.get("latitude"),
        "longitude": place.get("longitude"),
        "countryCode": place.get("country_code") or place.get("countryCode"),
        "streetAddress": place.get("streetAddress") or place.get("address"),
    }


def _social_counts(raw: dict[str, Any]) -> tuple[int | None, int | None]:
    social = raw.get("social_context") if isinstance(raw.get("social_context"), dict) else {}
    text = social.get("text") if isinstance(social.get("text"), str) else ""
    going = interested = None
    m_g = re.search(r"([\d,]+)\s+going", text, re.I)
    m_i = re.search(r"([\d,]+)\s+interested", text, re.I)
    if m_g:
        going = int(m_g.group(1).replace(",", ""))
    if m_i:
        interested = int(m_i.group(1).replace(",", ""))
    return going, interested


def normalize_raw_event(raw: dict[str, Any]) -> dict[str, Any]:
    """Map Relay event card → Apify-like fields for router._normalize_event."""
    eid = str(raw.get("id") or raw.get("event_id") or "").strip()
    url = raw.get("eventUrl") or raw.get("event_url") or raw.get("url")
    if not url and eid:
        url = f"https://www.facebook.com/events/{eid}/"
    ts = raw.get("start_timestamp") or raw.get("startTimestamp")
    start_date = None
    if ts is not None:
        try:
            start_date = datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat().replace("+00:00", "Z")
        except (TypeError, ValueError, OSError):
            start_date = None
    place = _place(raw)
    going, interested = _social_counts(raw)
    is_online = raw.get("is_online")
    if is_online is None:
        is_online = raw.get("is_online_or_detected_online")
    return {
        "id": eid or None,
        "event_id": eid or None,
        "url": url,
        "eventUrl": url,
        "name": raw.get("name") or raw.get("title"),
        "title": raw.get("name") or raw.get("title"),
        "description": raw.get("description"),
        "utcStartDate": start_date,
        "start_date": start_date,
        "startTime": raw.get("day_time_sentence") or start_date,
        "dateTimeSentence": raw.get("day_time_sentence"),
        "isOnline": is_online,
        "is_online": is_online,
        "isPast": raw.get("is_past") if raw.get("is_past") is not None else raw.get("isPast"),
        "eventType": raw.get("event_kind") or raw.get("eventType"),
        "imageUrl": _cover_image(raw),
        "image": _cover_image(raw),
        "usersGoing": going,
        "usersInterested": interested,
        "location": place,
        "location_name": place.get("name"),
        "location_city": place.get("city"),
    }


async def _fetch_html(url: str) -> str | None:
    if not decodo_fetch.enabled():
        return None
    got = await decodo_fetch.fetch_url(url, timeout=120.0, headless="html")
    if not got:
        return None
    status, body = got
    if status != 200 or not body:
        return None
    if "eventUrl" not in body and "/events/" not in body:
        return None
    return body


async def fetch_page_events(page_url: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    if limit <= 0:
        return []
    url = page_events_url(page_url)
    html = await _fetch_html(url)
    if not html:
        return None
    raw = extract_events_from_html(html)
    if not raw:
        log.info("facebook_events_native_page_empty", url=url[:120])
        return None
    out = [normalize_raw_event(e) for e in raw[:limit]]
    out = [e for e in out if e.get("id") and e.get("name")]
    if not out:
        return None
    log.info("facebook_events_native_page_ok", url=url[:120], n=len(out))
    return out


async def fetch_search_events(q: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    if limit <= 0:
        return []
    query = (q or "").strip()
    if len(query) < 2:
        return None
    url = search_events_url(query)
    html = await _fetch_html(url)
    if not html:
        return None
    raw = extract_events_from_html(html)
    if not raw:
        log.info("facebook_events_native_search_empty", q=query[:80])
        return None
    out = [normalize_raw_event(e) for e in raw[:limit]]
    out = [e for e in out if e.get("id") and e.get("name")]
    if not out:
        return None
    log.info("facebook_events_native_search_ok", q=query[:80], n=len(out))
    return out