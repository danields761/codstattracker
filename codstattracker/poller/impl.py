from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple

from codstattracker.api.exceptions import FetchError, UnrecoverableFetchError
from codstattracker.api.interfaces import PlayerAPI
from codstattracker.api.models import Game, PlayerID, PlayerMatch
from codstattracker.storage.exceptions import StorageIOError
from codstattracker.storage.interfaces import SaveStorage, StorageContext

if TYPE_CHECKING:
    from loguru import Logger


class Poller:
    def __init__(
        self,
        storage_ctx: StorageContext[SaveStorage],
        api: PlayerAPI,
        player_ids: List[Tuple[Game, PlayerID]],
        logger: Logger,
    ):
        self._storage_ctx = storage_ctx
        self._api = api
        self._player_ids = player_ids
        self._logger = logger

    def regular_pool(self) -> None:
        try:
            self._regular_pool()
        except UnrecoverableFetchError as exc:
            self._logger.error(
                'Unrecoverable fetch error occurs, starting shutdown ...',
                exc=exc,
            )
            raise
        except StorageIOError as exc:
            self._logger.warning(
                'Storage IO error, maybe you will try later?', exc=exc
            )
            raise

    def _regular_pool(self) -> None:
        players_matches: Dict[PlayerID, List[PlayerMatch]] = {}

        self._logger.info('Starting fetching player stats')
        for game, player_id in self._player_ids:
            logger = self._logger.bind(game=game, player_id=repr(player_id))
            logger.info('Fetching player stats')
            try:
                matches = self._api.get_recent_matches(game, player_id)
            except FetchError as exc:
                logger.exception('Skipping player stats due to error', exc=exc)
                continue

            logger.info('Matches info received', num_of_matches=len(matches))
            players_matches[player_id] = list(matches)

        self._logger.info('Saving players stats')
        with self._storage_ctx() as save_storage:
            for player_id, matches in players_matches.items():
                self._logger.info(
                    'Saving player stats',
                    player_id=repr(player_id),
                    num_matches=len(matches),
                )
                save_storage.save_match_series(player_id, matches)
