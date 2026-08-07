-- Weekly fetch-path / pricing subsidy report (after migration 0022).
-- Repricing rule: extended <10% keep flat; 10-30% raise flat; >30% fix native.
-- Window: 2 weeks of traffic or 500 calls/endpoint, whichever first.

select
  r.endpoint,
  count(*) filter (where r.status_code < 400 and not r.cache_hit) as calls,
  round(
    100.0 * count(*) filter (
      where r.status_code < 400
        and not r.cache_hit
        and r.source in ('extended', 'apify')
    )
    / nullif(count(*) filter (where r.status_code < 400 and not r.cache_hit), 0),
    1
  ) as extended_pct,
  round(
    avg(r.result_count) filter (
      where r.status_code < 400 and not r.cache_hit and r.result_count is not null
    ),
    1
  ) as avg_results,
  coalesce(
    sum(
      greatest(coalesce(r.credits_computed, r.credits_used) - r.credits_used, 0)
    ) filter (where r.status_code < 400 and not r.cache_hit),
    0
  ) as subsidy_credits,
  round(avg(r.response_time_ms) filter (where r.status_code < 400 and not r.cache_hit) / 1000.0, 1) as avg_s
from public.requests r
where r.created_at >= now() - interval '7 days'
group by r.endpoint
order by subsidy_credits desc, calls desc;
