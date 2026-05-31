import asyncio, json, time, sys
import httpx

BASE = "https://api.captapi.com"
KEY  = sys.argv[1] if len(sys.argv) > 1 else ""

TIKTOK_VIDEO   = "https://www.tiktok.com/@charlidamelio/video/7228896391451037994"
TIKTOK_PROFILE = "https://www.tiktok.com/@charlidamelio"
TIKTOK_MUSIC   = "https://www.tiktok.com/music/a-negroni-sbagliato-w-prosecco-l-hbo-max-7149523537730997035"
IG_PROFILE     = "https://www.instagram.com/nasa/"
IG_AUDIO       = "https://www.instagram.com/reels/audio/1053894982231129/"
YT_CHANNEL     = "https://www.youtube.com/@MrBeast"

async def call(client, name, path, params):
    t0 = time.perf_counter()
    try:
        r = await client.get(BASE + path, params=params, timeout=180)
        elapsed = round(time.perf_counter() - t0, 1)
        try:
            body = r.json()
            data = body.get("data", {})
            excerpt = json.dumps(data, ensure_ascii=False)[:220]
        except Exception:
            excerpt = r.text[:220]
        return {"name": name, "code": r.status_code, "ok": 200 <= r.status_code < 300, "elapsed": elapsed, "excerpt": excerpt, "raw": r.text}
    except Exception as e:
        return {"name": name, "code": 0, "ok": False, "elapsed": round(time.perf_counter()-t0,1), "excerpt": f"EXCEPTION: {e}", "raw": ""}

async def main():
    headers = {"Authorization": f"Bearer {KEY}"}
    async with httpx.AsyncClient(headers=headers) as client:
        # Prefetch a real comment_id for the replies test
        print("Prefetching comment_id...")
        pre = await call(client, "prefetch", "/v1/tiktok/comments", {"url": TIKTOK_VIDEO, "limit": 5})
        comment_id = None
        try:
            cdata = json.loads(pre["raw"]).get("data", {})
            comments = cdata.get("comments", [])
            if comments:
                comment_id = comments[0].get("id")
        except Exception:
            pass
        print(f"comment_id = {comment_id}\n")

        tests = [
            ("TT channel-posts",   "/v1/tiktok/channel-posts",   {"url": TIKTOK_PROFILE, "limit": 5}),
            ("TT user-followers",  "/v1/tiktok/user-followers",   {"url": TIKTOK_PROFILE, "limit": 10}),
            ("TT user-followings", "/v1/tiktok/user-followings",  {"url": TIKTOK_PROFILE, "limit": 10}),
            ("TT music-posts",     "/v1/tiktok/music-posts",      {"url": TIKTOK_MUSIC, "limit": 5}),
            ("IG tagged-posts",    "/v1/instagram/tagged-posts",  {"url": IG_PROFILE, "limit": 5}),
            ("IG music-posts",     "/v1/instagram/music-posts",   {"url": IG_AUDIO, "limit": 5}),
            ("YT channel-shorts",  "/v1/youtube/channel-shorts",  {"url": YT_CHANNEL, "limit": 5}),
            ("YT channel-streams", "/v1/youtube/channel-streams", {"url": YT_CHANNEL, "limit": 5}),
            ("YT hashtag-search",  "/v1/youtube/hashtag-search",  {"q": "gaming", "limit": 5}),
        ]
        if comment_id:
            tests.insert(1, ("TT comment-replies", "/v1/tiktok/comment-replies", {"url": TIKTOK_VIDEO, "comment_id": comment_id, "limit": 10}))

        print(f"Running {len(tests)} endpoints in parallel...\n")
        t0 = time.perf_counter()
        results = await asyncio.gather(*[call(client, n, p, q) for n, p, q in tests])
        total = time.perf_counter() - t0

    print(f"\n{'NAME':<24} {'PASS/FAIL':<9} {'CODE':>4} {'TIME':>6}  EXCERPT")
    print("-" * 140)
    passed = 0
    for r in results:
        icon = "PASS" if r["ok"] else "FAIL"
        passed += r["ok"]
        print(f"{r['name']:<24} {icon:<9} {r['code']:>4} {r['elapsed']:>5}s  {r['excerpt']}")
    print("-" * 140)
    print(f"\n{passed}/{len(results)} passed  (total wall-time {total:.1f}s)\n")

asyncio.run(main())