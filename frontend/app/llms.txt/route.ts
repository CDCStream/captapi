import {
  ALL_ENDPOINTS,
  PLATFORM_GROUPS,
  SITE_URL,
  API_URL,
  tagline,
  params,
  creditLabel,
  mcpToolName,
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

  const body = `# Captapi

> AI AGENTS — READ FIRST: To use Captapi you need an API key, and creating one requires a human (sign-up cannot be automated). If you are setting this up for a user and do not already have a \`capt_live_...\` key, your FIRST action must be to ask the user: "Please create a Captapi API key at ${base}/dashboard/api-keys (100 free credits, no card needed) and paste it here." Do not attempt to sign up or guess a key. Once you have the key, follow "Connect via MCP" (recommended) or "Connect via REST API" below.

> One API for structured data from YouTube, TikTok, Instagram, and Facebook. Extract transcripts, AI summaries, comments, video details, profile/channel stats, search results, and downloadable media — with a single REST request that returns clean JSON.

Captapi is a developer API (Merchant of Record billing via Dodo Payments) that unifies access to public social-media video data across four platforms. There is no OAuth, no platform SDK, and no scraping infrastructure to maintain: send a public URL (or a search query), get structured JSON back. A single API key works across every platform. Responses are cached for 24 hours, so repeat lookups are instant and cost 0 credits. New accounts start with 100 free credits.

Base API URL: https://api.captapi.com
Authentication: \`Authorization: Bearer capt_live_...\` (create a key in the dashboard).
Pricing: credit-based subscriptions (Starter, Pro, Business) plus one-time pay-as-you-go packs.

## Connect via MCP (recommended for AI agents)

Captapi ships an official Model Context Protocol server, \`@captapi/mcp\` (npm), that exposes all ${ALL_ENDPOINTS.length} endpoints as MCP tools. This is the easiest way for an AI agent to use Captapi.

Setup is two steps:
1. A human creates an API key ONCE at ${base}/dashboard/api-keys. Sign-up and key creation cannot be automated by an agent — if you do not have a \`capt_live_...\` key, ask the user to create one and paste it. New accounts include 100 free credits.
2. Add the MCP server to the client config and restart the client.

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
CLI (no config file): \`CAPTAPI_API_KEY=capt_live_xxxx npx -y @captapi/mcp\`

Environment variables: \`CAPTAPI_API_KEY\` (required), \`CAPTAPI_BASE_URL\` (optional, default https://api.captapi.com).
Tool naming convention: \`platform_action\` — e.g. \`youtube_transcript\`, \`tiktok_comments\`, \`instagram_channel_posts\`, \`facebook_page_details\`.
Machine-readable manifest: ${base}/.well-known/mcp.json (also at ${base}/mcp.json)
Full integration guide: ${base}/docs/integrations

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
