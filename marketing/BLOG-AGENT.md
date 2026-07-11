# Captapi SEO blog agent

The agent turns an Ahrefs keyword export into scheduled, SERP-aware articles:

1. Ahrefs CSV supplies the candidate keywords and initial metrics.
2. DataForSEO refreshes US search volume and keyword difficulty.
3. Serper supplies current Google results, snippets, People Also Ask, and
   related searches.
4. The configured LLM writes a 1,200-1,800 word developer-focused HTML post.
5. The article LLM marks two [[IMAGE: ...]] spots; the agent renders them with
   OpenAI images (gpt-image-1, dall-e-3 fallback), uploads them to Supabase
   Storage via /api/blog/upload-image, and embeds them as <figure> blocks.
   One extra [[PHOTO: ...]] spot is filled with a commercially usable
   CC-licensed photo from Openverse, re-hosted on Supabase and credited with
   a "Source: title by creator (license)" figcaption linking to the origin.
6. Automated checks reject short articles, missing headings, bad metadata,
   and missing internal links.
7. `/api/blog/save` upserts the post into Supabase `blog_posts`.
8. The agent generates an Outrank-style sketch cover (white paper, black serif
   headline, blue ink doodles) with `gpt-image-1` at high quality and uploads it
   to Supabase Storage. If generation fails it falls back to the branded card at
   `/api/blog/cover/[slug]`.

## Import an Ahrefs export

Export CSV from Ahrefs Keywords Explorer. Common column names such as
`Keyword`, `Volume`, `Keyword Difficulty`, `KD`, `Intent`, and
`Traffic Potential` are recognized.

```powershell
python scripts/blog_pipeline.py --import-ahrefs "C:\path\keywords.csv"
```

The import merges into `marketing/keyword-bank.csv`; it never removes the
existing manually curated keywords.

## Run locally

Required environment variables:

```text
OPENAI_API_KEY=
SERPER_API_KEY=
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=
BLOG_ADMIN_SECRET=
```

Generate a local preview without writing to Supabase:

```powershell
python scripts/blog_pipeline.py --count 1 --enrich --dry-run
```

Save one reviewed-quality draft:

```powershell
python scripts/blog_pipeline.py --count 1 --enrich --status draft
```

Automatic publishing is supported, but enable it only after reviewing several
drafts:

```powershell
python scripts/blog_pipeline.py --count 1 --enrich --status published
```

Local previews are written to `marketing/blog-drafts/`.

## Schedule

`.github/workflows/seo-blog-agent.yml` runs Monday, Tuesday, Thursday, and
Saturday at 06:15 UTC. It skips slugs already present in `blog_posts`, so a
fresh GitHub runner does not recreate the same draft.

Add these repository secrets:

- `OPENAI_API_KEY`
- `SERPER_API_KEY`
- `DATAFORSEO_LOGIN`
- `DATAFORSEO_PASSWORD`
- `BLOG_ADMIN_SECRET`

Optional repository variables:

- `BLOG_MODEL` (default `gpt-4o-mini`)
- `BLOG_IMAGE_MODEL` (default `gpt-image-1`)
- `BLOG_STATUS` (`draft` while validating quality; later `published`)

Use **Actions → SEO blog agent → Run workflow** for a manual test.

## Quality and cost controls

- One Serper query and one DataForSEO keyword-overview request per article.
- DataForSEO errors do not block an article; Ahrefs metrics remain the fallback.
- Serper is preferred for live research; DuckDuckGo is the no-key fallback.
- Existing posts are read through the authenticated blog admin endpoint.
- The AI cover costs roughly $0.25 per post at high quality (gpt-image-1); the
  branded card fallback is free.
- Inline illustrations cost roughly $0.08-0.15 per article; if image generation
  fails the article still publishes without them.
- Publishing triggers the existing IndexNow integration.
