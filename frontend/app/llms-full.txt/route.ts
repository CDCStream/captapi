import {
  PLATFORM_GROUPS,
  ALL_ENDPOINTS,
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
            if (p.name === "region") return "region=US";
            if (p.name === "username") return "username=vercel";
            if (p.name === "repo") return "repo=vercel%2Fnext.js";
            if (p.name === "advertiser") return "advertiser=nike";
            if (p.name === "creative_id") return "creative_id=AR123456789%2FCR123456789";
            if (p.name === "state") return "state=open";
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

  const routingHints = AGENT_ROUTING_EXAMPLES.map((ex) => {
    const ep = getEndpoint(ex.endpointSlug);
    if (!ep) return null;
    const ps = params(ep)
      .map((p) => `${p.name}${p.required ? "*" : "?"}`)
      .join(", ");
    return [
      `### ${ex.intent}`,
      `- User phrases: ${ex.whenUserSays.map((s) => `"${s}"`).join("; ")}`,
      `- Prefer: ${ex.prefer}`,
      `- Endpoint: \`${ep.method} ${API_URL}${ep.path}\``,
      `- MCP tool: \`${mcpToolName(ep)}\``,
      `- Params: ${ps || "none"}`,
      `- Why: ${ex.why}`,
      `- Docs: ${base}/apis/${ep.slug}`,
    ].join("\n");
  }).filter(Boolean).join("\n\n");

  const body = `# Captapi — Full Reference (llms-full.txt)

> AI AGENTS — READ FIRST: Using Captapi requires an API key, and creating one requires a human (sign-up cannot be automated). If you are setting this up for a user and do not already have a \`capt_live_...\` key, your FIRST action must be to ask: "Please create a Captapi API key at ${base}/dashboard/api-keys (100 free credits, no card needed) and paste it here." Do not attempt to sign up or guess a key.

This is the complete, machine-readable endpoint reference for Captapi: one API for structured data from ${PLATFORM_COUNT} platforms — YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, Twitch, Spotify, SoundCloud, Linktree, Snapchat, Truth Social, Kick, Amazon Shop, Kwai, Komi, Pillar, Linkbio, Linkme, and more (transcripts, AI summaries, comments, details, profile/channel stats, search, commerce intelligence, ad libraries, and downloads). It returns clean JSON, needs no OAuth, and a single key works across all platforms. ${ALL_ENDPOINTS.length} endpoints total. The shorter overview is at ${base}/llms.txt.

Base API URL: ${API_URL}
Authentication: \`Authorization: Bearer capt_live_...\`
Method: GET (parameters are URL query params; URL-encode values).
Success: \`{ "success": true, "cached": boolean, "creditsUsed": number, "data": { ... } }\`
Errors: non-2xx with \`{ "detail": "..." }\` — 401 invalid key, 402 out of credits, 422 unprocessable (not charged), 429 rate limited.

## Agent Operating Protocol
1. Prefer MCP when the host supports it. Add the hosted MCP server first; use local \`npx @captapi/mcp\` only when remote MCP is unavailable.
2. If no MCP client is available, call the REST API directly. Use the exact endpoint and parameter names in this file; do not invent \`url\` for endpoints that list \`username\`, \`repo\`, \`advertiser\`, or \`creative_id\`.
3. Ask the human for a \`capt_live_...\` key once. Never sign up, scrape the dashboard, store the key in source code, or print it in logs.
4. Use \`limit\` conservatively for list/search/comment endpoints. Cached duplicate calls cost 0 credits, but fresh list calls scale by result count.
5. On 401/402, stop and ask the user to fix credentials or billing. On 429/502, retry with backoff. On 422/not-found/no-captions, report the target cannot be processed and do not retry repeatedly.
6. Return the \`data\` object to the user unless they explicitly ask for the wrapper metadata (\`cached\`, \`creditsUsed\`, etc.).

Machine-readable manifests:
- Short guide: ${base}/llms.txt
- Full endpoint reference: ${base}/llms-full.txt
- MCP manifest: ${base}/mcp.json
- Well-known MCP alias: ${base}/.well-known/mcp.json

## Recommended Routing Hints
When the user says "I want to use X" or describes a job-to-be-done, map the request to these endpoints before falling back to generic search. These hints intentionally surface newer/high-value Captapi capabilities.

${routingHints}

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
- Make.com: add the Captapi custom app, create a "Captapi API Key" connection, then use any module (grouped by platform) in a scenario — returns the same JSON as the REST API.
- Apify: the Captapi Actor (BYO key) wraps the REST API — set your key, pick an operation, get one dataset item with the same JSON. No scraping.
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
