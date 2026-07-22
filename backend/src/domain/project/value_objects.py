from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.project.exceptions import ProjectDescriptionError, ProjectNameError


@dataclass(frozen=True, slots=True)
class ProjectId:
    value: UUID

    @classmethod
    def new(cls) -> ProjectId:
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> ProjectId:
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ProjectName:
    value: str

    MIN_LENGTH = 3
    MAX_LENGTH = 100

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        length = len(normalized)

        if length == 0:
            msg = "Project name is required."
            raise ProjectNameError(msg)

        if length < self.MIN_LENGTH:
            msg = f"Project name must contain at least {self.MIN_LENGTH} characters."
            raise ProjectNameError(msg)

        if length > self.MAX_LENGTH:
            msg = f"Project name must contain at most {self.MAX_LENGTH} characters."
            raise ProjectNameError(msg)

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ProjectDescription:
    value: str | None

    MAX_LENGTH = 280

    def __post_init__(self) -> None:
        if self.value is None:
            return

        normalized = self.value.strip()
        if not normalized:
            object.__setattr__(self, "value", None)
            return

        if len(normalized) > self.MAX_LENGTH:
            msg = f"Project description must contain at most {self.MAX_LENGTH} characters."
            raise ProjectDescriptionError(msg)

        object.__setattr__(self, "value", normalized)
