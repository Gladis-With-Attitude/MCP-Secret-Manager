from __future__ import annotations

import argparse
import os
import re
import shlex
import sys
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from infrastructure.config import AppSettings, ConfigurationError, RuntimeConfiguration

BACKEND_ENV_PREFIX = "MCP_SECRET_MANAGER_"
ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def main() -> None:
    raise SystemExit(run())


def run(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-env":
        return _run_validate_env(args)

    parser.print_help(sys.stderr)
    return 2


def validate_deployment_environment(
    values: Mapping[str, str],
    *,
    expected_environment: str = "production",
) -> RuntimeConfiguration:
    settings = _settings_from_env_values(values)
    errors: list[str] = []

    configured_environment = values.get("MCP_SECRET_MANAGER_ENVIRONMENT")
    if configured_environment is None:
        errors.append("MCP_SECRET_MANAGER_ENVIRONMENT must be set explicitly.")
    if settings.environment != expected_environment:
        errors.append(
            "MCP_SECRET_MANAGER_ENVIRONMENT must be "
            f"{expected_environment!r} for deployment readiness validation."
        )

    errors.extend(settings.validation_errors())
    errors.extend(_validate_frontend_environment(values, settings.environment))
    errors.extend(_validate_deployment_only_values(values))

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ConfigurationError(f"Deployment environment is not ready:\n{joined}")

    return settings.runtime_configuration()


def load_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ConfigurationError(f"Environment file does not exist: {path}")

    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        if "=" not in line:
            raise ConfigurationError(f"{path}:{line_number} must use KEY=VALUE syntax.")

        key, raw_value = line.split("=", 1)
        key = key.strip()
        if ENV_KEY_PATTERN.fullmatch(key) is None:
            raise ConfigurationError(f"{path}:{line_number} contains an invalid key: {key!r}.")
        values[key] = _parse_env_value(raw_value)

    return values


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcp-secret-manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_env = subparsers.add_parser(
        "validate-env",
        help="Validate deployment environment configuration without printing secrets.",
    )
    validate_env.add_argument(
        "--env-file",
        type=Path,
        required=True,
        help="Path to the deployment environment file to validate.",
    )
    validate_env.add_argument(
        "--environment",
        default="production",
        choices=("staging", "production"),
        help="Expected deployment environment.",
    )

    return parser


def _run_validate_env(args: argparse.Namespace) -> int:
    try:
        values = load_env_file(args.env_file)
        configuration = validate_deployment_environment(
            values,
            expected_environment=args.environment,
        )
    except ConfigurationError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    sys.stdout.write("Deployment environment validation passed.\n")
    sys.stdout.write(f"Environment: {configuration.application.environment}\n")
    sys.stdout.write(f"Service: {configuration.application.service_name}\n")
    sys.stdout.write(
        "Backend: database configured, cryptography configured, security controls enabled.\n"
    )
    sys.stdout.write(
        "Frontend: NEXT_PUBLIC_APP_ENV and NEXT_PUBLIC_API_BASE_URL are deployment-ready.\n"
    )
    sys.stdout.write(
        "Safe summary: "
        f"cors_origins={len(configuration.rest_api.cors.allowed_origins)}, "
        f"rate_limit={configuration.rest_api.rate_limit.enabled}, "
        f"hsts={configuration.rest_api.security_headers.hsts_enabled}.\n"
    )
    return 0


def _settings_from_env_values(values: Mapping[str, str]) -> AppSettings:
    settings_kwargs = {
        key.removeprefix(BACKEND_ENV_PREFIX).lower(): value
        for key, value in values.items()
        if key.startswith(BACKEND_ENV_PREFIX)
    }
    with _without_backend_environment():
        return AppSettings(_env_file=None, **settings_kwargs)  # type: ignore[call-arg, arg-type]


def _validate_frontend_environment(
    values: Mapping[str, str],
    environment: str,
) -> list[str]:
    errors: list[str] = []
    app_env = _optional_value(values.get("NEXT_PUBLIC_APP_ENV"))
    api_base_url = _optional_value(values.get("NEXT_PUBLIC_API_BASE_URL"))

    if app_env is None:
        errors.append("NEXT_PUBLIC_APP_ENV is required for deployment builds.")
    elif environment == "production" and app_env != "production":
        errors.append(
            "NEXT_PUBLIC_APP_ENV must be production when backend environment is production."
        )

    if api_base_url is None:
        errors.append("NEXT_PUBLIC_API_BASE_URL is required for deployment builds.")
        return errors

    parsed = urlparse(api_base_url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc == "":
        errors.append("NEXT_PUBLIC_API_BASE_URL must be an absolute HTTP(S) URL.")
    if environment == "production":
        if parsed.scheme != "https":
            errors.append("NEXT_PUBLIC_API_BASE_URL must use HTTPS in production.")
        if parsed.hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:  # noqa: S104
            errors.append("NEXT_PUBLIC_API_BASE_URL cannot point at a local host in production.")

    return errors


def _validate_deployment_only_values(values: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    if _is_truthy(values.get("MCP_SECRET_MANAGER_ALLOW_DB_RESET")):
        errors.append("MCP_SECRET_MANAGER_ALLOW_DB_RESET must not be enabled for deployments.")
    if _optional_value(values.get("MCP_SECRET_MANAGER_TEST_DATABASE_URL")) is not None:
        errors.append("MCP_SECRET_MANAGER_TEST_DATABASE_URL must not be set for deployments.")
    return errors


def _parse_env_value(raw_value: str) -> str:
    value = raw_value.strip()
    if value.startswith(("'", '"')):
        parsed = shlex.split(value, comments=False, posix=True)
        if len(parsed) != 1:
            raise ConfigurationError("Quoted environment values must contain exactly one value.")
        return parsed[0]
    return re.sub(r"\s+#.*$", "", value).strip()


def _optional_value(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    value = raw_value.strip()
    return value or None


def _is_truthy(raw_value: str | None) -> bool:
    value = _optional_value(raw_value)
    return value is not None and value.lower() in {"1", "true", "yes", "on"}


@contextmanager
def _without_backend_environment() -> Iterator[None]:
    original = {
        key: value for key, value in os.environ.items() if key.startswith(BACKEND_ENV_PREFIX)
    }
    for key in original:
        del os.environ[key]
    try:
        yield
    finally:
        for key in list(os.environ):
            if key.startswith(BACKEND_ENV_PREFIX):
                del os.environ[key]
        os.environ.update(original)


if __name__ == "__main__":
    main()
