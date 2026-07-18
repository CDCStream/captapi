// Changelog data layer: reads changelog_entries from Supabase with a static
// fallback so the page renders even before the migration is applied.
import { getServiceClient } from "@/lib/supabase/admin";

export type ChangelogCategory =
  | "feature"
  | "improvement"
  | "fix"
  | "integration"
  | "platform";

export interface ChangelogEntry {
  id: string;
  publishedAt: string; // ISO date (YYYY-MM-DD)
  category: ChangelogCategory;
  title: string;
  description: string;
  items: string[];
}

export const CATEGORY_LABELS: Record<ChangelogCategory, string> = {
  feature: "New",
  improvement: "Improved",
  fix: "Fixed",
  integration: "Integrations",
  platform: "Platforms",
};

interface ChangelogRow {
  id: string;
  published_at: string;
  category: string;
  title: string;
  description: string | null;
  items: unknown;
}

function parseRow(row: ChangelogRow): ChangelogEntry {
  return {
    id: row.id,
    publishedAt: row.published_at,
    category: (row.category as ChangelogCategory) ?? "improvement",
    title: row.title,
    description: row.description ?? "",
    items: Array.isArray(row.items) ? row.items.filter((i): i is string => typeof i === "string") : [],
  };
}

/** Static mirror of the migration seed — used only when the table is unavailable. */
const FALLBACK_ENTRIES: Omit<ChangelogEntry, "id">[] = [
  {
    publishedAt: "2026-07-17",
    category: "platform",
    title: "Retired media-download and privacy-workaround endpoints and tools",
    description:
      "To keep Captapi focused on public data and analytics, we've retired the media-download endpoints and a set of free tools that copied media files or worked around platform privacy features. Retired APIs: YouTube Video Download, TikTok Video Download, Instagram Video Download, Instagram Story Highlights, and Instagram Highlights Details. Retired free tools: YouTube to MP4/MP3, YouTube Shorts Downloader, YouTube Thumbnail Downloader, Instagram Photo Downloader, Instagram Highlights Viewer, Snapchat Story Viewer, Who Viewed My Profile, Am I Blocked, What Happens When You Block, Screenshot Notification Checker, and Snapchat+ Checker. All transcript, summary, profile, stats, comment, search, and trend endpoints are unchanged.",
    items: [
      "Retired 5 download/story endpoints across YouTube, TikTok, and Instagram",
      "Retired 12 media-download and privacy-workaround free tools",
      "No change to transcripts, summaries, profiles, stats, comments, search, or trends",
    ],
  },
  {
    publishedAt: "2026-07-17",
    category: "improvement",
    title: "TikTok Search Suggestions now returns a ready-to-open search link",
    description:
      "Every suggestion from the TikTok Search Suggestions API now includes a searchUrl — a direct TikTok search link that runs that exact query, so you can jump straight from a suggested keyword to its results. Alongside the existing suggestion text, rank, seed keyword, region, and language, it makes the endpoint a more complete keyword-research tool. No change to pricing.",
    items: [
      "New searchUrl field on each suggestion — opens that exact search on TikTok",
      "Rank now reflects TikTok's own suggestion order",
    ],
  },
  {
    publishedAt: "2026-07-17",
    category: "feature",
    title: "TikTok search, reworked: Search by Hashtag and Search Users",
    description:
      "TikTok search is now two focused endpoints. Search by Hashtag (/v1/tiktok/search/hashtag) returns the videos posted under a tag — each with its URL, caption, author, and full engagement counts — plus an optional region parameter that sets the proxy's exit country. Search Users (/v1/tiktok/search/users) returns the creators whose username, display name, or bio match a query, each with follower count, verified flag, and avatar. Both add cursor pagination: pass the returned nextCursor to page through results and check hasMore to know when you've reached the end. This replaces the older TikTok Search, TikTok Hashtag Search, and TikTok User Search endpoints, which have been retired. Billed per result.",
    items: [
      "TikTok Search by Hashtag API — videos under a hashtag with engagement counts and an optional proxy region",
      "TikTok Search Users API — creators matching a query with follower count, verified flag, and avatar",
      "Both support cursor pagination via nextCursor + hasMore",
      "Retired the old /v1/tiktok/search, /hashtag-search, and /user-search endpoints",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "TikTok Audience Demographics is now native — a real country breakdown",
    description:
      "The TikTok Audience Demographics API now returns a ranked breakdown of a creator's audience by country. TikTok never publishes follower geography, but every commenter's country is exposed on its own data, so we sample the people engaging across a creator's recent videos and tally their countries into audienceLocations — each with a country name, ISO countryCode, a raw count, and a percentage of the sample, plus videosSampled and sampleSize for transparency. It's computed natively from TikTok's own data (no third-party audience panel) and now costs a flat 3 credits.",
    items: [
      "New audienceLocations array: country, countryCode, count, and percentage",
      "Engagement-based country mix sampled from real commenters",
      "videosSampled and sampleSize included so you can judge the sample",
      "Native, no audience actor — flat 3 credits; cached results stay free",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "TikTok Profile Region now resolves a country even when TikTok hides it",
    description:
      "TikTok no longer exposes an account's country on any public surface, so the region field used to be almost always null. It's now filled with the best available signal: TikTok's authoritative value when present, otherwise an AI-inferred country (e.g. IT or US) guessed from public profile cues — bio, display name, and language. A regionSource field tells you which one you got (\"tiktok\" or \"inferred\") and regionConfidence (high/medium/low) grades an inferred guess. Flat 2 credits per call.",
    items: [
      "region is now populated: TikTok's own value, else an AI-inferred country",
      "regionSource labels the origin — \"tiktok\" or \"inferred\"",
      "regionConfidence grades inferred guesses (high/medium/low)",
      "Flat 2 credits per call; cached results stay free",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Cheaper pricing on native endpoints",
    description:
      "Endpoints that we serve directly from the platform's own data (no third-party actor) now cost far fewer credits. TikTok Comments drops to a flat 2 credits per call, and a range of native single-fetch endpoints drop to just 1 credit. Cached results are still free and failed or empty calls are never charged.",
    items: [
      "TikTok Comments: flat 2 credits per call (was up to 10)",
      "YouTube Community Post Details: 1 credit",
      "Twitch Profile, Twitch Clip, and Twitch User Schedule: 1 credit",
      "SoundCloud Artist and SoundCloud Track: 1 credit",
      "Facebook Marketplace Item: 1 credit",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "TikTok Comments is now native with cursor pagination",
    description:
      "The TikTok Comments API now fetches straight from TikTok's own data (no third-party actor) and supports true cursor pagination. Each response includes totalComments (the video's full comment count) and a nextCursor — pass it back in the cursor parameter to page through every comment, up to 500 per call. Comments still return text, author username and avatar, like count, and publish time. Now billed as a flat 2 credits per call (no matter how many comments you fetch), and the API automatically falls back to the actor if the native path is unavailable.",
    items: [
      "Native TikTok source — no Apify actor on the hot path",
      "Cursor pagination: pass the returned nextCursor to fetch the next page",
      "New totalComments field with the video's full comment count",
      "Reply threads still available via the TikTok Comment Replies API",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "cache defaults to false — fresh data unless you opt in",
    description:
      "The optional cache query parameter on every data endpoint now defaults to false, so requests fetch fresh data unless you explicitly pass cache=true. Previously the default was true (serve from the 24h cache). Pass cache=true when you want the cached copy for free/instant repeat lookups.",
    items: [
      "Default is now cache=false on all data endpoints (always fresh)",
      "Pass cache=true to serve from the 24h response cache",
      "Updated across OpenAPI, docs, playground, MCP, SDKs, CLI, n8n, Make, Zapier, and Apify",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Instagram Basic Profile is now native, by user ID — richer fields",
    description:
      "The Instagram Basic Profile API now takes an Instagram numeric user ID (e.g. 314216) and returns a much richer public profile — username, full name, biography, follower/following/media counts, verification and privacy flags, business/professional status, and standard + HD profile pictures — straight from Instagram's own data. A profile URL, @handle, or username is still accepted and resolved automatically. It runs on our native resolver (no third-party actor), still costs 1 credit, and null/empty fields are stripped for a tidy response.",
    items: [
      "Accepts a numeric userId (URL/@handle/username also work)",
      "Returns bio, counts, verification, business flags, pk/fbid, and HD profile pic",
      "Native resolver — no Apify actor — with Decodo as a fallback",
      "Null/empty fields are dropped, so you only see populated data",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Instagram Embed API is now the Instagram Embed HTML API — full embed doc + profiles",
    description:
      "The Instagram Embed API is now called the Instagram Embed HTML API. It now returns Instagram's own self-contained embed page as full HTML (the document served at /embed/) instead of just the blockquote snippet, plus an embedUrl you can point an <iframe src> at. It also accepts profile URLs and @handles in addition to posts and reels — posts/reels come back as a media card, profiles as a profile card.",
    items: [
      "html is now Instagram's full self-contained embed document (iframe-ready)",
      "New embedUrl field to load the embed directly via <iframe src>",
      "Accepts profile URLs/@handles too; adds a type flag (post/reel/profile)",
      "Falls back to the classic blockquote + embed.js snippet if the page is unavailable",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Instagram Highlights Details is now native, by highlight ID — 1 credit",
    description:
      "The Instagram Highlights Details API now takes a single Highlight ID (the id returned by the Story Highlights API) and returns just that album's stories, straight from Instagram's own data. Pair it with Story Highlights: list a profile's albums, then pass an ID here to pull its contents. It's faster, richer, and the price dropped from 9 credits to 1.",
    items: [
      "Now accepts id (e.g. highlight:18201653992314974) instead of a profile URL + limit",
      "Returns one highlight's stories with media/video URL, thumbnail, size, duration, and post date",
      "Runs on our native resolver — ~1s, no third-party actor — and now costs 1 credit (was 9)",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "fix",
    title: "Instagram Story Highlights: dropped the always-empty itemCount",
    description:
      "The Instagram Story Highlights API listed every highlight album with an itemCount that was always null — the light listing endpoint never loads the stories inside, so it could never count them. We removed the misleading field. To get the real count (and the stories themselves), use the Instagram Highlights Details API, where itemCount is now always populated.",
    items: [
      "Each highlight now returns id, title, and coverUrl (no more null itemCount)",
      "Instagram Highlights Details now always fills itemCount from the expanded stories",
      "Response cache was refreshed so you see the new shape immediately",
    ],
  },
  {
    publishedAt: "2026-07-16",
    category: "improvement",
    title: "Instagram Profile Search is now native — 1 credit",
    description:
      "The Instagram Profile Search API now runs on our native resolver instead of a third-party actor. Pass an account name, @handle, or profile URL and it resolves the matching public profile directly from Instagram. It's faster, more reliable, and the price dropped from 12 credits to 1.",
    items: [
      "Now costs 1 credit per lookup (was 12) and returns results in ~1s",
      "Accepts a name, @handle, or profile URL — e.g. nike, @nasa, instagram.com/natgeo",
      "The limit parameter was removed; the endpoint resolves the single matching profile",
    ],
  },
  {
    publishedAt: "2026-07-15",
    category: "improvement",
    title: "Instagram Music Posts API retired",
    description:
      "The Instagram Music Posts API has been removed — it was a duplicate of the Instagram Reels By Audio ID API (same scraper, same data) at a higher price. Use Reels By Audio ID instead; it accepts both audio IDs and full audio page URLs.",
    items: [
      "GET /v1/instagram/music-posts no longer exists (returns 404)",
      "Migrate to GET /v1/instagram/reels-by-audio-id — pass your audio page URL or the numeric audio ID as audio_id",
      "Old docs links redirect to the Reels By Audio ID page automatically",
    ],
  },
  {
    publishedAt: "2026-07-15",
    category: "improvement",
    title: "cache parameter on every endpoint (historical)",
    description:
      "Historical note: on this date every data endpoint gained an optional cache query parameter. Later (2026-07-16) the default flipped to cache=false (always fresh). Prefer the 2026-07-16 changelog entry for current behavior.",
    items: [
      "Superseded by: cache defaults to false — pass cache=true to use the 24h cache",
      "Documented across docs, playground, MCP, SDKs, CLI, and n8n",
      "Account endpoints (balance, usage) are always live and unaffected",
    ],
  },
  {
    publishedAt: "2026-07-14",
    category: "feature",
    title: "Report a bug from any API page",
    description:
      "A Report a bug button on every API docs page and in the dashboard lets you flag a wrong response, an error, or something slow in a couple of clicks.",
    items: [
      "Modal form with an endpoint picker (prefilled on API pages), a description field, and an optional email for logged-out users",
      "Reports are linked to your account automatically when you're signed in — no need to type your details",
      "Sits next to \"Try it\" on each API page and in the dashboard sidebar",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Integrations hub at /integrations",
    description:
      "A dedicated page listing every official integration with setup guides, plus a hover dropdown in the navbar.",
    items: [
      "MCP Server (hosted + local), TypeScript & Python SDKs, CLI, n8n, Make.com, Apify Actor, and the REST API in one place",
      "Each card links to its setup guide and npm/PyPI package",
      "Machine-readable manifests highlighted for AI agents (/mcp.json, /llms.txt, OpenAPI 3)",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Monitors + HMAC-signed webhooks",
    description:
      "Point a monitor at any list-returning endpoint and get only new items POSTed to your webhook — no polling loops on your side.",
    items: [
      "POST /v1/monitors: watch subreddit posts, channel videos, ad-library searches and more on your schedule (15 min to 24 h)",
      "Deliveries are HMAC-SHA256 signed (X-Captapi-Signature over timestamp.body) so you can verify authenticity",
      "POST /v1/monitors/{id}/test sends a signed test delivery",
      "Runs bill credits exactly like direct API calls; cached results stay free",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Automatic metric history (GET /v1/history)",
    description:
      "Follower, view, and like counts now accumulate into a time series automatically whenever tracked profile or post endpoints are fetched fresh.",
    items: [
      "Chart growth without building your own snapshot pipeline",
      "Covers profile and details endpoints across YouTube, TikTok, Instagram, X, Reddit, Bluesky, Twitch and more",
      "Query by endpoint + URL with a configurable window (up to 365 days)",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Batch endpoint (POST /v1/batch)",
    description: "Run up to 20 endpoint calls concurrently in a single HTTP request.",
    items: [
      "Per-item status and per-item billing — one failed item never fails the batch",
      "Cached items are free, exactly like single calls",
      "Ideal for enriching lists of profiles or videos in one round-trip",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Public status page",
    description:
      "Live API health at /status, computed from real production traffic — not a manually flipped switch.",
    items: [
      "GET /v1/status (no auth) returns overall and per-platform success rates and response times over the last 24 h",
      "Human view at captapi.com/status refreshes every 2 minutes",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "feature",
    title: "Official TypeScript & Python SDKs",
    description:
      "Typed clients generated from the same catalog that powers the API, MCP server, and CLI.",
    items: [
      "npm install @captapi/sdk — zero dependencies, works on Node 18+, Deno, Bun, and edge runtimes",
      "pip install captapi — sync (Captapi) and async (AsyncCaptapi) clients on httpx",
      "A typed, namespaced method for every endpoint; errors always throw with status + code",
      "x-api-key header now accepted as an alias for Authorization: Bearer",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "integration",
    title: "MCP catalog synced to all endpoints",
    description:
      "The hosted MCP server and every published package now expose the full endpoint catalog.",
    items: [
      "@captapi/mcp 0.4.0, @captapi/cli 0.3.0, n8n-nodes-captapi 0.3.0, Apify Actor 0.3 published",
      "OpenAPI 3 spec linked from llms.txt manifests for AI agent discovery",
    ],
  },
  {
    publishedAt: "2026-07-04",
    category: "improvement",
    title: "Richer response data across 11 platforms",
    description: "Closed field gaps against competitors with dedicated upstream sources.",
    items: [
      "Reddit: comment upvotes + threading (residential routing, optional OAuth app support)",
      "Twitch: clip/profile metadata and streamer schedules via a dedicated actor",
      "TikTok Shop: product reviews via a dedicated actor",
      "Also enriched: link-in-bio socials/email, Rumble embeds/streams/comments, Pinterest pin details, SoundCloud artist fields, Bluesky embeds, Truth Social website, GitHub repo/license/topics, X profile counts",
    ],
  },
  {
    publishedAt: "2026-07-03",
    category: "improvement",
    title: "Real response examples for all endpoints",
    description:
      "Every endpoint page now shows a real captured response, refreshed in batches across the whole catalog.",
    items: [
      "Batches covered Twitter/LinkedIn/Reddit, TikTok Shop/Threads/Snapchat/ad libraries, GitHub/Facebook Marketplace/Events/Pinterest/Spotify, and Rumble/Twitch/Bluesky/SoundCloud/Kwai",
      "Dozens of mapper fixes along the way: timestamped transcript segments, YouTube comment author metadata, duration parsing, Instagram actor replacement and more",
    ],
  },
  {
    publishedAt: "2026-07-03",
    category: "feature",
    title: "Platform landing pages + APIs dropdown",
    description:
      "Every platform got a dedicated landing page with endpoint lists, FAQ, and structured data; the navbar now opens the full API catalog.",
    items: [],
  },
  {
    publishedAt: "2026-06-28",
    category: "platform",
    title: "180 endpoints across 29 platforms",
    description: "Major catalog expansion with reliability fixes across the board.",
    items: [
      "New platforms and endpoints across the catalog, audited live end-to-end",
      "Endpoint reliability, agent URL validation, and integration discovery improvements",
      "Comprehensive live audit reports added to the repo",
    ],
  },
  {
    publishedAt: "2026-05-31",
    category: "platform",
    title: "EnsembleData & Scrape Creators parity push",
    description:
      "Expanded TikTok, Instagram, YouTube, and Facebook coverage to close competitor gaps.",
    items: [
      "19 new endpoints: TikTok hashtag/top/user search, song details, trending; IG hashtag/profile search, story highlights, embed; YT comment replies, channel playlists, community posts; FB profile posts/reels, group posts, comment replies",
      "Per-result pricing normalized to guarantee margins; dashboard analytics tab with daily usage charts",
    ],
  },
  {
    publishedAt: "2026-05-29",
    category: "feature",
    title: "Captapi launch",
    description:
      "One API for structured public social-media data: transcripts, AI summaries, comments, profiles, search, and downloads.",
    items: [
      "REST API with Bearer auth, credit-based billing, and cached-result discounts",
      "Dashboard with API keys, playground, usage analytics, and billing",
      "SEO/AEO foundation: llms.txt, structured data, programmatic docs",
    ],
  },
];

export async function getChangelog(): Promise<ChangelogEntry[]> {
  const sb = getServiceClient();
  if (sb) {
    const { data, error } = await sb
      .from("changelog_entries")
      .select("*")
      .order("published_at", { ascending: false })
      .order("created_at", { ascending: false });
    if (!error && data && data.length > 0) {
      return (data as ChangelogRow[]).map(parseRow);
    }
  }
  return FALLBACK_ENTRIES.map((e, i) => ({ ...e, id: `fallback-${i}` }));
}

/** Group entries by publish date (already sorted desc). */
export function groupByDate(entries: ChangelogEntry[]): { date: string; entries: ChangelogEntry[] }[] {
  const groups: { date: string; entries: ChangelogEntry[] }[] = [];
  for (const entry of entries) {
    const last = groups[groups.length - 1];
    if (last && last.date === entry.publishedAt) {
      last.entries.push(entry);
    } else {
      groups.push({ date: entry.publishedAt, entries: [entry] });
    }
  }
  return groups;
}
