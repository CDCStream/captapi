# Captapi

API-as-a-Service that extracts transcripts, AI summaries, comments, engagement metrics, and channel analytics from YouTube, TikTok, Instagram, and Facebook videos.

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

## API Endpoints

All endpoints require `Authorization: Bearer capt_live_...` header.

### YouTube
- `GET /v1/youtube/transcript?url=...`
- `GET /v1/youtube/summarize?url=...`
- `GET /v1/youtube/video-details?url=...`
- `GET /v1/youtube/comments?url=...&limit=...`
- `GET /v1/youtube/channel-details?url=...`
- `GET /v1/youtube/channel-videos?url=...&limit=...`
- `GET /v1/youtube/playlist-videos?url=...&limit=...`
- `GET /v1/youtube/search?q=...&limit=...`

### TikTok
- `GET /v1/tiktok/transcript|summarize|video-details|comments|channel-details`

### Instagram
- `GET /v1/instagram/transcript|summarize|details|comments|channel-details|channel-posts|channel-reels|reels-search`

### Facebook
- `GET /v1/facebook/transcript|summarize|details|comments|page-details`

### Video Files
- `POST /v1/video/transcript` — multipart upload, Whisper transcription
- `POST /v1/video/summarize` — transcription + AI summary

### Account
- `GET /v1/account/usage` — credit balance + recent requests
- `GET /v1/account/limits` — plan + remaining quota

## Pricing

| Plan      | Price/mo | Credits/mo | $/Credit |
|-----------|----------|-----------:|---------:|
| Free      | $0       | 100 lifetime | —      |
| Starter   | $9       | 1,500       | $0.006  |
| Pro       | $29      | 6,000       | $0.0048 |
| Business  | $99      | 25,000      | $0.0039 |
| Top-up    | $5       | 500         | $0.01   |

## License

MIT
