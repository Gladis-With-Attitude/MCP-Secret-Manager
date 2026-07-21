from __future__ import annotations

from typing import Protocol


class ApiKeyHasher(Protocol):
    def hash(self, api_key: str) -> str:
        raise NotImplementedError

    def verify(self, api_key: str, hashed_key: str) -> bool:
        raise NotImplementedError


class ApiKeySecretGenerator(Protocol):
    def generate(self) -> str:
        raise NotImplementedError

    def extract_prefix(self, api_key: str) -> str | None:
        raise NotImplementedError
