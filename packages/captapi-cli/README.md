# @captapi/cli

Official command-line interface for [Captapi](https://captapi.com) — pull
structured social-media data from 29 platforms (YouTube, TikTok, Instagram,
Facebook, X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, Truth
Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop) from your terminal, check your credit balance, and
wire Captapi into AI agents.

```bash
npm install -g @captapi/cli
# or run without installing:
npx @captapi/cli list
```

## Quick start

```bash
captapi login                 # paste your capt_live_… key (saved to ~/.captapi/config.json)
captapi balance               # credits + recent requests
captapi list                  # every endpoint (180 commands)
captapi youtube-transcript --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

Get an API key at https://captapi.com/dashboard/api-keys.

## Authentication

The CLI is API-key based. Authenticate either way:

- `captapi login` — verifies and saves your key to `~/.captapi/config.json` (mode `600`).
- `CAPTAPI_API_KEY` environment variable — always wins over the saved key, ideal for CI.

Override the API host with `CAPTAPI_BASE_URL` (default `https://api.captapi.com`).

## Commands

| Command | Description |
| --- | --- |
| `captapi login [--key <key>]` | Verify and save an API key |
| `captapi logout` | Remove the saved key |
| `captapi whoami` | Show the active (masked) key and base URL |
| `captapi balance [--json]` | Credit balance + recent requests |
| `captapi list [platform] [--json]` | List endpoints, optionally by platform |
| `captapi agent add <claude\|cursor>` | Add the Captapi MCP server to an agent |
| `captapi <endpoint> [flags]` | Call any of the 180 data endpoints |

### Calling endpoints

Every Captapi endpoint is its own command. Parameters become flags; required
parameters are enforced. Output is JSON on stdout, so it pipes cleanly:

```bash
captapi tiktok-channel-details --url "https://tiktok.com/@username"
captapi youtube-comments --url "https://youtube.com/watch?v=ID" --limit 50
captapi instagram-channel-posts --url "https://instagram.com/nasa/" --limit 12 | jq '.data[0]'
```

Run `captapi <command> --help` to see a command's exact parameters, path, and
credit cost. Cached results are free; failed requests are never charged.

### Wiring AI agents

`agent add` writes the Captapi MCP server into Claude Desktop or Cursor config,
embedding your saved key:

```bash
captapi agent add cursor          # writes ~/.cursor/mcp.json
captapi agent add claude          # writes the Claude Desktop config for your OS
captapi agent add cursor --print  # print the snippet instead of writing
```

Restart the agent afterwards to load the [`@captapi/mcp`](https://www.npmjs.com/package/@captapi/mcp)
server (180 tools).

## License

MIT
