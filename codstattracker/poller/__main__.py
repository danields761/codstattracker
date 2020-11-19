from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import create_engine

from codstattracker.api import mycallofduty
from codstattracker.app import main_ctx
from codstattracker.logging import create_empty_logger
from codstattracker.poller.impl import Poller
from codstattracker.poller.settings import DB, Settings
from codstattracker.storage import loggable, sql
from codstattracker.storage.interfaces import SaveStorage, StorageContext

if TYPE_CHECKING:
    from loguru import Logger


def _create_api_save_log(log_file: Path) -> Logger:
    def json_default(value):
        return str(value)

    def formatter(record):
        record["extra"]["serialized"] = json.dumps(
            {
                'time': record['time'].timestamp(),
                'level': record['level'].name,
                'name': record['name'],
                'function': record['function'],
                'line': record['line'],
                'message': record['message'],
                'extra': record['extra'],
            },
            indent=2,
            default=json_default,
        )
        return "{extra[serialized]}\n"

    logger = create_empty_logger()
    logger.add(log_file, format=formatter)
    return logger


def _create_save_storage_ctx(
    db_settings: DB,
) -> StorageContext[SaveStorage]:
    engine = create_engine(db_settings.uri)
    if not db_settings.log_file:
        ss_factory = sql.SaveStorage
    else:

        def ss_factory(session):
            return loggable.SaveStorage(
                sql.SaveStorage(session),
                _create_api_save_log(db_settings.log_file),
            )

    return sql.StorageContext(engine, ss_factory)


def _create_poller(settings: Settings, logger: Logger) -> Poller:
    api = mycallofduty.api_factory(settings.api.auth_cookie, collect_meta=True)

    storage_ctx = _create_save_storage_ctx(settings.db)
    return Poller(storage_ctx, api, settings.players_to_poll, logger)


def main(*args: str) -> None:
    parser = argparse.ArgumentParser(
        'cst-poller',
    )
    parser.add_argument('settings_path', type=Path)
    parsed = parser.parse_args(args if args else None)

    with main_ctx('poller', Settings, parsed.settings_path) as app:
        poller = _create_poller(app.settings, app.logger)
        poller.regular_pool()


if __name__ == '__main__':
    main()
