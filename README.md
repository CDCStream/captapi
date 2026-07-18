# Captapi

One REST API for structured public data across **27 platforms** and **174 endpoints** — transcripts, AI summaries, comments, profiles, search, commerce data, ad libraries, analytics helpers, and engagement metrics. Clean JSON, no OAuth, one Bearer key.

## Architecture

- **Backend**: FastAPI (Python 3.12) — Apify data collection + OpenAI summarization
- **Frontend**: Next.js 15 + Tailwind + shadcn/ui — landing, dashboard, billing
- **DB / Auth**: Supabase (Postgres + Auth + Storage)
- **Cache / Rate limit**: Upstash Redis
- **Data collection**: Apify Actors
- **AI**: OpenAI (gpt-4o-mini + Whisper)
- **Billing**: Paddle (Merchant of Record — subscriptions + top-up credits; Dodo Payments kept as a dormant fallback)

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Supabase project (free tier)
- Apify account + API token
- OpenAI API key
- Paddle account (sandbox mode)
- Upstash Redis (free tier)

### 1. Supabase Setup

```bash
# Install Supabase CLI
npm i -g supabase

# Login and link your project
supabase login
supabase link --project-ref YOUR_PROJECT_REF

# Push schema
supabase db push
```

### 2. Backend Setup

```bash
cd backend
cp .env.example .env
# Fill in env vars

# Install dependencies (using uv)
pip install uv
uv pip install -e .

# Run dev server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
cp .env.example .env.local
# Fill in env vars

npm install
npm run dev
```

Open http://localhost:3000.

## Project Structure

```
socialkit-clone/
├── backend/                FastAPI service
│   ├── app/
│   │   ├── main.py         App entry
│   │   ├── core/           Config, auth, credits, security
│   │   ├── routers/        Endpoint handlers per platform
│   │   ├── services/       Apify, OpenAI, Supabase, Cache, Paddle
│   │   ├── schemas/        Pydantic models
│   │   └── utils/          Helpers
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/               Next.js 15 app
│   ├── app/                App Router
│   ├── components/         UI components
│   └── lib/                Supabase + API client
└── supabase/
    └── migrations/         SQL schema
```

## API

All endpoints require `Authorization: Bearer capt_live_...` (or `x-api-key`).

Base URL: `https://api.captapi.com` (local: `http://localhost:8000`).

Requests fetch fresh data by default. Pass `cache=true` for a free 24h cache hit.

Full catalog (platforms, paths, credits, params): [frontend/lib/api-catalog.ts](frontend/lib/api-catalog.ts) and https://captapi.com/apis.

### Platforms (27)

YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, TikTok Shop, GitHub, Ad Library, Twitch, Spotify, SoundCloud, Linktree, Snapchat, Truth Social, Kick, Amazon Shop, Kwai, Komi, Pillar, Linkbio, Linkme.

### Example endpoints

- `GET /v1/youtube/transcript?url=...`
- `GET /v1/tiktok/video-details?url=...`
- `GET /v1/instagram/channel-details?url=...`
- `GET /v1/facebook/marketplace-search?q=...&location=...`

### Account

- `GET /v1/account/balance` — remaining credits
- `GET /v1/account/request-history` — recent requests
- `GET /v1/account/daily-usage` — day-by-day credit usage
- `GET /v1/account/most-used-routes` — ranked endpoint usage

## Pricing

Credit-based. Prices mirror the live pricing page (`frontend/components/marketing/pricing-plans.tsx`).

| Plan      | Credits              | Notes                          |
|-----------|----------------------|--------------------------------|
| Free      | 100 lifetime         | No card required               |
| Starter   | 2,000 / month        | Side projects                  |
| Pro       | 6,000 / month        | Growing products               |
| Business  | 20,000 / month       | Data pipelines                 |

One-time packs (never expire): Starter 2,000 · Growth 10,000 · Scale 50,000 credits.

## License

MIT
