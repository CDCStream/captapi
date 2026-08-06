# Captapi

[![MCP Queen operational grade](https://mcpqueen.com/badge/io.github.CDCStream/captapi.svg)](https://mcpqueen.com/s/io.github.CDCStream/captapi)

One REST API for structured public data across **32 platforms** and **177 endpoints** — transcripts, AI summaries, comments, profiles, search, commerce data, ad libraries, analytics helpers, and engagement metrics. Clean JSON, no OAuth, one Bearer key.

**Product:** [captapi.com](https://captapi.com) · **API docs:** [captapi.com/docs](https://captapi.com/docs) · **Catalog:** [captapi.com/apis](https://captapi.com/apis)

## What you get

- Stable REST responses (`success`, `data`, billing meta) with consistent camelCase JSON
- One Bearer key for YouTube, TikTok, Instagram, Facebook, X, Reddit, and 20+ more sources
- MCP server, CLI, n8n, Make, and an optional Apify Store client (BYO Captapi key — calls this API; it does not scrape)
- Credit-based pricing with a free tier — see [Pricing](https://captapi.com/pricing)

## Repository layout

```
.
├── backend/       FastAPI API service
├── frontend/      Next.js marketing site + dashboard
├── packages/      MCP, CLI, n8n, Make, SDKs, Apify Store client
├── supabase/      Database migrations
└── playground/    Local API console for development
```

## API (hosted)

Base URL: `https://api.captapi.com`

```bash
curl -H "Authorization: Bearer capt_live_..." \
  "https://api.captapi.com/v1/tiktok/video-details?url=https://www.tiktok.com/@x/video/123"
```

Requests fetch fresh data by default. Pass `cache=true` for a free 24h cache hit.

Full endpoint catalog: [`frontend/lib/api-catalog.ts`](frontend/lib/api-catalog.ts) or https://captapi.com/apis.

### Example endpoints

- `GET /v1/youtube/transcript?url=...`
- `GET /v1/tiktok/video-details?url=...`
- `GET /v1/instagram/channel-details?url=...`
- `GET /v1/facebook/marketplace-search?q=...&location=...`

### Account

- `GET /v1/account/balance`
- `GET /v1/account/request-history`
- `GET /v1/account/daily-usage`
- `GET /v1/account/most-used-routes`

## Local development

### Prerequisites

- Python 3.12+
- Node.js 20+
- Supabase project
- OpenAI API key (summaries / Whisper fallbacks)
- Paddle sandbox (billing)
- Upstash Redis (cache / rate limits)
- Provider credentials as required by your deployment (see `backend/.env.example`)

### Backend

```bash
cd backend
cp .env.example .env   # fill in secrets — never commit .env
pip install uv
uv pip install -e .
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000.

### Database

```bash
npm i -g supabase
supabase login
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

## Pricing (summary)

| Plan     | Credits       |
|----------|---------------|
| Free     | 100 lifetime  |
| Starter  | 2,000 / month |
| Pro      | 6,000 / month |
| Business | 20,000 / month|

Details: https://captapi.com/pricing

## License

MIT
