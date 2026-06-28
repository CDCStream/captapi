// Generates the Apify Actor's input schema + endpoint table from the shared
// catalog (single source of truth: ../captapi-n8n/src/catalog.ts).
//
// Run with Node >= 22.6 (TypeScript type-stripping enabled):
//   node generate.mjs

import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const { ENDPOINTS } = await import("../captapi-n8n/src/catalog.ts");

const HERE = dirname(fileURLToPath(import.meta.url));

const PLATFORM_LABELS = {
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  facebook: "Facebook",
  twitter: "Twitter/X",
  reddit: "Reddit",
  threads: "Threads",
  bluesky: "Bluesky",
  pinterest: "Pinterest",
  linkedin: "LinkedIn",
  rumble: "Rumble",
  tiktok_shop: "TikTok Shop",
  github: "GitHub",
  google: "Google",
  twitch: "Twitch",
  spotify: "Spotify",
  soundcloud: "SoundCloud",
  linktree: "Linktree",
  snapchat: "Snapchat",
  truth_social: "Truth Social",
  kick: "Kick",
  amazon_shop: "Amazon Shop",
  age_gender: "Age and Gender",
  account: "Account",
  kwai: "Kwai",
  komi: "Komi",
  pillar: "Pillar",
  linkbio: "Linkbio",
  linkme: "Linkme",
  ad_library: "Ad Library",
};

function writeJson(relPath, value) {
  const full = `${HERE}/${relPath}`;
  mkdirSync(dirname(full), { recursive: true });
  writeFileSync(full, JSON.stringify(value, null, 2) + "\n", "utf8");
}

// --- Endpoint table the Actor reads at runtime ------------------------------
const endpoints = ENDPOINTS.map((e) => ({
  tool: e.tool,
  platform: e.platform,
  name: e.name,
  path: e.path,
  credits: e.credits,
  summary: e.summary,
  params: e.params.map((p) => ({
    name: p.name,
    type: p.type,
    required: !!p.required,
    description: p.description,
  })),
}));
writeJson("src/endpoints.json", endpoints);

// --- Build the human-facing list of which params each operation uses --------
const opLines = ENDPOINTS.map((e) => {
  const ps = e.params
    .map((p) => (p.required ? `${p.name}*` : p.name))
    .join(", ");
  return `- ${e.tool} -> needs: ${ps || "(none)"}`;
}).join("\n");

// --- Input schema (Apify renders this as the run form) ----------------------
const inputSchema = {
  title: "Captapi input",
  description:
    "Bring your own Captapi API key and pick an operation. This Actor calls the Captapi REST API (it does not scrape) and returns the structured result.",
  type: "object",
  schemaVersion: 1,
  properties: {
    apiKey: {
      title: "Captapi API key",
      type: "string",
      description:
        "Your capt_live_... key from https://captapi.com/dashboard/api-keys. Stored encrypted. Credits are billed to your own Captapi account.",
      editor: "textfield",
      isSecret: true,
    },
    operation: {
      title: "Operation",
      type: "string",
      description:
        "Which Captapi endpoint to call. Each operation needs specific fields below (url, search query, limit, ...).",
      editor: "select",
      enum: ENDPOINTS.map((e) => e.tool),
      enumTitles: ENDPOINTS.map(
        (e) => `${PLATFORM_LABELS[e.platform] ?? e.platform}: ${e.name}`,
      ),
      prefill: "youtube_transcript",
    },
    url: {
      title: "URL",
      type: "string",
      description:
        "Content/profile URL for the operation (video, reel, post, channel, profile, playlist, music...). Required by most operations.",
      editor: "textfield",
      prefill: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    q: {
      title: "Search query",
      type: "string",
      description:
        "Keyword/hashtag for search operations (*_search, *_hashtag_search, *_user_search, etc.). Min 2 chars.",
      editor: "textfield",
    },
    limit: {
      title: "Limit",
      type: "integer",
      description:
        "Max items to return for list/search operations. Defaults and caps vary per operation; billed per result.",
      editor: "number",
      minimum: 1,
    },
    language: {
      title: "Language",
      type: "string",
      description:
        "Preferred caption language ISO code (e.g. en) for transcript/summarize operations. Optional; defaults to auto-detect.",
      editor: "textfield",
    },
    comment_id: {
      title: "Comment ID",
      type: "string",
      description:
        "Parent comment ID for *_comment_replies operations (from the comments endpoint).",
      editor: "textfield",
    },
    country: {
      title: "Country",
      type: "string",
      description:
        "Two-letter ISO country code (e.g. US, GB, TR). Used by trending, TikTok Shop, and Ad Library operations.",
      editor: "textfield",
    },
    region: {
      title: "Region",
      type: "string",
      description:
        "Two-letter TikTok Shop region (e.g. US, GB, SG). Optional.",
      editor: "textfield",
    },
    username: {
      title: "Username",
      type: "string",
      description:
        "Username/profile handle for GitHub or TikTok Shop creator showcase operations.",
      editor: "textfield",
    },
    repo: {
      title: "Repository",
      type: "string",
      description: "GitHub repository URL or owner/name.",
      editor: "textfield",
    },
    state: {
      title: "Pull request state",
      type: "string",
      description: "GitHub pull request state: open, closed, or all.",
      editor: "select",
      enum: ["open", "closed", "all"],
      enumTitles: ["Open", "Closed", "All"],
    },
    sort: {
      title: "Sort",
      type: "string",
      description: "Sort mode for endpoints that support it, e.g. relevance or date.",
      editor: "textfield",
    },
    advertiser: {
      title: "Advertiser",
      type: "string",
      description:
        "Advertiser name, domain, or Google advertiser ID for Google Ads Transparency Center operations.",
      editor: "textfield",
    },
    creative_id: {
      title: "Creative ID",
      type: "string",
      description: "Google creative/ad ID or preview URL.",
      editor: "textfield",
    },
    query: {
      title: "Topic (popular hashtags)",
      type: "string",
      description:
        "Topic/keyword for tiktok_popular_hashtags. Optional; distinct from the search query field.",
      editor: "textfield",
    },
    baseUrl: {
      title: "API base URL",
      type: "string",
      description:
        "Advanced: override the Captapi API base URL. Leave as default unless self-hosting.",
      editor: "textfield",
      default: "https://api.captapi.com",
      sectionCaption: "Advanced",
    },
  },
  required: ["apiKey", "operation"],
};
writeJson(".actor/input_schema.json", inputSchema);

console.log(
  `Generated input_schema.json + endpoints.json for ${ENDPOINTS.length} operations.\n\nOperation -> required(*) params:\n${opLines}`,
);
