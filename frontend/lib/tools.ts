export interface Tool {
  slug: string;
  title: string;
  description: string;
  platform: string;
  apiEndpoint: string;
  faq: { q: string; a: string }[];
}

// Single source of truth for free tools — used by the tools hub, the
// /tools/[slug] pages, and the sitemap. Add a tool here and it shows up
// everywhere (page, listing, sitemap) automatically.
export const TOOLS: Record<string, Tool> = {
  "youtube-transcript": {
    slug: "youtube-transcript",
    title: "Free YouTube Transcript Extractor",
    description: "Get the full transcript of any YouTube video in seconds. Powered by Captapi.",
    platform: "YouTube",
    apiEndpoint: "/v1/youtube/transcript",
    faq: [
      { q: "Is this really free?", a: "Yes — you get 100 free credits when you sign up. Transcripts cost 1 credit each." },
      { q: "Does it work for any language?", a: "We support all languages auto-detected by YouTube captions." },
      { q: "Can I use it programmatically?", a: "Yes — just call our API directly. See docs." },
    ],
  },
  "youtube-summarizer": {
    slug: "youtube-summarizer",
    title: "Free YouTube Video Summarizer",
    description: "AI-powered summary, key points, and topics from any YouTube video.",
    platform: "YouTube",
    apiEndpoint: "/v1/youtube/summarize",
    faq: [
      { q: "What AI model do you use?", a: "GPT-4o-mini for the right balance of quality and cost." },
      { q: "How long are the summaries?", a: "2-3 paragraphs + 4-8 key bullet points." },
    ],
  },
  "tiktok-transcript": {
    slug: "tiktok-transcript",
    title: "Free TikTok Transcript Extractor",
    description: "Extract speech and captions from any TikTok video.",
    platform: "TikTok",
    apiEndpoint: "/v1/tiktok/transcript",
    faq: [
      { q: "What if the TikTok has no captions?", a: "We use AI to transcribe the audio." },
    ],
  },
  "tiktok-summarizer": {
    slug: "tiktok-summarizer",
    title: "Free TikTok Video Summarizer",
    description: "Get the gist of any TikTok in seconds.",
    platform: "TikTok",
    apiEndpoint: "/v1/tiktok/summarize",
    faq: [
      { q: "Does it work for private accounts?", a: "No — public TikToks only." },
    ],
  },
  "instagram-transcript": {
    slug: "instagram-transcript",
    title: "Free Instagram Reel Transcript",
    description: "Extract transcripts from public Instagram Reels.",
    platform: "Instagram",
    apiEndpoint: "/v1/instagram/transcript",
    faq: [{ q: "Stories?", a: "No, Reels and Posts only." }],
  },
  "instagram-summarizer": {
    slug: "instagram-summarizer",
    title: "Free Instagram Reel Summarizer",
    description: "AI summaries for Instagram Reels.",
    platform: "Instagram",
    apiEndpoint: "/v1/instagram/summarize",
    faq: [],
  },
  "facebook-transcript": {
    slug: "facebook-transcript",
    title: "Free Facebook Video Transcript",
    description: "Transcripts from public Facebook videos.",
    platform: "Facebook",
    apiEndpoint: "/v1/facebook/transcript",
    faq: [],
  },
};

export const TOOL_LIST: Tool[] = Object.values(TOOLS);
export const TOOL_SLUGS: string[] = Object.keys(TOOLS);

export function getTool(slug: string): Tool | undefined {
  return TOOLS[slug];
}
