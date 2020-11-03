def pytest_addoption(parser):
    parser.addoption(
        '--test-db-uri',
        help='Database URI which will be used for DB tests along with sqlite',
    )
