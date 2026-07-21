from __future__ import annotations

import pytest

from domain.project.exceptions import ProjectNameError
from domain.project.value_objects import ProjectName


def test_project_name_trims_surrounding_spaces() -> None:
    name = ProjectName("  API  ")

    assert name.value == "API"


def test_project_name_rejects_empty_value() -> None:
    with pytest.raises(ProjectNameError, match="required"):
        ProjectName("   ")


def test_project_name_rejects_values_shorter_than_three_characters() -> None:
    with pytest.raises(ProjectNameError, match="at least 3"):
        ProjectName("ab")


def test_project_name_rejects_values_longer_than_one_hundred_characters() -> None:
    with pytest.raises(ProjectNameError, match="at most 100"):
        ProjectName("a" * 101)


def test_project_name_accepts_boundary_lengths() -> None:
    assert ProjectName("abc").value == "abc"
    assert ProjectName("a" * 100).value == "a" * 100
