-- =====================================================
-- Captapi — Dodo Payments migration
-- Adds Dodo Payments identifiers alongside (or replacing) the Stripe ones.
-- =====================================================

alter table public.subscriptions
  add column if not exists dodo_customer_id text,
  add column if not exists dodo_subscription_id text;

create unique index if not exists idx_subscriptions_dodo_customer
  on public.subscriptions(dodo_customer_id)
  where dodo_customer_id is not null;

create unique index if not exists idx_subscriptions_dodo_subscription
  on public.subscriptions(dodo_subscription_id)
  where dodo_subscription_id is not null;

alter table public.credit_transactions
  add column if not exists dodo_payment_id text;
