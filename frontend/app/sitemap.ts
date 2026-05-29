import type { MetadataRoute } from "next";

const tools = [
  "youtube-transcript", "youtube-summarizer",
  "tiktok-transcript", "tiktok-summarizer",
  "instagram-transcript", "instagram-summarizer",
  "facebook-transcript",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
  const now = new Date();
  return [
    { url: `${base}/`, lastModified: now, priority: 1 },
    { url: `${base}/pricing`, lastModified: now, priority: 0.9 },
    { url: `${base}/docs`, lastModified: now, priority: 0.9 },
    { url: `${base}/tools`, lastModified: now, priority: 0.8 },
    ...tools.map((slug) => ({
      url: `${base}/tools/${slug}`,
      lastModified: now,
      priority: 0.7,
    })),
  ];
}
