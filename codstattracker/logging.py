import sys
from typing import Any


def _loguru_patcher(log_record: dict[str, Any]) -> None:
    log_record['extra'] = ' '.join(
        f'{var_name}={value}'
        for var_name, value in log_record['extra'].items()
    )


def create_loguru_logger():
    from loguru import _logger

    log_format = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> '
        '<level>{level: <7}</level> '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line: <4}</cyan> '
        '<level>{message: <40}</level> - '
        '<red>{extra}</red>'
    )
    logger = _logger.Logger(
        _logger.Core(),
        None,
        0,
        False,
        False,
        False,
        False,
        True,
        _loguru_patcher,
        {},
    )
    logger.add(sys.stdout, format=log_format)
    return logger


default = create_loguru_logger()
