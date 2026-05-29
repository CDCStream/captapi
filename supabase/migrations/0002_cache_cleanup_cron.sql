-- Optional: enable pg_cron and schedule daily cleanup of expired DB cache rows.
-- Supabase exposes pg_cron under the "extensions" schema.

-- create extension if not exists pg_cron with schema extensions;

-- select cron.schedule(
--   'captapi-cache-cleanup',
--   '0 3 * * *',
--   $$ select public.cleanup_expired_cache(); $$
-- );

-- Reset monthly subscription credits at period start. The Stripe `invoice.paid`
-- webhook already handles this for active subscriptions, but this is a safety net
-- in case a webhook is missed.

create or replace function public.reset_expired_subscription_credits()
returns void language sql security definer as $$
  update public.credit_balances
     set subscription_credits = 0,
         plan = 'free'
   where subscription_renews_at is not null
     and subscription_renews_at < now() - interval '7 days'
     and plan <> 'free';
$$;

-- select cron.schedule(
--   'captapi-reset-expired',
--   '0 4 * * *',
--   $$ select public.reset_expired_subscription_credits(); $$
-- );
