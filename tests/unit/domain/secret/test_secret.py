from __future__ import annotations

from domain.project.value_objects import ProjectId
from domain.secret.entities import Secret
from domain.secret.value_objects import SecretDescription, SecretId, SecretKey


def test_secret_create_assigns_id_project_key_and_description() -> None:
    project_id = ProjectId.new()
    key = SecretKey("OPENAI_API_KEY")
    description = SecretDescription("OpenAI API token metadata.")

    secret = Secret.create(project_id=project_id, key=key, description=description)

    assert isinstance(secret.id, SecretId)
    assert secret.project_id == project_id
    assert secret.key == key
    assert secret.description == description


def test_secrets_are_equal_when_their_ids_are_equal() -> None:
    secret_id = SecretId.new()
    first = Secret(
        id=secret_id,
        project_id=ProjectId.new(),
        key=SecretKey("OPENAI_API_KEY"),
        description=SecretDescription(None),
    )
    second = Secret(
        id=secret_id,
        project_id=ProjectId.new(),
        key=SecretKey("DATABASE_URL"),
        description=SecretDescription("Different metadata."),
    )

    assert first == second
    assert hash(first) == hash(second)


def test_secrets_are_different_when_their_ids_are_different() -> None:
    project_id = ProjectId.new()
    first = Secret.create(
        project_id=project_id,
        key=SecretKey("OPENAI_API_KEY"),
        description=SecretDescription(None),
    )
    second = Secret.create(
        project_id=project_id,
        key=SecretKey("OPENAI_API_KEY"),
        description=SecretDescription(None),
    )

    assert first != second
