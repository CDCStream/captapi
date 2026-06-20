import { NextRequest, NextResponse } from "next/server";
import { submitToIndexNow } from "@/lib/blog";
import sitemap from "@/app/sitemap";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// IndexNow accepts up to 10,000 URLs per request; batch conservatively.
const BATCH_SIZE = 5000;

/**
 * Submit every public URL (from the sitemap) to IndexNow so Bing/Yandex pick up
 * static and programmatic pages (tools, APIs, how-to), not just blog posts.
 *
 * Protected by BLOG_ADMIN_SECRET. Trigger with either:
 *   GET  /api/indexnow?secret=...         (manual, from a browser)
 *   POST /api/indexnow  + x-admin-secret  (cron / script)
 * Optionally POST a JSON body { "urls": [...] } to submit a specific subset.
 */
function authorized(req: NextRequest): boolean {
  // Vercel Cron sends an "Authorization: Bearer <CRON_SECRET>" header.
  const cronSecret = process.env.CRON_SECRET;
  if (cronSecret) {
    const auth = req.headers.get("authorization");
    if (auth === `Bearer ${cronSecret}`) return true;
  }

  const adminSecret = process.env.BLOG_ADMIN_SECRET;
  if (!adminSecret) return false;
  const provided =
    req.headers.get("x-admin-secret") ||
    req.nextUrl.searchParams.get("secret") ||
    "";
  return provided === adminSecret;
}

async function handle(req: NextRequest): Promise<NextResponse> {
  if (!process.env.BLOG_ADMIN_SECRET && !process.env.CRON_SECRET) {
    return NextResponse.json({ error: "admin disabled" }, { status: 403 });
  }
  if (!authorized(req)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  let urls: string[] = [];

  if (req.method === "POST") {
    try {
      const body = (await req.json()) as { urls?: unknown };
      if (Array.isArray(body?.urls)) {
        urls = body.urls.map((u) => String(u)).filter(Boolean);
      }
    } catch {
      // no/invalid body -> fall back to full sitemap
    }
  }

  if (!urls.length) {
    const entries = await sitemap();
    urls = entries.map((e) => e.url).filter(Boolean);
  }

  urls = Array.from(new Set(urls));

  let submitted = 0;
  const statuses: (number | null)[] = [];
  for (let i = 0; i < urls.length; i += BATCH_SIZE) {
    const batch = urls.slice(i, i + BATCH_SIZE);
    const status = await submitToIndexNow(batch);
    statuses.push(status);
    submitted += batch.length;
  }

  return NextResponse.json({ ok: true, submitted, statuses });
}

export async function GET(req: NextRequest) {
  return handle(req);
}

export async function POST(req: NextRequest) {
  return handle(req);
}
