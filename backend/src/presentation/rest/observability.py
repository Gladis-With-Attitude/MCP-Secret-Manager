from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from threading import Lock
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from infrastructure.logging import bind_request_id, reset_request_id, safe_log_extra

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:/=-]{1,128}$")

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class HttpMetricKey:
    method: str
    path: str
    status_code: int


class InMemoryHttpMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._request_totals: dict[HttpMetricKey, int] = {}
        self._duration_seconds_sum = 0.0

    def observe_request(
        self,
        *,
        method: str,
        path: str,
        status_code: int,
        duration_seconds: float,
    ) -> None:
        key = HttpMetricKey(method=method, path=path, status_code=status_code)
        with self._lock:
            self._request_totals[key] = self._request_totals.get(key, 0) + 1
            self._duration_seconds_sum += duration_seconds

    def render_prometheus(self) -> str:
        with self._lock:
            request_totals = dict(self._request_totals)
            duration_seconds_sum = self._duration_seconds_sum
            duration_seconds_count = sum(request_totals.values())

        lines = [
            "# HELP mcp_secret_manager_http_requests_total Total REST requests.",
            "# TYPE mcp_secret_manager_http_requests_total counter",
        ]
        for key, count in sorted(
            request_totals.items(),
            key=lambda item: (item[0].method, item[0].path, item[0].status_code),
        ):
            labels = _render_labels(
                {
                    "method": key.method,
                    "path": key.path,
                    "status": str(key.status_code),
                }
            )
            lines.append(f"mcp_secret_manager_http_requests_total{{{labels}}} {count}")

        lines.extend(
            [
                "# HELP mcp_secret_manager_http_request_duration_seconds "
                "REST request duration summary.",
                "# TYPE mcp_secret_manager_http_request_duration_seconds summary",
                f"mcp_secret_manager_http_request_duration_seconds_sum {duration_seconds_sum:.6f}",
                f"mcp_secret_manager_http_request_duration_seconds_count {duration_seconds_count}",
            ]
        )
        return "\n".join(lines) + "\n"


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        metrics: InMemoryHttpMetrics,
    ) -> None:
        super().__init__(app)
        self._metrics = metrics

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = get_or_create_request_id(request)
        token = bind_request_id(request_id)
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_seconds = perf_counter() - started_at
            path = _route_path(request)
            self._metrics.observe_request(
                method=request.method,
                path=path,
                status_code=500,
                duration_seconds=duration_seconds,
            )
            logger.exception(
                "HTTP request failed.",
                extra=safe_log_extra(
                    event="http_request_failed",
                    request_id=request_id,
                    http_method=request.method,
                    http_path=path,
                    http_status_code=500,
                    duration_ms=round(duration_seconds * 1000, 3),
                ),
            )
            reset_request_id(token)
            raise

        duration_seconds = perf_counter() - started_at
        path = _route_path(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        self._metrics.observe_request(
            method=request.method,
            path=path,
            status_code=response.status_code,
            duration_seconds=duration_seconds,
        )
        logger.info(
            "HTTP request completed.",
            extra=safe_log_extra(
                event="http_request_completed",
                request_id=request_id,
                http_method=request.method,
                http_path=path,
                http_status_code=response.status_code,
                duration_ms=round(duration_seconds * 1000, 3),
            ),
        )
        reset_request_id(token)
        return response


def get_or_create_request_id(request: Request) -> str:
    request_id = getattr(request.state, "request_id", None)
    if isinstance(request_id, str) and REQUEST_ID_PATTERN.fullmatch(request_id):
        return request_id

    header_value = request.headers.get(REQUEST_ID_HEADER)
    if header_value is not None:
        normalized_header_value = header_value.strip()
        if REQUEST_ID_PATTERN.fullmatch(normalized_header_value):
            request.state.request_id = normalized_header_value
            return normalized_header_value

    generated_request_id = str(uuid4())
    request.state.request_id = generated_request_id
    return generated_request_id


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if isinstance(path, str):
        return path
    return request.url.path


def _render_labels(labels: Mapping[str, str]) -> str:
    return ",".join(f'{key}="{_escape_label_value(value)}"' for key, value in labels.items())


def _escape_label_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
