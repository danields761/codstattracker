from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import create_engine

from codstattracker.api import mycallofduty
from codstattracker.app import app_ctx
from codstattracker.poller.impl import Poller
from codstattracker.poller.settings import Settings
from codstattracker.storage import msql

if TYPE_CHECKING:
    from loguru import Logger


def _create_poller(settings: Settings, logger: Logger) -> Poller:
    api = mycallofduty.api_factory(settings.api.auth_cookie)
    engine = create_engine(settings.db.uri)
    storage_ctx = msql.StorageContext(engine, msql.SaveStorage)
    return Poller(storage_ctx, api, settings.players_to_poll, logger)


def main():
    with app_ctx('poller', Settings) as app:
        poller = _create_poller(app.settings, app.logger)
        poller.regular_pool()


if __name__ == '__main__':
    main()
