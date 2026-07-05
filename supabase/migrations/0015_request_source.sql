-- Track which scraping path served each request so we can measure the
-- self-scraping migration (direct HTTP vs Apify actor fallback).
--   'direct'  = our own scraper (no actor cost)
--   'apify'   = Apify actor (fallback or not yet migrated)
--   null      = cache hit or endpoint not yet instrumented
alter table public.requests
  add column if not exists source text;

comment on column public.requests.source is
  'Scraping path: direct (self-scraped) | apify (actor) | null (cache/unknown)';

-- Handy view for the migration dashboard: hit-rate per endpoint, last 7 days.
create or replace view public.scrape_source_stats as
select
  endpoint,
  coalesce(platform, 'other')                       as platform,
  count(*) filter (where source = 'direct')         as direct_hits,
  count(*) filter (where source = 'apify')          as apify_hits,
  count(*) filter (where cache_hit)                 as cache_hits,
  round(
    100.0 * count(*) filter (where source = 'direct')
    / nullif(count(*) filter (where source in ('direct', 'apify')), 0),
    1
  )                                                 as direct_pct
from public.requests
where created_at >= now() - interval '7 days'
group by 1, 2;
