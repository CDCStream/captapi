# @captapi/mcp

Official **Captapi** MCP server. Give Claude, Cursor, VS Code, and any
MCP-compatible AI agent direct access to **180 social, web, and account endpoints**
across 29 platforms (YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads,
Bluesky, Pinterest, LinkedIn, Rumble, Truth Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop) —
transcripts, summaries, comments, channel stats, search, bulk lists, and downloads.

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
`facebook_profile_posts`. Every tool declares its exact inputs (and the precise
URL type expected — video, profile, playlist, sound, group, …):

- **Most tools** take a `url`. The description tells you which URL type.
- **Search** tools take `q`; list/comments tools also accept an optional `limit`.
- **Comment-replies** tools (`*_comment_replies`) additionally require `comment_id`.
- `tiktok_trending_feed` takes `country` (ISO-2, default `US`);
  `tiktok_popular_hashtags` takes `query` (default `trending`).
- **Transcript / summarize** tools accept an optional `language`.

Cached results (24h) are free. Failed or empty results are never charged.

## License

MIT
