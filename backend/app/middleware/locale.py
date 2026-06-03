"""Resolve a request's locale and expose it on `request.state.locale`.

Order: `?lang=` → `X-Locale` → `Accept-Language` → `DEFAULT_LOCALE`.
Sets `Content-Language` and `Vary` so caches don't mix locales.
"""

from __future__ import annotations

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.i18n import resolve_locale


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Could short-circuit for /docs /openapi.json but the cost of
        # stamping Content-Language there is basically zero and starlette
        # strips the header on streaming responses anyway. Keep it simple.
        locale = resolve_locale(request)
        request.state.locale = locale
        response = await call_next(request)
        response.headers["Content-Language"] = locale

        # Shared caches must not serve one locale to a client asking for
        # another. `?lang=` is part of the URL so it keys naturally.
        vary = response.headers.get("Vary", "")
        parts = {p.strip().lower() for p in vary.split(",") if p.strip()}
        parts.update({"accept-language", "x-locale"})
        response.headers["Vary"] = ", ".join(sorted(parts))
        return response


def get_request_locale(request: Request) -> str:
    """FastAPI dep returning the resolved locale for a request."""
    return getattr(request.state, "locale", "en")
