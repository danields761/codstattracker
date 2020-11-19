from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from codstattracker.api.models import PlayerID, PlayerMatch
from codstattracker.base_model import TrackableEntity
from codstattracker.storage.interfaces import SaveStorage as _SaveStorage

if TYPE_CHECKING:
    from loguru import Logger


class SaveStorage(_SaveStorage):
    def __init__(self, wrapped: _SaveStorage, logger: Logger):
        self._wrapped = wrapped
        self._logger = logger

    def save_match_series(
        self, player_id: PlayerID, match_series: Sequence[PlayerMatch]
    ) -> None:
        for match in match_series:
            if not isinstance(match, TrackableEntity):
                continue
            source, meta = match.get_entity_info()
            self._logger.info(
                'Match info',
                match_id=match.id,
                match_player_id=player_id,
                match_source=source,
                match_meta=meta,
            )

        return self._wrapped.save_match_series(player_id, match_series)
