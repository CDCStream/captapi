-- Monitors: scheduled watches over any list-returning Captapi endpoint.
-- New items since the previous run are pushed to the user's webhook with
-- an HMAC-signed payload. Runs bill credits exactly like direct API calls.

create table if not exists public.monitors (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  name text not null default '',
  endpoint text not null,
  params jsonb not null default '{}'::jsonb,
  interval_minutes int not null default 60 check (interval_minutes >= 15),
  webhook_url text not null,
  secret text not null,
  active boolean not null default true,
  last_run_at timestamptz,
  next_run_at timestamptz not null default now(),
  last_status text,
  last_error text,
  seen_ids jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_monitors_due
  on public.monitors (next_run_at)
  where active;

create index if not exists idx_monitors_user
  on public.monitors (user_id);

alter table public.monitors enable row level security;

-- Backend uses the service role (bypasses RLS). Dashboard users can read
-- their own monitors directly if we ever query from the browser.
create policy "monitors_select_own" on public.monitors
  for select using (auth.uid() = user_id);
