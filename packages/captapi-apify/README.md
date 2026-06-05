# Captapi - Apify Actor (BYO key)

A thin **Apify Actor** that calls the [Captapi](https://captapi.com) REST API
(it does not scrape) for social media data from YouTube, TikTok, Instagram &
Facebook. Users bring their own `capt_live_...` key; credits are billed to their
Captapi account.

The input form and the runtime endpoint table are generated from the shared
endpoint catalog, so the Actor always matches the API.

## Layout

| Path | Purpose |
| --- | --- |
| `.actor/actor.json` | Actor definition (name, version, Dockerfile, input, readme) |
| `.actor/input_schema.json` | **Generated** run form (apiKey + operation + params) |
| `.actor/Dockerfile` | `apify/actor-node:20` base image |
| `.actor/ACTOR.md` | Readme shown on the Apify Store |
| `src/main.js` | Reads input, calls the API, pushes one dataset item |
| `src/endpoints.json` | **Generated** operation -> path/params table |

## Regenerate

```bash
node generate.mjs
```

Requires Node >= 22.6 (reads `../captapi-n8n/src/catalog.ts` directly via
TypeScript type-stripping). The console output also lists the required params
per operation. Re-run after the catalog changes.

## Run locally

```bash
npm install
npm install -g apify-cli   # if you don't have it
apify run -i '{ "apiKey": "capt_live_...", "operation": "youtube_transcript", "url": "https://youtube.com/watch?v=dQw4w9WgXcQ" }'
```

## Publish (free Actor)

```bash
apify login
apify push
```

Then in the Apify Console open the Actor -> **Publication**, set it **public**
and keep the **pricing model = Free** (rental price 0), fill the Store listing,
and publish. Users run it with their own Captapi key, so there is no shared
secret and nothing to meter on your side.

Docs: <https://captapi.com/docs/integrations>
