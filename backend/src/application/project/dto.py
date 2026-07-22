from __future__ import annotations

from dataclasses import dataclass

from application.audit.dto import AuditContext
from domain.project.entities import Project


@dataclass(frozen=True, slots=True)
class CreateProjectRequest:
    vault_id: str
    name: str
    description: str | None = None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ListProjectsRequest:
    vault_id: str
    page: int = 1
    page_size: int = 20
    search: str | None = None
    status: str | None = None
    archived: bool | None = None


@dataclass(frozen=True, slots=True)
class GetProjectRequest:
    project_id: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class UpdateProjectRequest:
    project_id: str
    name: str
    description: str | None = None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ArchiveProjectRequest:
    project_id: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ProjectResponse:
    id: str
    vault_id: str
    name: str
    description: str | None = None
    archived: bool = False
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""
    archived_at: str | None = None

    @classmethod
    def from_domain(cls, project: Project) -> ProjectResponse:
        status = "archived" if project.archived else "active"
        return cls(
            id=str(project.id),
            vault_id=str(project.vault_id),
            name=project.name.value,
            description=project.description.value,
            archived=project.archived,
            status=status,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat(),
            archived_at=project.archived_at.isoformat() if project.archived_at else None,
        )


@dataclass(frozen=True, slots=True)
class ProjectPermissionsResponse:
    create: bool
    read: bool
    update: bool
    archive: bool


@dataclass(frozen=True, slots=True)
class PaginationResponse:
    page: int
    page_size: int
    total: int
    has_next_page: bool
    has_previous_page: bool


@dataclass(frozen=True, slots=True)
class ProjectListResponse:
    data: tuple[ProjectResponse, ...]
    pagination: PaginationResponse
    permissions: ProjectPermissionsResponse
