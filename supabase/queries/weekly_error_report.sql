-- ============================================================================
-- Haftalik Hata Raporu (Weekly Error Report)
-- ============================================================================
-- Supabase SQL editorunde calistirin. Her bolum bagimsizdir; istediginizi
-- tek basina secip calistirabilirsiniz. Pencere: son 7 gun (bir onceki 7 gun
-- ile karsilastirmali). Sadece 5xx (sistemsel) hatalar sayilir; 4xx kullanici
-- hatasidir ve rapora dahil edilmez.
--
-- Haftalik iyilestirme rutini:
--   1) Bolum 1 ile genel gidisati gorun (bu hafta vs gecen hafta).
--   2) Bolum 2/3 ile en cok hata ureten endpoint ve mesajlari bulun.
--   3) Bolum 4 ile hatalarin hangi gun/saatte yogunlastigina bakin.
--   4) Bolum 5 ile yavaslayan endpointleri tespit edin.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1) Platform bazinda haftalik ozet: istek, 5xx, hata orani + onceki hafta
-- ----------------------------------------------------------------------------
with this_week as (
  select
    coalesce(platform, 'other') as platform,
    count(*)                                        as requests,
    count(*) filter (where status_code >= 500)      as errors_5xx,
    round(avg(response_time_ms))                    as avg_ms
  from public.requests
  where created_at >= now() - interval '7 days'
  group by 1
),
prev_week as (
  select
    coalesce(platform, 'other') as platform,
    count(*)                                        as requests,
    count(*) filter (where status_code >= 500)      as errors_5xx
  from public.requests
  where created_at >= now() - interval '14 days'
    and created_at <  now() - interval '7 days'
  group by 1
)
select
  t.platform,
  t.requests,
  t.errors_5xx,
  round(100.0 * t.errors_5xx / t.requests, 2)                 as error_pct,
  coalesce(p.errors_5xx, 0)                                   as prev_week_5xx,
  t.errors_5xx - coalesce(p.errors_5xx, 0)                    as change_5xx,
  t.avg_ms
from this_week t
left join prev_week p using (platform)
order by t.errors_5xx desc, t.requests desc;


-- ----------------------------------------------------------------------------
-- 2) Endpoint bazinda en cok 5xx ureten endpointler (ornek hata mesajiyla)
-- ----------------------------------------------------------------------------
select
  endpoint,
  coalesce(platform, 'other')                            as platform,
  count(*)                                               as errors_5xx,
  min(created_at)                                        as first_seen,
  max(created_at)                                        as last_seen,
  (array_agg(left(error_message, 160) order by created_at desc)
     filter (where error_message is not null))[1]        as latest_error_message
from public.requests
where created_at >= now() - interval '7 days'
  and status_code >= 500
group by endpoint, platform
order by errors_5xx desc
limit 25;


-- ----------------------------------------------------------------------------
-- 3) En sik gorulen hata mesajlari (kok neden gruplamasi icin)
-- ----------------------------------------------------------------------------
select
  left(coalesce(error_message, '(mesaj yok)'), 160)  as error_message,
  count(*)                                           as occurrences,
  count(distinct endpoint)                           as affected_endpoints,
  max(created_at)                                    as last_seen
from public.requests
where created_at >= now() - interval '7 days'
  and status_code >= 500
group by 1
order by occurrences desc
limit 25;


-- ----------------------------------------------------------------------------
-- 4) Gunluk trend: son 7 gunun gun gun istek / 5xx dagilimi
-- ----------------------------------------------------------------------------
select
  date_trunc('day', created_at)::date                as day,
  count(*)                                           as requests,
  count(*) filter (where status_code >= 500)         as errors_5xx,
  round(100.0 * count(*) filter (where status_code >= 500) / count(*), 2)
                                                     as error_pct
from public.requests
where created_at >= now() - interval '7 days'
group by 1
order by 1;


-- ----------------------------------------------------------------------------
-- 5) En yavas endpointler (ortalama ve p95 yanit suresi, ms)
-- ----------------------------------------------------------------------------
select
  endpoint,
  count(*)                                                         as requests,
  round(avg(response_time_ms))                                     as avg_ms,
  percentile_cont(0.95) within group (order by response_time_ms)   as p95_ms,
  count(*) filter (where status_code >= 500)                       as errors_5xx
from public.requests
where created_at >= now() - interval '7 days'
  and response_time_ms is not null
group by endpoint
having count(*) >= 5
order by p95_ms desc
limit 25;
