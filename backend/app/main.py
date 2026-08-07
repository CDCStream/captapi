"""FastAPI application entry."""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import sentry_sdk
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.core.config import get_settings
from app.services.apify_client import ApifyError
from app.routers import (
    account,
    ad_library,
    analytics,
    amazon_shop,
    auth_keys,
    batch,
    billing,
    creator_pages,
    facebook,
    github,
    history,
    instagram,
    kick,
    kwai,
    bluesky,
    linkedin,
    linktree,
    mcp,
    monitors,
    pinterest,
    reddit,
    rumble,
    snapchat,
    soundcloud,
    spotify,
    status,
    threads,
    tiktok,
    tiktok_shop,
    truth_social,
    twitch,
    twitter,
    video,
    youtube,
)


class BillingHeaderMiddleware:
    """Stamp billing metadata onto response headers and the JSON envelope.

    Pure-ASGI (no task hop) so it shares the async context with the endpoint;
    billed_call publishes into `request_meta` in its finally, which runs before
    the response is sent. Injects ``cached``, ``creditsUsed``, ``requestId``,
    ``fetchedAt``, and ``cachedAt`` into successful JSON bodies so clients do
    not have to rely on headers alone.
    """

    _MAX_INJECT_BYTES = 2_000_000

    def __init__(self, app):  # noqa: ANN001 - ASGI app
        self.app = app

    async def __call__(self, scope, receive, send):  # noqa: ANN001
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        import json

        from app.core.credits import request_meta

        request_meta.set(None)
        start_message: dict | None = None
        body_chunks: list[bytes] = []

        async def send_wrapper(message):  # noqa: ANN001
            nonlocal start_message
            if message["type"] == "http.response.start":
                start_message = message
                return
            if message["type"] != "http.response.body" or start_message is None:
                await send(message)
                return

            body_chunks.append(message.get("body") or b"")
            if message.get("more_body"):
                return

            body = b"".join(body_chunks)
            meta = request_meta.get() or {}
            headers = list(start_message.get("headers") or [])
            if meta:
                cache_hit = bool(meta.get("cache_hit"))
                source = "cache" if cache_hit else (meta.get("source") or "unknown")
                request_id = str(meta.get("request_id") or "")
                headers.extend(
                    [
                        (b"x-captapi-source", str(source).encode()),
                        (b"x-captapi-credits", str(meta.get("credits", 0)).encode()),
                        (b"x-captapi-cache", b"1" if cache_hit else b"0"),
                    ]
                )
                if request_id:
                    headers.append((b"x-captapi-request-id", request_id.encode()))

                status = int(start_message.get("status", 200))
                ctype = b""
                for k, v in headers:
                    if k.lower() == b"content-type":
                        ctype = v.lower()
                        break
                if (
                    status < 400
                    and b"application/json" in ctype
                    and 0 < len(body) <= self._MAX_INJECT_BYTES
                ):
                    try:
                        payload = json.loads(body)
                    except (ValueError, TypeError):
                        payload = None
                    if isinstance(payload, dict) and payload.get("success") is True:
                        cache_hit = bool(meta.get("cache_hit"))
                        fetched_at = meta.get("fetched_at")
                        data = payload.get("data")
                        # Pad every object-array to a uniform key set (absent → null)
                        # before clients see the body. Safe default — only adds nulls.
                        if data is not None:
                            from app.utils.array_normalise import normalise_object_arrays
                            from app.core.credits import rewrite_public_path_fields

                            data = normalise_object_arrays(data)
                            if isinstance(data, dict):
                                rewrite_public_path_fields(data)
                            payload["data"] = data
                        if fetched_at is None and isinstance(data, dict):
                            fetched_at = data.get("fetchedAt")
                        payload["cached"] = cache_hit
                        payload["creditsUsed"] = int(meta.get("credits") or 0)
                        if request_id:
                            payload["requestId"] = request_id
                        if fetched_at:
                            payload["fetchedAt"] = fetched_at
                        payload["cachedAt"] = fetched_at if cache_hit else None
                        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
                        headers = [
                            (k, v)
                            for k, v in headers
                            if k.lower() != b"content-length"
                        ]
                        headers.append((b"content-length", str(len(body)).encode()))

            start_message["headers"] = headers
            await send(start_message)
            await send({"type": "http.response.body", "body": body})

        await self.app(scope, receive, send_wrapper)


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
            "media videos and related public sources (YouTube, TikTok, Instagram, "
            "Facebook, and more). Connect via MCP (@captapi/mcp), CLI "
            "(@captapi/cli), n8n (n8n-nodes-captapi), Make.com, or the optional "
            "Apify Store client that calls this REST API with your Captapi key. "
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
        expose_headers=[
            "X-Captapi-Source",
            "X-Captapi-Credits",
            "X-Captapi-Cache",
        ],
    )
    # Stamps X-Captapi-Source/Credits/Cache onto every response (see class doc).
    app.add_middleware(BillingHeaderMiddleware)

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

    def _error_envelope(
        *,
        status_code: int,
        code: str,
        message: str,
        extra: dict | None = None,
        timings: dict | None = None,
    ) -> dict:
        """Catalogue-wide error body — same outer fields as success envelopes."""
        from app.core.credits import request_meta

        meta = request_meta.get() or {}
        error_obj: dict = {"code": code, "message": message}
        if extra:
            for key, value in extra.items():
                if key in ("code", "message", "timings") or value is None:
                    continue
                error_obj[key] = value
        body: dict = {
            "success": False,
            "error": error_obj,
            "creditsUsed": int(meta.get("credits") or 0),
            "requestId": meta.get("request_id") or None,
            "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        # Stage timings sit beside error (MS1) — not buried inside error{}.
        if timings:
            body["timings"] = timings
        elif isinstance(extra, dict) and isinstance(extra.get("timings"), dict):
            body["timings"] = extra["timings"]
        return body

    _STATUS_ERROR_CODES = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        502: "UPSTREAM_UNAVAILABLE",
        503: "SERVICE_UNAVAILABLE",
        504: "UPSTREAM_TIMEOUT",
    }

    def _http_exception_parts(
        exc: StarletteHTTPException,
    ) -> tuple[str, str, dict, dict | None]:
        detail = exc.detail
        timings: dict | None = None
        if isinstance(detail, dict) and isinstance(detail.get("timings"), dict):
            timings = detail["timings"]
        if isinstance(detail, dict):
            nested = detail.get("error")
            if isinstance(nested, dict) and nested.get("code"):
                code = str(nested["code"])
                message = str(
                    detail.get("message")
                    or nested.get("message")
                    or nested.get("reason")
                    or code
                )
                extra = {k: v for k, v in nested.items() if k not in ("code", "message")}
                if timings is None and isinstance(nested.get("timings"), dict):
                    timings = nested["timings"]
                return code, message, extra, timings
            if detail.get("code") and (detail.get("message") or detail.get("detail")):
                code = str(detail["code"])
                message = str(detail.get("message") or detail.get("detail") or code)
                extra = {
                    k: v
                    for k, v in detail.items()
                    if k not in ("code", "message", "detail", "error", "timings")
                }
                return code, message, extra, timings
            # Opaque structured detail — stringify for message, keep as extras.
            code = _STATUS_ERROR_CODES.get(exc.status_code, "HTTP_ERROR")
            return (
                code,
                str(detail.get("message") or detail),
                {k: v for k, v in detail.items() if k not in ("message", "timings")},
                timings,
            )
        if isinstance(detail, str) and detail.strip():
            code = _STATUS_ERROR_CODES.get(exc.status_code, "HTTP_ERROR")
            return code, detail, {}, None
        code = _STATUS_ERROR_CODES.get(exc.status_code, "HTTP_ERROR")
        return code, code.replace("_", " ").title(), {}, None

    @app.exception_handler(StarletteHTTPException)
    @app.exception_handler(HTTPException)
    async def http_exception_envelope(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        # HTTPException used to return raw {"detail": "..."} — a second contract
        # from ApiResponse. Wrap every raised HTTP error in the catalogue envelope.
        code, message, extra, timings = _http_exception_parts(exc)
        headers = _error_cors_headers(request)
        if getattr(exc, "headers", None):
            headers = {**headers, **dict(exc.headers)}
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(
                status_code=exc.status_code,
                code=code,
                message=message,
                extra=extra or None,
                timings=timings,
            ),
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_envelope(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Default FastAPI shape is {"detail": [...]} — same second contract (MP2).
        return JSONResponse(
            status_code=422,
            content=_error_envelope(
                status_code=422,
                code="VALIDATION_ERROR",
                message="Request validation failed",
                extra={"issues": exc.errors()},
            ),
            headers=_error_cors_headers(request),
        )

    @app.exception_handler(ApifyError)
    async def upstream_actor_error(request: Request, exc: ApifyError) -> JSONResponse:
        # A third-party Apify actor failed (unrented/quota/timeout/upstream 4xx-5xx).
        # This is an upstream dependency failure, not a bug in our service, so it
        # must surface as 502 rather than falling through to the 500 catch-all.
        logger = structlog.get_logger()
        logger.warning("apify_actor_error", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=502,
            content=_error_envelope(
                status_code=502,
                code="UPSTREAM_UNAVAILABLE",
                message=str(exc) or "Upstream actor error",
                extra={"reason": "upstream_actor_error"},
            ),
            headers=_error_cors_headers(request),
        )

    from postgrest.exceptions import APIError as PostgrestAPIError

    @app.exception_handler(PostgrestAPIError)
    async def postgrest_error(request: Request, exc: PostgrestAPIError) -> JSONResponse:
        # 42P01 = relation does not exist, PGRST205 = table missing from the
        # PostgREST schema cache: a feature table (monitors, metric_history,
        # ...) whose migration has not been applied yet.
        if getattr(exc, "code", "") in ("42P01", "PGRST205"):
            return JSONResponse(
                status_code=503,
                content=_error_envelope(
                    status_code=503,
                    code="NOT_PROVISIONED",
                    message=(
                        "A required database table is missing. Apply the latest "
                        "files in supabase/migrations/ to enable this feature."
                    ),
                ),
                headers=_error_cors_headers(request),
            )
        sentry_sdk.capture_exception(exc)
        structlog.get_logger().exception("postgrest_error", error=str(exc))
        return JSONResponse(
            status_code=500,
            content=_error_envelope(
                status_code=500,
                code="INTERNAL_SERVER_ERROR",
                message="Internal server error",
            ),
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
            content=_error_envelope(
                status_code=500,
                code="INTERNAL_SERVER_ERROR",
                message="Internal server error",
            ),
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
    app.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])
    app.include_router(video.router, prefix="/v1/video", tags=["Video Files"])
    app.include_router(account.router, prefix="/v1/account", tags=["Account"])
    app.include_router(auth_keys.router, prefix="/v1/auth/keys", tags=["API Keys"])
    app.include_router(billing.router, prefix="/v1/billing", tags=["Billing"])
    app.include_router(monitors.router, prefix="/v1/monitors", tags=["Monitors"])
    app.include_router(history.router, prefix="/v1/history", tags=["History"])
    app.include_router(batch.router, prefix="/v1/batch", tags=["Batch"])
    app.include_router(status.router, prefix="/v1/status", tags=["Status"])
    app.include_router(mcp.router, prefix="/mcp", tags=["MCP"], include_in_schema=False)

    @app.on_event("startup")
    async def start_monitor_loop() -> None:
        from app.services.monitor_runner import monitor_loop

        app.state.monitor_task = asyncio.create_task(monitor_loop(app))

    @app.on_event("shutdown")
    async def stop_monitor_loop() -> None:
        task = getattr(app.state, "monitor_task", None)
        if task is not None:
            task.cancel()

    return app


app = create_app()
