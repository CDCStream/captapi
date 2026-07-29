import { NextRequest, NextResponse } from "next/server";
import sharp from "sharp";
import { getServiceClient } from "@/lib/supabase/admin";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BUCKET = "blog-images";
const MAX_BYTES = 8 * 1024 * 1024;
const MAX_WIDTH = 1600;
const WEBP_QUALITY = 75;
const TARGET_BYTES = 800 * 1024;

function authorized(req: NextRequest): boolean {
  const secret = process.env.BLOG_ADMIN_SECRET;
  return Boolean(secret && req.headers.get("x-admin-secret") === secret);
}

function toWebpName(name: string): string {
  return name.replace(/\.(png|jpe?g|webp)$/i, ".webp");
}

async function optimizeToWebp(input: Buffer): Promise<Buffer> {
  let quality = WEBP_QUALITY;
  let output = await sharp(input)
    .rotate()
    .resize({ width: MAX_WIDTH, withoutEnlargement: true })
    .webp({ quality, effort: 4 })
    .toBuffer();

  while (output.length > TARGET_BYTES && quality > 45) {
    quality -= 10;
    output = await sharp(input)
      .rotate()
      .resize({ width: MAX_WIDTH, withoutEnlargement: true })
      .webp({ quality, effort: 4 })
      .toBuffer();
  }
  return output;
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

  const rawName = String(body.name ?? "");
  const contentType = String(body.contentType ?? "image/png");
  if (!/^[a-z0-9][a-z0-9-]*\.(png|webp|jpe?g)$/i.test(rawName)) {
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

  let optimized: Buffer;
  try {
    optimized = await optimizeToWebp(buffer);
  } catch (err) {
    const message = err instanceof Error ? err.message : "image optimize failed";
    return NextResponse.json({ error: message }, { status: 400 });
  }

  const name = toWebpName(rawName.toLowerCase());

  // Idempotent: returns an "already exists" error after the first call.
  await sb.storage.createBucket(BUCKET, { public: true });

  const { error } = await sb.storage
    .from(BUCKET)
    .upload(name, optimized, { contentType: "image/webp", upsert: true });
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const { data } = sb.storage.from(BUCKET).getPublicUrl(name);
  return NextResponse.json({
    ok: true,
    url: data.publicUrl,
    bytes: optimized.length,
  });
}
