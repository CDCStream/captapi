import { NextRequest, NextResponse } from "next/server";
import { SITE_URL } from "@/lib/api-catalog";
import { getServiceClient } from "@/lib/supabase/admin";
import {
  pickArray,
  pickString,
  pingSearchEngines,
  slugify,
  type BlogPostRow,
} from "@/lib/blog";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Json = Record<string, unknown>;

/** Auth: accepts all requests if no secret is configured. */
function authorize(req: NextRequest): boolean {
  const secret = process.env.OUTRANK_WEBHOOK_SECRET;
  if (!secret) return true;

  const sig = req.headers.get("x-webhook-signature");
  const auth = req.headers.get("authorization");
  const bearer = auth?.startsWith("Bearer ") ? auth.slice(7).trim() : null;

  return sig === secret || bearer === secret;
}

/** Flexibly pull an array of article objects out of various payload shapes. */
function extractArticles(payload: unknown): Json[] {
  if (!payload || typeof payload !== "object") return [];
  const p = payload as Json;

  const candidates: unknown[] = [
    p.articles,
    (p.data as Json | undefined)?.articles,
    p.article,
    (p.data as Json | undefined)?.article,
  ];

  for (const c of candidates) {
    if (Array.isArray(c)) return c.filter((x) => x && typeof x === "object") as Json[];
    if (c && typeof c === "object") return [c as Json];
  }

  if (Array.isArray(payload)) {
    return (payload as unknown[]).filter((x) => x && typeof x === "object") as Json[];
  }

  // Treat the payload itself as a single article if it looks like one.
  if (p.title || p.content_html || p.content || p.html || p.body) return [p];
  return [];
}

/** Map a raw article object onto a blog_posts row. Returns null if unusable. */
function toRow(a: Json): BlogPostRow | null {
  const title = pickString(a, ["title", "headline", "name", "meta_title"]);
  const content = pickString(a, [
    "content_html",
    "content",
    "html",
    "body",
    "body_html",
    "markdown",
  ]);

  let slug = pickString(a, ["slug", "permalink", "handle", "path"]);
  if (slug) slug = slugify(slug);
  if (!slug && title) slug = slugify(title);
  if (!slug) return null;

  const description = pickString(a, [
    "description",
    "excerpt",
    "meta_description",
    "summary",
    "seo_description",
  ]);
  const image = pickString(a, [
    "image",
    "image_url",
    "cover",
    "cover_image",
    "featured_image",
    "thumbnail",
    "og_image",
  ]);
  const tags = pickArray(a, ["tags", "keywords", "categories", "labels"]);
  const author = pickString(a, ["author", "author_name", "byline"]) || "Outrank";

  // No content → keep it as a draft instead of publishing an empty page.
  const status = content
    ? pickString(a, ["status"]) || "published"
    : "draft";

  const publishedAt =
    pickString(a, ["published_at", "publishedAt", "date", "created_at"]) ||
    new Date().toISOString();

  return {
    slug,
    title: title || slug,
    description,
    content,
    image,
    tags,
    author,
    status,
    published_at: publishedAt,
    updated_at: new Date().toISOString(),
  };
}

export async function POST(req: NextRequest) {
  if (!authorize(req)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const sb = getServiceClient();
  if (!sb) {
    return NextResponse.json(
      { error: "Supabase service role not configured" },
      { status: 500 },
    );
  }

  let payload: unknown;
  try {
    payload = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const articles = extractArticles(payload);
  if (!articles.length) {
    return NextResponse.json({ error: "no articles in payload" }, { status: 400 });
  }

  const rows = articles
    .map(toRow)
    .filter((r): r is BlogPostRow => r !== null);
  if (!rows.length) {
    return NextResponse.json({ error: "no valid articles" }, { status: 400 });
  }

  const { error } = await sb.from("blog_posts").upsert(rows, { onConflict: "slug" });
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const publishedUrls = rows
    .filter((r) => r.status === "published")
    .map((r) => `${SITE_URL}/blog/${r.slug}`);
  if (publishedUrls.length) {
    await pingSearchEngines(publishedUrls);
  }

  return NextResponse.json({
    ok: true,
    count: rows.length,
    slugs: rows.map((r) => r.slug),
  });
}

export async function GET(req: NextRequest) {
  const params = req.nextUrl.searchParams;
  const challenge = params.get("challenge") || params.get("hub.challenge");
  if (challenge) {
    return new NextResponse(challenge, {
      status: 200,
      headers: { "content-type": "text/plain" },
    });
  }
  return NextResponse.json({
    status: "ok",
    service: "outrank-webhook",
    configured: Boolean(process.env.OUTRANK_WEBHOOK_SECRET),
  });
}
