from __future__ import annotations

import logging
from enum import Enum

from infrastructure.logging import safe_log_extra


def log_application_event(
    logger: logging.Logger,
    *,
    event: str,
    result: str | Enum,
    **fields: object,
) -> None:
    result_value = _normalize_result(result)
    log_method = logger.info if result_value == "success" else logger.warning
    log_method(
        "Application event completed.",
        extra=safe_log_extra(
            event=event,
            result=result_value,
            **fields,
        ),
    )


def _normalize_result(result: str | Enum) -> str:
    if isinstance(result, Enum):
        return str(result.value).lower()
    return result.lower()
