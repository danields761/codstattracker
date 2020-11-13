from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Generic, Optional, Type, TypeVar

import sentry_sdk
from pydantic import BaseModel
from pydantic_settings import BaseSettingsModel, load_settings

from codstattracker.log import create_loguru_logger

if TYPE_CHECKING:
    from loguru import Logger


class Sentry(BaseModel):
    #: Sentry connection DSN
    dsn: str


class BaseAppSettings(BaseSettingsModel):
    class Config:
        env_prefix = 'CST'

    #: Sentry settings
    sentry: Optional[Sentry] = None


SC = TypeVar('SC', bound=BaseAppSettings)


@dataclass(frozen=True)
class AppState(Generic[SC]):
    settings: SC
    logger: Logger
    hub: Optional[sentry_sdk.Hub] = None


def _load_settings(
    settings_cls: Type[SC], settings_path: Optional[Path] = None
) -> SC:
    class SettingsLoc(BaseSettingsModel):
        class Config:
            env_prefix = 'CST'

        settings_path: Optional[Path]

    if not settings_path:
        settings_path = load_settings(SettingsLoc, load_env=True).settings_path

    return load_settings(settings_cls, settings_path, load_env=True)


def _create_sentry_hub(settings: BaseAppSettings) -> Optional[sentry_sdk.Hub]:
    sentry_sdk.init(dsn=settings.sentry.dsn)
    if not settings.sentry:
        return None
    sentry_sdk.init(dsn=settings.sentry.dsn)
    return sentry_sdk.Hub.current


@contextmanager
def app_ctx(
    app_mode: str,
    settings_cls: Type[SC],
    settings_path: Optional[Path] = None,
) -> Generator[AppState, None, None]:
    settings = _load_settings(settings_cls, settings_path)
    hub = _create_sentry_hub(settings)

    logger = create_loguru_logger().bind(app_mode=app_mode)
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
