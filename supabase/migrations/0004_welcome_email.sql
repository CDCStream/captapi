-- Track whether the one-time welcome email has been sent to a user.
alter table public.credit_balances
  add column if not exists welcomed_at timestamptz;
