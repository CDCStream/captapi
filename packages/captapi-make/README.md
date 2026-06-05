# Captapi - Make.com custom app

A [Make.com](https://www.make.com) (Integromat) custom app that exposes every
Captapi endpoint as a module. Structured social media data from **YouTube,
TikTok, Instagram & Facebook** - transcripts, AI summaries, comments, stats,
search and downloads - with one API-key connection.

The app definition lives in [`app/`](./app) as a Make **local app** and is
generated from the shared endpoint catalog, so it always matches the API.

## What's in `app/`

| Path | Purpose |
| --- | --- |
| `makecomapp.json` | App manifest (connection + 62 modules, grouped by platform) |
| `general/base.iml.json` | Base URL + `Authorization: Bearer {{connection.apiKey}}` + error handling |
| `connections/captapi/` | API-key connection: params + verification request (`GET /v1/account/limits`) |
| `modules/<name>/` | One **action** module per endpoint (`communication` + `mappable-params`) |
| `modules/groups.json` | Picker grouping by YouTube / TikTok / Instagram / Facebook |

Every module returns the API `data` payload directly (`{{body.data}}`). List
endpoints return their array inside that payload.

## Regenerate

```bash
node generate.mjs
```

Requires Node >= 22.6 (reads `../captapi-n8n/src/catalog.ts` directly via
TypeScript type-stripping). Re-run after the catalog changes.

## Deploy to Make

You need a Make account and a **Make API key** with Custom-Apps scopes
(Profile -> API -> Add token). Then:

1. Install the **Make Apps Editor** extension (`Integromat.apps-sdk`) in VS Code.
2. Add your API key to the extension when prompted.
3. Open the `app/` folder, right-click `makecomapp.json` ->
   **Deploy to Make**. Pick your zone (e.g. `https://eu2.make.com/api`); the
   extension creates the remote app and writes the origin back into
   `makecomapp.json`.
4. Open the app in your Make dashboard, create a **Captapi API Key** connection
   with a key from <https://captapi.com/dashboard>, and test any module in a
   scenario.

To publish the app publicly, submit it for review from the Make dashboard
(**App -> Settings -> Publish**).

> The Make API key is stored locally under `.secrets/` (git-ignored). Never
> commit it.

Docs: <https://captapi.com/docs>
