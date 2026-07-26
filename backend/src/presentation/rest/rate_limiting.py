from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import ceil
from threading import Lock
from time import monotonic

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from infrastructure.configuration.models import RateLimitConfig

DEFAULT_RATE_LIMIT = RateLimitConfig(
    enabled=True,
    requests=120,
    window_seconds=60,
    exempt_paths=("/v1/health", "/v1/metrics"),
    max_clients=10000,
)
UNKNOWN_CLIENT = "unknown"


@dataclass(frozen=True, slots=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_seconds: int
    retry_after_seconds: int | None = None


@dataclass(slots=True)
class _ClientWindow:
    started_at: float
    request_count: int
    last_seen_at: float


class FixedWindowRateLimiter:
    def __init__(
        self,
        config: RateLimitConfig = DEFAULT_RATE_LIMIT,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._config = config
        self._clock = clock
        self._lock = Lock()
        self._windows: dict[str, _ClientWindow] = {}

    def check(self, client_id: str) -> RateLimitResult:
        now = self._clock()
        with self._lock:
            window = self._windows.get(client_id)
            if window is None or now - window.started_at >= self._config.window_seconds:
                self._prune_locked(now)
                self._windows[client_id] = _ClientWindow(
                    started_at=now,
                    request_count=1,
                    last_seen_at=now,
                )
                return RateLimitResult(
                    allowed=True,
                    limit=self._config.requests,
                    remaining=self._config.requests - 1,
                    reset_seconds=self._config.window_seconds,
                )

            window.last_seen_at = now
            reset_seconds = max(1, ceil(self._config.window_seconds - (now - window.started_at)))
            if window.request_count >= self._config.requests:
                return RateLimitResult(
                    allowed=False,
                    limit=self._config.requests,
                    remaining=0,
                    reset_seconds=reset_seconds,
                    retry_after_seconds=reset_seconds,
                )

            window.request_count += 1
            return RateLimitResult(
                allowed=True,
                limit=self._config.requests,
                remaining=self._config.requests - window.request_count,
                reset_seconds=reset_seconds,
            )

    def _prune_locked(self, now: float) -> None:
        if len(self._windows) < self._config.max_clients:
            return

        expired_before = now - self._config.window_seconds
        expired_client_ids = [
            client_id
            for client_id, window in self._windows.items()
            if window.last_seen_at <= expired_before
        ]
        for client_id in expired_client_ids:
            del self._windows[client_id]

        if len(self._windows) < self._config.max_clients:
            return

        oldest_client_id = min(
            self._windows,
            key=lambda client_id: self._windows[client_id].last_seen_at,
        )
        del self._windows[oldest_client_id]


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        config: RateLimitConfig = DEFAULT_RATE_LIMIT,
        limiter: FixedWindowRateLimiter | None = None,
    ) -> None:
        super().__init__(app)
        self._config = config
        self._exempt_paths = frozenset(config.exempt_paths)
        self._limiter = limiter or FixedWindowRateLimiter(config)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if not self._config.enabled or request.url.path in self._exempt_paths:
            return await call_next(request)

        result = self._limiter.check(_client_id(request))
        if not result.allowed:
            response: Response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded."},
            )
            _apply_rate_limit_headers(response, result)
            return response

        response = await call_next(request)
        _apply_rate_limit_headers(response, result)
        return response


def _client_id(request: Request) -> str:
    if request.client is None or request.client.host is None:
        return UNKNOWN_CLIENT
    return request.client.host


def _apply_rate_limit_headers(response: Response, result: RateLimitResult) -> None:
    response.headers["RateLimit-Limit"] = str(result.limit)
    response.headers["RateLimit-Remaining"] = str(result.remaining)
    response.headers["RateLimit-Reset"] = str(result.reset_seconds)
    if result.retry_after_seconds is not None:
        response.headers["Retry-After"] = str(result.retry_after_seconds)
