import time
from typing import Callable, Dict, Optional, Tuple

from fastapi import Request, Response
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.config import get_settings

settings = get_settings()

DEFAULT_RATE_LIMIT = settings.RATE_LIMIT_DEFAULT
DEFAULT_RATE_WINDOW = settings.RATE_LIMIT_WINDOW

ENDPOINT_RATE_LIMITS: Dict[str, Tuple[int, int]] = {
    "POST /api/v1/auth/login": (5, 60),
    "POST /api/v1/auth/register": (3, 60),
    "POST /api/v1/auth/refresh": (10, 60),
    "GET /api/v1/skills/search": (30, 60),
    "POST /api/v1/skills": (10, 60),
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        redis_client: Optional[Redis] = None,
        default_limit: int = DEFAULT_RATE_LIMIT,
        default_window: int = DEFAULT_RATE_WINDOW,
    ):
        super().__init__(app)
        self._redis = redis_client
        self.default_limit = default_limit
        self.default_window = default_window

    async def _get_redis(self) -> Optional[Redis]:
        if self._redis is not None:
            return self._redis
        try:
            self._redis = Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        except Exception:
            self._redis = None
        return self._redis

    def _get_route_key(self, request: Request) -> str:
        method = request.method
        path = request.url.path

        for route in request.app.routes:
            if hasattr(route, "path_regex") and route.path_regex.match(path):
                path = route.path
                break

        return f"{method} {path}"

    def _get_limit_and_window(self, route_key: str) -> Tuple[int, int]:
        for pattern, (limit, window) in ENDPOINT_RATE_LIMITS.items():
            if self._match_route(route_key, pattern):
                return limit, window
        return self.default_limit, self.default_window

    def _match_route(self, route_key: str, pattern: str) -> bool:
        route_method, route_path = route_key.split(" ", 1)
        pattern_method, pattern_path = pattern.split(" ", 1)

        if route_method != pattern_method:
            return False

        route_parts = route_path.strip("/").split("/")
        pattern_parts = pattern_path.strip("/").split("/")

        if len(route_parts) != len(pattern_parts):
            return False

        for rp, pp in zip(route_parts, pattern_parts):
            if pp.startswith("{") and pp.endswith("}"):
                continue
            if rp != pp:
                return False

        return True

    def _get_client_key(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        return client_ip

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        route_key = self._get_route_key(request)
        client_key = self._get_client_key(request)
        limit, window = self._get_limit_and_window(route_key)

        redis = await self._get_redis()

        if redis is not None:
            rate_key = f"rate_limit:{client_key}:{route_key}"
            now = int(time.time())
            window_start = now - window

            pipe = redis.pipeline()
            pipe.zremrangebyscore(rate_key, 0, window_start)
            pipe.zcard(rate_key)
            pipe.zadd(rate_key, {str(now): now})
            pipe.expire(rate_key, window + 1)
            _, current_count, _, _ = await pipe.execute()

            if current_count and current_count >= limit:
                retry_after = window - (now - window_start)
                return Response(
                    content='{"detail":"Too many requests, please try again later."}',
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                    headers={
                        "Retry-After": str(max(1, retry_after)),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(now + window),
                    },
                )

            response = await call_next(request)
            remaining = max(0, limit - current_count - 1)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(now + window)
            return response

        return await call_next(request)