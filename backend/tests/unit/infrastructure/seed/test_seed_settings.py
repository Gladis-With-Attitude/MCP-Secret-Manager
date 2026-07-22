from __future__ import annotations

import pytest

from infrastructure.config import AppSettings
from infrastructure.seed.settings import SeedSettings


def test_seed_settings_requires_admin_email_when_enabled() -> None:
    with pytest.raises(RuntimeError, match="BOOTSTRAP_ADMIN_EMAIL"):
        SeedSettings.from_app_settings(
            AppSettings(
                bootstrap_enabled=True,
                bootstrap_admin_email=None,
                bootstrap_admin_name="Administrator",
            )
        )


def test_seed_settings_normalizes_admin_identity() -> None:
    settings = SeedSettings.from_app_settings(
        AppSettings(
            bootstrap_enabled=True,
            bootstrap_admin_email=" Admin@Example.Local ",
            bootstrap_admin_name=" Administrator ",
            bootstrap_admin_password="configured-test-value",  # noqa: S106
            bootstrap_admin_api_key="",
        )
    )

    assert settings.admin_email.value == "admin@example.local"
    assert settings.admin_name.value == "Administrator"
    assert settings.admin_password_configured is True
    assert settings.admin_api_key is None
