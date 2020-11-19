from __future__ import annotations

import dataclasses
from typing import Any, Iterable, Optional, Protocol, Type, runtime_checkable


@runtime_checkable
class TrackableEntity(Protocol):
    def get_entity_source(self) -> dict[str, Any]:
        raise NotImplementedError

    def get_entity_source_meta(self) -> dict[str, Any]:
        raise NotImplementedError


class Model:
    def __init_subclass__(
        cls,
        frozen: bool = False,
        unsafe_hash: bool = False,
        **kwargs,
    ):
        dataclasses.dataclass(cls, frozen=frozen, unsafe_hash=unsafe_hash)

    @classmethod
    def all_fields(cls) -> Iterable[dataclasses.Field]:
        mro = cls.__mro__
        for base in mro:
            try:
                yield from dataclasses.fields(base)
            except TypeError:
                pass

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def as_dict_flat(
        self, as_parent: Optional[Type[Model]] = None
    ) -> dict[str, Any]:
        if as_parent:
            self_cls = type(self)
            mro = set(self_cls.__mro__)
            if as_parent not in mro:
                raise TypeError(
                    f'Given model {as_parent.__name__!r} is not parent of '
                    f'current model {self_cls.__name__!r}'
                )

            all_fields = as_parent.all_fields()
        else:
            all_fields = self.all_fields()

        return {field.name: getattr(self, field.name) for field in all_fields}
