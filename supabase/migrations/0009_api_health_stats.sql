-- Aggregated API health for the public status page (/v1/status).
-- 5xx responses count as server errors; 4xx are caller errors and ignored.

create or replace function public.api_health_stats(p_hours int default 24)
returns table (
  platform text,
  total bigint,
  server_errors bigint,
  avg_response_ms numeric
)
language sql
stable
security definer
set search_path = public
as $$
  select
    coalesce(platform, 'other') as platform,
    count(*) as total,
    count(*) filter (where status_code >= 500) as server_errors,
    round(avg(response_time_ms)) as avg_response_ms
  from requests
  where created_at > now() - make_interval(hours => p_hours)
  group by 1
  order by 2 desc;
$$;

-- Speeds up the 24h window scan on busy instances.
create index if not exists idx_requests_created_at on public.requests (created_at desc);
