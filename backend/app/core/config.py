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
    APIFY_ACTOR_YOUTUBE_CHANNEL: str = "streamers/youtube-channel-scraper"
    APIFY_ACTOR_YOUTUBE_DOWNLOAD: str = "api-ninja/youtube-video-downloader"
    # Fallback downloader (used only if the primary returns no link), so a
    # single downloader outage doesn't break /video-download. Slower (~2min)
    # but high-volume/reliable; returns discrete file URLs.
    APIFY_ACTOR_YOUTUBE_DOWNLOAD_FALLBACK: str = "streamers/youtube-video-downloader"

    APIFY_ACTOR_TIKTOK: str = "clockworks/tiktok-scraper"
    APIFY_ACTOR_TIKTOK_COMMENTS: str = "clockworks/tiktok-comments-scraper"
    # Dedicated comment+reply scraper with a real reply API (parentCommentId
    # linking); far more reliable for fetching replies than the base comments
    # actor, billed pay-per-result.
    APIFY_ACTOR_TIKTOK_COMMENT_REPLIES: str = "coregent/tiktok-comment-scraper"
    APIFY_ACTOR_TIKTOK_PROFILE: str = "clockworks/tiktok-profile-scraper"
    APIFY_ACTOR_TIKTOK_SEARCH: str = "clockworks/tiktok-scraper"
    # Followers / followings use the official Clockworks relationship scraper
    # (returns `authorMeta` + `connectionType`); music feeds use the clockworks
    # sound scraper.
    APIFY_ACTOR_TIKTOK_FOLLOWERS: str = "clockworks/tiktok-followers-scraper"
    APIFY_ACTOR_TIKTOK_FOLLOWINGS: str = "clockworks/tiktok-followers-scraper"
    APIFY_ACTOR_TIKTOK_MUSIC: str = "clockworks/tiktok-sound-scraper"
    # Song/sound metadata only. apidojo returns song details in ~9s vs ~40s for
    # the clockworks sound scraper (which crawls the sound's video feed); the
    # latter stays as the music-posts actor and a song-details fallback.
    APIFY_ACTOR_TIKTOK_SONG: str = "apidojo/tiktok-music-scraper"
    # Trending (For You) video feed by region. HTTP-only, cheap pay-per-result.
    # `content_type` ("video") + `country_code`.
    APIFY_ACTOR_TIKTOK_TRENDING: str = "xtracto/tiktok-trending-scraper"
    # Popular/trending hashtag entity discovery. Pay-per-result ($1.60/1k),
    # no monthly rent. Input: searchQueries + includeHashtags.
    APIFY_ACTOR_TIKTOK_TREND_DISCOVERY: str = "coregent/tiktok-trend-discovery-scraper"
    APIFY_ACTOR_TIKTOK_LIVE: str = "unseenuser/tiktok-live-status-scraper"

    APIFY_ACTOR_INSTAGRAM: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_REEL: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_PROFILE: str = "apify/instagram-profile-scraper"
    APIFY_ACTOR_INSTAGRAM_POST: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_COMMENT: str = "apify/instagram-comment-scraper"
    APIFY_ACTOR_INSTAGRAM_TAGGED: str = "apify/instagram-tagged-scraper"
    # Dedicated reels-by-audio scraper (input: audioUrls). The generic
    # apify/instagram-scraper does not reliably resolve audio pages.
    APIFY_ACTOR_INSTAGRAM_AUDIO: str = "kinaesthetic_millionaire/instagram-reels-audio-scraper"
    # Story highlights (list + expanded items). Input: `usernames`.
    APIFY_ACTOR_INSTAGRAM_HIGHLIGHTS: str = "goat255/instagram-stories-highlights-scraper"

    APIFY_ACTOR_FACEBOOK_POSTS: str = "apify/facebook-posts-scraper"
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
    APIFY_ACTOR_FACEBOOK_EVENTS: str = "apify/facebook-events-scraper"
    APIFY_ACTOR_FACEBOOK_PHOTOS: str = "apify/facebook-photos-scraper"

    # YouTube community ("posts") tab. alpha-scraper is the cheapest rental
    # ($7.50/mo). Input: startUrls/usernames + maxposts.
    APIFY_ACTOR_YOUTUBE_COMMUNITY: str = "alpha-scraper/youtube-community-posts-scraper"

    # Twitter / X. apidojo "Tweet Scraper V2" handles tweets by URL, search
    # terms, and per-handle timelines (input: startUrls / searchTerms /
    # twitterHandles + maxItems). The user-scraper returns profile metadata.
    APIFY_ACTOR_TWITTER_TWEET: str = "apidojo/tweet-scraper"
    APIFY_ACTOR_TWITTER_PROFILE: str = "apidojo/twitter-user-scraper"

    # Reddit. trudax "Reddit Scraper Lite" handles subreddit URLs, post URLs
    # (with comments), and keyword search (input: startUrls / searches + type +
    # maxItems). Slug is config-driven so it can be swapped without code edits.
    APIFY_ACTOR_REDDIT: str = "trudax/reddit-scraper-lite"

    # Threads (Meta). User media actor accepts username + maxPosts; post media
    # actor accepts direct post links.
    APIFY_ACTOR_THREADS: str = "igview-owner/threads-user-media-scraper"
    APIFY_ACTOR_THREADS_POST: str = "easyapi/threads-post-media-downloader"
    APIFY_ACTOR_THREADS_SEARCH: str = "automation-lab/threads-scraper"

    # Pinterest. Pay-per-result actor (no monthly rent). Input:
    # searchQueries / usernames / boardUrls / pinUrls + maxResults.
    APIFY_ACTOR_PINTEREST: str = "thirdwatch/pinterest-scraper"
    APIFY_ACTOR_PINTEREST_BOARDS: str = "shareze001/pinterest-boards"

    # LinkedIn. Profile + company + post/search actors (rental, public data
    # only). Slugs are config-driven; verify access in the Apify console.
    APIFY_ACTOR_LINKEDIN_PROFILE: str = "apimaestro/linkedin-profile-detail"
    APIFY_ACTOR_LINKEDIN_COMPANY: str = "apimaestro/linkedin-company-detail"
    APIFY_ACTOR_LINKEDIN_POST: str = "apimaestro/linkedin-post-detail"
    APIFY_ACTOR_LINKEDIN_COMPANY_POSTS: str = "automation-lab/linkedin-company-posts-scraper"
    APIFY_ACTOR_LINKEDIN_POST_SEARCH: str = "apimaestro/linkedin-posts-search-scraper-no-cookies"

    # Rumble. Input: searchQueries + maxItems.
    APIFY_ACTOR_RUMBLE: str = "kawsar/rumble-video-extractor"
    APIFY_ACTOR_RUMBLE_COMMENTS: str = "thescrapelab/apify-rumble-scraper"
    APIFY_ACTOR_RUMBLE_TRANSCRIPT: str = "bulletproof/rumble-transcript-extractor"

    # TikTok Shop. 5 modes: shop_search, shop_catalog, product_details,
    # product_reviews, creator_showcase.
    APIFY_ACTOR_TIKTOK_SHOP: str = "unseenuser/tiktok-shop-scraper"

    # Public ad libraries. Kept separate because each platform has a different
    # public transparency surface and actor input schema.
    APIFY_ACTOR_FACEBOOK_AD_LIBRARY: str = "scrapemint/facebook-ads-library-scraper"
    APIFY_ACTOR_FACEBOOK_AD_LIBRARY_V2: str = "apify/facebook-ads-scraper"
    APIFY_ACTOR_TIKTOK_AD_LIBRARY: str = "brilliant_gum/tiktok-ads-library-scraper"
    APIFY_ACTOR_TIKTOK_AD_LIBRARY_DETAIL: str = "jy-labs/tiktok-ad-library-fast-search"
    APIFY_ACTOR_GOOGLE_AD_LIBRARY: str = "automation-lab/google-ads-scraper"
    APIFY_ACTOR_GOOGLE_AD_LIBRARY_V2: str = "unseenuser/google-ads"
    APIFY_ACTOR_LINKEDIN_AD_LIBRARY: str = "s-r/linkedin-ads-library"
    APIFY_ACTOR_LINKEDIN_AD_LIBRARY_DETAIL: str = "elliotpadfield/linkedin-ad-library-scraper"

    # Optional GitHub token avoids low unauthenticated public API limits.
    GITHUB_TOKEN: str = ""

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
