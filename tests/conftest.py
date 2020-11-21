from pathlib import Path

from pytest import fixture


def pytest_addoption(parser):
    parser.addoption(
        '--test-db-uri',
        help='Database URI which will be used for DB tests instead of sqlite',
    )
    parser.addoption(
        '--use-migrations',
        help='Use migrations instead of auto-creation via `Base.metadata`',
        action='store_true',
        default=False,
    )


@fixture
def project_root():
    return Path(__file__).parent.parent
