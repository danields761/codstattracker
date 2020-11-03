from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import create_engine

from codstattracker.api import mycallofduty
from codstattracker.app import main_ctx
from codstattracker.poller.impl import Poller
from codstattracker.poller.settings import DB, Settings
from codstattracker.storage import sql
from codstattracker.storage.interfaces import SaveStorage, StorageContext

if TYPE_CHECKING:
    from loguru import Logger


def _create_save_storage_ctx(
    db_settings: DB,
) -> StorageContext[SaveStorage]:
    engine = create_engine(db_settings.uri)

    def storage_factory(session):
        return sql.SaveStorage(
            session, save_matches_logs=db_settings.save_matches_log
        )

    return sql.StorageContext(engine, storage_factory)


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
