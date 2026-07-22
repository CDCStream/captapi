"""Capture real docs examples for endpoints that still use generic placeholders.

Creates a temp API key, calls the live API (SMOKE_BASE, default
https://api.captapi.com) in two phases (phase 2 inputs are derived from
phase 1 responses, e.g. a tweet URL from user-tweets), writes successful
responses into api_snapshots.json and regenerates the frontend examples.

Usage:  python scripts/capture_snapshots_batch.py batch1
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.core.security import generate_api_key  # noqa: E402
from app.services.supabase_client import get_supabase  # noqa: E402

BASE = os.environ.get("SMOKE_BASE", "https://api.captapi.com")

# Trim huge lists so the generated docs file stays reasonable.
MAX_LIST = 5


def _truncate(value: Any, depth: int = 0) -> Any:
    if isinstance(value, list):
        return [_truncate(v, depth + 1) for v in value[:MAX_LIST if depth else 8]]
    if isinstance(value, dict):
        return {k: _truncate(v, depth + 1) for k, v in value.items()}
    return value


async def call(client: httpx.AsyncClient, slug: str, path: str, params: dict) -> tuple[str, dict]:
    started = time.perf_counter()
    try:
        r = await client.get(f"{BASE}{path}", params=params, timeout=300)
        elapsed = round(time.perf_counter() - started, 1)
        try:
            body = r.json()
        except Exception:  # noqa: BLE001
            body = {"raw": r.text[:300]}
        return slug, {"status": r.status_code, "elapsed": elapsed, "body": body}
    except Exception as e:  # noqa: BLE001
        return slug, {"status": 0, "elapsed": round(time.perf_counter() - started, 1), "body": {"error": str(e)}}


async def run_phase(
    client: httpx.AsyncClient,
    tests: list[tuple[str, str, dict]],
    *,
    concurrency: int = 0,
) -> dict[str, dict]:
    """Run endpoint captures. concurrency=0 means fully parallel (legacy)."""
    out: dict[str, dict] = {}
    if concurrency and concurrency > 0:
        sem = asyncio.Semaphore(concurrency)

        async def _one(slug: str, path: str, params: dict) -> tuple[str, dict]:
            async with sem:
                return await call(client, slug, path, params)

        results = await asyncio.gather(*(_one(slug, path, params) for slug, path, params in tests))
    else:
        results = await asyncio.gather(*(call(client, slug, path, params) for slug, path, params in tests))
    for slug, res in results:
        ok = 200 <= res["status"] < 300
        print(f"{'PASS' if ok else 'FAIL':4} {res['status']:>3} {res['elapsed']:>6}s  {slug}")
        if not ok:
            print(f"          {json.dumps(res['body'], ensure_ascii=False)[:220]}")
        out[slug] = res
    return out


def batch1_phase1() -> list[tuple[str, str, dict]]:
    return [
        ("twitter-profile", "/v1/twitter/profile", {"url": "https://x.com/nasa"}),
        ("twitter-user-tweets", "/v1/twitter/user-tweets", {"url": "https://x.com/nasa", "limit": 5}),
        ("twitter-search", "/v1/twitter/search", {"q": "artificial intelligence", "limit": 5}),
        ("twitter-community", "/v1/twitter/community", {"url": "https://x.com/i/communities/1493446837214187523"}),
        ("twitter-community-tweets", "/v1/twitter/community-tweets", {"url": "https://x.com/i/communities/1493446837214187523", "limit": 5}),
        ("linkedin-profile", "/v1/linkedin/profile", {"url": "https://www.linkedin.com/in/satyanadella"}),
        ("linkedin-company", "/v1/linkedin/company", {"url": "https://www.linkedin.com/company/microsoft"}),
        ("linkedin-company-posts", "/v1/linkedin/company-posts", {"url": "https://www.linkedin.com/company/microsoft", "limit": 5}),
        ("linkedin-search-posts", "/v1/linkedin/search-posts", {"q": "artificial intelligence", "limit": 5}),
        ("linkedin-ad-library-search-ads", "/v1/ad-library/linkedin/search-ads", {"q": "microsoft", "limit": 5}),
        ("reddit-subreddit-posts", "/v1/reddit/subreddit-posts", {"url": "r/space", "limit": 5}),
        ("reddit-subreddit-details", "/v1/reddit/subreddit-details", {"url": "r/space"}),
        ("reddit-search", "/v1/reddit/search", {"q": "james webb telescope", "limit": 5}),
        ("reddit-subreddit-search", "/v1/reddit/subreddit-search", {"url": "r/space", "q": "moon", "limit": 5}),
    ]


def batch1_phase2(p1: dict[str, dict]) -> list[tuple[str, str, dict]]:
    tests: list[tuple[str, str, dict]] = []

    def data_of(slug: str) -> dict:
        body = p1.get(slug, {}).get("body") or {}
        return body.get("data") or {}

    tweets = data_of("twitter-user-tweets").get("tweets") or data_of("twitter-user-tweets").get("posts") or []
    tweet_url = next((t.get("url") for t in tweets if isinstance(t, dict) and t.get("url")), None)
    if tweet_url:
        tests.append(("twitter-tweet-details", "/v1/twitter/tweet-details", {"url": tweet_url}))
        tests.append(("twitter-transcript", "/v1/twitter/transcript", {"url": tweet_url}))
    else:
        print("!! no tweet url from user-tweets; skipping tweet-details/transcript")

    li_posts = data_of("linkedin-company-posts").get("posts") or []
    li_url = next((p.get("url") for p in li_posts if isinstance(p, dict) and p.get("url")), None)
    if not li_url:
        srch = data_of("linkedin-search-posts").get("results") or data_of("linkedin-search-posts").get("posts") or []
        li_url = next((p.get("url") for p in srch if isinstance(p, dict) and p.get("url")), None)
    if li_url:
        tests.append(("linkedin-post-details", "/v1/linkedin/post-details", {"url": li_url}))
        tests.append(("linkedin-post-transcript", "/v1/linkedin/post-transcript", {"url": li_url}))
    else:
        print("!! no linkedin post url; skipping post-details/transcript")

    li_ads = data_of("linkedin-ad-library-search-ads").get("ads") or data_of("linkedin-ad-library-search-ads").get("results") or []
    ad_url = next((a.get("url") or a.get("adUrl") for a in li_ads if isinstance(a, dict) and (a.get("url") or a.get("adUrl"))), None)
    if ad_url:
        tests.append(("linkedin-ad-library-ad-details", "/v1/ad-library/linkedin/ad-details", {"url": ad_url}))
    else:
        print("!! no linkedin ad url; skipping ad-details")

    rd_posts = data_of("reddit-subreddit-posts").get("posts") or []
    rd_url = next((p.get("url") or p.get("permalink") for p in rd_posts if isinstance(p, dict) and (p.get("url") or p.get("permalink"))), None)
    if rd_url:
        tests.append(("reddit-post-details", "/v1/reddit/post-details", {"url": rd_url}))
        tests.append(("reddit-post-comments", "/v1/reddit/post-comments", {"url": rd_url, "limit": 5}))
        tests.append(("reddit-post-transcript", "/v1/reddit/post-transcript", {"url": rd_url, "limit": 5}))
    else:
        print("!! no reddit post url; skipping post endpoints")

    return tests


def batch2_phase1() -> list[tuple[str, str, dict]]:
    return [
        ("tiktok-profile-region", "/v1/tiktok/profile-region", {"url": "https://www.tiktok.com/@khaby.lame"}),
        ("tiktok-audience-demographics", "/v1/tiktok/audience-demographics", {"url": "https://www.tiktok.com/@khaby.lame"}),
        ("tiktok-search-suggestions", "/v1/tiktok/search-suggestions", {"q": "makeup", "country": "US", "language": "en-US", "limit": 5}),
        ("tiktok-live", "/v1/tiktok/live", {"url": "https://www.tiktok.com/@espn"}),
        ("tiktok-live-info", "/v1/tiktok/live-info", {"url": "https://www.tiktok.com/@espn"}),
        ("tiktok-popular-creators", "/v1/tiktok/popular-creators", {"country": "US", "limit": 5}),
        ("tiktok-shop-search", "/v1/tiktok-shop/shop-search", {"q": "phone case", "region": "US", "limit": 5}),
        ("tiktok-shop-user-showcase", "/v1/tiktok-shop/user-showcase", {"username": "jeffreestar", "limit": 5}),
        ("tiktok-ad-library-search", "/v1/ad-library/tiktok/search", {"q": "fashion", "limit": 5}),
        ("facebook-ad-library-search", "/v1/ad-library/facebook/search", {"q": "nike", "country": "US", "limit": 5}),
        ("facebook-ad-library-search-companies", "/v1/ad-library/facebook/search-companies", {"q": "nike", "limit": 5}),
        ("facebook-ad-library-company-ads", "/v1/ad-library/facebook/company-ads", {"url": "https://www.facebook.com/nike", "limit": 5}),
        ("google-ad-library-company-ads", "/v1/ad-library/google/company-ads", {"advertiser": "nike", "country": "US", "limit": 5}),
        ("google-ad-library-advertiser-search", "/v1/ad-library/google/advertiser-search", {"q": "nike", "limit": 5}),
        ("threads-profile", "/v1/threads/profile", {"url": "@zuck"}),
        ("threads-user-posts", "/v1/threads/user-posts", {"url": "@zuck", "limit": 5}),
        ("threads-search", "/v1/threads/search", {"q": "artificial intelligence", "limit": 5}),
        ("threads-search-users", "/v1/threads/search-users", {"q": "tech", "limit": 5}),
        ("snapchat-user-profile", "/v1/snapchat/user-profile", {"url": "nba"}),
    ]


def batch2_phase2(p1: dict[str, dict]) -> list[tuple[str, str, dict]]:
    tests: list[tuple[str, str, dict]] = []

    def data_of(slug: str) -> dict:
        body = p1.get(slug, {}).get("body") or {}
        return body.get("data") or {}

    def first_of(slug: str, *list_keys: str) -> dict:
        d = data_of(slug)
        for key in list_keys:
            rows = d.get(key)
            if isinstance(rows, list) and rows:
                return next((r for r in rows if isinstance(r, dict)), {})
        return {}

    product = first_of("tiktok-shop-search", "products", "results")
    product_url = product.get("url") or product.get("productUrl")
    if product_url:
        tests.append(("tiktok-shop-product-details", "/v1/tiktok-shop/product-details", {"url": product_url}))
        tests.append(("tiktok-shop-product-reviews", "/v1/tiktok-shop/product-reviews", {"url": product_url, "limit": 5}))
    else:
        print("!! no tiktok shop product url")
    seller = product.get("seller") or {}
    store_url = (seller.get("url") if isinstance(seller, dict) else None) or product.get("shopUrl") or product.get("storeUrl")
    if store_url:
        tests.append(("tiktok-shop-products", "/v1/tiktok-shop/shop-products", {"url": store_url, "limit": 5}))
    else:
        print("!! no tiktok shop store url")

    tt_ad = first_of("tiktok-ad-library-search", "ads", "results")
    tt_ad_ref = tt_ad.get("url") or tt_ad.get("id")
    if tt_ad_ref:
        tests.append(("tiktok-ad-library-ad-details", "/v1/ad-library/tiktok/ad-details", {"url": str(tt_ad_ref)}))
    else:
        print("!! no tiktok ad id")

    fb_ad = first_of("facebook-ad-library-search", "ads", "results")
    fb_ad_ref = fb_ad.get("url") or fb_ad.get("id")
    if fb_ad_ref:
        tests.append(("facebook-ad-library-ad-details", "/v1/ad-library/facebook/ad-details", {"url": str(fb_ad_ref)}))
        tests.append(("facebook-ad-library-ad-transcript", "/v1/ad-library/facebook/ad-transcript", {"url": str(fb_ad_ref)}))
    else:
        print("!! no facebook ad id")

    g_ad = first_of("google-ad-library-company-ads", "ads", "results")
    g_ref = g_ad.get("url") or g_ad.get("adTransparencyUrl") or g_ad.get("id")
    if g_ref:
        tests.append(("google-ad-library-ad-details", "/v1/ad-library/google/ad-details", {"creative_id": str(g_ref)}))
    else:
        print("!! no google creative url")

    th_post = first_of("threads-user-posts", "posts", "threads")
    th_url = th_post.get("url") or th_post.get("postUrl")
    if th_url:
        tests.append(("threads-post-details", "/v1/threads/post-details", {"url": th_url}))
    else:
        print("!! no threads post url")

    return tests


def batch3_phase1() -> list[tuple[str, str, dict]]:
    return [
        ("github-user", "/v1/github/user", {"username": "torvalds"}),
        ("github-repositories", "/v1/github/repositories", {"username": "torvalds", "limit": 5}),
        ("github-repository", "/v1/github/repository", {"repo": "torvalds/linux"}),
        ("github-pull-requests", "/v1/github/pull-requests", {"repo": "vercel/next.js", "state": "closed", "limit": 5}),
        ("github-activity", "/v1/github/activity", {"username": "torvalds", "limit": 5}),
        ("github-followers", "/v1/github/followers", {"username": "torvalds", "limit": 5}),
        ("github-following", "/v1/github/following", {"username": "gaearon", "limit": 5}),
        ("github-contributions", "/v1/github/contributions", {"username": "torvalds"}),
        ("github-trending-repositories", "/v1/github/trending-repositories", {"limit": 5}),
        ("github-trending-developers", "/v1/github/trending-developers", {"limit": 5}),
        ("facebook-marketplace-search", "/v1/facebook/marketplace-search", {"q": "desk chair", "location": "Austin, TX", "limit": 5, "details": "true"}),
        ("facebook-marketplace-location-search", "/v1/facebook/marketplace-location-search", {"q": "Austin", "limit": 5, "details": "true"}),
        ("facebook-event-search", "/v1/facebook/event-search", {"q": "comedy Chicago", "limit": 5}),
        ("facebook-profile-photos", "/v1/facebook/profile-photos", {"url": "https://www.facebook.com/nasa", "limit": 5}),
        ("facebook-profile-events", "/v1/facebook/profile-events", {"url": "https://www.facebook.com/MadisonSquareGarden", "limit": 5}),
        ("pinterest-search", "/v1/pinterest/search", {"q": "living room decor", "limit": 5}),
        ("pinterest-user-pins", "/v1/pinterest/user-pins", {"url": "https://www.pinterest.com/potterybarn/", "limit": 5}),
        ("pinterest-user-boards", "/v1/pinterest/user-boards", {"url": "https://www.pinterest.com/potterybarn/", "limit": 5}),
        ("spotify-artist", "/v1/spotify/artist", {"url": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"}),
        ("spotify-track", "/v1/spotify/track", {"url": "https://open.spotify.com/track/0V3wPSX9ygBnCm8psDIegu"}),
        ("spotify-album", "/v1/spotify/album", {"url": "https://open.spotify.com/album/151w1FgRZfnKZA9FEcg9Z3"}),
        ("spotify-search", "/v1/spotify/search", {"q": "lofi beats", "type": "tracks", "limit": 5}),
        ("spotify-podcast", "/v1/spotify/podcast", {"url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk", "limit": 5}),
        ("spotify-podcast-episodes", "/v1/spotify/podcast-episodes", {"url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk", "limit": 5}),
    ]


def batch3_phase2(p1: dict[str, dict]) -> list[tuple[str, str, dict]]:
    tests: list[tuple[str, str, dict]] = []

    def first_of(slug: str, *list_keys: str) -> dict:
        body = p1.get(slug, {}).get("body") or {}
        d = body.get("data") or {}
        for key in list_keys:
            rows = d.get(key)
            if isinstance(rows, list) and rows:
                return next((r for r in rows if isinstance(r, dict)), {})
        return {}

    event = first_of("facebook-event-search", "events", "results")
    event_url = event.get("url") or event.get("eventUrl")
    if event_url:
        tests.append(("facebook-event-details", "/v1/facebook/event-details", {"url": event_url}))
    else:
        print("!! no facebook event url")

    listing = first_of("facebook-marketplace-search", "listings", "results")
    listing_url = listing.get("url") or listing.get("listingUrl")
    if listing_url:
        tests.append(("facebook-marketplace-item", "/v1/facebook/marketplace-item", {"url": listing_url}))
    else:
        print("!! no marketplace listing url")

    pin = first_of("pinterest-search", "results", "pins")
    pin_url = pin.get("url") or pin.get("pinUrl")
    if pin_url:
        tests.append(("pinterest-pin-details", "/v1/pinterest/pin-details", {"url": pin_url}))
    else:
        print("!! no pinterest pin url")

    board = first_of("pinterest-user-boards", "boards")
    board_url = board.get("url") or board.get("boardUrl")
    if board_url:
        tests.append(("pinterest-board", "/v1/pinterest/board", {"url": board_url, "limit": 5}))
    else:
        print("!! no pinterest board url")

    return tests


def batch4_phase1() -> list[tuple[str, str, dict]]:
    return [
        ("rumble-search", "/v1/rumble/search", {"q": "space", "limit": 5}),
        ("rumble-channel-videos", "/v1/rumble/channel-videos", {"url": "https://rumble.com/c/Bongino", "limit": 5}),
        ("youtube-playlist", "/v1/youtube/playlist", {"url": "https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj", "limit": 5}),
        ("youtube-trending-shorts", "/v1/youtube/trending-shorts", {"limit": 10}),
        ("youtube-community-post-details", "/v1/youtube/community-post-details", {"url": "https://www.youtube.com/post/UgkxfMvMnSnV3Ww9HwAY2wFGmVevmhRaYAYO"}),
        ("youtube-video-sponsors", "/v1/youtube/video-sponsors", {"url": "https://www.youtube.com/watch?v=Wdjh81uH6FU"}),
        ("twitch-profile", "/v1/twitch/profile", {"url": "https://www.twitch.tv/shroud"}),
        ("twitch-user-videos", "/v1/twitch/user-videos", {"url": "https://www.twitch.tv/shroud", "limit": 5}),
        ("twitch-user-schedule", "/v1/twitch/user-schedule", {"url": "https://www.twitch.tv/criticalrole"}),
        ("twitch-clip", "/v1/twitch/clip", {"url": "https://www.twitch.tv/xqc", "limit": 10}),
        ("account-balance", "/v1/account/balance", {}),
        ("account-request-history", "/v1/account/request-history", {"limit": 5}),
        ("account-daily-usage", "/v1/account/daily-usage", {"days": 7}),
        ("account-most-used-routes", "/v1/account/most-used-routes", {"days": 30, "limit": 5}),
        ("instagram-basic-profile", "/v1/instagram/basic-profile", {"userId": "314216"}),
        ("instagram-trending-reels", "/v1/instagram/trending-reels", {"country": "United States", "limit": 10}),
        ("instagram-reels-by-audio-id", "/v1/instagram/reels-by-audio-id", {"audio_id": "27919946310946207", "limit": 5}),
        ("bluesky-profile", "/v1/bluesky/profile", {"url": "https://bsky.app/profile/jay.bsky.team"}),
        ("bluesky-user-posts", "/v1/bluesky/user-posts", {"url": "https://bsky.app/profile/jay.bsky.team", "limit": 5}),
        ("soundcloud-artist", "/v1/soundcloud/artist", {"url": "https://soundcloud.com/flume"}),
        ("soundcloud-artist-tracks", "/v1/soundcloud/artist-tracks", {"url": "https://soundcloud.com/flume", "limit": 5}),
        ("truth-social-profile", "/v1/truth-social/profile", {"url": "@realDonaldTrump"}),
        ("truth-social-user-posts", "/v1/truth-social/user-posts", {"url": "@realDonaldTrump", "limit": 5}),
        # International Kwai web model — actor expects kwai.com/@handle, not kuaishou.com/profile/<id>.
        ("kwai-profile", "/v1/kwai/profile", {"url": "https://www.kwai.com/@topfilmeseseriesnatv"}),
        ("kwai-user-posts", "/v1/kwai/user-posts", {"url": "https://www.kwai.com/@topfilmeseseriesnatv", "limit": 5}),
        ("reddit-post-transcript", "/v1/reddit/post-transcript", {"url": "https://www.reddit.com/r/space/comments/1umfd43/radiation_exposure_may_become_the_biggest/", "limit": 5}),
        ("tiktok-shop-products", "/v1/tiktok-shop/shop-products", {"url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079", "limit": 5}),
        ("linktree-page", "/v1/linktree/page", {"url": "https://linktr.ee/selenagomez"}),
        ("kick-clip", "/v1/kick/clip", {"url": "https://kick.com/xqc", "limit": 10}),
        ("amazon-shop-page", "/v1/amazon-shop/page", {"url": "https://www.amazon.com/sp?seller=A294P4X9EWVXLJ", "limit": 5}),
        ("komi-page", "/v1/komi/page", {"url": "https://komi.io/ksi"}),
        ("pillar-page", "/v1/pillar/page", {"url": "https://pillar.io/jayshetty"}),
        ("linkbio-page", "/v1/linkbio/page", {"url": "https://lnk.bio/charlidamelio"}),
        ("linkme-profile", "/v1/linkme/profile", {"url": "https://link.me/kevinhart"}),
    ]


def batch4_phase2(p1: dict[str, dict]) -> list[tuple[str, str, dict]]:
    tests: list[tuple[str, str, dict]] = []

    def first_of(slug: str, *list_keys: str) -> dict:
        body = p1.get(slug, {}).get("body") or {}
        d = body.get("data") or {}
        for key in list_keys:
            rows = d.get(key)
            if isinstance(rows, list) and rows:
                return next((r for r in rows if isinstance(r, dict)), {})
        return {}

    def rumble_video_url() -> str | None:
        for slug, keys in (("rumble-search", ("results", "videos")), ("rumble-channel-videos", ("videos",))):
            body = p1.get(slug, {}).get("body") or {}
            d = body.get("data") or {}
            for key in keys:
                for row in d.get(key) or []:
                    u = row.get("url") if isinstance(row, dict) else None
                    # Shorts pages lack og-meta/transcripts; stick to regular videos.
                    if u and "/shorts/" not in u:
                        return u
        return None

    video_url = rumble_video_url()
    if video_url:
        tests.append(("rumble-video-details", "/v1/rumble/video-details", {"url": video_url}))
        tests.append(("rumble-comments", "/v1/rumble/comments", {"url": video_url, "limit": 5}))
    else:
        print("!! no rumble video url")

    body = p1.get("soundcloud-artist-tracks", {}).get("body") or {}
    sc_tracks = (body.get("data") or {}).get("tracks") or []
    track = next((t for t in sc_tracks if isinstance(t, dict) and t.get("title")), {})
    track_url = track.get("url") or track.get("permalink")
    if track_url:
        tests.append(("soundcloud-track", "/v1/soundcloud/track", {"url": track_url}))
    else:
        print("!! no soundcloud track url")

    bsky_post = first_of("bluesky-user-posts", "posts")
    bsky_url = bsky_post.get("url")
    if bsky_url:
        tests.append(("bluesky-post-details", "/v1/bluesky/post-details", {"url": bsky_url}))
    else:
        print("!! no bluesky post url")

    truth_post = first_of("truth-social-user-posts", "posts")
    truth_url = truth_post.get("url") or truth_post.get("id")
    if truth_url:
        tests.append(("truth-social-post", "/v1/truth-social/post", {"url": truth_url}))
    else:
        print("!! no truth social post url")

    kwai_post = first_of("kwai-user-posts", "posts")
    kwai_url = kwai_post.get("url") or kwai_post.get("postUrl")
    if kwai_url:
        tests.append(("kwai-post", "/v1/kwai/post", {"url": kwai_url}))
    else:
        print("!! no kwai post url")

    return tests


def batch4b_phase1() -> list[tuple[str, str, dict]]:
    """Retry set for the endpoints that failed in the first batch-4 pass."""
    return [
        ("rumble-channel-videos", "/v1/rumble/channel-videos", {"url": "https://rumble.com/c/Bongino", "limit": 5}),
        ("soundcloud-artist-tracks", "/v1/soundcloud/artist-tracks", {"url": "https://soundcloud.com/flume", "limit": 5}),
        ("reddit-post-transcript", "/v1/reddit/post-transcript", {"url": "https://www.reddit.com/r/space/comments/1umfd43/radiation_exposure_may_become_the_biggest/", "limit": 5}),
        ("instagram-trending-reels", "/v1/instagram/trending-reels", {"country": "United States", "limit": 10}),
    ]


def batch_fix_phase1() -> list[tuple[str, str, dict]]:
    """Recapture endpoints that failed due to bad params / flaky upstream."""
    return [
        ("tiktok-search-suggestions", "/v1/tiktok/search-suggestions", {"q": "makeup", "country": "US", "language": "en-US", "limit": 5}),
        ("instagram-basic-profile", "/v1/instagram/basic-profile", {"userId": "314216"}),
        ("kwai-profile", "/v1/kwai/profile", {"url": "https://www.kwai.com/@topfilmeseseriesnatv"}),
        ("kwai-user-posts", "/v1/kwai/user-posts", {"url": "https://www.kwai.com/@topfilmeseseriesnatv", "limit": 5}),
    ]


def batch_fix_phase2(p1: dict[str, dict]) -> list[tuple[str, str, dict]]:
    body = p1.get("kwai-user-posts", {}).get("body") or {}
    posts = (body.get("data") or {}).get("posts") or []
    post = next((p for p in posts if isinstance(p, dict) and (p.get("url") or p.get("postUrl"))), None)
    if not post:
        print("!! no kwai post url")
        return []
    return [("kwai-post", "/v1/kwai/post", {"url": post.get("url") or post.get("postUrl")})]


def batch5_phase1() -> list[tuple[str, str, dict]]:
    """Refresh set for the response-enrichment pass (reddit threading, link-in-bio
    socials/email, twitch/rumble metadata, pinterest pidgets, soundcloud, bluesky,
    truth social, github, twitter profile)."""
    return [
        ("reddit-post-comments", "/v1/reddit/post-comments", {"url": "https://www.reddit.com/r/space/comments/1umfd43/radiation_exposure_may_become_the_biggest/", "limit": 5}),
        ("reddit-post-transcript", "/v1/reddit/post-transcript", {"url": "https://www.reddit.com/r/space/comments/1umfd43/radiation_exposure_may_become_the_biggest/", "limit": 5}),
        ("komi-page", "/v1/komi/page", {"url": "https://komi.io/ksi"}),
        ("pillar-page", "/v1/pillar/page", {"url": "https://pillar.io/jayshetty"}),
        ("linkbio-page", "/v1/linkbio/page", {"url": "https://lnk.bio/charlidamelio"}),
        ("linkme-profile", "/v1/linkme/profile", {"url": "https://link.me/kevinhart"}),
        ("linktree-page", "/v1/linktree/page", {"url": "https://linktr.ee/selenagomez"}),
        ("twitch-profile", "/v1/twitch/profile", {"url": "https://www.twitch.tv/shroud"}),
        ("twitch-user-videos", "/v1/twitch/user-videos", {"url": "https://www.twitch.tv/shroud", "limit": 5}),
        ("twitch-clip", "/v1/twitch/clip", {"url": "https://www.twitch.tv/xqc", "limit": 10}),
        ("rumble-channel-videos", "/v1/rumble/channel-videos", {"url": "https://rumble.com/c/Bongino", "limit": 5}),
        ("pinterest-pin-details", "/v1/pinterest/pin-details", {"url": "https://www.pinterest.com/pin/422281212828530/"}),
        ("soundcloud-artist", "/v1/soundcloud/artist", {"url": "https://soundcloud.com/flume"}),
        ("soundcloud-artist-tracks", "/v1/soundcloud/artist-tracks", {"url": "https://soundcloud.com/flume", "limit": 5}),
        ("bluesky-profile", "/v1/bluesky/profile", {"url": "https://bsky.app/profile/jay.bsky.team"}),
        ("bluesky-user-posts", "/v1/bluesky/user-posts", {"url": "https://bsky.app/profile/jay.bsky.team", "limit": 5}),
        ("truth-social-profile", "/v1/truth-social/profile", {"url": "@realDonaldTrump"}),
        ("truth-social-user-posts", "/v1/truth-social/user-posts", {"url": "@realDonaldTrump", "limit": 5}),
        ("github-user", "/v1/github/user", {"username": "torvalds"}),
        ("github-repositories", "/v1/github/repositories", {"username": "torvalds", "limit": 5}),
        ("github-repository", "/v1/github/repository", {"repo": "torvalds/linux"}),
        ("github-trending-repositories", "/v1/github/trending-repositories", {"limit": 5}),
        ("twitter-profile", "/v1/twitter/profile", {"url": "https://x.com/nasa"}),
    ]


def batch5_phase2(p1: dict[str, dict]) -> list[tuple[str, str, dict]]:
    tests: list[tuple[str, str, dict]] = []

    def first_of(slug: str, *list_keys: str) -> dict:
        body = p1.get(slug, {}).get("body") or {}
        d = body.get("data") or {}
        for key in list_keys:
            rows = d.get(key)
            if isinstance(rows, list) and rows:
                return next((r for r in rows if isinstance(r, dict)), {})
        return {}

    video = first_of("rumble-channel-videos", "videos")
    video_url = video.get("url")
    if video_url and "/shorts/" not in video_url:
        tests.append(("rumble-video-details", "/v1/rumble/video-details", {"url": video_url}))
        tests.append(("rumble-comments", "/v1/rumble/comments", {"url": video_url, "limit": 5}))
    else:
        print("!! no rumble video url")

    track = first_of("soundcloud-artist-tracks", "tracks")
    track_url = track.get("url")
    if track_url:
        tests.append(("soundcloud-track", "/v1/soundcloud/track", {"url": track_url}))
    else:
        print("!! no soundcloud track url")

    bsky_post = first_of("bluesky-user-posts", "posts")
    if bsky_post.get("url"):
        tests.append(("bluesky-post-details", "/v1/bluesky/post-details", {"url": bsky_post["url"]}))
    else:
        print("!! no bluesky post url")

    truth_post = first_of("truth-social-user-posts", "posts")
    truth_url = truth_post.get("url") or truth_post.get("id")
    if truth_url:
        tests.append(("truth-social-post", "/v1/truth-social/post", {"url": truth_url}))
    else:
        print("!! no truth social post url")

    return tests


def batch_nullfix_phase1() -> list[tuple[str, str, dict]]:
    """Recapture endpoints whose normalizers were fixed for always-null fields."""
    return [
        ("github-repository", "/v1/github/repository", {"repo": "https://github.com/torvalds/linux"}),
        ("github-repositories", "/v1/github/repositories", {"username": "torvalds", "limit": 5}),
        ("github-trending-repositories", "/v1/github/trending-repositories", {"q": "stars:>1000 language:python", "limit": 5}),
        ("twitch-clip", "/v1/twitch/clip", {"url": "https://www.twitch.tv/xqc/clip/EnergeticEmpathicElephantJKanStyle-0sOlvgAod9mDhCw4"}),
        ("twitch-profile", "/v1/twitch/profile", {"url": "https://www.twitch.tv/shroud"}),
        ("twitch-user-videos", "/v1/twitch/user-videos", {"url": "https://www.twitch.tv/shroud", "limit": 5}),
        ("tiktok-live", "/v1/tiktok/live", {"url": "https://www.tiktok.com/@espn"}),
        ("tiktok-live-info", "/v1/tiktok/live-info", {"url": "https://www.tiktok.com/@espn"}),
        ("tiktok-popular-creators", "/v1/tiktok/popular-creators", {"country": "US", "limit": 5}),
        ("tiktok-music-posts", "/v1/tiktok/music-posts", {"url": "https://www.tiktok.com/music/original-sound-7646812079113898783", "limit": 5}),
        ("pinterest-pin-details", "/v1/pinterest/pin-details", {"url": "https://www.pinterest.com/pin/422281212828530/"}),
        ("pinterest-user-boards", "/v1/pinterest/user-boards", {"url": "https://www.pinterest.com/potterybarn/", "limit": 5}),
        ("pinterest-user-pins", "/v1/pinterest/user-pins", {"url": "https://www.pinterest.com/potterybarn/", "limit": 5}),
        ("pinterest-board", "/v1/pinterest/board", {"url": "https://www.pinterest.com/potterybarn/indigo-blues-lookbook/", "limit": 5}),
        ("youtube-playlist-videos", "/v1/youtube/playlist-videos", {"url": "https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj", "limit": 5}),
        ("youtube-trending-shorts", "/v1/youtube/trending-shorts", {"q": "trending", "limit": 5}),
        ("youtube-shorts-stats", "/v1/youtube/shorts/video-details", {"url": "https://www.youtube.com/shorts/DXVHmGoCTco"}),
        (
            "youtube-comment-replies",
            "/v1/youtube/comment-replies",
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "comment_id": "Ugzge340dBgB75hWBm54AaABAg",
                "limit": 10,
            },
        ),
        ("facebook-marketplace-search", "/v1/facebook/marketplace-search", {"q": "desk chair", "location": "Austin, TX", "limit": 5, "details": "true"}),
        ("facebook-event-details", "/v1/facebook/event-details", {"url": "https://www.facebook.com/events/2905221439853710/"}),
        ("threads-search-users", "/v1/threads/search-users", {"q": "tech", "limit": 5}),
        ("rumble-channel-videos", "/v1/rumble/channel-videos", {"url": "https://rumble.com/c/Bongino", "limit": 5}),
        ("rumble-video-details", "/v1/rumble/video-details", {"url": "https://rumble.com/v7cv2cc-now-i-can-finally-talk-about-it-ep.-2555-07172026.html"}),
        ("linkme-profile", "/v1/linkme/profile", {"url": "https://link.me/kevinhart"}),
        ("pillar-page", "/v1/pillar/page", {"url": "https://pillar.io/jayshetty"}),
        ("amazon-shop-page", "/v1/amazon-shop/page", {"url": "https://www.amazon.com/sp?seller=A294P4X9EWVXLJ", "limit": 5}),
        ("tiktok-shop-product-details", "/v1/tiktok-shop/product-details", {"url": "https://www.tiktok.com/shop/pdp/1731743608991158724"}),
        ("tiktok-shop-search", "/v1/tiktok-shop/shop-search", {"q": "phone case", "limit": 5}),
        ("tiktok-shop-products", "/v1/tiktok-shop/shop-products", {"url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079", "limit": 5}),
        ("tiktok-shop-user-showcase", "/v1/tiktok-shop/user-showcase", {"username": "jeffreestar", "limit": 5}),
    ]


BATCHES = {
    "batch1": (batch1_phase1, batch1_phase2),
    "batch2": (batch2_phase1, batch2_phase2),
    "batch3": (batch3_phase1, batch3_phase2),
    "batch4": (batch4_phase1, batch4_phase2),
    "batch_fix": (batch_fix_phase1, batch_fix_phase2),
    "batch4b": (batch4b_phase1, batch4_phase2),
    "batch4c": (
        lambda: [
            ("rumble-search", "/v1/rumble/search", {"q": "space", "limit": 5}),
            ("rumble-channel-videos", "/v1/rumble/channel-videos", {"url": "https://rumble.com/c/Bongino", "limit": 5}),
        ],
        batch4_phase2,
    ),
    "batch4d": (
        lambda: [
            ("kick-clip", "/v1/kick/clip", {"url": "https://kick.com/xqc", "limit": 10}),
            ("youtube-community-post-details", "/v1/youtube/community-post-details", {"url": "https://www.youtube.com/post/UgkxfMvMnSnV3Ww9HwAY2wFGmVevmhRaYAYO"}),
        ],
        lambda p1: [],
    ),
    "batch5": (batch5_phase1, batch5_phase2),
    # Actor swaps: reddit comment scores (clearpath), twitch schedule
    # (easyapi), tiktok shop reviews (web_wanderer). The reddit post is an
    # older thread so comment scores are public (fresh posts hide them).
    "batch6": (
        lambda: [
            ("reddit-post-details", "/v1/reddit/post-details", {"url": "https://www.reddit.com/r/Astronomy/comments/1ldt0qj/pope_leo_james_webb_telescope_shows_us_what_the/"}),
            ("reddit-post-comments", "/v1/reddit/post-comments", {"url": "https://www.reddit.com/r/Astronomy/comments/1ldt0qj/pope_leo_james_webb_telescope_shows_us_what_the/", "limit": 5}),
            ("reddit-post-transcript", "/v1/reddit/post-transcript", {"url": "https://www.reddit.com/r/Astronomy/comments/1ldt0qj/pope_leo_james_webb_telescope_shows_us_what_the/", "limit": 5}),
            ("twitch-user-schedule", "/v1/twitch/user-schedule", {"url": "https://www.twitch.tv/criticalrole"}),
            ("tiktok-shop-product-reviews", "/v1/tiktok-shop/product-reviews", {"url": "https://www.tiktok.com/shop/pdp/1731962298839634826", "limit": 5}),
        ],
        lambda p1: [],
    ),
    "batch_nullfix": (batch_nullfix_phase1, lambda _p1: []),
}


async def main() -> None:
    batch = sys.argv[1] if len(sys.argv) > 1 else "batch1"
    phase1_fn, phase2_fn = BATCHES[batch]

    sb = get_supabase()
    # Prefer a balance with enough credits; list_users()[0] is often empty.
    bals = (
        sb.table("credit_balances")
        .select("user_id,subscription_credits,topup_credits")
        .execute()
    )
    cands = [
        b
        for b in (bals.data or [])
        if (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0) > 200
    ]
    cands.sort(
        key=lambda b: (b.get("subscription_credits") or 0) + (b.get("topup_credits") or 0),
        reverse=True,
    )
    if not cands:
        raise SystemExit("No credit_balances with >200 credits available for capture")
    user_id = cands[0]["user_id"]
    available = (cands[0].get("subscription_credits") or 0) + (cands[0].get("topup_credits") or 0)
    print(f"Target: {BASE} | user: {user_id} | credits~={available}")
    plain, key_hash, prefix = generate_api_key()
    ins = sb.table("api_keys").insert(
        {"user_id": user_id, "key_hash": key_hash, "key_prefix": prefix, "name": f"capture-{batch}"}
    ).execute()
    key_id = ins.data[0]["id"]

    # Heavy Apify batches (nullfix) need low concurrency to avoid 429s / timeouts.
    conc = 3 if batch == "batch_nullfix" else 0
    try:
        async with httpx.AsyncClient(headers={"Authorization": f"Bearer {plain}"}) as client:
            print("--- phase 1")
            p1 = await run_phase(client, phase1_fn(), concurrency=conc)
            print("--- phase 2")
            p2 = await run_phase(client, phase2_fn(p1), concurrency=conc)
    finally:
        sb.table("api_keys").delete().eq("id", key_id).execute()
        print(f"Revoked temp key {prefix}…")

    snap_path = BACKEND / "api_snapshots.json"
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    updated = []
    for slug, res in {**p1, **p2}.items():
        body = res["body"]
        if not (200 <= res["status"] < 300) or not isinstance(body, dict) or not isinstance(body.get("data"), dict):
            continue
        # Don't clobber a populated example with a transiently-empty run.
        if body["data"].get("totalReturned") == 0 and (snap.get(slug) or {}).get("data", {}).get("totalReturned"):
            print(f"skip {slug}: empty result, keeping existing snapshot")
            continue
        snap[slug] = {
            "ok": True,
            "status": res["status"],
            "credits": (body.get("meta") or {}).get("creditsUsed"),
            "data": _truncate(body["data"]),
        }
        updated.append(slug)
    snap_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("snapshot updated:", ", ".join(sorted(updated)) or "(none)")

    import subprocess

    subprocess.run([sys.executable, "gen_examples.py"], cwd=BACKEND, check=True)


if __name__ == "__main__":
    asyncio.run(main())
