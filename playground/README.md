# Captapi Playground

Standalone dev console to try Captapi endpoints and integration snippets,
time each call, and keep a local run history so you can compare results
**before vs after** a code change.

Lives outside the main app — it only talks to the API over HTTP.

## Run

```bash
cd playground
npm install
npm run dev
```

Open http://localhost:5273. The endpoint catalog is synced from
`packages/captapi-mcp/src/catalog.ts` via `predev`; refresh anytime with
`npm run sync-catalog`.

## Setup

In the top bar set:

- **API key** — a `capt_live_…` / `capt_test_…` key (browser localStorage only)
- **Target** — Prod (`api.captapi.com`) or Local (`localhost:8000` via Vite proxy)
- **$/credit** and **markup×** — optional cost display for local estimates

## Tabs

- **Endpoints** — pick platform + endpoint, fill parameters, Run
- **Integrations** — copy-paste snippets for cURL, CLI, SDK, MCP, and the
  Captapi Apify Store client (BYO key → Captapi REST)

## History

Persisted in localStorage. Filter, annotate, compare two runs, or export JSON.
