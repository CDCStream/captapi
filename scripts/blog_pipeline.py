"""Scheduled SEO blog agent for captapi.com.

The agent imports Ahrefs CSV exports, optionally verifies metrics with
DataForSEO, researches the live SERP through Serper, writes an HTML article
with inline AI illustrations plus one sourced CC web photo, assigns a
permanent branded cover, and upserts the result into ``blog_posts``.

Examples:
  python scripts/blog_pipeline.py --import-ahrefs exports/keywords.csv
  python scripts/blog_pipeline.py --count 1
  python scripts/blog_pipeline.py --count 4 --dry-run
  python scripts/blog_pipeline.py --keyword "tiktok transcript api"

Required for article generation:
  OPENAI_API_KEY

Required for upload:
  BLOG_ADMIN_SECRET

Recommended:
  SERPER_API_KEY
  DATAFORSEO_LOGIN
  DATAFORSEO_PASSWORD

Optional:
  BLOG_MODEL          default gpt-4o
  BLOG_IMAGE_MODEL    default gpt-image-1 (dall-e-3 fallback is automatic)
  BLOG_SITE_URL       default https://captapi.com
  BLOG_STATUS         draft or published; default draft
  BLOG_AUTHOR         default Captapi
"""

from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "marketing" / "keyword-bank.csv"
DRAFTS_DIR = ROOT / "marketing" / "blog-drafts"

# "or" instead of get() default: CI may set these to empty strings.
SITE = (os.environ.get("BLOG_SITE_URL") or "https://captapi.com").rstrip("/")
MODEL = os.environ.get("BLOG_MODEL") or "gpt-4o"
IMAGE_MODEL = os.environ.get("BLOG_IMAGE_MODEL") or "gpt-image-1"
DEFAULT_STATUS = (os.environ.get("BLOG_STATUS") or "draft").strip().lower()
AUTHOR = os.environ.get("BLOG_AUTHOR", "Captapi").strip() or "Captapi"

BANK_FIELDS = [
    "keyword",
    "bucket",
    "kd",
    "volume",
    "traffic_potential",
    "priority",
    "target_slug",
    "internal_links",
    "status",
    "notes",
    "last_checked_at",
]

SYSTEM_PROMPT = """You are the technical content writer for Captapi (captapi.com), \
a REST API that returns social media data (profiles, posts, comments, transcripts, \
AI summaries) from 29 platforms (YouTube, TikTok, Instagram, Facebook, X, Reddit, \
Threads, Bluesky, Pinterest, LinkedIn and more) as clean JSON with one API key. \
Free tier: 100 credits, no card. Docs: captapi.com/docs.

Write for developers. Rules:
- Answer the search intent in the FIRST 100 words, before any background.
- Use plain, direct language. No fluff, no "in today's digital landscape".
- Include at least one of: a comparison table, a code example (curl + Python), \
or a real JSON response snippet.
- Mention Captapi naturally where relevant (1-3 times max). Never trash \
competitors with false claims; be factual about trade-offs.
- End with an FAQ section (3-5 questions) using <h3> per question.
- Insert exactly 2 image placeholders on their own lines, each formatted as \
[[IMAGE: detailed description of a helpful illustration]] - one right after \
the intro section and one mid-article. Never place them inside tables, \
lists, code blocks, or the FAQ.
- Insert exactly 1 photo placeholder on its own line, formatted as \
[[PHOTO: 2-4 word English stock-photo search query]], in a section that \
has no illustration placeholder.
- Output valid, semantic HTML only (h2/h3/p/table/pre/code/ul/ol). \
NO <html>, <head>, <body>, <h1> tags. No markdown.
- 1200-1800 words of body text. Articles under 1200 words are rejected \
automatically, so write complete, deep sections rather than summaries."""

USER_PROMPT_TEMPLATE = """Target keyword: "{keyword}"

Current Google results (differentiate; do not copy unsupported claims):
{serp_context}

People also ask / related searches:
{questions}

Internal links you MUST weave in naturally (anchor text should be descriptive):
{internal_links}

Extra context/notes from our marketing plan: {notes}

Write the article now. Output ONLY the raw article HTML - no JSON, no
markdown code fences, no commentary before or after."""

META_PROMPT_TEMPLATE = """Target keyword: "{keyword}"

Article (plain-text excerpt):
{excerpt}

Return a JSON object with exactly these keys:
- "title": SEO title, <= 60 chars, contains the keyword or a close variant
- "description": meta description, <= 155 chars
- "tags": array of 3-5 short topic tags"""

IMAGE_STYLE = (
    "Minimal flat vector illustration for a developer blog. Dark navy "
    "background (#0b1220), cyan (#22d3ee) and indigo (#6366f1) accents, soft "
    "glow, clean geometric shapes, no text, no words, no letters, no logos, "
    "no watermarks. Scene: {scene}"
)

IMAGE_MARKER = re.compile(r"(?:<p>\s*)?\[\[IMAGE:\s*(.*?)\]\](?:\s*</p>)?", re.S)
PHOTO_MARKER = re.compile(r"(?:<p>\s*)?\[\[PHOTO:\s*(.*?)\]\](?:\s*</p>)?", re.S)
PHOTO_EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def read_bank() -> list[dict]:
    if not BANK.exists():
        return []
    with open(BANK, newline="", encoding="utf-8-sig") as f:
        return [normalize_bank_row(row) for row in csv.DictReader(f)]


def write_bank(rows: list[dict]) -> None:
    fields = list(BANK_FIELDS)
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    BANK.parent.mkdir(parents=True, exist_ok=True)
    with open(BANK, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows({key: row.get(key, "") for key in fields} for row in rows)


def normalize_bank_row(row: dict[str, Any]) -> dict[str, str]:
    normalized = {str(k).strip(): str(v or "").strip() for k, v in row.items() if k}
    return {key: normalized.get(key, "") for key in BANK_FIELDS} | {
        key: value for key, value in normalized.items() if key not in BANK_FIELDS
    }


def first_value(row: dict[str, str], aliases: list[str]) -> str:
    lower = {key.lower().strip(): value for key, value in row.items()}
    for alias in aliases:
        value = lower.get(alias.lower())
        if value:
            return value.strip()
    return ""


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:96]


def infer_bucket(keyword: str, intent: str) -> str:
    text = f"{keyword} {intent}".lower()
    if any(token in text for token in ("alternative", " vs ", "best ", "pricing")):
        return "comparison"
    if any(token in text for token in ("calculator", "viewer", "generator", "downloader")):
        return "tool-support"
    return "informational"


def as_number(value: str, default: float = 0) -> float:
    try:
        return float((value or "").replace(",", "").strip() or default)
    except ValueError:
        return default


def priority_for(kd: str, volume: str) -> str:
    try:
        difficulty = float(kd.replace(",", "."))
    except ValueError:
        difficulty = 50
    try:
        searches = float(volume.replace(",", ""))
    except ValueError:
        searches = 0
    if difficulty <= 15 and searches >= 500:
        return "1"
    if difficulty <= 30 and searches >= 100:
        return "2"
    return "3"


def import_ahrefs(path: Path, rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    """Merge a standard Ahrefs Keywords Explorer export into the keyword bank."""
    with open(path, newline="", encoding="utf-8-sig") as handle:
        source = list(csv.DictReader(handle))

    by_keyword = {row["keyword"].casefold(): row for row in rows if row.get("keyword")}
    imported = 0
    for raw in source:
        item = {str(k): str(v or "") for k, v in raw.items() if k}
        keyword = first_value(item, ["Keyword", "keyword"])
        if not keyword:
            continue
        volume = first_value(item, ["Volume", "Search volume", "Global volume"])
        kd = first_value(item, ["Keyword Difficulty", "KD", "Difficulty"])
        intent = first_value(item, ["Intents", "Intent"])
        traffic = first_value(item, ["Traffic Potential", "Traffic potential"])
        key = keyword.casefold()
        current = by_keyword.get(key)
        if current is None:
            current = normalize_bank_row(
                {
                    "keyword": keyword,
                    "bucket": infer_bucket(keyword, intent),
                    "kd": kd,
                    "volume": volume,
                    "traffic_potential": traffic,
                    "priority": priority_for(kd, volume),
                    "target_slug": slugify(keyword),
                    "status": "queued",
                    "notes": f"Ahrefs intent: {intent}" if intent else "Imported from Ahrefs",
                }
            )
            rows.append(current)
            by_keyword[key] = current
            imported += 1
        else:
            current["kd"] = kd or current.get("kd", "")
            current["volume"] = volume or current.get("volume", "")
            current["traffic_potential"] = traffic or current.get("traffic_potential", "")
            current["priority"] = priority_for(current["kd"], current["volume"])
    return rows, imported


def http_request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: Any | None = None,
    timeout: int = 30,
) -> str:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers or {"User-Agent": "Mozilla/5.0"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code} from {url.split('?')[0]}: {detail}") from exc


def research_serp(keyword: str) -> tuple[list[dict[str, str]], list[str]]:
    """Return current organic results and question ideas, preferring Serper."""
    serper_key = os.environ.get("SERPER_API_KEY", "").strip()
    if serper_key:
        try:
            payload = {"q": keyword, "gl": "us", "hl": "en", "num": 10}
            body = http_request(
                "https://google.serper.dev/search",
                method="POST",
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
                payload=payload,
            )
            data = json.loads(body)
            organic = [
                {
                    "title": str(item.get("title", "")),
                    "link": str(item.get("link", "")),
                    "snippet": str(item.get("snippet", "")),
                }
                for item in data.get("organic", [])[:8]
            ]
            questions = [
                str(item.get("question", ""))
                for item in data.get("peopleAlsoAsk", [])
                if item.get("question")
            ]
            questions.extend(
                str(item.get("query", ""))
                for item in data.get("relatedSearches", [])
                if item.get("query")
            )
            return organic, questions[:10]
        except Exception as e:  # quota/network issues must not block drafting
            print(f"  serper failed ({e}); falling back to duckduckgo")

    # Free fallback keeps local dry-runs useful when Serper is not configured.
    try:
        q = urllib.parse.quote_plus(keyword)
        body = http_request(f"https://html.duckduckgo.com/html/?q={q}")
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', body, re.S)
        clean = [html.unescape(re.sub(r"<[^>]+>", "", t)).strip() for t in titles]
        return [{"title": title, "link": "", "snippet": ""} for title in clean if title][:6], []
    except Exception as e:  # SERP research is optional; never block drafting
        print(f"  serp research failed ({e}); continuing without it")
        return [], []


def dataforseo_metrics(keyword: str) -> dict[str, str]:
    """Fetch US Google volume and difficulty from DataForSEO Labs."""
    login = os.environ.get("DATAFORSEO_LOGIN", "").strip()
    password = os.environ.get("DATAFORSEO_PASSWORD", "").strip()
    if not login or not password:
        return {}
    auth = base64.b64encode(f"{login}:{password}".encode()).decode()
    body = http_request(
        "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live",
        method="POST",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
        payload=[{"keywords": [keyword], "location_code": 2840, "language_code": "en"}],
        timeout=60,
    )
    data = json.loads(body)
    try:
        item = data["tasks"][0]["result"][0]["items"][0]
    except (KeyError, IndexError, TypeError):
        return {}
    info = item.get("keyword_info") or {}
    props = item.get("keyword_properties") or {}
    return {
        "volume": str(info.get("search_volume") or ""),
        "kd": str(props.get("keyword_difficulty") or ""),
        "last_checked_at": datetime.now(UTC).isoformat(),
    }


def chat_completion(messages: list[dict[str, str]], *, json_mode: bool = False) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        sys.exit("OPENAI_API_KEY is not set")
    payload: dict[str, Any] = {"model": MODEL, "messages": messages}
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    body = http_request(
        "https://api.openai.com/v1/chat/completions",
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        payload=payload,
        timeout=300,
    )
    return str(json.loads(body)["choices"][0]["message"]["content"] or "")


def call_openai(
    keyword: str,
    results: list[dict[str, str]],
    questions: list[str],
    internal_links: str,
    notes: str,
    feedback: str = "",
) -> dict:
    links = "\n".join(f"- {SITE}{p.strip()}" for p in internal_links.split(";") if p.strip())
    user = USER_PROMPT_TEMPLATE.format(
        keyword=keyword,
        serp_context="\n".join(
            f"- {item['title']} | {item['snippet']} | {item['link']}" for item in results
        )
        or "(none found)",
        questions="\n".join(f"- {question}" for question in questions) or "(none found)",
        internal_links=links or "(none)",
        notes=notes or "(none)",
    )
    if feedback:
        user += (
            "\n\nYour previous attempt was rejected by automated checks: "
            + feedback
            + ". Fix every issue and rewrite the complete article. Expand every"
            " section with concrete detail; target 1400-1600 words of body text."
        )

    # The article is requested as raw HTML (not JSON-wrapped): models compress
    # long content dramatically when it has to live inside a JSON string.
    content = chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ]
    ).strip()
    content = re.sub(r"^```(?:html)?\s*|\s*```$", "", content).strip()
    if not content:
        raise ValueError("LLM returned an empty article")

    excerpt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))[:4000]
    meta = json.loads(
        chat_completion(
            [
                {
                    "role": "system",
                    "content": "You write SEO metadata for developer articles. "
                    "Return JSON only.",
                },
                {
                    "role": "user",
                    "content": META_PROMPT_TEMPLATE.format(
                        keyword=keyword, excerpt=excerpt
                    ),
                },
            ],
            json_mode=True,
        )
    )
    out = {
        "title": str(meta.get("title", "")).strip(),
        "description": str(meta.get("description", "")).strip(),
        "tags": meta.get("tags") or [],
        "content": content,
    }
    for key in ("title", "description", "content"):
        if not out.get(key):
            raise ValueError(f"LLM output missing '{key}'")
    return out


def validate_article(article: dict[str, Any], keyword: str, internal_links: str) -> None:
    title = str(article.get("title", "")).strip()
    description = str(article.get("description", "")).strip()
    content = str(article.get("content", "")).strip()
    plain = re.sub(r"<[^>]+>", " ", content)
    words = len(re.findall(r"\b[\w'-]+\b", plain))
    errors: list[str] = []
    if not title or len(title) > 65:
        errors.append("title must be 1-65 characters")
    if not description or len(description) > 160:
        errors.append("description must be 1-160 characters")
    if words < 900:
        errors.append(f"article is too short ({words} words)")
    if "<h2" not in content or "<h3" not in content:
        errors.append("article needs h2 and h3 sections")
    # Event handlers are only dangerous inside a tag; a bare "on_update ="
    # in a code sample is fine.
    if re.search(r"<(?:script|iframe|object|embed)\b|<[^>]*\son\w+\s*=", content, re.I):
        errors.append("article contains unsafe HTML")
    if keyword.split()[0].lower() not in f"{title} {plain[:800]}".lower():
        errors.append("primary topic is missing from title/opening")
    expected = [path.strip() for path in internal_links.split(";") if path.strip()]
    if expected and not any(path in content for path in expected):
        errors.append("none of the required internal links were included")
    if errors:
        raise ValueError("; ".join(errors))


def cover_url(slug: str) -> str:
    return f"{SITE}/blog/{slug}/opengraph-image"


def generate_image(description: str) -> tuple[bytes, str] | None:
    """Render one inline illustration; returns (bytes, content_type) or None."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    prompt = IMAGE_STYLE.format(scene=description)
    for model in dict.fromkeys((IMAGE_MODEL, "dall-e-3")):
        if model.startswith("gpt-image"):
            payload: dict[str, Any] = {
                "model": model,
                "prompt": prompt,
                "size": "1536x1024",
                "quality": "medium",
                "output_format": "webp",
            }
            content_type = "image/webp"
        else:
            payload = {
                "model": model,
                "prompt": prompt,
                "size": "1792x1024",
                "response_format": "b64_json",
            }
            content_type = "image/png"
        try:
            body = http_request(
                "https://api.openai.com/v1/images/generations",
                method="POST",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                payload=payload,
                timeout=240,
            )
            b64 = json.loads(body)["data"][0]["b64_json"]
            return base64.b64decode(b64), content_type
        except Exception as exc:
            print(f"  image model {model} failed ({exc})")
    return None


def upload_image(name: str, image: bytes, content_type: str) -> str:
    secret = os.environ.get("BLOG_ADMIN_SECRET", "").strip()
    body = http_request(
        f"{SITE}/api/blog/upload-image",
        method="POST",
        headers={"Content-Type": "application/json", "x-admin-secret": secret},
        payload={
            "name": name,
            "b64": base64.b64encode(image).decode(),
            "contentType": content_type,
        },
        timeout=120,
    )
    return str(json.loads(body).get("url") or "")


def embed_images(content: str, slug: str, generate: bool) -> str:
    """Replace [[IMAGE: ...]] markers with hosted illustrations (max 2)."""
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        description = match.group(1).strip()
        if not generate or count >= 2 or not description:
            return ""
        rendered = generate_image(description)
        if not rendered:
            return ""
        image, content_type = rendered
        count += 1
        ext = "webp" if content_type == "image/webp" else "png"
        try:
            url = upload_image(f"{slug}-{count}.{ext}", image, content_type)
        except Exception as exc:
            print(f"  image upload failed ({exc}); skipping illustration")
            return ""
        if not url:
            return ""
        alt = html.escape(description[:150], quote=True)
        print(f"  illustration {count} -> {url}")
        return f'<figure><img src="{url}" alt="{alt}" loading="lazy" /></figure>'

    return IMAGE_MARKER.sub(replace, content)


def search_web_photo(query: str) -> dict[str, str] | None:
    """Find one commercially usable CC-licensed photo on Openverse."""
    params = urllib.parse.urlencode(
        {
            "q": query,
            "license_type": "commercial",
            "page_size": "20",
            "filter_dead": "true",
        }
    )
    body = http_request(
        f"https://api.openverse.org/v1/images/?{params}",
        headers={"User-Agent": "captapi-blog-agent/1.0", "Accept": "application/json"},
        timeout=45,
    )
    for item in json.loads(body).get("results", []):
        url = str(item.get("url") or "")
        if not url.lower().split("?")[0].endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
        if (item.get("width") or 0) < 640:
            continue
        return {
            "url": url,
            "title": str(item.get("title") or "Photo"),
            "creator": str(item.get("creator") or "Unknown"),
            "license": str(item.get("license") or "").upper(),
            "license_version": str(item.get("license_version") or ""),
            "source_url": str(item.get("foreign_landing_url") or url),
        }
    return None


def download_photo(url: str) -> tuple[bytes, str] | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        content_type = (r.headers.get_content_type() or "").lower()
        data = r.read()
    if content_type not in PHOTO_EXTENSIONS or not data or len(data) > 7_000_000:
        return None
    return data, content_type


def embed_web_photos(content: str, slug: str, generate: bool) -> str:
    """Replace [[PHOTO: ...]] markers with sourced CC photos (max 1)."""
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        query = match.group(1).strip()
        if not generate or count >= 1 or not query:
            return ""
        try:
            photo = search_web_photo(query)
            if not photo:
                print(f"  no usable CC photo found for '{query}'")
                return ""
            downloaded = download_photo(photo["url"])
            if not downloaded:
                print(f"  photo download rejected for '{query}'")
                return ""
            image, content_type = downloaded
            count += 1
            ext = PHOTO_EXTENSIONS[content_type]
            url = upload_image(f"{slug}-photo-{count}.{ext}", image, content_type)
        except Exception as exc:
            print(f"  web photo failed ({exc}); skipping")
            return ""
        if not url:
            return ""
        if photo["license"] in {"CC0", "PDM"}:
            license_label = "Public Domain" if photo["license"] == "PDM" else "CC0"
        else:
            license_label = " ".join(
                part
                for part in (f"CC {photo['license']}", photo["license_version"])
                if part.strip()
            )
        source = html.escape(photo["source_url"], quote=True)
        title = html.escape(photo["title"][:80])
        creator = html.escape(photo["creator"][:60])
        alt = html.escape(query[:150], quote=True)
        print(f"  web photo -> {url}")
        return (
            f'<figure><img src="{url}" alt="{alt}" loading="lazy" />'
            f'<figcaption>Source: <a href="{source}" rel="noopener nofollow" '
            f'target="_blank">{title} by {creator}</a> ({license_label})'
            f"</figcaption></figure>"
        )

    return PHOTO_MARKER.sub(replace, content)


def existing_posts() -> dict[str, str]:
    secret = os.environ.get("BLOG_ADMIN_SECRET", "").strip()
    if not secret:
        return {}
    try:
        body = http_request(
            f"{SITE}/api/blog/save",
            headers={"x-admin-secret": secret},
            timeout=30,
        )
        return {
            str(item["slug"]): str(item.get("status", ""))
            for item in json.loads(body).get("posts", [])
        }
    except Exception as exc:
        print(f"  existing-post sync failed ({exc}); continuing")
        return {}


def upload_article(slug: str, article: dict, status: str) -> str:
    secret = os.environ.get("BLOG_ADMIN_SECRET", "").strip()
    if not secret:
        sys.exit("BLOG_ADMIN_SECRET is not set (use --dry-run to skip upload)")
    body = {
        "slug": slug,
        "title": article["title"],
        "description": article["description"],
        "content": article["content"],
        "image": cover_url(slug),
        "tags": article.get("tags", []),
        "author": AUTHOR,
        "status": status,
    }
    response = http_request(
        f"{SITE}/api/blog/save",
        method="POST",
        headers={"Content-Type": "application/json", "x-admin-secret": secret},
        payload=body,
        timeout=60,
    )
    return json.loads(response).get("slug", slug)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--keyword", help="draft this exact keyword from the bank")
    ap.add_argument("--import-ahrefs", type=Path, help="merge an Ahrefs CSV export")
    ap.add_argument("--enrich", action="store_true", help="refresh metrics with DataForSEO")
    ap.add_argument(
        "--status",
        choices=("draft", "published"),
        default=DEFAULT_STATUS if DEFAULT_STATUS in {"draft", "published"} else "draft",
    )
    ap.add_argument("--dry-run", action="store_true", help="write local preview only")
    args = ap.parse_args()

    rows = read_bank()
    if args.import_ahrefs:
        rows, imported = import_ahrefs(args.import_ahrefs, rows)
        write_bank(rows)
        print(f"imported {imported} new keywords; bank now contains {len(rows)}")
        if not args.keyword and args.count == 1:
            return

    remote = {} if args.dry_run else existing_posts()
    for row in rows:
        slug = row.get("target_slug") or slugify(row["keyword"])
        if slug in remote and row.get("status") == "queued":
            row["status"] = remote[slug] or "saved"

    if args.keyword:
        todo = [r for r in rows if r["keyword"].lower() == args.keyword.lower()]
        if not todo:
            sys.exit(f"keyword not in bank: {args.keyword}")
    else:
        queued = [r for r in rows if r["status"] == "queued"]
        queued.sort(
            key=lambda r: (
                as_number(r.get("priority", ""), default=9),
                -as_number(r.get("volume", "")),
                r["keyword"],
            )
        )
        todo = queued[: args.count]
    if not todo:
        sys.exit("nothing queued in keyword-bank.csv")

    DRAFTS_DIR.mkdir(exist_ok=True)
    for row in todo:
        kw = row["keyword"]
        print(f"drafting: {kw}")
        if args.enrich or not row.get("volume") or not row.get("kd"):
            try:
                metrics = dataforseo_metrics(kw)
                row.update({key: value for key, value in metrics.items() if value})
                row["priority"] = priority_for(row.get("kd", ""), row.get("volume", ""))
            except Exception as exc:
                print(f"  DataForSEO enrichment failed ({exc}); using Ahrefs values")

        results, questions = research_serp(kw)
        article: dict | None = None
        feedback = ""
        for attempt in range(1, 4):
            candidate = call_openai(
                kw,
                results,
                questions,
                row.get("internal_links", ""),
                row.get("notes", ""),
                feedback=feedback,
            )
            try:
                validate_article(candidate, kw, row.get("internal_links", ""))
                article = candidate
                break
            except ValueError as exc:
                feedback = str(exc)
                print(f"  attempt {attempt} rejected: {feedback}")
        if article is None:
            sys.exit(f"could not produce a valid article for {kw!r}: {feedback}")

        slug = row.get("target_slug") or slugify(kw)
        article["content"] = embed_images(
            article["content"], slug, generate=not args.dry_run
        )
        article["content"] = embed_web_photos(
            article["content"], slug, generate=not args.dry_run
        )

        preview = DRAFTS_DIR / f"{slug}.html"
        preview.write_text(
            f"<!-- title: {article['title']} -->\n"
            f"<!-- description: {article['description']} -->\n"
            f"<!-- tags: {', '.join(article.get('tags', []))} -->\n"
            f"{article['content']}",
            encoding="utf-8",
        )
        print(f"  preview -> {preview.relative_to(ROOT)}")

        if not args.dry_run:
            saved = upload_article(slug, article, args.status)
            print(f"  uploaded as {args.status.upper()} (slug: {saved})")
            row["status"] = args.status
        else:
            row["status"] = "drafted-local"
        time.sleep(1)

    write_bank(rows)
    print("done.")


if __name__ == "__main__":
    main()
