import { SITE_URL } from "@/lib/api-catalog";

export interface BlogPostRow {
  id?: string;
  slug: string;
  title: string;
  description?: string | null;
  content?: string | null;
  image?: string | null;
  tags?: string[] | null;
  author?: string | null;
  status?: string | null;
  published_at?: string | null;
  updated_at?: string | null;
  created_at?: string | null;
}

export interface BlogPost {
  slug: string;
  title: string;
  description: string;
  content: string;
  author: string;
  image: string;
  tags: string[];
  status: string;
  publishedAt: string;
  updatedAt: string;
  readingTime: number;
}

/** URL-safe slug from arbitrary text. */
export function slugify(input: string): string {
  const s = (input || "")
    .toLowerCase()
    .trim()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 96);
  return s || "post";
}

export function stripHtml(html: string): string {
  return (html || "")
    .replace(/<[^>]*>/g, " ")
    .replace(/&[a-z]+;/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** Estimated reading time in minutes (200 wpm). */
export function readingTime(html: string): number {
  const words = stripHtml(html).split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 200));
}

/** First non-empty string value among the given keys. */
export function pickString(obj: Record<string, unknown>, keys: string[]): string {
  for (const k of keys) {
    const v = obj?.[k];
    if (typeof v === "string" && v.trim()) return v.trim();
  }
  return "";
}

/** First array-of-strings value among the given keys (also splits CSV strings). */
export function pickArray(obj: Record<string, unknown>, keys: string[]): string[] {
  for (const k of keys) {
    const v = obj?.[k];
    if (Array.isArray(v)) {
      return v.map((x) => String(x).trim()).filter(Boolean);
    }
    if (typeof v === "string" && v.trim()) {
      return v
        .split(",")
        .map((x) => x.trim())
        .filter(Boolean);
    }
  }
  return [];
}

/** Normalise a raw DB row into a typed, render-ready blog post. */
export function parseBlogPost(row: BlogPostRow): BlogPost {
  const content = row.content ?? "";
  const now = new Date().toISOString();
  return {
    slug: row.slug,
    title: row.title,
    description: row.description ?? "",
    content,
    author: row.author || "Outrank",
    image: row.image ?? "",
    tags: row.tags ?? [],
    status: row.status || "published",
    publishedAt: row.published_at ?? row.created_at ?? now,
    updatedAt: row.updated_at ?? row.published_at ?? now,
    readingTime: readingTime(content),
  };
}

/** Best-effort sitemap ping to Google & Bing. Never throws. */
export async function pingSearchEngines(): Promise<void> {
  const sitemap = encodeURIComponent(`${SITE_URL}/sitemap.xml`);
  const urls = [
    `https://www.google.com/ping?sitemap=${sitemap}`,
    `https://www.bing.com/ping?sitemap=${sitemap}`,
  ];
  try {
    await Promise.allSettled(urls.map((u) => fetch(u, { method: "GET" })));
  } catch {
    // ignore — pinging is non-critical
  }
}

export function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return "";
  }
}
