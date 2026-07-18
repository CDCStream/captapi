# Deploy the app/ definition to Make.com via the SDK Apps API.
# Run from the repo root: python packages/captapi-make/deploy.py <make-token> [zone]
# Idempotent: reuses the existing app/connection/modules and re-uploads sections.
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

TOKEN = sys.argv[1]
ZONE = sys.argv[2] if len(sys.argv) > 2 else "eu1"
BASE = f"https://{ZONE}.make.com/api/v2"
APP_DIR = Path(__file__).resolve().parent / "app"
APP_NAME = "captapi"
APP_VERSION = 1


def call(method: str, path: str, payload=None, content_type="application/json", raw=None):
    url = f"{BASE}{path}"
    data = raw if raw is not None else (
        json.dumps(payload).encode() if payload is not None else None
    )
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Token {TOKEN}")
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    )
    if data is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]


def must(status, body, what):
    if status >= 300:
        print(f"FAIL {what}: {status} {body}")
        sys.exit(1)
    return body


manifest = json.loads((APP_DIR / "makecomapp.json").read_text(encoding="utf-8-sig"))
modules = manifest["components"]["module"]
print(f"manifest: {len(modules)} modules")

# 1. App (reuse if it already exists)
status, body = call("GET", "/sdk/apps")
existing_app = None
if status == 200:
    for a in body.get("apps", []):
        if a.get("label") == "Captapi" or a.get("name", "").startswith("captapi"):
            existing_app = a
            break
if existing_app:
    APP_NAME = existing_app["name"]
    APP_VERSION = existing_app.get("version", 1)
    print(f"app exists, reusing: {APP_NAME} v{APP_VERSION}")
else:
    status, body = call("POST", "/sdk/apps", {
        "name": APP_NAME,
        "label": "Captapi",
        "description": (
            "Structured social media data from 27 platforms (YouTube, TikTok, "
            "Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest, "
            "LinkedIn and more): transcripts, AI summaries, comments, stats, "
            "search and downloads with one API key."
        ),
        "theme": "#0891b2",
        "language": "en",
        "audience": "global",
    })
    must(status, body, "create app")
    created = body.get("app") or {}
    APP_NAME = created.get("name", APP_NAME)
    APP_VERSION = created.get("version", APP_VERSION)
    print("app created:", json.dumps(body))

# 2. Base
base = json.loads((APP_DIR / "general/base.iml.json").read_text(encoding="utf-8-sig"))
status, body = call("PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/base", base, "application/jsonc")
if status >= 300:
    status, body = call("PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/base", base)
must(status, body, "set base")
print("base set")

# 3. Readme
readme_path = APP_DIR / "README.md"
if readme_path.exists():
    status, body = call(
        "PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/readme",
        raw=readme_path.read_text(encoding="utf-8-sig").encode(),
        content_type="text/markdown",
    )
    print(f"readme: {status}")

# 4. Connection
status, body = call("GET", f"/sdk/apps/{APP_NAME}/connections")
conn_name = None
if status == 200:
    conns = body.get("appConnections") or body.get("connections") or []
    if conns:
        conn_name = conns[0]["name"]
        print("connection exists:", conn_name)
if not conn_name:
    status, body = call("POST", f"/sdk/apps/{APP_NAME}/connections", {
        "type": "basic",
        "label": "Captapi API Key",
    })
    must(status, body, "create connection")
    conn_name = (body.get("appConnection") or {}).get("name")
    print("connection created:", conn_name)

conn_api = json.loads((APP_DIR / "connections/captapi/communication.iml.json").read_text(encoding="utf-8-sig"))
conn_params = json.loads((APP_DIR / "connections/captapi/params.iml.json").read_text(encoding="utf-8-sig"))
status, body = call("PUT", f"/sdk/apps/connections/{conn_name}/api", conn_api, "application/jsonc")
if status >= 300:
    status, body = call("PUT", f"/sdk/apps/connections/{conn_name}/api", conn_api)
must(status, body, "connection api")
status, body = call("PUT", f"/sdk/apps/connections/{conn_name}/parameters", conn_params, "application/jsonc")
if status >= 300:
    status, body = call("PUT", f"/sdk/apps/connections/{conn_name}/parameters", conn_params)
must(status, body, "connection parameters")
print("connection configured")

# 5. Modules
status, body = call("GET", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/modules")
existing = set()
if status == 200:
    for m in body.get("appModules", []):
        existing.add(m["name"])

failed = []
for i, (name, spec) in enumerate(modules.items(), 1):
    if name not in existing:
        status, body = call("POST", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/modules", {
            "name": name,
            "label": spec["label"],
            "description": spec.get("description", ""),
            "typeId": 4,
            "connection": conn_name,
            "moduleInitMode": "blank",
            "crud": spec.get("actionCrud") or "read",
        })
        if status >= 300:
            print(f"  [{i}] create {name} FAILED: {status} {body}")
            failed.append(name)
            continue

    comm = json.loads((APP_DIR / spec["codeFiles"]["communication"]).read_text(encoding="utf-8-sig"))
    status, body = call(
        "PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/modules/{name}/api", comm, "application/jsonc",
    )
    if status >= 300:
        status, body = call("PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/modules/{name}/api", comm)
    if status >= 300:
        print(f"  [{i}] api {name} FAILED: {status} {body}")
        failed.append(name)
        continue

    mp_file = spec["codeFiles"].get("mappableParams")
    if mp_file:
        mp = json.loads((APP_DIR / mp_file).read_text(encoding="utf-8-sig"))
        status, body = call(
            "PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/modules/{name}/expect", mp, "application/jsonc",
        )
        if status >= 300:
            status, body = call("PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/modules/{name}/expect", mp)
        if status >= 300:
            print(f"  [{i}] expect {name} FAILED: {status} {body}")
            failed.append(name)
            continue

    if i % 10 == 0:
        print(f"  {i}/{len(modules)} modules done")
    time.sleep(0.12)

print(f"modules complete: {len(modules) - len(failed)}/{len(modules)} ok")
if failed:
    print("failed:", failed)

# 6. Groups
groups = json.loads((APP_DIR / "modules/groups.json").read_text(encoding="utf-8-sig"))
status, body = call("PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/groups", groups, "application/jsonc")
if status >= 300:
    status, body = call("PUT", f"/sdk/apps/{APP_NAME}/{APP_VERSION}/groups", {"groups": groups})
print(f"groups: {status}" + (f" {body}" if status >= 300 else ""))

print("DONE")
