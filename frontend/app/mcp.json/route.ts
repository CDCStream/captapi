import { ALL_ENDPOINTS, SITE_URL, API_URL } from "@/lib/api-catalog";

export const dynamic = "force-static";

const VERSION = "0.2.0";

export async function GET() {
  const manifest = {
    $schema: "https://modelcontextprotocol.io/schema/mcp.json",
    name: "captapi",
    title: "Captapi",
    description:
      "Official Captapi MCP server. Gives AI agents structured data from YouTube, TikTok, Instagram, and Facebook — transcripts, summaries, comments, profiles, search, and downloads.",
    instructions_for_agent: `Before installing, you need a Captapi API key, and key creation requires a human. If you do not already have a capt_live_... key, your FIRST action must be to ask the user to create one at ${SITE_URL}/dashboard/api-keys (100 free credits, no card) and paste it back. Do not sign up or guess a key. Then add the config from "clients" below and restart the client.`,
    version: VERSION,
    homepage: SITE_URL,
    documentation: `${SITE_URL}/docs/integrations`,
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
      naming: "platform_action",
      examples: [
        "youtube_transcript",
        "tiktok_comments",
        "instagram_channel_posts",
        "facebook_page_details",
      ],
    },
    api: {
      base_url: API_URL,
      auth_header: "Authorization: Bearer <CAPTAPI_API_KEY>",
    },
  };

  return new Response(JSON.stringify(manifest, null, 2), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=86400",
    },
  });
}
