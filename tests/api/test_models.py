from pytest import mark

from codstattracker.api.models import Model, PlayerID


class RootModel(Model):
    foo: int
    bar: float
    baz: str


class NestedModel(Model):
    field: list[int]
    nested: RootModel


class MultipleInheritedModel(RootModel, NestedModel):
    pass


@mark.parametrize(
    'model_inst, output',
    [
        (
            RootModel(foo=10, bar=20.0, baz='test'),
            {
                'foo': 10,
                'bar': 20.0,
                'baz': 'test',
            },
        ),
        (
            NestedModel(
                field=[1], nested=RootModel(foo=10, bar=20.0, baz='test')
            ),
            {'field': [1], 'nested': RootModel(foo=10, bar=20.0, baz='test')},
        ),
        (
            MultipleInheritedModel(
                foo=10,
                bar=20.0,
                baz='test',
                field=[1],
                nested=RootModel(foo=10, bar=20.0, baz='test'),
            ),
            {
                'foo': 10,
                'bar': 20.0,
                'baz': 'test',
                'field': [1],
                'nested': RootModel(foo=10, bar=20.0, baz='test'),
            },
        ),
    ],
)
def test_get_dict_flat(model_inst, output):
    assert model_inst.as_dict_flat() == output


def test_player_id_repr():
    assert (
        repr(
            PlayerID(
                platform='testplatform', nickname='test_nickname', id='1234'
            )
        )
        == 'testplatform:test_nickname#1234'
    )
