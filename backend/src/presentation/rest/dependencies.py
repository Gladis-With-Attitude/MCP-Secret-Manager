from __future__ import annotations

from typing import NoReturn

from fastapi import HTTPException, status


async def get_create_user_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="User persistence is not configured.",
    )


async def get_create_service_account_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="ServiceAccount persistence is not configured.",
    )


async def get_create_api_key_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="ApiKey persistence is not configured.",
    )


async def get_list_api_keys_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="ApiKey persistence is not configured.",
    )


async def get_api_key_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="ApiKey persistence is not configured.",
    )


async def get_update_api_key_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="ApiKey persistence is not configured.",
    )


async def get_revoke_api_key_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="ApiKey persistence is not configured.",
    )


async def get_create_session_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Session persistence is not configured.",
    )


async def get_current_session_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Session persistence is not configured.",
    )


async def get_revoke_current_session_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Session persistence is not configured.",
    )


async def get_current_profile_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile persistence is not configured.",
    )


async def get_update_current_profile_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile persistence is not configured.",
    )


async def get_account_security_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile persistence is not configured.",
    )


async def get_list_active_sessions_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile persistence is not configured.",
    )


async def get_revoke_session_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile persistence is not configured.",
    )


async def get_change_password_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile persistence is not configured.",
    )


async def get_settings_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Settings persistence is not configured.",
    )


async def get_update_preferences_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Settings persistence is not configured.",
    )


async def get_update_notifications_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Settings persistence is not configured.",
    )


async def get_authorize_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_list_permissions_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_list_roles_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_role_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_create_role_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_update_role_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_list_actor_roles_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_assign_actor_role_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_revoke_actor_role_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="RBAC persistence is not configured.",
    )


async def get_list_audit_events_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Audit persistence is not configured.",
    )


async def get_audit_event_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Audit persistence is not configured.",
    )


async def get_create_vault_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Vault persistence is not configured.",
    )


async def get_list_vaults_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Vault persistence is not configured.",
    )


async def get_vault_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Vault persistence is not configured.",
    )


async def get_update_vault_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Vault persistence is not configured.",
    )


async def get_archive_vault_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Vault persistence is not configured.",
    )


async def get_create_project_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Project persistence is not configured.",
    )


async def get_list_projects_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Project persistence is not configured.",
    )


async def get_project_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Project persistence is not configured.",
    )


async def get_update_project_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Project persistence is not configured.",
    )


async def get_archive_project_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Project persistence is not configured.",
    )


async def get_create_secret_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Secret persistence is not configured.",
    )


async def get_list_secrets_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Secret persistence is not configured.",
    )


async def get_secret_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Secret persistence is not configured.",
    )


async def get_update_secret_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Secret persistence is not configured.",
    )


async def get_archive_secret_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Secret persistence is not configured.",
    )


async def get_create_secret_version_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="SecretVersion persistence is not configured.",
    )


async def get_list_secret_versions_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="SecretVersion persistence is not configured.",
    )


async def get_secret_version_metadata_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="SecretVersion persistence is not configured.",
    )


async def get_active_secret_version_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="SecretVersion persistence is not configured.",
    )


async def get_restore_secret_version_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="SecretVersion persistence is not configured.",
    )
