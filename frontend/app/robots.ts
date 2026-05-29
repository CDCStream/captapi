import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/api-catalog";

// Block private/non-content areas everywhere.
const DISALLOW = ["/dashboard/", "/auth/", "/login", "/signup", "/api/"];

// AI / answer-engine crawlers we explicitly welcome (GEO / AEO).
const AI_BOTS = [
  "GPTBot",
  "OAI-SearchBot",
  "ChatGPT-User",
  "ClaudeBot",
  "Claude-Web",
  "anthropic-ai",
  "PerplexityBot",
  "Perplexity-User",
  "Google-Extended",
  "Applebot-Extended",
  "CCBot",
  "Bytespider",
  "Meta-ExternalAgent",
];

export default function robots(): MetadataRoute.Robots {
  const base = SITE_URL;
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: DISALLOW },
      ...AI_BOTS.map((bot) => ({ userAgent: bot, allow: "/", disallow: DISALLOW })),
    ],
    sitemap: `${base}/sitemap.xml`,
    host: base,
  };
}
