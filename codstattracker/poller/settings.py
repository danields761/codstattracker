import re
from typing import Callable, Iterable, List, Pattern, Tuple, Type

from pydantic import BaseModel
from pydantic.validators import str_validator

from codstattracker.api.models import Game as _Game
from codstattracker.api.models import PlayerID as _PlayerID
from codstattracker.app import BaseAppSettings
from codstattracker.base_model import Model


def _create_validators(
    cls: Type[Model], pattern: Pattern[str]
) -> Iterable[Callable]:
    def from_string(val: str) -> Model:
        match = pattern.match(val)
        if not match:
            raise ValueError(f'Pattern matching failed: {pattern.pattern}')
        return cls(*match.groups())

    return str_validator, from_string


class Game(_Game):
    pattern = re.compile(r'(\w+):(\w+)')

    @classmethod
    def __get_validators__(cls) -> Iterable[Callable]:
        yield from _create_validators(_Game, cls.pattern)


class PlayerID(_PlayerID):
    pattern = re.compile(r'(\w+):(\w+)#(\w+)')

    @classmethod
    def __get_validators__(cls) -> Iterable[Callable]:
        yield from _create_validators(_PlayerID, cls.pattern)


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
