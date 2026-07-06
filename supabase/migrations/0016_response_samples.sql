-- Temporary response-body samples for correctness auditing of the scraping
-- migration (native vs Apify output quality). Kept in its own table so the hot
-- `requests` table stays lean and analytics queries stay fast. Populated by a
-- fire-and-forget background writer (see app/services/response_sampler.py),
-- gated behind LOG_RESPONSE_BODIES and sampled by LOG_RESPONSE_SAMPLE_RATE.
--
-- This is meant to be dropped once the audit is done:
--   drop table if exists public.response_samples;

create table if not exists public.response_samples (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  user_id uuid,
  api_key_id uuid,
  endpoint text not null,
  platform text,
  resource_url text,
  source text,                       -- direct | apify | null (matches requests.source)
  status_code int,
  response_time_ms int,
  cache_hit boolean not null default false,
  truncated boolean not null default false,  -- body exceeded LOG_RESPONSE_MAX_BYTES -> not stored
  response_json jsonb                -- the exact payload we returned (null when truncated)
);

-- Audit queries slice by endpoint + freshness.
create index if not exists idx_response_samples_endpoint
  on public.response_samples (endpoint, created_at desc);

create index if not exists idx_response_samples_source
  on public.response_samples (source, endpoint);
