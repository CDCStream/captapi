// Single source of truth for use-case (category) pages at /for/[slug].
// Programmatic SEO: one template, one data source. Add a use case here and it
// shows up on the hub, its own page, and the sitemap automatically.

export interface UseCase {
  slug: string; // URL: /for/{slug}
  audience: string; // e.g. "AI Startups"
  metaTitle: string;
  metaDescription: string;
  keyword: string; // primary target keyword
  h1: string;
  intro: string;
  builds: { title: string; desc: string }[]; // "what you can build"
  apiSlugs: string[]; // related /apis/[slug] for internal linking
  faqs: { q: string; a: string }[];
}

export const USE_CASES: Record<string, UseCase> = {
  "ai-startups": {
    slug: "ai-startups",
    audience: "AI Startups",
    metaTitle: "Video Data API for AI Startups & LLM Apps | Captapi",
    metaDescription:
      "Feed clean transcripts and summaries into your RAG pipeline, fine-tuning dataset, or video Q&A agent. One REST API for YouTube, TikTok, Instagram & Facebook.",
    keyword: "video data api for ai",
    h1: "The video data API for AI startups",
    intro:
      "Building RAG pipelines, fine-tuning datasets, or video Q&A agents? Captapi turns social video into clean, structured text your models can use — transcripts, AI summaries, comments and metadata from YouTube, TikTok, Instagram and Facebook, all behind one REST API.",
    builds: [
      { title: "RAG knowledge bases", desc: "Pull transcripts at scale and embed them into your vector store for grounded answers." },
      { title: "Video Q&A agents", desc: "Let users ask questions about any video — fetch the transcript on demand and answer." },
      { title: "Fine-tuning datasets", desc: "Collect clean, labelled transcript + metadata pairs across four platforms." },
      { title: "Content moderation", desc: "Summarize and classify video content before it reaches your users." },
    ],
    apiSlugs: ["youtube-transcript", "tiktok-transcript", "instagram-transcript", "youtube-summarizer"],
    faqs: [
      {
        q: "Can I use Captapi to build a RAG pipeline from videos?",
        a: "Yes. Call the transcript endpoint for any YouTube, TikTok, Instagram or Facebook video, get clean JSON text back, then chunk and embed it into your vector database.",
      },
      {
        q: "Do you return clean text suitable for LLMs?",
        a: "Yes — responses are structured JSON with plain-text transcripts and AI summaries, so you can feed them directly into embeddings or prompts without scraping or cleanup.",
      },
    ],
  },

  agencies: {
    slug: "agencies",
    audience: "Marketing Agencies",
    metaTitle: "Social Media Monitoring API for Agencies & Brands | Captapi",
    metaDescription:
      "Track competitor content, monitor brand mentions, and analyze sentiment across YouTube, TikTok, Instagram & Facebook with one social media data API.",
    keyword: "social media monitoring api",
    h1: "Social media data API for agencies & brands",
    intro:
      "Captapi gives agencies and brands a single API to track competitor content, monitor mentions, and analyze engagement across YouTube, TikTok, Instagram and Facebook — comments, summaries and metrics in clean JSON, ready for your dashboards and reports.",
    builds: [
      { title: "Competitor content tracking", desc: "Pull videos, summaries and engagement metrics to see what's working for rivals." },
      { title: "Brand & mention monitoring", desc: "Search and collect comments to surface what people say about a brand." },
      { title: "Sentiment analysis", desc: "Feed comments and transcripts into your NLP stack for sentiment at scale." },
      { title: "Automated reporting", desc: "Power client dashboards with structured engagement and performance data." },
    ],
    apiSlugs: ["youtube-comments", "tiktok-comments", "instagram-comments", "youtube-summarizer"],
    faqs: [
      {
        q: "Can I monitor competitors across platforms with one API?",
        a: "Yes. Captapi covers YouTube, TikTok, Instagram and Facebook through a single REST API, so you can collect content, comments and engagement metrics without juggling four integrations.",
      },
      {
        q: "Is the data ready for client reporting?",
        a: "Responses are clean JSON, so you can pipe engagement metrics, comments and summaries straight into your reporting tools and dashboards.",
      },
    ],
  },

  "content-creators": {
    slug: "content-creators",
    audience: "Content Creators",
    metaTitle: "Transcript & Summary API for Content Creators | Captapi",
    metaDescription:
      "Auto-generate timestamps, blog posts and social captions from your videos. Transcripts and AI summaries for YouTube, TikTok and Instagram via one API.",
    keyword: "transcript api for creators",
    h1: "Transcript & repurposing API for creators",
    intro:
      "Turn one video into a dozen assets. Captapi extracts transcripts and AI summaries from YouTube, TikTok and Instagram so you can auto-generate timestamps, blog posts, show notes and social captions — without copy-pasting or manual transcription.",
    builds: [
      { title: "Repurpose to blog posts", desc: "Convert a video transcript into a draft article in seconds." },
      { title: "Auto timestamps & chapters", desc: "Generate chapter markers and key moments from the transcript." },
      { title: "Social captions & threads", desc: "Summarize a video into captions, hooks and X/LinkedIn threads." },
      { title: "Searchable show notes", desc: "Publish clean, SEO-friendly transcripts alongside every episode." },
    ],
    apiSlugs: ["youtube-transcript", "youtube-summarizer", "tiktok-transcript", "instagram-transcript"],
    faqs: [
      {
        q: "Can I get a transcript of my own videos automatically?",
        a: "Yes. Send the video URL to Captapi's transcript endpoint and get clean text back, ready to repurpose into blogs, captions or show notes.",
      },
      {
        q: "Does it work for Shorts and Reels?",
        a: "Yes — Captapi supports YouTube (including Shorts), TikTok and Instagram Reels for transcripts and summaries.",
      },
    ],
  },

  researchers: {
    slug: "researchers",
    audience: "Researchers & Journalists",
    metaTitle: "Social Media Data API for Research & Journalism | Captapi",
    metaDescription:
      "Bulk-export comments, transcripts and metadata for trend analysis, OSINT and academic studies. One API for YouTube, TikTok, Instagram & Facebook.",
    keyword: "social media data for research",
    h1: "Social media data API for researchers & journalists",
    intro:
      "Captapi helps researchers and journalists collect public social data at scale — comments, transcripts, video details and engagement metrics across YouTube, TikTok, Instagram and Facebook — in clean JSON ready for analysis, with no scraping infrastructure to maintain.",
    builds: [
      { title: "Trend & discourse analysis", desc: "Bulk-collect comments and transcripts to study narratives over time." },
      { title: "OSINT investigations", desc: "Pull public metadata and engagement signals for verification work." },
      { title: "Academic datasets", desc: "Assemble structured, reproducible datasets across multiple platforms." },
      { title: "Misinformation tracking", desc: "Summarize and compare video claims and audience reactions." },
    ],
    apiSlugs: ["youtube-comments", "youtube-search", "instagram-comments", "youtube-channel-videos"],
    faqs: [
      {
        q: "Can I export comments in bulk for analysis?",
        a: "Yes. Captapi's comments endpoints return structured JSON you can collect at scale and load into your analysis pipeline or spreadsheet.",
      },
      {
        q: "Is this only public data?",
        a: "Captapi works exclusively with publicly accessible data. You are responsible for compliant use within your jurisdiction and institution's guidelines.",
      },
    ],
  },

  developers: {
    slug: "developers",
    audience: "Developers",
    metaTitle: "Social Media API for Developers | Captapi",
    metaDescription:
      "Add transcripts, summaries, comments and video details to your app with one REST API. No OAuth, no scraping. 100 free credits to start.",
    keyword: "social media api for developers",
    h1: "Social media data API for developers",
    intro:
      "Ship video-data features without building scrapers or wrangling four platform APIs. Captapi is a plain REST API — no OAuth, no quotas to negotiate — that returns transcripts, summaries, comments and video details from YouTube, TikTok, Instagram and Facebook as clean JSON.",
    builds: [
      { title: "Add video search & details", desc: "Embed search and metadata lookups into your product in minutes." },
      { title: "On-demand transcripts", desc: "Fetch transcripts when a user pastes a link — no pre-processing." },
      { title: "Engagement features", desc: "Surface comments and metrics inside your app from one endpoint." },
      { title: "Automations & workflows", desc: "Wire Captapi into Zapier-style flows, cron jobs or background workers." },
    ],
    apiSlugs: ["youtube-transcript", "youtube-video-details", "tiktok-video-details", "instagram-details"],
    faqs: [
      {
        q: "Do I need OAuth or per-platform API keys?",
        a: "No. One Captapi key works across YouTube, TikTok, Instagram and Facebook. We handle authentication, proxies, rate limits and retries for you.",
      },
      {
        q: "How fast can I integrate?",
        a: "Sign up, create a key, and make your first call in about 60 seconds. Every endpoint is a simple GET that returns clean JSON.",
      },
    ],
  },
};

export const USE_CASE_LIST: UseCase[] = Object.values(USE_CASES);
export const USE_CASE_SLUGS: string[] = Object.keys(USE_CASES);

export function getUseCase(slug: string): UseCase | undefined {
  return USE_CASES[slug];
}
