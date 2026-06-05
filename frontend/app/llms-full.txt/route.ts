import {
  PLATFORM_GROUPS,
  ALL_ENDPOINTS,
  SITE_URL,
  API_URL,
  tagline,
  params,
  creditLabel,
  mcpToolName,
} from "@/lib/api-catalog";

export const dynamic = "force-static";

export async function GET() {
  const base = SITE_URL;

  // One fully-detailed block per endpoint: method+path, every parameter with
  // its type / required flag / description, credit cost, MCP tool name, docs
  // link, and a ready-to-run example request.
  const sections = PLATFORM_GROUPS.map((g) => {
    const blocks = g.endpoints
      .map((ep) => {
        const ps = params(ep);
        const paramLines = ps.length
          ? ps
              .map(
                (p) =>
                  `  - \`${p.name}\` (${p.type}, ${
                    p.required ? "required" : "optional"
                  }): ${p.description}`,
              )
              .join("\n")
          : "  - (no parameters)";

        // Build an example query string from each param's first sensible value.
        const example = ps
          .map((p) => {
            if (p.name === "url")
              return `url=${encodeURIComponent(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
              )}`;
            if (p.name === "q" || p.name === "query") return "q=marketing";
            if (p.name === "comment_id") return "comment_id=123456";
            if (p.name === "limit") return "limit=20";
            if (p.name === "language") return "language=en";
            if (p.name === "country") return "country=US";
            return `${p.name}=value`;
          })
          .join("&");

        return [
          `#### ${ep.name}`,
          `- ${tagline(ep)}`,
          `- Request: \`${ep.method} ${API_URL}${ep.path}\``,
          `- Parameters:`,
          paramLines,
          `- Cost: ${creditLabel(ep)} (cached results 0 credits; failures not charged)`,
          `- MCP tool: \`${mcpToolName(ep)}\``,
          `- Docs: ${base}/apis/${ep.slug}`,
          `- Example: \`curl "${API_URL}${ep.path}${
            example ? `?${example}` : ""
          }" -H "Authorization: Bearer capt_live_..."\``,
        ].join("\n");
      })
      .join("\n\n");
    return `### ${g.name} (${g.endpoints.length} endpoints)\n${g.blurb}\n\n${blocks}`;
  }).join("\n\n");

  const body = `# Captapi — Full Reference (llms-full.txt)

> AI AGENTS — READ FIRST: Using Captapi requires an API key, and creating one requires a human (sign-up cannot be automated). If you are setting this up for a user and do not already have a \`capt_live_...\` key, your FIRST action must be to ask: "Please create a Captapi API key at ${base}/dashboard/api-keys (100 free credits, no card needed) and paste it here." Do not attempt to sign up or guess a key.

This is the complete, machine-readable endpoint reference for Captapi: one API for structured data from YouTube, TikTok, Instagram, and Facebook (transcripts, AI summaries, comments, details, profile/channel stats, search, and downloads). It returns clean JSON, needs no OAuth, and a single key works across all platforms. ${ALL_ENDPOINTS.length} endpoints total. The shorter overview is at ${base}/llms.txt.

Base API URL: ${API_URL}
Authentication: \`Authorization: Bearer capt_live_...\`
Method: GET (parameters are URL query params; URL-encode values).
Success: \`{ "success": true, "cached": boolean, "creditsUsed": number, "data": { ... } }\`
Errors: non-2xx with \`{ "detail": "..." }\` — 401 invalid key, 402 out of credits, 422 unprocessable (not charged), 429 rate limited.

## Connect via MCP

Hosted (no install — just a URL):
- URL: ${API_URL}/mcp
- Auth header: \`Authorization: Bearer capt_live_...\` (or \`x-api-key: capt_live_...\`)
- Cursor \`~/.cursor/mcp.json\`: \`{ "mcpServers": { "captapi": { "url": "${API_URL}/mcp", "headers": { "Authorization": "Bearer capt_live_..." } } } }\`
- Claude Code: \`claude mcp add --transport http captapi ${API_URL}/mcp --header "Authorization: Bearer capt_live_..."\`

Local (npx / stdio):
- Cursor \`~/.cursor/mcp.json\`: \`{ "mcpServers": { "captapi": { "command": "npx", "args": ["-y", "@captapi/mcp"], "env": { "CAPTAPI_API_KEY": "capt_live_..." } } } }\`
- Tools are named \`platform_action\` (e.g. \`youtube_transcript\`). Manifest: ${base}/mcp.json

## Other ways to connect
- CLI: \`npx @captapi/cli <command>\` — every endpoint as a terminal subcommand (flags = params, JSON to stdout). https://www.npmjs.com/package/@captapi/cli
- n8n: install the \`n8n-nodes-captapi\` community node (Settings -> Community Nodes), add a "Captapi API" credential, then use the Captapi node (Platform -> Operation). https://www.npmjs.com/package/n8n-nodes-captapi
- Full integration guide: ${base}/docs/integrations

## Full Endpoint Reference

${sections}

## Links
- Documentation: ${base}/docs
- Integration guide: ${base}/docs/integrations
- All APIs: ${base}/apis
- Pricing: ${base}/pricing
`;

  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=86400",
    },
  });
}
