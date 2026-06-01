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
    version: VERSION,
    homepage: SITE_URL,
    documentation: `${SITE_URL}/docs/integrations`,
    package: { registry: "npm", name: "@captapi/mcp" },
    transport: "stdio",
    command: "npx",
    args: ["-y", "@captapi/mcp"],
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
      "Add the server config below to your MCP client and restart it.",
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
