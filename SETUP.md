# Captapi — Setup Guide

This guide walks you through getting a working dev environment in ~30 minutes.

## 1. Create accounts

You will need accounts on:

1. **Supabase** — https://supabase.com (free tier)
2. **Apify** — https://apify.com (pay-as-you-go, ~$5 to start)
3. **OpenAI** — https://platform.openai.com (pay-as-you-go)
4. **Stripe** — https://stripe.com (test mode is free)
5. **Upstash Redis** — https://upstash.com (free tier) — optional, can run local Redis instead
6. **Vercel** (frontend hosting) and **Railway** or **Fly.io** (backend hosting) — for production

## 2. Provision Supabase

```bash
npm i -g supabase
supabase login
supabase init
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

Then in the Supabase dashboard:
- Authentication → Providers → enable Email (with confirmation).
- Authentication → URL Configuration → add `http://localhost:3000` and your prod URL to redirect URLs.

## 3. Configure Apify

In the Apify console, copy your token from Settings → Integrations.

Search for and "Try" each actor you intend to use so they are linked to your account.
Default actor IDs are in `backend/.env.example` — override them if you fork or pin a different version.

For each actor, run it once manually with a sample input so Apify caches its compute units.

## 4. Configure Stripe

In Stripe Test mode:

1. Create 3 Products: **Starter**, **Pro**, **Business** — each with a recurring monthly Price.
2. Create 1 Product: **Top-up 500 credits** — with a one-time Price.
3. Note the price IDs (`price_...`) and put them in `backend/.env` AND `frontend/.env.local`:
   ```env
   STRIPE_PRICE_STARTER=price_...
   STRIPE_PRICE_PRO=price_...
   STRIPE_PRICE_BUSINESS=price_...
   STRIPE_PRICE_TOPUP_500=price_...

   NEXT_PUBLIC_STRIPE_PRICE_STARTER=price_...
   NEXT_PUBLIC_STRIPE_PRICE_PRO=price_...
   NEXT_PUBLIC_STRIPE_PRICE_BUSINESS=price_...
   NEXT_PUBLIC_STRIPE_PRICE_TOPUP_500=price_...
   ```
4. Create a webhook endpoint pointing to `https://your-api.com/v1/billing/webhook`.
   - Subscribed events: `checkout.session.completed`, `customer.subscription.created`,
     `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`.
   - Copy the signing secret → `STRIPE_WEBHOOK_SECRET`.

For local development use the Stripe CLI:
```bash
stripe listen --forward-to localhost:8000/v1/billing/webhook
```

## 5. Run locally

### Option A — Docker Compose

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# fill in keys
docker compose up
```

### Option B — manual

Backend:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate # macOS/Linux
pip install uv
uv pip install -e .
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## 6. Smoke test

1. Sign up at http://localhost:3000/signup
2. Confirm email (Supabase will send a magic link)
3. Go to **Dashboard → API Keys**, create a key, copy it
4. Go to **Playground**, paste the key, try a YouTube URL
5. You should see a response and the request appear in **Usage**

## 7. Deploy

### Frontend (Vercel)
- Connect repo, set root directory to `frontend/`
- Add all `NEXT_PUBLIC_*` env vars
- Deploy

### Backend (Railway / Fly.io)
- Railway: connect repo, set root to `backend/`, add env vars, Railway builds the Dockerfile
- Fly.io: `fly launch` inside `backend/`, set secrets with `fly secrets set`

### Database
- Already provisioned on Supabase. No further action.

### Stripe webhook
- After deploying backend, update the webhook URL in the Stripe Dashboard from
  `localhost` to your live API URL.

## 8. Monitoring & ops

- Add `SENTRY_DSN` to backend env — errors will start flowing.
- Set up an uptime monitor (UptimeRobot, BetterStack) pointing to `/healthz`.
- Daily, run `select public.cleanup_expired_cache();` via Supabase pg_cron
  (see `supabase/migrations/0002_cache_cleanup_cron.sql`).

## 9. Launch checklist

- [ ] Production Stripe keys swapped in
- [ ] Webhook endpoint verified in Stripe
- [ ] Custom domain + SSL on Vercel
- [ ] Custom subdomain (api.yourdomain.com) for backend
- [ ] CORS origins in `APP_CORS_ORIGINS` includes production frontend domain
- [ ] Sentry / log drain configured
- [ ] Rate limits validated (try to hit `RATE_LIMIT_PER_MINUTE` and confirm 429)
- [ ] At least 1 free tool landing page indexed by Google
- [ ] Product Hunt + Hacker News launch posts prepared
- [ ] Zapier integration submitted (Phase 6)
