from __future__ import annotations

from dataclasses import dataclass

from domain.identity.exceptions import IdentityDomainError
from domain.identity.value_objects import ServiceAccountName, UserDisplayName, UserEmail
from domain.project.value_objects import ProjectId
from infrastructure.config import AppSettings


@dataclass(frozen=True, slots=True)
class SeedSettings:
    enabled: bool
    admin_email: UserEmail
    admin_name: UserDisplayName
    admin_password_configured: bool
    admin_api_key: str | None
    service_account_enabled: bool
    service_account_project_id: ProjectId | None
    service_account_name: ServiceAccountName | None
    service_account_api_key: str | None

    @classmethod
    def from_app_settings(cls, settings: AppSettings) -> SeedSettings:
        admin_email = _required_value(
            settings.bootstrap_admin_email,
            "MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL",
        )
        admin_name = _required_value(
            settings.bootstrap_admin_name,
            "MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME",
        )
        service_account_project_id_value = _optional_value(
            settings.bootstrap_service_account_project_id
        )
        service_account_name_value = _optional_value(settings.bootstrap_service_account_name)
        try:
            service_account_project_id = (
                ProjectId.from_string(service_account_project_id_value)
                if service_account_project_id_value is not None
                else None
            )
            service_account_name = (
                ServiceAccountName(service_account_name_value)
                if service_account_name_value is not None
                else None
            )
            return cls(
                enabled=settings.bootstrap_enabled,
                admin_email=UserEmail(admin_email),
                admin_name=UserDisplayName(admin_name),
                admin_password_configured=(
                    _optional_value(settings.bootstrap_admin_password) is not None
                ),
                admin_api_key=_optional_value(settings.bootstrap_admin_api_key),
                service_account_enabled=settings.bootstrap_service_account_enabled,
                service_account_project_id=service_account_project_id,
                service_account_name=service_account_name,
                service_account_api_key=_optional_value(settings.bootstrap_service_account_api_key),
            )
        except (IdentityDomainError, ValueError) as exc:
            msg = f"Bootstrap seed configuration is invalid: {exc}"
            raise RuntimeError(msg) from exc


def _required_value(raw_value: str | None, env_name: str) -> str:
    value = _optional_value(raw_value)
    if value is None:
        msg = f"{env_name} is required when system bootstrap is enabled."
        raise RuntimeError(msg)
    return value


def _optional_value(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    value = raw_value.strip()
    if value == "":
        return None
    return value
