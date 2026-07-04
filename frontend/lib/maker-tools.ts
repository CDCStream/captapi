// Registry for the interactive "maker"/generator free tools (Canvas + AI).
// These live at /tools/<slug> as their own self-contained pages (separate from
// the data-driven /tools/[slug] transcript tools in lib/tools.ts).
// Used by the tools hub, the tools layout footer, the sitemap, and the nav.

export type MakerToolType = "canvas" | "ai" | "converter" | "viewer" | "downloader" | "reference" | "calculator";

export interface MakerTool {
  slug: string;
  name: string;
  /** Short card blurb. */
  blurb: string;
  platform: "YouTube" | "TikTok" | "Instagram" | "Facebook" | "Snapchat" | "Discord" | "Twitch" | "General";
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
    slug: "youtube-shorts-downloader",
    name: "YouTube Shorts Downloader",
    blurb: "Paste a YouTube Shorts link to preview it and pick an MP4 quality from 360p to 1080p HD. Free, no watermark.",
    platform: "YouTube",
    type: "downloader",
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
    slug: "youtube-name-generator",
    name: "YouTube Name Generator",
    blurb: "15 catchy, brandable channel name ideas from your niche. Pick personal or business and a style. AI, no sign-up.",
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
    slug: "tiktok-emojis",
    name: "TikTok Emojis",
    blurb: "All 46 secret TikTok emoji codes with meanings. Search and copy codes like [smile] in one click.",
    platform: "TikTok",
    type: "reference",
  },
  {
    slug: "instagram-highlights-viewer",
    name: "Instagram Highlights Viewer",
    blurb: "Enter any public username to open and browse their story highlights anonymously. Free, no login.",
    platform: "Instagram",
    type: "viewer",
  },
  {
    slug: "instagram-profile-viewer",
    name: "Instagram Profile Viewer",
    blurb: "Enter any public username to browse the profile photo, posts, reels, and highlights anonymously. Free, no login.",
    platform: "Instagram",
    type: "viewer",
  },
  {
    slug: "instagram-photo-downloader",
    name: "Instagram Photo Downloader",
    blurb: "Paste a public post or reel link to open and save the image in original quality. Free, no login.",
    platform: "Instagram",
    type: "downloader",
  },
  {
    slug: "social-media-bio-generator",
    name: "Social Media Bio Generator",
    blurb: "6 on-brand bios for YouTube, TikTok, Instagram, or X — within each platform's limit.",
    platform: "General",
    type: "ai",
  },
  {
    slug: "tiktok-coin-calculator",
    name: "TikTok Coin Calculator",
    blurb: "Convert TikTok coins to USD and back, see gift values, and estimate what creators earn from any gift. Free, always current.",
    platform: "TikTok",
    type: "calculator",
  },
  {
    slug: "best-time-to-post-on-tiktok",
    name: "Best Time to Post on TikTok",
    blurb: "Day-by-day posting schedule in your local time zone, backed by engagement data. Includes today's best slots.",
    platform: "TikTok",
    type: "reference",
  },
  {
    slug: "best-time-to-post-on-instagram",
    name: "Best Time to Post on Instagram",
    blurb: "The best times to post Reels, photos, and Stories every day of the week — shown in your local time zone.",
    platform: "Instagram",
    type: "reference",
  },
  {
    slug: "best-time-to-post-on-facebook",
    name: "Best Time to Post on Facebook",
    blurb: "Data-backed posting times for Facebook Pages and Reels, adjusted to your local time zone.",
    platform: "Facebook",
    type: "reference",
  },
  {
    slug: "best-time-to-post-on-youtube",
    name: "Best Time to Post on YouTube",
    blurb: "The best days and hours to upload videos and Shorts, shown in your local time zone.",
    platform: "YouTube",
    type: "reference",
  },
  {
    slug: "snapchat-planets",
    name: "Snapchat Planets Order & Meaning",
    blurb: "What each Snapchat Plus friend planet means, in order from Mercury to Neptune, with visuals.",
    platform: "Snapchat",
    type: "reference",
  },
  {
    slug: "discord-fonts",
    name: "Discord Fonts & Text Generator",
    blurb: "Turn text into bold, cursive, gothic, and 20+ styles you can paste into Discord, plus a markdown formatting cheat sheet.",
    platform: "Discord",
    type: "converter",
  },
  {
    slug: "youtube-thumbnail-downloader",
    name: "YouTube Thumbnail Downloader",
    blurb: "Grab any video's thumbnail in HD (1280×720) and every other size — plus the exact thumbnail dimensions YouTube uses.",
    platform: "YouTube",
    type: "downloader",
  },
  {
    slug: "engagement-rate-calculator",
    name: "Engagement Rate Calculator",
    blurb: "Calculate TikTok, Instagram, or YouTube engagement rate from likes, comments, and followers — with benchmarks by follower size.",
    platform: "General",
    type: "calculator",
  },
  {
    slug: "instagram-username-generator",
    name: "Instagram Username Generator",
    blurb: "15 available-style Instagram name ideas in your niche — aesthetic, minimal, or funny. AI-powered, no sign-up.",
    platform: "Instagram",
    type: "ai",
  },
  {
    slug: "screenshot-notification-checker",
    name: "Screenshot Notification Checker",
    blurb: "Does Instagram, Snapchat, TikTok, Facebook, or WhatsApp notify screenshots? Pick a platform and action for an instant answer.",
    platform: "General",
    type: "reference",
  },
  {
    slug: "tiktok-money-calculator",
    name: "TikTok Money Calculator",
    blurb: "Estimate what TikTok pays per view and per video from Creator Rewards, plus brand deal rates by follower count.",
    platform: "TikTok",
    type: "calculator",
  },
  {
    slug: "am-i-blocked",
    name: "Am I Blocked? Checker",
    blurb: "Answer a few quick questions to find out if someone blocked you on Instagram, Snapchat, or WhatsApp.",
    platform: "General",
    type: "reference",
  },
  {
    slug: "social-media-slang",
    name: "Social Media Slang Dictionary",
    blurb: "What does PMO, NFS, or the green dot mean? Search 60+ TikTok, Snapchat, Instagram, and Discord slang terms.",
    platform: "General",
    type: "reference",
  },
  {
    slug: "social-media-image-sizes",
    name: "Social Media Image Sizes",
    blurb: "Every 2026 dimension in one cheat sheet — Instagram posts and Stories, TikTok ratios, YouTube thumbnails and banners, and more.",
    platform: "General",
    type: "reference",
  },
  {
    slug: "twitch-emote-resizer",
    name: "Twitch Emote Resizer",
    blurb: "Resize any image to Twitch's 112, 56, and 28 px emote sizes plus Discord's 128 px — right in your browser, free.",
    platform: "Twitch",
    type: "converter",
  },
  {
    slug: "instagram-caption-generator",
    name: "Instagram Caption Generator",
    blurb: "10 scroll-stopping captions in your vibe — funny, aesthetic, short, or hard — with hashtags and emoji. AI, no sign-up.",
    platform: "Instagram",
    type: "ai",
  },
  {
    slug: "discord-bio-generator",
    name: "Discord Bio Generator",
    blurb: "6 About Me bios that fit Discord's 190-character limit, in your style — aesthetic, funny, edgy, or minimal.",
    platform: "Discord",
    type: "ai",
  },
];

export const MAKER_TOOL_SLUGS = MAKER_TOOLS.map((t) => t.slug);

export function getMakerTool(slug: string): MakerTool | undefined {
  return MAKER_TOOLS.find((t) => t.slug === slug);
}
