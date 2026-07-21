from __future__ import annotations

import anyio
from httpx import ASGITransport, AsyncClient, Response

from presentation.rest.app import create_app


async def fetch_health_response() -> Response:
    transport = ASGITransport(app=create_app(service_name="test-service"))

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get("/v1/health")


def test_health_endpoint_returns_minimal_liveness_payload() -> None:
    response = anyio.run(fetch_health_response)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "test-service",
    }
