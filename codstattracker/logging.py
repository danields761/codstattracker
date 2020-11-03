from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from loguru import Logger


def _loguru_patcher(log_record: dict[str, Any]) -> None:
    log_record['extra'] = ' '.join(
        f'{var_name}={value}'
        for var_name, value in log_record['extra'].items()
    )


def create_empty_logger() -> Logger:
    from loguru import _logger

    logger = _logger.Logger(
        _logger.Core(),
        None,
        0,
        False,
        False,
        False,
        False,
        True,
        None,
        {},
    )
    return logger


def create_loguru_logger() -> Logger:
    log_format = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> '
        '<level>{level: <7}</level> '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line: <4}</cyan> '
        '<level>{message: <40}</level> - '
        '<red>{extra}</red>'
    )
    logger = create_empty_logger()
    logger.add(sys.stdout, format=log_format)
    return logger.patch(_loguru_patcher)


default = create_loguru_logger()
