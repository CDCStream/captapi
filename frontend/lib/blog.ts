import { SITE_URL } from "@/lib/api-catalog";

export const DEFAULT_BLOG_IMAGE = `${SITE_URL}/opengraph-image`;

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

export function normalizeImageUrl(value: string | null | undefined): string {
  const raw = (value || "").trim();
  if (!raw || raw.startsWith("data:") || raw.startsWith("blob:")) return "";

  try {
    const url = new URL(raw, SITE_URL);
    if (url.pathname === "/_next/image") {
      const nested = url.searchParams.get("url");
      return normalizeImageUrl(nested);
    }
    if (url.origin === SITE_URL && url.pathname === "/opengraph-image") {
      return DEFAULT_BLOG_IMAGE;
    }
    // Metadata opengraph-image files are not directly fetchable; serve the
    // identical cover from the real API route instead.
    const cover = url.pathname.match(/^\/blog\/([^/]+)\/opengraph-image$/);
    if (url.origin === SITE_URL && cover) {
      return `${SITE_URL}/api/blog/cover/${cover[1]}`;
    }
    return url.toString();
  } catch {
    return "";
  }
}

export function normalizeContentImageUrls(content: string): string {
  return (content || "").replace(
    /\s(src|srcset)=["']([^"']+)["']/gi,
    (match, attr: string, value: string) => {
      if (attr.toLowerCase() === "srcset") {
        const normalizedSet = value
          .split(",")
          .map((part) => {
            const [url, descriptor] = part.trim().split(/\s+/, 2);
            const normalized = normalizeImageUrl(url);
            return normalized ? [normalized, descriptor].filter(Boolean).join(" ") : "";
          })
          .filter(Boolean)
          .join(", ");
        return normalizedSet ? ` ${attr}="${normalizedSet}"` : "";
      }
      const normalized = normalizeImageUrl(value);
      return normalized ? ` ${attr}="${normalized}"` : "";
    },
  );
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
  const content = normalizeContentImageUrls(row.content ?? "");
  const now = new Date().toISOString();
  return {
    slug: row.slug,
    title: row.title,
    description: row.description ?? "",
    content,
    author: row.author || "Outrank",
    image: normalizeImageUrl(row.image),
    tags: row.tags ?? [],
    status: row.status || "published",
    publishedAt: row.published_at ?? row.created_at ?? now,
    updatedAt: row.updated_at ?? row.published_at ?? now,
    readingTime: readingTime(content),
  };
}

// Public IndexNow key — published at /<key>.txt (NOT a secret by design).
export const INDEXNOW_KEY = "7c3e1a9f4b2d486e8a05f1c6d92b3e74";

/**
 * Submit specific URLs to IndexNow (Bing, Yandex, Seznam, Naver…).
 * The legacy Google/Bing `?sitemap=` ping endpoints were both deprecated,
 * so IndexNow is the only working instant-notification protocol now.
 * Google does not support IndexNow — it relies on the sitemap + crawl.
 * Never throws; indexing notifications are best-effort.
 */
export async function submitToIndexNow(urls: string[]): Promise<number | null> {
  const list = Array.from(new Set(urls.filter(Boolean)));
  if (!list.length) return null;
  let host: string;
  try {
    host = new URL(SITE_URL).host;
  } catch {
    return null;
  }
  try {
    const res = await fetch("https://api.indexnow.org/indexnow", {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        host,
        key: INDEXNOW_KEY,
        keyLocation: `${SITE_URL}/${INDEXNOW_KEY}.txt`,
        urlList: list,
      }),
    });
    return res.status;
  } catch {
    // ignore — pinging is non-critical
    return null;
  }
}

/**
 * Notify search engines about new/updated blog content. Always includes the
 * blog index so listing pages refresh too. Never throws.
 */
export async function pingSearchEngines(urls: string[] = []): Promise<void> {
  await submitToIndexNow([...urls, `${SITE_URL}/blog`]);
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
