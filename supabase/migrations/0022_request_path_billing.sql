-- Published-flat measurement window: log uncapped path cost vs charged credits,
-- and rename customer-facing path vocabulary (native | extended) without naming
-- infrastructure suppliers. See scrape_path_weekly view for the subsidy report.

alter table public.requests
  add column if not exists credits_computed integer;

alter table public.requests
  add column if not exists result_count integer;

comment on column public.requests.source is
  'Fetch path: native | extended | cache | null (legacy rows may still say direct|apify)';

comment on column public.requests.credits_computed is
  'What the serving path would have cost before the published-price cap';

comment on column public.requests.result_count is
  'Result rows returned on list/search endpoints (for avgResults / subsidy reports)';

-- Prefer new vocabulary; still count legacy direct/apify rows during rollout.
create or replace view public.scrape_source_stats as
select
  endpoint,
  coalesce(platform, 'other') as platform,
  count(*) filter (
    where source in ('native', 'direct')
  ) as native_hits,
  count(*) filter (
    where source in ('extended', 'apify')
  ) as extended_hits,
  count(*) filter (where cache_hit) as cache_hits,
  round(
    100.0 * count(*) filter (where source in ('native', 'direct'))
    / nullif(
      count(*) filter (
        where source in ('native', 'direct', 'extended', 'apify')
      ),
      0
    ),
    1
  ) as native_pct
from public.requests
where created_at >= now() - interval '7 days'
group by 1, 2;

-- Weekly subsidy report: sum(credits_computed - credits_used) is the absorbed cost.
create or replace view public.scrape_path_weekly as
select
  endpoint,
  count(*) filter (where status_code < 400 and not cache_hit) as calls,
  round(
    100.0 * count(*) filter (
      where status_code < 400
        and not cache_hit
        and source in ('extended', 'apify')
    )
    / nullif(count(*) filter (where status_code < 400 and not cache_hit), 0),
    1
  ) as extended_pct,
  round(
    avg(result_count) filter (
      where status_code < 400 and not cache_hit and result_count is not null
    ),
    1
  ) as avg_results,
  coalesce(
    sum(
      greatest(coalesce(credits_computed, credits_used) - credits_used, 0)
    ) filter (where status_code < 400 and not cache_hit),
    0
  ) as subsidy_credits,
  round(
    avg(response_time_ms) filter (where status_code < 400 and not cache_hit),
    0
  ) as avg_ms
from public.requests
where created_at >= now() - interval '7 days'
group by 1;
