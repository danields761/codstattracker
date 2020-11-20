from contextlib import contextmanager

from pytest import fixture
from sqlalchemy import create_engine

from codstattracker.storage.sql.ext import Session
from codstattracker.storage.sql.models import Base


def pytest_generate_tests(metafunc):
    test_db_uri = metafunc.config.getoption('test_db_uri', None)
    if 'innocent_engine' in metafunc.fixturenames and test_db_uri:
        params = (test_db_uri,)
        metafunc.parametrize('innocent_engine', params, indirect=True)


@fixture
def innocent_engine(request):
    try:
        uri = request.param
    except AttributeError:
        uri = 'sqlite://'

    return create_engine(uri)


@fixture
def engine(innocent_engine):
    Base.metadata.create_all(innocent_engine)
    yield innocent_engine
    Base.metadata.drop_all(innocent_engine)


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
