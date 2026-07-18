# Directory Listing Kit

Ready-to-paste copy for the Phase 2 backlink starter stack (target: 10 referring domains by day 60). Work through these top-to-bottom. G2 and Capterra come first, since their reviews feed the homepage "Wall of love".

Once reviews land, publish them on the site with:

```sql
insert into public.testimonials
  (source, author_name, author_role, quote, rating, source_url, published, sort_order)
values
  ('g2', 'Jane Doe', 'Founder, acme.dev',
   'Switched from building our own scrapers - Captapi just works.', 5,
   'https://www.g2.com/products/captapi/reviews/...', true, 10);
```

---

## Shared assets (all directories)

- Name: Captapi
- Website: https://captapi.com
- Category: Developer Tools / APIs / Web Scraping / Social Media Analytics
- One-liner (60 chars): One API for structured data from 20+ social platforms.
- Short description (150 chars):
  Captapi turns TikTok, YouTube, Instagram, Facebook, X, Reddit and 15+ more
  platforms into clean JSON - one REST key, no OAuth, no scrapers.
- Long description (500+ chars):
  Captapi is a social data API for developers. One Bearer key gives you
  profiles, posts, videos, comments, transcripts, AI summaries, search, ad
  libraries, and commerce data across 20+ platforms - YouTube, TikTok,
  Instagram, Facebook, Twitter/X, Reddit, Threads, Bluesky, Pinterest,
  LinkedIn, Twitch, Spotify, and more. Responses are clean, consistent JSON;
  pass cache=true for a free 24h cache hit (default is always fresh). Ships
  with TypeScript and Python SDKs, a CLI, a hosted MCP server for AI agents,
  n8n/Make/Apify integrations, monitors with HMAC-signed webhooks, and a
  public status page. Start free with 100 credits - no credit card required.
- Pricing model: Free tier + pay-as-you-go credits
- Screenshots to prepare: landing hero, /apis catalog, endpoint page with
  playground, dashboard usage view, /status page, /integrations page.
- Logo: frontend/public/logo.png (prepare a 400x400 PNG)

---

## 1. G2 - g2.com/products/new (do first)

- Category: "Web Scraping Software" + "Big Data Analytics" secondary.
- After the listing is approved, collect the first 5 reviews by emailing
  active users (see the review-request template below).
- G2 requires reviewers to have a LinkedIn account or business email - warn
  users so reviews don't get rejected.

## 2. Capterra - capterra.com/vendors (Gartner Digital Markets)

- One vendor form covers Capterra + GetApp + Software Advice (3 domains, 1 form).
- Category: "Data Extraction Software".
- Reviews sync across all three sites.

## 3. Product Hunt - producthunt.com/posts/new

- Launch on a Tuesday-Thursday at 12:01 AM PT.
- Tagline: "One API for TikTok, YouTube, Instagram & 20+ social platforms"
- First comment: founder story - why building scrapers in-house is a
  treadmill, and what 100 free credits lets people test.
- Prepare: 5 gallery images + a 30-60s demo GIF of the playground.

## 4. SaaSHub - saashub.com/submit-service

- Free, instant, gives a followed link. List alternatives: ScrapeCreators,
  Apify, EnsembleData, TikAPI - this also feeds "alternative to X" search
  traffic to our /alternatives pages.

## 5. AlternativeTo - alternativeto.net (Add application)

- Register as the app's official representative after submitting.
- Add Captapi as an alternative to: ScrapeCreators, Apify, Phantombuster,
  TikAPI, EnsembleData.

## 6. Betalist - betalist.com/submit

- Works even post-launch if positioned as "recently launched".

## 7. Community (the week after directories)

- IndieHackers: product page + a "building in public" milestone post.
- Reddit: r/SideProject, r/webscraping, r/webdev - value-first posts
  (e.g. the free tools or the status-page architecture), not ads.
- Discord/Slack: n8n community, Make community, MCP/AI-agent servers - we
  have native integrations to show, which keeps posts on-topic.

---

## Review-request email template

Send after a user's ~50th successful request.

Subject: Quick favor? (2 minutes, genuinely helps)

> Hi {name},
>
> You've made {n} requests with Captapi - hope it's been smooth. We just got
> listed on G2/Capterra, and early reviews decide whether other developers
> find us at all.
>
> If Captapi saved you time, a short honest review would mean a lot:
> {g2_link} or {capterra_link}
>
> It takes about 2 minutes. And if anything has annoyed you, reply to this
> email instead - I read every reply and usually fix things the same week.
>
> Thanks!

Rules of thumb: never incentivize reviews with credits on G2/Capterra (it is
against their terms and gets reviews removed); stagger requests so reviews
trickle in over weeks instead of arriving in one suspicious batch.
