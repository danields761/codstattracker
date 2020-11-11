from contextlib import contextmanager

from pytest import fixture
from sqlalchemy import create_engine

from codstattracker.api.models import MW_MULTIPLAYER
from codstattracker.storage.msql.ext import Session
from codstattracker.storage.msql.models import Base, GameModel


@fixture
def engine():
    e = create_engine('sqlite://')
    Base.metadata.create_all(e)
    return e


@fixture
def session(engine):
    s = Session(engine)
    yield s
    s.close()


@fixture
def session_ctx(engine):
    @contextmanager
    def ctx():
        s = Session(engine)
        try:
            yield s
        finally:
            s.close()

    return ctx


@fixture
def game_mode(session_ctx):
    with session_ctx() as s:
        return s.upsert(GameModel, **MW_MULTIPLAYER.as_dict_flat())
