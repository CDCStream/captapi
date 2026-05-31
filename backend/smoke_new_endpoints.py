"""Offline smoke tests for ALL new endpoints (post-actor-upgrade).

Mocks every external boundary (Apify, Redis, Supabase) so the test is free,
deterministic, and runs in-process via FastAPI TestClient.

Actors tested:
  - clockworks/tiktok-followers-scraper  (followers + followings)
  - coregent/tiktok-comment-scraper      (comment-replies)
  - clockworks/tiktok-sound-scraper      (music-posts)
  - clockworks/tiktok-scraper            (channel-posts)
  - apify/instagram-tagged-scraper       (ig tagged-posts)
  - streamers/youtube-channel-scraper    (yt shorts, streams)
  - streamers/youtube-scraper            (yt hashtag-search)

Run:  python smoke_new_endpoints.py   (from the backend/ directory)
"""

from __future__ import annotations

import os

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "dummy")
os.environ.setdefault("SUPABASE_ANON_KEY", "dummy")
os.environ.setdefault("APIFY_TOKEN", "dummy")
os.environ.setdefault("OPENAI_API_KEY", "dummy")

from fastapi.testclient import TestClient  # noqa: E402
from app.core import credits as credits_mod  # noqa: E402
from app.core.auth import ApiCaller, require_api_key  # noqa: E402
from app import services as _svc  # noqa: E402
from app.services import apify_client as apify_mod  # noqa: E402
from app.services import cached_runner  # noqa: E402

# ------------------------------------------------------------------
# Fixtures (shaped like the real Apify actor outputs)
# ------------------------------------------------------------------
PARENT_COMMENT_ID = "7300000000000000001"

# clockworks/tiktok-scraper output items
TIKTOK_VIDEOS = [
    {
        "id": "7111111111111111111",
        "text": "having fun #comedy",
        "webVideoUrl": "https://www.tiktok.com/@creator/video/7111111111111111111",
        "createTimeISO": "2024-05-01T00:00:00.000Z",
        "authorMeta": {"name": "creator", "nickName": "Creator", "fans": 12000, "verified": True, "avatar": "http://img/a.jpg"},
        "playCount": 5000, "diggCount": 220, "commentCount": 10, "shareCount": 9,
        "videoMeta": {"duration": 15, "coverUrl": "http://img/cover.jpg"},
        "videoUrl": "http://cdn/video.mp4",
        "hashtags": [{"name": "comedy"}],
        "musicMeta": {"musicName": "Funny Sound"},
    }
]

# coregent/tiktok-comment-scraper output — reply rows carry parentCommentId
TIKTOK_COMMENT_ITEMS = [
    # top-level comment (no parentCommentId)
    {
        "commentId": PARENT_COMMENT_ID,
        "commentText": "top level comment",
        "authorUsername": "alice",
        "likeCount": 12,
        "replyCount": 2,
        "createTime": "2024-05-02T00:00:00.000Z",
    },
    # reply 1
    {
        "parentCommentId": PARENT_COMMENT_ID,
        "replyId": "r1",
        "replyText": "first reply",
        "replyAuthorUsername": "bob",
        "replyAuthorNickname": "Bob",
        "replyLikeCount": 3,
        "replyCreateTime": "2024-05-02T01:00:00.000Z",
        "replyAuthorVerified": False,
        "replyAuthorAvatar": "http://img/f1.jpg",
    },
    # reply 2
    {
        "parentCommentId": PARENT_COMMENT_ID,
        "replyId": "r2",
        "replyText": "second reply",
        "replyAuthorUsername": "carol",
        "replyAuthorNickname": "Carol",
        "replyLikeCount": 1,
        "replyCreateTime": "2024-05-02T02:00:00.000Z",
        "replyAuthorVerified": False,
        "replyAuthorAvatar": "http://img/f2.jpg",
    },
    # unrelated reply (should NOT appear in results)
    {
        "parentCommentId": "9999",
        "replyId": "r3",
        "replyText": "reply to different comment",
        "replyAuthorUsername": "dave",
        "replyLikeCount": 0,
        "replyCreateTime": "2024-05-02T03:00:00.000Z",
    },
]

# clockworks/tiktok-followers-scraper output
# connectionType distinguishes followers from followings
TIKTOK_CONNECTIONS = [
    {
        "authorMeta": {
            "name": "follower_one",
            "nickName": "Follower One",
            "signature": "bio here",
            "profileUrl": "https://www.tiktok.com/@follower_one",
            "fans": 500,
            "following": 200,
            "verified": False,
            "avatar": "http://img/f1.jpg",
        },
        "connectionType": "follower",
        "connectionDescription": "follower_one is a follower of creator",
    },
    {
        "authorMeta": {
            "name": "follower_two",
            "nickName": "Follower Two",
            "signature": "",
            "profileUrl": "https://www.tiktok.com/@follower_two",
            "fans": 88,
            "following": 50,
            "verified": True,
            "avatar": "http://img/f2.jpg",
        },
        "connectionType": "follower",
        "connectionDescription": "follower_two is a follower of creator",
    },
    {
        "authorMeta": {
            "name": "following_one",
            "nickName": "Following One",
            "signature": "followed account",
            "profileUrl": "https://www.tiktok.com/@following_one",
            "fans": 9000,
            "following": 300,
            "verified": True,
            "avatar": "http://img/fo1.jpg",
        },
        "connectionType": "following",
        "connectionDescription": "creator follows following_one",
    },
]

# clockworks/tiktok-sound-scraper output
TIKTOK_MUSIC_ITEMS = TIKTOK_VIDEOS  # same shape

# apify/instagram-tagged-scraper output
IG_TAGGED = [
    {
        "url": "https://www.instagram.com/p/CAB1C23/",
        "id": "CAB1C23",
        "caption": "tagged/music post",
        "timestamp": "2024-05-01T12:00:00.000Z",
        "displayUrl": "http://img/ig.jpg",
        "videoUrl": "http://cdn/ig.mp4",
        "ownerUsername": "natgeo",
        "ownerFullName": "Nat Geo",
        "likesCount": 2400,
        "commentsCount": 88,
        "videoViewCount": 99000,
        "hashtags": ["nature"],
    }
]

# streamers/youtube-channel-scraper / youtube-scraper output
YT_ITEMS = [
    {
        "url": "https://www.youtube.com/watch?v=abc1234567",
        "title": "Sample item",
        "date": "2024-04-01",
        "viewCount": 15000,
        "duration": 45,
        "thumbnailUrl": "http://img/yt.jpg",
        "channelName": "Some Channel",
    }
]

# ------------------------------------------------------------------
# Record every Apify call so we can print what each route built
# ------------------------------------------------------------------
CALLS: list[dict] = []


async def fake_run_actor_sync(self, actor_id, run_input, max_items=None):
    CALLS.append({"actor": actor_id, "input": run_input, "max_items": max_items})
    # Route fixture based on actor id
    if "comment-scraper" in actor_id and "comment-replies" not in actor_id.lower():
        # coregent/tiktok-comment-scraper
        if "comment-scraper" in actor_id:
            return TIKTOK_COMMENT_ITEMS
    if "followers-scraper" in actor_id:
        return TIKTOK_CONNECTIONS
    if "sound-scraper" in actor_id:
        return TIKTOK_MUSIC_ITEMS
    if "instagram-tagged" in actor_id:
        return IG_TAGGED
    if "youtube" in actor_id or "startUrls" in run_input:
        return YT_ITEMS
    if "profiles" in run_input:
        return TIKTOK_VIDEOS
    if "postURLs" in run_input or "videoUrls" in run_input:
        return TIKTOK_COMMENT_ITEMS
    return TIKTOK_VIDEOS


# ------------------------------------------------------------------
# Patch every external boundary
# ------------------------------------------------------------------
apify_mod.ApifyClient.run_actor_sync = fake_run_actor_sync

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
        user_id="00000000-00-00-00-000000000000",
        api_key_id="test",
        plan="business",
        subscription_credits=1000000,
        topup_credits=0,
    )


from app.main import app  # noqa: E402
app.dependency_overrides[require_api_key] = _fake_caller
client = TestClient(app)

TIKTOK_PROFILE = "https://www.tiktok.com/@creator"
TIKTOK_VIDEO   = "https://www.tiktok.com/@creator/video/7111111111111111111"
TIKTOK_MUSIC   = "https://www.tiktok.com/music/Funny-Sound-688950256305264151214"
IG_PROFILE     = "https://www.instagram.com/natgeo/"
IG_MUSIC       = "https://www.instagram.com/reels/audio/1234567890/"
YT_CHANNEL     = "https://www.youtube.com/@MrBeast"

TESTS = [
    ("TT channel-posts",      "/v1/tiktok/channel-posts",      {"url": TIKTOK_PROFILE, "limit": 5}, "posts", 1),
    ("TT comment-replies",    "/v1/tiktok/comment-replies",    {"url": TIKTOK_VIDEO, "comment_id": PARENT_COMMENT_ID, "limit": 10}, "replies", 2),
    ("TT user-followers",     "/v1/tiktok/user-followers",     {"url": TIKTOK_PROFILE, "limit": 5}, "followers", 2),
    ("TT user-followings",    "/v1/tiktok/user-followings",    {"url": TIKTOK_PROFILE, "limit": 5}, "followings", 1),
    ("TT music-posts",        "/v1/tiktok/music-posts",        {"url": TIKTOK_MUSIC, "limit": 5}, "posts", 1),
    ("IG tagged-posts",       "/v1/instagram/tagged-posts",    {"url": IG_PROFILE, "limit": 5}, "posts", 1),
    ("IG music-posts",        "/v1/instagram/music-posts",     {"url": IG_MUSIC, "limit": 5}, "posts", 1),
    ("YT channel-shorts",     "/v1/youtube/channel-shorts",    {"url": YT_CHANNEL, "limit": 5}, "shorts", 1),
    ("YT channel-streams",    "/v1/youtube/channel-streams",   {"url": YT_CHANNEL, "limit": 5}, "streams", 1),
    ("YT hashtag-search",     "/v1/youtube/hashtag-search",    {"q": "#gaming", "limit": 5}, "results", 1),
]


def run() -> None:
    print(f"\n{'':22} {'RES':>3} {'CODE':>5} DETAIL")
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
            detail = f"(want {key}[{expected_n}], got {key}[{len(items) if isinstance(items, list) else '?'}])"
        except Exception as e:
            ok = False
            detail = f"EXCEPTION: {e}"
        print(f"{name:<22} {'RES':>3} {'PASS' if ok else 'FAIL':>5} {last_code}  {detail}")
        passed += ok

    print("-" * 100)
    print(f"\n{passed}/{len(TESTS)} passed\n")

    print("\nValidation checks (negative cases):")
    bad_profile = client.get("/v1/tiktok/channel-posts", params={"url": "https://example.com/x"})
    print(f"  invalid TikTok profile -> {bad_profile.status_code} (want 400)")
    missing_cid = client.get("/v1/tiktok/comment-replies", params={"url": TIKTOK_VIDEO})
    print(f"  missing comment_id      -> {missing_cid.status_code} (want 422)")

    print("\nApify inputs built by each route:")
    for c in CALLS:
        print(f"  {c['actor']:<48} {c['input']}")


if __name__ == "__main__":
    run()