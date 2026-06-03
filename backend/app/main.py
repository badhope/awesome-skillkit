from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.i18n import compile_catalogs
from app.core.logging import get_logger
from app.core.seed import seed_initial_data
from app.db import async_session_factory, engine
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.locale import LocaleMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.response_envelope import ResponseEnvelopeMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

settings = get_settings()
logger = get_logger(__name__)

_resource = Resource(attributes={SERVICE_NAME: settings.APP_NAME})
_tracer_provider = TracerProvider(resource=_resource)
trace.set_tracer_provider(_tracer_provider)

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        environment="development" if settings.DEBUG else "production",
        release=settings.APP_VERSION,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application", app_name=settings.APP_NAME, version=settings.APP_VERSION)
    # Compile any .po -> .mo catalogs on startup so a fresh checkout
    # (or a freshly-pulled Docker image) can serve localized errors
    # without a separate build step. msgfmt is a hard requirement; if
    # it's missing, fail fast with a clear error.
    try:
        n = compile_catalogs()
        if n:
            logger.info("Compiled i18n catalogs", count=n)
    except Exception as e:
        logger.error("Failed to compile i18n catalogs", error=str(e))
        raise
    try:
        async with engine.begin():
            logger.info("Database connection established")
    except Exception as e:
        logger.error("Failed to connect to database", error=str(e))
        raise
    try:
        async with async_session_factory() as db:
            await seed_initial_data(db)
    except Exception as e:
        # Seeding is best-effort — if it fails we still want the API to
        # come up so an operator can debug from inside. (We do log loudly.)
        # One day we'll make this a startup gate for production but not
        # until we have proper pre-deployment migration runs.
        logger.error("Failed to seed initial data, continuing startup", error=str(e))
    yield
    logger.info("Shutting down application")
    await engine.dispose()
    logger.info("Database connections disposed")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

if settings.BACKEND_CORS_ORIGINS:
    # CORS is intentionally the LAST `add_middleware` call so it is the
    # outermost layer in the Starlette stack. That means OPTIONS preflight
    # is answered before rate-limit, envelope wrapping, or error handler
    # can short-circuit it. Middleware order in Starlette is reverse-of-
    # registration (the last add wraps the previous ones).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "Accept",
            "Origin",
            "User-Agent",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        max_age=600,
    )

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LocaleMiddleware)
# Envelope wrapper runs as the second-outermost layer so it sees the
# response body after the locale tag has done its work.
app.add_middleware(ResponseEnvelopeMiddleware)

FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_PREFIX,
        "docs": "/docs" if settings.DEBUG else None,
        "environment": "development" if settings.DEBUG else "production",
    }
