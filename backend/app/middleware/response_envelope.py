"""Response envelope middleware.

Wraps every successful (2xx) JSON response body in the envelope

    {
        "data":    <original body>,
        "success": true,
        "message": null
    }

so the frontend can rely on a single response shape. Errors (4xx / 5xx),
non-JSON content (e.g. file downloads, SSE, plain text health checks),
and 204 No Content responses are passed through untouched.

The wrapper is idempotent: if a downstream handler already returned the
envelope (e.g. a manually-constructed `ApiResponse(...)`), we don't
double-wrap.
"""

from __future__ import annotations

import json
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Only wrap 2xx responses with a JSON body.
        if response.status_code < 200 or response.status_code >= 300:
            return response
        if response.status_code == 204:
            return response

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return response

        # Read the full body (BaseHTTPMiddleware already consumes the upstream
        # body iterator, so we can read once and rebuild a fresh response).
        body = b""
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                body += chunk.encode("utf-8")
            else:
                body += chunk

        if not body:
            return response

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            # Body wasn't valid JSON; pass through unchanged.
            return Response(
                content=body,
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items() if k.lower() != "content-length"},
                media_type=content_type or "application/json",
            )

        # Idempotency: don't double-wrap a response that's already an envelope.
        if (
            isinstance(data, dict)
            and set(data.keys()) >= {"data", "success"}
            and isinstance(data.get("success"), bool)
        ):
            return JSONResponse(
                content=data,
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items() if k.lower() != "content-length"},
            )

        envelope = {"data": data, "success": True, "message": None}
        return JSONResponse(
            content=envelope,
            status_code=response.status_code,
            headers={k: v for k, v in response.headers.items() if k.lower() != "content-length"},
        )
