from __future__ import annotations

import json
import logging

from infrastructure.logging import (
    REDACTED_VALUE,
    JsonLogFormatter,
    redact_mapping,
    safe_log_extra,
)


def test_redact_mapping_removes_sensitive_values() -> None:
    redacted = redact_mapping(
        {
            "api_key": "credential-material",
            "nested": {
                "password": "password-material",
                "secret_key_configured": True,
                "safe": "visible",
            },
            "items": [{"token": "token-material"}],
        }
    )

    assert redacted == {
        "api_key": REDACTED_VALUE,
        "nested": {
            "password": REDACTED_VALUE,
            "secret_key_configured": True,
            "safe": "visible",
        },
        "items": [{"token": REDACTED_VALUE}],
    }


def test_json_log_formatter_includes_redacted_structured_fields() -> None:
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Created API key.",
        args=(),
        exc_info=None,
    )
    for key, value in safe_log_extra(
        event="api_key_created",
        request_id="req-1",
        api_key="credential-material",
    ).items():
        setattr(record, key, value)

    payload = json.loads(JsonLogFormatter().format(record))

    assert payload["event"] == "api_key_created"
    assert payload["request_id"] == "req-1"
    assert payload["api_key"] == REDACTED_VALUE
    assert "credential-material" not in json.dumps(payload)
