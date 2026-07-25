from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from infrastructure.configuration.models import OpenTelemetryConfig
from infrastructure.logging import safe_log_extra

if TYPE_CHECKING:
    from fastapi import Request

logger = logging.getLogger(__name__)

_TRACING_CONFIGURED = False


def configure_opentelemetry_tracing(
    config: OpenTelemetryConfig,
    *,
    service_name: str,
    environment: str,
    service_version: str,
) -> bool:
    if not config.traces_enabled:
        return False

    modules = _load_opentelemetry_sdk()
    if modules is None:
        logger.warning(
            "OpenTelemetry tracing requested but dependencies are unavailable.",
            extra=safe_log_extra(event="opentelemetry_tracing_unavailable"),
        )
        return False

    global _TRACING_CONFIGURED
    if _TRACING_CONFIGURED:
        return True

    trace_api = modules["trace_api"]
    resource_class = modules["resource_class"]
    tracer_provider_class = modules["tracer_provider_class"]
    batch_span_processor_class = modules["batch_span_processor_class"]
    otlp_span_exporter_class = modules["otlp_span_exporter_class"]

    exporter_kwargs: dict[str, object] = {}
    if config.exporter_otlp_endpoint is not None:
        exporter_kwargs["endpoint"] = config.exporter_otlp_endpoint

    provider = tracer_provider_class(
        resource=resource_class.create(
            {
                "service.name": service_name,
                "service.version": service_version,
                "deployment.environment.name": environment,
            }
        )
    )
    provider.add_span_processor(
        batch_span_processor_class(otlp_span_exporter_class(**exporter_kwargs))
    )
    trace_api.set_tracer_provider(provider)
    _TRACING_CONFIGURED = True

    logger.info(
        "OpenTelemetry tracing configured.",
        extra=safe_log_extra(
            event="opentelemetry_tracing_configured",
            exporter_otlp_endpoint_configured=config.exporter_otlp_endpoint is not None,
        ),
    )
    return True


def opentelemetry_api_available() -> bool:
    return _load_opentelemetry_api() is not None


class OpenTelemetryTracingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._tracer_name = "mcp-secret-manager.fastapi"

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        modules = _load_opentelemetry_api()
        if modules is None:
            return await call_next(request)

        trace_api = modules["trace_api"]
        propagate = modules["propagate"]
        span_kind = modules["span_kind"]
        status_class = modules["status_class"]
        status_code_class = modules["status_code_class"]

        parent_context = propagate.extract(_safe_trace_context_headers(request.headers))
        tracer = trace_api.get_tracer(self._tracer_name)

        with tracer.start_as_current_span(
            "HTTP request",
            context=parent_context,
            kind=span_kind.SERVER,
        ) as span:
            try:
                response = await call_next(request)
            except Exception as exc:
                annotate_http_server_span(
                    span,
                    method=request.method,
                    route_path=safe_route_path(request),
                    status_code=500,
                    request_id=_request_id_from_state(request),
                )
                span.record_exception(exc)
                span.set_status(status_class(status_code_class.ERROR))
                raise

            annotate_http_server_span(
                span,
                method=request.method,
                route_path=safe_route_path(request),
                status_code=response.status_code,
                request_id=_request_id_from_state(request),
            )
            return response


def annotate_current_trace_request_id(request_id: str) -> None:
    modules = _load_opentelemetry_api()
    if modules is None:
        return

    span = modules["trace_api"].get_current_span()
    span_context = span.get_span_context()
    if span_context.is_valid:
        span.set_attribute("request.id", request_id)


def annotate_http_server_span(
    span: Any,
    *,
    method: str,
    route_path: str,
    status_code: int,
    request_id: str | None,
) -> None:
    attributes = safe_http_server_span_attributes(
        method=method,
        route_path=route_path,
        status_code=status_code,
        request_id=request_id,
    )
    for key, value in attributes.items():
        span.set_attribute(key, value)
    span.update_name(f"{method} {route_path}")


def safe_http_server_span_attributes(
    *,
    method: str,
    route_path: str,
    status_code: int,
    request_id: str | None,
) -> dict[str, str | int]:
    attributes: dict[str, str | int] = {
        "http.request.method": method,
        "http.route": route_path,
        "http.response.status_code": status_code,
    }
    if request_id is not None:
        attributes["request.id"] = request_id
    return attributes


def current_trace_log_fields() -> dict[str, object]:
    modules = _load_opentelemetry_api()
    if modules is None:
        return {}

    span = modules["trace_api"].get_current_span()
    span_context = span.get_span_context()
    if not span_context.is_valid:
        return {}

    return {
        "trace_id": f"{span_context.trace_id:032x}",
        "span_id": f"{span_context.span_id:016x}",
    }


def safe_route_path(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if isinstance(path, str):
        return path
    return "unmatched_route"


def _request_id_from_state(request: Request) -> str | None:
    request_id = getattr(request.state, "request_id", None)
    return request_id if isinstance(request_id, str) else None


def _safe_trace_context_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value for key, value in headers.items() if key.lower() in {"traceparent", "tracestate"}
    }


def _load_opentelemetry_api() -> dict[str, Any] | None:
    try:
        from opentelemetry import propagate
        from opentelemetry import trace as trace_api
        from opentelemetry.trace import SpanKind
        from opentelemetry.trace.status import Status, StatusCode
    except ModuleNotFoundError:
        return None

    return {
        "propagate": propagate,
        "trace_api": trace_api,
        "span_kind": SpanKind,
        "status_class": Status,
        "status_code_class": StatusCode,
    }


def _load_opentelemetry_sdk() -> dict[str, Any] | None:
    try:
        from opentelemetry import trace as trace_api
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ModuleNotFoundError:
        return None

    return {
        "trace_api": trace_api,
        "resource_class": Resource,
        "tracer_provider_class": TracerProvider,
        "batch_span_processor_class": BatchSpanProcessor,
        "otlp_span_exporter_class": OTLPSpanExporter,
    }
