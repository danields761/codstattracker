from datetime import datetime
from typing import Optional, Sequence

from codstattracker.api.models import Game, PlayerID, PlayerMatch


class PlayerAPI:
    def get_recent_matches(
        self,
        game: Game,
        player_id: PlayerID,
        from_: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Sequence[PlayerMatch]:
        """

        :param game:
        :param player_id:
        :param from_:
        :param until:
        :return:
        :raises FetchError:
        :raises UnrecoverableFetchError:
        """
        raise NotImplementedError
