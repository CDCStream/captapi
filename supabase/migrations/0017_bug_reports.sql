-- User-submitted bug reports from API docs pages and the dashboard.
-- Inserts go through the Next.js /api/bug-report route with the service role;
-- the table has no public policies (RLS on, nothing exposed to anon).

create table if not exists public.bug_reports (
  id uuid primary key default gen_random_uuid(),
  -- Catalog slug like "instagram-details"; null when the user didn't pick one.
  endpoint_slug text,
  message text not null check (char_length(message) between 3 and 5000),
  -- Optional contact email typed into the form (logged-out users).
  email text,
  -- Set server-side from the Supabase session when the reporter is logged in.
  user_id uuid references auth.users (id) on delete set null,
  user_email text,
  -- Page the report was sent from, e.g. "/apis/instagram-details".
  page text,
  status text not null default 'open'
    check (status in ('open', 'in_progress', 'resolved', 'wont_fix')),
  created_at timestamptz not null default now()
);

create index if not exists idx_bug_reports_status_created
  on public.bug_reports (status, created_at desc);

alter table public.bug_reports enable row level security;
