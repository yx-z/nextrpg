from collections.abc import Callable
from dataclasses import Field, dataclass, field, fields
from typing import (
    Any,
    dataclass_transform,
    overload,
)


def private_init_below() -> Any:
    return None


@dataclass(frozen=True)
class default[O, R]:
    init: Callable[[O], R]

    def __call__(self, obj: O) -> R:
        return self.init(obj)


@overload
def dataclass_with_default[T](
    **kwargs: Any,
) -> Callable[[type[T]], type[T]]: ...


@overload
@dataclass_transform(
    field_descriptors=(field, Field, private_init_below, default)
)
def dataclass_with_default[T](cls: type[T]) -> type[T]: ...


@dataclass_transform(
    field_descriptors=(field, Field, private_init_below, default)
)
def dataclass_with_default[T](
    cls: type[T] | None = None, /, **kwargs: Any
) -> Callable[[type[T]], type[T]] | type[T]:
    if cls is None:
        return lambda c: dataclass_with_default(c, **kwargs)

    def post_init(self, *_: Any, **__: Any) -> None:
        if getattr(self, _NEXTRPG_INSTANCE_INIT, None):
            return

        for f in cls_fields:
            if isinstance(attr := getattr(self, f.name, None), default):
                object.__setattr__(self, f.name, attr(self))
        object.__setattr__(self, _NEXTRPG_INSTANCE_INIT, True)

    cls.__post_init__ = post_init

    datacls = dataclass(cls, **kwargs)
    cls_fields = fields(datacls)
    return datacls


_NEXTRPG_INSTANCE_INIT = "_nextrpg_instance_init"
