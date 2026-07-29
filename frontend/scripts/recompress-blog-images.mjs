/**
 * Download oversized blog-images, compress with sharp, upsert to Supabase storage.
 * Usage: node scripts/recompress-blog-images.mjs  (from frontend/)
 *
 * Prefers SUPABASE_SERVICE_ROLE_KEY direct storage upload; falls back to
 * BLOG_ADMIN_SECRET + /api/blog/upload-image.
 * Loads frontend/.env.production, frontend/.env.local, backend/.env.
 */
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND = resolve(HERE, "..");

const SITE = (process.env.SITE || "https://captapi.com").replace(/\/$/, "");
const MAX_WIDTH = 1600;
const TARGET_BYTES = 800 * 1024;
const AHREFS_THRESHOLD = 1024 * 1024;
const BUCKET = "blog-images";
const PUBLIC_PREFIX =
  "https://auth.captapi.com/storage/v1/object/public/blog-images/";

function loadEnvFile(path) {
  if (!existsSync(path)) return;
  for (const line of readFileSync(path, "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
    const i = trimmed.indexOf("=");
    const key = trimmed.slice(0, i).trim();
    let val = trimmed.slice(i + 1).trim();
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    if (!process.env[key]) process.env[key] = val;
  }
}

loadEnvFile(resolve(FRONTEND, ".env.production"));
loadEnvFile(resolve(FRONTEND, ".env.local"));
loadEnvFile(resolve(FRONTEND, "../backend/.env"));

const SECRET = (process.env.BLOG_ADMIN_SECRET || "").trim();
const SUPABASE_URL = (
  process.env.NEXT_PUBLIC_SUPABASE_URL ||
  process.env.SUPABASE_URL ||
  ""
).trim();
const SERVICE_KEY = (process.env.SUPABASE_SERVICE_ROLE_KEY || "").trim();

const FALLBACK_NAMES = [
  "instagram-automation-cover.webp",
  "youtube-automation-cover.webp",
  "apify-alternatives-cover.webp",
  "ig-follower-export-tool-cover.webp",
  "tiktok-transcript-cover.webp",
  "tiktok-ad-library-cover.webp",
  "instagram-api-guide-cover.webp",
  "reddit-api-guide-cover.webp",
  "what-is-youtube-automation-cover.webp",
  "extract-audio-from-youtube-cover.webp",
  "linkedin-ad-library-cover.webp",
  "apify-alternatives-1.webp",
  "apify-alternatives-2.webp",
  "extract-audio-from-youtube-1.webp",
  "extract-audio-from-youtube-2.webp",
  "what-is-youtube-automation-1.webp",
  "tiktok-ad-library-2.webp",
  "instagram-automation-1.webp",
  "instagram-automation-2.webp",
  "youtube-automation-2.webp",
  "reddit-api-guide-1.webp",
  "reddit-api-guide-2.webp",
  "tiktok-transcript-1.webp",
  "tiktok-transcript-2.webp",
  "instagram-api-guide-2.webp",
  "ig-follower-export-tool-2.webp",
  "linkedin-ad-library-1.webp",
  "linkedin-ad-library-2.webp",
  "tiktok-ad-library-1.webp",
  "instagram-api-guide-1.webp",
  "ig-follower-export-tool-1.webp",
  "youtube-automation-1.webp",
];

async function listBucketNames() {
  if (!SUPABASE_URL || !SERVICE_KEY) return [];
  const names = [];
  let offset = 0;
  const limit = 100;
  while (true) {
    const res = await fetch(
      `${SUPABASE_URL}/storage/v1/object/list/${BUCKET}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${SERVICE_KEY}`,
          apikey: SERVICE_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prefix: "",
          limit,
          offset,
          sortBy: { column: "name", order: "asc" },
        }),
      },
    );
    if (!res.ok) {
      console.warn("bucket list failed:", res.status, await res.text());
      break;
    }
    const rows = await res.json();
    if (!Array.isArray(rows) || rows.length === 0) break;
    for (const row of rows) {
      if (row.name && /\.(webp|png|jpe?g)$/i.test(row.name) && row.id != null) {
        names.push(row.name);
      }
    }
    if (rows.length < limit) break;
    offset += limit;
  }
  return names;
}

async function optimize(input) {
  let quality = 75;
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

async function uploadDirect(name, bytes) {
  const res = await fetch(
    `${SUPABASE_URL}/storage/v1/object/${BUCKET}/${name}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${SERVICE_KEY}`,
        apikey: SERVICE_KEY,
        "Content-Type": "image/webp",
        "x-upsert": "true",
      },
      body: bytes,
    },
  );
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`storage upload ${res.status}: ${text}`);
  }
}

async function uploadViaApi(name, bytes) {
  const res = await fetch(`${SITE}/api/blog/upload-image`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-admin-secret": SECRET,
    },
    body: JSON.stringify({
      name,
      b64: bytes.toString("base64"),
      contentType: "image/webp",
    }),
  });
  const body = await res.json();
  if (!res.ok || !body.url) {
    throw new Error(body.error || `upload failed ${res.status}`);
  }
}

async function upload(name, bytes) {
  if (SUPABASE_URL && SERVICE_KEY) {
    await uploadDirect(name, bytes);
    return;
  }
  if (SECRET) {
    await uploadViaApi(name, bytes);
    return;
  }
  throw new Error("Need SUPABASE_SERVICE_ROLE_KEY or BLOG_ADMIN_SECRET");
}

async function headSize(url) {
  try {
    const res = await fetch(url, { method: "HEAD" });
    if (!res.ok) return null;
    const len = res.headers.get("content-length");
    return len ? Number(len) : null;
  } catch {
    return null;
  }
}

async function main() {
  if (!SERVICE_KEY && !SECRET) {
    console.error("Need SUPABASE_SERVICE_ROLE_KEY or BLOG_ADMIN_SECRET");
    process.exit(1);
  }

  const listed = await listBucketNames();
  const names = [...new Set(listed.length ? listed : FALLBACK_NAMES)]
    .filter((n) => n && !n.includes(" "))
    .sort();
  console.log(
    `candidates: ${names.length} (source=${listed.length ? "bucket" : "fallback"}) mode=${SERVICE_KEY ? "storage" : "api"}`,
  );

  let skipped = 0;
  let updated = 0;
  let failed = 0;

  for (const name of names) {
    const url = `${PUBLIC_PREFIX}${name}`;
    const before = await headSize(url);
    if (before != null && before < AHREFS_THRESHOLD) {
      skipped += 1;
      console.log(`skip ${name} (${(before / 1024).toFixed(0)} KB)`);
      continue;
    }

    try {
      const res = await fetch(url);
      if (!res.ok) {
        console.warn(`miss ${name}: HTTP ${res.status}`);
        failed += 1;
        continue;
      }
      const input = Buffer.from(await res.arrayBuffer());
      if (input.length < AHREFS_THRESHOLD) {
        skipped += 1;
        console.log(`skip ${name} (${(input.length / 1024).toFixed(0)} KB)`);
        continue;
      }
      const optimized = await optimize(input);
      const webpName = name.replace(/\.(png|jpe?g|webp)$/i, ".webp");
      await upload(webpName, optimized);
      updated += 1;
      console.log(
        `ok ${name}: ${(input.length / 1024).toFixed(0)} KB -> ${(optimized.length / 1024).toFixed(0)} KB`,
      );
    } catch (err) {
      failed += 1;
      console.error(`fail ${name}:`, err instanceof Error ? err.message : err);
    }
  }

  console.log(`done updated=${updated} skipped=${skipped} failed=${failed}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
