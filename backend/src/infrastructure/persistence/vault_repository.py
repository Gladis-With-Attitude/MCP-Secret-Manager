from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
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

    async def update(self, vault: Vault) -> Vault:
        model = await self._session.get(VaultModel, vault.id.value)
        if model is None:
            return vault

        model.name = vault.name.value
        model.description = vault.description.value
        model.archived = vault.archived
        model.locked = vault.locked
        model.created_at = vault.created_at
        model.updated_at = vault.updated_at
        model.archived_at = vault.archived_at

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise VaultRepositoryConflictError("Vault persistence conflict.") from exc

        return model.to_domain()

    async def list(
        self,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
    ) -> Sequence[Vault]:
        statement = self._filter_statement(
            select(VaultModel),
            include_archived=include_archived,
            search=search,
            status=status,
        )
        statement = statement.order_by(VaultModel.name).offset(offset).limit(limit)
        result = await self._session.scalars(statement)
        return tuple(model.to_domain() for model in result.all())

    async def count(
        self,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        statement = self._filter_statement(
            select(func.count()).select_from(VaultModel),
            include_archived=include_archived,
            search=search,
            status=status,
        )
        return int(await self._session.scalar(statement) or 0)

    async def exists_by_name(
        self,
        name: VaultName,
        *,
        exclude_vault_id: VaultId | None = None,
    ) -> bool:
        statement = select(VaultModel.id).where(VaultModel.name == name.value).limit(1)
        if exclude_vault_id is not None:
            statement = statement.where(VaultModel.id != exclude_vault_id.value)
        result = await self._session.scalar(statement)
        return result is not None

    @staticmethod
    def _filter_statement(
        statement: Select[tuple[VaultModel]] | Select[tuple[int]],
        *,
        include_archived: bool,
        search: str | None,
        status: str | None,
    ) -> Select[tuple[VaultModel]] | Select[tuple[int]]:
        normalized_status = status.strip().lower() if status else None

        if normalized_status == "archived":
            statement = statement.where(VaultModel.archived.is_(True))
        elif normalized_status == "locked":
            statement = statement.where(VaultModel.locked.is_(True), VaultModel.archived.is_(False))
        elif normalized_status == "active":
            statement = statement.where(
                VaultModel.archived.is_(False),
                VaultModel.locked.is_(False),
            )
        elif not include_archived:
            statement = statement.where(VaultModel.archived.is_(False))

        normalized_search = search.strip() if search else None
        if normalized_search:
            pattern = f"%{normalized_search}%"
            statement = statement.where(
                or_(
                    VaultModel.name.ilike(pattern),
                    VaultModel.description.ilike(pattern),
                )
            )

        return statement
