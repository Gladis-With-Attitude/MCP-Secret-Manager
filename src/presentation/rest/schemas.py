from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from application.project.dto import ProjectResponse
from application.vault.dto import VaultResponse


class CreateVaultHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class VaultHttpResponse(BaseModel):
    id: str
    name: str

    @classmethod
    def from_application(cls, response: VaultResponse) -> VaultHttpResponse:
        return cls(id=response.id, name=response.name)


class CreateProjectHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class ProjectHttpResponse(BaseModel):
    id: str
    vault_id: str
    name: str

    @classmethod
    def from_application(cls, response: ProjectResponse) -> ProjectHttpResponse:
        return cls(id=response.id, vault_id=response.vault_id, name=response.name)
