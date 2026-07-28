"""Native Facebook events via Decodo JS-rendered HTML (no Apify).

Facebook returns 400 on plain datacenter/residential for /events pages.
Decodo headless=html hydrates ScheduledServerJS payloads that embed event
cards for page listings. Discovery search (/events/?q=...) is login-walled
logged-out — callers should fall through to Apify for keyword search.
"""

from __future__ import annotations

import html as html_lib
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
    out = [normalize_raw_event(e) for e in raw[: max(limit, 40)]]
    out = [e for e in out if e.get("id") and e.get("name")]
    out = out[:limit]
    if not out:
        return None
    log.info("facebook_events_native_page_ok", url=url[:120], n=len(out))
    return out


async def fetch_search_events(q: str, *, limit: int = 20) -> list[dict[str, Any]] | None:
    """Keyword search. Logged-out Decodo often hits a login shell — return None
    so the router can serve Apify snapshots instead of burning a cold browser run.
    """
    if limit <= 0:
        return []
    query = (q or "").strip()
    if len(query) < 2:
        return None
    url = search_events_url(query)
    # No scroll: discovery search rarely hydrates cards without a session.
    html = await _fetch_html(url, scroll=False)
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
    if chosen is None and raw_list:
        chosen = raw_list[0]
    if not chosen:
        log.info("facebook_events_native_details_empty", url=target[:120])
        return None
    out = normalize_raw_event(chosen)
    if not out.get("id") and eid:
        out["id"] = eid
        out["event_id"] = eid
    if not out.get("url"):
        out["url"] = target
        out["eventUrl"] = target
    if not out.get("name"):
        return None
    log.info("facebook_events_native_details_ok", url=target[:120], id=out.get("id"))
    return out
