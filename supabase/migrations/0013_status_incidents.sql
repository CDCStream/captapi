-- Status incidents: manually curated incident history shown at /status.
-- Add a row when something breaks; append updates as the situation evolves.
--
-- updates jsonb shape: [{"at": "2026-07-04T12:00:00Z", "status": "investigating",
--                        "message": "..."}, ...] (newest last)

create table if not exists public.status_incidents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  severity text not null default 'minor'
    check (severity in ('minor', 'major')),
  status text not null default 'investigating'
    check (status in ('investigating', 'monitoring', 'resolved')),
  started_at timestamptz not null default now(),
  resolved_at timestamptz,
  updates jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_status_incidents_started
  on public.status_incidents (started_at desc);

alter table public.status_incidents enable row level security;

create policy "status_incidents_public_read" on public.status_incidents
  for select using (true);
