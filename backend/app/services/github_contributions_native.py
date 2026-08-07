"""Scrape a GitHub user contribution calendar (the real heatmap).

Public HTML at ``https://github.com/users/{login}/contributions`` exposes
the last ~365 days with per-day counts (tool-tip text) and intensity levels.
This is the contribution graph — not ``/users/{u}/events/public`` (max 90
events / 90 days).
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

import httpx
import structlog

from app.utils.formatters import safe_int, safe_str, strip_empty

log = structlog.get_logger(__name__)

CREDIT_GITHUB_CONTRIBUTIONS_NATIVE = 2

_TOTAL_RE = re.compile(
    r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year",
    re.I,
)
_DAY_RE = re.compile(
    r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d+)"',
    re.I,
)
_TIP_RE = re.compile(r"<tool-tip[^>]*>(.*?)</tool-tip>", re.S)
_TIP_COUNT_RE = re.compile(
    r"^(?:(\d+)\s+contributions?|No contributions)\b",
    re.I,
)


def _comma_int(raw: str | None) -> int | None:
    if not raw:
        return None
    return safe_int(str(raw).replace(",", ""))


def _tip_count(text: str) -> int:
    t = (text or "").strip()
    if t.lower().startswith("no contribution"):
        return 0
    m = _TIP_COUNT_RE.match(t)
    if m and m.group(1):
        return int(m.group(1))
    return 0


def _current_streak(days: list[dict[str, Any]], *, today: str | None = None) -> int:
    """Consecutive nonzero days ending at the latest calendar day.

    GitHub convention: a zero on *today* does not break the streak (the day is
    not over). A zero on any earlier day does.
    ``days`` must already be ascending by ``date``.
    """
    if not days:
        return 0
    today_s = today or date.today().isoformat()
    i = len(days) - 1
    if days[i].get("date") == today_s and int(days[i].get("count") or 0) == 0:
        i -= 1
    n = 0
    while i >= 0 and int(days[i].get("count") or 0) > 0:
        n += 1
        i -= 1
    return n


def _longest_streak(days: list[dict[str, Any]]) -> int:
    """Longest run of consecutive days with count > 0 (any position in the window)."""
    best = cur = 0
    for d in days:
        if int(d.get("count") or 0) > 0:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 0
    return best


def parse_contributions_html(
    html: str,
    *,
    today: str | None = None,
) -> dict[str, Any] | None:
    """Return totalContributions + days[{date,count,level}] from the calendar HTML.

    GitHub emits day cells weekday-major (all Sundays, then Mondays, …). We sort
    ascending by date before deriving from/to/streaks so windowed callers and
    streak walks see chronological order.
    """
    if not html:
        return None
    days_meta = _DAY_RE.findall(html)
    tips = _TIP_RE.findall(html)
    if not days_meta:
        return None
    # Tips are emitted in the same order as day cells on the public calendar.
    days: list[dict[str, Any]] = []
    for i, (dt, level_s) in enumerate(days_meta):
        count = _tip_count(tips[i]) if i < len(tips) else 0
        days.append(
            {
                "date": dt,
                "count": count,
                "level": safe_int(level_s) or 0,
            }
        )
    # DOM order is weekday-major — force chronological before any derived field.
    days.sort(key=lambda d: d["date"])

    total_m = _TOTAL_RE.search(html)
    total = _comma_int(total_m.group(1) if total_m else None)
    if total is None:
        total = sum(d["count"] for d in days)

    return {
        "totalContributions": total,
        "from": days[0]["date"],
        "to": days[-1]["date"],
        "currentStreak": _current_streak(days, today=today),
        "longestStreak": _longest_streak(days),
        "days": days,
    }


async def _fetch_html(url: str) -> str | None:
    try:
        from app.services import decodo_fetch

        if decodo_fetch.enabled():
            got = await decodo_fetch.fetch_url(url, timeout=60.0)
            if got and got[0] == 200 and got[1]:
                return got[1]
    except Exception as exc:  # noqa: BLE001
        log.info("github_contributions_decodo_fail", error=str(exc)[:160])

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        async with httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception as exc:  # noqa: BLE001
        log.info("github_contributions_http_fail", error=str(exc)[:160])
    return None


async def contributions_native(login: str) -> dict[str, Any] | None:
    login_n = safe_str(login)
    if not login_n:
        return None
    url = f"https://github.com/users/{login_n}/contributions"
    html = await _fetch_html(url)
    if not html:
        return None
    parsed = parse_contributions_html(html)
    if not parsed:
        log.info("github_contributions_empty", login=login_n)
        return None
    out = strip_empty(
        {
            "username": login_n,
            "url": f"https://github.com/{login_n}",
            "totalContributions": parsed["totalContributions"],
            "from": parsed["from"],
            "to": parsed["to"],
            "currentStreak": parsed["currentStreak"],
            "longestStreak": parsed["longestStreak"],
            "days": parsed["days"],
        }
    )
    out["source"] = f"github.com/users/{login_n}/contributions"
    log.info(
        "github_contributions_ok",
        login=login_n,
        total=out.get("totalContributions"),
        days=len(parsed["days"]),
        current_streak=out.get("currentStreak"),
        longest_streak=out.get("longestStreak"),
    )
    return out