"""Offline smoke test for the NEWLY ADDED endpoints.

Runs fully in-process via FastAPI's TestClient. It does NOT touch Supabase,
Redis, OpenAI or Apify - every external boundary is monkeypatched with
realistic fixtures so we can verify, deterministically and for free:

  1. each new route is registered and reachable
  2. query-param validation behaves
  3. the router builds the CORRECT Apify actor input
  4. the raw actor output is normalized into the expected response shape

Run:  python smoke_new_endpoints.py     (from the backend/ directory)
"""

from __future__ import annotations

import os

# Ensure settings can load even if .env lacks a field (safe dummies).
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "dummy")
os.environ.setdefault("SUPABASE_ANON_KEY", "dummy")
os.environ.setdefault("APIFY_TOKEN", "dummy")
os.environ.setdefault("OPENAI_API_KEY", "dummy")

from fastapi.testclient import TestClient  # noqa: E402

from app.core import credits as credits_mod  # noqa: E402
from app.core.auth import ApiCaller, require_api_key  # noqa: E402
from app.services import apify_client  # noqa: E402
from app.services import cached_runner  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures (shaped like the real Apify actor outputs)
# ---------------------------------------------------------------------------
PARENT_COMMENT_ID = "7300000000000000001"

TIKTOK_VIDEOS = [
    {
        "id": "7311111111111111111",
        "text": "having fun #comedy",
        "webVideoUrl": "https://www.tiktok.com/@creator/video/7311111111111111111",
        "createTimeISO": "2024-05-01T10:00:00.000Z",
        "authorMeta": {"name": "creator", "nickName": "Creator", "fans": 12000, "verified": True, "avatar": "http://img/a.jpg"},
        "playCount": 50000, "diggCount": 2200, "commentCount": 140, "shareCount": 90,
        "videoMeta": {"duration": 15, "coverUrl": "http://img/cover.jpg"},
        "videoUrl": "http://cdn/video.mp4",
        "hashtags": [{"name": "comedy"}],
        "musicMeta": {"musicName": "Funny Sound"},
    }
]

TIKTOK_COMMENTS = [
    {"cid": PARENT_COMMENT_ID, "text": "top level comment", "user": {"uniqueId": "alice"}, "diggCount": 12, "createTimeISO": "2024-05-02T00:00:00Z"},
    {"cid": "r1", "text": "first reply", "repliesToId": PARENT_COMMENT_ID, "user": {"uniqueId": "bob"}, "diggCount": 3, "createTimeISO": "2024-05-02T01:00:00Z"},
    {"cid": "r2", "text": "second reply", "repliesToId": PARENT_COMMENT_ID, "user": {"uniqueId": "carol"}, "diggCount": 1, "createTimeISO": "2024-05-02T02:00:00Z"},
    {"cid": "r3", "text": "reply to other comment", "repliesToId": "9999", "user": {"uniqueId": "dave"}, "diggCount": 0, "createTimeISO": "2024-05-02T03:00:00Z"},
]

TIKTOK_USERS = [
    {"isSummary": True, "mode": "followers"},  # summary row -> must be filtered out
    {"username": "follower_one", "nickname": "Follower One", "signature": "bio here", "profileUrl": "https://www.tiktok.com/@follower_one", "followerCount": 500, "verified": False, "avatar": "http://img/f1.jpg"},
    {"username": "follower_two", "nickname": "Follower Two", "followerCount": 88, "verified": True, "avatar": "http://img/f2.jpg"},
]

IG_POSTS = [
    {
        "url": "https://www.instagram.com/p/CABC123/", "id": "CABC123",
        "caption": "tagged/music post", "timestamp": "2024-05-01T12:00:00Z",
        "displayUrl": "http://img/ig.jpg", "videoUrl": "http://cdn/ig.mp4",
        "ownerUsername": "natgeo", "ownerFullName": "Nat Geo",
        "likesCount": 4200, "commentsCount": 88, "videoViewCount": 99000,
        "hashtags": ["nature"],
    }
]

YT_ITEMS = [
    {
        "url": "https://www.youtube.com/watch?v=abc12345678", "title": "Sample item",
        "date": "2024-04-01", "viewCount": 150000, "duration": 45,
        "thumbnailUrl": "http://img/yt.jpg", "channelName": "Some Channel",
    }
]

# Records every Apify call so we can print the input that each route built.
CALLS: list[dict] = []


async def fake_run_actor_sync(self, actor_id, run_input, max_items=None):
    CALLS.append({"actor": actor_id, "input": run_input, "max_items": max_items})
    if "maxRepliesPerComment" in run_input or "comments" in actor_id:
        return TIKTOK_COMMENTS
    if "mode" in run_input:  # coregent followers/following scraper
        return TIKTOK_USERS
    if "musics" in run_input:  # clockworks sound scraper
        return TIKTOK_VIDEOS
    if "tagged" in actor_id:  # instagram tagged scraper
        return IG_POSTS
    if "youtube" in actor_id or "startUrls" in run_input:  # youtube search/channel
        return YT_ITEMS
    if "directUrls" in run_input or "username" in run_input:  # IG music-posts / others
        return IG_POSTS
    if "profiles" in run_input:  # tiktok channel-posts
        return TIKTOK_VIDEOS
    return []


# ---------------------------------------------------------------------------
# Patch every external boundary
# ---------------------------------------------------------------------------
apify_client.ApifyClient.run_actor_sync = fake_run_actor_sync


async def _cache_get(key):
    return None


async def _cache_set(key, value, ttl=None):
    return None


cached_runner.cache_get = _cache_get
cached_runner.cache_set = _cache_set

credits_mod.deduct_credits = lambda user_id, amount: True
credits_mod.log_request = lambda **kwargs: None


def _fake_caller() -> ApiCaller:
    return ApiCaller(
        user_id="00000000-0000-0000-0000-000000000000",
        api_key_id="test",
        plan="business",
        subscription_credits=10_000,
        topup_credits=0,
    )


from app.main import app  # noqa: E402

app.dependency_overrides[require_api_key] = _fake_caller
client = TestClient(app)

TIKTOK_VIDEO = "https://www.tiktok.com/@creator/video/7311111111111111111"
TIKTOK_PROFILE = "https://www.tiktok.com/@creator"
TIKTOK_MUSIC = "https://www.tiktok.com/music/Funny-Sound-6889520563052645121"
IG_PROFILE = "https://www.instagram.com/natgeo/"
IG_MUSIC = "https://www.instagram.com/reels/audio/123456789/"
YT_CHANNEL = "https://www.youtube.com/@MrBeast"

# name, path, params, expected data key, expected item count
TESTS = [
    ("TT channel-posts", "/v1/tiktok/channel-posts", {"url": TIKTOK_PROFILE, "limit": 5}, "posts", 1),
    ("TT comment-replies", "/v1/tiktok/comment-replies", {"url": TIKTOK_VIDEO, "comment_id": PARENT_COMMENT_ID, "limit": 10}, "replies", 2),
    ("TT user-followers", "/v1/tiktok/user-followers", {"url": TIKTOK_PROFILE, "limit": 10}, "followers", 2),
    ("TT user-followings", "/v1/tiktok/user-followings", {"url": TIKTOK_PROFILE, "limit": 10}, "followings", 2),
    ("TT music-posts", "/v1/tiktok/music-posts", {"url": TIKTOK_MUSIC, "limit": 5}, "posts", 1),
    ("IG tagged-posts", "/v1/instagram/tagged-posts", {"url": IG_PROFILE, "limit": 5}, "posts", 1),
    ("IG music-posts", "/v1/instagram/music-posts", {"url": IG_MUSIC, "limit": 5}, "posts", 1),
    ("YT channel-shorts", "/v1/youtube/channel-shorts", {"url": YT_CHANNEL, "limit": 5}, "shorts", 1),
    ("YT channel-streams", "/v1/youtube/channel-streams", {"url": YT_CHANNEL, "limit": 5}, "streams", 1),
    ("YT hashtag-search", "/v1/youtube/hashtag-search", {"q": "#gaming", "limit": 5}, "results", 1),
]


def run() -> None:
    print("\n{:<22} {:<5} {:<5} DETAIL".format("NAME", "RES", "CODE"))
    print("-" * 100)
    passed = 0
    last_code = 0
    for name, path, params, key, expected_n in TESTS:
        try:
            r = client.get(path, params=params)
            last_code = r.status_code
            body = r.json()
            data = body.get("data", {})
            items = data.get(key)
            ok = (
                r.status_code == 200
                and body.get("success") is True
                and isinstance(items, list)
                and len(items) == expected_n
            )
            detail = "{}={} (want {})".format(
                key, len(items) if isinstance(items, list) else items, expected_n
            )
        except Exception as e:  # noqa: BLE001
            ok = False
            detail = "EXCEPTION: {}".format(e)
        passed += ok
        print("{:<22} {:<5} {:<5} {}".format(name, "PASS" if ok else "FAIL", last_code, detail))

    print("-" * 100)
    print("{}/{} passed\n".format(passed, len(TESTS)))

    print("Validation checks (negative cases):")
    bad_profile = client.get("/v1/tiktok/channel-posts", params={"url": "https://example.com/x"})
    print("  invalid TikTok profile -> {} (want 400)".format(bad_profile.status_code))
    missing_cid = client.get("/v1/tiktok/comment-replies", params={"url": TIKTOK_VIDEO})
    print("  missing comment_id     -> {} (want 422)".format(missing_cid.status_code))

    print("\nApify inputs built by each route:")
    for c in CALLS:
        print("  {:<48} {}".format(c["actor"], c["input"]))


if __name__ == "__main__":
    run()
