import re
import pathlib

names = set()
for p in pathlib.Path(__file__).resolve().parents[1].joinpath("app", "routers").glob("*.py"):
    for m in re.finditer(r'endpoint="([a-z0-9_.\-]+)"', p.read_text(encoding="utf-8")):
        names.add(m.group(1))

keys = ("channel-details", "profile", "subreddit-details", "artist", "user", "followers", "community", "page", "details")
interesting = [n for n in sorted(names) if any(k in n for k in keys)]
print(len(names), "total cached names")
print("\n".join(interesting))
