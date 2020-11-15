from contextlib import contextmanager

from pytest import fixture
from sqlalchemy import create_engine

from codstattracker.storage.sql.ext import Session
from codstattracker.storage.sql.models import Base


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
