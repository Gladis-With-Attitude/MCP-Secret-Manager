from __future__ import annotations

from infrastructure.tracing import safe_http_server_span_attributes


def test_safe_http_server_span_attributes_are_allowlisted() -> None:
    attributes = safe_http_server_span_attributes(
        method="GET",
        route_path="/v1/secrets/{secret_id}",
        status_code=200,
        request_id="req-123",
    )

    assert attributes == {
        "http.request.method": "GET",
        "http.route": "/v1/secrets/{secret_id}",
        "http.response.status_code": 200,
        "request.id": "req-123",
    }
