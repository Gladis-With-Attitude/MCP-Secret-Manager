from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class HealthStatus:
    status: Literal["degraded", "ok"]
    service: str
    api: Literal["ok"]
    configuration: Literal["invalid", "ok"]
    database: Literal["not_configured", "ok", "unavailable"]
    repositories: Literal["not_configured", "ok"]
    use_cases: Literal["not_configured", "ok"]

    def as_public_dict(self) -> dict[str, str]:
        return {
            "status": self.status,
            "service": self.service,
            "api": self.api,
            "configuration": self.configuration,
            "database": self.database,
            "repositories": self.repositories,
            "use_cases": self.use_cases,
        }


def get_liveness_status(service_name: str) -> HealthStatus:
    return HealthStatus(
        status="ok",
        service=service_name,
        api="ok",
        configuration="ok",
        database="not_configured",
        repositories="not_configured",
        use_cases="not_configured",
    )
