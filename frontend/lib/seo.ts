// Shared SEO/GEO helpers: canonical-aware metadata + JSON-LD builders.
// Single source of truth so every marketing page ships consistent
// openGraph/twitter/canonical tags and structured data.
import type { Metadata } from "next";
import { SITE_URL } from "./api-catalog";

/** Resolve a path (or pass-through absolute URL) to an absolute production URL. */
export function absoluteUrl(path = "/"): string {
  if (/^https?:\/\//.test(path)) return path;
  return `${SITE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export const DEFAULT_OG_IMAGE = `${SITE_URL}/opengraph-image`;

// Freshness signal: bump when catalog / marketing content meaningfully changes.
// Used for dateModified JSON-LD + sitemap lastModified on programmatic pages.
export const CONTENT_UPDATED = "2026-06-04";
export const CONTENT_UPDATED_DATE = new Date(CONTENT_UPDATED);

export interface PageMetaInput {
  title: string;
  description: string;
  path: string;
  ogType?: "website" | "article";
  image?: string;
  keywords?: string[];
  publishedTime?: string;
  modifiedTime?: string;
}

/** Build a complete Metadata object with canonical + OpenGraph + Twitter. */
export function buildMetadata(input: PageMetaInput): Metadata {
  const url = absoluteUrl(input.path);
  const image = input.image ? absoluteUrl(input.image) : DEFAULT_OG_IMAGE;
  return {
    title: { absolute: input.title },
    description: input.description,
    keywords: input.keywords,
    alternates: { canonical: url },
    openGraph: {
      title: input.title,
      description: input.description,
      url,
      siteName: "Captapi",
      type: input.ogType ?? "website",
      images: [image],
      ...(input.publishedTime ? { publishedTime: input.publishedTime } : {}),
      ...(input.modifiedTime ? { modifiedTime: input.modifiedTime } : {}),
    },
    twitter: {
      card: "summary_large_image",
      title: input.title,
      description: input.description,
      images: [image],
    },
  };
}

/** Standard BreadcrumbList JSON-LD from [name, path] pairs. */
export function breadcrumbLd(items: { name: string; path: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: it.name,
      item: absoluteUrl(it.path),
    })),
  };
}

/** FAQPage JSON-LD from question/answer pairs. */
export function faqLd(faqs: { q: string; a: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };
}
