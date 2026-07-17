-- =====================================================
-- Captapi — Paddle Billing migration
-- Adds Paddle identifiers alongside the Dodo ones so the active merchant of
-- record (settings.PAYMENT_PROVIDER) can be switched without losing history.
-- =====================================================

alter table public.subscriptions
  add column if not exists paddle_customer_id text,
  add column if not exists paddle_subscription_id text;

create unique index if not exists idx_subscriptions_paddle_customer
  on public.subscriptions(paddle_customer_id)
  where paddle_customer_id is not null;

create unique index if not exists idx_subscriptions_paddle_subscription
  on public.subscriptions(paddle_subscription_id)
  where paddle_subscription_id is not null;

alter table public.credit_transactions
  add column if not exists paddle_transaction_id text;
