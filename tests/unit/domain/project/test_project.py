from __future__ import annotations

from domain.project.entities import Project
from domain.project.value_objects import ProjectId, ProjectName
from domain.vault.value_objects import VaultId


def test_project_create_assigns_id_vault_and_name() -> None:
    vault_id = VaultId.new()
    name = ProjectName("API")

    project = Project.create(vault_id=vault_id, name=name)

    assert isinstance(project.id, ProjectId)
    assert project.vault_id == vault_id
    assert project.name == name


def test_projects_are_equal_when_their_ids_are_equal() -> None:
    project_id = ProjectId.new()
    first = Project(id=project_id, vault_id=VaultId.new(), name=ProjectName("API"))
    second = Project(id=project_id, vault_id=VaultId.new(), name=ProjectName("Worker"))

    assert first == second
    assert hash(first) == hash(second)


def test_projects_are_different_when_their_ids_are_different() -> None:
    vault_id = VaultId.new()
    first = Project.create(vault_id=vault_id, name=ProjectName("API"))
    second = Project.create(vault_id=vault_id, name=ProjectName("API"))

    assert first != second
