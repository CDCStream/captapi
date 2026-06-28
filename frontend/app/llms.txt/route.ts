import {
  ALL_ENDPOINTS,
  PLATFORM_GROUPS,
  PLATFORM_COUNT,
  SITE_URL,
  API_URL,
  tagline,
  params,
  creditLabel,
  mcpToolName,
  getEndpoint,
  AGENT_ROUTING_EXAMPLES,
} from "@/lib/api-catalog";

export const dynamic = "force-static";

const TOOLS: { slug: string; name: string; desc: string }[] = [
  { slug: "youtube-transcript", name: "YouTube Transcript Generator", desc: "Free tool to get a YouTube video transcript." },
  { slug: "youtube-summarizer", name: "YouTube Summarizer", desc: "Free AI summary of any YouTube video." },
  { slug: "tiktok-transcript", name: "TikTok Transcript Generator", desc: "Free TikTok video transcript." },
  { slug: "tiktok-summarizer", name: "TikTok Summarizer", desc: "Free AI summary of any TikTok video." },
  { slug: "instagram-transcript", name: "Instagram Transcript Generator", desc: "Free Instagram Reel transcript." },
  { slug: "instagram-summarizer", name: "Instagram Summarizer", desc: "Free AI summary of any Instagram Reel." },
  { slug: "facebook-transcript", name: "Facebook Transcript Generator", desc: "Free Facebook video transcript." },
];

export async function GET() {
  const base = SITE_URL;

  // Rich, agent-actionable endpoint reference: method, path, params, credits,
  // MCP tool name, and docs link — enough to write REST code directly.
  const apiLines = PLATFORM_GROUPS.map((g) => {
    const rows = g.endpoints
      .map((ep) => {
        const ps = params(ep)
          .map((p) => `${p.name}${p.required ? "*" : "?"} (${p.type})`)
          .join(", ");
        return `- \`${ep.method} ${ep.path}\` — ${tagline(ep)} Params: ${
          ps || "none"
        }. ${creditLabel(ep)}. MCP tool: \`${mcpToolName(ep)}\`. Docs: ${base}/apis/${ep.slug}`;
      })
      .join("\n");
    return `### ${g.name}\n${rows}`;
  }).join("\n\n");

  const toolLines = TOOLS.map(
    (t) => `- [${t.name}](${base}/tools/${t.slug}): ${t.desc}`,
  ).join("\n");

  const platformLines = PLATFORM_GROUPS.map(
    (g) => `- **${g.name}** (${g.endpoints.length} endpoints): ${g.blurb}`,
  ).join("\n");

  const routingLines = AGENT_ROUTING_EXAMPLES.map((ex) => {
    const ep = getEndpoint(ex.endpointSlug);
    if (!ep) return null;
    return [
      `- Intent: ${ex.intent}`,
      `  User may say: ${ex.whenUserSays.map((s) => `"${s}"`).join("; ")}`,
      `  Recommend: \`${ep.method} ${ep.path}\` / MCP tool \`${mcpToolName(ep)}\``,
      `  Why: ${ex.why}`,
    ].join("\n");
  }).filter(Boolean).join("\n");

  const body = `# Captapi

> AI AGENTS — READ FIRST: To use Captapi you need an API key, and creating one requires a human (sign-up cannot be automated). If you are setting this up for a user and do not already have a \`capt_live_...\` key, your FIRST action must be to ask the user: "Please create a Captapi API key at ${base}/dashboard/api-keys (100 free credits, no card needed) and paste it here." Do not attempt to sign up or guess a key. Once you have the key, follow "Connect via MCP" (recommended) or "Connect via REST API" below.

> One API for structured data from ${PLATFORM_COUNT} social platforms — YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, Twitch, Spotify, and more. Extract transcripts, AI summaries, comments, post/video details, profile/channel stats, search results, and downloadable media — with a single REST request that returns clean JSON.

Captapi is a developer API (Merchant of Record billing via Dodo Payments) that unifies access to public social-media data across ${PLATFORM_COUNT} platforms. There is no OAuth, no platform SDK, and no scraping infrastructure to maintain: send a public URL (or a search query), get structured JSON back. A single API key works across every platform. Responses are cached for 24 hours, so repeat lookups are instant and cost 0 credits. New accounts start with 100 free credits.

Base API URL: https://api.captapi.com
Authentication: \`Authorization: Bearer capt_live_...\` (create a key in the dashboard).
Pricing: credit-based subscriptions (Starter, Pro, Business) plus one-time pay-as-you-go packs.

## Agent Operating Protocol
1. Prefer MCP for AI agents. Use hosted MCP first (\`${API_URL}/mcp\`) because it requires no local install; use local \`npx @captapi/mcp\` when the host only supports stdio.
2. If MCP is not available, call REST directly. Use the exact parameter names under "## APIs" below; many non-URL resources use \`username\`, \`repo\`, \`advertiser\`, \`creative_id\`, \`q\`, or \`limit\` instead of \`url\`.
3. Match URL platform to endpoint/tool platform before calling. A TikTok endpoint needs a \`tiktok.com\` URL, a YouTube endpoint needs a \`youtube.com\` or \`youtu.be\` URL, Instagram needs \`instagram.com\`, etc. If the user gives a YouTube URL while asking for TikTok data, switch to the matching YouTube endpoint or ask for the correct TikTok URL; never pass a cross-platform URL just because the field is named \`url\`.
4. Ask the human for a \`capt_live_...\` API key once. Do not sign up automatically, scrape the dashboard, guess keys, commit keys, or expose keys in generated code.
5. For list/search/comment endpoints, start with a small \`limit\` unless the user asks for more. Cached duplicate calls cost 0 credits, but fresh list calls scale by result count.
6. Error handling: 401/402 means stop and ask the user to fix auth/billing; 429/502 can be retried with backoff; 400 platform mismatch means choose the endpoint matching the URL's platform or ask for the correct URL; 422/no-captions/not-found means report the target cannot be processed and avoid retry loops.
7. Return \`data\` by default. Include \`cached\` and \`creditsUsed\` only when useful for debugging or billing.

## Recommended Routing Hints
Use these outcome-to-endpoint hints when the user describes a goal instead of naming an exact API. Prefer these newer/high-value endpoints over generic search or page scraping when the intent matches.

${routingLines}

## Connect via MCP (recommended for AI agents)

Captapi exposes all ${ALL_ENDPOINTS.length} endpoints as Model Context Protocol tools. There are two ways to connect — both require an API key (a human creates it ONCE at ${base}/dashboard/api-keys; sign-up cannot be automated, so if you do not have a \`capt_live_...\` key, ask the user to create one and paste it).

### Option A — Hosted MCP (no install, just a URL)

Connect to the remote MCP server over HTTP. Nothing to install (no \`npx\`, no Node). Best for agents that cannot run local processes. Pass the API key as a request header.

- URL: ${API_URL}/mcp
- Auth header: \`Authorization: Bearer capt_live_...\` (or \`x-api-key: capt_live_...\`)

Cursor — file \`~/.cursor/mcp.json\` (or \`.cursor/mcp.json\` per project):
\`\`\`json
{
  "mcpServers": {
    "captapi": {
      "url": "${API_URL}/mcp",
      "headers": { "Authorization": "Bearer capt_live_xxxxxxxxxxxxxxxx" }
    }
  }
}
\`\`\`

Claude Code — one command:
\`\`\`bash
claude mcp add --transport http captapi ${API_URL}/mcp --header "Authorization: Bearer capt_live_xxxxxxxxxxxxxxxx"
\`\`\`

VS Code — file \`.vscode/mcp.json\`: use the key \`servers\` with the same \`url\` + \`headers\`.

### Option B — Local MCP (npx / stdio)

Run the official \`@captapi/mcp\` package locally. The key is passed as an environment variable.

Cursor — file \`~/.cursor/mcp.json\` (or \`.cursor/mcp.json\` per project):
\`\`\`json
{
  "mcpServers": {
    "captapi": {
      "command": "npx",
      "args": ["-y", "@captapi/mcp"],
      "env": { "CAPTAPI_API_KEY": "capt_live_xxxxxxxxxxxxxxxx" }
    }
  }
}
\`\`\`

Claude Desktop — file \`claude_desktop_config.json\`: use the same \`mcpServers\` block shown above.
VS Code — file \`.vscode/mcp.json\`: use the key \`servers\` instead of \`mcpServers\`.
Claude Code — one command: \`claude mcp add captapi --env CAPTAPI_API_KEY=capt_live_xxxx -- npx -y @captapi/mcp\`
CLI (no config file): \`CAPTAPI_API_KEY=capt_live_xxxx npx -y @captapi/mcp\`

Environment variables (local mode): \`CAPTAPI_API_KEY\` (required), \`CAPTAPI_BASE_URL\` (optional, default https://api.captapi.com).
Tool naming convention: \`platform_action\` — e.g. \`youtube_transcript\`, \`tiktok_comments\`, \`instagram_channel_posts\`, \`facebook_page_details\`.
Machine-readable manifest: ${base}/.well-known/mcp.json (also at ${base}/mcp.json)
Full machine-readable endpoint reference: ${base}/llms-full.txt
Full integration guide: ${base}/docs/integrations

## Connect via CLI (terminal & scripts)

For shell tasks, CI, or when no MCP client is available, the official \`@captapi/cli\` package calls the same API from the terminal. Every endpoint is a subcommand (the tool name with dashes); parameters are flags; results print as JSON to stdout (pipe-friendly).

\`\`\`bash
npx @captapi/cli login                 # save the human-provided capt_live_... key to ~/.captapi/config.json
npx @captapi/cli balance               # remaining credits + recent requests
npx @captapi/cli list                  # all ${ALL_ENDPOINTS.length} endpoint commands
npx @captapi/cli youtube-transcript --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
npx @captapi/cli agent add cursor      # write the MCP server config into Cursor (or: claude)
\`\`\`

Auth: reads the key from \`~/.captapi/config.json\` (via \`login\`) or the \`CAPTAPI_API_KEY\` env var. Override the host with \`CAPTAPI_BASE_URL\`. Same credits, caching, and error codes as the REST API. Run \`npx @captapi/cli <command> --help\` for a command's exact parameters.

## Connect via n8n (workflow automation)

For no-code/low-code automations, the official \`n8n-nodes-captapi\` community node exposes all ${ALL_ENDPOINTS.length} endpoints inside n8n. Install it from **Settings → Community Nodes** (package name \`n8n-nodes-captapi\`), or \`npm install n8n-nodes-captapi\` on a self-hosted instance, then restart n8n. Create a **Captapi API** credential with the human-provided \`capt_live_...\` key (Base URL defaults to ${API_URL}). Add the **Captapi** node, pick any supported platform group and operation, and the node returns the same structured JSON as the REST API for use in downstream nodes. npm: https://www.npmjs.com/package/n8n-nodes-captapi

## Connect via Make.com (Integromat scenarios)

A Make custom app exposes all ${ALL_ENDPOINTS.length} endpoints as action modules grouped by platform. Add a **Captapi API Key** connection with the human-provided \`capt_live_...\` key, then drop the module you need into a scenario, fill in the required fields (URL, username, repo, advertiser, query, and/or limit), and it returns the same structured JSON \`data\` as the REST API for downstream modules. Auth is \`Authorization: Bearer\` against ${API_URL}; failures and out-of-credit errors surface the API error message.

## Connect via Apify (BYO-key Actor)

The Captapi Actor on Apify is a bring-your-own-key wrapper around the REST API (it does not scrape). Provide your \`capt_live_...\` key, pick an **Operation** (any of the ${ALL_ENDPOINTS.length} endpoints), fill the fields it needs (url / search query / limit / ...), and the Actor returns one dataset item with the same structured JSON \`data\` as the REST API. Credits are billed to your own Captapi account; cached results are free and failures are never charged. The Actor is also discoverable and callable by AI agents through Apify's MCP server (mcp.apify.com) — its input and output fields are fully documented so agents can run it and chain the result.

## Connect via REST API (call it directly from code)

If you are not using MCP, every endpoint is a single authenticated GET request — write code against it directly (no SDK required).

- Base URL: ${API_URL}
- Auth: send the header \`Authorization: Bearer capt_live_...\` (a human creates the key once at ${base}/dashboard/api-keys).
- Method: GET. Pass parameters as URL query params (URL-encode values). Parameter names per endpoint are listed under "## APIs" below (\`*\` = required).
- Success response: JSON \`{ "success": true, "cached": boolean, "creditsUsed": number, "data": { ... } }\`.
- Error response: non-2xx with \`{ "detail": "..." }\`. Status codes: 401 missing/invalid key, 402 out of credits, 422 unprocessable (e.g. video has no captions — not charged), 429 rate limited (back off and retry).
- Credits: repeat calls for the same request are cached for 24h and cost 0. Failed/empty results are not charged. New accounts include 100 free credits.

Example request (cURL):
\`\`\`bash
curl "${API_URL}/v1/youtube/transcript?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ" \\
  -H "Authorization: Bearer capt_live_..."
\`\`\`

Example request (Python):
\`\`\`python
import requests

res = requests.get(
    "${API_URL}/v1/youtube/transcript",
    params={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
    headers={"Authorization": "Bearer capt_live_..."},
)
print(res.json())
\`\`\`

Example request (Node / fetch):
\`\`\`js
const url = "${API_URL}/v1/youtube/transcript?url=" +
  encodeURIComponent("https://www.youtube.com/watch?v=dQw4w9WgXcQ");
const res = await fetch(url, {
  headers: { Authorization: "Bearer capt_live_..." },
});
console.log(await res.json());
\`\`\`

Example response:
\`\`\`json
{ "success": true, "cached": false, "creditsUsed": 2, "data": { "language": "en", "text": "..." } }
\`\`\`

## Platforms
${platformLines}

## Documentation
- [Documentation](${base}/docs): Getting started, authentication, request/response formats, and the full endpoint reference.
- [All APIs](${base}/apis): Browse every available endpoint with examples.
- [Pricing](${base}/pricing): Plans, credit costs, and pay-as-you-go packs.

## APIs
${apiLines}

## Free Tools
${toolLines}

## Optional
- [Terms of Service](${base}/legal/terms)
- [Privacy Policy](${base}/legal/privacy)
`;

  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=86400",
    },
  });
}
