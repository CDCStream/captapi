"""Native-first live audit: ~1000 balanced requests against api.captapi.com.

Measures X-Captapi-Source (direct/apify/cache/unknown), latency, and saves
response JSON per request for quality review.

Usage:
  python scripts/native_first_live_audit.py
  TOTAL=1000 CONCURRENCY=8 SMOKE_BASE=https://api.captapi.com python scripts/native_first_live_audit.py
"""

from __future__ import annotations

import asyncio
import json
import os
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.core.security import generate_api_key
from app.services.supabase_client import get_supabase

BASE = os.environ.get("SMOKE_BASE", "https://api.captapi.com").rstrip("/")
TOTAL = int(os.environ.get("TOTAL", "1000"))
CONCURRENCY = int(os.environ.get("CONCURRENCY", "8"))
TIMEOUT = float(os.environ.get("TIMEOUT", "180"))
OUT_ROOT = Path(__file__).resolve().parents[1] / "_audit_native_live"
TARGET_NATIVE_PCT = 98.2

# Fixtures
YT_VIDEO = "https://www.youtube.com/watch?v=kJQP7kiw5Fk"
YT_VIDEO2 = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
YT_VIDEO3 = "https://www.youtube.com/watch?v=9bZkp7q19f0"
YT_CH = "https://www.youtube.com/@MrBeast"
YT_CH2 = "https://www.youtube.com/@NASA"
# Live post from @charlidamelio channel-posts (old 7228… id is dead → 404).
TT_VIDEO_REAL = "https://www.tiktok.com/@charlidamelio/video/7667257618544495886"
TT_VIDEO2 = "https://www.tiktok.com/@khaby.lame/video/7135723405012479238"
TT_USER = "https://www.tiktok.com/@charlidamelio"
TT_USER2 = "https://www.tiktok.com/@khaby.lame"
IG_USER = "https://www.instagram.com/nasa/"
IG_USER2 = "https://www.instagram.com/natgeo/"
# Real NASA post from channel-posts (C8H0v1tNS9x was invalid → empty Apify stub).
IG_POST = "https://www.instagram.com/p/DbTmwYKFkZo/"
FB_PAGE = "https://www.facebook.com/Meta"
FB_PAGE2 = "https://www.facebook.com/nintendo"
TW_USER = "https://x.com/nasa"
TW_TWEET = "https://x.com/jack/status/20"
RD_SUB = "https://www.reddit.com/r/programming/"
RD_POST = "https://www.reddit.com/r/AskReddit/comments/1c5x8kq/what_is_something_that_sounds_fake_but_is_actually/"
TH_USER = "https://www.threads.net/@zuck"
PIN_USER = "https://www.pinterest.com/nasa/"
LI_PROFILE = "https://www.linkedin.com/in/williamhgates"
LI_COMPANY = "https://www.linkedin.com/company/microsoft"
SC_USER = "nba"
KWAI_USER = "https://www.kwai.com/@topfilmeseseriesnatv"
RUMBLE_Q = "news"
FB_MARKET_LOCATION = "Austin, TX"
FB_EVENT_Q = "live music"


def _ep(
    eid: str,
    path: str,
    params: dict[str, Any],
    *,
    paginated: bool = False,
    weight: int = 1,
) -> dict[str, Any]:
    return {
        "id": eid,
        "path": path,
        "params": params,
        "paginated": paginated,
        "weight": weight,
    }


CATALOG: list[dict[str, Any]] = [
    _ep("youtube.video-details", "/v1/youtube/video-details", {"url": YT_VIDEO}, weight=2),
    _ep("youtube.video-details.b", "/v1/youtube/video-details", {"url": YT_VIDEO2}, weight=1),
    _ep("youtube.video-details.c", "/v1/youtube/video-details", {"url": YT_VIDEO3}, weight=1),
    _ep("youtube.channel-details", "/v1/youtube/channel-details", {"url": YT_CH}, weight=2),
    _ep("youtube.channel-details.b", "/v1/youtube/channel-details", {"url": YT_CH2}, weight=1),
    _ep("youtube.channel-videos", "/v1/youtube/channel-videos", {"url": YT_CH, "limit": 10}, paginated=True, weight=2),
    _ep("youtube.comments", "/v1/youtube/comments", {"url": YT_VIDEO, "limit": 20}, paginated=True, weight=2),
    _ep("youtube.search", "/v1/youtube/search", {"q": "lofi hip hop", "limit": 10}, weight=2),
    _ep("youtube.trending-shorts", "/v1/youtube/trending-shorts", {"limit": 10}, weight=1),
    _ep("tiktok.video-details", "/v1/tiktok/video-details", {"url": TT_VIDEO_REAL}, weight=2),
    _ep("tiktok.video-details.b", "/v1/tiktok/video-details", {"url": TT_VIDEO2}, weight=1),
    _ep("tiktok.channel-details", "/v1/tiktok/channel-details", {"url": TT_USER}, weight=2),
    _ep("tiktok.channel-details.b", "/v1/tiktok/channel-details", {"url": TT_USER2}, weight=1),
    _ep("tiktok.channel-posts", "/v1/tiktok/channel-posts", {"url": TT_USER, "limit": 10}, paginated=True, weight=2),
    _ep("tiktok.channel-posts.b", "/v1/tiktok/channel-posts", {"url": TT_USER2, "limit": 10}, paginated=True, weight=1),
    _ep("tiktok.comments", "/v1/tiktok/comments", {"url": TT_VIDEO_REAL, "limit": 20}, paginated=True, weight=2),
    _ep("tiktok.comments.b", "/v1/tiktok/comments", {"url": TT_VIDEO2}, weight=1),
    _ep("tiktok.top-search", "/v1/tiktok/top-search", {"q": "cooking", "limit": 10}, weight=1),
    _ep("tiktok.search-users", "/v1/tiktok/search/users", {"q": "nasa", "limit": 10}, weight=1),
    _ep("tiktok.trending-feed", "/v1/tiktok/trending-feed", {"limit": 10}, weight=1),
    _ep(
        "tiktok.popular-hashtags",
        "/v1/tiktok/popular-hashtags",
        {"query": "cooking", "limit": 10},
        weight=1,
    ),
    _ep("instagram.channel-details", "/v1/instagram/channel-details", {"url": IG_USER}, weight=2),
    _ep("instagram.channel-details.b", "/v1/instagram/channel-details", {"url": IG_USER2}, weight=1),
    _ep("instagram.channel-posts", "/v1/instagram/channel-posts", {"url": IG_USER, "limit": 12}, paginated=True, weight=2),
    _ep("instagram.channel-posts.b", "/v1/instagram/channel-posts", {"url": IG_USER2, "limit": 12}, paginated=True, weight=1),
    _ep("instagram.channel-reels", "/v1/instagram/channel-reels", {"url": IG_USER, "limit": 12}, paginated=True, weight=2),
    _ep("instagram.details", "/v1/instagram/details", {"url": IG_POST}, weight=1),
    _ep("instagram.trending-reels", "/v1/instagram/trending-reels", {"country": "US", "limit": 10}, weight=1),
    _ep("instagram.hashtag-search", "/v1/instagram/hashtag-search", {"q": "travel", "limit": 10}, weight=1),
    _ep("facebook.page-details", "/v1/facebook/page-details", {"url": FB_PAGE}, weight=2),
    _ep("facebook.page-details.b", "/v1/facebook/page-details", {"url": FB_PAGE2}, weight=1),
    _ep("facebook.profile-posts", "/v1/facebook/profile-posts", {"url": FB_PAGE, "limit": 10}, weight=2),
    _ep("facebook.event-search", "/v1/facebook/event-search", {"q": FB_EVENT_Q, "limit": 8}, weight=1),
    _ep("facebook.event-search.b", "/v1/facebook/event-search", {"q": "concert", "limit": 8}, weight=1),
    _ep(
        "facebook.marketplace-search",
        "/v1/facebook/marketplace-search",
        {"q": "iphone", "location": FB_MARKET_LOCATION, "limit": 8},
        weight=1,
    ),
    _ep("twitter.profile", "/v1/twitter/profile", {"url": TW_USER}, weight=2),
    _ep("twitter.tweet-details", "/v1/twitter/tweet-details", {"url": TW_TWEET}, weight=2),
    _ep("twitter.user-tweets", "/v1/twitter/user-tweets", {"url": TW_USER, "limit": 10}, paginated=True, weight=2),
    _ep("twitter.search", "/v1/twitter/search", {"q": "openai", "limit": 10}, weight=1),
    _ep("reddit.subreddit-details", "/v1/reddit/subreddit-details", {"url": RD_SUB}, weight=1),
    _ep("reddit.subreddit-posts", "/v1/reddit/subreddit-posts", {"url": RD_SUB, "limit": 10}, paginated=True, weight=2),
    _ep("reddit.post-details", "/v1/reddit/post-details", {"url": RD_POST}, weight=1),
    _ep("reddit.search", "/v1/reddit/search", {"q": "python tips", "limit": 10}, weight=1),
    _ep("threads.profile", "/v1/threads/profile", {"url": TH_USER}, weight=1),
    _ep("threads.user-posts", "/v1/threads/user-posts", {"url": TH_USER, "limit": 10}, weight=1),
    _ep("bluesky.profile", "/v1/bluesky/profile", {"url": "https://bsky.app/profile/bsky.app"}, weight=1),
    _ep("pinterest.user-pins", "/v1/pinterest/user-pins", {"url": PIN_USER, "limit": 10}, weight=1),
    _ep("pinterest.search", "/v1/pinterest/search", {"q": "minimalist kitchen", "limit": 10}, weight=2),
    _ep("linkedin.profile", "/v1/linkedin/profile", {"url": LI_PROFILE}, weight=1),
    _ep("linkedin.company", "/v1/linkedin/company", {"url": LI_COMPANY}, weight=1),
    _ep("linkedin.search-posts", "/v1/linkedin/search-posts", {"q": "AI agents", "limit": 8}, weight=1),
    _ep("snapchat.user-profile", "/v1/snapchat/user-profile", {"url": SC_USER}, weight=2),
    _ep("kwai.profile", "/v1/kwai/profile", {"url": KWAI_USER}, weight=1),
    _ep("kwai.user-posts", "/v1/kwai/user-posts", {"url": KWAI_USER, "limit": 8}, weight=1),
    _ep("rumble.search", "/v1/rumble/search", {"q": RUMBLE_Q, "limit": 10}, weight=1),
    _ep("tiktok_shop.shop-search", "/v1/tiktok-shop/shop-search", {"q": "phone case", "region": "US", "limit": 8}, weight=2),
    _ep("ad_library.fb.search", "/v1/ad-library/facebook/search", {"q": "nike", "limit": 8}, weight=1),
    _ep("ad_library.tt.search", "/v1/ad-library/tiktok/search", {"q": "skincare", "limit": 8}, weight=1),
    _ep("analytics.post.yt", "/v1/analytics/post", {"url": YT_VIDEO}, weight=1),
    _ep("analytics.post.tw", "/v1/analytics/post", {"url": TW_TWEET}, weight=1),
    _ep("spotify.search", "/v1/spotify/search", {"q": "Taylor Swift", "limit": 8}, weight=1),
    _ep("twitch.profile", "/v1/twitch/profile", {"url": "https://www.twitch.tv/ninja"}, weight=1),
    _ep("github.user", "/v1/github/user", {"username": "torvalds"}, weight=1),
]


def _alloc_quotas(catalog: list[dict[str, Any]], total: int) -> dict[str, int]:
    weights = [max(1, int(e.get("weight") or 1)) for e in catalog]
    wsum = sum(weights)
    raw = [total * w / wsum for w in weights]
    quotas = [max(1, int(x)) for x in raw]
    while sum(quotas) > total:
        i = max(range(len(quotas)), key=lambda j: quotas[j])
        if quotas[i] > 1:
            quotas[i] -= 1
        else:
            break
    while sum(quotas) < total:
        i = max(range(len(quotas)), key=lambda j: weights[j])
        quotas[i] += 1
    return {catalog[i]["id"]: quotas[i] for i in range(len(catalog))}


def _null_paths(obj: Any, prefix: str = "", out: list[str] | None = None, depth: int = 0) -> list[str]:
    if out is None:
        out = []
    if depth > 6:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            if v is None:
                out.append(p)
            else:
                _null_paths(v, p, out, depth + 1)
    elif isinstance(obj, list) and obj:
        _null_paths(obj[0], f"{prefix}[0]", out, depth + 1)
    return out


async def _one(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    *,
    eid: str,
    path: str,
    params: dict[str, Any],
    page: int,
    out_dir: Path,
    seq: int,
    jsonl_path: Path,
    jsonl_lock: asyncio.Lock,
) -> dict[str, Any]:
    async with sem:
        t0 = time.perf_counter()
        status = 0
        source = "error"
        credits = None
        body: Any = None
        err = None
        try:
            r = await client.get(f"{BASE}{path}", params=params, timeout=TIMEOUT)
            status = r.status_code
            source = (r.headers.get("x-captapi-source") or "unknown").lower()
            credits_h = r.headers.get("x-captapi-credits")
            credits = int(credits_h) if credits_h and credits_h.isdigit() else None
            try:
                body = r.json()
            except Exception:
                body = {"_raw": (r.text or "")[:4000]}
        except Exception as exc:  # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
            body = {"error": err}
        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        body_path = out_dir / "bodies" / eid.replace("/", "_") / f"{seq:05d}_p{page}.json"
        body_path.parent.mkdir(parents=True, exist_ok=True)
        body_path.write_text(json.dumps(body, ensure_ascii=False, indent=2)[:2_000_000], encoding="utf-8")

        data = body.get("data") if isinstance(body, dict) else None
        nulls = _null_paths(data)[:40] if data is not None else []
        next_cursor = None
        if isinstance(data, dict):
            next_cursor = data.get("nextCursor") or data.get("cursor") or data.get("next_cursor")

        row = {
            "seq": seq,
            "endpoint_id": eid,
            "path": path,
            "page": page,
            "params": params,
            "status": status,
            "ok": 200 <= status < 300,
            "source": source,
            "credits": credits,
            "elapsed_ms": elapsed_ms,
            "next_cursor": next_cursor,
            "null_fields": nulls,
            "null_count": len(nulls),
            "body_file": str(body_path.relative_to(out_dir)),
            "error": err,
        }
        # Incremental append — process death must not lose the run.
        line = json.dumps(row, ensure_ascii=False) + "\n"
        async with jsonl_lock:
            with jsonl_path.open("a", encoding="utf-8") as fh:
                fh.write(line)
        return row


def _build_summary(
    results: list[dict[str, Any]],
    *,
    stamp: str,
    wall_s: float,
    credits_avail: int,
    partial: bool = False,
) -> dict[str, Any]:
    by_ep: dict[str, dict[str, Any]] = {}
    source_counts: dict[str, int] = defaultdict(int)
    ok_rows = [r for r in results if r.get("ok")]
    for r in results:
        source_counts[r.get("source") or "unknown"] += 1
        eid = r["endpoint_id"]
        slot = by_ep.setdefault(
            eid,
            {
                "endpoint_id": eid,
                "path": r["path"],
                "n": 0,
                "ok": 0,
                "direct": 0,
                "apify": 0,
                "cache": 0,
                "unknown": 0,
                "error": 0,
                "latencies_ms": [],
                "pages": defaultdict(int),
                "null_field_freq": defaultdict(int),
            },
        )
        slot["n"] += 1
        if r.get("ok"):
            slot["ok"] += 1
        src = r.get("source") or "unknown"
        if src in ("direct", "apify", "cache", "unknown", "error"):
            slot[src] += 1
        else:
            slot["unknown"] += 1
        slot["latencies_ms"].append(r["elapsed_ms"])
        slot["pages"][r.get("page", 1)] += 1
        for nf in r.get("null_fields") or []:
            slot["null_field_freq"][nf] += 1

    scored = []
    for eid, slot in by_ep.items():
        denom = slot["direct"] + slot["apify"]
        native_pct = round(100.0 * slot["direct"] / denom, 2) if denom else None
        lats = sorted(slot["latencies_ms"])
        scored.append(
            {
                "endpoint_id": eid,
                "path": slot["path"],
                "n": slot["n"],
                "ok": slot["ok"],
                "ok_pct": round(100.0 * slot["ok"] / slot["n"], 2) if slot["n"] else 0,
                "direct": slot["direct"],
                "apify": slot["apify"],
                "cache": slot["cache"],
                "unknown": slot["unknown"],
                "error": slot["error"],
                "native_pct": native_pct,
                "below_target": bool(native_pct is not None and native_pct < TARGET_NATIVE_PCT),
                "latency_ms": {
                    "p50": lats[len(lats) // 2] if lats else None,
                    "p95": lats[int(len(lats) * 0.95)] if lats else None,
                    "avg": int(statistics.mean(lats)) if lats else None,
                    "max": max(lats) if lats else None,
                },
                "pages": dict(slot["pages"]),
                "top_null_fields": sorted(slot["null_field_freq"].items(), key=lambda x: -x[1])[:15],
            }
        )

    scored.sort(
        key=lambda x: (
            x["native_pct"] is None,
            x["native_pct"] if x["native_pct"] is not None else 999,
            -x["n"],
        )
    )

    direct_n = source_counts.get("direct", 0)
    apify_n = source_counts.get("apify", 0)
    denom = direct_n + apify_n
    overall_native = round(100.0 * direct_n / denom, 2) if denom else None

    return {
        "target_base": BASE,
        "started_utc": stamp,
        "wall_seconds": round(wall_s, 1),
        "total_requests": len(results),
        "ok": len(ok_rows),
        "source_counts": dict(source_counts),
        "native_pct_of_resolved": overall_native,
        "target_native_pct": TARGET_NATIVE_PCT,
        "meets_target": bool(overall_native is not None and overall_native >= TARGET_NATIVE_PCT),
        "credits_available_before": credits_avail,
        "partial": partial,
        "by_endpoint": scored,
        "worst_native_endpoints": [e for e in scored if e.get("below_target")],
        "slowest_endpoints": sorted(
            scored, key=lambda x: -((x.get("latency_ms") or {}).get("p95") or 0)
        )[:15],
    }


def _write_artifacts(
    out_dir: Path,
    summary: dict[str, Any],
    *,
    write_report: bool = True,
) -> None:
    tmp = out_dir / "summary.json.tmp"
    tmp.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(out_dir / "summary.json")
    if not write_report:
        return
    scored = summary.get("by_endpoint") or []
    lines = [
        f"# Native-first live audit {summary.get('started_utc')}",
        f"Base: {summary.get('target_base')}",
        f"Requests: {summary.get('total_requests')} ok={summary.get('ok')} wall={summary.get('wall_seconds')}s",
        f"Sources: {summary.get('source_counts')}",
        (
            f"Native% (direct/(direct+apify)): {summary.get('native_pct_of_resolved')}%  "
            f"target={summary.get('target_native_pct')}%  meet={summary.get('meets_target')}"
        ),
        "",
        "## Per-endpoint (sorted by native% ascending)",
        "",
        f"{'endpoint':<36} {'n':>4} {'ok%':>6} {'nat%':>6} {'p50':>6} {'p95':>6} {'apify':>5}",
        "-" * 80,
    ]
    for e in scored:
        nat = f"{e['native_pct']}%" if e["native_pct"] is not None else "n/a"
        lines.append(
            f"{e['endpoint_id']:<36} {e['n']:>4} {e['ok_pct']:>5.1f}% "
            f"{nat:>6} {(e['latency_ms']['p50'] or 0):>5} {(e['latency_ms']['p95'] or 0):>5} {e['apify']:>5}"
        )
    report = "\n".join(lines) + "\n"
    (out_dir / "REPORT.md").write_text(report, encoding="utf-8")


async def run_audit() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = OUT_ROOT / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "bodies").mkdir(exist_ok=True)

    sb = get_supabase()
    bals = (
        sb.table("credit_balances")
        .select("user_id, subscription_credits, topup_credits")
        .execute()
    )
    cands = [
        b
        for b in (bals.data or [])
        if (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0) > 500
    ]
    cands.sort(
        key=lambda b: (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0),
        reverse=True,
    )
    if not cands:
        raise SystemExit("No user with >500 credits for live audit")
    user_id = cands[0]["user_id"]
    credits_avail = (cands[0].get("subscription_credits") or 0) + (cands[0].get("topup_credits") or 0)
    plain, kh, pfx = generate_api_key()
    ins = (
        sb.table("api_keys")
        .insert({"user_id": user_id, "key_hash": kh, "key_prefix": pfx, "name": f"native-audit-{stamp}"})
        .execute()
    )
    kid = ins.data[0]["id"]

    quotas = _alloc_quotas(CATALOG, TOTAL)
    by_id = {e["id"]: e for e in CATALOG}

    print(f"Target {BASE}")
    print(f"Credits available ~{credits_avail} | TOTAL={TOTAL} CONCURRENCY={CONCURRENCY}")
    print(f"Endpoints {len(CATALOG)} | out {out_dir}")
    print(f"Key prefix {pfx}...")

    sem = asyncio.Semaphore(CONCURRENCY)
    results: list[dict[str, Any]] = []
    results_lock = asyncio.Lock()
    seq = 0
    seq_lock = asyncio.Lock()
    jsonl_path = out_dir / "requests.jsonl"
    jsonl_path.write_text("", encoding="utf-8")
    jsonl_lock = asyncio.Lock()

    async def next_seq() -> int:
        nonlocal seq
        async with seq_lock:
            seq += 1
            return seq

    async def record(row: dict[str, Any]) -> None:
        async with results_lock:
            results.append(row)
            n = len(results)
            if n % 25 == 0:
                wall = time.perf_counter() - started
                summary = _build_summary(
                    list(results),
                    stamp=stamp,
                    wall_s=wall,
                    credits_avail=credits_avail,
                    partial=True,
                )
                _write_artifacts(out_dir, summary, write_report=False)

    headers = {"Authorization": f"Bearer {plain}"}
    started = time.perf_counter()

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        async def call_one(
            *, eid: str, path: str, params: dict[str, Any], page: int
        ) -> dict[str, Any]:
            s = await next_seq()
            row = await _one(
                client,
                sem,
                eid=eid,
                path=path,
                params=params,
                page=page,
                out_dir=out_dir,
                seq=s,
                jsonl_path=jsonl_path,
                jsonl_lock=jsonl_lock,
            )
            await record(row)
            return row

        async def run_endpoint(eid: str, n: int) -> list[dict[str, Any]]:
            ep = by_id[eid]
            local: list[dict[str, Any]] = []
            starters = max(1, n // 3) if ep["paginated"] else n
            done = 0
            for _i in range(starters):
                if done >= n:
                    break
                params = dict(ep["params"])
                params["cache"] = "false"
                row = await call_one(eid=eid, path=ep["path"], params=params, page=1)
                local.append(row)
                done += 1
                print(f"[{done}/{n} {eid}] p1 {row['status']} {row['source']} {row['elapsed_ms']}ms", flush=True)

                if ep["paginated"] and row.get("ok") and row.get("next_cursor") and done < n:
                    p2 = dict(params)
                    p2["cursor"] = row["next_cursor"]
                    row2 = await call_one(eid=eid, path=ep["path"], params=p2, page=2)
                    local.append(row2)
                    done += 1
                    print(f"[{done}/{n} {eid}] p2 {row2['status']} {row2['source']} {row2['elapsed_ms']}ms", flush=True)

                    if row2.get("ok") and row2.get("next_cursor") and done < n:
                        p3 = dict(params)
                        p3["cursor"] = row2["next_cursor"]
                        row3 = await call_one(eid=eid, path=ep["path"], params=p3, page=3)
                        local.append(row3)
                        done += 1
                        print(f"[{done}/{n} {eid}] p3 {row3['status']} {row3['source']} {row3['elapsed_ms']}ms", flush=True)

            while done < n:
                params = dict(ep["params"])
                params["cache"] = "false"
                if "q" in params and done % 2 == 1:
                    params["q"] = f"{params['q']} tip"
                row = await call_one(eid=eid, path=ep["path"], params=params, page=1)
                local.append(row)
                done += 1
                print(f"[{done}/{n} {eid}] p1 {row['status']} {row['source']} {row['elapsed_ms']}ms", flush=True)
            return local

        ep_sem = asyncio.Semaphore(3)

        async def wrap(eid: str, n: int) -> list[dict[str, Any]]:
            async with ep_sem:
                return await run_endpoint(eid, n)

        await asyncio.gather(*[wrap(eid, n) for eid, n in quotas.items()])

    wall_s = time.perf_counter() - started

    try:
        sb.table("api_keys").delete().eq("id", kid).execute()
    except Exception as exc:  # noqa: BLE001
        print("key revoke warn:", exc)

    summary = _build_summary(
        results, stamp=stamp, wall_s=wall_s, credits_avail=credits_avail, partial=False
    )
    _write_artifacts(out_dir, summary, write_report=True)
    report = (out_dir / "REPORT.md").read_text(encoding="utf-8")
    print("\n" + report)
    print(f"Artifacts: {out_dir}")
    return out_dir


if __name__ == "__main__":
    asyncio.run(run_audit())
