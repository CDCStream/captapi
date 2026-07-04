-- Time-series snapshots of profile/post metrics, recorded automatically on
-- cache-miss fetches of tracked endpoints (see app/services/metric_history.py)
-- and served by GET /v1/history. One row per resource per ~6h.

create table if not exists public.metric_history (
  id bigint generated always as identity primary key,
  endpoint text not null,
  resource text not null,
  metrics jsonb not null,
  captured_at timestamptz not null default now()
);

create index if not exists idx_metric_history_lookup
  on public.metric_history (endpoint, resource, captured_at desc);
