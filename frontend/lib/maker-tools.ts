// Registry for the interactive "maker"/generator free tools (Canvas + AI).
// These live at /tools/<slug> as their own self-contained pages (separate from
// the data-driven /tools/[slug] transcript tools in lib/tools.ts).
// Used by the tools hub, the tools layout footer, the sitemap, and the nav.

export type MakerToolType = "canvas" | "ai";

export interface MakerTool {
  slug: string;
  name: string;
  /** Short card blurb. */
  blurb: string;
  platform: "YouTube" | "TikTok" | "General";
  type: MakerToolType;
}

export const MAKER_TOOLS: MakerTool[] = [
  {
    slug: "youtube-thumbnail-maker",
    name: "YouTube Thumbnail Maker",
    blurb: "Design click-worthy 1280×720 thumbnails in your browser. Templates, bold text, no watermark.",
    platform: "YouTube",
    type: "canvas",
  },
  {
    slug: "youtube-banner-maker",
    name: "YouTube Banner Maker",
    blurb: "Create 2560×1440 channel art with a safe-zone guide. Backgrounds, text, social icons.",
    platform: "YouTube",
    type: "canvas",
  },
  {
    slug: "youtube-hashtag-generator",
    name: "YouTube Hashtag Generator",
    blurb: "Generate 30 relevant YouTube hashtags grouped by trending, niche, and broad reach.",
    platform: "YouTube",
    type: "ai",
  },
  {
    slug: "youtube-title-generator",
    name: "YouTube Title Generator",
    blurb: "10 catchy, CTR-scored video titles in any style — clickbait, how-to, listicle, and more.",
    platform: "YouTube",
    type: "ai",
  },
  {
    slug: "youtube-description-generator",
    name: "YouTube Description Generator",
    blurb: "SEO-optimized descriptions with a hook, keywords, timestamps, CTA, and hashtags.",
    platform: "YouTube",
    type: "ai",
  },
  {
    slug: "youtube-shorts-idea-generator",
    name: "YouTube Shorts Idea Generator",
    blurb: "8 Shorts ideas with hooks, 60-second script outlines, and retention tips.",
    platform: "YouTube",
    type: "ai",
  },
  {
    slug: "tiktok-username-generator",
    name: "TikTok Username Generator",
    blurb: "15 available-style usernames in your vibe — aesthetic, funny, edgy, or cute.",
    platform: "TikTok",
    type: "ai",
  },
  {
    slug: "tiktok-hashtag-generator",
    name: "TikTok Hashtag Generator",
    blurb: "30 viral, niche, and FYP-boosting hashtags with a live character counter.",
    platform: "TikTok",
    type: "ai",
  },
  {
    slug: "tiktok-video-idea-generator",
    name: "TikTok Video Idea Generator",
    blurb: "8 video ideas with hooks, concepts, suggested sounds, and a virality score.",
    platform: "TikTok",
    type: "ai",
  },
  {
    slug: "social-media-bio-generator",
    name: "Social Media Bio Generator",
    blurb: "6 on-brand bios for YouTube, TikTok, Instagram, or X — within each platform's limit.",
    platform: "General",
    type: "ai",
  },
];

export const MAKER_TOOL_SLUGS = MAKER_TOOLS.map((t) => t.slug);

export function getMakerTool(slug: string): MakerTool | undefined {
  return MAKER_TOOLS.find((t) => t.slug === slug);
}
