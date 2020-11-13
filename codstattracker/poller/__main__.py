from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from pydantic import BaseModel
from sqlalchemy import create_engine

from codstattracker.api import mycallofduty
from codstattracker.api.models import Game, PlayerID
from codstattracker.app import BaseAppSettings, app_ctx
from codstattracker.poller.impl import Poller
from codstattracker.storage import msql

if TYPE_CHECKING:
    from loguru import Logger


class API(BaseModel):
    #: my.callofduty.com auth cookie value (named "ACT_SSO_COOKIE")
    auth_cookie: str


class DB(BaseModel):
    #: Database URI
    uri: str


class Settings(BaseAppSettings):
    #: Database connection parameters
    db: DB

    #: API-settings
    api: API

    #: List of processed players with mode
    players_to_poll: List[Tuple[Game, PlayerID]]


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
