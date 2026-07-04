-- Testimonials / social proof wall. Rows come from G2, Capterra, X, Product
-- Hunt, or direct emails. The homepage renders published rows ordered by
-- sort_order; the section hides itself while the table is empty, so this can
-- ship before the first review lands.

create table if not exists public.testimonials (
  id uuid primary key default gen_random_uuid(),
  source text not null default 'other'
    check (source in ('g2', 'capterra', 'x', 'producthunt', 'reddit', 'email', 'other')),
  author_name text not null,
  -- e.g. "Founder, acme.dev" or "@handle" — free-form, shown under the name.
  author_role text not null default '',
  quote text not null,
  -- 1-5; null when the source has no star system (tweets, emails).
  rating smallint check (rating between 1 and 5),
  -- Link to the original review/tweet for authenticity.
  source_url text,
  published boolean not null default false,
  sort_order int not null default 100,
  created_at timestamptz not null default now()
);

create index if not exists idx_testimonials_published
  on public.testimonials (published, sort_order);

alter table public.testimonials enable row level security;

-- Public read of published rows only; writes go through the service role.
create policy "testimonials_public_read" on public.testimonials
  for select using (published = true);
