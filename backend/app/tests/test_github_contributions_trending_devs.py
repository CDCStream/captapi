"""GitHub contributions calendar + trending developers HTML."""

from __future__ import annotations

from datetime import date, timedelta

from app.services.github_contributions_native import (
    _current_streak,
    _longest_streak,
    parse_contributions_html,
)
from app.services.github_trending_native import parse_trending_developers_html


def test_parse_contributions_uses_tip_counts_not_event_ceiling():
    html = '''
    <h2>164 contributions in the last year</h2>
    <td data-date="2025-08-03" data-level="0"></td>
    <tool-tip>No contributions on August 3rd.</tool-tip>
    <td data-date="2025-08-04" data-level="2"></td>
    <tool-tip>5 contributions on August 4th.</tool-tip>
    <td data-date="2025-08-05" data-level="1"></td>
    <tool-tip>2 contributions on August 5th.</tool-tip>
    '''
    out = parse_contributions_html(html, today="2025-08-05")
    assert out is not None
    assert out["totalContributions"] == 164
    assert out["days"][0] == {"date": "2025-08-03", "count": 0, "level": 0}
    assert out["days"][1]["count"] == 5
    assert out["currentStreak"] == 2  # last two days nonzero
    assert out["longestStreak"] == 2
    assert out["from"] == "2025-08-03"
    assert out["to"] == "2025-08-05"
    assert "recentPublicEvents" not in out


def test_days_sorted_ascending_from_weekday_major_dom():
    """GitHub DOM order is weekday-major; we must emit chronological days[]."""
    # Two weeks of cells as GitHub emits them: all Sundays, then Mondays, …
    sundays = ["2025-08-03", "2025-08-10"]
    mondays = ["2025-08-04", "2025-08-11"]
    tuesdays = ["2025-08-05", "2025-08-12"]
    tips = {
        "2025-08-03": "No contributions on August 3rd.",
        "2025-08-10": "1 contribution on August 10th.",
        "2025-08-04": "2 contributions on August 4th.",
        "2025-08-11": "3 contributions on August 11th.",
        "2025-08-05": "No contributions on August 5th.",
        "2025-08-12": "4 contributions on August 12th.",
    }
    parts = ['<h2>10 contributions in the last year</h2>']
    for week_days in (sundays, mondays, tuesdays):
        for d in week_days:
            parts.append(f'<td data-date="{d}" data-level="1"></td>')
            parts.append(f"<tool-tip>{tips[d]}</tool-tip>")
    out = parse_contributions_html("\n".join(parts), today="2025-08-12")
    assert out is not None
    dates = [d["date"] for d in out["days"]]
    assert dates == sorted(dates)
    assert dates[0] == "2025-08-03"
    assert dates[-1] == "2025-08-12"
    assert out["from"] == dates[0]
    assert out["to"] == dates[-1]
    # Chronological: 0,2,0,1,3,4 → current streak ends on 12 with 4 then 3 then 1 = 3
    assert out["currentStreak"] == 3
    assert out["longestStreak"] == 3


def test_current_streak_today_zero_is_grace_day():
    today = date.today().isoformat()
    yday = (date.today() - timedelta(days=1)).isoformat()
    earlier = (date.today() - timedelta(days=2)).isoformat()
    days = [
        {"date": earlier, "count": 1, "level": 1},
        {"date": yday, "count": 2, "level": 1},
        {"date": today, "count": 0, "level": 0},
    ]
    assert _current_streak(days, today=today) == 2
    # Zero yesterday breaks even if today has activity.
    broken = [
        {"date": earlier, "count": 5, "level": 1},
        {"date": yday, "count": 0, "level": 0},
        {"date": today, "count": 9, "level": 2},
    ]
    assert _current_streak(broken, today=today) == 1


def test_longest_streak_independent_of_current():
    days = [
        {"date": "2025-01-01", "count": 1, "level": 1},
        {"date": "2025-01-02", "count": 1, "level": 1},
        {"date": "2025-01-03", "count": 1, "level": 1},
        {"date": "2025-01-04", "count": 0, "level": 0},
        {"date": "2025-01-05", "count": 2, "level": 1},
        {"date": "2025-01-06", "count": 2, "level": 1},
    ]
    assert _longest_streak(days) == 3
    assert _current_streak(days, today="2025-01-06") == 2


def test_parse_trending_developers_no_search_score():
    html = '''
    <article class="Box-row d-flex" id="pa-getify">
      <h1><a href="/getify">Kyle Simpson</a></h1>
      <img src="https://avatars.githubusercontent.com/u/150330?v=4" />
      <a href="/getify/You-Dont-Know-JS">repo</a>
      <div class="f6 color-fg-muted">A book series on JS</div>
    </article>
    '''
    rows = parse_trending_developers_html(html, since="daily")
    assert len(rows) == 1
    r = rows[0]
    assert r["login"] == "getify"
    assert r["name"] == "Kyle Simpson"
    assert r["popularRepo"] == "getify/You-Dont-Know-JS"
    assert r["rank"] == 1
    assert "score" not in r