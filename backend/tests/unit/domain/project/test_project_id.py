from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from domain.project.value_objects import ProjectId


def test_project_id_generates_uuid() -> None:
    project_id = ProjectId.new()

    assert isinstance(project_id.value, UUID)


def test_project_id_can_be_created_from_string() -> None:
    value = "a99da5c2-4be3-4262-bb60-d6f360b6a8f6"

    project_id = ProjectId.from_string(value)

    assert str(project_id) == value


def test_project_id_is_immutable() -> None:
    project_id = ProjectId.new()

    with pytest.raises(FrozenInstanceError):
        project_id.__setattr__("value", UUID("a99da5c2-4be3-4262-bb60-d6f360b6a8f6"))
