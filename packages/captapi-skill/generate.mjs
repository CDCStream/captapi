#!/usr/bin/env node
/**
 * Generates SKILL.md from the shared Captapi endpoint catalog so the agent
 * skill never drifts from the MCP server / API. Run after changing the
 * catalog:  `node generate.mjs`  (build @captapi/mcp first).
 */
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { ENDPOINTS } from "../captapi-mcp/dist/catalog.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const API_URL = "https://api.captapi.com";
const SITE_URL = "https://captapi.com";

const PLATFORM_LABEL = {
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  facebook: "Facebook",
  twitter: "Twitter / X",
  reddit: "Reddit",
  threads: "Threads",
  bluesky: "Bluesky",
  pinterest: "Pinterest",
  linkedin: "LinkedIn",
  rumble: "Rumble",
  tiktok_shop: "TikTok Shop",
  github: "GitHub",
  google: "Google Search",
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
  ad_library: "Public Ad Libraries",
};

const PLATFORM_ORDER = [
  "youtube",
  "tiktok",
  "instagram",
  "facebook",
  "twitter",
  "reddit",
  "threads",
  "bluesky",
  "pinterest",
  "linkedin",
  "rumble",
  "tiktok_shop",
  "github",
  "google",
  "twitch",
  "spotify",
  "soundcloud",
  "linktree",
  "snapchat",
  "truth_social",
  "kick",
  "amazon_shop",
  "age_gender",
  "kwai",
  "komi",
  "pillar",
  "linkbio",
  "linkme",
  "account",
  "ad_library",
];

function paramStr(p) {
  return `\`${p.name}\`${p.required ? "" : "?"} (${p.type})`;
}

function endpointRows(platform) {
  return ENDPOINTS.filter((e) => e.platform === platform)
    .map((e) => {
      const ps = e.params.map(paramStr).join(", ") || "none";
      return `| \`${e.tool}\` | \`${e.path}\` | ${ps} | ${e.credits} |`;
    })
    .join("\n");
}

function platformSection(platform) {
  return `### ${PLATFORM_LABEL[platform]}

| Tool / endpoint | REST path | Parameters | Credits |
| --- | --- | --- | --- |
${endpointRows(platform)}`;
}

const total = ENDPOINTS.length;
const platformCount = PLATFORM_ORDER.filter((platform) => platform !== "account").length;

const body = `---
name: captapi
description: Use when extracting public social-media and web data from YouTube, TikTok, Instagram, Facebook, X/Twitter, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, GitHub, Google Search, Twitch, Spotify, SoundCloud, Linktree, Snapchat, Truth Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop, TikTok Shop, Age/Gender enrichment, public Ad Libraries, or Captapi account usage — transcripts, AI summaries, comments, video/post details, profile & channel stats, search, hashtag/music lookups, commerce data, video downloads, credit balance, and request history. Captapi is one REST API (and MCP server) covering all ${platformCount} data platforms with a single key. Trigger on requests like "get this YouTube transcript", "scrape this TikTok profile", "fetch Instagram reel comments", or "summarize this video".
---

# Captapi

Captapi is one API for structured data from **YouTube, TikTok, Instagram, Facebook, X (Twitter), Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, GitHub, Google Search, Twitch, Spotify, SoundCloud, Linktree, Snapchat, Truth Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop, TikTok Shop, Age/Gender enrichment, public Ad Libraries, and account usage utilities**. One key works across all ${platformCount} data platforms. No OAuth, no per-platform SDKs. Responses are clean JSON. Pass cache=true for the 24h response cache (repeat hits cost 0 credits); default is cache=false (always fresh). ${total} endpoints total.

- Base URL: \`${API_URL}\`
- Docs: ${SITE_URL}/docs · Full machine reference: ${SITE_URL}/llms-full.txt

## Step 0 — Get the API key (ask the human)

Using Captapi requires a \`capt_live_...\` API key, and **creating one requires a human** (sign-up cannot be automated). Before doing anything else:

1. If you do **not** already have a key, ask the user: *"Create a Captapi API key at ${SITE_URL}/dashboard/api-keys (100 free credits, no card) and paste it here."*
2. Never guess, invent, or try to sign up for a key. Store the key the user gives you and use it for all requests.

## How to call Captapi

Every endpoint is a single authenticated \`GET\` request. Pass parameters as URL query params (URL-encode values). Send the key as a Bearer token:

\`\`\`bash
curl "${API_URL}/v1/youtube/transcript?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ" \\
  -H "Authorization: Bearer capt_live_..."
\`\`\`

Response shape:

\`\`\`json
{ "success": true, "cached": false, "creditsUsed": 2, "data": { "language": "en", "text": "..." } }
\`\`\`

If you have the **MCP server** connected instead, call the tool named in the tables below (e.g. \`youtube_transcript\`) with the same parameters — no URL building needed.

## Use from the command line (@captapi/cli)

For shell tasks, scripts, or when no MCP client is available, the official CLI calls the same API. Every endpoint is a subcommand (the tool name with dashes), parameters are flags, and results print as JSON to stdout:

\`\`\`bash
npx @captapi/cli login                 # save the human-provided key to ~/.captapi/config.json
npx @captapi/cli balance               # remaining credits
npx @captapi/cli list                  # all ${total} commands
npx @captapi/cli youtube-transcript --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
npx @captapi/cli tiktok-comment-replies --url "<video>" --comment_id "<id>" --limit 20
\`\`\`

The CLI reads the key from \`~/.captapi/config.json\` (via \`login\`) or the \`CAPTAPI_API_KEY\` env var. \`npx @captapi/cli agent add cursor\` writes the MCP config into Cursor/Claude for you. Same auth, credits, and error codes as the REST API.

## Use in n8n workflows (n8n-nodes-captapi)

For no-code/low-code automations, the official \`n8n-nodes-captapi\` community node exposes all ${total} endpoints in n8n. Install it from **Settings → Community Nodes** (package \`n8n-nodes-captapi\`; self-hosted: \`npm install n8n-nodes-captapi\`, then restart). Create a **Captapi API** credential with the human-provided \`capt_live_...\` key, add the **Captapi** node, pick a **Platform** and **Operation**, and it returns the same structured JSON as the REST API for downstream nodes.

## Use in Make.com scenarios (custom app)

For Make.com (Integromat), the Captapi custom app exposes all ${total} endpoints as action modules grouped by platform. Create a **Captapi API Key** connection with the human-provided \`capt_live_...\` key (verified against \`/v1/account/limits\`), then drop the module you need into a scenario, fill in the \`url\` (or search query) and optional \`limit\`, and it returns the same structured JSON \`data\` as the REST API for downstream modules.

## Use on Apify (BYO-key Actor)

On Apify, the Captapi Actor is a bring-your-own-key wrapper around the REST API (no scraping). Set the \`apiKey\` input to the human-provided \`capt_live_...\` key, choose an \`operation\` (any of the ${total} endpoints), fill the fields it needs (\`url\` / search query / \`limit\` / ...), and the Actor returns one dataset item with the same structured JSON \`data\` as the REST API. Credits are billed to the user's own Captapi account. The Actor is also callable through Apify's MCP server (mcp.apify.com), so agents already connected to Apify can run it by name.

## Choosing the right endpoint

- **Single piece of content** (one video / reel / post): use \`*_transcript\`, \`*_summarize\`, \`*_video_details\` / \`*_details\`, or \`*_comments\` with the content \`url\`.
- **A creator / account**: use \`*_channel_details\` (stats) or \`*_channel_posts\` / \`*_channel_reels\` (their content) with the profile \`url\`.
- **Discovery**: use \`*_search\`, \`*_hashtag_search\`, or \`*_user_search\` with a \`q\` query.

## Parameter rules (important gotchas)

- \`url\` — pass the **full public URL** of the video/reel/post/profile. Each endpoint's table notes the expected URL type.
- \`q\` — search query or keyword (min 2 chars). For hashtag endpoints, pass the tag **without** \`#\`.
- \`limit\` — optional; controls how many items list/search/comment endpoints return. **Billed per result**, so request only what you need. Defaults and maxes vary per endpoint.
- \`language\` — optional ISO code (e.g. \`en\`) for the **YouTube** transcript/summary endpoints (incl. Shorts); defaults to auto-detect. Other platforms' transcript/summary endpoints take only \`url\`.
- \`comment_id\` — required for \`*_comment_replies\`; get it from the corresponding \`*_comments\` response.

## Credits & errors

- Each endpoint costs a fixed number of credits (see tables). **Cached results (within 24h) cost 0.** Failed or empty results are **never charged**.
- Error responses are non-2xx with \`{ "detail": "..." }\`:
  - \`401\` — missing/invalid key. Re-check the key with the user.
  - \`402\` — out of credits. Tell the user to top up at ${SITE_URL}/dashboard/billing.
  - \`422\` — unprocessable (e.g. the video has no captions). Not charged; do not retry blindly.
  - \`429\` — rate limited. Back off and retry after a short delay.

## Endpoint reference

${PLATFORM_ORDER.map(platformSection).join("\n\n")}

---
Generated from the Captapi catalog. Do not edit by hand — run \`node generate.mjs\`.
`;

writeFileSync(join(__dirname, "SKILL.md"), body, "utf8");
console.log(`Wrote SKILL.md (${total} endpoints).`);
