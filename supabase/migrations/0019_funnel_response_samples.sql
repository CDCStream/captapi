-- Funnel: link response_samples -> requests, indexes, 14-day retention cleanup.

alter table public.response_samples
  add column if not exists request_id uuid;

create index if not exists idx_response_samples_request_id
  on public.response_samples (request_id)
  where request_id is not null;

create index if not exists idx_response_samples_user_created
  on public.response_samples (user_id, created_at desc);

create index if not exists idx_response_samples_created
  on public.response_samples (created_at desc);

-- Drop samples older than N days (default 14). Schedule via pg_cron if available.
create or replace function public.cleanup_response_samples(retention_days int default 14)
returns void
language sql
security definer
as $$
  delete from public.response_samples
   where created_at < now() - make_interval(days => retention_days);
$$;

-- Optional cron (uncomment on Supabase after enabling pg_cron):
-- select cron.schedule(
--   'captapi-response-samples-cleanup',
--   '15 3 * * *',
--   $$ select public.cleanup_response_samples(14); $$
-- );
