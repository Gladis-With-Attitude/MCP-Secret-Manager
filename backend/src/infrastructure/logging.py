from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from typing import Any

REDACTED_VALUE = "[REDACTED]"
SENSITIVE_FIELD_MARKERS = (
    "authorization",
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "master_key",
    "raw_value",
)
SAFE_SENSITIVE_METADATA_SUFFIXES = ("_configured", "_bytes", "_count")

_request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


def bind_request_id(request_id: str) -> Token[str | None]:
    return _request_id_context.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    _request_id_context.reset(token)


def current_request_id() -> str | None:
    return _request_id_context.get()


def redact_mapping(fields: Mapping[str, object]) -> dict[str, object]:
    return {key: _redact_value(key, value) for key, value in fields.items()}


def safe_log_extra(**fields: object) -> dict[str, object]:
    return {"event_fields": redact_mapping(fields)}


def configure_runtime_logging(level: str, *, json_enabled: bool = False) -> None:
    handler = logging.StreamHandler()
    if json_enabled:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            KeyValueLogFormatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(_record_event_fields(record))

        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


class KeyValueLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        fields = _record_event_fields(record)
        if not fields:
            return rendered

        suffix = " ".join(
            f"{key}={value}" for key, value in sorted(fields.items(), key=lambda item: item[0])
        )
        return f"{rendered} {suffix}"


def _record_event_fields(record: logging.LogRecord) -> dict[str, object]:
    fields: dict[str, object] = {}
    request_id = current_request_id()
    if request_id is not None:
        fields["request_id"] = request_id
    fields.update(_current_trace_fields())

    event_fields = getattr(record, "event_fields", None)
    if isinstance(event_fields, Mapping):
        fields.update(redact_mapping(_string_key_mapping(event_fields)))

    return fields


def _string_key_mapping(fields: Mapping[Any, Any]) -> dict[str, object]:
    return {str(key): value for key, value in fields.items()}


def _current_trace_fields() -> dict[str, object]:
    try:
        from infrastructure.tracing import current_trace_log_fields
    except ModuleNotFoundError:
        return {}

    return current_trace_log_fields()


def _redact_value(key: str, value: object) -> object:
    normalized_key = key.lower()
    has_sensitive_marker = any(marker in normalized_key for marker in SENSITIVE_FIELD_MARKERS)
    is_safe_metadata = normalized_key.endswith(SAFE_SENSITIVE_METADATA_SUFFIXES)
    if has_sensitive_marker and not is_safe_metadata:
        return REDACTED_VALUE
    if isinstance(value, Mapping):
        return redact_mapping(_string_key_mapping(value))
    if isinstance(value, list):
        return [_redact_nested_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_nested_value(item) for item in value)
    return value


def _redact_nested_value(value: object) -> object:
    if isinstance(value, Mapping):
        return redact_mapping(_string_key_mapping(value))
    if isinstance(value, list):
        return [_redact_nested_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_nested_value(item) for item in value)
    return value
