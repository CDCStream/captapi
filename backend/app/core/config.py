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
    APIFY_ACTOR_YOUTUBE_TRANSCRIPT: str = "pintostudio/youtube-transcript-scraper"
    APIFY_ACTOR_YOUTUBE_VIDEO: str = "streamers/youtube-scraper"
    APIFY_ACTOR_YOUTUBE_COMMENTS: str = "streamers/youtube-comments-scraper"
    APIFY_ACTOR_YOUTUBE_SEARCH: str = "streamers/youtube-scraper"
    APIFY_ACTOR_YOUTUBE_CHANNEL: str = "streamers/youtube-channel-scraper"
    APIFY_ACTOR_YOUTUBE_DOWNLOAD: str = "api-ninja/youtube-video-downloader"

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

    APIFY_ACTOR_INSTAGRAM: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_REEL: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_PROFILE: str = "apify/instagram-profile-scraper"
    APIFY_ACTOR_INSTAGRAM_POST: str = "apify/instagram-scraper"
    APIFY_ACTOR_INSTAGRAM_COMMENT: str = "apify/instagram-comment-scraper"
    APIFY_ACTOR_INSTAGRAM_TAGGED: str = "apify/instagram-tagged-scraper"

    APIFY_ACTOR_FACEBOOK_POSTS: str = "apify/facebook-posts-scraper"
    APIFY_ACTOR_FACEBOOK_PAGES: str = "apify/facebook-pages-scraper"
    APIFY_ACTOR_FACEBOOK_COMMENTS: str = "apify/facebook-comments-scraper"

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

    CACHE_TTL_SECONDS: int = 86_400
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
