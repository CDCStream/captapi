-- =====================================================
-- Captapi — Initial Schema
-- =====================================================

-- Required extensions
create extension if not exists "pgcrypto";

-- =====================================================
-- API KEYS
-- =====================================================
create table public.api_keys (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  key_hash text not null unique,
  key_prefix text not null,
  name text,
  last_used_at timestamptz,
  created_at timestamptz not null default now(),
  revoked_at timestamptz
);

create index idx_api_keys_user on public.api_keys(user_id);
create index idx_api_keys_hash on public.api_keys(key_hash) where revoked_at is null;

-- =====================================================
-- CREDIT BALANCES
-- =====================================================
create table public.credit_balances (
  user_id uuid primary key references auth.users(id) on delete cascade,
  subscription_credits int not null default 0,
  topup_credits int not null default 0,
  subscription_renews_at timestamptz,
  plan text not null default 'free',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- =====================================================
-- REQUEST LOG
-- =====================================================
create table public.requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  api_key_id uuid references public.api_keys(id) on delete set null,
  endpoint text not null,
  platform text,
  resource_url text,
  credits_used int not null default 0,
  cache_hit boolean not null default false,
  status_code int,
  response_time_ms int,
  error_message text,
  created_at timestamptz not null default now()
);

create index idx_requests_user_created on public.requests(user_id, created_at desc);
create index idx_requests_endpoint on public.requests(endpoint);

-- =====================================================
-- CACHED RESULTS (fallback if Redis unavailable)
-- =====================================================
create table public.cached_results (
  cache_key text primary key,
  payload jsonb not null,
  expires_at timestamptz not null,
  created_at timestamptz not null default now()
);

create index idx_cache_expires on public.cached_results(expires_at);

-- =====================================================
-- STRIPE SUBSCRIPTIONS
-- =====================================================
create table public.subscriptions (
  user_id uuid primary key references auth.users(id) on delete cascade,
  stripe_customer_id text unique,
  stripe_subscription_id text unique,
  status text,
  plan text,
  current_period_end timestamptz,
  cancel_at_period_end boolean default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- =====================================================
-- CREDIT TRANSACTIONS (audit)
-- =====================================================
create table public.credit_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  type text not null,
  amount int not null,
  description text,
  stripe_payment_intent_id text,
  request_id uuid references public.requests(id) on delete set null,
  created_at timestamptz not null default now()
);

create index idx_credit_tx_user on public.credit_transactions(user_id, created_at desc);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================
alter table public.api_keys enable row level security;
alter table public.credit_balances enable row level security;
alter table public.requests enable row level security;
alter table public.subscriptions enable row level security;
alter table public.credit_transactions enable row level security;

-- Users see only their own data
create policy "users_own_api_keys" on public.api_keys
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "users_own_credit_balance" on public.credit_balances
  for select using (auth.uid() = user_id);

create policy "users_own_requests" on public.requests
  for select using (auth.uid() = user_id);

create policy "users_own_subscription" on public.subscriptions
  for select using (auth.uid() = user_id);

create policy "users_own_credit_tx" on public.credit_transactions
  for select using (auth.uid() = user_id);

-- service_role can do anything (used by backend)
-- (service_role bypasses RLS by default in Supabase)

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-create credit_balances row on user signup
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
as $$
begin
  insert into public.credit_balances (user_id, subscription_credits, plan)
  values (new.id, 100, 'free')
  on conflict (user_id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- updated_at trigger
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end; $$;

create trigger trg_credit_balances_updated
  before update on public.credit_balances
  for each row execute function public.set_updated_at();

create trigger trg_subscriptions_updated
  before update on public.subscriptions
  for each row execute function public.set_updated_at();

-- =====================================================
-- RPC: atomic credit deduction
-- =====================================================
-- Returns the number of credits actually deducted (0 if insufficient).
-- Spends subscription credits first, then topup credits.
create or replace function public.deduct_credits(
  p_user_id uuid,
  p_amount int
) returns int
language plpgsql
security definer
as $$
declare
  v_sub int;
  v_top int;
  v_from_sub int;
  v_from_top int;
begin
  select subscription_credits, topup_credits
    into v_sub, v_top
    from public.credit_balances
   where user_id = p_user_id
   for update;

  if v_sub is null then
    return 0;
  end if;

  if (v_sub + v_top) < p_amount then
    return 0;
  end if;

  v_from_sub := least(v_sub, p_amount);
  v_from_top := p_amount - v_from_sub;

  update public.credit_balances
     set subscription_credits = subscription_credits - v_from_sub,
         topup_credits        = topup_credits        - v_from_top
   where user_id = p_user_id;

  return p_amount;
end;
$$;

grant execute on function public.deduct_credits(uuid, int) to service_role;

-- RPC: grant credits
create or replace function public.grant_credits(
  p_user_id uuid,
  p_subscription int default 0,
  p_topup int default 0,
  p_plan text default null,
  p_renews_at timestamptz default null
) returns void
language plpgsql
security definer
as $$
begin
  insert into public.credit_balances (user_id, subscription_credits, topup_credits, plan, subscription_renews_at)
  values (p_user_id, p_subscription, p_topup, coalesce(p_plan, 'free'), p_renews_at)
  on conflict (user_id) do update
    set subscription_credits   = excluded.subscription_credits,
        topup_credits          = public.credit_balances.topup_credits + p_topup,
        plan                   = coalesce(p_plan, public.credit_balances.plan),
        subscription_renews_at = coalesce(p_renews_at, public.credit_balances.subscription_renews_at);
end;
$$;

grant execute on function public.grant_credits(uuid, int, int, text, timestamptz) to service_role;

-- =====================================================
-- CACHE CLEANUP (run via pg_cron)
-- =====================================================
create or replace function public.cleanup_expired_cache()
returns void language sql security definer as $$
  delete from public.cached_results where expires_at < now();
$$;
