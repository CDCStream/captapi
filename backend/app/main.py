"""FastAPI application entry."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import sentry_sdk
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app import __version__
from app.core.config import get_settings
from app.services.apify_client import ApifyError
from app.routers import (
    account,
    ad_library,
    age_gender,
    analytics,
    amazon_shop,
    auth_keys,
    billing,
    creator_pages,
    facebook,
    github,
    google_search,
    instagram,
    kick,
    kwai,
    bluesky,
    linkedin,
    linktree,
    mcp,
    pinterest,
    reddit,
    rumble,
    snapchat,
    soundcloud,
    spotify,
    threads,
    tiktok,
    tiktok_shop,
    truth_social,
    twitch,
    twitter,
    video,
    youtube,
)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=level.upper(),
        format="%(message)s",
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level.upper())
        ),
    )


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)

    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.05 if settings.is_production else 0.0,
            environment=settings.APP_ENV,
            send_default_pii=True,
        )

    app = FastAPI(
        title="Captapi API",
        version=__version__,
        description=(
            "Extract transcripts, summaries, comments and stats from social "
            "media videos (YouTube, TikTok, Instagram, Facebook). Connect by AI "
            "agents and no-code tools via the MCP server (@captapi/mcp), the CLI "
            "(@captapi/cli), the n8n community node (n8n-nodes-captapi), the "
            "Make.com custom app, or the Apify Actor (BYO key). "
            "Full guide: https://captapi.com/docs/integrations"
        ),
        openapi_url="/v1/openapi.json",
        docs_url="/v1/docs",
        redoc_url="/v1/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def _error_cors_headers(request: Request) -> dict[str, str]:
        # Starlette runs this catch-all via ServerErrorMiddleware, which sits
        # OUTSIDE CORSMiddleware — so 500 responses would otherwise ship without
        # CORS headers and surface in browsers as an opaque "Failed to fetch".
        origin = request.headers.get("origin")
        allowed = settings.cors_origins
        if origin and (origin in allowed or "*" in allowed):
            return {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Vary": "Origin",
            }
        return {}

    @app.exception_handler(ApifyError)
    async def upstream_actor_error(request: Request, exc: ApifyError) -> JSONResponse:
        # A third-party Apify actor failed (unrented/quota/timeout/upstream 4xx-5xx).
        # This is an upstream dependency failure, not a bug in our service, so it
        # must surface as 502 rather than falling through to the 500 catch-all.
        logger = structlog.get_logger()
        logger.warning("apify_actor_error", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=502,
            content={"success": False, "error": "upstream_actor_error"},
            headers=_error_cors_headers(request),
        )

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception) -> JSONResponse:
        # The catch-all handler "consumes" the exception, so report it to
        # Sentry explicitly to make sure it isn't swallowed silently.
        sentry_sdk.capture_exception(exc)
        logger = structlog.get_logger()
        logger.exception("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "internal_server_error"},
            headers=_error_cors_headers(request),
        )

    static_dir = Path(__file__).parent / "static"

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {
            "name": "Captapi API",
            "version": __version__,
            "docs": "/v1/docs",
        }

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> FileResponse:
        return FileResponse(static_dir / "favicon.ico", media_type="image/x-icon")

    @app.get("/healthz", tags=["meta"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    # Temporary route to verify Sentry is wired up. Disabled in production.
    if not settings.is_production:

        @app.get("/sentry-debug", tags=["meta"], include_in_schema=False)
        async def sentry_debug() -> dict[str, str]:
            _ = 1 / 0  # noqa: F841 — intentional error for Sentry test
            return {"status": "unreachable"}

    app.include_router(youtube.router, prefix="/v1/youtube", tags=["YouTube"])
    app.include_router(tiktok.router, prefix="/v1/tiktok", tags=["TikTok"])
    app.include_router(tiktok_shop.router, prefix="/v1/tiktok-shop", tags=["TikTok Shop"])
    app.include_router(truth_social.router, prefix="/v1/truth-social", tags=["Truth Social"])
    app.include_router(instagram.router, prefix="/v1/instagram", tags=["Instagram"])
    app.include_router(facebook.router, prefix="/v1/facebook", tags=["Facebook"])
    app.include_router(ad_library.router, prefix="/v1/ad-library", tags=["Ad Library"])
    app.include_router(google_search.router, prefix="/v1/google", tags=["Google"])
    app.include_router(github.router, prefix="/v1/github", tags=["GitHub"])
    app.include_router(twitter.router, prefix="/v1/twitter", tags=["Twitter"])
    app.include_router(reddit.router, prefix="/v1/reddit", tags=["Reddit"])
    app.include_router(threads.router, prefix="/v1/threads", tags=["Threads"])
    app.include_router(bluesky.router, prefix="/v1/bluesky", tags=["Bluesky"])
    app.include_router(pinterest.router, prefix="/v1/pinterest", tags=["Pinterest"])
    app.include_router(linkedin.router, prefix="/v1/linkedin", tags=["LinkedIn"])
    app.include_router(rumble.router, prefix="/v1/rumble", tags=["Rumble"])
    app.include_router(kick.router, prefix="/v1/kick", tags=["Kick"])
    app.include_router(kwai.router, prefix="/v1/kwai", tags=["Kwai"])
    app.include_router(creator_pages.router, prefix="/v1", tags=["Creator Pages"])
    app.include_router(twitch.router, prefix="/v1/twitch", tags=["Twitch"])
    app.include_router(spotify.router, prefix="/v1/spotify", tags=["Spotify"])
    app.include_router(soundcloud.router, prefix="/v1/soundcloud", tags=["SoundCloud"])
    app.include_router(linktree.router, prefix="/v1/linktree", tags=["Linktree"])
    app.include_router(snapchat.router, prefix="/v1/snapchat", tags=["Snapchat"])
    app.include_router(amazon_shop.router, prefix="/v1/amazon-shop", tags=["Amazon Shop"])
    app.include_router(age_gender.router, prefix="/v1/age-gender", tags=["Age and Gender"])
    app.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])
    app.include_router(video.router, prefix="/v1/video", tags=["Video Files"])
    app.include_router(account.router, prefix="/v1/account", tags=["Account"])
    app.include_router(auth_keys.router, prefix="/v1/auth/keys", tags=["API Keys"])
    app.include_router(billing.router, prefix="/v1/billing", tags=["Billing"])
    app.include_router(mcp.router, prefix="/mcp", tags=["MCP"], include_in_schema=False)

    return app


app = create_app()
