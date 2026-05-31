import asyncio, json, sys
import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://api.captapi.com"
KEY  = "capt_live_12kphAtUmxSNFiuZcnPN0KqQhd7NvfB"

async def main():
    headers = {"Authorization": f"Bearer {KEY}"}
    async with httpx.AsyncClient(headers=headers) as client:
        r = await client.get(BASE + "/v1/tiktok/user-followers",
                             params={"url": "https://www.tiktok.com/@charlidamelio", "limit": 3},
                             timeout=60)
        data = r.json()
        followers = data.get("data", {}).get("followers", [])
        print(f"totalReturned: {data.get('data',{}).get('totalReturned')}")
        for f in followers[:2]:
            print(json.dumps(f, indent=2, ensure_ascii=True))

asyncio.run(main())