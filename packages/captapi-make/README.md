# Captapi - Make.com custom app

A [Make.com](https://www.make.com) (Integromat) custom app that exposes every
Captapi endpoint as a module. Structured social media data from **27 platforms**
(YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest,
LinkedIn, Rumble, Truth Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop) - transcripts, AI summaries,
comments, stats, search, commerce data and downloads - with one API-key connection.

The app definition lives in [`app/`](./app) as a Make **local app** and is
generated from the shared endpoint catalog, so it always matches the API.

## What's in `app/`

| Path | Purpose |
| --- | --- |
| `makecomapp.json` | App manifest (connection + 85 modules, grouped by platform) |
| `general/base.iml.json` | Base URL + `Authorization: Bearer {{connection.apiKey}}` + error handling |
| `connections/captapi/` | API-key connection: params + verification request (`GET /v1/account/limits`) |
| `modules/<name>/` | One **action** module per endpoint (`communication` + `mappable-params`) |
| `modules/groups.json` | Picker grouping by platform (11 groups) |

Every module returns the API `data` payload directly (`{{body.data}}`). List
endpoints return their array inside that payload.

## Regenerate

```bash
node generate.mjs
```

Requires Node >= 22.6 (reads `../captapi-n8n/src/catalog.ts` directly via
TypeScript type-stripping). Re-run after the catalog changes.

## Deploy to Make

You need a Make account and a **Make API token** with `custom-apps` (sdk-apps)
read/write scopes (Profile -> API/MCP Access -> Add token). Then:

```bash
python packages/captapi-make/deploy.py <make-token> [zone]   # zone default: eu1
```

The script is idempotent: it reuses the existing app/connection/modules and
re-uploads the base, readme, connection sections, every module's
communication + mappable parameters, and the platform groups.

> First deployed 2026-07-11 as `captapi-qspcy5` (eu1, 170 modules).

Alternatively, the `app/` folder is a Make **local app**: install the
**Make Apps Editor** VS Code extension, add the token, right-click
`makecomapp.json` -> Deploy to Make.

After deploying, open the app in your Make dashboard, create a **Captapi API
Key** connection with a key from <https://captapi.com/dashboard>, and test any
module in a scenario.

To publish the app publicly, submit it for review from the Make dashboard
(**App -> Settings -> Publish**).

> The Make API key is stored locally under `.secrets/` (git-ignored). Never
> commit it.

Docs: <https://captapi.com/docs>
