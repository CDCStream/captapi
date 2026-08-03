-- =====================================================
-- Add oakon.com to disposable signup blocklist.
-- CREATE OR REPLACE so this applies even if 0020 already ran.
-- =====================================================

create or replace function public.reject_disposable_email()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  domain text;
begin
  domain := lower(split_part(coalesce(new.email, ''), '@', 2));
  if domain in (
    'web-library.net',
    'oakon.com',
    'mailinator.com',
    'guerrillamail.com',
    'tempmail.com',
    'throwaway.email',
    'temp-mail.org',
    '10minutemail.com',
    'trashmail.com',
    'yopmail.com',
    'sharklasers.com',
    'guerrillamailblock.com',
    'grr.la',
    'dispostable.com',
    'mailnesia.com',
    'maildrop.cc',
    'fakeinbox.com',
    'mailcatch.com',
    'tempail.com',
    'tempr.email',
    'discard.email',
    'tmpmail.net',
    'tmpmail.org',
    'emailondeck.com',
    'mohmal.com',
    'getnada.com',
    'burnermail.io',
    'mailsac.com',
    'inboxkitten.com',
    '33mail.com',
    'mytemp.email',
    'spam4.me',
    'tmail.ws',
    'mt2015.com',
    'jnxjn.com',
    'mailforspam.com',
    'mvrht.net'
  )
  or domain like '%.web-library.net'
  or domain like '%.oakon.com'
  then
    raise exception 'Disposable email addresses are not allowed'
      using errcode = 'check_violation';
  end if;
  return new;
end;
$$;

drop trigger if exists on_auth_user_reject_disposable on auth.users;
create trigger on_auth_user_reject_disposable
  before insert on auth.users
  for each row execute function public.reject_disposable_email();
