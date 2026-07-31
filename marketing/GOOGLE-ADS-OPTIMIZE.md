# Google Ads optimize - Captapi (~1150 TL/day)

Checklist + RSA copy for redistributing demand beyond Instagram/TikTok.

Assets:

- `ads-keyword-plan.csv` - research plan (action=add|pause|skip)
- `google-ads-editor-import.csv` - phrase+exact keywords + final URLs
- Script: `python scripts/ads_keyword_research.py` (needs DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD)

---

## 0) Signup conversion (code shipped - finish in Ads UI)

Code fires signup conversion when:

- Password signup succeeds (`/signup`)
- New OAuth / email-confirm users land on dashboard with `?ads_signup=1`

You:

1. Google Ads -> Goals -> Conversions -> New conversion -> Website -> category Sign-up.
2. Copy the conversion **label** (the part after `AW-XXXXXXX/`).
3. Set on Vercel / production:

```
NEXT_PUBLIC_GOOGLE_ADS_SIGNUP_LABEL=xxxxxxxxxxxxxxxx
```

(`NEXT_PUBLIC_GOOGLE_ADS_ID` must already be set.)

4. Redeploy frontend.
5. Campaign settings -> conversion goals -> include Signup (primary for Free Tools / Core / Expansion). Keep Subscribe/Purchase for billing.

Until the label is set, Ads will still show 0 signup conversions.

---

## 1) Pause now (UI - do today)

| Item | Action |
|---|---|
| Campaign Search - Transcript API (YouTube transcript KW) | Pause entire campaign |
| Ad group Kral API under Social Media Data API | Pause |
| Any keyword containing youtube transcript / caption / subtitle | Remove or pause |
| Free Tools broad matches that pull YouTube | Negatives: youtube, yt, subtitle |

---

## 2) Target daily budgets (~1150 TL)

| Campaign | Daily budget | Notes |
|---|---|---|
| Search - Free Tools | 200 TL | TikTok + Instagram transcript tools only |
| Search - Core Platforms | 500 TL | IG, TikTok, LinkedIn, Reddit, X/Twitter, Facebook |
| Search - Expansion Platforms | 250 TL | Threads, Pinterest, Twitch, Snapchat, Ad Library, GitHub, YouTube non-transcript |
| Search - Brand + Competitor | 100 TL | Brand exact + competitor phrases |
| Search - Transcript API | 0 | Paused |
| Buffer | 50-100 TL | Optional |

Rename/migrate existing Search - Social Media Data API into Core + Expansion (or create new and pause old after import).

---

## 3) Import keywords

Re-run research with live volumes:

```powershell
$env:DATAFORSEO_LOGIN="your_login"
$env:DATAFORSEO_PASSWORD="your_password"
python scripts/ads_keyword_research.py
```

Then import `google-ads-editor-import.csv` (phrase + exact only). Landings are `https://captapi.com/apis/...` or `/tools/...`.

### Shared negative keywords (campaign level)

```
job
jobs
salary
course
courses
tutorial
how to become
internship
hiring
download apk
crack
free download
whatsapp
```

Free Tools extras:

```
youtube
yt
caption generator
subtitle download
```

---

## 4) RSA copy - Core Platforms

One RSA per ad group. Final URL = platform landing from the CSV.

### Instagram API

Headlines:

1. Instagram Scraper API
2. Instagram Data API - Clean JSON
3. Instagram Profile and Reels API
4. No OAuth Required
5. 100 Free Credits on Signup
6. Captapi Instagram API
7. Comments, Profiles, Reels
8. Built for Developers
9. One Key - 25+ Platforms
10. Start in 60 Seconds
11. Instagram API Without Login
12. Production-Ready Instagram Data
13. Skip Scrapers - Use Captapi
14. Flat Credit Pricing
15. Try the Playground Free

Descriptions:

1. Pull Instagram profiles, reels, and comments as clean JSON. No OAuth maze - 100 free credits to start.
2. Captapi: one REST API for Instagram and 25+ platforms. Cache-friendly, docs and playground included.

### TikTok API

Headlines:

1. TikTok Scraper API
2. TikTok Data API - Clean JSON
3. TikTok Profile and Video API
4. TikTok Comments API
5. No Scrapers to Babysit
6. 100 Free Credits on Signup
7. Captapi TikTok API
8. One Key - 25+ Platforms
9. Start in 60 Seconds
10. Production-Ready TikTok Data
11. Built for Developers
12. Try Playground Free
13. Flat Credit Pricing
14. Transcripts + Profiles + Stats
15. Skip Proxy Hell

Descriptions:

1. TikTok profiles, videos, comments, and more as structured JSON. 100 free credits - no card required.
2. Captapi replaces brittle TikTok scrapers with one REST key, docs, and a live playground.

### LinkedIn API

Headlines:

1. LinkedIn Scraper API
2. LinkedIn Profile API
3. LinkedIn Data API
4. Clean JSON - No Headaches
5. 100 Free Credits on Signup
6. Captapi LinkedIn API
7. Built for Developers
8. One Key - 25+ Platforms
9. Analytics-Ready LinkedIn Data
10. Start Free Today
11. Skip Official API Limits
12. Production LinkedIn Endpoints
13. Try Captapi Playground
14. Flat Credit Pricing
15. REST API for LinkedIn Data

Descriptions:

1. Get LinkedIn profile and post data as clean JSON via Captapi. 100 free credits to test.
2. Developer-friendly LinkedIn data API - same key works across 25+ social platforms.

### Reddit API

Headlines:

1. Reddit Scraper API
2. Reddit API Alternative
3. Reddit Data API - JSON
4. Subreddit and Comments API
5. 100 Free Credits on Signup
6. Captapi Reddit API
7. Bypass Reddit API Pricing Pain
8. One Key - 25+ Platforms
9. Built for Developers
10. Clean Structured Reddit Data
11. Start in 60 Seconds
12. Try Playground Free
13. Flat Credit Pricing
14. Posts, Comments, Search
15. Production-Ready Reddit API

Descriptions:

1. Fetch subreddit posts, comments, and search results as JSON. 100 free credits - no card.
2. Captapi is a Reddit data API for builders tired of official API pricing changes.

### Twitter / X API

Headlines:

1. Twitter Scraper API
2. X API Alternative
3. Tweet and Profile Data API
4. Clean JSON from X / Twitter
5. 100 Free Credits on Signup
6. Captapi Twitter API
7. Skip Expensive X API Tiers
8. One Key - 25+ Platforms
9. Built for Developers
10. Start Free Today
11. Production Twitter Data
12. Try Captapi Playground
13. Flat Credit Pricing
14. Profiles, Tweets, Search
15. REST API for X Data

Descriptions:

1. Pull tweets and profiles as clean JSON without enterprise X API bills. 100 free credits.
2. Captapi: Twitter/X data API plus 25+ platforms on one key.

### Facebook API

Headlines:

1. Facebook Scraper API
2. Facebook Page Data API
3. Facebook Video and Comments API
4. Clean JSON - One REST Key
5. 100 Free Credits on Signup
6. Captapi Facebook API
7. Built for Developers
8. One Key - 25+ Platforms
9. Start in 60 Seconds
10. Production Facebook Endpoints
11. Try Playground Free
12. Flat Credit Pricing
13. Pages, Videos, Comments
14. Skip Brittle Scrapers
15. Facebook Data for Apps

Descriptions:

1. Public Facebook page and video data as structured JSON. 100 free credits to start.
2. Captapi delivers Facebook data alongside Instagram, TikTok, and 20+ other platforms.

---

## 5) Free Tools RSA

### TikTok Transcript Tool -> /tools/tiktok-transcript

Headlines: TikTok to Transcript | Free TikTok Transcript Tool | Transcribe TikTok Videos | No Install Needed | Captapi Free Tools

Descriptions: Paste a TikTok URL and get the transcript. Free daily tries - upgrade anytime with API credits.

### Instagram Transcript Tool -> /tools/instagram-transcript

Headlines: Instagram Reel Transcript | Transcribe Instagram Reels | Free IG Transcript Tool | Captapi Free Tools | No Install Needed

Descriptions: Turn Instagram Reels into text in seconds. Free tool with optional API access for automation.

---

## 6) 7-day review loop

| Day | Check |
|---|---|
| 1-2 | Signup conversion firing (Ads diagnostics) |
| 3 | Pause Expansion ad groups with 0 impressions |
| 5 | Move winners from Expansion to Core budget |
| 7 | Cut keywords with spend and 0 signup |

Use `/dashboard/admin/funnel` to see signup -> API key.

---

## 7) Re-run DataForSEO

Credentials were not in the agent environment when CSVs were first written.
Some head-term volumes came from `keyword-bank.csv` (Ahrefs).

```powershell
cd socialkit-clone
$env:DATAFORSEO_LOGIN="..."
$env:DATAFORSEO_PASSWORD="..."
python scripts/ads_keyword_research.py
```

This overwrites `ads-keyword-plan.csv` and `google-ads-editor-import.csv` with live US volume/CPC.
