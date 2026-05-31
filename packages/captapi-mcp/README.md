# @captapi/mcp

Official **Captapi** MCP server. Give Claude, Cursor, VS Code, and any
MCP-compatible AI agent direct access to **62 social media data endpoints**
across YouTube, TikTok, Instagram, and Facebook — transcripts, summaries,
comments, channel stats, search, bulk lists, and downloads.

One Captapi key works across every platform. The agent calls a tool, Captapi
handles proxies, rate limits, retries, and auth, and returns clean JSON.

## Quick start

You need a Captapi API key (`capt_live_...`). Get one at
[captapi.com/dashboard/api-keys](https://captapi.com/dashboard/api-keys).

### Cursor

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per-project):

```json
{
  "mcpServers": {
    "captapi": {
      "command": "npx",
      "args": ["-y", "@captapi/mcp"],
      "env": {
        "CAPTAPI_API_KEY": "capt_live_xxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Claude Desktop

Add the same block to `claude_desktop_config.json`
(Settings → Developer → Edit Config).

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "captapi": {
      "command": "npx",
      "args": ["-y", "@captapi/mcp"],
      "env": {
        "CAPTAPI_API_KEY": "capt_live_xxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

## Configuration

| Env var             | Required | Default                    | Description                              |
| ------------------- | -------- | -------------------------- | ---------------------------------------- |
| `CAPTAPI_API_KEY`   | yes      | —                          | Your `capt_live_...` / `capt_test_...` key. |
| `CAPTAPI_BASE_URL`  | no       | `https://api.captapi.com`  | Override the API base URL.               |

## Tools

Each endpoint is exposed as a tool named `<platform>_<action>`, e.g.
`youtube_transcript`, `tiktok_comments`, `instagram_channel_posts`,
`facebook_profile_posts`. Inputs:

- **Search** tools take `q` (query) and optional `limit`.
- **Channel** tools take a profile/channel `url`.
- **Comments / list** tools take a `url` and optional `limit`.
- **Transcript / summarize** tools take a `url` and optional `language`.
- **Details / download** tools take a `url`.

Cached results (24h) are free. Failed or empty results are never charged.

## License

MIT
