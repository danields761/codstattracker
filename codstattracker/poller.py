from typing import Sequence

from loguru import Logger

from codstattracker.api.exceptions import FetchError, UnrecoverableFetchError
from codstattracker.api.interfaces import PlayerAPI, PlayerGameMatch, PlayerID
from codstattracker.storage.exceptions import StorageIOError
from codstattracker.storage.interfaces import SaveStorage, StorageContext


class Poller:
    def __init__(
        self,
        storage_ctx: StorageContext[SaveStorage],
        api: PlayerAPI,
        player_ids: Sequence[PlayerID],
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
        players_matches: dict[PlayerID, Sequence[PlayerGameMatch]] = {}

        self._logger.info('Starting fetching player stats')
        for player_id in self._player_ids:
            logger = self._logger.bind(player_id=repr(player_id))
            logger.info('Fetching player stats')
            try:
                matches = self._api.get_recent_matches(player_id)
            except FetchError as exc:
                logger.warning('Skipping player stats due to error', exc=exc)
                continue

            logger.info('Matches info received', num_of_matches=len(matches))
            players_matches[player_id] = matches

        self._logger.info('Saving players stats')
        with self._storage_ctx() as save_storage:
            for player_id, matches in players_matches.items():
                self._logger.info(
                    'Saving player stats', player_id=repr(player_id)
                )
                save_storage.save_match_series(player_id, matches)
