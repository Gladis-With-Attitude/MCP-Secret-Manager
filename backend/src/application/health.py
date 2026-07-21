from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class HealthStatus:
    status: Literal["ok"]
    service: str

    def as_public_dict(self) -> dict[str, str]:
        return {
            "status": self.status,
            "service": self.service,
        }


def get_liveness_status(service_name: str) -> HealthStatus:
    return HealthStatus(status="ok", service=service_name)
