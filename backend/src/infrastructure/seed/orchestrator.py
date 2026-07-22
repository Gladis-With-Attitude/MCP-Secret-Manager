from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.seed.contracts import SeedContext, SystemSeed
from infrastructure.seed.seeds import (
    AdminApiKeySeed,
    AdminSeed,
    PermissionsSeed,
    RolesSeed,
    ServiceAccountSeed,
)
from infrastructure.seed.settings import SeedSettings

logger = logging.getLogger(__name__)


class SeedRegistry:
    def __init__(self, seeds: Sequence[SystemSeed]) -> None:
        self._seeds = tuple(seeds)

    @classmethod
    def default(cls) -> SeedRegistry:
        return cls(
            (
                PermissionsSeed(),
                RolesSeed(),
                AdminSeed(),
                AdminApiKeySeed(),
                ServiceAccountSeed(),
            )
        )

    @property
    def seeds(self) -> tuple[SystemSeed, ...]:
        return self._seeds


class SeedOrchestrator:
    def __init__(
        self,
        session_factory: Callable[[], AbstractAsyncContextManager[AsyncSession]],
        registry: SeedRegistry | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._registry = registry or SeedRegistry.default()

    async def run(self, settings: SeedSettings) -> None:
        if not settings.enabled:
            logger.info("System bootstrap disabled")
            return

        async with self._session_factory() as session, session.begin():
            context = SeedContext(session=session, settings=settings)
            for seed in self._registry.seeds:
                logger.info("Running system seed: %s", seed.name)
                await seed.run(context)

        logger.info("✓ Bootstrap completed")
