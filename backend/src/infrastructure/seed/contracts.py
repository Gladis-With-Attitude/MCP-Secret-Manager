from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.seed.settings import SeedSettings


@dataclass(frozen=True, slots=True)
class SeedContext:
    session: AsyncSession
    settings: SeedSettings


class SystemSeed(Protocol):
    name: str

    async def run(self, context: SeedContext) -> None:
        """Run an idempotent system seed."""
