// Registry for the interactive "maker"/generator free tools (Canvas + AI).
// These live at /tools/<slug> as their own self-contained pages (separate from
// the data-driven /tools/[slug] transcript tools in lib/tools.ts).
// Used by the tools hub, the tools layout footer, the sitemap, and the nav.

export type MakerToolType = "canvas" | "ai" | "converter" | "viewer";

export interface MakerTool {
  slug: string;
  name: string;
  /** Short card blurb. */
  blurb: string;
  platform: "YouTube" | "TikTok" | "Instagram" | "General";
  type: MakerToolType;
}

export const MAKER_TOOLS: MakerTool[] = [
  {
    slug: "youtube-to-mp4",
    name: "YouTube to MP4 Converter",
    blurb: "Paste a YouTube link to preview the video and pick an MP4 quality from 144p to 1080p HD. Free, no sign-up.",
    platform: "YouTube",
    type: "converter",
  },
  {
    slug: "youtube-to-mp3",
    name: "YouTube to MP3 Converter",
    blurb: "Paste a YouTube link to preview the video and pick an MP3 audio quality from 64 to 320 kbps. Free, no sign-up.",
    platform: "YouTube",
    type: "converter",
  },
  {
    slug: "youtube-thumbnail-maker",
    name: "Free AI YouTube Thumbnail Maker",
    blurb: "Generate click-ready AI thumbnails from a title, portrait, and reference image. Multiple 16:9 variations, no sign-up.",
    platform: "YouTube",
    type: "ai",
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
    slug: "instagram-highlights-viewer",
    name: "Instagram Highlights Viewer",
    blurb: "Enter any public username to open and browse their story highlights anonymously. Free, no login.",
    platform: "Instagram",
    type: "viewer",
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
