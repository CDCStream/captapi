import { NextRequest, NextResponse } from "next/server";
import { SITE_URL } from "@/lib/api-catalog";
import { getServiceClient } from "@/lib/supabase/admin";
import { normalizeImageUrl, pingSearchEngines, slugify, type BlogPostRow } from "@/lib/blog";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const secret = process.env.BLOG_ADMIN_SECRET;
  if (!secret) {
    return NextResponse.json({ error: "admin disabled" }, { status: 403 });
  }
  if (req.headers.get("x-admin-secret") !== secret) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const sb = getServiceClient();
  if (!sb) {
    return NextResponse.json(
      { error: "Supabase service role not configured" },
      { status: 500 },
    );
  }

  let body: Record<string, unknown>;
  try {
    body = (await req.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const title = String(body.title ?? "").trim();
  const content = String(body.content ?? "").trim();
  const rawSlug = String(body.slug ?? "").trim();
  if (!title || !content) {
    return NextResponse.json(
      { error: "title and content are required" },
      { status: 400 },
    );
  }

  const tags = Array.isArray(body.tags)
    ? body.tags.map((t) => String(t).trim()).filter(Boolean)
    : String(body.tags ?? "")
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);

  const status = String(body.status ?? "published");
  const row: BlogPostRow = {
    slug: slugify(rawSlug || title),
    title,
    content,
    description: String(body.description ?? ""),
    image: normalizeImageUrl(String(body.image ?? "")),
    author: String(body.author ?? "Captapi"),
    tags,
    status,
    updated_at: new Date().toISOString(),
  };
  if (status === "published") {
    row.published_at = new Date().toISOString();
  }

  const { error } = await sb.from("blog_posts").upsert(row, { onConflict: "slug" });
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  if (status === "published") {
    await pingSearchEngines([`${SITE_URL}/blog/${row.slug}`]);
  }

  return NextResponse.json({ ok: true, slug: row.slug });
}
