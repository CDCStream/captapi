# Captapi for Zapier

Zapier integration for the [Captapi](https://captapi.com) social media data API.
Built with the Zapier Platform CLI (`zapier-platform-core` 19).

## What's inside

- **28 featured actions** covering the most-used endpoints (YouTube / TikTok /
  Instagram transcripts, summaries, details, comments, profiles, search;
  Facebook, Twitter/X, Reddit, LinkedIn, Threads; account balance).
- **1 "Custom API Request" action** that exposes all 170 endpoints via a
  dropdown — picking an endpoint dynamically shows its exact input fields.
- **API key auth** (Bearer), validated against `GET /v1/account/limits`.
- Friendly error mapping: 401/403 → reconnect prompt, 402 → "top up credits".

## Layout

| File | Purpose |
| --- | --- |
| `index.js` | App definition (auth, middleware, creates) |
| `authentication.js` | Custom API-key auth + connection test |
| `creates.js` | Featured actions + Custom API Request, all driven by `catalog.json` |
| `catalog.json` | Generated endpoint catalog (do not edit by hand) |
| `generate.mjs` | Regenerates `catalog.json` from `../captapi-n8n/src/catalog.ts` |
| `smoke.test.mjs` | Offline smoke test (`node smoke.test.mjs`) |

## Updating after catalog changes

```bash
npm run generate     # rebuild catalog.json from the shared catalog
node smoke.test.mjs  # sanity check
npx zapier-platform push
```

## First-time deploy

```bash
npm install
npx zapier-platform login       # opens browser, stores credentials in ~/.zapierrc
npx zapier-platform register "Captapi"
npx zapier-platform push
```

After pushing, the app is **private**: test it in the Zap editor, invite users
with `npx zapier-platform users:add email@example.com 1.0.0`, and when ready
submit for public listing from https://developer.zapier.com (Publishing →
submit for review).
