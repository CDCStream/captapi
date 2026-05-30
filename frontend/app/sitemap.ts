import type { MetadataRoute } from "next";
import { ALL_ENDPOINTS, SITE_URL } from "@/lib/api-catalog";
import { TOOL_SLUGS } from "@/lib/tools";
import { COMPETITOR_SLUGS } from "@/lib/competitors";
import { USE_CASE_SLUGS } from "@/lib/use-cases";
import { getServiceClient } from "@/lib/supabase/admin";

export const revalidate = 3600;

async function blogEntries(base: string): Promise<MetadataRoute.Sitemap> {
  const sb = getServiceClient();
  if (!sb) return [];
  const { data } = await sb
    .from("blog_posts")
    .select("slug, updated_at")
    .eq("status", "published");
  return (data ?? []).map((p: { slug: string; updated_at: string | null }) => ({
    url: `${base}/blog/${p.slug}`,
    lastModified: p.updated_at ? new Date(p.updated_at) : new Date(),
    changeFrequency: "monthly" as const,
    priority: 0.7,
  }));
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = SITE_URL;
  const now = new Date();

  const staticPages: MetadataRoute.Sitemap = [
    { url: `${base}/`, lastModified: now, changeFrequency: "weekly", priority: 1 },
    { url: `${base}/apis`, lastModified: now, changeFrequency: "weekly", priority: 0.9 },
    { url: `${base}/pricing`, lastModified: now, changeFrequency: "monthly", priority: 0.9 },
    { url: `${base}/docs`, lastModified: now, changeFrequency: "weekly", priority: 0.8 },
    { url: `${base}/tools`, lastModified: now, changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/alternatives`, lastModified: now, changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/for`, lastModified: now, changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/blog`, lastModified: now, changeFrequency: "daily", priority: 0.8 },
    { url: `${base}/legal/terms`, lastModified: now, changeFrequency: "yearly", priority: 0.3 },
    { url: `${base}/legal/privacy`, lastModified: now, changeFrequency: "yearly", priority: 0.3 },
  ];

  const apiPages: MetadataRoute.Sitemap = ALL_ENDPOINTS.map((ep) => ({
    url: `${base}/apis/${ep.slug}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: 0.7,
  }));

  const toolPages: MetadataRoute.Sitemap = TOOL_SLUGS.map((slug) => ({
    url: `${base}/tools/${slug}`,
    lastModified: now,
    changeFrequency: "monthly",
    priority: 0.6,
  }));

  const alternativePages: MetadataRoute.Sitemap = COMPETITOR_SLUGS.map((slug) => ({
    url: `${base}/alternatives/${slug}`,
    lastModified: now,
    changeFrequency: "monthly",
    priority: 0.7,
  }));

  const useCasePages: MetadataRoute.Sitemap = USE_CASE_SLUGS.map((slug) => ({
    url: `${base}/for/${slug}`,
    lastModified: now,
    changeFrequency: "monthly",
    priority: 0.7,
  }));

  const blogPages = await blogEntries(base);

  return [...staticPages, ...apiPages, ...toolPages, ...alternativePages, ...useCasePages, ...blogPages];
}
