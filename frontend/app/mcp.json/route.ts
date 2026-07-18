import {
  ALL_ENDPOINTS,
  PLATFORM_COUNT,
  SITE_URL,
  API_URL,
  params,
  mcpToolName,
  getEndpoint,
  AGENT_ROUTING_EXAMPLES,
} from "@/lib/api-catalog";

export const dynamic = "force-static";

const VERSION = "0.4.0"; // keep in sync with packages/captapi-mcp/package.json

export async function GET() {
  const manifest = {
    $schema: "https://modelcontextprotocol.io/schema/mcp.json",
    name: "captapi",
    title: "Captapi",
    description: `Official Captapi MCP server. Gives AI agents structured public data from ${PLATFORM_COUNT} platforms — including YouTube, TikTok, Instagram, Facebook, X/Twitter, Reddit, LinkedIn, Threads, Pinterest, Twitch, Spotify, Ad Library, TikTok Shop, GitHub, Kwai, and link-in-bio pages — with transcripts, summaries, comments, profiles, search, commerce data, and ad intelligence.`,
    instructions_for_agent: `Before installing, you need a Captapi API key, and key creation requires a human. If you do not already have a capt_live_... key, your FIRST action must be to ask the user to create one at ${SITE_URL}/dashboard/api-keys (100 free credits, no card) and paste it back. Do not sign up or guess a key. Then add the config from "clients" below and restart the client.`,
    version: VERSION,
    homepage: SITE_URL,
    documentation: `${SITE_URL}/docs/integrations`,
    llms_txt: `${SITE_URL}/llms.txt`,
    llms_full_txt: `${SITE_URL}/llms-full.txt`,
    package: { registry: "npm", name: "@captapi/mcp" },
    cli: {
      package: { registry: "npm", name: "@captapi/cli" },
      bin: "captapi",
      description:
        "Official command-line interface. Calls the same API from the terminal; every endpoint is a subcommand, params are flags, output is JSON.",
      install: "npm install -g @captapi/cli",
      examples: [
        "npx @captapi/cli login",
        "npx @captapi/cli balance",
        "npx @captapi/cli list",
        'npx @captapi/cli youtube-transcript --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"',
        "npx @captapi/cli agent add cursor",
      ],
      auth: "Reads CAPTAPI_API_KEY env var or ~/.captapi/config.json (via `captapi login`).",
    },
    n8n: {
      package: { registry: "npm", name: "n8n-nodes-captapi" },
      type: "n8n-community-node",
      description:
        "Official n8n community node. Exposes all endpoints as a single Captapi node (Platform → Operation) for no-code/low-code workflows.",
      install: "In n8n: Settings → Community Nodes → install `n8n-nodes-captapi` (self-hosted: `npm install n8n-nodes-captapi`, then restart n8n).",
      credential: "Create a 'Captapi API' credential with your capt_live_... key; Base URL defaults to the Captapi API.",
      auth: "Captapi API credential (API key). The credential test calls /v1/account/limits.",
    },
    make: {
      type: "make-custom-app",
      description:
        "Captapi custom app for Make.com (Integromat). Exposes all endpoints as action modules grouped by platform for no-code scenarios.",
      install: "Add the Captapi app in Make, or deploy the local app from packages/captapi-make with the Make Apps Editor.",
      credential: "Create a 'Captapi API Key' connection with your capt_live_... key; verified against /v1/account/limits.",
      auth: "Authorization: Bearer <CAPTAPI_API_KEY> (set on the connection).",
    },
    apify: {
      type: "apify-actor",
      description:
        "Captapi Actor on Apify (bring-your-own-key wrapper around the REST API, no scraping). Pick an operation, get one dataset item with the same JSON.",
      install: "Run the Captapi Actor on Apify, or push the source in packages/captapi-apify with `apify push`.",
      credential: "Set the apiKey input to your capt_live_... key (stored encrypted). Credits are billed to your own Captapi account.",
      auth: "Authorization: Bearer <CAPTAPI_API_KEY> (sent by the Actor).",
    },
    transport: "stdio",
    command: "npx",
    args: ["-y", "@captapi/mcp"],
    remote: {
      transport: "http",
      url: `${API_URL}/mcp`,
      auth_header: "Authorization: Bearer <CAPTAPI_API_KEY>",
      alt_auth_header: "x-api-key: <CAPTAPI_API_KEY>",
      note: "Hosted MCP — no install required. Add the url to your client and pass your capt_live_... key via header.",
      clients: {
        cursor: {
          file: "~/.cursor/mcp.json",
          config: {
            mcpServers: {
              captapi: {
                url: `${API_URL}/mcp`,
                headers: { Authorization: "Bearer capt_live_xxxxxxxxxxxxxxxx" },
              },
            },
          },
        },
        claude_code: {
          command: `claude mcp add --transport http captapi ${API_URL}/mcp --header "Authorization: Bearer capt_live_xxxxxxxxxxxxxxxx"`,
        },
        vscode: {
          file: ".vscode/mcp.json",
          config: {
            servers: {
              captapi: {
                url: `${API_URL}/mcp`,
                headers: { Authorization: "Bearer capt_live_xxxxxxxxxxxxxxxx" },
              },
            },
          },
        },
      },
    },
    env: {
      CAPTAPI_API_KEY: {
        required: true,
        description: `Your capt_live_... API key. Create one at ${SITE_URL}/dashboard/api-keys`,
      },
      CAPTAPI_BASE_URL: {
        required: false,
        default: API_URL,
        description: "Override the Captapi API base URL.",
      },
    },
    auth: {
      type: "api_key",
      obtain: `${SITE_URL}/dashboard/api-keys`,
      note: "Sign-up and key creation require a human and cannot be automated. If you do not have a key, ask the user to create one and paste it.",
    },
    setup: [
      `A human creates an API key once at ${SITE_URL}/dashboard/api-keys (100 free credits on signup).`,
      "Pick a transport: 'remote' (hosted, just a URL — no install) or stdio (local via npx).",
      "Add the matching server config to your MCP client and restart it.",
    ],
    clients: {
      cursor: {
        file: "~/.cursor/mcp.json",
        config: {
          mcpServers: {
            captapi: {
              command: "npx",
              args: ["-y", "@captapi/mcp"],
              env: { CAPTAPI_API_KEY: "capt_live_xxxxxxxxxxxxxxxx" },
            },
          },
        },
      },
      claude_desktop: {
        file: "claude_desktop_config.json",
        config: {
          mcpServers: {
            captapi: {
              command: "npx",
              args: ["-y", "@captapi/mcp"],
              env: { CAPTAPI_API_KEY: "capt_live_xxxxxxxxxxxxxxxx" },
            },
          },
        },
      },
      vscode: {
        file: ".vscode/mcp.json",
        config: {
          servers: {
            captapi: {
              command: "npx",
              args: ["-y", "@captapi/mcp"],
              env: { CAPTAPI_API_KEY: "capt_live_xxxxxxxxxxxxxxxx" },
            },
          },
        },
      },
    },
    tools: {
      count: ALL_ENDPOINTS.length,
      platform_count: PLATFORM_COUNT,
      naming: "platform_action",
      examples: [
        "youtube_transcript",
        "tiktok_comments",
        "instagram_channel_posts",
        "facebook_page_details",
        "github_repository",
        "google_ad_library_company_ads",
        "tiktok_shop_user_showcase",
      ],
    },
    api: {
      base_url: API_URL,
      auth_header: "Authorization: Bearer <CAPTAPI_API_KEY>",
      docs: `${SITE_URL}/apis`,
      openapi: `${API_URL}/v1/openapi.json`,
      endpoint_reference: `${SITE_URL}/llms-full.txt`,
    },
    agent_usage: {
      recommended_path: "Use hosted MCP first; use local stdio MCP when the client cannot connect to remote HTTP MCP; use REST as a fallback.",
      key_policy: "Ask the human for a capt_live_... key. Never sign up automatically, guess keys, commit keys, or print keys in logs.",
      parameter_policy: "Use each tool schema exactly. Some endpoints require username, repo, advertiser, creative_id, q, or limit instead of url. For url parameters, the URL platform must match the tool platform: do not pass a YouTube URL to a TikTok tool, or a TikTok URL to a YouTube tool. If the URL platform differs from the requested tool, switch to the matching platform tool or ask the user for the correct URL.",
      retry_policy: "Do not retry 401/402; ask the user to fix auth or credits. Retry 429/502 with backoff. Do not retry 400 platform mismatch; choose the endpoint matching the URL's platform or ask for the correct URL. Do not loop on 422/not-found/no-captions.",
      output_policy: "Return the API data object by default; include cached and creditsUsed only when relevant.",
    },
    routing_hints: AGENT_ROUTING_EXAMPLES.map((ex) => {
      const ep = getEndpoint(ex.endpointSlug)!;
      return {
        intent: ex.intent,
        user_phrases: ex.whenUserSays,
        prefer: ex.prefer,
        endpoint: {
          slug: ep.slug,
          method: ep.method,
          path: ep.path,
          url: `${API_URL}${ep.path}`,
          mcp_tool: mcpToolName(ep),
          params: params(ep).map((p) => ({
            name: p.name,
            type: p.type,
            required: p.required,
            description: p.description,
          })),
          docs: `${SITE_URL}/apis/${ep.slug}`,
        },
        why: ex.why,
      };
    }),
  };

  return new Response(JSON.stringify(manifest, null, 2), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=86400",
    },
  });
}
