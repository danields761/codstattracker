from argparse import Namespace
from contextlib import contextmanager

from alembic import command as _a_commands
from alembic.config import Config as _AConfig
from pytest import UsageError, fixture, param
from sqlalchemy import create_engine

from codstattracker.storage.sql.ext import Session
from codstattracker.storage.sql.models import Base


def pytest_generate_tests(metafunc):
    test_db_uri = metafunc.config.getoption('test_db_uri', None)
    use_migrations = metafunc.config.getoption('use_migrations', False)
    if 'innocent_engine' in metafunc.fixturenames and test_db_uri:
        metafunc.parametrize('innocent_engine', (test_db_uri,), indirect=True)
    if 'engine' in metafunc.fixturenames and use_migrations:
        metafunc.parametrize(
            'engine', (param(True, id='use-migrations'),), indirect=True
        )


def _alembic_cfg(project_root, db_type=None, db_uri=None):
    x_opts = [
        f'{name}={val}'
        for name, val in (('db-type', db_type), ('uri', db_uri))
        if val
    ]

    cfg = _AConfig(
        str(project_root / 'alembic.ini'), cmd_opts=Namespace(x=x_opts)
    )
    cfg.set_main_option('script_location', str(project_root / 'migrations'))
    cfg.set_main_option(
        'version_locations', str(project_root / 'migrations/versions')
    )
    return cfg


@fixture
def innocent_engine(request):
    try:
        uri = request.param
    except AttributeError:
        uri = 'sqlite://'

    return create_engine(uri)


@fixture
def engine(request, innocent_engine, project_root):
    try:
        use_migrations = request.param
    except AttributeError:
        use_migrations = False

    if not use_migrations:
        Base.metadata.create_all(innocent_engine)
        yield innocent_engine
        Base.metadata.drop_all(innocent_engine)
    else:
        url = innocent_engine.url
        if (
            url.drivername == 'sqlite'
            and url.host is None
            and url.database is None
        ):
            raise UsageError(
                'Migrations is not supported with in-memory sqlite database'
            )

        cfg = _alembic_cfg(project_root, db_uri=innocent_engine.url)
        _a_commands.upgrade(cfg, 'head')
        yield innocent_engine
        _a_commands.downgrade(cfg, 'base')


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
