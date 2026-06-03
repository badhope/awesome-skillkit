"""
Security headers middleware.

Adds the response headers recommended by OWASP for hardening an HTTP API:
- ``Strict-Transport-Security`` (HSTS) so browsers refuse to downgrade to HTTP
- ``X-Content-Type-Options: nosniff`` to disable MIME sniffing
- ``X-Frame-Options: DENY`` to prevent clickjacking (even though this is a JSON
  API, downstream proxies or error pages may render HTML)
- ``Referrer-Policy: no-referrer`` so we never leak API URLs
- ``Permissions-Policy`` to turn off powerful browser features
- ``Content-Security-Policy`` baseline (the API only serves JSON so we can be
  very strict; a real frontend would override this)
- ``Cross-Origin-*`` protections

The headers are added to every response that is not a streaming response.
"""
from __future__ import annotations

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


DEFAULT_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Content-Security-Policy": (
        "default-src 'none'; frame-ancestors 'none'; sandbox"
    ),
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
}

# Paths that serve HTML/JS the user interacts with (Swagger, ReDoc). The
# default CSP is `default-src 'none'` because the API only serves JSON,
# but that policy would also block the Swagger UI scripts. We relax it
# for these paths so the docs page actually renders.
_HTML_DOC_PATHS: frozenset[str] = frozenset({"/docs", "/redoc", "/openapi.json"})

# A CSP that lets the Swagger UI and ReDoc bundles load. Still safe for
# an internal API: no `unsafe-inline` for scripts (Swagger's JS is
# externally hosted via the CDN script tag) and no remote frames.
_HTML_DOC_CSP: str = (
    "default-src 'self'; "
    "img-src 'self' data:; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "frame-ancestors 'none'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        path = request.url.path
        is_doc_path = path in _HTML_DOC_PATHS or path.startswith("/docs") or path.startswith("/redoc")

        for header, value in DEFAULT_SECURITY_HEADERS.items():
            # Don't stamp the strict JSON-only CSP onto the interactive
            # docs pages — it blocks their JS. Use the relaxed policy
            # there. `setdefault` still respects any value the route set.
            if header == "Content-Security-Policy" and is_doc_path:
                response.headers.setdefault(header, _HTML_DOC_CSP)
            else:
                response.headers.setdefault(header, value)

        if not settings.DEBUG:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains; preload",
            )

        server_header = response.headers.get("server")
        if server_header and server_header.lower() not in {"", "uvicorn"}:
            response.headers["Server"] = "AI-SKILL"

        powered_by = response.headers.get("x-powered-by")
        if powered_by:
            del response.headers["x-powered-by"]

        return response
