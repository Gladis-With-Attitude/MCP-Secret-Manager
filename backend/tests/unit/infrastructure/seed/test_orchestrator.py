from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import cast

import anyio
from sqlalchemy.ext.asyncio import AsyncSession

from domain.identity.value_objects import UserDisplayName, UserEmail
from infrastructure.seed.contracts import SeedContext
from infrastructure.seed.orchestrator import SeedOrchestrator, SeedRegistry
from infrastructure.seed.settings import SeedSettings


class FakeTransaction:
    async def __aenter__(self) -> FakeTransaction:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> None:
        return None


class FakeSession:
    def begin(self) -> FakeTransaction:
        return FakeTransaction()


class FakeSessionContext:
    async def __aenter__(self) -> FakeSession:
        return FakeSession()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> None:
        return None


class FakeSessionFactory:
    def __call__(self) -> FakeSessionContext:
        return FakeSessionContext()


class FakeSeed:
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self._calls = calls

    async def run(self, _context: SeedContext) -> None:
        self._calls.append(self.name)


def fake_session_factory() -> Callable[[], AbstractAsyncContextManager[AsyncSession]]:
    return cast(Callable[[], AbstractAsyncContextManager[AsyncSession]], FakeSessionFactory())


def seed_settings(enabled: bool = True) -> SeedSettings:
    return SeedSettings(
        enabled=enabled,
        admin_email=UserEmail("admin@example.local"),
        admin_name=UserDisplayName("Administrator"),
        admin_password_configured=False,
        admin_api_key=None,
        service_account_enabled=False,
        service_account_project_id=None,
        service_account_name=None,
        service_account_api_key=None,
    )


def test_orchestrator_runs_seeds_in_registry_order() -> None:
    async def run() -> None:
        calls: list[str] = []
        orchestrator = SeedOrchestrator(
            fake_session_factory(),
            registry=SeedRegistry(
                (
                    FakeSeed("permissions", calls),
                    FakeSeed("roles", calls),
                    FakeSeed("admin", calls),
                )
            ),
        )

        await orchestrator.run(seed_settings())

        assert calls == ["permissions", "roles", "admin"]

    anyio.run(run)


def test_orchestrator_skips_all_seeds_when_disabled() -> None:
    async def run() -> None:
        calls: list[str] = []
        orchestrator = SeedOrchestrator(
            fake_session_factory(),
            registry=SeedRegistry((FakeSeed("permissions", calls),)),
        )

        await orchestrator.run(seed_settings(enabled=False))

        assert calls == []

    anyio.run(run)
