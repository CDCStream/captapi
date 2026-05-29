"""FastAPI application entry."""

from __future__ import annotations

import logging
import sys

import sentry_sdk
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app import __version__
from app.core.config import get_settings
from app.routers import (
    account,
    auth_keys,
    billing,
    facebook,
    instagram,
    tiktok,
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
        description="Extract transcripts, summaries, comments and stats from social media videos.",
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

    @app.exception_handler(Exception)
    async def unhandled(_: Request, exc: Exception) -> JSONResponse:
        # The catch-all handler "consumes" the exception, so report it to
        # Sentry explicitly to make sure it isn't swallowed silently.
        sentry_sdk.capture_exception(exc)
        logger = structlog.get_logger()
        logger.exception("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "internal_server_error"},
        )

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {
            "name": "Captapi API",
            "version": __version__,
            "docs": "/v1/docs",
        }

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
    app.include_router(instagram.router, prefix="/v1/instagram", tags=["Instagram"])
    app.include_router(facebook.router, prefix="/v1/facebook", tags=["Facebook"])
    app.include_router(video.router, prefix="/v1/video", tags=["Video Files"])
    app.include_router(account.router, prefix="/v1/account", tags=["Account"])
    app.include_router(auth_keys.router, prefix="/v1/auth/keys", tags=["API Keys"])
    app.include_router(billing.router, prefix="/v1/billing", tags=["Billing"])

    return app


app = create_app()
