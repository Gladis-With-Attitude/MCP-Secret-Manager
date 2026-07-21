from __future__ import annotations

from dataclasses import dataclass

from application.audit.dto import AuditContext
from domain.project.entities import Project


@dataclass(frozen=True, slots=True)
class CreateProjectRequest:
    vault_id: str
    name: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ProjectResponse:
    id: str
    vault_id: str
    name: str

    @classmethod
    def from_domain(cls, project: Project) -> ProjectResponse:
        return cls(id=str(project.id), vault_id=str(project.vault_id), name=project.name.value)
