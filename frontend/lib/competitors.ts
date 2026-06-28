// Single source of truth for competitor "alternative" pages.
// Used by the /alternatives hub, /alternatives/[slug] pages, and the sitemap.
// Add a competitor here and it shows up everywhere automatically.
//
// IMPORTANT: competitor capability flags are best-effort, based on publicly
// available information. Where we are not certain, we use "varies" (rendered
// as "Varies") instead of a hard "no", and every page shows an "as of" note.

export type Cap = boolean | "varies";

export interface Competitor {
  slug: string; // URL: /alternatives/{slug}
  name: string; // brand name, e.g. "Supadata"
  domain: string; // e.g. "supadata.ai"
  targetKeyword: string; // primary keyword, e.g. "supadata alternative"
  focus: string; // one-line positioning of the competitor
  platforms: string; // platforms they cover (public info)
  intro: string; // 2-3 sentence intro paragraph
  transcripts: Cap;
  summaries: Cap;
  comments: Cap;
  freeTools: Cap;
  freeTier: string; // free tier note
  pricing: string; // pricing model note
  edge: string[]; // Captapi advantages
  faqs: { q: string; a: string }[];
}

// Captapi's own baseline used on every comparison table.
export const CAPTAPI = {
  platforms: "YouTube, TikTok, Instagram, Facebook",
  transcripts: true as Cap,
  summaries: true as Cap,
  comments: true as Cap,
  freeTools: true as Cap,
  freeTier: "100 credits, no card",
  pricing: "Pay-as-you-go credits, from $9/mo",
};

export const COMPARE_AS_OF = "May 2026";

export const COMPETITORS: Record<string, Competitor> = {
  supadata: {
    slug: "supadata",
    name: "Supadata",
    domain: "supadata.ai",
    targetKeyword: "supadata alternative",
    focus: "Video transcript API for YouTube, TikTok & Instagram",
    platforms: "YouTube, TikTok, Instagram",
    intro:
      "Supadata is a popular video transcript API. If you also need AI summaries, comments, engagement data, profiles, search, ad intelligence, commerce data, or broader platform coverage, Captapi gives you all of it behind a single REST API, with 100 free credits to start.",
    transcripts: true,
    summaries: "varies",
    comments: "varies",
    freeTools: true,
    freeTier: "Varies",
    pricing: "Subscription / credits",
    edge: [
      "Goes beyond the core video platforms with 29 social, commerce, ad library, and creator data sources",
      "Goes beyond transcripts: AI summaries, comments and engagement metrics from the same endpoints",
      "100 free credits on signup, no credit card required",
      "Free public tools you can try without an account",
      "Clean JSON with 24h response caching so repeat calls are free",
    ],
    faqs: [
      {
        q: "Is Captapi a good Supadata alternative?",
        a: "Yes. Captapi covers the same transcript use cases and adds broader social, commerce, ad library, and creator data endpoints — all through one REST API with pay-as-you-go credits.",
      },
      {
        q: "Can I migrate from Supadata easily?",
        a: "Captapi is a standard REST API that returns clean JSON. You sign up, create a key, and swap your transcript calls to the matching Captapi endpoint. You get 100 free credits to test before committing.",
      },
    ],
  },

  socialkit: {
    slug: "socialkit",
    name: "SocialKit",
    domain: "socialkit.dev",
    targetKeyword: "socialkit alternative",
    focus: "Transcript extractors and comment viewers",
    platforms: "YouTube, TikTok, Instagram",
    intro:
      "SocialKit offers transcript extractors and comment viewers. Captapi packages the same capabilities into one developer-first REST API across 29 platforms, with summaries, search, profiles, ad intelligence, commerce data, and engagement metrics included.",
    transcripts: true,
    summaries: "varies",
    comments: true,
    freeTools: true,
    freeTier: "Varies",
    pricing: "Varies",
    edge: [
      "One unified REST API instead of separate tools — transcripts, comments, summaries and details",
      "Covers 29 social, commerce, ad library, and creator data platforms",
      "Predictable credit pricing with 100 free credits to start",
      "Full developer docs and clean JSON responses",
      "Free public tools for quick one-off extractions",
    ],
    faqs: [
      {
        q: "Is Captapi a good SocialKit alternative?",
        a: "Yes. Captapi delivers transcripts, comments, summaries, video details, profiles, search, ad intelligence, and commerce data through a single REST API, designed for developers who want to build, not just view.",
      },
    ],
  },

  "scrape-creators": {
    slug: "scrape-creators",
    name: "Scrape Creators",
    domain: "scrapecreators.com",
    targetKeyword: "scrape creators alternative",
    focus: "Broad social media scraping API",
    platforms: "Instagram, TikTok, YouTube, Snapchat & more",
    intro:
      "Scrape Creators is a broad social scraping API. If your focus is video content intelligence — transcripts, AI summaries and comments — Captapi is purpose-built for it, with cleaner JSON and a generous free tier.",
    transcripts: true,
    summaries: "varies",
    comments: "varies",
    freeTools: true,
    freeTier: "Varies",
    pricing: "Credits",
    edge: [
      "Purpose-built for video content: transcripts, AI summaries, comments and engagement",
      "Simple, predictable per-call credit pricing",
      "100 free credits on signup — no credit card",
      "Free public tools (no account needed) for quick tasks",
      "Clean, consistent JSON with 24h caching",
    ],
    faqs: [
      {
        q: "Is Captapi a good Scrape Creators alternative?",
        a: "If you need transcripts, summaries, comments, profiles, search, engagement metrics, ad intelligence, or commerce data across many public platforms, Captapi is a focused, developer-friendly option with a free tier and free tools.",
      },
    ],
  },

  tikapi: {
    slug: "tikapi",
    name: "TikAPI",
    domain: "tikapi.io",
    targetKeyword: "tikapi alternative",
    focus: "TikTok-only API",
    platforms: "TikTok",
    intro:
      "TikAPI focuses on TikTok. Captapi gives you TikTok plus 28 more social, commerce, ad library, and creator data sources in one API — including transcripts, AI summaries, comments, search, profiles, commerce data, and engagement metrics.",
    transcripts: "varies",
    summaries: "varies",
    comments: "varies",
    freeTools: "varies",
    freeTier: "Varies",
    pricing: "Subscription",
    edge: [
      "29 platforms in one API — not TikTok only",
      "Transcripts, AI summaries, comments and video details from a single key",
      "100 free credits on signup, no credit card",
      "Free public tools you can try instantly",
      "Pay-as-you-go credits instead of fixed monthly tiers",
    ],
    faqs: [
      {
        q: "Is Captapi a good TikAPI alternative?",
        a: "Yes, especially if you need more than TikTok. Captapi covers 29 platforms with transcripts, summaries, comments, details, search, profiles, ad intelligence, and commerce data behind one REST API.",
      },
    ],
  },

  apify: {
    slug: "apify",
    name: "Apify",
    domain: "apify.com",
    targetKeyword: "apify alternative",
    focus: "General-purpose scraping platform & actor marketplace",
    platforms: "Any (via individual actors)",
    intro:
      "Apify is a powerful general-purpose scraping platform where you assemble and run individual \"actors\" per site. Captapi is the opposite trade-off: a single, ready-made REST API purpose-built for structured social, commerce, ad library, and creator data — transcripts, AI summaries, comments, search, profiles, commerce data, and engagement — with no actor selection, scaling or output-shape wrangling.",
    transcripts: "varies",
    summaries: "varies",
    comments: "varies",
    freeTools: true,
    freeTier: "$5 free credit",
    pricing: "Platform usage + per-actor",
    edge: [
      "One stable REST endpoint per task — no choosing, chaining or maintaining actors",
      "Consistent, normalized JSON shape across every endpoint (we handle actor drift for you)",
      "Built-in transcripts and AI summaries, not just raw scrapes",
      "Predictable per-call credits with 24h caching — repeat calls are free",
      "100 free credits and free public tools to start, no platform to learn",
    ],
    faqs: [
      {
        q: "Is Captapi a good Apify alternative?",
        a: "If your goal is social-video data specifically, yes. Apify gives you maximum flexibility but you pick, configure and maintain actors and normalize their output yourself. Captapi wraps that work into one REST API with a stable response shape, built-in transcripts/summaries, and resilient multi-actor fallbacks behind the scenes.",
      },
      {
        q: "Can I use Captapi on top of Apify?",
        a: "Captapi already runs on a curated set of battle-tested actors with automatic fallbacks, so you don't have to. You call one endpoint and get clean JSON — no Apify account, actor selection or scaling setup required.",
      },
    ],
  },

  ensembledata: {
    slug: "ensembledata",
    name: "EnsembleData",
    domain: "ensembledata.com",
    targetKeyword: "ensembledata alternative",
    focus: "Social media scraping API",
    platforms: "Instagram, TikTok, YouTube, Twitter, Snapchat",
    intro:
      "EnsembleData is a social media scraping API. Captapi specializes in structured social, commerce, ad library, and creator intelligence — transcripts, AI summaries, comments, search, profiles, commerce data, and engagement — with a simple credit model and a free tier.",
    transcripts: "varies",
    summaries: "varies",
    comments: "varies",
    freeTools: "varies",
    freeTier: "Varies",
    pricing: "Credits / units",
    edge: [
      "Focused on video content: transcripts, AI summaries, comments and engagement",
      "Covers 29 social, commerce, ad library, and creator data platforms",
      "100 free credits on signup — no credit card",
      "Free public tools without an account",
      "Clean JSON with 24h response caching",
    ],
    faqs: [
      {
        q: "Is Captapi a good EnsembleData alternative?",
        a: "If your use case needs transcripts, summaries, comments, search, profiles, commerce data, ad intelligence, or engagement metrics from public platforms, Captapi is a focused, developer-friendly alternative with a free tier and transparent credit pricing.",
      },
    ],
  },
};

export const COMPETITOR_LIST: Competitor[] = Object.values(COMPETITORS);
export const COMPETITOR_SLUGS: string[] = Object.keys(COMPETITORS);

export function getCompetitor(slug: string): Competitor | undefined {
  return COMPETITORS[slug];
}
