# Captapi — Launch Checklist

A pragmatic launch playbook based on what works for API-as-a-Service products.

## Pre-launch (Week -2 to 0)

### Product
- [ ] All endpoints return shape consistent with documented schema
- [ ] Cache hit ratio > 30% measured over a week of internal use
- [ ] p95 response time < 4s for cached, < 30s for cold
- [ ] Stripe end-to-end test: signup → checkout → credits granted → renewal credited
- [ ] Failed payment flow tested (Stripe test card 4000 0000 0000 0341)
- [ ] Refund handling tested
- [ ] Account deletion + key revocation works
- [ ] Rate limit returns proper 429 with Retry-After

### Marketing
- [ ] Domain + SSL
- [ ] Landing page with above-the-fold cURL example
- [ ] All 4 platform logos and a "single API for all" headline
- [ ] Pricing page with explicit credit cost per endpoint
- [ ] Public API docs with at least 3 cURL examples per platform
- [ ] At least 4 free-tool SEO landing pages live (`/tools/[slug]`)
- [ ] Robots.txt + sitemap.xml live

### Compliance
- [ ] Privacy policy
- [ ] Terms of service (cover: API usage, scraping responsibility, refund policy)
- [ ] Cookie banner if EU traffic expected
- [ ] DPA template ready if any B2B prospect asks

## Launch week

### Channels
- [ ] **Product Hunt** — schedule for Tuesday/Wednesday 00:01 PST
  - Tagline (~60 chars): "One API for YouTube, TikTok, Instagram & Facebook data"
  - First comment with a demo GIF + 3 use cases
  - Prepare 5 quick screenshots
- [ ] **Hacker News** — Show HN post the same day, separate from PH
  - Title format: "Show HN: I built an API for social media video data"
- [ ] **Indie Hackers** — milestone post explaining the build
- [ ] **Reddit** — r/SaaS, r/IndieDev, r/sideproject (not r/programming — they hate launches)
- [ ] **Twitter/X** — thread with the build journey
- [ ] **LinkedIn** — for B2B credibility

### Outreach
- [ ] Email 30 potential customers (small AI agencies, content tools, no-code builders)
- [ ] Reach out to 5 no-code platforms about a native integration
- [ ] Cold DM 10 content creator tool founders

## Post-launch (Week 1-4)

### Iterate based on signal
- [ ] Monitor sign-ups daily; count free → paid conversion
- [ ] Read every support ticket and turn into either a docs improvement or feature
- [ ] Identify the single most-used endpoint and write a deep-dive blog post about it

### SEO compounding
- [ ] Add 10 more `/tools/[slug]` landing pages (one per endpoint variant)
- [ ] Submit sitemap to Google Search Console
- [ ] Write 2 long-form blog posts: "How to scrape TikTok without getting banned" / "Building an AI agent that summarizes YouTube videos"

### Integrations
- [ ] Zapier integration — submit for review (takes 2-4 weeks)
- [x] Make.com app — local app built (packages/captapi-make), deploy via Make Apps Editor + submit for review
- [x] n8n community node — published (n8n-nodes-captapi)
- [ ] Publish Python SDK on PyPI
- [ ] Publish Node SDK on npm
- [ ] Free Chrome extension for transcript extraction (funnel to signup)

### Metrics to watch
- Free → paid conversion rate (target: 2-5%)
- Cache hit ratio (target: 40%+)
- Gross margin per active user (target: 80%+)
- MRR growth week-over-week (target: 15-25%)
- p95 latency
- Apify cost / revenue ratio

## Failure modes to watch for

| Symptom | Likely cause | Fix |
|---|---|---|
| Sudden Apify cost spike | One user looping requests | Add per-user daily hard limit |
| TikTok endpoint 429 from us | Actor blocked by TikTok | Failover to backup actor / pause endpoint |
| Margin under 50% | Heavy users on cheap plan | Raise Starter price OR cap Starter credits |
| Webhook missed → credits not granted | Stripe outage | Manual reconcile script via Stripe events.list |
| GPT cost runaway | Huge transcripts | Already truncated to 60k chars; double-check |

## When to invest in...

- **SDKs**: After 50+ paying customers asking for one
- **Webhooks**: Once anyone has a use case for >60s scrape jobs
- **Bulk endpoints**: When a top customer asks (will pay 2x)
- **Enterprise / SOC2**: First $30k+ MRR
- **Custom contracts**: First time a customer asks "can we negotiate?"
