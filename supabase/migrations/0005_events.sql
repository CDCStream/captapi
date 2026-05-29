-- =====================================================
-- Captapi — user activity / analytics events
-- Captures behaviour from BOTH logged-in users and anonymous visitors.
-- Anonymous rows have user_id = null and are correlated via anon_id
-- (a UUID persisted in the browser's localStorage).
-- =====================================================

create table if not exists public.events (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references auth.users(id) on delete set null,
  anon_id     text,
  event       text not null,
  path        text,
  referrer    text,
  properties  jsonb not null default '{}'::jsonb,
  user_agent  text,
  created_at  timestamptz not null default now()
);

create index if not exists idx_events_user_id    on public.events(user_id);
create index if not exists idx_events_anon_id     on public.events(anon_id);
create index if not exists idx_events_event       on public.events(event);
create index if not exists idx_events_created_at  on public.events(created_at desc);

alter table public.events enable row level security;

-- Anonymous visitors (anon key) may insert events, but only with a null user_id.
drop policy if exists "events_insert_anon" on public.events;
create policy "events_insert_anon"
  on public.events for insert
  to anon
  with check (user_id is null);

-- Signed-in users may insert events attributed to themselves (or anonymous).
drop policy if exists "events_insert_authenticated" on public.events;
create policy "events_insert_authenticated"
  on public.events for insert
  to authenticated
  with check (user_id is null or user_id = auth.uid());

-- No public SELECT/UPDATE/DELETE: only the service role (which bypasses RLS)
-- can read events, e.g. from the backend or SQL editor.
