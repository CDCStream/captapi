import asyncio, json, sys
import httpx
sys.stdout.reconfigure(encoding="utf-8")
BASE = "https://api.captapi.com"
KEY  = "capt_live_12kphAtUmxSNFiuZcnPN0KqQhd7NvfB"
# A known-popular audio page (Believer - Imagine Dragons sample from the actor docs)
AUDIO = "https://www.instagram.com/reels/audio/579408562507956/"

async def main():
    headers = {"Authorization": f"Bearer {KEY}"}
    async with httpx.AsyncClient(headers=headers) as client:
        r = await client.get(BASE + "/v1/instagram/music-posts",
                             params={"url": AUDIO, "limit": 3}, timeout=180)
        print("HTTP", r.status_code)
        data = r.json().get("data", {})
        print("totalReturned:", data.get("totalReturned"))
        for p in data.get("posts", [])[:3]:
            print(json.dumps({
                "url": p.get("url"), "id": p.get("id"),
                "author": p.get("author", {}).get("username"),
                "views": p.get("engagement", {}).get("views"),
                "likes": p.get("engagement", {}).get("likes"),
                "musicId": p.get("musicId"),
            }, ensure_ascii=True))

asyncio.run(main())