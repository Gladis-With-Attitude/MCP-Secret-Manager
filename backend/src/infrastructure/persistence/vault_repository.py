from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.vault.entities import Vault
from domain.vault.repositories import VaultRepositoryConflictError
from domain.vault.value_objects import VaultId, VaultName
from infrastructure.persistence.vault_model import VaultModel


class SqlAlchemyVaultRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, vault: Vault) -> Vault:
        model = VaultModel.from_domain(vault)
        self._session.add(model)

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise VaultRepositoryConflictError("Vault persistence conflict.") from exc

        return model.to_domain()

    async def get(self, vault_id: VaultId) -> Vault | None:
        model = await self._session.get(VaultModel, vault_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def list(self) -> Sequence[Vault]:
        result = await self._session.scalars(select(VaultModel).order_by(VaultModel.name))
        return tuple(model.to_domain() for model in result.all())

    async def exists_by_name(self, name: VaultName) -> bool:
        statement = select(VaultModel.id).where(VaultModel.name == name.value).limit(1)
        result = await self._session.scalar(statement)
        return result is not None
