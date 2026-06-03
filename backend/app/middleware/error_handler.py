import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.i18n import _
from app.core.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            locale = getattr(request.state, "locale", "en")
            logger.exception(
                "Unhandled exception",
                request_id=request_id,
                method=request.method,
                path=str(request.url.path),
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": _("An internal server error occurred.", locale),
                    "request_id": request_id,
                    "error_type": type(exc).__name__,
                },
                headers={
                    "X-Request-ID": request_id,
                    "Content-Language": locale,
                },
            )
