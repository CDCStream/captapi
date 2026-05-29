-- =====================================================
-- Captapi — add geo (country/region/city) to activity events
-- Populated from Vercel's edge IP-geolocation headers via /api/geo,
-- so no third-party geo service is required.
-- =====================================================

alter table public.events
  add column if not exists country text,
  add column if not exists region  text,
  add column if not exists city    text;

create index if not exists idx_events_country on public.events(country);
