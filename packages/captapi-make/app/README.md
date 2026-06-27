# Captapi for Make.com

Structured social media data from 11 platforms — YouTube, TikTok, Instagram,
Facebook, X (Twitter), Reddit, Threads, Bluesky, Pinterest, LinkedIn & Rumble —
transcripts, AI summaries, comments, stats, search and downloads.

- **85 action modules**, one per Captapi endpoint.
- **One connection**: paste your Captapi API key (Bearer auth).
- Every module returns the API `data` payload directly.

## Connection

Create a **Captapi API Key** connection and paste the key from
https://captapi.com/dashboard. The key is validated against
`GET /v1/account/limits`.

## Modules

Modules are grouped by platform (YouTube, TikTok, Instagram, Facebook, X/Twitter,
Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble). Pick the operation you
need, fill in the URL (or search query) and an optional limit, and the module
returns the structured result.

Docs: https://captapi.com/docs
