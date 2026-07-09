"""Native tweet lookup via Twitter's public syndication endpoint.

``cdn.syndication.twimg.com/tweet-result`` is the same unauthenticated API
that powers embedded tweets. It returns the tweet text, author, timestamp,
language, entities and media — everything a transcript/text extraction needs,
for free and in ~200ms.

It does NOT expose full engagement metrics (retweets, quotes, views,
bookmarks) or follower counts, so it is only suitable for the text-only
transcript path — not the engagement-rich ``tweet-details`` endpoint, which
stays on the Apify actor.
"""

from __future__ import annotations

import math
from typing import Any

import httpx

_UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_BASE = "https://cdn.syndication.twimg.com/tweet-result"
_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def _token(tweet_id: str) -> str:
    """Reproduce the JS token the web embed derives from the tweet id.

    ``((id / 1e15) * pi).toString(36)`` with ``0`` and ``.`` stripped.
    """
    val = (int(tweet_id) / 1e15) * math.pi
    intpart = int(val)
    frac = val - intpart
    s = "" if intpart else "0"
    while intpart > 0:
        s = _DIGITS[intpart % 36] + s
        intpart //= 36
    s += "."
    for _ in range(12):
        frac *= 36
        d = int(frac)
        s += _DIGITS[d]
        frac -= d
    return s.replace("0", "").replace(".", "")


async def tweet_result(tweet_id: str, lang: str = "en") -> dict[str, Any] | None:
    """Fetch a tweet's public syndication record, or None on any failure."""
    if not tweet_id or not tweet_id.isdigit():
        return None
    try:
        async with httpx.AsyncClient(timeout=10, headers=_UA, follow_redirects=True) as client:
            resp = await client.get(
                _BASE, params={"id": tweet_id, "token": _token(tweet_id), "lang": lang}
            )
    except httpx.HTTPError:
        return None
    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) and data.get("text") is not None else None
