"""DataForSEO keyword research for Google Ads platform campaigns.

Builds seed keywords per Captapi platform, fetches US Google volume/CPC/KD,
classifies into Core / Expansion / Free Tools / Brand+Competitor, and writes:

  marketing/ads-keyword-plan.csv
  marketing/google-ads-editor-import.csv

Usage:
  set DATAFORSEO_LOGIN=...
  set DATAFORSEO_PASSWORD=...
  python scripts/ads_keyword_research.py
  python scripts/ads_keyword_research.py --dry-run   # seeds only, no API

Env (optional):
  DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD
  Also loads KEY=VAL from frontend/.env.local and repo .env if present.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_PLAN = ROOT / "marketing" / "ads-keyword-plan.csv"
OUT_EDITOR = ROOT / "marketing" / "google-ads-editor-import.csv"
BANK = ROOT / "marketing" / "keyword-bank.csv"
SITE = "https://captapi.com"

LOCATION_US = 2840
LANG = "en"
BATCH = 20
SLEEP_S = 0.35
MIN_VOLUME = 50

CORE_PLATFORMS = {
    "instagram",
    "tiktok",
    "linkedin",
    "reddit",
    "twitter",
    "facebook",
}

# (platform_id, display name, landing path, seed keywords)
PLATFORMS: list[tuple[str, str, str, list[str]]] = [
    (
        "tiktok",
        "TikTok API",
        "/apis/tiktok-api",
        [
            "tiktok api",
            "tiktok scraper api",
            "tiktok data api",
            "tiktok profile api",
            "tiktok comments api",
            "tiktok video api",
            "tiktok analytics api",
        ],
    ),
    (
        "instagram",
        "Instagram API",
        "/apis/instagram-api",
        [
            "instagram api",
            "instagram scraper api",
            "instagram data api",
            "instagram profile api",
            "instagram comments api",
            "instagram reels api",
            "instagram api without login",
        ],
    ),
    (
        "facebook",
        "Facebook API",
        "/apis/facebook-api",
        [
            "facebook scraper api",
            "facebook page api",
            "facebook video api",
            "facebook data api",
            "facebook comments api",
        ],
    ),
    (
        "twitter",
        "Twitter X API",
        "/apis/twitter-api",
        [
            "twitter api",
            "x api twitter",
            "twitter scraper api",
            "twitter data api",
            "tweet scraper api",
            "twitter api alternative",
        ],
    ),
    (
        "reddit",
        "Reddit API",
        "/apis/reddit-api",
        [
            "reddit api",
            "reddit scraper api",
            "reddit data api",
            "reddit api alternative",
            "scrape reddit api",
        ],
    ),
    (
        "linkedin",
        "LinkedIn API",
        "/apis/linkedin-api",
        [
            "linkedin api",
            "linkedin scraper api",
            "linkedin profile api",
            "linkedin data api",
            "linkedin analytics api",
        ],
    ),
    (
        "youtube",
        "YouTube API",
        "/apis/youtube-api",
        [
            "youtube data api",
            "youtube comments api",
            "youtube channel api",
            "youtube analytics api",
            "youtube scraper api",
            # intentionally NO youtube transcript* (paused product line for ads)
        ],
    ),
    (
        "threads",
        "Threads API",
        "/apis/threads-api",
        ["threads api", "threads scraper api", "meta threads api"],
    ),
    (
        "bluesky",
        "Bluesky API",
        "/apis/bluesky-api",
        ["bluesky api", "bluesky scraper api", "bsky api"],
    ),
    (
        "pinterest",
        "Pinterest API",
        "/apis/pinterest-api",
        ["pinterest api", "pinterest scraper api", "pinterest data api"],
    ),
    (
        "rumble",
        "Rumble API",
        "/apis/rumble-api",
        ["rumble api", "rumble scraper api"],
    ),
    (
        "twitch",
        "Twitch API",
        "/apis/twitch-api",
        ["twitch api", "twitch scraper api", "twitch data api"],
    ),
    (
        "snapchat",
        "Snapchat API",
        "/apis/snapchat-api",
        ["snapchat api", "snapchat scraper api", "snapchat profile api"],
    ),
    (
        "github",
        "GitHub API",
        "/apis/github-api",
        ["github api", "github scraper api"],
    ),
    (
        "ad_library",
        "Ad Library API",
        "/apis/ad-library-api",
        [
            "ad library api",
            "facebook ad library api",
            "tiktok ad library api",
            "linkedin ad library api",
            "google ad library api",
        ],
    ),
    (
        "spotify",
        "Spotify API",
        "/apis/spotify-api",
        ["spotify api", "spotify scraper api"],
    ),
    (
        "soundcloud",
        "SoundCloud API",
        "/apis/soundcloud-api",
        ["soundcloud api", "soundcloud scraper api"],
    ),
    (
        "linktree",
        "Linktree API",
        "/apis/linktree-api",
        ["linktree api", "linktree scraper"],
    ),
    (
        "truth_social",
        "Truth Social API",
        "/apis/truth-social-api",
        ["truth social api", "truth social scraper"],
    ),
    (
        "kick",
        "Kick API",
        "/apis/kick-api",
        ["kick api streaming", "kick.com api"],
    ),
    (
        "tiktok_shop",
        "TikTok Shop API",
        "/apis/tiktok-shop-api",
        ["tiktok shop api", "tiktok shop scraper"],
    ),
]

FREE_TOOLS: list[tuple[str, str, list[str]]] = [
    (
        "TikTok Transcript Tool",
        "/tools/tiktok-transcript",
        [
            "tiktok transcript",
            "tiktok to transcript",
            "tiktok video transcript",
            "transcribe tiktok video",
            "tiktok transcript api",
        ],
    ),
    (
        "Instagram Transcript Tool",
        "/tools/instagram-transcript",
        [
            "instagram transcript",
            "instagram reel transcript",
            "transcribe instagram reel",
        ],
    ),
]

BRAND_COMPETITOR: list[tuple[str, str, list[str]]] = [
    (
        "Brand",
        "/",
        ["captapi", "capt api", "captapi api", "captapi pricing"],
    ),
    (
        "Competitor",
        "/alternatives",
        [
            "socialkit",
            "tikapi",
            "ensembledata",
            "scrapecreators",
            "tikapi alternative",
            "ensembledata alternative",
            "scrapecreators alternative",
        ],
    ),
]

PAUSE_KEYWORDS = [
    "youtube transcript",
    "youtube transcript api",
    "youtube api transcript",
    "youtube subtitle api",
    "youtube caption api",
    "get youtube transcript api",
    "youtube transcript api free",
    "free youtube transcript api",
]

PLAN_FIELDS = [
    "campaign",
    "ad_group",
    "keyword",
    "match_type",
    "volume",
    "cpc",
    "kd",
    "landing_path",
    "action",
    "notes",
]

EDITOR_FIELDS = [
    "Campaign",
    "Ad Group",
    "Keyword",
    "Criterion Type",
    "Final URL",
    "Max CPC",
]


def load_dotenv_files() -> None:
    for path in (
        ROOT / "frontend" / ".env.local",
        ROOT / "frontend" / ".env",
        ROOT / ".env",
        ROOT / "scripts" / ".env",
    ):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


def http_json(url: str, payload: list[dict[str, Any]], auth: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def dfs_auth() -> str | None:
    login = (os.environ.get("DATAFORSEO_LOGIN") or "").strip()
    password = (os.environ.get("DATAFORSEO_PASSWORD") or "").strip()
    if not login or not password:
        return None
    return base64.b64encode(f"{login}:{password}".encode()).decode()


def fetch_overview(auth: str, keywords: list[str]) -> dict[str, dict[str, Any]]:
    """Batch keyword overview (volume, CPC, KD)."""
    out: dict[str, dict[str, Any]] = {}
    for i in range(0, len(keywords), BATCH):
        chunk = keywords[i : i + BATCH]
        try:
            data = http_json(
                "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live",
                [
                    {
                        "keywords": chunk,
                        "location_code": LOCATION_US,
                        "language_code": LANG,
                    }
                ],
                auth,
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"  overview batch failed: {e}", file=sys.stderr)
            time.sleep(1)
            continue
        try:
            items = data["tasks"][0]["result"][0]["items"] or []
        except (KeyError, IndexError, TypeError):
            items = []
        for item in items:
            kw = (item.get("keyword") or "").lower().strip()
            if not kw:
                continue
            info = item.get("keyword_info") or {}
            props = item.get("keyword_properties") or {}
            out[kw] = {
                "volume": info.get("search_volume") or 0,
                "cpc": info.get("cpc") or 0,
                "kd": props.get("keyword_difficulty") or "",
            }
        time.sleep(SLEEP_S)
    return out


def load_bank_volumes() -> dict[str, dict[str, str]]:
    if not BANK.is_file():
        return {}
    rows: dict[str, dict[str, str]] = {}
    with BANK.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            kw = (row.get("keyword") or "").lower().strip()
            if kw:
                rows[kw] = row
    return rows


def campaign_for(platform_id: str) -> str:
    if platform_id in CORE_PLATFORMS:
        return "Search - Core Platforms"
    if platform_id == "youtube":
        return "Search - Expansion Platforms"
    return "Search - Expansion Platforms"


def match_types_for(keyword: str, volume: int) -> list[str]:
    """Phrase + exact for high intent; skip broad to control spend."""
    if volume >= 500:
        return ["Phrase", "Exact"]
    return ["Phrase", "Exact"]


def build_seeds() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for platform_id, ad_group, landing, seeds in PLATFORMS:
        camp = campaign_for(platform_id)
        for kw in seeds:
            rows.append(
                {
                    "campaign": camp,
                    "ad_group": ad_group,
                    "keyword": kw.lower(),
                    "landing_path": landing,
                    "action": "add",
                    "notes": f"seed:{platform_id}",
                }
            )
    for ad_group, landing, seeds in FREE_TOOLS:
        for kw in seeds:
            rows.append(
                {
                    "campaign": "Search - Free Tools",
                    "ad_group": ad_group,
                    "keyword": kw.lower(),
                    "landing_path": landing,
                    "action": "add",
                    "notes": "seed:free_tools",
                }
            )
    for ad_group, landing, seeds in BRAND_COMPETITOR:
        for kw in seeds:
            rows.append(
                {
                    "campaign": "Search - Brand + Competitor",
                    "ad_group": ad_group,
                    "keyword": kw.lower(),
                    "landing_path": landing,
                    "action": "add",
                    "notes": "seed:brand_competitor",
                }
            )
    for kw in PAUSE_KEYWORDS:
        rows.append(
            {
                "campaign": "Search - Transcript API",
                "ad_group": "YouTube Transcript (PAUSE)",
                "keyword": kw.lower(),
                "landing_path": "/",
                "action": "pause",
                "notes": "youtube_transcript_removed_from_ads",
            }
        )
    # dedupe by campaign+ad_group+keyword
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, str]] = []
    for row in rows:
        key = (row["campaign"], row["ad_group"], row["keyword"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def enrich(
    seeds: list[dict[str, str]],
    metrics: dict[str, dict[str, Any]],
    bank: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in seeds:
        kw = row["keyword"]
        m = metrics.get(kw) or {}
        b = bank.get(kw) or {}
        volume = int(m.get("volume") or 0) or int(b.get("volume") or 0 or 0)
        try:
            volume = int(float(m.get("volume") or b.get("volume") or 0))
        except (TypeError, ValueError):
            volume = 0
        try:
            cpc = float(m.get("cpc") or 0)
        except (TypeError, ValueError):
            cpc = 0.0
        kd = str(m.get("kd") if m.get("kd") not in (None, "") else b.get("kd") or "")
        action = row["action"]
        notes = row["notes"]
        if action == "add" and row["campaign"].startswith("Search - Expansion"):
            if volume > 0 and volume < MIN_VOLUME and cpc < 5:
                action = "skip"
                notes += ";low_volume"
        if action == "add" and "youtube transcript" in kw:
            action = "pause"
            notes += ";blocked_yt_transcript"
        out.append(
            {
                **row,
                "match_type": "|".join(match_types_for(kw, volume)),
                "volume": volume,
                "cpc": round(cpc, 2) if cpc else "",
                "kd": kd,
                "action": action,
                "notes": notes,
            }
        )
    out.sort(
        key=lambda r: (
            0 if r["action"] == "add" else 1,
            -int(r["volume"] or 0),
            r["campaign"],
            r["ad_group"],
            r["keyword"],
        )
    )
    return out


def write_plan(rows: list[dict[str, Any]]) -> None:
    OUT_PLAN.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PLAN.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=PLAN_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in PLAN_FIELDS})
    print(f"Wrote {OUT_PLAN} ({len(rows)} rows)")


def write_editor(rows: list[dict[str, Any]]) -> None:
    """Google Ads Editor-friendly keyword rows (phrase + exact)."""
    editor_rows: list[dict[str, str]] = []
    for r in rows:
        if r.get("action") != "add":
            continue
        url = SITE + r["landing_path"]
        for mt in str(r.get("match_type") or "Phrase").split("|"):
            mt = mt.strip()
            if not mt:
                continue
            kw = r["keyword"]
            if mt == "Exact":
                criterion = f"[{kw}]"
            elif mt == "Phrase":
                criterion = f'"{kw}"'
            else:
                criterion = kw
            editor_rows.append(
                {
                    "Campaign": r["campaign"],
                    "Ad Group": r["ad_group"],
                    "Keyword": criterion,
                    "Criterion Type": mt,
                    "Final URL": url,
                    "Max CPC": "",
                }
            )
    with OUT_EDITOR.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=EDITOR_FIELDS)
        w.writeheader()
        w.writerows(editor_rows)
    print(f"Wrote {OUT_EDITOR} ({len(editor_rows)} keyword rows)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip DataForSEO; use keyword-bank volumes only",
    )
    args = ap.parse_args()
    load_dotenv_files()

    seeds = build_seeds()
    print(f"Seeds: {len(seeds)}")
    bank = load_bank_volumes()
    metrics: dict[str, dict[str, Any]] = {}

    auth = None if args.dry_run else dfs_auth()
    if args.dry_run:
        print("Dry-run: skipping DataForSEO API")
    elif not auth:
        print(
            "DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD not set — "
            "using keyword-bank volumes only. Set env and re-run for live metrics.",
            file=sys.stderr,
        )
    else:
        kws = sorted({s["keyword"] for s in seeds if s["action"] != "pause"})
        print(f"Fetching DataForSEO overview for {len(kws)} keywords…")
        metrics = fetch_overview(auth, kws)
        print(f"Got metrics for {len(metrics)} keywords")

    rows = enrich(seeds, metrics, bank)
    write_plan(rows)
    write_editor(rows)

    add_n = sum(1 for r in rows if r["action"] == "add")
    pause_n = sum(1 for r in rows if r["action"] == "pause")
    skip_n = sum(1 for r in rows if r["action"] == "skip")
    print(f"Summary: add={add_n} pause={pause_n} skip={skip_n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
