"""GitHub contributions calendar + trending developers HTML."""

from __future__ import annotations

from app.services.github_contributions_native import parse_contributions_html
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
    out = parse_contributions_html(html)
    assert out is not None
    assert out["totalContributions"] == 164
    assert out["days"][0] == {"date": "2025-08-03", "count": 0, "level": 0}
    assert out["days"][1]["count"] == 5
    assert out["currentStreak"] == 2  # last two days nonzero
    assert "recentPublicEvents" not in out


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
