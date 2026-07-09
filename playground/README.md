# Captapi Playground

Standalone dev console to try every Captapi endpoint and integration snippet,
time each call, estimate cost ($), and keep a local run history so you can
compare results **before vs after** a code change.

Lives outside the main app — it only talks to the API over HTTP, so running it
never affects the frontend or backend.

## Run

```bash
cd playground
npm install
npm run dev
```

Open http://localhost:5273. The endpoint catalog is copied from
`packages/captapi-mcp/src/catalog.ts` automatically (via `predev`); refresh it
manually any time with `npm run sync-catalog`.

## Setup

In the top bar set:

- **API key** — a `capt_live_…` / `capt_test_…` key (stored only in your
  browser's localStorage).
- **Target** — `Prod (api.captapi.com)` or `Local (localhost:8000)`. Local goes
  through the Vite proxy (`/local-api`) so there's no CORS setup; just have the
  backend running on port 8000.
- **$/credit** and **markup×** — the cost model. Customer price =
  `credits × $/credit × markup`; our estimated cost = `credits × $/credit` for
  Apify-backed calls and ~$0 for native (self-scraped) ones.

## Tabs

- **Endpoints** — pick platform + endpoint, fill parameters, Run. Shows HTTP
  status, latency (ms), returned item count, customer price and our estimated
  cost, plus the full response JSON. Every run is saved to history.
- **Integrations** — the same endpoint + params rendered as copy-paste snippets
  for each connector: cURL, CLI (`@captapi/cli`), SDK (`@captapi/sdk`), MCP tool
  call, and Apify actor input.

## History (right panel)

- Persisted in localStorage (survives reloads).
- Filter by tool/platform, add a note per run, view the stored JSON.
- Tick **two** runs to compare latency and our-cost delta (e.g. the same
  endpoint before and after switching it to native scraping).
- **Export** dumps the whole history to a JSON file.

## Notes on estimates

- The **native vs Apify** badge and "our cost" are heuristics from
  `src/lib/native.ts` (kept in sync with the backend migration state). The
  authoritative source/cost is the `requests.source` column + `response_samples`
  table on the backend. Update `native.ts` as more endpoints migrate.
- Credit estimates use the catalog's per-endpoint credits; list endpoints are
  scaled by returned item count (approximate).
