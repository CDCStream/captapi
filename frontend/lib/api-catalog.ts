// Central catalog of every Captapi endpoint.
// Drives the landing "One API. Every platform." section, the /apis index,
// and the programmatic SEO (pSEO) detail pages at /apis/[slug].
//
// Content (taglines, descriptions, params, FAQs, example responses) is generated
// from a small declarative spec so every endpoint gets a unique, answer-first
// page that is SEO / GEO / AEO friendly without hand-writing 34 pages.

export type PlatformId = "youtube" | "tiktok" | "instagram" | "facebook";

export type Category =
  | "transcript"
  | "summarize"
  | "details"
  | "comments"
  | "channel"
  | "search"
  | "list"
  | "download";

export interface ApiParam {
  name: string;
  type: string;
  required: boolean;
  description: string;
}

export interface FaqItem {
  q: string;
  a: string;
}

export interface ResponseField {
  name: string;
  desc: string;
}

export interface ResponseGroup {
  title: string;
  note?: string;
  fields: ResponseField[];
}

export interface UseCase {
  title: string;
  desc: string;
}

export interface ApiEndpoint {
  slug: string;
  platform: PlatformId;
  /** Full marketing name, e.g. "YouTube Transcript API" */
  name: string;
  /** Short label used inside grouped cards, e.g. "Transcript" */
  shortName: string;
  category: Category;
  method: "GET" | "POST";
  path: string;
  /**
   * Typical credit cost of a standard request. For list/search/comments
   * endpoints this is the cost at the default result count (a fixed average so
   * users know roughly what a call consumes); actual billing scales with the
   * number of results returned at `creditsPerResult`.
   */
  credits: number;
  /** Credits billed per result for list/search/comments endpoints. */
  creditsPerResult?: number;
  /** Optional override for the "what you get" bullet list. */
  delivers?: string[];
}

export interface PlatformGroup {
  id: PlatformId;
  name: string;
  blurb: string;
  /** lucide-react icon name (resolved in components) */
  icon: "youtube" | "music" | "instagram" | "facebook";
  /** brand color class for the icon */
  color: string;
  exampleUrl: string;
  endpoints: ApiEndpoint[];
}

export const SITE_URL =
  process.env.NEXT_PUBLIC_APP_URL?.replace(/\/$/, "") || "https://captapi.com";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "https://api.captapi.com";

/**
 * Human-friendly credit cost label for an endpoint. `credits` already holds the
 * typical cost of a standard request (for list endpoints, the cost at the
 * default result count), so we display a single fixed number everywhere.
 */
export function creditLabel(e: Pick<ApiEndpoint, "credits">): string {
  return `${e.credits} credit${e.credits === 1 ? "" : "s"}`;
}

const PLATFORM_LABEL: Record<PlatformId, string> = {
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  facebook: "Facebook",
};

// ---------------------------------------------------------------------------
// Raw spec — kept terse; everything else is derived.
// ---------------------------------------------------------------------------

type Spec = Omit<ApiEndpoint, "platform">;

const YOUTUBE: Spec[] = [
  { slug: "youtube-transcript", name: "YouTube Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/youtube/transcript", credits: 2 },
  { slug: "youtube-summarizer", name: "YouTube Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/youtube/summarize", credits: 4 },
  { slug: "youtube-video-details", name: "YouTube Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/youtube/video-details", credits: 1 },
  { slug: "youtube-comments", name: "YouTube Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/youtube/comments", credits: 20, creditsPerResult: 0.4 },
  { slug: "youtube-channel-details", name: "YouTube Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/youtube/channel-details", credits: 1 },
  { slug: "youtube-search", name: "YouTube Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/youtube/search", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-channel-videos", name: "YouTube Channel Videos API", shortName: "Channel Videos", category: "list", method: "GET", path: "/v1/youtube/channel-videos", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-playlist-videos", name: "YouTube Playlist Videos API", shortName: "Playlist Videos", category: "list", method: "GET", path: "/v1/youtube/playlist-videos", credits: 50, creditsPerResult: 1 },
  { slug: "youtube-video-download", name: "YouTube Video Download API", shortName: "Video Download", category: "download", method: "GET", path: "/v1/youtube/video-download", credits: 3 },
  { slug: "youtube-shorts-transcript", name: "YouTube Shorts Transcript API", shortName: "Shorts Transcript", category: "transcript", method: "GET", path: "/v1/youtube/shorts/transcript", credits: 2 },
  { slug: "youtube-shorts-summarizer", name: "YouTube Shorts Summarizer API", shortName: "Shorts Summarizer", category: "summarize", method: "GET", path: "/v1/youtube/shorts/summarize", credits: 4 },
  { slug: "youtube-shorts-stats", name: "YouTube Shorts Stats API", shortName: "Shorts Stats", category: "details", method: "GET", path: "/v1/youtube/shorts/video-details", credits: 1 },
  { slug: "youtube-shorts-comments", name: "YouTube Shorts Comments API", shortName: "Shorts Comments", category: "comments", method: "GET", path: "/v1/youtube/shorts/comments", credits: 20, creditsPerResult: 0.4 },
  { slug: "youtube-channel-shorts", name: "YouTube Channel Shorts API", shortName: "Channel Shorts", category: "list", method: "GET", path: "/v1/youtube/channel-shorts", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-channel-streams", name: "YouTube Channel Streams API", shortName: "Channel Streams", category: "list", method: "GET", path: "/v1/youtube/channel-streams", credits: 20, creditsPerResult: 1 },
  { slug: "youtube-hashtag-search", name: "YouTube Hashtag Search API", shortName: "Hashtag Search", category: "search", method: "GET", path: "/v1/youtube/hashtag-search", credits: 20, creditsPerResult: 1 },
];

const TIKTOK: Spec[] = [
  { slug: "tiktok-transcript", name: "TikTok Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/tiktok/transcript", credits: 2 },
  { slug: "tiktok-summarizer", name: "TikTok Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/tiktok/summarize", credits: 4 },
  { slug: "tiktok-video-details", name: "TikTok Video Details API", shortName: "Video Details", category: "details", method: "GET", path: "/v1/tiktok/video-details", credits: 1 },
  { slug: "tiktok-comments", name: "TikTok Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/tiktok/comments", credits: 10, creditsPerResult: 0.2 },
  { slug: "tiktok-channel-details", name: "TikTok Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/tiktok/channel-details", credits: 1 },
  { slug: "tiktok-search", name: "TikTok Search API", shortName: "Search", category: "search", method: "GET", path: "/v1/tiktok/search", credits: 14, creditsPerResult: 0.7 },
  { slug: "tiktok-video-download", name: "TikTok Video Download API", shortName: "Video Download", category: "download", method: "GET", path: "/v1/tiktok/video-download", credits: 3 },
  { slug: "tiktok-channel-posts", name: "TikTok Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/tiktok/channel-posts", credits: 14, creditsPerResult: 0.7 },
  { slug: "tiktok-comment-replies", name: "TikTok Comment Replies API", shortName: "Comment Replies", category: "comments", method: "GET", path: "/v1/tiktok/comment-replies", credits: 50 },
  { slug: "tiktok-user-followers", name: "TikTok User Followers API", shortName: "User Followers", category: "list", method: "GET", path: "/v1/tiktok/user-followers", credits: 20, creditsPerResult: 0.4 },
  { slug: "tiktok-user-followings", name: "TikTok User Followings API", shortName: "User Followings", category: "list", method: "GET", path: "/v1/tiktok/user-followings", credits: 20, creditsPerResult: 0.4 },
  { slug: "tiktok-music-posts", name: "TikTok Music Posts API", shortName: "Music Posts", category: "list", method: "GET", path: "/v1/tiktok/music-posts", credits: 32, creditsPerResult: 1.6 },
];

const INSTAGRAM: Spec[] = [
  { slug: "instagram-transcript", name: "Instagram Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/instagram/transcript", credits: 2 },
  { slug: "instagram-summarizer", name: "Instagram Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/instagram/summarize", credits: 4 },
  { slug: "instagram-details", name: "Instagram Details API", shortName: "Details", category: "details", method: "GET", path: "/v1/instagram/details", credits: 1 },
  { slug: "instagram-comments", name: "Instagram Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/instagram/comments", credits: 45, creditsPerResult: 0.9 },
  { slug: "instagram-channel-details", name: "Instagram Channel Details API", shortName: "Channel Details", category: "channel", method: "GET", path: "/v1/instagram/channel-details", credits: 1 },
  { slug: "instagram-channel-posts", name: "Instagram Channel Posts API", shortName: "Channel Posts", category: "list", method: "GET", path: "/v1/instagram/channel-posts", credits: 12, creditsPerResult: 0.6 },
  { slug: "instagram-channel-reels", name: "Instagram Channel Reels API", shortName: "Channel Reels", category: "list", method: "GET", path: "/v1/instagram/channel-reels", credits: 12, creditsPerResult: 0.6 },
  { slug: "instagram-reels-search", name: "Instagram Reels Search API", shortName: "Reels Search", category: "search", method: "GET", path: "/v1/instagram/reels-search", credits: 12, creditsPerResult: 0.6 },
  { slug: "instagram-video-download", name: "Instagram Video Download API", shortName: "Video Download", category: "download", method: "GET", path: "/v1/instagram/video-download", credits: 3 },
  { slug: "instagram-tagged-posts", name: "Instagram Tagged Posts API", shortName: "Tagged Posts", category: "list", method: "GET", path: "/v1/instagram/tagged-posts", credits: 18, creditsPerResult: 0.9 },
  { slug: "instagram-music-posts", name: "Instagram Music Posts API", shortName: "Music Posts", category: "list", method: "GET", path: "/v1/instagram/music-posts", credits: 18, creditsPerResult: 0.9 },
];

const FACEBOOK: Spec[] = [
  { slug: "facebook-details", name: "Facebook Details API", shortName: "Details", category: "details", method: "GET", path: "/v1/facebook/details", credits: 1 },
  { slug: "facebook-transcript", name: "Facebook Transcript API", shortName: "Transcript", category: "transcript", method: "GET", path: "/v1/facebook/transcript", credits: 2 },
  { slug: "facebook-summarizer", name: "Facebook Summarizer API", shortName: "Summarizer", category: "summarize", method: "GET", path: "/v1/facebook/summarize", credits: 4 },
  { slug: "facebook-comments", name: "Facebook Comments API", shortName: "Comments", category: "comments", method: "GET", path: "/v1/facebook/comments", credits: 30, creditsPerResult: 0.6 },
  { slug: "facebook-page-details", name: "Facebook Page Details API", shortName: "Page Details", category: "channel", method: "GET", path: "/v1/facebook/page-details", credits: 1 },
];

export const PLATFORM_GROUPS: PlatformGroup[] = [
  {
    id: "youtube",
    name: "YouTube & Shorts",
    blurb: "Extract transcripts, summaries, stats, comments, and more from YouTube videos and Shorts.",
    icon: "youtube",
    color: "text-red-500",
    exampleUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    endpoints: YOUTUBE.map((s) => ({ ...s, platform: "youtube" as const })),
  },
  {
    id: "tiktok",
    name: "TikTok",
    blurb: "Analyze TikTok videos with transcripts, summaries, engagement metrics, and comments.",
    icon: "music",
    color: "text-pink-500",
    exampleUrl: "https://www.tiktok.com/@username/video/7311234567890123456",
    endpoints: TIKTOK.map((s) => ({ ...s, platform: "tiktok" as const })),
  },
  {
    id: "instagram",
    name: "Instagram Reels",
    blurb: "Extract data from Instagram Reels and posts including transcripts and profile analytics.",
    icon: "instagram",
    color: "text-fuchsia-500",
    exampleUrl: "https://www.instagram.com/reel/CzKZqfdN5j8/",
    endpoints: INSTAGRAM.map((s) => ({ ...s, platform: "instagram" as const })),
  },
  {
    id: "facebook",
    name: "Facebook",
    blurb: "Pull details, transcripts, summaries, and comments from public Facebook videos and pages.",
    icon: "facebook",
    color: "text-blue-600",
    exampleUrl: "https://www.facebook.com/watch/?v=1234567890123456",
    endpoints: FACEBOOK.map((s) => ({ ...s, platform: "facebook" as const })),
  },
];

export const ALL_ENDPOINTS: ApiEndpoint[] = PLATFORM_GROUPS.flatMap(
  (g) => g.endpoints,
);

export function getEndpoint(slug: string): ApiEndpoint | undefined {
  return ALL_ENDPOINTS.find((e) => e.slug === slug);
}

export function getGroup(id: PlatformId): PlatformGroup {
  return PLATFORM_GROUPS.find((g) => g.id === id)!;
}

export function relatedEndpoints(slug: string, max = 6): ApiEndpoint[] {
  const ep = getEndpoint(slug);
  if (!ep) return [];
  return getGroup(ep.platform)
    .endpoints.filter((e) => e.slug !== slug)
    .slice(0, max);
}

// ---------------------------------------------------------------------------
// Derived content
// ---------------------------------------------------------------------------

const ACTION: Record<Category, string> = {
  transcript: "extract the full, timestamped transcript",
  summarize: "generate an AI summary with key points and topics",
  details: "fetch full metadata and engagement stats",
  comments: "pull comments with author, text, likes, and replies",
  channel: "fetch profile/channel details and audience stats",
  search: "search and return matching results",
  list: "list items in bulk with metadata",
  download: "get a direct, no-watermark download URL",
};

export function platformLabel(p: PlatformId): string {
  return PLATFORM_LABEL[p];
}

export function tagline(ep: ApiEndpoint): string {
  const platform = PLATFORM_LABEL[ep.platform];
  switch (ep.category) {
    case "transcript":
      return `Extract timestamped transcripts from any public ${platform} video in a single request.`;
    case "summarize":
      return `Turn any ${platform} video into an AI summary with key points, topics, and sentiment.`;
    case "details":
      return `Get full ${platform} video metadata — title, views, likes, duration, and more.`;
    case "comments":
      return `Pull ${platform} comments at scale with author, text, likes, and reply threads.`;
    case "channel":
      return `Fetch ${platform} profile data — follower counts, bio, verification, and stats.`;
    case "search":
      return `Search ${platform} programmatically and get structured, ranked results.`;
    case "list":
      return `Bulk-list ${platform} content with full metadata for each item.`;
    case "download":
      return `Get a direct, watermark-free download URL for any public ${platform} video.`;
  }
}

export function longDescription(ep: ApiEndpoint): string {
  const platform = PLATFORM_LABEL[ep.platform];
  return `The ${ep.name} lets you ${ACTION[ep.category]} from ${platform} with a single REST call. No OAuth, no scraping infrastructure, and no platform SDKs — send the URL, get clean structured JSON back. Results are cached for 24 hours, so repeat lookups are instant and free.`;
}

export function delivers(ep: ApiEndpoint): string[] {
  if (ep.delivers) return ep.delivers;
  switch (ep.category) {
    case "transcript":
      return [
        "Full transcript text with start/end timestamps",
        "Auto-detected language and segment count",
        "AI audio transcription fallback when no captions exist",
        "Clean JSON ready for RAG, search, or subtitles",
      ];
    case "summarize":
      return [
        "2–3 paragraph AI summary of the video",
        "4–8 bullet key points and detected topics",
        "Overall sentiment and tone",
        "Powered by the transcript under the hood",
      ];
    case "details":
      return [
        "Title, description, and thumbnail URLs",
        "View, like, comment, and share counts",
        "Duration, publish date, and author handle",
        "Stable IDs for joining with other endpoints",
      ];
    case "comments":
      return [
        "Comment text, author name, and handle",
        "Like counts and reply threads",
        "Pagination via the limit parameter",
        "Timestamps for trend and sentiment analysis",
      ];
    case "channel":
      return [
        "Display name, handle, bio, and avatar",
        "Follower / subscriber and content counts",
        "Verification status and external links",
        "Aggregate engagement signals",
      ];
    case "search":
      return [
        "Ranked, structured result list",
        "Title, URL, author, and thumbnail per result",
        "Engagement metrics where available",
        "Configurable result limit",
      ];
    case "list":
      return [
        "Bulk list of items with full metadata",
        "View counts, dates, and direct URLs",
        "Configurable result limit",
        "Ideal for monitoring and content pipelines",
      ];
    case "download":
      return [
        "Direct, watermark-free media URL",
        "Available quality/format variants",
        "File size and duration metadata",
        "Short-lived signed link",
      ];
  }
}

export function params(ep: ApiEndpoint): ApiParam[] {
  const base: ApiParam[] = [];
  if (ep.category === "search") {
    base.push({ name: "q", type: "string", required: true, description: "Search query or keywords." });
  } else {
    base.push({
      name: "url",
      type: "string",
      required: true,
      description:
        ep.category === "channel"
          ? `Public ${PLATFORM_LABEL[ep.platform]} profile / channel URL.`
          : `Public ${PLATFORM_LABEL[ep.platform]} ${ep.category === "list" ? "channel/playlist" : "video"} URL.`,
    });
  }
  if (["comments", "search", "list"].includes(ep.category)) {
    base.push({ name: "limit", type: "integer", required: false, description: "Max items to return (default 20)." });
  }
  if (ep.category === "transcript" || ep.category === "summarize") {
    base.push({ name: "language", type: "string", required: false, description: "Preferred caption language (ISO code, e.g. \"en\")." });
  }
  return base;
}

function exampleData(ep: ApiEndpoint): Record<string, unknown> {
  switch (ep.category) {
    case "transcript":
      return {
        transcript:
          "Hey everyone, welcome back to the channel. Today we're breaking down structured data APIs.",
        wordCount: 1240,
        segments: 86,
        transcriptSegments: [
          { text: "Hey everyone, welcome back to the channel.", start: 0.0, duration: 4.12, timestamp: "00:00" },
          { text: "Today we're breaking down structured data APIs.", start: 4.12, duration: 4.28, timestamp: "00:04" },
        ],
      };
    case "summarize":
      return {
        summary: "A concise walkthrough of how to extract structured data from social video at scale.",
        keyPoints: ["One key per platform", "24h shared cache", "No OAuth required"],
        topics: ["APIs", "data extraction", "automation"],
        sentiment: "positive",
      };
    case "details":
      return {
        id: "dQw4w9WgXcQ",
        title: "Example video",
        author: "@creator",
        views: 1842203,
        likes: 95210,
        comments: 4123,
        durationSec: 213,
        publishedAt: "2024-11-02T10:00:00Z",
      };
    case "comments":
      return {
        total: 2,
        comments: [
          { author: "@viewer1", text: "This is exactly what I needed!", likes: 42, replies: 3 },
          { author: "@viewer2", text: "Great breakdown.", likes: 11, replies: 0 },
        ],
      };
    case "channel":
      return {
        handle: "@creator",
        name: "Creator",
        followers: 1280000,
        posts: 412,
        verified: true,
        bio: "Building in public.",
      };
    case "search":
      return {
        total: 2,
        results: [
          { title: "Top result", url: "https://example.com/1", author: "@creator", views: 530120 },
          { title: "Second result", url: "https://example.com/2", author: "@maker", views: 210430 },
        ],
      };
    case "list":
      return {
        total: 2,
        items: [
          { title: "Latest upload", url: "https://example.com/a", views: 90120, publishedAt: "2025-01-12" },
          { title: "Previous upload", url: "https://example.com/b", views: 75230, publishedAt: "2025-01-04" },
        ],
      };
    case "download":
      return {
        downloadUrl: "https://cdn.captapi.com/dl/abc123.mp4",
        format: "mp4",
        quality: "1080p",
        sizeBytes: 18432044,
        expiresIn: 3600,
      };
  }
}

export function exampleResponse(ep: ApiEndpoint): string {
  return JSON.stringify(
    { success: true, cached: false, creditsUsed: ep.credits, data: exampleData(ep) },
    null,
    2,
  );
}

export function exampleQueryString(ep: ApiEndpoint): string {
  const g = getGroup(ep.platform);
  if (ep.category === "search") return "q=structured%20data%20api";
  if (ep.category === "channel") {
    const profile =
      ep.platform === "youtube"
        ? "https://www.youtube.com/@MrBeast"
        : ep.platform === "tiktok"
        ? "https://www.tiktok.com/@khaby.lame"
        : ep.platform === "instagram"
        ? "https://www.instagram.com/natgeo/"
        : "https://www.facebook.com/NASA";
    return `url=${encodeURIComponent(profile)}`;
  }
  return `url=${encodeURIComponent(g.exampleUrl)}`;
}

export function curlExample(ep: ApiEndpoint): string {
  return `curl "${API_URL}${ep.path}?${exampleQueryString(ep)}" \\\n  -H "Authorization: Bearer capt_live_..."`;
}

export function faqs(ep: ApiEndpoint): FaqItem[] {
  const platform = PLATFORM_LABEL[ep.platform];
  const list: FaqItem[] = [
    {
      q: `What does the ${ep.name} do?`,
      a: `The ${ep.name} lets you ${ACTION[ep.category]} from a public ${platform} ${
        ep.category === "search" ? "query" : ep.category === "channel" ? "profile" : "video"
      } using one ${ep.method} request to ${ep.path}. It returns clean JSON — no OAuth or scraping setup required.`,
    },
    {
      q: `How many credits does the ${ep.name} cost?`,
      a: `Each successful call costs ${ep.credits} credit${ep.credits === 1 ? "" : "s"}. Responses are cached for 24 hours, and cached results cost 0 credits. Failed or empty results are never charged.`,
    },
    {
      q: `Do I need a ${platform} API key or OAuth?`,
      a: `No. A single Captapi key works across YouTube, TikTok, Instagram, and Facebook. We handle proxies, rate limits, retries, and authentication for you.`,
    },
  ];

  if (ep.category === "transcript") {
    list.push({
      q: `What if the ${platform} video has no captions?`,
      a: `When no captions are available, Captapi transcribes the audio with AI (Whisper) automatically, so you still get a usable transcript.`,
    });
  }
  if (ep.category === "summarize") {
    list.push({
      q: `Which AI model powers the summaries?`,
      a: `Summaries are generated with GPT-4o-mini for a strong balance of quality, speed, and cost, built on top of the video transcript.`,
    });
  }
  if (ep.category === "download") {
    list.push({
      q: `Are the downloads watermark-free?`,
      a: `Yes — the ${ep.name} returns a direct, watermark-free media URL where the platform allows it, along with available quality variants.`,
    });
  }
  list.push({
    q: `Is the ${ep.name} suitable for production use?`,
    a: `Yes. It is a stable REST endpoint with predictable JSON, automatic retries, and a shared 24-hour cache. Use it for RAG pipelines, analytics, monitoring, and content automation.`,
  });

  return list;
}

// ---------------------------------------------------------------------------
// Response structure (per category)
// ---------------------------------------------------------------------------

export function responseStructure(ep: ApiEndpoint): ResponseGroup[] {
  switch (ep.category) {
    case "transcript":
      return [
        {
          title: "Full transcript",
          fields: [
            { name: "transcript", desc: "Complete text transcript of the video." },
            { name: "wordCount", desc: "Total number of words in the transcript." },
            { name: "segments", desc: "Total number of transcript segments." },
          ],
        },
        {
          title: "Timestamped segments",
          note: "Each item in transcriptSegments contains:",
          fields: [
            { name: "text", desc: "The spoken text for this segment." },
            { name: "start", desc: "Start time in seconds." },
            { name: "duration", desc: "Duration of the segment in seconds." },
            { name: "timestamp", desc: "Human-readable timestamp (MM:SS format)." },
          ],
        },
      ];
    case "summarize":
      return [
        {
          title: "Summary",
          fields: [
            { name: "summary", desc: "AI-generated summary of the video (2–3 paragraphs)." },
            { name: "sentiment", desc: "Overall tone of the content (positive, neutral, negative)." },
          ],
        },
        {
          title: "Structured output",
          fields: [
            { name: "keyPoints", desc: "Array of the most important takeaways." },
            { name: "topics", desc: "Array of detected topics and themes." },
          ],
        },
      ];
    case "details":
      return [
        {
          title: "Video",
          fields: [
            { name: "id", desc: "Stable platform ID for the video." },
            { name: "title", desc: "Video title." },
            { name: "author", desc: "Creator handle or channel name." },
            { name: "durationSec", desc: "Video length in seconds." },
            { name: "publishedAt", desc: "Publish date (ISO 8601)." },
          ],
        },
        {
          title: "Engagement",
          fields: [
            { name: "views", desc: "Total view count." },
            { name: "likes", desc: "Total like count." },
            { name: "comments", desc: "Total comment count." },
          ],
        },
      ];
    case "comments":
      return [
        {
          title: "Result",
          fields: [{ name: "total", desc: "Number of comments returned." }],
        },
        {
          title: "Each comment",
          note: "Each item in comments contains:",
          fields: [
            { name: "author", desc: "Comment author name or handle." },
            { name: "text", desc: "The comment text." },
            { name: "likes", desc: "Number of likes on the comment." },
            { name: "replies", desc: "Number of replies in the thread." },
          ],
        },
      ];
    case "channel":
      return [
        {
          title: "Profile",
          fields: [
            { name: "handle", desc: "Profile / channel handle." },
            { name: "name", desc: "Display name." },
            { name: "bio", desc: "Profile bio or description." },
            { name: "verified", desc: "Whether the account is verified." },
          ],
        },
        {
          title: "Stats",
          fields: [
            { name: "followers", desc: "Follower / subscriber count." },
            { name: "posts", desc: "Total number of posts / videos." },
          ],
        },
      ];
    case "search":
      return [
        {
          title: "Result",
          fields: [{ name: "total", desc: "Number of results returned." }],
        },
        {
          title: "Each result",
          note: "Each item in results contains:",
          fields: [
            { name: "title", desc: "Result title." },
            { name: "url", desc: "Direct URL to the content." },
            { name: "author", desc: "Creator handle." },
            { name: "views", desc: "View count where available." },
          ],
        },
      ];
    case "list":
      return [
        {
          title: "Result",
          fields: [{ name: "total", desc: "Number of items returned." }],
        },
        {
          title: "Each item",
          note: "Each item in items contains:",
          fields: [
            { name: "title", desc: "Item title." },
            { name: "url", desc: "Direct URL to the content." },
            { name: "views", desc: "View count." },
            { name: "publishedAt", desc: "Publish date (ISO 8601)." },
          ],
        },
      ];
    case "download":
      return [
        {
          title: "Download",
          fields: [
            { name: "downloadUrl", desc: "Direct, watermark-free media URL." },
            { name: "format", desc: "Container/format of the file (e.g. mp4)." },
            { name: "quality", desc: "Resolution of the returned media." },
            { name: "sizeBytes", desc: "File size in bytes." },
            { name: "expiresIn", desc: "Seconds until the signed link expires." },
          ],
        },
      ];
  }
}

// ---------------------------------------------------------------------------
// Use cases (per category)
// ---------------------------------------------------------------------------

export function useCases(ep: ApiEndpoint): UseCase[] {
  switch (ep.category) {
    case "transcript":
      return [
        { title: "Accessibility", desc: "Provide captions and transcripts for hearing-impaired users." },
        { title: "Content Analysis", desc: "Analyze spoken content for keywords, topics, and sentiment." },
        { title: "Search & Discovery", desc: "Make video content searchable by text." },
        { title: "Content Creation", desc: "Extract quotes and key phrases from videos." },
        { title: "Language Learning", desc: "Provide text alongside audio for language learners." },
        { title: "Research", desc: "Analyze large volumes of video content efficiently." },
        { title: "SEO", desc: "Extract text content for search engine optimization." },
      ];
    case "summarize":
      return [
        { title: "Content Triage", desc: "Decide what's worth watching without watching it." },
        { title: "Newsletters & Digests", desc: "Auto-generate summaries for roundups and emails." },
        { title: "Research", desc: "Condense long videos into key points at scale." },
        { title: "SEO", desc: "Generate descriptions and meta content from videos." },
        { title: "Social", desc: "Draft captions and posts from video content." },
      ];
    case "details":
      return [
        { title: "Analytics", desc: "Track views, likes, and engagement over time." },
        { title: "Competitor Monitoring", desc: "Benchmark the performance of other creators." },
        { title: "Dashboards", desc: "Power reporting and BI with real metadata." },
        { title: "Content Curation", desc: "Filter and rank videos by performance." },
      ];
    case "comments":
      return [
        { title: "Sentiment Analysis", desc: "Understand how audiences react to content." },
        { title: "Community Insights", desc: "Surface FAQs, requests, and recurring themes." },
        { title: "Moderation", desc: "Detect spam, abuse, or policy violations at scale." },
        { title: "Market Research", desc: "Mine genuine opinions and product feedback." },
      ];
    case "channel":
      return [
        { title: "Influencer Discovery", desc: "Find and vet creators by audience size." },
        { title: "CRM Enrichment", desc: "Add social stats to your contact profiles." },
        { title: "Competitive Analysis", desc: "Track follower growth and posting cadence." },
        { title: "Outreach", desc: "Qualify partnership and sponsorship targets." },
      ];
    case "search":
      return [
        { title: "Trend Discovery", desc: "Find trending content by keyword or hashtag." },
        { title: "Content Sourcing", desc: "Build feeds and playlists programmatically." },
        { title: "Monitoring", desc: "Track topics, brands, and competitors." },
        { title: "Research", desc: "Sample large sets of content for analysis." },
      ];
    case "list":
      return [
        { title: "Content Pipelines", desc: "Ingest a channel's catalog in bulk." },
        { title: "Monitoring", desc: "Detect new uploads automatically." },
        { title: "Archiving", desc: "Snapshot a creator's full library." },
        { title: "Analytics", desc: "Aggregate performance across many videos." },
      ];
    case "download":
      return [
        { title: "Backup & Archiving", desc: "Save copies of public videos you own or license." },
        { title: "Repurposing", desc: "Clip and remix content for other platforms." },
        { title: "ML Datasets", desc: "Collect video and audio for model training." },
        { title: "Offline Analysis", desc: "Process media without streaming it live." },
      ];
  }
}
