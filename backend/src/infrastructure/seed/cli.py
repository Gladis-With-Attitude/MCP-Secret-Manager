from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import Sequence

from infrastructure.config import get_settings
from infrastructure.persistence.database import create_database_engine, create_session_factory
from infrastructure.seed.orchestrator import SeedOrchestrator
from infrastructure.seed.settings import SeedSettings

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(levelname)s:%(name)s:%(message)s",
    )


async def run_bootstrap() -> None:
    settings = get_settings()
    if settings.database_url is None:
        msg = "MCP_SECRET_MANAGER_DATABASE_URL is required to bootstrap system data."
        raise RuntimeError(msg)

    seed_settings = SeedSettings.from_app_settings(settings)
    engine = create_database_engine(settings.database_url)
    try:
        orchestrator = SeedOrchestrator(create_session_factory(engine))
        await orchestrator.run(seed_settings)
    finally:
        await engine.dispose()


def main(_argv: Sequence[str] | None = None) -> int:
    configure_logging()
    try:
        asyncio.run(run_bootstrap())
    except Exception:
        logger.exception("System data bootstrap failed.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
