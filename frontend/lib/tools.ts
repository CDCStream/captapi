export interface Tool {
  slug: string;
  title: string;
  description: string;
  platform: string;
  apiEndpoint: string;
  faq: { q: string; a: string }[];
  /** Whether the live widget returns a transcript or an AI summary. */
  kind?: "transcript" | "summary";
  /** SEO keywords for <meta keywords> + content. */
  keywords?: string[];
  /** Example URL shown in the input placeholder. */
  urlPlaceholder?: string;
}

// Single source of truth for free tools — used by the tools hub, the
// /tools/[slug] pages, and the sitemap. Add a tool here and it shows up
// everywhere (page, listing, sitemap) automatically.
export const TOOLS: Record<string, Tool> = {
  "youtube-transcript": {
    slug: "youtube-transcript",
    title: "Free YouTube Transcript Extractor",
    description: "Get the full, timestamped transcript of any public YouTube video in seconds. Free, no sign-up — copy or download the text for subtitles, notes, or repurposing.",
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
    description: "Summarize any YouTube video with AI in seconds — get a concise overview, key bullet points, and the main topics. Free, no sign-up, copy or download the result.",
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
    description: "Extract speech and captions from any public TikTok video as clean, copyable text. Free and no sign-up — AI transcribes the audio when there are no captions.",
    platform: "TikTok",
    apiEndpoint: "/v1/tiktok/transcript",
    faq: [
      { q: "What if the TikTok has no captions?", a: "We use AI to transcribe the audio." },
    ],
  },
  "tiktok-summarizer": {
    slug: "tiktok-summarizer",
    title: "Free TikTok Video Summarizer",
    description: "Summarize any public TikTok video with AI in seconds — get the key takeaways, main points, and topics as copyable text. Free, no sign-up, no install.",
    platform: "TikTok",
    apiEndpoint: "/v1/tiktok/summarize",
    faq: [
      { q: "Does it work for private accounts?", a: "No — public TikToks only." },
    ],
  },
  "instagram-transcript": {
    slug: "instagram-transcript",
    title: "Free Instagram Reel Transcript",
    description: "Extract a clean, copyable transcript from any public Instagram Reel in seconds. Free, no sign-up — turn Reels into text for captions, notes, or content.",
    platform: "Instagram",
    apiEndpoint: "/v1/instagram/transcript",
    faq: [{ q: "Stories?", a: "No, Reels and Posts only." }],
  },
  "instagram-summarizer": {
    slug: "instagram-summarizer",
    title: "Free Instagram Reel Summarizer",
    description: "Summarize any public Instagram Reel with AI in seconds — get a short overview, key points, and topics as copyable text. Free, no sign-up required.",
    platform: "Instagram",
    apiEndpoint: "/v1/instagram/summarize",
    faq: [],
  },
  "facebook-transcript": {
    slug: "facebook-transcript",
    title: "Free Facebook Video Transcript",
    description: "Get a clean, timestamped transcript from any public Facebook video in seconds. Free, no sign-up — copy or download the text for subtitles, notes, or research.",
    platform: "Facebook",
    apiEndpoint: "/v1/facebook/transcript",
    faq: [],
  },
};

const URL_PLACEHOLDERS: Record<string, string> = {
  YouTube: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  TikTok: "https://www.tiktok.com/@user/video/1234567890",
  Instagram: "https://www.instagram.com/reel/Cxxxxxxxxxx/",
  Facebook: "https://www.facebook.com/watch/?v=1234567890",
};

// Fill derived fields (kind, keywords, urlPlaceholder) so each entry stays terse.
for (const t of Object.values(TOOLS)) {
  if (!t.kind) t.kind = t.apiEndpoint.includes("summarize") ? "summary" : "transcript";
  if (!t.urlPlaceholder) t.urlPlaceholder = URL_PLACEHOLDERS[t.platform];
  if (!t.keywords) {
    const p = t.platform.toLowerCase();
    t.keywords =
      t.kind === "summary"
        ? [`${p} summarizer`, `${p} video summary`, `summarize ${p} video`, `${p} ai summary`, `free ${p} summarizer`]
        : [`${p} transcript`, `${p} transcript generator`, `${p} to text`, `${p} caption extractor`, `free ${p} transcript`, `get ${p} transcript`];
  }
}

export const TOOL_LIST: Tool[] = Object.values(TOOLS);
export const TOOL_SLUGS: string[] = Object.keys(TOOLS);

export function getTool(slug: string): Tool | undefined {
  return TOOLS[slug];
}

/** Platform/kind-aware FAQ set (SEO/AEO/GEO), merged with tool-specific FAQs. */
export function toolFaqs(t: Tool): { q: string; a: string }[] {
  const p = t.platform;
  const isSummary = t.kind === "summary";
  const action = isSummary ? "summary" : "transcript";

  const base: { q: string; a: string }[] = isSummary
    ? [
        {
          q: `Is the ${p} summarizer free?`,
          a: `Yes. You can summarize a public ${p} video right here for free. For automation or higher volume, sign up for 100 free credits — no credit card required.`,
        },
        {
          q: `How does the ${p} AI summary work?`,
          a: `Paste a ${p} video URL and we transcribe it, then an AI model condenses it into a short summary, key bullet points, and the main topics in seconds.`,
        },
        {
          q: "What exactly do I get back?",
          a: "A concise summary, a list of key points, and the main topics — copyable with one click or downloadable as a .txt file.",
        },
      ]
    : [
        {
          q: `Is the ${p} transcript tool free?`,
          a: `Yes. Paste a public ${p} URL and get the full text for free. For programmatic access or higher volume, sign up for 100 free credits — no card required.`,
        },
        {
          q: `How do I get a transcript from a ${p} video?`,
          a: `Paste the video URL above and click Get transcript. We pull the captions or audio, convert them to clean text, and show a copyable transcript in seconds.`,
        },
        {
          q: "Can I copy or download the transcript?",
          a: "Yes — copy the full transcript to your clipboard with one click, or download it as a .txt file to use anywhere.",
        },
      ];

  const shared: { q: string; a: string }[] = [
    {
      q: "Does it work in any language?",
      a: `We auto-detect the spoken language and support dozens of languages, so creators and researchers in the US, UK, India, Brazil, Indonesia, Nigeria, and beyond can all use it.`,
    },
    {
      q: "Do I need an account or to install anything?",
      a: "No. The tool runs in your browser with no login or install. An account is only needed if you want to call the API programmatically.",
    },
    {
      q: `Does it work for long ${p} videos?`,
      a: "Yes, including long-form uploads. Very long videos may take a few extra seconds to process.",
    },
    {
      q: "Is my data private?",
      a: "We only fetch the public video you submit and don't sell your data. Results are briefly cached to keep the tool fast for everyone.",
    },
    {
      q: `What can I use a ${p} ${action} for?`,
      a: `Common uses include subtitles and captions, repurposing video into blog posts and social clips, study and research notes, translation, accessibility, and content analysis.`,
    },
    {
      q: "Can I automate this with an API?",
      a: `Yes. The same data is available via the Captapi REST API — a single \`${t.apiEndpoint}\` call returns clean JSON. It also works through MCP, our CLI, n8n, Make.com, and Apify.`,
    },
  ];

  // Merge tool-specific FAQs that aren't near-duplicates of the generated ones.
  const extra = t.faq.filter((f) => !/free|language|programmatically/i.test(f.q));
  return [...base, ...shared, ...extra];
}
