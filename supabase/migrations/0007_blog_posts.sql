-- =====================================================
-- Captapi — blog posts (Outrank.so auto-publishing)
-- Posts are written by the service role (webhook / admin) and read publicly
-- when status = 'published'.
-- =====================================================

create table if not exists public.blog_posts (
  id           uuid primary key default gen_random_uuid(),
  slug         text unique not null,
  title        text not null,
  description  text default '',
  content      text default '',
  image        text default '',
  tags         text[] default '{}',
  author       text default 'Outrank',
  status       text default 'published',
  published_at timestamptz default now(),
  updated_at   timestamptz default now(),
  created_at   timestamptz default now()
);

create index if not exists idx_blog_posts_status        on public.blog_posts(status);
create index if not exists idx_blog_posts_slug          on public.blog_posts(slug);
create index if not exists idx_blog_posts_published_at   on public.blog_posts(published_at desc);

alter table public.blog_posts enable row level security;

-- Anyone may read published posts. Drafts and writes stay service-role only.
drop policy if exists "blog_posts_public_read" on public.blog_posts;
create policy "blog_posts_public_read"
  on public.blog_posts for select
  to anon, authenticated
  using (status = 'published');
