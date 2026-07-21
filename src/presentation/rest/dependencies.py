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


async def get_create_vault_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Vault persistence is not configured.",
    )


async def get_create_project_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Project persistence is not configured.",
    )


async def get_create_secret_use_case() -> NoReturn:
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


async def get_active_secret_version_use_case() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="SecretVersion persistence is not configured.",
    )
