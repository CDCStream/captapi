-- Changelog: public release notes shown at /changelog.
-- Entries are grouped by day on the page; categories drive the badge color.

create table if not exists public.changelog_entries (
  id uuid primary key default gen_random_uuid(),
  published_at date not null,
  category text not null default 'improvement'
    check (category in ('feature', 'improvement', 'fix', 'integration', 'platform')),
  title text not null,
  description text not null default '',
  items jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_changelog_published
  on public.changelog_entries (published_at desc);

alter table public.changelog_entries enable row level security;

-- Public read: the page is public, and anon access keeps options open.
create policy "changelog_public_read" on public.changelog_entries
  for select using (true);

-- ---------------------------------------------------------------------------
-- Seed: the story so far.
-- ---------------------------------------------------------------------------

insert into public.changelog_entries (published_at, category, title, description, items) values

('2026-07-04', 'feature', 'Integrations hub at /integrations',
 'A dedicated page listing every official integration with setup guides, plus a hover dropdown in the navbar.',
 '["MCP Server (hosted + local), TypeScript & Python SDKs, CLI, n8n, Make.com, Apify Actor, and the REST API in one place", "Each card links to its setup guide and npm/PyPI package", "Machine-readable manifests highlighted for AI agents (/mcp.json, /llms.txt, OpenAPI 3)"]'),

('2026-07-04', 'feature', 'Monitors + HMAC-signed webhooks',
 'Point a monitor at any list-returning endpoint and get only new items POSTed to your webhook — no polling loops on your side.',
 '["POST /v1/monitors: watch subreddit posts, channel videos, ad-library searches and more on your schedule (15 min to 24 h)", "Deliveries are HMAC-SHA256 signed (X-Captapi-Signature over timestamp.body) so you can verify authenticity", "POST /v1/monitors/{id}/test sends a signed test delivery", "Runs bill credits exactly like direct API calls; cached results stay free"]'),

('2026-07-04', 'feature', 'Automatic metric history (GET /v1/history)',
 'Follower, view, and like counts now accumulate into a time series automatically whenever tracked profile or post endpoints are fetched fresh.',
 '["Chart growth without building your own snapshot pipeline", "Covers profile and details endpoints across YouTube, TikTok, Instagram, X, Reddit, Bluesky, Twitch and more", "Query by endpoint + URL with a configurable window (up to 365 days)"]'),

('2026-07-04', 'feature', 'Batch endpoint (POST /v1/batch)',
 'Run up to 20 endpoint calls concurrently in a single HTTP request.',
 '["Per-item status and per-item billing — one failed item never fails the batch", "Cached items are free, exactly like single calls", "Ideal for enriching lists of profiles or videos in one round-trip"]'),

('2026-07-04', 'feature', 'Public status page',
 'Live API health at /status, computed from real production traffic — not a manually flipped switch.',
 '["GET /v1/status (no auth) returns overall and per-platform success rates and response times over the last 24 h", "Human view at captapi.com/status refreshes every 2 minutes"]'),

('2026-07-04', 'feature', 'Official TypeScript & Python SDKs',
 'Typed clients generated from the same catalog that powers the API, MCP server, and CLI.',
 '["npm install @captapi/sdk — zero dependencies, works on Node 18+, Deno, Bun, and edge runtimes", "pip install captapi — sync (Captapi) and async (AsyncCaptapi) clients on httpx", "A typed, namespaced method for every endpoint; errors always throw with status + code", "x-api-key header now accepted as an alias for Authorization: Bearer"]'),

('2026-07-04', 'integration', 'MCP catalog synced to all 179 tools',
 'The hosted MCP server and every published package now expose the full endpoint catalog.',
 '["@captapi/mcp 0.4.0, @captapi/cli 0.3.0, n8n-nodes-captapi 0.3.0, Apify Actor 0.3 published", "OpenAPI 3 spec linked from llms.txt manifests for AI agent discovery"]'),

('2026-07-04', 'improvement', 'Richer response data across 11 platforms',
 'Closed field gaps against competitors with dedicated upstream sources.',
 '["Reddit: comment upvotes + threading (residential routing, optional OAuth app support)", "Twitch: clip/profile metadata and streamer schedules via a dedicated actor", "TikTok Shop: product reviews via a dedicated actor", "Also enriched: link-in-bio socials/email, Rumble embeds/streams/comments, Pinterest pin details, SoundCloud artist fields, Bluesky embeds, Truth Social website, GitHub repo/license/topics, X profile counts"]'),

('2026-07-03', 'improvement', 'Real response examples for all 179 endpoints',
 'Every endpoint page now shows a real captured response, refreshed in batches across the whole catalog.',
 '["Batches covered Twitter/LinkedIn/Reddit, TikTok Shop/Threads/Snapchat/ad libraries, GitHub/Facebook Marketplace/Events/Pinterest/Spotify, and Rumble/Twitch/Bluesky/SoundCloud/Kwai", "Dozens of mapper fixes along the way: timestamped transcript segments, YouTube comment author metadata, duration parsing, Instagram actor replacement and more"]'),

('2026-07-03', 'feature', 'Platform landing pages + APIs dropdown',
 'Every platform got a dedicated landing page with endpoint lists, FAQ, and structured data; the navbar now opens the full API catalog.',
 '[]'),

('2026-06-28', 'platform', '180 endpoints across 29 platforms',
 'Major catalog expansion with reliability fixes across the board.',
 '["New platforms and endpoints across the catalog, audited live end-to-end", "Endpoint reliability, agent URL validation, and integration discovery improvements", "Comprehensive live audit reports added to the repo"]'),

('2026-05-31', 'platform', 'EnsembleData & Scrape Creators parity push',
 'Expanded TikTok, Instagram, YouTube, and Facebook coverage to close competitor gaps.',
 '["19 new endpoints: TikTok hashtag/top/user search, song details, trending; IG hashtag/profile search, story highlights, embed; YT comment replies, channel playlists, community posts; FB profile posts/reels, group posts, comment replies", "Per-result pricing normalized to guarantee margins; dashboard analytics tab with daily usage charts"]'),

('2026-05-29', 'feature', 'Captapi launch',
 'One API for structured public social-media data: transcripts, AI summaries, comments, profiles, search, and downloads.',
 '["REST API with Bearer auth, credit-based billing, and cached-result discounts", "Dashboard with API keys, playground, usage analytics, and billing", "SEO/AEO foundation: llms.txt, structured data, programmatic docs"]');
