import json
from pathlib import Path
from unittest.mock import Mock, call, patch

from pytest import fixture

from codstattracker import app


@fixture(autouse=True)
def disable_sentry():
    with patch('sentry_sdk.hub._init'):
        yield


@fixture(autouse=True)
def load_settings_content_reader():
    content_reader = Mock(name='content_reader')
    content_reader.return_value = '{}'

    orig_load_settings = app.load_settings

    def new_load_settings(*args, _content_reader=None, **kwargs):
        return orig_load_settings(
            *args, _content_reader=content_reader, **kwargs
        )

    with patch.object(
        app,
        'load_settings',
        new_load_settings,
    ):
        yield content_reader


def test_uses_base_settings():
    with app.main_ctx('test') as a:
        assert isinstance(a.settings, app.BaseAppSettings)
        assert a.settings.sentry is None
        assert a.settings.env == 'debug'


def test_respects_env_settings_path(load_settings_content_reader):
    load_settings_content_reader.return_value = '{}'
    environ = {'CST_SETTINGS_PATH': 'some/test/path.json'}

    with patch.dict('os.environ', environ):
        with app.main_ctx('test'):
            assert load_settings_content_reader.mock_calls == [
                call(Path('some/test/path.json'))
            ]


def test_direct_settings_path_overrides_env(load_settings_content_reader):
    load_settings_content_reader.return_value = '{}'
    environ = {'CST_SETTINGS_PATH': 'env/path.json'}

    with patch.dict('os.environ', environ):
        with app.main_ctx('test', settings_path=Path('direct/path.json')):
            assert load_settings_content_reader.mock_calls == [
                call(Path('direct/path.json'))
            ]


def test_respects_app_env(load_settings_content_reader):
    environ = {'CST_ENV': 'test-test-test'}
    with patch.dict('os.environ', environ):
        with app.main_ctx('test') as a:
            assert a.settings.env == 'test-test-test'


class CustomSettings(app.BaseAppSettings):
    foo: str
    bar: int


def test_custom_settings_from_file(load_settings_content_reader):
    load_settings_content_reader.return_value = json.dumps(
        {
            'env': 'test-test',
            'foo': 'foo-val',
            'bar': 12345,
        }
    )

    with app.main_ctx(
        'test', CustomSettings, Path('some-path'), settings_type_hint='json'
    ) as a:
        assert isinstance(a.settings, CustomSettings)
        assert a.settings == CustomSettings(
            env='test-test',
            foo='foo-val',
            bar=12345,
        )


def test_custom_settings_from_env(load_settings_content_reader):
    environ = {
        'CST_ENV': 'test-test',
        'CST_FOO': 'new-foo',
        'CST_BAR': '54321',
    }

    with patch.dict('os.environ', environ, clear=True):
        with app.main_ctx('test', CustomSettings) as a:
            assert a.settings == CustomSettings(
                env='test-test',
                foo='new-foo',
                bar=54321,
            )
