from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import create_engine

from codstattracker.api import mycallofduty
from codstattracker.app import app_ctx
from codstattracker.poller.impl import Poller
from codstattracker.poller.settings import Settings
from codstattracker.storage import sql

if TYPE_CHECKING:
    from loguru import Logger


def _create_poller(settings: Settings, logger: Logger) -> Poller:
    api = mycallofduty.api_factory(settings.api.auth_cookie)
    engine = create_engine(settings.db.uri)
    storage_ctx = sql.StorageContext(engine, sql.SaveStorage)
    return Poller(storage_ctx, api, settings.players_to_poll, logger)


def main():
    parser = argparse.ArgumentParser(
        'cst-poller',
    )
    parser.add_argument('settings_path', type=Path)
    parsed = parser.parse_args()

    with app_ctx('poller', Settings, parsed.settings_path) as app:
        poller = _create_poller(app.settings, app.logger)
        poller.regular_pool()


if __name__ == '__main__':
    main()
