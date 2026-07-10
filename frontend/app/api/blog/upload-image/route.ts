import { NextRequest, NextResponse } from "next/server";
import { getServiceClient } from "@/lib/supabase/admin";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BUCKET = "blog-images";
const MAX_BYTES = 8 * 1024 * 1024;

function authorized(req: NextRequest): boolean {
  const secret = process.env.BLOG_ADMIN_SECRET;
  return Boolean(secret && req.headers.get("x-admin-secret") === secret);
}

export async function POST(req: NextRequest) {
  if (!authorized(req)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const sb = getServiceClient();
  if (!sb) {
    return NextResponse.json(
      { error: "Supabase service role not configured" },
      { status: 500 },
    );
  }

  let body: { name?: unknown; b64?: unknown; contentType?: unknown };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const name = String(body.name ?? "");
  const contentType = String(body.contentType ?? "image/png");
  if (!/^[a-z0-9][a-z0-9-]*\.(png|webp|jpe?g)$/.test(name)) {
    return NextResponse.json({ error: "invalid image name" }, { status: 400 });
  }
  if (!/^image\/(png|webp|jpeg)$/.test(contentType)) {
    return NextResponse.json({ error: "invalid content type" }, { status: 400 });
  }
  const buffer = Buffer.from(String(body.b64 ?? ""), "base64");
  if (!buffer.length || buffer.length > MAX_BYTES) {
    return NextResponse.json(
      { error: "image is empty or too large" },
      { status: 400 },
    );
  }

  // Idempotent: returns an "already exists" error after the first call.
  await sb.storage.createBucket(BUCKET, { public: true });

  const { error } = await sb.storage
    .from(BUCKET)
    .upload(name, buffer, { contentType, upsert: true });
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const { data } = sb.storage.from(BUCKET).getPublicUrl(name);
  return NextResponse.json({ ok: true, url: data.publicUrl });
}
