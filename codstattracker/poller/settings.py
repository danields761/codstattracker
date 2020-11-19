import re
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Pattern, Tuple, Type

from pydantic import BaseModel, validator
from pydantic.validators import str_validator

from codstattracker.api.models import Game
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

    #: Matches log file
    log_file: Optional[Path] = None

    @validator('log_file')
    def log_file_must_be_writable(
        cls, log_file: Optional[Path]
    ) -> Optional[Path]:
        if log_file is None:
            return None

        try:
            with open(log_file, 'wt'):
                pass
        except PermissionError:
            raise ValueError('Log file must be writable!')

        return log_file


class Settings(BaseAppSettings):
    #: Database connection parameters
    db: DB

    #: API-settings
    api: API

    #: list of processed players with mode
    players_to_poll: List[Tuple[Game, PlayerID]]
