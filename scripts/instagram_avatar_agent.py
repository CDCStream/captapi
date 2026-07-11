"""Generate one daily Captapi Instagram Reel with a HeyGen AI avatar.

Flow:
  product config + recent Instagram captions -> LLM creative -> HeyGen Avatar IV
  -> local MP4 artifact -> optional Instagram Graph API publish.

Examples:
  python scripts/instagram_avatar_agent.py --dry-run
  python scripts/instagram_avatar_agent.py
  python scripts/instagram_avatar_agent.py --publish

Required:
  OPENAI_API_KEY

Required for video:
  HEYGEN_API_KEY
  HEYGEN_AVATAR_ID
  HEYGEN_VOICE_ID

Required for publishing:
  META_IG_USER_ID
  META_ACCESS_TOKEN
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "marketing" / "instagram-agent-config.json"
RUNS_DIR = ROOT / "marketing" / "instagram-runs"

OPENAI_MODEL = os.environ.get("INSTAGRAM_SCRIPT_MODEL") or "gpt-4o-mini"
GRAPH_VERSION = os.environ.get("META_GRAPH_VERSION") or "v25.0"

PILLARS = {
    0: "developer pain point",
    1: "one endpoint demo",
    2: "cost and maintenance comparison",
    3: "AI agent or automation use case",
    4: "build in public / product proof",
    5: "unexpected social-data use case",
    6: "myth, objection, or FAQ",
}

SYSTEM_PROMPT = """You are Mara, Captapi's clearly disclosed AI CMO.
Write one short UGC-style vertical video for developers: it must feel like a
creator casually talking to their phone camera, NOT like a produced ad.

Captapi is a REST API that returns structured social-media data from many
platforms with one API key. The audience dislikes hype and responds to concrete
developer pain, code, speed, reliability, and honest trade-offs.

UGC style rules:
- First person, conversational, contractions, spoken rhythm ("so", "okay",
  "honestly"), as if sharing a discovery with a friend - never announcer voice.
- The first sentence is a scroll-stopping hook grounded in a real dev moment
  (a broken scraper, a 3am rate-limit, a ridiculous quote from a vendor).
- Tell it as a tiny story or hot take: one pain, one concrete Captapi benefit.

Content rules:
- Spoken script: 38-58 words, 15-25 seconds, natural spoken English.
- Never invent customer counts, uptime, latency, savings, or platform support.
- Do not claim official partnership with social networks.
- Avoid "revolutionize", "game-changer", "unlock", and generic AI hype.
- End with one low-friction CTA, said casually.
- Caption: useful even without watching, max 600 characters.
- Include 3-6 relevant hashtags, including #AIAvatar for disclosure.
- Return JSON only."""

USER_TEMPLATE = """Date: {today}
Today's content pillar: {pillar}
Product facts (only make claims found here):
{facts}

Recent captions to avoid repeating:
{recent}

Return exactly:
{{
  "hook": "short on-screen headline, max 8 words",
  "spoken_script": "38-58 words",
  "caption": "Instagram caption without hashtags",
  "hashtags": ["#DeveloperTools", "#AIAvatar"],
  "cta": "short CTA"
}}"""


def http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: Any | None = None,
    form: dict[str, str] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    data: bytes | None = None
    request_headers = dict(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode()
        request_headers.setdefault("Content-Type", "application/json")
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(
        url,
        data=data,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code} from {url.split('?')[0]}: {detail}") from exc


def load_config() -> dict[str, Any]:
    with open(CONFIG_PATH, encoding="utf-8-sig") as handle:
        return json.load(handle)


def recent_instagram_captions(limit: int = 8) -> list[str]:
    ig_user = os.environ.get("META_IG_USER_ID", "").strip()
    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    if not ig_user or not token:
        return []
    query = urllib.parse.urlencode(
        {
            "fields": "caption,timestamp",
            "limit": str(limit),
            "access_token": token,
        }
    )
    try:
        data = http_json(
            f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_user}/media?{query}"
        )
        return [
            str(item["caption"])[:500]
            for item in data.get("data", [])
            if item.get("caption")
        ]
    except Exception as exc:
        print(f"recent-caption lookup failed ({exc}); continuing")
        return []


def generate_creative(config: dict[str, Any], run_date: date) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    recent = recent_instagram_captions()
    prompt = USER_TEMPLATE.format(
        today=run_date.isoformat(),
        pillar=PILLARS[run_date.weekday()],
        facts=json.dumps(config, indent=2),
        recent="\n---\n".join(recent) if recent else "(new account; no recent posts)",
    )
    payload = {
        "model": OPENAI_MODEL,
        "response_format": {"type": "json_object"},
        "temperature": 0.8,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    data = http_json(
        "https://api.openai.com/v1/chat/completions",
        method="POST",
        headers={"Authorization": f"Bearer {api_key}"},
        payload=payload,
        timeout=180,
    )
    creative = json.loads(data["choices"][0]["message"]["content"])
    validate_creative(creative)
    return creative


def validate_creative(creative: dict[str, Any]) -> None:
    hook = str(creative.get("hook", "")).strip()
    script = str(creative.get("spoken_script", "")).strip()
    caption = str(creative.get("caption", "")).strip()
    cta = str(creative.get("cta", "")).strip()
    hashtags = creative.get("hashtags")
    words = len(re.findall(r"\b[\w'-]+\b", script))
    errors: list[str] = []
    if not hook or len(hook.split()) > 8:
        errors.append("hook must contain 1-8 words")
    if not 35 <= words <= 65:
        errors.append(f"spoken script must contain 35-65 words (got {words})")
    if not caption or len(caption) > 800:
        errors.append("caption must contain 1-800 characters")
    if not cta:
        errors.append("cta is required")
    if not isinstance(hashtags, list) or not 3 <= len(hashtags) <= 6:
        errors.append("hashtags must contain 3-6 items")
    if isinstance(hashtags, list) and "#aiavatar" not in {
        str(tag).casefold() for tag in hashtags
    }:
        errors.append("hashtags must disclose #AIAvatar")
    if errors:
        raise ValueError("; ".join(errors))


def create_heygen_video(creative: dict[str, Any], run_date: date) -> str:
    api_key = os.environ.get("HEYGEN_API_KEY", "").strip()
    avatar_id = os.environ.get("HEYGEN_AVATAR_ID", "").strip()
    voice_id = os.environ.get("HEYGEN_VOICE_ID", "").strip()
    if not api_key or not avatar_id or not voice_id:
        raise RuntimeError(
            "HEYGEN_API_KEY, HEYGEN_AVATAR_ID, and HEYGEN_VOICE_ID are required"
        )

    # v3 avatar video: correct photo-avatar pipeline with proper lip-sync,
    # motion prompt, expressiveness, and burned-in captions.
    payload = {
        "type": "avatar",
        "title": f"Captapi Mara {run_date.isoformat()} - {creative['hook']}",
        "avatar_id": avatar_id,
        "script": creative["spoken_script"],
        "voice_id": voice_id,
        "voice_settings": {"speed": 1.0},
        "resolution": "1080p",
        "aspect_ratio": "9:16",
        "caption": {"style": "default", "file_format": "srt"},
        "motion_prompt": (
            "Casual creator talking to their phone camera: relaxed posture, "
            "natural eye contact, small authentic hand gestures, slight head "
            "movement, friendly and candid, not a polished presenter."
        ),
        "expressiveness": "medium",
    }
    data = http_json(
        "https://api.heygen.com/v3/videos",
        method="POST",
        headers={"X-Api-Key": api_key},
        payload=payload,
        timeout=90,
    )
    video_id = str((data.get("data") or {}).get("video_id") or "")
    if not video_id:
        raise RuntimeError(f"HeyGen did not return video_id: {json.dumps(data)[:500]}")
    return video_id


def wait_for_heygen(video_id: str, timeout_seconds: int = 1200) -> dict[str, Any]:
    api_key = os.environ.get("HEYGEN_API_KEY", "").strip()
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        data = http_json(
            f"https://api.heygen.com/v3/videos/{video_id}",
            headers={"X-Api-Key": api_key},
            timeout=60,
        )
        detail = data.get("data") or data
        status = str(detail.get("status", "")).lower()
        if status == "completed":
            return detail
        if status == "failed":
            raise RuntimeError(
                f"HeyGen failed: {detail.get('failure_code')} "
                f"{detail.get('failure_message')}"
            )
        print(f"HeyGen {video_id}: {status or 'processing'}")
        time.sleep(15)
    raise TimeoutError(f"HeyGen video timed out after {timeout_seconds}s")


def download_video(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Captapi/1.0"})
    with urllib.request.urlopen(req, timeout=180) as response:
        path.write_bytes(response.read())


def reel_caption(creative: dict[str, Any]) -> str:
    hashtags = " ".join(str(tag) for tag in creative["hashtags"])
    return f"{creative['caption']}\n\n{creative['cta']}\n\n{hashtags}".strip()


def publish_reel(video_url: str, creative: dict[str, Any]) -> str:
    ig_user = os.environ.get("META_IG_USER_ID", "").strip()
    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    if not ig_user or not token:
        raise RuntimeError("META_IG_USER_ID and META_ACCESS_TOKEN are required")

    created = http_json(
        f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_user}/media",
        method="POST",
        form={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": reel_caption(creative),
            "share_to_feed": "true",
            "access_token": token,
        },
    )
    container_id = str(created.get("id") or "")
    if not container_id:
        raise RuntimeError(f"Meta did not return a container ID: {created}")

    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        query = urllib.parse.urlencode(
            {"fields": "status_code,status", "access_token": token}
        )
        status = http_json(
            f"https://graph.facebook.com/{GRAPH_VERSION}/{container_id}?{query}"
        )
        code = str(status.get("status_code", "")).upper()
        if code == "FINISHED":
            break
        if code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Meta container failed: {status}")
        print(f"Meta container {container_id}: {code or 'processing'}")
        time.sleep(15)
    else:
        raise TimeoutError("Meta Reel container processing timed out")

    published = http_json(
        f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_user}/media_publish",
        method="POST",
        form={"creation_id": container_id, "access_token": token},
    )
    media_id = str(published.get("id") or "")
    if not media_id:
        raise RuntimeError(f"Meta did not return a media ID: {published}")
    return media_id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="write creative JSON only")
    parser.add_argument("--publish", action="store_true", help="publish completed Reel")
    parser.add_argument("--date", help="override date (YYYY-MM-DD)")
    args = parser.parse_args()

    run_date = date.fromisoformat(args.date) if args.date else datetime.now(UTC).date()
    config = load_config()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stem = run_date.isoformat()
    json_path = RUNS_DIR / f"{stem}.json"

    creative = generate_creative(config, run_date)
    record: dict[str, Any] = {
        "date": stem,
        "created_at": datetime.now(UTC).isoformat(),
        "creative": creative,
        "status": "creative_ready",
    }
    json_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"creative -> {json_path.relative_to(ROOT)}")
    if args.dry_run:
        return

    video_id = create_heygen_video(creative, run_date)
    record.update({"heygen_video_id": video_id, "status": "rendering"})
    json_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    detail = wait_for_heygen(video_id)
    video_url = str(detail.get("captioned_video_url") or detail.get("video_url") or "")
    if not video_url:
        raise RuntimeError("HeyGen completed without a video URL")
    mp4_path = RUNS_DIR / f"{stem}.mp4"
    download_video(video_url, mp4_path)
    record.update(
        {
            "status": "video_ready",
            "duration_seconds": detail.get("duration"),
            "local_video": str(mp4_path.relative_to(ROOT)),
        }
    )
    json_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"video -> {mp4_path.relative_to(ROOT)}")

    auto_publish = os.environ.get("INSTAGRAM_AUTO_PUBLISH", "").lower() == "true"
    if args.publish or auto_publish:
        media_id = publish_reel(video_url, creative)
        record.update({"status": "published", "instagram_media_id": media_id})
        json_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(f"published Instagram Reel: {media_id}")
    else:
        print("publish skipped; use --publish or INSTAGRAM_AUTO_PUBLISH=true")


if __name__ == "__main__":
    main()
