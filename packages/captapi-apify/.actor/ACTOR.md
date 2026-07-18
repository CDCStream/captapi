# Captapi - Social Media Data (27 platforms, BYO key)

Bring your own **Captapi** API key and pull structured social media data -
transcripts, AI summaries, comments, video/profile stats, search results and
download URLs - from **YouTube, TikTok, Instagram, Facebook, X (Twitter),
Reddit, Threads, Bluesky, Pinterest, LinkedIn & Rumble**.

This Actor is a thin wrapper: it **calls the official Captapi REST API** and
returns the result. It does **not** scrape. Credits are billed to your own
Captapi account, pass cache=true for a free 24h cache hit (default is always fresh); and failed requests are never charged.

## Get a key

Create a free `capt_live_...` key at
<https://captapi.com/dashboard/api-keys> (100 free credits to start).

## Input

| Field | Required | Notes |
| --- | --- | --- |
| **Captapi API key** | yes | Your `capt_live_...` key (stored encrypted). |
| **Operation** | yes | Which endpoint to call (170 options, grouped by platform). |
| **URL** | most ops | Video / reel / post / channel / profile / playlist / music URL. |
| **Search query** | search ops | Keyword or hashtag (min 2 chars). |
| **Limit** | list ops | Max items to return (billed per result). |
| **Language** | transcripts | ISO code (e.g. `en`); defaults to auto-detect. |
| **Comment ID** | reply ops | Parent comment ID from the comments endpoint. |
| **Country** | trending feed | Two-letter ISO code (e.g. `US`). |
| **Topic** | popular hashtags | Topic/keyword for `tiktok_popular_hashtags`. |

Each operation only uses the fields it needs; the Actor validates required
fields and returns a clear message if one is missing.

## Output

One dataset item:

```json
{
  "operation": "youtube_transcript",
  "ok": true,
  "cached": false,
  "creditsUsed": 2,
  "data": { "...": "the same payload as the REST API" }
}
```

On error, `ok` is `false` with `status` and `error`, and the run fails with the
API's error message.

## Other ways to use Captapi

REST API, MCP server (`@captapi/mcp`), CLI (`@captapi/cli`), an n8n community
node (`n8n-nodes-captapi`), and a Make.com app. See
<https://captapi.com/docs/integrations>.
