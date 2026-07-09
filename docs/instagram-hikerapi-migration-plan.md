# Instagram -> HikerAPI Gecis Plani (Beklemede)

**Durum:** Uygulandi (details haric).
**Tetikleyici:** Kullanici "Instagram icin HikerAPI'ye gecelim" dediginde basla.
**Tarih:** 2026-07-06

---

## Neden HikerAPI?

Instagram'in iki sorunu var: (1) native scraping residential proxy ile bile acilmiyor
(Instagram web_profile_info her istekte 429; Reddit gibi hesap/oturum tabanli koruma),
(2) Apify actor modeli her istekte container ayaga kaldirdigi icin yavas (cold start 5-60 sn).

Degerlendirilen 3 secenek:

| Secenek | Karar | Gerekce |
|---|---|---|
| Apify Standby Mode | ELENDI | Kullandigimiz `apify/instagram-scraper` gibi actor'lar standby-enabled degil; baskasinin actor'inda bu ayari acamiyoruz. Fork + kendi HTTP server gerekir. Ayrica idle suresince CU yakar -> bursty trafikte maliyet tuzagi. |
| EnsembleData | ELENDI | Aylik sabit abonelik ($100-1400/ay), unit tabanli, 8 platform bundle. Instagram-agirlikli iste parayi bosa harcatir; YouTube/TikTok/Twitch'i zaten self-scrape ediyoruz. |
| HikerAPI | SECILDI | Pay-per-request $0.0006/istek, aylik taahhut yok, bakiye suresiz, sadece basarili istekte kesiliyor. Sub-second (~700ms) senkron yanit. 100+ IG endpoint'i. x-access-key header + JSON. 100 ucretsiz istek. |

**Maliyet kiyasi:** 100K profil -> HikerAPI ~$60 vs EnsembleData Gold $800/ay. Hiz: 5-60sn (Apify) -> sub-second.

**Not:** HikerAPI IG'ye ozeldir. TikTok/YouTube/Twitch'te kullanilmaz (oralari zaten self-scrape ediyoruz). Bu hamle SADECE Instagram'in "proxy ile acilmiyor + Apify yavas" ikili sorununu cozer.

---

## Response JSON'lari bozulur mu? -> HAYIR

Dis JSON semasi birebir korunur, cunku response'u Apify ham veriyi gecirerek degil kendi
kodumuz kurarak uretiyor (`_normalize_post`, channel-details elle kurulan dict, vb.).
HikerAPI'ye geciste sadece mapper'in SAG tarafini (kaynak alan adlarini) degistiririz;
SOL taraf (musterinin gordugu alanlar: username, displayName, followers...) sabit kalir.

Bu, YouTube/TikTok/Twitch'te yaptigimiz native-first pattern'in aynisi: native servis
"router'in bekledigi sekli" dondurur, dis sozlesme degismez.

### Tek gercek risk: alan kapsami
- Apify camelCase duz alanlar verir (`followersCount`, `fullName`).
- HikerAPI Instagram'in ham alanlarini verir, cogu nested (`edge_followed_by.count`,
  `full_name`, `biography`, `profile_pic_url`).
- HikerAPI bir alani hic vermiyorsa o alan sessizce null/0 dusebilir.
- Onlem: her endpoint icin eski Apify ciktisi ile yeni HikerAPI ciktisini ayni input icin
  yan yana diff'le; alan alan tuttugunu dogrula.

---

## Uygulama Adimlari

1. **Config:** `app/core/config.py`'ye `HIKERAPI_KEY: str = ""` ekle.
   `credentials_configured()` mantigi: key varsa native (HikerAPI) yolu ac, yoksa Apify'da kal.

2. **Servis katmani:** `app/services/instagram_hiker.py` (yeni).
   - x-access-key header'li httpx client, token cache gerekmez (API key sabit).
   - Her fonksiyon router'in bekledigi sekli dondurur veya None (fallback icin).
   - HikerAPI base URL + endpoint eslemesi dokumana gore netlestirilecek.

3. **Router:** `app/routers/instagram.py` endpoint'lerini native-first + Apify fallback yap.
   `ctx["source"] = "direct"` (HikerAPI hit) / `"apify"` (fallback).

4. **Oncelik sirasi (en cok kullanilan / en cok kazandiran once):**
   - [ ] channel-details (profil bilgisi) - ilk pilot, diff testi burada yapilir
   - [ ] channel-posts (profil gonderileri)
   - [ ] details (post/reel detay)
   - [ ] comments (yorumlar)
   - [ ] channel-reels, basic-profile, reels-search, video-download, kalanlar

5. **Dogrulama:**
   - 100 ucretsiz istekle once channel-details diff testi (eski vs yeni, alan alan).
   - `source` kolonundan direct hit-rate + latency + maliyet dususunu olc.
   - Her endpoint icin ayri diff + smoke test.

6. **Commit + push**, sonra prod'da smoke test.

---

## Baslamak icin kullanicidan gereken

- HikerAPI hesabi + API key (x-access-key). 100 ucretsiz istek kayitla geliyor.
- Key `backend/.env`'e `HIKERAPI_KEY=...` olarak eklenir.

---

## Ilgili mevcut altyapi
- `supabase/migrations/0015_request_source.sql` - source kolonu (direct/apify/null) + scrape_source_stats view.
- Native-first + Apify fallback pattern: `youtube_native.py`, `tiktok_native.py`, `twitch_native.py` ornek alinabilir.
- Instagram actor'lari: `app/core/config.py` icinde `APIFY_ACTOR_INSTAGRAM*` (fallback olarak kalacak).
