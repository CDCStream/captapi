"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_PORT: int = 8000
    APP_CORS_ORIGINS: str = "http://localhost:3000"
    APP_BASE_URL: str = "http://localhost:8000"

    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_ANON_KEY: str

    APIFY_TOKEN: str
    # Let legitimate long-running actors finish. Endpoint code should use fast
    # public paths or actor fallbacks for responsiveness instead of cutting off
    # valid actor runs with an aggressive global timeout.
    APIFY_SYNC_TIMEOUT_SECONDS: float = 120.0
    APIFY_SYNC_MAX_ATTEMPTS: int = 1
    APIFY_SYNC_RETRY_MAX_WAIT_SECONDS: float = 3.0
    MCP_TOOL_TIMEOUT_SECONDS: float = 120.0
    # Legacy single transcript actor (kept for backward-compat env binding).
    APIFY_ACTOR_YOUTUBE_TRANSCRIPT: str = "pintostudio/youtube-transcript-scraper"
    # Primary + fallback timestamped transcript actors. The old pintostudio
    # actor started returning empty `{"data": []}` for every video, so we run
    # two independent actors for resilience. New names (not the legacy var) so
    # deployments that pinned APIFY_ACTOR_YOUTUBE_TRANSCRIPT still pick these up.
    APIFY_ACTOR_YT_TRANSCRIPT_1: str = "scrape-creators/best-youtube-transcripts-scraper"
    APIFY_ACTOR_YT_TRANSCRIPT_2: str = "automation-lab/youtube-transcript"
    APIFY_ACTOR_YOUTUBE_VIDEO: str = "streamers/youtube-scraper"
    APIFY_ACTOR_YOUTUBE_COMMENTS: str = "streamers/youtube-comments-scraper"
    APIFY_ACTOR_YOUTUBE_SEARCH: str = "streamers/youtube-scraper"
    APIFY_ACTOR_YOUTUBE_PLAYLIST: str = "powerai/youtube-playlist-videos-scraper"
    APIFY_ACTOR_YOUTUBE_PLAYLIST_FALLBACK: str = "streamers/youtube-scraper"
    APIFY_ACTOR_YOUTUBE_CHANNEL: str = "streamers/youtube-channel-scraper"
    APIFY_ACTOR_YOUTUBE_DOWNLOAD: str = "api-ninja/youtube-video-downloader"
    # Fallback downloader (used only if the primary returns no link), so a
    # single downloader outage doesn't break /video-download. Slower (~2min)
    # but high-volume/reliable; returns discrete file URLs.
    APIFY_ACTOR_YOUTUBE_DOWNLOAD_FALLBACK: str = "streamers/youtube-video-downloader"

    APIFY_ACTOR_TIKTOK: str = "clockworks/tiktok-scraper"
    # Dedicated transcript actor: native TikTok captions with timestamped
    # segments, Whisper fallback for videos without captions.
    APIFY_ACTOR_TIKTOK_TRANSCRIPT: str = "crawlerbros/tiktok-transcript-scraper"
    APIFY_ACTOR_TIKTOK_COMMENTS: str = "clockworks/tiktok-comments-scraper"
    # Dedicated comment+reply scraper with a real reply API (parentCommentId
    # linking); far more reliable for fetching replies than the base comments
    # actor, billed pay-per-result.
    APIFY_ACTOR_TIKTOK_COMMENT_REPLIES: str = "coregent/tiktok-comment-scraper"
    APIFY_ACTOR_TIKTOK_COMMENT_REPLIES_FAST: str = "automation-lab/tiktok-comments-scraper"
    APIFY_ACTOR_TIKTOK_PROFILE: str = "clockworks/tiktok-profile-scraper"
    APIFY_ACTOR_TIKTOK_SEARCH: str = "clockworks/tiktok-scraper"
    # Followers / followings use the official Clockworks relationship scraper
    # (returns `authorMeta` + `connectionType`); music feeds use the clockworks
    # sound scraper.
    APIFY_ACTOR_TIKTOK_FOLLOWERS: str = "clockworks/tiktok-followers-scraper"
    APIFY_ACTOR_TIKTOK_FOLLOWINGS: str = "clockworks/tiktok-followers-scraper"
    APIFY_ACTOR_TIKTOK_MUSIC: str = "coregent/tiktok-sound-music-scraper"
    APIFY_ACTOR_TIKTOK_MUSIC_POSTS: str = "powerai/tiktok-music-posts-video-scraper"
    APIFY_ACTOR_TIKTOK_MUSIC_FALLBACK: str = "clockworks/tiktok-sound-scraper"
    # Song/sound metadata only. apidojo returns song details in ~9s vs ~40s for
    # the clockworks sound scraper (which crawls the sound's video feed); the
    # latter stays as the music-posts actor and a song-details fallback.
    APIFY_ACTOR_TIKTOK_SONG: str = "apidojo/tiktok-music-scraper"
    APIFY_ACTOR_TIKTOK_SONG_FAST_FALLBACK: str = "coregent/tiktok-sound-music-scraper"
    # Trending (For You) video feed by region. HTTP-only, cheap pay-per-result.
    # `content_type` ("video") + `country_code`.
    APIFY_ACTOR_TIKTOK_TRENDING: str = "xtracto/tiktok-trending-scraper"
    # Popular/trending hashtag entity discovery. Pay-per-result ($1.60/1k),
    # no monthly rent. Input: searchQueries + includeHashtags.
    APIFY_ACTOR_TIKTOK_TREND_DISCOVERY: str = "coregent/tiktok-trend-discovery-scraper"
    APIFY_ACTOR_TIKTOK_LIVE: str = "unseenuser/tiktok-live-status-scraper"
    APIFY_ACTOR_TIKTOK_SEARCH_SUGGESTIONS: str = "automation-lab/tiktok-keywords-discovery"
    # Creative Center trending creators (input: {"trendType": "creator",
    # "countryCode": "US", "maxResults": n}). The scraperx actor is a paid
    # rental we don't have, and burbn returns empty datasets — kept only as
    # last-resort fallbacks.
    APIFY_ACTOR_TIKTOK_POPULAR_CREATORS: str = "automation-lab/tiktok-trends-scraper"
    APIFY_ACTOR_TIKTOK_POPULAR_CREATORS_FALLBACK: str = "burbn/tiktok-trending-creators"
    APIFY_ACTOR_TIKTOK_AUDIENCE: str = ""

    # spry_headset/instagram-page-post-scraper was disabled by its author
    # (every run now fails), so the official Apify scraper is primary and the
    # profile scraper acts as a schema-compatible fallback.
    APIFY_ACTOR_INSTAGRAM: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_FALLBACK: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_REEL: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_REEL_FALLBACK: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_PROFILE: str = "apify/instagram-profile-scraper"
    APIFY_ACTOR_INSTAGRAM_POST: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_COMMENT: str = "apify/instagram-comment-scraper"
    APIFY_ACTOR_INSTAGRAM_TRANSCRIPT: str = "crawlerbros/instagram-transcript-scraper"
    # "auto" tries native Instagram captions first, then falls back to Whisper
    # speech-to-text (with timestamped segments). "native" alone returns
    # nothing for most reels because IG rarely exposes captions.
    APIFY_INSTAGRAM_TRANSCRIPT_METHOD: str = "auto"
    APIFY_ACTOR_INSTAGRAM_TAGGED: str = "apify/instagram-tagged-scraper"
    # Dedicated reels-by-audio scraper (input: audioUrls). The generic
    # apify/instagram-scraper does not reliably resolve audio pages.
    APIFY_ACTOR_INSTAGRAM_AUDIO: str = "kinaesthetic_millionaire/instagram-reels-audio-scraper"
    # Story highlights (list + expanded items). Input: `usernames`.
    APIFY_ACTOR_INSTAGRAM_HIGHLIGHTS: str = "goat255/instagram-stories-highlights-scraper"
    APIFY_ACTOR_INSTAGRAM_TRENDING: str = "agentx/instagram-trending-scraper"

    APIFY_ACTOR_FACEBOOK_POSTS: str = "apify/facebook-posts-scraper"
    # AI transcript extractor for FB videos/reels (Whisper): returns full
    # transcript + timestamped normalizedSegments. The posts scraper never
    # returns subtitles, so it only serves as a text-post fallback.
    APIFY_ACTOR_FACEBOOK_TRANSCRIPT: str = "sian.agency/facebook-ai-transcript-extractor"
    APIFY_ACTOR_FACEBOOK_PAGES: str = "apify/facebook-pages-scraper"
    APIFY_ACTOR_FACEBOOK_COMMENTS: str = "apify/facebook-comments-scraper"
    # Reels are filtered out of the official posts scraper's feed (no separate
    # reels actor needed -> trusted, no full-permission grant, no monthly rent).
    APIFY_ACTOR_FACEBOOK_REELS: str = "apify/facebook-posts-scraper"
    APIFY_ACTOR_FACEBOOK_GROUPS: str = "apify/facebook-groups-scraper"
    # Marketplace: keyword + location search (no login). Input: queries +
    # locationName (or lat/lng) + fetchItemDetails. Events: official Apify
    # actor; input: searchQueries / startUrls + maxEvents.
    APIFY_ACTOR_FACEBOOK_MARKETPLACE: str = "unseenuser/fb-marketplace"
    # Single-listing details by listingId (the search actor above has no
    # per-item mode). Returns FB's raw GraphQL listing entity.
    APIFY_ACTOR_FACEBOOK_MARKETPLACE_ITEM: str = "data-slayer/facebook-marketplace-details"
    APIFY_ACTOR_FACEBOOK_EVENTS: str = "apify/facebook-events-scraper"
    APIFY_ACTOR_FACEBOOK_EVENT_DETAILS: str = "crawlerbros/facebook-events-scraper"
    APIFY_ACTOR_FACEBOOK_PHOTOS: str = "apify/facebook-photos-scraper"

    # YouTube community ("posts") tab. alpha-scraper is the cheapest rental
    # ($7.50/mo). Input: startUrls/usernames + maxposts.
    APIFY_ACTOR_YOUTUBE_COMMUNITY: str = "alpha-scraper/youtube-community-posts-scraper"
    APIFY_ACTOR_YOUTUBE_TRENDING: str = "app.tanalytics/youtube-trending-videos"
    APIFY_ACTOR_YOUTUBE_SHORTS: str = "khadinakbar/youtube-shorts-scraper"

    # Twitter / X. apidojo "Tweet Scraper V2" handles tweets by URL, search
    # terms, and per-handle timelines (input: startUrls / searchTerms /
    # twitterHandles + maxItems). The user-scraper returns profile metadata.
    APIFY_ACTOR_TWITTER_TWEET: str = "apidojo/tweet-scraper"
    APIFY_ACTOR_TWITTER_PROFILE: str = "apidojo/twitter-user-scraper"
    APIFY_ACTOR_TWITTER_COMMUNITY: str = "scrape.badger/twitter-community-scraper"

    # Reddit. trudax "Reddit Scraper Lite" handles subreddit URLs, post URLs
    # (with comments), and keyword search (input: startUrls / searches + type +
    # maxItems). Slug is config-driven so it can be swapped without code edits.
    APIFY_ACTOR_REDDIT: str = "trudax/reddit-scraper-lite"

    # Score-rich post search (input: {"queries": ["keyword" | "r/sub" |
    # "r/sub keyword"], "maxItems": n}). Unlike the trudax lite actor its rows
    # include score / num_comments / over_18 / created_utc, so the listing
    # endpoints prefer it when Reddit public JSON is unavailable.
    APIFY_ACTOR_REDDIT_SEARCH: str = "fatihtahta/reddit-scraper-search-fast"

    # Subreddit community profile (members, description, title, rules, flags).
    # Input: {"community": "<name>"}. The trudax lite actor returns empty
    # communities, so subreddit-details uses this dedicated profiler instead.
    APIFY_ACTOR_REDDIT_COMMUNITY: str = "truefetch/reddit-community-profile"

    # Post + full comment tree with real scores, threading (parentId/depth),
    # and permalinks (input: {"postUrl", "maxCommentsPerPost", "sort"}). Used
    # when Reddit's public JSON blocks our IPs, before the sparser trudax
    # fallback which lacks comment scores entirely.
    APIFY_ACTOR_REDDIT_COMMENTS: str = "clearpath/reddit-post-comments-bulk-scraper"

    # Threads (Meta). User media actor accepts username + maxPosts; post media
    # actor accepts direct post links.
    APIFY_ACTOR_THREADS: str = "igview-owner/threads-user-media-scraper"
    APIFY_ACTOR_THREADS_POST: str = "easyapi/threads-post-media-downloader"
    APIFY_ACTOR_THREADS_SEARCH: str = "automation-lab/threads-scraper"

    # Pinterest. Pay-per-result actor (no monthly rent). Input:
    # searchQueries / usernames / boardUrls / pinUrls + maxResults.
    # crawlerbros "Pinterest Scraper Pro": single actor, mode-based
    # (search / pinDetail / userPins / userBoards / boardPins / userProfile),
    # residential proxy with HTML fallback, pay-per-result (no monthly rent).
    APIFY_ACTOR_PINTEREST: str = "crawlerbros/pinterest-scraper-pro"

    # LinkedIn. Profile + company + post/search actors (rental, public data
    # only). Slugs are config-driven; verify access in the Apify console.
    APIFY_ACTOR_LINKEDIN_PROFILE: str = "apimaestro/linkedin-profile-detail"
    APIFY_ACTOR_LINKEDIN_COMPANY: str = "apimaestro/linkedin-company-detail"
    APIFY_ACTOR_LINKEDIN_POST: str = "apimaestro/linkedin-post-detail"
    APIFY_ACTOR_LINKEDIN_COMPANY_POSTS: str = "automation-lab/linkedin-company-posts-scraper"
    APIFY_ACTOR_LINKEDIN_POST_SEARCH: str = "apimaestro/linkedin-posts-search-scraper-no-cookies"

    # Rumble. Input: searchQueries + maxItems.
    APIFY_ACTOR_RUMBLE: str = "kawsar/rumble-video-extractor"
    # All-inclusive scraper: resolves single video URLs and channel video
    # listings directly (the keyword actor above can't).
    APIFY_ACTOR_RUMBLE_DETAILS: str = "azzouzana/rumble-all-inclusive-scraper"
    APIFY_ACTOR_RUMBLE_COMMENTS: str = "thescrapelab/apify-rumble-scraper"
    # Long-tail public platforms.
    APIFY_ACTOR_GOOGLE_SEARCH: str = "apify/google-search-scraper"
    APIFY_ACTOR_TWITCH: str = "maximedupre/twitch-scraper"
    APIFY_ACTOR_TWITCH_URL: str = "abotapi/twitch-scraper"
    # Upcoming broadcast schedule (nextSchedule) per channel; the actors above
    # never return schedule segments. Input: {"keywords": [login],
    # "maxItems": 20} (actor-enforced minimum of 20).
    APIFY_ACTOR_TWITCH_SCHEDULE: str = "easyapi/twitch-channel-scraper"
    # Search: automation-lab covers tracks/artists/albums reliably; the
    # apiharvest all-types actor (often returns "No results") is kept only for
    # podcast/episode search which automation-lab does not support.
    APIFY_ACTOR_SPOTIFY_SEARCH: str = "automation-lab/spotify-scraper"
    APIFY_ACTOR_SPOTIFY_SEARCH_ALL: str = "apiharvest/spotify-search-all-types"
    APIFY_ACTOR_SPOTIFY_DETAILS: str = "apiharvest/spotify-scraper-get-full-details"
    APIFY_ACTOR_SOUNDCLOUD: str = "automation-lab/soundcloud-scraper"
    APIFY_ACTOR_SNAPCHAT_PROFILE: str = "crawlerbros/snapchat-profile-scraper"
    APIFY_ACTOR_TRUTH_SOCIAL: str = "simpleapi/truth-social-scraper"
    APIFY_ACTOR_TRUTH_SOCIAL_FALLBACK: str = "automation-lab/truth-social-scraper"
    APIFY_ACTOR_KICK: str = "scrapestorm/kick-videos-clips-scraper-cheap"
    APIFY_ACTOR_AMAZON_SHOP: str = "piotrv1001/amazon-storefront-scraper"
    APIFY_ACTOR_AGE_GENDER: str = "parseforge/agify-name-demographics-scraper"
    APIFY_ACTOR_KWAI: str = "sian.agency/kwai-kuaishou-scraper"

    # TikTok Shop. 5 modes: shop_search, shop_catalog, product_details,
    # product_reviews, creator_showcase.
    APIFY_ACTOR_TIKTOK_SHOP: str = "unseenuser/tiktok-shop-scraper"

    # Product-detail lookups via TikTok's mobile API (input: {"productInput":
    # url_or_id, "region": "US"}). Returns title/price/images/stock/store_info
    # where the generic scraper's product_details mode only echoes the URL.
    APIFY_ACTOR_TIKTOK_SHOP_DETAILS: str = "cunning_soil/tiktok-shop-product-scraper-mobile-api"

    # Dedicated review scraper (input: {"region", "product_ids": [url|id],
    # "reviews_limit"}). Returns rating/text/date/images/verified-purchase
    # where the generic scraper's product_reviews mode usually returns 0 rows.
    APIFY_ACTOR_TIKTOK_SHOP_REVIEWS: str = "web_wanderer/tiktok-reviews-scraper"

    # Public ad libraries. Kept separate because each platform has a different
    # public transparency surface and actor input schema.
    APIFY_ACTOR_FACEBOOK_AD_LIBRARY: str = "scrapemint/facebook-ads-library-scraper"
    APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2: str = "apify/facebook-ads-scraper"
    APIFY_ACTOR_TIKTOK_AD_LIBRARY: str = "brilliant_gum/tiktok-ads-library-scraper"
    APIFY_ACTOR_TIKTOK_AD_LIBRARY_DETAIL: str = "jy-labs/tiktok-ad-library-fast-search"
    APIFY_ACTOR_TIKTOK_AD_LIBRARY_DETAIL_FALLBACK: str = "prodiger/tiktok-ads-library-scraper"
    APIFY_ACTOR_GOOGLE_AD_LIBRARY: str = "automation-lab/google-ads-scraper"
    APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2: str = "unseenuser/google-ads"
    APIFY_ACTOR_LINKEDIN_AD_LIBRARY: str = "s-r/linkedin-ads-library"
    APIFY_ACTOR_LINKEDIN_AD_LIBRARY_DETAIL: str = "elliotpadfield/linkedin-ad-library-scraper"
    APIFY_ACTOR_LINKEDIN_AD_LIBRARY_DETAIL_FALLBACK: str = "silentflow/linkedin-ads-scraper"

    # Optional GitHub token avoids low unauthenticated public API limits.
    GITHUB_TOKEN: str = ""

    # Optional Reddit OAuth app (script/client-credentials). When set, comment
    # fetches use oauth.reddit.com, which works from datacenter IPs and keeps
    # vote counts + threading that the actor fallback lacks.
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""

    # Self-scraping proxy pool. When set, direct HTTP scrapers (YouTube,
    # Reddit, ...) route through these instead of hitting upstreams from the
    # datacenter IP, which gets blocked. Order = preference:
    #   PROXY_DATACENTER_URL  -> cheap, for lenient targets (YouTube, Reddit)
    #   PROXY_RESIDENTIAL_URL -> pricier, for strict targets / on block
    # Format: http://user:pass@host:port  (rotating gateway recommended)
    PROXY_DATACENTER_URL: str = ""
    PROXY_RESIDENTIAL_URL: str = ""

    # Bluesky uses the public AT-Protocol AppView API directly (no actor).
    BLUESKY_API_BASE: str = "https://public.api.bsky.app"

    # SponsorBlock public crowdsourced API (no key) powers YouTube ad/sponsor
    # segment lookups. Free, so the endpoint only bills a flat credit.
    SPONSORBLOCK_API_BASE: str = "https://sponsor.ajay.app"

    OPENAI_API_KEY: str
    OPENAI_MODEL_SUMMARY: str = "gpt-4o-mini"
    OPENAI_MODEL_TRANSCRIPTION: str = "whisper-1"

    # Dodo Payments (Merchant of Record)
    DODO_PAYMENTS_API_KEY: str = ""
    DODO_PAYMENTS_WEBHOOK_KEY: str = ""
    DODO_PAYMENTS_ENVIRONMENT: Literal["test_mode", "live_mode"] = "test_mode"

    # Subscription product IDs (one per plan / billing cycle)
    DODO_PRODUCT_STARTER_MONTHLY: str = ""
    DODO_PRODUCT_STARTER_YEARLY: str = ""
    DODO_PRODUCT_PRO_MONTHLY: str = ""
    DODO_PRODUCT_PRO_YEARLY: str = ""
    DODO_PRODUCT_BUSINESS_MONTHLY: str = ""
    DODO_PRODUCT_BUSINESS_YEARLY: str = ""

    # One-time (PAYG) credit pack product IDs
    DODO_PRODUCT_PACK_STARTER: str = ""
    DODO_PRODUCT_PACK_GROWTH: str = ""
    DODO_PRODUCT_PACK_SCALE: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"

    # Default fallback TTL (kept for backwards compatibility).
    CACHE_TTL_SECONDS: int = 86_400
    # Tiered cache TTLs by how time-sensitive the data is (all <= 24h to stay
    # within our data-retention policy):
    #  - STATIC: content that never changes (transcripts, AI summaries).
    #  - DYNAMIC: data that changes over time (likes/views/followers/comments,
    #    lists, search). Short TTL so metrics stay fresh. Set 0 to disable caching.
    #  - VOLATILE: short-lived signed URLs (video downloads).
    CACHE_TTL_STATIC: int = 86_400  # 24 hours
    CACHE_TTL_DYNAMIC: int = 3_600  # 1 hour
    CACHE_TTL_VOLATILE: int = 3_600  # 1 hour
    RATE_LIMIT_PER_MINUTE: int = 60  # fallback when a plan has no explicit limit

    # Per-plan request-per-minute limits (must match the pricing page).
    RATE_LIMIT_FREE: int = 40
    RATE_LIMIT_STARTER: int = 120
    RATE_LIMIT_PRO: int = 300
    RATE_LIMIT_BUSINESS: int = 600

    MAX_VIDEO_UPLOAD_MB: int = 200
    MAX_VIDEO_DURATION_MINUTES: int = 60

    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    # Transactional email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Captapi <no-reply@captapi.com>"
    FRONTEND_URL: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.APP_CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    def rate_limit_for_plan(self, plan: str | None) -> int:
        """Requests-per-minute allowed for the caller's plan."""
        limits = {
            "free": self.RATE_LIMIT_FREE,
            "starter": self.RATE_LIMIT_STARTER,
            "pro": self.RATE_LIMIT_PRO,
            "business": self.RATE_LIMIT_BUSINESS,
        }
        return limits.get((plan or "free").lower(), self.RATE_LIMIT_PER_MINUTE)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
