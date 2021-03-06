import os

from alembic.config import main
from pytest import fixture


@fixture
def workon_proj_root(project_root):
    old_cwd = os.getcwd()
    os.chdir(project_root)
    yield
    os.chdir(old_cwd)


def test_migrations(innocent_engine, workon_proj_root):
    base_args = ('-x', f'uri={innocent_engine.url}')

    main(base_args + ('upgrade', 'head'))
    main(base_args + ('downgrade', 'base'))

    main(base_args + ('upgrade', 'head'))
    main(base_args + ('downgrade', 'base'))

    main(base_args + ('upgrade', 'head'))
    main(base_args + ('downgrade', 'base'))
