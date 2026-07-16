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
    title: "cache=false parameter on every endpoint",
    description:
      "Every data endpoint now accepts an optional cache=false query parameter to bypass the cache and always fetch fresh data. Previously only transcript, summarizer, and Spotify endpoints supported it.",
    items: [
      "Add cache=false to any request when you need live numbers instead of the cached copy (fresh calls are billed as usual; the result still refreshes the cache)",
      "Documented on all 179 API pages and available in the playground, MCP server, SDKs, CLI, and n8n node",
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
    title: "MCP catalog synced to all 179 tools",
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
    title: "Real response examples for all 179 endpoints",
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
