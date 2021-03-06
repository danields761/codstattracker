from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Generic, Optional, Type, TypeVar

import sentry_sdk
from pydantic import BaseModel
from pydantic_settings import BaseSettingsModel, load_settings

from codstattracker import logging

if TYPE_CHECKING:
    from loguru import Logger


class Sentry(BaseModel):
    #: Sentry connection DSN
    dsn: str


class BaseAppSettings(BaseSettingsModel):
    class Config:
        env_prefix = 'CST'

    #: Current environment
    env: str = 'debug'

    #: Sentry settings
    sentry: Optional[Sentry] = None


SC = TypeVar('SC', bound=BaseAppSettings)


@dataclass(frozen=True)
class AppState(Generic[SC]):
    settings: SC
    logger: Logger
    hub: Optional[sentry_sdk.Hub] = None


def _load_settings(
    settings_cls: Type[SC],
    settings_path: Optional[Path] = None,
    settings_type_hint: Optional[str] = None,
) -> SC:
    class SettingsLoc(BaseSettingsModel):
        class Config:
            env_prefix = 'CST'

        settings_path: Optional[Path]

    if not settings_path:
        settings_path = load_settings(SettingsLoc, load_env=True).settings_path

    return load_settings(
        settings_cls,
        settings_path,
        type_hint=settings_type_hint,
        load_env=True,
    )


def _create_sentry_hub(settings: BaseAppSettings) -> Optional[sentry_sdk.Hub]:
    if not settings.sentry:
        return None
    sentry_sdk.init(dsn=settings.sentry.dsn, environment=settings.env)
    return sentry_sdk.Hub.current


@contextmanager
def main_ctx(
    app_mode: str,
    settings_cls: Type[SC] = BaseAppSettings,
    settings_path: Optional[Path] = None,
    settings_type_hint: Optional[str] = None,
) -> Generator[AppState, None, None]:
    settings = _load_settings(settings_cls, settings_path, settings_type_hint)
    hub = _create_sentry_hub(settings)

    logger = logging.default.bind(app_mode=app_mode)
    try:
        yield AppState(
            settings=settings,
            logger=logger,
            hub=hub,
        )
    except Exception as exc:
        if hub:
            hub.capture_exception(exc)
        raise
